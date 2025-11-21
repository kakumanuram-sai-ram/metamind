"""
Script to generate final tables_columns.csv output using DSPy extraction

This script:
1. Loads DSPy examples from dspy_examples.py
2. Uses DSPy to extract tables and columns from dashboard
3. Generates final output CSV file
4. Optionally fetches schema information from Starburst
"""
import os
import sys
import argparse
# Import from same directory (scripts/)
from llm_extractor import generate_final_tables_columns_output
from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL


def main():
    parser = argparse.ArgumentParser(
        description='Generate final tables_columns.csv output using DSPy extraction'
    )
    parser.add_argument(
        'dashboard_id',
        type=int,
        help='Dashboard ID to process'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help=f'LLM model to use (default: {LLM_MODEL} from config)'
    )
    parser.add_argument(
        '--base-url',
        type=str,
        default=None,
        help=f'API base URL (default: {LLM_BASE_URL} from config)'
    )
    parser.add_argument(
        '--fetch-schemas',
        action='store_true',
        help='Fetch schema information from Starburst'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output CSV file path (default: extracted_meta/{dashboard_id}_tables_columns.csv)'
    )
    
    args = parser.parse_args()
    
    # Get API key from args, environment, or config
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY') or LLM_API_KEY
    if not api_key:
        print("Error: API key required. Set ANTHROPIC_API_KEY env var, config.LLM_API_KEY, or use --api-key")
        sys.exit(1)
    
    # Use defaults from config if not provided
    model = args.model or LLM_MODEL
    base_url = args.base_url or LLM_BASE_URL
    
    try:
        # Generate final output
        df = generate_final_tables_columns_output(
            dashboard_id=args.dashboard_id,
            api_key=api_key,
            model=model,
            base_url=base_url,
            fetch_schemas=args.fetch_schemas,
            output_file=args.output
        )
        
        print("\n✅ Success! Final output generated.")
        print(f"\nPreview of output:")
        print(df.head(20).to_string())
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        print("\nMake sure the dashboard JSON file exists.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

