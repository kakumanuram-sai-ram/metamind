"""
FastAPI server for Superset Dashboard Extractor Frontend

This server provides REST API endpoints to:
- List available dashboard files
- Extract dashboard information from a URL
- Serve JSON and CSV data
"""

import sys
import os
from pathlib import Path

# Add scripts directory to Python path to allow imports
# This handles both running from project root (python scripts/api_server.py) 
# and from scripts directory (python api_server.py)
script_dir = Path(__file__).parent.absolute()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import re
import glob
import threading
from pathlib import Path
from query_extract import SupersetExtractor
from config import BASE_URL, HEADERS, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from sql_parser import extract_table_column_mapping
from trino_client import get_column_datatypes_from_trino
# Lazy import for llm_extractor to avoid dspy dependency at startup
def get_llm_extractor():
    try:
        from llm_extractor import extract_table_column_mapping_llm
        return extract_table_column_mapping_llm
    except ImportError:
        return None
from dataclasses import asdict
from progress_tracker import get_progress_tracker
import zipfile
import shutil
import logging
from datetime import datetime

# Configure logging for api_server and imported modules
def setup_api_logging():
    """Setup logging configuration for API server"""
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{logs_dir}/api_server_{timestamp}.log"
    
    # Configure root logger to capture all module logs
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=True  # Override any existing configuration
    )
    
    # Set specific log levels
    logging.getLogger('query_extract').setLevel(logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    
    return log_file

# Setup logging when module is imported
_log_file = setup_api_logging()
logger = logging.getLogger(__name__)
logger.info(f"API Server logging initialized. Log file: {_log_file}")

app = FastAPI(title="Superset Dashboard Extractor API")

# Add favicon endpoint to avoid 404 errors
@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)  # No Content - browser will use default

# Add request logging middleware with selective logging to reduce noise
@app.middleware("http")
async def log_requests(request, call_next):
    import sys
    import time

    start_time = time.time()

    # Skip logging for these paths to reduce noise
    skip_logging_paths = [
        '/api/progress',
        '/api/knowledge-base/download',
    ]

    # Check if we should skip logging
    should_skip = any(skip_path in request.url.path for skip_path in skip_logging_paths)

    # Process request
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Log only if not skipped AND (error OR POST request)
        if not should_skip and (response.status_code >= 400 or request.method == 'POST'):
            logger.info(f"[{request.method}] {request.url.path} | Status: {response.status_code} | Duration: {duration:.2f}ms")

        return response
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"[REQUEST ERROR] {request.method} {request.url.path} | Error: {str(e)} | Duration: {duration:.2f}ms", exc_info=True)
        raise

# Enable CORS for React frontend - allow all origins for EC2 access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for EC2 access (can restrict later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


class DashboardExtractRequest(BaseModel):
    dashboard_url: str
    dashboard_id: Optional[int] = None


class DashboardFile(BaseModel):
    dashboard_id: int
    dashboard_title: str
    json_file: str
    csv_file: str
    sql_file: Optional[str] = None
    dashboard_url: str


def extract_dashboard_id_from_url(url: str) -> Optional[int]:
    """Extract dashboard ID from Superset dashboard URL"""
    # Pattern: /dashboard/{id}/ or /dashboard/{id}
    match = re.search(r'/dashboard/(\d+)', url)
    if match:
        return int(match.group(1))
    return None


def find_dashboard_files() -> List[DashboardFile]:
    """Find all dashboard JSON and CSV files in the current directory"""
    dashboard_files = []
    
    # Find all JSON files matching pattern
    json_files = glob.glob("extracted_meta/*_json.json")
    
    for json_file in json_files:
        # Extract dashboard ID from filename
        match = re.search(r'(\d+)_json\.json', json_file)
        if not match:
            continue
        
        dashboard_id = int(match.group(1))
        
        # Find corresponding CSV and SQL files
        csv_file = f"extracted_meta/{dashboard_id}_csv.csv"
        sql_file = f"extracted_meta/{dashboard_id}_queries.sql"
        
        # Read dashboard title from JSON
        dashboard_title = "Unknown"
        dashboard_url = ""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                dashboard_title = data.get('dashboard_title', 'Unknown')
                dashboard_url = data.get('dashboard_url', '')
        except:
            pass
        
        dashboard_files.append(DashboardFile(
            dashboard_id=dashboard_id,
            dashboard_title=dashboard_title,
            json_file=json_file if os.path.exists(json_file) else "",
            csv_file=csv_file if os.path.exists(csv_file) else "",
            sql_file=sql_file if os.path.exists(sql_file) else None,
            dashboard_url=dashboard_url
        ))
    
    return sorted(dashboard_files, key=lambda x: x.dashboard_id, reverse=True)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Superset Dashboard Extractor API", "version": "1.0.0"}


@app.get("/api/dashboards", response_model=List[DashboardFile])
async def list_dashboards():
    """List all available dashboard files"""
    try:
        dashboards = find_dashboard_files()
        return dashboards
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/{dashboard_id}/json")
async def get_dashboard_json(dashboard_id: int):
    """Get dashboard JSON data"""
    json_file = f"extracted_meta/{dashboard_id}_json.json"
    
    if not os.path.exists(json_file):
        raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} JSON file not found")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading JSON file: {str(e)}")


@app.get("/api/dashboard/{dashboard_id}/csv")
async def get_dashboard_csv(dashboard_id: int):
    """Get dashboard CSV data as JSON"""
    import pandas as pd
    import numpy as np
    
    csv_file = f"extracted_meta/{dashboard_id}_csv.csv"
    
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} CSV file not found")
    
    try:
        df = pd.read_csv(csv_file)
        
        # Replace NaN, Infinity, and -Infinity with None (which becomes null in JSON)
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        
        # Convert DataFrame to JSON
        return {
            "columns": df.columns.tolist(),
            "data": df.to_dict('records'),
            "total_rows": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV file: {str(e)}")


@app.get("/api/dashboard/{dashboard_id}/json/download")
async def download_dashboard_json(dashboard_id: int):
    """Download dashboard JSON file"""
    json_file = f"extracted_meta/{dashboard_id}_json.json"
    
    if not os.path.exists(json_file):
        raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} JSON file not found")
    
    return FileResponse(
        json_file,
        media_type='application/json',
        filename=os.path.basename(json_file)
    )


@app.get("/api/dashboard/{dashboard_id}/csv/download")
async def download_dashboard_csv(dashboard_id: int):
    """Download dashboard CSV file"""
    csv_file = f"extracted_meta/{dashboard_id}_csv.csv"
    
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} CSV file not found")
    
    return FileResponse(
        csv_file,
        media_type='text/csv',
        filename=os.path.basename(csv_file)
    )


@app.get("/api/dashboard/{dashboard_id}/tables-columns")
async def get_dashboard_tables_columns(dashboard_id: int):
    """Get dashboard tables and columns mapping"""
    import pandas as pd
    
    json_file = f"extracted_meta/{dashboard_id}_json.json"
    csv_file = f"extracted_meta/{dashboard_id}_tables_columns.csv"
    
    if not os.path.exists(json_file):
        raise HTTPException(
            status_code=404, 
            detail=f"Dashboard {dashboard_id} JSON file not found. Please extract the dashboard first."
        )
    
    try:
        # First, try to read from existing CSV file (if LLM extraction completed)
        if os.path.exists(csv_file) and os.path.getsize(csv_file) > 10:  # More than just headers
            try:
                df = pd.read_csv(csv_file)
                # Filter out rows with empty column_name (fix for old format)
                if 'column_name' in df.columns:
                    df = df[df['column_name'].notna() & (df['column_name'] != '')]
                if len(df) > 0:
                    return {
                        "columns": df.columns.tolist(),
                        "data": df.to_dict('records'),
                        "total_rows": len(df)
                    }
            except Exception as e:
                print(f"Error reading CSV file, will re-extract: {str(e)}")
        
        # If CSV doesn't exist or is empty, extract from JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            dashboard_info = json.load(f)
        
        # For view endpoint, use rule-based extraction (faster, no thread issues)
        # LLM extraction happens during initial extraction in background
        print("Using rule-based extraction for fast response...")
        try:
            trino_columns = get_column_datatypes_from_trino(dashboard_info, BASE_URL, HEADERS)
        except Exception as e:
            print(f"Trino query failed (will continue without data types): {str(e)}")
            trino_columns = {}
        table_column_mapping = extract_table_column_mapping(dashboard_info, trino_columns)
        
        if not table_column_mapping:
            return {
                "columns": ["table_name", "column_name", "column_label__chart_json", "data_type"],
                "data": [],
                "total_rows": 0,
                "message": "No tables and columns found in dashboard charts"
            }
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(table_column_mapping)
        
        # Filter out rows with empty column_name (should not happen, but as safeguard)
        if 'column_name' in df.columns:
            df = df[df['column_name'].notna() & (df['column_name'] != '')]
        
        # Replace NaN, Infinity, and -Infinity with None (JSON compliant)
        import numpy as np
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)
        
        # Convert to dict and clean any remaining float issues
        data_dict = df.to_dict('records')
        for row in data_dict:
            for key, value in row.items():
                if isinstance(value, (float, np.floating)):
                    if np.isnan(value) or np.isinf(value):
                        row[key] = None
                    elif not np.isfinite(value):
                        row[key] = None
        
        # Save to CSV for future use
        df.to_csv(csv_file, index=False)
        
        return {
            "columns": df.columns.tolist(),
            "data": data_dict,
            "total_rows": len(df)
        }
    except Exception as e:
        import traceback
        error_detail = f"Error processing tables and columns: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/dashboard/{dashboard_id}/tables-columns/download")
async def download_dashboard_tables_columns(dashboard_id: int):
    """Download dashboard tables and columns CSV file"""
    csv_file = f"extracted_meta/{dashboard_id}_tables_columns.csv"
    
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} tables-columns file not found")
    
    return FileResponse(
        csv_file,
        media_type='text/csv',
        filename=os.path.basename(csv_file)
    )


@app.post("/api/dashboard/extract")
async def extract_dashboard(request: DashboardExtractRequest):
    """Extract dashboard information from a URL"""
    try:
        # Extract dashboard ID from URL if not provided
        dashboard_id = request.dashboard_id
        if not dashboard_id:
            dashboard_id = extract_dashboard_id_from_url(request.dashboard_url)
        
        if not dashboard_id:
            raise HTTPException(
                status_code=400,
                detail="Could not extract dashboard ID from URL. Please provide dashboard_id."
            )
        
        # Initialize extractor
        extractor = SupersetExtractor(BASE_URL, HEADERS)
        
        # Extract dashboard information (with timeout handling)
        try:
            dashboard_info = extractor.extract_dashboard_complete_info(dashboard_id)
        except Exception as e:
            import traceback
            error_msg = f"Error extracting dashboard {dashboard_id}: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract dashboard: {str(e)}. Check backend logs for details."
            )
        
        # Create extracted_meta directory if it doesn't exist
        os.makedirs("extracted_meta", exist_ok=True)
        
        # Export to files (FAST - script-based, no LLM)
        extractor.export_to_json(dashboard_info)
        extractor.export_to_csv(dashboard_info)
        extractor.export_sql_queries(dashboard_info)
        
        # Extract table and column mapping using LLM (SLOW - runs after JSON/CSV)
        # This is done asynchronously to not block the response
        use_llm = os.getenv("USE_LLM_EXTRACTION", "true").lower() == "true"
        
        if use_llm:
            print("Note: LLM-based table/column extraction will run in background...")
            # Run LLM extraction in background to not block the response
            
            def run_llm_extraction():
                try:
                    print("Starting LLM-based extraction...")
                    # Get API key from env, config, or use default
                    api_key = os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
                    if not api_key:
                        raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
                    
                    # Use model and base_url from config
                    model = LLM_MODEL
                    base_url = LLM_BASE_URL
                    
                    # Extract source tables and columns (only source tables/columns, no derived columns)
                    from llm_extractor import extract_source_tables_columns_llm
                    table_column_mapping = extract_source_tables_columns_llm(
                        asdict(dashboard_info), 
                        api_key=api_key, 
                        model=model,
                        base_url=base_url
                    )
                    
                    # Save table-column mapping to CSV
                    import pandas as pd
                    dashboard_dir = f"extracted_meta/{dashboard_id}"
                    os.makedirs(dashboard_dir, exist_ok=True)
                    mapping_df = pd.DataFrame(table_column_mapping)
                    mapping_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
                    mapping_df.to_csv(mapping_file, index=False)
                    print(f"LLM extraction completed. Saved to {mapping_file}")
                    
                    # Generate comprehensive metadata files
                    print("Generating comprehensive metadata files...")
                    from metadata_generator import generate_all_metadata
                    generate_all_metadata(dashboard_id, api_key, model=model)
                    print("✅ All metadata files generated successfully!")
                except Exception as e:
                    import traceback
                    print(f"Error in LLM extraction: {str(e)}")
                    print(traceback.format_exc())
            
            # Run in background thread
            thread = threading.Thread(target=run_llm_extraction, daemon=True)
            thread.start()
        else:
            # Fallback to rule-based extraction (faster)
            print("Using rule-based extraction...")
            trino_columns = get_column_datatypes_from_trino(asdict(dashboard_info), BASE_URL, HEADERS)
            table_column_mapping = extract_table_column_mapping(asdict(dashboard_info), trino_columns)
            
            # Save table-column mapping to CSV
            import pandas as pd
            mapping_df = pd.DataFrame(table_column_mapping)
            mapping_file = f"dashboard_{dashboard_id}_tables_columns.csv"
            mapping_df.to_csv(mapping_file, index=False)
        
        return {
            "success": True,
            "dashboard_id": dashboard_id,
            "dashboard_title": dashboard_info.dashboard_title,
            "dashboard_url": dashboard_info.dashboard_url,
            "total_charts": len(dashboard_info.charts),
            "message": f"Dashboard {dashboard_id} extracted successfully. JSON and CSV files created. LLM extraction running in background."
        }
    except Exception as e:
        # Check if it's an HTTP error (from requests library)
        if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
            if e.response.status_code == 401:
                error_detail = (
                    "Authentication failed: Your session cookie has expired. "
                    "Please update the Cookie and X-CSRFToken in config.py. "
                    "See AUTHORIZATION.md for instructions on how to get fresh credentials."
                )
                raise HTTPException(status_code=401, detail=error_detail)
        raise HTTPException(status_code=500, detail=f"Error extracting dashboard: {str(e)}")


class DashboardMetadataChoice(BaseModel):
    dashboard_id: int
    use_existing: bool  # True = use existing, False = create fresh

class MultiDashboardRequest(BaseModel):
    dashboard_ids: List[int]
    extract: bool = True
    merge: bool = True
    build_kb: bool = True
    metadata_choices: Optional[Dict[int, bool]] = None  # dashboard_id -> use_existing


@app.get("/api/progress")
async def get_progress():
    """Get current progress of multi-dashboard processing"""
    import sys
    try:
        tracker = get_progress_tracker()
        progress = tracker.get_progress()
        
        # Check if KB build is complete but all files aren't ready yet
        # If KB build status is 'completed', mark it as completed (don't re-check old dashboard IDs)
        kb_status = progress.get('kb_build_status', {}).get('status')
        if kb_status == 'completed':
            # KB build is completed - ensure status reflects this
            # Don't re-check files for old dashboard IDs that may be in progress from previous runs
            if progress.get('status') != 'completed':
                progress['status'] = 'completed'
                progress['current_operation'] = None
        
        # Only log progress when status changes significantly (not on every poll)
        # This reduces log noise from frequent frontend polling
        
        return progress
    except Exception as e:
        print(f"[API] GET /api/progress - ERROR: {str(e)}", flush=True)
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=f"Error getting progress: {str(e)}")


@app.post("/api/dashboards/process-multiple")
async def process_multiple_dashboards(request: MultiDashboardRequest):
    """Process multiple dashboards: extract, merge, and build KB"""
    import sys
    try:
        print(f"\n{'='*80}", flush=True)
        print(f"[API] 📋 Processing request for dashboards: {request.dashboard_ids}", flush=True)
        print(f"   📋 Request received from UI", flush=True)
        print(f"   📊 Dashboard IDs: {request.dashboard_ids}", flush=True)
        print(f"   ⚙️  Extract: {request.extract}, Merge: {request.merge}, Build KB: {request.build_kb}", flush=True)
        print(f"{'='*80}", flush=True)
        sys.stdout.flush()
        
        # Run in background thread
        def run_processing():
            import sys
            import os
            sys.stdout.flush()
            sys.stderr.flush()
            try:
                # Try to activate virtual environment if available
                script_dir = os.path.dirname(os.path.abspath(__file__))
                metamind_dir = os.path.dirname(script_dir)
                venv_python = os.path.join(metamind_dir, "meta_env", "bin", "python")
                
                # If virtual env exists, use it; otherwise use current Python
                if os.path.exists(venv_python):
                    # Add venv site-packages to path
                    venv_site_packages = os.path.join(metamind_dir, "meta_env", "lib", "python3.11", "site-packages")
                    if os.path.exists(venv_site_packages):
                        sys.path.insert(0, venv_site_packages)
                    # Also add scripts directory
                    sys.path.insert(0, script_dir)
                
                # Initialize progress tracker for new extraction
                try:
                    from progress_tracker import get_progress_tracker
                    tracker = get_progress_tracker()
                    if request.extract:
                        tracker.start_extraction(request.dashboard_ids)
                except Exception as tracker_error:
                    print(f"⚠️  Failed to initialize progress tracker: {tracker_error}", flush=True)
                
                print(f"\n{'='*80}", flush=True)
                print(f"🚀 Starting multi-dashboard processing", flush=True)
                print(f"   Dashboard IDs: {request.dashboard_ids}", flush=True)
                print(f"   Extract: {request.extract}, Merge: {request.merge}, Build KB: {request.build_kb}", flush=True)
                print(f"   Python: {sys.executable}", flush=True)
                print(f"{'='*80}\n", flush=True)
                
                # Process metadata choices
                metadata_choices = request.metadata_choices or {}
                
                # Convert metadata_choices dict to proper format
                choices_dict = {}
                if request.metadata_choices:
                    choices_dict = {int(k): bool(v) for k, v in request.metadata_choices.items()}
                
                # Change to metamind directory for proper file paths
                original_cwd = os.getcwd()
                try:
                    os.chdir(metamind_dir)
                    
                    # Import here after path is set
                    from process_multiple_dashboards import process_multiple_dashboards
                    
                    process_multiple_dashboards(
                        dashboard_ids=request.dashboard_ids,
                        extract=request.extract,
                        merge=request.merge,
                        build_kb=request.build_kb,
                        continue_on_error=True,
                        metadata_choices=choices_dict
                    )
                finally:
                    os.chdir(original_cwd)
                
                print(f"\n{'='*80}", flush=True)
                print(f"✅ Multi-dashboard processing completed", flush=True)
                print(f"{'='*80}\n", flush=True)
            except Exception as e:
                import traceback
                error_msg = str(e)
                error_trace = traceback.format_exc()
                print(f"\n{'='*80}", flush=True)
                print(f"❌ Error in multi-dashboard processing: {error_msg}", flush=True)
                print(f"{'='*80}", flush=True)
                print(error_trace, flush=True)
                
                # Update progress tracker with error
                try:
                    from progress_tracker import get_progress_tracker
                    tracker = get_progress_tracker()
                    for dashboard_id in request.dashboard_ids:
                        tracker.update_dashboard_status(
                            dashboard_id,
                            'error',
                            error=error_msg
                        )
                except Exception as tracker_error:
                    print(f"⚠️  Failed to update progress tracker: {tracker_error}", flush=True)
        
        thread = threading.Thread(target=run_processing, daemon=True)
        thread.start()
        
        print(f"[API] ✅ Background processing thread started", flush=True)
        print(f"[API] 📡 Returning response to UI", flush=True)
        sys.stdout.flush()
        
        return {
            "success": True,
            "message": f"Processing {len(request.dashboard_ids)} dashboards in background",
            "dashboard_ids": request.dashboard_ids,
            "check_progress": "/api/progress"
        }
    except Exception as e:
        print(f"[API] ❌ ERROR in /api/dashboards/process-multiple: {str(e)}", flush=True)
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=f"Error starting processing: {str(e)}")


@app.get("/api/dashboard/{dashboard_id}/files")
async def get_dashboard_files(dashboard_id: int):
    """Get list of all metadata files for a dashboard"""
    import sys
    # Removed verbose logging - only log on errors
    sys.stdout.flush()
    try:
        dashboard_dir = f"extracted_meta/{dashboard_id}"
        
        if not os.path.exists(dashboard_dir):
            raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} not found")
        
        files = []
        file_types = [
            ("json", f"{dashboard_id}_json.json", "JSON"),
            ("csv", f"{dashboard_id}_csv.csv", "CSV"),
            ("queries", f"{dashboard_id}_queries.sql", "SQL"),
            ("tables_columns", f"{dashboard_id}_tables_columns.csv", "CSV"),
            ("tables_columns_enriched", f"{dashboard_id}_tables_columns_enriched.csv", "CSV"),
            ("table_metadata", f"{dashboard_id}_table_metadata.csv", "CSV"),
            ("columns_metadata", f"{dashboard_id}_columns_metadata.csv", "CSV"),
            ("joining_conditions", f"{dashboard_id}_joining_conditions.csv", "CSV"),
            ("filter_conditions", f"{dashboard_id}_filter_conditions.txt", "TXT"),
            ("definitions", f"{dashboard_id}_definitions.csv", "CSV")
        ]
        
        for file_type, filename, file_format in file_types:
            filepath = os.path.join(dashboard_dir, filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                files.append({
                    "type": file_type,
                    "filename": filename,
                    "format": file_format,
                    "size": file_size,
                    "download_url": f"/api/dashboard/{dashboard_id}/download/{file_type}"
                })
        
        return {
            "dashboard_id": dashboard_id,
            "files": files,
            "total_files": len(files)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting files: {str(e)}")


@app.get("/api/dashboard/{dashboard_id}/file/{file_type}")
async def get_dashboard_file_content(dashboard_id: int, file_type: str):
    """Get metadata file content as JSON (for display in UI)"""
    import pandas as pd
    import numpy as np
    import json

    file_mapping = {
        "table_metadata": f"{dashboard_id}_table_metadata.csv",
        "columns_metadata": f"{dashboard_id}_columns_metadata.csv",
        "joining_conditions": f"{dashboard_id}_joining_conditions.csv",
        "filter_conditions": f"{dashboard_id}_filter_conditions.txt",
        "definitions": f"{dashboard_id}_definitions.csv"
    }

    if file_type not in file_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file_type}")

    filename = file_mapping[file_type]
    # Get the script directory and construct path relative to metamind directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    metamind_dir = os.path.dirname(script_dir)
    filepath = os.path.join(metamind_dir, "extracted_meta", str(dashboard_id), filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    try:
        # Handle TXT files (filter_conditions)
        if file_type == "filter_conditions":
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return JSONResponse({
                "type": "text",
                "content": content,
                "filename": filename
            })

        # Handle CSV files
        df = pd.read_csv(filepath)

        # Replace NaN, Infinity, and -Infinity with None (JSON compliant)
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notnull(df), None)

        # Convert DataFrame to records with proper type handling
        data = []
        for record in df.to_dict('records'):
            converted_record = {}
            for key, val in record.items():
                # Handle all numpy types and missing values
                if pd.isna(val) or val is None:
                    converted_record[key] = None
                elif isinstance(val, (np.integer, np.int64, np.int32)):
                    converted_record[key] = int(val)
                elif isinstance(val, (np.floating, np.float64, np.float32)):
                    # Make sure it's a valid float
                    float_val = float(val)
                    if np.isfinite(float_val):
                        converted_record[key] = float_val
                    else:
                        converted_record[key] = None
                elif isinstance(val, (np.bool_, bool)):
                    converted_record[key] = bool(val)
                else:
                    # Convert to string if it's not a standard type
                    converted_record[key] = str(val)
            data.append(converted_record)

        # Use JSONResponse with default handler to ensure proper encoding
        response_data = {
            "type": "csv",
            "columns": df.columns.tolist(),
            "data": data,
            "total_rows": len(df),
            "filename": filename
        }

        return JSONResponse(response_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@app.get("/api/dashboard/{dashboard_id}/download/{file_type}")
async def download_dashboard_file(dashboard_id: int, file_type: str):
    """Download a specific metadata file for a dashboard"""
    import sys
    # Removed verbose logging - only log on errors
    sys.stdout.flush()
    try:
        file_mapping = {
            "json": f"{dashboard_id}_json.json",
            "csv": f"{dashboard_id}_csv.csv",
            "queries": f"{dashboard_id}_queries.sql",
            "tables_columns": f"{dashboard_id}_tables_columns.csv",
            "tables_columns_enriched": f"{dashboard_id}_tables_columns_enriched.csv",
            "table_metadata": f"{dashboard_id}_table_metadata.csv",
            "columns_metadata": f"{dashboard_id}_columns_metadata.csv",
            "joining_conditions": f"{dashboard_id}_joining_conditions.csv",
            "filter_conditions": f"{dashboard_id}_filter_conditions.txt",
            "definitions": f"{dashboard_id}_definitions.csv"
        }
        
        if file_type not in file_mapping:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file_type}")
        
        filename = file_mapping[file_type]
        filepath = f"extracted_meta/{dashboard_id}/{filename}"
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Determine media type
        media_types = {
            "json": "application/json",
            "csv": "text/csv",
            "sql": "text/plain",
            "txt": "text/plain"
        }
        ext = filename.split('.')[-1]
        media_type = media_types.get(ext, "application/octet-stream")
        
        return FileResponse(
            filepath,
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@app.get("/api/dashboard/{dashboard_id}/download-all")
async def download_all_dashboard_files(dashboard_id: int):
    """Download all metadata files for a dashboard as a ZIP archive"""
    try:
        dashboard_dir = f"extracted_meta/{dashboard_id}"
        
        if not os.path.exists(dashboard_dir):
            raise HTTPException(status_code=404, detail=f"Dashboard {dashboard_id} not found")
        
        # Create temporary ZIP file
        zip_filename = f"dashboard_{dashboard_id}_metadata.zip"
        zip_path = f"extracted_meta/{zip_filename}"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files in dashboard directory
            for root, dirs, files in os.walk(dashboard_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, dashboard_dir)
                    zipf.write(file_path, arcname)
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ZIP: {str(e)}")


@app.get("/api/knowledge-base/download")
@app.head("/api/knowledge-base/download")
async def download_knowledge_base_zip():
    """Download the knowledge base ZIP file (supports GET and HEAD for file existence checks)"""
    # Removed verbose logging - only log on errors
    try:
        kb_zip_path = "extracted_meta/knowledge_base/knowledge_base.zip"
        
        if not os.path.exists(kb_zip_path):
            raise HTTPException(status_code=404, detail="Knowledge base ZIP file not found. Please wait for processing to complete.")
        
        return FileResponse(
            kb_zip_path,
            media_type="application/zip",
            filename="knowledge_base.zip"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading knowledge base ZIP: {str(e)}")


@app.post("/api/knowledge-base/connect-n8n")
async def connect_to_n8n():
    """Connect to N8N workflow and upload knowledge base"""
    import sys
    import subprocess
    # Removed verbose logging - only log on errors
    sys.stdout.flush()
    try:
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        n8n_script = os.path.join(script_dir, "n8n_kb_upload.py")
        
        if not os.path.exists(n8n_script):
            raise HTTPException(status_code=500, detail="N8N upload script not found")
        
        # Run the n8n upload script
        result = subprocess.run(
            ["python", n8n_script],
            capture_output=True,
            text=True,
            cwd=script_dir,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Successfully connected to N8N and uploaded knowledge base",
                "output": result.stdout
            }
        else:
            error_msg = result.stderr or result.stdout or "Unknown error"
            return {
                "success": False,
                "message": f"Failed to connect to N8N: {error_msg}",
                "error": error_msg
            }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="N8N connection timed out")
    except Exception as e:
        import traceback
        error_detail = f"Error connecting to N8N: {str(e)}\n{traceback.format_exc()}"
        print(f"[API] ERROR: {error_detail}", flush=True)
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/knowledge-base/enable-prism")
async def enable_on_prism():
    """Enable knowledge base on Prism"""
    import sys
    import subprocess
    # Removed verbose logging - only log on errors
    sys.stdout.flush()
    try:
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prism_script = os.path.join(script_dir, "prism_api_client.py")
        
        if not os.path.exists(prism_script):
            raise HTTPException(status_code=500, detail="Prism API client script not found")
        
        # Run the prism script
        result = subprocess.run(
            ["python", prism_script],
            capture_output=True,
            text=True,
            cwd=script_dir,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Successfully enabled knowledge base on Prism",
                "output": result.stdout
            }
        else:
            error_msg = result.stderr or result.stdout or "Unknown error"
            return {
                "success": False,
                "message": f"Failed to enable on Prism: {error_msg}",
                "error": error_msg
            }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Prism connection timed out")
    except Exception as e:
        import traceback
        error_detail = f"Error enabling on Prism: {str(e)}\n{traceback.format_exc()}"
        print(f"[API] ERROR: {error_detail}", flush=True)
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=error_detail)


if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Get port from environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Ensure all output is flushed immediately
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    
    print("\n" + "="*80, flush=True)
    print("🚀 Starting MetaMind API Server", flush=True)
    print("="*80, flush=True)
    print(f"📍 Server will be available at: http://localhost:{port}", flush=True)
    print(f"📚 API docs will be available at: http://localhost:{port}/docs", flush=True)
    print("📊 All API requests and backend activity will be logged here", flush=True)
    print("="*80 + "\n", flush=True)
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

