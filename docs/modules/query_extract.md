# Query Extract Module

**File**: `query_extract.py`

## Purpose

Extracts comprehensive dashboard metadata from Apache Superset via REST API.

## Key Classes

### `SupersetExtractor`

Main class for extracting dashboard information.

**Methods:**
- `extract_dashboard_complete_info(dashboard_id)` - Extracts full dashboard metadata
- `export_to_json(dashboard_info, filename)` - Exports to JSON
- `export_to_csv(dashboard_info, filename)` - Exports to CSV
- `export_sql_queries(dashboard_info, filename)` - Exports SQL queries

### Data Classes

- `ChartInfo` - Chart metadata (ID, name, type, SQL query, metrics, columns)
- `DashboardInfo` - Dashboard metadata (ID, title, URL, charts)

## Usage

```python
from query_extract import SupersetExtractor
from config import BASE_URL, HEADERS

extractor = SupersetExtractor(BASE_URL, HEADERS)
dashboard_info = extractor.extract_dashboard_complete_info(282)

# Export files
extractor.export_to_json(dashboard_info)
extractor.export_to_csv(dashboard_info)
extractor.export_sql_queries(dashboard_info)
```

## Output Files

Files are saved to `extracted_meta/`:
- `{id}_json.json` - Complete dashboard metadata
- `{id}_csv.csv` - Tabular chart metadata
- `{id}_queries.sql` - All SQL queries

## Dependencies

- `requests` - HTTP client
- `pandas` - Data manipulation
- `dataclasses` - Data structures

