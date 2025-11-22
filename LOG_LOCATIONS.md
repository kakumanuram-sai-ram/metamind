# Log File Locations

This document describes where log files are stored for the MetaMind application.

## Primary Log Locations

### Backend Logs
- **Location**: `metamind/logs/api_server_{timestamp}.log`
- **Description**: FastAPI backend server logs including API requests, responses, and processing status
- **View latest logs**: `tail -f metamind/logs/api_server_*.log | tail -1`
- **View recent logs**: `tail -100 metamind/logs/api_server_*.log | tail -1`
- **List all logs**: `ls -lht metamind/logs/api_server_*.log`

### Frontend Logs
- **Location**: `metamind/logs/frontend_{timestamp}.log`
- **Description**: React frontend development server logs including compilation status and warnings
- **View latest logs**: `tail -f metamind/logs/frontend_*.log | tail -1`
- **View recent logs**: `tail -100 metamind/logs/frontend_*.log | tail -1`
- **List all logs**: `ls -lht metamind/logs/frontend_*.log`

### Legacy Log Locations (Deprecated)
- `/tmp/api_server.log` - Old location (may not be accessible)
- `/tmp/frontend.log` - Old location (may not be accessible)

## Additional Log Files

### Other Temporary Logs
- `/tmp/api_server_test.log` - Test run logs
- `/tmp/dashboard_processing.log` - Dashboard processing logs
- `/tmp/phase5_rerun.log` - Phase 5 rerun logs

### Evaluation Logs
- **Location**: `/home/devuser/sai_dev/eval/prism_eval/multithreaded_batch_processor_{timestamp}.log`
- **Description**: Timestamped logs for batch processing evaluations

## Log Viewing Commands

### View Latest Backend Logs in Real-Time
```bash
cd /home/devuser/sai_dev/metamind
tail -f logs/api_server_*.log | tail -1
```

### View Latest Frontend Logs in Real-Time
```bash
cd /home/devuser/sai_dev/metamind
tail -f logs/frontend_*.log | tail -1
```

### View Most Recent Backend Log File
```bash
cd /home/devuser/sai_dev/metamind
LATEST_BACKEND=$(ls -t logs/api_server_*.log | head -1)
tail -f "$LATEST_BACKEND"
```

### View Most Recent Frontend Log File
```bash
cd /home/devuser/sai_dev/metamind
LATEST_FRONTEND=$(ls -t logs/frontend_*.log | head -1)
tail -f "$LATEST_FRONTEND"
```

### View Last 100 Lines of Latest Backend Logs
```bash
cd /home/devuser/sai_dev/metamind
LATEST_BACKEND=$(ls -t logs/api_server_*.log | head -1)
tail -100 "$LATEST_BACKEND"
```

### View Last 100 Lines of Latest Frontend Logs
```bash
cd /home/devuser/sai_dev/metamind
LATEST_FRONTEND=$(ls -t logs/frontend_*.log | head -1)
tail -100 "$LATEST_FRONTEND"
```

### List All Log Files
```bash
cd /home/devuser/sai_dev/metamind
ls -lht logs/*.log
```

### Use the Built-in Log Viewer Script
```bash
cd /home/devuser/sai_dev/metamind
bash view_backend_logs.sh
```

## Log File Organization

- Logs are stored in `metamind/logs/` directory
- Each log file is timestamped: `api_server_YYYYMMDD_HHMMSS.log`
- Logs are automatically created when services start
- Old logs are preserved (not automatically deleted)

## Notes

- Logs are now stored in a persistent location (`metamind/logs/`) instead of `/tmp`
- Log files are timestamped to allow tracking multiple service runs
- The backend logs include detailed API request/response information
- The frontend logs include webpack compilation warnings and errors
- Log files are git-ignored (see `logs/.gitignore`)

