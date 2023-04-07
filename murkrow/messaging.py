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


def assistant(message):
    return {
        'role': 'assistant',
        'content': message,
    }


def user(message):
    return {
        'role': 'user',
        'content': message,
    }


def system(message):
    return {
        'role': 'system',
        'content': message,
    }


# Aliases
def narrate(message):
    return system(message)


def human(message):
    return user(message)


def ai(message):
    return assistant(message)
