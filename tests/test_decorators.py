# flake8: noqa
import pytest

from chatlab.decorators import ChatlabMetadata, expose_exception_to_llm


class MyException(Exception):
    pass


@expose_exception_to_llm
def raise_exception():
    """This function just raises an exception."""
    raise MyException("test exception")


def no_exception():
    """This function does not raise an exception."""
    return "No exception here!"


def test_expose_exception_to_llm_decorator():
    """Tests the expose_exception_to_llm decorator."""
    assert isinstance(raise_exception.chatlab_metadata, ChatlabMetadata)
    assert raise_exception.chatlab_metadata.expose_exception_to_llm == True


def test_no_decorator():
    """Tests a function without the decorator."""
    assert not hasattr(no_exception, 'chatlab_metadata')


def test_decorator_raises_exception():
    """Tests that the decorator raises an exception when chatlab_metadata is not an instance of ChatlabMetadata."""

    def func():
        pass

    func.chatlab_metadata = "Not an instance of ChatlabMetadata"

    with pytest.raises(Exception):
        expose_exception_to_llm(func)
