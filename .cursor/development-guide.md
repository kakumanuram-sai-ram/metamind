# MetaMind Development Guide

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- Access to Superset instance
- Anthropic API key

### Setup

**Backend:**
```bash
cd /home/devuser/sai_dev/metamind
python -m venv meta_env
source meta_env/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd /home/devuser/sai_dev/metamind/frontend
npm install
```

### Configuration

**1. Superset Authentication (`scripts/config.py`):**
```python
BASE_URL = "https://superset.example.com"
HEADERS = {
    "Cookie": "session=your-session-cookie",
    "X-CSRFToken": "your-csrf-token"
}
```

**How to get session cookie:**
1. Open Superset in browser
2. Open DevTools (F12) → Network tab
3. Refresh page
4. Find any request → Headers → Cookie → Copy `session=...`
5. Find CSRF token in response headers or cookies

**2. LLM API (`environment`):**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### Running Services

**Backend:**
```bash
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
python scripts/api_server.py
# Server starts on http://localhost:8000
```

**Frontend:**
```bash
cd /home/devuser/sai_dev/metamind/frontend
npm start
# UI opens on http://localhost:3000
```

**Helper Scripts:**
```bash
./start_backend.sh   # Start backend in background
./start_frontend.sh  # Start frontend in background
./restart_api.sh     # Restart API server
```

## Project Structure

### Backend Modules

**Core Extraction:**
- `query_extract.py` - Superset API client
- `llm_extractor.py` - LLM-based extraction (DSPy)
- `sql_parser.py` - Rule-based SQL parsing (fallback)
- `trino_client.py` - Trino/Starburst integration

**Processing:**
- `extract_dashboard_with_timing.py` - Single dashboard entry point
- `orchestrator.py` - Multi-dashboard extraction
- `chart_level_extractor.py` - Chart-by-chart LLM processing
- `metadata_generator.py` - Metadata file generation

**Merging & KB:**
- `merger.py` - LLM-based metadata consolidation
- `knowledge_base_builder.py` - KB format conversion

**API & State:**
- `api_server.py` - FastAPI REST API
- `progress_tracker.py` - Thread-safe progress tracking
- `instruction_set_generator.py` - Business verticals & tags

### Frontend Components

**Main Components:**
- `App.js` - Main application, state management
- `BusinessVertical.js` - Vertical/sub-vertical selector
- `SupersetTab.js` - Dashboard selection & extraction
- `DashboardSection.js` - Progress display per dashboard

**Services:**
- `services/api.js` - API client (Axios)

## Development Workflow

### Adding a New Feature

**1. Backend API Endpoint:**
```python
# scripts/api_server.py
@app.post("/api/my-new-endpoint")
async def my_new_endpoint(request: MyRequest):
    try:
        # Your logic here
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**2. Frontend API Method:**
```javascript
// frontend/src/services/api.js
export const myAPI = {
  myNewMethod: async (param) => {
    const response = await api.post('/api/my-new-endpoint', { param });
    return response.data;
  }
};
```

**3. React Component:**
```javascript
// frontend/src/components/MyComponent.js
import { myAPI } from '../services/api';

const MyComponent = () => {
  const handleClick = async () => {
    const result = await myAPI.myNewMethod('value');
    console.log(result);
  };
  
  return <button onClick={handleClick}>Click Me</button>;
};
```

### Adding a New Metadata Type

**1. DSPy Signature (if using LLM):**
```python
# scripts/llm_extractor.py or chart_level_extractor.py
class MyMetadataExtractor(dspy.Signature):
    """Extract my custom metadata from dashboard SQL query."""
    
    dashboard_title = dspy.InputField()
    chart_name = dspy.InputField()
    sql_query = dspy.InputField()
    
    my_metadata = dspy.OutputField(desc="JSON list of extracted metadata")
```

**2. Extraction Logic:**
```python
# scripts/chart_level_extractor.py
def process_charts_for_my_metadata(charts, dashboard_title, api_key, model, base_url, max_workers=5):
    """Process charts in parallel to extract my metadata."""
    # Similar to existing process_charts_for_* functions
    pass
```

**3. File Generation:**
```python
# scripts/extract_dashboard_with_timing.py
# Add new phase after Phase 8
my_metadata = process_charts_for_my_metadata(charts, ...)
metadata_file = f"{dashboard_dir}/{dashboard_id}_my_metadata.csv"
df.to_csv(metadata_file, index=False)

if progress_tracker:
    progress_tracker.add_completed_file(dashboard_id, f"{dashboard_id}_my_metadata.csv")
```

**4. Frontend Display:**
```javascript
// frontend/src/components/DashboardSection.js
// Add new metadata card
{
  key: 'my_metadata',
  title: 'My Metadata',
  fileType: 'my_metadata'
}
```

### Adding a New Business Vertical

**1. Update Backend Config:**
```python
# scripts/instruction_set_generator.py
VERTICAL_CONTEXT = {
    # ... existing verticals
    'my_vertical': {
        'name': 'My Vertical Name',
        'short_name': 'MyVertical',  # Used for tag matching
        'description': 'Description of my vertical',
        'domain_context': 'Business domain context',
        'sub_verticals': {
            'Sub-Vertical 1': ['tag1', 'tag2'],
            'Sub-Vertical 2': ['tag3', 'tag4'],
        },
        'tags': ['my-vertical', 'general-tag'],
    }
}
```

**2. Update Frontend:**
```javascript
// frontend/src/components/BusinessVertical.js
const verticals = [
  // ... existing verticals
  { 
    id: 'my_vertical', 
    name: 'My Vertical', 
    subVerticals: ['Sub-Vertical 1', 'Sub-Vertical 2'] 
  },
];
```

**3. Tag Superset Dashboards:**
- Go to Superset dashboard
- Edit → Add tags: "MyVertical", "Sub-Vertical 1", etc.
- Case doesn't matter (matching is lowercase)

## Testing

### Manual Testing

**Single Dashboard:**
```bash
python scripts/extract_dashboard_with_timing.py 476
```

**Multi-Dashboard:**
```bash
python scripts/process_multiple_dashboards.py 476 511 729
```

**API Testing:**
```bash
# Start server
python scripts/api_server.py

# Test endpoint
curl -X POST http://localhost:8000/api/dashboards/by-vertical \
  -H "Content-Type: application/json" \
  -d '{"vertical": "upi", "sub_vertical": "UPI Growth"}'
```

### Unit Tests

```bash
python -m pytest tests/
```

### Common Test Scenarios

**Test dashboard extraction:**
```python
from scripts.query_extract import SupersetExtractor
from scripts.config import BASE_URL, HEADERS

extractor = SupersetExtractor(BASE_URL, HEADERS)
dashboard_info = extractor.extract_dashboard_complete_info(476)
assert len(dashboard_info.charts) > 0
```

**Test tag filtering:**
```python
from scripts.instruction_set_generator import get_tags_for_vertical

tags = get_tags_for_vertical('upi', 'UPI Growth')
assert 'UPI Growth' in tags
```

## Debugging

### Backend Debugging

**1. Check Logs:**
```bash
# Find latest log
ls -lt logs/ | head -5

# Tail log
tail -f logs/api_server_YYYYMMDD_HHMMSS.log
```

**2. Check Progress State:**
```bash
cat extracted_meta/progress.json | python -m json.tool
```

**3. Verify Files:**
```bash
ls -lh extracted_meta/476/
```

**4. Test LLM Connection:**
```python
import dspy
from scripts.config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL

lm = dspy.LM(model=f"anthropic/{LLM_MODEL}", api_base=LLM_BASE_URL, api_key=LLM_API_KEY)
response = lm("Say hello")
print(response)
```

### Frontend Debugging

**1. Browser Console:**
- F12 → Console tab
- Check for API errors
- Look for "Error fetching dashboards" etc.

**2. Network Tab:**
- F12 → Network tab
- Filter by "Fetch/XHR"
- Check API response times and payloads

**3. React DevTools:**
- Install React DevTools extension
- Inspect component props and state

### Common Issues

**"Session expired" Error:**
- Update session cookie in `scripts/config.py`
- Get fresh cookie from browser (see Configuration section)

**"File not found" Error:**
- Check if extraction completed: `ls extracted_meta/{id}/`
- Check progress state: `cat extracted_meta/progress.json`
- Verify phase completion in logs

**"Timeout" Error:**
- Increase timeout in `frontend/src/services/api.js`
- Check backend logs for actual error
- Large dashboards may take longer

**"No dashboards found" Message:**
- Verify Superset dashboards have correct tags
- Check tag matching logic in logs
- Test API directly with curl

## Code Style

### Python

**Type Hints:**
```python
def my_function(param: str, optional: int = None) -> Dict[str, Any]:
    return {"result": param}
```

**Docstrings:**
```python
def my_function(param: str) -> Dict[str, Any]:
    """
    Short description of function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Dictionary containing result
    """
    pass
```

**Error Handling:**
```python
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {str(e)}")
    raise  # Re-raise for API error handling
```

### JavaScript

**Functional Components:**
```javascript
const MyComponent = ({ prop1, prop2 }) => {
  const [state, setState] = useState(initial);
  
  useEffect(() => {
    // Effect logic
  }, [dependencies]);
  
  return <div>{content}</div>;
};
```

**Styled Components:**
```javascript
const StyledButton = styled.button`
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.primary};
  color: white;
`;
```

**API Calls:**
```javascript
const fetchData = async () => {
  try {
    const response = await api.get('/endpoint');
    setData(response.data);
  } catch (error) {
    console.error('Error:', error);
    setError(error.message);
  }
};
```

## Performance Tips

### Backend Optimization

**1. Parallel Processing:**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_chart, chart) for chart in charts]
    results = [f.result() for f in futures]
```

**2. Caching:**
```python
# DSPy caching is automatic
# For custom caching:
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param):
    return result
```

### Frontend Optimization

**1. Avoid Unnecessary Re-renders:**
```javascript
const MyComponent = React.memo(({ prop }) => {
  return <div>{prop}</div>;
});
```

**2. Use Callbacks:**
```javascript
const handleClick = useCallback(() => {
  doSomething();
}, [dependencies]);
```

**3. Cleanup Effects:**
```javascript
useEffect(() => {
  const interval = setInterval(poll, 3000);
  return () => clearInterval(interval);  // Cleanup
}, []);
```

## Deployment

### Production Checklist

- [ ] Update `BASE_URL` and `HEADERS` in `config.py`
- [ ] Set `ANTHROPIC_API_KEY` environment variable
- [ ] Configure proper log rotation
- [ ] Set up monitoring (logs, disk space)
- [ ] Test all API endpoints
- [ ] Verify frontend build works
- [ ] Document any environment-specific settings

### Building Frontend

```bash
cd frontend
npm run build
# Build artifacts in frontend/build/
```

### Running in Production

**Using systemd (Linux):**
```bash
# Create service file: /etc/systemd/system/metamind-api.service
[Unit]
Description=MetaMind API Server

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/metamind
Environment="ANTHROPIC_API_KEY=your-key"
ExecStart=/path/to/meta_env/bin/python scripts/api_server.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable metamind-api
sudo systemctl start metamind-api
```

**Using Docker (TODO):**
- Dockerfile not yet created
- Planned for future releases

## Contributing

### Branching Strategy

- `main` - Stable production code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes

### Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Update documentation
4. Submit PR with description
5. Code review
6. Merge to develop
7. Test in develop
8. Merge to main

### Commit Messages

```
feat: Add new metadata type for X
fix: Resolve timeout issue in dashboard filtering
docs: Update API reference for new endpoint
refactor: Simplify tag matching logic
test: Add unit tests for LLM extractor
```

## Resources

- Main README: `/home/devuser/sai_dev/metamind/README.md`
- Architecture: `.cursor/architecture.md`
- API Reference: `.cursor/api-reference.md`
- Features: `.cursor/features.md`
- Superset API Docs: https://superset.apache.org/docs/api
- DSPy Docs: https://dspy-docs.vercel.app/
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
