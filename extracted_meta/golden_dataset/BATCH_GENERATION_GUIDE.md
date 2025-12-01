# Batch Golden Dataset Generation Guide

This guide shows you how to generate golden datasets for multiple dashboards.

## Available Dashboards

Based on your extracted metadata, you have the following dashboards available:

- 249
- 476
- 511
- 567
- 583
- 585
- 588
- 657
- 729
- 842
- 915
- 964 ✅ (Already generated)
- 999

## Single Dashboard Generation

```bash
# Generate for dashboard 964 (already completed)
python3 scripts/golden_dataset_generator.py 964

# Generate for dashboard 476
python3 scripts/golden_dataset_generator.py 476

# Generate for dashboard 729
python3 scripts/golden_dataset_generator.py 729
```

## Multi-Dashboard Batch Generation

### Example 1: Generate for a few specific dashboards

```bash
# Generate combined dataset for dashboards 964, 476, and 729
python3 scripts/golden_dataset_generator.py 964 476 729

# Output: extracted_meta/golden_dataset/golden_dataset_combined_964_476_729.csv
```

### Example 2: Generate for all UPI-related dashboards

```bash
# If you know which dashboards are UPI-related, combine them
python3 scripts/golden_dataset_generator.py 249 476 511 729 964

# Output: extracted_meta/golden_dataset/golden_dataset_combined_249_476_511_729_964.csv
```

### Example 3: Generate all available dashboards

```bash
# Generate for all extracted dashboards
python3 scripts/golden_dataset_generator.py 249 476 511 567 583 585 588 657 729 842 915 964 999

# Output: extracted_meta/golden_dataset/golden_dataset_combined_249_476_..._999.csv
```

## Custom Output Location

```bash
# Save to a custom location
python3 scripts/golden_dataset_generator.py 964 476 729 \
  --output /path/to/my_custom_dataset.csv
```

## Processing Tips

### 1. Estimate Processing Time

Each chart takes approximately 2-5 seconds for LLM processing:
- Dashboard with 10 charts: ~20-50 seconds
- Dashboard with 20 charts: ~40-100 seconds

For batch processing:
- 3 dashboards × 15 charts average = ~1.5-4 minutes
- 10 dashboards × 15 charts average = ~5-12 minutes

### 2. Check Dashboard Quality First

Before batch processing, check if a dashboard has valid data:

```bash
# Check if JSON exists and has charts
cat extracted_meta/476/476_json.json | jq '.charts | length'

# View first chart name
cat extracted_meta/476/476_json.json | jq '.charts[0].chart_name'
```

### 3. Monitor Progress

The script provides real-time progress:

```
[1/10] Chart ID: 4616
  → Generating question for: Home Page Traffic Dashboard - UPI Traffic Dashboard
  ✅ Generated: How are our UPI traffic campaigns performing...

[2/10] Chart ID: 4617
  → Generating question for: Home Page Traffic Dashboard - DOD Impressions
  ✅ Generated: What is the daily click-through rate trend...
```

### 4. Handle Errors Gracefully

The script continues even if some charts fail:
- Skips charts without SQL queries
- Logs errors but continues processing
- Reports final count of successful generations

## Batch Script Example

Create a shell script for common batch operations:

```bash
#!/bin/bash
# File: batch_generate_golden_dataset.sh

echo "Generating golden datasets for all dashboards..."

# UPI-related dashboards
echo "Processing UPI dashboards..."
python3 scripts/golden_dataset_generator.py 249 476 511 729 964 \
  --output extracted_meta/golden_dataset/upi_dashboards.csv

# Merchant dashboards (example - adjust based on your verticals)
echo "Processing Merchant dashboards..."
python3 scripts/golden_dataset_generator.py 567 583 585 \
  --output extracted_meta/golden_dataset/merchant_dashboards.csv

# All dashboards combined
echo "Processing ALL dashboards..."
python3 scripts/golden_dataset_generator.py 249 476 511 567 583 585 588 657 729 842 915 964 999 \
  --output extracted_meta/golden_dataset/all_dashboards_combined.csv

echo "✅ Batch generation complete!"
```

Make it executable:
```bash
chmod +x batch_generate_golden_dataset.sh
./batch_generate_golden_dataset.sh
```

## Quality Assurance

After generation, review the output:

```bash
# View the generated dataset
python3 scripts/view_golden_dataset.py \
  extracted_meta/golden_dataset/golden_dataset_combined_964_476_729.csv \
  --rows 5

# Check total count
wc -l extracted_meta/golden_dataset/golden_dataset_combined_964_476_729.csv

# Check for any empty queries
grep -c '""' extracted_meta/golden_dataset/golden_dataset_combined_964_476_729.csv
```

## Post-Processing

### Combine Multiple Generated Files

If you generated separately, combine them:

```bash
cd extracted_meta/golden_dataset/

# Combine multiple CSVs (keeping header from first file only)
head -1 golden_dataset_964.csv > combined_all.csv
tail -n +2 golden_dataset_964.csv >> combined_all.csv
tail -n +2 golden_dataset_476.csv >> combined_all.csv
tail -n +2 golden_dataset_729.csv >> combined_all.csv
```

### Filter by Dashboard

```python
import pandas as pd

# Load combined dataset
df = pd.read_csv('extracted_meta/golden_dataset/all_dashboards_combined.csv')

# Filter for specific dashboard
upi_df = df[df['dashboard_id'].isin([249, 476, 511, 729, 964])]
upi_df.to_csv('upi_only.csv', index=False)
```

### Statistics

```python
import pandas as pd

df = pd.read_csv('extracted_meta/golden_dataset/all_dashboards_combined.csv')

print(f"Total entries: {len(df)}")
print(f"Unique dashboards: {df['dashboard_id'].nunique()}")
print(f"Unique charts: {df['chart_id'].nunique()}")
print(f"\nEntries per dashboard:")
print(df.groupby('dashboard_id').size())
```

## Recommended Workflow

1. **Start Small**: Test with 1-2 dashboards first
   ```bash
   python3 scripts/golden_dataset_generator.py 964
   ```

2. **Review Quality**: Check if questions make sense
   ```bash
   python3 scripts/view_golden_dataset.py extracted_meta/golden_dataset/golden_dataset_964.csv --rows 3
   ```

3. **Expand Gradually**: Add more dashboards
   ```bash
   python3 scripts/golden_dataset_generator.py 964 476 729
   ```

4. **Full Batch**: Process all available dashboards
   ```bash
   python3 scripts/golden_dataset_generator.py 249 476 511 567 583 585 588 657 729 842 915 964 999
   ```

5. **Validate & Use**: Check final dataset and use for training

## Common Issues

### Issue: "Dashboard JSON not found"
**Solution**: Ensure dashboard has been extracted first using the main extraction script

### Issue: "No SQL query" warnings
**Solution**: Normal - some charts may not have SQL (e.g., markdown, dividers)

### Issue: LLM generation timeout
**Solution**: Check network connection to proxy server, or retry

### Issue: Out of memory (large batches)
**Solution**: Process in smaller batches, then combine CSV files

## Next Steps

After generating your golden dataset:

1. **Train text-to-SQL models** using the question-SQL pairs
2. **Create benchmarks** to evaluate SQL generation accuracy
3. **Fine-tune LLMs** on your domain-specific data
4. **Build semantic search** over your SQL queries
5. **Create a chatbot** that translates questions to SQL

Happy generating! 🚀


