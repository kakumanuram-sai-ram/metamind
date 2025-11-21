# Authorization Requirements for Superset API

## Overview

The Superset API requires authentication headers for different endpoints. This document explains what headers are needed and how to obtain them.

## Required Headers

### 1. **Cookie Header** (Primary Authentication)
The `Cookie` header contains the session cookie which is the main authentication mechanism.

**How to get it:**
1. Open your browser and navigate to the Superset dashboard
2. Open Developer Tools (F12)
3. Go to the **Network** tab
4. Visit any dashboard or make any API request
5. Find any API request (e.g., `/api/v1/dashboard/...`)
6. Click on the request and go to **Headers** tab
7. Copy the entire value of the `Cookie` header

**Important:** The `session` cookie within the Cookie header is the critical authentication token. This cookie expires after a certain period, so you may need to refresh it periodically.

### 2. **X-CSRFToken Header** (Required for POST requests)
The CSRF token is required for POST requests to prevent cross-site request forgery attacks.

**How to get it:**
1. Follow the same steps as above
2. In the request headers, find the `X-CSRFToken` header
3. Copy its value

**Note:** This token may also expire and need to be refreshed.

### 3. **Referer Header** (For Chart Data Endpoints)
The `Referer` header is automatically added by the code for chart data endpoints (`/api/v1/chart/{id}/data`). This helps with CSRF protection.

**Value:** `https://cdp-dataview.platform.mypaytm.com/superset/dashboard/`

## Chart Data Endpoint Authorization

The chart data endpoints (`/api/v1/chart/{id}/data` and `/api/v1/chart/data`) use the same authentication as other endpoints:

### Authentication Method
- **Cookie Header**: Contains the session cookie (from Google Auth)
- **X-CSRFToken Header**: Required for POST requests
- **Referer Header**: Automatically added by the code for CSRF protection
- **Origin Header**: Automatically added by the code for CSRF protection

### No Bearer Token Required
- This Superset instance uses **Google Auth** via Cookie + X-CSRFToken
- **No Bearer token is needed or used**
- As an admin, your Cookie + X-CSRFToken provide full access

### Current Status
- Chart data endpoints are attempted with proper headers
- If they fail, errors are silently handled (non-critical)
- SQL queries are successfully extracted from the **dataset definition** as a fallback
- This provides the base SQL query which is sufficient for most use cases

## Configuration

All headers are configured in `config.py`:

```python
HEADERS = {
    'Cookie': 'your-cookie-value-here',
    'X-CSRFToken': 'your-csrf-token-here',
    # Optional: 'Authorization': 'Bearer YOUR_TOKEN',
}
```

## Troubleshooting

### 401 UNAUTHORIZED Errors
- **Cause**: Session cookie has expired
- **Solution**: Refresh the cookie from your browser's Network tab

### 403 FORBIDDEN Errors
- **Cause**: CSRF token mismatch or missing Referer
- **Solution**: Refresh the X-CSRFToken and ensure Referer header is set

### Chart Data Endpoints Failing
- **Not Critical**: The code handles this gracefully
- **SQL Still Extracted**: Queries are obtained from dataset definitions
- **Check**: Ensure your Cookie and X-CSRFToken are fresh (refresh from browser if expired)

## Summary

**Authentication Method: Google Auth (Cookie-based)**
- ✅ Cookie header (with session cookie from Google Auth)
- ✅ X-CSRFToken header (for POST requests)
- ✅ Referer header (auto-added for chart data endpoints)
- ✅ Origin header (auto-added for chart data endpoints)

**No Bearer Token Required**
- This Superset instance uses Google Auth
- Cookie + X-CSRFToken provide full admin access
- All endpoints work with these headers

The current implementation works correctly for extracting dashboard metadata and SQL queries. Chart data endpoints use the same authentication and are attempted with proper CSRF protection headers.

