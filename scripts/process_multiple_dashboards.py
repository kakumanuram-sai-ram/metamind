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
from typing import List, Optional, Dict

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
    incremental_merge: Optional[bool] = None,
    metadata_choices: Optional[Dict[int, bool]] = None  # dashboard_id -> use_existing
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
        
        # Filter dashboards based on metadata choices
        dashboards_to_extract = []
        dashboards_to_skip = []
        
        if metadata_choices:
            for dashboard_id in dashboard_ids:
                use_existing = metadata_choices.get(dashboard_id, False)
                if use_existing:
                    # Check if metadata actually exists
                    dashboard_dir = f"extracted_meta/{dashboard_id}"
                    table_metadata_file = f"{dashboard_dir}/{dashboard_id}_table_metadata.csv"
                    if os.path.exists(table_metadata_file):
                        dashboards_to_skip.append(dashboard_id)
                        print(f"  ℹ️  Dashboard {dashboard_id}: Using existing metadata (skipping extraction)")
                    else:
                        dashboards_to_extract.append(dashboard_id)
                        print(f"  ⚠️  Dashboard {dashboard_id}: Existing metadata not found, will extract")
                else:
                    dashboards_to_extract.append(dashboard_id)
                    print(f"  📝 Dashboard {dashboard_id}: Creating fresh metadata")
        else:
            dashboards_to_extract = dashboard_ids
        
        if dashboards_to_extract:
            orchestrator = DashboardMetadataOrchestrator(
                dashboard_ids=dashboards_to_extract,
                continue_on_error=continue_on_error,
                parallel=parallel
            )
            results = orchestrator.extract_all()
        else:
            print("  ℹ️  All dashboards using existing metadata, skipping extraction")
            results = {}
        
        # Combine extracted and skipped dashboards
        if dashboards_to_extract:
            successful_ids = orchestrator.get_successful_dashboard_ids()
            # Add dashboards that were skipped (using existing)
            all_dashboard_ids = successful_ids + dashboards_to_skip
            
            if not all_dashboard_ids:
                print("\n❌ No dashboards available for merging.")
                return
            
            if len(all_dashboard_ids) < len(dashboard_ids):
                print(f"\n⚠️  Only {len(all_dashboard_ids)}/{len(dashboard_ids)} dashboards available.")
                print(f"   Proceeding with available dashboards: {all_dashboard_ids}")
            dashboard_ids = all_dashboard_ids
        else:
            # All using existing metadata
            dashboard_ids = dashboards_to_skip
    
    # Step 2: Merge metadata from all dashboards
    if merge:
        print("\n" + "="*80)
        print("STEP 2: MERGING METADATA FROM ALL DASHBOARDS")
        print("="*80)
        
        try:
            merger = MetadataMerger(dashboard_ids=dashboard_ids)
            # Determine merge strategy based on metadata choices
            if incremental_merge is None:
                # If any dashboard is using existing metadata, we might want to merge with existing merged_metadata
                # But if all are fresh, we create fresh merge
                has_existing_merged = os.path.exists("extracted_meta/merged_metadata/consolidated_table_metadata.csv")
                
                # Check if we should merge with existing based on choices
                # If all dashboards are fresh, don't merge with existing
                # If some are using existing, merge with existing merged_metadata
                if metadata_choices:
                    all_fresh = all(not metadata_choices.get(did, False) for did in dashboard_ids)
                    include_existing = has_existing_merged and not all_fresh
                else:
                    # Default: merge with existing if it exists
                    include_existing = has_existing_merged
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
        
        # Wait for all metadata files to be ready before building KB
        from progress_tracker import get_progress_tracker
        progress_tracker = get_progress_tracker()
        
        print("\n⏳ Checking if all dashboard metadata files are ready...")
        max_wait_time = 3600  # Maximum wait time: 1 hour
        check_interval = 5  # Check every 5 seconds
        waited_time = 0
        
        while not progress_tracker.are_all_metadata_files_ready(dashboard_ids):
            if waited_time >= max_wait_time:
                print(f"\n⚠️  Timeout: Waited {max_wait_time} seconds for metadata files. Proceeding with KB build anyway.")
                break
            
            print(f"  Waiting for all metadata files... ({waited_time}s elapsed)")
            import time
            time.sleep(check_interval)
            waited_time += check_interval
        
        if progress_tracker.are_all_metadata_files_ready(dashboard_ids):
            print("  ✅ All metadata files are ready!")
        else:
            print("  ⚠️  Some metadata files are still missing, but proceeding with KB build...")
        
        try:
            kb_builder = KnowledgeBaseBuilder()
            unified_kb = kb_builder.build_from_merged_metadata()
            
            # Verify all files are ready before marking KB as complete
            if progress_tracker.are_all_metadata_files_ready(dashboard_ids):
                print(f"\n✅ Knowledge base built successfully")
                print(f"   Knowledge base files saved to: extracted_meta/knowledge_base/")
                # Mark KB build as completed only when all files are ready
                progress_tracker.complete_kb_build()
            else:
                print(f"\n⚠️  Knowledge base built, but waiting for all metadata files to be ready...")
                # Don't mark as complete yet - will be checked periodically
                # Keep status as 'processing' until all files are ready
                
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
    print("      📄 instruction_set.json (LLM-generated SQL agent instructions)")
    print("      📄 instruction_set.txt (human-readable version)")
    print("      📄 knowledge_base.zip (compressed archive of all files)")
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

