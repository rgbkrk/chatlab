"""Abstract classes for buffers."""
import os
from abc import ABC, abstractmethod
from binascii import hexlify

from IPython.core import display_functions
from openai.types.chat import ChatCompletionMessageParam


class AutoDisplayer(ABC):
    """Simple auto displayer."""

    _display_id: str

    def __init__(self):
        """Initialize a `AutoDisplayer` object."""
        self._display_id = self.generate_display_id()

    def generate_display_id(self) -> str:
        """Generate a display ID."""
        return hexlify(os.urandom(8)).decode("ascii")

    def display(self):
        """Display the object with a display ID to allow updating."""
        display_functions.display(self, display_id=self._display_id)

    def update_displays(self) -> None:
        """Force an update to all displays of this object."""
        display_functions.display(self, display_id=self._display_id, update=True)


class BufferInterface(AutoDisplayer):
    """Interface for buffers."""

    @abstractmethod
    def append(self, delta: str):
        """Append a string to the buffer."""
        pass

    @property
    @abstractmethod
    def content(self) -> str:
        """Return the buffer content."""
        pass


class BufferView(ABC):
    """A generic buffer view."""

    buffer: BufferInterface

    def __init__(self, content: str = ""):
        """Initialize a `BufferView` object with optional starting content."""
        self.buffer = self.create_buffer(content)
        self.active = False

    @abstractmethod
    def create_buffer(self, content: str = "") -> BufferInterface:
        """Creates the specific buffer for the view. To be overridden in subclasses."""
        pass

    def display(self):
        """Create an updating display for the message."""
        if not self.active:
            self.buffer.display()
        self.active = True

    def append(self, delta: str):
        """Append a string to the message."""
        self.display()
        self.buffer.append(delta)

    @property
    def content(self):
        """Returns the raw content."""
        return self.buffer.content

    def is_empty(self):
        """Returns True if the message is empty, False otherwise."""
        return self.content.strip() == ""

    def in_progress(self):
        """Returns True if the message is in progress, False otherwise."""
        return self.active and not self.is_empty()

    @abstractmethod
    def get_message(self) -> ChatCompletionMessageParam:
        """Returns the crafted message. To be overridden in subclasses."""
        pass

    def flush(self) -> ChatCompletionMessageParam:
        """Flushes the message buffer."""
        message = self.get_message()
        self.buffer = self.create_buffer()
        self.active = False
        return message

    def _ipython_display_(self):
        """Display the buffer."""
        self.buffer.display()
        self.active = True
