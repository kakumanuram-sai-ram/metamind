"""
Dashboard Metadata Orchestrator

This module orchestrates the extraction of metadata from multiple dashboards.
It iterates through a list of dashboard IDs and calls the existing extraction
logic for each dashboard independently, storing results in separate folders.
"""
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add scripts directory to path for imports
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from extract_dashboard_with_timing import extract_dashboard_with_timing
from progress_tracker import get_progress_tracker


class DashboardMetadataOrchestrator:
    """
    Orchestrates metadata extraction for multiple dashboards.
    
    For each dashboard ID:
    1. Calls extract_dashboard_with_timing() to extract all metadata
    2. Stores results in extracted_meta/{dashboard_id}/ folder
    3. Tracks success/failure for each dashboard
    """
    
    def __init__(self, dashboard_ids: List[int], continue_on_error: bool = True, parallel: bool = True, max_workers: int = None):
        """
        Initialize the orchestrator.
        
        Args:
            dashboard_ids: List of dashboard IDs to process
            continue_on_error: If True, continue processing other dashboards if one fails
            parallel: If True, process dashboards in parallel (default: True)
            max_workers: Maximum number of parallel workers (default: number of dashboards)
        """
        self.dashboard_ids = dashboard_ids
        self.continue_on_error = continue_on_error
        self.parallel = parallel
        self.max_workers = max_workers or len(dashboard_ids)
        self.results: Dict[int, Dict] = {}
        self.progress_tracker = get_progress_tracker()
        self.lock = threading.Lock()
        
    def extract_all(self) -> Dict[int, Dict]:
        """
        Extract metadata for all dashboards.
        
        Returns:
            Dictionary mapping dashboard_id to result dict with:
            - status: 'success' or 'error'
            - error: Error message if status is 'error'
            - files: List of generated files if status is 'success'
        """
        total_dashboards = len(self.dashboard_ids)
        start_time = time.time()
        
        # Initialize progress tracking
        self.progress_tracker.start_extraction(self.dashboard_ids)
        
        print(f"\n{'='*80}")
        print(f"Dashboard Metadata Orchestrator")
        print(f"Processing {total_dashboards} dashboards")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        if self.parallel and total_dashboards > 1:
            # Parallel processing
            print(f"\n🚀 Processing {total_dashboards} dashboards in PARALLEL mode")
            print(f"   Max workers: {self.max_workers}\n")
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_dashboard = {
                    executor.submit(self._extract_single_dashboard, dashboard_id, idx, total_dashboards): dashboard_id
                    for idx, dashboard_id in enumerate(self.dashboard_ids, 1)
                }
                
                # Process as they complete
                for future in as_completed(future_to_dashboard):
                    dashboard_id = future_to_dashboard[future]
                    try:
                        result = future.result()
                        with self.lock:
                            self.results[dashboard_id] = result
                    except Exception as e:
                        error_msg = str(e)
                        with self.lock:
                            self.results[dashboard_id] = {
                                'status': 'error',
                                'error': error_msg,
                                'time_seconds': 0,
                                'files': []
                            }
                        print(f"\n❌ Dashboard {dashboard_id} failed: {error_msg}", flush=True)
                        if not self.continue_on_error:
                            print(f"\n⚠️  Stopping processing due to error (continue_on_error=False)")
                            break
        else:
            # Sequential processing
            for idx, dashboard_id in enumerate(self.dashboard_ids, 1):
                result = self._extract_single_dashboard(dashboard_id, idx, total_dashboards)
                self.results[dashboard_id] = result
                
                if result['status'] == 'error' and not self.continue_on_error:
                    print(f"\n⚠️  Stopping processing due to error (continue_on_error=False)")
                    break
    
    def _extract_single_dashboard(self, dashboard_id: int, idx: int, total_dashboards: int) -> Dict:
        """
        Extract metadata for a single dashboard.
        
        Args:
            dashboard_id: Dashboard ID to process
            idx: Current index (1-based)
            total_dashboards: Total number of dashboards
            
        Returns:
            Result dictionary with status, files, time, etc.
        """
        print(f"\n{'─'*80}", flush=True)
        print(f"Processing Dashboard {idx}/{total_dashboards}: ID {dashboard_id}", flush=True)
        print(f"{'─'*80}", flush=True)
        
        # Update progress: dashboard started
        self.progress_tracker.update_dashboard_status(
            dashboard_id, 
            'processing',
            current_phase='Initializing'
        )
        
        dashboard_start = time.time()
        
        try:
            # Call existing extraction function with progress tracker
            extract_dashboard_with_timing(dashboard_id, progress_tracker=self.progress_tracker)
            
            # Verify output files exist and update progress
            dashboard_dir = f"extracted_meta/{dashboard_id}"
            file_phases = [
                ("Phase 1: Dashboard Extraction", f"{dashboard_id}_json.json"),
                ("Phase 1: Dashboard Extraction", f"{dashboard_id}_csv.csv"),
                ("Phase 1: Dashboard Extraction", f"{dashboard_id}_queries.sql"),
                ("Phase 2: Tables & Columns", f"{dashboard_id}_tables_columns.csv"),
                ("Phase 3: Schema Enrichment", f"{dashboard_id}_tables_columns_enriched.csv"),
                ("Phase 4: Table Metadata", f"{dashboard_id}_table_metadata.csv"),
                ("Phase 5: Column Metadata", f"{dashboard_id}_columns_metadata.csv"),
                ("Phase 6: Joining Conditions", f"{dashboard_id}_joining_conditions.csv"),
                ("Phase 7: Filter Conditions", f"{dashboard_id}_filter_conditions.txt"),
                ("Phase 8: Term Definitions", f"{dashboard_id}_definitions.csv")
            ]
            
            generated_files = []
            for phase_name, filename in file_phases:
                filepath = os.path.join(dashboard_dir, filename)
                if os.path.exists(filepath):
                    generated_files.append(filepath)
                    # Update progress: file completed
                    self.progress_tracker.add_completed_file(dashboard_id, filename)
                    self.progress_tracker.update_dashboard_status(
                        dashboard_id,
                        'processing',
                        current_phase=phase_name,
                        current_file=filename
                    )
                
            dashboard_time = time.time() - dashboard_start
            
            # Update progress: dashboard completed
            self.progress_tracker.update_dashboard_status(
                dashboard_id,
                'completed',
                current_phase='Completed',
                current_file=None
            )
            
            result = {
                'status': 'success',
                'files': generated_files,
                'time_seconds': dashboard_time,
                'files_count': len(generated_files)
            }
            
            print(f"\n✅ Dashboard {dashboard_id} completed successfully", flush=True)
            print(f"   Generated {len(generated_files)} files in {dashboard_time:.2f} seconds ({dashboard_time/60:.2f} minutes)", flush=True)
            
            return result
            
        except Exception as e:
            dashboard_time = time.time() - dashboard_start
            error_msg = str(e)
            
            # Update progress: dashboard failed
            self.progress_tracker.update_dashboard_status(
                dashboard_id,
                'error',
                error=error_msg
            )
            
            result = {
                'status': 'error',
                'error': error_msg,
                'time_seconds': dashboard_time,
                'files': []
            }
            
            print(f"\n❌ Dashboard {dashboard_id} failed after {dashboard_time:.2f} seconds", flush=True)
            print(f"   Error: {error_msg}", flush=True)
            
            return result
        
        total_time = time.time() - start_time
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"Orchestration Summary")
        print(f"{'='*80}")
        print(f"Total dashboards: {total_dashboards}")
        print(f"Successful: {sum(1 for r in self.results.values() if r['status'] == 'success')}")
        print(f"Failed: {sum(1 for r in self.results.values() if r['status'] == 'error')}")
        print(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Print per-dashboard summary
        if self.results:
            print("Per-Dashboard Results:")
            print("-" * 80)
            for dashboard_id, result in self.results.items():
                status_icon = "✅" if result['status'] == 'success' else "❌"
                print(f"{status_icon} Dashboard {dashboard_id}: {result['status']} "
                      f"({result['time_seconds']:.2f}s, {result['files_count']} files)")
            print()
        
        return self.results
    
    def get_successful_dashboard_ids(self) -> List[int]:
        """Get list of successfully processed dashboard IDs."""
        return [did for did, result in self.results.items() if result['status'] == 'success']
    
    def get_failed_dashboard_ids(self) -> List[int]:
        """Get list of failed dashboard IDs."""
        return [did for did, result in self.results.items() if result['status'] == 'error']


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Orchestrate metadata extraction for multiple dashboards'
    )
    parser.add_argument(
        'dashboard_ids',
        type=int,
        nargs='+',
        help='Dashboard IDs to extract (space-separated)'
    )
    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='Stop processing if any dashboard fails (default: continue)'
    )
    
    args = parser.parse_args()
    
    orchestrator = DashboardMetadataOrchestrator(
        dashboard_ids=args.dashboard_ids,
        continue_on_error=not args.stop_on_error
    )
    
    try:
        results = orchestrator.extract_all()
        
        # Exit with error code if any failed
        failed_count = sum(1 for r in results.values() if r['status'] == 'error')
        if failed_count > 0:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Orchestration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

