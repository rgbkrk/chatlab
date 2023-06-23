"""Little messaging helpers for ChatLab.

>>> from chatlab import ChatLab, ai, human, system
>>> chatlab = ChatLab(system("You are a large bird"))
>>> chatlab.submit(human("What are you?"))
I am a large bird.

"""
from typing import Iterator, List, Optional, TypedDict

from typing_extensions import NotRequired

FunctionCall = TypedDict(
    "FunctionCall",
    {
        "name": Optional[str],
        "arguments": Optional[str],
    },
)

Delta = TypedDict(
    "Delta",
    {
        "function_call": Optional[FunctionCall],
        "content": Optional[str],
        "finish_reason": Optional[str],
    },
)


StreamChoice = TypedDict(
    "StreamChoice",
    {
        "delta": Delta,
    },
)

StreamCompletion = TypedDict(
    "StreamCompletion",
    {
        "choices": List[StreamChoice],
    },
)


Message = TypedDict(
    "Message",
    {
        "role": str,
        "content": Optional[str],
        "name": NotRequired[str],
        "function_call": NotRequired[FunctionCall],
    },
)


def assistant(content: str) -> Message:
    """Create a message from the assistant.

    >>> from chatlab import assistant
    >>> assistant("Hello!")
    {'role': 'assistant', 'content': 'Hello!'}
    """
    return {
        'role': 'assistant',
        'content': content,
    }


def user(content: str) -> Message:
    """Create a message from the user."""
    return {
        'role': 'user',
        'content': content,
    }


def system(content: str) -> Message:
    """Create a message from the system."""
    return {
        'role': 'system',
        'content': content,
    }


def assistant_function_call(name: str, arguments: Optional[str]) -> Message:
    """Create a function call message."""
    return {
        'role': 'assistant',
        'content': None,
        'function_call': {
            'name': name,
            'arguments': arguments,
        },
    }


def function_result(name: str, content: str) -> Message:
    """Create a function message."""
    return {
        'role': 'function',
        'content': content,
        'name': name,
    }


# Aliases
narrate = system
human = user
ai = assistant
