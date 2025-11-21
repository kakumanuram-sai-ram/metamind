"""
Metadata Merger

This module merges metadata from multiple dashboards into unified metadata files.
It uses LLM-based merging with conflict detection and resolution.
"""
import os
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple

try:
    import dspy
    from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
except ImportError:
    # If running as module
    import sys
    import os
    _scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    import dspy
    from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL

from progress_tracker import get_progress_tracker


# ============================================================================
# DSPy Signatures for Merging
# ============================================================================

class TableMetadataMerger(dspy.Signature):
    """
    Merge table metadata from multiple dashboards into a unified entry.
    
    SYSTEM PROMPT: Table Metadata Merger
    
    ## Objective
    Consolidate table metadata entries from multiple dashboards into a single unified entry.
    Detect conflicts (different descriptions, refresh frequencies, verticals, partition columns)
    and resolve them intelligently.
    
    ## Input
    You will receive multiple table metadata entries for the same table from different dashboards.
    Each entry contains: table_name, table_description (with data_description and business_description),
    refresh_frequency, vertical, partition_column, remarks, relationship_context.
    
    ## Output Requirements
    
    ### 1. Unified Table Description
    - **data_description**: Merge all data descriptions, highlighting commonalities and unique aspects
    - **business_description**: Combine business use cases from all dashboards, showing how the table
      is used across different contexts
    
    ### 2. Refresh Frequency
    - If all dashboards agree: use that value
    - If different: use the most frequent value OR flag as "varies" if significant differences exist
    
    ### 3. Vertical
    - If all dashboards agree: use that value
    - If different: list all verticals (comma-separated) OR identify the primary vertical
    
    ### 4. Partition Column
    - If all dashboards agree: use that value
    - If different: use the most common value OR list all if they're all valid
    
    ### 5. Remarks
    - Merge all remarks, noting which dashboard each came from
    - Highlight any important differences or special considerations
    
    ### 6. Relationship Context
    - Combine relationship contexts from all dashboards
    - Show how the table is used in different join patterns across dashboards
    
    ### 7. Conflict Detection
    - Identify conflicts in: descriptions, refresh_frequency, vertical, partition_column
    - For each conflict, note: the conflicting values, which dashboards they came from, and resolution approach
    
    ## Conflict Resolution Rules
    
    1. **Most Common Wins**: If 3+ dashboards agree on a value, use that
    2. **Flag for Review**: If significant conflicts exist (e.g., different verticals), flag it
    3. **Merge Intelligently**: For descriptions, merge content rather than picking one
    
    ## Critical Instructions
    
    ### DO:
    ✅ Merge descriptions comprehensively (don't just pick one)
    ✅ Identify and document all conflicts
    ✅ Preserve information from all dashboards
    ✅ Use "most_common_wins" for categorical fields (refresh_frequency, vertical)
    ✅ Combine relationship contexts to show full picture
    
    ### DON'T:
    ❌ Simply pick the first entry
    ❌ Ignore conflicts
    ❌ Lose information from any dashboard
    ❌ Create duplicate entries
    """
    
    table_name: str = dspy.InputField(desc="Table name to merge")
    dashboard_metadata_entries: str = dspy.InputField(desc="JSON array of table metadata entries from different dashboards, each with dashboard_id, table_description, refresh_frequency, vertical, partition_column, remarks, relationship_context")
    
    merged_table_description: str = dspy.OutputField(desc="Unified table description with data_description and business_description merged from all dashboards")
    merged_refresh_frequency: str = dspy.OutputField(desc="Unified refresh frequency (resolved from conflicts)")
    merged_vertical: str = dspy.OutputField(desc="Unified vertical (resolved from conflicts)")
    merged_partition_column: str = dspy.OutputField(desc="Unified partition column (resolved from conflicts)")
    merged_remarks: str = dspy.OutputField(desc="Merged remarks from all dashboards")
    merged_relationship_context: str = dspy.OutputField(desc="Merged relationship context from all dashboards")
    conflicts_detected: str = dspy.OutputField(desc="JSON array of detected conflicts with: field_name, conflicting_values, dashboard_ids, resolution_approach")


class ColumnMetadataMerger(dspy.Signature):
    """
    Merge column metadata from multiple dashboards into a unified entry.
    
    SYSTEM PROMPT: Column Metadata Merger
    
    ## Objective
    Consolidate column metadata entries from multiple dashboards into a single unified entry.
    Detect conflicts (different descriptions, variable types, required flags) and resolve them.
    
    ## Input
    You will receive multiple column metadata entries for the same (table_name, column_name) from different dashboards.
    Each entry contains: table_name, column_name, variable_type, column_description, required_flag.
    
    ## Output Requirements
    
    ### 1. Unified Column Description
    - Merge all descriptions, showing how the column is used across different dashboards
    - Highlight common usage patterns and unique use cases
    
    ### 2. Variable Type
    - If all dashboards agree: use that value
    - If different: use the most common value OR flag as "varies" if significant differences
    
    ### 3. Required Flag
    - If all dashboards agree: use that value
    - If different: use "Y" if ANY dashboard marks it as required, OR use most common value
    
    ### 4. Conflict Detection
    - Identify conflicts in: descriptions, variable_type, required_flag
    - For each conflict, note: conflicting values, dashboard sources, resolution approach
    
    ## Conflict Resolution Rules
    
    1. **Most Common Wins**: For variable_type
    2. **Any Required = Required**: For required_flag, if any dashboard says required, mark as required
    3. **Merge Descriptions**: Combine all descriptions to show full usage context
    
    ## Critical Instructions
    
    ### DO:
    ✅ Merge descriptions to show full usage across dashboards
    ✅ Identify all conflicts
    ✅ Use "any_required" logic for required_flag
    ✅ Preserve information from all dashboards
    
    ### DON'T:
    ❌ Pick first entry only
    ❌ Ignore conflicts
    ❌ Lose usage context from any dashboard
    """
    
    table_name: str = dspy.InputField(desc="Table name")
    column_name: str = dspy.InputField(desc="Column name to merge")
    dashboard_metadata_entries: str = dspy.InputField(desc="JSON array of column metadata entries from different dashboards, each with dashboard_id, variable_type, column_description, required_flag")
    
    merged_column_description: str = dspy.OutputField(desc="Unified column description merged from all dashboards")
    merged_variable_type: str = dspy.OutputField(desc="Unified variable type (resolved from conflicts)")
    merged_required_flag: str = dspy.OutputField(desc="Unified required flag (Y/N, resolved from conflicts)")
    conflicts_detected: str = dspy.OutputField(desc="JSON array of detected conflicts with: field_name, conflicting_values, dashboard_ids, resolution_approach")


class JoiningConditionMerger(dspy.Signature):
    """
    Merge joining conditions from multiple dashboards.
    
    SYSTEM PROMPT: Joining Condition Merger
    
    ## Objective
    Consolidate joining conditions between the same table pairs from multiple dashboards.
    Different dashboards may use different join conditions for the same table pair - preserve all of them.
    
    ## Input
    You will receive multiple joining condition entries for the same (table1, table2) pair from different dashboards.
    Each entry contains: table1, table2, joining_condition, remarks, dashboard_id.
    
    ## Output Requirements
    
    ### 1. Multiple Join Conditions
    - If dashboards use the SAME join condition: create one entry with merged remarks
    - If dashboards use DIFFERENT join conditions: create separate entries for each unique condition
    - Preserve all unique join patterns
    
    ### 2. Remarks
    - For identical joins: merge remarks from all dashboards
    - For different joins: keep separate remarks explaining when each join is used
    
    ### 3. Conflict Detection
    - Note if same table pair has multiple different join conditions
    - Document which dashboards use which join condition
    
    ## Critical Instructions
    
    ### DO:
    ✅ Preserve ALL unique join conditions (don't merge different joins)
    ✅ Merge remarks only for identical joins
    ✅ Document which dashboards use which join condition
    ✅ Note if multiple valid join patterns exist
    
    ### DON'T:
    ❌ Merge different join conditions into one
    ❌ Lose any unique join patterns
    ❌ Ignore that same tables can be joined differently
    """
    
    table1: str = dspy.InputField(desc="First table name")
    table2: str = dspy.InputField(desc="Second table name")
    dashboard_join_entries: str = dspy.InputField(desc="JSON array of joining condition entries from different dashboards, each with dashboard_id, joining_condition, remarks")
    
    merged_joining_conditions: str = dspy.OutputField(desc="JSON array of merged joining conditions. If joins are identical, merge into one entry with combined remarks. If different, keep separate entries. Each entry: joining_condition, remarks, dashboard_ids (list of dashboards using this join)")
    conflicts_detected: str = dspy.OutputField(desc="JSON array noting if multiple different join conditions exist for this table pair, with details on which dashboards use which join")


class TermDefinitionMerger(dspy.Signature):
    """
    Merge term definitions from multiple dashboards.
    
    SYSTEM PROMPT: Term Definition Merger
    
    ## Objective
    Consolidate term definitions from multiple dashboards, identifying synonyms and unifying definitions.
    
    ## Input
    You will receive multiple term definition entries for the same or similar terms from different dashboards.
    Each entry contains: term, type, definition, business_alias, dashboard_id.
    
    ## Output Requirements
    
    ### 1. Term Unification
    - Identify if different terms refer to the same concept (synonyms)
    - Merge synonyms into a single entry with all term names listed
    
    ### 2. Unified Definition
    - Merge definitions from all dashboards
    - Show how the term is used across different contexts
    - If definitions conflict significantly, note the conflict
    
    ### 3. Type Resolution
    - If all dashboards agree on type: use that
    - If different: use the most specific type (Metric / Calculated Field > Metric > Synonym > Category)
    
    ### 4. Business Alias
    - Merge all business aliases from all dashboards
    - Include all alternative names
    
    ### 5. Conflict Detection
    - Identify if same term has different definitions
    - Note if term type conflicts
    - Document synonym relationships
    
    ## Conflict Resolution Rules
    
    1. **Merge Synonyms**: Group terms that refer to same concept
    2. **Most Specific Type**: Use most specific type classification
    3. **Merge Definitions**: Combine definitions showing all usage contexts
    4. **Preserve All Aliases**: Include all business aliases from all dashboards
    
    ## Critical Instructions
    
    ### DO:
    ✅ Identify and merge synonyms
    ✅ Combine definitions from all dashboards
    ✅ Preserve all business aliases
    ✅ Use most specific type classification
    ✅ Document synonym relationships
    
    ### DON'T:
    ❌ Create duplicate entries for synonyms
    ❌ Pick only one definition
    ❌ Lose business aliases
    ❌ Ignore synonym relationships
    """
    
    term_variants: str = dspy.InputField(desc="JSON array of term definition entries from different dashboards, each with dashboard_id, term, type, definition, business_alias. May include same term or synonyms.")
    
    merged_term: str = dspy.OutputField(desc="Unified term name (primary term, with synonyms noted)")
    merged_type: str = dspy.OutputField(desc="Unified type (Metric, Metric / Calculated Field, Synonym, or Category)")
    merged_definition: str = dspy.OutputField(desc="Unified definition merged from all dashboards")
    merged_business_alias: str = dspy.OutputField(desc="Merged business aliases from all dashboards (comma-separated)")
    synonyms_identified: str = dspy.OutputField(desc="JSON array of synonym relationships found: {term1, term2, relationship_type}")
    conflicts_detected: str = dspy.OutputField(desc="JSON array of detected conflicts: field_name, conflicting_values, dashboard_ids, resolution_approach")


# ============================================================================
# Metadata Merger Class
# ============================================================================

class MetadataMerger:
    """
    Merges metadata from multiple dashboards into unified metadata files.
    """
    
    def __init__(self, dashboard_ids: List[int], api_key: Optional[str] = None, 
                 model: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the merger.
        
        Args:
            dashboard_ids: List of dashboard IDs to merge
            api_key: LLM API key
            model: LLM model name
            base_url: LLM base URL
        """
        self.dashboard_ids = dashboard_ids
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or LLM_API_KEY
        self.model = model or LLM_MODEL
        self.base_url = base_url or LLM_BASE_URL
        
        if not self.api_key:
            raise ValueError("LLM API key not configured. Set ANTHROPIC_API_KEY env var or config.LLM_API_KEY")
        
        # Initialize DSPy extractors
        self._init_dspy_extractors()
        
        # Output directory
        self.merged_dir = "extracted_meta/merged_metadata"
        os.makedirs(self.merged_dir, exist_ok=True)
        
        # Track conflicts
        self.all_conflicts = []
        
        # Progress tracker
        self.progress_tracker = get_progress_tracker()
    
    def _init_dspy_extractors(self):
        """Initialize DSPy extractors for merging."""
        # Configure model - don't call dspy.configure() if already configured in another thread
        # Instead, create LM instances and pass them directly to ChainOfThought
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
            # DSPy already configured in another thread, use the existing configuration
            pass
        
        # Create extractors - they will use the configured LM
        self.table_merger = dspy.ChainOfThought(TableMetadataMerger)
        self.column_merger = dspy.ChainOfThought(ColumnMetadataMerger)
        self.join_merger = dspy.ChainOfThought(JoiningConditionMerger)
        self.term_merger = dspy.ChainOfThought(TermDefinitionMerger)
    
    def load_dashboard_metadata(self, dashboard_id) -> Dict:
        """
        Load all metadata files for a dashboard.
        
        Args:
            dashboard_id: Dashboard ID (int) or 'merged' (str) for existing merged metadata
        
        Returns:
            Dict with keys: table_metadata, columns_metadata, joining_conditions, 
            definitions, filter_conditions
        """
        if dashboard_id == 'merged':
            # Load existing merged metadata
            return self.load_merged_metadata()
        
        dashboard_dir = f"extracted_meta/{dashboard_id}"
        
        metadata = {
            'dashboard_id': dashboard_id,
            'table_metadata': None,
            'columns_metadata': None,
            'joining_conditions': None,
            'definitions': None,
            'filter_conditions': None
        }
        
        # Load table metadata
        table_file = f"{dashboard_dir}/{dashboard_id}_table_metadata.csv"
        if os.path.exists(table_file):
            metadata['table_metadata'] = pd.read_csv(table_file)
        
        # Load columns metadata
        columns_file = f"{dashboard_dir}/{dashboard_id}_columns_metadata.csv"
        if os.path.exists(columns_file):
            try:
                df = pd.read_csv(columns_file)
                if len(df) > 0:
                    metadata['columns_metadata'] = df
                else:
                    metadata['columns_metadata'] = pd.DataFrame(columns=['table_name', 'column_name', 'variable_type', 'column_description', 'required_flag'])
            except (pd.errors.EmptyDataError, ValueError):
                # Empty file, create empty DataFrame with correct columns
                metadata['columns_metadata'] = pd.DataFrame(columns=['table_name', 'column_name', 'variable_type', 'column_description', 'required_flag'])
        
        # Load joining conditions
        joins_file = f"{dashboard_dir}/{dashboard_id}_joining_conditions.csv"
        if os.path.exists(joins_file):
            metadata['joining_conditions'] = pd.read_csv(joins_file)
        
        # Load definitions
        definitions_file = f"{dashboard_dir}/{dashboard_id}_definitions.csv"
        if os.path.exists(definitions_file):
            metadata['definitions'] = pd.read_csv(definitions_file)
        
        # Load filter conditions (text file)
        filter_file = f"{dashboard_dir}/{dashboard_id}_filter_conditions.txt"
        if os.path.exists(filter_file):
            with open(filter_file, 'r', encoding='utf-8') as f:
                metadata['filter_conditions'] = f.read()
        
        return metadata
    
    def merge_table_metadata(self) -> pd.DataFrame:
        """Merge table metadata from all dashboards."""
        print("\n" + "="*80)
        print("Merging Table Metadata")
        print("="*80)
        
        # Load all table metadata
        all_tables = {}
        for dashboard_id in self.dashboard_ids:
            metadata = self.load_dashboard_metadata(dashboard_id)
            if metadata['table_metadata'] is not None:
                df = metadata['table_metadata']
                for _, row in df.iterrows():
                    table_name = row['table_name']
                    if table_name not in all_tables:
                        all_tables[table_name] = []
                    # Use 'merged' as dashboard_id if it's the merged metadata
                    dash_id = 'merged' if dashboard_id == 'merged' else dashboard_id
                    all_tables[table_name].append({
                        'dashboard_id': dash_id,
                        'table_description': row.get('table_description', ''),
                        'refresh_frequency': row.get('refresh_frequency', ''),
                        'vertical': row.get('vertical', ''),
                        'partition_column': row.get('partition_column', ''),
                        'remarks': row.get('remarks', ''),
                        'relationship_context': row.get('relationship_context', '')
                    })
        
        # Merge each table
        merged_rows = []
        for table_name, entries in all_tables.items():
            if len(entries) == 1:
                # Single entry, no merging needed
                entry = entries[0]
                merged_rows.append({
                    'table_name': table_name,
                    'table_description': entry['table_description'],
                    'refresh_frequency': entry['refresh_frequency'],
                    'vertical': entry['vertical'],
                    'partition_column': entry['partition_column'],
                    'remarks': entry['remarks'],
                    'relationship_context': entry['relationship_context']
                })
            else:
                # Multiple entries, merge using LLM
                print(f"  Merging {table_name} from {len(entries)} dashboards...")
                entries_json = json.dumps(entries, indent=2)
                
                try:
                    result = self.table_merger(
                        table_name=table_name,
                        dashboard_metadata_entries=entries_json
                    )
                    
                    # Parse conflicts
                    conflicts = []
                    try:
                        conflicts = json.loads(result.conflicts_detected) if result.conflicts_detected else []
                        for conflict in conflicts:
                            conflict['table_name'] = table_name
                            conflict['metadata_type'] = 'table_metadata'
                            self.all_conflicts.append(conflict)
                    except:
                        pass
                    
                    merged_rows.append({
                        'table_name': table_name,
                        'table_description': result.merged_table_description,
                        'refresh_frequency': result.merged_refresh_frequency,
                        'vertical': result.merged_vertical,
                        'partition_column': result.merged_partition_column,
                        'remarks': result.merged_remarks,
                        'relationship_context': result.merged_relationship_context
                    })
                except Exception as e:
                    print(f"    ⚠️  Error merging {table_name}: {str(e)}")
                    # Fallback: use first entry
                    entry = entries[0]
                    merged_rows.append({
                        'table_name': table_name,
                        'table_description': entry['table_description'],
                        'refresh_frequency': entry['refresh_frequency'],
                        'vertical': entry['vertical'],
                        'partition_column': entry['partition_column'],
                        'remarks': entry['remarks'],
                        'relationship_context': entry['relationship_context']
                    })
        
        merged_df = pd.DataFrame(merged_rows)
        output_file = f"{self.merged_dir}/consolidated_table_metadata.csv"
        merged_df.to_csv(output_file, index=False)
        print(f"\n✅ Merged table metadata saved to: {output_file}")
        print(f"   Total tables: {len(merged_df)}")
        
        return merged_df
    
    def merge_columns_metadata(self) -> pd.DataFrame:
        """Merge column metadata from all dashboards."""
        print("\n" + "="*80)
        print("Merging Column Metadata")
        print("="*80)
        
        # Load all column metadata
        all_columns = {}
        for dashboard_id in self.dashboard_ids:
            metadata = self.load_dashboard_metadata(dashboard_id)
            if metadata['columns_metadata'] is not None:
                df = metadata['columns_metadata']
                for _, row in df.iterrows():
                    key = (row['table_name'], row['column_name'])
                    if key not in all_columns:
                        all_columns[key] = []
                    dash_id = 'merged' if dashboard_id == 'merged' else dashboard_id
                    all_columns[key].append({
                        'dashboard_id': dash_id,
                        'variable_type': row.get('variable_type', ''),
                        'column_description': row.get('column_description', ''),
                        'required_flag': row.get('required_flag', '')
                    })
        
        # Merge each column
        merged_rows = []
        for (table_name, column_name), entries in all_columns.items():
            if len(entries) == 1:
                # Single entry
                entry = entries[0]
                merged_rows.append({
                    'table_name': table_name,
                    'column_name': column_name,
                    'variable_type': entry['variable_type'],
                    'column_description': entry['column_description'],
                    'required_flag': entry['required_flag']
                })
            else:
                # Multiple entries, merge using LLM
                print(f"  Merging {table_name}.{column_name} from {len(entries)} dashboards...")
                entries_json = json.dumps(entries, indent=2)
                
                try:
                    result = self.column_merger(
                        table_name=table_name,
                        column_name=column_name,
                        dashboard_metadata_entries=entries_json
                    )
                    
                    # Parse conflicts
                    conflicts = []
                    try:
                        conflicts = json.loads(result.conflicts_detected) if result.conflicts_detected else []
                        for conflict in conflicts:
                            conflict['table_name'] = table_name
                            conflict['column_name'] = column_name
                            conflict['metadata_type'] = 'columns_metadata'
                            self.all_conflicts.append(conflict)
                    except:
                        pass
                    
                    merged_rows.append({
                        'table_name': table_name,
                        'column_name': column_name,
                        'variable_type': result.merged_variable_type,
                        'column_description': result.merged_column_description,
                        'required_flag': result.merged_required_flag
                    })
                except Exception as e:
                    print(f"    ⚠️  Error merging {table_name}.{column_name}: {str(e)}")
                    # Fallback: use first entry
                    entry = entries[0]
                    merged_rows.append({
                        'table_name': table_name,
                        'column_name': column_name,
                        'variable_type': entry['variable_type'],
                        'column_description': entry['column_description'],
                        'required_flag': entry['required_flag']
                    })
        
        merged_df = pd.DataFrame(merged_rows)
        output_file = f"{self.merged_dir}/consolidated_columns_metadata.csv"
        merged_df.to_csv(output_file, index=False)
        print(f"\n✅ Merged column metadata saved to: {output_file}")
        print(f"   Total columns: {len(merged_df)}")
        
        return merged_df
    
    def merge_joining_conditions(self) -> pd.DataFrame:
        """Merge joining conditions from all dashboards."""
        print("\n" + "="*80)
        print("Merging Joining Conditions")
        print("="*80)
        
        # Load all joining conditions
        all_joins = {}
        for dashboard_id in self.dashboard_ids:
            metadata = self.load_dashboard_metadata(dashboard_id)
            if metadata['joining_conditions'] is not None:
                df = metadata['joining_conditions']
                for _, row in df.iterrows():
                    # Use sorted tuple as key to handle (A,B) and (B,A) as same
                    table1 = row['table1']
                    table2 = row['table2']
                    key = tuple(sorted([table1, table2]))
                    
                    if key not in all_joins:
                        all_joins[key] = []
                    dash_id = 'merged' if dashboard_id == 'merged' else dashboard_id
                    all_joins[key].append({
                        'dashboard_id': dash_id,
                        'table1': table1,
                        'table2': table2,
                        'joining_condition': row.get('joining_condition', ''),
                        'remarks': row.get('remarks', '')
                    })
        
        # Merge each table pair
        merged_rows = []
        for (table1, table2), entries in all_joins.items():
            if len(entries) == 1:
                # Single entry
                entry = entries[0]
                merged_rows.append({
                    'table1': entry['table1'],
                    'table2': entry['table2'],
                    'joining_condition': entry['joining_condition'],
                    'remarks': entry['remarks']
                })
            else:
                # Multiple entries, merge using LLM
                print(f"  Merging joins between {table1} and {table2} from {len(entries)} dashboards...")
                entries_json = json.dumps(entries, indent=2)
                
                try:
                    result = self.join_merger(
                        table1=table1,
                        table2=table2,
                        dashboard_join_entries=entries_json
                    )
                    
                    # Parse conflicts
                    conflicts = []
                    try:
                        conflicts = json.loads(result.conflicts_detected) if result.conflicts_detected else []
                        for conflict in conflicts:
                            conflict['table1'] = table1
                            conflict['table2'] = table2
                            conflict['metadata_type'] = 'joining_conditions'
                            self.all_conflicts.append(conflict)
                    except:
                        pass
                    
                    # Parse merged joining conditions (may be multiple if different joins exist)
                    try:
                        merged_joins = json.loads(result.merged_joining_conditions) if result.merged_joining_conditions else []
                        for join_entry in merged_joins:
                            merged_rows.append({
                                'table1': table1,
                                'table2': table2,
                                'joining_condition': join_entry.get('joining_condition', ''),
                                'remarks': join_entry.get('remarks', '')
                            })
                    except:
                        # Fallback: create one entry per original entry
                        for entry in entries:
                            merged_rows.append({
                                'table1': entry['table1'],
                                'table2': entry['table2'],
                                'joining_condition': entry['joining_condition'],
                                'remarks': entry['remarks']
                            })
                except Exception as e:
                    print(f"    ⚠️  Error merging joins: {str(e)}")
                    # Fallback: keep all entries
                    for entry in entries:
                        merged_rows.append({
                            'table1': entry['table1'],
                            'table2': entry['table2'],
                            'joining_condition': entry['joining_condition'],
                            'remarks': entry['remarks']
                        })
        
        merged_df = pd.DataFrame(merged_rows)
        output_file = f"{self.merged_dir}/consolidated_joining_conditions.csv"
        merged_df.to_csv(output_file, index=False)
        print(f"\n✅ Merged joining conditions saved to: {output_file}")
        print(f"   Total join pairs: {len(merged_df)}")
        
        return merged_df
    
    def merge_term_definitions(self) -> pd.DataFrame:
        """Merge term definitions from all dashboards."""
        print("\n" + "="*80)
        print("Merging Term Definitions")
        print("="*80)
        
        # Load all term definitions
        all_terms = {}
        for dashboard_id in self.dashboard_ids:
            metadata = self.load_dashboard_metadata(dashboard_id)
            if metadata['definitions'] is not None:
                df = metadata['definitions']
                for _, row in df.iterrows():
                    term = row['term']
                    # Group by term (case-insensitive)
                    term_key = term.lower().strip()
                    if term_key not in all_terms:
                        all_terms[term_key] = []
                    dash_id = 'merged' if dashboard_id == 'merged' else dashboard_id
                    all_terms[term_key].append({
                        'dashboard_id': dash_id,
                        'term': term,
                        'type': row.get('type', ''),
                        'definition': row.get('definition', ''),
                        'business_alias': row.get('business_alias', '')
                    })
        
        # Merge each term (or group of synonyms)
        merged_rows = []
        processed_terms = set()
        
        for term_key, entries in all_terms.items():
            if term_key in processed_terms:
                continue
            
            if len(entries) == 1:
                # Single entry
                entry = entries[0]
                merged_rows.append({
                    'term': entry['term'],
                    'type': entry['type'],
                    'definition': entry['definition'],
                    'business_alias': entry['business_alias']
                })
                processed_terms.add(term_key)
            else:
                # Multiple entries, merge using LLM (may include synonyms)
                print(f"  Merging term '{entries[0]['term']}' from {len(entries)} dashboards...")
                entries_json = json.dumps(entries, indent=2)
                
                try:
                    result = self.term_merger(term_variants=entries_json)
                    
                    # Parse conflicts
                    conflicts = []
                    try:
                        conflicts = json.loads(result.conflicts_detected) if result.conflicts_detected else []
                        for conflict in conflicts:
                            conflict['term'] = entries[0]['term']
                            conflict['metadata_type'] = 'definitions'
                            self.all_conflicts.append(conflict)
                    except:
                        pass
                    
                    # Parse synonyms
                    synonyms = []
                    try:
                        synonyms = json.loads(result.synonyms_identified) if result.synonyms_identified else []
                        for syn in synonyms:
                            # Mark synonym terms as processed
                            for syn_term in [syn.get('term1', ''), syn.get('term2', '')]:
                                if syn_term:
                                    processed_terms.add(syn_term.lower().strip())
                    except:
                        pass
                    
                    merged_rows.append({
                        'term': result.merged_term,
                        'type': result.merged_type,
                        'definition': result.merged_definition,
                        'business_alias': result.merged_business_alias
                    })
                    processed_terms.add(term_key)
                except Exception as e:
                    print(f"    ⚠️  Error merging term: {str(e)}")
                    # Fallback: use first entry
                    entry = entries[0]
                    merged_rows.append({
                        'term': entry['term'],
                        'type': entry['type'],
                        'definition': entry['definition'],
                        'business_alias': entry['business_alias']
                    })
                    processed_terms.add(term_key)
        
        merged_df = pd.DataFrame(merged_rows)
        output_file = f"{self.merged_dir}/consolidated_definitions.csv"
        merged_df.to_csv(output_file, index=False)
        print(f"\n✅ Merged term definitions saved to: {output_file}")
        print(f"   Total terms: {len(merged_df)}")
        
        return merged_df
    
    def merge_filter_conditions(self) -> str:
        """Merge filter conditions from all dashboards (concatenate text files)."""
        print("\n" + "="*80)
        print("Merging Filter Conditions")
        print("="*80)
        
        all_filter_conditions = []
        
        for dashboard_id in self.dashboard_ids:
            metadata = self.load_dashboard_metadata(dashboard_id)
            if metadata['filter_conditions']:
                all_filter_conditions.append(f"\n{'='*80}\n")
                all_filter_conditions.append(f"## Dashboard {dashboard_id}\n")
                all_filter_conditions.append(f"{'='*80}\n\n")
                all_filter_conditions.append(metadata['filter_conditions'])
                all_filter_conditions.append("\n")
        
        merged_content = "".join(all_filter_conditions)
        output_file = f"{self.merged_dir}/consolidated_filter_conditions.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        print(f"\n✅ Merged filter conditions saved to: {output_file}")
        
        return merged_content
    
    def generate_conflicts_report(self):
        """Generate conflicts report JSON."""
        print("\n" + "="*80)
        print("Generating Conflicts Report")
        print("="*80)
        
        conflicts_report = {
            'total_conflicts': len(self.all_conflicts),
            'conflicts_by_type': {},
            'conflicts': self.all_conflicts
        }
        
        # Group by metadata type
        for conflict in self.all_conflicts:
            metadata_type = conflict.get('metadata_type', 'unknown')
            if metadata_type not in conflicts_report['conflicts_by_type']:
                conflicts_report['conflicts_by_type'][metadata_type] = []
            conflicts_report['conflicts_by_type'][metadata_type].append(conflict)
        
        output_file = f"{self.merged_dir}/conflicts_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(conflicts_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Conflicts report saved to: {output_file}")
        print(f"   Total conflicts: {len(self.all_conflicts)}")
        for metadata_type, conflicts in conflicts_report['conflicts_by_type'].items():
            print(f"   - {metadata_type}: {len(conflicts)} conflicts")
        
        return conflicts_report
    
    def merge_all(self, include_existing_merged: bool = False):
        """
        Merge all metadata types.
        
        Args:
            include_existing_merged: If True, also merge with existing merged_metadata
        """
        # Initialize merge progress
        self.progress_tracker.start_merge()
        
        print("\n" + "="*80)
        print("METADATA MERGER")
        print("="*80)
        
        if include_existing_merged:
            print(f"Merging metadata from {len(self.dashboard_ids)} new dashboards with existing merged metadata")
            print(f"New Dashboard IDs: {', '.join(map(str, self.dashboard_ids))}")
        else:
            print(f"Merging metadata from {len(self.dashboard_ids)} dashboards")
            print(f"Dashboard IDs: {', '.join(map(str, self.dashboard_ids))}")
        print("="*80)
        
        # If including existing merged metadata, add 'merged' to dashboard_ids list
        dashboard_ids_to_process = self.dashboard_ids.copy()
        if include_existing_merged:
            # Check if merged metadata exists
            merged_metadata = self.load_merged_metadata()
            has_existing = any([
                merged_metadata['table_metadata'] is not None and len(merged_metadata['table_metadata']) > 0,
                merged_metadata['columns_metadata'] is not None and len(merged_metadata['columns_metadata']) > 0,
                merged_metadata['definitions'] is not None and len(merged_metadata['definitions']) > 0
            ])
            if has_existing:
                dashboard_ids_to_process = ['merged'] + dashboard_ids_to_process
                print(f"  ℹ️  Including existing merged metadata in merge process")
            else:
                print(f"  ℹ️  No existing merged metadata found, proceeding with new dashboards only")
        
        # Temporarily update dashboard_ids for processing
        original_dashboard_ids = self.dashboard_ids
        self.dashboard_ids = dashboard_ids_to_process
        
        # Merge each metadata type with progress updates
        self.progress_tracker.update_merge_status('table_metadata', [])
        table_metadata = self.merge_table_metadata()
        
        self.progress_tracker.update_merge_status('columns_metadata', ['table_metadata'])
        columns_metadata = self.merge_columns_metadata()
        
        self.progress_tracker.update_merge_status('joining_conditions', ['table_metadata', 'columns_metadata'])
        joining_conditions = self.merge_joining_conditions()
        
        self.progress_tracker.update_merge_status('definitions', ['table_metadata', 'columns_metadata', 'joining_conditions'])
        term_definitions = self.merge_term_definitions()
        
        self.progress_tracker.update_merge_status('filter_conditions', ['table_metadata', 'columns_metadata', 'joining_conditions', 'definitions'])
        filter_conditions = self.merge_filter_conditions()
        
        # Generate conflicts report
        self.progress_tracker.update_merge_status('conflicts_report', ['table_metadata', 'columns_metadata', 'joining_conditions', 'definitions', 'filter_conditions'])
        conflicts_report = self.generate_conflicts_report()
        
        # Mark merge as completed
        self.progress_tracker.complete_merge()
        
        # Restore original dashboard_ids for summary
        self.dashboard_ids = original_dashboard_ids
        
        # Create merged_metadata.json summary
        merged_metadata_summary = {
            'dashboard_ids': self.dashboard_ids,
            'incremental_merge': include_existing_merged,
            'merged_files': {
                'table_metadata': f"{self.merged_dir}/consolidated_table_metadata.csv",
                'columns_metadata': f"{self.merged_dir}/consolidated_columns_metadata.csv",
                'joining_conditions': f"{self.merged_dir}/consolidated_joining_conditions.csv",
                'definitions': f"{self.merged_dir}/consolidated_definitions.csv",
                'filter_conditions': f"{self.merged_dir}/consolidated_filter_conditions.txt",
                'conflicts_report': f"{self.merged_dir}/conflicts_report.json"
            },
            'statistics': {
                'total_tables': len(table_metadata),
                'total_columns': len(columns_metadata),
                'total_joins': len(joining_conditions),
                'total_terms': len(term_definitions),
                'total_conflicts': len(self.all_conflicts)
            },
            'conflict_resolution_rules': {
                'most_common_wins': 'For categorical fields (refresh_frequency, vertical, variable_type), use the most common value across dashboards',
                'any_required': 'For required_flag, if ANY dashboard marks it as required, mark as required',
                'merge_descriptions': 'For descriptions, merge content from all dashboards rather than picking one',
                'preserve_all_joins': 'For joining conditions, preserve all unique join patterns (don\'t merge different joins)',
                'merge_synonyms': 'For term definitions, identify and merge synonyms into single entries'
            }
        }
        
        output_file = f"{self.merged_dir}/merged_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_metadata_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Merged metadata summary saved to: {output_file}")
        print("\n" + "="*80)
        print("MERGE COMPLETE")
        print("="*80)
        
        return merged_metadata_summary

