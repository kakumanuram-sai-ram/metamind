# Progress Tracking and Download Features

## Overview

Added comprehensive progress tracking and download functionality for multi-dashboard processing.

## Features Implemented

### 1. Progress Tracking System

**File**: `scripts/progress_tracker.py`

- Thread-safe progress tracking
- Real-time status updates stored in JSON file
- Tracks:
  - Overall status (idle, extracting, merging, building_kb, completed)
  - Per-dashboard status (pending, processing, completed, error)
  - Current phase and file being processed
  - Completed files count
  - Merge and KB build progress

**Progress File**: `extracted_meta/progress.json`

### 2. Enhanced Orchestrator

**File**: `scripts/orchestrator.py`

- Integrated progress tracking
- Reports current phase and file for each dashboard
- Updates progress after each file is created
- Tracks completion and errors

### 3. Enhanced Merger

**File**: `scripts/merger.py`

- Progress tracking for merge operations
- Reports current merge step
- Tracks completed merge steps

### 4. Enhanced Knowledge Base Builder

**File**: `scripts/knowledge_base_builder.py`

- Progress tracking for KB build
- Reports current KB build step

### 5. API Endpoints

**File**: `scripts/api_server.py`

New endpoints:
- `GET /api/progress` - Get current processing progress
- `POST /api/dashboards/process-multiple` - Start multi-dashboard processing
- `GET /api/dashboard/{dashboard_id}/files` - Get list of all metadata files
- `GET /api/dashboard/{dashboard_id}/download/{file_type}` - Download specific file
- `GET /api/dashboard/{dashboard_id}/download-all` - Download all files as ZIP

### 6. Frontend Components

**Files**:
- `frontend/src/components/MultiDashboardProcessor.js` - Multi-dashboard processing with progress
- `frontend/src/components/DashboardFileDownloader.js` - Download metadata files by dashboard ID
- `frontend/src/services/api.js` - Updated with new API methods

## Usage

### Start Multi-Dashboard Processing

1. **Via UI**: 
   - Navigate to "Process Multiple Dashboards" section
   - Enter dashboard IDs (comma or space separated)
   - Click "Start Processing"
   - Monitor progress in real-time

2. **Via API**:
   ```bash
   curl -X POST http://localhost:8000/api/dashboards/process-multiple \
     -H "Content-Type: application/json" \
     -d '{
       "dashboard_ids": [585, 729, 476, 842],
       "extract": true,
       "merge": true,
       "build_kb": true
     }'
   ```

3. **Via Command Line**:
   ```bash
   python scripts/process_multiple_dashboards.py 585 729 476 842
   ```

### Monitor Progress

1. **Via UI**: Progress is displayed automatically in the Multi-Dashboard Processor component
2. **Via API**:
   ```bash
   curl http://localhost:8000/api/progress
   ```

### Download Metadata Files

1. **Via UI**:
   - Navigate to "Download Dashboard Metadata Files" section
   - Enter dashboard ID
   - Click "Load Files"
   - Download individual files or all as ZIP

2. **Via API**:
   ```bash
   # Get list of files
   curl http://localhost:8000/api/dashboard/842/files
   
   # Download specific file
   curl http://localhost:8000/api/dashboard/842/download/table_metadata -o table_metadata.csv
   
   # Download all files as ZIP
   curl http://localhost:8000/api/dashboard/842/download-all -o dashboard_842_metadata.zip
   ```

## Progress JSON Structure

```json
{
  "status": "extracting",
  "current_operation": "extraction",
  "total_dashboards": 13,
  "completed_dashboards": 5,
  "failed_dashboards": 0,
  "dashboards": {
    "842": {
      "dashboard_id": 842,
      "status": "processing",
      "current_phase": "Phase 4: Table Metadata",
      "current_file": "842_table_metadata.csv",
      "completed_files": [
        "842_json.json",
        "842_csv.csv",
        "842_queries.sql",
        "842_tables_columns.csv"
      ],
      "total_files": 11,
      "completed_files_count": 4,
      "error": null,
      "start_time": "2024-11-19T21:00:00",
      "end_time": null
    }
  },
  "merge_status": {
    "status": "pending",
    "current_step": null,
    "completed_steps": []
  },
  "kb_build_status": {
    "status": "pending",
    "current_step": null
  },
  "start_time": "2024-11-19T21:00:00",
  "last_update": "2024-11-19T21:05:30"
}
```

## Available File Types for Download

- `json` - Dashboard JSON metadata
- `csv` - Dashboard CSV metadata
- `queries` - SQL queries
- `tables_columns` - Tables and columns mapping
- `tables_columns_enriched` - Enriched tables and columns
- `table_metadata` - Table metadata
- `columns_metadata` - Column metadata
- `joining_conditions` - Joining conditions
- `filter_conditions` - Filter conditions (TXT)
- `definitions` - Term definitions

## Services

### Backend API Server
- **Port**: 8000
- **URL**: http://localhost:8000
- **Status**: Running in background
- **Log**: `/tmp/api_server.log`

### Frontend React App
- **Port**: 3000
- **URL**: http://localhost:3000
- **Status**: Running in background
- **Log**: `/tmp/frontend.log`

## Example Workflow

1. **Start Processing**:
   ```
   Dashboard IDs: 585, 729, 476, 842, 511, 588, 964, 915, 567, 583, 657, 195, 249
   ```

2. **Monitor Progress**:
   - Dashboard 585: Processing → Phase 4: Table Metadata → Completed
   - Dashboard 729: Processing → Phase 2: Tables & Columns → ...
   - Dashboard 476: Pending → ...

3. **After Completion**:
   - Individual files in `extracted_meta/{dashboard_id}/`
   - Merged files in `extracted_meta/merged_metadata/`
   - Knowledge base in `extracted_meta/knowledge_base/`

4. **Download Files**:
   - Enter dashboard ID (e.g., 842)
   - View all available files
   - Download individual files or all as ZIP

## Troubleshooting

### Progress Not Updating
- Check if progress file exists: `extracted_meta/progress.json`
- Verify API server is running: `curl http://localhost:8000/api/progress`
- Check API server logs: `tail -f /tmp/api_server.log`

### Files Not Found
- Verify dashboard extraction completed successfully
- Check `extracted_meta/{dashboard_id}/` directory exists
- Verify file names match expected format

### Services Not Running
- Start backend: `cd metamind && source meta_env/bin/activate && python3 scripts/api_server.py &`
- Start frontend: `cd metamind/frontend && npm start &`

