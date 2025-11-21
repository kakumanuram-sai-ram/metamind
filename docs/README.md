# MetaMind

Intelligent dashboard metadata extraction and analysis system for Apache Superset.

## Overview

MetaMind extracts comprehensive metadata from Superset dashboards and generates structured metadata files using LLM-powered analysis. It identifies tables, columns, relationships, and filter conditions from dashboard SQL queries.

## Features

- 🔍 **Intelligent Extraction**: LLM-powered analysis of SQL queries
- 📊 **Comprehensive Metadata**: Table descriptions, relationships, and context
- 🔗 **Trino Integration**: Automatic column data type detection
- 📁 **Structured Output**: Multiple metadata file formats
- ⚡ **Fast API**: Non-blocking background processing
- 🎨 **Modern UI**: React-based frontend

## Quick Start

```bash
# Setup
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
export PATH="$HOME/.local/bin:$PATH"

# Configure (edit config.py with Superset credentials)
# Set ANTHROPIC_API_KEY environment variable

# Start backend
python api_server.py

# Start frontend (optional)
cd frontend && npm start
```

## Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) directory:

- **[System Overview](./docs/system-overview.md)** - Architecture and components
- **[Getting Started](./docs/getting-started.md)** - Setup and usage guide
- **[API Reference](./docs/api-reference.md)** - Complete API documentation
- **[Architecture Decisions](./docs/adrs/)** - ADRs explaining design choices
- **[Module Documentation](./docs/modules/)** - Detailed module docs

## Project Structure

```
metamind/
├── extracted_meta/          # Generated dashboard files
├── docs/                    # Documentation
│   ├── adrs/               # Architecture Decision Records
│   ├── modules/            # Module-specific docs
│   └── guides/             # User guides
├── frontend/               # React frontend
├── api_server.py           # FastAPI server
├── query_extract.py        # Dashboard extraction
├── llm_extractor.py        # LLM-based analysis
├── sql_parser.py           # SQL parsing (fallback)
├── trino_client.py         # Trino integration
├── metadata_generator.py   # Metadata file generation
└── config.py              # Configuration
```

## Output Files

For each dashboard (ID: `{id}`):

- `{id}_json.json` - Complete dashboard metadata
- `{id}_csv.csv` - Tabular chart metadata
- `{id}_queries.sql` - All SQL queries
- `{id}_tables_columns.csv` - Table-column mapping
- `{id}_tables_metadata.csv` - Comprehensive table metadata
- `{id}_columns_metadata.csv` - Column metadata with types
- `{id}_filter_conditions.txt` - Filter conditions

## Technology Stack

- **Backend**: Python 3.11, FastAPI, pandas, DSPy
- **LLM**: Claude Sonnet 4 (via Anthropic API)
- **Frontend**: React.js, styled-components
- **Database**: Trino/Starburst (via Superset API)

## License

Internal use only.

## Support

See [Troubleshooting Guide](./docs/guides/troubleshooting.md) for common issues.

