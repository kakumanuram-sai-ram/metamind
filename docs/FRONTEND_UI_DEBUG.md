# Frontend UI Debugging Guide

## Overview

This document provides a structured approach to debugging the MetaMind frontend UI. Use this guide when troubleshooting issues instead of searching through the entire codebase.

## Component Structure

### Main Application
- **File**: `frontend/src/App.js`
- **Purpose**: Main application entry point with header and tab navigation
- **Key Features**:
  - MetaMind header (must remain exactly the same)
  - Tab navigation (Superset, Google Docs, Confluence/Wiki)
  - Tab content rendering

### Tab Components

#### 1. TabNavigation
- **File**: `frontend/src/components/TabNavigation.js`
- **Purpose**: Renders tab buttons and handles tab switching
- **Props**: `activeTab`, `onTabChange`
- **Common Issues**:
  - Tabs not switching: Check `onTabChange` callback in App.js
  - Active tab styling: Verify `active` prop is correctly passed

#### 2. SupersetTab
- **File**: `frontend/src/components/SupersetTab.js`
- **Purpose**: Main Superset dashboard extraction interface
- **Key State**:
  - `dashboardIds`: Comma-separated dashboard IDs input
  - `activeDashboardIds`: Array of parsed dashboard IDs
  - `progress`: Progress data from API
  - `statusMessage`: Current status message (merging, validation, etc.)
  - `finalZipAvailable`: Boolean for final ZIP download availability
- **Key Functions**:
  - `handleStartExtraction`: Parses IDs and starts extraction
  - `fetchProgress`: Polls API for progress updates (every 2 seconds)
  - `handleDownloadFinalZip`: Downloads final consolidated ZIP
- **Common Issues**:
  - Progress not updating: Check `progressInterval` is set correctly
  - Status messages not showing: Verify `progress.status` values match expected states
  - Final ZIP not available: Check if `progress.status === 'completed'`

#### 3. DashboardSection
- **File**: `frontend/src/components/DashboardSection.js`
- **Purpose**: Displays metadata sections for a single dashboard
- **Props**: `dashboardId`, `progress`
- **Key Features**:
  - Horizontal layout of metadata sections
  - Progress bars for each section
  - Download buttons (JSON/CSV) when complete
- **Metadata Types**:
  - `table_metadata`
  - `columns_metadata`
  - `definitions`
  - `joining_conditions`
  - `filter_conditions`
- **Common Issues**:
  - Progress not showing: Check `progress.dashboards[dashboardId]` structure
  - Download buttons not appearing: Verify `getStatus()` returns 'completed'
  - File downloads failing: Check API endpoint `/api/dashboard/{id}/download/{fileType}`

## API Integration

### API Service
- **File**: `frontend/src/services/api.js`
- **Base URL**: `process.env.REACT_APP_API_URL || 'http://localhost:8000'`

### Key Endpoints Used

1. **Start Extraction**
   - `POST /api/dashboards/process-multiple`
   - Body: `{ dashboard_ids: [int], extract: true, merge: true, build_kb: true }`

2. **Get Progress**
   - `GET /api/progress`
   - Returns: Progress object with status, dashboards, merge_status, kb_build_status

3. **Get Dashboard Files**
   - `GET /api/dashboard/{dashboard_id}/files`
   - Returns: List of available files for a dashboard

4. **Download File**
   - `GET /api/dashboard/{dashboard_id}/download/{file_type}`
   - Response: Blob (file content)
   - File types: `json`, `csv`, `table_metadata`, `columns_metadata`, `definitions`, `joining_conditions`, `filter_conditions`

5. **Download Final ZIP**
   - `GET /api/download-final-zip` or `/api/knowledge-base/download`
   - Response: Blob (ZIP file)

## Progress States

### Overall Status Values
- `idle`: No processing happening
- `extracting`: Dashboards are being extracted
- `merging`: Metadata is being merged
- `building_kb`: Knowledge base is being built
- `completed`: All processing complete

### Dashboard Status Values
- `pending`: Not started
- `processing`: Currently processing
- `completed`: Finished successfully
- `error`: Failed with error

### Status Message Mapping
- `merging` → "Metadata merging is happening..."
- `building_kb` → "Validation is happening..."
- `completed` → "All processing complete! Final ZIP file is available for download."

## Common Debugging Scenarios

### 1. Dashboard IDs Not Processing

**Symptoms**: Clicking "Start Extraction" doesn't start processing

**Debug Steps**:
1. Check browser console for errors
2. Verify API is running on port 8000
3. Check network tab for failed requests
4. Verify dashboard IDs are valid integers
5. Check `handleStartExtraction` function in SupersetTab.js

**Common Causes**:
- API server not running
- Invalid dashboard ID format
- CORS issues
- Network connectivity problems

### 2. Progress Not Updating

**Symptoms**: Progress bars don't update, status doesn't change

**Debug Steps**:
1. Check if `progressInterval` is set in SupersetTab
2. Verify `fetchProgress` is being called
3. Check API response in network tab
4. Verify progress.json file exists on backend
5. Check browser console for polling errors

**Common Causes**:
- Progress interval cleared prematurely
- API endpoint returning errors
- Progress file not being updated on backend
- Component unmounted while polling

### 3. Download Buttons Not Appearing

**Symptoms**: Files are complete but download buttons don't show

**Debug Steps**:
1. Check `getStatus()` function in DashboardSection.js
2. Verify `fileAvailable` state is set correctly
3. Check if `getDashboardFiles` API call succeeds
4. Verify file type matches expected format
5. Check browser console for errors

**Common Causes**:
- File type mismatch
- API returning empty file list
- Status not updating to 'completed'
- File check failing silently

### 4. Final ZIP Not Available

**Symptoms**: Processing complete but ZIP download doesn't work

**Debug Steps**:
1. Check if `finalZipAvailable` state is true
2. Verify `progress.status === 'completed'`
3. Check API endpoint exists for final ZIP
4. Verify knowledge_base.zip file exists on backend
5. Check network tab for download request

**Common Causes**:
- API endpoint not implemented
- ZIP file not created on backend
- File path incorrect
- CORS issues with blob download

### 5. UI Not Rendering

**Symptoms**: Blank screen or component not showing

**Debug Steps**:
1. Check browser console for React errors
2. Verify all imports are correct
3. Check if GlobalStyles is imported in App.js
4. Verify ThemeProvider is wrapping components
5. Check for syntax errors in component files

**Common Causes**:
- Missing imports
- Syntax errors
- Theme not provided
- Component not exported correctly

## File Structure Reference

```
frontend/src/
├── App.js                    # Main app with header and tabs
├── components/
│   ├── TabNavigation.js      # Tab switching component
│   ├── SupersetTab.js        # Main Superset interface
│   ├── DashboardSection.js   # Individual dashboard display
│   ├── GoogleDocsTab.js      # Placeholder for Google Docs
│   └── ConfluenceTab.js      # Placeholder for Confluence
├── services/
│   └── api.js                # API service functions
└── styles/
    ├── theme.js              # Theme configuration
    └── GlobalStyles.js       # Global CSS styles
```

## Quick Debug Checklist

When debugging frontend issues, check in this order:

1. **Browser Console**: Look for JavaScript errors
2. **Network Tab**: Check API requests/responses
3. **React DevTools**: Inspect component state and props
4. **Component State**: Verify state variables are updating
5. **API Endpoints**: Confirm backend endpoints are working
6. **File Paths**: Verify file paths match backend structure
7. **Environment Variables**: Check REACT_APP_API_URL is set

## Testing Locally

1. **Start Backend**: `cd metamind && python scripts/api_server.py`
2. **Start Frontend**: `cd metamind/frontend && npm start`
3. **Open Browser**: `http://localhost:3000`
4. **Test Flow**:
   - Enter dashboard IDs (e.g., "585, 729")
   - Click "Start Extraction"
   - Watch progress bars update
   - Verify download buttons appear when complete
   - Test download functionality

## Key Files to Check When Debugging

- **Progress Issues**: `SupersetTab.js` → `fetchProgress()`
- **Download Issues**: `DashboardSection.js` → `handleDownload()`
- **API Issues**: `services/api.js`
- **Styling Issues**: `styles/theme.js` and component styled-components
- **State Issues**: Component useState hooks and useEffect dependencies

## Notes

- Progress polling runs every 2 seconds
- File availability is checked when status is 'completed'
- Download buttons use outline icons (non-opaque)
- All metadata sections are displayed horizontally
- Dashboard sections are scrollable when many dashboards are processed

