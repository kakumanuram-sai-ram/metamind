"""
Starburst Schema Fetcher

This module normalizes table names and fetches schema information (DESCRIBE)
from Starburst/Trino using direct connection.

It processes tables extracted from DSPy calls and returns a consolidated
DataFrame with table schema information.
"""
import pandas as pd
from trino.dbapi import connect
from trino.auth import BasicAuthentication
from typing import List, Dict, Set, Optional
import re


def normalize_table_name(table_name: str) -> str:
    """
    Normalize table name to hive.db_name.table_name format
    
    Handles formats:
    - hive.db_name.table_name -> hive.db_name.table_name (already normalized)
    - db_name.table_name -> hive.db_name.table_name
    - "hive"."db_name"."table_name" -> hive.db_name.table_name
    - "db_name"."table_name" -> hive.db_name.table_name
    
    Args:
        table_name: Table name in various formats
        
    Returns:
        Normalized table name in format: hive.db_name.table_name
    """
    if not table_name:
        return table_name
    
    # Remove quotes if present
    table_name = table_name.strip().strip('"')
    
    # Split by dots (handle quoted identifiers)
    parts = re.split(r'\.', table_name)
    parts = [p.strip().strip('"') for p in parts if p.strip()]
    
    if len(parts) == 0:
        return table_name
    
    # Case 1: Already has 3 parts (catalog.schema.table)
    if len(parts) == 3:
        catalog, schema, table = parts[0], parts[1], parts[2]
        # If catalog is not 'hive', normalize it
        if catalog.lower() != 'hive':
            return f"hive.{schema}.{table}"
        return f"{catalog}.{schema}.{table}"
    
    # Case 2: Has 2 parts (schema.table) - add 'hive' as catalog
    elif len(parts) == 2:
        schema, table = parts[0], parts[1]
        return f"hive.{schema}.{table}"
    
    # Case 3: Has 1 part (just table name) - can't normalize without schema
    elif len(parts) == 1:
        # Return as is, but log warning
        print(f"Warning: Table name '{table_name}' has only one part, cannot normalize")
        return table_name
    
    # Case 4: More than 3 parts - take last 3
    else:
        catalog, schema, table = parts[-3], parts[-2], parts[-1]
        if catalog.lower() != 'hive':
            return f"hive.{schema}.{table}"
        return f"{catalog}.{schema}.{table}"


def get_unique_tables_from_dspy_results(dspy_results: List[Dict]) -> Set[str]:
    """
    Extract unique table names from DSPy extraction results
    
    Args:
        dspy_results: List of dicts from extract_source_tables_columns_llm
                     Each dict has 'tables_involved' key
        
    Returns:
        Set of unique normalized table names
    """
    unique_tables = set()
    
    for result in dspy_results:
        table_name = result.get('tables_involved', '')
        if table_name:
            normalized = normalize_table_name(table_name)
            unique_tables.add(normalized)
    
    return unique_tables


def get_starburst_connection(user_email: str = "kakumanu.ram@paytm.com"):
    """
    Create Starburst/Trino connection
    
    Args:
        user_email: User email for authentication
        
    Returns:
        Connection object
    """
    return connect(
        host="https://cdp-dashboarding.platform.mypaytm.com",
        port=443,
        user=user_email,
        catalog='hive'
    )


def describe_table(conn, table_name: str) -> Optional[pd.DataFrame]:
    """
    Execute DESCRIBE query on a table and return results as DataFrame
    
    Args:
        conn: Starburst connection object
        table_name: Table name in format hive.schema.table
        
    Returns:
        DataFrame with columns: Column, Type, Extra, Comment
        Returns None if query fails
    """
    try:
        # Parse table name to get catalog, schema, table
        parts = table_name.split('.')
        if len(parts) != 3:
            print(f"Error: Invalid table name format: {table_name}")
            return None
        
        catalog, schema, table = parts
        
        # Build DESCRIBE query
        # Use quoted identifiers to handle special characters
        query = f'DESCRIBE "{catalog}"."{schema}"."{table}"'
        
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print(f"Warning: No results for DESCRIBE {table_name}")
            return None
        
        # Get column names from cursor description
        columns = [desc[0] for desc in cursor.description]
        result_df = pd.DataFrame(results, columns=columns)
        
        cursor.close()
        
        return result_df
        
    except Exception as e:
        print(f"Error describing table {table_name}: {str(e)}")
        return None


def fetch_schemas_for_tables(
    table_names: List[str],
    user_email: str = "kakumanu.ram@paytm.com",
    normalize: bool = True
) -> pd.DataFrame:
    """
    Fetch schema information (DESCRIBE) for multiple tables
    
    Args:
        table_names: List of table names (can be in various formats)
        user_email: User email for Starburst authentication
        normalize: Whether to normalize table names (default: True)
        
    Returns:
        DataFrame with columns:
        - table_name: Normalized table name (hive.schema.table)
        - column_name: Column name from DESCRIBE
        - column_datatype: Data type from DESCRIBE
        - extra: Extra information (e.g., partition info)
        - comment: Column comment
    """
    # Normalize table names
    if normalize:
        normalized_tables = [normalize_table_name(t) for t in table_names]
    else:
        normalized_tables = table_names
    
    # Remove duplicates while preserving order
    unique_tables = []
    seen = set()
    for table in normalized_tables:
        if table and table not in seen:
            unique_tables.append(table)
            seen.add(table)
    
    print(f"Fetching schemas for {len(unique_tables)} unique tables...")
    
    # Create connection
    conn = get_starburst_connection(user_email)
    
    all_results = []
    
    try:
        for i, table_name in enumerate(unique_tables, 1):
            print(f"  [{i}/{len(unique_tables)}] Describing {table_name}...")
            
            df = describe_table(conn, table_name)
            
            if df is not None and not df.empty:
                # Standardize column names
                # Trino/Starburst DESCRIBE typically returns: Column, Type, Extra, Comment (in that order)
                column_mapping = {}
                
                # Map common variations (case-insensitive)
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['column', 'col_name', 'name', 'col']:
                        column_mapping[col] = 'column_name'
                    elif col_lower in ['type', 'data_type', 'datatype', 'data type']:
                        column_mapping[col] = 'column_datatype'
                    elif col_lower in ['extra', 'extras', 'extra info']:
                        column_mapping[col] = 'extra'
                    elif col_lower in ['comment', 'comments', 'description']:
                        column_mapping[col] = 'comment'
                
                # Rename columns
                if column_mapping:
                    df = df.rename(columns=column_mapping)
                
                # If column names still don't match, use positional mapping
                # Trino DESCRIBE returns columns in order: Column, Type, Extra, Comment
                expected_cols = ['column_name', 'column_datatype', 'extra', 'comment']
                for i, expected_col in enumerate(expected_cols):
                    if expected_col not in df.columns and i < len(df.columns):
                        # Rename the i-th column to expected_col
                        current_col = df.columns[i]
                        if current_col not in expected_cols:  # Don't rename if already correct
                            df = df.rename(columns={current_col: expected_col})
                
                # Add table_name column
                df['table_name'] = table_name
                
                # Ensure all required columns exist
                required_cols = ['table_name', 'column_name', 'column_datatype', 'extra', 'comment']
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = None
                
                # Select only required columns in correct order
                df = df[required_cols]
                
                all_results.append(df)
            else:
                print(f"    Warning: Could not describe {table_name}")
        
        # Combine all results
        if all_results:
            final_df = pd.concat(all_results, ignore_index=True)
            print(f"\n✅ Successfully fetched schemas for {len(final_df)} columns from {len(unique_tables)} tables")
            return final_df
        else:
            print("\n⚠️  No schema information retrieved")
            return pd.DataFrame(columns=['table_name', 'column_name', 'column_datatype', 'extra', 'comment'])
            
    finally:
        conn.close()


def process_dspy_extraction_results(
    dspy_results: List[Dict],
    user_email: str = "kakumanu.ram@paytm.com"
) -> pd.DataFrame:
    """
    Main function to process DSPy extraction results and fetch table schemas
    
    This function:
    1. Extracts unique table names from DSPy results
    2. Normalizes them to hive.schema.table format
    3. Fetches DESCRIBE information for each table
    4. Returns consolidated DataFrame
    
    Args:
        dspy_results: List of dicts from extract_source_tables_columns_llm
                     Each dict should have 'tables_involved' key
        user_email: User email for Starburst authentication
        
    Returns:
        DataFrame with columns:
        - table_name: Normalized table name (hive.schema.table)
        - column_name: Column name
        - column_datatype: Data type
        - extra: Extra information
        - comment: Column comment
    """
    print("Processing DSPy extraction results...")
    
    # Extract unique tables
    unique_tables = get_unique_tables_from_dspy_results(dspy_results)
    
    if not unique_tables:
        print("No tables found in DSPy results")
        return pd.DataFrame(columns=['table_name', 'column_name', 'column_datatype', 'extra', 'comment'])
    
    print(f"Found {len(unique_tables)} unique tables:")
    for table in sorted(unique_tables):
        print(f"  - {table}")
    
    # Fetch schemas
    return fetch_schemas_for_tables(list(unique_tables), user_email, normalize=False)


# Example usage
if __name__ == "__main__":
    # Example DSPy results format
    example_dspy_results = [
        {
            'tables_involved': 'user_paytm_payments.upi_tracker_insight',
            'column_names': 'day_id',
            'alias_column_name': 'day_id',
            'source_or_derived': 'source',
            'derived_column_logic': 'NA'
        },
        {
            'tables_involved': 'hive.user_paytm_payments.upi_tracker_insight_cm',
            'column_names': 'segment',
            'alias_column_name': 'segment',
            'source_or_derived': 'source',
            'derived_column_logic': 'NA'
        }
    ]
    
    # Process and fetch schemas
    schema_df = process_dspy_extraction_results(example_dspy_results)
    print("\nSchema DataFrame:")
    print(schema_df.head(20))

