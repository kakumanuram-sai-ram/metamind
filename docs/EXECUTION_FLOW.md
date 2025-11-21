# Execution Flow: Dashboard ID to Final Output

This document describes the exact order of file execution when a dashboard ID is provided.

## Two Main Entry Points

### Entry Point 1: API Server (`scripts/api_server.py`)
When dashboard ID is provided via API endpoint `/api/dashboard/extract`

### Entry Point 2: Command Line Script (`scripts/generate_final_output.py`)
When dashboard ID is provided via command line: `python scripts/generate_final_output.py <dashboard_id>`

---

## Execution Flow: API Server Path

### Phase 1: Dashboard Extraction (Fast - No LLM)

**1. `scripts/api_server.py`** (Line 300-318)
   - Entry: `extract_dashboard()` function
   - Creates: `SupersetExtractor(BASE_URL, HEADERS)`
   - Calls: `extractor.extract_dashboard_complete_info(dashboard_id)`

**2. `scripts/query_extract.py`** (Line 422)
   - Function: `extract_dashboard_complete_info()`
   - Calls: `get_dashboard_metadata(dashboard_id)` (Line 120)
     - **API Call**: `GET /api/v1/dashboard/{dashboard_id}`
   - Extracts chart IDs from dashboard metadata
   - For each chart:
     - Calls: `extract_chart_info(chart_id, chart_name)` (Line 316)

**3. `scripts/query_extract.py`** (Line 316)
   - Function: `extract_chart_info()`
   - Calls: `get_chart_details(chart_id)` (Line 124)
     - **API Call**: `GET /api/v1/chart/{chart_id}`
   - Calls: `get_dataset_details(dataset_id)` (Line 148)
     - **API Call**: `GET /api/v1/dataset/{dataset_id}`
   - Calls: `get_chart_data_and_query(chart_id, dataset_id, query_context)` (Line 152)
     - **API Call**: `GET /api/v1/chart/{chart_id}/data` or `POST /api/v1/chart/data`
     - **Extracts SQL query** from response (Line 394)

**4. `scripts/api_server.py`** (Line 324-326)
   - Saves dashboard info:
     - `extractor.export_to_json()` → `extracted_meta/{dashboard_id}_json.json`
     - `extractor.export_to_csv()` → `extracted_meta/{dashboard_id}_metadata.csv`
     - `extractor.export_sql_queries()` → `extracted_meta/{dashboard_id}_queries.sql`

### Phase 2: LLM Extraction (Slow - Background Thread)

**5. `scripts/api_server.py`** (Line 336-376)
   - Background thread starts: `run_llm_extraction()`
   - Calls: `extract_source_tables_columns_llm()` (Line 349)

**6. `scripts/llm_extractor.py`** (Line 443)
   - Function: `extract_source_tables_columns_llm()`
   - Creates: `DashboardTableColumnExtractor(api_key, model, base_url)`
   - For each chart in dashboard_info:
     - Calls: `extractor.extract_source_from_chart(chart)` (Line 474)

**7. `scripts/llm_extractor.py`** (Line 261)
   - Function: `extract_source_from_chart()`
   - Prepares chart metadata (metrics, columns, etc.)
   - Calls: `self.source_extractor()` (Line 290)
     - **DSPy LLM Call**: Uses `SourceTableColumnExtractor` signature
     - **LLM API Call**: Claude via proxy (`https://cst-ai-proxy.paytm.com/v1`)
   - Parses LLM response:
     - `source_tables` (comma-separated)
     - `source_columns` (comma-separated)
     - `derived_columns_mapping` (JSON)

**8. `scripts/llm_extractor.py`** (Line 479-550)
   - Formats results into CSV rows:
     - Source columns: `tables_involved`, `column_names`, `alias_column_name`, `source_or_derived="source"`, `derived_column_logic="NA"`
     - Derived columns: `tables_involved`, `column_names`, `alias_column_name`, `source_or_derived="derived"`, `derived_column_logic="<SQL expression>"`

**9. `scripts/api_server.py`** (Line 358-361)
   - Saves to CSV: `extracted_meta/{dashboard_id}_tables_columns.csv`

**10. `scripts/api_server.py`** (Line 366)
   - Calls: `generate_all_metadata(dashboard_id, api_key, model)`

**11. `scripts/metadata_generator.py`** (Line 311)
   - Function: `generate_all_metadata()`
   - Loads: `extracted_meta/{dashboard_id}_json.json`
   - Calls: `generate_tables_metadata()` (Line 339)
   - Generates additional metadata files

---

## Execution Flow: Command Line Script Path

### Phase 1: Load Dashboard JSON (Assumes JSON already exists)

**1. `scripts/generate_final_output.py`** (Line 18-78)
   - Entry: `main()` function
   - Parses command line arguments
   - Calls: `generate_final_tables_columns_output(dashboard_id, ...)` (Line 71)

**2. `scripts/llm_extractor.py`** (Line 541)
   - Function: `generate_final_tables_columns_output()`
   - Loads: `extracted_meta/{dashboard_id}_json.json` (Line 570)
   - Calls: `extract_source_tables_columns_llm()` (Line 583)
     - **Same as Step 6-8 above**

**3. `scripts/llm_extractor.py`** (Line 590-594)
   - If `fetch_schemas=True`:
     - Calls: `process_dspy_extraction_results()` from `starburst_schema_fetcher.py`
     - **Starburst Connection**: Direct Trino connection to fetch DESCRIBE queries

**4. `scripts/llm_extractor.py`** (Line 600-620)
   - Consolidates results into final DataFrame
   - Saves to: `extracted_meta/{dashboard_id}_tables_columns.csv`

---

## Complete Execution Order Summary

### API Server Path (Full Flow)

```
1. scripts/api_server.py
   └─> extract_dashboard()
       └─> scripts/query_extract.py
           └─> SupersetExtractor.extract_dashboard_complete_info()
               ├─> get_dashboard_metadata() → API: GET /api/v1/dashboard/{id}
               └─> For each chart:
                   └─> extract_chart_info()
                       ├─> get_chart_details() → API: GET /api/v1/chart/{id}
                       ├─> get_dataset_details() → API: GET /api/v1/dataset/{id}
                       └─> get_chart_data_and_query() → API: GET /api/v1/chart/{id}/data
                           └─> Extracts SQL query
       └─> export_to_json() → Saves JSON
       └─> export_to_csv() → Saves CSV
       └─> export_sql_queries() → Saves SQL
       └─> [Background Thread] extract_source_tables_columns_llm()
           └─> scripts/llm_extractor.py
               └─> extract_source_tables_columns_llm()
                   └─> For each chart:
                       └─> extract_source_from_chart()
                           └─> DSPy LLM Call → Claude API
                               └─> Parses: tables, columns, derived logic
                   └─> Formats into CSV rows
           └─> Save: {dashboard_id}_tables_columns.csv
           └─> generate_all_metadata()
               └─> scripts/metadata_generator.py
                   └─> generate_tables_metadata()
```

### Command Line Script Path (Assumes JSON exists)

```
1. scripts/generate_final_output.py
   └─> main()
       └─> generate_final_tables_columns_output()
           └─> scripts/llm_extractor.py
               └─> Load: {dashboard_id}_json.json
               └─> extract_source_tables_columns_llm()
                   └─> [Same as API path steps 6-8]
               └─> [Optional] starburst_schema_fetcher.py
                   └─> Fetch schemas from Starburst
               └─> Save: {dashboard_id}_tables_columns.csv
```

---

## Key Files and Their Roles

| File | Role | Key Functions |
|------|------|---------------|
| `scripts/api_server.py` | API entry point | `extract_dashboard()` |
| `scripts/query_extract.py` | Superset API calls | `extract_dashboard_complete_info()`, `extract_chart_info()`, `get_chart_data_and_query()` |
| `scripts/llm_extractor.py` | LLM-based extraction | `extract_source_tables_columns_llm()`, `extract_source_from_chart()`, `generate_final_tables_columns_output()` |
| `scripts/metadata_generator.py` | Metadata generation | `generate_all_metadata()`, `generate_tables_metadata()` |
| `scripts/starburst_schema_fetcher.py` | Schema fetching | `process_dspy_extraction_results()`, `fetch_schemas_for_tables()` |
| `scripts/config.py` | Configuration | Provides `BASE_URL`, `HEADERS`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL` |
| `scripts/sql_parser.py` | SQL parsing utilities | `normalize_table_name()`, `extract_table_column_mapping()` |
| `scripts/trino_client.py` | Trino client | Used by metadata_generator for schema info |

---

## API Calls Made

### Superset API Calls (via `query_extract.py`)
1. `GET /api/v1/dashboard/{dashboard_id}` - Get dashboard metadata
2. `GET /api/v1/chart/{chart_id}` - Get chart details
3. `GET /api/v1/dataset/{dataset_id}` - Get dataset details
4. `GET /api/v1/chart/{chart_id}/data` - Get chart data and SQL query
   - OR `POST /api/v1/chart/data` - Alternative endpoint

### LLM API Calls (via `llm_extractor.py`)
1. `POST https://cst-ai-proxy.paytm.com/v1` - Claude API via proxy
   - Called once per chart via DSPy framework
   - Uses `SourceTableColumnExtractor` signature

### Starburst/Trino Calls (via `starburst_schema_fetcher.py`)
1. Direct Trino connection - `DESCRIBE` queries for each table
   - Only if `fetch_schemas=True`

---

## Output Files Generated

1. `extracted_meta/{dashboard_id}_json.json` - Complete dashboard info
2. `extracted_meta/{dashboard_id}_metadata.csv` - Chart metadata
3. `extracted_meta/{dashboard_id}_queries.sql` - All SQL queries
4. `extracted_meta/{dashboard_id}_tables_columns.csv` - **Main output**: Tables, columns, derived logic
5. `extracted_meta/{dashboard_id}_tables_metadata.csv` - Table metadata (if metadata_generator runs)

---

## Timing

- **Phase 1 (Dashboard Extraction)**: ~5-30 seconds (depends on number of charts)
- **Phase 2 (LLM Extraction)**: ~1-5 minutes (depends on number of charts, ~5-10 seconds per chart)
- **Total**: ~2-6 minutes for typical dashboard with 20-30 charts


