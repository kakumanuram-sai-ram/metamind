# Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- Superset credentials (Cookie and X-CSRFToken in `config.py`)

### Step 1: Install Backend Dependencies

**Using uv (Recommended - Fast and Modern):**
```bash
cd /home/devuser/sai_dev/metamind
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Create virtual environment and install dependencies
uv venv meta_env
source meta_env/bin/activate
uv pip install -r requirements.txt
```

**Or using traditional pip:**
```bash
cd /home/devuser/sai_dev/metamind
python3 -m venv meta_env
source meta_env/bin/activate
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 3: Configure Backend

Update `config.py` with your Superset credentials:
- `Cookie`: Your session cookie from Superset
- `X-CSRFToken`: Your CSRF token from Superset

### Step 4: Start the Backend Server

In one terminal:
```bash
cd /home/devuser/sai_dev/metamind
source meta_env/bin/activate  # Activate virtual environment
./start_backend.sh
# OR
python api_server.py
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Step 5: Start the Frontend

In another terminal:
```bash
cd /home/devuser/sai_dev/metamind/frontend
./start_frontend.sh
# OR
npm start
```

The frontend will open at: http://localhost:3000

## 📖 Usage

1. **Extract a Dashboard**:
   - Enter a Superset dashboard URL (e.g., `https://cdp-dataview.platform.mypaytm.com/superset/dashboard/729/`)
   - Optionally provide the dashboard ID
   - Click "Extract Dashboard"
   - Wait for extraction to complete

2. **View Dashboard Data**:
   - Click on any dashboard card in the "Available Dashboards" section
   - View the JSON metadata in the JSON Viewer
   - View the CSV data in the CSV Viewer table
   - Download the CSV file if needed

3. **Refresh Dashboard List**:
   - Click the "Refresh" button to see newly extracted dashboards

## 🎨 Features

- ✅ Extract dashboard metadata from Superset URLs
- ✅ View JSON metadata with syntax highlighting
- ✅ View CSV data in an interactive table
- ✅ Download CSV files
- ✅ Paytm color palette (Blue #002970, Orange #FF6F00)
- ✅ Responsive design
- ✅ Modular React components

## 📁 Project Structure

```
metamind/
├── api_server.py              # FastAPI backend
├── query_extract.py           # Superset extraction library
├── config.py                  # Configuration
├── requirements.txt           # Python dependencies
├── start_backend.sh          # Backend startup script
├── start_frontend.sh          # Frontend startup script
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── DashboardList.js
│   │   │   ├── DashboardExtractor.js
│   │   │   ├── JSONViewer.js
│   │   │   └── CSVViewer.js
│   │   ├── services/          # API service
│   │   │   └── api.js
│   │   ├── styles/            # Theme
│   │   │   ├── theme.js
│   │   │   └── GlobalStyles.js
│   │   ├── App.js             # Main app
│   │   └── index.js           # Entry point
│   ├── package.json
│   └── README.md
└── dashboard_*_*.{json,csv,sql}  # Extracted files
```

## 🔧 Troubleshooting

### Backend Issues
- **Port 8000 already in use**: Change the port in `api_server.py` (last line)
- **Import errors**: Make sure all Python dependencies are installed
- **Authentication errors**: Update `config.py` with valid credentials

### Frontend Issues
- **Port 3000 already in use**: React will prompt to use another port
- **API connection errors**: Check that backend is running and `REACT_APP_API_URL` is correct
- **Module not found**: Run `npm install` again

## 📝 API Endpoints

- `GET /api/dashboards` - List all dashboards
- `GET /api/dashboard/{id}/json` - Get JSON data
- `GET /api/dashboard/{id}/csv` - Get CSV data
- `GET /api/dashboard/{id}/csv/download` - Download CSV
- `POST /api/dashboard/extract` - Extract dashboard

## 🎯 Next Steps

- Customize the color palette in `frontend/src/styles/theme.js`
- Add more features to the components
- Deploy to production (build frontend with `npm run build`)

