"""
Reflexion-Based Metadata Extraction Module

This module wraps chart_level_extractor.py to add reflexion loops for low-confidence
metadata extraction results. It uses LLM judges from metadata_quality_judge.py to
validate extractions and re-extracts with targeted feedback when confidence < 0.85.

Key Features:
- Iterative refinement of metadata extraction
- Confidence scoring for all 5 metadata types
- Score degradation detection to stop reflexion
- Thread-safe operations
"""

import os
import sys
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field, asdict

# Add scripts directory to path for imports
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL

logger = logging.getLogger(__name__)

# Confidence threshold - hardcoded as per requirements
CONFIDENCE_THRESHOLD = 0.85
MAX_REFLEXION_ITERATIONS = 2


@dataclass
class JudgeResult:
    """Result from a single judge evaluation."""
    confidence: float  # 0-1 scale
    quality_issues: str
    recommendations: str
    missing_items: List[str] = field(default_factory=list)


@dataclass
class ReflexionMetadata:
    """Extended ChartMetadata with reflexion tracking."""
    chart_id: int
    chart_name: str
    table_metadata: List[Dict]
    column_metadata: List[Dict]
    joining_conditions: List[Dict]
    filter_conditions: str
    definitions: List[Dict]
    # Reflexion tracking
    reflexion_iterations: Dict[str, int] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)


def normalize_score(score: int) -> float:
    """
    Convert 0-100 integer score to 0-1 float.
    
    Args:
        score: Integer score from 0-100
        
    Returns:
        Float score from 0-1
    """
    if isinstance(score, (int, float)):
        return min(max(float(score) / 100.0, 0.0), 1.0)
    return 0.0


def should_skip_reflexion(initial_scores: Dict[str, float]) -> bool:
    """
    Skip reflexion if all scores already >= 0.85.
    
    Args:
        initial_scores: Dict mapping metadata type to confidence score (0-1)
        
    Returns:
        True if can skip (all good), False if need reflexion
    """
    if not initial_scores:
        return False
    return all(score >= CONFIDENCE_THRESHOLD for score in initial_scores.values())


def detect_score_degradation(iteration_history: List[Dict]) -> bool:
    """
    Stop reflexion if score is getting worse.
    
    Args:
        iteration_history: List of iteration records with scores
            [
                {'iteration': 0, 'scores': {'tables': 0.82, ...}},
                {'iteration': 1, 'scores': {'tables': 0.78, ...}}  # Degraded!
            ]
    
    Returns:
        True if latest score < previous score (stop reflexion)
    """
    if len(iteration_history) < 2:
        return False
    
    prev_scores = iteration_history[-2].get('scores', {})
    curr_scores = iteration_history[-1].get('scores', {})
    
    if not prev_scores or not curr_scores:
        return False
    
    prev_avg = sum(prev_scores.values()) / len(prev_scores)
    curr_avg = sum(curr_scores.values()) / len(curr_scores)
    
    return curr_avg < prev_avg


def validate_with_all_judges(
    chart_json: Dict,
    metadata: ReflexionMetadata,
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> Dict[str, JudgeResult]:
    """
    Run all 5 judges from metadata_quality_judge.py.
    
    Args:
        chart_json: Original chart JSON with sql_query, filters, metrics
        metadata: Extracted ReflexionMetadata object
    
    Returns:
        Dict mapping metadata type to JudgeResult:
        {
            'tables': JudgeResult(confidence=0.90, issues='...', recommendations='...'),
            'columns': JudgeResult(confidence=0.82, issues='...', recommendations='...'),
            ...
        }
    """
    from metadata_quality_judge import MetadataQualityJudge
    import pandas as pd
    
    api_key = api_key or LLM_API_KEY
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    results = {}
    
    try:
        judge = MetadataQualityJudge(api_key=api_key, model=model, base_url=base_url)
        
        # Convert metadata to CSV strings for judge input
        # Table metadata
        if metadata.table_metadata:
            table_df = pd.DataFrame(metadata.table_metadata)
            table_csv = table_df.to_csv(index=False)
            table_report = judge.judge_table_metadata(chart_json, table_csv)
            results['tables'] = JudgeResult(
                confidence=normalize_score(table_report.scores.get('confidence', 0)),
                quality_issues='; '.join(table_report.quality_issues),
                recommendations='; '.join(table_report.recommendations),
                missing_items=table_report.missing_items
            )
        else:
            results['tables'] = JudgeResult(confidence=0.5, quality_issues='No table metadata extracted', recommendations='Extract table metadata')
        
        # Column metadata
        if metadata.column_metadata:
            column_df = pd.DataFrame(metadata.column_metadata)
            column_csv = column_df.to_csv(index=False)
            column_report = judge.judge_column_metadata(chart_json, column_csv)
            results['columns'] = JudgeResult(
                confidence=normalize_score(column_report.scores.get('confidence', 0)),
                quality_issues='; '.join(column_report.quality_issues),
                recommendations='; '.join(column_report.recommendations),
                missing_items=column_report.missing_items
            )
        else:
            results['columns'] = JudgeResult(confidence=0.5, quality_issues='No column metadata extracted', recommendations='Extract column metadata')
        
        # Joining conditions
        if metadata.joining_conditions:
            joins_df = pd.DataFrame(metadata.joining_conditions)
            joins_csv = joins_df.to_csv(index=False)
            joins_report = judge.judge_joining_conditions(chart_json, joins_csv)
            results['joins'] = JudgeResult(
                confidence=normalize_score(joins_report.scores.get('confidence', 0)),
                quality_issues='; '.join(joins_report.quality_issues),
                recommendations='; '.join(joins_report.recommendations),
                missing_items=joins_report.missing_items
            )
        else:
            # No joins might be valid if single table
            results['joins'] = JudgeResult(confidence=0.85, quality_issues='', recommendations='')
        
        # Filter conditions (TXT format)
        if metadata.filter_conditions:
            filters_report = judge.judge_filter_conditions(chart_json, metadata.filter_conditions)
            results['filters'] = JudgeResult(
                confidence=normalize_score(filters_report.scores.get('confidence', 0)),
                quality_issues='; '.join(filters_report.quality_issues),
                recommendations='; '.join(filters_report.recommendations),
                missing_items=filters_report.missing_items
            )
        else:
            results['filters'] = JudgeResult(confidence=0.5, quality_issues='No filter conditions extracted', recommendations='Extract filter conditions')
        
        # Definitions
        if metadata.definitions:
            defs_df = pd.DataFrame(metadata.definitions)
            defs_csv = defs_df.to_csv(index=False)
            defs_report = judge.judge_definitions(chart_json, defs_csv)
            results['definitions'] = JudgeResult(
                confidence=normalize_score(defs_report.scores.get('confidence', 0)),
                quality_issues='; '.join(defs_report.quality_issues),
                recommendations='; '.join(defs_report.recommendations),
                missing_items=defs_report.missing_items
            )
        else:
            results['definitions'] = JudgeResult(confidence=0.5, quality_issues='No definitions extracted', recommendations='Extract term definitions')
        
    except Exception as e:
        logger.error(f"Error in validate_with_all_judges: {str(e)}", exc_info=True)
        # Return default low-confidence results on error
        for meta_type in ['tables', 'columns', 'joins', 'filters', 'definitions']:
            if meta_type not in results:
                results[meta_type] = JudgeResult(
                    confidence=0.5,
                    quality_issues=f'Error during validation: {str(e)}',
                    recommendations='Retry extraction'
                )
    
    return results


def generate_reflection_prompt(
    metadata_type: str,
    chart_json: Dict,
    current_metadata: Any,
    judge_result: JudgeResult
) -> str:
    """
    Generate targeted reflection prompt for failed metadata type.
    
    Args:
        metadata_type: One of ['tables', 'columns', 'joins', 'filters', 'definitions']
        chart_json: Original chart JSON
        current_metadata: The extraction that failed validation
        judge_result: Judge's feedback with issues and recommendations
    
    Returns:
        Reflection prompt string (max 2000 tokens)
    """
    chart_name = chart_json.get('chart_name', 'Unknown')
    sql_query = chart_json.get('sql_query', '')
    metrics = chart_json.get('metrics', [])
    
    # Truncate SQL query if too long
    sql_display = sql_query[:500] + '...' if len(sql_query) > 500 else sql_query
    
    # Format current metadata for display
    if isinstance(current_metadata, list):
        metadata_display = json.dumps(current_metadata[:3], indent=2)  # First 3 items
        if len(current_metadata) > 3:
            metadata_display += f"\n... and {len(current_metadata) - 3} more items"
    elif isinstance(current_metadata, str):
        metadata_display = current_metadata[:500] + '...' if len(current_metadata) > 500 else current_metadata
    else:
        metadata_display = str(current_metadata)[:500]
    
    prompt = f"""You previously extracted {metadata_type} metadata with the following issues:

## Issues Found
{judge_result.quality_issues or 'No specific issues identified'}

## Missing Items
{', '.join(judge_result.missing_items) if judge_result.missing_items else 'None identified'}

## Recommendations
{judge_result.recommendations or 'No specific recommendations'}

## Original Chart Context
- Chart Name: {chart_name}
- SQL Query:
```sql
{sql_display}
```
- Metrics: {json.dumps(metrics[:5], indent=2) if metrics else 'None'}

## Your Previous Extraction (NEEDS IMPROVEMENT)
{metadata_display}

## Task
Re-extract {metadata_type} metadata addressing ALL issues above.
Focus specifically on: {judge_result.recommendations}

CRITICAL: Ensure your new extraction fixes ALL identified issues and includes ALL missing items.
"""
    
    return prompt[:4000]  # Hard limit to prevent token overflow


def re_extract_with_reflection(
    metadata_type: str,
    chart: Dict,
    dashboard_title: str,
    reflection_prompt: str,
    tables_columns_df: Any,
    api_key: str,
    model: str,
    base_url: str
) -> Any:
    """
    Re-extract only the failed metadata type with reflection context.
    
    Calls appropriate extractor from chart_level_extractor.py with
    the reflection prompt injected into the context.
    
    Args:
        metadata_type: One of ['tables', 'columns', 'joins', 'filters', 'definitions']
        chart: Chart dict with chart_id, chart_name, sql_query, etc.
        dashboard_title: Dashboard title for context
        reflection_prompt: Generated reflection prompt with issues/recommendations
        tables_columns_df: DataFrame with tables_columns data (for columns/joins/filters)
        api_key: LLM API key
        model: LLM model name
        base_url: LLM base URL
    
    Returns:
        Improved metadata for that type only
    """
    from chart_level_extractor import (
        extract_table_metadata_for_chart,
        extract_column_metadata_for_chart,
        extract_joining_conditions_for_chart,
        extract_filter_conditions_for_chart,
        extract_definitions_for_chart
    )
    
    # Inject reflection context into chart for extraction
    # This is done by adding the reflection prompt as additional context
    enhanced_chart = chart.copy()
    
    # Add reflection context to sql_query or metrics as additional context
    original_sql = enhanced_chart.get('sql_query', '')
    enhanced_chart['_reflection_context'] = reflection_prompt
    
    try:
        if metadata_type == 'tables':
            return extract_table_metadata_for_chart(
                enhanced_chart, dashboard_title, api_key, model, base_url
            )
        
        elif metadata_type == 'columns':
            return extract_column_metadata_for_chart(
                enhanced_chart, dashboard_title, tables_columns_df, api_key, model, base_url
            )
        
        elif metadata_type == 'joins':
            return extract_joining_conditions_for_chart(
                enhanced_chart, dashboard_title, tables_columns_df, api_key, model, base_url
            )
        
        elif metadata_type == 'filters':
            return extract_filter_conditions_for_chart(
                enhanced_chart, dashboard_title, tables_columns_df, api_key, model, base_url
            )
        
        elif metadata_type == 'definitions':
            return extract_definitions_for_chart(
                enhanced_chart, dashboard_title, api_key, model, base_url
            )
        
        else:
            raise ValueError(f"Unknown metadata type: {metadata_type}")
            
    except Exception as e:
        logger.error(f"Error in re_extract_with_reflection for {metadata_type}: {str(e)}", exc_info=True)
        raise


def extract_chart_with_reflexion(
    chart: Dict,
    dashboard_title: str,
    api_key: str = None,
    model: str = None,
    base_url: str = None,
    tables_columns_df: Any = None,
    max_iterations: int = MAX_REFLEXION_ITERATIONS,
    confidence_threshold: float = CONFIDENCE_THRESHOLD
) -> Tuple[ReflexionMetadata, Dict[str, float]]:
    """
    Extract metadata with reflexion loop for low-confidence results.
    
    Algorithm:
    1. Initial extraction (iteration 0)
    2. Validate with all 5 judges
    3. For each metadata type with confidence < 0.85:
       a. Generate reflection prompt from judge feedback
       b. Re-extract that metadata type only
       c. Re-validate
    4. Stop if: all types >= 0.85 OR max_iterations reached OR score degrades
    
    Args:
        chart: Chart dict with chart_id, chart_name, sql_query, etc.
        dashboard_title: Dashboard title for context
        api_key: LLM API key
        model: LLM model name
        base_url: LLM base URL
        tables_columns_df: DataFrame with tables_columns data (optional)
        max_iterations: Max reflexion loops (default: 2)
        confidence_threshold: Skip reflexion if >= this (default: 0.85)
    
    Returns:
        (reflexion_metadata, confidence_scores)
        
        confidence_scores = {
            'tables': 0.90,
            'columns': 0.82,
            'joins': 0.88,
            'filters': 0.75,
            'definitions': 0.91,
            'overall': 0.85
        }
    """
    from chart_level_extractor import (
        extract_table_metadata_for_chart,
        extract_column_metadata_for_chart,
        extract_joining_conditions_for_chart,
        extract_filter_conditions_for_chart,
        extract_definitions_for_chart
    )
    import pandas as pd
    
    # Validate inputs
    if not chart or 'chart_id' not in chart:
        raise ValueError("Invalid chart dict: missing chart_id")
    
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence_threshold must be between 0 and 1")
    
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")
    
    api_key = api_key or LLM_API_KEY
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    chart_id = chart.get('chart_id')
    chart_name = chart.get('chart_name', 'Unknown')
    
    logger.info(f"Starting reflexion extraction for chart {chart_id}: {chart_name}")
    
    # Initialize empty DataFrame if not provided
    if tables_columns_df is None:
        tables_columns_df = pd.DataFrame(columns=['tables_involved', 'column_names', 'column_datatype'])
    
    # =========================================================================
    # ITERATION 0: Initial Extraction
    # =========================================================================
    
    print(f"    🔄 Initial extraction for chart {chart_id}...", flush=True)
    
    try:
        table_metadata = extract_table_metadata_for_chart(
            chart, dashboard_title, api_key, model, base_url
        )
    except Exception as e:
        logger.warning(f"Table metadata extraction failed: {e}")
        table_metadata = []
    
    try:
        column_metadata = extract_column_metadata_for_chart(
            chart, dashboard_title, tables_columns_df, api_key, model, base_url
        )
    except Exception as e:
        logger.warning(f"Column metadata extraction failed: {e}")
        column_metadata = []
    
    try:
        joining_conditions = extract_joining_conditions_for_chart(
            chart, dashboard_title, tables_columns_df, api_key, model, base_url
        )
    except Exception as e:
        logger.warning(f"Joining conditions extraction failed: {e}")
        joining_conditions = []
    
    try:
        filter_conditions = extract_filter_conditions_for_chart(
            chart, dashboard_title, tables_columns_df, api_key, model, base_url
        )
    except Exception as e:
        logger.warning(f"Filter conditions extraction failed: {e}")
        filter_conditions = ""
    
    try:
        definitions = extract_definitions_for_chart(
            chart, dashboard_title, api_key, model, base_url
        )
    except Exception as e:
        logger.warning(f"Definitions extraction failed: {e}")
        definitions = []
    
    # Create metadata object
    metadata = ReflexionMetadata(
        chart_id=chart_id,
        chart_name=chart_name,
        table_metadata=table_metadata,
        column_metadata=column_metadata,
        joining_conditions=joining_conditions,
        filter_conditions=filter_conditions,
        definitions=definitions,
        reflexion_iterations={
            'tables': 0, 'columns': 0, 'joins': 0, 'filters': 0, 'definitions': 0
        },
        confidence_scores={}
    )
    
    # =========================================================================
    # VALIDATION: Run judges
    # =========================================================================
    
    print(f"    🔍 Validating extraction for chart {chart_id}...", flush=True)
    
    judge_results = validate_with_all_judges(chart, metadata, api_key, model, base_url)
    
    # Extract confidence scores
    confidence_scores = {
        meta_type: result.confidence 
        for meta_type, result in judge_results.items()
    }
    confidence_scores['overall'] = sum(confidence_scores.values()) / len(confidence_scores)
    
    metadata.confidence_scores = confidence_scores.copy()
    
    # Check if we can skip reflexion
    type_scores = {k: v for k, v in confidence_scores.items() if k != 'overall'}
    if should_skip_reflexion(type_scores):
        print(f"    ✅ All scores >= {confidence_threshold}, skipping reflexion", flush=True)
        return metadata, confidence_scores
    
    # =========================================================================
    # REFLEXION LOOP
    # =========================================================================
    
    iteration_history = [{'iteration': 0, 'scores': type_scores.copy()}]
    
    for iteration in range(1, max_iterations + 1):
        print(f"    🔄 Reflexion iteration {iteration}/{max_iterations} for chart {chart_id}...", flush=True)
        
        # Find metadata types that need improvement
        types_to_improve = [
            meta_type for meta_type, score in type_scores.items()
            if score < confidence_threshold
        ]
        
        if not types_to_improve:
            print(f"    ✅ All scores improved, stopping reflexion", flush=True)
            break
        
        # Re-extract each low-confidence type
        for meta_type in types_to_improve:
            judge_result = judge_results.get(meta_type)
            if not judge_result:
                continue
            
            # Get current metadata for this type
            current_metadata = getattr(metadata, _get_metadata_attr(meta_type))
            
            # Generate reflection prompt
            reflection_prompt = generate_reflection_prompt(
                meta_type, chart, current_metadata, judge_result
            )
            
            print(f"      🔧 Re-extracting {meta_type} (score: {type_scores[meta_type]:.2f})...", flush=True)
            
            try:
                # Re-extract with reflection
                improved_metadata = re_extract_with_reflection(
                    meta_type, chart, dashboard_title, reflection_prompt,
                    tables_columns_df, api_key, model, base_url
                )
                
                # Update metadata
                setattr(metadata, _get_metadata_attr(meta_type), improved_metadata)
                metadata.reflexion_iterations[meta_type] = iteration
                
            except Exception as e:
                logger.warning(f"Re-extraction failed for {meta_type}: {e}")
                continue
        
        # Re-validate all metadata
        judge_results = validate_with_all_judges(chart, metadata, api_key, model, base_url)
        
        # Update scores
        type_scores = {
            meta_type: result.confidence 
            for meta_type, result in judge_results.items()
        }
        
        iteration_history.append({'iteration': iteration, 'scores': type_scores.copy()})
        
        # Check for score degradation
        if detect_score_degradation(iteration_history):
            print(f"    ⚠️ Score degradation detected, stopping reflexion", flush=True)
            # Revert to previous iteration's metadata if possible
            break
        
        # Update confidence scores in metadata
        confidence_scores = type_scores.copy()
        confidence_scores['overall'] = sum(type_scores.values()) / len(type_scores)
        metadata.confidence_scores = confidence_scores.copy()
    
    # Final confidence scores
    confidence_scores['overall'] = sum(type_scores.values()) / len(type_scores)
    
    print(f"    ✅ Reflexion complete for chart {chart_id}, overall confidence: {confidence_scores['overall']:.2f}", flush=True)
    
    return metadata, confidence_scores


def _get_metadata_attr(meta_type: str) -> str:
    """Get attribute name for metadata type."""
    type_to_attr = {
        'tables': 'table_metadata',
        'columns': 'column_metadata',
        'joins': 'joining_conditions',
        'filters': 'filter_conditions',
        'definitions': 'definitions'
    }
    return type_to_attr.get(meta_type, meta_type)


def calculate_overall_confidence(
    per_chart_scores: List[Dict[str, float]]
) -> Dict[str, float]:
    """
    Calculate aggregate confidence scores across all charts.
    
    Args:
        per_chart_scores: List of confidence score dicts from each chart
        
    Returns:
        Aggregated confidence scores
    """
    if not per_chart_scores:
        return {
            'tables': 0.0, 'columns': 0.0, 'joins': 0.0,
            'filters': 0.0, 'definitions': 0.0, 'overall': 0.0
        }
    
    aggregated = {}
    all_types = ['tables', 'columns', 'joins', 'filters', 'definitions']
    
    for meta_type in all_types:
        scores = [s.get(meta_type, 0.0) for s in per_chart_scores if meta_type in s]
        aggregated[meta_type] = sum(scores) / len(scores) if scores else 0.0
    
    type_scores = [aggregated[t] for t in all_types]
    aggregated['overall'] = sum(type_scores) / len(type_scores)
    
    return aggregated


def save_confidence_scores(
    dashboard_id: int,
    overall_confidence: float,
    per_metadata_type: Dict[str, float],
    per_chart_confidence: List[Dict],
    reflexion_stats: Dict,
    output_dir: str = "extracted_meta"
):
    """
    Save confidence scores to JSON file.
    
    Args:
        dashboard_id: Dashboard ID
        overall_confidence: Overall confidence score (0-1)
        per_metadata_type: Dict of metadata type -> confidence score
        per_chart_confidence: List of per-chart confidence dicts
        reflexion_stats: Stats about reflexion iterations
        output_dir: Output directory
    """
    output_path = f"{output_dir}/{dashboard_id}/confidence_scores.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    scores = {
        'dashboard_id': dashboard_id,
        'overall_confidence': overall_confidence,
        'per_metadata_type': per_metadata_type,
        'per_chart_confidence': per_chart_confidence,
        'reflexion_stats': reflexion_stats,
        'threshold': CONFIDENCE_THRESHOLD,
        'max_iterations': MAX_REFLEXION_ITERATIONS
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Confidence scores saved to {output_path}")

