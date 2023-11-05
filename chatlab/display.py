"""Stylized representation of a Chat Function Call as we dance with the LLM."""

from typing import Optional

from openai.types.chat import ChatCompletionMessageParam

from .components.function_details import ChatFunctionComponent
from .messaging import function_result, system
from .registry import FunctionArgumentError, FunctionRegistry, UnknownFunctionError
from .views.abstracts import AutoDisplayer


class ChatFunctionCall(AutoDisplayer):
    """Operates like the Markdown class, but with the ChatFunctionComponent."""

    function_name: str
    function_args: Optional[str] = None
    function_result: Optional[str] = None
    state: str = "Generating"
    finished: bool = False

    def __init__(
        self,
        function_name: str,
        function_arguments: str,
        function_registry: FunctionRegistry,
        display_id: Optional[str] = None,
    ):
        """Initialize a `ChatFunctionCall` object with an optional message."""
        self.function_name = function_name
        self.function_registry = function_registry
        self.function_args = function_arguments

        if display_id is None:
            display_id = self.generate_display_id()

        self._display_id = display_id
        self.update_displays()

    async def call(self) -> ChatCompletionMessageParam:
        """Call the function and return a stack of messages for LLM and human consumption."""
        function_name = self.function_name
        function_args = self.function_args

        self.set_state("Running")

        # Execute the function and get the result
        try:
            output = await self.function_registry.call(function_name, function_args)
        except FunctionArgumentError as e:
            self.finished = True
            self.set_state("Errored")
            self.function_result = repr(e)
            return system(f"Function arguments for {function_name} were invalid: {e}")
        except UnknownFunctionError as e:
            self.finished = True
            self.set_state("No function named")
            self.function_result = repr(e)
            return system(f"Function {function_name} not found in function registry: {e}")
        except Exception as e:
            # Check to see if the user has requested that the exception be exposed to LLM.
            # If not, then we just raise it and let the user handle it.
            chatlab_metadata = self.function_registry.get_chatlab_metadata(function_name)

            if not chatlab_metadata.expose_exception_to_llm:
                # Bubble up the exception to the user
                raise

            repr_llm = repr(e)

            self.function_result = repr_llm
            self.finished = True
            self.state = "Errored"
            self.update_displays()

            return function_result(name=function_name, content=repr_llm)

        repr_llm = ""
        if isinstance(output, str):
            repr_llm = output
        elif getattr(output, "_repr_llm_", None) is not None:
            repr_llm = output._repr_llm_()
        else:
            repr_llm = repr(output)

        self.function_result = repr_llm
        self.finished = True
        self.state = "Ran"
        self.update_displays()

        return function_result(name=function_name, content=repr_llm)

    def set_state(self, state: str):
        """Set the state of the ChatFunctionCall."""
        self.state = state
        self.update_displays()

    def _repr_mimebundle_(self, include=None, exclude=None):
        vdom_component = ChatFunctionComponent(
            name=self.function_name,
            verbage=self.state,
            input=self.function_args,
            output=self.function_result,
            finished=self.finished,
        )
        return {
            "text/html": vdom_component.to_html(),
            # "application/vdom.v1+json": vdom_component.to_dict(),
        }
