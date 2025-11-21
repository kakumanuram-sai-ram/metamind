# API Reference

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. List Available Dashboards

**GET** `/api/dashboards`

Returns list of all extracted dashboards.

**Response:**
```json
{
  "dashboards": [
    {
      "dashboard_id": 282,
      "dashboard_title": "UPI Tracker",
      "dashboard_url": "https://...",
      "has_json": true,
      "has_csv": true
    }
  ]
}
```

### 2. Extract Dashboard

**POST** `/api/dashboard/extract`

Extracts dashboard metadata from Superset.

**Request Body:**
```json
{
  "dashboard_url": "https://superset.com/dashboard/282/",
  "dashboard_id": 282
}
```

**Response:**
```json
{
  "success": true,
  "dashboard_id": 282,
  "dashboard_title": "UPI Tracker",
  "total_charts": 16,
  "message": "Dashboard extracted successfully..."
}
```

**Files Generated:**
- `extracted_meta/282_json.json`
- `extracted_meta/282_csv.csv`
- `extracted_meta/282_queries.sql`
- `extracted_meta/282_tables_columns.csv` (background)
- `extracted_meta/282_tables_metadata.csv` (background)
- `extracted_meta/282_columns_metadata.csv` (background)
- `extracted_meta/282_filter_conditions.txt` (background)

### 3. Get Dashboard JSON

**GET** `/api/dashboard/{dashboard_id}/json`

Returns dashboard JSON data.

**Response:**
```json
{
  "columns": ["dashboard_id", "dashboard_title", ...],
  "data": {...},
  "total_rows": 1
}
```

### 4. Download Dashboard JSON

**GET** `/api/dashboard/{dashboard_id}/json/download`

Downloads dashboard JSON file.

### 5. Get Dashboard CSV

**GET** `/api/dashboard/{dashboard_id}/csv`

Returns dashboard CSV data.

### 6. Download Dashboard CSV

**GET** `/api/dashboard/{dashboard_id}/csv/download`

Downloads dashboard CSV file.

### 7. Get Tables and Columns

**GET** `/api/dashboard/{dashboard_id}/tables-columns`

Returns table-column mapping.

**Response:**
```json
{
  "columns": ["table_name", "column_name", "column_label__chart_json", "data_type"],
  "data": [
    {
      "table_name": "hive.schema.table",
      "column_name": "column1",
      "column_label__chart_json": "{\"1561\": \"Label1\"}",
      "data_type": "varchar"
    }
  ],
  "total_rows": 20
}
```

### 8. Download Tables and Columns CSV

**GET** `/api/dashboard/{dashboard_id}/tables-columns/download`

Downloads tables-columns CSV file.

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid request
- `404 Not Found` - Dashboard not found
- `500 Internal Server Error` - Server error

**Error Format:**
```json
{
  "detail": "Error message here"
}
```

## Authentication

Currently uses session cookies and CSRF tokens from Superset. Configure in `config.py`.

## Rate Limiting

No rate limiting implemented. LLM extraction runs in background to avoid blocking.

## CORS

CORS enabled for frontend on `http://localhost:3000`.

