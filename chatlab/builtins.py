"""Builtins for ChatLab."""
from typing import Any

from chatlab.decorators import expose_exception_to_llm

# __shell: Optional[ChatLabShell] = None

__shell: Any = None


@expose_exception_to_llm
def run_cell(code: str):
    """Execute code in python and return the result."""
    global __shell

    if __shell is None:
        # Since ChatLabShell has imports that are "costly" (e.g. IPython, numpy, pandas),
        # we only import it on the first call to run_cell.
        from .shells.python import ChatLabShell

        __shell = ChatLabShell()

    return __shell.run_cell(code)
