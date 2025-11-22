#!/bin/bash
# Start the React frontend development server

cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
LOGS_DIR="logs"
mkdir -p "$LOGS_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOGS_DIR/frontend_${TIMESTAMP}.log"

cd frontend
echo "Starting React frontend..."
echo "Frontend will be available at http://localhost:3000"
echo "Logs: $LOG_FILE"
echo ""
npm start 2>&1 | tee "../$LOG_FILE"

