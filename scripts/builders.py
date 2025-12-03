"""
Builder Pattern - Fluent API for Complex Object Construction

This module provides builder classes for constructing complex objects
with a fluent, chainable API.
"""
from typing import List, Optional
from datetime import datetime

try:
    from models import (
        ChartInfo, DashboardInfo, ChartMetric, ChartFilter,
        ChartType, ProcessingStatus, ExtractionPhase
    )
except ImportError:
    from scripts.models import (
        ChartInfo, DashboardInfo, ChartMetric, ChartFilter,
        ChartType, ProcessingStatus, ExtractionPhase
    )


class ChartBuilder:
    """Fluent builder for ChartInfo objects"""
    
    def __init__(self):
        """Initialize builder with defaults"""
        self._chart_id: Optional[int] = None
        self._chart_name: str = ""
        self._chart_type: ChartType = ChartType.UNKNOWN
        self._sql_query: str = ""
        self._dataset_id: int = 0
        self._dataset_name: str = ""
        self._database_name: str = ""
        self._metrics: List[ChartMetric] = []
        self._filters: List[ChartFilter] = []
        self._groupby_columns: List[str] = []
        self._time_range: Optional[str] = None
    
    def with_id(self, chart_id: int) -> 'ChartBuilder':
        """Set chart ID"""
        self._chart_id = chart_id
        return self
    
    def with_name(self, name: str) -> 'ChartBuilder':
        """Set chart name"""
        self._chart_name = name
        return self
    
    def with_type(self, chart_type: ChartType) -> 'ChartBuilder':
        """Set chart type"""
        self._chart_type = chart_type
        return self
    
    def with_sql(self, sql_query: str) -> 'ChartBuilder':
        """Set SQL query"""
        self._sql_query = sql_query
        return self
    
    def with_dataset(self, dataset_id: int, dataset_name: str) -> 'ChartBuilder':
        """Set dataset information"""
        self._dataset_id = dataset_id
        self._dataset_name = dataset_name
        return self
    
    def with_database(self, database_name: str) -> 'ChartBuilder':
        """Set database name"""
        self._database_name = database_name
        return self
    
    def add_metric(self, metric: ChartMetric) -> 'ChartBuilder':
        """Add a metric"""
        self._metrics.append(metric)
        return self
    
    def add_filter(self, filter: ChartFilter) -> 'ChartBuilder':
        """Add a filter"""
        self._filters.append(filter)
        return self
    
    def add_groupby_column(self, column: str) -> 'ChartBuilder':
        """Add a groupby column"""
        self._groupby_columns.append(column)
        return self
    
    def with_time_range(self, time_range: str) -> 'ChartBuilder':
        """Set time range"""
        self._time_range = time_range
        return self
    
    def build(self) -> ChartInfo:
        """
        Build the final ChartInfo object.
        
        Returns:
            ChartInfo instance
        
        Raises:
            ValueError: If required fields are missing
        """
        if self._chart_id is None:
            raise ValueError("Chart ID is required")
        if not self._sql_query:
            raise ValueError("SQL query is required")
        
        return ChartInfo(
            chart_id=self._chart_id,
            chart_name=self._chart_name,
            chart_type=self._chart_type,
            sql_query=self._sql_query,
            dataset_id=self._dataset_id,
            dataset_name=self._dataset_name,
            database_name=self._database_name,
            metrics=self._metrics,
            filters=self._filters,
            groupby_columns=self._groupby_columns,
            time_range=self._time_range
        )


class DashboardBuilder:
    """Fluent builder for DashboardInfo objects"""
    
    def __init__(self):
        """Initialize builder with defaults"""
        self._dashboard_id: Optional[int] = None
        self._dashboard_title: str = ""
        self._dashboard_url: Optional[str] = None
        self._charts: List[ChartInfo] = []
        self._owner: Optional[str] = None
        self._created_on: Optional[datetime] = None
        self._changed_on: Optional[datetime] = None
        self._status: ProcessingStatus = ProcessingStatus.PENDING
        self._current_phase: Optional[ExtractionPhase] = None
        self._error_message: Optional[str] = None
    
    def with_id(self, dashboard_id: int) -> 'DashboardBuilder':
        """Set dashboard ID"""
        self._dashboard_id = dashboard_id
        return self
    
    def with_title(self, title: str) -> 'DashboardBuilder':
        """Set dashboard title"""
        self._dashboard_title = title
        return self
    
    def with_url(self, url: str) -> 'DashboardBuilder':
        """Set dashboard URL"""
        self._dashboard_url = url
        return self
    
    def with_owner(self, owner: str) -> 'DashboardBuilder':
        """Set dashboard owner"""
        self._owner = owner
        return self
    
    def with_created_on(self, created_on: datetime) -> 'DashboardBuilder':
        """Set created timestamp"""
        self._created_on = created_on
        return self
    
    def with_changed_on(self, changed_on: datetime) -> 'DashboardBuilder':
        """Set changed timestamp"""
        self._changed_on = changed_on
        return self
    
    def with_status(self, status: ProcessingStatus) -> 'DashboardBuilder':
        """Set processing status"""
        self._status = status
        return self
    
    def with_phase(self, phase: ExtractionPhase) -> 'DashboardBuilder':
        """Set current phase"""
        self._current_phase = phase
        return self
    
    def with_error_message(self, error_message: str) -> 'DashboardBuilder':
        """Set error message for failed processing"""
        self._error_message = error_message
        return self
    
    def add_chart(self, chart: ChartInfo) -> 'DashboardBuilder':
        """Add a chart"""
        self._charts.append(chart)
        return self
    
    def add_charts(self, charts: List[ChartInfo]) -> 'DashboardBuilder':
        """Add multiple charts"""
        self._charts.extend(charts)
        return self
    
    def build(self) -> DashboardInfo:
        """
        Build the final DashboardInfo object.
        
        Returns:
            DashboardInfo instance
        
        Raises:
            ValueError: If required fields are missing
        """
        if self._dashboard_id is None:
            raise ValueError("Dashboard ID is required")
        if not self._dashboard_title:
            raise ValueError("Dashboard title is required")
        
        return DashboardInfo(
            dashboard_id=self._dashboard_id,
            dashboard_title=self._dashboard_title,
            dashboard_url=self._dashboard_url,
            charts=self._charts,
            owner=self._owner,
            created_on=self._created_on,
            changed_on=self._changed_on,
            status=self._status,
            current_phase=self._current_phase,
            error_message=self._error_message
        )


# Convenience functions
def build_chart() -> ChartBuilder:
    """Create a new ChartBuilder"""
    return ChartBuilder()


def build_dashboard() -> DashboardBuilder:
    """Create a new DashboardBuilder"""
    return DashboardBuilder()

