"""Builtins for ChatLab."""
from typing import Optional

from IPython.core.formatters import DisplayFormatter, PlainTextFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from traitlets import ObjectName, Unicode

try:
    import numpy as np
    import pandas as pd

    PANDAS_INSTALLED = True
except ImportError:
    PANDAS_INSTALLED = False


# TODO: Figure out how to register this as a formatter for LLM consumers.
class LLMFormatter(PlainTextFormatter):
    """A formatter for producing text content for LLMs.

    To define the callables that compute the LLM representation of your
    objects, define a :meth:`_repr_llm_` method or use the :meth:`for_type`
    or :meth:`for_type_by_name` methods to register functions that handle
    this.

    The return value of this formatter should be plaintext.
    """

    format_type = Unicode('text/llm+plain')  # type: ignore

    print_method = ObjectName('_repr_markdown_')  # type: ignore


class LLMDisplayFormatter(DisplayFormatter):
    """A custom display formatter to create tailored outputs for LLMs."""

    richest_formats = [
        'text/llm+plain',
        'application/vnd.dex.v1+json',
        'application/vnd.jupyter.widget-view+json',
        'application/vnd.jupyter.error+json',
        'application/vnd.dataresource+json',
        'application/vnd.plotly.v1+json',
        # Too big for LLMs.
        # 'text/vnd.plotly.v1+html',
        'application/vdom.v1+json',
        'application/json',
        'application/javascript',
        'text/latex',
        'text/html',
        'text/markdown',
        'image/svg+xml',
        'text/plain',
    ]

    def __init__(self, *args, **kwargs):
        """Create a new LLMDisplayFormatter."""
        super().__init__(*args, **kwargs)

        self.active_types = self.richest_formats
        self.format_types.append("text/llm+plain")
        # No idea how to set this in traitlets to pick up the formatter for _repr_llm_.
        # self.formatters["text/llm+plain"] = LLMFormatter(parent=self.shell)

    def format(self, obj, include=None, exclude=None):
        """Format an object as rich text."""
        if hasattr(obj, '_repr_llm_'):
            return obj._repr_llm_(), {}

        # TODO: If the object is a pandas DataFrame or Series, use the to_markdown
        #       method to get a markdown representation of the object. We can pluck
        #       this from genai's code. This will be a lot more useful than the
        #       default html repr or even the data explorer (dataresource+json).
        data, metadata = super().format(obj, include, exclude)

        richest_format = self._find_richest_format(data)

        if richest_format:
            d = data.pop(richest_format, None)
            m = metadata.pop(richest_format, None)

            return d, m

        return None, {}

    def _find_richest_format(self, formats):
        for format in self.richest_formats:
            if format in formats:
                return format

        return None


def get_or_create_ipython() -> InteractiveShell:
    """Get the current IPython shell or create a new one."""
    shell = None
    # This is what `get_ipython` does. For type inference to work, we need to
    # do it manually.
    if InteractiveShell.initialized():
        shell = InteractiveShell.instance()

    if not shell:
        shell = InteractiveShell()

    return shell


class ChatLabShell:
    """A custom shell for ChatLab that uses the current IPython shell and formats outputs for LLMs."""

    shell: InteractiveShell
    display_formatter: DisplayFormatter

    def __init__(self, shell: Optional[InteractiveShell] = None):
        """Create a new ChatLabShell."""
        self.shell = get_or_create_ipython()

        self.display_formatter = LLMDisplayFormatter(parent=self.shell)
        # self.shell.display_formatter.formatters.set('text/llm+plain', LLMFormatter(parent=self.shell))

        # = self.display_formatter.format_types[
        #     'text/llm+plain'
        # ]

    def run_cell(self, code: str):
        """Execute code in python and return the result."""
        try:
            with capture_output() as captured:
                result = self.shell.run_cell(code)

                if not result.success:
                    return str(result.error_in_exec)

                outputs = []

                if captured.stdout is not None and captured.stdout.strip() != '':
                    outputs.append({'stdout': captured.stdout})

                if captured.stderr is not None and captured.stderr.strip() != '':
                    outputs.append({'stderr': captured.stderr})

                if captured.outputs is not None:
                    for output in captured.outputs:
                        # Dropping metadata and only showing that richest type
                        data, _ = self.display_formatter.format(output)
                        outputs.append(data)

                if result.result is not None:
                    outputs.append({'result': self.display_formatter.format(result.result)})

                return {'outputs': outputs}

        except Exception as e:
            return e
