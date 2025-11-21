# Getting Started with MetaMind

## Prerequisites

- Python 3.11+
- Node.js 16+ (for frontend)
- Access to Superset instance with valid credentials
- Anthropic API key for Claude Sonnet 4

## Installation

### 1. Clone and Setup

```bash
cd /home/devuser/sai_dev/metamind
```

### 2. Python Environment Setup

Using `uv` (recommended):

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Activate virtual environment
source meta_env/bin/activate

# Install dependencies (already done if using uv)
export PATH="$HOME/.local/bin:$PATH"
```

### 3. Configuration

Edit `config.py` with your Superset credentials:

```python
BASE_URL = "https://your-superset-instance.com"
HEADERS = {
    'Cookie': 'your-session-cookie',
    'X-CSRFToken': 'your-csrf-token',
}
```

Set environment variable for Anthropic API key:

```bash
export ANTHROPIC_API_KEY="sk-your-key-here"
```

Or use the default key in `api_server.py` (for testing only).

### 4. Start Backend Server

```bash
cd /home/devuser/sai_dev/metamind
export PATH="$HOME/.local/bin:$PATH"
source meta_env/bin/activate
python api_server.py
```

Server runs on `http://localhost:8000`

### 5. Start Frontend (Optional)

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

## Usage

### Extract Dashboard via API

```bash
curl -X POST http://localhost:8000/api/dashboard/extract \
  -H "Content-Type: application/json" \
  -d '{"dashboard_id": 282}'
```

### Extract Dashboard via Frontend

1. Open `http://localhost:3000`
2. Enter dashboard URL or ID
3. Click "Extract Dashboard"
4. Download generated files

### Extract Dashboard via Python

```python
from query_extract import SupersetExtractor
from config import BASE_URL, HEADERS

extractor = SupersetExtractor(BASE_URL, HEADERS)
dashboard_info = extractor.extract_dashboard_complete_info(282)

# Files are automatically saved to extracted_meta/
```

## Output Files

All files are saved to `extracted_meta/` directory:

- `282_json.json` - Complete dashboard metadata
- `282_csv.csv` - Tabular chart metadata
- `282_queries.sql` - All SQL queries
- `282_tables_columns.csv` - Table-column mapping
- `282_tables_metadata.csv` - Table metadata (LLM-generated)
- `282_columns_metadata.csv` - Column metadata
- `282_filter_conditions.txt` - Filter conditions

## Next Steps

- Read [System Overview](./system-overview.md) for architecture details
- Check [API Reference](./api-reference.md) for endpoint documentation
- Review [Module Documentation](./modules/) for implementation details

