# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.13.0]

### Added

-   Include a builtin `python` chat function to handle the model's hallucination of `python` being an available chat function. Enable it with `include_builtin_python` to the `Conversation` or the `FunctionRegistry`. NOTE: it runs in the same runtime as the `Conversation` and _will_ be used to execute arbitrary code. Use with caution. Or delight.
-   Accept functions _without_ a model. Just run `session.register(function)`. This is a great way to get started quickly. You may still get better results out of using pydantic models since those can have descriptions and other metadata in the resulting JSON schema.

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
