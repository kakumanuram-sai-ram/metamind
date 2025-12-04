# MetaMind - Technical Architecture & Implementation Document

**Version:** 1.0  
**Date:** December 2024  
**Purpose:** Expert Software Engineer Review  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Technology Stack & Dependencies](#3-technology-stack--dependencies)
4. [Core Components & Implementation Details](#4-core-components--implementation-details)
5. [Processing Pipeline](#5-processing-pipeline)
6. [Data Models & Output Structures](#6-data-models--output-structures)
7. [API Design](#7-api-design)
8. [Frontend Architecture](#8-frontend-architecture)
9. [LLM Integration & DSPy Framework](#9-llm-integration--dspy-framework)
10. [Design Patterns & Architectural Decisions](#10-design-patterns--architectural-decisions)
11. [Concurrency & Thread Safety](#11-concurrency--thread-safety)
12. [Error Handling & Resilience](#12-error-handling--resilience)
13. [Security Considerations](#13-security-considerations)
14. [Performance Characteristics](#14-performance-characteristics)
15. [Areas for Expert Review](#15-areas-for-expert-review)

---

## 1. Executive Summary

### 1.1 Purpose
MetaMind is an intelligent metadata extraction and analysis system designed for Apache Superset dashboards. It leverages Large Language Models (LLMs) to automatically extract, analyze, and consolidate metadata from dashboard SQL queries, transforming raw dashboard configurations into structured, analyzable knowledge bases.

### 1.2 Core Capabilities
- **Automated Extraction**: Fetches dashboard metadata from Superset REST API
- **LLM-Powered Analysis**: Uses Claude Sonnet 4 via DSPy framework to extract tables, columns, relationships, and business context from SQL queries
- **Schema Enrichment**: Integrates with Trino/Starburst to fetch actual column data types
- **Multi-Dashboard Processing**: Parallel extraction and intelligent merging of metadata from multiple dashboards
- **Knowledge Base Generation**: Creates consolidated, LLM-ready knowledge bases for downstream consumption

### 1.3 Business Value
The system eliminates manual documentation of dashboard metadata, providing:
- Automated table/column extraction with business descriptions
- Joining condition documentation
- Filter condition analysis
- Term definitions (metrics, calculated fields, synonyms)
- Unified knowledge bases for LLM context injection

---

## 2. System Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION LAYER                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    React 18 Frontend (Port 3000)                      │   │
│  │  - Styled Components for UI                                           │   │
│  │  - Axios for HTTP                                                     │   │
│  │  - Real-time progress polling                                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ REST/HTTP
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                  FastAPI Server (Port 8000)                           │   │
│  │  - REST API endpoints                                                 │   │
│  │  - Background thread processing                                       │   │
│  │  - CORS middleware                                                    │   │
│  │  - File serving                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                      │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Query Extractor │  │  LLM Extractor  │  │   Metadata Generator        │  │
│  │ (query_extract) │  │ (llm_extractor) │  │ (metadata_generator)        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   SQL Parser    │  │  Trino Client   │  │      Orchestrator           │  │
│  │  (sql_parser)   │  │ (trino_client)  │  │   (orchestrator)            │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │     Merger      │  │   KB Builder    │  │   Progress Tracker          │  │
│  │   (merger.py)   │  │ (knowledge_base)│  │ (progress_tracker)          │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL INTEGRATIONS                                 │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   Superset API  │  │   Trino/Starburst│  │      Claude LLM            │  │
│  │  (REST/HTTP)    │  │   (SQL Lab API) │  │   (via DSPy + Proxy)       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA/STORAGE LAYER                                 │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                  File System (extracted_meta/)                       │    │
│  │  - Per-dashboard folders: {id}/                                      │    │
│  │  - Merged metadata: merged_metadata/                                 │    │
│  │  - Knowledge base: knowledge_base/                                   │    │
│  │  - Progress state: progress.json                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction Flow

```
User Request → API Server → Orchestrator → [
    Query Extractor (Superset API)
    → SQL Parser / LLM Extractor
    → Trino Client (Schema Enrichment)
    → Metadata Generator (LLM-based)
] → Merger (Multi-dashboard) → KB Builder → File Output
```

---

## 3. Technology Stack & Dependencies

### 3.1 Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.11 | Core language |
| Web Framework | FastAPI | 0.104.1 | REST API server |
| ASGI Server | Uvicorn | 0.24.0 | HTTP server |
| Data Validation | Pydantic | 2.5.0 | Request/response models |
| Data Processing | Pandas | 2.1.3 | CSV/DataFrame operations |
| HTTP Client | Requests | 2.31.0 | Superset API calls |
| LLM Framework | DSPy | Latest | Structured LLM interactions |
| File Handling | python-multipart | 0.0.6 | File uploads |

### 3.2 Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| UI Framework | React | 18.2.0 | Component-based UI |
| Styling | Styled Components | 6.1.0 | CSS-in-JS |
| HTTP Client | Axios | 1.6.0 | API communication |
| Routing | React Router DOM | 6.20.0 | Client-side routing |
| Build Tool | Create React App | 5.0.1 | Build configuration |

### 3.3 External Integrations

| Integration | Protocol | Purpose |
|-------------|----------|---------|
| Apache Superset | REST API | Dashboard metadata source |
| Trino/Starburst | SQL via Superset SQL Lab | Column datatype enrichment |
| Claude Sonnet 4 | HTTP via DSPy | LLM-powered analysis |
| Anthropic Proxy | HTTPS | Internal LLM API proxy |

### 3.4 Dependency Analysis

**Core Dependencies (requirements.txt):**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pandas==2.1.3
requests==2.31.0
python-multipart==0.0.6
```

**Implicit Dependencies (via DSPy):**
- `litellm` - LLM abstraction layer
- `dspy-ai` - DSPy framework

**Frontend Dependencies (package.json):**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "axios": "^1.6.0",
  "react-router-dom": "^6.20.0",
  "styled-components": "^6.1.0"
}
```

---

## 4. Core Components & Implementation Details

### 4.1 SupersetExtractor (`query_extract.py`)

**Purpose:** Fetches dashboard metadata from Apache Superset REST API.

**Key Classes:**
```python
@dataclass
class ChartInfo:
    chart_id: int
    chart_name: str
    chart_type: str
    dataset_id: int
    dataset_name: str
    database_name: str
    sql_query: Optional[str]
    metrics: List[Dict[str, Any]]
    columns: List[str]
    groupby_columns: List[str]
    filters: List[Dict[str, Any]]
    time_range: Optional[str]

@dataclass
class DashboardInfo:
    dashboard_id: int
    dashboard_title: str
    dashboard_url: str
    owner: str
    created_on: str
    changed_on: str
    charts: List[ChartInfo]
```

**Key Methods:**
- `extract_dashboard_complete_info(dashboard_id)` - Main extraction entry point
- `get_chart_data_and_query(chart_id, dataset_id)` - Fetches SQL from chart data endpoint
- `get_dashboards_by_tags(tags)` - Filters dashboards by Superset tags
- `export_to_json/csv/sql()` - Output generation

**Implementation Notes:**
- Uses session-based authentication (Cookie + CSRF token)
- Handles both quoted and unquoted table identifiers
- Falls back to dataset SQL if chart data endpoint fails

### 4.2 LLM Extractor (`llm_extractor.py`)

**Purpose:** Uses DSPy framework with Claude Sonnet 4 to extract structured metadata from SQL queries.

**DSPy Signatures Defined:**

| Signature | Purpose | Input Fields | Output Fields |
|-----------|---------|--------------|---------------|
| `TableNameExtractor` | Extract source table names | sql_query | table_names |
| `TableColumnExtractor` | Extract tables & columns | sql_query, chart_metadata | tables_used, original_columns, column_aliases |
| `SourceTableColumnExtractor` | Extract source + derived columns | sql_query, chart_metadata | source_tables, source_columns, derived_columns_mapping |
| `TableMetadataExtractor` | Generate table descriptions | dashboard_title, table_name, table_columns, etc. | table_description, refresh_frequency, vertical, partition_column, remarks |
| `ColumnMetadataExtractor` | Generate column descriptions | column_name, table_name, usage_context | column_description |
| `JoiningConditionExtractor` | Extract JOIN conditions | table1, table2, sql_query | joining_condition, joining_type, remarks |
| `FilterConditionsExtractor` | Document filter logic | chart_name, sql_query, chart_filters | use_case_description, filter_conditions_sql |
| `TermDefinitionExtractor` | Extract business terms | dashboard_title, chart_names_and_labels | term_definitions (JSON array) |

**Rate Limiting Implementation:**
```python
def retry_on_rate_limit(max_retries=5, initial_delay=2.0, max_delay=60.0, backoff_factor=2.0):
    """Decorator with exponential backoff and jitter"""
    # Detects 429 errors and 'rate limit' in error messages
    # Implements exponential backoff: delay *= backoff_factor
    # Adds random jitter to prevent thundering herd
```

**Thread Safety:**
```python
_dspy_lm = None
_dspy_extractor = None
_dspy_lock = threading.Lock()

def _get_dspy_extractor(api_key, model, base_url):
    """Thread-safe DSPy extractor initialization"""
    with _dspy_lock:
        if _dspy_extractor is None:
            # Configure DSPy and create extractor
```

### 4.3 SQL Parser (`sql_parser.py`)

**Purpose:** Rule-based SQL parsing as fallback when LLM is unavailable.

**Key Functions:**
- `extract_tables(sql)` - Extracts table names from FROM/JOIN clauses
- `extract_columns(sql, tables)` - Maps columns to tables
- `normalize_table_name(table_name)` - Adds `hive.` prefix if missing
- `extract_table_column_mapping(dashboard_info, trino_columns)` - Main extraction function

**CTE Handling:**
```python
def extract_cte_names(self, sql: str) -> Set[str]:
    """Extract CTE names to exclude from source table list"""
    # Matches: WITH cte_name AS (...)
    # Also handles recursive CTEs: , cte_name AS (...)
```

### 4.4 Trino Client (`trino_client.py`)

**Purpose:** Fetches column data types from Trino/Starburst via Superset SQL Lab API.

**Implementation Approach:**
```python
def get_table_columns(self, table_name: str, database_id: int = 1) -> Dict[str, str]:
    """Execute DESCRIBE query via Superset SQL Lab"""
    query = f'DESCRIBE {catalog}.{schema}.{table}'
    
    response = requests.post(
        self.query_endpoint,  # /api/v1/sqllab/execute/
        json={
            "database_id": database_id,
            "sql": query,
            "runAsync": False
        }
    )
```

**Note:** Does not connect directly to Trino; uses Superset as a proxy.

### 4.5 Orchestrator (`orchestrator.py`)

**Purpose:** Manages extraction of multiple dashboards with parallel processing.

**Key Features:**
- Parallel processing via `ThreadPoolExecutor`
- Progress tracking per dashboard
- Configurable error handling (continue vs. stop on error)
- File completion verification

```python
class DashboardMetadataOrchestrator:
    def __init__(self, dashboard_ids, continue_on_error=True, parallel=True, max_workers=None):
        self.max_workers = max_workers or len(dashboard_ids)
        self.progress_tracker = get_progress_tracker()
        
    def extract_all(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_dashboard = {
                executor.submit(self._extract_single_dashboard, did): did
                for did in self.dashboard_ids
            }
```

### 4.6 Metadata Merger (`merger.py`)

**Purpose:** LLM-based merging of metadata from multiple dashboards with conflict detection.

**Merging DSPy Signatures:**

| Signature | Conflict Resolution Strategy |
|-----------|------------------------------|
| `TableMetadataMerger` | Most common wins for categorical, merge descriptions |
| `ColumnMetadataMerger` | Any required = required, merge descriptions |
| `JoiningConditionMerger` | Preserve ALL unique join patterns |
| `TermDefinitionMerger` | Identify synonyms, merge definitions |

**Conflict Detection:**
```python
def merge_all(self, include_existing_merged=False):
    # Tracks conflicts across all merge operations
    self.all_conflicts = []
    
    # Each merge method adds to self.all_conflicts
    # Final conflicts_report.json generated
```

### 4.7 Knowledge Base Builder (`knowledge_base_builder.py`)

**Purpose:** Converts merged metadata into LLM-friendly knowledge base format.

**Output Files Generated:**
| File | Format | Content |
|------|--------|---------|
| `table_metadata.json` | JSON Array | Table descriptions, refresh frequencies |
| `column_metadata.json` | JSON Array | Column descriptions, types |
| `joining_conditions.json` | JSON Array | Table relationships |
| `definitions.json` | JSON Array | Business term definitions |
| `filter_conditions.txt` | Plain Text | Filter documentation |
| `business_context.json` | JSON Object | Empty template |
| `validations.json` | JSON Object | Empty template |
| `instruction_set.json/txt` | JSON/Text | SQL agent instructions |
| `knowledge_base.zip` | ZIP | All files compressed |

### 4.8 Progress Tracker (`progress_tracker.py`)

**Purpose:** Thread-safe progress tracking for multi-dashboard processing.

**State Machine:**
```
idle → extracting → merging → building_kb → completed
         ↓
       error
```

**Per-Dashboard Progress:**
```python
{
    "dashboard_id": int,
    "status": "pending" | "processing" | "completed" | "error",
    "current_phase": str,
    "current_file": str,
    "completed_files": List[str],
    "total_files": 11,
    "error": Optional[str]
}
```

**Thread Safety:**
```python
class ProgressTracker:
    def __init__(self):
        self.lock = threading.Lock()
    
    def update_dashboard_status(self, ...):
        with self.lock:
            progress = self._read_progress()
            # Update progress
            self._write_progress(progress)
```

---

## 5. Processing Pipeline

### 5.1 Single Dashboard Extraction Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 1: Dashboard Extraction                     │
│                                                                      │
│  Superset API → Dashboard Metadata → Charts → SQL Queries           │
│                                                                      │
│  Output: {id}_json.json, {id}_csv.csv, {id}_queries.sql             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                Phase 2: Table/Column Extraction (LLM)                │
│                                                                      │
│  SQL Queries → DSPy SourceTableColumnExtractor → Tables, Columns    │
│                                                                      │
│  Output: {id}_tables_columns.csv                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Phase 3: Trino Schema Enrichment                       │
│                                                                      │
│  Table Names → Trino DESCRIBE → Column Data Types                   │
│                                                                      │
│  Output: {id}_tables_columns_enriched.csv                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Phase 4-8: Metadata Generation (LLM)                    │
│                                                                      │
│  Phase 4: Table Metadata → {id}_table_metadata.csv                  │
│  Phase 5: Column Metadata → {id}_columns_metadata.csv               │
│  Phase 6: Joining Conditions → {id}_joining_conditions.csv          │
│  Phase 7: Filter Conditions → {id}_filter_conditions.txt            │
│  Phase 8: Term Definitions → {id}_definitions.csv                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Multi-Dashboard Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 1-8: Per-Dashboard Extraction               │
│                         (Parallel Processing)                        │
│                                                                      │
│  Dashboard A ──┐                                                     │
│  Dashboard B ──┼── ThreadPoolExecutor → Per-Dashboard Metadata      │
│  Dashboard C ──┘                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 9: Metadata Consolidation                   │
│                                                                      │
│  Per-Dashboard Files → LLM Merger → Consolidated Files              │
│                                                                      │
│  Output:                                                             │
│  - merged_metadata/consolidated_table_metadata.csv                   │
│  - merged_metadata/consolidated_columns_metadata.csv                 │
│  - merged_metadata/consolidated_joining_conditions.csv               │
│  - merged_metadata/consolidated_definitions.csv                      │
│  - merged_metadata/consolidated_filter_conditions.txt                │
│  - merged_metadata/conflicts_report.json                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Phase 10: Knowledge Base Build                     │
│                                                                      │
│  Consolidated CSVs → JSON Conversion → ZIP Archive                   │
│                                                                      │
│  Output: knowledge_base/knowledge_base.zip                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Data Models & Output Structures

### 6.1 Per-Dashboard Output Files

| File | Format | Schema |
|------|--------|--------|
| `{id}_json.json` | JSON | Complete dashboard metadata (charts, filters, layout) |
| `{id}_csv.csv` | CSV | Tabular chart metadata |
| `{id}_queries.sql` | SQL | All SQL queries |
| `{id}_tables_columns.csv` | CSV | tables_involved, column_names, alias_column_name, source_or_derived, derived_column_logic |
| `{id}_tables_columns_enriched.csv` | CSV | Same + column_datatype |
| `{id}_table_metadata.csv` | CSV | table_name, table_description, refresh_frequency, vertical, partition_column, remarks, relationship_context |
| `{id}_columns_metadata.csv` | CSV | table_name, column_name, variable_type, column_description, required_flag |
| `{id}_joining_conditions.csv` | CSV | table1, table2, joining_condition, remarks |
| `{id}_filter_conditions.txt` | Text | Markdown-formatted filter documentation |
| `{id}_definitions.csv` | CSV | term, type, definition, business_alias |

### 6.2 Progress Tracking Schema

```json
{
  "status": "idle|extracting|merging|building_kb|completed",
  "current_operation": "extraction|merge|kb_build|null",
  "total_dashboards": 3,
  "completed_dashboards": 2,
  "failed_dashboards": 0,
  "dashboards": {
    "476": {
      "dashboard_id": 476,
      "status": "completed|processing|pending|error",
      "current_phase": "Phase 4: Table Metadata",
      "current_file": "476_table_metadata.csv",
      "completed_files": ["476_json.json", "476_csv.csv"],
      "total_files": 11,
      "completed_files_count": 2,
      "error": null,
      "start_time": "2024-12-03T10:30:00",
      "end_time": "2024-12-03T10:35:00"
    }
  },
  "merge_status": {
    "status": "pending|processing|completed",
    "current_step": "table_metadata",
    "completed_steps": ["table_metadata", "columns_metadata"]
  },
  "kb_build_status": {
    "status": "pending|processing|completed",
    "current_step": "tables"
  },
  "start_time": "2024-12-03T10:30:00",
  "last_update": "2024-12-03T10:35:00"
}
```

---

## 7. API Design

### 7.1 API Endpoints

#### Dashboard Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/dashboards` | List extracted dashboards |
| GET | `/api/dashboard/{id}/json` | Get dashboard JSON |
| GET | `/api/dashboard/{id}/csv` | Get dashboard CSV as JSON |
| GET | `/api/dashboard/{id}/files` | List available metadata files |
| GET | `/api/dashboard/{id}/file/{type}` | Get metadata file content |
| GET | `/api/dashboard/{id}/download/{type}` | Download specific file |
| GET | `/api/dashboard/{id}/download-all` | Download all as ZIP |

#### Extraction & Processing
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/dashboard/extract` | Extract single dashboard |
| POST | `/api/dashboards/process-multiple` | Process multiple dashboards |

#### Vertical-Based Selection
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/verticals` | Get business verticals |
| POST | `/api/dashboards/by-vertical` | Get dashboards by vertical |

#### Progress & Downloads
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/progress` | Get processing progress |
| GET | `/api/knowledge-base/download` | Download KB ZIP |

### 7.2 Request/Response Models

**Multi-Dashboard Request:**
```python
class MultiDashboardRequest(BaseModel):
    dashboard_ids: List[int]
    extract: bool = True
    merge: bool = True
    build_kb: bool = True
    metadata_choices: Optional[Dict[int, bool]] = None  # dashboard_id -> use_existing
```

**Progress Response Structure:**
```json
{
  "status": "extracting",
  "dashboards": {
    "476": {"status": "completed", "current_phase": "Completed"},
    "511": {"status": "processing", "current_phase": "Phase 4"}
  },
  "merge_status": {"status": "pending"},
  "kb_build_status": {"status": "pending"}
}
```

### 7.3 Background Processing Pattern

```python
@app.post("/api/dashboards/process-multiple")
async def process_multiple_dashboards(request: MultiDashboardRequest):
    def run_processing():
        # Long-running extraction/merge/KB build
        process_multiple_dashboards(...)
    
    # Non-blocking: start background thread
    thread = threading.Thread(target=run_processing, daemon=True)
    thread.start()
    
    return {
        "success": True,
        "message": f"Processing {len(request.dashboard_ids)} dashboards",
        "check_progress": "/api/progress"
    }
```

---

## 8. Frontend Architecture

### 8.1 Component Structure

```
src/
├── App.js                      # Root component, tab management
├── components/
│   ├── BusinessVertical.js     # Vertical/sub-vertical selector
│   ├── TabNavigation.js        # Tab switcher (Superset/Docs/Confluence)
│   ├── SupersetTab.js          # Main dashboard extraction UI
│   ├── DashboardSection.js     # Per-dashboard progress display
│   ├── MultiDashboardProcessor.js  # Multi-dashboard form
│   ├── DashboardFileDownloader.js  # File download buttons
│   ├── KnowledgeBaseZipSection.js  # KB download
│   ├── MetadataChoiceModal.js  # Fresh/existing metadata selection
│   ├── CSVViewer.js            # CSV data display
│   └── JSONViewer.js           # JSON data display
├── services/
│   └── api.js                  # Axios API client
└── styles/
    ├── theme.js                # Design tokens
    └── GlobalStyles.js         # Global CSS
```

### 8.2 State Management

**App-Level State:**
```javascript
function App() {
  const [activeTab, setActiveTab] = useState('superset');
  const [selectedVertical, setSelectedVertical] = useState(null);
  const [selectedSubVertical, setSelectedSubVertical] = useState(null);
  
  // Preserved SupersetTab state across tab switches
  const [supersetState, setSupersetState] = useState({
    dashboardIds: '',
    activeDashboardIds: [],
    progress: null,
    statusMessage: null,
    metadataChoices: {},
    existingMetadata: {},
  });
}
```

### 8.3 Progress Polling

```javascript
// Poll every 3 seconds during processing
useEffect(() => {
  if (status === 'processing' || status === 'pending') {
    const pollInterval = setInterval(async () => {
      const progress = await dashboardAPI.getProgress();
      setProgress(progress);
    }, 3000);
    
    return () => clearInterval(pollInterval);
  }
}, [status]);
```

### 8.4 API Client Configuration

```javascript
const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,  // Default timeout
});

// Request timing interceptor
api.interceptors.request.use((config) => {
  config.metadata = { startTime: performance.now() };
  return config;
});

// Response timing interceptor
api.interceptors.response.use((response) => {
  const duration = performance.now() - response.config.metadata.startTime;
  console.log(`[API] ${response.config.url} took ${duration}ms`);
  return response;
});
```

---

## 9. LLM Integration & DSPy Framework

### 9.1 DSPy Overview

DSPy (Declarative Self-improving Python) is a framework for building reliable LLM-based systems. Key concepts used:

- **Signatures**: Declarative input/output specifications
- **ChainOfThought**: Prompts LLM to reason step-by-step
- **Few-shot Examples**: Training examples for better extraction

### 9.2 DSPy Configuration

```python
def _get_dspy_source_extractor(api_key, model, base_url):
    # Configure LLM
    lm = dspy.LM(
        model=f"anthropic/{model}",  # e.g., "anthropic/claude-sonnet-4"
        api_key=api_key,
        api_provider="anthropic",
        api_base=base_url  # Custom proxy URL
    )
    dspy.configure(lm=lm)
    
    # Create extractor
    extractor = dspy.ChainOfThought(SourceTableColumnExtractor)
    
    # Load few-shot examples if available
    from dspy_examples import EXAMPLES
    extractor.demos = EXAMPLES[:5]
    
    return extractor
```

### 9.3 Signature Example

```python
class SourceTableColumnExtractor(dspy.Signature):
    """Extract source tables, columns, and derived column logic from SQL."""
    
    sql_query: str = dspy.InputField(
        desc="SQL query from dashboard chart"
    )
    chart_metadata: str = dspy.InputField(
        desc="Chart metadata including metrics, columns"
    )
    
    source_tables: str = dspy.OutputField(
        desc="Comma-separated source table names"
    )
    source_columns: str = dspy.OutputField(
        desc="Comma-separated original column names"
    )
    derived_columns_mapping: str = dspy.OutputField(
        desc="JSON object mapping alias to {source_column, source_table, logic}"
    )
```

### 9.4 LLM Provider Configuration

```python
# config.py
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'anthropic')

if LLM_PROVIDER == 'truefoundry':
    LLM_MODEL = 'pi-agentic/us-anthropic-claude-sonnet-4-20250514-v1-0'
    LLM_BASE_URL = 'https://tfy.internal.../api/inference/openai'
elif LLM_PROVIDER == 'anthropic':
    LLM_MODEL = 'anthropic/claude-sonnet-4'
    LLM_BASE_URL = 'https://cst-ai-proxy.paytm.com'  # Internal proxy
```

---

## 10. Design Patterns & Architectural Decisions

### 10.1 ADRs Summary

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | LLM-based extraction | More accurate than rule-based for complex SQL |
| ADR-002 | DSPy framework | Declarative signatures, built-in retries |
| ADR-003 | Per-dashboard folders | Isolation, easier debugging |
| ADR-004 | Background processing | Non-blocking API for long-running tasks |
| ADR-005 | Thread-safe progress | File-based JSON with locks |
| ADR-006 | Trino via Superset | Reuses existing auth, no direct DB access |

### 10.2 Key Design Patterns

**1. Facade Pattern** - `api_server.py`
- Provides unified REST interface to complex subsystems
- Hides orchestration, extraction, merging complexity

**2. Strategy Pattern** - Extraction approaches
- LLM-based extraction (primary)
- Rule-based SQL parsing (fallback)

**3. Observer Pattern** - Progress tracking
- Components update shared progress state
- Frontend polls for changes

**4. Singleton Pattern** - DSPy extractors
```python
_dspy_extractor = None
_dspy_lock = threading.Lock()

def _get_dspy_extractor(...):
    global _dspy_extractor
    with _dspy_lock:
        if _dspy_extractor is None:
            _dspy_extractor = dspy.ChainOfThought(...)
    return _dspy_extractor
```

**5. Template Method Pattern** - Metadata generation
- Base flow: Load → Transform → Save
- Variations per metadata type (tables, columns, joins)

### 10.3 Architectural Decisions

**Why FastAPI?**
- Native async support (for future optimization)
- Automatic OpenAPI docs
- Pydantic validation built-in
- Good performance characteristics

**Why File-Based Storage?**
- Simplicity (no database setup)
- Easy debugging (human-readable files)
- Stateless server restarts
- Git-compatible output

**Why Background Threads (not Celery)?**
- Simpler deployment (single process)
- No message broker required
- Sufficient for current scale

---

## 11. Concurrency & Thread Safety

### 11.1 Thread Safety Mechanisms

**1. Global Locks for Shared Resources:**
```python
# progress_tracker.py
class ProgressTracker:
    def __init__(self):
        self.lock = threading.Lock()
    
    def update_dashboard_status(self, ...):
        with self.lock:
            progress = self._read_progress()
            # ... modifications
            self._write_progress(progress)
```

**2. DSPy Configuration Lock:**
```python
# llm_extractor.py
_dspy_lock = threading.Lock()

def _get_dspy_extractor(...):
    with _dspy_lock:
        if _dspy_lm is None:
            dspy.configure(lm=...)  # One-time configuration
```

**3. Global Progress Tracker Singleton:**
```python
_global_tracker = None
_tracker_lock = threading.Lock()

def get_progress_tracker():
    global _global_tracker
    with _tracker_lock:
        if _global_tracker is None:
            _global_tracker = ProgressTracker()
    return _global_tracker
```

### 11.2 Parallel Processing

```python
# orchestrator.py
class DashboardMetadataOrchestrator:
    def extract_all(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_dashboard = {
                executor.submit(self._extract_single_dashboard, did): did
                for did in self.dashboard_ids
            }
            
            for future in as_completed(future_to_dashboard):
                dashboard_id = future_to_dashboard[future]
                try:
                    result = future.result()
                    with self.lock:  # Thread-safe result collection
                        self.results[dashboard_id] = result
                except Exception as e:
                    # Error handling...
```

### 11.3 Potential Concurrency Issues

| Issue | Current Mitigation | Risk Level |
|-------|-------------------|------------|
| DSPy global state | Lock around configuration | Low |
| File I/O race conditions | Single-writer pattern | Medium |
| Progress file corruption | Lock per operation | Low |
| LLM rate limits | Per-request retry | Medium |

---

## 12. Error Handling & Resilience

### 12.1 Rate Limit Handling

```python
def retry_on_rate_limit(max_retries=5, initial_delay=2.0, max_delay=60.0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if '429' in str(e) and attempt < max_retries:
                        actual_delay = delay * (0.5 + random.random())  # Jitter
                        time.sleep(actual_delay)
                        delay = min(delay * 2.0, max_delay)  # Exponential backoff
                    else:
                        raise
        return wrapper
    return decorator
```

### 12.2 Continue-on-Error Pattern

```python
# orchestrator.py
for dashboard_id in self.dashboard_ids:
    try:
        result = self._extract_single_dashboard(dashboard_id)
        self.results[dashboard_id] = result
    except Exception as e:
        self.results[dashboard_id] = {'status': 'error', 'error': str(e)}
        if not self.continue_on_error:
            break  # Stop processing
        # Otherwise continue with next dashboard
```

### 12.3 Fallback Strategies

| Component | Primary | Fallback |
|-----------|---------|----------|
| Table/Column Extraction | LLM (DSPy) | Rule-based SQL Parser |
| Schema Enrichment | Trino via Superset | Skip (continue without types) |
| Chart SQL | Chart Data API | Dataset SQL definition |

### 12.4 Graceful Degradation

```python
# trino_client.py
def get_column_datatypes_from_trino(...):
    try:
        trino_client = TrinoClient(base_url, headers)
        return trino_client.get_columns_for_tables(list(unique_tables))
    except Exception as e:
        print(f"Warning: Trino query failed, continuing without data types")
        return {}  # Empty dict - extraction continues
```

---

## 13. Security Considerations

### 13.1 Authentication Architecture

**Superset Authentication:**
- Session-based (Cookie + CSRF token)
- Credentials stored in environment variables
- No direct database credentials

```python
# config.py
HEADERS = {
    'Cookie': os.getenv('SUPERSET_COOKIE', ''),
    'X-CSRFToken': os.getenv('SUPERSET_CSRF_TOKEN', ''),
}
```

**LLM API Authentication:**
- API key stored in environment variable
- Routed through internal proxy

```python
LLM_API_KEY = os.getenv('LLM_API_KEY', '') or os.getenv('ANTHROPIC_API_KEY', '')
```

### 13.2 Security Concerns

| Area | Current State | Recommendation |
|------|--------------|----------------|
| API Authentication | None (localhost only) | Add JWT/API key auth for production |
| CORS | Allow all origins (`*`) | Restrict to specific domains |
| Session Management | Manual cookie refresh | Implement OAuth flow |
| Input Validation | Pydantic models | Add SQL injection checks |
| Logging | Full requests logged | Redact sensitive data |

### 13.3 Data Sensitivity

**Potentially Sensitive Data:**
- SQL queries (may contain business logic)
- Table/column names (schema exposure)
- Dashboard structure (business intelligence)

**Current Controls:**
- All data stored locally (file system)
- No external data transmission except to configured APIs
- LLM calls go through internal proxy

---

## 14. Performance Characteristics

### 14.1 Typical Processing Times

| Phase | Time (per dashboard) | Factors |
|-------|---------------------|---------|
| Dashboard Extraction | 30-60 seconds | # of charts, Superset latency |
| LLM Table/Column | 2-5 seconds/chart | SQL complexity |
| Trino Schema | 5-10 seconds/table | # of tables |
| LLM Metadata | 5-10 seconds/table | LLM latency |
| Merge (multi-dashboard) | 10-30 seconds | # of entities |
| KB Build | 5-10 seconds | File I/O |

**Total for 3 dashboards (typical):** 10-20 minutes

### 14.2 Scalability Considerations

**Horizontal Scaling:**
- Currently single-process
- Progress file limits multi-instance deployment
- Recommendation: Use Redis/DB for shared state

**Vertical Scaling:**
- Parallel dashboard extraction (ThreadPoolExecutor)
- Sequential LLM calls (rate limits prevent parallelism)
- Memory: ~500MB for typical workloads

### 14.3 Bottlenecks

| Bottleneck | Impact | Mitigation |
|------------|--------|------------|
| LLM API Rate Limits | 429 errors | Exponential backoff, jitter |
| Superset Chart Data API | Slow response | Timeout handling |
| Sequential LLM Calls | Long total time | Future: Batch requests |
| File I/O Locks | Contention | Minimal (fast operations) |

---

## 15. Areas for Expert Review

### 15.1 Architecture Review Questions

1. **DSPy Framework Choice:**
   - Is DSPy the right choice for structured LLM extraction?
   - Alternative frameworks: LangChain, Instructor, Marvin?
   - Trade-offs with simpler prompt engineering?

2. **Thread-Based Background Processing:**
   - Should we migrate to Celery/RQ for task queues?
   - Benefits: Better monitoring, retry policies, scaling
   - Trade-offs: Complexity, infrastructure requirements

3. **File-Based State Management:**
   - Is progress.json appropriate for production?
   - Should we use Redis/PostgreSQL for state?
   - Concerns: Multi-instance, crash recovery

4. **API Design:**
   - Is background processing the right pattern for extraction?
   - Should we use WebSockets for real-time progress?
   - Rate limiting / throttling considerations?

### 15.2 Code Quality Concerns

1. **Global State:**
   - Multiple global singletons (`_dspy_lm`, `_global_tracker`)
   - Thread locks for initialization
   - Alternative: Dependency injection?

2. **Error Handling:**
   - Broad exception catches in some areas
   - Error messages not always structured
   - Missing error codes/categories

3. **Test Coverage:**
   - Limited unit tests
   - No integration tests
   - No mocking of external services

### 15.3 LLM-Specific Concerns

1. **Prompt Stability:**
   - Long prompts in DSPy signatures
   - Version control for prompts?
   - Prompt testing/evaluation?

2. **Output Parsing:**
   - JSON parsing of LLM outputs
   - Handling malformed responses
   - Fallback strategies?

3. **Cost Management:**
   - No token counting
   - No cost estimation
   - No budget limits

### 15.4 Operational Concerns

1. **Monitoring:**
   - Logging present but basic
   - No metrics collection
   - No alerting

2. **Deployment:**
   - Manual scripts (start_backend.sh)
   - No containerization (Docker)
   - No CI/CD pipeline defined

3. **Documentation:**
   - Good inline comments
   - API docs via FastAPI/OpenAPI
   - Missing: Runbook, troubleshooting guide

### 15.5 Specific Code Review Items

**File: `llm_extractor.py`**
- Lines 147-548: DSPy signatures very long, embedded prompts
- Lines 606-712: Complex thread-safe initialization
- Consider: Extract prompts to separate files?

**File: `merger.py`**
- Lines 35-297: Similar DSPy signature patterns
- Lines 522-700: Deep nesting in merge methods
- Consider: Extract common merge logic?

**File: `api_server.py`**
- Lines 554-687: Long `process_multiple_dashboards` function
- Lines 89-118: Custom logging middleware
- Consider: Use structured logging (JSON)?

---

## Appendix A: Environment Variables

```bash
# Superset Authentication
SUPERSET_BASE_URL=https://cdp-dataview.platform.mypaytm.com
SUPERSET_COOKIE="session=..."
SUPERSET_CSRF_TOKEN="..."

# LLM Configuration
LLM_PROVIDER=anthropic  # or truefoundry
LLM_API_KEY="..."
LLM_MODEL=anthropic/claude-sonnet-4
LLM_BASE_URL=https://cst-ai-proxy.paytm.com

# Processing Settings
MAX_CONCURRENT_DASHBOARDS=5
ENABLE_LLM_EXTRACTION=true
ENABLE_TRINO_ENRICHMENT=true

# Output
BASE_DIR=extracted_meta
LOG_LEVEL=INFO
```

---

## Appendix B: File Structure

```
metamind/
├── scripts/                      # Python backend
│   ├── api_server.py             # FastAPI REST API (1220 lines)
│   ├── config.py                 # Configuration (144 lines)
│   ├── query_extract.py          # Superset extraction (726 lines)
│   ├── sql_parser.py             # Rule-based parsing (625 lines)
│   ├── llm_extractor.py          # DSPy extraction (2232 lines)
│   ├── trino_client.py           # Schema enrichment (161 lines)
│   ├── metadata_generator.py     # Metadata files
│   ├── orchestrator.py           # Multi-dashboard (295 lines)
│   ├── merger.py                 # LLM-based merging (1102 lines)
│   ├── knowledge_base_builder.py # KB generation (327 lines)
│   └── progress_tracker.py       # Progress state (297 lines)
│
├── frontend/                     # React frontend
│   └── src/
│       ├── App.js                # Root component (147 lines)
│       ├── components/           # UI components
│       │   ├── SupersetTab.js    # Main extraction UI
│       │   ├── DashboardSection.js
│       │   └── ...
│       └── services/
│           └── api.js            # API client (361 lines)
│
├── extracted_meta/               # Output directory
│   ├── {dashboard_id}/           # Per-dashboard
│   ├── merged_metadata/          # Consolidated
│   ├── knowledge_base/           # KB format
│   └── progress.json             # Progress state
│
├── docs/                         # Documentation
│   ├── adrs/                     # Architecture Decision Records
│   └── modules/                  # Module documentation
│
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project metadata
└── README.md                    # Main documentation
```

---

**Document Prepared For:** Expert Software Engineering Review  
**System:** MetaMind - Intelligent Dashboard Metadata Extraction System  
**Codebase Size:** ~12,000 lines Python, ~3,000 lines JavaScript  
**LLM Integration:** DSPy with Claude Sonnet 4 via internal proxy



