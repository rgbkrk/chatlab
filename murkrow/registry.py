from typing import Callable, Type

import json

from pydantic import BaseModel


def create_function_schema(function, parameters_model) -> dict:
    return {
        "name": function.__name__,
        "description": function.__doc__,
        "parameters": parameters_model.schema(),
    }


class FunctionRegistry:
    """Captures a function with schema both for sending to OpenAI and for
    executing locally"""

    __functions: dict[str, Callable]
    __schemas: dict[str, dict]

    def __init__(self):
        self.__functions = {}
        self.__schemas = {}

    def register(self, function: Callable, parameters_model: "BaseModel"):
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
        return self.__functions[function_name]

    def call(self, function_call):
        function = self.get(function_call.name)
        parameters = json.loads(function_call.arguments)
        return function(**parameters)

    @property
    def function_definitions(self) -> list[dict]:
        return list(self.__schemas.values())
