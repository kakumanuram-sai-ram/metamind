#!/bin/bash
# Restart the FastAPI server with updated config

cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"

echo "Stopping existing API server..."
pkill -f "scripts/api_server.py" || echo "No existing server found"

sleep 2

echo "Starting API server with updated config..."
source meta_env/bin/activate
python scripts/api_server.py

