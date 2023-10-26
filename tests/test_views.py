# flake8: noqa
import pytest

from chatlab.views.argument_buffer import ArgumentBuffer
from chatlab.views.assistant import AssistantMessageView
from chatlab.views.assistant_function_call import AssistantFunctionCallView
from chatlab.views.markdown import Markdown


def test_assistant_message_view_creation():
    amv = AssistantMessageView()
    assert isinstance(amv, AssistantMessageView)


def test_markdown_creation():
    md = Markdown()
    assert isinstance(md, Markdown)


def test_assistant_message_get():
    amv = AssistantMessageView()
    amv.append("test")
    message = amv.get_message()

    assert message == {
        "role": "assistant",
        "content": "test",
    }


def test_assistant_message_flush():
    amv = AssistantMessageView()
    amv.append("test")
    message = amv.flush()
    assert amv.content == ""
    assert message == {
        "role": "assistant",
        "content": "test",
    }


def test_assistant_function_call_view_creation():
    afcv = AssistantFunctionCallView("compute_pi")
    assert isinstance(afcv, AssistantFunctionCallView)


def test_assistant_function_call_view_get():
    afcv = AssistantFunctionCallView("compute_pi")
    afcv.append("you can do it")
    message = afcv.get_message()

    assert message == {
        "role": "assistant",
        "content": None,
        "function_call": {
            "name": "compute_pi",
            "arguments": "you can do it",
        },
    }

    assert afcv.finalize() == {
        "function_name": "compute_pi",
        "function_arguments": "you can do it",
        "display_id": afcv.buffer._display_id,
    }


def test_argument_buffer_initialization():
    # Initializing the ArgumentBuffer object
    arg_buffer = ArgumentBuffer("fun")

    assert arg_buffer.content == ""

    arg_buffer.append("woo")
    arg_buffer.append("who")
    assert arg_buffer.content == "woowho"

    arg_buffer._repr_mimebundle_()


def test_markdown_methods():
    md = Markdown()

    md.append("test")
    assert md.content == "test"
    repr_md = repr(md)
    assert repr_md == "test"

    assert md.message == "test"
    md.message = "well alright"

    assert md.content == "well alright"

    md2 = Markdown()
    data, metadata = md2._repr_markdown_()

    assert data == " "


def test_assistant_message_view_flush():
    amv = AssistantMessageView("wahoo")
    amv.append("test")
    amv.flush()
    assert amv.content == ""


def test_assistant_message_view_ipython_display():
    amv = AssistantMessageView()
    amv._ipython_display_()
    assert amv.active


def test_markdown_metadata():
    md = Markdown()
    assert md.metadata == {"chatlab": {"default": True}}
