"""
Simple example of using the Superset Extractor

This script demonstrates how to extract metadata from a Superset dashboard
and save it to a CSV file with chart id, label, and query information.
"""
import os
import sys
# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

from query_extract import SupersetExtractor
from config import BASE_URL, HEADERS, DEFAULT_DASHBOARD_ID

# Dashboard ID to extract (can be overridden)
DASHBOARD_ID = DEFAULT_DASHBOARD_ID

# Initialize the extractor
extractor = SupersetExtractor(BASE_URL, HEADERS)

# Extract dashboard information
print(f"Starting extraction for dashboard ID: {DASHBOARD_ID}...")
try:
    dashboard_info = extractor.extract_dashboard_complete_info(DASHBOARD_ID)
    
    # Export to CSV (primary output - contains chart id, label, and query)
    print("\nExporting metadata to CSV...")
    extractor.export_to_csv(dashboard_info)
    
    # Optional: Export to JSON and SQL files
    print("\nExporting additional formats...")
    extractor.export_to_json(dashboard_info)
    extractor.export_sql_queries(dashboard_info)

    # Print summary
    print("\n" + "="*80)
    print(f"Dashboard: {dashboard_info.dashboard_title}")
    print(f"URL: {dashboard_info.dashboard_url}")
    print(f"Owner: {dashboard_info.owner}")
    print(f"Total Charts: {len(dashboard_info.charts)}")
    print("="*80)
    
    # Print key information for each chart (id, label, query status)
    print("\nChart Summary:")
    for i, chart in enumerate(dashboard_info.charts, 1):
        print(f"\n{i}. Chart ID: {chart.chart_id}")
        print(f"   Label: {chart.chart_name}")
        print(f"   Type: {chart.chart_type}")
        print(f"   Query Available: {'Yes' if chart.sql_query else 'No'}")
        if chart.sql_query:
            sql_preview = chart.sql_query[:150].replace('\n', ' ')
            print(f"   Query Preview: {sql_preview}...")
    
    print("\n" + "="*80)
    print("Extraction completed successfully!")
    print(f"\nFiles generated:")
    print(f"  - dashboard_{DASHBOARD_ID}_metadata.csv (primary output)")
    print(f"  - dashboard_{DASHBOARD_ID}_info.json")
    print(f"  - dashboard_{DASHBOARD_ID}_queries.sql")
    
except Exception as e:
    print(f"\nError during extraction: {e}")
    import traceback
    traceback.print_exc()