# flake8: noqa
import pytest

from chatlab.views.assistant import AssistantMessageView
from chatlab.views.markdown import Markdown


def test_assistant_message_view_creation():
    amv = AssistantMessageView()
    assert isinstance(amv, AssistantMessageView)


def test_markdown_creation():
    md = Markdown()
    assert isinstance(md, Markdown)


def test_assistant_message_get():
    amv = AssistantMessageView()
    try:
        amv.append("test")
        message = amv.get_message()

        assert message == {
            "role": "assistant",
            "content": "test",
        }
    except Exception:
        pytest.fail("Method raised an exception unexpectedly!")


def test_markdown_methods():
    md = Markdown()
    try:
        md.append("test")
        assert md.content == "test"
        repr_md = repr(md)
        assert repr_md == "test"
    except Exception:
        pytest.fail("Method raised an exception unexpectedly!")
