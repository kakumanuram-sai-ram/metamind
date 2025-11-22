# Logs Directory

This directory contains log files for the MetaMind application.

## Log Files

- `api_server_{timestamp}.log` - Backend FastAPI server logs
- `frontend_{timestamp}.log` - Frontend React development server logs

## Viewing Logs

### View Latest Backend Log
```bash
cd /home/devuser/sai_dev/metamind
LATEST=$(ls -t logs/api_server_*.log | head -1)
tail -f "$LATEST"
```

### View Latest Frontend Log
```bash
cd /home/devuser/sai_dev/metamind
LATEST=$(ls -t logs/frontend_*.log | head -1)
tail -f "$LATEST"
```

### List All Logs
```bash
ls -lht logs/*.log
```

## Notes

- Log files are automatically created when services start
- Files are timestamped to track multiple runs
- Logs are git-ignored (see `.gitignore`)

