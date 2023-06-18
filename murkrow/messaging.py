"""Little messaging helpers for Murkrow.

>>> from murkrow import Murkrow, ai, human, system
>>> murkrow = Murkrow(system("You are a large bird"))
>>> murkrow.chat(human("What are you?"))
I am a large bird.

"""
from typing import Iterator, List, Optional, TypedDict

Delta = TypedDict(
    "Delta",
    {
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
        delta = chunk["choices"][0]["delta"]

        if "finish_reason" in delta:
            if delta["finish_reason"] == "stop":
                break

            print(chunk)

        elif "content" in delta and delta["content"] is not None:
            yield delta["content"]
        else:
            print(chunk)
            print(delta)


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
