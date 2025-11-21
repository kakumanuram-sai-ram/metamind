# Multi-Dashboard Metadata Processing

This document describes the multi-dashboard metadata processing system that extends the single-dashboard extraction to handle multiple dashboards, merge their metadata, and build a unified knowledge base.

## Overview

The multi-dashboard processing system consists of three main components:

1. **DashboardMetadataOrchestrator**: Extracts metadata for each dashboard independently
2. **MetadataMerger**: Merges metadata from all dashboards using LLM-based consolidation
3. **KnowledgeBaseBuilder**: Converts merged metadata into a knowledge base format

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  process_multiple_dashboards.py (Main Entry Point)          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Orchestrator │   │    Merger    │   │  KB Builder  │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
extracted_meta/    extracted_meta/    extracted_meta/
{dashboard_id}/    merged_metadata/    knowledge_base/
```

## Components

### 1. DashboardMetadataOrchestrator

**File**: `scripts/orchestrator.py`

**Purpose**: Iterates through a list of dashboard IDs and calls the existing `extract_dashboard_with_timing()` function for each dashboard independently.

**Features**:
- Processes dashboards sequentially
- Tracks success/failure for each dashboard
- Continues processing on error (configurable)
- Verifies output files are generated

**Usage**:
```python
from orchestrator import DashboardMetadataOrchestrator

orchestrator = DashboardMetadataOrchestrator(
    dashboard_ids=[842, 729, 100],
    continue_on_error=True
)
results = orchestrator.extract_all()
```

**Output**: 
- Individual dashboard metadata files in `extracted_meta/{dashboard_id}/`
- Results dictionary with status for each dashboard

### 2. MetadataMerger

**File**: `scripts/merger.py`

**Purpose**: Merges metadata from multiple dashboards into unified metadata files using LLM-based consolidation.

**Features**:
- LLM-based merging for each metadata type
- Conflict detection and reporting
- Intelligent conflict resolution
- Preserves all unique information

**Metadata Types Merged**:
1. **Table Metadata**: Merges table descriptions, refresh frequencies, verticals, partition columns
2. **Column Metadata**: Merges column descriptions, variable types, required flags
3. **Joining Conditions**: Preserves all unique join patterns (doesn't merge different joins)
4. **Term Definitions**: Identifies and merges synonyms, unifies definitions
5. **Filter Conditions**: Concatenates filter conditions from all dashboards

**DSPy Signatures**:
- `TableMetadataMerger`: Merges table metadata with conflict detection
- `ColumnMetadataMerger`: Merges column metadata with conflict detection
- `JoiningConditionMerger`: Preserves all unique join conditions
- `TermDefinitionMerger`: Merges terms and identifies synonyms

**Conflict Resolution Rules**:
- **Most Common Wins**: For categorical fields (refresh_frequency, vertical, variable_type)
- **Any Required = Required**: For required_flag, if any dashboard marks it as required
- **Merge Descriptions**: Combine descriptions from all dashboards
- **Preserve All Joins**: Don't merge different join conditions
- **Merge Synonyms**: Group terms that refer to the same concept

**Usage**:
```python
from merger import MetadataMerger

merger = MetadataMerger(
    dashboard_ids=[842, 729, 100],
    api_key=api_key,
    model=model,
    base_url=base_url
)
merged_summary = merger.merge_all()
```

**Output**:
- `extracted_meta/merged_metadata/consolidated_table_metadata.csv`
- `extracted_meta/merged_metadata/consolidated_columns_metadata.csv`
- `extracted_meta/merged_metadata/consolidated_joining_conditions.csv`
- `extracted_meta/merged_metadata/consolidated_definitions.csv`
- `extracted_meta/merged_metadata/consolidated_filter_conditions.txt`
- `extracted_meta/merged_metadata/conflicts_report.json`
- `extracted_meta/merged_metadata/merged_metadata.json`

### 3. KnowledgeBaseBuilder

**File**: `scripts/knowledge_base_builder.py`

**Purpose**: Converts merged metadata into a knowledge base format suitable for LLM context injection, documentation, and business user reference.

**Features**:
- Creates structured JSON knowledge base
- Generates markdown documentation
- Creates searchable index
- Organizes by component (tables, columns, joins, definitions, filters)

**Usage**:
```python
from knowledge_base_builder import KnowledgeBaseBuilder

kb_builder = KnowledgeBaseBuilder()
unified_kb = kb_builder.build_from_merged_metadata()
```

**Output**:
- `extracted_meta/knowledge_base/unified_knowledge_base.json`
- `extracted_meta/knowledge_base/knowledge_base.md`
- `extracted_meta/knowledge_base/search_index.json`
- `extracted_meta/knowledge_base/tables_knowledge_base.json`
- `extracted_meta/knowledge_base/columns_knowledge_base.json`
- `extracted_meta/knowledge_base/joins_knowledge_base.json`
- `extracted_meta/knowledge_base/definitions_knowledge_base.json`
- `extracted_meta/knowledge_base/filter_conditions_knowledge_base.txt`

## Main Entry Point

**File**: `scripts/process_multiple_dashboards.py`

**Purpose**: Orchestrates the complete workflow: extract → merge → build KB

**Usage**:
```bash
# Process multiple dashboards
python scripts/process_multiple_dashboards.py 842 729 100

# Skip extraction (if already done)
python scripts/process_multiple_dashboards.py 842 729 100 --skip-extract

# Only merge (skip KB build)
python scripts/process_multiple_dashboards.py 842 729 100 --skip-kb

# Stop on error
python scripts/process_multiple_dashboards.py 842 729 100 --stop-on-error
```

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

## Conflict Detection

The merger detects and reports conflicts in:

1. **Table Metadata**:
   - Different table descriptions
   - Different refresh frequencies
   - Different verticals
   - Different partition columns

2. **Column Metadata**:
   - Different column descriptions
   - Different variable types
   - Different required flags

3. **Joining Conditions**:
   - Multiple different join conditions for same table pair

4. **Term Definitions**:
   - Same term with different definitions
   - Term type conflicts
   - Synonym relationships

Conflicts are reported in `conflicts_report.json` with:
- Field name
- Conflicting values
- Dashboard IDs where conflicts occur
- Resolution approach used

## System Prompts for Merging

Each metadata type has a dedicated DSPy signature with a detailed system prompt:

1. **TableMetadataMerger**: Merges table descriptions, resolves refresh frequency, vertical, partition column conflicts
2. **ColumnMetadataMerger**: Merges column descriptions, resolves variable type and required flag conflicts
3. **JoiningConditionMerger**: Preserves all unique join patterns, merges remarks for identical joins
4. **TermDefinitionMerger**: Identifies synonyms, merges definitions, resolves type conflicts

All prompts follow the same structure:
- Objective
- Input format
- Output requirements
- Conflict resolution rules
- Critical instructions (DO/DON'T)

## Example Workflow

```bash
# Step 1: Extract metadata for each dashboard
python scripts/process_multiple_dashboards.py 842 729 100

# This will:
# 1. Extract metadata for dashboards 842, 729, 100
# 2. Merge all metadata into consolidated files
# 3. Build knowledge base from merged metadata

# Step 2: Review conflicts (if any)
cat extracted_meta/merged_metadata/conflicts_report.json

# Step 3: Use knowledge base
# - For LLM context injection: use unified_knowledge_base.json
# - For documentation: use knowledge_base.md
# - For search: use search_index.json
```

## Error Handling

- **Extraction Errors**: Configurable to continue or stop on error
- **Merge Errors**: Falls back to first entry if LLM merge fails
- **KB Build Errors**: Continues with available components

## Performance Considerations

- **LLM Calls**: Each merge operation requires LLM calls (can be slow for many dashboards)
- **Context Windows**: Claude Sonnet 4 supports 200K tokens (sufficient for 10+ dashboards)
- **Batching**: Consider batching for 20+ dashboards

## Future Enhancements

1. Parallel dashboard extraction
2. Incremental merging (merge new dashboard into existing merged metadata)
3. Version control for merged metadata
4. Advanced conflict resolution strategies
5. Knowledge base query interface

