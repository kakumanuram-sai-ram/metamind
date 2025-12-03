# DSPy Examples Status

## Summary

| Signature Class | Has Examples | Count | File Location |
|----------------|--------------|-------|---------------|
| `SourceTableColumnExtractor` | ✅ Yes | 18 | `dspy_examples.py` |
| `TableColumnExtractor` | ❌ No | 0 | - |
| `TermDefinitionExtractor` | ❌ No | 0 | - |
| `FilterConditionsExtractor` | ❌ No | 0 | - |
| `JoiningConditionExtractor` | ❌ No | 0 | - |
| `ColumnMetadataExtractor` | ❌ No | 0 | - |
| `TableMetadataExtractor` | ❌ No | 0 | - |

## Signatures Without Examples (Need Examples)

### 1. TableColumnExtractor
**Purpose**: Extract table and column information from dashboard chart SQL queries.

**Input Fields**:
- `sql_query`: SQL query from dashboard chart
- `chart_metadata`: Chart metadata including metrics and columns

**Output Fields**:
- `tables_used`: Comma-separated list of source table names
- `original_columns`: JSON object mapping table_name to list of original column names
- `column_aliases`: JSON object mapping alias_name to original_column_name

---

### 2. TermDefinitionExtractor
**Purpose**: Extract term definitions from dashboard charts (metrics, calculated fields, synonyms, categories).

**Input Fields**:
- `dashboard_title`: Dashboard title providing business context
- `chart_names_and_labels`: JSON string with all chart names and their metric labels
- `sql_queries`: JSON string with all SQL queries showing calculation logic
- `metrics_context`: JSON string with detailed metric information

**Output Fields**:
- `term_definitions`: JSON array of term definitions with term, type, definition, business_alias

---

### 3. FilterConditionsExtractor
**Purpose**: Transform Superset dashboard chart metadata into structured filter condition documentation.

**Input Fields**:
- `dashboard_title`: Dashboard title
- `chart_names_and_labels`: JSON with chart names and labels
- `sql_queries`: JSON with SQL queries
- `metrics_context`: JSON with metric information

**Output Fields**:
- `filter_conditions`: Structured documentation of filter conditions

---

### 4. JoiningConditionExtractor
**Purpose**: Extract and describe joining conditions between tables.

**Input Fields**:
- `table1`: First table name (full name)
- `table2`: Second table name (full name)
- `sql_query`: SQL query using both tables
- `chart_name`: Chart name providing business context
- `dashboard_title`: Dashboard title

**Output Fields**:
- `joining_condition`: Exact joining condition
- `joining_type`: Join type (INNER, LEFT, RIGHT, FULL)
- `remarks`: Explanation of when and why to use this join

---

### 5. ColumnMetadataExtractor
**Purpose**: Extract column descriptions based on usage context.

**Input Fields**:
- `column_name`: Column name to describe
- `table_name`: Table name containing this column
- `column_datatype`: Data type of the column
- `chart_labels_and_aliases`: JSON with chart labels and aliases
- `derived_column_usage`: JSON showing how column is used in derived columns
- `sql_usage_context`: Sample SQL showing how column is used

**Output Fields**:
- `column_description`: Clear, concise description of the column

---

### 6. TableMetadataExtractor
**Purpose**: Extract comprehensive table metadata.

**Input Fields**:
- `dashboard_title`: Dashboard title
- `chart_names_and_labels`: JSON with chart names and labels
- `table_name`: Table name in format hive.schema.table
- `table_columns`: JSON with column names, datatypes, and usage context
- `sql_queries_context`: Sample SQL queries using this table

**Output Fields**:
- `table_description`: Comprehensive table description (data_description + business_description)
- `refresh_frequency`: Estimated refresh frequency
- `vertical`: Business vertical
- `partition_column`: Partition column name if evident
- `remarks`: Additional notes
- `relationship_context`: How table relates to other tables

---

## How to Add Examples

Examples should be added to `scripts/dspy_examples.py` following this pattern:

```python
example_term_def_1 = dspy.Example(
    # Input fields
    dashboard_title="UPI Transaction Overview",
    chart_names_and_labels=json.dumps({
        "Chart 1": ["Total Transactions", "Success Rate"],
        "Chart 2": ["DAU", "MAU"]
    }),
    sql_queries=json.dumps([
        "SELECT count(*) as total_txns FROM transactions WHERE status='success'",
        "SELECT count(distinct user_id) as dau FROM transactions"
    ]),
    metrics_context=json.dumps({
        "Total Transactions": {"expression": "COUNT(*)", "type": "aggregate"},
        "Success Rate": {"expression": "SUM(CASE WHEN status='success' THEN 1 ELSE 0 END)/COUNT(*)", "type": "calculated"}
    }),
    
    # Output fields
    term_definitions=json.dumps([
        {
            "term": "Total Transactions",
            "type": "Metric",
            "definition": "Count of all transaction records",
            "business_alias": "Txn Count, Total Txns"
        },
        {
            "term": "Success Rate",
            "type": "Metric / Calculated Field",
            "definition": "Percentage of successful transactions out of total transactions",
            "business_alias": "SR, Txn Success %"
        }
    ])
).with_inputs('dashboard_title', 'chart_names_and_labels', 'sql_queries', 'metrics_context')

# Add to EXAMPLES list
TERM_DEFINITION_EXAMPLES = [example_term_def_1, ...]
```

## Recommendations

1. **Priority**: Create examples for `TermDefinitionExtractor` and `FilterConditionsExtractor` first as these are the most complex.

2. **Source**: Use actual extracted data from dashboards 476, 511, 585 as source material for examples.

3. **Coverage**: Aim for 5-10 diverse examples per signature covering edge cases.

4. **Testing**: Use DSPy's evaluation framework to measure example quality.

