"""TODO: DOCSTRING."""

from chatlab.components.function_details import ChatFunctionComponent

from .abstracts import BufferInterface


class ArgumentBuffer(BufferInterface):
    """A class for displaying arguments that update in place.

    This version only supports updating the arguments, not the function name.

    So far, OpenAI will only stream the arguments.
    """

    __function_name: str
    __function_arguments: str

    __state: str = "Generating"

    def __init__(self, function_name: str, function_arguments: str = ""):
        """Initialize a `ArgumentBuffer` object with an optional message."""
        self.__function_name = function_name
        self.__function_arguments = function_arguments
        super().__init__()

    @property
    def content(self) -> str:
        """Return the current arguments."""
        return self.__function_arguments

    def append(self, delta: str) -> None:
        """Append to the arguments."""
        self.__function_arguments += delta
        self.update_displays()

    def _repr_mimebundle_(self, include=None, exclude=None):
        vdom_component = ChatFunctionComponent(
            name=self.__function_name,
            verbage=self.__state,
            input=self.__function_arguments,
        )
        return {
            "text/html": vdom_component.to_html(),
            # "application/vdom.v1+json": vdom_component.to_dict(),
        }
