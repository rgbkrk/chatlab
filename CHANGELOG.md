# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.13.0]

### Added

-   Accept functions _without_ a model by using `inspect` to determine the signature

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
