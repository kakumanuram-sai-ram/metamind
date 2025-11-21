"""
Main entry point for multi-dashboard metadata processing.

This script orchestrates the complete workflow:
1. Extract metadata for each dashboard individually
2. Merge metadata from all dashboards
3. Build knowledge base from merged metadata
"""
import os
import sys
import argparse
from typing import List, Optional

# Add scripts directory to path for imports
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from orchestrator import DashboardMetadataOrchestrator
from merger import MetadataMerger
from knowledge_base_builder import KnowledgeBaseBuilder


def process_multiple_dashboards(
    dashboard_ids: List[int],
    extract: bool = True,
    merge: bool = True,
    build_kb: bool = True,
    continue_on_error: bool = True,
    parallel: bool = True,
    incremental_merge: Optional[bool] = None
):
    """
    Process multiple dashboards through the complete workflow.
    
    Args:
        dashboard_ids: List of dashboard IDs to process
        extract: Whether to extract metadata for each dashboard
        merge: Whether to merge metadata from all dashboards
        build_kb: Whether to build knowledge base from merged metadata
        continue_on_error: Whether to continue if extraction fails for a dashboard
    """
    print("\n" + "="*80)
    print("MULTI-DASHBOARD METADATA PROCESSING")
    print("="*80)
    print(f"Dashboard IDs: {', '.join(map(str, dashboard_ids))}")
    print(f"Steps: Extract={extract}, Merge={merge}, Build KB={build_kb}")
    print("="*80 + "\n")
    
    # Step 1: Extract metadata for each dashboard
    if extract:
        print("\n" + "="*80)
        print("STEP 1: EXTRACTING METADATA FOR EACH DASHBOARD")
        print("="*80)
        
        orchestrator = DashboardMetadataOrchestrator(
            dashboard_ids=dashboard_ids,
            continue_on_error=continue_on_error,
            parallel=parallel
        )
        results = orchestrator.extract_all()
        
        # Check if we have any successful extractions
        successful_ids = orchestrator.get_successful_dashboard_ids()
        if not successful_ids:
            print("\n❌ No dashboards were successfully extracted. Cannot proceed with merge.")
            return
        
        if len(successful_ids) < len(dashboard_ids):
            print(f"\n⚠️  Only {len(successful_ids)}/{len(dashboard_ids)} dashboards extracted successfully.")
            print(f"   Proceeding with successful dashboards: {successful_ids}")
            dashboard_ids = successful_ids
    
    # Step 2: Merge metadata from all dashboards
    if merge:
        print("\n" + "="*80)
        print("STEP 2: MERGING METADATA FROM ALL DASHBOARDS")
        print("="*80)
        
        try:
            merger = MetadataMerger(dashboard_ids=dashboard_ids)
            # Determine if we should do incremental merge
            if incremental_merge is None:
                # Auto-detect: merge with existing if it exists
                include_existing = os.path.exists("extracted_meta/merged_metadata/consolidated_table_metadata.csv")
            else:
                include_existing = incremental_merge
            
            merged_summary = merger.merge_all(include_existing_merged=include_existing)
            
            print(f"\n✅ Merge completed successfully")
            print(f"   Merged files saved to: extracted_meta/merged_metadata/")
            if include_existing:
                print(f"   ℹ️  Incremental merge: New dashboards merged with existing consolidated metadata")
            
        except Exception as e:
            print(f"\n❌ Merge failed: {str(e)}")
            import traceback
            traceback.print_exc()
            if build_kb:
                print("\n⚠️  Skipping knowledge base build due to merge failure.")
                build_kb = False
    
    # Step 3: Build knowledge base
    if build_kb:
        print("\n" + "="*80)
        print("STEP 3: BUILDING KNOWLEDGE BASE")
        print("="*80)
        
        try:
            kb_builder = KnowledgeBaseBuilder()
            unified_kb = kb_builder.build_from_merged_metadata()
            
            print(f"\n✅ Knowledge base built successfully")
            print(f"   Knowledge base files saved to: extracted_meta/knowledge_base/")
            
        except Exception as e:
            print(f"\n❌ Knowledge base build failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Final summary
    print("\n" + "="*80)
    print("PROCESSING COMPLETE")
    print("="*80)
    print("\nOutput Structure:")
    print("  📁 extracted_meta/")
    print("    📁 {dashboard_id}/          - Individual dashboard metadata (for debugging)")
    print("    📁 merged_metadata/         - Consolidated metadata (master schema)")
    print("      📄 consolidated_table_metadata.csv")
    print("      📄 consolidated_columns_metadata.csv")
    print("      📄 consolidated_joining_conditions.csv")
    print("      📄 consolidated_definitions.csv")
    print("      📄 consolidated_filter_conditions.txt")
    print("      📄 conflicts_report.json")
    print("      📄 merged_metadata.json")
    print("    📁 knowledge_base/          - Knowledge base for LLM/documentation")
    print("      📄 table_metadata.json")
    print("      📄 column_metadata.json")
    print("      📄 joining_conditions.json")
    print("      📄 definitions.json")
    print("      📄 filter_conditions.txt")
    print("      📄 business_context.json (empty)")
    print("      📄 validations.json (empty)")
    print("      📄 knowledge_base.zip (compressed archive of all 7 files)")
    print("="*80 + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process multiple dashboards: extract, merge, and build knowledge base'
    )
    parser.add_argument(
        'dashboard_ids',
        type=int,
        nargs='+',
        help='Dashboard IDs to process (space-separated)'
    )
    parser.add_argument(
        '--skip-extract',
        action='store_true',
        help='Skip extraction step (assume metadata already extracted)'
    )
    parser.add_argument(
        '--skip-merge',
        action='store_true',
        help='Skip merge step'
    )
    parser.add_argument(
        '--skip-kb',
        action='store_true',
        help='Skip knowledge base build step'
    )
    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='Stop processing if any dashboard extraction fails'
    )
    parser.add_argument(
        '--incremental-merge',
        action='store_true',
        help='Merge new dashboards with existing merged_metadata (if it exists)'
    )
    parser.add_argument(
        '--no-incremental-merge',
        action='store_true',
        help='Force fresh merge (ignore existing merged_metadata)'
    )
    
    args = parser.parse_args()
    
    try:
        # Determine incremental_merge setting
        incremental_merge = None
        if args.incremental_merge:
            incremental_merge = True
        elif args.no_incremental_merge:
            incremental_merge = False
        
        process_multiple_dashboards(
            dashboard_ids=args.dashboard_ids,
            extract=not args.skip_extract,
            merge=not args.skip_merge,
            build_kb=not args.skip_kb,
            continue_on_error=not args.stop_on_error,
            incremental_merge=incremental_merge
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

