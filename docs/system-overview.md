# MetaMind System Overview

## Purpose

MetaMind is an intelligent dashboard metadata extraction and analysis system that extracts comprehensive information from Apache Superset dashboards and generates structured metadata files using LLM-powered analysis.

## Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Server │
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│Superset│ │  Trino   │
│  API   │ │  API     │
└────────┘ └──────────┘
    │
    ▼
┌─────────────────┐
│  LLM (Claude)   │
│  via DSPy       │
└─────────────────┘
```

## Core Components

### 1. Dashboard Extraction (`query_extract.py`)
- Extracts dashboard metadata from Superset API
- Retrieves chart information, SQL queries, and metadata
- Exports to JSON and CSV formats

### 2. SQL Parser (`sql_parser.py`)
- Parses SQL queries to extract tables and columns
- Identifies original column names (not aliases)
- Normalizes table names (adds catalog prefix if missing)

### 3. LLM Extractor (`llm_extractor.py`)
- Uses DSPy framework with Claude Sonnet 4
- Extracts tables, columns, and relationships from SQL
- Generates comprehensive table descriptions

### 4. Trino Client (`trino_client.py`)
- Connects to Starburst/Trino via Superset SQL Lab API
- Executes DESCRIBE queries to get column data types
- Detects partition columns

### 5. Metadata Generator (`metadata_generator.py`)
- Generates `tables_metadata.csv` with table descriptions
- Generates `columns_metadata.csv` with column types
- Generates `filter_conditions.txt` with SQL filter context

### 6. API Server (`api_server.py`)
- FastAPI REST API server
- Exposes endpoints for dashboard extraction
- Serves extracted metadata files

## Data Flow

1. **Extraction**: User provides dashboard ID → System extracts from Superset API
2. **Storage**: Raw data saved to `extracted_meta/{id}_json.json` and `extracted_meta/{id}_csv.csv`
3. **Analysis**: LLM analyzes SQL queries to extract tables and columns
4. **Enrichment**: Trino queries fetch column data types and partition info
5. **Generation**: Metadata files generated in `extracted_meta/` directory

## Output Files

For each dashboard (ID: `{id}`), the system generates:

- `{id}_json.json` - Complete dashboard metadata
- `{id}_csv.csv` - Tabular chart metadata
- `{id}_queries.sql` - All SQL queries
- `{id}_tables_columns.csv` - Table-column mapping
- `{id}_tables_metadata.csv` - Comprehensive table metadata
- `{id}_columns_metadata.csv` - Column metadata with types
- `{id}_filter_conditions.txt` - Filter conditions and SQL context

## Technology Stack

- **Backend**: Python 3.11, FastAPI, pandas
- **LLM**: Claude Sonnet 4 via DSPy framework
- **Frontend**: React.js with styled-components
- **Database**: Trino/Starburst (via Superset API)
- **Source**: Apache Superset REST API

## Key Features

1. **Intelligent Extraction**: LLM-powered analysis of SQL queries
2. **Comprehensive Metadata**: Table descriptions, relationships, and context
3. **Partition Detection**: Automatic detection of partition columns
4. **Filter Analysis**: Extraction of filter conditions from SQL
5. **Background Processing**: Non-blocking LLM extraction
6. **Thread-Safe**: Handles concurrent requests safely

