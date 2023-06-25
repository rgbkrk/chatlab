"""ChatLab annotations for functions."""


class ChatlabMetadata:
    """ChatLab metadata for a function."""

    expose_exception_to_llm: bool

    def __init__(self, expose_exception_to_llm=False):
        """Initialize ChatLab metadata for a function."""
        self.expose_exception_to_llm = expose_exception_to_llm


def expose_exception_to_llm(func):
    """Expose exceptions from calling the function to the LLM.

    Args:
        func (Callable): The function to annotate.

    Examples:
        >>> import chatlab
        >>> from chatlab.decorators import expose_exception_to_llm

        >>> @expose_exception_to_llm
        ... def roll_die():
        ...     roll = random.randint(1, 6)
        ...     if roll == 1:
        ...         raise Exception("The die rolled a 1!")
        ...     return roll
        >>> conversation = chatlab.Conversation()
        >>> conversation.submit("Roll the dice!")
        The die rolled a 1!

    """
    if not hasattr(func, 'chatlab_metadata'):
        func.chatlab_metadata = ChatlabMetadata()

    # Make sure that chatlab_metadata is an instance of ChatlabMetadata
    if not isinstance(func.chatlab_metadata, ChatlabMetadata):
        raise Exception("func.chatlab_metadata must be an instance of ChatlabMetadata")

    func.chatlab_metadata.expose_exception_to_llm = True
    return func
