"""
Progress Tracker for Multi-Dashboard Processing

Tracks the progress of metadata extraction and merging operations,
storing status in a JSON file that can be read by the API.
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import threading


class ProgressTracker:
    """
    Thread-safe progress tracker for multi-dashboard processing.
    """
    
    def __init__(self, progress_file: str = "extracted_meta/progress.json"):
        """
        Initialize the progress tracker.
        
        Args:
            progress_file: Path to JSON file storing progress
        """
        self.progress_file = progress_file
        self.lock = threading.Lock()
        self._ensure_progress_file()
    
    def _ensure_progress_file(self):
        """Ensure progress file exists with initial structure."""
        if not os.path.exists(self.progress_file):
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            self._write_progress({
                'status': 'idle',
                'current_operation': None,
                'total_dashboards': 0,
                'completed_dashboards': 0,
                'failed_dashboards': 0,
                'dashboards': {},
                'merge_status': {
                    'status': 'pending',
                    'current_step': None,
                    'completed_steps': []
                },
                'kb_build_status': {
                    'status': 'pending',
                    'current_step': None
                },
                'start_time': None,
                'last_update': None
            })
    
    def _read_progress(self) -> Dict:
        """Read progress from file."""
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _write_progress(self, progress: Dict):
        """Write progress to file."""
        progress['last_update'] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    
    def start_extraction(self, dashboard_ids: List[int]):
        """Initialize progress tracking for extraction."""
        with self.lock:
            progress = self._read_progress()
            progress['status'] = 'extracting'
            progress['current_operation'] = 'extraction'
            progress['total_dashboards'] = len(dashboard_ids)
            progress['completed_dashboards'] = 0
            progress['failed_dashboards'] = 0
            progress['start_time'] = datetime.now().isoformat()
            progress['dashboards'] = {
                str(did): {
                    'dashboard_id': did,
                    'status': 'pending',
                    'current_phase': None,
                    'current_file': None,
                    'completed_files': [],
                    'total_files': 11,
                    'completed_files_count': 0,
                    'error': None,
                    'start_time': None,
                    'end_time': None
                }
                for did in dashboard_ids
            }
            self._write_progress(progress)
    
    def update_dashboard_status(self, dashboard_id: int, status: str, 
                                current_phase: Optional[str] = None,
                                current_file: Optional[str] = None,
                                error: Optional[str] = None):
        """Update status for a specific dashboard."""
        with self.lock:
            progress = self._read_progress()
            did_str = str(dashboard_id)
            
            if did_str not in progress['dashboards']:
                progress['dashboards'][did_str] = {
                    'dashboard_id': dashboard_id,
                    'status': status,
                    'current_phase': current_phase,
                    'current_file': current_file,
                    'completed_files': [],
                    'total_files': 11,
                    'completed_files_count': 0,
                    'error': error,
                    'start_time': None,
                    'end_time': None
                }
            
            dashboard_progress = progress['dashboards'][did_str]
            dashboard_progress['status'] = status
            if current_phase:
                dashboard_progress['current_phase'] = current_phase
            if current_file:
                dashboard_progress['current_file'] = current_file
            if error:
                dashboard_progress['error'] = error
            
            if status == 'processing' and not dashboard_progress['start_time']:
                dashboard_progress['start_time'] = datetime.now().isoformat()
            if status in ['completed', 'error']:
                dashboard_progress['end_time'] = datetime.now().isoformat()
            
            # Update counts
            if status == 'completed':
                progress['completed_dashboards'] = sum(
                    1 for d in progress['dashboards'].values() 
                    if d['status'] == 'completed'
                )
            elif status == 'error':
                progress['failed_dashboards'] = sum(
                    1 for d in progress['dashboards'].values() 
                    if d['status'] == 'error'
                )
            
            self._write_progress(progress)
    
    def add_completed_file(self, dashboard_id: int, filename: str):
        """Mark a file as completed for a dashboard."""
        with self.lock:
            progress = self._read_progress()
            did_str = str(dashboard_id)
            
            if did_str not in progress['dashboards']:
                return
            
            dashboard_progress = progress['dashboards'][did_str]
            if filename not in dashboard_progress['completed_files']:
                dashboard_progress['completed_files'].append(filename)
                dashboard_progress['completed_files_count'] = len(dashboard_progress['completed_files'])
            
            self._write_progress(progress)
    
    def start_merge(self):
        """Initialize progress tracking for merge."""
        with self.lock:
            progress = self._read_progress()
            progress['status'] = 'merging'
            progress['current_operation'] = 'merge'
            progress['merge_status'] = {
                'status': 'processing',
                'current_step': 'initializing',
                'completed_steps': []
            }
            self._write_progress(progress)
    
    def update_merge_status(self, current_step: str, completed_steps: List[str]):
        """Update merge progress."""
        with self.lock:
            progress = self._read_progress()
            progress['merge_status'] = {
                'status': 'processing',
                'current_step': current_step,
                'completed_steps': completed_steps
            }
            self._write_progress(progress)
    
    def complete_merge(self):
        """Mark merge as completed."""
        with self.lock:
            progress = self._read_progress()
            progress['merge_status'] = {
                'status': 'completed',
                'current_step': None,
                'completed_steps': ['table_metadata', 'columns_metadata', 'joining_conditions', 'definitions', 'filter_conditions']
            }
            self._write_progress(progress)
    
    def start_kb_build(self):
        """Initialize progress tracking for KB build."""
        with self.lock:
            progress = self._read_progress()
            progress['status'] = 'building_kb'
            progress['current_operation'] = 'kb_build'
            progress['kb_build_status'] = {
                'status': 'processing',
                'current_step': 'initializing'
            }
            self._write_progress(progress)
    
    def update_kb_build_status(self, current_step: str):
        """Update KB build progress."""
        with self.lock:
            progress = self._read_progress()
            progress['kb_build_status'] = {
                'status': 'processing',
                'current_step': current_step
            }
            self._write_progress(progress)
    
    def complete_kb_build(self):
        """Mark KB build as completed."""
        with self.lock:
            progress = self._read_progress()
            progress['status'] = 'completed'
            progress['current_operation'] = None
            progress['kb_build_status'] = {
                'status': 'completed',
                'current_step': None
            }
            self._write_progress(progress)
    
    def get_progress(self) -> Dict:
        """Get current progress."""
        with self.lock:
            return self._read_progress()
    
    def reset(self):
        """Reset progress tracker."""
        self._ensure_progress_file()


# Global progress tracker instance
_global_tracker = None
_tracker_lock = threading.Lock()


def get_progress_tracker() -> ProgressTracker:
    """Get or create global progress tracker instance."""
    global _global_tracker
    with _tracker_lock:
        if _global_tracker is None:
            _global_tracker = ProgressTracker()
        return _global_tracker

