from spork import AutoUpdate

from ..components.function_details import ChatFunctionComponent

from ..registry import FunctionRegistry, FunctionArgumentError, UnknownFunctionError

from ..messaging import assistant_function_call, function_result
    
class ToolCalled(AutoUpdate):
    """Once a tool has finished up, this is the view."""
    id: str
    name: str
    arguments: str = ""
    verbage: str = "Called"
    result: str = ""

    def render(self):
        return ChatFunctionComponent(
            name=self.name,
            verbage="ok",
            input=self.arguments,
            output=self.result
        )
    
    # TODO: This is only here for legacy function calling
    def get_function_called_message(self):
        return function_result(self.name, self.result)



class ToolArguments(AutoUpdate):
    id: str
    name: str
    arguments: str = ""
    verbage: str = "Receiving arguments for"
    finished: bool = False

    # TODO: This is only here for legacy function calling
    def get_function_message(self):
        return assistant_function_call(self.name, self.arguments)

    def render(self):
        return ChatFunctionComponent(
            name=self.name,
            verbage=self.verbage,
            input=self.arguments
        )
    
    def append_arguments(self, arguments: str):
        self.arguments += arguments
    
    def apply_result(self, result: str):
        """Replaces the existing display with a new one that shows the result of the tool being called."""
        return ToolCalled(
            id=self.id,
            name=self.name,
            arguments=self.arguments,
            result=result,
            display_id=self.display_id
        )
    
    async def call(self, function_registry: FunctionRegistry) -> ToolCalled:
        """Call the function and return a stack of messages for LLM and human consumption."""
        function_name = self.name
        function_args = self.arguments

        self.verbage = "Running"

        # Execute the function and get the result
        try:
            output = await function_registry.call(function_name, function_args)
        except FunctionArgumentError as e:
            self.finished = True
            self.verbage = "Errored"

            result = f"Function arguments for {function_name} were invalid: {repr(e)}"
            return self.apply_result(result)

        except UnknownFunctionError as e:
            self.finished = True
            self.verbage = "No function named"
            result = f"No function named {function_name} found in function registry: {repr(e)}"

            return self.apply_result(result)

        except Exception as e:
            # Check to see if the user has requested that the exception be exposed to LLM.
            # If not, then we just raise it and let the user handle it.
            chatlab_metadata = function_registry.get_chatlab_metadata(function_name)

            if not chatlab_metadata.expose_exception_to_llm:
                # Bubble up the exception to the user
                raise

            repr_llm = repr(e)

            self.finished = True
            self.verbage = "Errored"

            result = repr_llm

            return self.apply_result(result)

        repr_llm = ""
        if isinstance(output, str):
            repr_llm = output
        elif getattr(output, "_repr_llm_", None) is not None:
            repr_llm = output._repr_llm_()
        else:
            repr_llm = repr(output)

        self.finished = True
        self.verbage = "Ran"

        return self.apply_result(repr_llm)

