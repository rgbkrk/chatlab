"""The in-IPython python code runner for ChatLab."""
from traceback import TracebackException
from typing import Optional

from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from repr_llm import register_llm_formatter
from repr_llm.pandas import format_dataframe_for_llm, format_series_for_llm

from chatlab.decorators import expose_exception_to_llm

from ._mediatypes import pluck_richest_text, redisplay_superrich


def apply_llm_formatter(shell: InteractiveShell):
    """Apply the LLM formatter to the given shell."""
    llm_formatter = register_llm_formatter(shell)

    llm_formatter.for_type_by_name("pandas.core.frame", "DataFrame", format_dataframe_for_llm)
    llm_formatter.for_type_by_name("pandas.core.series", "Series", format_series_for_llm)


def get_or_create_ipython() -> InteractiveShell:
    """Get the current IPython shell or create a new one."""
    shell = None
    # This is what `get_ipython` does. For type inference to work, we need to
    # do it manually.
    if InteractiveShell.initialized():
        shell = InteractiveShell.instance()
        apply_llm_formatter(shell)

    if not shell:
        shell = InteractiveShell()
        apply_llm_formatter(shell)

    return shell


class ChatLabShell:
    """A custom shell for ChatLab that uses the current IPython shell and formats outputs for LLMs."""

    shell: InteractiveShell

    def __init__(self, shell: Optional[InteractiveShell] = None):
        """Create a new ChatLabShell."""
        self.shell = get_or_create_ipython()

    def run_cell(self, code: str):
        """Execute code in python and return the result."""
        try:
            # Since we include the traceback inside the ChatLab display, we
            # don't want to show it inline.
            # Sadly `capture_output` doesn't grab the show traceback side effect,
            # so we have to do it manually.
            original_showtraceback = self.shell.showtraceback
            with capture_output() as captured:
                # HACK: don't show the exception inline if the LLM is running it
                self.shell.showtraceback = lambda *args, **kwargs: None  # type: ignore
                result = self.shell.run_cell(code)
                self.shell.showtraceback = original_showtraceback  # type: ignore
        except Exception as e:
            self.shell.showtraceback = original_showtraceback  # type: ignore
            formatted = TracebackException.from_exception(e, limit=3).format(chain=True)
            plaintext_traceback = "\n".join(formatted)

            return plaintext_traceback

        if not result.success:
            # Grab which exception was raised
            exception = result.error_before_exec or result.error_in_exec

            # If success was False and yet neither of these are set, then
            # something went wrong in the IPython internals
            if exception is None:
                raise Exception("Unknown IPython error for result", result)

            # Create a formatted traceback that includes the last 3 frames
            # and the exception message
            formatted = TracebackException.from_exception(exception, limit=3).format(chain=True)
            plaintext_traceback = "\n".join(formatted)

            return plaintext_traceback

        outputs = ""

        if captured.stdout is not None and captured.stdout.strip() != "":
            stdout = captured.stdout
            # Truncate stdout if it's too long
            if len(stdout) > 1000:
                stdout = stdout[:500] + "...[TRUNCATED]..." + stdout[-500:]

            outputs += f"STDOUT:\n{stdout}\n\n"

        if captured.stderr is not None and captured.stderr.strip() != "":
            stderr = captured.stderr
            if len(stderr) > 1000:
                stdout = stderr[:500] + "...[TRUNCATED]..." + stderr[-500:]
            outputs += f"STDERR:\n{stderr}\n\n"

        if captured.outputs is not None:
            for output in captured.outputs:
                # If image/* are in the output, redisplay it
                # then include a text/plain version of the object, telling the llm
                # that the image is displayed for the user
                redisplay_superrich(output)

                # Now for text for the llm
                text, _ = pluck_richest_text(output)

                if text is None:
                    continue

                outputs += f"OUTPUT:\n{text}\n\n"

        if result.result is not None:
            output = result.result
            # If image/* are in the output, redisplay it
            # then include a text/plain version of the object, telling the llm
            # that the image is displayed for the user
            redisplay_superrich(result.result)

            # Now for text for the llm
            text, _ = pluck_richest_text(result.result)

            if text is not None:
                outputs += f"RESULT:\n{text}\n\n"

        return outputs


__shell: Optional[ChatLabShell] = None


@expose_exception_to_llm
def run_python(code: str):
    """Execute code in python and return the result."""
    global __shell

    if __shell is None:
        # Since ChatLabShell has imports that are "costly" (e.g. IPython, numpy, pandas),
        # we only import it on the first call to run_cell.
        from .python import ChatLabShell

        __shell = ChatLabShell()

    return __shell.run_cell(code)


@expose_exception_to_llm
def get_python_docs(module_name: str):
    """Read docs for a Python package."""
    import importlib
    import inspect

    package = importlib.import_module(module_name)
    return inspect.getdoc(package)


__all__ = ["run_python", "ChatLabShell"]


def __dir__():
    return __all__
