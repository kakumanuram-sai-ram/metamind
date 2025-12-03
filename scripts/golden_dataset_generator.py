"""
Golden Dataset Generator

This script generates a golden dataset of natural language questions paired with SQL queries
from dashboard metadata. It uses LLM to convert SQL queries into natural language questions
that a user might ask.

Output: CSV with columns: dashboard_id, chart_id, chart_name, user_query, sql_query
"""

import json
import os
import sys
import pandas as pd
from typing import Dict, List, Optional
import dspy
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL


class SQLToQuestionSignature(dspy.Signature):
    """Convert a SQL query and chart metadata into a natural language question a user might ask."""
    
    chart_name = dspy.InputField(desc="The name/title of the chart")
    dashboard_title = dspy.InputField(desc="The title of the dashboard this chart belongs to")
    sql_query = dspy.InputField(desc="The SQL query that generates the chart data")
    
    user_question = dspy.OutputField(
        desc="A natural language question that a user might ask to get this data. "
             "The question should be clear, concise, and reflect what the chart shows. "
             "Do not include implementation details like table names or SQL syntax. "
             "Focus on the business question being answered."
    )


class GoldenDatasetGenerator:
    """Generates golden dataset from dashboard metadata using LLM."""
    
    def __init__(self, api_key: str, model: str, base_url: str):
        """
        Initialize the generator with LLM configuration.
        
        Args:
            api_key: API key for LLM service
            model: Model name (e.g., 'anthropic/claude-sonnet-4')
            base_url: Base URL for LLM API
        """
        # Configure DSPy LLM
        self.lm = dspy.LM(
            model=model,
            api_key=api_key,
            api_base=base_url,
            cache=False
        )
        dspy.configure(lm=self.lm)
        
        # Initialize the predictor
        self.question_generator = dspy.ChainOfThought(SQLToQuestionSignature)
        
    def generate_question_for_chart(
        self, 
        chart: Dict, 
        dashboard_title: str
    ) -> Optional[str]:
        """
        Generate a natural language question for a single chart.
        
        Args:
            chart: Chart metadata dictionary
            dashboard_title: Title of the dashboard
            
        Returns:
            Generated user question or None if generation fails
        """
        try:
            chart_name = chart.get('chart_name', 'Unnamed Chart')
            sql_query = chart.get('sql_query', '')
            
            if not sql_query or sql_query.strip() == '':
                print(f"  ⚠️  Skipping chart {chart.get('chart_id')} - no SQL query")
                return None
            
            # Truncate very long SQL queries for the LLM (keep first 2000 chars)
            truncated_sql = sql_query[:2000] if len(sql_query) > 2000 else sql_query
            
            print(f"  → Generating question for: {chart_name}")
            
            # Generate the question using DSPy
            result = self.question_generator(
                chart_name=chart_name,
                dashboard_title=dashboard_title,
                sql_query=truncated_sql
            )
            
            user_question = result.user_question.strip()
            
            # Clean up the question (remove quotes if present)
            if user_question.startswith('"') and user_question.endswith('"'):
                user_question = user_question[1:-1]
            if user_question.startswith("'") and user_question.endswith("'"):
                user_question = user_question[1:-1]
            
            print(f"  ✅ Generated: {user_question[:100]}...")
            
            return user_question
            
        except Exception as e:
            print(f"  ❌ Error generating question for chart {chart.get('chart_id')}: {str(e)}")
            return None
    
    def process_dashboard(
        self, 
        dashboard_json_path: str,
        output_csv_path: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Process a dashboard JSON file and generate questions for all charts.
        
        Args:
            dashboard_json_path: Path to dashboard JSON file
            output_csv_path: Optional path to save CSV output
            
        Returns:
            DataFrame with columns: dashboard_id, chart_id, chart_name, user_query, sql_query
        """
        print(f"\n{'='*80}")
        print(f"Processing Dashboard: {dashboard_json_path}")
        print(f"{'='*80}\n")
        
        # Load the dashboard JSON
        with open(dashboard_json_path, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)
        
        dashboard_id = dashboard_data.get('dashboard_id')
        dashboard_title = dashboard_data.get('dashboard_title', 'Unnamed Dashboard')
        charts = dashboard_data.get('charts', [])
        
        print(f"Dashboard ID: {dashboard_id}")
        print(f"Dashboard Title: {dashboard_title}")
        print(f"Total Charts: {len(charts)}\n")
        
        # Generate questions for each chart
        results = []
        for idx, chart in enumerate(charts, 1):
            chart_id = chart.get('chart_id')
            chart_name = chart.get('chart_name', 'Unnamed Chart')
            sql_query = chart.get('sql_query', '')
            
            print(f"[{idx}/{len(charts)}] Chart ID: {chart_id}")
            
            # Skip charts without SQL
            if not sql_query or sql_query.strip() == '':
                print(f"  ⚠️  Skipping - no SQL query\n")
                continue
            
            # Generate the question
            user_query = self.generate_question_for_chart(chart, dashboard_title)
            
            if user_query:
                results.append({
                    'dashboard_id': dashboard_id,
                    'chart_id': chart_id,
                    'chart_name': chart_name,
                    'user_query': user_query,
                    'sql_query': sql_query
                })
            
            print()  # Blank line between charts
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        print(f"\n{'='*80}")
        print(f"✅ Generated {len(results)} question-SQL pairs")
        print(f"{'='*80}\n")
        
        # Save to CSV if path provided
        if output_csv_path:
            df.to_csv(output_csv_path, index=False, encoding='utf-8')
            print(f"💾 Saved to: {output_csv_path}\n")
        
        return df
    
    def process_multiple_dashboards(
        self,
        dashboard_ids: List[int],
        extracted_meta_dir: str = "extracted_meta",
        output_csv_path: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Process multiple dashboards and combine results.
        
        Args:
            dashboard_ids: List of dashboard IDs to process
            extracted_meta_dir: Directory containing dashboard metadata
            output_csv_path: Optional path to save combined CSV output
            
        Returns:
            Combined DataFrame with all question-SQL pairs
        """
        all_results = []
        
        for dashboard_id in dashboard_ids:
            json_path = os.path.join(
                extracted_meta_dir,
                str(dashboard_id),
                f"{dashboard_id}_json.json"
            )
            
            if not os.path.exists(json_path):
                print(f"⚠️  Dashboard {dashboard_id} JSON not found: {json_path}")
                continue
            
            try:
                df = self.process_dashboard(json_path)
                all_results.append(df)
            except Exception as e:
                print(f"❌ Error processing dashboard {dashboard_id}: {str(e)}\n")
                continue
        
        # Combine all results
        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            
            print(f"\n{'='*80}")
            print(f"🎉 TOTAL: Generated {len(combined_df)} question-SQL pairs from {len(all_results)} dashboards")
            print(f"{'='*80}\n")
            
            # Save combined results if path provided
            if output_csv_path:
                combined_df.to_csv(output_csv_path, index=False, encoding='utf-8')
                print(f"💾 Saved combined results to: {output_csv_path}\n")
            
            return combined_df
        else:
            print("⚠️  No results generated")
            return pd.DataFrame()


def main():
    """Main function to run the golden dataset generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate golden dataset of natural language questions from SQL queries"
    )
    parser.add_argument(
        'dashboard_ids',
        nargs='+',
        type=int,
        help='Dashboard ID(s) to process (e.g., 964 or 964 476 729)'
    )
    parser.add_argument(
        '--extracted-meta-dir',
        default='extracted_meta',
        help='Directory containing dashboard metadata (default: extracted_meta)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output CSV file path (default: extracted_meta/golden_dataset/golden_dataset_DASHBOARDID.csv)'
    )
    parser.add_argument(
        '--api-key',
        default=LLM_API_KEY,
        help=f'LLM API key (default: from config.py)'
    )
    parser.add_argument(
        '--model',
        default=LLM_MODEL,
        help=f'LLM model (default: {LLM_MODEL})'
    )
    parser.add_argument(
        '--base-url',
        default=LLM_BASE_URL,
        help=f'LLM API base URL (default: {LLM_BASE_URL})'
    )
    
    args = parser.parse_args()
    
    # Create golden_dataset directory if it doesn't exist
    golden_dataset_dir = os.path.join(args.extracted_meta_dir, 'golden_dataset')
    os.makedirs(golden_dataset_dir, exist_ok=True)
    
    # Determine output path
    if args.output:
        output_path = args.output
    elif len(args.dashboard_ids) == 1:
        output_path = os.path.join(
            golden_dataset_dir,
            f"golden_dataset_{args.dashboard_ids[0]}.csv"
        )
    else:
        # Multiple dashboards - use combined filename
        dashboard_str = '_'.join(map(str, args.dashboard_ids))
        output_path = os.path.join(
            golden_dataset_dir,
            f"golden_dataset_combined_{dashboard_str}.csv"
        )
    
    print(f"\n{'='*80}")
    print(f"🚀 Golden Dataset Generator")
    print(f"{'='*80}")
    print(f"Dashboard IDs: {args.dashboard_ids}")
    print(f"LLM Model: {args.model}")
    print(f"Output: {output_path}")
    print(f"{'='*80}\n")
    
    # Initialize generator
    generator = GoldenDatasetGenerator(
        api_key=args.api_key,
        model=args.model,
        base_url=args.base_url
    )
    
    # Process dashboard(s)
    if len(args.dashboard_ids) == 1:
        # Single dashboard
        json_path = os.path.join(
            args.extracted_meta_dir,
            str(args.dashboard_ids[0]),
            f"{args.dashboard_ids[0]}_json.json"
        )
        
        if not os.path.exists(json_path):
            print(f"❌ Error: Dashboard JSON not found: {json_path}")
            sys.exit(1)
        
        df = generator.process_dashboard(json_path, output_path)
    else:
        # Multiple dashboards
        df = generator.process_multiple_dashboards(
            args.dashboard_ids,
            args.extracted_meta_dir,
            output_path
        )
    
    # Display sample results
    if not df.empty:
        print(f"\n{'='*80}")
        print(f"📊 Sample Results (first 3 rows):")
        print(f"{'='*80}\n")
        
        for idx, row in df.head(3).iterrows():
            print(f"Dashboard ID: {row['dashboard_id']}")
            print(f"Chart ID: {row['chart_id']}")
            print(f"Chart Name: {row['chart_name']}")
            print(f"User Query: {row['user_query']}")
            print(f"SQL Query (first 200 chars): {row['sql_query'][:200]}...")
            print(f"-" * 80)
        
        print(f"\n✅ Generation complete! Total pairs: {len(df)}")
        print(f"📁 Saved to: {output_path}\n")
    else:
        print("\n⚠️  No data generated\n")


if __name__ == "__main__":
    main()



