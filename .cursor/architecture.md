# MetaMind System Architecture

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        React Frontend (Port 3000)                 │
│  ┌────────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Business Vertical  │  │  Superset Tab    │  │  Dashboard   │ │
│  │    Selector        │→ │  (Dashboard      │→ │   Section    │ │
│  │                    │  │   Selection)     │  │  (Progress)  │ │
│  └────────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────┬────────────────────────────────────┘
                              │ HTTP/REST (Axios)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ API Endpoints│→│ Orchestrator │→│ Progress Tracker       │ │
│  │ (REST API)  │  │ (Multi-dash) │  │ (Thread-safe state)    │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
└────┬──────────────────┬──────────────────┬──────────────────────┘
     │                  │                  │
     ▼                  ▼                  ▼
┌──────────┐      ┌──────────┐      ┌──────────────┐
│ Superset │      │  Trino/  │      │  Claude LLM  │
│   API    │      │Starburst │      │  (via DSPy)  │
│          │      │  (via    │      │   Internal   │
│  - Auth  │      │ Superset)│      │    Proxy     │
│  - Dash  │      └──────────┘      └──────────────┘
│  - Charts│
└──────────┘
     │
     ▼
┌────────────────────────────────────────┐
│       File System (extracted_meta/)    │
│  - {dashboard_id}/                     │
│  - merged_metadata/                    │
│  - knowledge_base/                     │
│  - progress.json                       │
└────────────────────────────────────────┘
```

## Processing Pipeline

```
User Selects Vertical/Sub-Vertical
           │
           ▼
   Filter Dashboards by Tags
    (Superset tags API)
           │
           ▼
   User Selects Dashboards
           │
           ▼
   Click "Start Extraction"
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│Dash 476│   │Dash 511│ ... (Parallel Processing)
└────┬───┘   └────┬───┘
     │            │
     ▼            ▼
┌─────────────────────────────────────┐
│ Phase 1: Dashboard Extraction        │
│  - Superset API calls               │
│  - Export JSON/CSV/SQL              │
│  - Files: json, csv, queries.sql    │
│  - Duration: ~5-30 seconds          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 2: LLM Table/Column Extraction │
│  - DSPy + Claude Sonnet 4           │
│  - Chart-by-chart processing        │
│  - Files: tables_columns.csv        │
│  - Duration: ~1-3 minutes           │
│  - Progress: X/Y charts processed   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 3: Trino Schema Enrichment     │
│  - DESCRIBE queries via Superset    │
│  - Add column datatypes             │
│  - Files: tables_columns_enriched   │
│  - Duration: ~30-60 seconds         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 4: Table Metadata (LLM)        │
│  - Generate table descriptions      │
│  - Files: table_metadata.csv        │
│  - Duration: ~2-4 minutes           │
│  - Progress: X/Y charts processed   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 5: Column Metadata (LLM)       │
│  - Generate column descriptions     │
│  - Files: columns_metadata.csv      │
│  - Duration: ~2-4 minutes           │
│  - Progress: X/Y charts processed   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 6: Joining Conditions (LLM)    │
│  - Extract table relationships      │
│  - Files: joining_conditions.csv    │
│  - Duration: ~1-2 minutes           │
│  - Progress: X/Y charts processed   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 7: Filter Conditions (LLM)     │
│  - Extract filter logic             │
│  - Files: filter_conditions.txt     │
│  - Duration: ~1-2 minutes           │
│  - Progress: X/Y charts processed   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 8: Term Definitions (LLM)      │
│  - Extract metrics, KPIs            │
│  - Files: definitions.csv           │
│  - Duration: ~1-2 minutes           │
│  - Progress: X/Y charts processed   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 9: Metadata Merge (Optional)   │
│  - Consolidate all dashboards       │
│  - LLM-based conflict resolution    │
│  - Files: consolidated_*.csv        │
│  - Duration: ~3-5 minutes           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 10: Knowledge Base (Optional)  │
│  - Convert to KB format             │
│  - Create ZIP archive               │
│  - Files: knowledge_base.zip        │
│  - Duration: ~10-30 seconds         │
└─────────────────────────────────────┘
```

## Component Architecture

### Backend Components

```
scripts/
├── api_server.py           # FastAPI Server
│   ├── Endpoints           # REST API routes
│   ├── Background Tasks    # Async processing
│   └── CORS & Middleware   # Request handling
│
├── orchestrator.py         # Multi-Dashboard Orchestrator
│   ├── extract_all()       # Parallel processing
│   ├── _extract_single()   # Per-dashboard extraction
│   └── ThreadPoolExecutor  # Thread pool
│
├── progress_tracker.py     # Progress State Manager
│   ├── ProgressTracker     # Thread-safe singleton
│   ├── update_status()     # Update dashboard status
│   ├── add_completed_file()# Track file completion
│   └── get_progress()      # Get current state
│
├── query_extract.py        # Superset API Client
│   ├── SupersetExtractor   # Main extractor class
│   ├── extract_dashboard() # Dashboard metadata
│   ├── extract_chart()     # Chart metadata
│   └── get_dashboards_by_tags()  # Tag-based filtering
│
├── llm_extractor.py        # LLM Extraction (DSPy)
│   ├── DSPy Signatures     # Structured LLM I/O
│   ├── extract_tables()    # Table/column extraction
│   └── Chart-level funcs   # Per-chart processing
│
├── chart_level_extractor.py  # Chart Processing
│   ├── process_charts_for_table_metadata()
│   ├── process_charts_for_column_metadata()
│   ├── merge_chart_*()     # Merge chart results
│   └── ThreadPoolExecutor  # Parallel LLM calls
│
├── trino_client.py         # Trino/Starburst Client
│   ├── get_column_datatypes()  # DESCRIBE queries
│   └── Via Superset SQL Lab    # No direct connection
│
├── merger.py               # Metadata Merger (LLM)
│   ├── MetadataMerger      # Main merger class
│   ├── merge_*_metadata()  # Per-type merging
│   ├── DSPy Signatures     # Conflict resolution
│   └── _detect_conflicts() # Conflict detection
│
└── knowledge_base_builder.py  # KB Generator
    ├── KnowledgeBaseBuilder
    ├── convert_to_kb()     # Format conversion
    └── create_zip()        # Compress archive
```

### Frontend Components

```
frontend/src/
├── App.js                  # Main Application
│   ├── State: selectedVertical
│   ├── State: selectedSubVertical
│   └── Passes to children
│
├── components/
│   ├── BusinessVertical.js  # Vertical Selector
│   │   ├── Vertical buttons (UPI, Merchant, etc.)
│   │   ├── Sub-vertical buttons (UPI Growth, etc.)
│   │   └── Triggers dashboard filtering
│   │
│   ├── SupersetTab.js      # Dashboard Selection
│   │   ├── Fetches dashboards by tags
│   │   ├── Dashboard dropdown (multi-select)
│   │   ├── Manual ID input (fallback)
│   │   ├── "Start Extraction" button
│   │   └── Progress display
│   │
│   └── DashboardSection.js  # Progress Display
│       ├── Per-dashboard section
│       ├── Metadata cards (independent polling)
│       ├── File status (checking/processing/completed)
│       ├── Download buttons
│       └── File viewer
│
└── services/
    └── api.js              # API Client
        ├── Axios instance (with interceptors)
        ├── dashboardAPI methods
        ├── Progress polling
        └── Error handling
```

## Data Flow: Tag-Based Dashboard Selection

```
1. User Selects Vertical (e.g., "UPI")
   └─> App.js: setSelectedVertical('upi')
       └─> BusinessVertical.js: highlight UPI button
           └─> Show sub-verticals for UPI

2. User Selects Sub-Vertical (e.g., "UPI Growth")
   └─> App.js: setSelectedSubVertical('UPI Growth')
       └─> SupersetTab.js: useEffect triggers
           └─> dashboardAPI.getDashboardsByVertical('upi', 'UPI Growth')

3. Backend: POST /api/dashboards/by-vertical
   └─> instruction_set_generator.get_tags_for_vertical('upi', 'UPI Growth')
       └─> Returns: ['UPI Growth']  # Only sub-vertical if provided
   └─> query_extract.SupersetExtractor.get_dashboards_by_tags(['UPI Growth'])
       └─> Fetches all Superset dashboards
       └─> Filters: dashboard.tags contains 'upi growth' (lowercase match)
       └─> Returns: [{id: 476, title: "...", url: "...", tags: [...]}, ...]

4. Frontend: Display Filtered Dashboards
   └─> SupersetTab.js: setAvailableDashboards(response.dashboards)
       └─> Dropdown shows: "476: UPI Profile wise MAU Distribution" etc.
       └─> User can select one or multiple

5. User Clicks "Start Extraction"
   └─> POST /api/dashboards/process-multiple
       └─> Orchestrator processes selected dashboards
```

## Thread Safety & Concurrency

### Backend Threading Model

```
Main Thread (FastAPI)
    │
    ├─> Request Handler Thread
    │   └─> Creates background thread for LLM work
    │
    └─> Background Thread Pool
        ├─> Dashboard 1 Extraction Thread
        │   └─> Calls extract_dashboard_with_timing()
        │       ├─> Phase 1-3: Sequential
        │       └─> Phase 4-8: Parallel chart processing
        │           └─> ThreadPoolExecutor (5 workers)
        │               ├─> Chart 1 LLM call
        │               ├─> Chart 2 LLM call
        │               └─> Chart N LLM call
        │
        ├─> Dashboard 2 Extraction Thread
        └─> Dashboard N Extraction Thread
```

### Thread-Safe Components

**ProgressTracker** (`progress_tracker.py`):
- Uses `threading.Lock()` for all state modifications
- Singleton pattern ensures single instance
- Writes to `progress.json` atomically

**File I/O**:
- Each dashboard writes to separate directory
- No shared file writes during extraction
- Merge phase is sequential (no conflicts)

## Error Handling Strategy

### Continue-on-Error (Multi-Dashboard)
- Individual dashboard failure doesn't stop others
- Status marked as 'error' in progress.json
- Error details logged to logs/api_server_*.log

### Rollback Strategy
- No rollback needed (files are append-only)
- Partial files remain for debugging
- User can re-run extraction for failed dashboards

### User Feedback
- Real-time progress updates via polling
- Status messages show current phase
- Error messages displayed in UI
- Download buttons disabled if file not available

## Performance Characteristics

### Single Dashboard (~20 charts)
- Phase 1 (Extraction): 10-20 seconds
- Phase 2 (LLM Tables): 2-3 minutes
- Phase 3 (Trino): 30-60 seconds
- Phase 4-8 (LLM Metadata): 8-12 minutes
- **Total**: ~12-16 minutes

### Multi-Dashboard (3 dashboards, parallel)
- Extraction: Same as single (parallel)
- Phase 9 (Merge): 3-5 minutes
- Phase 10 (KB Build): 10-30 seconds
- **Total**: ~15-20 minutes

### Optimization Points
- Parallel chart processing (5 workers)
- DSPy caching (reduces redundant LLM calls)
- Incremental merge (reuse existing metadata)
- Background processing (non-blocking API)

## Security & Authentication

### Superset Authentication
- Session cookie (`session`) in headers
- CSRF token (`X-CSRFToken`) in headers
- Stored in `scripts/config.py` (not committed)
- Refresh required when session expires

### LLM API Authentication
- Anthropic API key via environment variable
- Internal proxy for corporate network
- No key storage in code

### Frontend-Backend
- CORS enabled for localhost:3000
- No authentication (internal tool)
- File access restricted to extracted_meta/

## Scalability Considerations

### Current Limitations
- LLM API rate limits (~50 req/min)
- Single server (no horizontal scaling)
- In-memory progress tracking (resets on restart)

### Future Improvements
- Redis for distributed progress tracking
- Queue-based processing (Celery/RQ)
- Database for metadata storage
- Multiple backend instances

## Monitoring & Logging

### Logs Location
- `logs/api_server_{timestamp}.log` - Backend logs
- Progress tracking: `extracted_meta/progress.json`

### What's Logged
- API requests (POST only, excludes polling)
- Errors and exceptions with stack traces
- Processing start/completion messages
- Per-phase timing information
- LLM API call count and duration

### Log Retention
- Logs rotate by timestamp (one file per server start)
- No automatic cleanup (manual deletion)
- Debug level can be set via environment variable




