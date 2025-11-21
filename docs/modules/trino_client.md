# Trino Client Module

**File**: `trino_client.py`

## Purpose

Connects to Trino/Starburst via Superset SQL Lab API to fetch column data types and schema information.

## Key Classes

### `TrinoClient`

Wraps Superset SQL Lab API for Trino queries.

**Methods:**
- `get_table_columns(table_name, database_id)` - Get columns for a table
- `get_columns_for_tables(table_names, database_id)` - Get columns for multiple tables

### Functions

- `get_column_datatypes_from_trino(dashboard_info, base_url, headers)` - Main function

## Usage

```python
from trino_client import TrinoClient, get_column_datatypes_from_trino
from config import BASE_URL, HEADERS

# Get column data types for all tables in dashboard
trino_columns = get_column_datatypes_from_trino(dashboard_info, BASE_URL, HEADERS)

# Returns: Dict[str, Dict[str, str]]
# Format: {table_name: {column_name: data_type}}
```

## Implementation

1. Extracts unique tables from dashboard SQL queries
2. Executes `DESCRIBE {catalog}.{schema}.{table}` via Superset API
3. Parses response to extract column names and types
4. Returns dictionary mapping table → column → data_type

## Partition Detection

The `detect_partition_columns()` function in `metadata_generator.py` uses this module to:
- Query table schema
- Look for partition column patterns (dt, date, day_id, etc.)
- Check data types (date/timestamp more likely to be partitions)

## Dependencies

- `requests` - HTTP client
- `sql_parser` - For parsing SQL to extract tables

