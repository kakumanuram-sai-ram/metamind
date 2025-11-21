# Superset Dashboard Extractor - Full Stack Application

This application provides a React frontend and FastAPI backend for extracting and visualizing Superset dashboard metadata.

## Architecture

- **Backend**: FastAPI server (`api_server.py`)
- **Frontend**: React application with Paytm color palette
- **Backend Library**: Python module for Superset extraction (`query_extract.py`)

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
```bash
cd /home/devuser/sai_dev/metamind
pip install -r requirements.txt
```

2. Update `config.py` with your Superset credentials (Cookie and X-CSRFToken)

3. Start the FastAPI server:
```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd /home/devuser/sai_dev/metamind/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (optional, defaults to localhost:8000):
```
REACT_APP_API_URL=http://localhost:8000
```

4. Start the React development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Features

### Dashboard Extraction
- Enter a Superset dashboard URL
- Optionally provide dashboard ID
- Extract dashboard metadata (JSON, CSV, SQL)

### Dashboard List
- View all extracted dashboards
- Click on a dashboard to view details
- Refresh to see newly extracted dashboards

### JSON Viewer
- View complete dashboard JSON metadata
- Expandable/collapsible view
- Syntax-highlighted JSON display

### CSV Viewer
- View dashboard CSV data in a table
- Download CSV files
- View SQL queries for each chart
- Responsive table with horizontal scroll

## API Endpoints

- `GET /api/dashboards` - List all available dashboards
- `GET /api/dashboard/{id}/json` - Get dashboard JSON
- `GET /api/dashboard/{id}/csv` - Get dashboard CSV data
- `GET /api/dashboard/{id}/csv/download` - Download CSV file
- `POST /api/dashboard/extract` - Extract dashboard from URL

## Color Palette

The application uses Paytm's brand colors:
- Primary Blue: `#002970`
- Secondary Orange: `#FF6F00`
- Accent Cyan: `#00BAF2`

## Project Structure

```
metamind/
├── api_server.py          # FastAPI backend server
├── query_extract.py       # Superset extraction library
├── config.py              # Configuration (credentials)
├── requirements.txt       # Python dependencies
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service
│   │   ├── styles/        # Theme and styles
│   │   └── App.js         # Main app component
│   ├── package.json
│   └── README.md
└── dashboard_*_*.{json,csv,sql}  # Extracted dashboard files
```

## Usage

1. Start the backend server
2. Start the frontend development server
3. Open `http://localhost:3000` in your browser
4. Enter a Superset dashboard URL and click "Extract Dashboard"
5. Once extracted, click on the dashboard card to view JSON and CSV data

