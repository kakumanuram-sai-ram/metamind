#!/bin/bash
# Script to view backend API logs in real-time

echo "=========================================="
echo "MetaMind Backend Log Viewer"
echo "=========================================="
echo ""
echo "This will show all backend activity in real-time."
echo "Press Ctrl+C to stop."
echo ""
echo "=========================================="
echo ""

# Check if log file exists
if [ -f "/tmp/api_server.log" ]; then
    tail -f /tmp/api_server.log
else
    echo "⚠️  Log file not found at /tmp/api_server.log"
    echo ""
    echo "The backend might be running without log redirection."
    echo "Check if the backend process is running:"
    echo "  ps aux | grep api_server"
    echo ""
    echo "To see logs in terminal, restart the backend:"
    echo "  cd /home/devuser/sai_dev/metamind"
    echo "  source meta_env/bin/activate"
    echo "  python scripts/api_server.py"
fi

