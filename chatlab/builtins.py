"""Builtins for ChatLab."""
from typing import Optional

from IPython.core.formatters import DisplayFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output


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
        'text/vnd.plotly.v1+html',
        'application/javascript',
        'text/latex',
        'text/html',
        'text/markdown',
        'image/svg+xml',
        'text/plain',
    ]

    def format(self, obj, include=None, exclude=None):
        if hasattr(obj, '_repr_llm_'):
            return obj._repr_llm_(), {}

        formats = super().format(obj, include, exclude)

        richest_format = self._find_richest_format(formats)

        if richest_format:
            data, metadata = formats.pop(richest_format)
            richest_data = self._extract_richest_data(data)
            return richest_data, metadata

        return None, {}

    def _find_richest_format(self, formats):
        for format in self.richest_formats:
            if format in formats:
                return format

        return None

    def _extract_richest_data(self, data):
        for format in self.richest_formats:
            richest_data = data.get(format)
            if richest_data:
                if format == 'application/json':
                    return json.dumps(richest_data, indent=2)
                return richest_data

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

        self.display_formatter = LLMDisplayFormatter()

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
