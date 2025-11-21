# ADR-004: Background Processing for LLM Extraction

**Status**: Accepted  
**Date**: 2025-11-19  
**Deciders**: Development Team

## Context

LLM-based extraction takes 30-60 seconds for a dashboard with 16 charts. If done synchronously, this blocks the API response and creates poor user experience.

## Decision

Run LLM extraction in a background thread after immediately returning the API response. The response includes:
- Success status
- Dashboard ID
- Message indicating background processing

Files are generated asynchronously:
- `{id}_tables_columns.csv`
- `{id}_tables_metadata.csv`
- `{id}_columns_metadata.csv`
- `{id}_filter_conditions.txt`

## Implementation

- Python `threading.Thread` with `daemon=True`
- Fast API response (< 1 second)
- Background thread processes LLM calls
- Errors logged but don't affect API response

## Consequences

### Positive
- Fast API response time
- Better user experience
- Non-blocking operation
- Can process multiple dashboards concurrently

### Negative
- No immediate feedback on LLM extraction status
- Files may not be immediately available
- Error handling more complex
- Need to check file existence before serving

## Alternatives Considered

1. **Synchronous processing**: Simple but slow
2. **Task queue (Celery)**: Overkill for current scale
3. **Async/await**: More complex, similar benefits

## References

- [API Server Module](../modules/api_server.md)

