from typing import Callable, Optional
from pydantic import ValidationError
from spork import AutoUpdate

import warnings

from ..components.function_details import ChatFunctionComponent

from ..registry import FunctionRegistry, FunctionArgumentError, UnknownFunctionError, extract_model_from_function

from ..messaging import assistant_function_call, function_result, tool_result

from openai.types.chat import ChatCompletionMessageToolCallParam

from IPython.display import display
from IPython.core.getipython import get_ipython

from instructor.dsl.partialjson import JSONParser



class ToolArguments(AutoUpdate):
    id: str
    name: str
    arguments: str = ""
    verbage: str = "Receiving arguments for"
    finished: bool = False

    custom_render: Optional[Callable] = None

    # TODO: This is only here for legacy function calling
    def get_function_message(self):
        return assistant_function_call(self.name, self.arguments)

    def get_tool_arguments_parameter(self) -> ChatCompletionMessageToolCallParam:
        return {"id": self.id, "function": {"name": self.name, "arguments": self.arguments}, "type": "function"}

    def format_as_raw(self):
        ip = get_ipython()

        if ip is None or ip.display_formatter is None:
            return

        rendered = self.render()

        if rendered is None:
            return

        data, metadata = ip.display_formatter.format(rendered)  # type: ignore
        return data

    def display(self) -> None:
        raw_format = self.format_as_raw()

        if raw_format is None:
            display(None, display_id=self.display_id)
            return

        # First display will always display the raw format
        display(raw_format, raw=True, display_id=self.display_id)

    def update(self) -> None:
        """
        Update the display with the current state of the object.

        This method is intended to be called after modifications to the object
        to refresh the display in the notebook environment.
        """
        raw_format = self.format_as_raw()

        if raw_format is None:
            return

        display(raw_format, raw=True, update=True, display_id=self.display_id)

    def render(self):
        if self.custom_render is not None:
            # We use the same definition as was in the original function
            try:
                parser = JSONParser()
                possible_args = parser.parse(self.arguments)

                Model = extract_model_from_function(self.name, self.custom_render)
                # model = Model.model_validate(possible_args)
                model = Model(**possible_args)

                # Pluck the kwargs out from the crafted model, as we can't pass the pydantic model as the arguments
                # However any "inner" models should retain their pydantic Model nature
                kwargs = {k: getattr(model, k) for k in model.__dict__.keys()}

            except FunctionArgumentError:
                return None
            except ValidationError:
                return None

            try:
                return self.custom_render(**kwargs)
            except Exception as e:
                # Exception in userland code
                # Would be preferable to bubble up, however
                # it might be due to us passing a not-quite model
                warnings.warn_explicit(f"Exception in userland code: {e}", UserWarning, "chatlab", 0)
                raise

        return ChatFunctionComponent(name=self.name, verbage=self.verbage, input=self.arguments)

    def append_arguments(self, arguments: str):
        self.arguments += arguments

    def apply_result(self, result: str):
        """Replaces the existing display with a new one that shows the result of the tool being called."""
        tc = ToolCalled(
            id=self.id, name=self.name, arguments=self.arguments, result=result, display_id=self.display_id,
            custom_render=self.custom_render
        )
        tc.update()
        return tc

    async def call(self, function_registry: FunctionRegistry) -> 'ToolCalled':
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

            if chatlab_metadata.bubble_exceptions:
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


class ToolCalled(ToolArguments):
    """Once a tool has finished up, this is the view."""

    id: str
    name: str
    arguments: str = ""
    verbage: str = "Called"
    result: str = ""
    finished: bool = True

    def render(self):
        if self.custom_render is not None:
            # We use the same definition as was in the original function
            try:
                parser = JSONParser()
                possible_args = parser.parse(self.arguments)

                Model = extract_model_from_function(self.name, self.custom_render)
                # model = Model.model_validate(possible_args)
                model = Model(**possible_args)

                # Pluck the kwargs out from the crafted model, as we can't pass the pydantic model as the arguments
                # However any "inner" models should retain their pydantic Model nature
                kwargs = {k: getattr(model, k) for k in model.__dict__.keys()}

            except FunctionArgumentError:
                return None
            except ValidationError:
                return None

            try:
                return self.custom_render(**kwargs)
            except Exception as e:
                # Exception in userland code
                # Would be preferable to bubble up, however
                # it might be due to us passing a not-quite model
                warnings.warn_explicit(f"Exception in userland code: {e}", UserWarning, "chatlab", 0)
                raise

        return ChatFunctionComponent(name=self.name, verbage=self.verbage, input=self.arguments, output=self.result)

    # TODO: This is only here for legacy function calling
    def get_function_called_message(self):
        return function_result(self.name, self.result)

    def get_tool_called_message(self):
        # NOTE: OpenAI has mismatched types where it doesn't include the `name`
        # xref: https://github.com/openai/openai-python/issues/1078
        return tool_result(tool_call_id=self.id, content=self.result, name=self.name)
