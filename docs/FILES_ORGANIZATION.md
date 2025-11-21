# Files Organization & Cleanup Guide

## Core Files (Keep in Root)

### Essential Production Code:
1. **`query_extract.py`** ⭐ - **Superset API calls & chart data extraction**
2. **`llm_extractor.py`** ⭐ - **Table/column/derived logic extraction**
3. **`api_server.py`** - FastAPI backend server
4. **`config.py`** - Central configuration
5. **`metadata_generator.py`** - Metadata generation
6. **`sql_parser.py`** - SQL parsing utilities
7. **`trino_client.py`** - Trino database client (used by metadata_generator.py)
8. **`starburst_schema_fetcher.py`** - Starburst schema fetching (used optionally by llm_extractor.py)

### Core Data Files:
9. **`dspy_examples.py`** - DSPy few-shot examples (loaded by llm_extractor.py)

---

## Files That Can Be Moved/Organized

### Documentation Files (Move to `docs/`):
- `DSPY_EXAMPLES_GUIDE.md` → `docs/guides/dspy-examples-guide.md`
- `DSPY_INTEGRATION_SUMMARY.md` → `docs/dspy-integration-summary.md`
- `dspy_examples_format.md` → `docs/guides/dspy-examples-format.md`
- `STARBURST_SCHEMA_FETCHER_README.md` → `docs/modules/starburst-schema-fetcher.md`
- `FRONTEND_DEBUG.md` → `docs/guides/frontend-debug.md`
- `SUMMARY.md` → `docs/summary.md`
- `STRUCTURE.md` → `docs/structure.md` (or keep in root as project overview)
- `KEY_FILES_GUIDE.md` → `docs/guides/key-files-guide.md`

### Shell Scripts (Move to `scripts/`):
- `start_backend.sh` → `scripts/start_backend.sh`
- `start_frontend.sh` → `scripts/start_frontend.sh`
- `restart_api.sh` → `scripts/restart_api.sh`
- `uv_setup.sh` → `scripts/uv_setup.sh`

### Keep in Root:
- `README.md` - Main project README (standard location)
- `requirements.txt` - Python dependencies (standard location)
- `pyproject.toml` - Project configuration (standard location)

---

## File Usage Summary

### `trino_client.py`
- **Used by**: `metadata_generator.py`
- **Purpose**: Trino database connection and column datatype fetching
- **Keep**: ✅ Yes, it's a core module

### `starburst_schema_fetcher.py`
- **Used by**: `llm_extractor.py` (optional, when `fetch_schemas=True`)
- **Purpose**: Direct Starburst connection for DESCRIBE queries
- **Keep**: ✅ Yes, it's a core module (optional feature)

### `uv_setup.sh`
- **Purpose**: Setup script for UV package manager
- **Move**: ✅ Can move to `scripts/` (not frequently used)

### Shell Scripts
- **Purpose**: Convenience scripts for starting services
- **Move**: ✅ Can move to `scripts/` (but update any references)

---

## Recommended Action Plan

### Phase 1: Move Documentation
```bash
# Move documentation files
mv DSPY_EXAMPLES_GUIDE.md docs/guides/
mv DSPY_INTEGRATION_SUMMARY.md docs/
mv dspy_examples_format.md docs/guides/
mv STARBURST_SCHEMA_FETCHER_README.md docs/modules/
mv FRONTEND_DEBUG.md docs/guides/
mv SUMMARY.md docs/
mv KEY_FILES_GUIDE.md docs/guides/
# Keep STRUCTURE.md in root (project overview)
```

### Phase 2: Move Shell Scripts
```bash
# Move shell scripts
mv start_backend.sh scripts/
mv start_frontend.sh scripts/
mv restart_api.sh scripts/
mv uv_setup.sh scripts/
```

### Phase 3: Update References
- Update any documentation that references moved files
- Update any scripts that call the moved shell scripts
- Update README.md if it references these files

---

## Final Clean Root Directory

After cleanup, root should have:
```
metamind/
├── Core Python modules (8 files)
├── README.md
├── requirements.txt
├── pyproject.toml
├── STRUCTURE.md (optional - project overview)
├── scripts/ (utility scripts)
├── tests/ (test files)
├── examples/ (example scripts)
├── docs/ (all documentation)
└── frontend/ (React app)
```

