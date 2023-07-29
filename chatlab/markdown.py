"""An enhanced updateable Markdown display for use in Notebooks.

* The `Markdown` display updates in place while messages are appended to it
* The `Markdown` display can be updated from an iterator

"""

import os
from binascii import hexlify
from typing import Any, Dict, Iterator, Tuple, Union

from IPython.core import display_functions


class Markdown:
    """A class for displaying a markdown string that can be updated in place.

    This class provides an easy way to create and update a Markdown string in Jupyter Notebooks. It
    supports real-time updates of Markdown content which is useful for emitting ChatGPT suggestions
    as they are generated.

    Attributes:
        message (str): The Markdown string to display

    Example:
        >>> from chatlab import Markdown
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

    def __init__(self, content: str = "") -> None:
        """Initialize a `Markdown` object with an optional message."""
        self._content: str = content
        self._display_id: str = hexlify(os.urandom(8)).decode('ascii')

    def append(self, delta: str) -> None:
        """Append a string to the `Markdown`."""
        self.content += delta

    def extend(self, delta_generator: Iterator[str]) -> None:
        """Extend the `Markdown` with a generator/iterator of strings."""
        for delta in delta_generator:
            self.append(delta)

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
            "chatlab": {
                "default": True,
            }
        }

    def __repr__(self) -> str:
        """Provide a plaintext version of the `Markdown`."""
        content = self._content
        if content is None or content == "":
            content = " "
        return content

    def _repr_markdown_(self) -> Union[str, Tuple[str, Dict[str, Any]]]:
        """Emit our markdown with metadata."""
        content = self._content
        # Handle some platforms that don't support empty Markdown
        if content is None or content == "":
            content = " "

        return content, self.metadata

    @property
    def message(self) -> str:
        """Return the `Markdown` content. Deprecated."""
        return self._content

    @message.setter
    def message(self, value: str) -> None:
        self._content = value
        self.update_displays()

    @property
    def content(self) -> str:
        """Return the `Markdown` content."""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value
        self.update_displays()
