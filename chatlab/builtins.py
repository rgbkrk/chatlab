"""Builtins for ChatLab."""
from typing import Optional

from .shells.python import ChatLabShell

__shell: Optional[ChatLabShell] = None


def run_cell(code: str):
    """Execute code in python and return the result."""
    global __shell

    if __shell is None:
        from chatlab.shells.python import ChatLabShell

        __shell = ChatLabShell()

    return __shell.run_cell(code)
