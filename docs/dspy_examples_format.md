# DSPy Examples Format for SourceTableColumnExtractor

This document shows the format for creating few-shot learning examples for the `SourceTableColumnExtractor` signature.

## DSPy Example Format

DSPy examples are created using the `dspy.Example` class. Each example should match the signature's input and output fields.

### Signature Fields

**Input Fields:**
- `sql_query`: str - The SQL query from the dashboard chart
- `chart_metadata`: str - JSON string of chart metadata (metrics, columns, chart_id, chart_name)

**Output Fields:**
- `source_tables`: str - Comma-separated list of source table names
- `source_columns`: str - Comma-separated list of source column names
- `derived_columns_mapping`: str - JSON object mapping derived columns to their source and logic

### Example Format

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
```

### Example 2: Complex query with CASE statements and window functions

```python
example2 = dspy.Example(
    sql_query="""SELECT case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end AS "Segments_", date_trunc('month', day_id) AS "date_trunc('month', day_id)", (sum(mau*1.0000)/lag(sum(mau)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS prev_month_mau, sum(mau) AS "MAU__", sum(n_txns) AS "Txns", (sum(n_txns*1.0000)/lag(sum(n_txns)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS "prev_month_Txns", sum(gmv) AS "Gmv", (sum(gmv*1.0000)/lag(sum(gmv)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS "Prev_month_gmv" 
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
WHERE ((day(day_id)<= day(current_date - interval '01' day))) GROUP BY case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end, date_trunc('month', day_id) ORDER BY prev_month_mau ASC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({
        "metrics": [
            {"label": "MAU", "column": {"column_name": "mau"}},
            {"label": "Transactions", "column": {"column_name": "n_txns"}},
            {"label": "GMV", "column": {"column_name": "gmv"}}
        ],
        "columns": ["Segments_", "date_trunc('month', day_id)", "prev_month_mau", "MAU__", "Txns", "prev_month_Txns", "Gmv", "Prev_month_gmv"],
        "chart_id": "5678",
        "chart_name": "Monthly Metrics by Segment"
    }),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="segment, day_id, mau, n_txns, gmv, dau",
    
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
        "Segments_": {
            "source_column": "segment",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end"
        },
        "date_trunc('month', day_id)": {
            "source_column": "day_id",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "date_trunc('month', day_id)"
        },
        "prev_month_mau": {
            "source_column": "mau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "(sum(mau*1.0000)/lag(sum(mau)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        },
        "MAU__": {
            "source_column": "mau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(mau)"
        },
        "Txns": {
            "source_column": "n_txns",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(n_txns)"
        },
        "prev_month_Txns": {
            "source_column": "n_txns",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "(sum(n_txns*1.0000)/lag(sum(n_txns)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        },
        "Gmv": {
            "source_column": "gmv",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(gmv)"
        },
        "Prev_month_gmv": {
            "source_column": "gmv",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "(sum(gmv*1.0000)/lag(sum(gmv)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        }
    })
).with_inputs('sql_query', 'chart_metadata')
```

## How to Use Examples

Once you have created examples, you can use them with DSPy's few-shot learning:

```python
from llm_extractor import SourceTableColumnExtractor
import dspy

# Create examples list
examples = [example1, example2, ...]  # Add all your examples

# Configure DSPy with examples
lm = dspy.LM(model="claude-sonnet-4-20250514", api_key=api_key)
dspy.configure(lm=lm)

# Create a module with examples
extractor = dspy.ChainOfThought(SourceTableColumnExtractor)

# The examples will be automatically used for few-shot learning
# when you call the extractor
```

## Key Points for Creating Examples

1. **Source Tables**: Only include actual physical tables, exclude:
   - CTEs (Common Table Expressions)
   - Subqueries (even if aliased)
   - Virtual tables (UNION results, etc.)

2. **Source Columns**: Only base columns from source tables, not computed/derived columns

3. **Derived Columns Mapping**: Include ALL derived columns:
   - Aggregations (sum, count, avg, etc.)
   - Window functions (lag, lead, over, etc.)
   - Date functions (date_trunc, date_format, etc.)
   - CASE statements
   - Computed columns in subqueries

4. **Logic Field**: Provide the exact SQL expression that creates the derived column

5. **Source Table/Column**: Map each derived column to the primary source table and column it's derived from

## Template for Creating New Examples

```python
example = dspy.Example(
    sql_query="""YOUR_SQL_QUERY_HERE""",
    
    chart_metadata=json.dumps({
        "metrics": [...],  # List of metric dicts
        "columns": [...],  # List of column names
        "chart_id": "...",
        "chart_name": "..."
    }),
    
    source_tables="table1, table2",  # Comma-separated, no spaces after commas
    
    source_columns="col1, col2, col3",  # Comma-separated, no spaces after commas
    
    derived_columns_mapping=json.dumps({
        "alias1": {
            "source_column": "source_col1",
            "source_table": "table1",
            "logic": "SQL_EXPRESSION_HERE"
        },
        # ... more derived columns
    })
).with_inputs('sql_query', 'chart_metadata')
```

