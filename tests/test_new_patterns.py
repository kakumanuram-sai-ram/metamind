"""
Unit Tests for New Architectural Patterns

Tests for:
- Configuration Object
- Value Objects
- Decorators
- Repository Pattern
- Factory Pattern
- Strategy Pattern
- Event System (Observer Pattern)
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import shutil

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from settings import AppSettings, Environment, get_settings, reset_settings
from models import (
    ChartType, ProcessingStatus, ExtractionPhase,
    ChartMetric, ChartFilter, ChartInfo, DashboardInfo, ExtractionResult
)
from decorators import retry, timed, cache_with_ttl, handle_errors, validate_args
from repositories import FileSystemDashboardRepository, InMemoryDashboardRepository
from factories import ServiceFactory, get_factory, reset_factory
from events import Event, EventType, EventBus, get_event_bus, reset_event_bus


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

class TestAppSettings:
    """Test AppSettings configuration management"""
    
    def test_settings_creation(self):
        """Test creating settings with valid data"""
        settings = AppSettings(
            superset_base_url="http://test.com",
            superset_cookie="test-cookie",
            superset_csrf_token="test-csrf",
            llm_api_key="test-key"
        )
        
        assert settings.superset_base_url == "http://test.com"
        assert settings.llm_model == "anthropic/claude-sonnet-4"
        assert settings.environment == Environment.DEVELOPMENT
    
    def test_settings_validation_missing_url(self):
        """Test validation fails with missing URL"""
        with pytest.raises(ValueError, match="superset_base_url"):
            AppSettings(
                superset_base_url="",
                superset_cookie="test",
                superset_csrf_token="test",
                llm_api_key="test"
            )
    
    def test_settings_from_env(self):
        """Test loading settings from environment"""
        with patch.dict(os.environ, {
            'SUPERSET_BASE_URL': 'http://env-test.com',
            'SUPERSET_COOKIE': 'env-cookie',
            'SUPERSET_CSRF_TOKEN': 'env-csrf',
            'ANTHROPIC_API_KEY': 'env-key'
        }):
            reset_settings()
            settings = get_settings()
            assert settings.superset_base_url == 'http://env-test.com'
    
    def test_settings_is_production(self):
        """Test production environment detection"""
        settings = AppSettings(
            superset_base_url="http://test.com",
            superset_cookie="test",
            superset_csrf_token="test",
            llm_api_key="test",
            environment=Environment.PRODUCTION
        )
        
        assert settings.is_production
        assert not settings.is_development


# ============================================================================
# VALUE OBJECT TESTS
# ============================================================================

class TestChartMetric:
    """Test ChartMetric value object"""
    
    def test_metric_creation(self):
        """Test creating a valid metric"""
        metric = ChartMetric(
            label="Total Users",
            expression_type="SQL",
            sql_expression="SUM(users)"
        )
        
        assert metric.label == "Total Users"
        assert metric.is_sql_metric
        assert not metric.is_simple_metric
    
    def test_metric_validation_empty_label(self):
        """Test validation fails with empty label"""
        with pytest.raises(ValueError, match="label cannot be empty"):
            ChartMetric(label="", expression_type="SQL")


class TestChartInfo:
    """Test ChartInfo value object"""
    
    def test_chart_creation(self):
        """Test creating a valid chart"""
        chart = ChartInfo(
            chart_id=123,
            chart_name="Test Chart",
            chart_type=ChartType.LINE,
            sql_query="SELECT * FROM table",
            dataset_id=456,
            dataset_name="Test Dataset",
            database_name="Trino"
        )
        
        assert chart.chart_id == 123
        assert chart.chart_type == ChartType.LINE
        assert not chart.is_time_series
    
    def test_chart_validation_invalid_id(self):
        """Test validation fails with invalid ID"""
        with pytest.raises(ValueError, match="Invalid chart_id"):
            ChartInfo(
                chart_id=-1,
                chart_name="Test",
                chart_type=ChartType.LINE,
                sql_query="SELECT 1",
                dataset_id=1,
                dataset_name="Test",
                database_name="Trino"
            )
    
    def test_chart_from_dict(self):
        """Test creating chart from dictionary"""
        data = {
            'chart_id': 123,
            'chart_name': 'Test Chart',
            'chart_type': 'line',
            'sql_query': 'SELECT 1',
            'dataset_id': 456,
            'dataset_name': 'Test Dataset',
            'database_name': 'Trino',
            'metrics': [
                {'label': 'Metric1', 'expressionType': 'SIMPLE'}
            ]
        }
        
        chart = ChartInfo.from_dict(data)
        assert chart.chart_id == 123
        assert len(chart.metrics) == 1


class TestDashboardInfo:
    """Test DashboardInfo entity"""
    
    def test_dashboard_creation(self):
        """Test creating a valid dashboard"""
        chart = ChartInfo(
            chart_id=1,
            chart_name="Chart 1",
            chart_type=ChartType.BAR,
            sql_query="SELECT 1",
            dataset_id=1,
            dataset_name="Test",
            database_name="Trino"
        )
        
        dashboard = DashboardInfo(
            dashboard_id=964,
            dashboard_title="Test Dashboard",
            charts=[chart]
        )
        
        assert dashboard.dashboard_id == 964
        assert dashboard.chart_count == 1
        assert not dashboard.is_completed
    
    def test_dashboard_status_transitions(self):
        """Test dashboard status transitions"""
        dashboard = DashboardInfo(
            dashboard_id=1,
            dashboard_title="Test",
            charts=[]
        )
        
        assert dashboard.status == ProcessingStatus.PENDING
        
        dashboard.mark_processing(ExtractionPhase.DASHBOARD_EXTRACTION)
        assert dashboard.is_processing
        assert dashboard.current_phase == ExtractionPhase.DASHBOARD_EXTRACTION
        
        dashboard.mark_completed()
        assert dashboard.is_completed
        assert dashboard.current_phase is None
    
    def test_dashboard_mark_failed(self):
        """Test marking dashboard as failed"""
        dashboard = DashboardInfo(
            dashboard_id=1,
            dashboard_title="Test",
            charts=[]
        )
        
        dashboard.mark_failed("Test error")
        assert dashboard.is_failed
        assert dashboard.error_message == "Test error"


# ============================================================================
# DECORATOR TESTS
# ============================================================================

class TestDecorators:
    """Test decorator functionality"""
    
    def test_retry_decorator_success(self):
        """Test retry decorator with successful function"""
        call_count = [0]
        
        @retry(max_attempts=3, delay=0.1)
        def flaky_function():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert call_count[0] == 2  # Failed once, succeeded second time
    
    def test_retry_decorator_exhaustion(self):
        """Test retry decorator exhausts attempts"""
        @retry(max_attempts=2, delay=0.1)
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_fails()
    
    def test_handle_errors_decorator(self):
        """Test error handling decorator"""
        @handle_errors(default_return="fallback", log_error=False)
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        assert result == "fallback"
    
    def test_validate_args_decorator(self):
        """Test argument validation decorator"""
        @validate_args(
            x=lambda v: v > 0,
            y=lambda v: isinstance(v, str)
        )
        def test_func(x: int, y: str):
            return x, y
        
        # Valid call
        result = test_func(5, "test")
        assert result == (5, "test")
        
        # Invalid call
        with pytest.raises(ValueError, match="Validation failed"):
            test_func(-1, "test")
    
    def test_cache_decorator(self):
        """Test caching decorator"""
        call_count = [0]
        
        @cache_with_ttl(ttl_seconds=1)
        def expensive_function(x):
            call_count[0] += 1
            return x * 2
        
        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count[0] == 1
        
        # Second call - should hit cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count[0] == 1  # No additional call
        
        # Clear cache
        expensive_function.cache_clear()
        
        # Third call - cache cleared
        result3 = expensive_function(5)
        assert result3 == 10
        assert call_count[0] == 2  # Additional call


# ============================================================================
# REPOSITORY PATTERN TESTS
# ============================================================================

class TestFileSystemRepository:
    """Test FileSystemDashboardRepository"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)
    
    @pytest.fixture
    def repository(self, temp_dir):
        """Create repository instance"""
        return FileSystemDashboardRepository(temp_dir)
    
    @pytest.fixture
    def sample_dashboard(self):
        """Create sample dashboard"""
        chart = ChartInfo(
            chart_id=1,
            chart_name="Test Chart",
            chart_type=ChartType.LINE,
            sql_query="SELECT 1",
            dataset_id=1,
            dataset_name="Test",
            database_name="Trino"
        )
        
        return DashboardInfo(
            dashboard_id=999,
            dashboard_title="Test Dashboard",
            charts=[chart]
        )
    
    def test_save_and_get_dashboard(self, repository, sample_dashboard):
        """Test saving and retrieving dashboard"""
        # Save
        repository.save(sample_dashboard)
        
        # Retrieve
        loaded = repository.get(999)
        assert loaded is not None
        assert loaded.dashboard_id == 999
        assert loaded.dashboard_title == "Test Dashboard"
    
    def test_exists(self, repository, sample_dashboard):
        """Test checking if dashboard exists"""
        assert not repository.exists(999)
        
        repository.save(sample_dashboard)
        assert repository.exists(999)
    
    def test_delete(self, repository, sample_dashboard):
        """Test deleting dashboard"""
        repository.save(sample_dashboard)
        assert repository.exists(999)
        
        repository.delete(999)
        assert not repository.exists(999)
    
    def test_list_all(self, repository, sample_dashboard):
        """Test listing all dashboards"""
        # Initially empty
        dashboards = repository.list_all()
        assert len(dashboards) == 0
        
        # Save dashboard
        repository.save(sample_dashboard)
        
        # Should have one
        dashboards = repository.list_all()
        assert len(dashboards) == 1


class TestInMemoryRepository:
    """Test InMemoryDashboardRepository"""
    
    @pytest.fixture
    def repository(self):
        """Create in-memory repository"""
        return InMemoryDashboardRepository()
    
    @pytest.fixture
    def sample_dashboard(self):
        """Create sample dashboard"""
        return DashboardInfo(
            dashboard_id=999,
            dashboard_title="Test Dashboard",
            charts=[]
        )
    
    def test_save_and_get(self, repository, sample_dashboard):
        """Test in-memory save and get"""
        repository.save(sample_dashboard)
        
        loaded = repository.get(999)
        assert loaded is not None
        assert loaded.dashboard_id == 999
    
    def test_isolation(self):
        """Test that different instances don't share data"""
        repo1 = InMemoryDashboardRepository()
        repo2 = InMemoryDashboardRepository()
        
        dashboard = DashboardInfo(
            dashboard_id=1,
            dashboard_title="Test",
            charts=[]
        )
        
        repo1.save(dashboard)
        
        assert repo1.exists(1)
        assert not repo2.exists(1)  # Different instance


# ============================================================================
# FACTORY PATTERN TESTS
# ============================================================================

class TestServiceFactory:
    """Test ServiceFactory"""
    
    @pytest.fixture(autouse=True)
    def reset(self):
        """Reset factory before each test"""
        reset_factory()
        yield
        reset_factory()
    
    @pytest.fixture
    def test_settings(self):
        """Create test settings"""
        return AppSettings(
            superset_base_url="http://test.com",
            superset_cookie="test-cookie",
            superset_csrf_token="test-csrf",
            llm_api_key="test-key"
        )
    
    def test_factory_creation(self, test_settings):
        """Test creating factory with settings"""
        factory = ServiceFactory(test_settings)
        assert factory.settings == test_settings
    
    def test_create_repository(self, test_settings):
        """Test creating repository via factory"""
        factory = ServiceFactory(test_settings)
        repo = factory.create_dashboard_repository()
        
        assert repo is not None
        assert isinstance(repo, FileSystemDashboardRepository)
    
    def test_singleton_behavior(self, test_settings):
        """Test factory returns same instance for cached services"""
        factory = ServiceFactory(test_settings)
        
        repo1 = factory.create_dashboard_repository()
        repo2 = factory.create_dashboard_repository()
        
        assert repo1 is repo2  # Same instance
    
    def test_get_event_bus(self, test_settings):
        """Test getting event bus from factory"""
        factory = ServiceFactory(test_settings)
        event_bus = factory.get_event_bus()
        
        assert event_bus is not None
        assert isinstance(event_bus, EventBus)


# ============================================================================
# EVENT SYSTEM TESTS
# ============================================================================

class TestEventSystem:
    """Test Observer pattern implementation"""
    
    @pytest.fixture(autouse=True)
    def reset(self):
        """Reset event bus before each test"""
        reset_event_bus()
        yield
        reset_event_bus()
    
    def test_subscribe_and_publish(self):
        """Test basic publish-subscribe"""
        event_bus = get_event_bus()
        received_events = []
        
        def handler(event: Event):
            received_events.append(event)
        
        event_bus.subscribe(EventType.DASHBOARD_STARTED, handler)
        
        # Publish event
        event = Event(
            EventType.DASHBOARD_STARTED,
            {'dashboard_id': 123}
        )
        event_bus.publish(event)
        
        # Verify handler was called
        assert len(received_events) == 1
        assert received_events[0].data['dashboard_id'] == 123
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same event"""
        event_bus = get_event_bus()
        call_counts = {'handler1': 0, 'handler2': 0}
        
        def handler1(event: Event):
            call_counts['handler1'] += 1
        
        def handler2(event: Event):
            call_counts['handler2'] += 1
        
        event_bus.subscribe(EventType.DASHBOARD_STARTED, handler1)
        event_bus.subscribe(EventType.DASHBOARD_STARTED, handler2)
        
        event = Event(EventType.DASHBOARD_STARTED, {})
        event_bus.publish(event)
        
        assert call_counts['handler1'] == 1
        assert call_counts['handler2'] == 1
    
    def test_subscribe_all(self):
        """Test subscribing to all events"""
        event_bus = get_event_bus()
        received_events = []
        
        def global_handler(event: Event):
            received_events.append(event)
        
        event_bus.subscribe_all(global_handler)
        
        # Publish different event types
        event_bus.publish(Event(EventType.DASHBOARD_STARTED, {}))
        event_bus.publish(Event(EventType.DASHBOARD_COMPLETED, {}))
        
        # Should receive both
        assert len(received_events) == 2
    
    def test_error_in_handler_doesnt_break_others(self):
        """Test that errors in one handler don't affect others"""
        event_bus = get_event_bus()
        handler2_called = [False]
        
        def failing_handler(event: Event):
            raise ValueError("Handler error")
        
        def success_handler(event: Event):
            handler2_called[0] = True
        
        event_bus.subscribe(EventType.DASHBOARD_STARTED, failing_handler)
        event_bus.subscribe(EventType.DASHBOARD_STARTED, success_handler)
        
        event = Event(EventType.DASHBOARD_STARTED, {})
        event_bus.publish(event)  # Should not raise
        
        assert handler2_called[0]  # Second handler still executed


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test patterns working together"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)
    
    def test_full_workflow(self, temp_dir):
        """Test complete workflow with all patterns"""
        # Setup
        reset_factory()
        reset_event_bus()
        
        settings = AppSettings(
            superset_base_url="http://test.com",
            superset_cookie="test",
            superset_csrf_token="test",
            llm_api_key="test",
            base_dir=temp_dir
        )
        
        factory = ServiceFactory(settings)
        event_bus = factory.get_event_bus()
        repository = factory.create_dashboard_repository()
        
        # Subscribe to events
        events_received = []
        
        def track_events(event: Event):
            events_received.append(event.event_type)
        
        event_bus.subscribe_all(track_events)
        
        # Create dashboard
        chart = ChartInfo(
            chart_id=1,
            chart_name="Test",
            chart_type=ChartType.TABLE,
            sql_query="SELECT 1",
            dataset_id=1,
            dataset_name="Test",
            database_name="Trino"
        )
        
        dashboard = DashboardInfo(
            dashboard_id=123,
            dashboard_title="Integration Test",
            charts=[chart]
        )
        
        # Publish start event
        event_bus.publish(Event(
            EventType.DASHBOARD_STARTED,
            {'dashboard_id': 123}
        ))
        
        # Process (using repository)
        dashboard.mark_processing(ExtractionPhase.DASHBOARD_EXTRACTION)
        repository.save(dashboard)
        
        # Verify saved
        loaded = repository.get(123)
        assert loaded is not None
        
        # Complete
        dashboard.mark_completed()
        repository.save(dashboard)
        
        event_bus.publish(Event(
            EventType.DASHBOARD_COMPLETED,
            {'dashboard_id': 123}
        ))
        
        # Verify events
        assert EventType.DASHBOARD_STARTED in events_received
        assert EventType.DASHBOARD_COMPLETED in events_received


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

