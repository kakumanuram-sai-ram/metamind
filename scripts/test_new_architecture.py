"""
Test Script for New Architecture

This script demonstrates all the new architectural patterns working together
to extract dashboard metadata.
"""
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import new architecture components
from settings import get_settings, AppSettings
from models import DashboardInfo, ProcessingStatus, ExtractionPhase
from repositories import FileSystemDashboardRepository
from factories import get_factory
from events import Event, EventType, get_event_bus
from decorators import timed, retry, handle_errors


# Event handlers to demonstrate Observer pattern
def on_dashboard_started(event: Event):
    """Handle dashboard started event"""
    dashboard_id = event.data.get('dashboard_id')
    logger.info(f"📊 Dashboard {dashboard_id} extraction started")


def on_dashboard_completed(event: Event):
    """Handle dashboard completed event"""
    dashboard_id = event.data.get('dashboard_id')
    logger.info(f"✅ Dashboard {dashboard_id} extraction completed")


def on_dashboard_failed(event: Event):
    """Handle dashboard failed event"""
    dashboard_id = event.data.get('dashboard_id')
    error = event.data.get('error', 'Unknown error')
    logger.error(f"❌ Dashboard {dashboard_id} extraction failed: {error}")


@timed(log_level="INFO")
@retry(max_attempts=2, delay=1)
@handle_errors(default_return=None, log_error=True)
def extract_dashboard_metadata(dashboard_id: int) -> DashboardInfo:
    """
    Extract dashboard metadata using new architecture.
    
    Demonstrates:
    - Settings management
    - Repository pattern
    - Factory pattern
    - Event bus (Observer pattern)
    - Decorators
    - Value objects (DashboardInfo, ChartInfo)
    
    Args:
        dashboard_id: ID of dashboard to extract
    
    Returns:
        DashboardInfo object or None on failure
    """
    # Get settings (Configuration Object pattern)
    settings = get_settings()
    logger.info(f"Using Superset URL: {settings.superset_base_url}")
    logger.info(f"LLM extraction enabled: {settings.enable_llm_extraction}")
    
    # Get factory (Factory pattern)
    factory = get_factory(settings)
    
    # Get services from factory
    repository = factory.create_dashboard_repository()
    extractor = factory.create_superset_extractor()
    event_bus = factory.get_event_bus()
    
    # Subscribe to events (Observer pattern)
    event_bus.subscribe(EventType.DASHBOARD_STARTED, on_dashboard_started)
    event_bus.subscribe(EventType.DASHBOARD_COMPLETED, on_dashboard_completed)
    event_bus.subscribe(EventType.DASHBOARD_FAILED, on_dashboard_failed)
    
    try:
        # Publish start event
        event_bus.publish(Event(
            EventType.DASHBOARD_STARTED,
            {'dashboard_id': dashboard_id},
            source='test_script'
        ))
        
        logger.info(f"Extracting dashboard {dashboard_id} from Superset...")
        
        # Extract dashboard data - returns a dataclass DashboardInfo
        dashboard = extractor.extract_dashboard_complete_info(dashboard_id)
        
        if not dashboard:
            raise Exception(f"Failed to extract dashboard {dashboard_id}")
        
        logger.info(f"Dashboard extracted: {dashboard.dashboard_title}")
        logger.info(f"Total charts: {len(dashboard.charts)}")
        
        # The dashboard is already extracted and saved by the extractor
        # Demonstrate repository pattern by verifying it exists
        logger.info(f"Verifying dashboard in repository...")
        
        # Check if files exist
        json_file = repository.get_file_path(dashboard_id, 'json')
        if json_file and json_file.exists():
            logger.info(f"✅ Dashboard JSON found: {json_file}")
        
        sql_file = repository.get_file_path(dashboard_id, 'sql')
        if sql_file and sql_file.exists():
            logger.info(f"✅ Dashboard SQL found: {sql_file}")
        
        csv_file = repository.get_file_path(dashboard_id, 'csv')
        if csv_file and csv_file.exists():
            logger.info(f"✅ Dashboard CSV found: {csv_file}")
        
        # Publish completion event
        event_bus.publish(Event(
            EventType.DASHBOARD_COMPLETED,
            {'dashboard_id': dashboard_id, 'charts': len(dashboard.charts)},
            source='test_script'
        ))
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Error extracting dashboard: {e}", exc_info=True)
        
        # Publish failure event
        event_bus.publish(Event(
            EventType.DASHBOARD_FAILED,
            {'dashboard_id': dashboard_id, 'error': str(e)},
            source='test_script'
        ))
        
        raise


def demonstrate_type_safety():
    """Demonstrate type safety with Value Objects"""
    from models import ChartInfo, ChartType, ChartMetric
    
    logger.info("\n" + "="*80)
    logger.info("Demonstrating Type Safety with Value Objects")
    logger.info("="*80)
    
    # Create a chart with type safety
    try:
        metric = ChartMetric(
            label="Total Users",
            expression_type="SQL",
            sql_expression="SUM(users)"
        )
        
        chart = ChartInfo(
            chart_id=1,
            chart_name="User Growth",
            chart_type=ChartType.LINE,
            sql_query="SELECT date, SUM(users) FROM table GROUP BY date",
            dataset_id=100,
            dataset_name="Analytics",
            database_name="Trino",
            metrics=[metric]
        )
        
        logger.info(f"✅ Created chart: {chart.chart_name}")
        logger.info(f"   Type: {chart.chart_type.value}")
        logger.info(f"   Has metrics: {chart.has_metrics}")
        logger.info(f"   Is time series: {chart.is_time_series}")
        
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")


def demonstrate_settings():
    """Demonstrate centralized configuration"""
    logger.info("\n" + "="*80)
    logger.info("Demonstrating Centralized Configuration")
    logger.info("="*80)
    
    settings = get_settings()
    
    logger.info(f"Superset URL: {settings.superset_base_url}")
    logger.info(f"LLM Model: {settings.llm_model}")
    logger.info(f"Base Directory: {settings.base_dir}")
    logger.info(f"Cache Enabled: {settings.enable_caching}")
    logger.info(f"Cache TTL: {settings.cache_ttl_seconds}s")
    logger.info(f"Environment: {settings.environment.value}")
    logger.info(f"Is Production: {settings.is_production}")


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test new architecture with dashboard extraction")
    parser.add_argument(
        'dashboard_id',
        type=int,
        nargs='?',
        default=511,
        help='Dashboard ID to extract (default: 511)'
    )
    parser.add_argument(
        '--demo-only',
        action='store_true',
        help='Only run demonstrations without extracting'
    )
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("🚀 Testing New MetaMind Architecture")
    logger.info("="*80)
    
    # Demonstrate patterns
    demonstrate_settings()
    demonstrate_type_safety()
    
    if not args.demo_only:
        logger.info("\n" + "="*80)
        logger.info(f"Extracting Dashboard {args.dashboard_id}")
        logger.info("="*80)
        
        try:
            dashboard = extract_dashboard_metadata(args.dashboard_id)
            
            if dashboard:
                logger.info("\n" + "="*80)
                logger.info("📊 Extraction Summary")
                logger.info("="*80)
                logger.info(f"Dashboard ID: {dashboard.dashboard_id}")
                logger.info(f"Title: {dashboard.dashboard_title}")
                logger.info(f"Total Charts: {len(dashboard.charts)}")
                logger.info(f"URL: {dashboard.dashboard_url}")
                
                # Show chart types breakdown
                from collections import Counter
                chart_types = Counter(c.chart_type for c in dashboard.charts)
                logger.info("\nChart Types:")
                for chart_type, count in chart_types.most_common():
                    # chart_type is a string in the old DashboardInfo
                    logger.info(f"  {chart_type}: {count}")
                
                logger.info("\n✅ All patterns demonstrated successfully!")
                return 0
            else:
                logger.error("Extraction failed")
                return 1
                
        except Exception as e:
            logger.error(f"Test failed: {e}", exc_info=True)
            return 1
    else:
        logger.info("\n✅ Demonstrations completed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())

