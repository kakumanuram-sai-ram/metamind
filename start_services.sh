#!/bin/bash
# Script to start both backend and frontend services

echo "=========================================="
echo "Starting MetaMind Services"
echo "=========================================="
echo ""

# Kill any existing processes
echo "Stopping existing services..."
pkill -f "api_server.py" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null
sleep 2

# Create logs directory if it doesn't exist
LOGS_DIR="/home/devuser/sai_dev/metamind/logs"
mkdir -p "$LOGS_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Start Backend
echo "Starting Backend API Server..."
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate 2>/dev/null || true
nohup python scripts/api_server.py > "$LOGS_DIR/api_server_${TIMESTAMP}.log" 2>&1 &
BACKEND_PID=$!
echo "  Backend started (PID: $BACKEND_PID)"
echo "  Logs: tail -f $LOGS_DIR/api_server_${TIMESTAMP}.log"
echo "  URL: http://localhost:8000"
echo ""

# Wait a moment for backend to start
sleep 3

# Start Frontend
echo "Starting Frontend React App..."
cd /home/devuser/sai_dev/metamind/frontend
nohup npm start > "$LOGS_DIR/frontend_${TIMESTAMP}.log" 2>&1 &
FRONTEND_PID=$!
echo "  Frontend started (PID: $FRONTEND_PID)"
echo "  Logs: tail -f $LOGS_DIR/frontend_${TIMESTAMP}.log"
echo "  URL: http://localhost:3000"
echo ""

# Wait a moment for frontend to start
sleep 5

# Check if services are running
echo "=========================================="
echo "Service Status"
echo "=========================================="
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "✅ Backend is running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start"
fi

if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "✅ Frontend is running (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend failed to start"
fi

echo ""
echo "=========================================="
echo "View Logs:"
echo "  Backend:  tail -f $LOGS_DIR/api_server_${TIMESTAMP}.log"
echo "  Frontend: tail -f $LOGS_DIR/frontend_${TIMESTAMP}.log"
echo "  Latest:   tail -f $LOGS_DIR/api_server_*.log (most recent)"
echo "=========================================="



