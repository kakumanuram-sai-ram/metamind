#!/bin/bash
# Real-time backend extraction progress monitor

clear
echo "=================================================================================="
echo "🔍 MetaMind Backend Extraction Progress Monitor"
echo "=================================================================================="
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""
echo "=================================================================================="
echo ""

# Function to show current status
show_status() {
    echo ""
    echo "📊 CURRENT STATUS:"
    curl -s http://localhost:8000/api/progress 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"   Status: {d['status']}\")
    print(f\"   Operation: {d.get('current_operation', 'N/A')}\")
    if 'dashboards' in d and d['dashboards']:
        for dash_id, dash_info in d['dashboards'].items():
            print(f\"\\n   Dashboard {dash_id}:\")
            print(f\"     Phase: {dash_info.get('current_phase', 'N/A')}\")
            print(f\"     Current File: {dash_info.get('current_file', 'N/A')}\")
            print(f\"     Progress: {dash_info.get('completed_files_count', 0)}/{dash_info.get('total_files', 0)} files\")
except:
    print(\"   Unable to fetch status\")
" 2>/dev/null
    echo ""
    echo "=================================================================================="
    echo ""
}

# Show initial status
show_status

# Monitor logs with filtering
tail -f /tmp/api_server.log 2>&1 | while IFS= read -r line; do
    # Filter for important extraction messages
    if echo "$line" | grep -qE "(Step|Phase|Extracting|Chart|Getting chart|Calling|endpoint|✅|❌|⚠️|Processing chart|LLM|tables|columns|metadata|Completed|Error|Exception)"; then
        echo "$line"
        # Update status every 10 important messages
        if echo "$line" | grep -qE "(Step|Phase|Completed)"; then
            show_status
        fi
    fi
done
