"""
FastAPI server for Superset Dashboard Extractor Frontend

This server provides REST API endpoints to:
- List available dashboard files
- Extract dashboard information from a URL
- Serve JSON and CSV data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import re
import glob
import threading
from pathlib import Path
from query_extract import SupersetExtractor
from config import BASE_URL, HEADERS, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from sql_parser import extract_table_column_mapping
from llm_extractor import extract_table_column_mapping_llm
from trino_client import get_column_datatypes_from_trino
from dataclasses import asdict
from progress_tracker import get_progress_tracker
import zipfile
import shutil

app = FastAPI(title="Superset Dashboard Extractor API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        
        # Extract dashboard information
        dashboard_info = extractor.extract_dashboard_complete_info(dashboard_id)
        
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


class MultiDashboardRequest(BaseModel):
    dashboard_ids: List[int]
    extract: bool = True
    merge: bool = True
    build_kb: bool = True


@app.get("/api/progress")
async def get_progress():
    """Get current progress of multi-dashboard processing"""
    try:
        tracker = get_progress_tracker()
        progress = tracker.get_progress()
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting progress: {str(e)}")


@app.post("/api/dashboards/process-multiple")
async def process_multiple_dashboards(request: MultiDashboardRequest):
    """Process multiple dashboards: extract, merge, and build KB"""
    try:
        from process_multiple_dashboards import process_multiple_dashboards
        
        # Run in background thread
        def run_processing():
            try:
                process_multiple_dashboards(
                    dashboard_ids=request.dashboard_ids,
                    extract=request.extract,
                    merge=request.merge,
                    build_kb=request.build_kb,
                    continue_on_error=True
                )
            except Exception as e:
                import traceback
                print(f"Error in multi-dashboard processing: {str(e)}")
                print(traceback.format_exc())
        
        thread = threading.Thread(target=run_processing, daemon=True)
        thread.start()
        
        return {
            "success": True,
            "message": f"Processing {len(request.dashboard_ids)} dashboards in background",
            "dashboard_ids": request.dashboard_ids,
            "check_progress": "/api/progress"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting processing: {str(e)}")


@app.get("/api/dashboard/{dashboard_id}/files")
async def get_dashboard_files(dashboard_id: int):
    """Get list of all metadata files for a dashboard"""
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


@app.get("/api/dashboard/{dashboard_id}/download/{file_type}")
async def download_dashboard_file(dashboard_id: int, file_type: str):
    """Download a specific metadata file for a dashboard"""
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

