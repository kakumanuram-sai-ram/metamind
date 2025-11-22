# Current Log Status

Generated: $(date)

## Log File Locations

### Primary Logs
- **Backend**: `/tmp/api_server.log` (127KB, ~2,337 lines)
- **Frontend**: `/tmp/frontend.log` (11KB, ~170 lines)

### Additional Logs
- `/tmp/api_server_test.log` (204KB)
- `/tmp/dashboard_processing.log` (11KB)
- `/tmp/phase5_rerun.log` (2.5KB)

## Recent Backend Logs (Last 50 lines)

The backend is currently processing dashboard extraction. Recent activity includes:

- API progress checks: `GET /api/progress` - Status: completed
- Dashboard file checks: `GET /api/dashboard/195/files` - Status: 200 OK
- Chart extraction in progress:
  - Extracting chart ID: 1557 (16/17)
  - Chart 1386 extracted successfully
  - POST endpoint succeeded in 7.17s

## Recent Frontend Logs

The frontend is running with one ESLint warning:
- Warning: `'isCompleted' is assigned a value but never used` in `DashboardSection.js` line 753
- Status: Compiled successfully (with warnings)

## View Logs Commands

### Real-time Backend Logs
```bash
tail -f /tmp/api_server.log
```

### Real-time Frontend Logs
```bash
tail -f /tmp/frontend.log
```

### Last 100 Lines of Backend
```bash
tail -100 /tmp/api_server.log
```

### Last 100 Lines of Frontend
```bash
tail -100 /tmp/frontend.log
```

### Use Built-in Viewer
```bash
cd /home/devuser/sai_dev/metamind
bash view_backend_logs.sh
```

## Log Summary

- **Backend**: Active, processing dashboard 195, extracting charts
- **Frontend**: Running, compiled successfully with minor warnings
- **Status**: Both services operational

