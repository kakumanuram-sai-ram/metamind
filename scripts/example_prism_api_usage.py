"""
Example script demonstrating how to use PrismAPIClient to:
1. Create a new model
2. Upload a knowledge base (KB) ZIP file

This script shows how to use the modular API client for different use cases.
"""

from prism_api_client import PrismAPIClient
from pathlib import Path
import json


def example_create_model_and_upload_kb():
    """
    Example: Create a model and upload KB in sequence.
    """
    # Initialize client
    client = PrismAPIClient(
        base_url="https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"
    )
    
    # Step 1: Create a new model
    print("=" * 60)
    print("Step 1: Creating a new model...")
    print("=" * 60)
    
    model_data = {
        "name": "my-test-model",
        "description": "Test model created via API client"
        # Add any other model configuration fields as needed
    }
    
    try:
        model_response = client.create_model(model_data)
        print(f"✓ Model created successfully!")
        print(f"Response: {json.dumps(model_response, indent=2)}")
        
        # Extract model_id from response (adjust based on actual API response structure)
        model_id = (
            model_response.get("id") or 
            model_response.get("model_id") or 
            model_response.get("name") or
            model_data["name"]
        )
        print(f"Model ID: {model_id}")
        
    except Exception as e:
        print(f"✗ Error creating model: {e}")
        return
    
    # Step 2: Upload KB (ZIP file)
    print("\n" + "=" * 60)
    print("Step 2: Uploading knowledge base (KB) ZIP file...")
    print("=" * 60)
    
    # Replace with your actual ZIP file path
    zip_file_path = "knowledge_base.zip"
    
    if not Path(zip_file_path).exists():
        print(f"⚠ ZIP file not found: {zip_file_path}")
        print("Please update zip_file_path with the actual path to your KB ZIP file.")
        return
    
    try:
        upload_response = client.upload_kb(
            model_id=model_id,
            zip_file_path=zip_file_path
        )
        print(f"✓ KB uploaded successfully!")
        print(f"Response: {json.dumps(upload_response, indent=2)}")
        
    except Exception as e:
        print(f"✗ Error uploading KB: {e}")


def example_using_generic_post():
    """
    Example: Using the generic post_request method for different API calls.
    This demonstrates how the same function can be used for different endpoints.
    """
    client = PrismAPIClient(
        base_url="https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"
    )
    
    print("\n" + "=" * 60)
    print("Example: Using generic post_request for different endpoints")
    print("=" * 60)
    
    # Example 1: Create model using generic POST
    print("\n1. Creating model using generic POST...")
    model_payload = {
        "name": "generic-model",
        "description": "Created using generic post_request"
    }
    
    try:
        response1 = client.post_request(
            endpoint="/v1/models/",
            payload=model_payload
        )
        print(f"✓ Model created: {json.dumps(response1, indent=2)}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 2: Upload KB using generic POST
    print("\n2. Uploading KB using generic POST...")
    zip_file = "knowledge_base.zip"
    if Path(zip_file).exists():
        try:
            response2 = client.post_request(
                endpoint=f"/v1/files/upload/generic-model",
                files={"file": zip_file}
            )
            print(f"✓ KB uploaded: {json.dumps(response2, indent=2)}")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print(f"⚠ ZIP file not found: {zip_file}")


def example_get_operations():
    """
    Example: Using GET requests to retrieve information.
    """
    client = PrismAPIClient(
        base_url="https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"
    )
    
    print("\n" + "=" * 60)
    print("Example: GET operations")
    print("=" * 60)
    
    # List all models
    print("\n1. Listing all models...")
    try:
        models = client.list_models()
        print(f"✓ Models retrieved: {json.dumps(models, indent=2)}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Get specific model
    print("\n2. Getting specific model...")
    model_id = "my-test-model"
    try:
        model = client.get_model(model_id)
        print(f"✓ Model info: {json.dumps(model, indent=2)}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    # Run examples
    example_create_model_and_upload_kb()
    example_using_generic_post()
    example_get_operations()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


