# Troubleshooting Guide

## Problem: 401 UNAUTHORIZED After Updating Credentials

### Symptoms
- You updated `config.py` with fresh cookies
- Test script (`test_auth.py`) shows ✅ authentication works
- But the API server still returns 401 errors

### Root Cause
The FastAPI server loads `config.py` **once when it starts**. If you update `config.py` while the server is running, it continues using the old credentials.

### Solution: Restart the API Server

**Option 1: Manual Restart**
```bash
# Find and kill the server process
pkill -f "api_server.py"

# Start it again
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
python api_server.py
```

**Option 2: Use the Restart Script**
```bash
cd /home/devuser/sai_dev/metamind
./restart_api.sh
```

**Option 3: Quick Restart Command**
```bash
cd /home/devuser/sai_dev/metamind && export PATH="$HOME/.local/bin:$PATH" && pkill -f "api_server.py" && sleep 2 && source meta_env/bin/activate && python api_server.py &
```

### Verification Steps

1. **Test authentication:**
   ```bash
   cd /home/devuser/sai_dev/metamind
   source meta_env/bin/activate
   python test_auth.py
   ```
   Should show ✅

2. **Test specific dashboard:**
   ```bash
   python test_dashboard_access.py
   ```
   Should show ✅ for the dashboard you want to extract

3. **Restart API server** (see above)

4. **Test via API:**
   ```bash
   curl http://localhost:8000/api/dashboards
   ```

5. **Try extracting dashboard from frontend** at http://localhost:3000

## Common Issues

### Issue: "Missing Authorization Header"
- **Cause**: Session cookie expired
- **Fix**: Get fresh cookies from browser and update `config.py`, then **restart the server**

### Issue: Works in test but fails in API
- **Cause**: API server using old config
- **Fix**: Restart the API server

### Issue: Dashboard 729 works but others don't
- **Cause**: Permission issue - you may not have access to that dashboard
- **Fix**: Check if you can access the dashboard in the browser

### Issue: Server won't start
- **Cause**: Port 8000 already in use
- **Fix**: 
  ```bash
  pkill -f "api_server.py"
  # Or change port in api_server.py (last line)
  ```

## Quick Reference

| Problem | Solution |
|--------|----------|
| 401 after updating config | Restart API server |
| Test works, API doesn't | Restart API server |
| Cookies expired | Get fresh cookies, update config, restart server |
| Permission denied | Check dashboard access in browser |
| Port in use | Kill existing process or change port |

## Best Practices

1. **Always restart the server** after updating `config.py`
2. **Test authentication** with `test_auth.py` before using the API
3. **Keep cookies fresh** - they expire after ~30 minutes of inactivity
4. **Check dashboard access** in browser before trying to extract

