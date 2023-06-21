"""Registry of functions for use by ChatCompletions.

Example usage:

    from murkrow import FunctionRegistry
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

    
    import murkrow
    registry = murkrow.FunctionRegistry()

    session = murkrow.Session(
        function_registry=registry,
    )

    session.chat("What time is it?")

"""

import inspect
from typing import Callable, Optional

from pydantic import BaseModel

# Allowed types for auto-inferred schemas
ALLOWED_TYPES = [int, str, bool, float, list, dict]


class FunctionRegistry:
    """Captures a function with schema both for sending to OpenAI and for executing locally."""

    __functions: dict[str, Callable]
    __schemas: dict[str, dict]

    def __init__(self):
        """Initialize a FunctionRegistry object."""
        self.__functions = {}
        self.__schemas = {}

    def register(
        self, function: Callable, parameters_model: Optional["BaseModel"] = None, json_schema: Optional[dict] = None
    ):
        """Register a function with a schema for sending to OpenAI."""
        doc = function.__doc__ or parameters_model.__doc__ if parameters_model else None
        name = function.__name__

        if not name:
            raise Exception("Function must have a name")
        if name == "<lambda>":
            raise Exception("Lambda functions can only be used if their __name__ is set")
        if not doc:
            raise Exception("Function or parameter model must have a docstring")

        self.__functions[function.__name__] = function

        if json_schema:
            schema = json_schema
        elif parameters_model:
            schema = parameters_model.schema()
        else:
            sig = inspect.signature(function)
            for name, param in sig.parameters.items():
                if param.annotation == inspect.Parameter.empty:
                    raise Exception(f"Parameter {name} of function {function.__name__} must have a type annotation")
                elif param.annotation not in ALLOWED_TYPES:
                    raise Exception(
                        f"Type annotation of parameter {name} in function {function.__name__} must"
                        f" be a JSON serializable type ({ALLOWED_TYPES})"
                    )
            schema = {
                "type": "object",
                "properties": {
                    name: {"type": str(param.annotation.__name__)} for name, param in sig.parameters.items()
                },
                "required": [
                    name for name, param in sig.parameters.items() if param.default == inspect.Parameter.empty
                ],
            }

        self.__schemas[function.__name__] = {
            "name": name,
            "description": doc,
            "parameters": schema,
        }

    def get(self, function_name):
        """Get a function by name."""
        return self.__functions[function_name]

    def call(self, name, arguments):
        """Call a function by name with the given parameters."""
        function = self.get(name)
        parameters = arguments
        return function(**parameters)

    def __contains__(self, name):
        """Check if a function is registered by name."""
        return name in self.__functions

    @property
    def function_definitions(self) -> list[dict]:
        """Get a list of function definitions."""
        return list(self.__schemas.values())
