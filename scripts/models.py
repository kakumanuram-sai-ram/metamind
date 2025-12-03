"""
Domain Models - Value Objects and Entities

This module defines type-safe, validated domain models to replace dictionaries.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json


class ChartType(Enum):
    """Enumeration of chart types"""
    BAR = "bar"
    LINE = "line"
    TABLE = "table"
    PIVOT = "pivot_table_v2"
    TIME_SERIES = "echarts_timeseries_smooth"
    TIME_SERIES_BAR = "echarts_timeseries_bar"
    TIME_SERIES_LINE = "echarts_timeseries_line"
    MIXED_TIME_SERIES = "mixed_timeseries"
    AREA = "area"
    PIE = "pie"
    BIG_NUMBER = "big_number"
    BIG_NUMBER_TOTAL = "big_number_total"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, value: str) -> 'ChartType':
        """Create ChartType from string, return UNKNOWN if not found"""
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExtractionPhase(Enum):
    """Extraction phase enumeration"""
    DASHBOARD_EXTRACTION = "dashboard_extraction"
    TABLE_COLUMN_EXTRACTION = "table_column_extraction"
    TRINO_ENRICHMENT = "trino_enrichment"
    TABLE_METADATA = "table_metadata"
    COLUMN_METADATA = "column_metadata"
    JOINING_CONDITIONS = "joining_conditions"
    FILTER_CONDITIONS = "filter_conditions"
    TERM_DEFINITIONS = "term_definitions"
    METADATA_CONSOLIDATION = "metadata_consolidation"
    KNOWLEDGE_BASE_BUILD = "knowledge_base_build"


@dataclass(frozen=True)
class ChartMetric:
    """Represents a chart metric - Immutable"""
    label: str
    expression_type: str
    aggregate: Optional[str] = None
    sql_expression: Optional[str] = None
    column_name: Optional[str] = None
    
    def __post_init__(self):
        if not self.label:
            raise ValueError("Metric label cannot be empty")
    
    @property
    def is_sql_metric(self) -> bool:
        """Check if metric is SQL-based"""
        return self.expression_type == "SQL"
    
    @property
    def is_simple_metric(self) -> bool:
        """Check if metric is simple aggregation"""
        return self.expression_type == "SIMPLE"


@dataclass(frozen=True)
class ChartFilter:
    """Represents a chart filter - Immutable"""
    subject: str
    operator: str
    comparator: Any
    expression_type: str = "SIMPLE"
    sql_expression: Optional[str] = None
    clause: str = "WHERE"
    
    @property
    def is_sql_filter(self) -> bool:
        """Check if filter is SQL-based"""
        return self.expression_type == "SQL"


@dataclass(frozen=True)
class ChartInfo:
    """
    Represents chart information - IMMUTABLE
    
    This is a Value Object - once created, it cannot be modified.
    Create a new instance if you need different values.
    """
    chart_id: int
    chart_name: str
    chart_type: ChartType
    sql_query: str
    dataset_id: int
    dataset_name: str
    database_name: str
    metrics: List[ChartMetric] = field(default_factory=list)
    filters: List[ChartFilter] = field(default_factory=list)
    groupby_columns: List[str] = field(default_factory=list)
    time_range: Optional[str] = None
    
    def __post_init__(self):
        # Validation
        if self.chart_id <= 0:
            raise ValueError(f"Invalid chart_id: {self.chart_id}")
        if not self.sql_query:
            raise ValueError(f"SQL query cannot be empty for chart {self.chart_id}")
    
    @property
    def has_metrics(self) -> bool:
        """Check if chart has metrics"""
        return len(self.metrics) > 0
    
    @property
    def has_filters(self) -> bool:
        """Check if chart has filters"""
        return len(self.filters) > 0
    
    @property
    def is_time_series(self) -> bool:
        """Check if chart is time series"""
        return self.chart_type in [
            ChartType.TIME_SERIES,
            ChartType.TIME_SERIES_BAR,
            ChartType.TIME_SERIES_LINE,
            ChartType.MIXED_TIME_SERIES
        ]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChartInfo':
        """Factory method to create from dictionary"""
        # Parse metrics
        metrics = []
        for m in data.get('metrics', []):
            if isinstance(m, dict):
                metrics.append(ChartMetric(
                    label=m.get('label', ''),
                    expression_type=m.get('expressionType', 'SIMPLE'),
                    aggregate=m.get('aggregate'),
                    sql_expression=m.get('sqlExpression'),
                    column_name=m.get('column', {}).get('column_name') if isinstance(m.get('column'), dict) else None
                ))
        
        # Parse filters
        filters = []
        for f in data.get('filters', []):
            if isinstance(f, dict):
                filters.append(ChartFilter(
                    subject=f.get('subject', ''),
                    operator=f.get('operator', ''),
                    comparator=f.get('comparator'),
                    expression_type=f.get('expressionType', 'SIMPLE'),
                    sql_expression=f.get('sqlExpression'),
                    clause=f.get('clause', 'WHERE')
                ))
        
        # Parse groupby columns
        groupby_cols = []
        for col in data.get('groupby_columns', []):
            if isinstance(col, str):
                groupby_cols.append(col)
            elif isinstance(col, dict):
                groupby_cols.append(col.get('column_name', col.get('label', '')))
        
        return cls(
            chart_id=data['chart_id'],
            chart_name=data.get('chart_name', 'Unnamed Chart'),
            chart_type=ChartType.from_string(data.get('chart_type', 'unknown')),
            sql_query=data.get('sql_query', ''),
            dataset_id=data.get('dataset_id', 0),
            dataset_name=data.get('dataset_name', ''),
            database_name=data.get('database_name', ''),
            metrics=metrics,
            filters=filters,
            groupby_columns=groupby_cols,
            time_range=data.get('time_range')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'chart_id': self.chart_id,
            'chart_name': self.chart_name,
            'chart_type': self.chart_type.value,
            'sql_query': self.sql_query,
            'dataset_id': self.dataset_id,
            'dataset_name': self.dataset_name,
            'database_name': self.database_name,
            'metrics': [
                {
                    'label': m.label,
                    'expressionType': m.expression_type,
                    'aggregate': m.aggregate,
                    'sqlExpression': m.sql_expression,
                }
                for m in self.metrics
            ],
            'filters': [
                {
                    'subject': f.subject,
                    'operator': f.operator,
                    'comparator': f.comparator,
                    'expressionType': f.expression_type,
                    'sqlExpression': f.sql_expression,
                    'clause': f.clause
                }
                for f in self.filters
            ],
            'groupby_columns': self.groupby_columns,
            'time_range': self.time_range
        }


@dataclass
class DashboardInfo:
    """
    Represents dashboard information - MUTABLE
    
    This is an Entity - it has identity (dashboard_id) and can change state.
    Use methods to modify state in a controlled way.
    """
    dashboard_id: int
    dashboard_title: str
    charts: List[ChartInfo]
    dashboard_url: Optional[str] = None
    owner: Optional[str] = None
    created_on: Optional[datetime] = None
    changed_on: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    current_phase: Optional[ExtractionPhase] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.dashboard_id <= 0:
            raise ValueError(f"Invalid dashboard_id: {self.dashboard_id}")
        if not self.dashboard_title:
            raise ValueError("Dashboard title cannot be empty")
    
    @property
    def chart_count(self) -> int:
        """Get number of charts"""
        return len(self.charts)
    
    @property
    def is_completed(self) -> bool:
        """Check if processing is completed"""
        return self.status == ProcessingStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if processing failed"""
        return self.status == ProcessingStatus.FAILED
    
    @property
    def is_processing(self) -> bool:
        """Check if currently processing"""
        return self.status == ProcessingStatus.PROCESSING
    
    def get_charts_by_type(self, chart_type: ChartType) -> List[ChartInfo]:
        """Get charts filtered by type"""
        return [c for c in self.charts if c.chart_type == chart_type]
    
    def mark_processing(self, phase: ExtractionPhase) -> None:
        """Mark dashboard as processing"""
        self.status = ProcessingStatus.PROCESSING
        self.current_phase = phase
        self.error_message = None
    
    def mark_completed(self) -> None:
        """Mark dashboard as completed"""
        self.status = ProcessingStatus.COMPLETED
        self.current_phase = None
        self.error_message = None
    
    def mark_failed(self, error: str) -> None:
        """Mark dashboard as failed"""
        self.status = ProcessingStatus.FAILED
        self.error_message = error
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DashboardInfo':
        """Factory method to create from dictionary"""
        # Parse charts
        charts = []
        for chart_data in data.get('charts', []):
            try:
                charts.append(ChartInfo.from_dict(chart_data))
            except Exception as e:
                # Skip invalid charts but log the error
                print(f"Warning: Skipping invalid chart: {e}")
        
        # Parse dates
        created_on = None
        if data.get('created_on'):
            try:
                created_on = datetime.fromisoformat(data['created_on'].replace('Z', '+00:00'))
            except:
                pass
        
        changed_on = None
        if data.get('changed_on'):
            try:
                changed_on = datetime.fromisoformat(data['changed_on'].replace('Z', '+00:00'))
            except:
                pass
        
        return cls(
            dashboard_id=data['dashboard_id'],
            dashboard_title=data.get('dashboard_title', 'Unnamed Dashboard'),
            dashboard_url=data.get('dashboard_url'),
            charts=charts,
            owner=data.get('owner'),
            created_on=created_on,
            changed_on=changed_on,
            status=ProcessingStatus(data.get('status', 'pending'))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'dashboard_id': self.dashboard_id,
            'dashboard_title': self.dashboard_title,
            'dashboard_url': self.dashboard_url,
            'owner': self.owner,
            'created_on': self.created_on.isoformat() if self.created_on else None,
            'changed_on': self.changed_on.isoformat() if self.changed_on else None,
            'status': self.status.value,
            'current_phase': self.current_phase.value if self.current_phase else None,
            'error_message': self.error_message,
            'charts': [chart.to_dict() for chart in self.charts]
        }


@dataclass(frozen=True)
class ExtractionResult:
    """Result of an extraction operation - Immutable"""
    dashboard_id: int
    success: bool
    phase: ExtractionPhase
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_success(self) -> bool:
        """Check if extraction succeeded"""
        return self.success
    
    @property
    def is_failure(self) -> bool:
        """Check if extraction failed"""
        return not self.success


