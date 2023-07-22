"""Stylized representation of a Chat Function Call as we dance with the LLM."""

import os
from binascii import hexlify
from typing import Optional

from IPython.core import display_functions
from vdom import details, div, span, style, summary

# Importing for the sake of backwards compatibility
from .markdown import Markdown  # noqa: F401
from .messaging import Message, function_result, system
from .registry import FunctionArgumentError, FunctionRegistry, UnknownFunctionError

# Palette used here is https://colorhunt.co/palette/27374d526d829db2bfdde6ed
colors = {
    "darkest": "#27374D",
    "dark": "#526D82",
    "light": "#9DB2BF",
    "lightest": "#DDE6ED",
    "ultralight": "#F7F9FA",
    # Named variants (not great names...)
    "Japanese Indigo": "#27374D",
    "Approximate Arapawa": "#526D82",
    "Light Slate": "#9DB2BF",
    "Pattens Blue": "#DDE6ED",
    # ChatLab Colors
    "Charcoal": "#2B4155",
    "Lapis Lazuli": "#3C5B79",
    "UCLA Blue": "#527498",
    "Redwood": "#A04446",
    "Sunset": "#EFCF99",
}


def function_logo():
    """Styled 𝑓 logo component for use in the chat function component."""
    return span("𝑓", style=dict(color=colors["light"], paddingRight="5px", paddingLeft="5px"))


def function_verbage(state: str):
    """Simple styled state component."""
    return span(state, style=dict(color=colors["darkest"], paddingRight="5px", paddingLeft="5px"))


def inline_pre(text: str):
    """A simple preformatted monospace component that works in all Jupyter frontends."""
    return span(text, style=dict(unicodeBidi="embed", fontFamily="monospace", whiteSpace="pre"))


def raw_function_interface_heading(text: str):
    """Display Input: or Output: headings for the chat function interface."""
    return div(
        text,
        style=dict(
            color=colors["darkest"],
            fontWeight="500",
            marginBottom="5px",
        ),
    )


def raw_function_interface(text: str):
    """For inputs and outputs of the chat function interface."""
    return div(
        text,
        style=dict(
            background=colors["ultralight"],
            color=colors["darkest"],
            padding="10px",
            marginBottom="10px",
            unicodeBidi="embed",
            fontFamily="monospace",
            whiteSpace="pre",
            overflowX="auto",
        ),
    )


def ChatFunctionComponent(
    name: str,
    verbage: str,
    input: Optional[str] = None,
    output: Optional[str] = None,
    finished: bool = False,
):
    """A component for displaying a chat function's state and input/output."""
    input_element = div()
    if input is not None:
        input = input.strip()
        input_element = div(raw_function_interface_heading("Input:"), raw_function_interface(input))

    output_element = div()
    if output is not None:
        output = output.strip()
        output_element = div(
            raw_function_interface_heading("Output:"),
            raw_function_interface(output),
        )

    return div(
        style(".chatlab-chat-details summary > *  { display: inline; color: #27374D; }"),
        details(
            summary(
                function_logo(),
                function_verbage(verbage),
                inline_pre(name),
                # If not finished, show "...", otherwise show nothing
                inline_pre("..." if not finished else ""),
                style=dict(cursor="pointer", color=colors["darkest"]),
            ),
            div(
                input_element,
                output_element,
                style=dict(
                    # Need some space above to separate from the summary
                    marginTop="10px",
                    marginLeft="10px",
                ),
            ),
            className="chatlab-chat-details",
            style=dict(
                background=colors["lightest"],
                padding=".5rem 1rem",
                borderRadius="5px",
            ),
        ),
    )


class ChatFunctionCall:
    """Operates like the Markdown class, but with the ChatFunctionComponent."""

    function_name: str
    function_args: Optional[str] = None

    function_result: Optional[str] = None
    _display_id: str

    state: str = "Generating"

    finished: bool = False

    def __init__(self, function_name: str, function_registry: FunctionRegistry):
        """Initialize a `ChatFunctionCall` object with an optional message."""
        self.function_name = function_name
        self.function_registry = function_registry
        self._display_id: str = hexlify(os.urandom(8)).decode('ascii')

    def display(self):
        """Display the `ChatFunctionCall` with a display ID for receiving updates."""
        display_functions.display(self, display_id=self._display_id)

    def update_displays(self) -> None:
        """Force an update to all displays of this `ChatFunctionCall`."""
        display_functions.display(self, display_id=self._display_id, update=True)

    async def call(self) -> Message:
        """Call the function and return a stack of messages for LLM and human consumption."""
        function_name = self.function_name
        function_args = self.function_args

        if function_name is None:
            self.set_state("Error")
            return system("Function call message finished without function name")

        self.set_state("Running")

        # Execute the function and get the result
        try:
            output = await self.function_registry.call(function_name, function_args)
        except FunctionArgumentError as e:
            self.finished = True
            self.set_state("Errored")
            self.function_result = repr(e)
            return system(f"Function arguments for {function_name} were invalid: {e}")
        except UnknownFunctionError as e:
            self.finished = True
            self.set_state("No function named")
            self.function_result = repr(e)
            return system(f"Function {function_name} not found in function registry: {e}")
        except Exception as e:
            # Check to see if the user has requested that the exception be exposed to LLM.
            # If not, then we just raise it and let the user handle it.
            chatlab_metadata = self.function_registry.get_chatlab_metadata(function_name)

            if not chatlab_metadata.expose_exception_to_llm:
                # Bubble up the exception to the user
                raise

            repr_llm = repr(e)

            self.function_result = repr_llm
            self.finished = True
            self.state = "Errored"
            self.update_displays()

            return function_result(name=function_name, content=repr_llm)

        repr_llm = ""
        if isinstance(output, str):
            repr_llm = output
        elif getattr(output, "_repr_llm_", None) is not None:
            repr_llm = output._repr_llm_()
        else:
            repr_llm = repr(output)

        self.function_result = repr_llm
        self.finished = True
        self.state = "Ran"
        self.update_displays()

        return function_result(name=function_name, content=repr_llm)

    def append_arguments(self, args: str):
        """Append more characters to the `function_args`."""
        if self.function_args is None:
            self.function_args = ""
        self.function_args += args
        self.update_displays()

    def set_state(self, state: str):
        """Set the state of the ChatFunctionCall."""
        self.state = state
        self.update_displays()

    def _repr_mimebundle_(self, include=None, exclude=None):
        vdom_component = ChatFunctionComponent(
            name=self.function_name,
            verbage=self.state,
            input=self.function_args,
            output=self.function_result,
            finished=self.finished,
        )
        return {
            "text/html": vdom_component.to_html(),
            "application/vdom.v1+json": vdom_component.to_dict(),
        }
