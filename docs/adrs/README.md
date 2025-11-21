# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) documenting key architectural decisions made in the MetaMind project.

## What are ADRs?

ADRs are documents that capture important architectural decisions made along with their context and consequences. They help future developers understand why certain choices were made.

## ADR Index

1. **[ADR-001: LLM-Based Extraction](./adr-001-llm-based-extraction.md)** - Decision to use LLM for table/column extraction
2. **[ADR-002: DSPy Framework](./adr-002-dspy-framework.md)** - Choice of DSPy for LLM orchestration
3. **[ADR-003: File Organization](./adr-003-file-organization.md)** - Directory structure and file naming conventions
4. **[ADR-004: Background Processing](./adr-004-background-processing.md)** - Asynchronous LLM extraction
5. **[ADR-005: Thread Safety](./adr-005-thread-safety.md)** - DSPy configuration and thread safety
6. **[ADR-006: Trino Integration](./adr-006-trino-integration.md)** - Integration with Trino/Starburst for schema information

## ADR Format

Each ADR follows this structure:

- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: The issue motivating this decision
- **Decision**: The change that we're proposing or have agreed to implement
- **Consequences**: What becomes easier or more difficult to do because of this change

## Contributing

When making significant architectural decisions:

1. Create a new ADR file following the template
2. Update this index
3. Get review from the team
4. Update status as the decision is implemented

