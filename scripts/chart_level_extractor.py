"""
Chart-level metadata extraction module for token optimization.

This module processes metadata extraction chart-by-chart to optimize token usage,
then merges chart-level results into dashboard-level metadata.
"""
import os
import json
import re
import pandas as pd
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from llm_extractor import (
    _get_dspy_table_metadata_extractor,
    _get_dspy_column_metadata_extractor,
    _get_dspy_joining_condition_extractor,
    _get_dspy_filter_conditions_extractor,
    _get_dspy_term_definition_extractor,
    TableMetadataExtractor,
    ColumnMetadataExtractor,
    JoiningConditionExtractor,
    FilterConditionsExtractor,
    TermDefinitionExtractor
)
from starburst_schema_fetcher import normalize_table_name


@dataclass
class ChartMetadata:
    """Container for chart-level metadata extraction results"""
    chart_id: int
    chart_name: str
    table_metadata: List[Dict]
    column_metadata: List[Dict]
    joining_conditions: List[Dict]
    filter_conditions: str
    definitions: List[Dict]


def extract_table_metadata_for_chart(
    chart: Dict,
    dashboard_title: str,
    api_key: str,
    model: str,
    base_url: str
) -> List[Dict]:
    """
    Extract table metadata for a single chart.
    
    Args:
        chart: Chart dict with chart_id, chart_name, sql_query, metrics, etc.
        dashboard_title: Dashboard title for context
        api_key: LLM API key
        model: LLM model name
        base_url: LLM base URL
        
    Returns:
        List of table metadata dicts for tables used in this chart
    """
    extractor = _get_dspy_table_metadata_extractor(api_key, model, base_url)
    
    chart_name = chart.get('chart_name', 'Unknown')
    sql_query = chart.get('sql_query', '')
    metrics = chart.get('metrics', [])
    
    if not sql_query:
        return []
    
    # Extract tables from SQL (simple parsing)
    tables_used = set()
    sql_lower = sql_query.lower()
    
    # Common table patterns
    from_clause_match = sql_lower.find('from')
    if from_clause_match != -1:
        # Extract table names after FROM
        from_part = sql_query[from_clause_match + 4:]
        # Look for table patterns like schema.table or table
        import re
        # Match patterns like hive.schema.table or just table
        table_patterns = re.findall(r'from\s+([a-zA-Z0-9_\.]+)', sql_lower)
        for pattern in table_patterns:
            if '.' in pattern:
                tables_used.add(pattern)
            else:
                # Try to find schema from context
                tables_used.add(pattern)
    
    # Also check JOIN clauses
    join_patterns = re.findall(r'join\s+([a-zA-Z0-9_\.]+)', sql_lower)
    for pattern in join_patterns:
        if '.' in pattern:
            tables_used.add(pattern)
    
    if not tables_used:
        return []
    
    # Collect chart labels
    labels = []
    for metric in metrics:
        if isinstance(metric, dict):
            label = metric.get('label') or metric.get('column', {}).get('verbose_name', '')
            if label:
                labels.append(label)
    
    chart_context = json.dumps([{
        'chart_name': chart_name,
        'labels': labels
    }], indent=2)
    
    results = []
    for table_name in tables_used:
        normalized_table = normalize_table_name(table_name)
        
        try:
            # Truncate SQL if too long
            sql_context = sql_query[:2000] if len(sql_query) > 2000 else sql_query
            
            # Call LLM for this table
            result = extractor(
                dashboard_title=dashboard_title,
                chart_names_and_labels=chart_context,
                table_name=normalized_table,
                table_columns=json.dumps([], indent=2),  # Empty for chart-level
                sql_queries_context=sql_context
            )
            
            metadata = {
                'table_name': normalized_table,
                'table_description': result.table_description,
                'refresh_frequency': result.refresh_frequency,
                'vertical': result.vertical,
                'partition_column': result.partition_column,
                'remarks': result.remarks,
                'relationship_context': result.relationship_context,
                'source_chart_id': chart.get('chart_id'),
                'source_chart_name': chart_name
            }
            results.append(metadata)
            
        except Exception as e:
            print(f"    ⚠️  Error extracting table metadata for {normalized_table} in chart {chart_name}: {str(e)}")
            results.append({
                'table_name': normalized_table,
                'table_description': f'Error: {str(e)}',
                'refresh_frequency': '',
                'vertical': '',
                'partition_column': '',
                'remarks': '',
                'relationship_context': '',
                'source_chart_id': chart.get('chart_id'),
                'source_chart_name': chart_name
            })
    
    return results


def extract_column_metadata_for_chart(
    chart: Dict,
    dashboard_title: str,
    tables_columns_df: pd.DataFrame,
    api_key: str,
    model: str,
    base_url: str
) -> List[Dict]:
    """
    Extract column metadata for a single chart.
    
    Args:
        chart: Chart dict
        dashboard_title: Dashboard title
        tables_columns_df: DataFrame with tables_columns data
        api_key: LLM API key
        model: LLM model name
        base_url: LLM base URL
        
    Returns:
        List of column metadata dicts
    """
    extractor = _get_dspy_column_metadata_extractor(api_key, model, base_url)
    
    chart_name = chart.get('chart_name', 'Unknown')
    sql_query = chart.get('sql_query', '')
    metrics = chart.get('metrics', [])
    chart_id = chart.get('chart_id')
    
    if not sql_query:
        return []
    
    # Find columns used in this chart from tables_columns_df
    # Match by checking if table/column appears in SQL
    sql_lower = sql_query.lower()
    chart_columns = []
    
    for _, row in tables_columns_df.iterrows():
        table = row['tables_involved']
        col = row['column_names']
        table_short = table.split('.')[-1].lower()
        col_lower = col.lower()
        
        # Check if this column is used in this chart's SQL
        if (table_short in sql_lower or table.lower() in sql_lower) and col_lower in sql_lower:
            chart_columns.append(row)
    
    if not chart_columns:
        return []
    
    # Collect labels from metrics
    labels = []
    for metric in metrics:
        if isinstance(metric, dict):
            label = metric.get('label', '')
            if label:
                labels.append(label)
    
    chart_labels_json = json.dumps({
        'aliases': labels,
        'chart_names': [chart_name]
    }, indent=2)
    
    results = []
    for row in chart_columns:
        table_name = row['tables_involved']
        column_name = row['column_names']
        variable_type = row.get('column_datatype', '')
        
        try:
            # Truncate SQL context
            sql_context = sql_query[:1500] if len(sql_query) > 1500 else sql_query
            
            result = extractor(
                column_name=column_name,
                table_name=table_name,
                column_datatype=variable_type or 'unknown',
                chart_labels_and_aliases=chart_labels_json,
                derived_column_usage=json.dumps([], indent=2),
                sql_usage_context=sql_context
            )
            
            # Determine required_flag
            required_flag = "no"
            if column_name.lower() in ['id', 'txn_id', 'user_id', 'customer_id', 'created_on', 'date', 'dt']:
                required_flag = "yes"
            elif any(keyword in column_name.lower() for keyword in ['_id', '_key', 'timestamp', 'date']):
                required_flag = "yes"
            
            metadata = {
                'table_name': table_name,
                'column_name': column_name,
                'variable_type': variable_type or '',
                'column_description': result.column_description,
                'required_flag': required_flag,
                'source_chart_id': chart_id,
                'source_chart_name': chart_name
            }
            results.append(metadata)
            
        except Exception as e:
            print(f"    ⚠️  Error extracting column metadata for {table_name}.{column_name}: {str(e)}")
            results.append({
                'table_name': table_name,
                'column_name': column_name,
                'variable_type': variable_type or '',
                'column_description': f'Error: {str(e)}',
                'required_flag': 'no',
                'source_chart_id': chart_id,
                'source_chart_name': chart_name
            })
    
    return results


def extract_joining_conditions_for_chart(
    chart: Dict,
    dashboard_title: str,
    tables_columns_df: pd.DataFrame,
    api_key: str,
    model: str,
    base_url: str
) -> List[Dict]:
    """
    Extract joining conditions for a single chart.
    
    Args:
        chart: Chart dict
        dashboard_title: Dashboard title
        tables_columns_df: DataFrame with tables_columns data
        api_key: LLM API key
        model: LLM model name
        base_url: LLM base URL
        
    Returns:
        List of joining condition dicts
    """
    extractor = _get_dspy_joining_condition_extractor(api_key, model, base_url)
    
    chart_name = chart.get('chart_name', 'Unknown')
    sql_query = chart.get('sql_query', '')
    chart_id = chart.get('chart_id')
    
    if not sql_query:
        return []
    
    # Find tables used in this chart
    tables_used = set()
    sql_lower = sql_query.lower()
    
    for table in tables_columns_df['tables_involved'].unique():
        table_short = table.split('.')[-1].lower()
        if table_short in sql_lower or table.lower() in sql_lower:
            tables_used.add(table)
    
    # Only process if 2+ tables
    if len(tables_used) < 2:
        return []
    
    tables_list = sorted(list(tables_used))
    
    try:
        # Truncate SQL if too long
        sql_context = sql_query[:3000] if len(sql_query) > 3000 else sql_query
        
        result = extractor(
            dashboard_title=dashboard_title,
            chart_name=chart_name,
            sql_query=sql_context,
            tables_involved=', '.join(tables_list)
        )
        
        # Parse result
        try:
            joining_conditions = json.loads(result.joining_conditions)
            if not isinstance(joining_conditions, list):
                joining_conditions = []
        except:
            joining_conditions = []
        
        # Add source chart info
        for condition in joining_conditions:
            condition['source_chart_id'] = chart_id
            condition['source_chart_name'] = chart_name
        
        return joining_conditions
        
    except Exception as e:
        print(f"    ⚠️  Error extracting joining conditions for chart {chart_name}: {str(e)}")
        return []


def extract_filter_conditions_for_chart(
    chart: Dict,
    dashboard_title: str,
    tables_columns_df: pd.DataFrame,
    api_key: str,
    model: str,
    base_url: str
) -> str:
    """
    Extract filter conditions for a single chart.
    
    Args:
        chart: Chart dict
        dashboard_title: Dashboard title
        tables_columns_df: DataFrame with tables_columns data
        api_key: LLM API key
        model: LLM model name
        base_url: LLM base URL
        
    Returns:
        String content for this chart's filter conditions
    """
    extractor = _get_dspy_filter_conditions_extractor(api_key, model, base_url)
    
    chart_name = chart.get('chart_name', 'Unknown')
    sql_query = chart.get('sql_query', '')
    metrics = chart.get('metrics', [])
    filters = chart.get('filters', [])
    
    if not sql_query:
        return ""
    
    # Find tables involved
    tables_used = set()
    sql_lower = sql_query.lower()
    
    for table in tables_columns_df['tables_involved'].unique():
        table_short = table.split('.')[-1].lower()
        if table_short in sql_lower or table.lower() in sql_lower:
            tables_used.add(table)
    
    tables_involved_str = ', '.join(sorted(tables_used)) if tables_used else 'Unknown'
    
    # Prepare inputs
    chart_metrics_json = json.dumps(metrics, indent=2)
    chart_filters_json = json.dumps(filters, indent=2)
    
    # Empty all_charts_context for single chart processing
    all_charts_json = json.dumps([], indent=2)
    
    try:
        # Truncate SQL if too long
        sql_context = sql_query[:4000] if len(sql_query) > 4000 else sql_query
        
        result = extractor(
            chart_name=chart_name,
            chart_metrics=chart_metrics_json,
            sql_query=sql_context,
            chart_filters=chart_filters_json,
            tables_involved=tables_involved_str,
            dashboard_title=dashboard_title,
            all_charts_context=all_charts_json
        )
        
        # Format output
        content = f"## {chart_name}\n\n"
        content += result.use_case_description + "\n\n"
        
        # Clean up SQL
        sql_content = result.filter_conditions_sql
        if sql_content.startswith('```sql'):
            sql_content = sql_content[6:]
        if sql_content.startswith('```'):
            sql_content = sql_content[3:]
        if sql_content.endswith('```'):
            sql_content = sql_content[:-3]
        sql_content = sql_content.strip()
        
        content += sql_content + "\n\n"
        
        return content
        
    except Exception as e:
        print(f"    ⚠️  Error extracting filter conditions for chart {chart_name}: {str(e)}")
        return f"## {chart_name}\n\nError extracting filter conditions: {str(e)}\n\n"


def extract_definitions_for_chart(
    chart: Dict,
    dashboard_title: str,
    api_key: str,
    model: str,
    base_url: str
) -> List[Dict]:
    """
    Extract term definitions for a single chart.
    
    Args:
        chart: Chart dict
        dashboard_title: Dashboard title
        api_key: LLM API key
        model: LLM model name
        base_url: LLM base URL
        
    Returns:
        List of term definition dicts
    """
    extractor = _get_dspy_term_definition_extractor(api_key, model, base_url)
    
    chart_name = chart.get('chart_name', 'Unknown')
    metrics = chart.get('metrics', [])
    sql_query = chart.get('sql_query', '')
    
    # Collect labels from metrics
    labels = []
    metric_details = []
    for metric in metrics:
        if isinstance(metric, dict):
            label = metric.get('label', '')
            sql_expr = metric.get('sqlExpression', '')
            if label:
                labels.append(label)
            if sql_expr:
                metric_details.append({
                    'label': label,
                    'expression': sql_expr
                })
    
    chart_names_and_labels = json.dumps([{
        'chart_name': chart_name,
        'labels': labels
    }], indent=2)
    
    sql_queries = json.dumps([{
        'chart_name': chart_name,
        'sql_query': sql_query[:2000] if len(sql_query) > 2000 else sql_query
    }], indent=2) if sql_query else json.dumps([], indent=2)
    
    metrics_context = json.dumps([{
        'chart_name': chart_name,
        'metrics': metric_details
    }], indent=2) if metric_details else json.dumps([], indent=2)
    
    try:
        result = extractor(
            dashboard_title=dashboard_title,
            chart_names_and_labels=chart_names_and_labels,
            sql_queries=sql_queries,
            metrics_context=metrics_context
        )
        
        # Parse JSON result
        try:
            term_definitions = json.loads(result.term_definitions)
            if not isinstance(term_definitions, list):
                term_definitions = []
        except:
            term_definitions = []
        
        # Add source chart info
        for definition in term_definitions:
            definition['source_chart_id'] = chart.get('chart_id')
            definition['source_chart_name'] = chart_name
        
        return term_definitions
        
    except Exception as e:
        print(f"    ⚠️  Error extracting definitions for chart {chart_name}: {str(e)}")
        return []


def process_chart_metadata(
    chart: Dict,
    dashboard_title: str,
    tables_columns_df: pd.DataFrame,
    api_key: str,
    model: str,
    base_url: str
) -> ChartMetadata:
    """
    Process all metadata types for a single chart.
    
    Args:
        chart: Chart dict
        dashboard_title: Dashboard title
        tables_columns_df: DataFrame with tables_columns data
        api_key: LLM API key
        model: LLM model name
        base_url: LLM base URL
        
    Returns:
        ChartMetadata object with all extracted metadata
    """
    chart_id = chart.get('chart_id')
    chart_name = chart.get('chart_name', 'Unknown')
    
    print(f"    Processing chart {chart_id}: {chart_name}...", flush=True)
    
    # Extract all metadata types
    table_metadata = extract_table_metadata_for_chart(
        chart, dashboard_title, api_key, model, base_url
    )
    
    column_metadata = extract_column_metadata_for_chart(
        chart, dashboard_title, tables_columns_df, api_key, model, base_url
    )
    
    joining_conditions = extract_joining_conditions_for_chart(
        chart, dashboard_title, tables_columns_df, api_key, model, base_url
    )
    
    filter_conditions = extract_filter_conditions_for_chart(
        chart, dashboard_title, tables_columns_df, api_key, model, base_url
    )
    
    definitions = extract_definitions_for_chart(
        chart, dashboard_title, api_key, model, base_url
    )
    
    return ChartMetadata(
        chart_id=chart_id,
        chart_name=chart_name,
        table_metadata=table_metadata,
        column_metadata=column_metadata,
        joining_conditions=joining_conditions,
        filter_conditions=filter_conditions,
        definitions=definitions
    )


def _extract_table_metadata_wrapper(chart, dashboard_title, api_key, model, base_url):
    """Wrapper function for extracting table metadata from a single chart."""
    return ChartMetadata(
        chart_id=chart.get('chart_id', 0),
        chart_name=chart.get('chart_name', 'Unknown'),
        table_metadata=extract_table_metadata_for_chart(chart, dashboard_title, api_key, model, base_url),
        column_metadata=[],
        joining_conditions=[],
        filter_conditions="",
        definitions=[]
    )


def process_charts_for_table_metadata(
    charts: List[Dict],
    dashboard_title: str,
    api_key: str,
    model: str,
    base_url: str,
    max_workers: int = 5
) -> List[ChartMetadata]:
    """Process charts in parallel to extract table metadata only."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chart = {
            executor.submit(
                _extract_table_metadata_wrapper,
                chart, dashboard_title, api_key, model, base_url
            ): chart
            for chart in charts
        }
        
        for future in as_completed(future_to_chart):
            chart = future_to_chart[future]
            try:
                chart_metadata = future.result()
                results.append(chart_metadata)
                print(f"    ✅ Completed table metadata for chart {chart.get('chart_id')}: {chart.get('chart_name', 'Unknown')}", flush=True)
            except Exception as e:
                print(f"    ❌ Error processing chart {chart.get('chart_id')}: {str(e)}", flush=True)
                results.append(ChartMetadata(
                    chart_id=chart.get('chart_id', 0),
                    chart_name=chart.get('chart_name', 'Unknown'),
                    table_metadata=[],
                    column_metadata=[],
                    joining_conditions=[],
                    filter_conditions="",
                    definitions=[]
                ))
    
    return results


def _extract_column_metadata_wrapper(chart, dashboard_title, tables_columns_df, api_key, model, base_url):
    """Wrapper function for extracting column metadata from a single chart."""
    return ChartMetadata(
        chart_id=chart.get('chart_id', 0),
        chart_name=chart.get('chart_name', 'Unknown'),
        table_metadata=[],
        column_metadata=extract_column_metadata_for_chart(chart, dashboard_title, tables_columns_df, api_key, model, base_url),
        joining_conditions=[],
        filter_conditions="",
        definitions=[]
    )


def process_charts_for_column_metadata(
    charts: List[Dict],
    dashboard_title: str,
    tables_columns_df: pd.DataFrame,
    api_key: str,
    model: str,
    base_url: str,
    max_workers: int = 5
) -> List[ChartMetadata]:
    """Process charts in parallel to extract column metadata only."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chart = {
            executor.submit(
                _extract_column_metadata_wrapper,
                chart, dashboard_title, tables_columns_df, api_key, model, base_url
            ): chart
            for chart in charts
        }
        
        for future in as_completed(future_to_chart):
            chart = future_to_chart[future]
            try:
                chart_metadata = future.result()
                results.append(chart_metadata)
                print(f"    ✅ Completed column metadata for chart {chart.get('chart_id')}: {chart.get('chart_name', 'Unknown')}", flush=True)
            except Exception as e:
                print(f"    ❌ Error processing chart {chart.get('chart_id')}: {str(e)}", flush=True)
                results.append(ChartMetadata(
                    chart_id=chart.get('chart_id', 0),
                    chart_name=chart.get('chart_name', 'Unknown'),
                    table_metadata=[],
                    column_metadata=[],
                    joining_conditions=[],
                    filter_conditions="",
                    definitions=[]
                ))
    
    return results


def _extract_joining_conditions_wrapper(chart, dashboard_title, tables_columns_df, api_key, model, base_url):
    """Wrapper function for extracting joining conditions from a single chart."""
    return ChartMetadata(
        chart_id=chart.get('chart_id', 0),
        chart_name=chart.get('chart_name', 'Unknown'),
        table_metadata=[],
        column_metadata=[],
        joining_conditions=extract_joining_conditions_for_chart(chart, dashboard_title, tables_columns_df, api_key, model, base_url),
        filter_conditions="",
        definitions=[]
    )


def process_charts_for_joining_conditions(
    charts: List[Dict],
    dashboard_title: str,
    tables_columns_df: pd.DataFrame,
    api_key: str,
    model: str,
    base_url: str,
    max_workers: int = 5
) -> List[ChartMetadata]:
    """Process charts in parallel to extract joining conditions only."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chart = {
            executor.submit(
                _extract_joining_conditions_wrapper,
                chart, dashboard_title, tables_columns_df, api_key, model, base_url
            ): chart
            for chart in charts
        }
        
        for future in as_completed(future_to_chart):
            chart = future_to_chart[future]
            try:
                chart_metadata = future.result()
                results.append(chart_metadata)
                print(f"    ✅ Completed joining conditions for chart {chart.get('chart_id')}: {chart.get('chart_name', 'Unknown')}", flush=True)
            except Exception as e:
                print(f"    ❌ Error processing chart {chart.get('chart_id')}: {str(e)}", flush=True)
                results.append(ChartMetadata(
                    chart_id=chart.get('chart_id', 0),
                    chart_name=chart.get('chart_name', 'Unknown'),
                    table_metadata=[],
                    column_metadata=[],
                    joining_conditions=[],
                    filter_conditions="",
                    definitions=[]
                ))
    
    return results


def _extract_filter_conditions_wrapper(chart, dashboard_title, tables_columns_df, api_key, model, base_url):
    """Wrapper function for extracting filter conditions from a single chart."""
    return ChartMetadata(
        chart_id=chart.get('chart_id', 0),
        chart_name=chart.get('chart_name', 'Unknown'),
        table_metadata=[],
        column_metadata=[],
        joining_conditions=[],
        filter_conditions=extract_filter_conditions_for_chart(chart, dashboard_title, tables_columns_df, api_key, model, base_url),
        definitions=[]
    )


def process_charts_for_filter_conditions(
    charts: List[Dict],
    dashboard_title: str,
    tables_columns_df: pd.DataFrame,
    api_key: str,
    model: str,
    base_url: str,
    max_workers: int = 5
) -> List[ChartMetadata]:
    """Process charts in parallel to extract filter conditions only."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chart = {
            executor.submit(
                _extract_filter_conditions_wrapper,
                chart, dashboard_title, tables_columns_df, api_key, model, base_url
            ): chart
            for chart in charts
        }
        
        for future in as_completed(future_to_chart):
            chart = future_to_chart[future]
            try:
                chart_metadata = future.result()
                results.append(chart_metadata)
                print(f"    ✅ Completed filter conditions for chart {chart.get('chart_id')}: {chart.get('chart_name', 'Unknown')}", flush=True)
            except Exception as e:
                print(f"    ❌ Error processing chart {chart.get('chart_id')}: {str(e)}", flush=True)
                results.append(ChartMetadata(
                    chart_id=chart.get('chart_id', 0),
                    chart_name=chart.get('chart_name', 'Unknown'),
                    table_metadata=[],
                    column_metadata=[],
                    joining_conditions=[],
                    filter_conditions="",
                    definitions=[]
                ))
    
    return results


def _extract_definitions_wrapper(chart, dashboard_title, api_key, model, base_url):
    """Wrapper function for extracting term definitions from a single chart."""
    return ChartMetadata(
        chart_id=chart.get('chart_id', 0),
        chart_name=chart.get('chart_name', 'Unknown'),
        table_metadata=[],
        column_metadata=[],
        joining_conditions=[],
        filter_conditions="",
        definitions=extract_definitions_for_chart(chart, dashboard_title, api_key, model, base_url)
    )


def process_charts_for_definitions(
    charts: List[Dict],
    dashboard_title: str,
    api_key: str,
    model: str,
    base_url: str,
    max_workers: int = 5
) -> List[ChartMetadata]:
    """Process charts in parallel to extract term definitions only."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chart = {
            executor.submit(
                _extract_definitions_wrapper,
                chart, dashboard_title, api_key, model, base_url
            ): chart
            for chart in charts
        }
        
        for future in as_completed(future_to_chart):
            chart = future_to_chart[future]
            try:
                chart_metadata = future.result()
                results.append(chart_metadata)
                print(f"    ✅ Completed definitions for chart {chart.get('chart_id')}: {chart.get('chart_name', 'Unknown')}", flush=True)
            except Exception as e:
                print(f"    ❌ Error processing chart {chart.get('chart_id')}: {str(e)}", flush=True)
                results.append(ChartMetadata(
                    chart_id=chart.get('chart_id', 0),
                    chart_name=chart.get('chart_name', 'Unknown'),
                    table_metadata=[],
                    column_metadata=[],
                    joining_conditions=[],
                    filter_conditions="",
                    definitions=[]
                ))
    
    return results


def process_all_charts_parallel(
    charts: List[Dict],
    dashboard_title: str,
    tables_columns_df: pd.DataFrame,
    api_key: str,
    model: str,
    base_url: str,
    max_workers: int = 5
) -> List[ChartMetadata]:
    """
    Process all charts in parallel to extract all metadata types.
    This is a convenience function that calls process_chart_metadata for each chart.
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chart = {
            executor.submit(
                process_chart_metadata,
                chart, dashboard_title, tables_columns_df, api_key, model, base_url
            ): chart
            for chart in charts
        }
        
        for future in as_completed(future_to_chart):
            chart = future_to_chart[future]
            try:
                chart_metadata = future.result()
                results.append(chart_metadata)
                print(f"    ✅ Completed chart {chart.get('chart_id')}: {chart.get('chart_name', 'Unknown')}", flush=True)
            except Exception as e:
                print(f"    ❌ Error processing chart {chart.get('chart_id')}: {str(e)}", flush=True)
                # Create empty metadata for failed chart
                results.append(ChartMetadata(
                    chart_id=chart.get('chart_id', 0),
                    chart_name=chart.get('chart_name', 'Unknown'),
                    table_metadata=[],
                    column_metadata=[],
                    joining_conditions=[],
                    filter_conditions="",
                    definitions=[]
                ))
    
    return results


def merge_chart_table_metadata(chart_metadata_list: List[ChartMetadata]) -> List[Dict]:
    """
    Merge table metadata from all charts into unified dashboard-level metadata.
    
    Args:
        chart_metadata_list: List of ChartMetadata objects
        
    Returns:
        List of merged table metadata dicts
    """
    # Group by table_name
    table_map = {}
    
    for chart_meta in chart_metadata_list:
        for table_meta in chart_meta.table_metadata:
            table_name = table_meta['table_name']
            
            if table_name not in table_map:
                table_map[table_name] = {
                    'table_name': table_name,
                    'table_description': [],
                    'refresh_frequency': [],
                    'vertical': [],
                    'partition_column': [],
                    'remarks': [],
                    'relationship_context': [],
                    'source_charts': []
                }
            
            # Collect all values
            if table_meta.get('table_description'):
                table_map[table_name]['table_description'].append(table_meta['table_description'])
            if table_meta.get('refresh_frequency'):
                table_map[table_name]['refresh_frequency'].append(table_meta['refresh_frequency'])
            if table_meta.get('vertical'):
                table_map[table_name]['vertical'].append(table_meta['vertical'])
            if table_meta.get('partition_column'):
                table_map[table_name]['partition_column'].append(table_meta['partition_column'])
            if table_meta.get('remarks'):
                table_map[table_name]['remarks'].append(table_meta['remarks'])
            if table_meta.get('relationship_context'):
                table_map[table_name]['relationship_context'].append(table_meta['relationship_context'])
            
            table_map[table_name]['source_charts'].append({
                'chart_id': table_meta.get('source_chart_id'),
                'chart_name': table_meta.get('source_chart_name')
            })
    
    # Merge into final format
    results = []
    for table_name, data in table_map.items():
        # Combine descriptions (take longest/most comprehensive)
        descriptions = [d for d in data['table_description'] if d and 'Error' not in d]
        if descriptions:
            # Use the longest description
            table_description = max(descriptions, key=len)
        else:
            table_description = data['table_description'][0] if data['table_description'] else ''
        
        # For other fields, take most common or combine
        refresh_frequency = max(set(data['refresh_frequency']), key=data['refresh_frequency'].count) if data['refresh_frequency'] else ''
        vertical = max(set(data['vertical']), key=data['vertical'].count) if data['vertical'] else ''
        partition_column = max(set(data['partition_column']), key=data['partition_column'].count) if data['partition_column'] else ''
        
        # Combine remarks and relationship_context
        remarks = '; '.join(set([r for r in data['remarks'] if r]))
        relationship_context = '; '.join(set([r for r in data['relationship_context'] if r]))
        
        results.append({
            'table_name': table_name,
            'table_description': table_description,
            'refresh_frequency': refresh_frequency,
            'vertical': vertical,
            'partition_column': partition_column,
            'remarks': remarks,
            'relationship_context': relationship_context
        })
    
    return results


def merge_chart_column_metadata(chart_metadata_list: List[ChartMetadata]) -> List[Dict]:
    """
    Merge column metadata from all charts into unified dashboard-level metadata.
    
    Args:
        chart_metadata_list: List of ChartMetadata objects
        
    Returns:
        List of merged column metadata dicts
    """
    # Group by (table_name, column_name)
    column_map = {}
    
    for chart_meta in chart_metadata_list:
        for col_meta in chart_meta.column_metadata:
            key = (col_meta['table_name'], col_meta['column_name'])
            
            if key not in column_map:
                column_map[key] = {
                    'table_name': col_meta['table_name'],
                    'column_name': col_meta['column_name'],
                    'variable_type': col_meta.get('variable_type', ''),
                    'column_description': [],
                    'required_flag': [],
                    'source_charts': []
                }
            
            if col_meta.get('column_description'):
                column_map[key]['column_description'].append(col_meta['column_description'])
            if col_meta.get('required_flag'):
                column_map[key]['required_flag'].append(col_meta['required_flag'])
            
            column_map[key]['source_charts'].append({
                'chart_id': col_meta.get('source_chart_id'),
                'chart_name': col_meta.get('source_chart_name')
            })
    
    # Merge into final format
    results = []
    for key, data in column_map.items():
        # Combine descriptions (take longest/most comprehensive)
        descriptions = [d for d in data['column_description'] if d and 'Error' not in d]
        if descriptions:
            column_description = max(descriptions, key=len)
        else:
            column_description = data['column_description'][0] if data['column_description'] else ''
        
        # Required flag: if any chart says yes, mark as yes
        required_flag = 'yes' if 'yes' in data['required_flag'] else 'no'
        
        results.append({
            'table_name': data['table_name'],
            'column_name': data['column_name'],
            'variable_type': data['variable_type'],
            'column_description': column_description,
            'required_flag': required_flag
        })
    
    return results


def merge_chart_joining_conditions(chart_metadata_list: List[ChartMetadata]) -> List[Dict]:
    """
    Merge joining conditions from all charts into unified dashboard-level metadata.
    
    Args:
        chart_metadata_list: List of ChartMetadata objects
        
    Returns:
        List of merged joining condition dicts
    """
    # Group by (table1, table2)
    join_map = {}
    
    for chart_meta in chart_metadata_list:
        for join_cond in chart_meta.joining_conditions:
            table1 = join_cond.get('table1', '')
            table2 = join_cond.get('table2', '')
            
            # Normalize order (always smaller first)
            if table1 > table2:
                table1, table2 = table2, table1
            
            key = (table1, table2)
            
            if key not in join_map:
                join_map[key] = {
                    'table1': table1,
                    'table2': table2,
                    'joining_condition': [],
                    'remarks': [],
                    'source_charts': []
                }
            
            if join_cond.get('joining_condition'):
                join_map[key]['joining_condition'].append(join_cond['joining_condition'])
            if join_cond.get('remarks'):
                join_map[key]['remarks'].append(join_cond['remarks'])
            
            join_map[key]['source_charts'].append({
                'chart_id': join_cond.get('source_chart_id'),
                'chart_name': join_cond.get('source_chart_name')
            })
    
    # Merge into final format
    results = []
    for key, data in join_map.items():
        # Combine joining conditions (take most common or first)
        if data['joining_condition']:
            joining_condition = max(set(data['joining_condition']), key=data['joining_condition'].count)
        else:
            joining_condition = ''
        
        # Combine remarks
        remarks = '; '.join(set([r for r in data['remarks'] if r]))
        
        results.append({
            'table1': data['table1'],
            'table2': data['table2'],
            'joining_condition': joining_condition,
            'remarks': remarks
        })
    
    return results


def merge_chart_filter_conditions(chart_metadata_list: List[ChartMetadata]) -> str:
    """
    Merge filter conditions from all charts into unified dashboard-level documentation.
    
    Args:
        chart_metadata_list: List of ChartMetadata objects
        
    Returns:
        Combined filter conditions string
    """
    content_lines = []
    
    for chart_meta in chart_metadata_list:
        if chart_meta.filter_conditions:
            content_lines.append(chart_meta.filter_conditions)
            content_lines.append("\n")
    
    return "\n".join(content_lines)


def merge_chart_definitions(chart_metadata_list: List[ChartMetadata]) -> List[Dict]:
    """
    Merge term definitions from all charts into unified dashboard-level definitions.
    
    Args:
        chart_metadata_list: List of ChartMetadata objects
        
    Returns:
        List of merged term definition dicts
    """
    # Group by term
    term_map = {}
    
    for chart_meta in chart_metadata_list:
        for definition in chart_meta.definitions:
            term = definition.get('term', '')
            
            if not term:
                continue
            
            if term not in term_map:
                term_map[term] = {
                    'term': term,
                    'type': definition.get('type', ''),
                    'definition': [],
                    'business_alias': [],
                    'source_charts': []
                }
            
            if definition.get('definition'):
                term_map[term]['definition'].append(definition['definition'])
            if definition.get('business_alias'):
                term_map[term]['business_alias'].append(definition['business_alias'])
            
            term_map[term]['source_charts'].append({
                'chart_id': definition.get('source_chart_id'),
                'chart_name': definition.get('source_chart_name')
            })
    
    # Merge into final format
    results = []
    for term, data in term_map.items():
        # Combine definitions (take longest/most comprehensive)
        definitions = [d for d in data['definition'] if d]
        if definitions:
            definition = max(definitions, key=len)
        else:
            definition = ''
        
        # Combine business aliases
        business_alias = ', '.join(set([a for a in data['business_alias'] if a]))
        
        results.append({
            'term': term,
            'type': data['type'],
            'definition': definition,
            'business_alias': business_alias
        })
    
    return results

