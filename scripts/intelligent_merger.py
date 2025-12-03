"""
Intelligent Merger Module for LLM-Based Metadata Deduplication

This module merges multi-chart/multi-dashboard metadata contexts using LLM-powered
deduplication and consolidation. It removes redundancy while preserving unique
contexts and explicitly flags conflicts for human review.

Key Features:
1. LLM-based consolidation of redundant descriptions
2. Conflict detection and flagging
3. Provenance tracking (which charts contributed)
4. Final CSVs without chart_id columns (clean output)

Output Files:
- extracted_meta/merged_metadata/consolidated_*.csv (clean, no chart_id)
- extracted_meta/merged_metadata/conflicts_report.csv (conflicts for review)
- extracted_meta/{dashboard_id}/contexts.json (full provenance)
"""

import os
import sys
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import dspy

# Add scripts directory to path for imports
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from context_storage import ChartContextStore, get_context_store

logger = logging.getLogger(__name__)


# ============================================================================
# DSPy Signatures for Intelligent Merging
# ============================================================================

class IntelligentTableMerger(dspy.Signature):
    """
    Merge multiple table descriptions from different charts.
    Remove redundancy while preserving unique contexts and use cases.
    
    CRITICAL RULES:
    1. If descriptions are similar → consolidate into ONE concise description.
    2. If different use cases → include all, organized by use case
    3. If CONFLICTING values (e.g., "daily" vs "hourly") → flag with [CONFLICT]
    4. Maximum output: 300 words (prevent bloat)
    5. Output format: Natural text description (not bullet points)
    
    Example Input:
    [
        {"chart_id": 2646, "description": "UPI P2P transfer transactions with success rates"},
        {"chart_id": 2650, "description": "UPI transactions including P2P and merchant payments"},
        {"chart_id": 2655, "description": "P2P UPI data for churn analysis"}
    ]
    
    Example Output:
    "Stores UPI transaction data across P2P and merchant payment flows. 
     Primary use cases: success rate monitoring, merchant payment analysis, 
     and churn analysis. Contains transaction-level details including 
     txn_id, amount, status, payer/payee handles, and flow categorizations."
    """
    
    table_name: str = dspy.InputField(desc="Table name being merged")
    
    chart_contexts: str = dspy.InputField(desc="""
    JSON array of table descriptions from different charts:
    [
        {
            "chart_id": 2646,
            "chart_name": "Overall SR",
            "table_description": "...",
            "refresh_frequency": "daily",
            "vertical": "payments",
            "confidence": 0.90
        },
        ...
    ]
    """)
    
    unified_table_description: str = dspy.OutputField(desc="""
    Single unified description (max 500 words) that consolidates all contexts.
    Format: Natural prose, not bullet points. Include all unique use cases.
    """)
    
    unified_refresh_frequency: str = dspy.OutputField(desc="""
    Resolved refresh frequency.
    If all agree: use that value (e.g., "daily")
    If conflict: "[CONFLICT: Chart X says daily, Chart Y says hourly]"
    """)
    
    unified_vertical: str = dspy.OutputField(desc="""
    Resolved vertical.
    If all agree: use that value.
    If multiple valid: "payments, lending" (comma-separated)
    """)
    
    conflicts_detected: str = dspy.OutputField(desc="""
    Comma-separated list of fields with conflicts.
    Format: "refresh_frequency, partition_column"
    If no conflicts: "None"
    """)
    
    redundancy_summary: str = dspy.OutputField(desc="""
    Brief summary of what redundancy was removed.
    Example: "Consolidated 8 similar descriptions of transaction data"
    """)


class IntelligentColumnMerger(dspy.Signature):
    """
    Merge column metadata from multiple charts.
    Consolidate descriptions while detecting type conflicts.
    """
    
    column_full_name: str = dspy.InputField(desc="Full column name (table.column)")
    
    chart_contexts: str = dspy.InputField(desc="JSON array of column metadata from charts")
    
    unified_column_description: str = dspy.OutputField(desc="Unified description (max 300 words)")
    
    unified_data_type: str = dspy.OutputField(desc="Resolved data type or [CONFLICT: ...]")
    
    unified_required_flag: str = dspy.OutputField(desc="Y/N or [CONFLICT: ...]")
    
    conflicts_detected: str = dspy.OutputField(desc="Comma-separated conflicts or None")


class IntelligentJoinMerger(dspy.Signature):
    """Merge joining conditions from multiple charts."""
    
    join_relationship: str = dspy.InputField(desc="Table1 <-> Table2 relationship")
    
    chart_contexts: str = dspy.InputField(desc="JSON array of join conditions")
    
    unified_join_condition: str = dspy.OutputField(desc="Unified join condition")
    
    relationship_type: str = dspy.OutputField(desc="one-to-many, many-to-many, etc.")
    
    conflicts_detected: str = dspy.OutputField(desc="Any conflicts in join logic")


class IntelligentDefinitionMerger(dspy.Signature):
    """Merge term definitions from multiple charts."""
    
    term: str = dspy.InputField(desc="Term being defined")
    
    chart_contexts: str = dspy.InputField(desc="JSON array of definitions")
    
    unified_definition: str = dspy.OutputField(desc="Unified definition (max 200 words)")
    
    unified_type: str = dspy.OutputField(desc="Metric, Calculated Field, Synonym, or Category")
    
    conflicts_detected: str = dspy.OutputField(desc="Any conflicting definitions")


# ============================================================================
# Merge Functions
# ============================================================================

def _get_merger_lm(api_key: str, model: str, base_url: str):
    """Get configured DSPy LM for merger operations."""
    if base_url:
        model_name = f"anthropic/{model}" if not model.startswith("anthropic/") else model
        clean_base_url = base_url.rstrip('/v1').rstrip('/')
        lm = dspy.LM(
            model=model_name,
            api_key=api_key,
            api_provider="anthropic",
            api_base=clean_base_url
        )
    else:
        lm = dspy.LM(
            model=model,
            api_key=api_key,
            api_provider="anthropic"
        )
    
    try:
        dspy.configure(lm=lm)
    except RuntimeError:
        pass  # Already configured
    
    return lm


def merge_table_metadata_with_deduplication(
    table_name: str,
    contexts: List[Dict],
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> Dict:
    """
    Merge table contexts using LLM deduplication.
    
    Args:
        table_name: Table being merged
        contexts: List of per-chart contexts
        api_key, model, base_url: LLM config
    
    Returns:
        {
            'table_name': 'hive.cdo.fact_upi_transactions',
            'table_description': 'Unified description...',
            'refresh_frequency': 'daily',
            'vertical': 'payments',
            'partition_column': 'transaction_date_key',
            'remarks': '...',
            'relationship_context': '...',
            'confidence_score': 0.88,
            'conflicts': '[CONFLICT: refresh_frequency]' or None
        }
    """
    api_key = api_key or LLM_API_KEY
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    if not contexts:
        return {
            'table_name': table_name,
            'table_description': '',
            'refresh_frequency': '',
            'vertical': '',
            'partition_column': '',
            'remarks': '',
            'relationship_context': '',
            'confidence_score': 0.0,
            'conflicts': None
        }
    
    # If only one context, return it directly
    if len(contexts) == 1:
        ctx = contexts[0]
        return {
            'table_name': table_name,
            'table_description': ctx.get('metadata', {}).get('table_description', ''),
            'refresh_frequency': ctx.get('metadata', {}).get('refresh_frequency', ''),
            'vertical': ctx.get('metadata', {}).get('vertical', ''),
            'partition_column': ctx.get('metadata', {}).get('partition_column', ''),
            'remarks': ctx.get('metadata', {}).get('remarks', ''),
            'relationship_context': ctx.get('metadata', {}).get('relationship_context', ''),
            'confidence_score': ctx.get('confidence', 0.0),
            'conflicts': None
        }
    
    try:
        # Initialize DSPy LM
        _get_merger_lm(api_key, model, base_url)
        
        # Prepare contexts for LLM
        llm_contexts = []
        for ctx in contexts:
            metadata = ctx.get('metadata', {})
            llm_contexts.append({
                'chart_id': ctx.get('chart_id'),
                'chart_name': ctx.get('chart_name', ''),
                'table_description': metadata.get('table_description', ''),
                'refresh_frequency': metadata.get('refresh_frequency', ''),
                'vertical': metadata.get('vertical', ''),
                'confidence': ctx.get('confidence', 0.0)
            })
        
        contexts_json = json.dumps(llm_contexts, indent=2)
        
        # Call merger
        merger = dspy.Predict(IntelligentTableMerger)
        result = merger(
            table_name=table_name,
            chart_contexts=contexts_json
        )
        
        # Parse conflicts
        has_conflicts = result.conflicts_detected.lower() != 'none'
        
        # Calculate average confidence
        avg_confidence = sum(c.get('confidence', 0) for c in contexts) / len(contexts)
        
        # Get most common partition_column
        partition_columns = [c.get('metadata', {}).get('partition_column', '') for c in contexts]
        partition_columns = [p for p in partition_columns if p]
        partition_column = max(set(partition_columns), key=partition_columns.count) if partition_columns else ''
        
        # Merge relationship contexts
        relationship_contexts = [c.get('metadata', {}).get('relationship_context', '') for c in contexts]
        relationship_contexts = [r for r in relationship_contexts if r]
        seen = set()
        unique_rel_contexts = []
        for r in relationship_contexts:
            if r not in seen:
                unique_rel_contexts.append(r)
                seen.add(r)
        relationship_context = ' | '.join(unique_rel_contexts)
        
        return {
            'table_name': table_name,
            'table_description': result.unified_table_description,
            'refresh_frequency': result.unified_refresh_frequency,
            'vertical': result.unified_vertical,
            'partition_column': partition_column,
            'remarks': f"Merged from {len(contexts)} charts. {result.redundancy_summary}",
            'relationship_context': relationship_context,
            'confidence_score': avg_confidence,
            'conflicts': result.conflicts_detected if has_conflicts else None
        }
        
    except Exception as e:
        logger.error(f"Error merging table {table_name}: {e}")
        # Fallback: Use first context
        ctx = contexts[0]
        return {
            'table_name': table_name,
            'table_description': ctx.get('metadata', {}).get('table_description', ''),
            'refresh_frequency': ctx.get('metadata', {}).get('refresh_frequency', ''),
            'vertical': ctx.get('metadata', {}).get('vertical', ''),
            'partition_column': ctx.get('metadata', {}).get('partition_column', ''),
            'remarks': f'Merge failed: {str(e)}',
            'relationship_context': ctx.get('metadata', {}).get('relationship_context', ''),
            'confidence_score': ctx.get('confidence', 0.0),
            'conflicts': f'Merge error: {str(e)}'
        }


def merge_column_metadata_with_deduplication(
    column_full_name: str,
    contexts: List[Dict],
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> Dict:
    """
    Merge column contexts using LLM deduplication.
    
    Args:
        column_full_name: Full column name (table.column)
        contexts: List of per-chart contexts
        api_key, model, base_url: LLM config
    
    Returns:
        Merged column metadata dict
    """
    api_key = api_key or LLM_API_KEY
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    if not contexts:
        return None
    
    # If only one context, return it directly
    if len(contexts) == 1:
        ctx = contexts[0]
        metadata = ctx.get('metadata', {})
        return {
            'table_name': metadata.get('table_name', column_full_name.rsplit('.', 1)[0] if '.' in column_full_name else ''),
            'column_name': metadata.get('column_name', column_full_name.rsplit('.', 1)[-1] if '.' in column_full_name else column_full_name),
            'variable_type': metadata.get('variable_type', ''),
            'column_description': metadata.get('column_description', ''),
            'required_flag': metadata.get('required_flag', 'no'),
            'confidence_score': ctx.get('confidence', 0.0),
            'conflicts': None
        }
    
    try:
        _get_merger_lm(api_key, model, base_url)
        
        # Prepare contexts for LLM
        llm_contexts = []
        for ctx in contexts:
            metadata = ctx.get('metadata', {})
            llm_contexts.append({
                'chart_id': ctx.get('chart_id'),
                'chart_name': ctx.get('chart_name', ''),
                'column_description': metadata.get('column_description', ''),
                'variable_type': metadata.get('variable_type', ''),
                'required_flag': metadata.get('required_flag', ''),
                'confidence': ctx.get('confidence', 0.0)
            })
        
        contexts_json = json.dumps(llm_contexts, indent=2)
        
        merger = dspy.Predict(IntelligentColumnMerger)
        result = merger(
            column_full_name=column_full_name,
            chart_contexts=contexts_json
        )
        
        has_conflicts = result.conflicts_detected.lower() != 'none'
        avg_confidence = sum(c.get('confidence', 0) for c in contexts) / len(contexts)
        
        # Parse column parts
        parts = column_full_name.rsplit('.', 1)
        table_name = parts[0] if len(parts) > 1 else ''
        column_name = parts[-1]
        
        return {
            'table_name': table_name,
            'column_name': column_name,
            'variable_type': result.unified_data_type,
            'column_description': result.unified_column_description,
            'required_flag': result.unified_required_flag.lower() if result.unified_required_flag.lower() in ['yes', 'no'] else 'no',
            'confidence_score': avg_confidence,
            'conflicts': result.conflicts_detected if has_conflicts else None
        }
        
    except Exception as e:
        logger.error(f"Error merging column {column_full_name}: {e}")
        ctx = contexts[0]
        metadata = ctx.get('metadata', {})
        return {
            'table_name': metadata.get('table_name', ''),
            'column_name': metadata.get('column_name', column_full_name),
            'variable_type': metadata.get('variable_type', ''),
            'column_description': metadata.get('column_description', ''),
            'required_flag': metadata.get('required_flag', 'no'),
            'confidence_score': ctx.get('confidence', 0.0),
            'conflicts': f'Merge error: {str(e)}'
        }


def merge_join_metadata_with_deduplication(
    join_key: str,
    contexts: List[Dict],
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> Dict:
    """
    Merge joining conditions using LLM deduplication.
    """
    api_key = api_key or LLM_API_KEY
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    if not contexts:
        return None
    
    # Parse join key
    tables = join_key.split('|')
    table1 = tables[0] if len(tables) > 0 else ''
    table2 = tables[1] if len(tables) > 1 else ''
    
    if len(contexts) == 1:
        ctx = contexts[0]
        metadata = ctx.get('metadata', {})
        return {
            'table1': table1,
            'table2': table2,
            'joining_condition': metadata.get('joining_condition', ''),
            'remarks': metadata.get('remarks', ''),
            'confidence_score': ctx.get('confidence', 0.0),
            'conflicts': None
        }
    
    try:
        _get_merger_lm(api_key, model, base_url)
        
        llm_contexts = []
        for ctx in contexts:
            metadata = ctx.get('metadata', {})
            llm_contexts.append({
                'chart_id': ctx.get('chart_id'),
                'chart_name': ctx.get('chart_name', ''),
                'joining_condition': metadata.get('joining_condition', ''),
                'remarks': metadata.get('remarks', ''),
                'confidence': ctx.get('confidence', 0.0)
            })
        
        contexts_json = json.dumps(llm_contexts, indent=2)
        
        merger = dspy.Predict(IntelligentJoinMerger)
        result = merger(
            join_relationship=f"{table1} <-> {table2}",
            chart_contexts=contexts_json
        )
        
        has_conflicts = result.conflicts_detected.lower() != 'none'
        avg_confidence = sum(c.get('confidence', 0) for c in contexts) / len(contexts)
        
        return {
            'table1': table1,
            'table2': table2,
            'joining_condition': result.unified_join_condition,
            'remarks': f"Relationship type: {result.relationship_type}. Merged from {len(contexts)} charts.",
            'confidence_score': avg_confidence,
            'conflicts': result.conflicts_detected if has_conflicts else None
        }
        
    except Exception as e:
        logger.error(f"Error merging join {join_key}: {e}")
        ctx = contexts[0]
        metadata = ctx.get('metadata', {})
        return {
            'table1': table1,
            'table2': table2,
            'joining_condition': metadata.get('joining_condition', ''),
            'remarks': f'Merge error: {str(e)}',
            'confidence_score': ctx.get('confidence', 0.0),
            'conflicts': f'Merge error: {str(e)}'
        }


def merge_definition_metadata_with_deduplication(
    term: str,
    contexts: List[Dict],
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> Dict:
    """
    Merge term definitions using LLM deduplication.
    """
    api_key = api_key or LLM_API_KEY
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    if not contexts:
        return None
    
    if len(contexts) == 1:
        ctx = contexts[0]
        metadata = ctx.get('metadata', {})
        return {
            'term': term,
            'type': metadata.get('type', ''),
            'definition': metadata.get('definition', ''),
            'business_alias': metadata.get('business_alias', ''),
            'confidence_score': ctx.get('confidence', 0.0),
            'conflicts': None
        }
    
    try:
        _get_merger_lm(api_key, model, base_url)
        
        llm_contexts = []
        for ctx in contexts:
            metadata = ctx.get('metadata', {})
            llm_contexts.append({
                'chart_id': ctx.get('chart_id'),
                'chart_name': ctx.get('chart_name', ''),
                'definition': metadata.get('definition', ''),
                'type': metadata.get('type', ''),
                'business_alias': metadata.get('business_alias', ''),
                'confidence': ctx.get('confidence', 0.0)
            })
        
        contexts_json = json.dumps(llm_contexts, indent=2)
        
        merger = dspy.Predict(IntelligentDefinitionMerger)
        result = merger(
            term=term,
            chart_contexts=contexts_json
        )
        
        has_conflicts = result.conflicts_detected.lower() != 'none'
        avg_confidence = sum(c.get('confidence', 0) for c in contexts) / len(contexts)
        
        # Merge business aliases
        aliases = [c.get('metadata', {}).get('business_alias', '') for c in contexts]
        aliases = [a for a in aliases if a]
        unique_aliases = list(set(', '.join(aliases).split(', ')))
        merged_alias = ', '.join([a for a in unique_aliases if a])
        
        return {
            'term': term,
            'type': result.unified_type,
            'definition': result.unified_definition,
            'business_alias': merged_alias,
            'confidence_score': avg_confidence,
            'conflicts': result.conflicts_detected if has_conflicts else None
        }
        
    except Exception as e:
        logger.error(f"Error merging definition {term}: {e}")
        ctx = contexts[0]
        metadata = ctx.get('metadata', {})
        return {
            'term': term,
            'type': metadata.get('type', ''),
            'definition': metadata.get('definition', ''),
            'business_alias': metadata.get('business_alias', ''),
            'confidence_score': ctx.get('confidence', 0.0),
            'conflicts': f'Merge error: {str(e)}'
        }


def _assess_conflict_severity(conflicts: str) -> str:
    """
    Assess conflict severity based on field types.
    
    HIGH: Data type conflicts, required flag conflicts
    MEDIUM: Refresh frequency conflicts
    LOW: Description wording differences
    """
    if not conflicts or conflicts.lower() == 'none':
        return 'NONE'
    
    conflicts_lower = conflicts.lower()
    
    if 'data_type' in conflicts_lower or 'variable_type' in conflicts_lower or 'required_flag' in conflicts_lower:
        return 'HIGH'
    elif 'refresh_frequency' in conflicts_lower or 'joining_condition' in conflicts_lower:
        return 'MEDIUM'
    else:
        return 'LOW'


def merge_all_metadata(
    dashboard_ids: List[int],
    context_store: ChartContextStore = None,
    api_key: str = None,
    model: str = None,
    base_url: str = None,
    output_dir: str = "extracted_meta"
) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    """
    Merge all metadata types across dashboards.
    
    Args:
        dashboard_ids: List of dashboard IDs to merge
        context_store: ChartContextStore with all contexts (or uses global)
        api_key, model, base_url: LLM config
        output_dir: Output directory
    
    Returns:
        (metadata_dfs, conflicts_df)
        
        metadata_dfs = {
            'tables': DataFrame with clean unified metadata (NO chart_id),
            'columns': DataFrame with clean unified metadata,
            'joins': DataFrame with clean unified metadata,
            'definitions': DataFrame with clean unified metadata
        }
        
        conflicts_df = DataFrame with:
            entity_type, entity_name, field, conflict_details, severity, affected_charts
    """
    api_key = api_key or LLM_API_KEY
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    if context_store is None:
        context_store = get_context_store()
    
    merged_metadata = {}
    all_conflicts = []
    
    # =========================================================================
    # Merge Tables
    # =========================================================================
    print("\n🔄 Merging table metadata...", flush=True)
    table_rows = []
    
    for table_name in context_store.get_all_entities('tables'):
        contexts = context_store.get_contexts('tables', table_name)
        
        if not contexts:
            continue
        
        merged = merge_table_metadata_with_deduplication(
            table_name, contexts, api_key, model, base_url
        )
        
        # Add to results (NO chart_id in final CSV)
        table_rows.append({
            'table_name': merged['table_name'],
            'table_description': merged['table_description'],
            'refresh_frequency': merged['refresh_frequency'],
            'vertical': merged['vertical'],
            'partition_column': merged['partition_column'],
            'remarks': merged['remarks'],
            'relationship_context': merged['relationship_context']
        })
        
        # Track conflicts
        if merged.get('conflicts'):
            all_conflicts.append({
                'entity_type': 'table',
                'entity_name': table_name,
                'field': 'various',
                'conflict_details': merged['conflicts'],
                'severity': _assess_conflict_severity(merged['conflicts']),
                'affected_charts': ','.join(str(c['chart_id']) for c in contexts)
            })
    
    merged_metadata['tables'] = pd.DataFrame(table_rows) if table_rows else pd.DataFrame()
    
    # =========================================================================
    # Merge Columns
    # =========================================================================
    print("🔄 Merging column metadata...", flush=True)
    column_rows = []
    
    for column_key in context_store.get_all_entities('columns'):
        contexts = context_store.get_contexts('columns', column_key)
        
        if not contexts:
            continue
        
        merged = merge_column_metadata_with_deduplication(
            column_key, contexts, api_key, model, base_url
        )
        
        if merged:
            column_rows.append({
                'table_name': merged['table_name'],
                'column_name': merged['column_name'],
                'variable_type': merged['variable_type'],
                'column_description': merged['column_description'],
                'required_flag': merged['required_flag']
            })
            
            if merged.get('conflicts'):
                all_conflicts.append({
                    'entity_type': 'column',
                    'entity_name': column_key,
                    'field': 'various',
                    'conflict_details': merged['conflicts'],
                    'severity': _assess_conflict_severity(merged['conflicts']),
                    'affected_charts': ','.join(str(c['chart_id']) for c in contexts)
                })
    
    merged_metadata['columns'] = pd.DataFrame(column_rows) if column_rows else pd.DataFrame()
    
    # =========================================================================
    # Merge Joins
    # =========================================================================
    print("🔄 Merging joining conditions...", flush=True)
    join_rows = []
    
    for join_key in context_store.get_all_entities('joins'):
        contexts = context_store.get_contexts('joins', join_key)
        
        if not contexts:
            continue
        
        merged = merge_join_metadata_with_deduplication(
            join_key, contexts, api_key, model, base_url
        )
        
        if merged:
            join_rows.append({
                'table1': merged['table1'],
                'table2': merged['table2'],
                'joining_condition': merged['joining_condition'],
                'remarks': merged['remarks']
            })
            
            if merged.get('conflicts'):
                all_conflicts.append({
                    'entity_type': 'join',
                    'entity_name': join_key,
                    'field': 'joining_condition',
                    'conflict_details': merged['conflicts'],
                    'severity': _assess_conflict_severity(merged['conflicts']),
                    'affected_charts': ','.join(str(c['chart_id']) for c in contexts)
                })
    
    merged_metadata['joins'] = pd.DataFrame(join_rows) if join_rows else pd.DataFrame()
    
    # =========================================================================
    # Merge Definitions
    # =========================================================================
    print("🔄 Merging definitions...", flush=True)
    definition_rows = []
    
    for term in context_store.get_all_entities('definitions'):
        contexts = context_store.get_contexts('definitions', term)
        
        if not contexts:
            continue
        
        merged = merge_definition_metadata_with_deduplication(
            term, contexts, api_key, model, base_url
        )
        
        if merged:
            definition_rows.append({
                'term': merged['term'],
                'type': merged['type'],
                'definition': merged['definition'],
                'business_alias': merged['business_alias']
            })
            
            if merged.get('conflicts'):
                all_conflicts.append({
                    'entity_type': 'definition',
                    'entity_name': term,
                    'field': 'definition',
                    'conflict_details': merged['conflicts'],
                    'severity': _assess_conflict_severity(merged['conflicts']),
                    'affected_charts': ','.join(str(c['chart_id']) for c in contexts)
                })
    
    merged_metadata['definitions'] = pd.DataFrame(definition_rows) if definition_rows else pd.DataFrame()
    
    # =========================================================================
    # Merge Filter Conditions (TXT format - concatenate)
    # =========================================================================
    print("🔄 Merging filter conditions...", flush=True)
    filter_content_parts = []
    
    for filter_key in context_store.get_all_entities('filters'):
        contexts = context_store.get_contexts('filters', filter_key)
        
        for ctx in contexts:
            metadata = ctx.get('metadata', {})
            content = metadata.get('filter_conditions', '')
            if content:
                filter_content_parts.append(content)
    
    merged_metadata['filters'] = '\n\n---\n\n'.join(filter_content_parts)
    
    # =========================================================================
    # Create conflicts DataFrame
    # =========================================================================
    conflicts_df = pd.DataFrame(all_conflicts) if all_conflicts else pd.DataFrame(
        columns=['entity_type', 'entity_name', 'field', 'conflict_details', 'severity', 'affected_charts']
    )
    
    # Sort by severity
    if not conflicts_df.empty:
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2, 'NONE': 3}
        conflicts_df['_severity_order'] = conflicts_df['severity'].map(severity_order)
        conflicts_df = conflicts_df.sort_values('_severity_order').drop('_severity_order', axis=1)
    
    # =========================================================================
    # Save merged metadata
    # =========================================================================
    merged_dir = f"{output_dir}/merged_metadata"
    os.makedirs(merged_dir, exist_ok=True)
    
    # Save CSVs (NO chart_id columns)
    if not merged_metadata['tables'].empty:
        merged_metadata['tables'].to_csv(f"{merged_dir}/consolidated_table_metadata.csv", index=False)
    
    if not merged_metadata['columns'].empty:
        merged_metadata['columns'].to_csv(f"{merged_dir}/consolidated_columns_metadata.csv", index=False)
    
    if not merged_metadata['joins'].empty:
        merged_metadata['joins'].to_csv(f"{merged_dir}/consolidated_joining_conditions.csv", index=False)
    
    if not merged_metadata['definitions'].empty:
        merged_metadata['definitions'].to_csv(f"{merged_dir}/consolidated_definitions.csv", index=False)
    
    # Save filter conditions as TXT
    if merged_metadata['filters']:
        with open(f"{merged_dir}/consolidated_filter_conditions.txt", 'w', encoding='utf-8') as f:
            f.write(merged_metadata['filters'])
    
    # Save conflicts report
    conflicts_df.to_csv(f"{merged_dir}/conflicts_report.csv", index=False)
    
    print(f"\n✅ Merge complete. {len(all_conflicts)} conflicts detected.", flush=True)
    print(f"   Files saved to: {merged_dir}/", flush=True)
    
    return merged_metadata, conflicts_df

