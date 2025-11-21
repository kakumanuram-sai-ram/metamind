# Multi-Dashboard Processing Implementation Summary

## Overview

Successfully extended the single-dashboard metadata extraction system to support multi-dashboard processing with three main components:

1. **DashboardMetadataOrchestrator** - Extracts metadata for each dashboard independently
2. **MetadataMerger** - Merges metadata from all dashboards using LLM-based consolidation
3. **KnowledgeBaseBuilder** - Converts merged metadata into knowledge base format

## Files Created

### 1. `scripts/orchestrator.py`
- **Purpose**: Iterates through dashboard IDs and extracts metadata for each
- **Key Features**:
  - Calls `extract_dashboard_with_timing()` for each dashboard
  - Tracks success/failure for each dashboard
  - Configurable error handling (continue or stop on error)
  - Verifies output files are generated

### 2. `scripts/merger.py`
- **Purpose**: Merges metadata from multiple dashboards using LLM
- **Key Features**:
  - LLM-based merging for all metadata types
  - Conflict detection and reporting
  - Four DSPy signatures for merging:
    - `TableMetadataMerger`
    - `ColumnMetadataMerger`
    - `JoiningConditionMerger`
    - `TermDefinitionMerger`
  - Generates `conflicts_report.json`
  - Creates consolidated CSV files

### 3. `scripts/knowledge_base_builder.py`
- **Purpose**: Converts merged metadata into knowledge base format
- **Key Features**:
  - Creates structured JSON knowledge base
  - Generates markdown documentation
  - Creates searchable index
  - Organizes by component (tables, columns, joins, definitions, filters)

### 4. `scripts/process_multiple_dashboards.py`
- **Purpose**: Main entry point orchestrating the complete workflow
- **Key Features**:
  - Coordinates extract → merge → build KB workflow
  - Configurable steps (can skip extract/merge/KB build)
  - Error handling and reporting

## System Prompts for Merging

Each metadata type has a dedicated DSPy signature with detailed system prompts:

### TableMetadataMerger
- Merges table descriptions (data_description + business_description)
- Resolves refresh_frequency conflicts (most common wins)
- Resolves vertical conflicts (list all or primary)
- Resolves partition_column conflicts (most common wins)
- Merges remarks and relationship_context

### ColumnMetadataMerger
- Merges column descriptions from all dashboards
- Resolves variable_type conflicts (most common wins)
- Resolves required_flag conflicts (any required = required)
- Preserves usage context from all dashboards

### JoiningConditionMerger
- **Preserves all unique join patterns** (doesn't merge different joins)
- Merges remarks only for identical joins
- Documents which dashboards use which join condition
- Notes if multiple valid join patterns exist

### TermDefinitionMerger
- Identifies and merges synonyms
- Merges definitions from all dashboards
- Resolves type conflicts (most specific type wins)
- Preserves all business aliases
- Documents synonym relationships

## Output Structure

```
extracted_meta/
├── {dashboard_id}/                    # Individual dashboard metadata (for debugging)
│   ├── {dashboard_id}_json.json
│   ├── {dashboard_id}_csv.csv
│   ├── {dashboard_id}_queries.sql
│   ├── {dashboard_id}_tables_columns.csv
│   ├── {dashboard_id}_tables_columns_enriched.csv
│   ├── {dashboard_id}_table_metadata.csv
│   ├── {dashboard_id}_columns_metadata.csv
│   ├── {dashboard_id}_joining_conditions.csv
│   ├── {dashboard_id}_filter_conditions.txt
│   └── {dashboard_id}_definitions.csv
│
├── merged_metadata/                   # Consolidated metadata (master schema)
│   ├── consolidated_table_metadata.csv
│   ├── consolidated_columns_metadata.csv
│   ├── consolidated_joining_conditions.csv
│   ├── consolidated_definitions.csv
│   ├── consolidated_filter_conditions.txt
│   ├── conflicts_report.json
│   └── merged_metadata.json
│
└── knowledge_base/                   # Knowledge base for LLM/documentation
    ├── unified_knowledge_base.json
    ├── knowledge_base.md
    ├── search_index.json
    ├── tables_knowledge_base.json
    ├── columns_knowledge_base.json
    ├── joins_knowledge_base.json
    ├── definitions_knowledge_base.json
    └── filter_conditions_knowledge_base.txt
```

## Conflict Resolution Rules

1. **Most Common Wins**: For categorical fields (refresh_frequency, vertical, variable_type)
2. **Any Required = Required**: For required_flag, if ANY dashboard marks it as required
3. **Merge Descriptions**: Combine descriptions from all dashboards (don't pick one)
4. **Preserve All Joins**: Don't merge different join conditions (preserve all unique patterns)
5. **Merge Synonyms**: Group terms that refer to the same concept

## Usage

### Command Line
```bash
# Process multiple dashboards (extract → merge → build KB)
python scripts/process_multiple_dashboards.py 842 729 100

# Skip extraction (if already done)
python scripts/process_multiple_dashboards.py 842 729 100 --skip-extract

# Only merge (skip KB build)
python scripts/process_multiple_dashboards.py 842 729 100 --skip-kb

# Stop on error
python scripts/process_multiple_dashboards.py 842 729 100 --stop-on-error
```

### Python API
```python
from scripts.process_multiple_dashboards import process_multiple_dashboards

process_multiple_dashboards(
    dashboard_ids=[842, 729, 100],
    extract=True,
    merge=True,
    build_kb=True,
    continue_on_error=True
)
```

## Key Design Decisions

1. **Separate Modules**: Each component is a separate module for maintainability
2. **LLM-Based Merging**: Uses LLM for intelligent merging rather than simple aggregation
3. **Conflict Detection**: Explicitly detects and reports conflicts
4. **Preserve Information**: Doesn't lose information from any dashboard
5. **Flexible Workflow**: Can run steps independently (extract only, merge only, etc.)
6. **Individual + Merged**: Keeps individual dashboard files for debugging, creates merged files as master schema

## Testing Recommendations

1. **Test with 2-3 dashboards first** to verify merging logic
2. **Review conflicts_report.json** to understand conflict resolution
3. **Verify knowledge base** structure and content
4. **Test error handling** with invalid dashboard IDs
5. **Test incremental processing** (skip extract, only merge)

## Future Enhancements

1. Parallel dashboard extraction
2. Incremental merging (merge new dashboard into existing merged metadata)
3. Version control for merged metadata
4. Advanced conflict resolution strategies
5. Knowledge base query interface
6. API endpoints for multi-dashboard processing

