"""Little messaging helpers for Murkrow.

>>> from murkrow import Murkrow, ai, human, system
>>> murkrow = Murkrow(system("You are a large bird"))
>>> murkrow.chat(human("What are you?"))
I am a large bird.

"""
from typing import Iterator, List, TypedDict

Delta = TypedDict(
    "Delta",
    {
        "content": str,
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
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            yield delta["content"]


Message = TypedDict(
    "Message",
    {
        "role": str,
        "content": str,
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


# Aliases
narrate = system
human = user
ai = assistant
