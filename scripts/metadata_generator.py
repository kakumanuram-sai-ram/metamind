"""
Metadata Generator Module

This module generates comprehensive metadata files from extracted dashboard information:
- tables_metadata.csv: Table descriptions, refresh frequency, vertical, partition columns, relationships
- columns_metadata.csv: Column types, descriptions, required flags
- filter_conditions.txt: Filter conditions and SQL context
"""

import json
import os
import pandas as pd
from typing import Dict, List, Optional, Any
from trino_client import TrinoClient, get_column_datatypes_from_trino
from sql_parser import normalize_table_name
from config import BASE_URL, HEADERS, LLM_MODEL, LLM_BASE_URL


def detect_partition_columns(table_name: str, trino_client: TrinoClient, database_id: int = 1) -> Optional[str]:
    """
    Detect partition column for a table by querying Trino metadata
    
    Args:
        table_name: Full table name (catalog.schema.table)
        trino_client: TrinoClient instance
        database_id: Database ID for Superset API
        
    Returns:
        Partition column name if found, None otherwise
    """
    try:
        # Query SHOW PARTITIONS or DESCRIBE to find partition column
        # For Hive tables, partition columns are typically in table metadata
        columns = trino_client.get_table_columns(table_name, database_id)
        
        # Check if any column name suggests it's a partition column
        # Common patterns: dt, date, day_id, partition_date, etc.
        partition_keywords = ['dt', 'date', 'day_id', 'partition', 'partition_date', 'snapshot_date']
        
        for col_name in columns.keys():
            col_lower = col_name.lower()
            if any(keyword in col_lower for keyword in partition_keywords):
                # Additional check: if it's a date/timestamp type, more likely to be partition
                col_type = columns.get(col_name, '').lower()
                if 'date' in col_type or 'timestamp' in col_type:
                    return col_name
        
        return None
    except Exception as e:
        print(f"Error detecting partition column for {table_name}: {str(e)}")
        return None


def generate_tables_metadata(
    dashboard_info: Dict,
    api_key: str,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    headers: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Generate tables_metadata.csv with comprehensive table information
    
    Args:
        dashboard_info: Dashboard info dictionary
        api_key: Anthropic API key for LLM
        model: LLM model name (default: from config.LLM_MODEL)
        base_url: Superset base URL (default: from config.BASE_URL)
        headers: Authentication headers (default: from config.HEADERS)
        
    Returns:
        DataFrame with table metadata
    """
    # Use defaults from config if not provided
    model = model or LLM_MODEL
    base_url = base_url or BASE_URL
    headers = headers or HEADERS
    import dspy
    
    if base_url is None:
        base_url = BASE_URL
    if headers is None:
        headers = HEADERS
    
    # Extract tables and columns using LLM
    print("Extracting tables and columns using LLM...")
    from llm_extractor import DashboardTableColumnExtractor
    extractor = DashboardTableColumnExtractor(api_key=api_key, model=model)
    table_column_mapping = extractor.extract_from_dashboard(dashboard_info)
    
    # Get unique tables
    unique_tables = set()
    table_context = {}  # Store context for each table
    for item in table_column_mapping:
        table_name = item['table_name']
        unique_tables.add(table_name)
        if table_name not in table_context:
            table_context[table_name] = {
                'columns': [],
                'chart_ids': set()
            }
        if item.get('column_name'):
            table_context[table_name]['columns'].append(item['column_name'])
        # Extract chart IDs from column_label__chart_json
        try:
            labels = json.loads(item.get('column_label__chart_json', '{}'))
            table_context[table_name]['chart_ids'].update(labels.keys())
        except:
            pass
    
    # Get column data types and partition info from Trino
    print("Fetching table schemas and partition information from Trino...")
    trino_columns = get_column_datatypes_from_trino(dashboard_info, base_url, headers)
    trino_client = TrinoClient(base_url, headers)
    
    # Generate table descriptions using LLM
    print("Generating table descriptions and metadata using LLM...")
    
    # Create DSPy signature for table metadata extraction
    class TableMetadataExtractor(dspy.Signature):
        """Extract comprehensive table metadata from dashboard context"""
        dashboard_title: str = dspy.InputField(desc="Dashboard title")
        table_name: str = dspy.InputField(desc="Full table name (catalog.schema.table)")
        columns_used: str = dspy.InputField(desc="Comma-separated list of columns used in this table")
        sql_queries: str = dspy.InputField(desc="SQL queries that use this table")
        chart_context: str = dspy.InputField(desc="Chart names and IDs that use this table")
        
        table_description: str = dspy.OutputField(desc="Comprehensive table description including purpose, use cases, and data categories")
        refresh_frequency: str = dspy.OutputField(desc="Expected refresh frequency (Daily, Weekly, Monthly, Real-time, etc.)")
        vertical: str = dspy.OutputField(desc="Business vertical (UPI, Lending, Insurance, etc.)")
        relationship_context: str = dspy.OutputField(desc="Relationships with other tables, join patterns, and usage context")
    
    # Configure DSPy
    lm = dspy.LM(model=model, api_key=api_key, api_provider="anthropic")
    dspy.configure(lm=lm)
    metadata_extractor = dspy.ChainOfThought(TableMetadataExtractor)
    
    tables_metadata = []
    charts = dashboard_info.get('charts', [])
    
    for table_name in sorted(unique_tables):
        # Collect SQL queries and chart context for this table
        table_sqls = []
        chart_names = []
        for chart in charts:
            sql_query = chart.get('sql_query', '')
            if sql_query and table_name.split('.')[-1].lower() in sql_query.lower():
                table_sqls.append(sql_query[:500])  # Limit length
                chart_names.append(f"{chart.get('chart_name', 'Unknown')} (ID: {chart.get('chart_id')})")
        
        context = table_context[table_name]
        columns_str = ', '.join(context['columns'][:10])  # Limit to first 10 columns
        
        # Detect partition column
        partition_column = detect_partition_columns(table_name, trino_client)
        
        try:
            # Use LLM to extract metadata
            result = metadata_extractor(
                dashboard_title=dashboard_info.get('dashboard_title', 'Unknown Dashboard'),
                table_name=table_name,
                columns_used=columns_str,
                sql_queries='\n---\n'.join(table_sqls[:3]),  # Limit to 3 queries
                chart_context='; '.join(chart_names[:5])  # Limit to 5 charts
            )
            
            tables_metadata.append({
                'table_name': table_name,
                'table_description': result.table_description,
                'refresh_frequency': result.refresh_frequency or 'Daily',
                'vertical': result.vertical or 'UPI',
                'partition_column': partition_column or '',
                'remarks': '',
                'relationship_context': result.relationship_context or ''
            })
        except Exception as e:
            print(f"Error extracting metadata for {table_name}: {str(e)}")
            # Fallback to basic metadata
            tables_metadata.append({
                'table_name': table_name,
                'table_description': f"Table used in dashboard: {dashboard_info.get('dashboard_title', 'Unknown')}. Columns: {columns_str[:200]}...",
                'refresh_frequency': 'Daily',
                'vertical': 'UPI',
                'partition_column': partition_column or '',
                'remarks': '',
                'relationship_context': ''
            })
    
    return pd.DataFrame(tables_metadata)


def generate_columns_metadata(
    dashboard_info: Dict,
    table_column_mapping: List[Dict],
    trino_columns: Dict[str, Dict[str, str]]
) -> pd.DataFrame:
    """
    Generate columns_metadata.csv with column information
    
    Args:
        dashboard_info: Dashboard info dictionary
        table_column_mapping: List of table-column mappings
        trino_columns: Dictionary of table -> {column: data_type}
        
    Returns:
        DataFrame with column metadata
    """
    columns_metadata = []
    
    for item in table_column_mapping:
        table_name = item['table_name']
        column_name = item.get('column_name', '')
        
        if not column_name:
            continue
        
        # Get data type from Trino
        normalized_table = normalize_table_name(table_name)
        data_type = None
        if normalized_table in trino_columns:
            data_type = trino_columns[normalized_table].get(column_name, 'varchar')
        elif table_name in trino_columns:
            data_type = trino_columns[table_name].get(column_name, 'varchar')
        else:
            data_type = 'varchar'  # Default
        
        # Extract column description from chart labels
        column_label_json = item.get('column_label__chart_json', '{}')
        try:
            labels = json.loads(column_label_json) if isinstance(column_label_json, str) else column_label_json
            # Use first non-empty label as description
            description = next((v for v in labels.values() if v), column_name)
        except:
            description = column_name
        
        columns_metadata.append({
            'table_name': table_name,
            'column_name': column_name,
            'variable_type': data_type or 'varchar',
            'column_description': description,
            'required_flag': 'no'  # Default, could be enhanced
        })
    
    # Remove duplicates
    seen = set()
    unique_columns = []
    for col in columns_metadata:
        key = (col['table_name'], col['column_name'])
        if key not in seen:
            seen.add(key)
            unique_columns.append(col)
    
    return pd.DataFrame(unique_columns)


def generate_filter_conditions(dashboard_info: Dict) -> str:
    """
    Generate filter_conditions.txt with SQL filter context
    
    Args:
        dashboard_info: Dashboard info dictionary
        
    Returns:
        String content for filter_conditions.txt
    """
    content = []
    
    charts = dashboard_info.get('charts', [])
    for chart in charts:
        chart_id = chart.get('chart_id')
        chart_name = chart.get('chart_name', 'Unknown')
        sql_query = chart.get('sql_query', '')
        
        if not sql_query:
            continue
        
        # Extract WHERE clause and filter conditions
        sql_upper = sql_query.upper()
        where_pos = sql_upper.find('WHERE')
        
        if where_pos > 0:
            # Extract WHERE clause
            where_clause = sql_query[where_pos:]
            # Try to find the end (GROUP BY, ORDER BY, LIMIT)
            for keyword in ['GROUP BY', 'ORDER BY', 'LIMIT', 'HAVING']:
                keyword_pos = sql_upper.find(keyword, where_pos)
                if keyword_pos > 0:
                    where_clause = sql_query[where_pos:keyword_pos]
                    break
            
            # Extract tables involved
            from_pos = sql_upper.find('FROM')
            if from_pos > 0:
                from_clause = sql_query[from_pos:where_pos]
                # Extract table names (simplified)
                tables = []
                for word in from_clause.split():
                    if '.' in word and word.upper() not in ['FROM', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'FULL']:
                        tables.append(word.strip(',').strip('(').strip(')'))
            
            content.append(f"## {chart_name} (Chart ID: {chart_id})")
            if tables:
                content.append(f"-- tables_involved")
                for table in tables[:3]:  # Limit to first 3 tables
                    content.append(f"{table}")
            
            # Add filter conditions
            content.append("--- standard filters to be applied unless specifically requested for a different categorical value")
            content.append(where_clause.strip())
            content.append("")
    
    return "\n".join(content)


def generate_all_metadata(
    dashboard_id: int,
    api_key: str,
    model: Optional[str] = None
):
    """
    Generate all metadata files for a dashboard
    
    Args:
        dashboard_id: Dashboard ID
        api_key: Anthropic API key
        model: LLM model name (default: from config.LLM_MODEL)
    """
    # Use default from config if not provided
    model = model or LLM_MODEL
    import os
    
    # Create extracted_meta directory
    os.makedirs("extracted_meta", exist_ok=True)
    
    # Load dashboard JSON
    json_file = f"extracted_meta/{dashboard_id}_json.json"
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Dashboard JSON file not found: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        dashboard_info = json.load(f)
    
    # Generate tables metadata
    print("Generating tables_metadata.csv...")
    tables_df = generate_tables_metadata(dashboard_info, api_key, model)
    tables_file = f"extracted_meta/{dashboard_id}_tables_metadata.csv"
    tables_df.to_csv(tables_file, index=False, sep='\t')
    print(f"Saved to {tables_file}")
    
    # Generate columns metadata
    print("Generating columns_metadata.csv...")
    from llm_extractor import DashboardTableColumnExtractor
    extractor = DashboardTableColumnExtractor(api_key=api_key, model=model)
    table_column_mapping = extractor.extract_from_dashboard(dashboard_info)
    trino_columns = get_column_datatypes_from_trino(dashboard_info, BASE_URL, HEADERS)
    columns_df = generate_columns_metadata(dashboard_info, table_column_mapping, trino_columns)
    columns_file = f"extracted_meta/{dashboard_id}_columns_metadata.csv"
    columns_df.to_csv(columns_file, index=False, sep='\t')
    print(f"Saved to {columns_file}")
    
    # Generate filter conditions
    print("Generating filter_conditions.txt...")
    filter_content = generate_filter_conditions(dashboard_info)
    filter_file = f"extracted_meta/{dashboard_id}_filter_conditions.txt"
    with open(filter_file, 'w', encoding='utf-8') as f:
        f.write(filter_content)
    print(f"Saved to {filter_file}")
    
    print("\n✅ All metadata files generated successfully!")

