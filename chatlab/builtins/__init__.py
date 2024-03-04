"""Simple tools for any LLM to use."""

from deprecation import deprecated

from ..tools import run_python, get_python_docs, file_functions, shell_functions

# TODO: Deprecate extra namespace
# compose all the file, shell, and python functions into one list for ease of use
os_functions = file_functions + shell_functions + [run_python, get_python_docs]

# To prevent naming confusion, the builtin that isn't really running a cell
# is deprecated.
run_cell = deprecated(
    deprecated_in="1.0.0",
    removed_in="2.0.0",
    details="run_cell is deprecated. Use run_python instead for same-session execution.",
)(run_python)


__all__ = [
    "run_python",
    "get_python_docs",
    "run_cell",
    "file_functions",
    "shell_functions",
    "os_functions",
]
