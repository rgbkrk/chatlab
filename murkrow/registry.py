from typing import Callable, Type

import json

from pydantic import BaseModel


class FunctionRegistry:
    """Captures a function with schema both for sending to OpenAI and for
    executing locally"""

    __functions: dict[str, Callable]
    __schemas: dict[str, dict]

    def __init__(self):
        """Initialize a FunctionRegistry object."""
        self.__functions = {}
        self.__schemas = {}

    def register(self, function: Callable, parameters_model: "BaseModel"):
        """Register a function with a schema for sending to OpenAI."""
        doc = function.__doc__ or parameters_model.__doc__
        name = function.__name__

        if not name:
            raise Exception("Function must have a name")
        if name == "<lambda>":
            raise Exception("Lambda functions can only be used if their __name__ is set")
        if not doc:
            raise Exception("Function or parameter model must have a docstring")

        self.__functions[function.__name__] = function
        self.__schemas[function.__name__] = {
            "name": name,
            "description": doc,
            "parameters": parameters_model.schema(),
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
