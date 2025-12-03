"""
Golden Dataset Viewer

A utility script to view the golden dataset in a readable format.
"""

import pandas as pd
import sys
import os


def view_golden_dataset(csv_path: str, num_rows: int = None):
    """
    View golden dataset in a readable format.
    
    Args:
        csv_path: Path to the golden dataset CSV file
        num_rows: Number of rows to display (None for all)
    """
    if not os.path.exists(csv_path):
        print(f"❌ Error: File not found: {csv_path}")
        sys.exit(1)
    
    # Load the dataset
    df = pd.read_csv(csv_path)
    
    print(f"\n{'='*80}")
    print(f"📊 Golden Dataset: {os.path.basename(csv_path)}")
    print(f"{'='*80}")
    print(f"Total Entries: {len(df)}")
    print(f"Columns: {', '.join(df.columns.tolist())}")
    print(f"{'='*80}\n")
    
    # Display rows
    rows_to_show = df.head(num_rows) if num_rows else df
    
    for idx, row in rows_to_show.iterrows():
        print(f"{'─'*80}")
        print(f"Entry {idx + 1}/{len(df)}")
        print(f"{'─'*80}")
        print(f"Dashboard ID: {row['dashboard_id']}")
        print(f"Chart ID: {row['chart_id']}")
        print(f"Chart Name: {row['chart_name']}")
        print(f"\n📝 User Query:")
        print(f"  {row['user_query']}")
        print(f"\n💾 SQL Query:")
        sql_preview = row['sql_query'][:500] + "..." if len(row['sql_query']) > 500 else row['sql_query']
        for line in sql_preview.split('\n'):
            print(f"  {line}")
        print()
    
    if num_rows and len(df) > num_rows:
        print(f"{'─'*80}")
        print(f"... and {len(df) - num_rows} more entries")
        print(f"{'─'*80}\n")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="View golden dataset in readable format")
    parser.add_argument(
        'csv_file',
        help='Path to golden dataset CSV file (e.g., extracted_meta/golden_dataset/golden_dataset_964.csv)'
    )
    parser.add_argument(
        '--rows', '-n',
        type=int,
        help='Number of rows to display (default: all)'
    )
    
    args = parser.parse_args()
    
    view_golden_dataset(args.csv_file, args.rows)


if __name__ == "__main__":
    main()



