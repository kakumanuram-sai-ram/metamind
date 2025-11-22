"""
Configuration file for Prism BA API Model Deployment

This file contains all configuration settings for:
- Prism API base URL
- Model creation settings
- Knowledge Base (KB) file path
"""

# Prism BA API Configuration
PRISM_API_BASE_URL = "https://prism-ba.internal.ap-south-1.staging.osmose.risk.pai.mypaytm.com"

# ============================================================================
# Model Configuration
# ============================================================================

# Model ID: Unique identifier suffix. Full ID will be 'ba-your-id'.
# Only lowercase letters, numbers, and hyphens allowed (no spaces).
# Example: "my-test-model" will become "ba-my-test-model"
MODEL_ID = "my-test-model"

# Model Name: Display name for the model (shown in UI)
MODEL_NAME = "My Test Model"

# Model Description: Optional description (can be blank)
# Set to "" or None if you want it blank
MODEL_DESCRIPTION = "Model created via API deployment script"

# ============================================================================
# Model Configuration Settings
# ============================================================================

# Max Tokens: Maximum number of tokens for responses
MAX_TOKENS = "4096"

# Temperature: Temperature value (range: 0 to 0.5)
# Controls randomness in responses. Lower = more deterministic.
TEMPERATURE = "0"  # Valid range: "0" to "0.5"

# Supported Features: Comma-separated list of features
# Example: "streaming" or "streaming,feature2,feature3"
SUPPORTED_FEATURES = "streaming"

# Email Pool: One email address per line for Trino database connections
# These emails will be rotated for Trino database connections.
# Leave empty string "" to use default pool.
# For multiple emails, use newlines: "email1@paytm.com\nemail2@paytm.com"
EMAIL_POOL = "kakumanu.ram@paytm.com"  # One email per line, or "" for default

# Knowledge Base (KB) Configuration
KB_ZIP_FILE_PATH = "/home/devuser/sai_dev/metamind/extracted_meta/knowledge_base/knowledge_base.zip"  # Path to the KB ZIP file

# Metadata (Optional): Custom metadata as a valid JSON object
# Set to None or {} if not needed
CUSTOM_METADATA = None  # Example: {"key": "value", "version": "1.0"}


