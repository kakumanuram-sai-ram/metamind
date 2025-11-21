# ADR-003: File Organization and Naming Conventions

**Status**: Accepted  
**Date**: 2025-11-19  
**Deciders**: Development Team

## Context

We need a consistent file organization structure that:
- Makes it easy to find files
- Supports multiple dashboards
- Is LLM-friendly for code exploration
- Separates concerns clearly

## Decision

Organize files as follows:

```
metamind/
├── extracted_meta/          # All extracted dashboard files
│   ├── {id}_json.json
│   ├── {id}_csv.csv
│   ├── {id}_queries.sql
│   ├── {id}_tables_columns.csv
│   ├── {id}_tables_metadata.csv
│   ├── {id}_columns_metadata.csv
│   └── {id}_filter_conditions.txt
├── docs/                    # Documentation
│   ├── adrs/               # Architecture Decision Records
│   └── modules/            # Module-specific docs
├── frontend/               # React frontend
└── *.py                    # Python modules
```

## Naming Conventions

- **Python modules**: `snake_case.py` (e.g., `query_extract.py`)
- **Dashboard files**: `{dashboard_id}_{type}.{ext}` (e.g., `282_json.json`)
- **Documentation**: `kebab-case.md` (e.g., `system-overview.md`)
- **ADRs**: `adr-{number}-{topic}.md` (e.g., `adr-001-llm-based-extraction.md`)

## Consequences

### Positive
- Clear separation of concerns
- Easy to locate files by dashboard ID
- LLM-friendly naming (descriptive, consistent)
- Scalable for many dashboards

### Negative
- Requires migration of existing files
- Need to update all file path references

## Implementation

- All extraction files go to `extracted_meta/`
- Documentation in `docs/` with subdirectories
- Module docs in `docs/modules/`
- ADRs in `docs/adrs/`

