"""A built-in for interacting with Noteable notebooks."""
import os
from typing import Optional

from origami.clients.api import APIClient
from origami.models.notebook import CodeCell, MarkdownCell
from ulid import ULID


class NotebookClient:
    """A notebook client for use with Noteable."""

    def __init__(self, api_client, rtu_client):
        """Create a new NotebookClient based on an existing API and RTU client."""
        self.api_client = api_client
        self.rtu_client = rtu_client

    def notebook_url(self):
        """Get the URL for the notebook."""
        return f"https://app.noteable.io/f/{self.rtu_client.file_id}"

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

        print("Setting up API Client")
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
        print("Setting up RTU")
        rtu_client = await api_client.rtu_client(file_id)

        print("Launching kernel")
        # Launch the kernel for the notebook
        await api_client.launch_kernel(file_id)

        print("Waiting for kernel to idle")
        # Wait for the kernel to start
        await rtu_client.wait_for_kernel_idle()

        cn = NotebookClient(api_client, rtu_client)

        return cn

    async def create_cell(
        self,
        source: str,
        cell_id: Optional[str] = None,
        and_run: bool = False,
        cell_type: str = "code",
        after_cell_id: Optional[str] = None,
    ):
        """Create a code or markdown cell."""
        if after_cell_id is None:
            existing_cells = self.rtu_client.cell_ids
            if existing_cells and len(existing_cells) > 0:
                after_cell_id = existing_cells[-1]

        if cell_id is None:
            cell_id = str(ULID())

        if cell_type == "markdown":
            cell = await self.rtu_client.add_cell(MarkdownCell(source=source, id=cell_id))
            return cell

        cell = await self.rtu_client.add_cell(CodeCell(source=source, id=cell_id), after_id=after_cell_id)

        if not and_run:
            return cell

        try:
            return await self.run_cell(cell.id)
        except Exception as e:
            return f"Cell created successfully. An error happened during run: {e}"

    async def run_cell(self, cell_id: str):
        """Run a Cell within a Notebook by ID."""
        # Queue up the execution
        results_future = await self.rtu_client.execute_cell(cell_id)

        # Wait for execution to finish
        results = await results_future
        # Pull the outputs for this execution of the cell
        output_collection = await self.api_client.get_output_collection(results.output_collection_id)

        outputs = output_collection.outputs

        # Not *that* friendly, but it's a start.
        llm_friendly_outputs = []

        for output in outputs:
            content = output.content

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

    """This `python` function is here for dealing with ChatGPT's `python` hallucination."""

    async def python(self, code: str):
        """Creates a python cell, runs it, and returns output."""
        return await self.create_cell(code, and_run=True)


__all__ = ["NotebookClient"]


# Only expose the NotebookClient to tab completion
def __dir__():
    return __all__
