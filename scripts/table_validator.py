"""
Table Validator - Validate tables against actual database schemas using SHOW TABLES

Uses trino.dbapi to:
1. First validate schemas exist using SHOW SCHEMAS
2. Then run SHOW TABLES for each valid schema to validate table existence
3. If SHOW TABLES times out, fall back to DESCRIBE for individual tables
"""
from typing import List, Dict, Set, Tuple
import logging
import pandas as pd
from trino.dbapi import connect

logger = logging.getLogger(__name__)


def parse_table_components(table_name: str) -> Dict[str, str]:
    """
    Parse table name into catalog, schema, and table components.
    
    Args:
        table_name: Full table name (e.g., 'hive.user_paytm_payments.bank_link')
    
    Returns:
        Dict with 'catalog', 'schema', 'table' keys
    """
    parts = table_name.split('.')
    if len(parts) == 3:
        return {
            'catalog': parts[0],
            'schema': parts[1],
            'table': parts[2]
        }
    return None


def get_valid_schemas(conn, catalog: str) -> Set[str]:
    """
    Get all valid schemas in a catalog using SHOW SCHEMAS.
    
    Args:
        conn: Trino connection
        catalog: Catalog name (e.g., 'hive')
    
    Returns:
        Set of schema names
    """
    try:
        query = f'SHOW SCHEMAS FROM "{catalog}"'
        print(f"\n  🔍 Running: SHOW SCHEMAS FROM \"{catalog}\"")
        logger.info(f"Running: {query}")
        
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        
        # Results come back as single column with schema names
        schemas = set()
        for row in results:
            schema_name = row[0]  # First column is schema name
            schemas.add(schema_name)
        
        print(f"     ✅ Found {len(schemas)} schemas in catalog \"{catalog}\"")
        logger.info(f"Found {len(schemas)} schemas in {catalog}")
        
        return schemas
        
    except Exception as e:
        print(f"     ❌ Error querying schemas in catalog \"{catalog}\": {e}")
        logger.error(f"Error querying schemas in {catalog}: {e}")
        return set()


def validate_table_with_describe(conn, catalog: str, schema: str, table: str) -> bool:
    """
    Validate a single table using DESCRIBE.
    
    Args:
        conn: Trino connection
        catalog: Catalog name
        schema: Schema name
        table: Table name
    
    Returns:
        True if table exists, False otherwise
    """
    try:
        query = f'DESCRIBE "{catalog}"."{schema}"."{table}"'
        logger.debug(f"Running DESCRIBE: {query}")
        
        cursor = conn.cursor()
        cursor.execute(query)
        # If DESCRIBE succeeds, table exists
        cursor.fetchall()  # Consume results
        cursor.close()
        
        return True
        
    except Exception as e:
        # Table doesn't exist or other error
        logger.debug(f"DESCRIBE failed for {catalog}.{schema}.{table}: {e}")
        return False


def get_tables_in_schema(conn, catalog: str, schema: str, fallback_tables: List[str] = None) -> Set[str]:
    """
    Get all tables in a specific schema using SHOW TABLES.
    Falls back to DESCRIBE for individual tables if SHOW TABLES times out.
    
    Args:
        conn: Trino connection
        catalog: Catalog name (e.g., 'hive')
        schema: Schema name (e.g., 'user_paytm_payments')
        fallback_tables: List of table names to check individually if SHOW TABLES fails
    
    Returns:
        Set of full table names (e.g., 'hive.user_paytm_payments.bank_link')
    """
    try:
        query = f'SHOW TABLES FROM "{catalog}"."{schema}"'
        print(f"    🔍 Running: SHOW TABLES FROM \"{catalog}\".\"{schema}\"")
        logger.info(f"Running: {query}")
        
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        
        # Results come back as single column with table names
        tables = set()
        for row in results:
            table_name = row[0]  # First column is table name
            full_table_name = f"{catalog}.{schema}.{table_name}"
            tables.add(full_table_name)
        
        print(f"       ✅ Found {len(tables)} tables in \"{catalog}\".\"{schema}\"")
        logger.info(f"Found {len(tables)} tables in {catalog}.{schema}")
        
        return tables
        
    except Exception as e:
        error_msg = str(e)
        
        # Check if it's a timeout error
        if "SocketTimeoutException" in error_msg or "Read timed out" in error_msg:
            print(f"       ⚠️  SHOW TABLES timed out for \"{catalog}\".\"{schema}\"")
            print(f"          Schema has too many tables, falling back to DESCRIBE method...")
            logger.warning(f"SHOW TABLES timed out for {catalog}.{schema}, using DESCRIBE fallback")
            
            # Fall back to checking individual tables with DESCRIBE
            if fallback_tables:
                print(f"          🔍 Validating {len(fallback_tables)} tables individually using DESCRIBE...")
                valid_tables = set()
                
                for i, table_name in enumerate(fallback_tables, 1):
                    if validate_table_with_describe(conn, catalog, schema, table_name):
                        full_table_name = f"{catalog}.{schema}.{table_name}"
                        valid_tables.add(full_table_name)
                        print(f"             {i}/{len(fallback_tables)} ✓ {table_name}")
                    else:
                        print(f"             {i}/{len(fallback_tables)} ✗ {table_name}")
                
                print(f"       ✅ DESCRIBE validation: {len(valid_tables)}/{len(fallback_tables)} tables exist")
                logger.info(f"DESCRIBE validation: {len(valid_tables)}/{len(fallback_tables)} tables exist in {catalog}.{schema}")
                
                return valid_tables
            else:
                print(f"       ⚠️  No fallback tables provided, marking all as invalid")
                return set()
        else:
            # Other error (not timeout)
            print(f"       ⚠️  Error querying schema \"{catalog}\".\"{schema}\": {e}")
            logger.warning(f"Error querying schema {catalog}.{schema}: {e}")
            return set()


def validate_tables(table_list: List[str], user_email: str = "kakumanu.ram@paytm.com") -> List[str]:
    """
    Validate tables by:
    1. First checking which schemas exist (SHOW SCHEMAS)
    2. Then running SHOW TABLES for each valid schema
    3. If SHOW TABLES times out, use DESCRIBE for individual tables
    
    Args:
        table_list: List of table names to validate
        user_email: User email for Trino connection
    
    Returns:
        List of valid table names
    """
    valid_tables, _ = validate_tables_with_confidence(table_list, user_email)
    return valid_tables


def validate_tables_with_confidence(table_list: List[str], user_email: str = "kakumanu.ram@paytm.com") -> Tuple[List[str], float]:
    """
    Validate tables and return confidence score.
    
    Args:
        table_list: List of table names to validate
        user_email: User email for Trino connection
    
    Returns:
        Tuple of (valid_table_list, confidence_score)
        confidence_score = len(valid_tables) / len(table_list)
    """
    if not table_list:
        return ([], 0.0)
    
    # Get unique table names
    unique_tables = list(set(table_list))
    
    print(f"🔍 Validating {len(unique_tables)} unique tables...")
    logger.info(f"Validating {len(unique_tables)} unique tables")
    
    # Parse tables to get unique schemas and group tables by schema
    schema_tables_map = {}  # Map of schema -> list of table names
    table_components = {}
    
    for table in unique_tables:
        components = parse_table_components(table)
        if components:
            schema_name = components['schema']
            table_name = components['table']
            
            if schema_name not in schema_tables_map:
                schema_tables_map[schema_name] = []
            schema_tables_map[schema_name].append(table_name)
            
            table_components[table] = components
    
    schemas_to_check = set(schema_tables_map.keys())
    
    print(f"  📊 Found {len(schemas_to_check)} unique schemas extracted from tables:")
    for schema in sorted(schemas_to_check):
        table_count = len(schema_tables_map[schema])
        print(f"     - {schema} ({table_count} tables)")
    
    logger.info(f"Found {len(schemas_to_check)} unique schemas: {schemas_to_check}")
    
    try:
        # Connect to Trino
        print(f"\n  🔌 Connecting to Trino...")
        print(f"     Host: cdp-dashboarding.platform.mypaytm.com:443")
        print(f"     User: {user_email}")
        print(f"     Catalog: hive")
        
        conn = connect(
            host="cdp-dashboarding.platform.mypaytm.com",
            port=443,
            user=user_email,
            catalog='hive',
            http_scheme='https'
        )
        
        print(f"     ✅ Connected successfully")
        
        # Step 1: Get all valid schemas in hive catalog
        print(f"\n  📋 Step 1: Verify which schemas exist in catalog")
        print(f"  " + "─"*76)
        
        all_valid_schemas = get_valid_schemas(conn, 'hive')
        
        # Filter our schemas to only those that exist
        valid_schemas_to_check = schemas_to_check & all_valid_schemas
        invalid_schemas = schemas_to_check - all_valid_schemas
        
        print(f"\n     📊 Schema Validation Results:")
        print(f"        ✅ Valid schemas (will check tables): {len(valid_schemas_to_check)}")
        if valid_schemas_to_check:
            for schema in sorted(valid_schemas_to_check):
                table_count = len(schema_tables_map[schema])
                print(f"           - {schema} ({table_count} tables to verify)")
        
        if invalid_schemas:
            print(f"\n        ❌ Invalid schemas (will skip): {len(invalid_schemas)}")
            for schema in sorted(invalid_schemas):
                print(f"           - {schema}")
        
        # Step 2: Get all valid tables from valid schemas
        print(f"\n  📋 Step 2: Check tables in each valid schema")
        print(f"  " + "─"*76)
        
        all_valid_tables = set()
        
        if valid_schemas_to_check:
            print()
            for schema_name in sorted(valid_schemas_to_check):
                # Pass the list of tables to check as fallback for DESCRIBE
                fallback_table_names = schema_tables_map[schema_name]
                schema_tables = get_tables_in_schema(conn, 'hive', schema_name, fallback_table_names)
                all_valid_tables.update(schema_tables)
                print()  # Empty line between schemas
        else:
            print("     ⚠️  No valid schemas to check!\n")
        
        # Step 3: Find which of our extracted tables are valid
        valid_tables = []
        invalid_tables = []
        
        for table in unique_tables:
            if table in all_valid_tables:
                valid_tables.append(table)
            else:
                invalid_tables.append(table)
        
        # Summary
        print(f"  📊 Final Validation Summary:")
        print(f"     ✅ Valid tables: {len(valid_tables)}")
        print(f"     ❌ Invalid tables: {len(invalid_tables)}")
        
        logger.info(f"Validation complete: {len(valid_tables)} valid, {len(invalid_tables)} invalid")
        
        if invalid_tables:
            logger.debug(f"Invalid tables: {invalid_tables}")
        
        # Calculate confidence score
        confidence = len(valid_tables) / len(unique_tables) if unique_tables else 0.0
        
        return valid_tables, confidence
        
    except Exception as e:
        logger.error(f"Error validating tables: {e}")
        print(f"  ❌ Error validating tables: {e}")
        raise


def get_validation_feedback(
    table_list: List[str],
    valid_tables: List[str]
) -> str:
    """
    Generate feedback for reflexion if tables are invalid.
    
    Args:
        table_list: Original list of table names
        valid_tables: List of valid table names
    
    Returns:
        Feedback string for reflexion prompt, empty if all valid
    """
    invalid = set(table_list) - set(valid_tables)
    
    if not invalid:
        return ""
    
    return f"These tables don't exist in database: {list(invalid)}. Please re-scan SQL query for correct table names or check for typos."
