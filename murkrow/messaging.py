"""Little messaging helpers for Murkrow.

>>> from murkrow import Murkrow, ai, human, system
>>> murkrow = Murkrow(system("You are a large bird"))
>>> murkrow.chat(human("What are you?"))
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


def deltas(completion: Iterator[StreamCompletion]) -> Iterator[str]:
    """Extract the deltas from a stream completion.

    >>> from murkrow import deltas
    >>> deltas([{'choices': [{'delta': {'content': 'Hello'}}]}])
    ['Hello']

    """

    for chunk in completion:
        # Note that chunk has an ID for the completion. We're not using it yet
        choice = chunk["choices"][0]

        delta = choice["delta"]

        if "finish_reason" in delta:
            if delta["finish_reason"] == "stop":
                break

        elif "content" in delta and delta["content"] is not None:
            yield delta["content"]
        else:
            pass


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

    >>> from murkrow import assistant
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


def assistant_function_call(name: str, arguments: str) -> Message:
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
