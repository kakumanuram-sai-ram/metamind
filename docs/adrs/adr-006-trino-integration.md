# ADR-006: Trino/Starburst Integration for Schema Information

**Status**: Accepted  
**Date**: 2025-11-19  
**Deciders**: Development Team

## Context

We need column data types and partition information for tables. Options:
- Query Trino directly
- Use Superset SQL Lab API
- Parse from SQL queries (unreliable)

## Decision

Use Superset SQL Lab API to execute Trino `DESCRIBE` queries. This approach:
- Works with existing authentication
- No need for separate Trino connection
- Leverages Superset's connection management
- Can detect partition columns from metadata

## Implementation

- `TrinoClient` class wraps Superset SQL Lab API
- Executes `DESCRIBE {catalog}.{schema}.{table}` queries
- Parses response to extract column names and types
- Detects partition columns by name patterns (dt, date, day_id, etc.)

## Consequences

### Positive
- Reuses existing authentication
- No additional connection setup
- Consistent with Superset workflow

### Negative
- Dependent on Superset API availability
- Some tables may not be accessible
- Partition detection is heuristic-based

## Alternatives Considered

1. **Direct Trino connection**: Requires separate credentials
2. **Superset metadata API**: Limited schema information
3. **SQL parsing**: Unreliable for data types

## References

- [Trino Client Module](../modules/trino_client.md)

