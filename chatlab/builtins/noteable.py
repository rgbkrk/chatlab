"""A built-in for interacting with Noteable notebooks."""
import logging
import os
import uuid
from typing import Optional

import ulid
from origami.clients.api import APIClient, RTUClient
from origami.models.api.outputs import KernelOutput
from origami.models.kernels import KernelSession
from origami.models.notebook import CodeCell, MarkdownCell

from ._mediatypes import formats_for_llm

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
        rtu_client = await api_client.connect_realtime(file_id)

        logger.info("Launching kernel")
        # Launch the kernel for the notebook
        # We have to track the kernel_session for now
        kernel_session = await api_client.launch_kernel(file_id)

        cn = NotebookClient(api_client, rtu_client, file_id=file_id, kernel_session=kernel_session)

        return cn

    async def get_or_create_rtu_client(self):
        """Get or create an RTU client."""
        if self.rtu_client is None:
            self.rtu_client = await self.api_client.connect_realtime(self.file_id)

        return self.rtu_client

    async def wait_for_kernel_idle(self):
        """Wait for the kernel to be idle."""
        rtu_client = await self.get_or_create_rtu_client()
        await rtu_client.wait_for_kernel_idle()

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

    async def _get_llm_friendly_outputs(self, output_collection_id: uuid.UUID):
        """Get the outputs for a given output collection ID."""
        output_collection = await self.api_client.get_output_collection(output_collection_id)

        outputs = output_collection.outputs

        # Not *that* friendly, but it's a start.
        llm_friendly_outputs = []

        for output in outputs:
            content = output.content
            if content is None:
                continue

            friendly_output = await self._get_llm_friendly_output(output)

            if friendly_output is not None:
                llm_friendly_outputs.append(friendly_output)

        return llm_friendly_outputs

    async def extract_llm_plain(self, output: KernelOutput):
        resp = await self.api_client.client.get(f"/outputs/{output.id}?mimetype=text%2Fllm%2Bplain")
        resp.raise_for_status()

        output_for_llm = KernelOutput.parse_obj(resp.json())

        if output_for_llm.content is None:
            return None

        return output_for_llm.content.raw

    async def _get_llm_friendly_output(self, output: KernelOutput):
        """Get the output for a given output."""
        content = output.content
        if content is None:
            return None

        if 'text/llm+plain' in output.available_mimetypes:
            # Fetch the specialized LLM+Plain directly
            result = await self.extract_llm_plain(output)
            if result is not None:
                return result

        if content.mimetype == 'application/vnd.dataresource+json':
            # TODO: Bring back a smaller representation to allow the LLM to do analysis
            return "<!-- DataFrame shown in notebook that user can see -->"

        if content.mimetype == 'application/vnd.plotly.v1+json':
            return "<!-- Plotly shown in notebook that user can see -->"
        if content.url is not None:
            return "<!-- Large output too large for chat. It is available in the notebook that the user can see -->"

        if content.mimetype in formats_for_llm:
            return content.raw

        mimetypes: list[str] = output.available_mimetypes

        for format in formats_for_llm:
            if format in mimetypes:
                resp = await self.api_client.client.get(f"/outputs/{output.id}?mimetype={format}")
                resp.raise_for_status()
                if resp.status_code == 200:
                    return

                next_best_output = KernelOutput.parse_obj(resp.json())

                if next_best_output.content is None:
                    continue

                if next_best_output.content.raw is not None:
                    return next_best_output.content.raw

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

        outputs = self._get_llm_friendly_outputs(output_collection_id)

        return outputs

    async def get_datasources(self):
        """Get a list of databases, AKA datasources."""
        return await self.api_client.get_datasources_for_notebook(self.file_id)

    async def get_cell(self, cell_id: str):
        """Get a cell by ID."""
        rtu_client = await self.get_or_create_rtu_client()
        try:
            _, cell = rtu_client.builder.get_cell(cell_id)
        except KeyError:
            return f"Cell {cell_id} not found."

        response = f"<!-- {cell.cell_type.title()} Cell, ID: {cell_id} -->\n"

        if cell.cell_type != "code":
            response += cell.source
            return response

        source_type = rtu_client.builder.nb.metadata.get("kernelspec", {}).get("language", "")

        if cell.metadata.get("noteable", {}).get("cell_type") == "sql":
            source_type = "sql"

        # Convert to a plaintext response
        response += f"\nIn:\n\n```{source_type}\n"
        response += cell.source
        response += "\n```\n"

        output_collection_id = cell.output_collection_id

        if isinstance(output_collection_id, str):
            try:
                output_collection_id = uuid.UUID(output_collection_id)
            except ValueError:
                # This is a case where the output collection ID in the notebook is invalid
                logger.exception("Invalid UUID", exc_info=True)
                return response + "\nUnable to get outputs."

        if output_collection_id is None:
            return response + "\nNo output."

        outputs = await self._get_llm_friendly_outputs(output_collection_id)
        if len(outputs) == 0:
            return response + "\nNo output."

        response += "\nOut:"

        for output in outputs:
            response += "\n" + str(output)

        return response

    async def get_cell_ids(self):
        """Get all cells."""
        rtu_client = await self.get_or_create_rtu_client()
        return rtu_client.cell_ids

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

    def chat_functions(self):
        """Functions to expose for LLMs."""
        return [
            self.create_cell,
            self.run_cell,
            self.get_cell,
            self.get_cell_ids,
            self.get_datasources,
        ]


__all__ = ["NotebookClient"]


# Only expose the NotebookClient to tab completion
def __dir__():
    return __all__
