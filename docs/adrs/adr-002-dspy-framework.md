# ADR-002: DSPy Framework for LLM Orchestration

**Status**: Accepted  
**Date**: 2025-11-19  
**Deciders**: Development Team

## Context

We need a framework to orchestrate LLM calls for extracting table and column information from SQL queries. We considered:

- Direct API calls to Claude
- LangChain
- DSPy
- Custom wrapper

## Decision

Use DSPy framework for LLM orchestration because:

1. **Signature-based approach**: Clean separation of inputs/outputs
2. **Chain of Thought**: Built-in reasoning capabilities
3. **Thread safety**: Better handling of concurrent requests
4. **Model abstraction**: Easy to switch LLM providers
5. **Lightweight**: Less overhead than LangChain

## Implementation

- `TableColumnExtractor` DSPy signature defines inputs/outputs
- `ChainOfThought` module for reasoning
- Global configuration with thread-safe initialization
- Claude Sonnet 4 via Anthropic API

## Consequences

### Positive
- Clean, declarative code
- Easy to extend with new extraction tasks
- Built-in reasoning capabilities
- Good documentation and examples

### Negative
- Learning curve for team members
- Additional dependency
- Thread safety requires careful configuration

## Alternatives Considered

1. **Direct Anthropic API**: More control but more boilerplate
2. **LangChain**: More features but heavier and more complex
3. **Custom wrapper**: Full control but more maintenance

## References

- [DSPy Documentation](https://github.com/stanfordnlp/dspy)
- [LLM Extractor Module](../modules/llm_extractor.md)

