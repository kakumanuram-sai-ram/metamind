# MetaMind API Reference

Base URL: `http://localhost:8000`

## API Overview

The MetaMind API provides REST endpoints for dashboard extraction, progress tracking, and file management.

## Authentication

Currently no authentication required (internal tool). Superset and LLM authentication handled in `scripts/config.py`.

---

## Vertical & Tag Management

### Get All Verticals

`GET /api/verticals`

Returns list of business verticals with sub-verticals.

**Response:**
```json
{
  "success": true,
  "verticals": [
    {
      "id": "upi",
      "name": "UPI (Unified Payments Interface)",
      "sub_verticals": ["UPI Growth", "User Growth"]
    },
    {
      "id": "merchant",
      "name": "Merchant Business",
      "sub_verticals": ["QR / SB", "EDC", "All Offline Merchant"]
    }
  ]
}
```

### Get Dashboards by Vertical

`POST /api/dashboards/by-vertical`

Returns dashboards matching selected vertical/sub-vertical based on tags.

**Request Body:**
```json
{
  "vertical": "upi",
  "sub_vertical": "UPI Growth"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "dashboards": [
    {
      "id": 476,
      "title": "UPI Profile wise MAU Distribution",
      "url": "https://superset.example.com/superset/dashboard/476",
      "tags": ["UPI Growth", "owner:224"]
    }
  ],
  "vertical": "upi",
  "sub_vertical": "UPI Growth",
  "tags_searched": ["UPI Growth"],
  "total_count": 8
}
```

---

## Dashboard Extraction

### Extract Single Dashboard

`POST /api/dashboard/extract`

Extracts metadata from a single Superset dashboard.

**Request Body:**
```json
{
  "dashboard_url": "https://superset.example.com/superset/dashboard/476",
  "dashboard_id": 476  // optional, extracted from URL if not provided
}
```

**Response:**
```json
{
  "success": true,
  "dashboard_id": 476,
  "dashboard_title": "UPI Profile wise MAU Distribution",
  "dashboard_url": "https://superset.example.com/superset/dashboard/476",
  "total_charts": 15,
  "message": "Dashboard 476 extracted successfully..."
}
```

**Processing:**
- Phase 1: Dashboard extraction (immediate)
- Phase 2-8: LLM processing (background thread)
- Files created in `extracted_meta/476/`

### Process Multiple Dashboards

`POST /api/dashboards/process-multiple`

Processes multiple dashboards with optional merge and KB build.

**Request Body:**
```json
{
  "dashboard_ids": [476, 511, 729],
  "extract": true,           // Run extraction
  "merge": true,             // Merge metadata
  "build_kb": true,          // Build knowledge base
  "incremental_merge": false,// Merge with existing
  "use_existing": {          // Use existing metadata
    "476": false,
    "511": true,
    "729": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Processing started for 3 dashboards",
  "dashboard_ids": [476, 511, 729],
  "progress_tracking": "Check /api/progress for status"
}
```

**Processing:**
- Runs in background thread
- Progress tracked in `progress.json`
- Poll `/api/progress` for updates

---

## Progress Tracking

### Get Current Progress

`GET /api/progress`

Returns current processing progress for multi-dashboard operations.

**Response:**
```json
{
  "status": "processing",  // pending, processing, merging, building_kb, completed, error
  "current_operation": "extract",
  "dashboards": {
    "476": {
      "status": "processing",
      "current_phase": "Phase 4: Table Metadata",
      "current_file": "476_table_metadata.csv",
      "completed_files": [
        "476_json.json",
        "476_csv.csv",
        "476_queries.sql",
        "476_tables_columns.csv",
        "476_tables_columns_enriched.csv"
      ],
      "completed_files_count": 5,
      "total_files": 11,
      "error": null,
      "start_time": "2025-11-25T20:00:00",
      "end_time": null
    },
    "511": {
      "status": "pending",
      // ...
    }
  },
  "merge_status": {
    "status": "not_started",
    "start_time": null,
    "end_time": null
  },
  "kb_build_status": {
    "status": "not_started",
    "start_time": null,
    "end_time": null
  }
}
```

**Status Values:**
- `pending` - Not started
- `processing` - Extraction in progress
- `completed` - Successfully completed
- `error` - Failed with error

---

## Dashboard Management

### List Extracted Dashboards

`GET /api/dashboards`

Returns list of all extracted dashboards.

**Response:**
```json
{
  "dashboards": [
    {
      "id": 476,
      "title": "UPI Profile wise MAU Distribution",
      "files": [
        "476_json.json",
        "476_csv.csv",
        "476_queries.sql",
        // ...
      ]
    }
  ]
}
```

### Get Dashboard Files

`GET /api/dashboard/{dashboard_id}/files`

Lists all available files for a dashboard.

**Response:**
```json
{
  "dashboard_id": 476,
  "files": [
    {
      "type": "json",
      "filename": "476_json.json",
      "path": "extracted_meta/476/476_json.json",
      "size": 125000,
      "exists": true
    },
    {
      "type": "table_metadata",
      "filename": "476_table_metadata.csv",
      "path": "extracted_meta/476/476_table_metadata.csv",
      "size": 5000,
      "exists": true
    }
  ]
}
```

### Get Specific File

`GET /api/dashboard/{dashboard_id}/file/{file_type}`

Returns specific metadata file.

**Path Parameters:**
- `dashboard_id` - Dashboard ID
- `file_type` - One of:
  - `json` - Complete dashboard metadata
  - `csv` - Chart metadata
  - `queries` - SQL queries
  - `tables_columns` - Table-column mapping
  - `tables_columns_enriched` - With datatypes
  - `table_metadata` - Table descriptions
  - `columns_metadata` - Column descriptions
  - `joining_conditions` - Table relationships
  - `filter_conditions` - Filter logic
  - `definitions` - Term definitions

**Response:**
- Content-Type: `application/json` or `text/csv` or `text/plain`
- Body: File contents

**Error Response:**
```json
{
  "detail": "File not found: 476_table_metadata.csv"
}
```

---

## File Downloads

### Download Specific File

`GET /api/dashboard/{dashboard_id}/download/{file_type}`

Downloads a specific file with proper Content-Disposition header.

**Response:**
- Content-Type: `application/octet-stream` or `text/csv` or `application/json`
- Content-Disposition: `attachment; filename="476_table_metadata.csv"`
- Body: File contents

### Download All Dashboard Files

`GET /api/dashboard/{dashboard_id}/download-all`

Downloads all files for a dashboard as a ZIP archive.

**Response:**
- Content-Type: `application/zip`
- Content-Disposition: `attachment; filename="dashboard_476_all_files.zip"`
- Body: ZIP archive containing all files

### Download Knowledge Base

`GET /api/knowledge-base/download`

Downloads the merged knowledge base ZIP.

**Response:**
- Content-Type: `application/zip`
- Content-Disposition: `attachment; filename="knowledge_base.zip"`
- Body: ZIP archive with KB files

**Error Response:**
```json
{
  "detail": "Knowledge base not found. Please run merge and KB build first."
}
```

---

## Table/Column Mapping

### Get Tables & Columns

`GET /api/dashboard/{dashboard_id}/tables-columns`

Returns table-column mapping for dashboard.

**Response:**
```json
{
  "success": true,
  "dashboard_id": 476,
  "data": [
    {
      "chart_id": "12345",
      "chart_name": "Monthly Revenue",
      "tables_involved": "hive.analytics.transactions",
      "column_names": "transaction_id",
      "alias_column_name": "txn_id",
      "source_or_derived": "source",
      "derived_column_logic": "NA",
      "column_datatype": "bigint"
    }
  ]
}
```

### Download Tables & Columns CSV

`GET /api/dashboard/{dashboard_id}/tables-columns/download`

Downloads tables-columns mapping as CSV.

**Response:**
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename="dashboard_476_tables_columns.csv"`

---

## Health & Status

### Health Check

`GET /`

Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "MetaMind API",
  "version": "1.0.0"
}
```

### API Documentation

`GET /docs`

Interactive API documentation (Swagger UI).

Access at: `http://localhost:8000/docs`

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (dashboard/file doesn't exist)
- `500` - Internal Server Error (processing failure)

---

## Rate Limiting

**Current Limits:**
- No rate limiting implemented
- LLM API has ~50 requests/minute limit
- Polling recommended at 3-5 second intervals

---

## CORS Configuration

**Allowed Origins:**
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)

**Allowed Methods:**
- `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`

**Allowed Headers:**
- `*` (all headers)

---

## Timeouts

**API Timeouts:**
- Default: 30 seconds
- Dashboard list by tags: 60 seconds
- Dashboard extraction: 180 seconds
- File operations: 30 seconds

**Frontend Timeouts:**
- Default API calls: 30 seconds
- Dashboard filtering: 60 seconds
- Extraction: 180 seconds
- Progress polling: 5 seconds

---

## Example Usage

### Complete Workflow (cURL)

**1. Get verticals:**
```bash
curl http://localhost:8000/api/verticals
```

**2. Get dashboards by vertical:**
```bash
curl -X POST http://localhost:8000/api/dashboards/by-vertical \
  -H "Content-Type: application/json" \
  -d '{"vertical": "upi", "sub_vertical": "UPI Growth"}'
```

**3. Process dashboards:**
```bash
curl -X POST http://localhost:8000/api/dashboards/process-multiple \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard_ids": [476, 511],
    "extract": true,
    "merge": true,
    "build_kb": true
  }'
```

**4. Poll progress:**
```bash
curl http://localhost:8000/api/progress
```

**5. Download file:**
```bash
curl -O http://localhost:8000/api/dashboard/476/download/table_metadata
```

**6. Download KB:**
```bash
curl -O http://localhost:8000/api/knowledge-base/download
```

---

## Python Client Example

```python
import requests

base_url = "http://localhost:8000"

# Get dashboards by vertical
response = requests.post(
    f"{base_url}/api/dashboards/by-vertical",
    json={"vertical": "upi", "sub_vertical": "UPI Growth"}
)
dashboards = response.json()["dashboards"]

# Start processing
dashboard_ids = [d["id"] for d in dashboards[:3]]
response = requests.post(
    f"{base_url}/api/dashboards/process-multiple",
    json={
        "dashboard_ids": dashboard_ids,
        "extract": True,
        "merge": True,
        "build_kb": True
    }
)

# Poll progress
import time
while True:
    progress = requests.get(f"{base_url}/api/progress").json()
    if progress["status"] == "completed":
        break
    time.sleep(5)

# Download KB
kb_response = requests.get(f"{base_url}/api/knowledge-base/download")
with open("knowledge_base.zip", "wb") as f:
    f.write(kb_response.content)
```




