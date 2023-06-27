"""Builtins for ChatLab."""
import json
from typing import Optional

from IPython.core.formatters import DisplayFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.display import display
from IPython.utils.capture import RichOutput, capture_output
from repr_llm import register_llm_formatter
from repr_llm.pandas import format_dataframe_for_llm, format_series_for_llm

# Formats to show to large language models
formats_for_llm = [
    # Repr LLM is the richest text
    'text/llm+plain',
    # All the normal ones
    'application/vnd.jupyter.error+json',
    'application/vdom.v1+json',
    'application/json',
    'text/latex',
    'text/html',
    'text/markdown',
    'image/svg+xml',
    'text/plain',
]

# Formats to redisplay for the user, since we capture the output during execution
formats_to_redisplay = [
    'application/vnd.jupyter.widget-view+json',
    'application/vnd.dex.v1+json',
    'application/vnd.dataresource+json',
    'application/vnd.plotly.v1+json',
    'text/vnd.plotly.v1+html',
    'application/vdom.v1+json',
    'application/json',
    'application/javascript',
    'image/svg+xml',
    'image/png',
    'image/jpeg',
    'image/gif',
]


def redisplay_superrich(output: RichOutput):
    """Redisplay an image."""
    data = output.data
    metadata = output.metadata

    richest_format = __find_richest_format(data, formats_to_redisplay)

    if richest_format:
        display(
            data,
            raw=True,
        )

        data.pop(richest_format, None)
        metadata.pop(richest_format, None)

        # Check to see if it already has a text/llm+plain representation
        if 'text/llm+plain' in data:
            return

        if richest_format.startswith('image/'):
            # Allow the LLM to see that we displayed for the user
            data['text/llm+plain'] = data['text/plain']
        else:
            data['text/llm+plain'] = f"<Displayed {richest_format}>"


def pluck_richest_text(output: RichOutput):
    """Format an object as rich text."""
    data = output.data
    metadata = output.metadata

    richest_format = __find_richest_format(data, formats_for_llm)

    if richest_format:
        d = data.pop(richest_format, None)
        m = metadata.pop(richest_format, None)

        if isinstance(d, dict):
            d = json.dumps(d, indent=2)

        # TODO: Reduce the size of the data if it's too big for LLMs.
        return d, m

    return None, {}


def __find_richest_format(payload: dict, formats: list[str]) -> Optional[str]:
    for format in formats:
        if format in payload:
            return format

    return None


def apply_llm_formatter(shell: InteractiveShell):
    """Apply the LLM formatter to the given shell."""
    llm_formatter = register_llm_formatter(shell)

    llm_formatter.for_type_by_name('pandas.core.frame', 'DataFrame', format_dataframe_for_llm)
    llm_formatter.for_type_by_name('pandas.core.series', 'Series', format_series_for_llm)


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
    display_formatter: DisplayFormatter

    def __init__(self, shell: Optional[InteractiveShell] = None):
        """Create a new ChatLabShell."""
        self.shell = get_or_create_ipython()

    def run_cell(self, code: str):
        """Execute code in python and return the result."""
        try:
            with capture_output() as captured:
                result = self.shell.run_cell(code)
        except Exception as e:
            return e

        if not result.success:
            return result

        outputs = ""

        if captured.stdout is not None and captured.stdout.strip() != '':
            stdout = captured.stdout
            # Truncate stdout if it's too long
            if len(stdout) > 1000:
                stdout = stdout[:500] + '...[TRUNCATED]...' + stdout[-500:]

            outputs += f"STDOUT:\n{stdout}\n\n"

        if captured.stderr is not None and captured.stderr.strip() != '':
            stderr = captured.stderr
            if len(stderr) > 1000:
                stdout = stderr[:500] + '...[TRUNCATED]...' + stderr[-500:]
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
