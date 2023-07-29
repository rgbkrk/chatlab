"""Views for the buffers."""

from ..messaging import assistant
from .abstracts import BufferView
from .markdown import Markdown


class AssistantMessageView(BufferView):
    """A view for the assistant's message."""

    buffer: Markdown

    def create_buffer(self, content: str = "") -> Markdown:
        """Creates the specific buffer for the view."""
        return Markdown(content)

    def get_message(self):
        """Returns the crafted message."""
        return assistant(self.content)
