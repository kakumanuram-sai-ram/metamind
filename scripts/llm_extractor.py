"""
LLM-based extractor for tables and columns from dashboard JSON using DSPy
"""
import json
import os
import sys
import threading
from typing import Dict, List, Optional
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate
import pandas as pd
from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL

# Add parent directory to path for dspy_examples.py
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_scripts_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)


class TableColumnExtractor(dspy.Signature):
    """
    Extract table and column information from dashboard chart SQL queries.
    Identify source tables, original column names, and aliases.
    
    Instructions:
    1. Identify ALL source tables used in the SQL (format: catalog.schema.table)
    2. EXCLUDE CTEs (Common Table Expressions) - only include actual source tables
    3. For each source table, identify the ORIGINAL column names (not aliases)
    4. Map aliases to their original column names
    5. If a table uses SELECT *, you may not see all columns - that's okay, list what you can identify
    """
    
    sql_query: str = dspy.InputField(desc="SQL query from dashboard chart")
    chart_metadata: str = dspy.InputField(desc="Chart metadata including metrics and columns")
    
    tables_used: str = dspy.OutputField(desc="Comma-separated list of source table names in format catalog.schema.table (exclude CTEs, only actual source tables)")
    original_columns: str = dspy.OutputField(desc="JSON object mapping table_name to list of original column names from that table. Only include columns that are actually referenced in the SQL, not computed/aliased columns.")
    column_aliases: str = dspy.OutputField(desc="JSON object mapping alias_name to original_column_name. Include computed columns like date_format(day_id,'Day %d') AS Day_ mapped to the source column 'day_id'")


class TermDefinitionExtractor(dspy.Signature):
    """
    Extract term definitions from dashboard charts, including metrics, calculated fields, synonyms, and categories.
    
    SYSTEM PROMPT: Term Definition Generator
    
    ## Objective
    Analyze dashboard charts, SQL queries, chart labels, and metrics to extract comprehensive term definitions including metrics, calculated fields, synonyms, and categories. Generate definitions that explain what each term represents, how it's calculated, and its business context.
    
    ## Output Format
    CSV format with columns: term, type, definition, business_alias
    
    ## Term Types
    
    **Metric**: A measurable quantity (e.g., "Total Sessions", "Reach", "Conversions")
    **Metric / Calculated Field**: A derived metric calculated from other metrics (e.g., "CTR", "Impression Frequency", "Average Frequency")
    **Synonym**: Alternative names for the same concept (e.g., "Customers" = "Total Users", "Audience" = "Total Users")
    **Category**: A grouping of related metrics (e.g., "User Engagement Metrics", "CG conversion")
    
    ## Extraction Rules
    
    ### 1. Term Identification
    - Extract from chart labels, metric names, column aliases
    - Include both source metrics and calculated/derived metrics
    - Identify synonyms (same concept, different names)
    - Identify categories (groups of related metrics)
    
    ### 2. Definition Guidelines
    - **For Metrics**: Explain what is being measured (e.g., "Total sum of impressions", "Unique count of users")
    - **For Calculated Fields**: Explain the calculation formula and what it represents (e.g., "Total Clicks divided by Total Impressions", "Total Impressions Divided by Total Users")
    - **For Synonyms**: Reference the primary term (e.g., "Total Users")
    - **For Categories**: Explain what metrics are included (e.g., "Impressions, Clicks and CTRs")
    - Include business context when relevant
    - Be concise but complete (1-2 sentences typically)
    
    ### 3. Business Alias
    - Include alternative names or abbreviations used in business context
    - Format: "Alias1, also referred as Alias2"
    - Examples: "TG/Target Group conversion", "CG/Control Group conversion", "Unique Impression(s) also referred as Total Impression(s)"
    - Leave empty if no business alias exists
    
    ### 4. Type Classification
    
    **Metric**: Direct measurement from data
    - Examples: Total Sessions, Reach, Conversions, hits
    
    **Metric / Calculated Field**: Derived from other metrics
    - Examples: CTR, Impression Frequency, Average Frequency, session per user
    
    **Synonym**: Alternative name for existing term
    - Examples: Customers = Total Users, Audience = Total Users
    
    **Category**: Group of related metrics
    - Examples: User Engagement Metrics, CG conversion
    
    ## Critical Instructions
    
    ### DO:
    ✅ Extract all unique terms from chart labels and metrics
    ✅ Identify calculated fields from SQL expressions
    ✅ Group related terms and identify synonyms
    ✅ Provide clear, concise definitions
    ✅ Include calculation formulas for calculated fields
    ✅ Identify business aliases and abbreviations
    ✅ Use proper type classification
    
    ### DON'T:
    ❌ Create duplicate entries for the same term
    ❌ Omit calculation logic for calculated fields
    ❌ Use vague definitions
    ❌ Miss business aliases when they exist
    ❌ Mix up Metric vs Metric / Calculated Field types
    """
    
    dashboard_title: str = dspy.InputField(desc="Dashboard title providing business context")
    chart_names_and_labels: str = dspy.InputField(desc="JSON string with all chart names and their metric labels")
    sql_queries: str = dspy.InputField(desc="JSON string with all SQL queries showing calculation logic")
    metrics_context: str = dspy.InputField(desc="JSON string with detailed metric information including expressions and labels")
    
    term_definitions: str = dspy.OutputField(desc="JSON array of term definitions. Each definition should have: term (string), type (string: 'Metric', 'Metric / Calculated Field', 'Synonym', or 'Category'), definition (string: clear explanation), business_alias (string: alternative names/abbreviations, empty if none). Extract all unique terms from charts, identify calculated fields, synonyms, and categories.")


class FilterConditionsExtractor(dspy.Signature):
    """
    Transform Superset dashboard chart metadata into structured filter condition documentation. Consolidate redundant metrics aggressively, represent common calculation patterns concisely, and document all SQL logic with clear business context.
    
    SYSTEM PROMPT: Filter Conditions Metadata Generator
    
    ## Objective
    Transform Superset dashboard chart metadata into structured filter condition documentation. Consolidate redundant metrics aggressively, represent common calculation patterns concisely, and document all SQL logic with clear business context.
    
    ## Output Format
    
    ```
    ## {Metric Name}
    
    {Single paragraph (80-150 words) explaining: what the metric measures, its business purpose, what filters are applied, what it represents, and if it has parameter variants (e.g., "segmented by payee PSP including ptyes, pthdfc, ptaxis, ptsbi").}
    
    -- tables_involved
    {schema.table_name} {alias}
    
    --- standard filters to be applied unless specifically requested for a different categorical value
    --- {comment explaining filter purpose}
    {alias}.{column} {operator} {value} AND
    --- {comment explaining filter purpose}
    {alias}.{column} {operator} {value}
    
    --- specific filters
    --- {comment explaining filter purpose}
    --- for variants: {alias}.{column} IN ({param_name}: value1, value2, value3)
    {alias}.{column} {operator} {value/pattern}
    
    --- calculation_logic
    {pattern_reference OR concise calculation}
    
    ---
    
    [Additional metrics follow same format]
    
    ---
    
    ## Common Calculation Patterns
    
    ### {pattern_name}
    **Description**: {what it does}
    **Formulas**: {actual SQL formulas with placeholders}
    **Usage**: {how to apply it}
    ```
    
    ## Consolidation Rules
    
    **MANDATORY: Consolidate if 3+ charts differ ONLY in one parameter value**
    
    Trigger conditions:
    - Same table source
    - Same business purpose (>80% overlap)
    - Same filters except ONE column value
    
    Action:
    - Create ONE entry with generic name ("by Payee PSP" not "PSP=HDFC")
    - Show parameter inline: `txn.payee_handle IN ({payee_psp}: ptyes, pthdfc, ptaxis, ptsbi)`
    - Mention variants in description: "segmented by payee PSP including..."
    
    DO NOT create separate entries for each parameter value.
    
    ## Calculation Logic Rules
    
    **For patterns appearing 3+ times:**
    ```sql
    --- calculation_logic
    pattern: temporal_daily_comparison
    base_metric: count(txn_id)
    dimensions: [hour_, payee_handle]
    ```
    
    **For unique calculations:**
    ```sql
    --- calculation_logic
    count(distinct txn.txn_id) as txn_count,
    sum(txn.amount) as total_amount
    ```
    
    **Include Common Calculation Patterns section at end** documenting reusable formulas.
    
    ## Metric Naming
    
    **Consolidated metrics:**
    - ✅ "P2P Inward Transactions by Payee PSP"
    - ❌ "P2P Inward Transaction (Payee PSP = HDFC)"
    
    **Distinct metrics:**
    - ✅ "P2P Transactions" (flow='p2p')
    - ✅ "P2M Transactions" (flow='p2m')
    
    ## Filter Documentation
    
    **Parameterized filters:**
    ```sql
    --- specific filters
    --- segment by payee PSP for partner performance analysis
    --- parameter values: ptyes (Yes Bank), pthdfc (HDFC), ptaxis (Axis), ptsbi (SBI)
    txn.payee_handle IN ({payee_psp})
    ```
    
    **Categorical filters:**
    ```sql
    --- specific filters
    --- PSP ecosystem categorization
    CASE 
      WHEN lower(txn.payer_handle) IN ('paytm','ptyes','ptaxis','pthdfc','ptsbi') 
      THEN 'Payer = Paytm'
      ELSE 'Payer = Other'
    END
    ```
    
    ## Business Descriptions
    
    For consolidated metrics:
    - Mention it's segmented: "tracks X segmented by Y"
    - List parameter values: "including ptyes, pthdfc, ptaxis, ptsbi"
    - Explain segmentation purpose
    - 80-150 words total
    - Single paragraph, no bullets
    
    Assume reader has access to separate definitions file - don't explain basic terms.
    
    ## Common Calculation Patterns Section
    
    Document reusable patterns at end:
    
    ```
    ## Common Calculation Patterns
    
    ### temporal_daily_comparison
    **Description**: Compare today vs yesterday and last month same day with growth %
    **Formulas**:
    - todays_value: {metric} FILTER(WHERE date(created_on) = current_date)
    - yesterdays_value: {metric} FILTER(WHERE date(created_on) = current_date - interval '1' day)
    - last_month_same_day: {metric} FILTER(WHERE date(created_on) = current_date - interval '1' month)
    - dod_growth: (todays_value / yesterdays_value) - 1
    - mom_growth: (todays_value / last_month_same_day) - 1
    **Usage**: Replace {metric} with COUNT(txn_id), SUM(amount), etc.
    ```
    
    ## Critical Instructions
    
    ### DO:
    ✅ Consolidate 3+ similar charts into 1 entry with parameters
    ✅ Reference calculation patterns instead of repeating formulas
    ✅ Show parameters inline: `IN ({param}: values)`
    ✅ Mention variants in description
    ✅ Use lowercase for SQL keywords in comments
    ✅ Include Common Patterns section at end
    ✅ Keep descriptions 80-150 words
    ✅ Use generic names for parameterized metrics
    
    ### DON'T:
    ❌ Create separate entries for parameter value changes only
    ❌ Repeat calculation formulas across metrics
    ❌ Use parameter-specific names for consolidated metrics
    ❌ Include term definitions (separate definitions file exists)
    ❌ Write verbose temporal filter logic repeatedly
    ❌ Exceed 150 words in descriptions
    ❌ Lose unique filter conditions during consolidation
    """
    
    chart_name: str = dspy.InputField(desc="Chart name providing business context")
    chart_metrics: str = dspy.InputField(desc="JSON string with chart metrics and their labels")
    sql_query: str = dspy.InputField(desc="SQL query showing filter conditions in WHERE clause")
    chart_filters: str = dspy.InputField(desc="JSON string with chart filter metadata from Superset")
    tables_involved: str = dspy.InputField(desc="Comma-separated list of tables used in this chart")
    dashboard_title: str = dspy.InputField(desc="Dashboard title providing overall context")
    all_charts_context: str = dspy.InputField(desc="JSON string with all charts in dashboard to enable consolidation detection")
    
    use_case_description: str = dspy.OutputField(desc="Single paragraph (80-150 words) explaining: what the metric measures, its business purpose, what filters are applied, what it represents, and if it has parameter variants (e.g., 'segmented by payee PSP including ptyes, pthdfc, ptaxis, ptsbi'). Mention variants in description if consolidated. NO bullet points, NO multiple paragraphs.")
    filter_conditions_sql: str = dspy.OutputField(desc="SQL code following exact format: -- tables_involved section with schema.table alias, --- standard filters section with comments and AND connectors, --- specific filters section with comments (show parameters inline: IN ({param}: values)), --- calculation_logic section (use pattern references for common patterns, full formulas only for unique). Do NOT include WHERE clause wrapper - just list conditions with AND connectors.")
    common_patterns: str = dspy.OutputField(desc="Common Calculation Patterns section documenting reusable formulas that appear 3+ times. Format: ### pattern_name, **Description**, **Formulas** (with placeholders), **Usage**. Only include if patterns are identified.")


class JoiningConditionExtractor(dspy.Signature):
    """
    Extract and describe joining conditions between two tables based on SQL query analysis.
    
    Instructions:
    1. Analyze the SQL query to identify how table1 and table2 are joined
    2. Extract the exact joining condition (e.g., table1.customer_id = table2.customer_id_payer)
    3. Generate remarks explaining when and why to use this join, what business context it enables
    4. If no explicit JOIN is found, analyze WHERE clause conditions that connect the tables
    """
    
    table1: str = dspy.InputField(desc="First table name (full name: catalog.schema.table)")
    table2: str = dspy.InputField(desc="Second table name (full name: catalog.schema.table)")
    sql_query: str = dspy.InputField(desc="SQL query that uses both tables")
    chart_name: str = dspy.InputField(desc="Chart name providing business context")
    dashboard_title: str = dspy.InputField(desc="Dashboard title providing business context")
    
    joining_condition: str = dspy.OutputField(desc="Exact joining condition in format: table1.column = table2.column (e.g., table1.customer_id = table2.customer_id_payer). If no explicit join found, extract from WHERE clause or infer based on common column patterns.")
    remarks: str = dspy.OutputField(desc="Detailed explanation of when and why to use this join, what business analysis it enables, and how it connects the data from both tables. Should be 2-3 sentences explaining the business context.")


class ColumnMetadataExtractor(dspy.Signature):
    """
    Extract column description based on usage context, chart labels, aliases, and derived column logic.
    
    Instructions:
    1. Analyze how the column is used in the dashboard:
       - Chart labels and aliases provide business context
       - Derived column logic shows how the column is transformed/used
       - SQL usage patterns indicate the column's purpose
    2. Generate a clear, concise description that explains:
       - What the column represents
       - How it's used in business context
       - Any important characteristics or constraints
    3. Keep descriptions concise but informative (1-2 sentences typically)
    """
    
    column_name: str = dspy.InputField(desc="Column name to describe")
    table_name: str = dspy.InputField(desc="Table name containing this column")
    column_datatype: str = dspy.InputField(desc="Data type of the column")
    chart_labels_and_aliases: str = dspy.InputField(desc="JSON string with chart labels and aliases used for this column in the dashboard")
    derived_column_usage: str = dspy.InputField(desc="JSON string showing how this column is used in derived columns (derived column logic)")
    sql_usage_context: str = dspy.InputField(desc="Sample SQL queries showing how this column is used")
    
    column_description: str = dspy.OutputField(desc="Clear, concise description of what the column represents and how it's used in business context (1-2 sentences)")


class TableMetadataExtractor(dspy.Signature):
    """
    Extract comprehensive table metadata including data description, business use cases, 
    refresh frequency, vertical, partition column, and relationship context.
    
    Instructions:
    1. TABLE DESCRIPTION should include TWO distinct sections:
       - data_description: Detailed description of what data the table contains, its structure, 
         key data categories, and primary purpose
       - business_description: Business use cases, contexts where this table is used, 
         and how it supports business operations
    
    2. REFRESH FREQUENCY: Estimate based on table usage patterns (e.g., Daily, Hourly, Real-time, Weekly)
    
    3. VERTICAL: Identify the business vertical (e.g., UPI, Payments, Lending, Marketing, etc.)
    
    4. PARTITION COLUMN: Identify the partition column if evident from usage (e.g., dt, date, day_id)
    
    5. REMARKS: Any additional notes or observations
    
    6. RELATIONSHIP CONTEXT: Describe how this table relates to other tables, joins, and usage contexts
    """
    
    dashboard_title: str = dspy.InputField(desc="Dashboard title providing business context")
    chart_names_and_labels: str = dspy.InputField(desc="JSON string with chart names and their metric/column labels - provides business context")
    table_name: str = dspy.InputField(desc="Table name in format hive.schema.table")
    table_columns: str = dspy.InputField(desc="JSON string with column names, datatypes, and usage context from the dashboard")
    sql_queries_context: str = dspy.InputField(desc="Sample SQL queries using this table - provides usage patterns")
    
    table_description: str = dspy.OutputField(desc="Comprehensive table description with TWO sections: (1) data_description: what data the table contains, its structure, key categories, primary purpose. (2) business_description: business use cases, contexts where used, how it supports operations. Format: 'data_description: [detailed description]\\n\\nbusiness_description: [detailed description]'")
    refresh_frequency: str = dspy.OutputField(desc="Estimated refresh frequency (e.g., Daily, Hourly, Real-time, Weekly)")
    vertical: str = dspy.OutputField(desc="Business vertical (e.g., UPI, Payments, Lending, Marketing)")
    partition_column: str = dspy.OutputField(desc="Partition column name if evident (e.g., dt, date, day_id), or empty if not clear")
    remarks: str = dspy.OutputField(desc="Additional notes or observations")
    relationship_context: str = dspy.OutputField(desc="How this table relates to other tables, common joins, and usage contexts")


class SourceTableColumnExtractor(dspy.Signature):
    """
    Extract source tables, source columns, derived columns, and derived column logic from SQL queries.
    
    CRITICAL INSTRUCTIONS - Follow these precisely:
    
    1. SOURCE TABLES:
       - Identify ONLY actual physical source tables (e.g., user_paytm_payments.upi_tracker_insight)
       - EXCLUDE: CTEs (WITH clauses), subqueries, virtual tables, UNION result aliases
       - Format: schema.table (e.g., user_paytm_payments.upi_tracker_insight) or 
                catalog.schema.table (e.g., hive.user_paytm_payments.upi_tracker_insight)
       - For UNION ALL queries, identify ALL source tables from both sides
    
    2. SOURCE COLUMNS:
       - List ONLY base or original column names from source tables
       - EXCLUDE: computed columns, aliases, aggregations, window functions
       - Examples: day_id, segment, mau, dau, n_txns, gmv, user_id, transaction_id
       - Include columns used in WHERE, GROUP BY, ORDER BY, and SELECT clauses
       - If SELECT * is used, from the chart json, list all identifiable columns from the source table
    
    3. DERIVED COLUMNS MAPPING:
       - Include ALL derived/computed columns from the entire query:
         * Aggregations: sum(), count(), avg(), max(), min()
         * Window functions: lag(), lead(), over(), row_number(), rank()
         * Date functions: date_format(), date_trunc(), extract()
         * CASE statements: case when ... then ... end
         * Computed columns in subqueries (e.g., mau_rolling, Day_, month_)
         * All aliases in SELECT clause (even if same source column)
       - For each derived column, provide:
         * source_column: The primary source column it's derived from
         * source_table: The source table name
         * logic: The exact SQL expression (preserve quotes, formatting)
    
    4. MAPPING RULES:
       - If a derived column uses multiple source columns, use the PRIMARY one
       - For window functions, identify the column being aggregated
       - For CASE statements, identify the column in the WHEN conditions
       - For date functions, identify the date column being transformed
       - Map subquery-derived columns to their source table and column
    
    5. OUTPUT FORMAT:
       - source_tables: Comma-separated, no spaces after commas
       - source_columns: Comma-separated, no spaces after commas
       - source_columns_aliases: JSON object mapping source column name to alias name
       - derived_columns_mapping: Valid JSON object with proper escaping
    """
    
    sql_query: str = dspy.InputField(desc="SQL query from dashboard chart - analyze the entire query including subqueries, UNION clauses, and all SELECT statements")
    chart_metadata: str = dspy.InputField(desc="Chart metadata including metrics, columns, chart_id, and chart_name - use this to understand column aliases and labels")
    
    source_tables: str = dspy.OutputField(desc="Comma-separated list of source table names in format schema.table (e.g., user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm). Only actual physical tables, exclude CTEs and virtual tables. For UNION queries, include all source tables from both sides.")
    source_columns: str = dspy.OutputField(desc="Comma-separated list of original column names from source tables (e.g., day_id, segment, mau, dau, n_txns, gmv). Only base columns, not computed/derived. Include all columns referenced in the query.")
    derived_columns_mapping: str = dspy.OutputField(desc="JSON object mapping each alias/derived column to {'source_column': 'col_name', 'source_table': 'schema.table', 'logic': 'exact_SQL_expression'}. Include ALL derived columns: aggregations, window functions, date functions, CASE statements, and subquery-computed columns. Preserve exact SQL syntax in logic field. Example: {\"Segments_\": {\"source_column\": \"segment\", \"source_table\": \"user_paytm_payments.upi_tracker_insight\", \"logic\": \"case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' end\"}, \"prev_month_mau\": {\"source_column\": \"mau\", \"source_table\": \"user_paytm_payments.upi_tracker_insight\", \"logic\": \"(sum(mau*1.0000)/lag(sum(mau)) over(partition by ... order by ...))-1\"}}")


# Global DSPy configuration - use a single instance per process
_dspy_lm = None
_dspy_extractor = None
_dspy_source_extractor = None
_dspy_lock = threading.Lock()

def _get_dspy_extractor(api_key: str, model: str, base_url: Optional[str] = None):
    """Get DSPy extractor, configure if needed (thread-safe)"""
    global _dspy_lm, _dspy_extractor
    with _dspy_lock:
        if _dspy_extractor is None:
            try:
                if _dspy_lm is None:
                    # Configure with custom base URL if provided
                    # When using custom base_url, need to specify provider in model name
                    if base_url:
                        # For custom proxy, use anthropic/ prefix
                        model_name = f"anthropic/{model}" if not model.startswith("anthropic/") else model
                    else:
                        model_name = model
                    
                    lm_kwargs = {
                        "model": model_name,
                        "api_key": api_key,
                        "api_provider": "anthropic"
                    }
                    if base_url:
                        # Note: base_url should NOT include /v1 - litellm adds it automatically
                        # If base_url ends with /v1, remove it to avoid /v1/v1/messages
                        clean_base_url = base_url.rstrip('/v1').rstrip('/')
                        lm_kwargs["api_base"] = clean_base_url
                    _dspy_lm = dspy.LM(**lm_kwargs)
                    dspy.configure(lm=_dspy_lm)
                _dspy_extractor = dspy.ChainOfThought(TableColumnExtractor)
            except RuntimeError as e:
                if "can only be changed by the thread" in str(e):
                    # Already configured, just create extractor
                    _dspy_extractor = dspy.ChainOfThought(TableColumnExtractor)
                else:
                    raise
    return _dspy_extractor

def _get_dspy_source_extractor(api_key: str, model: str, base_url: Optional[str] = None):
    """Get DSPy source extractor with examples, configure if needed (thread-safe)"""
    global _dspy_lm, _dspy_source_extractor
    with _dspy_lock:
        # Reset if base_url changes (for different proxy endpoints)
        if _dspy_source_extractor is None or (_dspy_lm and hasattr(_dspy_lm, 'api_base') and _dspy_lm.api_base != base_url):
            if _dspy_lm and hasattr(_dspy_lm, 'api_base') and _dspy_lm.api_base != base_url:
                _dspy_lm = None
                _dspy_source_extractor = None
        if _dspy_source_extractor is None:
            try:
                if _dspy_lm is None:
                    # Configure with custom base URL if provided
                    # When using custom base_url, need to specify provider in model name
                    if base_url:
                        # For custom proxy, use anthropic/ prefix
                        model_name = f"anthropic/{model}" if not model.startswith("anthropic/") else model
                    else:
                        model_name = model
                    
                    lm_kwargs = {
                        "model": model_name,
                        "api_key": api_key,
                        "api_provider": "anthropic"
                    }
                    if base_url:
                        # Note: base_url should NOT include /v1 - litellm adds it automatically
                        # If base_url ends with /v1, remove it to avoid /v1/v1/messages
                        clean_base_url = base_url.rstrip('/v1').rstrip('/')
                        lm_kwargs["api_base"] = clean_base_url
                    _dspy_lm = dspy.LM(**lm_kwargs)
                    dspy.configure(lm=_dspy_lm)
                
                # Create extractor
                extractor = dspy.ChainOfThought(SourceTableColumnExtractor)
                
                # Load examples if available
                try:
                    from dspy_examples import EXAMPLES as DSPY_EXAMPLES
                    if DSPY_EXAMPLES and len(DSPY_EXAMPLES) > 0:
                        # Use up to 5 examples for few-shot learning
                        num_examples = min(5, len(DSPY_EXAMPLES))
                        extractor.demos = DSPY_EXAMPLES[:num_examples]
                        print(f"Loaded {num_examples} DSPy examples for few-shot learning")
                except ImportError:
                    print("No DSPy examples found (dspy_examples.py not found or EXAMPLES not defined)")
                except Exception as e:
                    print(f"Warning: Could not load DSPy examples: {str(e)}")
                
                _dspy_source_extractor = extractor
            except RuntimeError as e:
                if "can only be changed by the thread" in str(e):
                    # Already configured, just create extractor
                    extractor = dspy.ChainOfThought(SourceTableColumnExtractor)
                    try:
                        from dspy_examples import EXAMPLES as DSPY_EXAMPLES
                        if DSPY_EXAMPLES and len(DSPY_EXAMPLES) > 0:
                            num_examples = min(5, len(DSPY_EXAMPLES))
                            extractor.demos = DSPY_EXAMPLES[:num_examples]
                    except:
                        pass
                    _dspy_source_extractor = extractor
                else:
                    raise
    return _dspy_source_extractor


class DashboardTableColumnExtractor:
    """Extract tables and columns from dashboard using LLM"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the LLM extractor
        
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var, or use config.LLM_API_KEY)
            model: Model to use (default: from config.LLM_MODEL)
            base_url: Custom API base URL (default: from config.LLM_BASE_URL)
        """
        # Get API key from parameter, env var, or config
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
        if not api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var, config.LLM_API_KEY, or pass api_key parameter")
        
        # Get model from parameter or config
        model = model or LLM_MODEL
        
        # Get base_url from parameter or config
        base_url = base_url or LLM_BASE_URL
        
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        # Get extractor (configured once globally)
        self.extractor = _get_dspy_extractor(api_key, model, base_url)
        self.source_extractor = _get_dspy_source_extractor(api_key, model, base_url)
    
    def extract_from_chart(self, chart: Dict) -> Dict:
        """
        Extract table and column information from a single chart
        
        Args:
            chart: Chart dictionary from dashboard JSON
            
        Returns:
            Dict with tables_used, original_columns, column_aliases
        """
        sql_query = chart.get('sql_query', '')
        if not sql_query:
            return {
                'tables_used': [],
                'original_columns': {},
                'column_aliases': {}
            }
        
        # Prepare chart metadata
        metrics = chart.get('metrics', [])
        columns_list = chart.get('columns', [])
        metadata = {
            'metrics': metrics,
            'columns': columns_list,
            'chart_id': chart.get('chart_id'),
            'chart_name': chart.get('chart_name')
        }
        
        # Use LLM to extract information
        result = self.extractor(
            sql_query=sql_query,
            chart_metadata=json.dumps(metadata, indent=2)
        )
        
        # Parse results
        tables_used = [t.strip() for t in result.tables_used.split(',') if t.strip()]
        
        try:
            original_columns = json.loads(result.original_columns)
        except:
            original_columns = {}
        
        try:
            column_aliases = json.loads(result.column_aliases)
        except:
            column_aliases = {}
        
        return {
            'tables_used': tables_used,
            'original_columns': original_columns,
            'column_aliases': column_aliases
        }
    
    def extract_source_from_chart(self, chart: Dict) -> Dict:
        """
        Extract source tables, source columns, derived columns, and derived column logic from a single chart
        
        Args:
            chart: Chart dictionary from dashboard JSON
            
        Returns:
            Dict with source_tables, source_columns, derived_columns_mapping
        """
        sql_query = chart.get('sql_query', '')
        if not sql_query:
            return {
                'source_tables': [],
                'source_columns': [],
                'derived_columns_mapping': {}
            }
        
        # Prepare chart metadata
        metrics = chart.get('metrics', [])
        columns_list = chart.get('columns', [])
        metadata = {
            'metrics': metrics,
            'columns': columns_list,
            'chart_id': chart.get('chart_id'),
            'chart_name': chart.get('chart_name')
        }
        
        # Use LLM to extract information
        result = self.source_extractor(
            sql_query=sql_query,
            chart_metadata=json.dumps(metadata, indent=2)
        )
        
        # Parse results
        source_tables = [t.strip() for t in result.source_tables.split(',') if t.strip()]
        source_columns = [c.strip() for c in result.source_columns.split(',') if c.strip()]
        
        try:
            derived_columns_mapping = json.loads(result.derived_columns_mapping)
        except:
            derived_columns_mapping = {}
        
        return {
            'source_tables': source_tables,
            'source_columns': source_columns,
            'derived_columns_mapping': derived_columns_mapping
        }
    
    def extract_from_dashboard(self, dashboard_info: Dict) -> List[Dict]:
        """
        Extract table and column information from entire dashboard
        
        Args:
            dashboard_info: Dashboard info dictionary
            
        Returns:
            List of dicts with: table_name, column_name, column_label__chart_json, data_type
        """
        from sql_parser import normalize_table_name
        from trino_client import get_column_datatypes_from_trino
        from config import BASE_URL, HEADERS
        
        charts = dashboard_info.get('charts', [])
        table_column_map = {}
        
        print(f"Extracting tables and columns from {len(charts)} charts using LLM...")
        
        # Extract from each chart
        for i, chart in enumerate(charts, 1):
            chart_id = chart.get('chart_id')
            print(f"  [{i}/{len(charts)}] Processing chart {chart_id}...")
            
            try:
                # Create new extractor instance for this chart (uses shared DSPy config)
                chart_extractor = DashboardTableColumnExtractor(api_key=self.api_key, model=self.model, base_url=self.base_url)
                chart_result = chart_extractor.extract_from_chart(chart)
                tables_used = chart_result['tables_used']
                original_columns = chart_result['original_columns']
                column_aliases = chart_result['column_aliases']
                
                # Get column labels from chart metadata
                column_labels = {}
                metrics = chart.get('metrics', [])
                columns_list = chart.get('columns', [])
                
                for metric in metrics:
                    if isinstance(metric, dict):
                        col = metric.get('column', {})
                        if isinstance(col, dict):
                            col_name = col.get('column_name')
                            label = metric.get('label') or col.get('verbose_name') or col_name
                            if col_name:
                                column_labels[col_name.lower()] = label
                
                if isinstance(columns_list, list):
                    for col_name in columns_list:
                        if isinstance(col_name, str) and col_name.lower() not in column_labels:
                            column_labels[col_name.lower()] = col_name
                
                # Process each table
                for table in tables_used:
                    normalized_table = normalize_table_name(table)
                    columns = original_columns.get(table, [])
                    
                    if not columns:
                        # If LLM didn't extract columns, try to get from aliases
                        # or use empty list
                        columns = []
                    
                    for column in columns:
                        # Get label if available
                        col_lower = column.lower()
                        column_label = column_labels.get(col_lower, column)
                        
                        # Create key for grouping
                        key = (normalized_table, column)
                        
                        if key not in table_column_map:
                            table_column_map[key] = {
                                'labels': {},
                                'data_type': None
                            }
                        
                        table_column_map[key]['labels'][chart_id] = column_label
                        
            except Exception as e:
                print(f"    Error processing chart {chart_id}: {str(e)}")
                continue
        
        # Get data types from Trino
        print("Fetching column data types from Trino...")
        trino_columns = get_column_datatypes_from_trino(dashboard_info, BASE_URL, HEADERS)
        
        # Convert to list format
        results = []
        for (table_name, column_name), info in table_column_map.items():
            column_label__chart_json = json.dumps(info['labels'], sort_keys=True)
            
            # Get data type from Trino
            data_type = info.get('data_type')
            if trino_columns:
                if table_name in trino_columns:
                    data_type = trino_columns[table_name].get(column_name)
                # Try without quotes
                table_no_quotes = table_name.replace('"', '')
                if table_no_quotes in trino_columns:
                    data_type = trino_columns[table_no_quotes].get(column_name)
            
            result = {
                'table_name': table_name,
                'column_name': column_name,
                'column_label__chart_json': column_label__chart_json
            }
            
            if data_type:
                result['data_type'] = data_type
            
            results.append(result)
        
        # Sort by table_name, then column_name
        results.sort(key=lambda x: (x['table_name'], x['column_name']))
        
        return results


def extract_table_column_mapping_llm(dashboard_info: Dict, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514") -> List[Dict]:
    """
    Extract table and column mapping using LLM
    
    Args:
        dashboard_info: Dashboard info dictionary
        api_key: Anthropic API key (optional, can use ANTHROPIC_API_KEY env var)
        model: Model to use (default: claude-sonnet-4-20250514)
    
    Returns:
        List of dicts with: table_name, column_name, column_label__chart_json, data_type
    """
    extractor = DashboardTableColumnExtractor(api_key=api_key, model=model)
    return extractor.extract_from_dashboard(dashboard_info)


def extract_source_tables_columns_llm(dashboard_info: Dict, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None) -> List[Dict]:
    """
    Extract source tables and columns using LLM for tables_columns.csv format
    
    This method extracts BOTH source columns and derived columns with their logic.
    Format: tables_involved, column_names, alias_column_name, source_or_derived, derived_column_logic
    
    Args:
        dashboard_info: Dashboard info dictionary
        api_key: Anthropic API key (optional, can use ANTHROPIC_API_KEY env var or config.LLM_API_KEY)
        model: Model to use (default: from config.LLM_MODEL)
        base_url: Custom API base URL (default: from config.LLM_BASE_URL)
    
    Returns:
        List of dicts with: tables_involved, column_names, alias_column_name, source_or_derived, derived_column_logic
    """
    from sql_parser import normalize_table_name
    
    extractor = DashboardTableColumnExtractor(api_key=api_key, model=model, base_url=base_url)
    charts = dashboard_info.get('charts', [])
    results = []
    
    print(f"Extracting source tables and columns from {len(charts)} charts using LLM...")
    
    # Extract from each chart
    for i, chart in enumerate(charts, 1):
        chart_id = chart.get('chart_id')
        print(f"  [{i}/{len(charts)}] Processing chart {chart_id}...")
        
        try:
            # Extract source tables and columns using new signature
            chart_result = extractor.extract_source_from_chart(chart)
            source_tables = chart_result['source_tables']
            source_columns = chart_result['source_columns']
            derived_columns_mapping = chart_result['derived_columns_mapping']
            
            # Process source columns: one row per (table, column) combination
            for table in source_tables:
                normalized_table = normalize_table_name(table)
                
                for column in source_columns:
                    # Source column row: alias_column_name = column_names
                    results.append({
                        'tables_involved': normalized_table,
                        'column_names': column,
                        'alias_column_name': column,
                        'source_or_derived': 'source',
                        'derived_column_logic': 'NA'
                    })
            
            # Process derived columns: one row per (table, alias) combination
            for alias_name, mapping_info in derived_columns_mapping.items():
                if isinstance(mapping_info, dict):
                    source_column = mapping_info.get('source_column', '')
                    source_table = mapping_info.get('source_table', '')
                    logic = mapping_info.get('logic', '')
                    
                    # Normalize table name
                    normalized_source_table = normalize_table_name(source_table)
                    
                    # Only add if we have valid source table and column
                    if normalized_source_table and source_column:
                        results.append({
                            'tables_involved': normalized_source_table,
                            'column_names': source_column,
                            'alias_column_name': alias_name,
                            'source_or_derived': 'derived',
                            'derived_column_logic': logic if logic else 'NA'
                        })
                    
        except Exception as e:
            print(f"    Error processing chart {chart_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    # Remove duplicates: same (tables_involved, column_names, alias_column_name) combination
    seen = set()
    unique_results = []
    for result in results:
        key = (result['tables_involved'], result['column_names'], result['alias_column_name'])
        if key not in seen:
            seen.add(key)
            unique_results.append(result)
    
    # Sort by tables_involved, then column_names, then alias_column_name
    unique_results.sort(key=lambda x: (x['tables_involved'], x['column_names'], x['alias_column_name']))
    
    return unique_results


def generate_final_tables_columns_output(
    dashboard_id: int,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    fetch_schemas: bool = False,
    output_file: Optional[str] = None
) -> pd.DataFrame:
    """
    Generate final tables_columns.csv output file using DSPy extraction
    
    This is the main function to generate the final output file with:
    - Source tables and columns
    - Derived columns with their logic
    - Optional: Schema information from Starburst
    
    Args:
        dashboard_id: Dashboard ID
        api_key: Anthropic API key (optional, can use ANTHROPIC_API_KEY env var)
        model: Model to use (default: claude-sonnet-4-20250514)
        fetch_schemas: Whether to fetch schema information from Starburst (default: False)
        output_file: Output CSV file path (default: extracted_meta/{dashboard_id}_tables_columns.csv)
        
    Returns:
        DataFrame with final output
    """
    import os
    
    # Create dashboard directory
    dashboard_dir = f"extracted_meta/{dashboard_id}"
    os.makedirs(dashboard_dir, exist_ok=True)
    
    # Load dashboard info
    json_file = f"{dashboard_dir}/{dashboard_id}_json.json"
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Dashboard JSON file not found: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        dashboard_info = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"Generating final tables_columns output for dashboard {dashboard_id}")
    print(f"{'='*60}\n")
    
    # Extract using DSPy with examples
    print("Step 1: Extracting tables and columns using DSPy (with examples)...")
    dspy_results = extract_source_tables_columns_llm(
        dashboard_info,
        api_key=api_key,
        model=model,
        base_url=base_url
    )
    
    print(f"✅ Extracted {len(dspy_results)} table-column mappings\n")
    
    # Convert to DataFrame
    df = pd.DataFrame(dspy_results)
    
    # Determine output file path
    dashboard_dir = f"extracted_meta/{dashboard_id}"
    os.makedirs(dashboard_dir, exist_ok=True)
    if output_file is None:
        output_file = f"{dashboard_dir}/{dashboard_id}_tables_columns.csv"
    
    # Optionally fetch schemas from Starburst
    if fetch_schemas:
        print("Step 2: Fetching schema information from Starburst...")
        try:
            from starburst_schema_fetcher import process_dspy_extraction_results
            schema_df = process_dspy_extraction_results(dspy_results)
            
            if not schema_df.empty:
                # Merge schema information
                # Create a key for merging: tables_involved + column_names
                df['merge_key'] = df['tables_involved'] + '|' + df['column_names']
                schema_df['merge_key'] = schema_df['table_name'] + '|' + schema_df['column_name']
                
                # Merge on source columns only (not derived)
                source_df = df[df['source_or_derived'] == 'source'].copy()
                source_df = source_df.merge(
                    schema_df[['merge_key', 'column_datatype', 'extra', 'comment']],
                    on='merge_key',
                    how='left'
                )
                
                # Add schema columns to derived rows (set to None)
                derived_df = df[df['source_or_derived'] == 'derived'].copy()
                derived_df['column_datatype'] = None
                derived_df['extra'] = None
                derived_df['comment'] = None
                
                # Combine
                df = pd.concat([source_df, derived_df], ignore_index=True)
                df = df.drop('merge_key', axis=1)
                
                # Reorder columns
                cols = ['tables_involved', 'column_names', 'alias_column_name', 
                       'source_or_derived', 'derived_column_logic', 
                       'column_datatype', 'extra', 'comment']
                df = df[[c for c in cols if c in df.columns]]
                
                print(f"✅ Merged schema information for {len(source_df)} source columns\n")
            else:
                print("⚠️  No schema information retrieved\n")
        except Exception as e:
            print(f"⚠️  Error fetching schemas: {str(e)}\n")
            print("Continuing without schema information...\n")
    
    # Save to CSV
    if output_file is None:
        output_file = f"extracted_meta/{dashboard_id}_tables_columns.csv"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Create empty DataFrame with correct columns if no results
    if df.empty:
        df = pd.DataFrame(columns=['tables_involved', 'column_names', 'alias_column_name', 
                                  'source_or_derived', 'derived_column_logic'])
        print("⚠️  Warning: No results extracted. Creating empty output file.")
    
    df.to_csv(output_file, index=False)
    
    print(f"{'='*60}")
    if len(df) > 0:
        print(f"✅ Final output generated successfully!")
        print(f"   File: {output_file}")
        print(f"   Rows: {len(df)}")


def extract_table_metadata_llm(
    dashboard_info: Dict,
    tables_columns_df: pd.DataFrame,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> List[Dict]:
    """
    Extract table metadata using LLM based on dashboard context, chart labels, and table usage.
    
    Args:
        dashboard_info: Dashboard info dict with title, charts, etc.
        tables_columns_df: DataFrame with tables_columns data (from Phase 2/3)
        api_key: Anthropic API key
        model: Model name
        base_url: Base URL for LLM API
        
    Returns:
        List of dicts with table metadata
    """
    import os
    
    # Get API key and model
    api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or LLM_API_KEY
    if not api_key:
        raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
    
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    # Get DSPy extractor
    extractor = _get_dspy_table_metadata_extractor(api_key, model, base_url)
    
    # Extract unique tables
    unique_tables = tables_columns_df['tables_involved'].unique().tolist()
    
    # Prepare dashboard context
    dashboard_title = dashboard_info.get('dashboard_title', 'Unknown Dashboard')
    charts = dashboard_info.get('charts', [])
    
    # Collect chart names and labels
    chart_context = []
    for chart in charts:
        chart_name = chart.get('chart_name', '')
        metrics = chart.get('metrics', [])
        columns = chart.get('columns', [])
        
        labels = []
        for metric in metrics:
            if isinstance(metric, dict):
                label = metric.get('label') or metric.get('column', {}).get('verbose_name', '')
                if label:
                    labels.append(label)
        
        chart_context.append({
            'chart_name': chart_name,
            'labels': labels,
            'columns': columns if isinstance(columns, list) else []
        })
    
    chart_names_and_labels = json.dumps(chart_context, indent=2)
    
    # Collect SQL queries context (sample queries using each table)
    table_sql_map = {}
    for chart in charts:
        sql_query = chart.get('sql_query', '')
        if not sql_query:
            continue
        
        # Find which tables are used in this query
        for table in unique_tables:
            # Simple check if table name appears in SQL
            table_short = table.split('.')[-1]  # Just table name
            if table_short.lower() in sql_query.lower() or table.lower() in sql_query.lower():
                if table not in table_sql_map:
                    table_sql_map[table] = []
                table_sql_map[table].append(sql_query[:500])  # First 500 chars
    
    # For each unique table, extract metadata
    results = []
    
    for i, table_name in enumerate(unique_tables, 1):
        print(f"  [{i}/{len(unique_tables)}] Extracting metadata for {table_name}...")
        
        try:
            # Get columns for this table
            table_cols_df = tables_columns_df[tables_columns_df['tables_involved'] == table_name]
            
            # Prepare column context
            columns_info = []
            for _, row in table_cols_df.iterrows():
                col_info = {
                    'column_name': row['column_names'],
                    'alias': row['alias_column_name'],
                    'source_or_derived': row['source_or_derived'],
                    'datatype': row.get('column_datatype', ''),
                    'derived_logic': row.get('derived_column_logic', '')
                }
                columns_info.append(col_info)
            
            table_columns_json = json.dumps(columns_info, indent=2)
            
            # Get SQL context for this table
            sql_queries_context = '\n\n---\n\n'.join(table_sql_map.get(table_name, ['No sample queries available']))
            if len(sql_queries_context) > 2000:
                sql_queries_context = sql_queries_context[:2000] + '...'
            
            # Call LLM
            result = extractor(
                dashboard_title=dashboard_title,
                chart_names_and_labels=chart_names_and_labels,
                table_name=table_name,
                table_columns=table_columns_json,
                sql_queries_context=sql_queries_context
            )
            
            # Parse result
            metadata = {
                'table_name': table_name,
                'table_description': result.table_description,
                'refresh_frequency': result.refresh_frequency,
                'vertical': result.vertical,
                'partition_column': result.partition_column,
                'remarks': result.remarks,
                'relationship_context': result.relationship_context
            }
            
            results.append(metadata)
            
        except Exception as e:
            print(f"    ⚠️  Error processing {table_name}: {str(e)}")
            # Add empty entry
            results.append({
                'table_name': table_name,
                'table_description': f'Error extracting metadata: {str(e)}',
                'refresh_frequency': '',
                'vertical': '',
                'partition_column': '',
                'remarks': '',
                'relationship_context': ''
            })
    
    return results


def _get_dspy_table_metadata_extractor(api_key: str, model: str, base_url: Optional[str] = None):
    """Get DSPy table metadata extractor, configure if needed (thread-safe)"""
    global _dspy_lm
    with _dspy_lock:
        # Use same LM configuration as other extractors
        if _dspy_lm is None:
            if base_url:
                model_name = f"anthropic/{model}" if not model.startswith("anthropic/") else model
            else:
                model_name = model
            
            lm_kwargs = {
                "model": model_name,
                "api_key": api_key,
                "api_provider": "anthropic"
            }
            if base_url:
                clean_base_url = base_url.rstrip('/v1').rstrip('/')
                lm_kwargs["api_base"] = clean_base_url
            
            _dspy_lm = dspy.LM(**lm_kwargs)
            dspy.configure(lm=_dspy_lm)
        
        # Create extractor
        extractor = dspy.ChainOfThought(TableMetadataExtractor)
        return extractor


def extract_column_metadata_llm(
    dashboard_info: Dict,
    tables_columns_df: pd.DataFrame,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> List[Dict]:
    """
    Extract column metadata using LLM based on usage context, chart labels, aliases, and derived column logic.
    
    Args:
        dashboard_info: Dashboard info dict with charts, metrics, etc.
        tables_columns_df: DataFrame with tables_columns_enriched data
        api_key: Anthropic API key
        model: Model name
        base_url: Base URL for LLM API
        
    Returns:
        List of dicts with column metadata: table_name, column_name, variable_type, column_description, required_flag
    """
    import os
    
    # Get API key and model
    api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or LLM_API_KEY
    if not api_key:
        raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
    
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    # Get DSPy extractor
    extractor = _get_dspy_column_metadata_extractor(api_key, model, base_url)
    
    # Filter to source columns only (we'll handle derived columns separately if needed)
    source_df = tables_columns_df[tables_columns_df['source_or_derived'] == 'source'].copy()
    
    # Get unique (table_name, column_name) combinations
    unique_columns = source_df[['tables_involved', 'column_names', 'column_datatype']].drop_duplicates()
    
    # Prepare dashboard context
    charts = dashboard_info.get('charts', [])
    
    # Build column usage context
    column_usage_map = {}
    for _, row in tables_columns_df.iterrows():
        table = row['tables_involved']
        col = row['column_names']
        key = (table, col)
        
        if key not in column_usage_map:
            column_usage_map[key] = {
                'aliases': [],
                'derived_usage': [],
                'sql_context': []
            }
        
        # Collect aliases
        alias = row.get('alias_column_name', '')
        if alias and alias != col:
            column_usage_map[key]['aliases'].append(alias)
        
        # Collect derived column usage
        if row['source_or_derived'] == 'derived':
            derived_logic = row.get('derived_column_logic', '')
            if derived_logic and col in derived_logic:
                column_usage_map[key]['derived_usage'].append({
                    'alias': alias,
                    'logic': derived_logic
                })
    
    # Collect chart labels and SQL context
    for chart in charts:
        chart_name = chart.get('chart_name', '')
        metrics = chart.get('metrics', [])
        sql_query = chart.get('sql_query', '')
        
        # Extract labels from metrics
        for metric in metrics:
            if isinstance(metric, dict):
                label = metric.get('label', '')
                sql_expr = metric.get('sqlExpression', '')
                
                # Try to match column names in SQL expression
                for _, col_row in unique_columns.iterrows():
                    table = col_row['tables_involved']
                    col = col_row['column_names']
                    key = (table, col)
                    
                    if col in sql_expr or col.lower() in sql_expr.lower():
                        if key not in column_usage_map:
                            column_usage_map[key] = {'aliases': [], 'derived_usage': [], 'sql_context': []}
                        if label:
                            column_usage_map[key]['aliases'].append(label)
                        if sql_query:
                            column_usage_map[key]['sql_context'].append(sql_query[:300])  # First 300 chars
    
    # For each unique column, extract metadata
    results = []
    
    for i, (_, row) in enumerate(unique_columns.iterrows(), 1):
        table_name = row['tables_involved']
        column_name = row['column_names']
        variable_type = row.get('column_datatype', '')
        
        print(f"  [{i}/{len(unique_columns)}] Extracting metadata for {table_name}.{column_name}...")
        
        try:
            # Get usage context for this column
            key = (table_name, column_name)
            usage = column_usage_map.get(key, {'aliases': [], 'derived_usage': [], 'sql_context': []})
            
            # Prepare context strings
            chart_labels_and_aliases = json.dumps({
                'aliases': list(set(usage['aliases'])),
                'chart_names': [c.get('chart_name', '') for c in charts if c.get('sql_query', '')]
            }, indent=2)
            
            derived_column_usage = json.dumps(usage['derived_usage'], indent=2)
            
            sql_usage_context = '\n\n---\n\n'.join(usage['sql_context'][:3])  # Max 3 SQL snippets
            if len(sql_usage_context) > 1500:
                sql_usage_context = sql_usage_context[:1500] + '...'
            
            # Call LLM
            result = extractor(
                column_name=column_name,
                table_name=table_name,
                column_datatype=variable_type or 'unknown',
                chart_labels_and_aliases=chart_labels_and_aliases,
                derived_column_usage=derived_column_usage,
                sql_usage_context=sql_usage_context or 'No SQL context available'
            )
            
            # Determine required_flag
            # "yes" if column is used in derived columns, filters, or is a key column
            required_flag = "no"
            if usage['derived_usage']:
                required_flag = "yes"
            elif column_name.lower() in ['id', 'txn_id', 'user_id', 'customer_id', 'created_on', 'date', 'dt']:
                required_flag = "yes"
            elif any(keyword in column_name.lower() for keyword in ['_id', '_key', 'timestamp', 'date']):
                required_flag = "yes"
            
            # Parse result
            metadata = {
                'table_name': table_name,
                'column_name': column_name,
                'variable_type': variable_type or '',
                'column_description': result.column_description,
                'required_flag': required_flag
            }
            
            results.append(metadata)
            
        except Exception as e:
            print(f"    ⚠️  Error processing {table_name}.{column_name}: {str(e)}")
            # Add entry with error description
            results.append({
                'table_name': table_name,
                'column_name': column_name,
                'variable_type': variable_type or '',
                'column_description': f'Error extracting description: {str(e)}',
                'required_flag': 'no'
            })
    
    return results


def _get_dspy_column_metadata_extractor(api_key: str, model: str, base_url: Optional[str] = None):
    """Get DSPy column metadata extractor, configure if needed (thread-safe)"""
    global _dspy_lm
    with _dspy_lock:
        # Use same LM configuration as other extractors
        if _dspy_lm is None:
            if base_url:
                model_name = f"anthropic/{model}" if not model.startswith("anthropic/") else model
            else:
                model_name = model
            
            lm_kwargs = {
                "model": model_name,
                "api_key": api_key,
                "api_provider": "anthropic"
            }
            if base_url:
                clean_base_url = base_url.rstrip('/v1').rstrip('/')
                lm_kwargs["api_base"] = clean_base_url
            
            _dspy_lm = dspy.LM(**lm_kwargs)
            dspy.configure(lm=_dspy_lm)
        
        # Create extractor
        extractor = dspy.ChainOfThought(ColumnMetadataExtractor)
        return extractor


def extract_joining_conditions_llm(
    dashboard_info: Dict,
    tables_columns_df: pd.DataFrame,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> List[Dict]:
    """
    Extract joining conditions between tables used in dashboard charts.
    
    Only processes charts that use 2+ different source tables.
    
    Args:
        dashboard_info: Dashboard info dict with charts, SQL queries
        tables_columns_df: DataFrame with tables_columns data
        api_key: Anthropic API key
        model: Model name
        base_url: Base URL for LLM API
        
    Returns:
        List of dicts with joining conditions: table1, table2, joining_condition, remarks
    """
    import os
    import re
    
    # Get API key and model
    api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or LLM_API_KEY
    if not api_key:
        raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
    
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    # Get DSPy extractor
    extractor = _get_dspy_joining_condition_extractor(api_key, model, base_url)
    
    # Get unique tables per chart
    charts = dashboard_info.get('charts', [])
    dashboard_title = dashboard_info.get('dashboard_title', 'Unknown Dashboard')
    
    # Group tables by chart
    chart_tables_map = {}
    for _, row in tables_columns_df.iterrows():
        # We need to map back to chart - this is tricky without chart_id in the CSV
        # Instead, we'll analyze each chart's SQL query directly
        pass
    
    # Analyze each chart's SQL query
    results = []
    processed_joins = set()  # Track (table1, table2) pairs to avoid duplicates
    
    for chart in charts:
        chart_id = chart.get('chart_id')
        chart_name = chart.get('chart_name', 'Unknown')
        sql_query = chart.get('sql_query', '')
        
        if not sql_query:
            continue
        
        # Extract source tables from this chart's SQL
        # Use the tables_columns_df to find tables used in this chart
        # Since we don't have chart_id in tables_columns_df, we'll extract from SQL directly
        
        # Extract tables from SQL
        sql_clean = sql_query.upper()
        
        # Find all table references (FROM, JOIN clauses)
        table_pattern = re.compile(
            r'(?:FROM|JOIN|INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+JOIN)\s+'
            r'(?:(\w+)\.)?(?:(\w+)\.)?(\w+)',
            re.IGNORECASE
        )
        
        tables_found = []
        for match in re.finditer(table_pattern, sql_query):
            parts = [p for p in match.groups() if p]
            if len(parts) >= 1:
                # Reconstruct table name
                table_name = '.'.join(parts)
                # Normalize
                if not table_name.startswith('hive.'):
                    if len(parts) == 2:
                        table_name = f"hive.{parts[0]}.{parts[1]}"
                    elif len(parts) == 1:
                        # Single part - might be in tables_columns_df
                        # Try to find matching table from tables_columns_df
                        matching = tables_columns_df[tables_columns_df['tables_involved'].str.contains(parts[0], case=False, na=False)]
                        if not matching.empty:
                            table_name = matching.iloc[0]['tables_involved']
                
                if table_name and table_name not in tables_found:
                    tables_found.append(table_name)
        
        # Also check tables_columns_df for this chart's tables
        # Since we can't directly map, we'll use a heuristic: if a table appears in SQL, use it
        chart_tables = set()
        for table in tables_columns_df['tables_involved'].unique():
            table_short = table.split('.')[-1].lower()
            if table_short in sql_query.lower() or table.lower() in sql_query.lower():
                chart_tables.add(table)
        
        # Use chart_tables if we found any, otherwise use tables_found
        if chart_tables:
            chart_tables = sorted(list(chart_tables))
        elif tables_found:
            chart_tables = sorted(list(set(tables_found)))
        else:
            continue
        
        # Only process if 2+ tables
        if len(chart_tables) < 2:
            continue
        
        # Generate all pairs of tables
        for i in range(len(chart_tables)):
            for j in range(i + 1, len(chart_tables)):
                table1 = chart_tables[i]
                table2 = chart_tables[j]
                
                # Skip if already processed
                join_key = tuple(sorted([table1, table2]))
                if join_key in processed_joins:
                    continue
                processed_joins.add(join_key)
                
                print(f"  Extracting join condition: {table1} <-> {table2} (Chart: {chart_name})...")
                
                try:
                    # Call LLM to extract joining condition
                    result = extractor(
                        table1=table1,
                        table2=table2,
                        sql_query=sql_query,
                        chart_name=chart_name,
                        dashboard_title=dashboard_title
                    )
                    
                    # Parse result
                    join_metadata = {
                        'table1': table1,
                        'table2': table2,
                        'joining_condition': result.joining_condition,
                        'remarks': result.remarks
                    }
                    
                    results.append(join_metadata)
                    
                except Exception as e:
                    print(f"    ⚠️  Error processing join {table1} <-> {table2}: {str(e)}")
                    # Add entry with error
                    results.append({
                        'table1': table1,
                        'table2': table2,
                        'joining_condition': f'Error extracting: {str(e)}',
                        'remarks': ''
                    })
    
    return results


def _get_dspy_joining_condition_extractor(api_key: str, model: str, base_url: Optional[str] = None):
    """Get DSPy joining condition extractor, configure if needed (thread-safe)"""
    global _dspy_lm
    with _dspy_lock:
        # Use same LM configuration as other extractors
        if _dspy_lm is None:
            if base_url:
                model_name = f"anthropic/{model}" if not model.startswith("anthropic/") else model
            else:
                model_name = model
            
            lm_kwargs = {
                "model": model_name,
                "api_key": api_key,
                "api_provider": "anthropic"
            }
            if base_url:
                clean_base_url = base_url.rstrip('/v1').rstrip('/')
                lm_kwargs["api_base"] = clean_base_url
            
            _dspy_lm = dspy.LM(**lm_kwargs)
            dspy.configure(lm=_dspy_lm)
        
        # Create extractor
        extractor = dspy.ChainOfThought(JoiningConditionExtractor)
        return extractor


def generate_filter_conditions_llm(
    dashboard_info: Dict,
    tables_columns_df: pd.DataFrame,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> str:
    """
    Generate filter_conditions.txt file with use-case descriptions and SQL filter logic for each chart.
    
    Args:
        dashboard_info: Dashboard info dict with charts, SQL queries, filters
        tables_columns_df: DataFrame with tables_columns data
        api_key: Anthropic API key
        model: Model name
        base_url: Base URL for LLM API
        
    Returns:
        String content for filter_conditions.txt file
    """
    import os
    import re
    
    # Get API key and model
    api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or LLM_API_KEY
    if not api_key:
        raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
    
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    # Get DSPy extractor
    extractor = _get_dspy_filter_conditions_extractor(api_key, model, base_url)
    
    dashboard_title = dashboard_info.get('dashboard_title', 'Unknown Dashboard')
    charts = dashboard_info.get('charts', [])
    
    # Prepare all charts context for consolidation detection
    all_charts_context = []
    for chart in charts:
        all_charts_context.append({
            'chart_id': chart.get('chart_id'),
            'chart_name': chart.get('chart_name', 'Unknown'),
            'sql_query': chart.get('sql_query', ''),
            'metrics': chart.get('metrics', []),
            'filters': chart.get('filters', [])
        })
    all_charts_json = json.dumps(all_charts_context, indent=2)
    
    # Build content - process all charts together for consolidation
    content_lines = []
    common_patterns_section = []
    processed_charts = set()
    
    # Group charts by similarity for consolidation
    # Charts with same base logic but different parameter values should be grouped
    chart_groups = []
    remaining_charts = []
    
    for chart in charts:
        chart_name = chart.get('chart_name', 'Unknown')
        sql_query = chart.get('sql_query', '')
        
        if not sql_query:
            continue
        
        # Simple heuristic: if chart name contains parameter values like "PSP = X", group them
        # Look for patterns like "(Payee Psp = yes)", "(Payee Psp = HDFC)", etc.
        base_name_match = re.search(r'^(.+?)\s*\([^)]*=\s*[^)]+\)', chart_name)
        if base_name_match:
            base_name = base_name_match.group(1).strip()
            # Find or create group
            group_found = False
            for group in chart_groups:
                if group['base_name'] == base_name:
                    group['charts'].append(chart)
                    group_found = True
                    break
            if not group_found:
                chart_groups.append({
                    'base_name': base_name,
                    'charts': [chart],
                    'is_consolidated': len([c for c in charts if base_name_match and base_name_match.group(1).strip() == base_name]) >= 3
                })
        else:
            remaining_charts.append(chart)
    
    # Process consolidated groups first
    for group in chart_groups:
        if group['is_consolidated'] and len(group['charts']) >= 3:
            # Process as consolidated group
            charts_to_process = group['charts']
            print(f"  Processing consolidated group: {group['base_name']} ({len(charts_to_process)} charts)...")
            
            # Use the first chart as representative, but include all in context
            representative_chart = charts_to_process[0]
            chart_id = representative_chart.get('chart_id')
            chart_name = f"{group['base_name']} by Payee PSP"  # Generic name
            sql_query = representative_chart.get('sql_query', '')
            metrics = representative_chart.get('metrics', [])
            filters = representative_chart.get('filters', [])
            
            try:
                # Get tables involved
                chart_tables = set()
                for table in tables_columns_df['tables_involved'].unique():
                    table_short = table.split('.')[-1].lower()
                    if table_short in sql_query.lower() or table.lower() in sql_query.lower():
                        chart_tables.add(table)
                
                tables_involved_str = ', '.join(sorted(chart_tables)) if chart_tables else 'Unknown'
                
                # Prepare inputs with all charts in group
                chart_metrics_json = json.dumps(metrics, indent=2)
                chart_filters_json = json.dumps(filters, indent=2)
                
                # Create consolidated context showing all variants
                consolidated_context = {
                    'charts': charts_to_process,
                    'base_name': group['base_name'],
                    'variants': [c.get('chart_name', '') for c in charts_to_process]
                }
                consolidated_context_json = json.dumps(consolidated_context, indent=2)
                
                # Call LLM with consolidated context
                result = extractor(
                    chart_name=chart_name,
                    chart_metrics=chart_metrics_json,
                    sql_query=sql_query,
                    chart_filters=chart_filters_json,
                    tables_involved=tables_involved_str,
                    dashboard_title=dashboard_title,
                    all_charts_context=consolidated_context_json
                )
                
                # Format output
                content_lines.append(f"## {chart_name}")
                content_lines.append("")
                content_lines.append(result.use_case_description)
                content_lines.append("")
                
                # Clean up SQL
                sql_content = result.filter_conditions_sql
                if sql_content.strip().startswith('```sql'):
                    sql_content = sql_content.strip()[6:].lstrip()
                if sql_content.strip().endswith('```'):
                    sql_content = sql_content.strip()[:-3].rstrip()
                
                content_lines.append("```sql")
                content_lines.append(sql_content)
                content_lines.append("```")
                content_lines.append("")
                content_lines.append("---")
                content_lines.append("")
                
                # Collect common patterns
                if result.common_patterns and result.common_patterns.strip():
                    if result.common_patterns not in common_patterns_section:
                        common_patterns_section.append(result.common_patterns)
                
                # Mark all charts in group as processed
                for c in charts_to_process:
                    processed_charts.add(c.get('chart_id'))
                    
            except Exception as e:
                print(f"    ⚠️  Error processing consolidated group: {str(e)}")
                # Fall through to process individually
                for c in charts_to_process:
                    remaining_charts.append(c)
        else:
            # Not consolidated, add to remaining
            remaining_charts.extend(group['charts'])
    
    # Process remaining charts individually
    for i, chart in enumerate(remaining_charts, 1):
        chart_id = chart.get('chart_id')
        chart_name = chart.get('chart_name', 'Unknown')
        sql_query = chart.get('sql_query', '')
        metrics = chart.get('metrics', [])
        filters = chart.get('filters', [])
        
        if not sql_query or chart_id in processed_charts:
            continue
        
        print(f"  [{i}/{len(remaining_charts)}] Processing chart {chart_id}: {chart_name}...")
        
        try:
            # Get tables involved for this chart
            chart_tables = set()
            for table in tables_columns_df['tables_involved'].unique():
                table_short = table.split('.')[-1].lower()
                if table_short in sql_query.lower() or table.lower() in sql_query.lower():
                    chart_tables.add(table)
            
            tables_involved_str = ', '.join(sorted(chart_tables)) if chart_tables else 'Unknown'
            
            # Prepare inputs
            chart_metrics_json = json.dumps(metrics, indent=2)
            chart_filters_json = json.dumps(filters, indent=2)
            
            # Call LLM with all charts context for consolidation
            result = extractor(
                chart_name=chart_name,
                chart_metrics=chart_metrics_json,
                sql_query=sql_query,
                chart_filters=chart_filters_json,
                tables_involved=tables_involved_str,
                dashboard_title=dashboard_title,
                all_charts_context=all_charts_json
            )
            
            # Format output
            content_lines.append(f"## {chart_name}")
            content_lines.append("")
            content_lines.append(result.use_case_description)
            content_lines.append("")
            
            # Clean up SQL - remove duplicate ```sql markers if present
            sql_content = result.filter_conditions_sql
            # Remove leading ```sql if present
            if sql_content.strip().startswith('```sql'):
                sql_content = sql_content.strip()[6:].lstrip()
            # Remove trailing ``` if present
            if sql_content.strip().endswith('```'):
                sql_content = sql_content.strip()[:-3].rstrip()
            
            content_lines.append("```sql")
            content_lines.append(sql_content)
            content_lines.append("```")
            content_lines.append("")
            content_lines.append("---")
            content_lines.append("")
            
            # Collect common patterns if provided
            if result.common_patterns and result.common_patterns.strip():
                # Only add if not already in the list
                if result.common_patterns not in common_patterns_section:
                    common_patterns_section.append(result.common_patterns)
            
            # Mark this chart as processed
            processed_charts.add(chart_id)
            
        except Exception as e:
            print(f"    ⚠️  Error processing chart {chart_id}: {str(e)}")
            # Add error entry
            content_lines.append(f"## {chart_name}")
            content_lines.append("")
            content_lines.append(f"Error generating filter conditions: {str(e)}")
            content_lines.append("")
            content_lines.append("---")
            content_lines.append("")
            processed_charts.add(chart_id)
    
    # Add Common Calculation Patterns section at the end if any patterns were identified
    if common_patterns_section:
        content_lines.append("")
        content_lines.append("## Common Calculation Patterns")
        content_lines.append("")
        # Deduplicate and merge patterns
        unique_patterns = []
        seen_patterns = set()
        for pattern_text in common_patterns_section:
            # Extract pattern name if possible
            pattern_name_match = re.search(r'###\s+(\w+)', pattern_text)
            if pattern_name_match:
                pattern_name = pattern_name_match.group(1)
                if pattern_name not in seen_patterns:
                    seen_patterns.add(pattern_name)
                    unique_patterns.append(pattern_text)
            else:
                # If no pattern name found, add it anyway
                if pattern_text not in seen_patterns:
                    seen_patterns.add(pattern_text)
                    unique_patterns.append(pattern_text)
        
        for pattern in unique_patterns:
            content_lines.append(pattern)
            content_lines.append("")
    
    return '\n'.join(content_lines)


def _get_dspy_filter_conditions_extractor(api_key: str, model: str, base_url: Optional[str] = None):
    """Get DSPy filter conditions extractor, configure if needed (thread-safe)"""
    global _dspy_lm
    with _dspy_lock:
        # Use same LM configuration as other extractors
        if _dspy_lm is None:
            if base_url:
                model_name = f"anthropic/{model}" if not model.startswith("anthropic/") else model
            else:
                model_name = model
            
            lm_kwargs = {
                "model": model_name,
                "api_key": api_key,
                "api_provider": "anthropic"
            }
            if base_url:
                clean_base_url = base_url.rstrip('/v1').rstrip('/')
                lm_kwargs["api_base"] = clean_base_url
            
            _dspy_lm = dspy.LM(**lm_kwargs)
            dspy.configure(lm=_dspy_lm)
        
        # Create extractor
        extractor = dspy.ChainOfThought(FilterConditionsExtractor)
        return extractor


def extract_term_definitions_llm(
    dashboard_info: Dict,
    tables_columns_df: pd.DataFrame,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> List[Dict]:
    """
    Extract term definitions from dashboard charts including metrics, calculated fields, synonyms, and categories.
    
    Args:
        dashboard_info: Dashboard info dict with charts, metrics, SQL queries
        tables_columns_df: DataFrame with tables_columns data
        api_key: Anthropic API key
        model: Model name
        base_url: Base URL for LLM API
        
    Returns:
        List of dicts with term definitions: term, type, definition, business_alias
    """
    import os
    
    # Get API key and model
    api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or LLM_API_KEY
    if not api_key:
        raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
    
    model = model or LLM_MODEL
    base_url = base_url or LLM_BASE_URL
    
    # Get DSPy extractor
    extractor = _get_dspy_term_definition_extractor(api_key, model, base_url)
    
    dashboard_title = dashboard_info.get('dashboard_title', 'Unknown Dashboard')
    charts = dashboard_info.get('charts', [])
    
    # Collect all chart names, labels, and SQL queries
    chart_names_and_labels = []
    sql_queries = []
    metrics_context = []
    
    for chart in charts:
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
        
        chart_names_and_labels.append({
            'chart_name': chart_name,
            'labels': labels
        })
        
        if sql_query:
            sql_queries.append({
                'chart_name': chart_name,
                'sql_query': sql_query
            })
        
        if metric_details:
            metrics_context.append({
                'chart_name': chart_name,
                'metrics': metric_details
            })
    
    chart_names_json = json.dumps(chart_names_and_labels, indent=2)
    sql_queries_json = json.dumps(sql_queries, indent=2)
    metrics_context_json = json.dumps(metrics_context, indent=2)
    
    print(f"  Extracting term definitions from {len(charts)} charts...")
    
    try:
        # Call LLM to extract all term definitions
        result = extractor(
            dashboard_title=dashboard_title,
            chart_names_and_labels=chart_names_json,
            sql_queries=sql_queries_json,
            metrics_context=metrics_context_json
        )
        
        # Parse JSON result
        try:
            term_definitions = json.loads(result.term_definitions)
            if not isinstance(term_definitions, list):
                term_definitions = []
        except:
            print("    ⚠️  Error parsing term definitions JSON, creating empty list")
            term_definitions = []
        
        return term_definitions
        
    except Exception as e:
        print(f"    ⚠️  Error extracting term definitions: {str(e)}")
        return []


def _get_dspy_term_definition_extractor(api_key: str, model: str, base_url: Optional[str] = None):
    """Get DSPy term definition extractor, configure if needed (thread-safe)"""
    global _dspy_lm
    with _dspy_lock:
        # Use same LM configuration as other extractors
        if _dspy_lm is None:
            if base_url:
                model_name = f"anthropic/{model}" if not model.startswith("anthropic/") else model
            else:
                model_name = model
            
            lm_kwargs = {
                "model": model_name,
                "api_key": api_key,
                "api_provider": "anthropic"
            }
            if base_url:
                clean_base_url = base_url.rstrip('/v1').rstrip('/')
                lm_kwargs["api_base"] = clean_base_url
            
            _dspy_lm = dspy.LM(**lm_kwargs)
            dspy.configure(lm=_dspy_lm)
        
        # Create extractor
        extractor = dspy.ChainOfThought(TermDefinitionExtractor)
        return extractor

