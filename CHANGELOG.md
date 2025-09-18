# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-09-18

### Added
- Initial release of shouldpy
- AI-driven test assertion decorator with natural language conditions
- Support for both sync and async functions
- Automatic capture of logs, print outputs, and return values
- Integration with LangChain-compatible LLM models
- Comprehensive error handling and reporting

### Features
- `@should("condition")` decorator for natural language test assertions
- Global LLM configuration with `should.use(llm_client)`
- Per-decorator LLM override support
- Automatic log and output capturing during test execution
- AI-powered assertion validation with detailed failure messages