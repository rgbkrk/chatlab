# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

-   🐛 Fix the `run_cell` builtin to actually return the result. This does however bring back side effects of display output.

### Changed

-   💬🔬 Package is now called `chatlab`!
-   💪🏻 Improved typing for messaging

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
