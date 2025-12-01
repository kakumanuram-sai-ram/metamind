"""
Repository Pattern - Abstract storage layer

This module provides abstraction over data storage, making it easy to swap
between file system, database, or other storage backends.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
import json
import shutil

try:
    from models import DashboardInfo, ChartInfo
except ImportError:
    from scripts.models import DashboardInfo, ChartInfo


class IDashboardRepository(ABC):
    """Abstract repository for dashboard metadata"""
    
    @abstractmethod
    def save(self, dashboard: DashboardInfo) -> None:
        """Save dashboard metadata"""
        pass
    
    @abstractmethod
    def get(self, dashboard_id: int) -> Optional[DashboardInfo]:
        """Get dashboard by ID"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[DashboardInfo]:
        """List all dashboards"""
        pass
    
    @abstractmethod
    def exists(self, dashboard_id: int) -> bool:
        """Check if dashboard exists"""
        pass
    
    @abstractmethod
    def delete(self, dashboard_id: int) -> None:
        """Delete dashboard metadata"""
        pass
    
    @abstractmethod
    def get_file_path(self, dashboard_id: int, file_type: str) -> Optional[Path]:
        """Get path to a specific dashboard file"""
        pass


class FileSystemDashboardRepository(IDashboardRepository):
    """File-based dashboard repository implementation"""
    
    def __init__(self, base_dir: Path):
        """
        Initialize repository.
        
        Args:
            base_dir: Base directory for storing dashboard data
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_dashboard_dir(self, dashboard_id: int) -> Path:
        """Get directory path for a dashboard"""
        return self.base_dir / str(dashboard_id)
    
    def _get_json_path(self, dashboard_id: int) -> Path:
        """Get path to dashboard JSON file"""
        return self._get_dashboard_dir(dashboard_id) / f"{dashboard_id}_json.json"
    
    def save(self, dashboard: DashboardInfo) -> None:
        """Save dashboard to JSON file"""
        dashboard_dir = self._get_dashboard_dir(dashboard.dashboard_id)
        dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = self._get_json_path(dashboard.dashboard_id)
        
        # Convert to dict and save
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get(self, dashboard_id: int) -> Optional[DashboardInfo]:
        """Load dashboard from JSON file"""
        json_path = self._get_json_path(dashboard_id)
        
        if not json_path.exists():
            return None
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return DashboardInfo.from_dict(data)
        except Exception as e:
            print(f"Error loading dashboard {dashboard_id}: {e}")
            return None
    
    def list_all(self) -> List[DashboardInfo]:
        """List all dashboards"""
        dashboards = []
        
        if not self.base_dir.exists():
            return dashboards
        
        for dashboard_dir in self.base_dir.iterdir():
            if dashboard_dir.is_dir() and dashboard_dir.name.isdigit():
                dashboard_id = int(dashboard_dir.name)
                dashboard = self.get(dashboard_id)
                if dashboard:
                    dashboards.append(dashboard)
        
        return dashboards
    
    def exists(self, dashboard_id: int) -> bool:
        """Check if dashboard exists"""
        return self._get_json_path(dashboard_id).exists()
    
    def delete(self, dashboard_id: int) -> None:
        """Delete dashboard directory and all its files"""
        dashboard_dir = self._get_dashboard_dir(dashboard_id)
        if dashboard_dir.exists():
            shutil.rmtree(dashboard_dir)
    
    def get_file_path(self, dashboard_id: int, file_type: str) -> Optional[Path]:
        """
        Get path to a specific dashboard file.
        
        Args:
            dashboard_id: Dashboard ID
            file_type: Type of file (e.g., 'json', 'csv', 'sql', 'table_metadata')
        
        Returns:
            Path to file if it exists, None otherwise
        """
        dashboard_dir = self._get_dashboard_dir(dashboard_id)
        
        # Map file types to filenames
        file_mapping = {
            'json': f'{dashboard_id}_json.json',
            'csv': f'{dashboard_id}_csv.csv',
            'sql': f'{dashboard_id}_queries.sql',
            'tables_columns': f'{dashboard_id}_tables_columns.csv',
            'tables_columns_enriched': f'{dashboard_id}_tables_columns_enriched.csv',
            'table_metadata': f'{dashboard_id}_table_metadata.csv',
            'column_metadata': f'{dashboard_id}_column_metadata.csv',
            'columns_metadata': f'{dashboard_id}_columns_metadata.csv',
            'joining_conditions': f'{dashboard_id}_joining_conditions.csv',
            'filter_conditions': f'{dashboard_id}_filter_conditions.txt',
            'definitions': f'{dashboard_id}_definitions.csv',
        }
        
        filename = file_mapping.get(file_type)
        if not filename:
            return None
        
        file_path = dashboard_dir / filename
        return file_path if file_path.exists() else None


class InMemoryDashboardRepository(IDashboardRepository):
    """In-memory repository for testing"""
    
    def __init__(self):
        """Initialize in-memory storage"""
        self.dashboards: dict[int, DashboardInfo] = {}
        self.files: dict[tuple[int, str], Path] = {}
    
    def save(self, dashboard: DashboardInfo) -> None:
        """Save dashboard to memory"""
        self.dashboards[dashboard.dashboard_id] = dashboard
    
    def get(self, dashboard_id: int) -> Optional[DashboardInfo]:
        """Get dashboard from memory"""
        return self.dashboards.get(dashboard_id)
    
    def list_all(self) -> List[DashboardInfo]:
        """List all dashboards in memory"""
        return list(self.dashboards.values())
    
    def exists(self, dashboard_id: int) -> bool:
        """Check if dashboard exists in memory"""
        return dashboard_id in self.dashboards
    
    def delete(self, dashboard_id: int) -> None:
        """Delete dashboard from memory"""
        if dashboard_id in self.dashboards:
            del self.dashboards[dashboard_id]
    
    def get_file_path(self, dashboard_id: int, file_type: str) -> Optional[Path]:
        """Get file path from memory"""
        return self.files.get((dashboard_id, file_type))
    
    def add_file(self, dashboard_id: int, file_type: str, path: Path) -> None:
        """Add file path to memory (for testing)"""
        self.files[(dashboard_id, file_type)] = path

