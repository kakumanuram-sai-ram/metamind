#!/usr/bin/env python3
"""
Standalone script to deploy a model and upload knowledge base (KB) to Prism BA API.

This script:
1. Reads configuration from prism_config.py
2. Creates a new model via API
3. Uploads the KB (ZIP file) for the created model

Usage:
    python deploy_model_and_kb.py

Configuration:
    Edit prism_config.py to set:
    - MODEL_NAME: Name of the model to create
    - KB_ZIP_FILE_PATH: Path to the KB ZIP file
    - PRISM_API_BASE_URL: API base URL
"""

import sys
from pathlib import Path
import json

# Add scripts directory to path to import modules
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from prism_api_client import PrismAPIClient
import prism_config


def validate_config():
    """
    Validate that all required configuration is set.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    errors = []
    
    # Check API base URL
    if not prism_config.PRISM_API_BASE_URL:
        errors.append("PRISM_API_BASE_URL is not set in prism_config.py")
    
    # Check model ID
    if not hasattr(prism_config, 'MODEL_ID') or not prism_config.MODEL_ID:
        errors.append("MODEL_ID is not set in prism_config.py")
    
    # Check model name
    if not hasattr(prism_config, 'MODEL_NAME') or not prism_config.MODEL_NAME:
        errors.append("MODEL_NAME is not set in prism_config.py")
    
    # Check KB ZIP file path
    if not prism_config.KB_ZIP_FILE_PATH:
        errors.append("KB_ZIP_FILE_PATH is not set in prism_config.py")
    else:
        kb_path = Path(prism_config.KB_ZIP_FILE_PATH)
        if not kb_path.exists():
            errors.append(f"KB ZIP file not found: {prism_config.KB_ZIP_FILE_PATH}")
        elif not kb_path.suffix.lower() == '.zip':
            errors.append(f"KB file must be a ZIP file, got: {kb_path.suffix}")
    
    if errors:
        return False, "\n".join(f"  - {error}" for error in errors)
    
    return True, None


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message: str):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"✗ {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ {message}")


def create_model(client: PrismAPIClient) -> dict:
    """
    Create a new model using the API client.
    
    Args:
        client: PrismAPIClient instance
        
    Returns:
        dict: Model creation response
        
    Raises:
        Exception: If model creation fails
    """
    print_section("Step 1: Creating Model")
    
    # Prepare model data with only basic fields accepted during creation
    # The API error indicates that fields like "temperature" don't exist as database columns
    # So we'll only send the basic fields: id, name, description
    # Configuration fields may need to be set via a separate endpoint after creation
    model_data = {
        "id": prism_config.MODEL_ID,  # Model ID (unique identifier suffix)
        "name": prism_config.MODEL_NAME,  # Display name
    }
    
    # Add description if provided (can be blank)
    if prism_config.MODEL_DESCRIPTION:
        model_data["description"] = prism_config.MODEL_DESCRIPTION
    
    # Note: Configuration fields (max_tokens, temperature, supported_features, email_pool)
    # are not sent during model creation to avoid database column errors.
    # These may need to be configured via the UI or a separate API endpoint after creation.
    
    # Display configuration summary
    print_info(f"Model ID: {prism_config.MODEL_ID}")
    print_info(f"Model Name: {prism_config.MODEL_NAME}")
    if prism_config.MODEL_DESCRIPTION:
        print_info(f"Description: {prism_config.MODEL_DESCRIPTION}")
    
    # Show config fields that are configured but won't be sent (due to API limitations)
    config_fields_configured = []
    if hasattr(prism_config, 'MAX_TOKENS') and prism_config.MAX_TOKENS:
        config_fields_configured.append(f"Max Tokens: {prism_config.MAX_TOKENS}")
    if hasattr(prism_config, 'TEMPERATURE') and prism_config.TEMPERATURE:
        config_fields_configured.append(f"Temperature: {prism_config.TEMPERATURE}")
    if hasattr(prism_config, 'SUPPORTED_FEATURES') and prism_config.SUPPORTED_FEATURES:
        config_fields_configured.append(f"Supported Features: {prism_config.SUPPORTED_FEATURES}")
    if hasattr(prism_config, 'EMAIL_POOL') and prism_config.EMAIL_POOL:
        config_fields_configured.append(f"Email Pool: {prism_config.EMAIL_POOL}")
    
    if config_fields_configured:
        print_info(f"\nNote: The following configuration fields are set in config but")
        print_info(f"      will not be sent during model creation (set via UI or separate API):")
        for field in config_fields_configured:
            print_info(f"      - {field}")
    
    if hasattr(prism_config, 'CUSTOM_METADATA') and prism_config.CUSTOM_METADATA:
        print_info(f"Custom Metadata: {json.dumps(prism_config.CUSTOM_METADATA, indent=2)}")
    
    print_info(f"\nFull Model Data:")
    print(json.dumps(model_data, indent=2))
    print()
    
    try:
        print("Creating model via API...")
        model_response = client.create_model(model_data)
        print_success("Model created successfully!")
        print(f"\nResponse:")
        print(json.dumps(model_response, indent=2))
        return model_response
    except Exception as e:
        print_error(f"Failed to create model: {e}")
        raise


def upload_kb(client: PrismAPIClient, model_id: str) -> dict:
    """
    Upload knowledge base (KB) ZIP file for the model.
    
    Args:
        client: PrismAPIClient instance
        model_id: ID of the model to upload KB for
        
    Returns:
        dict: KB upload response
        
    Raises:
        Exception: If KB upload fails
    """
    print_section("Step 2: Uploading Knowledge Base (KB)")
    
    kb_path = Path(prism_config.KB_ZIP_FILE_PATH)
    print_info(f"Model ID: {model_id}")
    print_info(f"KB ZIP File: {kb_path}")
    print_info(f"File Size: {kb_path.stat().st_size / (1024*1024):.2f} MB")
    print()
    
    try:
        print("Uploading KB ZIP file via API...")
        upload_response = client.upload_kb(
            model_id=model_id,
            zip_file_path=kb_path
        )
        print_success("KB uploaded successfully!")
        print(f"\nResponse:")
        print(json.dumps(upload_response, indent=2))
        return upload_response
    except Exception as e:
        print_error(f"Failed to upload KB: {e}")
        raise


def extract_model_id(model_response: dict) -> str:
    """
    Extract model ID from the model creation response.
    
    Args:
        model_response: Response from model creation API
        
    Returns:
        str: Model ID (full ID like 'ba-{model_id}' or just the model_id)
    """
    # Try different possible keys for model ID
    # The full ID might be 'ba-{model_id}' format
    model_id = (
        model_response.get("id") or
        model_response.get("model_id") or
        model_response.get("full_id") or
        prism_config.MODEL_ID
    )
    return str(model_id)


def main():
    """
    Main function to deploy model and KB.
    """
    print_section("Prism BA API - Model & KB Deployment")
    print_info("Starting deployment process...")
    
    # Validate configuration
    print_section("Configuration Validation")
    is_valid, error_message = validate_config()
    if not is_valid:
        print_error("Configuration validation failed:")
        print(error_message)
        print("\nPlease update prism_config.py with correct values.")
        sys.exit(1)
    
    print_success("Configuration validated successfully!")
    print_info(f"API Base URL: {prism_config.PRISM_API_BASE_URL}")
    print_info(f"Model ID: {prism_config.MODEL_ID}")
    print_info(f"Model Name: {prism_config.MODEL_NAME}")
    print_info(f"KB ZIP File: {prism_config.KB_ZIP_FILE_PATH}")
    
    # Initialize API client
    try:
        client = PrismAPIClient(base_url=prism_config.PRISM_API_BASE_URL)
        print_success("API client initialized")
    except Exception as e:
        print_error(f"Failed to initialize API client: {e}")
        sys.exit(1)
    
    # Step 1: Create model
    try:
        model_response = create_model(client)
        model_id = extract_model_id(model_response)
        print_success(f"Model ID extracted: {model_id}")
    except Exception as e:
        print_error(f"Model creation failed: {e}")
        sys.exit(1)
    
    # Step 2: Upload KB
    try:
        upload_response = upload_kb(client, model_id)
    except Exception as e:
        print_error(f"KB upload failed: {e}")
        sys.exit(1)
    
    # Summary
    print_section("Deployment Summary")
    print_success("Deployment completed successfully!")
    print_info(f"Model ID: {prism_config.MODEL_ID}")
    print_info(f"Model Name: {prism_config.MODEL_NAME}")
    print_info(f"Full Model ID: {model_id}")
    print_info(f"KB File: {prism_config.KB_ZIP_FILE_PATH}")
    print()
    print("You can now use this model in the Prism BA UI.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


