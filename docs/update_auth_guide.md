# How to Update Authentication Credentials

## Problem: 401 UNAUTHORIZED Error

If you're getting `401 Client Error: UNAUTHORIZED` or `Missing Authorization Header`, your session cookie has expired.

## Solution: Get Fresh Credentials

### Step 1: Open Superset in Browser
1. Go to: https://cdp-dataview.platform.mypaytm.com
2. **Make sure you're logged in** (you should see dashboards)

### Step 2: Open Developer Tools
1. Press **F12** (or right-click → Inspect)
2. Go to the **Network** tab
3. Make sure the network monitor is recording (red circle should be active)

### Step 3: Make an API Request
1. Visit any dashboard (e.g., https://cdp-dataview.platform.mypaytm.com/superset/dashboard/729/)
2. In the Network tab, look for requests to `/api/v1/dashboard/` or similar API endpoints
3. Click on one of these requests

### Step 4: Copy Headers
1. In the request details, go to the **Headers** tab
2. Scroll down to **Request Headers**
3. Find the **Cookie** header:
   - Copy the ENTIRE value (it's very long)
   - It should start with something like `rl_page_init_referrer=...`
4. Find the **X-CSRFToken** header:
   - Copy its value
   - It should look like `IjAwNTM5ZmMxYTkyYmM5MGY1MDM5NWU1Yzc1NDFhMmU2NjgxZWNlOTUi...`

### Step 5: Update config.py
1. Open `/home/devuser/sai_dev/metamind/config.py`
2. Update the `HEADERS` dictionary:
   ```python
   HEADERS = {
       'Cookie': 'PASTE_YOUR_NEW_COOKIE_HERE',
       'X-CSRFToken': 'PASTE_YOUR_NEW_CSRF_TOKEN_HERE',
   }
   ```
3. Save the file

### Step 6: Test Authentication
Run the test script:
```bash
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
python test_auth.py
```

If it shows ✅, your authentication is working!

## Quick Test Command

```bash
cd /home/devuser/sai_dev/metamind && source meta_env/bin/activate && python test_auth.py
```

## Important Notes

- **Cookies expire**: Session cookies typically expire after:
  - A period of inactivity (e.g., 30 minutes)
  - When you log out
  - When your browser session ends
  
- **Keep credentials fresh**: Update `config.py` whenever you get 401 errors

- **Security**: Never commit `config.py` with real credentials to version control

## Alternative: Use Environment Variables

You can also set credentials via environment variables (more secure):

```python
import os

HEADERS = {
    'Cookie': os.getenv('SUPERSET_COOKIE', 'your-default-cookie'),
    'X-CSRFToken': os.getenv('SUPERSET_CSRF_TOKEN', 'your-default-token'),
}
```

Then set them before running:
```bash
export SUPERSET_COOKIE="your-cookie-value"
export SUPERSET_CSRF_TOKEN="your-csrf-token"
```

