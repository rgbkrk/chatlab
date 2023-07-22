"""Registry of functions for use by ChatCompletions.

Example usage:

    from chatlab import FunctionRegistry
    from pydantic import BaseModel

    registry = FunctionRegistry()

    class Parameters(BaseModel):
        name: str

    from datetime import datetime
    from pytz import timezone, all_timezones, utc
    from typing import Optional
    from pydantic import BaseModel

    def what_time(tz: Optional[str] = None):
        '''Current time, defaulting to the user's current timezone'''
        if tz is None:
            pass
        elif tz in all_timezones:
            tz = timezone(tz)
        else:
            return 'Invalid timezone'
        return datetime.now(tz).strftime('%I:%M %p')

    class WhatTime(BaseModel):
        timezone: Optional[str]

    import chatlab
    registry = chatlab.FunctionRegistry()

    conversation = chatlab.Chat(
        function_registry=registry,
    )

    conversation.submit("What time is it?")

"""

import asyncio
import inspect
import json
from typing import Any, Callable, Optional, Type, Union, get_args, get_origin

from pydantic import BaseModel

from .decorators import ChatlabMetadata


class FunctionArgumentError(Exception):
    """Exception raised when a function is called with invalid arguments."""

    pass


class UnknownFunctionError(Exception):
    """Exception raised when a function is called that is not registered."""

    pass


# Allowed types for auto-inferred schemas
ALLOWED_TYPES = [int, str, bool, float, list, dict]

JSON_SCHEMA_TYPES = {
    int: 'integer',
    float: 'number',
    str: 'string',
    bool: 'boolean',
    list: 'array',
    dict: 'object',
}


def is_optional_type(t):
    """Check if a type is Optional."""
    return get_origin(t) is Union and len(get_args(t)) == 2 and type(None) in get_args(t)


def generate_function_schema(
    function: Callable,
    parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None,
):
    """Generate a function schema for sending to OpenAI."""
    doc = function.__doc__
    func_name = function.__name__

    if not func_name:
        raise Exception("Function must have a name")
    if func_name == "<lambda>":
        raise Exception("Lambdas cannot be registered. Use `def` instead.")
    if not doc:
        raise Exception("Only functions with docstrings can be registered")

    schema = None
    if isinstance(parameter_schema, dict):
        schema = parameter_schema
    elif parameter_schema is not None:
        schema = parameter_schema.schema()
    else:
        schema_properties = {}
        sig = inspect.signature(function)
        for name, param in sig.parameters.items():
            if param.annotation == inspect.Parameter.empty:
                raise Exception(f"Parameter {name} of function {func_name} must have a type annotation")

            if is_optional_type(param.annotation):
                actual_type = get_args(param.annotation)[0]

                if actual_type not in ALLOWED_TYPES:
                    raise Exception(
                        f"Type annotation of parameter {name} in function {func_name} "
                        f"must be a JSON serializable type ({ALLOWED_TYPES})"
                    )

                schema_properties[name] = {
                    "type": JSON_SCHEMA_TYPES[actual_type],
                }

            elif param.annotation in ALLOWED_TYPES:
                schema_properties[name] = {
                    "type": JSON_SCHEMA_TYPES[param.annotation],
                }

            else:
                raise Exception(
                    f"Type annotation of parameter {name} in function {func_name} "
                    f"must be a JSON serializable type ({ALLOWED_TYPES})"
                )

        schema = {"type": "object", "properties": {}, "required": []}
        if len(schema_properties) > 0:
            schema = {
                "type": "object",
                "properties": schema_properties,
                "required": [
                    name
                    for name, param in sig.parameters.items()
                    if param.default == inspect.Parameter.empty and param.annotation != Optional
                ],
            }

    if schema is None:
        raise Exception(f"Could not generate schema for function {func_name}")

    return {
        "name": func_name,
        "description": doc,
        "parameters": schema,
    }


# Declare the type for the python hallucination
PythonHallucinationFunction = Callable[[str], Any]


class FunctionRegistry:
    """Captures a function with schema both for sending to OpenAI and for executing locally."""

    __functions: dict[str, Callable]
    __schemas: dict[str, dict]

    # Allow passing in a callable that accepts a single string for the python
    # hallucination function. This is useful for testing.
    def __init__(self, python_hallucination_function: Optional[PythonHallucinationFunction] = None):
        """Initialize a FunctionRegistry object."""
        self.__functions = {}
        self.__schemas = {}

        self.python_hallucination_function = python_hallucination_function

    def register(
        self,
        function: Callable,
        parameter_schema: Optional[Union[Type["BaseModel"], dict]] = None,
    ) -> dict:
        """Register a function for use in `Chat`s."""
        final_schema = generate_function_schema(function, parameter_schema)

        self.__functions[function.__name__] = function
        self.__schemas[function.__name__] = final_schema

        return final_schema

    def get(self, function_name) -> Optional[Callable]:
        """Get a function by name."""
        if function_name == "python" and self.python_hallucination_function is not None:
            return self.python_hallucination_function

        return self.__functions.get(function_name)

    def get_chatlab_metadata(self, function_name) -> ChatlabMetadata:
        """Get the chatlab metadata for a function by name."""
        function = self.get(function_name)

        if function is None:
            raise UnknownFunctionError(f"Function {function_name} is not registered")

        chatlab_metadata = getattr(function, "chatlab_metadata", ChatlabMetadata())
        return chatlab_metadata

    async def call(self, name: str, arguments: Optional[str] = None) -> Any:
        """Call a function by name with the given parameters."""
        function = self.get(name)
        parameters: dict = {}

        # Handle the code interpreter hallucination
        if name == "python" and self.python_hallucination_function is not None:
            function = self.python_hallucination_function
            if arguments is None:
                arguments = ""

            # The "hallucinated" python function takes raw plaintext
            # instead of a JSON object. We can just pass it through.
            if asyncio.iscoroutinefunction(function):
                return await function(arguments)
            return function(arguments)
        elif function is None:
            raise UnknownFunctionError(f"Function {name} is not registered")
        elif arguments is None or arguments == "":
            parameters = {}
        else:
            try:
                parameters = json.loads(arguments)
                # TODO: Validate parameters against schema
            except json.JSONDecodeError:
                raise FunctionArgumentError(f"Invalid Function call on {name}. Arguments must be a valid JSON object")

        if function is None:
            raise UnknownFunctionError(f"Function {name} is not registered")

        if asyncio.iscoroutinefunction(function):
            result = await function(**parameters)
        else:
            result = function(**parameters)
        return result

    def __contains__(self, name) -> bool:
        """Check if a function is registered by name."""
        if name == "python" and self.python_hallucination_function:
            return True
        return name in self.__functions

    @property
    def function_definitions(self) -> list[dict]:
        """Get a list of function definitions."""
        return list(self.__schemas.values())
