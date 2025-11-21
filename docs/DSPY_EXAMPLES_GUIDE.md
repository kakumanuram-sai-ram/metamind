# DSPy Examples Format Guide

This guide explains how to provide examples to DSPy for few-shot learning with the `SourceTableColumnExtractor` signature.

## Format Options

DSPy supports multiple ways to provide examples. Here are the recommended formats:

## Method 1: Python File with dspy.Example Objects (Recommended)

Create a Python file with your examples:

**File: `dspy_examples.py`**

```python
import dspy
import json

# Example 1: Simple query with aggregations
example1 = dspy.Example(
    sql_query="""SELECT "Day_" AS "Day_", month_ AS month_, sum(dau) AS "SUM(dau)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'Overall' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY "Day_", month_ ORDER BY "SUM(dau)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({
        "metrics": [],
        "columns": ["Day_", "month_", "SUM(dau)"],
        "chart_id": "1234",
        "chart_name": "Daily Active Users"
    }),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, segment, mau, dau",
    
    derived_columns_mapping=json.dumps({
        "mau_rolling": {
            "source_column": "mau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        },
        "Day_": {
            "source_column": "day_id",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "date_Format(day_id, 'Day %d')"
        },
        "month_": {
            "source_column": "day_id",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "date_Format(day_id, '%b''%y')"
        },
        "SUM(dau)": {
            "source_column": "dau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(dau)"
        }
    })
).with_inputs('sql_query', 'chart_metadata')

# Example 2: Complex query with CASE statements
example2 = dspy.Example(
    sql_query="""SELECT case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 end AS "Segments_", sum(mau) AS "MAU__"
FROM user_paytm_payments.upi_tracker_insight
GROUP BY case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 end;""",
    
    chart_metadata=json.dumps({
        "metrics": [{"label": "MAU", "column": {"column_name": "mau"}}],
        "columns": ["Segments_", "MAU__"],
        "chart_id": "5678",
        "chart_name": "MAU by Segment"
    }),
    
    source_tables="user_paytm_payments.upi_tracker_insight",
    
    source_columns="segment, mau",
    
    derived_columns_mapping=json.dumps({
        "Segments_": {
            "source_column": "segment",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' end"
        },
        "MAU__": {
            "source_column": "mau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(mau)"
        }
    })
).with_inputs('sql_query', 'chart_metadata')

# Export all examples as a list
EXAMPLES = [example1, example2]
```

**Usage:**
```python
from dspy_examples import EXAMPLES
from llm_extractor import SourceTableColumnExtractor
import dspy

# Configure DSPy
lm = dspy.LM(model="claude-sonnet-4-20250514", api_key=api_key)
dspy.configure(lm=lm)

# Create extractor with examples
extractor = dspy.ChainOfThought(SourceTableColumnExtractor)

# Examples will be automatically used for few-shot learning
```

## Method 2: JSON File Format

Create a JSON file with your examples:

**File: `dspy_examples.json`**

```json
[
  {
    "sql_query": "SELECT sum(dau) AS \"SUM(dau)\" FROM user_paytm_payments.upi_tracker_insight WHERE segment = 'Overall';",
    "chart_metadata": "{\"metrics\": [], \"columns\": [\"SUM(dau)\"], \"chart_id\": \"1234\", \"chart_name\": \"DAU\"}",
    "source_tables": "user_paytm_payments.upi_tracker_insight",
    "source_columns": "dau, segment",
    "derived_columns_mapping": "{\"SUM(dau)\": {\"source_column\": \"dau\", \"source_table\": \"user_paytm_payments.upi_tracker_insight\", \"logic\": \"sum(dau)\"}}"
  },
  {
    "sql_query": "SELECT date_format(day_id, '%Y-%m') AS month, sum(mau) AS mau_sum FROM user_paytm_payments.upi_tracker_insight GROUP BY date_format(day_id, '%Y-%m');",
    "chart_metadata": "{\"metrics\": [{\"label\": \"MAU Sum\", \"column\": {\"column_name\": \"mau\"}}], \"columns\": [\"month\", \"mau_sum\"], \"chart_id\": \"5678\", \"chart_name\": \"Monthly MAU\"}",
    "source_tables": "user_paytm_payments.upi_tracker_insight",
    "source_columns": "day_id, mau",
    "derived_columns_mapping": "{\"month\": {\"source_column\": \"day_id\", \"source_table\": \"user_paytm_payments.upi_tracker_insight\", \"logic\": \"date_format(day_id, '%Y-%m')\"}, \"mau_sum\": {\"source_column\": \"mau\", \"source_table\": \"user_paytm_payments.upi_tracker_insight\", \"logic\": \"sum(mau)\"}}"
  }
]
```

**Load and use:**
```python
import json
import dspy
from llm_extractor import SourceTableColumnExtractor

# Load examples from JSON
with open('dspy_examples.json', 'r') as f:
    examples_data = json.load(f)

# Convert to dspy.Example objects
examples = []
for ex in examples_data:
    example = dspy.Example(
        sql_query=ex['sql_query'],
        chart_metadata=ex['chart_metadata'],
        source_tables=ex['source_tables'],
        source_columns=ex['source_columns'],
        derived_columns_mapping=ex['derived_columns_mapping']
    ).with_inputs('sql_query', 'chart_metadata')
    examples.append(example)

# Use with DSPy
lm = dspy.LM(model="claude-sonnet-4-20250514", api_key=api_key)
dspy.configure(lm=lm)
extractor = dspy.ChainOfThought(SourceTableColumnExtractor)
```

## Method 3: CSV File Format

Create a CSV file with your examples:

**File: `dspy_examples.csv`**

```csv
sql_query,chart_metadata,source_tables,source_columns,derived_columns_mapping
"SELECT sum(dau) AS ""SUM(dau)"" FROM user_paytm_payments.upi_tracker_insight WHERE segment = 'Overall';","{""metrics"": [], ""columns"": [""SUM(dau)""], ""chart_id"": ""1234"", ""chart_name"": ""DAU""}","user_paytm_payments.upi_tracker_insight","dau, segment","{""SUM(dau)"": {""source_column"": ""dau"", ""source_table"": ""user_paytm_payments.upi_tracker_insight"", ""logic"": ""sum(dau)""}}"
```

**Load and use:**
```python
import pandas as pd
import dspy
import json
from llm_extractor import SourceTableColumnExtractor

# Load from CSV
df = pd.read_csv('dspy_examples.csv')

# Convert to dspy.Example objects
examples = []
for _, row in df.iterrows():
    example = dspy.Example(
        sql_query=row['sql_query'],
        chart_metadata=row['chart_metadata'],
        source_tables=row['source_tables'],
        source_columns=row['source_columns'],
        derived_columns_mapping=row['derived_columns_mapping']
    ).with_inputs('sql_query', 'chart_metadata')
    examples.append(example)
```

## Method 4: Using BootstrapFewShot (Automatic Example Selection)

DSPy can automatically select the best examples from your training set:

```python
import dspy
from dspy.teleprompt import BootstrapFewShot
from llm_extractor import SourceTableColumnExtractor

# Load your examples (from any of the methods above)
from dspy_examples import EXAMPLES

# Configure DSPy
lm = dspy.LM(model="claude-sonnet-4-20250514", api_key=api_key)
dspy.configure(lm=lm)

# Create base module
base_module = dspy.ChainOfThought(SourceTableColumnExtractor)

# Use BootstrapFewShot to automatically select best examples
teleprompter = BootstrapFewShot(
    max_bootstrapped_demos=4,  # Maximum examples to use
    max_labeled_demos=8,       # Maximum training examples
)

# Optimize the module with your examples
optimized_module = teleprompter.compile(
    student=base_module,
    trainset=EXAMPLES  # Your training examples
)

# Use the optimized module
result = optimized_module(sql_query=query, chart_metadata=metadata)
```

## Method 5: Manual Example Injection

You can manually provide examples when calling the extractor:

```python
import dspy
from llm_extractor import SourceTableColumnExtractor

# Configure DSPy
lm = dspy.LM(model="claude-sonnet-4-20250514", api_key=api_key)
dspy.configure(lm=lm)

# Create extractor
extractor = dspy.ChainOfThought(SourceTableColumnExtractor)

# Load examples
from dspy_examples import EXAMPLES

# Set examples in the module
extractor = extractor.copy()
extractor.demos = EXAMPLES[:3]  # Use first 3 examples

# Use the extractor
result = extractor(sql_query=query, chart_metadata=metadata)
```

## Recommended Structure for Your Examples File

Create a file `dspy_examples.py` with this structure:

```python
"""
DSPy Examples for SourceTableColumnExtractor

Add your examples here. Each example should be a dspy.Example object
with all input and output fields populated.
"""
import dspy
import json

# ============================================================================
# EXAMPLE 1: Simple aggregation
# ============================================================================
example1 = dspy.Example(
    sql_query="""YOUR_SQL_HERE""",
    chart_metadata=json.dumps({...}),
    source_tables="table1, table2",
    source_columns="col1, col2, col3",
    derived_columns_mapping=json.dumps({...})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 2: Window functions
# ============================================================================
example2 = dspy.Example(...)

# ============================================================================
# EXAMPLE 3: CASE statements
# ============================================================================
example3 = dspy.Example(...)

# Export all examples
EXAMPLES = [
    example1,
    example2,
    example3,
    # Add more examples here
]

# Group examples by type (optional, for better organization)
EXAMPLES_BY_TYPE = {
    "simple_aggregation": [example1],
    "window_functions": [example2],
    "case_statements": [example3],
}
```

## Integration with llm_extractor.py

To use your examples in the existing code, update `llm_extractor.py`:

```python
# At the top of llm_extractor.py
try:
    from dspy_examples import EXAMPLES as DSPY_EXAMPLES
    USE_EXAMPLES = True
except ImportError:
    DSPY_EXAMPLES = []
    USE_EXAMPLES = False

# In the _get_dspy_source_extractor function:
def _get_dspy_source_extractor(api_key: str, model: str):
    """Get DSPy source extractor with examples"""
    global _dspy_lm, _dspy_source_extractor
    with _dspy_lock:
        if _dspy_source_extractor is None:
            try:
                if _dspy_lm is None:
                    _dspy_lm = dspy.LM(model=model, api_key=api_key, api_provider="anthropic")
                    dspy.configure(lm=_dspy_lm)
                
                extractor = dspy.ChainOfThought(SourceTableColumnExtractor)
                
                # Add examples if available
                if USE_EXAMPLES and DSPY_EXAMPLES:
                    extractor.demos = DSPY_EXAMPLES[:5]  # Use first 5 examples
                
                _dspy_source_extractor = extractor
            except RuntimeError as e:
                if "can only be changed by the thread" in str(e):
                    extractor = dspy.ChainOfThought(SourceTableColumnExtractor)
                    if USE_EXAMPLES and DSPY_EXAMPLES:
                        extractor.demos = DSPY_EXAMPLES[:5]
                    _dspy_source_extractor = extractor
                else:
                    raise
    return _dspy_source_extractor
```

## Best Practices

1. **Start with 3-5 examples**: Begin with a small set of diverse examples
2. **Cover different patterns**: Include examples for:
   - Simple aggregations
   - Window functions
   - CASE statements
   - Date functions
   - Subqueries with derived columns
   - UNION queries
3. **Keep examples accurate**: Ensure source_tables, source_columns, and derived_columns_mapping are correct
4. **Use consistent formatting**: Keep the same format across all examples
5. **Test incrementally**: Add examples one at a time and test the results
6. **Document examples**: Add comments explaining what each example demonstrates

## Example Validation

Before using examples, validate them:

```python
def validate_example(example: dspy.Example) -> bool:
    """Validate that an example has all required fields"""
    required_fields = ['sql_query', 'chart_metadata', 'source_tables', 
                      'source_columns', 'derived_columns_mapping']
    
    for field in required_fields:
        if not hasattr(example, field) or not getattr(example, field):
            print(f"Missing or empty field: {field}")
            return False
    
    # Validate JSON fields
    try:
        json.loads(example.chart_metadata)
        json.loads(example.derived_columns_mapping)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in example: {e}")
        return False
    
    return True

# Validate all examples
for i, ex in enumerate(EXAMPLES):
    if not validate_example(ex):
        print(f"Example {i+1} is invalid!")
```

## Quick Start Template

Copy this template to create your examples file:

```python
import dspy
import json

# Template for creating examples
def create_example(sql_query, chart_metadata_dict, source_tables, 
                   source_columns, derived_columns_dict):
    """Helper function to create examples"""
    return dspy.Example(
        sql_query=sql_query,
        chart_metadata=json.dumps(chart_metadata_dict),
        source_tables=source_tables,
        source_columns=source_columns,
        derived_columns_mapping=json.dumps(derived_columns_dict)
    ).with_inputs('sql_query', 'chart_metadata')

# Use the helper
example = create_example(
    sql_query="SELECT sum(dau) FROM table1;",
    chart_metadata_dict={"chart_id": "123", "chart_name": "Test"},
    source_tables="schema.table1",
    source_columns="dau",
    derived_columns_dict={"sum(dau)": {
        "source_column": "dau",
        "source_table": "schema.table1",
        "logic": "sum(dau)"
    }}
)

EXAMPLES = [example]
```

