"""Builtins for ChatLab."""

from deprecation import deprecated

from .files import chat_functions as file_functions
from .python import get_python_docs, run_python
from .shell import chat_functions as shell_functions

# To prevent naming confusion, the builtin that isn't really running a cell
# is deprecated.
run_cell = deprecated(
    deprecated_in="1.0.0",
    removed_in="2.0.0",
    details="run_cell is deprecated. Use run_python instead for same-session execution.",
)(run_python)

# compose all the file, shell, and python functions into one list for ease of use
os_functions = file_functions + shell_functions + [run_python, get_python_docs]

__all__ = [
    "run_python",
    "get_python_docs",
    "run_cell",
    "file_functions",
    "shell_functions",
    "os_functions",
]
