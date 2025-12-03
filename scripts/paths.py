"""
Centralized Path Configuration

This module provides all file and directory paths used in MetaMind.
All paths are relative to the project root, making the codebase portable.

Usage:
    from paths import Paths
    
    # Get dashboard output directory
    dashboard_dir = Paths.dashboard_dir(dashboard_id=476)
    
    # Get specific file paths
    json_file = Paths.dashboard_json(476)
    csv_file = Paths.tables_columns_csv(476)
"""
import os
from pathlib import Path
from typing import Optional


def _get_project_root() -> Path:
    """Get the project root directory (parent of scripts/)."""
    return Path(__file__).parent.parent


class Paths:
    """Centralized path management for MetaMind."""
    
    # Base directories
    PROJECT_ROOT: Path = _get_project_root()
    SCRIPTS_DIR: Path = PROJECT_ROOT / "scripts"
    
    @classmethod
    def _get_from_env(cls, env_var: str, default: str) -> Path:
        """Get path from environment variable or use default."""
        value = os.getenv(env_var, default)
        path = Path(value)
        # If relative, make it relative to project root
        if not path.is_absolute():
            path = cls.PROJECT_ROOT / path
        return path
    
    # Output directories
    @classmethod
    def base_dir(cls) -> Path:
        """Base directory for all extracted metadata."""
        return cls._get_from_env("BASE_DIR", "extracted_meta")
    
    @classmethod
    def merged_dir(cls) -> Path:
        """Directory for merged metadata from multiple dashboards."""
        return cls._get_from_env("MERGED_DIR", "extracted_meta/merged_metadata")
    
    @classmethod
    def kb_dir(cls) -> Path:
        """Directory for knowledge base files."""
        return cls._get_from_env("KB_DIR", "extracted_meta/knowledge_base")
    
    @classmethod
    def golden_dataset_dir(cls) -> Path:
        """Directory for golden dataset files."""
        return cls.base_dir() / "golden_dataset"
    
    @classmethod
    def logs_dir(cls) -> Path:
        """Directory for log files."""
        return cls._get_from_env("LOGS_DIR", "logs")
    
    # Dashboard-specific paths
    @classmethod
    def dashboard_dir(cls, dashboard_id: int) -> Path:
        """Get directory for a specific dashboard's output files."""
        return cls.base_dir() / str(dashboard_id)
    
    @classmethod
    def dashboard_json(cls, dashboard_id: int) -> Path:
        """Path to dashboard JSON file."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_json.json"
    
    @classmethod
    def dashboard_csv(cls, dashboard_id: int) -> Path:
        """Path to dashboard CSV file."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_csv.csv"
    
    @classmethod
    def dashboard_sql(cls, dashboard_id: int) -> Path:
        """Path to dashboard SQL queries file."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_queries.sql"
    
    @classmethod
    def tables_columns_csv(cls, dashboard_id: int) -> Path:
        """Path to tables/columns mapping CSV."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_tables_columns.csv"
    
    @classmethod
    def tables_columns_enriched_csv(cls, dashboard_id: int) -> Path:
        """Path to enriched tables/columns CSV with datatypes."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_tables_columns_enriched.csv"
    
    @classmethod
    def table_metadata_csv(cls, dashboard_id: int) -> Path:
        """Path to table metadata CSV."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_table_metadata.csv"
    
    @classmethod
    def columns_metadata_csv(cls, dashboard_id: int) -> Path:
        """Path to columns metadata CSV."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_columns_metadata.csv"
    
    @classmethod
    def joining_conditions_csv(cls, dashboard_id: int) -> Path:
        """Path to joining conditions CSV."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_joining_conditions.csv"
    
    @classmethod
    def filter_conditions_txt(cls, dashboard_id: int) -> Path:
        """Path to filter conditions text file."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_filter_conditions.txt"
    
    @classmethod
    def definitions_csv(cls, dashboard_id: int) -> Path:
        """Path to definitions CSV."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_definitions.csv"
    
    @classmethod
    def quality_report_json(cls, dashboard_id: int) -> Path:
        """Path to quality report JSON."""
        return cls.dashboard_dir(dashboard_id) / f"{dashboard_id}_quality_report.json"
    
    # Progress tracking
    @classmethod
    def progress_file(cls) -> Path:
        """Path to progress tracking JSON file."""
        return cls._get_from_env("PROGRESS_FILE", "extracted_meta/progress.json")
    
    # Merged metadata files
    @classmethod
    def consolidated_table_metadata(cls) -> Path:
        """Path to consolidated table metadata."""
        return cls.merged_dir() / "consolidated_table_metadata.csv"
    
    @classmethod
    def consolidated_columns_metadata(cls) -> Path:
        """Path to consolidated columns metadata."""
        return cls.merged_dir() / "consolidated_columns_metadata.csv"
    
    @classmethod
    def consolidated_joining_conditions(cls) -> Path:
        """Path to consolidated joining conditions."""
        return cls.merged_dir() / "consolidated_joining_conditions.csv"
    
    @classmethod
    def consolidated_definitions(cls) -> Path:
        """Path to consolidated definitions."""
        return cls.merged_dir() / "consolidated_definitions.csv"
    
    @classmethod
    def consolidated_filter_conditions(cls) -> Path:
        """Path to consolidated filter conditions."""
        return cls.merged_dir() / "consolidated_filter_conditions.txt"
    
    # Knowledge base files
    @classmethod
    def kb_table_metadata(cls) -> Path:
        """Path to KB table metadata JSON."""
        return cls.kb_dir() / "table_metadata.json"
    
    @classmethod
    def kb_column_metadata(cls) -> Path:
        """Path to KB column metadata JSON."""
        return cls.kb_dir() / "column_metadata.json"
    
    @classmethod
    def kb_joining_conditions(cls) -> Path:
        """Path to KB joining conditions JSON."""
        return cls.kb_dir() / "joining_conditions.json"
    
    @classmethod
    def kb_definitions(cls) -> Path:
        """Path to KB definitions JSON."""
        return cls.kb_dir() / "definitions.json"
    
    @classmethod
    def kb_filter_conditions(cls) -> Path:
        """Path to KB filter conditions text."""
        return cls.kb_dir() / "filter_conditions.txt"
    
    @classmethod
    def kb_business_context(cls) -> Path:
        """Path to KB business context JSON."""
        return cls.kb_dir() / "business_context.json"
    
    @classmethod
    def kb_zip(cls) -> Path:
        """Path to KB zip archive."""
        return cls.kb_dir() / "knowledge_base_csv.zip"
    
    # Utility methods
    @classmethod
    def ensure_dir(cls, path: Path) -> Path:
        """Ensure directory exists, create if needed."""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def ensure_dashboard_dir(cls, dashboard_id: int) -> Path:
        """Ensure dashboard directory exists."""
        return cls.ensure_dir(cls.dashboard_dir(dashboard_id))
    
    @classmethod
    def ensure_all_dirs(cls) -> None:
        """Ensure all required directories exist."""
        cls.ensure_dir(cls.base_dir())
        cls.ensure_dir(cls.merged_dir())
        cls.ensure_dir(cls.kb_dir())
        cls.ensure_dir(cls.golden_dataset_dir())
        cls.ensure_dir(cls.logs_dir())

