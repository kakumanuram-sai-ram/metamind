# MetaMind Current Features

## Dashboard Selection & Filtering

### Business Vertical Selection
- **Verticals**: UPI, Merchant, Lending, Travel, Recharges & Utilities
- **Sub-Verticals**: Each vertical has 2-3 sub-verticals (e.g., UPI → UPI Growth, User Growth)
- **Component**: `frontend/src/components/BusinessVertical.js`
- **State Management**: Managed in `App.js`, passed as props

### Tag-Based Dashboard Filtering
- **Superset Integration**: Fetches dashboards with tags from Superset API
- **Matching Logic**: 
  - Searches by sub-vertical if selected (e.g., "UPI Growth")
  - Falls back to vertical if no sub-vertical (e.g., "UPI")
  - Case-insensitive matching
- **Backend**: `scripts/query_extract.py:get_dashboards_by_tags`
- **Frontend**: `frontend/src/components/SupersetTab.js`

### Multi-Select Dashboard Dropdown
- Displays filtered dashboards with title and URL
- Clickable hyperlinks to Superset
- Multi-select checkbox interface
- Fallback to manual dashboard ID input

## Metadata Extraction

### 8-Phase Processing Pipeline
1. **Phase 1: Dashboard Extraction** (5-30 sec)
   - Fetch from Superset API
   - Export JSON, CSV, SQL files
   
2. **Phase 2: LLM Table/Column Extraction** (1-3 min)
   - Claude Sonnet 4 via DSPy
   - Chart-by-chart processing
   - Extract tables, columns, derived logic
   
3. **Phase 3: Trino Schema Enrichment** (30-60 sec)
   - DESCRIBE queries via Superset
   - Add column datatypes
   
4. **Phase 4: Table Metadata** (2-4 min)
   - Generate table descriptions
   - Identify refresh frequencies, verticals
   
5. **Phase 5: Column Metadata** (2-4 min)
   - Generate column descriptions
   - Classify variable types
   
6. **Phase 6: Joining Conditions** (1-2 min)
   - Extract table relationships
   - Identify join keys
   
7. **Phase 7: Filter Conditions** (1-2 min)
   - Extract filter logic
   - Document WHERE clauses
   
8. **Phase 8: Term Definitions** (1-2 min)
   - Extract business metrics
   - Define KPIs and calculated fields

### Chart-Level Progress Tracking
- Shows "X/Y charts processed" during LLM phases
- Real-time progress updates
- Per-chart timing information in logs

## Multi-Dashboard Processing

### Parallel Extraction
- Process multiple dashboards simultaneously
- ThreadPoolExecutor with 5 workers per dashboard
- Continue-on-error (individual failures don't stop others)

### Metadata Merging (Phase 9)
- LLM-based consolidation of metadata
- Conflict detection and resolution
- Generates unified schema
- Output: `extracted_meta/merged_metadata/`

### Knowledge Base Building (Phase 10)
- Converts merged metadata to KB format
- Creates compressed ZIP archive
- Ready for LLM context injection
- Output: `extracted_meta/knowledge_base/knowledge_base.zip`

## Progress Tracking & UI

### Real-Time Progress Display
- Overall status: pending → processing → merging → building_kb → completed
- Per-dashboard status tracking
- Per-phase progress indication
- Poll interval: 3 seconds

### Individual File Status
- Independent polling for each metadata file
- Status per file:
  - "Checking..." - Polling file existence
  - "Processing..." - File generation in progress
  - "Completed" - File ready for download
  - "Waiting..." - Queued for processing
- Shows completion as soon as file exists (not tied to overall status)
- Each file card polls every 3 seconds during processing

### Dashboard-Level Progress Cards
- Metadata type cards: JSON, CSV, Tables/Columns, Enriched, Table Metadata, Column Metadata, Joining Conditions, Filter Conditions, Definitions
- Download buttons (CSV, JSON where applicable)
- Click to view file contents
- Progress bar (light blue for in-progress, green for completed)

## LLM Integration

### DSPy Framework
- Structured LLM I/O with signatures
- Automatic prompt optimization
- Caching to reduce redundant calls
- Error handling and retry logic

### Claude Sonnet 4
- Primary LLM model
- Via internal proxy (corporate network)
- ~50 requests/minute rate limit
- Average response time: 5-10 seconds per chart

### Extraction Signatures
- `SourceTableColumnExtractor` - Tables and columns
- `TableMetadataExtractor` - Table descriptions
- `ColumnMetadataExtractor` - Column descriptions
- `JoiningConditionExtractor` - Table relationships
- `FilterConditionExtractor` - Filter logic
- `TermDefinitionExtractor` - Business metrics

## Data Enrichment

### Trino/Starburst Integration
- DESCRIBE queries via Superset SQL Lab API
- Fetch column datatypes, partitions, comments
- No direct Trino connection required
- Handles catalog.schema.table normalization

### Schema Matching
- Fuzzy table name matching
- Handles different catalog/schema prefixes
- Deduplicates columns across charts

## File Management

### Per-Dashboard Files
- Organized in `extracted_meta/{dashboard_id}/`
- 11 files per dashboard
- Standardized naming: `{id}_{type}.{ext}`

### Downloadable Formats
- JSON: Complete metadata
- CSV: Tabular data
- SQL: Query definitions
- TXT: Filter conditions
- ZIP: All files bundled

### File Viewer
- In-browser CSV/JSON viewer
- Syntax highlighting
- Search and filter
- Export functionality

## Error Handling

### Graceful Degradation
- Continue processing on individual failures
- Status marked as 'error' in progress tracking
- Detailed error logging
- User-friendly error messages in UI

### Retry Logic
- LLM calls: 3 retries with exponential backoff
- API calls: Automatic retry on timeout
- File operations: Graceful handling of missing files

### Debugging Support
- Comprehensive logging in `logs/`
- Progress state persisted to `progress.json`
- API request/response logging
- Timing information per phase

## Performance Optimizations

### Parallel Processing
- Multi-dashboard: Parallel extraction
- Per-dashboard: Parallel chart processing
- ThreadPoolExecutor: 5 workers

### Caching
- DSPy LLM response caching
- Reduces redundant API calls
- Significant speed improvement on re-runs

### Background Processing
- API returns immediately
- LLM work in background threads
- Non-blocking frontend

### Polling Optimization
- Progress: 3 second intervals
- File status: 3 second intervals (only during processing)
- No polling when idle

## Configuration

### Environment Variables
- `ANTHROPIC_API_KEY` - Claude API key
- `USE_LLM_EXTRACTION` - Enable/disable LLM (default: true)
- `ENABLE_QUALITY_JUDGE` - Enable quality judging (default: true)

### Config File (`scripts/config.py`)
- `BASE_URL` - Superset instance URL
- `HEADERS` - Session cookie and CSRF token
- `LLM_API_KEY` - Anthropic API key
- `LLM_MODEL` - Model name (default: claude-sonnet-4-20250514)
- `LLM_BASE_URL` - Proxy URL

## Limitations

### Current Constraints
- Single backend server (no horizontal scaling)
- In-memory progress tracking (resets on restart)
- No authentication (internal tool)
- LLM rate limits (~50 req/min)
- No incremental extraction (full re-run required)

### Known Issues
- Large dashboards (>50 charts) may timeout
- Session cookies expire after ~24 hours
- KB build requires all dashboards to complete first

## Future Enhancements

### Planned Features
- Incremental extraction (delta updates)
- Database storage for metadata
- Advanced search and filtering
- Metadata quality scoring
- Data lineage visualization
- Multi-user support with authentication
