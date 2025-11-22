# Starting MetaMind Services

## Quick Start (All-in-One)

```bash
cd /home/devuser/sai_dev/metamind
./start_services.sh
```

## Manual Start

### Start Backend Only

```bash
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
python scripts/api_server.py
```

Or in background:
```bash
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate
nohup python scripts/api_server.py > /tmp/api_server.log 2>&1 &
```

### Start Frontend Only

```bash
cd /home/devuser/sai_dev/metamind/frontend
npm start
```

Or in background:
```bash
cd /home/devuser/sai_dev/metamind/frontend
nohup npm start > /tmp/frontend.log 2>&1 &
```

## View Logs

### Backend Logs
```bash
tail -f /tmp/api_server.log
```

### Frontend Logs
```bash
tail -f /tmp/frontend.log
```

## Stop Services

```bash
# Stop backend
pkill -f "api_server.py"

# Stop frontend
pkill -f "react-scripts"

# Stop both
pkill -f "api_server.py" && pkill -f "react-scripts"
```

## Check Service Status

```bash
# Check if services are running
ps aux | grep -E "(api_server|react-scripts)" | grep -v grep

# Check ports
netstat -tlnp 2>/dev/null | grep -E ":(8000|3000)" || ss -tlnp 2>/dev/null | grep -E ":(8000|3000)"
```

## URLs

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:3000



