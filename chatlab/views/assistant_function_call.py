"""Views for the buffers."""

from typing import TypedDict

from ..messaging import assistant_function_call
from .abstracts import BufferView
from .argument_buffer import ArgumentBuffer

AssistantFunctionCallDict = TypedDict(
    "AssistantFunctionCallDict",
    {
        "function_name": str,
        "function_arguments": str,
        "display_id": str,
    },
)


class AssistantFunctionCallView(BufferView):
    """A view for the assistant's message."""

    buffer: ArgumentBuffer

    def __init__(self, function_name: str):
        """Initialize a `AssistantFunctionCallView` object with an optional message."""
        self.__function_name = function_name
        super().__init__()

    def create_buffer(self, content: str = "") -> ArgumentBuffer:
        """Creates the specific buffer for the view."""
        return ArgumentBuffer(self.__function_name, content)

    def get_message(self):
        """Returns the crafted message."""
        return assistant_function_call(self.__function_name, self.content)

    def finalize(self) -> AssistantFunctionCallDict:
        """Finalize the buffering."""
        return {
            "function_name": self.__function_name,
            "function_arguments": self.content,
            "display_id": self.buffer._display_id,
        }
