import os
from binascii import hexlify
from typing import Any, Dict, Iterator, Tuple, Union

from IPython.core import display_functions


class Markdown:
    """
    A class for displaying a markdown string that can be updated in place.

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
        self._message: str = message
        self._display_id: str = hexlify(os.urandom(8)).decode('ascii')

    def append(self, delta: str) -> None:
        self.message += delta

    def extend(self, delta_generator: Iterator[str]) -> None:
        for delta in delta_generator:
            self.append(delta)

    def consume(self, delta_generator: Iterator[str]) -> None:
        self.extend(delta_generator)

    def display(self) -> None:
        '''Display the `Markdown` with a display ID for receiving updates'''
        display_functions.display(self, display_id=self._display_id)

    def update_displays(self) -> None:
        '''Force an update to all displays'''
        display_functions.display(self, display_id=self._display_id, update=True)

    @property
    def metadata(self) -> Dict[str, Any]:
        return {
            "murkrow": {
                "default": True,
            }
        }

    def __repr__(self) -> str:
        message = self._message
        if message is None or message == "":
            message = " "
        return message

    def _repr_markdown_(self) -> Union[str, Tuple[str, Dict[str, Any]]]:
        message = self._message
        # Handle some platforms that don't support empty Markdown
        if message is None or message == "":
            message = " "

        return message, self.metadata

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value
        self.update_displays()
