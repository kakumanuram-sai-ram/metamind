"""
Example usage of starburst_schema_fetcher

This script demonstrates how to use the schema fetcher with DSPy extraction results.
"""
import os
import sys
# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

from starburst_schema_fetcher import (
    process_dspy_extraction_results,
    fetch_schemas_for_tables,
    normalize_table_name,
    get_unique_tables_from_dspy_results
)
from llm_extractor import extract_source_tables_columns_llm
import json


def example_1_normalize_tables():
    """Example: Normalize table names"""
    print("=" * 60)
    print("Example 1: Normalizing Table Names")
    print("=" * 60)
    
    test_tables = [
        "user_paytm_payments.upi_tracker_insight",
        "hive.user_paytm_payments.upi_tracker_insight_cm",
        '"hive"."user_paytm_payments"."upi_tracker_insight"',
        '"user_paytm_payments"."upi_tracker_insight"',
        "upi_tracker_insight"  # Can't normalize without schema
    ]
    
    for table in test_tables:
        normalized = normalize_table_name(table)
        print(f"  {table:50} -> {normalized}")


def example_2_fetch_schemas():
    """Example: Fetch schemas for specific tables"""
    print("\n" + "=" * 60)
    print("Example 2: Fetching Schemas for Tables")
    print("=" * 60)
    
    # List of tables to describe
    tables = [
        "hive.user_paytm_payments.upi_tracker_insight",
        "hive.user_paytm_payments.upi_tracker_insight_cm"
    ]
    
    # Fetch schemas
    schema_df = fetch_schemas_for_tables(tables)
    
    print(f"\nRetrieved {len(schema_df)} columns:")
    print(schema_df.head(20))
    
    return schema_df


def example_3_process_dspy_results():
    """Example: Process DSPy extraction results"""
    print("\n" + "=" * 60)
    print("Example 3: Processing DSPy Extraction Results")
    print("=" * 60)
    
    # Example DSPy results (format from extract_source_tables_columns_llm)
    dspy_results = [
        {
            'tables_involved': 'user_paytm_payments.upi_tracker_insight',
            'column_names': 'day_id',
            'alias_column_name': 'day_id',
            'source_or_derived': 'source',
            'derived_column_logic': 'NA'
        },
        {
            'tables_involved': 'user_paytm_payments.upi_tracker_insight',
            'column_names': 'segment',
            'alias_column_name': 'segment',
            'source_or_derived': 'source',
            'derived_column_logic': 'NA'
        },
        {
            'tables_involved': 'hive.user_paytm_payments.upi_tracker_insight_cm',
            'column_names': 'mau',
            'alias_column_name': 'mau',
            'source_or_derived': 'source',
            'derived_column_logic': 'NA'
        }
    ]
    
    # Process and fetch schemas
    schema_df = process_dspy_extraction_results(dspy_results)
    
    print(f"\nRetrieved schema for {len(schema_df)} columns from {schema_df['table_name'].nunique()} tables")
    print("\nSchema DataFrame:")
    print(schema_df)
    
    return schema_df


def example_4_integration_with_dspy():
    """Example: Full integration with DSPy extraction"""
    print("\n" + "=" * 60)
    print("Example 4: Integration with DSPy Extraction")
    print("=" * 60)
    
    # Load dashboard info (example)
    dashboard_id = 282
    json_file = f"extracted_meta/{dashboard_id}_json.json"
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            dashboard_info = json.load(f)
        
        # Extract tables and columns using DSPy
        print("Extracting tables and columns using DSPy...")
        api_key = "your-api-key-here"  # Replace with actual API key
        dspy_results = extract_source_tables_columns_llm(
            dashboard_info,
            api_key=api_key,
            model="claude-sonnet-4-20250514"
        )
        
        print(f"Found {len(dspy_results)} table-column mappings")
        
        # Process and fetch schemas
        schema_df = process_dspy_extraction_results(dspy_results)
        
        print(f"\nFinal schema DataFrame:")
        print(f"  - {len(schema_df)} total columns")
        print(f"  - {schema_df['table_name'].nunique()} unique tables")
        print(f"\nFirst 10 rows:")
        print(schema_df.head(10))
        
        # Save to CSV
        output_file = f"extracted_meta/{dashboard_id}_table_schemas.csv"
        schema_df.to_csv(output_file, index=False)
        print(f"\n✅ Saved schema information to {output_file}")
        
        return schema_df
        
    except FileNotFoundError:
        print(f"Dashboard JSON file not found: {json_file}")
        print("Skipping integration example")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    # Run examples
    example_1_normalize_tables()
    
    # Uncomment to run other examples (requires Starburst connection)
    # example_2_fetch_schemas()
    # example_3_process_dspy_results()
    # example_4_integration_with_dspy()

