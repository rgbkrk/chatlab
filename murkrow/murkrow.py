"""Main module."""

import openai

from .messaging import deltas, ai, human
from .display import Markdown


class Murkrow:
    def __init__(self, *initial_context, model="gpt-3.5-turbo"):
        if initial_context is None:
            initial_context = []

        self.messages = []
        self.messages.extend(initial_context)
        self.model = model

    def chat(self, *messages):
        # Messages are either a dict respecting the {role, content} format or a str that we convert to a human message
        for message in messages:
            if isinstance(message, str):
                self.messages.append(human(message))
            else:
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
