"""
Trino API Client to get column data types from tables
"""
import requests
import json
from typing import Dict, List, Optional
from config import BASE_URL, HEADERS


class TrinoClient:
    """Client to query Trino for table schema information via Superset API"""
    
    def __init__(self, base_url: str, headers: Dict):
        self.base_url = base_url
        self.headers = headers
        # Use Superset's SQL Lab endpoint to execute queries
        self.query_endpoint = f"{base_url}/api/v1/sqllab/execute/"
    
    def get_table_columns(self, table_name: str, database_id: int = 1) -> Dict[str, str]:
        """
        Get column names and data types for a table using DESCRIBE query
        
        Args:
            table_name: Table name in format "catalog"."schema"."table" or catalog.schema.table
            database_id: Database ID in Superset (default: 1 for Trino)
            
        Returns:
            Dict mapping column_name -> data_type
        """
        # Parse table name
        if table_name.startswith('"'):
            # Quoted format: "catalog"."schema"."table"
            parts = [p.strip('"') for p in table_name.split('"."')]
        else:
            # Unquoted format: catalog.schema.table
            parts = table_name.split('.')
        
        if len(parts) < 3:
            return {}
        
        catalog, schema, table = parts[0], parts[1], parts[2]
        
        # Build DESCRIBE query - use unquoted format for Trino
        query = f'DESCRIBE {catalog}.{schema}.{table}'
        
        try:
            # Use Superset's SQL Lab execute endpoint
            response = requests.post(
                self.query_endpoint,
                headers={
                    **self.headers,
                    'Content-Type': 'application/json',
                    'Referer': f'{self.base_url}/superset/sqllab/',
                    'Origin': self.base_url
                },
                json={
                    "database_id": database_id,
                    "sql": query,
                    "client_id": "trino_schema_query",
                    "queryLimit": 1000,
                    "schema": schema,
                    "runAsync": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                columns = {}
                
                # Parse the result - format depends on Superset version
                if 'data' in data:
                    result_data = data['data']
                    for row in result_data:
                        if isinstance(row, (list, tuple)) and len(row) >= 2:
                            col_name = str(row[0])
                            col_type = str(row[1])
                            columns[col_name] = col_type
                        elif isinstance(row, dict):
                            # Try different possible keys
                            col_name = row.get('Column', row.get('column_name', row.get('name', '')))
                            col_type = row.get('Type', row.get('data_type', row.get('type', '')))
                            if col_name:
                                columns[col_name] = col_type
                
                return columns
            else:
                print(f"Error querying Trino for {table_name}: {response.status_code} - {response.text[:200]}")
                return {}
        except Exception as e:
            print(f"Exception querying Trino for {table_name}: {str(e)}")
            return {}
    
    def get_columns_for_tables(self, table_names: List[str], database_id: int = 1) -> Dict[str, Dict[str, str]]:
        """
        Get columns for multiple tables
        
        Args:
            table_names: List of table names
            database_id: Database ID in Superset
            
        Returns:
            Dict mapping table_name -> {column_name: data_type}
        """
        result = {}
        print(f"Querying Trino for {len(table_names)} tables...")
        for i, table_name in enumerate(table_names, 1):
            print(f"  [{i}/{len(table_names)}] Getting columns for {table_name}...")
            columns = self.get_table_columns(table_name, database_id)
            if columns:
                result[table_name] = columns
                print(f"    Found {len(columns)} columns")
            else:
                print(f"    No columns found")
        return result


def get_column_datatypes_from_trino(dashboard_info: Dict, base_url: str = None, headers: Dict = None) -> Dict[str, Dict[str, str]]:
    """
    Get data types for all columns used in dashboard from Trino
    
    Args:
        dashboard_info: Dashboard info dict
        base_url: Superset base URL (defaults to config.BASE_URL)
        headers: Authentication headers (defaults to config.HEADERS)
        
    Returns:
        Dict mapping table_name -> {column_name: data_type}
    """
    from sql_parser import SQLParser, normalize_table_name
    
    if base_url is None:
        base_url = BASE_URL
    if headers is None:
        headers = HEADERS
    
    # Extract unique table names from all charts
    parser = SQLParser()
    unique_tables = set()
    
    charts = dashboard_info.get('charts', [])
    for chart in charts:
        sql_query = chart.get('sql_query')
        if sql_query:
            parsed = parser.parse_chart_sql(sql_query)
            for table in parsed['tables']:
                normalized_table = normalize_table_name(table)
                unique_tables.add(normalized_table)
    
    if not unique_tables:
        return {}
    
    # Query Trino for each table (fail gracefully if errors occur)
    try:
        trino_client = TrinoClient(base_url, headers)
        table_columns = trino_client.get_columns_for_tables(list(unique_tables))
        return table_columns
    except Exception as e:
        print(f"Warning: Trino query failed, continuing without data types: {str(e)}")
        return {}

