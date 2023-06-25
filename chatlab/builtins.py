"""Builtins for ChatLab."""
import json
from typing import Optional

from IPython.core.formatters import BaseFormatter, DisplayFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from traitlets import ObjectName, Unicode


class LLMFormatter(BaseFormatter):
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
        'application/vdom.v1+json',
        'application/json',
        # 'text/vnd.plotly.v1+html',
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

        # Register the LLM formatter
        # self.formatters.set('text/llm+plain', LLMFormatter(parent=self))

    def format(self, obj, include=None, exclude=None):
        """Format an object as rich text."""
        data, metadata = super().format(obj, include, exclude)

        richest_format = self._find_richest_format(data)

        if richest_format:
            d = data.pop(richest_format, None)
            m = metadata.pop(richest_format, None)

            return d, m

        return "no rich", {}

    def _find_richest_format(self, formats):
        for format in self.richest_formats:
            if format in formats:
                return format

        return None


class ChatLabShell:
    """A custom shell for ChatLab that uses the current IPython shell and formats outputs for LLMs."""

    shell: InteractiveShell
    display_formatter: DisplayFormatter

    def __init__(self, shell: Optional[InteractiveShell] = None):
        """Create a new ChatLabShell."""
        # This is what `get_ipython` does. For type inference to work, we need to
        # do it manually.
        if InteractiveShell.initialized():
            shell = InteractiveShell.instance()

        if not shell:
            shell = InteractiveShell()

        self.shell = shell

        self.display_formatter = LLMDisplayFormatter(parent=self.shell)

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
                        data, metadata = self.display_formatter.format(output)
                        outputs.append({'data': data, 'metadata': metadata})

                if result.result is not None:
                    outputs.append({'result': self.display_formatter.format(result.result)})

                return outputs

        except Exception as e:
            return e


run_cell = ChatLabShell().run_cell
