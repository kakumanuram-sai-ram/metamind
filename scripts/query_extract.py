"""
Superset Dashboard Information Extractor

This module provides functions to extract comprehensive information about
Superset dashboards, charts, datasets, and queries using the Superset REST API.

Usage:
    extractor = SupersetExtractor(base_url, headers)
    dashboard_info = extractor.extract_dashboard_complete_info(dashboard_id)
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class ChartInfo:
    """Data class to store chart information"""
    chart_id: int
    chart_name: str
    chart_type: str
    dataset_id: int
    dataset_name: str
    database_name: str
    sql_query: Optional[str]
    metrics: List[Dict[str, Any]]
    columns: List[str]
    groupby_columns: List[str]
    filters: List[Dict[str, Any]]
    time_range: Optional[str]


@dataclass
class DashboardInfo:
    """Data class to store dashboard information"""
    dashboard_id: int
    dashboard_title: str
    dashboard_url: str
    owner: str
    created_on: str
    changed_on: str
    charts: List[ChartInfo]


class SupersetExtractor:
    """
    A class to extract information from Apache Superset via REST API
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the Superset extractor
        
        Args:
            base_url: Base URL of Superset instance (e.g., 'https://cdp-dataview.platform.mypaytm.com')
            headers: Optional headers including authentication tokens
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if headers:
            self.session.headers.update(headers)
        
        # Default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, silent: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Make an API request with error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            silent: If True, suppress error messages (for non-critical endpoints)
            **kwargs: Additional arguments for requests (headers will be merged with session headers)
            
        Returns:
            Response JSON as dictionary, or empty dict if silent=True and request fails
            
        Raises:
            requests.exceptions.RequestException: If request fails and silent=False
        """
        url = f"{self.base_url}{endpoint}"
        
        # Merge any additional headers with session headers
        if 'headers' in kwargs:
            merged_headers = self.session.headers.copy()
            merged_headers.update(kwargs['headers'])
            kwargs['headers'] = merged_headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if not silent:
                print(f"Error making request to {url}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response: {e.response.text[:200]}")
            if silent:
                return {}
            raise
    
    def get_dashboard_metadata(self, dashboard_id: int) -> Dict[str, Any]:
        """
        Get dashboard metadata including all charts
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            Dictionary with dashboard metadata
        """
        endpoint = f"/api/v1/dashboard/{dashboard_id}"
        response = self._make_request('GET', endpoint)
        return response.get('result', {})
    
    def get_chart_details(self, chart_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific chart
        
        Args:
            chart_id: Chart ID
            
        Returns:
            Dictionary with chart details
        """
        endpoint = f"/api/v1/chart/{chart_id}"
        response = self._make_request('GET', endpoint)
        return response.get('result', {})
    
    def get_dataset_details(self, dataset_id: int) -> Dict[str, Any]:
        """
        Get dataset/table details including columns and metrics
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Dictionary with dataset details
        """
        endpoint = f"/api/v1/dataset/{dataset_id}"
        response = self._make_request('GET', endpoint)
        return response.get('result', {})
    
    def get_chart_data_and_query(self, chart_id: int, dataset_id: int, 
                                 query_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get the actual SQL query and data for a chart.
        Uses Cookie and X-CSRFToken for authentication (no Bearer token required).
        If this fails, the SQL query can still be obtained from the dataset definition.
        
        Args:
            chart_id: Chart ID
            dataset_id: Dataset ID
            query_context: Query context from chart (optional)
            
        Returns:
            Dictionary with query and data, or empty dict if unavailable
        """
        # Add headers required for chart data endpoints (CSRF protection)
        # These work with Cookie + X-CSRFToken authentication (Google Auth)
        additional_headers = {
            'Referer': f"{self.base_url}/superset/dashboard/",
            'Origin': self.base_url,  # Often required along with Referer for CSRF
        }
        
        # Try the simpler endpoint first
        import time
        start_time = time.time()
        endpoint = f"/api/v1/chart/{chart_id}/data"
        print(f"      → Calling GET {endpoint}...", flush=True)
        try:
            response = self._make_request('GET', endpoint, silent=True, headers=additional_headers)
            elapsed = time.time() - start_time
            if response:
                print(f"      ✅ GET endpoint succeeded in {elapsed:.2f}s", flush=True)
                return response
            else:
                print(f"      ⚠️  GET endpoint returned empty (took {elapsed:.2f}s)", flush=True)
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"      ❌ GET endpoint failed after {elapsed:.2f}s: {e}", flush=True)
        
        # If that fails and we have query_context, try POST endpoint
        if query_context:
            start_time = time.time()
            endpoint = "/api/v1/chart/data"
            print(f"      → Trying POST {endpoint}...", flush=True)
            # Extract queries from query_context properly
            queries = query_context.get('queries', []) if isinstance(query_context, dict) else []
            if not queries and isinstance(query_context, dict):
                # If query_context itself is a query, wrap it
                queries = [query_context]
            elif not queries:
                queries = [query_context] if query_context else []
            
            payload = {
                "datasource": {
                    "id": dataset_id,
                    "type": "table"
                },
                "queries": queries
            }
            
            try:
                response = self._make_request('POST', endpoint, silent=True, json=payload, headers=additional_headers)
                elapsed = time.time() - start_time
                if response:
                    print(f"      ✅ POST endpoint succeeded in {elapsed:.2f}s", flush=True)
                    return response
                else:
                    print(f"      ⚠️  POST endpoint returned empty (took {elapsed:.2f}s)", flush=True)
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"      ❌ POST endpoint failed after {elapsed:.2f}s: {e}", flush=True)
        
        print(f"      ⚠️  No chart data retrieved, will use dataset SQL if available", flush=True)
        return {}
    
    def parse_chart_metrics(self, chart_detail: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract metrics from chart configuration
        
        Args:
            chart_detail: Chart detail dictionary
            
        Returns:
            List of metric dictionaries
        """
        metrics = []
        
        # Try to get from params
        params_str = chart_detail.get('params', '{}')
        try:
            params = json.loads(params_str) if isinstance(params_str, str) else params_str
            metrics = params.get('metrics', [])
        except:
            pass
        
        # Try to get from query_context
        if not metrics:
            query_context_str = chart_detail.get('query_context', '{}')
            try:
                query_context = json.loads(query_context_str) if isinstance(query_context_str, str) else query_context_str
                queries = query_context.get('queries', [{}])
                if queries:
                    metrics = queries[0].get('metrics', [])
            except:
                pass
        
        return metrics
    
    def parse_chart_columns(self, chart_detail: Dict[str, Any]) -> tuple:
        """
        Extract columns and groupby columns from chart configuration
        
        Args:
            chart_detail: Chart detail dictionary
            
        Returns:
            Tuple of (columns, groupby_columns)
        """
        columns = []
        groupby = []
        
        # Try to get from params
        params_str = chart_detail.get('params', '{}')
        try:
            params = json.loads(params_str) if isinstance(params_str, str) else params_str
            columns = params.get('columns', [])
            groupby = params.get('groupby', [])
        except:
            pass
        
        # Try to get from query_context
        if not columns and not groupby:
            query_context_str = chart_detail.get('query_context', '{}')
            try:
                query_context = json.loads(query_context_str) if isinstance(query_context_str, str) else query_context_str
                queries = query_context.get('queries', [{}])
                if queries:
                    columns = queries[0].get('columns', [])
                    groupby = queries[0].get('groupby', [])
            except:
                pass
        
        return columns, groupby
    
    def parse_chart_filters(self, chart_detail: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract filters from chart configuration
        
        Args:
            chart_detail: Chart detail dictionary
            
        Returns:
            List of filter dictionaries
        """
        filters = []
        
        # Try to get from params
        params_str = chart_detail.get('params', '{}')
        try:
            params = json.loads(params_str) if isinstance(params_str, str) else params_str
            filters = params.get('adhoc_filters', [])
        except:
            pass
        
        return filters
    
    def parse_time_range(self, chart_detail: Dict[str, Any]) -> Optional[str]:
        """
        Extract time range from chart configuration
        
        Args:
            chart_detail: Chart detail dictionary
            
        Returns:
            Time range string or None
        """
        # Try to get from params
        params_str = chart_detail.get('params', '{}')
        try:
            params = json.loads(params_str) if isinstance(params_str, str) else params_str
            return params.get('time_range', None)
        except:
            pass
        
        return None
    
    def extract_chart_info(self, chart_id: int, chart_name: str) -> Optional[ChartInfo]:
        """
        Extract complete information for a single chart
        
        Args:
            chart_id: Chart ID
            chart_name: Chart name/label
            
        Returns:
            ChartInfo object or None if extraction fails
        """
        try:
            # Get chart details
            print(f"  Extracting chart ID: {chart_id}")
            chart_detail = self.get_chart_details(chart_id)
            
            # Get actual chart name from API response (more accurate)
            actual_chart_name = chart_detail.get('slice_name') or chart_detail.get('chart_name') or chart_name
            
            # Get dataset_id from different possible locations
            dataset_id = chart_detail.get('datasource_id')
            
            # Try to get from query_context
            if not dataset_id:
                query_context_str = chart_detail.get('query_context', '{}')
                try:
                    query_context = json.loads(query_context_str) if isinstance(query_context_str, str) else query_context_str
                    datasource = query_context.get('datasource', {})
                    if isinstance(datasource, dict):
                        dataset_id = datasource.get('id')
                except:
                    pass
            
            # Try to get from params (format: "1476__table")
            if not dataset_id:
                params_str = chart_detail.get('params', '{}')
                try:
                    params = json.loads(params_str) if isinstance(params_str, str) else params_str
                    datasource_param = params.get('datasource', '')
                    if isinstance(datasource_param, str) and '__' in datasource_param:
                        dataset_id = int(datasource_param.split('__')[0])
                except:
                    pass
            
            if not dataset_id:
                print(f"  Warning: No dataset_id found for chart {chart_id}")
                return None
            
            dataset = self.get_dataset_details(dataset_id)
            dataset_name = dataset.get('table_name', 'Unknown')
            database_name = dataset.get('database', {}).get('database_name', 'Unknown')
            
            # Get chart type
            chart_type = chart_detail.get('viz_type', 'unknown')
            
            # Parse metrics and columns
            metrics = self.parse_chart_metrics(chart_detail)
            columns, groupby = self.parse_chart_columns(chart_detail)
            filters = self.parse_chart_filters(chart_detail)
            time_range = self.parse_time_range(chart_detail)
            
            # Get SQL query
            sql_query = None
            query_context_str = chart_detail.get('query_context')
            query_context = None
            
            if query_context_str:
                try:
                    query_context = json.loads(query_context_str) if isinstance(query_context_str, str) else query_context_str
                except:
                    pass
            
            # Get chart data - this is required for complete extraction
            print(f"    Getting chart data for chart {chart_id}...", flush=True)
            chart_data = self.get_chart_data_and_query(chart_id, dataset_id, query_context)
            if chart_data:
                print(f"    ✅ Chart data retrieved for chart {chart_id}", flush=True)
            else:
                print(f"    ⚠️  Chart data not available for chart {chart_id} (will use dataset SQL if available)", flush=True)
            
            # Extract SQL from response
            if chart_data:
                results = chart_data.get('result', [])
                if results and len(results) > 0:
                    sql_query = results[0].get('query', None)
            
            # If no SQL found from data endpoint, check if dataset has a SQL definition
            if not sql_query:
                sql_query = dataset.get('sql', None)
            
            # Get all column names from dataset
            all_columns = [col.get('column_name') for col in dataset.get('columns', [])]
            
            return ChartInfo(
                chart_id=chart_id,
                chart_name=actual_chart_name,
                chart_type=chart_type,
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                database_name=database_name,
                sql_query=sql_query,
                metrics=metrics,
                columns=all_columns,
                groupby_columns=groupby,
                filters=filters,
                time_range=time_range
            )
            
        except Exception as e:
            print(f"  Error extracting chart {chart_id}: {e}")
            return None
    
    def extract_dashboard_complete_info(self, dashboard_id: int) -> DashboardInfo:
        """
        Extract complete information for a dashboard including all charts
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            DashboardInfo object with complete information
        """
        print(f"Extracting dashboard {dashboard_id}...")
        
        # Get dashboard metadata
        dashboard = self.get_dashboard_metadata(dashboard_id)
        
        dashboard_title = dashboard.get('dashboard_title', 'Unknown')
        dashboard_url = dashboard.get('url', '')
        
        # Try to get owner from different possible fields
        owner = 'Unknown'
        if dashboard.get('owners'):
            owner = dashboard.get('owners', [{}])[0].get('username', 'Unknown')
        elif dashboard.get('changed_by'):
            changed_by = dashboard.get('changed_by', {})
            owner = f"{changed_by.get('first_name', '')} {changed_by.get('last_name', '')}".strip() or 'Unknown'
        
        created_on = dashboard.get('created_on', '')
        changed_on = dashboard.get('changed_on', '')
        
        print(f"Dashboard: {dashboard_title}")
        
        # Extract chart IDs from json_metadata
        chart_ids = []
        chart_names_map = {}
        
        # Get chart names from charts array (if available)
        chart_names_list = dashboard.get('charts', [])
        
        # Parse json_metadata to get chart IDs
        json_metadata_str = dashboard.get('json_metadata', '{}')
        try:
            if isinstance(json_metadata_str, str):
                json_metadata = json.loads(json_metadata_str)
            else:
                json_metadata = json_metadata_str
            
            # Get chart IDs from global_chart_configuration.chartsInScope
            global_config = json_metadata.get('global_chart_configuration', {})
            chart_ids = global_config.get('chartsInScope', [])
            
            # Also check chart_configuration for additional chart IDs
            chart_config = json_metadata.get('chart_configuration', {})
            for chart_id_str in chart_config.keys():
                chart_id = int(chart_id_str) if chart_id_str.isdigit() else None
                if chart_id and chart_id not in chart_ids:
                    chart_ids.append(chart_id)
            
            # Convert all to integers
            chart_ids = [int(cid) for cid in chart_ids if str(cid).isdigit()]
            
        except Exception as e:
            print(f"Warning: Could not parse json_metadata: {e}")
            # Fallback: try to get from slices (old format)
            chart_ids = [chart.get('id') for chart in dashboard.get('slices', []) if chart.get('id')]
        
        print(f"Total charts found: {len(chart_ids)}")
        
        # Extract info for each chart
        charts_info = []
        for idx, chart_id in enumerate(chart_ids):
            # Try to get chart name from the list if available
            chart_name = chart_names_list[idx] if idx < len(chart_names_list) else f"Chart {chart_id}"
            
            print(f"  Extracting chart ID: {chart_id} ({idx+1}/{len(chart_ids)})", flush=True)
            try:
                chart_info = self.extract_chart_info(chart_id, chart_name)
                if chart_info:
                    charts_info.append(chart_info)
                    print(f"  ✅ Chart {chart_id} extracted successfully", flush=True)
                else:
                    print(f"  ⚠️  Chart {chart_id} extraction returned None", flush=True)
            except Exception as e:
                import traceback
                print(f"  ❌ Error extracting chart {chart_id}: {e}", flush=True)
                print(f"  Traceback: {traceback.format_exc()}", flush=True)
                # Continue with next chart instead of failing completely
                continue
            if chart_info:
                charts_info.append(chart_info)
        
        return DashboardInfo(
            dashboard_id=dashboard_id,
            dashboard_title=dashboard_title,
            dashboard_url=f"{self.base_url}{dashboard_url}" if dashboard_url else f"{self.base_url}/superset/dashboard/{dashboard_id}/",
            owner=owner,
            created_on=created_on,
            changed_on=changed_on,
            charts=charts_info
        )
    
    def export_to_json(self, dashboard_info: DashboardInfo, filename: str = None):
        """
        Export dashboard information to JSON file
        
        Args:
            dashboard_info: DashboardInfo object
            filename: Output filename (default: extracted_meta/{id}/{id}_json.json)
        """
        import os
        if not filename:
            # Create extracted_meta/{dashboard_id} directory if it doesn't exist
            dashboard_dir = f"extracted_meta/{dashboard_info.dashboard_id}"
            os.makedirs(dashboard_dir, exist_ok=True)
            filename = f"{dashboard_dir}/{dashboard_info.dashboard_id}_json.json"
        
        data = asdict(dashboard_info)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nExported to {filename}")
    
    def export_to_csv(self, dashboard_info: DashboardInfo, filename: str = None):
        """
        Export dashboard information to CSV file with chart id, label, and query.
        
        Args:
            dashboard_info: DashboardInfo object
            filename: Output filename (default: extracted_meta/{id}/{id}_csv.csv)
        """
        import os
        if not filename:
            # Create extracted_meta/{dashboard_id} directory if it doesn't exist
            dashboard_dir = f"extracted_meta/{dashboard_info.dashboard_id}"
            os.makedirs(dashboard_dir, exist_ok=True)
            filename = f"{dashboard_dir}/{dashboard_info.dashboard_id}_csv.csv"
        
        # Flatten the data for CSV - focusing on id, label (chart_name), and query
        rows = []
        for chart in dashboard_info.charts:
            rows.append({
                'chart_id': chart.chart_id,
                'chart_name': chart.chart_name,  # This is the label
                'sql_query': chart.sql_query if chart.sql_query else '',
                'dashboard_id': dashboard_info.dashboard_id,
                'dashboard_title': dashboard_info.dashboard_title,
                'chart_type': chart.chart_type,
                'dataset_id': chart.dataset_id,
                'dataset_name': chart.dataset_name,
                'database_name': chart.database_name,
                'time_range': chart.time_range if chart.time_range else '',
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"\nExported to {filename}")
        print(f"Total charts exported: {len(rows)}")
    
    def export_sql_queries(self, dashboard_info: DashboardInfo, filename: str = None):
        """
        Export SQL queries to a file.
        
        Args:
            dashboard_info: DashboardInfo object
            filename: Output filename (default: extracted_meta/{id}/{id}_queries.sql)
        """
        import os
        if not filename:
            # Create extracted_meta/{dashboard_id} directory if it doesn't exist
            dashboard_dir = f"extracted_meta/{dashboard_info.dashboard_id}"
            os.makedirs(dashboard_dir, exist_ok=True)
            filename = f"{dashboard_dir}/{dashboard_info.dashboard_id}_queries.sql"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"-- SQL Queries for Dashboard: {dashboard_info.dashboard_title}\n")
            f.write(f"-- Dashboard ID: {dashboard_info.dashboard_id}\n")
            f.write(f"-- Total Charts: {len(dashboard_info.charts)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, chart in enumerate(dashboard_info.charts, 1):
                f.write(f"-- Chart {i}: {chart.chart_name} (ID: {chart.chart_id})\n")
                f.write(f"-- Chart Type: {chart.chart_type}\n")
                f.write(f"-- Dataset: {chart.dataset_name}\n")
                f.write(f"-- Database: {chart.database_name}\n")
                f.write("-" * 80 + "\n")
                
                if chart.sql_query:
                    f.write(chart.sql_query)
                    f.write("\n")
                else:
                    f.write("-- No SQL query available for this chart\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
        
        print(f"\nExported SQL queries to {filename}")