"""
Prism BA API Client

A modular API client for interacting with the Prism BA API.
Supports creating models and uploading knowledge base (KB) files.

Usage:
    from prism_api_client import PrismAPIClient
    
    client = PrismAPIClient(base_url="https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com")
    
    # Create a model
    model_data = {"name": "my-model", "description": "My model"}
    model = client.create_model(model_data)
    
    # Upload KB (ZIP file)
    result = client.upload_kb(model_id="my-model", zip_file_path="knowledge_base.zip")
    
    # Or use generic POST for any endpoint
    response = client.post_request("/v1/some/endpoint", payload={"key": "value"})
"""

import requests
from typing import Dict, Any, Optional, Union
from pathlib import Path
import json


class PrismAPIClient:
    """
    A modular API client for Prism BA API.
    
    This client provides:
    - Generic POST/GET request methods that are configurable
    - Specific methods for common operations (create_model, upload_kb)
    - Error handling and response parsing
    """
    
    def __init__(self, base_url: str, timeout: int = 300):
        """
        Initialize the Prism API client.
        
        Args:
            base_url: Base URL of the Prism BA API
                     (e.g., "https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com")
            timeout: Request timeout in seconds (default: 300)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Default headers (no authentication needed for internal API)
        self.session.headers.update({
            'Accept': 'application/json',
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Union[Dict[str, Any], str]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generic request method for making HTTP requests.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., "/v1/models/" or "/v1/files/upload/{model_id}")
            payload: Request payload (dict for JSON, or string for raw data)
            files: Files to upload (dict with file-like objects or file paths)
            headers: Additional headers to include in the request
            params: Query parameters
            **kwargs: Additional arguments to pass to requests.request()
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Merge additional headers with session headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Prepare request arguments
        request_kwargs = {
            'timeout': self.timeout,
            'headers': request_headers,
            **kwargs
        }
        
        # Add query parameters if provided
        if params:
            request_kwargs['params'] = params
        
        # Handle payload based on content type
        if payload is not None:
            if files:
                # For multipart/form-data, payload should be a dict
                if isinstance(payload, dict):
                    request_kwargs['data'] = payload
                else:
                    request_kwargs['data'] = {'data': payload}
            else:
                # For JSON requests
                if isinstance(payload, dict):
                    request_kwargs['json'] = payload
                    request_headers['Content-Type'] = 'application/json'
                else:
                    request_kwargs['data'] = payload
        
        # Add files if provided
        opened_files = []
        if files:
            # Convert file paths to file objects if needed
            processed_files = {}
            for key, value in files.items():
                if isinstance(value, (str, Path)):
                    # It's a file path, open it
                    file_obj = open(value, 'rb')
                    processed_files[key] = file_obj
                    opened_files.append(file_obj)
                else:
                    # It's already a file-like object
                    processed_files[key] = value
            request_kwargs['files'] = processed_files
        
        try:
            response = self.session.request(method, url, **request_kwargs)
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                # If response is not JSON, return text
                return {"response": response.text, "status_code": response.status_code}
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making {method} request to {url}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f": {e.response.status_code} - {e.response.text[:200]}"
            else:
                error_msg += f": {str(e)}"
            raise requests.exceptions.RequestException(error_msg) from e
        
        finally:
            # Close any files we opened
            for file_obj in opened_files:
                try:
                    file_obj.close()
                except Exception:
                    pass
    
    def post_request(
        self,
        endpoint: str,
        payload: Optional[Union[Dict[str, Any], str]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a POST request to any endpoint.
        
        This is a configurable method that can be used for any POST endpoint.
        
        Args:
            endpoint: API endpoint path (e.g., "/v1/models/" or "/v1/files/upload/{model_id}")
            payload: Request payload (dict for JSON, or string for raw data)
            files: Files to upload (dict with file-like objects or file paths)
                   Format: {"file": "/path/to/file.zip"} or {"file": file_object}
            headers: Additional headers to include
            params: Query parameters
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response JSON as dictionary
            
        Example:
            # JSON POST request
            response = client.post_request(
                "/v1/models/",
                payload={"name": "my-model", "description": "Test model"}
            )
            
            # Multipart POST request with file
            response = client.post_request(
                "/v1/files/upload/my-model",
                files={"file": "knowledge_base.zip"}
            )
        """
        return self._make_request(
            'POST',
            endpoint,
            payload=payload,
            files=files,
            headers=headers,
            params=params,
            **kwargs
        )
    
    def get_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a GET request to any endpoint.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response JSON as dictionary
        """
        return self._make_request(
            'GET',
            endpoint,
            params=params,
            headers=headers,
            **kwargs
        )
    
    def create_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new model.
        
        Args:
            model_data: Dictionary containing model configuration
                       (e.g., {"name": "my-model", "description": "My model"})
                       
        Returns:
            Response from the API containing created model information
            
        Example:
            model = client.create_model({
                "name": "my-model",
                "description": "My test model",
                "config": {...}
            })
        """
        return self.post_request(
            "/v1/models/",
            payload=model_data
        )
    
    def upload_kb(
        self,
        model_id: str,
        zip_file_path: Union[str, Path],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload knowledge base (KB) data as a ZIP file for a specific model.
        
        This replaces the knowledge base data directory for the model with files from the ZIP.
        
        Args:
            model_id: The model ID to upload KB for
            zip_file_path: Path to the ZIP file containing KB data
            **kwargs: Additional arguments to pass to the request
            
        Returns:
            Response from the API
            
        Example:
            result = client.upload_kb(
                model_id="my-model",
                zip_file_path="knowledge_base.zip"
            )
        """
        zip_path = Path(zip_file_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"ZIP file not found: {zip_file_path}")
        
        if not zip_path.suffix.lower() == '.zip':
            raise ValueError(f"File must be a ZIP file, got: {zip_path.suffix}")
        
        return self.post_request(
            f"/v1/files/upload/{model_id}",
            files={"file": zip_path},
            **kwargs
        )
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get model information by ID.
        
        Args:
            model_id: The model ID
            
        Returns:
            Model information
        """
        return self.get_request(f"/v1/models/{model_id}")
    
    def list_models(self) -> Dict[str, Any]:
        """
        Get list of all available models.
        
        Returns:
            List of models
        """
        return self.get_request("/v1/models/")


def main():
    """
    Example usage of the PrismAPIClient.
    """
    # Initialize client
    client = PrismAPIClient(
        base_url="https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"
    )
    
    # Example 1: Create a model
    print("Creating model...")
    model_data = {
        "name": "test-model",
        "description": "Test model created via API"
    }
    try:
        model_response = client.create_model(model_data)
        print(f"Model created: {json.dumps(model_response, indent=2)}")
        model_id = model_response.get("id") or model_response.get("model_id") or "test-model"
    except Exception as e:
        print(f"Error creating model: {e}")
        return
    
    # Example 2: Upload KB (ZIP file)
    print(f"\nUploading KB for model: {model_id}")
    zip_file = "knowledge_base.zip"  # Replace with actual path
    if Path(zip_file).exists():
        try:
            upload_response = client.upload_kb(model_id=model_id, zip_file_path=zip_file)
            print(f"KB uploaded: {json.dumps(upload_response, indent=2)}")
        except Exception as e:
            print(f"Error uploading KB: {e}")
    else:
        print(f"ZIP file not found: {zip_file}")
    
    # Example 3: Use generic POST request
    print("\nUsing generic POST request...")
    try:
        custom_response = client.post_request(
            "/v1/models/",
            payload={"name": "another-model", "description": "Created via generic POST"}
        )
        print(f"Custom POST response: {json.dumps(custom_response, indent=2)}")
    except Exception as e:
        print(f"Error in custom POST: {e}")


if __name__ == "__main__":
    main()

