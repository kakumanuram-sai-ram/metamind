"""
Script to extract dashboard metadata (Phases 1, 2, 3, 4, 5, 6, 7 & 8) with timing logs

This script:
1. Extracts dashboard information from Superset (Phase 1)
2. Extracts tables, columns, and derived logic using LLM (Phase 2)
3. Enriches source columns with datatypes from Trino (Phase 3)
4. Generates table metadata using LLM (Phase 4)
5. Generates column metadata using LLM (Phase 5)
6. Generates joining conditions metadata using LLM (Phase 6)
7. Generates filter conditions documentation using LLM (Phase 7)
8. Generates term definitions using LLM (Phase 8)
9. Saves all outputs in extracted_meta/{dashboard_id}/ folder
10. Logs timing for each step
"""
import os
import sys
import time
from datetime import datetime
from query_extract import SupersetExtractor
from config import BASE_URL, HEADERS, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from llm_extractor import extract_source_tables_columns_llm, extract_table_metadata_llm, extract_column_metadata_llm, extract_joining_conditions_llm, generate_filter_conditions_llm, extract_term_definitions_llm
from chart_level_extractor import (
    process_charts_for_table_metadata,
    process_charts_for_column_metadata,
    process_charts_for_joining_conditions,
    process_charts_for_filter_conditions,
    process_charts_for_definitions,
    merge_chart_table_metadata,
    merge_chart_column_metadata,
    merge_chart_joining_conditions,
    merge_chart_filter_conditions,
    merge_chart_definitions
)
from starburst_schema_fetcher import fetch_schemas_for_tables, normalize_table_name
import pandas as pd
import json


def extract_dashboard_with_timing(dashboard_id: int, progress_tracker=None):
    """
    Extract dashboard metadata with timing logs
    
    Args:
        dashboard_id: Dashboard ID to extract
        progress_tracker: Optional ProgressTracker instance for progress updates
    """
    import sys
    # Ensure print statements are flushed immediately
    sys.stdout.flush()
    sys.stderr.flush()
    
    start_time = time.time()
    print(f"\n{'='*80}", flush=True)
    print(f"Starting extraction for Dashboard ID: {dashboard_id}", flush=True)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"{'='*80}\n", flush=True)
    
    # Create dashboard directory
    dashboard_dir = f"extracted_meta/{dashboard_id}"
    os.makedirs(dashboard_dir, exist_ok=True)
    
    # ============================================================
    # PHASE 1: Dashboard Extraction (Fast - No LLM)
    # ============================================================
    print("\n" + "="*80, flush=True)
    print("PHASE 1: Dashboard Extraction from Superset", flush=True)
    print("="*80, flush=True)
    phase1_start = time.time()
    
    try:
        # Step 1.1: Initialize extractor
        step_start = time.time()
        print("\n[Step 1.1] Initializing SupersetExtractor...", flush=True)
        extractor = SupersetExtractor(BASE_URL, HEADERS)
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        
        # Step 1.2: Extract dashboard complete info
        step_start = time.time()
        print("\n[Step 1.2] Extracting dashboard information from Superset API...", flush=True)
        dashboard_info = extractor.extract_dashboard_complete_info(dashboard_id)
        step_time = time.time() - step_start
        num_charts = len(dashboard_info.charts)
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  📊 Found {num_charts} charts in dashboard", flush=True)
        
        # Step 1.3: Export to JSON
        step_start = time.time()
        print("\n[Step 1.3] Exporting dashboard info to JSON...", flush=True)
        if progress_tracker:
            progress_tracker.update_dashboard_status(
                dashboard_id, 'processing', 
                current_phase='Phase 1: Dashboard Extraction',
                current_file=f"{dashboard_id}_json.json"
            )
        extractor.export_to_json(dashboard_info)
        step_time = time.time() - step_start
        json_file = f"{dashboard_dir}/{dashboard_id}_json.json"
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  💾 Saved to: {json_file}", flush=True)
        if progress_tracker:
            progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_json.json")
        
        # Step 1.4: Export to CSV
        step_start = time.time()
        print("\n[Step 1.4] Exporting chart metadata to CSV...", flush=True)
        if progress_tracker:
            progress_tracker.update_dashboard_status(
                dashboard_id, 'processing',
                current_phase='Phase 1: Dashboard Extraction',
                current_file=f"{dashboard_id}_csv.csv"
            )
        extractor.export_to_csv(dashboard_info)
        step_time = time.time() - step_start
        csv_file = f"{dashboard_dir}/{dashboard_id}_csv.csv"
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  💾 Saved to: {csv_file}", flush=True)
        if progress_tracker:
            progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_csv.csv")
        
        # Step 1.5: Export SQL queries
        step_start = time.time()
        print("\n[Step 1.5] Exporting SQL queries...", flush=True)
        if progress_tracker:
            progress_tracker.update_dashboard_status(
                dashboard_id, 'processing',
                current_phase='Phase 1: Dashboard Extraction',
                current_file=f"{dashboard_id}_queries.sql"
            )
        extractor.export_sql_queries(dashboard_info)
        step_time = time.time() - step_start
        sql_file = f"{dashboard_dir}/{dashboard_id}_queries.sql"
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  💾 Saved to: {sql_file}", flush=True)
        if progress_tracker:
            progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_queries.sql")
        
        phase1_time = time.time() - phase1_start
        print(f"\n{'─'*80}", flush=True)
        print(f"✅ PHASE 1 COMPLETED in {phase1_time:.2f} seconds ({phase1_time/60:.2f} minutes)", flush=True)
        print(f"{'─'*80}", flush=True)
        
    except Exception as e:
        phase1_time = time.time() - phase1_start
        print(f"\n❌ PHASE 1 FAILED after {phase1_time:.2f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # PHASE 2: LLM Extraction (Slow - Uses Claude API)
    # ============================================================
    print("\n" + "="*80, flush=True)
    print("PHASE 2: LLM-based Table/Column Extraction", flush=True)
    print("="*80, flush=True)
    phase2_start = time.time()
    
    try:
        # Step 2.1: Get API key and config
        step_start = time.time()
        print("\n[Step 2.1] Loading LLM configuration...", flush=True)
        api_key = os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
        if not api_key:
            raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
        model = LLM_MODEL
        base_url = LLM_BASE_URL
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  🔑 API Key: {'*' * 20}...{api_key[-4:] if len(api_key) > 4 else '****'}", flush=True)
        print(f"  🤖 Model: {model}", flush=True)
        print(f"  🌐 Base URL: {base_url}", flush=True)
        
        # Step 2.2: Extract tables and columns using LLM
        step_start = time.time()
        print(f"\n[Step 2.2] Extracting tables, columns, and derived logic using LLM...", flush=True)
        print(f"  Processing {num_charts} charts...", flush=True)
        
        # Convert dashboard_info to dict
        from dataclasses import asdict
        dashboard_dict = asdict(dashboard_info)
        
        table_column_mapping = extract_source_tables_columns_llm(
            dashboard_dict,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        step_time = time.time() - step_start
        num_mappings = len(table_column_mapping)
        print(f"  ✅ Completed in {step_time:.2f} seconds ({step_time/60:.2f} minutes)", flush=True)
        print(f"  📊 Extracted {num_mappings} table-column mappings", flush=True)
        print(f"  ⏱️  Average time per chart: {step_time/num_charts:.2f} seconds", flush=True)
        
        # Step 2.3: Save to CSV
        step_start = time.time()
        print("\n[Step 2.3] Saving table-column mappings to CSV...", flush=True)
        mapping_df = pd.DataFrame(table_column_mapping)
        mapping_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
        mapping_df.to_csv(mapping_file, index=False)
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  💾 Saved to: {mapping_file}", flush=True)
        print(f"  📊 Rows: {len(mapping_df)}", flush=True)
        print(f"  📋 Columns: {', '.join(mapping_df.columns.tolist())}", flush=True)
        
        # Step 2.4: Save to JSON (for easy inspection)
        step_start = time.time()
        print("\n[Step 2.4] Saving table-column mappings to JSON...", flush=True)
        json_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.json"
        mapping_df.to_json(json_file, orient='records', indent=2)
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  💾 Saved to: {json_file}", flush=True)
        
        phase2_time = time.time() - phase2_start
        print(f"\n{'─'*80}", flush=True)
        print(f"✅ PHASE 2 COMPLETED in {phase2_time:.2f} seconds ({phase2_time/60:.2f} minutes)", flush=True)
        print(f"{'─'*80}", flush=True)
        
    except Exception as e:
        phase2_time = time.time() - phase2_start
        print(f"\n❌ PHASE 2 FAILED after {phase2_time:.2f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # PHASE 3: Enrich with Trino Schema (Datatypes)
    # ============================================================
    print("\n" + "="*80, flush=True)
    print("PHASE 3: Enriching with Trino Schema (Datatypes)", flush=True)
    print("="*80, flush=True)
    phase3_start = time.time()
    
    try:
        # Step 3.1: Load tables_columns CSV
        step_start = time.time()
        print("\n[Step 3.1] Loading tables_columns CSV...", flush=True)
        mapping_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
        if not os.path.exists(mapping_file):
            raise FileNotFoundError(f"CSV file not found: {mapping_file}")
        
        df = pd.read_csv(mapping_file)
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  📊 Loaded {len(df)} rows from CSV", flush=True)
        
        # Step 3.2: Filter source columns only
        step_start = time.time()
        print("\n[Step 3.2] Filtering source columns...", flush=True)
        source_df = df[df['source_or_derived'] == 'source'].copy()
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  📊 Found {len(source_df)} source columns (out of {len(df)} total)", flush=True)
        
        if len(source_df) == 0:
            print("  ⚠️  No source columns found, skipping Phase 3", flush=True)
            phase3_time = time.time() - phase3_start
            print(f"\n{'─'*80}", flush=True)
            print(f"⚠️  PHASE 3 SKIPPED (no source columns)", flush=True)
            print(f"{'─'*80}", flush=True)
        else:
            # Step 3.3: Extract unique tables
            step_start = time.time()
            print("\n[Step 3.3] Extracting unique tables...", flush=True)
            unique_tables = source_df['tables_involved'].unique().tolist()
            # Normalize table names
            normalized_tables = [normalize_table_name(t) for t in unique_tables]
            # Remove duplicates
            unique_normalized = list(set(normalized_tables))
            step_time = time.time() - step_start
            print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
            print(f"  📊 Found {len(unique_normalized)} unique tables:", flush=True)
            for table in sorted(unique_normalized):
                print(f"    - {table}", flush=True)
            
            # Step 3.4: Fetch schemas from Trino
            step_start = time.time()
            print("\n[Step 3.4] Fetching schemas from Trino...", flush=True)
            print(f"  Connecting to Trino and describing {len(unique_normalized)} tables...", flush=True)
            schema_df = fetch_schemas_for_tables(
                unique_normalized,
                user_email="kakumanu.ram@paytm.com",
                normalize=False  # Already normalized
            )
            step_time = time.time() - step_start
            print(f"  ✅ Completed in {step_time:.2f} seconds ({step_time/60:.2f} minutes)", flush=True)
            print(f"  📊 Retrieved schema for {len(schema_df)} columns", flush=True)
            
            if len(schema_df) == 0:
                print("  ⚠️  No schema information retrieved from Trino", flush=True)
                phase3_time = time.time() - phase3_start
                print(f"\n{'─'*80}", flush=True)
                print(f"⚠️  PHASE 3 COMPLETED (no schema data) in {phase3_time:.2f} seconds", flush=True)
                print(f"{'─'*80}", flush=True)
            else:
                # Step 3.5: Merge datatypes back into CSV
                step_start = time.time()
                print("\n[Step 3.5] Merging datatypes into CSV...", flush=True)
                
                # Normalize table names in both dataframes for matching
                df['table_normalized'] = df['tables_involved'].apply(normalize_table_name)
                schema_df['table_normalized'] = schema_df['table_name'].apply(normalize_table_name)
                
                # Merge schema information into original dataframe
                # Match on normalized table name and column name
                df_enriched = df.merge(
                    schema_df[['table_normalized', 'column_name', 'column_datatype', 'extra', 'comment']],
                    left_on=['table_normalized', 'column_names'],
                    right_on=['table_normalized', 'column_name'],
                    how='left',
                    suffixes=('', '_schema')
                )
                
                # Drop temporary columns
                df_enriched = df_enriched.drop(columns=['table_normalized', 'column_name'])
                
                # Fill NaN values with empty string (for derived columns and source columns without schema)
                df_enriched['column_datatype'] = df_enriched['column_datatype'].fillna('')
                df_enriched['extra'] = df_enriched['extra'].fillna('')
                df_enriched['comment'] = df_enriched['comment'].fillna('')
                
                # Count how many source columns got datatypes
                source_with_datatype = df_enriched[
                    (df_enriched['source_or_derived'] == 'source') & 
                    (df_enriched['column_datatype'] != '')
                ]
                step_time = time.time() - step_start
                print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
                print(f"  📊 Enriched {len(source_with_datatype)} source columns with datatypes", flush=True)
                print(f"  📊 Total rows in enriched CSV: {len(df_enriched)}", flush=True)
                
                # Step 3.6: Save enriched CSV
                step_start = time.time()
                print("\n[Step 3.6] Saving enriched CSV with datatypes...", flush=True)
                enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns_enriched.csv"
                df_enriched.to_csv(enriched_file, index=False)
                step_time = time.time() - step_start
                print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
                print(f"  💾 Saved to: {enriched_file}", flush=True)
                print(f"  📋 Columns: {', '.join(df_enriched.columns.tolist())}", flush=True)
                if progress_tracker:
                    progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_tables_columns_enriched.csv")
                    progress_tracker.update_dashboard_status(
                        dashboard_id, 'processing',
                        current_phase='Phase 3: Schema Enrichment',
                        current_file=f"{dashboard_id}_tables_columns_enriched.csv"
                    )
                
                # Also update the original CSV with enriched data
                df_enriched.to_csv(mapping_file, index=False)
                print(f"  💾 Updated original CSV: {mapping_file}", flush=True)
                
                phase3_time = time.time() - phase3_start
                print(f"\n{'─'*80}", flush=True)
                print(f"✅ PHASE 3 COMPLETED in {phase3_time:.2f} seconds ({phase3_time/60:.2f} minutes)", flush=True)
                print(f"{'─'*80}", flush=True)
    
    except Exception as e:
        phase3_time = time.time() - phase3_start
        print(f"\n❌ PHASE 3 FAILED after {phase3_time:.2f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        # Don't return - continue to summary even if Phase 3 fails
    
    # ============================================================
    # PHASE 4: Generate Table Metadata using LLM
    # ============================================================
    print("\n" + "="*80, flush=True)
    print("PHASE 4: Generating Table Metadata using LLM", flush=True)
    print("="*80, flush=True)
    phase4_start = time.time()
    
    try:
        # Step 4.1: Load required data
        step_start = time.time()
        print("\n[Step 4.1] Loading dashboard info and tables_columns data...", flush=True)
        
        # Load dashboard JSON
        json_file = f"{dashboard_dir}/{dashboard_id}_json.json"
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Dashboard JSON not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            dashboard_info_dict = json.load(f)
        
        # Load enriched tables_columns CSV
        enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns_enriched.csv"
        if not os.path.exists(enriched_file):
            # Fallback to regular CSV
            enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
        
        if not os.path.exists(enriched_file):
            raise FileNotFoundError(f"Tables columns CSV not found: {enriched_file}")
        
        tables_columns_df = pd.read_csv(enriched_file)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  📊 Loaded dashboard: {dashboard_info_dict.get('dashboard_title', 'Unknown')}", flush=True)
        print(f"  📊 Loaded {len(tables_columns_df)} table-column mappings", flush=True)
        
        # Step 4.2: Extract table metadata using LLM (chart-by-chart for token optimization)
        step_start = time.time()
        print("\n[Step 4.2] Extracting table metadata using LLM (chart-by-chart)...", flush=True)
        
        charts = dashboard_info_dict.get('charts', [])
        print(f"  Processing {len(charts)} charts in parallel...", flush=True)
        
        # Get API key and config
        api_key = os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
        if not api_key:
            raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
        model = LLM_MODEL
        base_url = LLM_BASE_URL
        
        # Process all charts in parallel to extract table metadata
        chart_metadata_list = process_charts_for_table_metadata(
            charts,
            dashboard_info_dict.get('dashboard_title', 'Unknown Dashboard'),
            api_key,
            model,
            base_url,
            max_workers=5
        )
        
        # Merge chart-level table metadata into dashboard-level
        print("\n[Step 4.2.1] Merging chart-level table metadata...", flush=True)
        table_metadata = merge_chart_table_metadata(chart_metadata_list)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds ({step_time/60:.2f} minutes)", flush=True)
        print(f"  📊 Generated metadata for {len(table_metadata)} tables", flush=True)
        
        # Step 4.3: Save table metadata to CSV
        step_start = time.time()
        print("\n[Step 4.3] Saving table metadata to CSV...", flush=True)
        
        metadata_df = pd.DataFrame(table_metadata)
        metadata_file = f"{dashboard_dir}/{dashboard_id}_table_metadata.csv"
        metadata_df.to_csv(metadata_file, index=False)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  💾 Saved to: {metadata_file}", flush=True)
        print(f"  📊 Rows: {len(metadata_df)}", flush=True)
        print(f"  📋 Columns: {', '.join(metadata_df.columns.tolist())}", flush=True)
        
        # Validate: table_metadata must not be empty
        if len(metadata_df) == 0:
            raise ValueError(f"CRITICAL: table_metadata.csv is empty for dashboard {dashboard_id}. Extraction failed.")
        
        if progress_tracker:
            progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_table_metadata.csv")
            progress_tracker.update_dashboard_status(
                dashboard_id, 'processing',
                current_phase='Phase 4: Table Metadata',
                current_file=f"{dashboard_id}_table_metadata.csv"
            )
        
        phase4_time = time.time() - phase4_start
        print(f"\n{'─'*80}", flush=True)
        print(f"✅ PHASE 4 COMPLETED in {phase4_time:.2f} seconds ({phase4_time/60:.2f} minutes)", flush=True)
        print(f"{'─'*80}", flush=True)
    
    except Exception as e:
        phase4_time = time.time() - phase4_start
        print(f"\n❌ PHASE 4 FAILED after {phase4_time:.2f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        # Don't return - continue to summary even if Phase 4 fails
    
    # ============================================================
    # PHASE 5: Generate Column Metadata using LLM
    # ============================================================
    print("\n" + "="*80, flush=True)
    print("PHASE 5: Generating Column Metadata using LLM", flush=True)
    print("="*80, flush=True)
    phase5_start = time.time()
    
    try:
        # Step 5.1: Load required data
        step_start = time.time()
        print("\n[Step 5.1] Loading dashboard info and tables_columns_enriched data...", flush=True)
        
        # Load dashboard JSON
        json_file = f"{dashboard_dir}/{dashboard_id}_json.json"
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Dashboard JSON not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            dashboard_info_dict = json.load(f)
        
        # Load enriched tables_columns CSV
        enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns_enriched.csv"
        if not os.path.exists(enriched_file):
            # Fallback to regular CSV
            enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
        
        if not os.path.exists(enriched_file):
            raise FileNotFoundError(f"Tables columns CSV not found: {enriched_file}")
        
        tables_columns_df = pd.read_csv(enriched_file)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  📊 Loaded dashboard: {dashboard_info_dict.get('dashboard_title', 'Unknown')}", flush=True)
        print(f"  📊 Loaded {len(tables_columns_df)} table-column mappings", flush=True)
        
        # Step 5.2: Extract column metadata using LLM (chart-by-chart for token optimization)
        step_start = time.time()
        print("\n[Step 5.2] Extracting column metadata using LLM (chart-by-chart)...", flush=True)
        
        charts = dashboard_info_dict.get('charts', [])
        print(f"  Processing {len(charts)} charts in parallel...", flush=True)
        
        # Get API key and config
        api_key = os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
        if not api_key:
            raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
        model = LLM_MODEL
        base_url = LLM_BASE_URL
        
        # Process all charts in parallel to extract column metadata
        chart_metadata_list = process_charts_for_column_metadata(
            charts,
            dashboard_info_dict.get('dashboard_title', 'Unknown Dashboard'),
            tables_columns_df,
            api_key,
            model,
            base_url,
            max_workers=5
        )
        
        # Merge chart-level column metadata into dashboard-level
        print("\n[Step 5.2.1] Merging chart-level column metadata...", flush=True)
        column_metadata = merge_chart_column_metadata(chart_metadata_list)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds ({step_time/60:.2f} minutes)", flush=True)
        print(f"  📊 Generated metadata for {len(column_metadata)} columns", flush=True)
        
        # Step 5.3: Save column metadata to CSV
        step_start = time.time()
        print("\n[Step 5.3] Saving column metadata to CSV...", flush=True)
        
        metadata_df = pd.DataFrame(column_metadata)
        metadata_file = f"{dashboard_dir}/{dashboard_id}_columns_metadata.csv"
        metadata_df.to_csv(metadata_file, index=False)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  💾 Saved to: {metadata_file}", flush=True)
        print(f"  📊 Rows: {len(metadata_df)}", flush=True)
        print(f"  📋 Columns: {', '.join(metadata_df.columns.tolist())}", flush=True)
        
        # Validate: column_metadata must not be empty
        if len(metadata_df) == 0:
            raise ValueError(f"CRITICAL: columns_metadata.csv is empty for dashboard {dashboard_id}. Extraction failed.")
        
        if progress_tracker:
            progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_columns_metadata.csv")
            progress_tracker.update_dashboard_status(
                dashboard_id, 'processing',
                current_phase='Phase 5: Column Metadata',
                current_file=f"{dashboard_id}_columns_metadata.csv"
            )
        
        phase5_time = time.time() - phase5_start
        print(f"\n{'─'*80}", flush=True)
        print(f"✅ PHASE 5 COMPLETED in {phase5_time:.2f} seconds ({phase5_time/60:.2f} minutes)", flush=True)
        print(f"{'─'*80}", flush=True)
    
    except Exception as e:
        phase5_time = time.time() - phase5_start
        print(f"\n❌ PHASE 5 FAILED after {phase5_time:.2f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        # Don't return - continue to summary even if Phase 5 fails
    
    # ============================================================
    # PHASE 6: Generate Joining Conditions Metadata
    # ============================================================
    print("\n" + "="*80, flush=True)
    print("PHASE 6: Generating Joining Conditions Metadata", flush=True)
    print("="*80, flush=True)
    phase6_start = time.time()
    
    try:
        # Step 6.1: Load required data
        step_start = time.time()
        print("\n[Step 6.1] Loading dashboard info and tables_columns data...", flush=True)
        
        # Load dashboard JSON
        json_file = f"{dashboard_dir}/{dashboard_id}_json.json"
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Dashboard JSON not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            dashboard_info_dict = json.load(f)
        
        # Load tables_columns CSV (enriched or regular)
        enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns_enriched.csv"
        if not os.path.exists(enriched_file):
            enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
        
        if not os.path.exists(enriched_file):
            raise FileNotFoundError(f"Tables columns CSV not found: {enriched_file}")
        
        tables_columns_df = pd.read_csv(enriched_file)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  📊 Loaded dashboard: {dashboard_info_dict.get('dashboard_title', 'Unknown')}", flush=True)
        print(f"  📊 Loaded {len(tables_columns_df)} table-column mappings", flush=True)
        
        # Step 6.2: Extract joining conditions using LLM (chart-by-chart for token optimization)
        step_start = time.time()
        print("\n[Step 6.2] Extracting joining conditions using LLM (chart-by-chart)...", flush=True)
        print(f"  Processing {len(dashboard_info_dict.get('charts', []))} charts in parallel...", flush=True)
        
        # Get API key and config
        api_key = os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
        if not api_key:
            raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
        model = LLM_MODEL
        base_url = LLM_BASE_URL
        
        # Process all charts in parallel to extract joining conditions
        charts = dashboard_info_dict.get('charts', [])
        chart_metadata_list = process_charts_for_joining_conditions(
            charts,
            dashboard_info_dict.get('dashboard_title', 'Unknown Dashboard'),
            tables_columns_df,
            api_key,
            model,
            base_url,
            max_workers=5
        )
        
        # Merge chart-level joining conditions into dashboard-level
        print("\n[Step 6.2.1] Merging chart-level joining conditions...", flush=True)
        joining_conditions = merge_chart_joining_conditions(chart_metadata_list)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds ({step_time/60:.2f} minutes)", flush=True)
        print(f"  📊 Found {len(joining_conditions)} joining conditions", flush=True)
        
        if len(joining_conditions) == 0:
            print("  ℹ️  No multi-table joins found in this dashboard", flush=True)
        
        # Step 6.3: Save joining conditions to CSV
        step_start = time.time()
        print("\n[Step 6.3] Saving joining conditions to CSV...", flush=True)
        
        if len(joining_conditions) > 0:
            joins_df = pd.DataFrame(joining_conditions)
            joins_file = f"{dashboard_dir}/{dashboard_id}_joining_conditions.csv"
            joins_df.to_csv(joins_file, index=False)
            
            step_time = time.time() - step_start
            print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
            print(f"  💾 Saved to: {joins_file}", flush=True)
            print(f"  📊 Rows: {len(joins_df)}", flush=True)
            print(f"  📋 Columns: {', '.join(joins_df.columns.tolist())}", flush=True)
            if progress_tracker:
                progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_joining_conditions.csv")
        else:
            # Create empty file with headers
            joins_file = f"{dashboard_dir}/{dashboard_id}_joining_conditions.csv"
            empty_df = pd.DataFrame(columns=['table1', 'table2', 'joining_condition', 'remarks'])
            empty_df.to_csv(joins_file, index=False)
            step_time = time.time() - step_start
            print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
            print(f"  💾 Saved empty file to: {joins_file} (no multi-table joins found)", flush=True)
            if progress_tracker:
                progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_joining_conditions.csv")
                progress_tracker.update_dashboard_status(
                    dashboard_id, 'processing',
                    current_phase='Phase 6: Joining Conditions',
                    current_file=f"{dashboard_id}_joining_conditions.csv"
                )
        
        phase6_time = time.time() - phase6_start
        print(f"\n{'─'*80}", flush=True)
        print(f"✅ PHASE 6 COMPLETED in {phase6_time:.2f} seconds ({phase6_time/60:.2f} minutes)", flush=True)
        print(f"{'─'*80}", flush=True)
    
    except Exception as e:
        phase6_time = time.time() - phase6_start
        print(f"\n❌ PHASE 6 FAILED after {phase6_time:.2f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        # Don't return - continue to summary even if Phase 6 fails
    
    # ============================================================
    # PHASE 7: Generate Filter Conditions Documentation
    # ============================================================
    print("\n" + "="*80, flush=True)
    print("PHASE 7: Generating Filter Conditions Documentation", flush=True)
    print("="*80, flush=True)
    phase7_start = time.time()
    
    try:
        # Step 7.1: Load required data
        step_start = time.time()
        print("\n[Step 7.1] Loading dashboard info and tables_columns data...", flush=True)
        
        # Load dashboard JSON
        json_file = f"{dashboard_dir}/{dashboard_id}_json.json"
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Dashboard JSON not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            dashboard_info_dict = json.load(f)
        
        # Load tables_columns CSV (enriched or regular)
        enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns_enriched.csv"
        if not os.path.exists(enriched_file):
            enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
        
        if not os.path.exists(enriched_file):
            raise FileNotFoundError(f"Tables columns CSV not found: {enriched_file}")
        
        tables_columns_df = pd.read_csv(enriched_file)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  📊 Loaded dashboard: {dashboard_info_dict.get('dashboard_title', 'Unknown')}", flush=True)
        print(f"  📊 Loaded {len(tables_columns_df)} table-column mappings", flush=True)
        
        # Step 7.2: Generate filter conditions using LLM (chart-by-chart for token optimization)
        step_start = time.time()
        print("\n[Step 7.2] Generating filter conditions documentation using LLM (chart-by-chart)...", flush=True)
        print(f"  Processing {len(dashboard_info_dict.get('charts', []))} charts in parallel...", flush=True)
        
        # Get API key and config
        api_key = os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
        if not api_key:
            raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
        model = LLM_MODEL
        base_url = LLM_BASE_URL
        
        # Process all charts in parallel to extract filter conditions
        charts = dashboard_info_dict.get('charts', [])
        chart_metadata_list = process_charts_for_filter_conditions(
            charts,
            dashboard_info_dict.get('dashboard_title', 'Unknown Dashboard'),
            tables_columns_df,
            api_key,
            model,
            base_url,
            max_workers=5
        )
        
        # Merge chart-level filter conditions into dashboard-level
        print("\n[Step 7.2.1] Merging chart-level filter conditions...", flush=True)
        filter_conditions_content = merge_chart_filter_conditions(chart_metadata_list)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds ({step_time/60:.2f} minutes)", flush=True)
        print(f"  📊 Generated filter conditions for {len(dashboard_info_dict.get('charts', []))} charts", flush=True)
        
        # Step 7.3: Save filter conditions to text file
        step_start = time.time()
        print("\n[Step 7.3] Saving filter conditions to text file...", flush=True)
        
        filter_file = f"{dashboard_dir}/{dashboard_id}_filter_conditions.txt"
        with open(filter_file, 'w', encoding='utf-8') as f:
            f.write(filter_conditions_content)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  💾 Saved to: {filter_file}", flush=True)
        print(f"  📄 File size: {len(filter_conditions_content)} characters", flush=True)
        
        # Validate: filter_conditions must not be empty
        if len(filter_conditions_content.strip()) == 0:
            raise ValueError(f"CRITICAL: filter_conditions.txt is empty for dashboard {dashboard_id}. Extraction failed.")
        
        if progress_tracker:
            progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_filter_conditions.txt")
            progress_tracker.update_dashboard_status(
                dashboard_id, 'processing',
                current_phase='Phase 7: Filter Conditions',
                current_file=f"{dashboard_id}_filter_conditions.txt"
            )
        
        phase7_time = time.time() - phase7_start
        print(f"\n{'─'*80}", flush=True)
        print(f"✅ PHASE 7 COMPLETED in {phase7_time:.2f} seconds ({phase7_time/60:.2f} minutes)", flush=True)
        print(f"{'─'*80}", flush=True)
    
    except Exception as e:
        phase7_time = time.time() - phase7_start
        print(f"\n❌ PHASE 7 FAILED after {phase7_time:.2f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        # Don't return - continue to summary even if Phase 7 fails
    
    # ============================================================
    # PHASE 8: Generate Term Definitions
    # ============================================================
    print("\n" + "="*80, flush=True)
    print("PHASE 8: Generating Term Definitions", flush=True)
    print("="*80, flush=True)
    phase8_start = time.time()
    
    try:
        # Step 8.1: Load required data
        step_start = time.time()
        print("\n[Step 8.1] Loading dashboard info and tables_columns data...", flush=True)
        
        # Load dashboard JSON
        json_file = f"{dashboard_dir}/{dashboard_id}_json.json"
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Dashboard JSON not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            dashboard_info_dict = json.load(f)
        
        # Load tables_columns CSV (enriched or regular)
        enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns_enriched.csv"
        if not os.path.exists(enriched_file):
            enriched_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
        
        if not os.path.exists(enriched_file):
            raise FileNotFoundError(f"Tables columns CSV not found: {enriched_file}")
        
        tables_columns_df = pd.read_csv(enriched_file)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
        print(f"  📊 Loaded dashboard: {dashboard_info_dict.get('dashboard_title', 'Unknown')}", flush=True)
        print(f"  📊 Loaded {len(tables_columns_df)} table-column mappings", flush=True)
        
        # Step 8.2: Extract term definitions using LLM (chart-by-chart for token optimization)
        step_start = time.time()
        print("\n[Step 8.2] Extracting term definitions using LLM (chart-by-chart)...", flush=True)
        print(f"  Processing {len(dashboard_info_dict.get('charts', []))} charts in parallel...", flush=True)
        
        # Get API key and config
        api_key = os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
        if not api_key:
            raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
        model = LLM_MODEL
        base_url = LLM_BASE_URL
        
        # Process all charts in parallel to extract term definitions
        charts = dashboard_info_dict.get('charts', [])
        chart_metadata_list = process_charts_for_definitions(
            charts,
            dashboard_info_dict.get('dashboard_title', 'Unknown Dashboard'),
            api_key,
            model,
            base_url,
            max_workers=5
        )
        
        # Merge chart-level definitions into dashboard-level
        print("\n[Step 8.2.1] Merging chart-level term definitions...", flush=True)
        term_definitions = merge_chart_definitions(chart_metadata_list)
        
        step_time = time.time() - step_start
        print(f"  ✅ Completed in {step_time:.2f} seconds ({step_time/60:.2f} minutes)", flush=True)
        print(f"  📊 Generated {len(term_definitions)} term definitions", flush=True)
        
        # Step 8.3: Save term definitions to CSV
        step_start = time.time()
        print("\n[Step 8.3] Saving term definitions to CSV...", flush=True)
        
        if len(term_definitions) > 0:
            # Ensure all required columns exist
            for term_def in term_definitions:
                if 'term' not in term_def:
                    term_def['term'] = ''
                if 'type' not in term_def:
                    term_def['type'] = 'Metric'
                if 'definition' not in term_def:
                    term_def['definition'] = ''
                if 'business_alias' not in term_def:
                    term_def['business_alias'] = ''
            
            terms_df = pd.DataFrame(term_definitions)
            # Ensure column order
            terms_df = terms_df[['term', 'type', 'definition', 'business_alias']]
            terms_file = f"{dashboard_dir}/{dashboard_id}_definitions.csv"
            terms_df.to_csv(terms_file, index=False)
            
            step_time = time.time() - step_start
            print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
            print(f"  💾 Saved to: {terms_file}", flush=True)
            print(f"  📊 Rows: {len(terms_df)}", flush=True)
            print(f"  📋 Columns: {', '.join(terms_df.columns.tolist())}", flush=True)
            
            # Show sample terms
            print(f"\n  Sample terms extracted:", flush=True)
            for i, row in terms_df.head(5).iterrows():
                print(f"    - {row['term']} ({row['type']})", flush=True)
            
            # Validate: definitions must not be empty
            if len(terms_df) == 0:
                raise ValueError(f"CRITICAL: definitions.csv is empty for dashboard {dashboard_id}. Extraction failed.")
            
            if progress_tracker:
                progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_definitions.csv")
                progress_tracker.update_dashboard_status(
                    dashboard_id, 'processing',
                    current_phase='Phase 8: Term Definitions',
                    current_file=f"{dashboard_id}_definitions.csv"
                )
        else:
            # Create empty file with headers
            terms_file = f"{dashboard_dir}/{dashboard_id}_definitions.csv"
            empty_df = pd.DataFrame(columns=['term', 'type', 'definition', 'business_alias'])
            empty_df.to_csv(terms_file, index=False)
            step_time = time.time() - step_start
            print(f"  ✅ Completed in {step_time:.2f} seconds", flush=True)
            print(f"  💾 Saved empty file to: {terms_file} (no terms extracted)", flush=True)
            
            # Validate: definitions must not be empty
            raise ValueError(f"CRITICAL: definitions.csv is empty for dashboard {dashboard_id}. Extraction failed.")
        
        phase8_time = time.time() - phase8_start
        print(f"\n{'─'*80}", flush=True)
        print(f"✅ PHASE 8 COMPLETED in {phase8_time:.2f} seconds ({phase8_time/60:.2f} minutes)", flush=True)
        print(f"{'─'*80}", flush=True)
    
    except Exception as e:
        phase8_time = time.time() - phase8_start
        print(f"\n❌ PHASE 8 FAILED after {phase8_time:.2f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        # Don't return - continue to summary even if Phase 8 fails
    
    # ============================================================
    # PHASE 9: Metadata Quality Judging (Optional)
    # ============================================================
    phase9_start = time.time()
    
    # Check if quality judging is enabled (default: True)
    enable_quality_judge = os.getenv("ENABLE_QUALITY_JUDGE", "true").lower() == "true"
    
    if enable_quality_judge:
        print("\n" + "="*80, flush=True)
        print("PHASE 9: Metadata Quality Judging", flush=True)
        print("="*80, flush=True)
        
        try:
            # Import quality judge
            from metadata_quality_judge import judge_dashboard_metadata, save_quality_report
            
            # Get API key and config
            api_key = os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
            if not api_key:
                print("  ⚠️  LLM API key not configured. Skipping quality judging.", flush=True)
            else:
                model = LLM_MODEL
                base_url = LLM_BASE_URL
                
                print("\n[Step 9.1] Judging metadata quality...", flush=True)
                if progress_tracker:
                    progress_tracker.update_dashboard_status(
                        dashboard_id, 'processing',
                        current_phase='Phase 9: Quality Judging',
                        current_file=f"{dashboard_id}_quality_report.json"
                    )
                
                # Judge all metadata
                quality_report = judge_dashboard_metadata(
                    dashboard_id=dashboard_id,
                    api_key=api_key,
                    model=model,
                    base_url=base_url,
                    extracted_meta_dir="extracted_meta"
                )
                
                # Save quality report
                print("\n[Step 9.2] Saving quality report...", flush=True)
                save_quality_report(quality_report)
                
                step_time = time.time() - phase9_start
                print(f"  ✅ Completed in {step_time:.2f} seconds ({step_time/60:.2f} minutes)", flush=True)
                
                # Print summary
                print(f"\n  📊 Quality Summary:", flush=True)
                print(f"    Overall Confidence: {quality_report.summary['overall_confidence']:.2f}", flush=True)
                print(f"    Status: {quality_report.summary['status']}", flush=True)
                print(f"    Missing Items: {quality_report.summary['total_issues']['missing_items']}", flush=True)
                print(f"    Quality Issues: {quality_report.summary['total_issues']['quality_issues']}", flush=True)
                print(f"    Recommendations: {quality_report.summary['total_issues']['recommendations']}", flush=True)
                
                if progress_tracker:
                    progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_quality_report.json")
                
                phase9_time = time.time() - phase9_start
                print(f"\n{'─'*80}", flush=True)
                print(f"✅ PHASE 9 COMPLETED in {phase9_time:.2f} seconds ({phase9_time/60:.2f} minutes)", flush=True)
                print(f"{'─'*80}", flush=True)
        
        except ImportError:
            print("  ⚠️  metadata_quality_judge module not found. Skipping quality judging.", flush=True)
        except Exception as e:
            phase9_time = time.time() - phase9_start
            print(f"\n❌ PHASE 9 FAILED after {phase9_time:.2f} seconds", flush=True)
            print(f"Error: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            # Don't fail extraction if quality judging fails
    else:
        print("\n  ℹ️  Quality judging disabled (set ENABLE_QUALITY_JUDGE=true to enable)", flush=True)
    
    # ============================================================
    # Summary
    # ============================================================
    total_time = time.time() - start_time
    print("\n" + "="*80, flush=True)
    print("EXTRACTION SUMMARY", flush=True)
    print("="*80, flush=True)
    print(f"Dashboard ID: {dashboard_id}", flush=True)
    print(f"Total Charts: {num_charts}", flush=True)
    print(f"Total Mappings: {num_mappings}", flush=True)
    print(f"\nTiming Breakdown:", flush=True)
    print(f"  Phase 1 (Dashboard Extraction): {phase1_time:.2f}s ({phase1_time/60:.2f} min)", flush=True)
    print(f"  Phase 2 (LLM Extraction):      {phase2_time:.2f}s ({phase2_time/60:.2f} min)", flush=True)
    if 'phase3_time' in locals():
        print(f"  Phase 3 (Trino Schema):         {phase3_time:.2f}s ({phase3_time/60:.2f} min)", flush=True)
    if 'phase4_time' in locals():
        print(f"  Phase 4 (Table Metadata):      {phase4_time:.2f}s ({phase4_time/60:.2f} min)", flush=True)
    if 'phase5_time' in locals():
        print(f"  Phase 5 (Column Metadata):     {phase5_time:.2f}s ({phase5_time/60:.2f} min)", flush=True)
    if 'phase6_time' in locals():
        print(f"  Phase 6 (Joining Conditions):  {phase6_time:.2f}s ({phase6_time/60:.2f} min)", flush=True)
    if 'phase7_time' in locals():
        print(f"  Phase 7 (Filter Conditions):   {phase7_time:.2f}s ({phase7_time/60:.2f} min)", flush=True)
    if 'phase8_time' in locals():
        print(f"  Phase 8 (Term Definitions):     {phase8_time:.2f}s ({phase8_time/60:.2f} min)", flush=True)
    if 'phase9_time' in locals():
        print(f"  Phase 9 (Quality Judging):      {phase9_time:.2f}s ({phase9_time/60:.2f} min)", flush=True)
    print(f"  Total Time:                    {total_time:.2f}s ({total_time/60:.2f} min)", flush=True)
    print(f"\nOutput Files:", flush=True)
    print(f"  📄 {dashboard_dir}/{dashboard_id}_json.json", flush=True)
    print(f"  📄 {dashboard_dir}/{dashboard_id}_csv.csv", flush=True)
    print(f"  📄 {dashboard_dir}/{dashboard_id}_queries.sql", flush=True)
    print(f"  📄 {dashboard_dir}/{dashboard_id}_tables_columns.csv", flush=True)
    print(f"  📄 {dashboard_dir}/{dashboard_id}_tables_columns.json", flush=True)
    if 'phase3_time' in locals() and os.path.exists(f"{dashboard_dir}/{dashboard_id}_tables_columns_enriched.csv"):
        print(f"  📄 {dashboard_dir}/{dashboard_id}_tables_columns_enriched.csv", flush=True)
    if 'phase4_time' in locals() and os.path.exists(f"{dashboard_dir}/{dashboard_id}_table_metadata.csv"):
        print(f"  📄 {dashboard_dir}/{dashboard_id}_table_metadata.csv", flush=True)
    if 'phase5_time' in locals() and os.path.exists(f"{dashboard_dir}/{dashboard_id}_columns_metadata.csv"):
        print(f"  📄 {dashboard_dir}/{dashboard_id}_columns_metadata.csv", flush=True)
    if 'phase6_time' in locals() and os.path.exists(f"{dashboard_dir}/{dashboard_id}_joining_conditions.csv"):
        print(f"  📄 {dashboard_dir}/{dashboard_id}_joining_conditions.csv", flush=True)
    if 'phase7_time' in locals() and os.path.exists(f"{dashboard_dir}/{dashboard_id}_filter_conditions.txt"):
        print(f"  📄 {dashboard_dir}/{dashboard_id}_filter_conditions.txt", flush=True)
    if 'phase8_time' in locals() and os.path.exists(f"{dashboard_dir}/{dashboard_id}_definitions.csv"):
        print(f"  📄 {dashboard_dir}/{dashboard_id}_definitions.csv", flush=True)
    if 'phase9_time' in locals() and os.path.exists(f"{dashboard_dir}/{dashboard_id}_quality_report.json"):
        print(f"  📄 {dashboard_dir}/{dashboard_id}_quality_report.json", flush=True)
    print(f"\n✅ Extraction completed successfully!", flush=True)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("="*80 + "\n", flush=True)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract dashboard metadata with timing logs (Phases 1, 2, 3, 4, 5, 6, 7 & 8)'
    )
    parser.add_argument(
        'dashboard_id',
        type=int,
        help='Dashboard ID to extract'
    )
    
    args = parser.parse_args()
    
    try:
        extract_dashboard_with_timing(args.dashboard_id)
    except KeyboardInterrupt:
        print("\n\n⚠️  Extraction interrupted by user", flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


