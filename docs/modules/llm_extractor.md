# LLM Extractor Module

**File**: `llm_extractor.py`

## Purpose

Uses LLM (Claude Sonnet 4 via DSPy) to intelligently extract tables and columns from SQL queries.

## Key Classes

### `DashboardTableColumnExtractor`

Extracts table and column information using LLM.

**Methods:**
- `extract_from_chart(chart)` - Extract from single chart
- `extract_from_dashboard(dashboard_info)` - Extract from entire dashboard

### DSPy Signature

**`TableColumnExtractor`** - Defines LLM inputs/outputs:
- Inputs: SQL query, chart metadata
- Outputs: Tables used, original columns, column aliases

## Usage

```python
from llm_extractor import DashboardTableColumnExtractor

extractor = DashboardTableColumnExtractor(
    api_key="sk-...",
    model="claude-sonnet-4-20250514"
)

result = extractor.extract_from_dashboard(dashboard_info)
# Returns: List[Dict] with table_name, column_name, column_label__chart_json, data_type
```

## Thread Safety

Uses global, thread-safe DSPy configuration:
- Single `_dspy_extractor` instance
- Thread lock for initialization
- Reusable across threads

## Output Format

```python
[
    {
        "table_name": "hive.schema.table",
        "column_name": "column1",
        "column_label__chart_json": '{"1561": "Label1", "1562": "Label2"}',
        "data_type": "varchar"
    }
]
```

## Dependencies

- `dspy` - LLM orchestration framework
- `anthropic` (via litellm) - Claude API

