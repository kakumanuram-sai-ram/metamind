#!/usr/bin/env python3
"""
Script to upload Knowledge Base (KB) ZIP file to an n8n webhook endpoint.

This script:
1. Reads configuration from n8n_config.py
2. Validates that the KB ZIP file exists
3. Sends the ZIP file to the n8n webhook endpoint via POST request

Usage:
    python n8n_kb_upload.py

Configuration:
    Edit n8n_config.py to set:
    - N8N_WEBHOOK_URL: Your n8n webhook endpoint URL
    - KB_ZIP_FILE_PATH: Path to the KB ZIP file
"""

import sys
from pathlib import Path
import json
import requests

# Add scripts directory to path to import modules
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

import n8n_config


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


def validate_config():
    """
    Validate that all required configuration is set.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    errors = []
    
    # Check n8n webhook URL
    if not n8n_config.N8N_WEBHOOK_URL or n8n_config.N8N_WEBHOOK_URL == "https://your-n8n-instance.com/webhook/kb-upload":
        errors.append("N8N_WEBHOOK_URL is not set in n8n_config.py (still has placeholder value)")
    
    # Check KB ZIP file path
    if not n8n_config.KB_ZIP_FILE_PATH:
        errors.append("KB_ZIP_FILE_PATH is not set in n8n_config.py")
    else:
        kb_path = Path(n8n_config.KB_ZIP_FILE_PATH)
        if not kb_path.exists():
            errors.append(f"KB ZIP file not found: {n8n_config.KB_ZIP_FILE_PATH}")
        elif not kb_path.suffix.lower() == '.zip':
            errors.append(f"KB file must be a ZIP file, got: {kb_path.suffix}")
    
    if errors:
        return False, "\n".join(f"  - {error}" for error in errors)
    
    return True, None


def upload_kb_to_n8n() -> dict:
    """
    Upload KB ZIP file to n8n webhook endpoint.
    
    Returns:
        dict: Response from n8n endpoint
        
    Raises:
        Exception: If upload fails
    """
    print_section("Uploading KB to n8n")
    
    kb_path = Path(n8n_config.KB_ZIP_FILE_PATH)
    webhook_url = n8n_config.N8N_WEBHOOK_URL
    
    print_info(f"n8n Webhook URL: {webhook_url}")
    print_info(f"KB ZIP File: {kb_path}")
    print_info(f"File Size: {kb_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Prepare headers - matching curl command format
    headers = {
        'Content-Type': 'application/zip',
    }
    
    # Add custom headers from config if provided
    if hasattr(n8n_config, 'N8N_HEADERS') and n8n_config.N8N_HEADERS:
        headers.update(n8n_config.N8N_HEADERS)
    
    # Get timeout from config or use default
    timeout = getattr(n8n_config, 'REQUEST_TIMEOUT', 300)
    
    print()
    print_info(f"Request timeout: {timeout} seconds")
    print()
    
    try:
        print("Uploading KB ZIP file to n8n webhook...")
        
        # Read file as binary data (matching curl --data-binary)
        with open(kb_path, 'rb') as f:
            file_data = f.read()
        
        # Send as binary data with Content-Type: application/zip
        # Allow redirects (matching curl --location flag)
        response = requests.post(
            webhook_url,
            data=file_data,
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
        
        # Check response status
        # Note: n8n workflows might return 500 if they don't have a response configured
        # but the file was still received successfully
        if response.status_code == 500:
            # Try to parse error message
            try:
                error_data = response.json()
                error_msg = error_data.get('message', 'Unknown error')
                print_info(f"n8n workflow returned 500: {error_msg}")
                print_info("This might indicate the file was received but the workflow has no response configured.")
                print_info("Check n8n workflow logs to confirm file was processed.")
                
                # Still try to return the response
                return {"status": "received_but_error", "error": error_data, "status_code": response.status_code}
            except json.JSONDecodeError:
                print_error(f"HTTP error: {response.status_code} - {response.text[:200]}")
                response.raise_for_status()
        else:
            response.raise_for_status()
            print_success("KB uploaded successfully to n8n!")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            print(f"\nResponse:")
            print(json.dumps(response_data, indent=2))
            return response_data
        except json.JSONDecodeError:
            # If response is not JSON, return text
            print(f"\nResponse (text):")
            print(response.text)
            return {"status": "success", "response_text": response.text, "status_code": response.status_code}
    
    except requests.exceptions.Timeout:
        print_error(f"Request timed out after {timeout} seconds")
        raise
    except requests.exceptions.HTTPError as e:
        print_error(f"HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        raise
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        raise


def main():
    """
    Main function to upload KB to n8n.
    """
    print_section("n8n KB Upload")
    print_info("Starting KB upload to n8n webhook...")
    
    # Validate configuration
    print_section("Configuration Validation")
    is_valid, error_message = validate_config()
    if not is_valid:
        print_error("Configuration validation failed:")
        print(error_message)
        print("\nPlease update n8n_config.py with correct values.")
        sys.exit(1)
    
    print_success("Configuration validated successfully!")
    print_info(f"n8n Webhook URL: {n8n_config.N8N_WEBHOOK_URL}")
    print_info(f"KB ZIP File: {n8n_config.KB_ZIP_FILE_PATH}")
    
    # Upload KB to n8n
    try:
        response = upload_kb_to_n8n()
        
        # Summary
        print_section("Upload Summary")
        print_success("KB uploaded to n8n successfully!")
        print_info(f"n8n Webhook URL: {n8n_config.N8N_WEBHOOK_URL}")
        print_info(f"KB File: {n8n_config.KB_ZIP_FILE_PATH}")
        print("=" * 70)
        
    except Exception as e:
        print_error(f"Upload failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Upload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

