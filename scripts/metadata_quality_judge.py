"""
Metadata Quality Judge Module

This module evaluates the quality of extracted metadata by comparing it against
the original chart JSON data. It uses DSPy framework with LLM-powered analysis
to generate confidence scores and actionable feedback for each metadata type.

The judge evaluates 5 metadata types:
1. Table Metadata - Table descriptions, refresh frequency, vertical, partition columns
2. Column Metadata - Column names, data types, descriptions, business context
3. Joining Conditions - Table relationships, join conditions, relationship types
4. Filter Conditions - Dashboard and chart-level filter conditions
5. Definitions - Business term definitions, metrics, calculated fields, synonyms
"""

import json
import os
import sys
import time
import random
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
import pandas as pd
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate

# Add scripts directory to path for imports
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL


# ============================================================================
# Rate Limit Handling
# ============================================================================

class RateLimitExhaustedError(Exception):
    """
    Raised when rate limit retries are exhausted.
    This is a FATAL error that should stop the entire pipeline.
    """
    pass


def call_judge_with_retry(
    judge_func: Callable,
    max_retries: int = 5,
    initial_delay: float = 2.0,
    max_delay: float = 64.0,
    backoff_factor: float = 2.0,
    **kwargs
) -> Any:
    """
    Call a judge function with exponential backoff retry on rate limit errors.
    
    Retry schedule with backoff_factor=2.0:
        Attempt 1: immediate
        Attempt 2: ~2s delay
        Attempt 3: ~4s delay
        Attempt 4: ~8s delay
        Attempt 5: ~16s delay
        Attempt 6: ~32s delay
        FAIL: raises RateLimitExhaustedError (stops pipeline)
    
    Args:
        judge_func: The DSPy judge function to call
        max_retries: Maximum retry attempts (default: 5, gives up to ~64s delay)
        initial_delay: Initial delay in seconds (default: 2.0)
        max_delay: Maximum delay between retries (default: 64.0)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        **kwargs: Arguments to pass to the judge function
    
    Returns:
        Result from the judge function
    
    Raises:
        RateLimitExhaustedError: If all retries are exhausted (FATAL - stops pipeline)
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            return judge_func(**kwargs)
        except Exception as e:
            error_str = str(e).lower()
            # Check for rate limit errors (429, rate limit, too many tokens)
            is_rate_limit = (
                '429' in error_str or
                ('rate' in error_str and 'limit' in error_str) or
                'too many' in error_str or
                'ratelimit' in error_str or
                'too many tokens' in error_str
            )
            
            if is_rate_limit and attempt < max_retries:
                last_exception = e
                # Add jitter (0.5x to 1.5x) to prevent thundering herd
                actual_delay = delay * (0.5 + random.random())
                actual_delay = min(actual_delay, max_delay)
                
                print(f"    ⏳ Rate limit hit, waiting {actual_delay:.1f}s before retry {attempt + 1}/{max_retries}...", flush=True)
                time.sleep(actual_delay)
                
                # Exponential backoff: 2s -> 4s -> 8s -> 16s -> 32s -> 64s
                delay = min(delay * backoff_factor, max_delay)
            else:
                # Not a rate limit error OR we're on the last attempt
                if is_rate_limit:
                    # Exhausted all retries for rate limit - FATAL ERROR
                    raise RateLimitExhaustedError(
                        f"❌ FATAL: Rate limit exhausted after {max_retries} retries. "
                        f"Maximum delay reached: {max_delay:.1f}s. Stopping pipeline.\n"
                        f"Original error: {str(e)}"
                    )
                else:
                    # Some other error, re-raise it
                    raise e
    
    # Should not reach here, but just in case
    if last_exception:
        raise RateLimitExhaustedError(
            f"❌ FATAL: Rate limit exhausted after {max_retries} retries. Stopping pipeline.\n"
            f"Original error: {str(last_exception)}"
        )


# ============================================================================
# DSPy Signatures for Quality Judging
# ============================================================================

class TableMetadataJudge(dspy.Signature):
    """
    Judge the quality of extracted table metadata by comparing it against source chart JSON.
    
    Evaluate completeness (all tables captured), accuracy (descriptions match SQL usage),
    and clarity (business-focused descriptions).
    
    SYSTEM PROMPT: Table Metadata Quality Judge
    
    ## Objective
    Evaluate extracted table metadata quality by comparing it against actual SQL queries
    in the chart JSON. Focus on whether the metadata would help someone write SQL queries
    against these tables and understand their business purpose.
    
    ## Scoring Criteria
    
    **Completeness (40% weight):**
    - All tables from SQL queries (including CTEs if they represent real tables) captured?
    - Missing tables = major deduction
    
    **Accuracy (40% weight):**
    - Descriptions match actual table usage in queries?
    - Refresh frequency, vertical, partition columns correct?
    - Relationship context accurately reflects join patterns?
    
    **Clarity (20% weight):**
    - Descriptions are business-focused (not just technical)?
    - Would a business user understand what this table contains?
    - Descriptions are specific (not generic like "contains data")?
    
    ## Output Format
    Provide numeric scores (0-100) and specific, actionable feedback.
    """
    
    chart_json: str = dspy.InputField(desc="Original chart JSON containing SQL queries, chart names, filters, and dashboard context")
    table_metadata_csv: str = dspy.InputField(desc="Extracted table metadata CSV content with columns: table_name, table_description, refresh_frequency, vertical, partition_column, remarks, relationship_context")
    
    completeness_score: int = dspy.OutputField(desc="Completeness score (0-100): Percentage of source tables from SQL queries captured in metadata")
    accuracy_score: int = dspy.OutputField(desc="Accuracy score (0-100): Correctness of table descriptions, refresh frequencies, verticals, partition columns, and relationship context")
    clarity_score: int = dspy.OutputField(desc="Clarity score (0-100): How business-focused and specific the descriptions are (not generic or overly technical)")
    confidence_score: int = dspy.OutputField(desc="Overall confidence score (0-100): Weighted average (40% completeness + 40% accuracy + 20% clarity)")
    missing_tables: str = dspy.OutputField(desc="Comma-separated list of table names from SQL queries that are missing from metadata (empty if none)")
    quality_issues: str = dspy.OutputField(desc="Semicolon-separated list of specific quality issues found (e.g., 'table X description is too generic', 'missing refresh frequency for table Y')")
    recommendations: str = dspy.OutputField(desc="Semicolon-separated list of actionable recommendations for improvement (e.g., 'Add specific business context for table X', 'Specify refresh schedule for table Y')")


class ColumnMetadataJudge(dspy.Signature):
    """
    Judge the quality of extracted column metadata by comparing it against source chart JSON.
    
    Evaluate completeness (key columns captured), accuracy (data types and descriptions match SQL),
    and business context (descriptions explain business meaning).
    
    SYSTEM PROMPT: Column Metadata Quality Judge
    
    ## Objective
    Evaluate extracted column metadata quality by comparing it against actual SQL queries
    in the chart JSON. Focus on whether the metadata would help someone understand what
    each column represents from a business perspective.
    
    ## Scoring Criteria
    
    **Completeness (35% weight):**
    - Key columns from SELECT, WHERE, JOIN, GROUP BY clauses captured?
    - Missing critical columns = major deduction
    
    **Accuracy (35% weight):**
    - Data types match actual SQL usage?
    - Column descriptions match how columns are used in queries?
    - Required flags correct?
    
    **Business Context (30% weight):**
    - Descriptions explain business meaning, not just technical details?
    - Would a non-technical user understand what this column represents?
    - Descriptions are specific (not generic like "identifier" or "timestamp")?
    
    ## Output Format
    Provide numeric scores (0-100) and specific, actionable feedback.
    """
    
    chart_json: str = dspy.InputField(desc="Original chart JSON containing SQL queries, chart names, filters, and dashboard context")
    column_metadata_csv: str = dspy.InputField(desc="Extracted column metadata CSV content with columns: table_name, column_name, variable_type, column_description, required_flag")
    
    completeness_score: int = dspy.OutputField(desc="Completeness score (0-100): Percentage of key columns from SQL queries captured in metadata")
    accuracy_score: int = dspy.OutputField(desc="Accuracy score (0-100): Correctness of data types, descriptions, and required flags")
    business_context_score: int = dspy.OutputField(desc="Business context score (0-100): How well descriptions explain business meaning vs technical details")
    confidence_score: int = dspy.OutputField(desc="Overall confidence score (0-100): Weighted average (35% completeness + 35% accuracy + 30% business context)")
    missing_columns: str = dspy.OutputField(desc="Comma-separated list of critical column names from SQL queries that are missing from metadata (format: table.column, empty if none)")
    quality_issues: str = dspy.OutputField(desc="Semicolon-separated list of specific quality issues found (e.g., 'column X has incorrect data type', 'column Y description is too technical')")
    recommendations: str = dspy.OutputField(desc="Semicolon-separated list of actionable recommendations for improvement (e.g., 'Add business context for column X', 'Correct data type for column Y')")


class JoiningConditionsJudge(dspy.Signature):
    """
    Judge the quality of extracted joining conditions by comparing it against source chart JSON.
    
    Evaluate completeness (all JOIN clauses captured), accuracy (join conditions correctly extracted),
    and context (relationship types and business meanings clear).
    
    SYSTEM PROMPT: Joining Conditions Quality Judge
    
    ## Objective
    Evaluate extracted joining conditions quality by comparing it against actual JOIN clauses
    in the SQL queries. Focus on whether the metadata accurately captures how tables relate
    to each other.
    
    ## Scoring Criteria
    
    **Completeness (45% weight):**
    - All JOIN clauses from SQL queries captured?
    - Missing joins = major deduction
    
    **Accuracy (45% weight):**
    - Join conditions (columns, operators) correctly extracted?
    - Join types (LEFT JOIN, INNER JOIN, etc.) correctly identified?
    - Join keys match actual SQL?
    
    **Context (10% weight):**
    - Relationship types and business meanings clear?
    - Remarks explain why tables are joined?
    
    ## Output Format
    Provide numeric scores (0-100) and specific, actionable feedback.
    """
    
    chart_json: str = dspy.InputField(desc="Original chart JSON containing SQL queries, chart names, filters, and dashboard context")
    joining_conditions_csv: str = dspy.InputField(desc="Extracted joining conditions CSV content with columns: table1, table2, joining_condition, remarks")
    
    completeness_score: int = dspy.OutputField(desc="Completeness score (0-100): Percentage of JOIN clauses from SQL queries captured in metadata")
    accuracy_score: int = dspy.OutputField(desc="Accuracy score (0-100): Correctness of join conditions (columns, operators, join types)")
    context_score: int = dspy.OutputField(desc="Context score (0-100): Clarity of relationship types and business meanings")
    confidence_score: int = dspy.OutputField(desc="Overall confidence score (0-100): Weighted average (45% completeness + 45% accuracy + 10% context)")
    missing_joins: str = dspy.OutputField(desc="Comma-separated list of JOIN clauses from SQL queries that are missing from metadata (format: table1 JOIN table2 ON condition, empty if none)")
    quality_issues: str = dspy.OutputField(desc="Semicolon-separated list of specific quality issues found (e.g., 'join condition for X and Y is incorrect', 'missing join type specification')")
    recommendations: str = dspy.OutputField(desc="Semicolon-separated list of actionable recommendations for improvement (e.g., 'Correct join condition for X and Y', 'Add business context for join relationship')")


class FilterConditionsJudge(dspy.Signature):
    """
    Judge the quality of extracted filter conditions by comparing it against source chart JSON.
    
    Evaluate completeness (dashboard and chart-level filters captured), accuracy (filter conditions
    correctly transcribed), and clarity (filter purpose and business impact explained).
    
    SYSTEM PROMPT: Filter Conditions Quality Judge
    
    ## Objective
    Evaluate extracted filter conditions quality by comparing it against actual WHERE clauses
    and dashboard filters in the chart JSON. Focus on whether the metadata accurately captures
    all filtering logic.
    
    ## Scoring Criteria
    
    **Completeness (40% weight):**
    - Dashboard-level filters captured?
    - Chart-level WHERE clauses captured?
    - Missing filters = major deduction
    
    **Accuracy (40% weight):**
    - Filter conditions correctly transcribed (columns, values, operators)?
    - Date ranges, IN clauses, comparison operators correct?
    - Filter logic matches actual SQL?
    
    **Clarity (20% weight):**
    - Filter purpose and business impact explained?
    - Would someone understand why these filters are applied?
    
    ## Output Format
    Provide numeric scores (0-100) and specific, actionable feedback.
    """
    
    chart_json: str = dspy.InputField(desc="Original chart JSON containing SQL queries, chart names, filters, and dashboard context")
    filter_conditions_txt: str = dspy.InputField(desc="Extracted filter conditions text content")
    
    completeness_score: int = dspy.OutputField(desc="Completeness score (0-100): Percentage of dashboard and chart-level filters captured in metadata")
    accuracy_score: int = dspy.OutputField(desc="Accuracy score (0-100): Correctness of filter conditions (columns, values, operators)")
    clarity_score: int = dspy.OutputField(desc="Clarity score (0-100): How well filter purpose and business impact are explained")
    confidence_score: int = dspy.OutputField(desc="Overall confidence score (0-100): Weighted average (40% completeness + 40% accuracy + 20% clarity)")
    missing_filters: str = dspy.OutputField(desc="Comma-separated list of filter conditions from SQL queries that are missing from metadata (empty if none)")
    quality_issues: str = dspy.OutputField(desc="Semicolon-separated list of specific quality issues found (e.g., 'filter condition for column X is incorrect', 'missing explanation for date range filter')")
    recommendations: str = dspy.OutputField(desc="Semicolon-separated list of actionable recommendations for improvement (e.g., 'Add missing filter for column X', 'Explain business purpose of date range filter')")


class DefinitionsJudge(dspy.Signature):
    """
    Judge the quality of extracted term definitions by comparing it against source chart JSON.
    
    Evaluate completeness (key business terms defined), accuracy (definitions match SQL calculations),
    and usefulness (definitions helpful for non-technical business users).
    
    SYSTEM PROMPT: Definitions Quality Judge
    
    ## Objective
    Evaluate extracted term definitions quality by comparing it against actual metrics, calculated
    fields, and business terms used in the chart JSON. Focus on whether the definitions would help
    non-technical users understand the business meaning.
    
    ## Scoring Criteria
    
    **Completeness (30% weight):**
    - Key business terms and metrics from chart labels defined?
    - Calculated fields from SQL explained?
    - Missing important terms = deduction
    
    **Accuracy (40% weight):**
    - Definitions match SQL calculations and logic?
    - Calculation formulas correct?
    - Term types (Metric, Calculated Field, Synonym, Category) correctly classified?
    
    **Usefulness (30% weight):**
    - Definitions helpful for non-technical business users?
    - Business aliases and synonyms captured?
    - Definitions are clear and concise?
    
    ## Output Format
    Provide numeric scores (0-100) and specific, actionable feedback.
    """
    
    chart_json: str = dspy.InputField(desc="Original chart JSON containing SQL queries, chart names, filters, and dashboard context")
    definitions_csv: str = dspy.InputField(desc="Extracted definitions CSV content with columns: term, type, definition, business_alias")
    
    completeness_score: int = dspy.OutputField(desc="Completeness score (0-100): Percentage of key business terms and metrics from chart JSON captured in definitions")
    accuracy_score: int = dspy.OutputField(desc="Accuracy score (0-100): Correctness of definitions, calculation formulas, and term type classifications")
    usefulness_score: int = dspy.OutputField(desc="Usefulness score (0-100): How helpful definitions are for non-technical business users")
    confidence_score: int = dspy.OutputField(desc="Overall confidence score (0-100): Weighted average (30% completeness + 40% accuracy + 30% usefulness)")
    missing_terms: str = dspy.OutputField(desc="Comma-separated list of important business terms from chart JSON that are missing from definitions (empty if none)")
    quality_issues: str = dspy.OutputField(desc="Semicolon-separated list of specific quality issues found (e.g., 'term X definition is incorrect', 'term Y calculation formula is wrong')")
    recommendations: str = dspy.OutputField(desc="Semicolon-separated list of actionable recommendations for improvement (e.g., 'Add definition for term X', 'Correct calculation formula for term Y')")


# ============================================================================
# Data Classes for Structured Output
# ============================================================================

@dataclass
class MetadataTypeReport:
    """Report for a single metadata type."""
    metadata_type: str
    scores: Dict[str, float]  # completeness, accuracy, additional_score, confidence
    missing_items: List[str]
    quality_issues: List[str]
    recommendations: List[str]
    status: str  # EXCELLENT, GOOD, ACCEPTABLE, NEEDS_IMPROVEMENT, POOR


@dataclass
class MetadataQualityReport:
    """Complete quality report for all metadata types."""
    dashboard_id: int
    summary: Dict[str, Any]
    detailed_reports: Dict[str, MetadataTypeReport]
    timestamp: str


# ============================================================================
# Metadata Quality Judge Class
# ============================================================================

class MetadataQualityJudge:
    """
    Judge metadata quality by comparing extracted metadata against source chart JSON.
    
    Uses DSPy framework with LLM-powered analysis to generate confidence scores
    and actionable feedback for each metadata type.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, 
                 base_url: Optional[str] = None):
        """
        Initialize the metadata quality judge.
        
        Args:
            api_key: Anthropic API key (default: from config.LLM_API_KEY)
            model: LLM model name (default: from config.LLM_MODEL)
            base_url: Custom API base URL (default: from config.LLM_BASE_URL)
        """
        self.api_key = api_key or LLM_API_KEY
        self.model = model or LLM_MODEL
        self.base_url = base_url or LLM_BASE_URL
        
        if not self.api_key:
            raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or pass api_key parameter.")
        
        # Initialize DSPy judges
        self._init_dspy_judges()
    
    def _init_dspy_judges(self):
        """Initialize DSPy judges for each metadata type."""
        # Configure DSPy LM
        if self.base_url:
            model_name = f"anthropic/{self.model}" if not self.model.startswith("anthropic/") else self.model
            clean_base_url = self.base_url.rstrip('/v1').rstrip('/')
            lm = dspy.LM(
                model=model_name,
                api_key=self.api_key,
                api_provider="anthropic",
                api_base=clean_base_url
            )
        else:
            lm = dspy.LM(
                model=self.model,
                api_key=self.api_key,
                api_provider="anthropic"
            )
        
        # Try to configure, but catch error if already configured in another thread
        try:
            dspy.configure(lm=lm)
        except RuntimeError:
            # DSPy already configured in another thread, use existing configuration
            pass
        
        # Create judges - they will use the configured LM
        self.table_judge = dspy.ChainOfThought(TableMetadataJudge)
        self.column_judge = dspy.ChainOfThought(ColumnMetadataJudge)
        self.joining_judge = dspy.ChainOfThought(JoiningConditionsJudge)
        self.filter_judge = dspy.ChainOfThought(FilterConditionsJudge)
        self.definitions_judge = dspy.ChainOfThought(DefinitionsJudge)
    
    def _classify_status(self, confidence_score: float) -> str:
        """Classify quality status based on confidence score."""
        if confidence_score >= 90:
            return "EXCELLENT"
        elif confidence_score >= 75:
            return "GOOD"
        elif confidence_score >= 60:
            return "ACCEPTABLE"
        elif confidence_score >= 40:
            return "NEEDS_IMPROVEMENT"
        else:
            return "POOR"
    
    def _parse_judge_output(self, output: dspy.Prediction, metadata_type: str) -> MetadataTypeReport:
        """Parse DSPy judge output into structured report."""
        # Extract scores
        scores = {
            "completeness": float(getattr(output, 'completeness_score', 0)),
            "accuracy": float(getattr(output, 'accuracy_score', 0)),
            "confidence": float(getattr(output, 'confidence_score', 0))
        }
        
        # Add type-specific additional score
        if hasattr(output, 'clarity_score'):
            scores["clarity"] = float(output.clarity_score)
        elif hasattr(output, 'business_context_score'):
            scores["business_context"] = float(output.business_context_score)
        elif hasattr(output, 'context_score'):
            scores["context"] = float(output.context_score)
        elif hasattr(output, 'usefulness_score'):
            scores["usefulness"] = float(output.usefulness_score)
        
        # Extract missing items
        missing_items = []
        missing_field = None
        if metadata_type == "table_metadata":
            missing_field = "missing_tables"
        elif metadata_type == "column_metadata":
            missing_field = "missing_columns"
        elif metadata_type == "joining_conditions":
            missing_field = "missing_joins"
        elif metadata_type == "filter_conditions":
            missing_field = "missing_filters"
        elif metadata_type == "definitions":
            missing_field = "missing_terms"
        
        if missing_field and hasattr(output, missing_field):
            missing_str = getattr(output, missing_field, "").strip()
            if missing_str:
                missing_items = [item.strip() for item in missing_str.split(',') if item.strip()]
        
        # Extract quality issues
        quality_issues = []
        if hasattr(output, 'quality_issues'):
            issues_str = output.quality_issues.strip()
            if issues_str:
                quality_issues = [issue.strip() for issue in issues_str.split(';') if issue.strip()]
        
        # Extract recommendations
        recommendations = []
        if hasattr(output, 'recommendations'):
            rec_str = output.recommendations.strip()
            if rec_str:
                recommendations = [rec.strip() for rec in rec_str.split(';') if rec.strip()]
        
        # Classify status
        status = self._classify_status(scores["confidence"])
        
        return MetadataTypeReport(
            metadata_type=metadata_type,
            scores=scores,
            missing_items=missing_items,
            quality_issues=quality_issues,
            recommendations=recommendations,
            status=status
        )
    
    def judge_table_metadata(self, chart_json: Dict, table_metadata_csv: str) -> MetadataTypeReport:
        """
        Judge table metadata quality.
        
        Args:
            chart_json: Original chart JSON dictionary
            table_metadata_csv: CSV content of table metadata file
            
        Returns:
            MetadataTypeReport with scores and feedback
            
        Raises:
            RateLimitExhaustedError: If rate limit retries are exhausted (FATAL)
        """
        chart_json_str = json.dumps(chart_json, indent=2)
        
        try:
            # Use retry wrapper for rate limit handling
            output = call_judge_with_retry(
                self.table_judge,
                chart_json=chart_json_str,
                table_metadata_csv=table_metadata_csv
            )
            return self._parse_judge_output(output, "table_metadata")
        except RateLimitExhaustedError:
            # Re-raise to stop the pipeline - this is FATAL
            raise
        except Exception as e:
            print(f"Error judging table metadata: {str(e)}")
            # Return default report on non-fatal error
            return MetadataTypeReport(
                metadata_type="table_metadata",
                scores={"completeness": 0, "accuracy": 0, "clarity": 0, "confidence": 0},
                missing_items=[],
                quality_issues=[f"Error during judging: {str(e)}"],
                recommendations=["Fix judging error and retry"],
                status="POOR"
            )
    
    def judge_column_metadata(self, chart_json: Dict, column_metadata_csv: str) -> MetadataTypeReport:
        """
        Judge column metadata quality.
        
        Args:
            chart_json: Original chart JSON dictionary
            column_metadata_csv: CSV content of column metadata file
            
        Returns:
            MetadataTypeReport with scores and feedback
            
        Raises:
            RateLimitExhaustedError: If rate limit retries are exhausted (FATAL)
        """
        chart_json_str = json.dumps(chart_json, indent=2)
        
        try:
            # Use retry wrapper for rate limit handling
            output = call_judge_with_retry(
                self.column_judge,
                chart_json=chart_json_str,
                column_metadata_csv=column_metadata_csv
            )
            return self._parse_judge_output(output, "column_metadata")
        except RateLimitExhaustedError:
            # Re-raise to stop the pipeline - this is FATAL
            raise
        except Exception as e:
            print(f"Error judging column metadata: {str(e)}")
            return MetadataTypeReport(
                metadata_type="column_metadata",
                scores={"completeness": 0, "accuracy": 0, "business_context": 0, "confidence": 0},
                missing_items=[],
                quality_issues=[f"Error during judging: {str(e)}"],
                recommendations=["Fix judging error and retry"],
                status="POOR"
            )
    
    def judge_joining_conditions(self, chart_json: Dict, joining_conditions_csv: str) -> MetadataTypeReport:
        """
        Judge joining conditions quality.
        
        Args:
            chart_json: Original chart JSON dictionary
            joining_conditions_csv: CSV content of joining conditions file
            
        Returns:
            MetadataTypeReport with scores and feedback
            
        Raises:
            RateLimitExhaustedError: If rate limit retries are exhausted (FATAL)
        """
        chart_json_str = json.dumps(chart_json, indent=2)
        
        try:
            # Use retry wrapper for rate limit handling
            output = call_judge_with_retry(
                self.joining_judge,
                chart_json=chart_json_str,
                joining_conditions_csv=joining_conditions_csv
            )
            return self._parse_judge_output(output, "joining_conditions")
        except RateLimitExhaustedError:
            # Re-raise to stop the pipeline - this is FATAL
            raise
        except Exception as e:
            print(f"Error judging joining conditions: {str(e)}")
            return MetadataTypeReport(
                metadata_type="joining_conditions",
                scores={"completeness": 0, "accuracy": 0, "context": 0, "confidence": 0},
                missing_items=[],
                quality_issues=[f"Error during judging: {str(e)}"],
                recommendations=["Fix judging error and retry"],
                status="POOR"
            )
    
    def judge_filter_conditions(self, chart_json: Dict, filter_conditions_txt: str) -> MetadataTypeReport:
        """
        Judge filter conditions quality.
        
        Args:
            chart_json: Original chart JSON dictionary
            filter_conditions_txt: Text content of filter conditions file
            
        Returns:
            MetadataTypeReport with scores and feedback
            
        Raises:
            RateLimitExhaustedError: If rate limit retries are exhausted (FATAL)
        """
        chart_json_str = json.dumps(chart_json, indent=2)
        
        try:
            # Use retry wrapper for rate limit handling
            output = call_judge_with_retry(
                self.filter_judge,
                chart_json=chart_json_str,
                filter_conditions_txt=filter_conditions_txt
            )
            return self._parse_judge_output(output, "filter_conditions")
        except RateLimitExhaustedError:
            # Re-raise to stop the pipeline - this is FATAL
            raise
        except Exception as e:
            print(f"Error judging filter conditions: {str(e)}")
            return MetadataTypeReport(
                metadata_type="filter_conditions",
                scores={"completeness": 0, "accuracy": 0, "clarity": 0, "confidence": 0},
                missing_items=[],
                quality_issues=[f"Error during judging: {str(e)}"],
                recommendations=["Fix judging error and retry"],
                status="POOR"
            )
    
    def judge_definitions(self, chart_json: Dict, definitions_csv: str) -> MetadataTypeReport:
        """
        Judge definitions quality.
        
        Args:
            chart_json: Original chart JSON dictionary
            definitions_csv: CSV content of definitions file
            
        Returns:
            MetadataTypeReport with scores and feedback
            
        Raises:
            RateLimitExhaustedError: If rate limit retries are exhausted (FATAL)
        """
        chart_json_str = json.dumps(chart_json, indent=2)
        
        try:
            # Use retry wrapper for rate limit handling
            output = call_judge_with_retry(
                self.definitions_judge,
                chart_json=chart_json_str,
                definitions_csv=definitions_csv
            )
            return self._parse_judge_output(output, "definitions")
        except RateLimitExhaustedError:
            # Re-raise to stop the pipeline - this is FATAL
            raise
        except Exception as e:
            print(f"Error judging definitions: {str(e)}")
            return MetadataTypeReport(
                metadata_type="definitions",
                scores={"completeness": 0, "accuracy": 0, "usefulness": 0, "confidence": 0},
                missing_items=[],
                quality_issues=[f"Error during judging: {str(e)}"],
                recommendations=["Fix judging error and retry"],
                status="POOR"
            )
    
    def judge_all_metadata(
        self,
        chart_json: Dict,
        table_metadata_csv: Optional[str] = None,
        column_metadata_csv: Optional[str] = None,
        joining_conditions_csv: Optional[str] = None,
        filter_conditions_txt: Optional[str] = None,
        definitions_csv: Optional[str] = None
    ) -> Dict[str, MetadataTypeReport]:
        """
        Judge all metadata types in a single call.
        
        Args:
            chart_json: Original chart JSON dictionary
            table_metadata_csv: CSV content of table metadata (optional)
            column_metadata_csv: CSV content of column metadata (optional)
            joining_conditions_csv: CSV content of joining conditions (optional)
            filter_conditions_txt: Text content of filter conditions (optional)
            definitions_csv: CSV content of definitions (optional)
            
        Returns:
            Dictionary mapping metadata type to MetadataTypeReport
        """
        reports = {}
        
        if table_metadata_csv:
            print("Judging table metadata...")
            reports["table_metadata"] = self.judge_table_metadata(chart_json, table_metadata_csv)
        
        if column_metadata_csv:
            print("Judging column metadata...")
            reports["column_metadata"] = self.judge_column_metadata(chart_json, column_metadata_csv)
        
        if joining_conditions_csv:
            print("Judging joining conditions...")
            reports["joining_conditions"] = self.judge_joining_conditions(chart_json, joining_conditions_csv)
        
        if filter_conditions_txt:
            print("Judging filter conditions...")
            reports["filter_conditions"] = self.judge_filter_conditions(chart_json, filter_conditions_txt)
        
        if definitions_csv:
            print("Judging definitions...")
            reports["definitions"] = self.judge_definitions(chart_json, definitions_csv)
        
        return reports
    
    @staticmethod
    def generate_summary_report(reports: Dict[str, MetadataTypeReport]) -> Dict[str, Any]:
        """
        Generate summary statistics from all reports.
        
        Args:
            reports: Dictionary of metadata type reports
            
        Returns:
            Summary dictionary with overall statistics
        """
        if not reports:
            return {
                "overall_confidence": 0.0,
                "status": "POOR",
                "average_scores": {},
                "total_issues": {
                    "missing_items": 0,
                    "quality_issues": 0,
                    "recommendations": 0
                }
            }
        
        # Calculate averages
        completeness_scores = [r.scores.get("completeness", 0) for r in reports.values()]
        accuracy_scores = [r.scores.get("accuracy", 0) for r in reports.values()]
        confidence_scores = [r.scores.get("confidence", 0) for r in reports.values()]
        
        # Count issues
        total_missing = sum(len(r.missing_items) for r in reports.values())
        total_quality_issues = sum(len(r.quality_issues) for r in reports.values())
        total_recommendations = sum(len(r.recommendations) for r in reports.values())
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Classify overall status
        if overall_confidence >= 90:
            status = "EXCELLENT"
        elif overall_confidence >= 75:
            status = "GOOD"
        elif overall_confidence >= 60:
            status = "ACCEPTABLE"
        elif overall_confidence >= 40:
            status = "NEEDS_IMPROVEMENT"
        else:
            status = "POOR"
        
        return {
            "overall_confidence": round(overall_confidence, 2),
            "status": status,
            "average_scores": {
                "completeness": round(sum(completeness_scores) / len(completeness_scores), 2) if completeness_scores else 0.0,
                "accuracy": round(sum(accuracy_scores) / len(accuracy_scores), 2) if accuracy_scores else 0.0
            },
            "total_issues": {
                "missing_items": total_missing,
                "quality_issues": total_quality_issues,
                "recommendations": total_recommendations
            }
        }


# ============================================================================
# Helper Functions
# ============================================================================

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


def evaluate_all_metadata_types(
    chart_json: Dict,
    table_metadata_csv: str,
    column_metadata_csv: str,
    joining_conditions_csv: str,
    filter_conditions_txt: str,
    definitions_csv: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run all 5 judges and return unified results.
    
    Args:
        chart_json: Original chart JSON dictionary
        table_metadata_csv: CSV content of table metadata
        column_metadata_csv: CSV content of column metadata
        joining_conditions_csv: CSV content of joining conditions
        filter_conditions_txt: Text content of filter conditions
        definitions_csv: CSV content of definitions
        api_key: LLM API key (optional)
        model: LLM model name (optional)
        base_url: LLM base URL (optional)
        
    Returns:
        {
            'tables': {
                'confidence_score': 90,
                'quality_issues': '...',
                'recommendations': '...'
            },
            'columns': {...},
            'joins': {...},
            'filters': {...},
            'definitions': {...}
        }
    """
    judge = MetadataQualityJudge(api_key=api_key, model=model, base_url=base_url)
    
    results = {}
    
    # Table judge
    if table_metadata_csv:
        try:
            table_report = judge.judge_table_metadata(chart_json, table_metadata_csv)
            results['tables'] = {
                'confidence_score': table_report.scores.get('confidence', 0),
                'quality_issues': '; '.join(table_report.quality_issues),
                'recommendations': '; '.join(table_report.recommendations),
                'missing_items': table_report.missing_items,
                'status': table_report.status
            }
        except RateLimitExhaustedError:
            # FATAL: Re-raise to stop pipeline
            raise
        except Exception as e:
            results['tables'] = {
                'confidence_score': 0,
                'quality_issues': f'Error: {str(e)}',
                'recommendations': 'Retry evaluation',
                'missing_items': [],
                'status': 'ERROR'
            }
    
    # Column judge
    if column_metadata_csv:
        try:
            column_report = judge.judge_column_metadata(chart_json, column_metadata_csv)
            results['columns'] = {
                'confidence_score': column_report.scores.get('confidence', 0),
                'quality_issues': '; '.join(column_report.quality_issues),
                'recommendations': '; '.join(column_report.recommendations),
                'missing_items': column_report.missing_items,
                'status': column_report.status
            }
        except RateLimitExhaustedError:
            # FATAL: Re-raise to stop pipeline
            raise
        except Exception as e:
            results['columns'] = {
                'confidence_score': 0,
                'quality_issues': f'Error: {str(e)}',
                'recommendations': 'Retry evaluation',
                'missing_items': [],
                'status': 'ERROR'
            }
    
    # Joining conditions judge
    if joining_conditions_csv:
        try:
            joins_report = judge.judge_joining_conditions(chart_json, joining_conditions_csv)
            results['joins'] = {
                'confidence_score': joins_report.scores.get('confidence', 0),
                'quality_issues': '; '.join(joins_report.quality_issues),
                'recommendations': '; '.join(joins_report.recommendations),
                'missing_items': joins_report.missing_items,
                'status': joins_report.status
            }
        except RateLimitExhaustedError:
            # FATAL: Re-raise to stop pipeline
            raise
        except Exception as e:
            results['joins'] = {
                'confidence_score': 0,
                'quality_issues': f'Error: {str(e)}',
                'recommendations': 'Retry evaluation',
                'missing_items': [],
                'status': 'ERROR'
            }
    
    # Filter conditions judge
    if filter_conditions_txt:
        try:
            filters_report = judge.judge_filter_conditions(chart_json, filter_conditions_txt)
            results['filters'] = {
                'confidence_score': filters_report.scores.get('confidence', 0),
                'quality_issues': '; '.join(filters_report.quality_issues),
                'recommendations': '; '.join(filters_report.recommendations),
                'missing_items': filters_report.missing_items,
                'status': filters_report.status
            }
        except RateLimitExhaustedError:
            # FATAL: Re-raise to stop pipeline
            raise
        except Exception as e:
            results['filters'] = {
                'confidence_score': 0,
                'quality_issues': f'Error: {str(e)}',
                'recommendations': 'Retry evaluation',
                'missing_items': [],
                'status': 'ERROR'
            }
    
    # Definitions judge
    if definitions_csv:
        try:
            defs_report = judge.judge_definitions(chart_json, definitions_csv)
            results['definitions'] = {
                'confidence_score': defs_report.scores.get('confidence', 0),
                'quality_issues': '; '.join(defs_report.quality_issues),
                'recommendations': '; '.join(defs_report.recommendations),
                'missing_items': defs_report.missing_items,
                'status': defs_report.status
            }
        except RateLimitExhaustedError:
            # FATAL: Re-raise to stop pipeline
            raise
        except Exception as e:
            results['definitions'] = {
                'confidence_score': 0,
                'quality_issues': f'Error: {str(e)}',
                'recommendations': 'Retry evaluation',
                'missing_items': [],
                'status': 'ERROR'
            }
    
    return results


def load_chart_json(dashboard_id: int, extracted_meta_dir: str = "extracted_meta") -> Dict:
    """
    Load chart JSON for a dashboard.
    
    Args:
        dashboard_id: Dashboard ID
        extracted_meta_dir: Directory containing extracted metadata
        
    Returns:
        Chart JSON dictionary
    """
    json_file = f"{extracted_meta_dir}/{dashboard_id}/{dashboard_id}_json.json"
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Chart JSON not found: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_metadata_file(dashboard_id: int, file_type: str, extracted_meta_dir: str = "extracted_meta") -> Optional[str]:
    """
    Load metadata file content.
    
    Args:
        dashboard_id: Dashboard ID
        file_type: Type of metadata file (table_metadata, column_metadata, etc.)
        extracted_meta_dir: Directory containing extracted metadata
        
    Returns:
        File content as string, or None if file doesn't exist
    """
    file_mapping = {
        "table_metadata": f"{dashboard_id}_table_metadata.csv",
        "column_metadata": f"{dashboard_id}_columns_metadata.csv",
        "joining_conditions": f"{dashboard_id}_joining_conditions.csv",
        "filter_conditions": f"{dashboard_id}_filter_conditions.txt",
        "definitions": f"{dashboard_id}_definitions.csv"
    }
    
    if file_type not in file_mapping:
        raise ValueError(f"Unknown file type: {file_type}")
    
    file_path = f"{extracted_meta_dir}/{dashboard_id}/{file_mapping[file_type]}"
    
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def judge_dashboard_metadata(
    dashboard_id: int,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    extracted_meta_dir: str = "extracted_meta"
) -> MetadataQualityReport:
    """
    Judge metadata quality for a complete dashboard.
    
    Args:
        dashboard_id: Dashboard ID
        api_key: Anthropic API key (optional)
        model: LLM model name (optional)
        base_url: Custom API base URL (optional)
        extracted_meta_dir: Directory containing extracted metadata
        
    Returns:
        Complete MetadataQualityReport
    """
    # Load chart JSON
    chart_json = load_chart_json(dashboard_id, extracted_meta_dir)
    
    # Load metadata files
    table_metadata_csv = load_metadata_file(dashboard_id, "table_metadata", extracted_meta_dir)
    column_metadata_csv = load_metadata_file(dashboard_id, "column_metadata", extracted_meta_dir)
    joining_conditions_csv = load_metadata_file(dashboard_id, "joining_conditions", extracted_meta_dir)
    filter_conditions_txt = load_metadata_file(dashboard_id, "filter_conditions", extracted_meta_dir)
    definitions_csv = load_metadata_file(dashboard_id, "definitions", extracted_meta_dir)
    
    # Initialize judge
    judge = MetadataQualityJudge(api_key=api_key, model=model, base_url=base_url)
    
    # Judge all metadata
    reports = judge.judge_all_metadata(
        chart_json=chart_json,
        table_metadata_csv=table_metadata_csv,
        column_metadata_csv=column_metadata_csv,
        joining_conditions_csv=joining_conditions_csv,
        filter_conditions_txt=filter_conditions_txt,
        definitions_csv=definitions_csv
    )
    
    # Generate summary
    summary = MetadataQualityJudge.generate_summary_report(reports)
    
    # Create complete report
    from datetime import datetime
    quality_report = MetadataQualityReport(
        dashboard_id=dashboard_id,
        summary=summary,
        detailed_reports={k: r for k, r in reports.items()},
        timestamp=datetime.now().isoformat()
    )
    
    return quality_report


def save_quality_report(quality_report: MetadataQualityReport, output_path: Optional[str] = None):
    """
    Save quality report to JSON file.
    
    Args:
        quality_report: MetadataQualityReport to save
        output_path: Output file path (default: extracted_meta/{dashboard_id}/{dashboard_id}_quality_report.json)
    """
    if output_path is None:
        output_path = f"extracted_meta/{quality_report.dashboard_id}/{quality_report.dashboard_id}_quality_report.json"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert to dict
    report_dict = {
        "dashboard_id": quality_report.dashboard_id,
        "timestamp": quality_report.timestamp,
        "summary": quality_report.summary,
        "detailed_reports": {
            k: {
                "metadata_type": v.metadata_type,
                "scores": v.scores,
                "missing_items": v.missing_items,
                "quality_issues": v.quality_issues,
                "recommendations": v.recommendations,
                "status": v.status
            }
            for k, v in quality_report.detailed_reports.items()
        }
    }
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)
    
    print(f"Quality report saved to: {output_path}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(
        description='Judge metadata quality for a dashboard'
    )
    parser.add_argument(
        'dashboard_id',
        type=int,
        help='Dashboard ID to judge'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='Anthropic API key (default: from config or env)'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='LLM model name (default: from config)'
    )
    parser.add_argument(
        '--base-url',
        type=str,
        help='Custom API base URL (default: from config)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='extracted_meta',
        help='Directory containing extracted metadata (default: extracted_meta)'
    )
    
    args = parser.parse_args()
    
    try:
        print(f"\n{'='*80}")
        print(f"METADATA QUALITY JUDGE")
        print(f"{'='*80}")
        print(f"Dashboard ID: {args.dashboard_id}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Judge metadata
        quality_report = judge_dashboard_metadata(
            dashboard_id=args.dashboard_id,
            api_key=args.api_key,
            model=args.model,
            base_url=args.base_url,
            extracted_meta_dir=args.output_dir
        )
        
        # Save report
        save_quality_report(quality_report)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"QUALITY JUDGMENT SUMMARY")
        print(f"{'='*80}")
        print(f"Overall Confidence: {quality_report.summary['overall_confidence']:.2f}")
        print(f"Status: {quality_report.summary['status']}")
        print(f"\nAverage Scores:")
        print(f"  Completeness: {quality_report.summary['average_scores']['completeness']:.2f}")
        print(f"  Accuracy: {quality_report.summary['average_scores']['accuracy']:.2f}")
        print(f"\nTotal Issues:")
        print(f"  Missing Items: {quality_report.summary['total_issues']['missing_items']}")
        print(f"  Quality Issues: {quality_report.summary['total_issues']['quality_issues']}")
        print(f"  Recommendations: {quality_report.summary['total_issues']['recommendations']}")
        print(f"\nDetailed Reports:")
        for metadata_type, report in quality_report.detailed_reports.items():
            print(f"  {metadata_type}: {report.status} (confidence: {report.scores['confidence']:.2f})")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

