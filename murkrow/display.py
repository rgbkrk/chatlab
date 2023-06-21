"""display.py

This module provides a `Markdown` class that works similarly to `IPython.display.Markdown` with
a few extra features.

* The `Markdown`'s display updates in place while messages are appended to it
* The `Markdown`'s display can be updated from an iterator

"""

import json
import os
from binascii import hexlify
from typing import Any, Dict, Iterator, Optional, Tuple, Union

from IPython.core import display_functions
from IPython.core.getipython import get_ipython
from vdom import details, div, span, style, summary

from murkrow.registry import FunctionArgumentError, FunctionRegistry, UnknownFunctionError

from .messaging import Message, assistant_function_call, function_result, system


class Markdown:
    """A class for displaying a markdown string that can be updated in place.

    This class provides an easy way to create and update a Markdown string in Jupyter Notebooks. It
    supports real-time updates of Markdown content which is useful for emitting ChatGPT suggestions
    as they are generated.

    Attributes:
        message (str): The Markdown string to display

    Example:
        >>> from murkrow import Markdown
        ...
        >>> markdown = Markdown()
        >>> markdown.append("Hello")
        >>> markdown.append(" world!")
        >>> markdown.display()
        ```markdown
        Hello world!
        ```
        >>> markdown.append(" This is an update!")
        ```markdown
        Hello world! This is an update!
        ```
        >>> def text_generator():
        ...    yield " 1"
        ...    yield " 2"
        ...    yield " 3"
        ...
        >>> markdown.extend(text_generator())
        ```markdown
        Hello world! This is an update! 1 2 3
        ```
    """

    def __init__(self, message: str = "") -> None:
        """Initialize a `Markdown` object with an optional message."""
        self._message: str = message
        self._display_id: str = hexlify(os.urandom(8)).decode('ascii')

    def append(self, delta: str) -> None:
        """Append a string to the `Markdown`."""
        self.message += delta

    def extend(self, delta_generator: Iterator[str]) -> None:
        """Extend the `Markdown` with a generator/iterator of strings."""
        for delta in delta_generator:
            self.append(delta)

    # Alias consume
    consume = extend

    def display(self) -> None:
        """Display the `Markdown` with a display ID for receiving updates."""
        display_functions.display(self, display_id=self._display_id)

    def update_displays(self) -> None:
        """Force an update to all displays of this `Markdown`."""
        display_functions.display(self, display_id=self._display_id, update=True)

    @property
    def metadata(self) -> Dict[str, Any]:
        """Return the metadata for the `Markdown`."""
        return {
            "murkrow": {
                "default": True,
            }
        }

    def __repr__(self) -> str:
        """Provide a plaintext version of the `Markdown`."""
        message = self._message
        if message is None or message == "":
            message = " "
        return message

    def _repr_markdown_(self) -> Union[str, Tuple[str, Dict[str, Any]]]:
        """Emit our markdown with metadata."""
        message = self._message
        # Handle some platforms that don't support empty Markdown
        if message is None or message == "":
            message = " "

        return message, self.metadata

    @property
    def message(self) -> str:
        """Return the `Markdown` message."""
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value
        self.update_displays()


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
    # Murkrow Colors
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
        style(".murkrow-chat-details summary > *  { display: inline; color: #27374D; }"),
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
            className="murkrow-chat-details",
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
        """Initialize a `ChatFunctionDisplay` object with an optional message."""
        self.function_name = function_name
        self.function_registry = function_registry
        self._display_id: str = hexlify(os.urandom(8)).decode('ascii')

    def display(self):
        """Display the `ChatFunctionDisplay` with a display ID for receiving updates."""
        display_functions.display(self, display_id=self._display_id)

    def update_displays(self) -> None:
        """Force an update to all displays of this `ChatFunctionDisplay`."""
        display_functions.display(self, display_id=self._display_id, update=True)

    def call(self) -> Message:
        """Call the function and return a stack of messages for LLM and human consumption."""
        function_name = self.function_name
        function_args = self.function_args

        if function_name is None:
            self.set_state("Error")
            return system("Function call message finished without function name")

        if function_name not in self.function_registry:
            self.set_state("Error")
            return system(f"Function {function_name} not found in function registry")

        self.set_state("Running")

        # Execute the function and get the result
        try:
            output = self.function_registry.call(function_name, function_args)
        except FunctionArgumentError as e:
            self.set_state("Error")
            return system(f"Function arguments for {function_name} were invalid: {e}")
        except UnknownFunctionError as e:
            self.set_state("Error")
            return system(f"Function {function_name} not found in function registry: {e}")

        repr_llm = repr(output)

        self.append_result(repr_llm)
        self.set_state("Ran")
        self.set_finished(True)

        return function_result(name=function_name, content=repr_llm)

    def append_arguments(self, args: str):
        """Append more characters to the `function_args`."""
        if self.function_args is None:
            self.function_args = ""
        self.function_args += args
        self.update_displays()

    def append_result(self, result: str):
        """Append more characters to the `function_result`."""
        if self.function_result is None:
            self.function_result = ""
        self.function_result += result
        self.update_displays()

    def set_state(self, state: str):
        """Set the state of the function."""
        self.state = state
        self.update_displays()

    def set_finished(self, finished: bool = True):
        """Set the finished state of the function."""
        self.finished = finished
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
