# Model & KB Deployment Guide

This guide explains how to use the standalone deployment script to create a model and upload knowledge base (KB) files to the Prism BA API.

## Files

- `deploy_model_and_kb.py` - Standalone deployment script
- `prism_config.py` - Configuration file (edit this before running)
- `prism_api_client.py` - API client library (used by deployment script)

## Quick Start

### 1. Configure Settings

Edit `prism_config.py` and set:

```python
# Model name to create
MODEL_NAME = "my-production-model"

# Path to your KB ZIP file
KB_ZIP_FILE_PATH = "/path/to/knowledge_base.zip"

# API base URL (usually doesn't need to change)
PRISM_API_BASE_URL = "https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"
```

### 2. Run the Script

```bash
cd /home/devuser/sai_dev/metamind/scripts
python deploy_model_and_kb.py
```

Or make it executable and run directly:

```bash
chmod +x deploy_model_and_kb.py
./deploy_model_and_kb.py
```

## Configuration Details

### `prism_config.py`

All configuration is in this file:

```python
# Required Settings
PRISM_API_BASE_URL = "https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"
MODEL_NAME = "my-model"  # Name of the model to create
KB_ZIP_FILE_PATH = "/path/to/knowledge_base.zip"  # Path to KB ZIP file

# Optional Settings
MODEL_DESCRIPTION = "Description of the model"  # Optional description
ADDITIONAL_MODEL_CONFIG = {
    # Add any additional model configuration here
    # Example: "config": {...}, "metadata": {...}
}
```

### Configuration Fields

- **PRISM_API_BASE_URL**: Base URL of the Prism BA API (usually doesn't need to change)
- **MODEL_NAME**: The name of the model to create (required)
- **KB_ZIP_FILE_PATH**: Full path to the knowledge base ZIP file (required)
- **MODEL_DESCRIPTION**: Optional description for the model
- **ADDITIONAL_MODEL_CONFIG**: Dictionary for any additional model configuration fields

## What the Script Does

1. **Validates Configuration**
   - Checks that all required settings are set
   - Verifies that the KB ZIP file exists
   - Validates file format (must be .zip)

2. **Creates Model**
   - Calls `POST /v1/models/` API
   - Creates a new model with the configured name
   - Returns model information

3. **Uploads KB**
   - Calls `POST /v1/files/upload/{model_id}` API
   - Uploads the KB ZIP file for the created model
   - Replaces the knowledge base data directory

## Example Output

```
======================================================================
  Prism BA API - Model & KB Deployment
======================================================================
ℹ Starting deployment process...

======================================================================
  Configuration Validation
======================================================================
✓ Configuration validated successfully!
ℹ API Base URL: https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com
ℹ Model Name: my-test-model
ℹ KB ZIP File: /path/to/knowledge_base.zip

======================================================================
  Step 1: Creating Model
======================================================================
ℹ Model Name: my-test-model
ℹ Description: Model created via API deployment script
ℹ Model Data: {
  "name": "my-test-model",
  "description": "Model created via API deployment script"
}

Creating model via API...
✓ Model created successfully!

Response:
{
  "id": "my-test-model",
  "name": "my-test-model",
  ...
}

======================================================================
  Step 2: Uploading Knowledge Base (KB)
======================================================================
ℹ Model ID: my-test-model
ℹ KB ZIP File: /path/to/knowledge_base.zip
ℹ File Size: 2.45 MB

Uploading KB ZIP file via API...
✓ KB uploaded successfully!

Response:
{
  "status": "success",
  "message": "KB uploaded successfully"
}

======================================================================
  Deployment Summary
======================================================================
✓ Deployment completed successfully!
ℹ Model Name: my-test-model
ℹ Model ID: my-test-model
ℹ KB File: /path/to/knowledge_base.zip

You can now use this model in the Prism BA UI.
======================================================================
```

## Error Handling

The script validates configuration and provides clear error messages:

- **Missing Configuration**: Shows which settings are missing
- **File Not Found**: Indicates if KB ZIP file doesn't exist
- **Invalid File Format**: Warns if file is not a ZIP file
- **API Errors**: Shows detailed error messages from API calls

## Testing with Prism UI

After running the script:

1. Open the Prism BA UI
2. Navigate to the models section
3. You should see your newly created model
4. The model should have the KB data uploaded

## Troubleshooting

### Configuration Errors

If you see configuration validation errors:
- Check that `MODEL_NAME` is set
- Verify `KB_ZIP_FILE_PATH` points to an existing file
- Ensure the file path is absolute or relative to the script location

### API Errors

If API calls fail:
- Check that the API base URL is correct
- Verify network connectivity
- Check API response for specific error messages

### File Errors

If file upload fails:
- Ensure the ZIP file is not corrupted
- Check file permissions (script must be able to read the file)
- Verify file size is reasonable

## Advanced Usage

### Using Different Configurations

You can create multiple config files for different environments:

```bash
# Create config files
cp prism_config.py prism_config_prod.py
cp prism_config.py prism_config_dev.py

# Edit each config file with different settings

# Use specific config (modify script to import different config)
# Or use environment variables
```

### Programmatic Usage

You can also import and use the functions programmatically:

```python
from deploy_model_and_kb import create_model, upload_kb
from prism_api_client import PrismAPIClient

client = PrismAPIClient(base_url="...")
model_response = create_model(client)
model_id = extract_model_id(model_response)
upload_response = upload_kb(client, model_id)
```

## Notes

- The script is standalone and can be run independently
- No authentication is required (internal API)
- The script automatically handles file opening/closing
- All API responses are printed for debugging


