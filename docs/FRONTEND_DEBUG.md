# Frontend Debugging Guide

## Current Status
- ✅ Frontend is running on http://localhost:3000
- ✅ Backend is running on http://localhost:8000
- ✅ Bundle.js is being served (46,203 lines)
- ✅ All dependencies are installed
- ✅ React app compiled successfully

## Troubleshooting Steps

### 1. Check Browser Console
Open your browser's Developer Tools (F12) and check:
- **Console tab**: Look for any JavaScript errors (red messages)
- **Network tab**: Check if bundle.js is loading (should show 200 status)
- **Elements tab**: Check if `<div id="root">` has any content

### 2. Hard Refresh Browser
Try a hard refresh to clear cache:
- **Chrome/Edge**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- **Firefox**: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)

### 3. Check Network Connectivity
Verify the frontend can reach the backend:
```bash
curl http://localhost:8000/api/dashboards
```

### 4. Check for CORS Issues
Open browser console and check for CORS errors like:
- "Access to fetch at ... has been blocked by CORS policy"

### 5. Test Direct API Access
Try accessing the API directly:
```bash
curl http://localhost:8000/api/dashboards
```

### 6. Check React App Initialization
The app should render:
- Header with "MetaMind" title
- "Extract Dashboard" form with URL input
- Optional Dashboard ID input
- "Extract Dashboard" button

### 7. Common Issues

**Blank Page:**
- Check browser console for errors
- Verify JavaScript is enabled
- Check if bundle.js loaded (Network tab)

**Loading Forever:**
- Check if API calls are hanging
- Verify backend is responding
- Check browser console for failed requests

**CORS Errors:**
- Backend has CORS enabled for localhost:3000
- If using different port, update CORS settings in api_server.py

### 8. Restart Services

**Stop Frontend:**
```bash
lsof -ti:3000 | xargs kill -9
```

**Start Frontend:**
```bash
cd /home/devuser/sai_dev/metamind/frontend
npm start
```

**Stop Backend:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Start Backend:**
```bash
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
python3 api_server.py
```

## Expected Behavior

When you open http://localhost:3000, you should see:
1. A blue header with "MetaMind" title
2. A white card with "Extract Dashboard" form
3. Input fields for Dashboard URL and optional Dashboard ID
4. An "Extract Dashboard" button

If you see a blank page or loading spinner:
- Check browser console (F12) for errors
- Verify both services are running
- Try hard refresh (Ctrl+Shift+R)

