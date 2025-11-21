"""
Test access to specific dashboards
"""
import os
import sys
# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

from query_extract import SupersetExtractor
from config import BASE_URL, HEADERS

def test_dashboard_access(dashboard_id):
    """Test if we can access a specific dashboard"""
    print(f"\n{'=' * 80}")
    print(f"Testing access to Dashboard {dashboard_id}")
    print(f"{'=' * 80}")
    
    extractor = SupersetExtractor(BASE_URL, HEADERS)
    
    try:
        # Try to get dashboard metadata
        dashboard = extractor.get_dashboard_metadata(dashboard_id)
        
        if dashboard:
            print(f"✅ SUCCESS: Can access Dashboard {dashboard_id}")
            print(f"   Title: {dashboard.get('dashboard_title', 'Unknown')}")
            return True
        else:
            print(f"❌ FAILED: Dashboard {dashboard_id} returned empty response")
            return False
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"❌ FAILED: 401 UNAUTHORIZED - Authentication issue")
            print(f"   This could mean:")
            print(f"   1. Your credentials don't have access to this dashboard")
            print(f"   2. The dashboard doesn't exist")
            print(f"   3. The dashboard is private/restricted")
        elif e.response.status_code == 404:
            print(f"❌ FAILED: 404 NOT FOUND - Dashboard {dashboard_id} doesn't exist")
        else:
            print(f"❌ FAILED: {e.response.status_code} - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    import requests
    
    # Test known working dashboard
    print("Testing with Dashboard 729 (known to work)...")
    test_dashboard_access(729)
    
    # Test the problematic dashboard
    print("\n" + "=" * 80)
    print("Testing with Dashboard 282 (the one you're trying to extract)...")
    test_dashboard_access(282)
    
    print("\n" + "=" * 80)
    print("Note: If dashboard 282 fails, it might be:")
    print("  - A permission issue (you don't have access)")
    print("  - The dashboard doesn't exist")
    print("  - The dashboard is private/restricted")

