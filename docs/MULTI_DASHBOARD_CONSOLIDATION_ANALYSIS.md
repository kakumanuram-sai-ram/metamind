# Multi-Dashboard Consolidation Analysis

## Current Architecture Overview

### Single Dashboard Processing Model
All current DSPy signatures and extraction functions are designed to process **one dashboard at a time**:

1. **Input**: `dashboard_info: Dict` - Single dashboard JSON
2. **Processing**: Charts within that dashboard
3. **Output**: Metadata files per dashboard ID

### Current DSPy Signatures

#### 1. `SourceTableColumnExtractor`
- **Input**: Single SQL query + chart metadata
- **Scope**: Chart-level extraction
- **Consolidation**: None (processes each chart independently)

#### 2. `TableMetadataExtractor`
- **Input**: Single dashboard title, chart names/labels, table info
- **Scope**: Table-level, but only sees one dashboard's context
- **Consolidation**: None across dashboards

#### 3. `ColumnMetadataExtractor`
- **Input**: Column name, table name, chart labels/aliases from one dashboard
- **Scope**: Column-level within single dashboard
- **Consolidation**: None across dashboards

#### 4. `JoiningConditionExtractor`
- **Input**: Two tables, SQL query, chart name, dashboard title
- **Scope**: Chart-level join conditions
- **Consolidation**: None across dashboards

#### 5. `FilterConditionsExtractor`
- **Input**: Chart name, metrics, SQL query, filters, tables, dashboard title
- **Scope**: Chart-level filter documentation
- **Consolidation**: ✅ **YES - Within dashboard** (consolidates similar charts in same dashboard)
- **Multi-dashboard**: ❌ No - only sees `all_charts_context` from one dashboard

#### 6. `TermDefinitionExtractor`
- **Input**: Dashboard title, chart names/labels, SQL queries, metrics context
- **Scope**: Dashboard-level term extraction
- **Consolidation**: ✅ **YES - Within dashboard** (identifies synonyms, categories)
- **Multi-dashboard**: ❌ No - only processes one dashboard's terms

## Can Multi-Dashboard Consolidation Work?

### ✅ **YES - With Modifications**

The system prompts and LLM capabilities **CAN** handle multi-dashboard consolidation, but the **current architecture needs changes**.

### Current Capabilities That Support Multi-Dashboard

1. **FilterConditionsExtractor** already has consolidation logic:
   - Consolidates 3+ similar charts within a dashboard
   - Uses `all_charts_context` to detect redundancy
   - **Could be extended** to accept multiple dashboards' charts

2. **TermDefinitionExtractor** identifies synonyms and categories:
   - Already groups related terms
   - **Could be extended** to identify cross-dashboard synonyms

3. **System Prompts** are flexible:
   - They accept JSON context (could include multiple dashboards)
   - They have consolidation instructions
   - They can handle larger context windows

### What Needs to Change

#### 1. Function Signatures
**Current:**
```python
def extract_table_metadata_llm(
    dashboard_info: Dict,  # Single dashboard
    ...
)
```

**Needed:**
```python
def extract_table_metadata_llm(
    dashboards_info: List[Dict],  # Multiple dashboards
    ...
)
```

#### 2. DSPy Signature Inputs
**Current:**
```python
dashboard_title: str = dspy.InputField(...)  # Single title
chart_names_and_labels: str = dspy.InputField(...)  # Single dashboard's charts
```

**Needed:**
```python
dashboard_titles: str = dspy.InputField(...)  # Multiple titles
all_charts_across_dashboards: str = dspy.InputField(...)  # All charts from all dashboards
```

#### 3. Consolidation Logic
**Current:**
- Consolidates charts within one dashboard
- Uses regex pattern matching: `(Payee Psp = HDFC)` → group by base name

**Needed:**
- Consolidate across dashboards
- Identify:
  - Same tables used across dashboards
  - Same metrics with different names
  - Same calculation patterns
  - Cross-dashboard synonyms

#### 4. Context Window Management
**Current:**
- Processes ~6 charts per dashboard
- Context size: ~5-10K tokens per call

**For 10+ dashboards:**
- Could be 50-100+ charts
- Context size: ~50-200K tokens
- **Solution**: Batch processing or hierarchical consolidation

## Recommended Approach for Multi-Dashboard Consolidation

### Option 1: Two-Phase Consolidation (Recommended)

**Phase 1: Per-Dashboard Extraction** (Current - Keep as-is)
- Extract metadata for each dashboard individually
- Save per-dashboard files

**Phase 2: Cross-Dashboard Consolidation** (New)
- Load all dashboard metadata files
- Create new DSPy signatures for consolidation:
  - `CrossDashboardTableConsolidator`
  - `CrossDashboardTermConsolidator`
  - `CrossDashboardFilterConsolidator`

**Benefits:**
- ✅ Reuses existing single-dashboard logic
- ✅ Can process dashboards in parallel
- ✅ Consolidation is separate, testable phase
- ✅ Can handle large numbers of dashboards

### Option 2: Single-Pass Multi-Dashboard (More Complex)

**Modify existing functions to accept:**
```python
def extract_table_metadata_llm(
    dashboards_info: List[Dict],  # All dashboards at once
    ...
)
```

**Challenges:**
- Large context windows (10+ dashboards = 100+ charts)
- Token limits
- More complex prompts
- Harder to debug

## System Prompt Analysis

### Current Prompts Support Multi-Dashboard Context

#### FilterConditionsExtractor
- ✅ Has `all_charts_context` input field
- ✅ Has consolidation rules ("MANDATORY: Consolidate if 3+ charts...")
- ✅ Can accept JSON with multiple dashboards' charts
- **Modification needed**: Update prompt to say "across dashboards" not just "within dashboard"

#### TermDefinitionExtractor
- ✅ Processes all charts from dashboard
- ✅ Identifies synonyms and categories
- ✅ Can handle larger context
- **Modification needed**: Accept multiple dashboards' charts, identify cross-dashboard synonyms

#### TableMetadataExtractor
- ✅ Uses dashboard title and chart context
- ✅ Can see multiple charts' usage of same table
- **Modification needed**: Accept multiple dashboard titles, consolidate table descriptions

## Specific Recommendations

### For Term Definitions (Most Ready)
**Current**: `TermDefinitionExtractor` already processes all charts from one dashboard

**Enhancement**:
1. Modify input to accept `List[Dict]` of dashboards
2. Update prompt: "Analyze charts from multiple dashboards to identify..."
3. Add instruction: "Identify synonyms across dashboards (e.g., 'Txns' in Dashboard A = 'Transactions' in Dashboard B)"
4. Consolidate duplicate terms automatically

**Feasibility**: ✅ **HIGH** - Minimal changes needed

### For Filter Conditions (Partially Ready)
**Current**: Consolidates within dashboard

**Enhancement**:
1. Extend `all_charts_context` to include charts from all dashboards
2. Update consolidation rules: "Consolidate if 3+ charts across ANY dashboards..."
3. Add dashboard source tracking: "Used in: Dashboard A, Dashboard B, Dashboard C"

**Feasibility**: ✅ **MEDIUM** - Needs context management

### For Table Metadata (Needs More Work)
**Current**: One table = one metadata entry per dashboard

**Enhancement**:
1. Group tables across dashboards
2. Merge descriptions: "This table is used in X dashboards for..."
3. Consolidate refresh_frequency, vertical, partition_column
4. Merge relationship_context across dashboards

**Feasibility**: ⚠️ **MEDIUM-HIGH** - Needs aggregation logic

### For Column Metadata (Needs More Work)
**Current**: One column = one definition per dashboard

**Enhancement**:
1. Group same columns across dashboards
2. Merge descriptions from multiple usage contexts
3. Identify cross-dashboard aliases

**Feasibility**: ⚠️ **MEDIUM** - Similar to table metadata

## Implementation Complexity

### Low Complexity (Easy to Add)
- ✅ Term definitions consolidation
- ✅ Filter conditions cross-dashboard consolidation
- ✅ Joining conditions (if same tables appear in multiple dashboards)

### Medium Complexity
- ⚠️ Table metadata consolidation (need to merge descriptions)
- ⚠️ Column metadata consolidation (need to merge usage contexts)

### High Complexity
- ❌ Tables/columns extraction (Phase 2) - This is per-chart, harder to consolidate

## Token/Context Window Considerations

### Current Usage
- Single dashboard (6 charts): ~5-10K tokens per LLM call
- Filter conditions: ~15K tokens (includes all charts context)

### For 10 Dashboards
- 10 dashboards × 6 charts = 60 charts
- Estimated: ~50-100K tokens per consolidated call
- **Claude Sonnet 4**: Supports up to 200K context window ✅
- **Feasible**: Yes, but may need batching for very large sets

## Conclusion

### ✅ **YES, Multi-Dashboard Consolidation is Feasible**

**Key Findings:**

1. **System Prompts Support It**: The prompts are flexible enough to handle multi-dashboard context
2. **Consolidation Logic Exists**: Filter conditions already consolidate within dashboard
3. **LLM Can Handle It**: Context windows are sufficient for 10+ dashboards
4. **Architecture Needs Updates**: Functions need to accept `List[Dict]` instead of single `Dict`

**Recommended Approach:**
- **Phase 1**: Keep current per-dashboard extraction (already working)
- **Phase 2**: Add new consolidation functions that:
  - Load all dashboard metadata files
  - Use enhanced DSPy signatures with multi-dashboard context
  - Generate consolidated outputs

**Easiest to Implement:**
1. Term definitions (already processes all charts)
2. Filter conditions (already has consolidation logic)
3. Table/column metadata (needs more aggregation logic)

**Estimated Effort:**
- Term definitions: 2-4 hours
- Filter conditions: 4-6 hours  
- Table metadata: 6-8 hours
- Column metadata: 6-8 hours


