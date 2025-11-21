#!/bin/bash
# Start the FastAPI backend server

cd "$(dirname "$0")"
echo "Starting FastAPI backend server..."
echo "API will be available at http://localhost:8000"
echo "API docs will be available at http://localhost:8000/docs"
echo ""
python scripts/api_server.py

