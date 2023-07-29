"""Helpers for messaging in ChatLab.

This module contains helper functions for creating different types of messages in ChatLab.

Example:
    >>> from chatlab import ChatLab, ai, human, system
    >>> chatlab = ChatLab(system("You are a large bird"))
    >>> chatlab.submit(human("What are you?"))
    I am a large bird.

"""

from typing import List, Optional, TypedDict, Union

from typing_extensions import TypeGuard

BasicMessage = TypedDict(
    "BasicMessage",
    {
        "role": str,
        "content": str,
    },
)


FunctionCall = TypedDict(
    "FunctionCall",
    {
        "name": str,
        "arguments": str,
    },
)

FunctionCallMessage = TypedDict(
    "FunctionCallMessage",
    {
        "role": str,
        "content": Optional[str],
        "function_call": FunctionCall,
    },
)

FunctionResultMessage = TypedDict(
    "FunctionResultMessage",
    {
        "role": str,
        "content": str,
        "name": str,
    },
)


Message = Union[BasicMessage, FunctionCallMessage, FunctionResultMessage]


def is_function_call(message: Message) -> TypeGuard[FunctionCallMessage]:
    """Check if a message is a function call message."""
    return 'function_call' in message


def is_basic_message(message: Message) -> TypeGuard[BasicMessage]:
    """Check if a message is a basic message."""
    return 'content' in message and 'role' in message and 'function_call' not in message


#### STREAMING ####

Delta = TypedDict(
    "Delta",
    {
        "function_call": FunctionCall,
        "content": Optional[str],
    },
    total=False,
)


StreamChoice = TypedDict(
    "StreamChoice",
    {
        "finish_reason": Optional[str],
        "delta": Delta,
    },
)

StreamCompletion = TypedDict(
    "StreamCompletion",
    {
        "choices": List[StreamChoice],
    },
    total=False,
)

#### NON STREAMING ####

FullChoice = TypedDict(
    "FullChoice",
    {
        "finish_reason": Optional[str],
        "message": Message,
    },
)

ChatCompletion = TypedDict(
    "ChatCompletion",
    {
        "choices": List[FullChoice],
    },
    total=False,
)


def is_stream_choice(choice: Union[StreamChoice, FullChoice]) -> TypeGuard[StreamChoice]:
    """Check if a choice is a stream choice."""
    return 'delta' in choice


def is_full_choice(choice: Union[StreamChoice, FullChoice]) -> TypeGuard[FullChoice]:
    """Check if a choice is a regular choice."""
    return 'message' in choice


def assistant(content: str) -> BasicMessage:
    """Create a message from the assistant.

    Args:
        content: The content of the message.

    Returns:
        A dictionary representing the assistant's message.
    """
    return {
        'role': 'assistant',
        'content': content,
    }


def user(content: str) -> BasicMessage:
    """Create a message from the user.

    Args:
        content: The content of the message.

    Returns:
        A dictionary representing the user's message.
    """
    return {
        'role': 'user',
        'content': content,
    }


def system(content: str) -> BasicMessage:
    """Create a message from the system.

    Args:
        content: The content of the message.

    Returns:
        A dictionary representing the system's message.
    """
    return {
        'role': 'system',
        'content': content,
    }


def assistant_function_call(name: str, arguments: Optional[str] = None) -> FunctionCallMessage:
    """Create a function call message from the assistant.

    Args:
        name: The name of the function to call.
        arguments: Optional; The arguments to pass to the function.

    Returns:
        A dictionary representing a function call message from the assistant.
    """
    if arguments is None:
        arguments = ''

    return {
        'role': 'assistant',
        'content': None,
        'function_call': {
            'name': name,
            'arguments': arguments,
        },
    }


def function_result(name: str, content: str) -> FunctionResultMessage:
    """Create a function result message.

    Args:
        name: The name of the function.
        content: The content of the message.

    Returns:
        A dictionary representing a function result message.
    """
    return {
        'role': 'function',
        'content': content,
        'name': name,
    }


# Aliases
narrate = system
human = user
ai = assistant
