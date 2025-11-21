"""
SQL Parser to extract tables and columns from Superset dashboard queries
"""
import re
import json
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict


class SQLParser:
    """Parse SQL queries to extract tables and columns"""
    
    def __init__(self):
        self.table_pattern = re.compile(
            r'(?:FROM|JOIN|INTO|UPDATE)\s+'
            r'(?:(\w+)\.)?(?:(\w+)\.)?(\w+)'  # catalog.db.table or db.table or table
            r'(?:\s+AS\s+\w+)?',  # Optional alias
            re.IGNORECASE
        )
        
        # Pattern to match quoted identifiers: "catalog"."db"."table"
        self.quoted_table_pattern = re.compile(
            r'(?:FROM|JOIN|INTO|UPDATE)\s+'
            r'(?:"([^"]+)"\.)?(?:"([^"]+)"\.)?("([^"]+)")'
            r'(?:\s+AS\s+\w+)?',
            re.IGNORECASE
        )
        
        # Pattern to match CTEs (Common Table Expressions)
        self.cte_pattern = re.compile(
            r'^\s*WITH\s+(\w+)\s+AS\s*\(',
            re.IGNORECASE | re.MULTILINE
        )
    
    def remove_comments(self, sql: str) -> str:
        """Remove SQL comments from query"""
        # Remove single-line comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        # Remove multi-line comments
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        return sql
    
    def extract_cte_names(self, sql: str) -> Set[str]:
        """Extract CTE (Common Table Expression) names to exclude them"""
        cte_names = set()
        # Find all CTEs
        matches = re.finditer(
            r'WITH\s+(\w+)\s+AS\s*\(',
            sql,
            re.IGNORECASE
        )
        for match in matches:
            cte_names.add(match.group(1).lower())
        
        # Also find recursive CTEs
        matches = re.finditer(
            r',\s*(\w+)\s+AS\s*\(',
            sql,
            re.IGNORECASE
        )
        for match in matches:
            cte_names.add(match.group(1).lower())
        
        return cte_names
    
    def extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL query, excluding CTEs"""
        if not sql:
            return []
        
        sql = self.remove_comments(sql)
        cte_names = self.extract_cte_names(sql)
        
        tables = []
        seen_tables = set()
        
        # Pattern for quoted tables: "catalog"."db"."table" or "db"."table" or "table"
        quoted_pattern = re.compile(
            r'(?:FROM|JOIN|INTO|UPDATE)\s+'
            r'((?:"[^"]+"\.)*"[^"]+")',
            re.IGNORECASE
        )
        
        # Pattern for unquoted tables: catalog.db.table or db.table or table
        unquoted_pattern = re.compile(
            r'(?:FROM|JOIN|INTO|UPDATE)\s+'
            r'((?:\w+\.)*\w+)',
            re.IGNORECASE
        )
        
        # Find quoted table names
        for match in quoted_pattern.finditer(sql):
            table_ref = match.group(1).strip()
            # Extract parts
            parts = [p.strip('"') for p in table_ref.split('.')]
            if len(parts) >= 1:
                table_name = parts[-1].lower()
                if table_name and table_name not in cte_names:
                    # Reconstruct with quotes
                    quoted_parts = [f'"{p}"' for p in parts]
                    full_table = '.'.join(quoted_parts)
                    if full_table not in seen_tables:
                        tables.append(full_table)
                        seen_tables.add(full_table)
        
        # Find unquoted table names (like hive.promocard.table)
        for match in unquoted_pattern.finditer(sql):
            table_ref = match.group(1).strip()
            parts = table_ref.split('.')
            if len(parts) >= 1:
                table_name = parts[-1].lower()
                if table_name and table_name not in cte_names:
                    # Check if it's not a keyword
                    if table_name not in ['select', 'where', 'group', 'order', 'having', 'limit', 'union', 'all']:
                        full_table = '.'.join(parts)
                        if full_table not in seen_tables:
                            tables.append(full_table)
                            seen_tables.add(full_table)
        
        return tables
    
    def extract_columns(self, sql: str, tables: List[str]) -> Dict[str, List[str]]:
        """Extract columns used from each table"""
        if not sql:
            return {}
        
        sql = self.remove_comments(sql)
        
        # SQL keywords to exclude
        sql_keywords = {
            'select', 'from', 'where', 'group', 'order', 'by', 'having', 'limit', 
            'as', 'and', 'or', 'not', 'null', 'is', 'in', 'like', 'between', 'case',
            'when', 'then', 'else', 'end', 'union', 'all', 'inner', 'left', 'right',
            'outer', 'full', 'join', 'on', 'desc', 'asc', 'sum', 'count', 'avg', 'max',
            'min', 'distinct', 'cast', 'date', 'timestamp', 'interval', 'current_date',
            'date_trunc', 'date_format', 'day', 'month', 'year', 'hour', 'minute',
            'second', 'true', 'false', 'filter', 'over', 'partition', 'window'
        }
        
        # Create a mapping of table aliases to full table names
        alias_map = {}
        for table in tables:
            # Extract alias if present (with AS)
            alias_pattern = rf'{re.escape(table)}\s+AS\s+(\w+)'
            alias_match = re.search(alias_pattern, sql, re.IGNORECASE)
            if alias_match:
                alias_map[alias_match.group(1).lower()] = table
            
            # Also check for table alias without AS (single letter or short word after table)
            alias_pattern2 = rf'{re.escape(table)}\s+([a-z])(?:\s|,|$|JOIN|WHERE|GROUP|ORDER|HAVING)'
            alias_match2 = re.search(alias_pattern2, sql, re.IGNORECASE)
            if alias_match2:
                potential_alias = alias_match2.group(1).lower()
                if potential_alias not in ['j', 'i', 'o', 'w', 'g', 'h']:  # Common single-letter aliases
                    alias_map[potential_alias] = table
        
        # Extract table name without quotes for matching
        table_base_names = {}
        for table in tables:
            # Extract last part of table name
            parts = table.replace('"', '').split('.')
            base_name = parts[-1].lower()
            table_base_names[base_name] = table
        
        columns_by_table = defaultdict(set)
        
        # Extract columns from the actual source tables in FROM/JOIN clauses
        # Look for column references that come directly from source tables
        for table in tables:
            # Get table base name and potential aliases
            table_parts = table.replace('"', '').split('.')
            base_name = table_parts[-1].lower()
            
            # Find all references to this table (with or without alias)
            # Pattern: table_name alias or table_name AS alias
            table_ref_pattern = rf'{re.escape(table)}\s+(?:AS\s+)?(\w+)'
            alias_matches = list(re.finditer(table_ref_pattern, sql, re.IGNORECASE))
            
            aliases = [base_name]  # Include base name itself
            for alias_match in alias_matches:
                alias = alias_match.group(1).lower()
                if alias not in sql_keywords and len(alias) <= 3:  # Short aliases like 'a', 'b'
                    aliases.append(alias)
            
            # Now find columns referenced with these aliases
            for alias in aliases:
                # Pattern: alias.column_name
                col_pattern = rf'\b{re.escape(alias)}\.([a-zA-Z_][a-zA-Z0-9_]*)'
                col_matches = re.finditer(col_pattern, sql, re.IGNORECASE)
                for col_match in col_matches:
                    column = col_match.group(1)
                    col_lower = column.lower()
                    if (col_lower not in sql_keywords and 
                        len(column) > 1 and 
                        not col_lower.isdigit() and
                        col_lower not in ['id', 'as', 'on', 'by', 'in', 'is']):
                        columns_by_table[table].add(column)
        
        # Also extract columns from SELECT that are directly from source tables
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if select_match:
            select_clause = select_match.group(1)
            # Find table.column patterns
            col_refs = re.finditer(
                r'(\w+)\.([a-zA-Z_][a-zA-Z0-9_]*)',
                select_clause,
                re.IGNORECASE
            )
            for match in col_refs:
                table_prefix, column = match.groups()
                col_lower = column.lower()
                prefix_lower = table_prefix.lower()
                
                if (col_lower not in sql_keywords and 
                    len(column) > 1 and 
                    not col_lower.isdigit()):
                    # Check if prefix is an alias
                    if prefix_lower in alias_map:
                        columns_by_table[alias_map[prefix_lower]].add(column)
                    elif prefix_lower in table_base_names:
                        columns_by_table[table_base_names[prefix_lower]].add(column)
        
        # Extract columns from WHERE clause
        where_match = re.search(r'WHERE\s+(.*?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+HAVING|\s+LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1)
            col_refs = re.finditer(
                r'(?:(\w+)\.)?([a-zA-Z_][a-zA-Z0-9_]*)',
                where_clause,
                re.IGNORECASE
            )
            for match in col_refs:
                table_prefix, column = match.groups()
                col_lower = column.lower()
                if col_lower not in sql_keywords and len(column) > 1 and not col_lower.isdigit():
                    if table_prefix:
                        prefix_lower = table_prefix.lower()
                        if prefix_lower in alias_map:
                            columns_by_table[alias_map[prefix_lower]].add(column)
                        elif prefix_lower in table_base_names:
                            columns_by_table[table_base_names[prefix_lower]].add(column)
        
        # Extract columns from JOIN ON clause
        join_matches = re.finditer(
            r'JOIN\s+.*?\s+ON\s+(.*?)(?:\s+WHERE|\s+GROUP\s+BY|\s+ORDER\s+BY|\s+HAVING|$)',
            sql,
            re.IGNORECASE | re.DOTALL
        )
        for join_match in join_matches:
            on_clause = join_match.group(1)
            col_refs = re.finditer(
                r'(?:(\w+)\.)?([a-zA-Z_][a-zA-Z0-9_]*)',
                on_clause,
                re.IGNORECASE
            )
            for match in col_refs:
                table_prefix, column = match.groups()
                col_lower = column.lower()
                if col_lower not in sql_keywords and len(column) > 1 and not col_lower.isdigit():
                    if table_prefix:
                        prefix_lower = table_prefix.lower()
                        if prefix_lower in alias_map:
                            columns_by_table[alias_map[prefix_lower]].add(column)
                        elif prefix_lower in table_base_names:
                            columns_by_table[table_base_names[prefix_lower]].add(column)
        
        # Extract columns from GROUP BY
        groupby_match = re.search(r'GROUP\s+BY\s+(.*?)(?:\s+ORDER\s+BY|\s+HAVING|\s+LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if groupby_match:
            groupby_clause = groupby_match.group(1)
            col_refs = re.finditer(
                r'(?:(\w+)\.)?([a-zA-Z_][a-zA-Z0-9_]*)',
                groupby_clause,
                re.IGNORECASE
            )
            for match in col_refs:
                table_prefix, column = match.groups()
                col_lower = column.lower()
                if col_lower not in sql_keywords and len(column) > 1 and not col_lower.isdigit():
                    if table_prefix:
                        prefix_lower = table_prefix.lower()
                        if prefix_lower in alias_map:
                            columns_by_table[alias_map[prefix_lower]].add(column)
                        elif prefix_lower in table_base_names:
                            columns_by_table[table_base_names[prefix_lower]].add(column)
                    else:
                        for table in tables:
                            columns_by_table[table].add(column)
        
        # Convert sets to sorted lists and filter out invalid columns
        result = {}
        for table, cols in columns_by_table.items():
            # Filter out numeric-only, single characters, and SQL keywords
            valid_cols = [
                col for col in sorted(cols) 
                if col.lower() not in sql_keywords 
                and len(col) > 1 
                and not col.isdigit()
                and not col.lower() in ['id', 'as', 'on', 'by']
            ]
            if valid_cols:
                result[table] = valid_cols
        
        return result
    
    def parse_chart_sql(self, sql: str) -> Dict[str, any]:
        """Parse SQL query and return tables and columns"""
        if not sql:
            return {'tables': [], 'columns_by_table': {}}
        
        tables = self.extract_tables(sql)
        columns_by_table = self.extract_columns(sql, tables)
        
        return {
            'tables': tables,
            'columns_by_table': columns_by_table
        }


def normalize_table_name(table_name: str) -> str:
    """
    Normalize table name: add 'hive.' prefix if catalog is missing
    Format: "catalog"."db"."table" or catalog.db.table
    """
    if not table_name:
        return table_name
    
    # Check if it's quoted format: "catalog"."db"."table"
    if table_name.startswith('"'):
        parts = [p.strip('"') for p in table_name.split('"."')]
        # If only 2 parts (db.table), add hive as catalog
        if len(parts) == 2:
            return f'"hive"."{parts[0]}"."{parts[1]}"'
        # If 3 parts, return as is
        elif len(parts) == 3:
            return table_name
        # If 1 part, add hive and default schema
        elif len(parts) == 1:
            return f'"hive"."default"."{parts[0]}"'
    else:
        # Unquoted format: catalog.db.table
        parts = table_name.split('.')
        # If only 2 parts (db.table), add hive as catalog
        if len(parts) == 2:
            return f'hive.{parts[0]}.{parts[1]}'
        # If 3 parts, return as is
        elif len(parts) == 3:
            return table_name
        # If 1 part, add hive and default schema
        elif len(parts) == 1:
            return f'hive.default.{parts[0]}'
    
    return table_name


def extract_original_columns_from_sql(sql: str, tables: List[str]) -> Dict[str, List[str]]:
    """
    Extract original column names from SQL by finding direct table references
    (not aliases or computed columns)
    
    Returns dict mapping table -> list of original column names
    """
    if not sql:
        return {}
    
    sql_clean = SQLParser().remove_comments(sql)
    columns_by_table = {}
    
    for table in tables:
        columns = set()
        table_parts = table.replace('"', '').split('.')
        base_name = table_parts[-1].lower()
        
        # Find table aliases
        aliases = []
        # Pattern: table_name alias or table_name AS alias
        alias_patterns = [
            rf'{re.escape(table)}\s+AS\s+(\w+)',
            rf'{re.escape(table)}\s+(\w+)(?:\s|,|$|JOIN|WHERE|GROUP|ORDER)',
        ]
        
        for pattern in alias_patterns:
            matches = re.finditer(pattern, sql_clean, re.IGNORECASE)
            for match in matches:
                alias = match.group(1).lower()
                if alias not in ['join', 'inner', 'left', 'right', 'outer', 'full', 'where', 'group', 'order', 'having']:
                    aliases.append(alias)
        
        # Also use base name as potential alias
        aliases.append(base_name)
        
        # Find columns referenced with table/alias prefix: alias.column or table.column
        for alias in set(aliases):
            # Pattern: alias.column_name (original column reference)
            col_pattern = rf'\b{re.escape(alias)}\.([a-zA-Z_][a-zA-Z0-9_]*)'
            col_matches = re.finditer(col_pattern, sql_clean, re.IGNORECASE)
            for match in col_matches:
                col = match.group(1)
                col_lower = col.lower()
                # Filter out SQL keywords and common false positives
                if (col_lower not in ['select', 'from', 'where', 'group', 'order', 'by', 'having', 
                                     'limit', 'as', 'and', 'or', 'not', 'null', 'is', 'in', 'like', 
                                     'between', 'case', 'when', 'then', 'else', 'end', 'sum', 'count',
                                     'avg', 'max', 'min', 'distinct', 'cast', 'date', 'timestamp',
                                     'interval', 'current_date', 'date_trunc', 'date_format', 'day',
                                     'month', 'year', 'hour', 'minute', 'second', 'true', 'false',
                                     'filter', 'over', 'partition', 'window', 'desc', 'asc', 'union',
                                     'all', 'inner', 'left', 'right', 'outer', 'full', 'join', 'on',
                                     'id', 'as', 'on', 'by', 'in', 'is'] and
                    len(col) > 1 and not col_lower.isdigit()):
                    columns.add(col)
        
        if columns:
            columns_by_table[table] = sorted(list(columns))
    
    return columns_by_table


def extract_table_column_mapping(dashboard_info: Dict, trino_columns: Optional[Dict[str, Dict[str, str]]] = None) -> List[Dict]:
    """
    Extract table and column mapping from dashboard info
    
    Args:
        dashboard_info: Dashboard info dict
        trino_columns: Optional dict mapping table_name -> {column_name: data_type}
                      If provided, uses actual table columns from Trino
    
    Returns list of dicts with: table_name, column_name, column_label__chart_json, data_type
    Grouped by table_name and column_name (no duplicates)
    column_label__chart_json is a JSON string mapping chart_id to column_label
    """
    parser = SQLParser()
    # Use a dict to group by (table, column) -> {chart_id: column_label}
    table_column_map = {}
    
    charts = dashboard_info.get('charts', [])
    
    for chart in charts:
        chart_id = chart.get('chart_id')
        sql_query = chart.get('sql_query')
        
        if not sql_query:
            continue
        
        # Parse SQL to get tables
        parsed = parser.parse_chart_sql(sql_query)
        tables = parsed['tables']
        
        # Get original columns from SQL (not aliases)
        columns_by_table = extract_original_columns_from_sql(sql_query, tables)
        
        # If no columns found in SQL, try to get from chart metadata
        if not any(columns_by_table.values()):
            # Use columns from chart metadata as fallback
            columns_list = chart.get('columns', [])
            if columns_list and isinstance(columns_list, list):
                # Distribute columns across all tables (since we don't know which table they belong to)
                for table in tables:
                    columns_by_table[table] = [col for col in columns_list if isinstance(col, str)]
        
        # If Trino columns are provided, use actual table columns from Trino
        # Match SQL column references to actual table columns
        if trino_columns:
            for table in tables:
                normalized_table = normalize_table_name(table)
                # Get actual columns from Trino for this table
                actual_columns_dict = None
                if normalized_table in trino_columns:
                    actual_columns_dict = trino_columns[normalized_table]
                elif table in trino_columns:
                    actual_columns_dict = trino_columns[table]
                
                if actual_columns_dict:
                    actual_columns = list(actual_columns_dict.keys())
                    # Get columns referenced in SQL for this table
                    sql_cols = columns_by_table.get(table, [])
                    
                    if sql_cols:
                        # Match SQL columns to actual table columns (case-insensitive)
                        matched_columns = []
                        for sql_col in sql_cols:
                            # Find matching actual column (case-insensitive)
                            for actual_col in actual_columns:
                                if sql_col.lower() == actual_col.lower():
                                    matched_columns.append(actual_col)  # Use actual column name
                                    break
                        # If we have matches, use them; otherwise use all actual columns
                        columns_by_table[table] = matched_columns if matched_columns else actual_columns
                    else:
                        # No columns found in SQL (might be SELECT *), use all actual columns from Trino
                        columns_by_table[table] = actual_columns
                else:
                    # Trino columns not available, keep SQL-extracted columns
                    pass
        
        # Get column labels from chart metadata
        column_labels = {}
        metrics = chart.get('metrics', [])
        columns_list = chart.get('columns', [])
        
        # Map columns to labels from metrics
        for metric in metrics:
            if isinstance(metric, dict):
                col = metric.get('column', {})
                if isinstance(col, dict):
                    col_name = col.get('column_name')
                    label = metric.get('label') or col.get('verbose_name') or col_name
                    if col_name:
                        column_labels[col_name.lower()] = label
        
        # Also check columns list for labels
        if isinstance(columns_list, list):
            for col_name in columns_list:
                if isinstance(col_name, str) and col_name.lower() not in column_labels:
                    column_labels[col_name.lower()] = col_name
        
        # Process each table-column combination
        for table in tables:
            # Normalize table name (add hive. prefix if needed)
            normalized_table = normalize_table_name(table)
            
            columns = columns_by_table.get(table, [])
            if columns:
                for column in columns:
                    # Get label if available (case-insensitive match)
                    col_lower = column.lower()
                    column_label = column_labels.get(col_lower, column)
                    
                    # Get data type if available
                    data_type = None
                    if trino_columns:
                        if normalized_table in trino_columns:
                            data_type = trino_columns[normalized_table].get(column)
                        elif table in trino_columns:
                            data_type = trino_columns[table].get(column)
                    
                    # Create key for grouping
                    key = (normalized_table, column)
                    
                    # Initialize if not exists
                    if key not in table_column_map:
                        table_column_map[key] = {
                            'labels': {},
                            'data_type': data_type
                        }
                    
                    # Add chart_id -> column_label mapping
                    table_column_map[key]['labels'][chart_id] = column_label
            else:
                # Table found but no specific columns identified
                # If Trino columns available, use all columns from that table
                if trino_columns:
                    actual_columns_dict = None
                    if normalized_table in trino_columns:
                        actual_columns_dict = trino_columns[normalized_table]
                    elif table in trino_columns:
                        actual_columns_dict = trino_columns[table]
                    
                    if actual_columns_dict:
                        for column in actual_columns_dict.keys():
                            col_lower = column.lower()
                            column_label = column_labels.get(col_lower, column)
                            data_type = actual_columns_dict.get(column)
                            
                            key = (normalized_table, column)
                            if key not in table_column_map:
                                table_column_map[key] = {
                                    'labels': {},
                                    'data_type': data_type
                                }
                            table_column_map[key]['labels'][chart_id] = column_label
                else:
                    # No Trino columns and no SQL columns - mark table as used but no columns
                    key = (normalized_table, '')
                    if key not in table_column_map:
                        table_column_map[key] = {
                            'labels': {},
                            'data_type': None
                        }
                    table_column_map[key]['labels'][chart_id] = ''
    
    # Convert to list format
    results = []
    for (table_name, column_name), info in table_column_map.items():
        # Convert chart_labels dict to JSON string
        column_label__chart_json = json.dumps(info['labels'], sort_keys=True)
        
        result = {
            'table_name': table_name,
            'column_name': column_name,
            'column_label__chart_json': column_label__chart_json
        }
        
        # Add data type if available
        if info.get('data_type'):
            result['data_type'] = info['data_type']
        
        results.append(result)
    
    # Sort by table_name, then column_name
    results.sort(key=lambda x: (x['table_name'], x['column_name']))
    
    return results


if __name__ == '__main__':
    # Test the parser
    test_sql = '''
    SELECT 
        t1.col1,
        t2.col2,
        SUM(t1.col3) as total
    FROM "catalog"."db"."table1" t1
    JOIN "catalog"."db"."table2" t2 ON t1.id = t2.id
    WHERE t1.status = 'active'
    GROUP BY t1.col1, t2.col2
    '''
    
    parser = SQLParser()
    tables = parser.extract_tables(test_sql)
    columns = parser.extract_columns(test_sql, tables)
    
    print("Tables:", tables)
    print("Columns:", columns)

