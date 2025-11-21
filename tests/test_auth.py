"""
Test authentication and show what headers are being sent
"""
import os
import sys
import requests
# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

from config import BASE_URL, HEADERS

def test_auth():
    """Test if authentication is working"""
    print("=" * 80)
    print("Testing Superset API Authentication")
    print("=" * 80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"\nHeaders being used:")
    print(f"  - Cookie: {'Present' if HEADERS.get('Cookie') else 'MISSING'}")
    print(f"  - X-CSRFToken: {'Present' if HEADERS.get('X-CSRFToken') else 'MISSING'}")
    
    if HEADERS.get('Cookie'):
        cookie_preview = HEADERS['Cookie'][:100] + "..." if len(HEADERS['Cookie']) > 100 else HEADERS['Cookie']
        print(f"  - Cookie preview: {cookie_preview}")
    
    # Test with a known working dashboard (729)
    test_dashboard_id = 729
    print(f"\n{'=' * 80}")
    print(f"Testing with Dashboard {test_dashboard_id} (known to work)")
    print(f"{'=' * 80}")
    
    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    url = f"{BASE_URL}/api/v1/dashboard/{test_dashboard_id}"
    print(f"\nMaking request to: {url}")
    print(f"Headers being sent:")
    for key, value in session.headers.items():
        if key == 'Cookie':
            print(f"  {key}: {value[:80]}... (truncated)")
        else:
            print(f"  {key}: {value}")
    
    try:
        response = session.get(url)
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authentication is working!")
            data = response.json()
            if 'result' in data:
                print(f"✅ Dashboard found: {data['result'].get('dashboard_title', 'Unknown')}")
        elif response.status_code == 401:
            print("❌ Authentication failed: 401 UNAUTHORIZED")
            print(f"Response: {response.text[:500]}")
            print("\n⚠️  Your session cookie has likely expired!")
            print("\nTo fix this:")
            print("1. Open your browser and go to: https://cdp-dataview.platform.mypaytm.com")
            print("2. Open Developer Tools (F12) -> Network tab")
            print("3. Visit any dashboard page")
            print("4. Find any API request (e.g., /api/v1/dashboard/...)")
            print("5. Copy the 'Cookie' header value")
            print("6. Copy the 'X-CSRFToken' header value")
            print("7. Update config.py with the new values")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auth()

