"""display.py!

This module provides a `Markdown` class that works similarly to `IPython.display.Markdown` with
a few extra features.

* The `Markdown`'s display updates in place while messages are appended to it
* The `Markdown`'s display can be updated from an iterator

"""

import os
from binascii import hexlify
from typing import Any, Dict, Iterator, Optional, Tuple, Union

from IPython.core import display_functions
from vdom import b, details, div, p, pre, span, style, summary


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


def function_logo():
    """Styled 𝑓 logo component for use in the chat function component."""
    return span("𝑓", style=dict(color="#9DB2BF", paddingRight="10px"))


def ChatFunctionComponent(function_name: str, state: str, input: Optional[str], output: Optional[str]):
    """A component for displaying a chat function's state and input/output."""
    input_element = div()
    if input is not None:
        input = input.strip()
        input_element = div(
            p("Input:"),
            pre(input),
        )

    output_element = div()
    if output is not None:
        output = output.strip()
        output_element = div(
            p("Output:"),
            pre(output),
        )

    return div(
        style(
            """
.murkrow-chat-details summary > *  {
    display: inline;
}
    """
        ),
        details(
            summary(
                function_logo(), "Running ", pre("create_cell"), "...", style=dict(cursor="pointer", color="#27374D")
            ),
            div(
                input_element,
                output_element,
            ),
            className="murkrow-chat-details",
            style=dict(background="#DDE6ED", marginBottom="2rem", padding=".5rem 1rem"),
        ),
    )


class ChatFunctionDisplay:
    """Operates like the Markdown class, but with the ChatFunctionComponent."""

    function_name: str
    function_args: Optional[str] = None

    function_result: Optional[str] = None
    _display_id: str

    def __init__(self, function_name: str):
        """Initialize a `ChatFunctionDisplay` object with an optional message."""
        self.function_name = function_name
        self._display_id: str = hexlify(os.urandom(8)).decode('ascii')

    def display(self):
        """Display the `ChatFunctionDisplay` with a display ID for receiving updates."""
        display_functions.display(self, display_id=self._display_id)

    def update_displays(self) -> None:
        """Force an update to all displays of this `ChatFunctionDisplay`."""
        display_functions.display(self, display_id=self._display_id, update=True)

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

    def _repr_markdown_(self):
        return f"⍢ {self.function_name}"
