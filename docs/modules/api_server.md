# API Server Module

**File**: `api_server.py`

## Purpose

FastAPI REST API server that exposes endpoints for dashboard extraction and metadata retrieval.

## Key Endpoints

### Dashboard Extraction

- `POST /api/dashboard/extract` - Extract dashboard metadata
- `GET /api/dashboards` - List available dashboards

### Data Retrieval

- `GET /api/dashboard/{id}/json` - Get dashboard JSON
- `GET /api/dashboard/{id}/csv` - Get dashboard CSV
- `GET /api/dashboard/{id}/tables-columns` - Get table-column mapping

### File Downloads

- `GET /api/dashboard/{id}/json/download` - Download JSON file
- `GET /api/dashboard/{id}/csv/download` - Download CSV file
- `GET /api/dashboard/{id}/tables-columns/download` - Download tables CSV

## Background Processing

LLM extraction runs in background thread to avoid blocking API responses:

```python
def run_llm_extraction():
    # Extract tables/columns
    # Generate metadata files
    # Runs asynchronously
```

## Configuration

- CORS enabled for frontend
- File serving from `extracted_meta/` directory
- Error handling with proper HTTP status codes

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pandas` - Data manipulation
- `query_extract` - Dashboard extraction
- `llm_extractor` - LLM-based analysis
- `metadata_generator` - Metadata file generation

