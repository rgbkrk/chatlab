# flake8: noqa
import pytest

from chatlab.views import AssistantMessageView, ToolArguments


def test_assistant_message_view_creation():
    amv = AssistantMessageView()
    assert isinstance(amv, AssistantMessageView)


def test_assistant_message_get():
    amv = AssistantMessageView()
    amv.append("test")
    message = amv.get_message()

    assert message == {
        "role": "assistant",
        "content": "test",
    }


def test_assistant_function_call_view_creation():
    afcv = ToolArguments(id="eh", name="compute_pi")


def test_assistant_function_call_view_get():
    afcv = ToolArguments(id="eh", name="compute_pi")
    afcv.append_arguments("you can do it")
    message = afcv.get_function_message()

    assert message == {
        "role": "assistant",
        "content": None,
        "function_call": {
            "name": "compute_pi",
            "arguments": "you can do it",
        },
    }

    tool_result = afcv.apply_result("3.14159")

    assert tool_result.model_dump() == {
        "id": "eh",
        "name": "compute_pi",
        "arguments": "you can do it",
        "result": "3.14159",
        "verbage": "Called",
        "custom_render": None,
        "finished": True
    }

