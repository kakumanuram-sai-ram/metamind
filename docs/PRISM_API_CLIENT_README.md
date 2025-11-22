# Prism API Client

A modular, reusable API client for interacting with the Prism BA API. This client allows you to create models and upload knowledge base (KB) files programmatically.

## Features

- **Modular Design**: Base client class with reusable methods
- **Configurable POST Requests**: Generic `post_request()` method that works for any endpoint
- **Specific Methods**: Convenient methods for common operations (create_model, upload_kb)
- **No Authentication Required**: Works with internal API (no API keys needed)
- **Error Handling**: Comprehensive error handling and response parsing

## How It Works

### Architecture

The implementation follows a modular pattern:

1. **Base Client Class** (`PrismAPIClient`):
   - Handles base URL, session management, and default headers
   - Provides generic `_make_request()` method for all HTTP operations
   - Manages file handling (opening/closing files automatically)

2. **Generic Request Methods**:
   - `post_request()`: Configurable POST method for any endpoint
   - `get_request()`: Configurable GET method for any endpoint
   - Both accept payload, files, headers, params - fully configurable

3. **Specific Methods**:
   - `create_model()`: Creates a new model via POST `/v1/models/`
   - `upload_kb()`: Uploads KB ZIP file via POST `/v1/files/upload/{model_id}`
   - `get_model()`: Retrieves model information
   - `list_models()`: Lists all models

### API Endpoints Used

1. **Create Model**: `POST /v1/models/`
   - Content-Type: `application/json`
   - Body: JSON object with model configuration
   - Example: `{"name": "my-model", "description": "My model"}`

2. **Upload KB**: `POST /v1/files/upload/{model_id}`
   - Content-Type: `multipart/form-data`
   - Body: Form data with `file` field containing ZIP file
   - Replaces the knowledge base data directory for the model

### Key Design Decisions

1. **Configurable POST Method**:
   - The `post_request()` method accepts:
     - `endpoint`: Any API endpoint path
     - `payload`: Dict (for JSON) or string (for raw data)
     - `files`: Dict of files to upload (paths or file objects)
     - `headers`: Additional headers
     - `params`: Query parameters
   
   This allows the same function to be used for different API calls:
   ```python
   # JSON POST
   client.post_request("/v1/models/", payload={"name": "model"})
   
   # Multipart POST with file
   client.post_request("/v1/files/upload/model-id", files={"file": "data.zip"})
   ```

2. **Automatic File Handling**:
   - File paths are automatically opened and closed
   - Supports both file paths (str/Path) and file-like objects
   - Ensures files are properly closed even on errors

3. **No Authentication Layer**:
   - No API keys or tokens required (internal API)
   - Can be extended later if authentication is added

## Usage Examples

### Basic Usage

```python
from prism_api_client import PrismAPIClient

# Initialize client
client = PrismAPIClient(
    base_url="https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"
)

# Create a model
model = client.create_model({
    "name": "my-model",
    "description": "My test model"
})

# Upload KB (ZIP file)
result = client.upload_kb(
    model_id="my-model",
    zip_file_path="knowledge_base.zip"
)
```

### Using Generic POST for Different Endpoints

The same `post_request()` method can be used for different API calls:

```python
# Example 1: Create model (JSON POST)
response1 = client.post_request(
    "/v1/models/",
    payload={"name": "model1", "description": "Test"}
)

# Example 2: Upload KB (Multipart POST)
response2 = client.post_request(
    "/v1/files/upload/model1",
    files={"file": "kb.zip"}
)

# Example 3: Any other POST endpoint
response3 = client.post_request(
    "/v1/some/other/endpoint",
    payload={"key": "value"},
    headers={"Custom-Header": "value"}
)
```

### Complete Workflow

```python
from prism_api_client import PrismAPIClient
from pathlib import Path

client = PrismAPIClient(
    base_url="https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"
)

# Step 1: Create model
model_data = {
    "name": "production-model",
    "description": "Production model for RLAIF"
}
model_response = client.create_model(model_data)
model_id = model_response.get("id") or model_response.get("name")

# Step 2: Upload KB ZIP file
kb_zip_path = Path("knowledge_base.zip")
if kb_zip_path.exists():
    upload_response = client.upload_kb(
        model_id=model_id,
        zip_file_path=kb_zip_path
    )
    print(f"KB uploaded successfully: {upload_response}")
else:
    print(f"KB file not found: {kb_zip_path}")
```

## File Structure

```
metamind/scripts/
├── prism_api_client.py          # Main API client implementation
├── example_prism_api_usage.py    # Usage examples
└── PRISM_API_CLIENT_README.md   # This file
```

## Error Handling

The client raises `requests.exceptions.RequestException` on errors, with detailed error messages including:
- HTTP status codes
- Response text (first 200 chars)
- Original error messages

Example error handling:

```python
try:
    model = client.create_model({"name": "test"})
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
```

## Extending the Client

To add new methods, follow the pattern:

```python
def my_custom_method(self, param1: str, param2: int) -> Dict[str, Any]:
    """
    Custom method description.
    """
    return self.post_request(
        f"/v1/custom/endpoint/{param1}",
        payload={"param2": param2}
    )
```

Or use the generic methods directly:

```python
# For any endpoint
response = client.post_request("/v1/any/endpoint", payload={...})
response = client.get_request("/v1/any/endpoint", params={...})
```

## Notes

- **No Authentication**: Currently no API keys or tokens are required (internal API)
- **File Handling**: ZIP files are automatically opened and closed
- **Timeout**: Default timeout is 300 seconds (5 minutes)
- **Response Format**: All methods return dictionaries (parsed JSON or error info)

## Future Enhancements

If authentication is added later, you can extend the client:

```python
def __init__(self, base_url: str, api_key: Optional[str] = None):
    # ... existing code ...
    if api_key:
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}'
        })
```


