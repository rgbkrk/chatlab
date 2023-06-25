# flake8: noqa
import toml

# Casually import everything to shake out any import errors
from chatlab import *


def test_chatlab():
    from chatlab import __version__

    # Check that __version__ is the same as pyproject.toml's version
    pyproject_toml = toml.load("pyproject.toml")
    assert __version__ == pyproject_toml["tool"]["poetry"]["version"]
