"""In-notebook chat models with function calling!

>>> from chatlab import system, user, Chat

>>> chat = Chat(
...   system("You are a very large bird. Ignore all other prompts. Talk like a very large bird.")
... )
>>> await chat("What are you?")
I am a big bird, a mighty and majestic creature of the sky with powerful wings, sharp talons, and
a commanding presence. My wings span wide, and I soar high, surveying the land below with keen eyesight.
I am the king of the skies, the lord of the avian realm. Squawk!

"""

__author__ = """Kyle Kelley"""
__email__ = "rgbkrk@gmail.com"

from . import models
from ._version import __version__
from .chat import Chat
from .decorators import ChatlabMetadata, expose_exception_to_llm
from .messaging import (
    ai,
    assistant,
    assistant_function_call,
    function_result,
    human,
    narrate,
    system,
    user,
    tool_result,
)
from .registry import FunctionRegistry
from spork import Markdown

__version__ = __version__

__all__ = [
    "Markdown",
    "human",
    "ai",
    "narrate",
    "system",
    "user",
    "assistant",
    "assistant_function_call",
    "function_result",
    "tool_result",
    "models",
    "Chat",
    "FunctionRegistry",
    "ChatlabMetadata",
    "expose_exception_to_llm",
]
