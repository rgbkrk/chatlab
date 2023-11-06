"""Extracting Pydantic Data Models from OpenAI Chat Models."""
## Originally from https://github.com/jxnl/instructor/blob/main/instructor/function_calls.py
##
## Brought over because chatlab is on the new `openai` bindings and likely soon a different version of pydantic.
##


# MIT License
#
# Copyright (c) 2023 Jason Liu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from functools import wraps

from docstring_parser import parse
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, create_model


class OpenAISchema(BaseModel):
    """Augments a Pydantic model with OpenAI's schema for function calling.

    This class augments a Pydantic model with OpenAI's schema for function calling. The schema is generated from the
    model's signature and docstring. The schema can be used to validate the response from OpenAI's API and extract the
    function call.

    ## Usage

    ```python
    from instructor import OpenAISchema

    class User(OpenAISchema):
        name: str
        age: int

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "content": "Jason is 20 years old",
            "role": "user"
        }],
        functions=[User.openai_schema],
        function_call={"name": User.openai_schema["name"]},
    )

    user = User.from_response(completion)

    print(user.model_dump())
    ```
    ## Result

    ```
    {
        "name": "Jason Liu",
        "age": 20,
    }
    ```


    """

    @classmethod
    def openai_schema(cls):
        """Return the schema in the format of OpenAI's schema as jsonschema.

        Note:
            Its important to add a docstring to describe how to best use this class, it will be included in the
            description attribute and be part of the prompt.

        Returns:
            model_json_schema (dict): A dictionary in the format of OpenAI's schema as jsonschema
        """
        schema = cls.model_json_schema()
        docstring = parse(cls.__doc__ or "")
        parameters = {k: v for k, v in schema.items() if k not in ("title", "description")}
        for param in docstring.params:
            if (name := param.arg_name) in parameters["properties"] and (description := param.description):
                if "description" not in parameters["properties"][name]:
                    parameters["properties"][name]["description"] = description

        parameters["required"] = sorted(k for k, v in parameters["properties"].items() if "default" not in v)

        if "description" not in schema:
            if docstring.short_description:
                schema["description"] = docstring.short_description
            else:
                schema["description"] = (
                    f"Correctly extracted `{cls.__name__}` with all " f"the required parameters with correct types"
                )

        return {
            "name": schema["title"],
            "description": schema["description"],
            "parameters": parameters,
        }

    @classmethod
    def from_message(
        cls,
        message: ChatCompletionMessageParam,
        validation_context=None,
        strict: bool = False,
    ):
        """Execute the function from the response of an openai chat completion.

        Args:
            cls (OpenAISchema): An instance of the class

        Returns:
            None
        """
        assert "function_call" in message, "No function call detected"
        assert message["function_call"]["name"] == cls.openai_schema()["name"], "Function name does not match"

        return cls.model_validate_json(
            message["function_call"]["arguments"],
            context=validation_context,
            strict=strict,
        )


def openai_schema(cls) -> OpenAISchema:
    """Pull the OpenAISchema for a BaseModel."""
    if not issubclass(cls, BaseModel):
        raise TypeError("Class must be a subclass of pydantic.BaseModel")

    return wraps(cls, updated=())(
        create_model(
            cls.__name__,
            __base__=(cls, OpenAISchema),
        )
    )  # type: ignore
