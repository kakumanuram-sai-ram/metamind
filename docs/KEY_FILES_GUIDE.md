# Key Files Guide

This document explains the two main workflows in the codebase.

## 1. Superset API Calls & Chart Data Extraction

### **Main File: `query_extract.py`**

This file contains the `SupersetExtractor` class that makes all API calls to Superset.

#### Key Methods:

1. **`get_dashboard_info(dashboard_id)`** (line ~120)
   - **API Endpoint**: `GET /api/v1/dashboard/{dashboard_id}`
   - Extracts basic dashboard information

2. **`get_chart_details(chart_id)`** (line ~124)
   - **API Endpoint**: `GET /api/v1/chart/{chart_id}`
   - Gets chart metadata (metrics, columns, filters, etc.)

3. **`get_chart_data_and_query(chart_id, dataset_id, query_context)`** (line ~152)
   - **API Endpoints**: 
     - `GET /api/v1/chart/{chart_id}/data` (primary)
     - `POST /api/v1/chart/data` (fallback)
   - **This is where SQL queries are extracted!**
   - Returns the actual SQL query executed for the chart

4. **`extract_chart_info(chart_id, chart_name)`** (line ~316)
   - Orchestrates the extraction of complete chart information
   - Calls `get_chart_details()`, `get_chart_data_and_query()`, etc.
   - Returns a `ChartInfo` dataclass with all chart data including SQL query

5. **`extract_dashboard_complete_info(dashboard_id)`** (line ~422)
   - Main entry point for extracting all charts from a dashboard
   - Iterates through all charts and calls `extract_chart_info()` for each
   - Returns `DashboardInfo` with list of `ChartInfo` objects

#### Flow:
```
extract_dashboard_complete_info()
  └─> For each chart:
      └─> extract_chart_info()
          ├─> get_chart_details() → Chart metadata
          ├─> get_dataset_details() → Dataset info
          └─> get_chart_data_and_query() → **SQL QUERY EXTRACTION**
```

#### Key Code Location:
- **Line 388**: `chart_data = self.get_chart_data_and_query(chart_id, dataset_id, query_context)`
- **Line 394**: `sql_query = results[0].get('query', None)` - SQL extracted here!

---

## 2. Table, Column & Derived Logic Extraction

### **Main File: `llm_extractor.py`**

This file uses DSPy and LLM (Claude) to extract tables, columns, and derived column logic from the SQL queries.

#### Key Components:

1. **`SourceTableColumnExtractor` (DSPy Signature)** (line ~36)
   - Defines the input/output schema for LLM extraction
   - Input: SQL query + chart metadata
   - Output: source_tables, source_columns, derived_columns_mapping

2. **`DashboardTableColumnExtractor.extract_source_from_chart()`** (line ~261)
   - **Main method that extracts tables/columns from a single chart**
   - Takes chart dict (with SQL query) as input
   - Uses DSPy to call LLM and extract:
     - Source tables (physical tables, not CTEs)
     - Source columns (base columns from tables)
     - Derived columns with their logic (aggregations, window functions, etc.)

3. **`extract_source_tables_columns_llm()`** (line ~443)
   - **Main entry point for extracting from entire dashboard**
   - Takes `dashboard_info` (from `query_extract.py`) as input
   - Iterates through all charts
   - For each chart, calls `extract_source_from_chart()`
   - Formats results into CSV format:
     - `tables_involved`
     - `column_names`
     - `alias_column_name`
     - `source_or_derived`
     - `derived_column_logic`

#### Flow:
```
extract_source_tables_columns_llm(dashboard_info)
  └─> For each chart in dashboard_info['charts']:
      └─> extract_source_from_chart(chart)
          ├─> Prepare chart metadata (metrics, columns, etc.)
          ├─> Call DSPy LLM: source_extractor(sql_query, chart_metadata)
          └─> Parse LLM response:
              ├─> source_tables (comma-separated)
              ├─> source_columns (comma-separated)
              └─> derived_columns_mapping (JSON)
          └─> Format into rows for CSV output
```

#### Key Code Locations:
- **Line 290**: `result = self.source_extractor(sql_query=sql_query, chart_metadata=...)` - LLM call
- **Line 295-310**: Parsing LLM response into structured data
- **Line 474**: `chart_result = extractor.extract_source_from_chart(chart)` - Called for each chart
- **Line 479-550**: Formatting results into final CSV rows

---

## Complete Workflow

```
1. User requests dashboard extraction
   ↓
2. query_extract.py → SupersetExtractor.extract_dashboard_complete_info()
   ├─> Makes API calls to Superset
   ├─> Extracts chart metadata
   └─> Extracts SQL queries for each chart
   ↓
3. Dashboard JSON saved (with all chart info + SQL queries)
   ↓
4. llm_extractor.py → extract_source_tables_columns_llm()
   ├─> Reads dashboard JSON
   ├─> For each chart's SQL query:
   │   └─> Calls LLM (Claude via DSPy)
   │       └─> Extracts: tables, columns, derived logic
   └─> Formats into CSV: tables_columns.csv
```

---

## Integration Points

### In `api_server.py`:
- **Line ~330**: Calls `SupersetExtractor.extract_dashboard_complete_info()` to get dashboard JSON
- **Line ~343**: Calls `extract_source_tables_columns_llm()` to extract tables/columns

### In `scripts/generate_final_output.py`:
- Orchestrates the full process:
  1. Load dashboard JSON
  2. Call `extract_source_tables_columns_llm()`
  3. Optionally fetch schemas from Starburst
  4. Save final CSV

---

## Summary

| Task | File | Key Method |
|------|------|------------|
| **Superset API Calls** | `query_extract.py` | `SupersetExtractor.get_chart_data_and_query()` |
| **SQL Query Extraction** | `query_extract.py` | `SupersetExtractor.extract_chart_info()` |
| **Table/Column Extraction** | `llm_extractor.py` | `extract_source_from_chart()` |
| **Derived Logic Extraction** | `llm_extractor.py` | `SourceTableColumnExtractor` (DSPy) |
| **Full Dashboard Processing** | `llm_extractor.py` | `extract_source_tables_columns_llm()` |

