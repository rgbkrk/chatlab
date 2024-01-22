import asyncio
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall, Function
from openai.types.chat.chat_completion_chunk import (
    ChoiceDeltaToolCall,
)

from openai.types.chat import ChatCompletionToolMessageParam

from pydantic import BaseModel

from typing import Dict, List

from chatlab.registry import FunctionRegistry

# We need to build a model that will recieve updates to tool_calls (from a a collection of deltas or the whole thing)


class ToolCallBuilder(BaseModel):
    # Assuming that we might not get all the tool calls at once, we need to build a model that will recieve updates to tool_calls (from a a collection of deltas or the whole thing)
    # TODO: Declare this as a partial of ChatCompletionMessageToolCall
    tool_calls: Dict[int, ChoiceDeltaToolCall] = {}

    def update(self, *tool_calls: ChoiceDeltaToolCall):
        for tool_call in tool_calls:
            in_progress_call = self.tool_calls.get(tool_call.index)

            if in_progress_call:
                in_progress_call.function.arguments += tool_call.function.arguments
            else:
                self.tool_calls[tool_call.index] = tool_call.model_copy()

    def finalize(self) -> List[ChatCompletionMessageToolCall]:
        return [
            ChatCompletionMessageToolCall(
                id=tool_call.id,
                function=Function(name=tool_call.function.name, arguments=tool_call.function.arguments),
                type=tool_call.type,
            )
            for tool_call in self.tool_calls.values()
        ]

    async def run(self, function_registry: FunctionRegistry):
        tool_calls = self.finalize()

        tasks: List[asyncio.Future[ChatCompletionToolMessageParam]] = [
            function_registry.run_tool(tool) for tool in tool_calls
        ]

        for future in asyncio.as_completed(tasks):
            response = await future
            yield response
