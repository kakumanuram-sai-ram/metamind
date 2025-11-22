#!/usr/bin/env python3
"""
Bulk Extractor for Dashboard Metadata

This script extracts dashboard metadata for multiple dashboards using query_extract.py.
For each dashboard, it creates:
- {dashboard_id}_json.json
- {dashboard_id}_csv.csv
- {dashboard_id}_queries.sql

Usage:
    python bulk_json_extract.py --dashboard-ids 511 729 842 476 585
    python bulk_json_extract.py --dashboard-ids-file dashboard_ids.txt
"""

import os
import sys
import argparse
from typing import List
from query_extract import SupersetExtractor
from config import BASE_URL, HEADERS

# Get the metamind directory (parent of scripts directory)
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_metamind_dir = os.path.dirname(_scripts_dir)
DEFAULT_OUTPUT_DIR = os.path.join(_metamind_dir, "extracted_meta")


def extract_dashboard_metadata(
    dashboard_id: int,
    output_base_dir: str = None,
    extractor: SupersetExtractor = None
) -> dict:
    """
    Extract dashboard metadata for a single dashboard using query_extract.py methods.
    Creates: {dashboard_id}_json.json, {dashboard_id}_csv.csv, {dashboard_id}_queries.sql
    
    Args:
        dashboard_id: Dashboard ID to extract
        output_base_dir: Base directory for output (default: metamind/extracted_meta)
        extractor: SupersetExtractor instance (creates new one if None)
    
    Returns:
        Dict with extraction results: {
            'dashboard_id': int,
            'dashboard_title': str,
            'num_charts': int,
            'output_dir': str,
            'success': bool,
            'error': str or None
        }
    """
    if output_base_dir is None:
        output_base_dir = DEFAULT_OUTPUT_DIR
    
    if extractor is None:
        extractor = SupersetExtractor(BASE_URL, HEADERS)
    
    result = {
        'dashboard_id': dashboard_id,
        'dashboard_title': None,
        'num_charts': 0,
        'output_dir': None,
        'success': False,
        'error': None
    }
    
    try:
        print(f"\n{'='*80}")
        print(f"Extracting Dashboard ID: {dashboard_id}")
        print(f"{'='*80}")
        
        # Extract dashboard info (includes all charts)
        dashboard_info = extractor.extract_dashboard_complete_info(dashboard_id)
        
        result['dashboard_title'] = dashboard_info.dashboard_title
        result['num_charts'] = len(dashboard_info.charts)
        result['output_dir'] = f"{output_base_dir}/{dashboard_id}"
        
        print(f"Dashboard: {dashboard_info.dashboard_title}")
        print(f"Total charts found: {len(dashboard_info.charts)}")
        
        # Create output directory
        os.makedirs(result['output_dir'], exist_ok=True)
        
        # Export using query_extract.py methods (same structure as query_extract.py)
        print(f"\nExporting files to: {result['output_dir']}/")
        
        # 1. Export to JSON: {dashboard_id}_json.json
        json_file = f"{result['output_dir']}/{dashboard_id}_json.json"
        extractor.export_to_json(dashboard_info, filename=json_file)
        print(f"  ✅ Created: {dashboard_id}_json.json")
        
        # 2. Export to CSV: {dashboard_id}_csv.csv
        csv_file = f"{result['output_dir']}/{dashboard_id}_csv.csv"
        extractor.export_to_csv(dashboard_info, filename=csv_file)
        print(f"  ✅ Created: {dashboard_id}_csv.csv")
        
        # 3. Export SQL queries: {dashboard_id}_queries.sql
        sql_file = f"{result['output_dir']}/{dashboard_id}_queries.sql"
        extractor.export_sql_queries(dashboard_info, filename=sql_file)
        print(f"  ✅ Created: {dashboard_id}_queries.sql")
        
        result['success'] = True
        print(f"\n✅ Dashboard {dashboard_id}: All files extracted successfully")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"\n❌ Error extracting dashboard {dashboard_id}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return result


def extract_multiple_dashboards(
    dashboard_ids: List[int],
    output_base_dir: str = None
) -> List[dict]:
    """
    Extract dashboard metadata for multiple dashboards using query_extract.py.
    
    Args:
        dashboard_ids: List of dashboard IDs to extract
        output_base_dir: Base directory for output (default: metamind/extracted_meta)
    
    Returns:
        List of extraction results (one per dashboard)
    """
    if output_base_dir is None:
        output_base_dir = DEFAULT_OUTPUT_DIR
    
    print("\n" + "="*80)
    print("BULK DASHBOARD METADATA EXTRACTION")
    print("="*80)
    print(f"Dashboard IDs: {', '.join(map(str, dashboard_ids))}")
    print(f"Total dashboards: {len(dashboard_ids)}")
    print(f"Output base directory: {output_base_dir}")
    print("="*80)
    
    if not dashboard_ids:
        print("\n❌ No dashboards to process")
        return []
    
    # Create extractor once (reused for all dashboards)
    extractor = SupersetExtractor(BASE_URL, HEADERS)
    
    results = []
    for idx, dashboard_id in enumerate(dashboard_ids, 1):
        print(f"\n[{idx}/{len(dashboard_ids)}] Processing Dashboard {dashboard_id}...")
        result = extract_dashboard_metadata(
            dashboard_id=dashboard_id,
            output_base_dir=output_base_dir,
            extractor=extractor
        )
        results.append(result)
    
    # Print summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    for r in successful:
        print(f"   - Dashboard {r['dashboard_id']} ({r['dashboard_title']}): {r['num_charts']} charts")
        print(f"     Files: {r['dashboard_id']}_json.json, {r['dashboard_id']}_csv.csv, {r['dashboard_id']}_queries.sql")
        print(f"     Location: {r['output_dir']}/")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(results)}")
        for r in failed:
            print(f"   - Dashboard {r['dashboard_id']}: {r['error']}")
    
    total_charts = sum(r['num_charts'] for r in successful)
    print(f"\n📊 Total charts extracted: {total_charts}")
    print(f"📁 Files created: {len(successful) * 3} files ({len(successful)} dashboards × 3 files each)")
    print("="*80)
    
    return results


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Extract dashboard metadata for multiple dashboards (using query_extract.py)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script uses query_extract.py to extract dashboard metadata.
For each dashboard, it creates:
  - {dashboard_id}_json.json
  - {dashboard_id}_csv.csv
  - {dashboard_id}_queries.sql

Examples:
  # Extract metadata for specific dashboards
  python bulk_json_extract.py --dashboard-ids 511 729 842
  
  # Extract with custom output directory
  python bulk_json_extract.py --dashboard-ids 511 729 --output-dir custom_output
  
  # Extract from file with dashboard IDs (one per line)
  python bulk_json_extract.py --dashboard-ids-file dashboard_ids.txt
        """
    )
    
    parser.add_argument(
        '--dashboard-ids',
        type=int,
        nargs='+',
        help='List of dashboard IDs to extract (e.g., 511 729 842)'
    )
    
    parser.add_argument(
        '--dashboard-ids-file',
        type=str,
        help='File containing dashboard IDs (one per line)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help=f'Base output directory (default: {DEFAULT_OUTPUT_DIR})'
    )
    
    args = parser.parse_args()
    
    # Get dashboard IDs
    dashboard_ids = []
    
    if args.dashboard_ids:
        dashboard_ids = args.dashboard_ids
    elif args.dashboard_ids_file:
        if not os.path.exists(args.dashboard_ids_file):
            print(f"❌ Error: File not found: {args.dashboard_ids_file}")
            sys.exit(1)
        
        with open(args.dashboard_ids_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        dashboard_ids.append(int(line))
                    except ValueError:
                        print(f"⚠️  Warning: Skipping invalid dashboard ID: {line}")
    else:
        parser.print_help()
        print("\n❌ Error: Must provide either --dashboard-ids or --dashboard-ids-file")
        sys.exit(1)
    
    if not dashboard_ids:
        print("❌ Error: No valid dashboard IDs provided")
        sys.exit(1)
    
    # Extract dashboard metadata
    results = extract_multiple_dashboards(
        dashboard_ids=dashboard_ids,
        output_base_dir=args.output_dir
    )
    
    # Exit with error code if any extractions failed
    if any(not r['success'] for r in results):
        sys.exit(1)


if __name__ == '__main__':
    main()

