# Deployment Guide

## Production Deployment

### Prerequisites

- Python 3.11+
- Node.js 16+ (for frontend)
- Superset access
- Anthropic API key

### Backend Deployment

1. **Install Dependencies**

```bash
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
export PATH="$HOME/.local/bin:$PATH"
# Dependencies should already be installed via uv
```

2. **Configure Environment**

```bash
export ANTHROPIC_API_KEY="sk-your-key"
export USE_LLM_EXTRACTION="true"
```

3. **Run with Production Server**

```bash
# Using gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app --bind 0.0.0.0:8000

# Or using uvicorn directly
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment

1. **Build for Production**

```bash
cd frontend
npm install
npm run build
```

2. **Serve Static Files**

```bash
# Using nginx
# Configure nginx to serve frontend/build directory

# Or using Python
cd frontend/build
python -m http.server 3000
```

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

- `ANTHROPIC_API_KEY` - Required for LLM extraction
- `USE_LLM_EXTRACTION` - Set to "false" to disable LLM (use rule-based)
- `BASE_URL` - Superset base URL (or set in config.py)
- `PORT` - Server port (default: 8000)

### Monitoring

- Check logs for errors
- Monitor API response times
- Track LLM API usage/costs
- Monitor disk space for `extracted_meta/` directory

