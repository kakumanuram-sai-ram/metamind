"""
Configuration file for n8n KB Upload

This file contains configuration for sending Knowledge Base (KB) ZIP files
to an n8n webhook endpoint.
"""

# n8n Webhook Configuration
N8N_WEBHOOK_URL = "https://n8n.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com/webhook/upi-dashboard-bot-metadata"

# Knowledge Base (KB) Configuration
KB_ZIP_FILE_PATH = "/home/devuser/sai_dev/metamind/extracted_meta/knowledge_base/knowledge_base_csv.zip"  # Path to the KB ZIP file

# Request Configuration (Optional)
# Additional headers if needed for authentication or other purposes
N8N_HEADERS = {
    # Example: "Authorization": "Bearer your-token-here",
    # Example: "X-API-Key": "your-api-key",
    # Add any custom headers your n8n endpoint requires
}

# Request Timeout (in seconds)
REQUEST_TIMEOUT = 300  # 5 minutes default

# Additional Form Data (Optional)
# If your n8n endpoint expects additional form fields along with the file
# Example: {"model_id": "my-model", "version": "1.0"}
ADDITIONAL_FORM_DATA = {
    # Add any additional form fields here if needed
    # Example: "model_id": "my-model",
    # Example: "version": "1.0",
}

