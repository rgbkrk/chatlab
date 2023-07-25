"""A built-in for interacting with Noteable notebooks."""
import logging
import os
import uuid
from typing import Optional

import ulid
from origami.clients.api import APIClient, RTUClient
from origami.models.kernels import KernelSession
from origami.models.notebook import CodeCell, MarkdownCell

logger = logging.getLogger(__name__)


class NotebookClient:
    """A notebook client for use with Noteable."""

    api_client: APIClient
    rtu_client: Optional[RTUClient]
    kernel_session: KernelSession

    def __init__(self, api_client: APIClient, rtu_client: RTUClient, file_id: uuid.UUID, kernel_session: KernelSession):
        """Create a new NotebookClient based on an existing API and RTU client."""
        self.api_client = api_client
        self.rtu_client = rtu_client

        self.file_id = file_id

        # NOTE: We have to track the kernel session for now, though we probably
        # should be pulling this based on the file ID instead.
        self.kernel_session = kernel_session

    def notebook_url(self):
        """Get the URL for the notebook."""
        # HACK: Assuming the deployment is on the same domain as the API server.
        # True in most cases.
        base_url = self.api_client.api_base_url.split("/gate")[0]
        return f"{base_url}/f/{self.file_id}"

    @classmethod
    async def connect(cls, token=None, file_id=None):
        """Connect to an existing notebook."""
        return await cls.create(token=token, file_id=file_id)

    @classmethod
    async def create(cls, token=None, file_id=None, file_name=None, project_id=None):
        """Create a new notebook."""
        if token is None:
            token = os.environ.get("NOTEABLE_TOKEN")
            assert token is not None

        logger.info("Setting up API Client")
        api_client = APIClient(authorization_token=token)

        if file_id is None:
            if project_id is None:
                user_info = await api_client.user_info()
                # We'll use the user's default project ID for the rest of this example
                project_id = user_info.origamist_default_project_id

                if project_id is None:
                    raise Exception("User has no default project")

            if file_name is None:
                file_name = "Untitled.ipynb"
            file = await api_client.create_notebook(project_id, file_name)
            file_id = file.id

        # prepare our realtime client
        logger.info("Setting up RTU")
        rtu_client = await api_client.rtu_client(file_id)

        logger.info("Launching kernel")
        # Launch the kernel for the notebook
        # We have to track the kernel_session for now
        kernel_session = await api_client.launch_kernel(file_id)

        logger.info("Waiting for kernel to idle")
        # Wait for the kernel to start
        await rtu_client.wait_for_kernel_idle()

        cn = NotebookClient(api_client, rtu_client, file_id=file_id, kernel_session=kernel_session)

        return cn

    async def get_or_create_rtu_client(self):
        """Get or create an RTU client."""
        if self.rtu_client is None:
            self.rtu_client = await self.api_client.rtu_client(self.file_id)

        return self.rtu_client

    async def create_cell(
        self,
        source: str,
        cell_id: Optional[str] = None,
        and_run: bool = False,
        cell_type: str = "code",
        after_cell_id: Optional[str] = None,
    ):
        """Create a code, markdown, or SQL cell."""
        rtu_client = await self.get_or_create_rtu_client()

        if after_cell_id is None:
            existing_cells = rtu_client.cell_ids
            if existing_cells and len(existing_cells) > 0:
                after_cell_id = existing_cells[-1]

        if cell_id is None:
            cell_id = str(ulid.ULID())

        cell = None

        if cell_type == "markdown":
            cell = MarkdownCell(source=source, id=cell_id)
        elif cell_type == "code":
            cell = CodeCell(source=source, id=cell_id)
        elif cell_type == "sql":
            cell = CodeCell(source=source, id=cell_id)
            cell.metadata.update({"noteable": {"cell_type": "sql"}})

        if cell is None:
            return f"Unknown cell type {cell_type}. Valid types are: markdown, code, sql."

        cell = await rtu_client.add_cell(cell, after_id=after_cell_id)

        if cell.cell_type != "code" or not and_run:
            return cell

        try:
            return await self.run_cell(cell.id)
        except Exception as e:
            return f"Cell created successfully. An error happened during run: {e}"

    async def run_cell(self, cell_id: str):
        """Run a Cell within a Notebook by ID."""
        # Queue up the execution
        rtu_client = await self.get_or_create_rtu_client()
        results_future = await rtu_client.queue_execution(cell_id)

        # results_future is either a list of codecell or a codecell
        if isinstance(results_future, list):
            # HACK: queue_execute only returns a list when given a list (or requested to run all)
            # This is here just for types to be happy.
            results_future = results_future[0]

        # Wait for execution to finish
        cell = await results_future

        if cell.output_collection_id is None:
            # Hypothesis: if the output collection ID is None, we're in a bad
            # state. When the LLM sees this cell they will think its fine.
            return cell

        output_collection_id = cell.output_collection_id

        if isinstance(output_collection_id, str):
            try:
                output_collection_id = uuid.UUID(output_collection_id)
            except ValueError:
                logger.exception("Invalid UUID", exc_info=True)
                return cell

        # Pull the outputs for this execution of the cell
        output_collection = await self.api_client.get_output_collection(output_collection_id)

        outputs = output_collection.outputs

        # Not *that* friendly, but it's a start.
        llm_friendly_outputs = []

        for output in outputs:
            content = output.content
            if content is None:
                continue

            if content.mimetype == 'application/vnd.dataresource+json':
                content.raw = "[[DataFrame shown in notebook that user can see]]"
                content.url = None

                llm_friendly_outputs.append(content.dict(exclude_unset=True, exclude_none=True))
            elif content.url is not None:
                content.raw = "[[Output shown in notebook that user can see]]"
                content.url = None
                # Faking this in order to iterate
                llm_friendly_outputs.append({"embed": "![image.png](image.png)"})
            else:
                llm_friendly_outputs.append(content.dict(exclude_unset=True, exclude_none=True))

        return llm_friendly_outputs

    async def get_datasources(self):
        """Get a list of databases, AKA datasources."""
        return await self.api_client.get_datasources_for_notebook(self.file_id)

    async def get_cell(self, cell_id: str):
        """Get a cell by ID."""
        rtu_client = await self.get_or_create_rtu_client()
        return rtu_client.builder.get_cell(cell_id)

    async def shutdown(self):
        """Shutdown the notebook."""
        if self.rtu_client is not None:
            await self.rtu_client.shutdown()
        await self.api_client.shutdown_kernel(self.kernel_session.id)

        self.rtu_client = None

    """This `python` function is here for dealing with ChatGPT's `python` hallucination."""

    async def python(self, code: str):
        """Creates a python cell, runs it, and returns output."""
        return await self.create_cell(code, and_run=True)


__all__ = ["NotebookClient"]


# Only expose the NotebookClient to tab completion
def __dir__():
    return __all__
