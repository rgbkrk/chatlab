"""Builtins for ChatLab."""

from deprecation import deprecated

from .python import run_python

# To prevent naming confusion, the builtin that isn't really running a cell
# is deprecated.
run_cell = deprecated(
    deprecated_in="1.0.0",
    removed_in="2.0.0",
    details="run_cell is deprecated. Use run_python instead for same-session execution.",
)(run_python)


__all__ = ["run_python", "run_cell"]
