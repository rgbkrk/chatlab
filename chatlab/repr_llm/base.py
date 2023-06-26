"""Base class for Large Language Model Consumption of Rich Displays."""


class LLMPlain:
    """A plain text representation of an object for Large Language Model Consumption."""

    def __init__(self, content):
        """Create a new LLMPlain object.

        Args:
            content (str): The content to be displayed. Make use of the fact
            that large language models can understand fairly compact text while
            also only being able to accept a limited number of tokens.

        Returns:
            A new LLMPlain object.
        """
        self.content = content

    def _repr_llm_(self):
        return self.content

    def __repr__(self):
        """Return a string representation of the object."""
        return f"LLMPlain({self.content})"

    def _repr_mimebundle_(self, include=None, exclude=None):
        return {'text/llm+plain': self.content}, {}
