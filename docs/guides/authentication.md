# Authentication Guide

## Superset API Authentication

MetaMind uses session-based authentication with Superset. You need to provide:

1. **Session Cookie** - From your browser after logging into Superset
2. **CSRF Token** - Security token for API requests

## Getting Credentials

### Method 1: Browser Developer Tools

1. Log into Superset in your browser
2. Open Developer Tools (F12)
3. Go to Network tab
4. Make any request to Superset API
5. Find the request and check Headers
6. Copy:
   - `Cookie` header value
   - `X-CSRFToken` header value

### Method 2: Browser Console

```javascript
// Run in browser console on Superset page
document.cookie
// Look for 'session' cookie value
```

## Configuration

Edit `config.py`:

```python
HEADERS = {
    'Cookie': 'session=YOUR_SESSION_COOKIE_HERE',
    'X-CSRFToken': 'YOUR_CSRF_TOKEN_HERE',
}
```

## Testing Authentication

Run the test script:

```bash
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
python test_auth.py
```

Or test dashboard access:

```bash
python test_dashboard_access.py
```

## Token Expiration

Session cookies expire after a period of inactivity. If you get `401 Unauthorized` errors:

1. Log out and log back into Superset
2. Get fresh cookies and CSRF token
3. Update `config.py`
4. Restart the API server

## Security Notes

- Never commit `config.py` with real credentials to version control
- Use environment variables for production
- Rotate credentials regularly

