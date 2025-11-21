# DSPy Integration Summary

## What Was Updated

### 1. Enhanced DSPy Signature (`SourceTableColumnExtractor`)
- **Updated system prompts** with clearer, more detailed instructions
- **Better guidance** on identifying source tables vs derived columns
- **Improved output format** specifications
- **More examples** in the prompt descriptions

### 2. Integrated DSPy Examples
- **Automatic loading** of examples from `dspy_examples.py`
- **Few-shot learning** with up to 5 examples
- **Thread-safe** example loading
- **Graceful fallback** if examples are not available

### 3. Final Output Generation Function
- **`generate_final_tables_columns_output()`** - Main function to generate final CSV
- **Optional schema fetching** from Starburst
- **Automatic file saving** with progress reporting
- **Comprehensive error handling**

## How to Use

### Method 1: Using the Script (Recommended)

```bash
# Basic usage
python generate_final_output.py 282 --api-key YOUR_API_KEY

# With schema fetching
python generate_final_output.py 282 --api-key YOUR_API_KEY --fetch-schemas

# Custom output file
python generate_final_output.py 282 --api-key YOUR_API_KEY --output custom_output.csv
```

### Method 2: Using Python Directly

```python
from llm_extractor import generate_final_tables_columns_output
import os

# Generate final output
df = generate_final_tables_columns_output(
    dashboard_id=282,
    api_key=os.getenv('ANTHROPIC_API_KEY'),
    model='claude-sonnet-4-20250514',
    fetch_schemas=False,  # Set to True to fetch from Starburst
    output_file=None  # Uses default: extracted_meta/282_tables_columns.csv
)

print(df.head())
```

### Method 3: Just DSPy Extraction (Without Final Output)

```python
from llm_extractor import extract_source_tables_columns_llm
import json
import os

# Load dashboard
with open('extracted_meta/282_json.json', 'r') as f:
    dashboard_info = json.load(f)

# Extract using DSPy
results = extract_source_tables_columns_llm(
    dashboard_info,
    api_key=os.getenv('ANTHROPIC_API_KEY'),
    model='claude-sonnet-4-20250514'
)

# Results are in format:
# [
#   {
#     'tables_involved': 'hive.schema.table',
#     'column_names': 'column_name',
#     'alias_column_name': 'alias_name',
#     'source_or_derived': 'source' or 'derived',
#     'derived_column_logic': 'SQL expression' or 'NA'
#   },
#   ...
# ]
```

## Output Format

The final CSV file has the following columns:

1. **tables_involved**: Normalized table name (hive.schema.table)
2. **column_names**: Source column name
3. **alias_column_name**: Alias/derived column name
4. **source_or_derived**: Either "source" or "derived"
5. **derived_column_logic**: SQL expression for derived columns, "NA" for source
6. **column_datatype**: (Optional) Data type from Starburst
7. **extra**: (Optional) Extra info from Starburst
8. **comment**: (Optional) Column comment from Starburst

## Example Output

```csv
tables_involved,column_names,alias_column_name,source_or_derived,derived_column_logic
hive.user_paytm_payments.upi_tracker_insight,day_id,day_id,source,NA
hive.user_paytm_payments.upi_tracker_insight,segment,segment,source,NA
hive.user_paytm_payments.upi_tracker_insight,segment,Segments_,derived,"case when segment='Overall' then 'A:Overall' ... end"
hive.user_paytm_payments.upi_tracker_insight,mau,MAU__,derived,sum(mau)
hive.user_paytm_payments.upi_tracker_insight,mau,prev_month_mau,derived,"(sum(mau*1.0000)/lag(sum(mau)) over(...))-1"
```

## DSPy Examples Integration

The system automatically loads examples from `dspy_examples.py`:

- **18 examples** are available (example1 through example18)
- **Up to 5 examples** are used for few-shot learning
- Examples are loaded **automatically** when the extractor is created
- If examples are not available, the system falls back to zero-shot learning

## What Changed in the Code

### `llm_extractor.py`

1. **Updated `SourceTableColumnExtractor` signature**:
   - More detailed instructions
   - Better examples in field descriptions
   - Clearer output format specifications

2. **Updated `_get_dspy_source_extractor()` function**:
   - Loads examples from `dspy_examples.py`
   - Uses up to 5 examples for few-shot learning
   - Graceful error handling

3. **Added `generate_final_tables_columns_output()` function**:
   - Main function to generate final output
   - Integrates DSPy extraction
   - Optional Starburst schema fetching
   - Automatic CSV generation

## Testing

To test the integration:

```bash
# Make sure you have examples in dspy_examples.py
# Then run:
python generate_final_output.py 282 --api-key YOUR_API_KEY

# Check the output
cat extracted_meta/282_tables_columns.csv
```

## Troubleshooting

### Examples Not Loading
- Check that `dspy_examples.py` exists and has `EXAMPLES` list
- Check that examples are properly formatted `dspy.Example` objects
- Check console output for warnings

### API Key Issues
- Set `ANTHROPIC_API_KEY` environment variable
- Or pass `--api-key` argument

### Dashboard JSON Not Found
- Make sure dashboard has been extracted first
- Check that `extracted_meta/{dashboard_id}_json.json` exists

### Schema Fetching Fails
- Check Starburst connection credentials
- Schema fetching is optional - can continue without it
- Check `starburst_schema_fetcher.py` for connection details

## Next Steps

1. **Add more examples** to `dspy_examples.py` for better few-shot learning
2. **Test with different dashboards** to verify accuracy
3. **Tune the number of examples** used (currently 5, can be adjusted)
4. **Add validation** to check output quality
5. **Integrate with existing pipeline** in `api_server.py`

