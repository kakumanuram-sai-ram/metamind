# SQL Parser Module

**File**: `sql_parser.py`

## Purpose

Parses SQL queries to extract tables and columns using rule-based parsing (fallback when LLM is disabled).

## Key Classes

### `SQLParser`

Parses SQL queries to extract metadata.

**Methods:**
- `parse_chart_sql(sql)` - Parse SQL and extract tables
- `remove_comments(sql)` - Remove SQL comments
- `extract_tables(sql)` - Extract table names
- `extract_original_columns_from_sql(sql, tables)` - Extract original column names

### Functions

- `normalize_table_name(table)` - Add "hive." prefix if missing
- `extract_table_column_mapping(dashboard_info, trino_columns)` - Main extraction function

## Usage

```python
from sql_parser import SQLParser, extract_table_column_mapping

parser = SQLParser()
parsed = parser.parse_chart_sql(sql_query)
tables = parsed['tables']

# Full extraction
mapping = extract_table_column_mapping(dashboard_info, trino_columns)
```

## Features

- Extracts source tables (excludes CTEs)
- Identifies original column names (not aliases)
- Normalizes table names (catalog.schema.table format)
- Matches columns with Trino schema data

## Limitations

- Rule-based parsing is less accurate than LLM
- May miss complex SQL patterns
- Used as fallback when LLM extraction is disabled

## Dependencies

- `re` - Regular expressions
- `json` - JSON handling

