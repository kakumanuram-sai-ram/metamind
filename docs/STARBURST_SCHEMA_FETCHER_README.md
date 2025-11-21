# Starburst Schema Fetcher

This module normalizes table names and fetches schema information (DESCRIBE) from Starburst/Trino using direct connection.

## Features

1. **Table Name Normalization**: Converts table names to `hive.db_name.table_name` format
2. **Schema Fetching**: Executes DESCRIBE queries on tables via Starburst connection
3. **DSPy Integration**: Processes results from DSPy extraction and fetches schemas
4. **Consolidated Output**: Returns a DataFrame with table_name, column_name, column_datatype, extra, comment

## Functions

### `normalize_table_name(table_name: str) -> str`

Normalizes table names to `hive.db_name.table_name` format.

**Handles formats:**
- `hive.db_name.table_name` → `hive.db_name.table_name` (already normalized)
- `db_name.table_name` → `hive.db_name.table_name`
- `"hive"."db_name"."table_name"` → `hive.db_name.table_name`
- `"db_name"."table_name"` → `hive.db_name.table_name`

### `get_unique_tables_from_dspy_results(dspy_results: List[Dict]) -> Set[str]`

Extracts unique table names from DSPy extraction results and normalizes them.

### `get_starburst_connection(user_email: str) -> Connection`

Creates a Starburst/Trino connection.

**Parameters:**
- `user_email`: User email for authentication (default: "kakumanu.ram@paytm.com")

### `describe_table(conn, table_name: str) -> pd.DataFrame`

Executes DESCRIBE query on a single table.

**Returns:**
- DataFrame with columns from DESCRIBE (Column, Type, Extra, Comment)

### `fetch_schemas_for_tables(table_names: List[str], user_email: str, normalize: bool) -> pd.DataFrame`

Fetches schema information for multiple tables.

**Parameters:**
- `table_names`: List of table names (can be in various formats)
- `user_email`: User email for authentication
- `normalize`: Whether to normalize table names (default: True)

**Returns:**
- DataFrame with columns:
  - `table_name`: Normalized table name (hive.schema.table)
  - `column_name`: Column name
  - `column_datatype`: Data type
  - `extra`: Extra information (e.g., partition info)
  - `comment`: Column comment

### `process_dspy_extraction_results(dspy_results: List[Dict], user_email: str) -> pd.DataFrame`

Main function to process DSPy extraction results and fetch table schemas.

**Parameters:**
- `dspy_results`: List of dicts from `extract_source_tables_columns_llm`
  - Each dict should have `tables_involved` key
- `user_email`: User email for Starburst authentication

**Returns:**
- DataFrame with schema information for all tables

## Usage Examples

### Example 1: Normalize Table Names

```python
from starburst_schema_fetcher import normalize_table_name

tables = [
    "user_paytm_payments.upi_tracker_insight",
    "hive.user_paytm_payments.upi_tracker_insight_cm"
]

for table in tables:
    normalized = normalize_table_name(table)
    print(f"{table} -> {normalized}")
```

### Example 2: Fetch Schemas for Specific Tables

```python
from starburst_schema_fetcher import fetch_schemas_for_tables

tables = [
    "hive.user_paytm_payments.upi_tracker_insight",
    "hive.user_paytm_payments.upi_tracker_insight_cm"
]

schema_df = fetch_schemas_for_tables(tables)
print(schema_df)
```

### Example 3: Process DSPy Results

```python
from starburst_schema_fetcher import process_dspy_extraction_results
from llm_extractor import extract_source_tables_columns_llm
import json

# Load dashboard info
with open("extracted_meta/282_json.json", 'r') as f:
    dashboard_info = json.load(f)

# Extract using DSPy
dspy_results = extract_source_tables_columns_llm(
    dashboard_info,
    api_key="your-api-key",
    model="claude-sonnet-4-20250514"
)

# Fetch schemas
schema_df = process_dspy_extraction_results(dspy_results)

# Save to CSV
schema_df.to_csv("extracted_meta/282_table_schemas.csv", index=False)
```

### Example 4: Full Integration

```python
from starburst_schema_fetcher import process_dspy_extraction_results
from llm_extractor import extract_source_tables_columns_llm
import json
import os

# Configuration
dashboard_id = 282
api_key = os.getenv("ANTHROPIC_API_KEY")
json_file = f"extracted_meta/{dashboard_id}_json.json"

# Load dashboard
with open(json_file, 'r', encoding='utf-8') as f:
    dashboard_info = json.load(f)

# Extract tables and columns using DSPy
print("Extracting tables and columns using DSPy...")
dspy_results = extract_source_tables_columns_llm(
    dashboard_info,
    api_key=api_key,
    model="claude-sonnet-4-20250514"
)

print(f"Found {len(dspy_results)} table-column mappings")

# Fetch schemas from Starburst
print("\nFetching table schemas from Starburst...")
schema_df = process_dspy_extraction_results(dspy_results)

print(f"\nSchema information:")
print(f"  - {len(schema_df)} total columns")
print(f"  - {schema_df['table_name'].nunique()} unique tables")

# Save results
output_file = f"extracted_meta/{dashboard_id}_table_schemas.csv"
schema_df.to_csv(output_file, index=False)
print(f"\n✅ Saved to {output_file}")
```

## Output Format

The returned DataFrame has the following structure:

```
table_name                                    | column_name | column_datatype | extra | comment
----------------------------------------------|-------------|-----------------|-------|--------
hive.user_paytm_payments.upi_tracker_insight | day_id      | date            |       | 
hive.user_paytm_payments.upi_tracker_insight | segment     | varchar         |       |
hive.user_paytm_payments.upi_tracker_insight | mau         | bigint          |       |
...
```

## Connection Details

The module connects to Starburst using:
- **Host**: `https://cdp-dashboarding.platform.mypaytm.com`
- **Port**: `443`
- **Catalog**: `hive`
- **Authentication**: User email (default: `kakumanu.ram@paytm.com`)

## Dependencies

- `pandas`: For DataFrame operations
- `trino.dbapi`: For Starburst/Trino connection
- `trino.auth`: For authentication (if needed)

## Error Handling

- Invalid table names are logged with warnings
- Failed DESCRIBE queries are logged but don't stop processing
- Missing columns are filled with `None`
- Connection errors are caught and logged

## Notes

- Table names are automatically normalized to `hive.schema.table` format
- DESCRIBE queries use quoted identifiers to handle special characters
- The module handles different DESCRIBE output formats automatically
- All tables are processed sequentially (can be parallelized if needed)

