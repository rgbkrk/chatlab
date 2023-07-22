# flake8: noqa
from unittest import mock
from unittest.mock import MagicMock, patch

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
def test_generate_function_schema_lambda():
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
async def test_function_registry_unknown_function():
    registry = FunctionRegistry()
    with pytest.raises(UnknownFunctionError, match="Function unknown is not registered"):
        await registry.call("unknown")


async def test_function_registry_function_argument_error():
    registry = FunctionRegistry()
    registry.register(simple_func, SimpleModel)
    with pytest.raises(
        FunctionArgumentError, match="Invalid Function call on simple_func. Arguments must be a valid JSON object"
    ):
        await registry.call("simple_func", arguments="not json")


async def test_function_registry_call():
    registry = FunctionRegistry()
    registry.register(simple_func, SimpleModel)
    result = await registry.call("simple_func", arguments='{"x": 1, "y": "str", "z": true}')
    assert result == "1, str, True"


# Testing for registry's register method with an invalid function
def test_function_registry_register_invalid_function():
    registry = FunctionRegistry()
    with pytest.raises(Exception, match="Lambdas cannot be registered. Use `def` instead."):
        registry.register(lambda x: x)


# Testing for registry's get method
def test_function_registry_get():
    registry = FunctionRegistry()
    registry.register(simple_func, SimpleModel)
    assert registry.get("simple_func") == simple_func


# Testing for registry's __contains__ method
def test_function_registry_contains():
    registry = FunctionRegistry()
    registry.register(simple_func, SimpleModel)
    assert "simple_func" in registry
    assert "unknown" not in registry


# Testing for registry's function_definitions property
def test_function_registry_function_definitions():
    registry = FunctionRegistry()
    registry.register(simple_func, SimpleModel)
    function_definitions = registry.function_definitions
    assert len(function_definitions) == 1
    assert function_definitions[0]["name"] == "simple_func"


# Test that we do not allow python hallucination when False
async def test_function_registry_call_python_hallucination_invalid():
    registry = FunctionRegistry(python_hallucination_function=None)
    with pytest.raises(Exception, match="Function python is not registered"):
        await registry.call("python", arguments='1 + 4')


async def test_ensure_python_hallucination_not_enabled_by_default():
    registry = FunctionRegistry()
    with pytest.raises(Exception, match="Function python is not registered"):
        await registry.call("python", arguments='123 + 456')


# Test the generate_function_schema for function with optional arguments
def test_generate_function_schema_optional_args():
    def func_with_optional_args(x: int, y: str, z: bool = False):
        '''A function with optional arguments'''
        return f"{x}, {y}, {z}"

    schema = generate_function_schema(func_with_optional_args)
    assert "z" in schema["parameters"]["properties"]
    assert "z" not in schema["parameters"]["required"]


# Test the generate_function_schema for function with no arguments
def test_generate_function_schema_no_args():
    def func_no_args():
        """A function with no arguments"""
        pass

    schema = generate_function_schema(func_no_args)
    assert schema["parameters"]["properties"] == {}
    assert schema["parameters"]["required"] == []


# Testing edge cases with call method
async def test_function_registry_call_edge_cases():
    registry = FunctionRegistry()
    with pytest.raises(UnknownFunctionError):
        await registry.call("totes_not_real", arguments='{"x": 1, "y": "str", "z": true}')

    with pytest.raises(UnknownFunctionError):
        registry.call(None)  # type: ignore
