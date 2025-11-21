# Metadata Generator Module

**File**: `metadata_generator.py`

## Purpose

Generates comprehensive metadata files from extracted dashboard information.

## Key Functions

### `generate_tables_metadata()`

Generates `tables_metadata.csv` with:
- Table descriptions (LLM-generated)
- Refresh frequency
- Business vertical
- Partition column
- Relationship context

### `generate_columns_metadata()`

Generates `columns_metadata.csv` with:
- Variable types (from Trino)
- Column descriptions (from chart labels)
- Required flags

### `generate_filter_conditions()`

Generates `filter_conditions.txt` with:
- SQL filter context
- Tables involved
- Standard filter conditions

### `generate_all_metadata()`

Orchestrates generation of all metadata files.

## Usage

```python
from metadata_generator import generate_all_metadata

generate_all_metadata(
    dashboard_id=282,
    api_key="sk-...",
    model="claude-sonnet-4-20250514"
)
```

## Output Files

All files saved to `extracted_meta/`:
- `{id}_tables_metadata.csv` - Table metadata (tab-separated)
- `{id}_columns_metadata.csv` - Column metadata (tab-separated)
- `{id}_filter_conditions.txt` - Filter conditions

## LLM Integration

Uses DSPy `TableMetadataExtractor` signature to generate:
- Comprehensive table descriptions
- Business context and use cases
- Relationship information

## Dependencies

- `llm_extractor` - For LLM-based extraction
- `trino_client` - For schema information
- `sql_parser` - For table normalization
- `pandas` - For CSV generation

