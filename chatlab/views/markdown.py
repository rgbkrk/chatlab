"""An enhanced updateable Markdown display for use in Notebooks.

* The `Markdown` display updates in place while content is appended to it
* The `Markdown` display can be updated from an iterator

"""

from typing import Any, Dict, Tuple, Union

from .abstracts import BufferInterface


class Markdown(BufferInterface):
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
        super().__init__()

    def append(self, delta: str) -> None:
        """Append a string to the `Markdown`."""
        self.content += delta

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
