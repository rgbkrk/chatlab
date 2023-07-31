# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0-alpha.11]

### Added

-   📚 Documentation now available at [chatlab.dev](https://chatlab.dev)
-   📚 Pre-release Documentation now available at [pre.chatlab.dev](https://pre.chatlab.dev)
-   🎛️ New option `replace_hallucinated_python` to replace any hallucinated python function with a custom one. This allows you to create notebook cells, run IPython, or even shell out to a regular python interpreter.
-   🪄 Introduced `make_magic` on a `Chat` so that you can use a current chat as a cell magic in IPython and Jupyter notebooks
-   ⏩ Accept async functions as chat functions
-   📗 New experimental builtin: Noteable. Create notebooks on Noteable like you can via ChatGPT Plugins with even more flexibility.
-   🧩 Accept collections of functions to `Chat` and `FunctionRegistry` to register multiple functions at once

-   [Builtins] 📁 Chat File functions:

    -   `list_files`: List all files in a directory.
    -   `get_file_size`: Get the size of a file.
    -   `is_file`: Check if a path points to a file.
    -   `is_directory`: Check if a path points to a directory.
    -   `write_file`: Write content to a file.
    -   `read_file`: Read content from a file.

-   [Builtins] 🐚 Chat Shell Functions:

    -   `run_shell_command`: Run a shell command and return the output.

### Changed

-   🔄 `chatlab.Chat` is now `chatlab.Conversation` to improve readability
-   ⚠️ Deprecated `chatlab.Conversation`
-   🔄 `submit` is now an async function to allow registering functions
-   📜 Improved UI: Scrollbars for function inputs and outputs now only appear on the x-axis when content is too large
-   🛑🔙 Enhanced error handling: Python interpreter traceback is no longer displayed in the notebook when it is included in the ChatLab output pane.
-   🐍 The python builtin's name has been changed to `run_python`

### Deprecated

-   ⚠️ Both `chatlab.Session` and `chatlab.Conversation` are now deprecated in favor of `chatlab.Chat`

## [0.16.0]

### Changed

-   🐍🔙 Send a traceback to the LLM when an exception occurs in the builtin python interpreter

## [0.15.3]

### Changed

-   📦 Update description and classifiers for PyPI
-   ❌ Remove unused packages

## [0.15.2]

### Changed

-   📦 Include universal wheels in build

## [0.15.1]

### Changed

-   📦 Loosened the requirements for IPython and ipykernel to allow jupyterlite and pyodide to use this package

## [0.15.0]

### Changed

-   🐍 Greatly enhanced Python interpreter that displays images inline and provides a trimmed down representation of objects for Large Language Model Consumption, relying on [repr_llm](https://github.com/rgbkrk/repr_llm)

## [0.14.1]

### Fixed

-   One line in the changelog was off
-   Testing the release workflow

## [0.14.0]

### Added

-   🏷️ New `expose_exception_to_llm` decorator allows function exceptions to be exposed to the large language model. This is useful for when the model is running code via IPython's `run_cell` or any other interpreter where the model needs feedback on exceptions.

### Changed

-   🔄 Package name changed from `murkrow` to `chatlab`! 💬🔬
-   🤓 Simplified the `register` methods of the `Conversation` and `FunctionRegistry` classes. The parameters `parameters_model` and `json_schema` are replaced by a single parameter `parameter_schema`, which can be a pydantic model or a JSON schema. This streamlines and simplifies the function registration process by accepting both pydantic models and JSON schema as parameter schemas in a single argument instead of two separate arguments. This reduces ambiguity and simplifies the implementation.
-   💪🏻 Improved typing for messaging
-   📝 Documentation improvements
-   📜 When outputs and inputs are too big, allow scrolling instead of overflowing
-   🔐 Check for `OPENAI_API_KEY` on `Conversation` creation

### Fixed

-   🐛 Fixed the run_cell builtin to actually return the result. This reintroduces side effects of display output, meaning outputs from run_cell will now appear in the notebook and be visible to the Language Model as part of the run.
-   ✅ Extended type for parameters_model is now correctly `Optional[Type["BaseModel"]]` so that you can extend a model for parameters in your own typed Python code. This is now mypy compliant.

### Removed

-   🚗 Took out the `auto_continue` option since it only applied to function calls and generally should be `True` for function call responses

## [0.13.0]

### Added

-   🐍 Include a builtin `python` chat function to handle the model's hallucination of `python` being an available chat function. Enable it with `allow_hallucinated_python` to the `Conversation` or the `FunctionRegistry`. NOTE: it runs in the same runtime as the `Conversation` and _will_ be used to execute arbitrary code. Use with caution. Or delight.
-   🤩 Auto infer schemas for functions. Run `session.register(function)`. This is a great way to get started quickly. Note: you will get better results in some cases by using You may still get better results out of using pydantic models since those can have descriptions and other metadata in the resulting JSON schema.
-   🆕 Accept functions with a JSON Schema for [Function calling](https://platform.openai.com/docs/guides/gpt/function-calling). This should make functions portable across any other libraries are are accepting the OpenAI standard for function calling.

### Changed

-   `Session` has been renamed to `Conversation` to be more understandable. `Session` will have a deprecation warning until it is removed for 1.0.0.
-   `chat` has been renamed to `submit` to better reflect that it's sending the current batch of messages on. `chat` will have a deprecation warning until it is removed for 1.0.0
-   Shifted some errors that bubbled up as exceptions to the end user to instead be `system` messages for the LLM

### Removed

-   Removed `deltas` iterator for `StreamCompletion`, favoring the new conversations API instead.

## [0.12.3]

### Fixed

-   Don't emit empty assistant messages

## [0.12.2]

### Added

-   Updated README with more documentation

## [0.12.1]

### Fixed

-   Fixed a bug where zero functions would create an `InvalidRequestError: [] is too short - 'functions'`

## [0.12.0]

### Added

-   A little chat function displayer

## [0.11.4]

### Added

-   Created a simple OpenAI chat interface for use in interactive computing environments
