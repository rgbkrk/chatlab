from typing import Any, Dict, Iterator, List, TypedDict

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
    return {
        'role': 'assistant',
        'content': content,
    }


def user(content: str) -> Message:
    return {
        'role': 'user',
        'content': content,
    }


def system(content: str) -> Message:
    return {
        'role': 'system',
        'content': content,
    }


# Aliases
narrate = system
human = user
ai = assistant
