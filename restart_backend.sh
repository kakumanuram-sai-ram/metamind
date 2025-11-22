#!/bin/bash
# Script to restart the backend server

echo "Stopping existing backend..."
pkill -f "api_server.py" 2>/dev/null
sleep 2

echo "Starting backend server..."
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate 2>/dev/null || true

# Check if port is still in use
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is still in use. Killing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Start backend
echo "Starting backend..."
python scripts/api_server.py



