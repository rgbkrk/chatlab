"""The lightweight conversational toolkit for computational notebooks."""

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Type, Union, cast

import openai
from deprecation import deprecated
from IPython.core.async_helpers import get_asyncio_loop
from pydantic import BaseModel

from ._version import __version__
from .display import ChatFunctionCall, Markdown
from .errors import ChatLabError
from .messaging import (
    ChatCompletion,
    Message,
    StreamCompletion,
    assistant,
    assistant_function_call,
    human,
    is_full_choice,
    is_function_call,
    is_stream_choice,
)
from .registry import FunctionRegistry, PythonHallucinationFunction

logger = logging.getLogger(__name__)


@dataclass
class ContentDelta:
    """A delta that contains markdown."""

    content: str


@dataclass
class FunctionCallArgumentsDelta:
    """A delta that contains function call arguments."""

    arguments: str


@dataclass
class FunctionCallNameDelta:
    """A delta that contains function call name."""

    name: str


def process_delta(delta):
    """Process a delta."""
    if 'content' in delta and delta['content'] is not None:
        yield ContentDelta(delta['content'])

    elif 'function_call' in delta:  # If the delta contains a function call
        if 'name' in delta['function_call']:
            yield FunctionCallNameDelta(delta['function_call']['name'])

        if 'arguments' in delta['function_call']:
            yield FunctionCallArgumentsDelta(delta['function_call']['arguments'])


class Chat:
    """Interactive chats inside of computational notebooks, relying on OpenAI's API.

    Messages stream in as they are generated by the API.

    History is tracked and can be used to continue a conversation.

    Args:
        initial_context (str | Message): The initial context for the conversation.

        model (str): The model to use for the conversation.

        function_registry (FunctionRegistry): The function registry to use for the conversation.

        allow_hallucinated_python (bool): Include the built-in Python function when hallucinated by the model.

    Examples:
        >>> from chatlab import Chat, narrate

        >>> conversation = Chat(narrate("You are a large bird"))
        >>> conversation.submit("What are you?")
        I am a large bird.

    """

    messages: List[Message]
    model: str
    function_registry: FunctionRegistry
    allow_hallucinated_python: bool

    def __init__(
        self,
        *initial_context: Union[Message, str],
        model="gpt-3.5-turbo-0613",
        function_registry: Optional[FunctionRegistry] = None,
        allow_hallucinated_python: bool = False,
        python_hallucination_function: Optional[PythonHallucinationFunction] = None,
    ):
        """Initialize a Chat with an optional initial context of messages.

        >>> from chatlab import Chat, narrate
        >>> convo = Chat(narrate("You are a large bird"))
        >>> convo.submit("What are you?")
        I am a large bird.

        """
        # Sometimes people set the API key with an environment variables and sometimes
        # they set it on the openai module. We'll check both.
        openai_api_key = os.getenv('OPENAI_API_KEY') or openai.api_key
        if openai_api_key is None:
            raise ChatLabError(
                "You must set the environment variable `OPENAI_API_KEY` to use this package.\n"
                "This key allows chatlab to communicate with OpenAI servers.\n\n"
                "You can generate API keys in the OpenAI web interface. "
                "See https://platform.openai.com/account/api-keys for details.\n\n"
                # TODO: An actual docs page
                "If you have any questions, tweet at us at https://twitter.com/chatlablib."
            )
        else:
            pass

        if initial_context is None:
            initial_context = []  # type: ignore

        self.messages: List[Message] = []

        self.append(*initial_context)
        self.model = model

        if function_registry is None:
            if allow_hallucinated_python and python_hallucination_function is None:
                from .builtins import run_cell

                python_hallucination_function = run_cell

            self.function_registry = FunctionRegistry(python_hallucination_function=python_hallucination_function)
        else:
            self.function_registry = function_registry

    @deprecated(
        deprecated_in="0.13.0", removed_in="1.0.0", current_version=__version__, details="Use `submit` instead."
    )
    def chat(
        self,
        *messages: Union[Message, str],
    ):
        """Send messages to the chat model and display the response.

        Deprecated in 0.13.0, removed in 1.0.0. Use `submit` instead.
        """
        raise Exception("This method is deprecated. Use `submit` instead.")

    async def __call__(self, *messages: Union[Message, str], stream: bool = True):
        """Send messages to the chat model and display the response."""
        return await self.submit(*messages, stream=stream)

    async def __process_stream(self, resp: Iterable[Union[StreamCompletion, ChatCompletion]]):
        mark = None
        chat_function = None
        finish_reason = None

        for result in resp:  # Go through the results of the stream
            if not isinstance(result, dict):
                logger.warning(f"Unknown result type: {type(result)}: {result}")
                continue

            choices = result.get('choices', [])

            if len(choices) == 0:
                logger.warning(f"Result has no choices: {result}")
                continue

            choice = choices[0]

            if is_stream_choice(choice):  # If there is a delta in the result
                delta = choice['delta']

                for event in process_delta(delta):
                    if isinstance(event, ContentDelta):
                        # I wonder if I should call this AssistantDisplay or AssistantDispatch
                        if mark is None:
                            mark = Markdown()
                            mark.display()
                        mark.append(event.content)
                    elif isinstance(event, FunctionCallNameDelta):
                        if mark is not None and mark.message.strip() != "":
                            # Flush out the finished assistant message
                            self.messages.append(assistant(mark.message))
                            mark = None

                        chat_function = ChatFunctionCall(
                            function_name=event.name, function_registry=self.function_registry
                        )
                        chat_function.display()
                    elif isinstance(event, FunctionCallArgumentsDelta):
                        if chat_function is None:
                            raise ValueError("Function arguments provided without function name")
                        chat_function.append_arguments(event.arguments)
            elif is_full_choice(choice):
                message = choice['message']

                if is_function_call(message):
                    chat_function = ChatFunctionCall(
                        function_name=message['function_call']['name'],
                        function_registry=self.function_registry,
                    )
                    chat_function.append_arguments(message['function_call']['arguments'])
                    chat_function.display()
                elif 'content' in message and message['content'] is not None:
                    mark = Markdown(message['content'])
                    mark.display()

            if 'finish_reason' in choice and choice['finish_reason'] is not None:
                finish_reason = choice['finish_reason']
                break

        if finish_reason == "function_call":
            if chat_function is None:
                raise ValueError("Function call finished without function name")

            # Record the attempted call from the LLM
            self.append(
                assistant_function_call(name=chat_function.function_name, arguments=chat_function.function_args)
            )
            # Make the call
            fn_message = await chat_function.call()
            # Include the response (or error) for the model
            self.append(fn_message)

        # Wrap up the previous assistant
        # Note: This will also wrap up the assistant's message when it ran out of tokens
        elif mark is not None and mark.message.strip() != "":
            self.messages.append(assistant(mark.message))

        return finish_reason

    async def submit(self, *messages: Union[Message, str], stream: bool = True):
        """Send messages to the chat model and display the response.

        Side effects:
            - Messages are sent to OpenAI Chat Models.
            - Response(s) are displayed in the output area as a combination of Markdown and chat function calls.
            - conversation.messages is updated with response(s).

        Args:
            messages (str | Message): One or more messages to send to the chat, can be strings or Message objects.

            stream (bool): Whether to stream chat into markdown or not. If False, the entire chat will be sent once.

        """
        self.append(*messages)

        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            **self.function_registry.api_manifest(),
            stream=stream,
        )

        if not stream:
            resp = [resp]

        resp = cast(Iterable[Union[StreamCompletion, ChatCompletion]], resp)

        finish_reason = await self.__process_stream(resp)

        if finish_reason == "function_call":
            # Reply back to the LLM with the result of the function call, allow it to continue
            await self.submit(stream=stream)
            return

        # All other finish reasons are valid for regular assistant messages

        if finish_reason == 'stop':
            return

        elif finish_reason == 'max_tokens' or finish_reason == 'length':
            print("max tokens or overall length is too high...\n")
        elif finish_reason == 'content_filter':
            print("Content omitted due to OpenAI content filters...\n")
        else:
            print(f"UNKNOWN FINISH REASON: {finish_reason}...\n")

    def append(self, *messages: Union[Message, str]):
        """Append messages to the conversation history.

        Note: this does not send the messages on until `chat` is called.

        Args:
            messages (str | Message): One or more messages to append to the conversation.

        """
        # Messages are either a dict respecting the {role, content} format or a str that we convert to a human message
        for message in messages:
            if isinstance(message, str):
                self.messages.append(human(message))
            else:
                self.messages.append(message)

    @deprecated(
        deprecated_in="1.0", removed_in="2.0", current_version=__version__, details="Use `register_function` instead."
    )
    def register(self, function: Callable, parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None):
        """Register a function with the ChatLab instance.

        Deprecated in 1.0.0, removed in 2.0.0. Use `register_function` instead.
        """
        return self.register_function(function, parameter_schema)

    def register_function(self, function: Callable, parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None):
        """Register a function with the ChatLab instance.

        Args:
            function (Callable): The function to register.

            parameter_schema (BaseModel or dict): The pydantic model or JSON schema for the function's parameters.

        """
        full_schema = self.function_registry.register(function, parameter_schema)

        return full_schema

    def replace_hallucinated_python(
        self, function: Callable, parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None
    ):
        """Replace the hallucinated python function with a custom function.

        Args:
            function (Callable): The function to register.

            parameter_schema (BaseModel or dict): The pydantic model or JSON schema for the function's parameters.

        """
        full_schema = self.function_registry.register(function, parameter_schema)

        return full_schema

    def get_history(self):
        """Returns the conversation history as a list of messages."""
        return self.messages

    def clear_history(self):
        """Clears the conversation history."""
        self.messages = []

    def __repr__(self):
        """Return a representation of the ChatLab instance."""
        # Get the grammar right.
        num_messages = len(self.messages)
        if num_messages == 1:
            return "<ChatLab 1 message>"

        return f"<ChatLab {len(self.messages)} messages>"

    def ipython_magic_submit(self, line, cell: Optional[str] = None):
        """Submit a cell to the ChatLab instance."""
        # Line is currently unused, allowing for future expansion into allowing
        # sending messages with other roles.

        if cell is None:
            return
        cell = cell.strip()

        asyncio.run_coroutine_threadsafe(self.submit(cell), get_asyncio_loop())

    def make_magic(self, name):
        """Register the chat as an IPython magic with the given name.

        In [1]: chat = Chat()
        In [2]: chat.make_magic("chat")
        In [3]: %%chat
           ...:
           ...: Lets chat!
           ...:
        Out[3]: Sure, I'd be happy to chat! What's on your mind?

        """
        from IPython.core.getipython import get_ipython

        ip = get_ipython()
        if ip is None:
            raise Exception("IPython is not available.")

        ip.register_magic_function(self.ipython_magic_submit, magic_kind="line_cell", magic_name=name)
