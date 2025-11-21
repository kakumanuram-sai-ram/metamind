# Project Structure

This document describes the modular organization of the codebase.

## Directory Structure

```
metamind/
├── api_server.py              # FastAPI backend server
├── config.py                  # Central configuration (API keys, URLs, models)
├── llm_extractor.py           # LLM-based extraction using DSPy
├── metadata_generator.py      # Metadata generation from extracted data
├── query_extract.py           # Superset dashboard extraction
├── sql_parser.py              # SQL parsing utilities
├── starburst_schema_fetcher.py # Starburst/Trino schema fetching
├── trino_client.py            # Trino database client
│
├── scripts/                   # Utility scripts
│   ├── __init__.py
│   └── generate_final_output.py  # Generate final CSV output
│
├── tests/                     # Test files
│   ├── __init__.py
│   ├── test_auth.py           # Authentication tests
│   └── test_dashboard_access.py # Dashboard access tests
│
├── examples/                  # Example usage scripts
│   ├── __init__.py
│   ├── example_starburst_schema.py # Schema fetcher examples
│   └── example_usage.py       # Basic usage examples
│
├── docs/                      # Documentation
│   ├── adrs/                  # Architecture Decision Records
│   ├── guides/                # User guides
│   └── modules/               # Module documentation
│
├── frontend/                  # React frontend application
│   └── src/
│       ├── components/        # React components
│       └── services/          # API service layer
│
└── extracted_meta/            # Output directory for extracted data
    └── *.csv, *.json, *.sql   # Generated files
```

## Core Modules

### Configuration (`config.py`)
Central configuration file containing:
- **BASE_URL**: Superset API base URL
- **HEADERS**: Authentication headers (cookies, CSRF tokens)
- **LLM_API_KEY**: Anthropic API key (can be overridden via env var)
- **LLM_MODEL**: Default LLM model name
- **LLM_BASE_URL**: Custom API proxy base URL

### API Server (`api_server.py`)
FastAPI server providing REST endpoints for:
- Dashboard extraction
- File listing and serving
- Background LLM processing

### LLM Extractor (`llm_extractor.py`)
DSPy-based extraction for:
- Source tables and columns
- Derived columns with logic
- Table-column mappings

### Metadata Generator (`metadata_generator.py`)
Generates comprehensive metadata files:
- Tables metadata
- Columns metadata
- Filter conditions

## Usage

### Running Scripts
Scripts in the `scripts/` directory can be run from the project root:
```bash
python scripts/generate_final_output.py <dashboard_id> [options]
```

### Running Tests
Tests can be run from the project root:
```bash
python -m pytest tests/
# or
python tests/test_auth.py
```

### Running Examples
Examples demonstrate usage patterns:
```bash
python examples/example_usage.py
python examples/example_starburst_schema.py
```

## Configuration

All LLM-related settings are centralized in `config.py`:
- Set `LLM_API_KEY` directly in config (not recommended for production)
- Or set `ANTHROPIC_API_KEY` environment variable (recommended)
- Model and base URL can be overridden per function call

## Best Practices

1. **Configuration**: Always use `config.py` for default values
2. **Imports**: Use absolute imports from project root
3. **Testing**: Keep test files in `tests/` directory
4. **Examples**: Keep example scripts in `examples/` directory
5. **Scripts**: Keep utility scripts in `scripts/` directory

