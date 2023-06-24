"""Builtins for ChatLab."""
from IPython.core.getipython import get_ipython


def run_cell(code: str):
    """Run Python code in the IPython kernel.

    Sometimes the GPT Models hallucinate a function called `python`. This is a
    rudimentary implementation of that function relying on IPython.

    This could be further expanded to match what is in dangermode for an IPythonic combination
    of stdout, stderr, exceptions, and rich output.
    """
    ip = get_ipython()
    if ip is None:
        raise Exception("Could not get IPython instance")

    try:
        # Note: Any side effects, including display calls will end up in the notebook
        # We cannot use `silent=True` because then `output.result` will be `None`
        output = ip.run_cell(code)
        return output.result
    except Exception as e:
        # We want the exception to be returned to the LLM
        return e
