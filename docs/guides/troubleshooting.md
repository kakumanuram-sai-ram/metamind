# Troubleshooting Guide

## Common Issues

### 1. 401 Unauthorized Error

**Symptoms**: `401 Client Error: UNAUTHORIZED`

**Solutions**:
- Check if session cookie expired
- Get fresh cookies from Superset
- Update `config.py` with new credentials
- Restart API server

**Test**:
```bash
python test_auth.py
```

### 2. DSPy Thread Safety Error

**Symptoms**: `dspy.settings can only be changed by the thread that initially configured it`

**Solutions**:
- This should be fixed in current version
- If still occurring, restart the server
- Check `llm_extractor.py` for thread-safe configuration

### 3. JSON Serialization Error

**Symptoms**: `ValueError: Out of range float values are not JSON compliant`

**Solutions**:
- Fixed in current version with NaN/Infinity handling
- Check `api_server.py` for proper DataFrame cleaning

### 4. LLM Extraction Fails

**Symptoms**: No tables_metadata.csv generated

**Solutions**:
- Check Anthropic API key is valid
- Verify API key has sufficient credits
- Check server logs for LLM errors
- Try rule-based extraction: `export USE_LLM_EXTRACTION=false`

### 5. Trino Query Fails

**Symptoms**: `Error querying Trino for table: 500`

**Solutions**:
- Table may not be accessible via Superset
- Check table name format (catalog.schema.table)
- Verify Superset has access to the table
- System will continue without data types

### 6. No Tables/Columns Found

**Symptoms**: Empty tables_columns.csv

**Solutions**:
- Check if SQL queries are present in dashboard JSON
- Verify LLM extraction completed (check logs)
- Try rule-based extraction as fallback
- Check if tables are CTEs (excluded by design)

### 7. Slow Extraction

**Symptoms**: Dashboard extraction takes > 60 seconds

**Solutions**:
- LLM extraction runs in background (shouldn't block)
- Check network connectivity
- Verify Superset API response times
- Consider disabling LLM: `export USE_LLM_EXTRACTION=false`

### 8. Files Not Generated

**Symptoms**: Missing files in `extracted_meta/`

**Solutions**:
- Check if directory exists: `mkdir -p extracted_meta`
- Verify write permissions
- Check disk space
- Review server logs for errors

## Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Getting Help

1. Check server logs
2. Review error messages in API responses
3. Test individual components:
   - `python test_auth.py` - Test authentication
   - `python test_dashboard_access.py` - Test dashboard access
   - `python -c "from query_extract import SupersetExtractor; ..."` - Test extraction

## Log Files

Server logs are printed to stdout. For production, redirect to file:

```bash
python api_server.py > server.log 2>&1
```

