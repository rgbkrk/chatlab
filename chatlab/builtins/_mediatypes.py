"""Media types for rich output for LLMs and in-notebook."""
import json
from typing import Optional

from IPython.display import display
from IPython.utils.capture import RichOutput

# Prioritized formats to show to large language models
formats_for_llm = [
    # Repr LLM is the richest text
    "text/llm+plain",
    # Assume that if we get markdown we know it's rich for an LLM
    "text/markdown",
    # Same with LaTeX
    "text/latex",
    # All the normal ones
    "application/vnd.jupyter.error+json",
    # 'application/vdom.v1+json',
    "application/json",
    # Since every object has a text/plain repr, even though the LLM would understand `text/plain` well,
    # bumping this priority up would override more rich media types we definitely want to show.
    "text/plain",
    # Both HTML and SVG should be conditional on size, considering many libraries
    # Will emit giant JavaScript blobs for interactivity
    # For now, we'll assume not to show these
    # 'text/html',
    # 'image/svg+xml',
]

# Prioritized formats to redisplay for the user, since we capture the output during execution
formats_to_redisplay = [
    "application/vnd.jupyter.widget-view+json",
    "application/vnd.dex.v1+json",
    "application/vnd.dataresource+json",
    "application/vnd.plotly.v1+json",
    "text/vnd.plotly.v1+html",
    "application/vdom.v1+json",
    "application/json",
    "application/javascript",
    "image/svg+xml",
    "image/png",
    "image/jpeg",
    "image/gif",
    "text/html",
    "image/svg+xml",
]


def redisplay_superrich(output: RichOutput):
    """Redisplay an image."""
    data = output.data
    metadata = output.metadata

    richest_format = find_richest_format(data, formats_to_redisplay)

    if richest_format:
        display(
            data,
            raw=True,
        )

        data.pop(richest_format, None)
        metadata.pop(richest_format, None)

        # Check to see if it already has a text/llm+plain representation
        if "text/llm+plain" in data:
            return

        if richest_format.startswith("image/"):
            # Allow the LLM to see that we displayed for the user
            data["text/llm+plain"] = data["text/plain"]
        else:
            data["text/llm+plain"] = f"<Displayed {richest_format}>"


def pluck_richest_text(output: RichOutput):
    """Format an object as rich text."""
    data = output.data
    metadata = output.metadata

    richest_format = find_richest_format(data, formats_for_llm)

    if richest_format:
        d = data.pop(richest_format, None)
        m = metadata.pop(richest_format, None)

        if isinstance(d, dict):
            d = json.dumps(d, indent=2)

        # TODO: Reduce the size of the data if it's too big for LLMs.
        return d, m

    return None, {}


def find_richest_format(payload: dict, formats: list[str]) -> Optional[str]:
    for format in formats:
        if format in payload:
            return format

    return None
