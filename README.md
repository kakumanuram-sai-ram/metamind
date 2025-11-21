# MetaMind

**Intelligent Dashboard Metadata Extraction and Analysis System for Apache Superset**

MetaMind is a comprehensive system that extracts, analyzes, and consolidates metadata from Apache Superset dashboards using LLM-powered analysis. It identifies tables, columns, relationships, filter conditions, and business context from dashboard SQL queries, then merges metadata from multiple dashboards into a unified knowledge base.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Output Files](#output-files)
- [Technology Stack](#technology-stack)
- [Documentation](#documentation)
- [Contributing](#contributing)

---

## Overview

MetaMind automates the extraction of comprehensive metadata from Superset dashboards, transforming raw dashboard configurations into structured, analyzable metadata. The system:

1. **Extracts** dashboard metadata from Superset API (charts, SQL queries, filters)
2. **Analyzes** SQL queries using LLM to identify tables, columns, and relationships
3. **Enriches** metadata with data types from Trino/Starburst
4. **Merges** metadata from multiple dashboards into unified schemas
5. **Builds** knowledge bases for LLM context injection and documentation

The system supports both single-dashboard extraction and multi-dashboard processing workflows, with parallel processing capabilities and comprehensive progress tracking.

---

## Features

### 🔍 Intelligent Extraction
- **LLM-Powered Analysis**: Uses Claude Sonnet 4 via DSPy framework to extract tables, columns, and relationships from SQL queries
- **Rule-Based Fallback**: SQL parser for fast extraction when LLM is unavailable
- **Trino Integration**: Automatic column data type detection from Starburst/Trino databases

### 📊 Comprehensive Metadata
- **Table Metadata**: Descriptions, refresh frequencies, verticals, partition columns
- **Column Metadata**: Data types, descriptions, business context
- **Relationships**: Joining conditions between tables
- **Filter Conditions**: Dashboard-level and chart-level filters
- **Term Definitions**: Business metrics, calculated fields, synonyms

### 🔗 Multi-Dashboard Support
- **Parallel Processing**: Extract multiple dashboards simultaneously
- **Intelligent Merging**: LLM-based consolidation with conflict detection and resolution
- **Incremental Updates**: Merge new dashboards with existing consolidated metadata
- **Knowledge Base Generation**: Unified knowledge base from merged metadata

### ⚡ Performance & UX
- **Fast API**: Non-blocking background processing for LLM operations
- **Progress Tracking**: Real-time progress updates for multi-dashboard processing
- **Modern UI**: React-based frontend for dashboard visualization and management
- **RESTful API**: Complete REST API for programmatic access

### 📁 Structured Output
- **Multiple Formats**: JSON, CSV, SQL, TXT files
- **Organized Structure**: Per-dashboard folders with standardized naming
- **Consolidated Metadata**: Merged metadata files for unified schema view
- **Knowledge Base**: Compressed archive ready for LLM context injection

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│                      (Port 3000/5173)                           │
│              Dashboard Visualization & Management               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Server                             │
│                        (Port 8000)                             │
│  REST API: Extract, List, Download, Progress Tracking          │
└────────────┬──────────────────────────────┬────────────────────┘
             │                              │
    ┌────────┴────────┐          ┌─────────┴─────────┐
    │                 │          │                    │
    ▼                 ▼          ▼                    ▼
┌─────────┐    ┌──────────┐  ┌──────────┐    ┌──────────────┐
│Superset │    │  Trino   │  │   LLM    │    │  File System │
│   API   │    │   API    │  │ (Claude) │    │   (Output)   │
└─────────┘    └──────────┘  └──────────┘    └──────────────┘
```

### Processing Pipeline

```
Dashboard ID(s)
    │
    ▼
┌─────────────────────────────────────┐
│ 1. Dashboard Extraction              │
│    - Fetch dashboard metadata        │
│    - Extract charts & SQL queries    │
│    - Export to JSON/CSV/SQL         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Table/Column Extraction            │
│    - LLM-based SQL analysis          │
│    - Rule-based fallback             │
│    - Trino data type enrichment      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Metadata Generation               │
│    - Table metadata                  │
│    - Column metadata                 │
│    - Joining conditions              │
│    - Filter conditions               │
│    - Term definitions                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Multi-Dashboard Merge (Optional)   │
│    - LLM-based consolidation         │
│    - Conflict detection/resolution    │
│    - Unified schema generation       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Knowledge Base Build (Optional)    │
│    - Convert to KB format            │
│    - Create compressed archive       │
│    - Ready for LLM context           │
└──────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

- Python 3.8+ (Python 3.11 recommended)
- Node.js 16+ (for frontend)
- Access to Superset instance
- Anthropic API key (for LLM features)
- Access to Trino/Starburst (optional, for data type enrichment)

### Backend Setup

1. **Clone/Navigate to the repository:**
   ```bash
   cd /home/devuser/sai_dev/metamind
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv meta_env
   source meta_env/bin/activate  # On Windows: meta_env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # Or using uv (if available):
   # ./uv_setup.sh
   ```

4. **Configure authentication:**
   Edit `scripts/config.py`:
   - Set `BASE_URL` to your Superset instance URL
   - Update `HEADERS` with your session cookie and CSRF token
   - See [Authentication Guide](./docs/guides/authentication.md) for details

5. **Set LLM API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   # Or set in config.py (not recommended for production)
   ```

### Frontend Setup (Optional)

```bash
cd frontend
npm install
npm start  # Starts on http://localhost:3000
```

### Quick Start Scripts

```bash
# Start backend server
./start_backend.sh

# Start frontend (in separate terminal)
./start_frontend.sh

# Restart API server
./restart_api.sh
```

---

## Usage

### Command Line Interface

#### Single Dashboard Extraction

```bash
# Extract dashboard 729
python scripts/extract_dashboard_with_timing.py 729

# Output files saved to: extracted_meta/729/
```

#### Multi-Dashboard Processing

```bash
# Extract, merge, and build KB for multiple dashboards
python scripts/process_multiple_dashboards.py 585 729 842

# Skip extraction (if already done)
python scripts/process_multiple_dashboards.py 585 729 842 --skip-extract

# Skip merge step
python scripts/process_multiple_dashboards.py 585 729 842 --skip-merge

# Incremental merge (merge with existing consolidated metadata)
python scripts/process_multiple_dashboards.py 585 729 842 --incremental-merge

# Stop on first error
python scripts/process_multiple_dashboards.py 585 729 842 --stop-on-error
```

#### Orchestrator (Extraction Only)

```bash
# Extract multiple dashboards in parallel
python scripts/orchestrator.py 585 729 842

# Sequential processing
python scripts/orchestrator.py 585 729 842 --no-parallel
```

### API Server

#### Start the API Server

```bash
# From scripts directory
python scripts/api_server.py

# Or using uvicorn directly
uvicorn scripts.api_server:app --host 0.0.0.0 --port 8000
```

#### API Endpoints

**Dashboard Management:**
- `GET /api/dashboards` - List all extracted dashboards
- `GET /api/dashboard/{id}/json` - Get dashboard JSON
- `GET /api/dashboard/{id}/csv` - Get dashboard CSV data
- `GET /api/dashboard/{id}/tables-columns` - Get table/column mapping

**Extraction:**
- `POST /api/dashboard/extract` - Extract a single dashboard
- `POST /api/dashboards/process-multiple` - Process multiple dashboards

**Progress Tracking:**
- `GET /api/progress` - Get current processing progress

**Downloads:**
- `GET /api/dashboard/{id}/download/{file_type}` - Download specific file
- `GET /api/dashboard/{id}/download-all` - Download all files as ZIP

See [API Reference](./docs/api-reference.md) for complete documentation.

### Frontend UI

1. Start the backend API server (port 8000)
2. Start the frontend (port 3000)
3. Open http://localhost:3000 in your browser
4. Use the UI to:
   - Extract dashboards by URL or ID
   - View extracted dashboard metadata
   - Download files
   - Process multiple dashboards
   - Monitor progress

---

## Project Structure

```
metamind/
├── scripts/                          # Core Python modules
│   ├── api_server.py                 # FastAPI REST API server
│   ├── config.py                     # Configuration (URLs, auth, LLM settings)
│   ├── query_extract.py              # Superset dashboard extraction
│   ├── sql_parser.py                 # Rule-based SQL parsing (fallback)
│   ├── llm_extractor.py              # LLM-based extraction using DSPy
│   ├── trino_client.py               # Trino/Starburst integration
│   ├── metadata_generator.py          # Generate comprehensive metadata files
│   ├── orchestrator.py               # Multi-dashboard extraction orchestrator
│   ├── merger.py                     # LLM-based metadata merging
│   ├── knowledge_base_builder.py     # Knowledge base generation
│   ├── progress_tracker.py           # Progress tracking for multi-dashboard
│   ├── extract_dashboard_with_timing.py  # Single dashboard extraction entry point
│   └── process_multiple_dashboards.py    # Multi-dashboard processing entry point
│
├── frontend/                         # React frontend application
│   ├── src/
│   │   ├── App.js                    # Main application component
│   │   ├── components/               # React components
│   │   ├── services/
│   │   │   └── api.js                # API client
│   │   └── styles/                   # Styled components
│   └── package.json
│
├── extracted_meta/                   # Output directory
│   ├── {dashboard_id}/               # Per-dashboard metadata
│   │   ├── {id}_json.json            # Complete dashboard metadata
│   │   ├── {id}_csv.csv              # Tabular chart metadata
│   │   ├── {id}_queries.sql          # All SQL queries
│   │   ├── {id}_tables_columns.csv   # Table-column mapping
│   │   ├── {id}_tables_columns_enriched.csv  # With data types
│   │   ├── {id}_table_metadata.csv   # Table descriptions
│   │   ├── {id}_columns_metadata.csv # Column metadata
│   │   ├── {id}_joining_conditions.csv  # Table relationships
│   │   ├── {id}_filter_conditions.txt    # Filter conditions
│   │   └── {id}_definitions.csv          # Term definitions
│   │
│   ├── merged_metadata/              # Consolidated metadata (multi-dashboard)
│   │   ├── consolidated_table_metadata.csv
│   │   ├── consolidated_columns_metadata.csv
│   │   ├── consolidated_joining_conditions.csv
│   │   ├── consolidated_definitions.csv
│   │   ├── consolidated_filter_conditions.txt
│   │   ├── conflicts_report.json     # Merge conflicts
│   │   └── merged_metadata.json      # Complete merged metadata
│   │
│   ├── knowledge_base/               # Knowledge base (for LLM/documentation)
│   │   ├── table_metadata.json
│   │   ├── column_metadata.json
│   │   ├── joining_conditions.json
│   │   ├── definitions.json
│   │   ├── filter_conditions.txt
│   │   ├── business_context.json
│   │   ├── validations.json
│   │   └── knowledge_base.zip        # Compressed archive
│   │
│   └── progress.json                 # Progress tracking state
│
├── docs/                             # Comprehensive documentation
│   ├── README.md                     # Documentation index
│   ├── system-overview.md            # Architecture overview
│   ├── getting-started.md            # Setup guide
│   ├── api-reference.md              # API documentation
│   ├── adrs/                         # Architecture Decision Records
│   ├── modules/                      # Module-specific documentation
│   └── guides/                       # User guides
│
├── examples/                         # Example usage scripts
│   ├── example_usage.py              # Basic extraction examples
│   └── example_starburst_schema.py   # Schema fetcher examples
│
├── tests/                            # Test files
│   ├── test_auth.py                  # Authentication tests
│   └── test_dashboard_access.py     # Dashboard access tests
│
├── dspy_examples.py                  # DSPy signature examples
├── pyproject.toml                    # Python project configuration
├── requirements.txt                  # Python dependencies
├── start_backend.sh                  # Backend startup script
├── start_frontend.sh                 # Frontend startup script
└── restart_api.sh                    # API restart script
```

---

## Core Components

### 1. Dashboard Extraction (`query_extract.py`)
- Fetches dashboard metadata from Superset API
- Extracts chart information, SQL queries, and filters
- Exports to JSON, CSV, and SQL formats
- Handles authentication and API errors

### 2. SQL Parser (`sql_parser.py`)
- Rule-based SQL parsing (fallback when LLM unavailable)
- Extracts table and column names from SQL queries
- Identifies original column names (not aliases)
- Normalizes table names (adds catalog prefix if missing)

### 3. LLM Extractor (`llm_extractor.py`)
- Uses DSPy framework with Claude Sonnet 4
- Extracts tables, columns, and relationships from SQL
- Generates comprehensive table and column descriptions
- Extracts joining conditions, filter conditions, and term definitions
- Handles complex SQL with CTEs, subqueries, and aggregations

### 4. Trino Client (`trino_client.py`)
- Connects to Starburst/Trino via Superset SQL Lab API
- Executes DESCRIBE queries to get column data types
- Detects partition columns
- Enriches metadata with database schema information

### 5. Metadata Generator (`metadata_generator.py`)
- Generates comprehensive metadata files:
  - Table metadata with descriptions and context
  - Column metadata with data types and business context
  - Joining conditions between tables
  - Filter conditions (dashboard and chart level)
  - Term definitions (metrics, calculated fields, synonyms)

### 6. Orchestrator (`orchestrator.py`)
- Manages extraction of multiple dashboards
- Supports parallel and sequential processing
- Tracks progress and handles errors
- Organizes output into per-dashboard folders

### 7. Metadata Merger (`merger.py`)
- Merges metadata from multiple dashboards using LLM
- Detects and resolves conflicts (different descriptions, etc.)
- Consolidates into unified schema
- Generates conflict reports
- Supports incremental merging

### 8. Knowledge Base Builder (`knowledge_base_builder.py`)
- Converts merged metadata into knowledge base format
- Creates JSON files optimized for LLM context injection
- Generates compressed archive (knowledge_base.zip)
- Formats data for documentation and business user reference

### 9. Progress Tracker (`progress_tracker.py`)
- Tracks extraction progress for multi-dashboard processing
- Provides real-time status updates via API
- Persists progress to JSON file
- Thread-safe for parallel processing

### 10. API Server (`api_server.py`)
- FastAPI REST API for programmatic access
- Non-blocking background processing for LLM operations
- CORS-enabled for frontend integration
- File download endpoints
- Progress tracking endpoints

---

## Output Files

### Per-Dashboard Files (`extracted_meta/{dashboard_id}/`)

| File | Description |
|------|-------------|
| `{id}_json.json` | Complete dashboard metadata (charts, filters, layout) |
| `{id}_csv.csv` | Tabular representation of chart metadata |
| `{id}_queries.sql` | All SQL queries from dashboard charts |
| `{id}_tables_columns.csv` | Table-to-column mapping (source tables only) |
| `{id}_tables_columns_enriched.csv` | Table-column mapping with data types from Trino |
| `{id}_table_metadata.csv` | Comprehensive table metadata (descriptions, refresh, vertical) |
| `{id}_columns_metadata.csv` | Column metadata (data types, descriptions, business context) |
| `{id}_joining_conditions.csv` | Table relationships and join conditions |
| `{id}_filter_conditions.txt` | Dashboard and chart-level filter conditions |
| `{id}_definitions.csv` | Term definitions (metrics, calculated fields, synonyms) |

### Merged Metadata (`extracted_meta/merged_metadata/`)

| File | Description |
|------|-------------|
| `consolidated_table_metadata.csv` | Unified table metadata from all dashboards |
| `consolidated_columns_metadata.csv` | Unified column metadata from all dashboards |
| `consolidated_joining_conditions.csv` | Unified joining conditions |
| `consolidated_definitions.csv` | Unified term definitions |
| `consolidated_filter_conditions.txt` | All filter conditions |
| `conflicts_report.json` | Report of conflicts detected during merge |
| `merged_metadata.json` | Complete merged metadata in JSON format |

### Knowledge Base (`extracted_meta/knowledge_base/`)

| File | Description |
|------|-------------|
| `table_metadata.json` | Table metadata in LLM-friendly JSON format |
| `column_metadata.json` | Column metadata in LLM-friendly JSON format |
| `joining_conditions.json` | Joining conditions in JSON format |
| `definitions.json` | Term definitions in JSON format |
| `filter_conditions.txt` | Filter conditions (plain text) |
| `business_context.json` | Business context (empty template) |
| `validations.json` | Validation rules (empty template) |
| `knowledge_base.zip` | Compressed archive of all 7 files |

---

## Technology Stack

### Backend
- **Python 3.11** - Core language
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server
- **Pandas** - Data manipulation and CSV handling
- **DSPy** - LLM framework for structured extraction
- **Requests** - HTTP client for API calls

### LLM
- **Claude Sonnet 4** - Primary LLM (via Anthropic API)
- **Custom API Proxy** - PayTM internal proxy for LLM access

### Frontend
- **React 18** - UI framework
- **Styled Components** - CSS-in-JS styling
- **Axios** - HTTP client
- **React Router** - Client-side routing

### Database Integration
- **Trino/Starburst** - Data warehouse (via Superset SQL Lab API)
- **Superset API** - Dashboard metadata source

### Development Tools
- **UV** - Fast Python package manager (optional)
- **Node.js/npm** - Frontend package management

---

## Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) directory:

### Getting Started
- **[Getting Started Guide](./docs/getting-started.md)** - Setup and first steps
- **[Quick Start](./docs/QUICK_START.md)** - Fast setup guide
- **[Authentication Guide](./docs/guides/authentication.md)** - How to get Superset credentials

### Architecture & Design
- **[System Overview](./docs/system-overview.md)** - High-level architecture
- **[Architecture Decision Records](./docs/adrs/)** - Design decisions and rationale
- **[Execution Flow](./docs/EXECUTION_FLOW.md)** - Processing pipeline details

### API & Usage
- **[API Reference](./docs/api-reference.md)** - Complete API documentation
- **[Module Documentation](./docs/modules/)** - Detailed module docs
- **[Multi-Dashboard Processing](./docs/MULTI_DASHBOARD_PROCESSING.md)** - Multi-dashboard workflow

### Guides
- **[Deployment Guide](./docs/guides/deployment.md)** - Production deployment
- **[Troubleshooting](./docs/guides/troubleshooting.md)** - Common issues and solutions
- **[Download Buttons Guide](./docs/DOWNLOAD_BUTTONS_GUIDE.md)** - File download features

### Reference
- **[File Organization](./docs/FILES_ORGANIZATION.md)** - Output file structure
- **[Key Files Guide](./docs/KEY_FILES_GUIDE.md)** - Important files overview
- **[DSPy Examples](./docs/DSPY_EXAMPLES_GUIDE.md)** - DSPy signature examples

---

## Contributing

### Development Workflow

1. **Create a virtual environment:**
   ```bash
   python -m venv meta_env
   source meta_env/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests:**
   ```bash
   python -m pytest tests/
   ```

4. **Follow code style:**
   - Use type hints where possible
   - Add docstrings to functions and classes
   - Follow existing code patterns

### Key Design Principles

- **Modularity**: Each component has a single responsibility
- **LLM-First**: Prefer LLM extraction over rule-based when possible
- **Fallback Support**: Always provide rule-based fallback
- **Thread Safety**: Multi-dashboard processing must be thread-safe
- **Progress Tracking**: Long-running operations should report progress
- **Error Handling**: Continue processing on errors when possible

### Architecture Decision Records

See [`docs/adrs/`](./docs/adrs/) for documented design decisions:
- ADR-001: LLM-based extraction
- ADR-002: DSPy framework choice
- ADR-003: File organization
- ADR-004: Background processing
- ADR-005: Thread safety
- ADR-006: Trino integration

---

## License

Internal use only.

---

## Support

For issues, questions, or contributions:
1. Check the [Troubleshooting Guide](./docs/guides/troubleshooting.md)
2. Review relevant documentation in [`docs/`](./docs/)
3. Check existing issues or create a new one

---

**MetaMind** - Intelligent Dashboard Metadata Extraction System

