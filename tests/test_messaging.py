#!/usr/bin/env python
"""Tests for `chatlab` package."""

from chatlab import assistant, system, user
from chatlab.messaging import assistant_function_call, function_result


def test_assistant():
    message = assistant("Hello!")
    assert message['role'] == 'assistant'
    assert message['content'] == 'Hello!'


def test_user():
    message = user("How are you?")
    assert message['role'] == 'user'
    assert message['content'] == 'How are you?'


def test_system():
    message = system("System message")
    assert message['role'] == 'system'
    assert message['content'] == 'System message'


def test_assistant_function_call():
    message = assistant_function_call("func_name", "arg")
    assert message['role'] == 'assistant'
    assert message['function_call']['name'] == 'func_name'
    assert message['function_call']['arguments'] == 'arg'


def test_function_result():
    message = function_result("func_name", "result")
    assert message['role'] == 'function'
    assert message['name'] == 'func_name'
    assert message['content'] == 'result'
