# Quick Start Guide - New Architecture Patterns

## 🚀 5-Minute Quick Start

### 1. Import the New Patterns

```python
# Core configuration
from settings import get_settings

# Data models
from models import DashboardInfo, ChartInfo, ChartType, ProcessingStatus

# Service creation
from factories import get_factory

# Event system
from events import get_event_bus, Event, EventType

# Decorators
from decorators import retry, timed, cache_with_ttl, handle_errors

# Repository
from repositories import FileSystemDashboardRepository

# Builders
from builders import build_chart, build_dashboard
```

### 2. Basic Usage

```python
# Get configuration
settings = get_settings()
print(f"Superset URL: {settings.superset_base_url}")

# Create services using factory
factory = get_factory()
extractor = factory.create_superset_extractor()
repository = factory.create_dashboard_repository()

# Extract a dashboard
dashboard = extractor.extract_dashboard_complete_info(511)

# Save to repository
repository.save(dashboard)

# Verify
if repository.exists(511):
    print("✅ Dashboard 511 saved successfully!")
```

---

## 📖 Common Use Cases

### Use Case 1: Add Caching to Any Function

```python
from decorators import cache_with_ttl

@cache_with_ttl(ttl_seconds=600)  # Cache for 10 minutes
def get_all_verticals():
    """This will only hit the API once every 10 minutes"""
    return expensive_api_call()
```

### Use Case 2: Add Retry Logic

```python
from decorators import retry
import requests

@retry(max_attempts=3, delay=1, backoff=2, exceptions=(requests.RequestException,))
def fetch_chart_data(chart_id: int):
    """Automatically retries on network errors"""
    response = requests.get(f"/api/chart/{chart_id}")
    response.raise_for_status()
    return response.json()
```

### Use Case 3: Subscribe to Events

```python
from events import get_event_bus, EventType

event_bus = get_event_bus()

def on_dashboard_completed(event):
    dashboard_id = event.data['dashboard_id']
    print(f"🎉 Dashboard {dashboard_id} completed!")
    # Send notification, update UI, etc.

event_bus.subscribe(EventType.DASHBOARD_COMPLETED, on_dashboard_completed)
```

### Use Case 4: Build Complex Objects

```python
from builders import build_chart, build_dashboard
from models import ChartType, ProcessingStatus

# Build a chart with fluent API
chart = (build_chart()
    .with_id(123)
    .with_name("User Growth Chart")
    .with_type(ChartType.LINE)
    .with_sql("SELECT date, COUNT(*) FROM users GROUP BY date")
    .with_dataset(456, "User Analytics")
    .with_database("Trino")
    .build())

# Build a dashboard
dashboard = (build_dashboard()
    .with_id(964)
    .with_title("UPI Analytics Dashboard")
    .add_chart(chart)
    .with_status(ProcessingStatus.COMPLETED)
    .build())
```

### Use Case 5: Validate Function Arguments

```python
from decorators import validate_args

@validate_args(
    dashboard_id=lambda x: isinstance(x, int) and x > 0,
    extract_charts=lambda x: isinstance(x, bool)
)
def process_dashboard(dashboard_id: int, extract_charts: bool = True):
    """Arguments are validated automatically before function runs"""
    # Your logic here
    pass

# This will raise ValueError: Validation failed
# process_dashboard(-1, True)

# This works
process_dashboard(511, True)
```

### Use Case 6: Centralized Error Handling

```python
from decorators import handle_errors

@handle_errors(default_return=[], log_error=True)
def get_dashboard_charts(dashboard_id: int):
    """Returns [] on any error instead of crashing"""
    # If this raises an exception, [] is returned
    return api.get_charts(dashboard_id)
```

### Use Case 7: Type-Safe Data Models

```python
from models import ChartInfo, ChartType, ChartMetric

# Type-safe construction
metric = ChartMetric(
    label="Total Users",
    expression_type="SQL",
    sql_expression="SUM(users)"
)

chart = ChartInfo(
    chart_id=123,
    chart_name="User Growth",
    chart_type=ChartType.LINE,  # Enum, not string!
    sql_query="SELECT ...",
    dataset_id=456,
    dataset_name="Analytics",
    database_name="Trino",
    metrics=[metric]
)

# Type-safe access with autocomplete
if chart.is_time_series:
    print(f"Time series chart with {len(chart.metrics)} metrics")

# This won't compile with type checking:
# chart.chart_id = "wrong"  # Type error!
```

### Use Case 8: Repository Pattern for Storage

```python
from repositories import FileSystemDashboardRepository
from pathlib import Path

# Create repository
repo = FileSystemDashboardRepository(Path("extracted_meta"))

# Save
repo.save(dashboard)

# Load
dashboard = repo.get(511)

# Check existence
if repo.exists(511):
    print("Found!")

# List all
all_dashboards = repo.list_all()
for dash in all_dashboards:
    print(f"Dashboard {dash.dashboard_id}: {dash.dashboard_title}")

# Delete
repo.delete(511)
```

### Use Case 9: Strategy Pattern for Algorithms

```python
from strategies import create_extraction_strategy

# Create LLM-based extraction
llm_strategy = create_extraction_strategy(
    strategy_type="llm",
    api_key=settings.llm_api_key,
    model=settings.llm_model,
    base_url=settings.llm_base_url
)

# Create rule-based extraction
rule_strategy = create_extraction_strategy(
    strategy_type="rule_based"
)

# Create hybrid (tries LLM, falls back to rules)
hybrid_strategy = create_extraction_strategy(
    strategy_type="hybrid",
    api_key=settings.llm_api_key,
    model=settings.llm_model,
    base_url=settings.llm_base_url
)

# Use any strategy interchangeably
result = hybrid_strategy.extract_tables_columns(chart)
```

---

## 🔧 Configuration

### Option 1: Environment Variables (Recommended)

```bash
# Create .env file (don't commit!)
export SUPERSET_BASE_URL="https://cdp-dataview.platform.mypaytm.com"
export SUPERSET_COOKIE="session=..."
export SUPERSET_CSRF_TOKEN="..."
export ANTHROPIC_API_KEY="sk-..."
export LLM_MODEL="anthropic/claude-sonnet-4"
export ENABLE_CACHING="true"
export CACHE_TTL_SECONDS="600"
```

```python
# Load automatically
from settings import get_settings

settings = get_settings()  # Loads from env vars
```

### Option 2: Programmatic Configuration

```python
from settings import AppSettings, Environment

settings = AppSettings(
    superset_base_url="http://localhost:8088",
    superset_cookie="test-cookie",
    superset_csrf_token="test-csrf",
    llm_api_key="test-key",
    environment=Environment.DEVELOPMENT,
    enable_caching=True,
    cache_ttl_seconds=300
)
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all new pattern tests
python3 -m pytest tests/test_new_patterns.py -v

# Run specific test
python3 -m pytest tests/test_new_patterns.py::TestDecorators::test_retry_decorator_success -v

# Run with coverage
python3 -m pytest tests/test_new_patterns.py --cov=scripts --cov-report=html

# Run integration test
python3 scripts/test_new_architecture.py 511
```

### Writing Tests with New Patterns

```python
from repositories import InMemoryDashboardRepository
from models import DashboardInfo

def test_my_feature():
    # Use in-memory repository for fast tests
    repo = InMemoryDashboardRepository()
    
    # Create test data
    dashboard = DashboardInfo(
        dashboard_id=999,
        dashboard_title="Test Dashboard",
        charts=[]
    )
    
    # Test
    repo.save(dashboard)
    assert repo.exists(999)
    
    loaded = repo.get(999)
    assert loaded.dashboard_id == 999
```

---

## 📊 Before/After Comparison

### Before (Old Pattern)

```python
def get_dashboard(dashboard_id):
    # Manual validation
    if not isinstance(dashboard_id, int) or dashboard_id <= 0:
        print("Invalid ID")
        return None
    
    # Manual retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Manual timing
            start = time.time()
            
            # API call
            response = requests.get(url)
            
            # Manual error handling
            if response.status_code != 200:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    print(f"Failed after {max_retries} attempts")
                    return None
            
            # Manual timing log
            print(f"Took {time.time() - start:.2f}s")
            
            return response.json()
            
        except Exception as e:
            print(f"Error: {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)
```

### After (New Pattern)

```python
from decorators import retry, timed, handle_errors, validate_args
import requests

@timed(log_level="INFO")
@retry(max_attempts=3, delay=1, backoff=2, exceptions=(requests.RequestException,))
@handle_errors(default_return=None, log_error=True)
@validate_args(dashboard_id=lambda x: isinstance(x, int) and x > 0)
def get_dashboard(dashboard_id: int) -> dict:
    """All cross-cutting concerns handled automatically!"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

**Result**: 70 lines → 7 lines (90% reduction!)

---

## 💡 Pro Tips

### Tip 1: Combine Decorators for Maximum Effect

```python
from decorators import cache_with_ttl, retry, timed, handle_errors

@cache_with_ttl(ttl_seconds=600)       # Cache results for 10 min
@timed(log_level="INFO")                # Log execution time
@retry(max_attempts=3, delay=1)        # Retry on failure
@handle_errors(default_return=[])      # Return [] on error
def get_expensive_data():
    return expensive_api_call()
```

### Tip 2: Use Events for Loose Coupling

```python
# Instead of:
def process_dashboard(dashboard_id):
    result = extract(dashboard_id)
    send_slack_notification(result)     # Tight coupling!
    update_ui(result)                   # Tight coupling!
    save_to_db(result)                  # Tight coupling!

# Do this:
def process_dashboard(dashboard_id):
    result = extract(dashboard_id)
    event_bus.publish(Event(
        EventType.DASHBOARD_COMPLETED,
        {'dashboard_id': dashboard_id, 'result': result}
    ))
    # Other modules subscribe to handle their own concerns
```

### Tip 3: Use Builders for Complex Objects

```python
# Instead of:
dashboard = DashboardInfo(
    dashboard_id=964,
    dashboard_title="UPI Dashboard",
    dashboard_url="http://...",
    charts=[],
    owner="admin",
    created_on=datetime.now(),
    changed_on=datetime.now(),
    status=ProcessingStatus.PENDING,
    current_phase=None,
    error_message=None
)  # Hard to read, easy to forget parameters

# Do this:
dashboard = (build_dashboard()
    .with_id(964)
    .with_title("UPI Dashboard")
    .with_url("http://...")
    .with_owner("admin")
    .build())  # Clear, readable, hard to forget required fields
```

### Tip 4: Use Type Hints Everywhere

```python
from typing import List, Optional
from models import DashboardInfo, ChartInfo

def process_charts(
    dashboard: DashboardInfo,
    chart_ids: Optional[List[int]] = None
) -> List[ChartInfo]:
    """
    Your IDE will autocomplete everything!
    Type checker will catch errors at development time!
    """
    if chart_ids:
        return [c for c in dashboard.charts if c.chart_id in chart_ids]
    return dashboard.charts
```

---

## 🎯 Next Steps

1. **Read** `NEW_ARCHITECTURE_SUMMARY.md` for deep dive
2. **Run** the integration test: `python3 scripts/test_new_architecture.py 511`
3. **Explore** unit tests: `tests/test_new_patterns.py`
4. **Try** combining decorators on your own functions
5. **Experiment** with the builder pattern for object creation

---

## 📞 Quick Reference

| Pattern | File | Use When |
|---------|------|----------|
| **Configuration** | `settings.py` | Need centralized config |
| **Value Objects** | `models.py` | Need type safety, immutability |
| **Decorators** | `decorators.py` | Need retry, cache, timing, validation |
| **Repository** | `repositories.py` | Need to abstract storage |
| **Factory** | `factories.py` | Need to create complex objects |
| **Strategy** | `strategies.py` | Need pluggable algorithms |
| **Events** | `events.py` | Need loose coupling |
| **Builders** | `builders.py` | Need fluent object construction |

---

**🎉 You're now ready to use the new architecture!**

Start small, pick one pattern, and gradually adopt the others. The patterns work great individually and even better together!


