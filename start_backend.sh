#!/bin/bash
# Start the FastAPI backend server

cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
LOGS_DIR="logs"
mkdir -p "$LOGS_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOGS_DIR/api_server_${TIMESTAMP}.log"

# Activate virtual environment if it exists
if [ -d "meta_env" ]; then
    source meta_env/bin/activate
    echo "✓ Virtual environment activated"
fi

echo "Starting FastAPI backend server..."
echo "API will be available at http://localhost:8000"
echo "API docs will be available at http://localhost:8000/docs"
echo "Python: $(which python)"
echo "Logs: $LOG_FILE"
echo ""
python scripts/api_server.py 2>&1 | tee "$LOG_FILE"

