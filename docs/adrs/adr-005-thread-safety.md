# ADR-005: Thread Safety for DSPy Configuration

**Status**: Accepted  
**Date**: 2025-11-19  
**Deciders**: Development Team

## Context

DSPy settings can only be configured by the thread that initially configured it. When multiple threads (API requests + background processing) try to configure DSPy, we get:
```
RuntimeError: dspy.settings can only be changed by the thread that initially configured it.
```

## Decision

Use a global, thread-safe DSPy configuration:
- Single global `_dspy_extractor` instance
- Thread lock (`threading.Lock`) for initialization
- Configure once, reuse across threads
- Handle configuration errors gracefully

## Implementation

```python
_dspy_lm = None
_dspy_extractor = None
_dspy_lock = threading.Lock()

def _get_dspy_extractor(api_key: str, model: str):
    global _dspy_lm, _dspy_extractor
    with _dspy_lock:
        if _dspy_extractor is None:
            # Configure once
            _dspy_lm = dspy.LM(...)
            dspy.configure(lm=_dspy_lm)
            _dspy_extractor = dspy.ChainOfThought(...)
    return _dspy_extractor
```

## Consequences

### Positive
- Works with multiple threads
- Single configuration point
- Efficient (no repeated configuration)

### Negative
- Global state (but necessary for DSPy)
- Must handle configuration errors
- All threads use same model/API key

## Alternatives Considered

1. **Per-thread configuration**: Not possible with DSPy limitations
2. **Separate processes**: More complex, IPC overhead
3. **Single-threaded**: Not scalable

## References

- [LLM Extractor Module](../modules/llm_extractor.md)

