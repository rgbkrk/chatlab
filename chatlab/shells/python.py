"""Builtins for ChatLab."""
from typing import Any, Optional

from IPython.core.formatters import BaseFormatter, DisplayFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.display import display
from IPython.utils.capture import RichOutput, capture_output
from traitlets import ObjectName, Unicode

try:
    # Defer loading of numpy and pandas unless installed
    import numpy as np  # noqa: F401
    import pandas as pd

    from chatlab.repr_llm.pandas import summarize_dataframe, summarize_series

    PANDAS_INSTALLED = True
except ImportError:
    PANDAS_INSTALLED = False


def preprocess_pandas(output: Any) -> Any:
    """Create representations of known objects for Large Language Model consumption.

    Currently this handles only Pandas and Series.

    If the object is not a DataFrame or Series, return the object.
    """
    with pd.option_context('display.max_rows', 5, 'display.html.table_schema', False, 'display.max_columns', 20):
        if isinstance(output, pd.DataFrame):
            df = output
            num_columns = min(pd.options.display.max_columns, df.shape[1])
            num_rows = min(pd.options.display.max_rows, df.shape[0])
            return summarize_dataframe(df, sample_rows=num_rows, sample_columns=num_columns)
        elif isinstance(output, pd.Series):
            series = output
            num_rows = min(pd.options.display.max_rows, series.shape[0])
            return summarize_series(series, sample_size=num_rows)
        else:
            raise ValueError("Unknown type for preprocess_pandas")


class LLMFormatter(BaseFormatter):
    """A formatter for producing text content for LLMs.

    To define the callables that compute the LLM representation of your
    objects, define a :meth:`_repr_llm_` method or use the :meth:`for_type`
    or :meth:`for_type_by_name` methods to register functions that handle
    this.

    The return value of this formatter should be plaintext.
    """

    format_type = Unicode('text/llm+plain')  # type: ignore

    print_method = ObjectName('_repr_llm_')  # type: ignore


formats_for_llm = [
    # Repr LLM
    'text/llm+plain',
    # All the normal ones
    'application/vnd.jupyter.error+json',
    'application/vdom.v1+json',
    'application/json',
    'application/javascript',
    'text/latex',
    'text/html',
    'text/markdown',
    'image/svg+xml',
    'text/plain',
]

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

        # Allow the LLM to see that we displayed for the user
        data['text/llm+plain'] = f"[displayed {richest_format} inline for user]"


def pluck_richest_text(output: RichOutput):
    """Format an object as rich text."""
    data = output.data
    metadata = output.metadata

    richest_format = __find_richest_format(data, formats_for_llm)

    if richest_format:
        d = data.pop(richest_format, None)
        m = metadata.pop(richest_format, None)

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
    llm_formatter = LLMFormatter(parent=shell)

    shell.display_formatter.formatters[llm_formatter.format_type] = llm_formatter  # type: ignore

    llm_formatter.for_type_by_name('pandas.core.frame', 'DataFrame', preprocess_pandas)
    llm_formatter.for_type_by_name('pandas.core.series', 'Series', preprocess_pandas)


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

        outputs = []

        if captured.stdout is not None and captured.stdout.strip() != '':
            stdout = captured.stdout
            # Truncate stdout if it's too long
            if len(stdout) > 1000:
                stdout = stdout[:500] + '...[TRUNCATED]...' + stdout[-500:]

            outputs.append({'stdout': stdout})

        if captured.stderr is not None and captured.stderr.strip() != '':
            stderr = captured.stderr
            if len(stderr) > 1000:
                stdout = stderr[:500] + '...[TRUNCATED]...' + stderr[-500:]
            outputs.append({'stderr': stderr})

        if captured.outputs is not None:
            for output in captured.outputs:
                # If image/* are in the output, redisplay it
                # then include a text/plain version of the object, telling the llm
                # that the image is displayed for the user
                redisplay_superrich(output)

                # Now for text for the llm
                data, _ = pluck_richest_text(output)
                outputs.append(data)

        if result.result is not None:
            data, _ = pluck_richest_text(result.result)
            outputs.append({'result': data})

        return outputs
        return outputs
