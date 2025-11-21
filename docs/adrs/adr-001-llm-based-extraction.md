# ADR-001: LLM-Based Table and Column Extraction

**Status**: Accepted  
**Date**: 2025-11-19  
**Deciders**: Development Team

## Context

We need to extract tables and columns from Superset dashboard SQL queries. Initial attempts used rule-based SQL parsing, but this had limitations:

- Complex SQL with CTEs, subqueries, and joins
- Aliases vs original column names
- Computed columns and transformations
- Inconsistent SQL patterns across dashboards

## Decision

Use Large Language Models (LLM) - specifically Claude Sonnet 4 - to intelligently extract table and column information from SQL queries. The LLM understands SQL semantics and can identify:

- Source tables (excluding CTEs)
- Original column names (not aliases)
- Column aliases and their mappings
- Relationships between tables

## Implementation

- DSPy framework for LLM orchestration
- Claude Sonnet 4 model via Anthropic API
- Custom DSPy signature: `TableColumnExtractor`
- Background processing to avoid blocking API responses

## Consequences

### Positive
- More accurate extraction from complex SQL
- Handles edge cases better than regex parsing
- Can understand SQL semantics and context
- Easier to extend with new extraction requirements

### Negative
- Requires API key and incurs LLM costs
- Slower than rule-based parsing (mitigated by background processing)
- Dependency on external LLM service availability
- More complex error handling

## Alternatives Considered

1. **Enhanced SQL Parser**: More regex patterns and AST parsing
   - Rejected: Too brittle, hard to maintain
2. **Hybrid Approach**: Rule-based + LLM fallback
   - Considered: Current implementation supports this via `USE_LLM_EXTRACTION` env var
3. **Database Schema Queries**: Query Trino directly for all columns
   - Rejected: Doesn't identify which columns are actually used

## References

- [LLM Extractor Module](../modules/llm_extractor.md)
- [DSPy Framework](https://github.com/stanfordnlp/dspy)

