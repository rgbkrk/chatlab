# flake8: noqa
import pytest
from pydantic import BaseModel

from chatlab.registry import FunctionArgumentError, FunctionRegistry, UnknownFunctionError, generate_function_schema


# Define a function to use in testing
def simple_func(x: int, y: str, z: bool = False):
    """A simple test function"""
    return f"{x}, {y}, {z}"


class SimpleModel(BaseModel):
    x: int
    y: str
    z: bool = False


# Test the function generation schema
def test_generate_function_schema_no_args():
    with pytest.raises(Exception, match="Lambdas cannot be registered. Use `def` instead."):
        generate_function_schema(lambda x: x)


def test_generate_function_schema_no_docstring():
    def no_docstring(x: int):
        return x

    with pytest.raises(Exception, match="Only functions with docstrings can be registered"):
        generate_function_schema(no_docstring)


def test_generate_function_schema_no_type_annotation():
    def no_type_annotation(x):
        """Return back x"""
        return x

    with pytest.raises(Exception, match="Parameter x of function no_type_annotation must have a type annotation"):
        generate_function_schema(no_type_annotation)


def test_generate_function_schema_unallowed_type():
    def unallowed_type(x: set):
        '''Return back x'''
        return x

    with pytest.raises(
        Exception, match="Type annotation of parameter x in function unallowed_type must be a JSON serializable type"
    ):
        generate_function_schema(unallowed_type)


def test_generate_function_schema():
    schema = generate_function_schema(simple_func)
    expected_schema = {
        "name": "simple_func",
        "description": "A simple test function",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "string"},
                "z": {"type": "boolean"},
            },
            "required": ["x", "y"],
        },
    }
    assert schema == expected_schema


def test_generate_function_schema_with_model():
    schema = generate_function_schema(simple_func, SimpleModel)
    expected_schema = {
        "name": "simple_func",
        "description": "A simple test function",
        "parameters": SimpleModel.schema(),
    }
    assert schema == expected_schema


# Test the function registry
def test_function_registry_unknown_function():
    registry = FunctionRegistry()
    with pytest.raises(UnknownFunctionError, match="Function unknown is not registered"):
        registry.call("unknown")


def test_function_registry_function_argument_error():
    registry = FunctionRegistry()
    registry.register(simple_func, SimpleModel)
    with pytest.raises(FunctionArgumentError, match="Invalid JSON for parameters of function simple_func"):
        registry.call("simple_func", arguments="not json")


def test_function_registry_call():
    registry = FunctionRegistry()
    registry.register(simple_func, SimpleModel)
    result = registry.call("simple_func", arguments='{"x": 1, "y": "str", "z": true}')
    assert result == "1, str, True"
