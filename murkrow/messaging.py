import openai
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


class Murkrow:
    def __init__(self, *initial_context):
        if initial_context is None:
            initial_context = []

        self.messages = []
        self.messages.extend(initial_context)
        self.model = "gpt-3.5-turbo"

    def chat(self, *messages):
        self.messages.extend(messages)

        mark = Markdown()
        mark.display()

        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            stream=True,
        )

        mark.extend(deltas(resp))

        self.messages.append(ai(mark.message))
