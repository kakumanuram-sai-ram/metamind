#!/usr/bin/env python3
"""
Script to create knowledge_base_csv.zip from CSV and TXT files

This script:
1. Converts JSON files to CSV files (if needed)
2. Creates CSV files for business_context and validations (if needed)
3. Compresses all CSV/TXT files into knowledge_base_csv.zip

Files to include:
- business_context.csv
- column_metadata.csv
- definitions.csv
- filter_conditions.txt
- table_metadata.csv
- joining_conditions.csv
- validations.csv
"""

import os
import sys
import json
import zipfile
import pandas as pd
from pathlib import Path

# Get the metamind directory (parent of scripts directory)
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_metamind_dir = os.path.dirname(_scripts_dir)


def convert_json_to_csv(json_file: str, csv_file: str) -> bool:
    """
    Convert JSON file to CSV file.
    
    Args:
        json_file: Path to JSON file
        csv_file: Path to output CSV file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(json_file):
            print(f"  ⚠️  JSON file not found: {json_file}")
            return False
        
        # Read JSON file - handle potential JSON errors
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Try to fix common JSON issues (empty values)
                # Replace "key":  , with "key": null,
                import re
                content = re.sub(r':\s*,', ': null,', content)
                content = re.sub(r':\s*\]', ': null]', content)
                content = re.sub(r':\s*\}', ': null}', content)
                data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"  ⚠️  JSON parsing error in {json_file}: {str(e)}")
            print(f"     Attempting to read as pandas JSON...")
            # Try reading directly with pandas (more forgiving)
            try:
                df = pd.read_json(json_file)
                if len(df) > 0:
                    df.to_csv(csv_file, index=False, encoding='utf-8')
                    return True
                else:
                    create_empty_csv(csv_file)
                    return True
            except Exception as e2:
                print(f"  ❌ Pandas also failed: {str(e2)}")
                return False
        
        # Handle different JSON structures
        if isinstance(data, list):
            # List of dictionaries
            if len(data) == 0:
                # Create empty CSV with appropriate columns
                df = pd.DataFrame()
            else:
                df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Single dictionary - convert to DataFrame with one row
            if len(data) == 0:
                df = pd.DataFrame()
            else:
                df = pd.DataFrame([data])
        else:
            print(f"  ⚠️  Unsupported JSON structure in {json_file}")
            return False
        
        # Save as CSV
        if len(df) > 0:
            df.to_csv(csv_file, index=False, encoding='utf-8')
        else:
            # Create empty CSV file
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('')  # Empty file
        
        return True
    
    except Exception as e:
        print(f"  ❌ Error converting {json_file} to CSV: {str(e)}")
        return False


def create_empty_csv(csv_file: str, columns: list = None):
    """
    Create an empty CSV file with optional column headers.
    
    Args:
        csv_file: Path to output CSV file
        columns: List of column names (optional)
    """
    try:
        if columns:
            df = pd.DataFrame(columns=columns)
            df.to_csv(csv_file, index=False, encoding='utf-8')
        else:
            # Create completely empty file
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('')
    except Exception as e:
        print(f"  ❌ Error creating empty CSV {csv_file}: {str(e)}")


def create_kb_csv_zip():
    """
    Create knowledge_base_csv.zip from CSV and TXT files.
    """
    print("\n" + "="*80)
    print("CREATING KNOWLEDGE BASE CSV ZIP")
    print("="*80)
    
    # Set paths (absolute path from metamind directory)
    kb_dir = os.path.join(_metamind_dir, "extracted_meta", "knowledge_base")
    os.makedirs(kb_dir, exist_ok=True)
    
    print(f"Knowledge base directory: {kb_dir}")
    
    # Files to include in zip
    # Format: {output_filename: source_file_or_None}
    # If source_file is None, create empty file
    # If source_file ends with .txt, use it directly (no conversion needed)
    files_to_zip = {
        'business_context.csv': None,
        'column_metadata.csv': 'column_metadata.json',
        'definitions.csv': 'definitions.json',
        'filter_conditions.txt': 'filter_conditions.txt',  # TXT file, use directly
        'table_metadata.csv': 'table_metadata.json',
        'joining_conditions.csv': 'joining_conditions.json',
        'validations.csv': None
    }
    
    print("\n[Step 1] Converting JSON files to CSV (if needed)...")
    print("-" * 80)
    
    # Convert JSON files to CSV
    for csv_filename, source_file in files_to_zip.items():
        csv_path = os.path.join(kb_dir, csv_filename)
        
        if source_file:
            if source_file.endswith('.json'):
                # Convert JSON to CSV
                json_path = os.path.join(kb_dir, source_file)
                print(f"  Converting {source_file} → {csv_filename}...")
                success = convert_json_to_csv(json_path, csv_path)
                if success:
                    print(f"    ✅ Created: {csv_filename}")
                else:
                    print(f"    ⚠️  Failed to create: {csv_filename}")
            elif source_file.endswith('.txt'):
                # For TXT files, just use the existing file (filter_conditions.txt)
                txt_path = os.path.join(kb_dir, source_file)
                if os.path.exists(txt_path):
                    # File already exists, no need to copy (it's the same file)
                    print(f"  ✅ Found: {source_file}")
                else:
                    print(f"  ⚠️  File not found: {source_file}")
                    # Create empty file
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write('')
                    print(f"    Created empty: {source_file}")
        else:
            # Create empty CSV files for business_context and validations
            print(f"  Creating empty: {csv_filename}...")
            if csv_filename == 'business_context.csv':
                create_empty_csv(csv_path, columns=[])
            elif csv_filename == 'validations.csv':
                create_empty_csv(csv_path, columns=[])
            print(f"    ✅ Created: {csv_filename}")
    
    print("\n[Step 2] Creating knowledge_base_csv.zip...")
    print("-" * 80)
    
    # Create zip file
    zip_path = os.path.join(kb_dir, "knowledge_base_csv.zip")
    
    files_added = 0
    files_missing = []
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for output_filename, source_file in files_to_zip.items():
            # Determine the actual file path
            if source_file and source_file.endswith('.txt'):
                # For TXT files, use the source file directly
                file_path = os.path.join(kb_dir, source_file)
            else:
                # For CSV files, use the output filename
                file_path = os.path.join(kb_dir, output_filename)
            
            if os.path.exists(file_path):
                # Get file size to show progress
                file_size = os.path.getsize(file_path)
                # Use output_filename in zip (not source_file)
                zipf.write(file_path, output_filename)
                files_added += 1
                print(f"  ✅ Added {output_filename} ({file_size:,} bytes)")
            else:
                files_missing.append(output_filename)
                print(f"  ⚠️  File not found: {output_filename}")
    
    zip_size = os.path.getsize(zip_path)
    
    print("\n" + "="*80)
    print("KNOWLEDGE BASE CSV ZIP CREATION COMPLETE")
    print("="*80)
    print(f"✅ Zip file created: {zip_path}")
    print(f"   Zip file size: {zip_size:,} bytes ({zip_size / 1024:.2f} KB)")
    print(f"   Files added: {files_added}/{len(files_to_zip)}")
    
    if files_missing:
        print(f"\n⚠️  Missing files: {', '.join(files_missing)}")
    
    print("="*80)
    
    return zip_path


if __name__ == '__main__':
    try:
        zip_file = create_kb_csv_zip()
        print(f"\n✅ Success! Zip file: {zip_file}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

