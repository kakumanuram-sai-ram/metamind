/**
 * API Service for communicating with the backend
 */
import axios from 'axios';

// Determine API base URL
// Priority:
// 1. Environment variable REACT_APP_API_URL (for custom overrides)
// 2. Use the same host as the current page (for network access)
// 3. Fall back to localhost:8000
const getApiBaseUrl = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }

  // If running on a network address (not localhost), use same host with backend port
  const host = window.location.hostname;
  if (host !== 'localhost' && host !== '127.0.0.1') {
    return `http://${host}:8000`;
  }

  // Default to localhost
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds default timeout for most operations
});

// Performance tracking
const requestTimings = new Map();

// Add request interceptor for debugging with timing
api.interceptors.request.use(
  (config) => {
    const startTime = performance.now();
    const requestId = `${config.method?.toUpperCase()}_${config.url}_${Date.now()}`;
    requestTimings.set(requestId, { startTime, url: config.url, method: config.method });
    
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [API REQUEST START] ${config.method?.toUpperCase()} ${config.url}`, {
      timeout: config.timeout,
      data: config.data,
      requestId
    });
    
    config.metadata = { requestId, startTime };
    return config;
  },
  (error) => {
    const timestamp = new Date().toISOString();
    console.error(`[${timestamp}] [API REQUEST ERROR]`, error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging with timing
api.interceptors.response.use(
  (response) => {
    const { requestId, startTime } = response.config.metadata || {};
    const duration = requestId && startTime ? (performance.now() - startTime).toFixed(2) : 'N/A';
    const timestamp = new Date().toISOString();
    
    if (requestId) {
      requestTimings.delete(requestId);
    }
    
    console.log(`[${timestamp}] [API RESPONSE SUCCESS] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      duration: `${duration}ms`,
      requestId
    });
    
    return response;
  },
  (error) => {
    const { requestId, startTime } = error.config?.metadata || {};
    const duration = requestId && startTime ? (performance.now() - startTime).toFixed(2) : 'N/A';
    const timestamp = new Date().toISOString();
    
    if (requestId && requestTimings.has(requestId)) {
      requestTimings.delete(requestId);
    }
    
    console.error(`[${timestamp}] [API RESPONSE ERROR] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
      message: error.message,
      code: error.code,
      duration: `${duration}ms`,
      status: error.response?.status,
      response: error.response?.data,
      requestId
    });
    
    return Promise.reject(error);
  }
);

export const dashboardAPI = {
  /**
   * Get list of all available dashboards
   */
  getDashboards: async () => {
    const response = await api.get('/api/dashboards', {
      timeout: 5000, // 5 seconds timeout for dashboard list
    });
    return response.data;
  },

  /**
   * Get dashboard JSON data
   */
  getDashboardJSON: async (dashboardId) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/json`);
    return response.data;
  },

  /**
   * Get dashboard CSV data
   */
  getDashboardCSV: async (dashboardId) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/csv`);
    return response.data;
  },

  /**
   * Download JSON file
   */
  downloadJSON: async (dashboardId) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/json/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Download CSV file
   */
  downloadCSV: async (dashboardId) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/csv/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Extract dashboard from URL
   */
  extractDashboard: async (dashboardUrl, dashboardId = null) => {
    const response = await api.post('/api/dashboard/extract', {
      dashboard_url: dashboardUrl,
      dashboard_id: dashboardId,
    }, {
      timeout: 180000, // 3 minutes timeout for extraction (longer than default)
    });
    return response.data;
  },

  /**
   * Get dashboard tables and columns mapping
   */
  getDashboardTablesColumns: async (dashboardId) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/tables-columns`);
    return response.data;
  },

  /**
   * Get progress of multi-dashboard processing
   */
  getProgress: async () => {
    const response = await api.get('/api/progress', {
      timeout: 5000, // 5 seconds timeout for progress checks
    });
    return response.data;
  },

  /**
   * Check if dashboard metadata exists
   */
  checkDashboardMetadataExists: async (dashboardId) => {
    try {
      const response = await api.get(`/api/dashboard/${dashboardId}/files`, {
        timeout: 5000, // 5 seconds timeout for file checks
      });
      // Check if key metadata files exist
      const files = response.data.files || [];
      const hasTableMetadata = files.some(f => f.type === 'table_metadata');
      const hasColumnMetadata = files.some(f => f.type === 'columns_metadata');
      return hasTableMetadata && hasColumnMetadata;
    } catch (error) {
      return false;
    }
  },

  /**
   * Process multiple dashboards
   */
  processMultipleDashboards: async (dashboardIds, extract = true, merge = true, buildKb = true, metadataChoices = null) => {
    const response = await api.post('/api/dashboards/process-multiple', {
      dashboard_ids: dashboardIds,
      extract,
      merge,
      build_kb: buildKb,
      metadata_choices: metadataChoices,
    });
    return response.data;
  },

  /**
   * Get all metadata files for a dashboard
   */
  getDashboardFiles: async (dashboardId) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/files`, {
      timeout: 5000, // 5 seconds timeout for file list
    });
    return response.data;
  },

  /**
   * Download a specific metadata file
   */
  downloadDashboardFile: async (dashboardId, fileType) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/download/${fileType}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Download all metadata files as ZIP
   */
  downloadAllDashboardFiles: async (dashboardId) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/download-all`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Download tables and columns CSV file
   */
  downloadTablesColumns: async (dashboardId) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/tables-columns/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Download final consolidated ZIP file (knowledge base)
   */
  downloadFinalZip: async () => {
    const response = await api.get('/api/download-final-zip', {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Download knowledge base ZIP file
   */
  downloadKnowledgeBaseZip: async () => {
    const response = await api.get('/api/knowledge-base/download', {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Get metadata file content for display
   */
  getMetadataFileContent: async (dashboardId, fileType) => {
    const response = await api.get(`/api/dashboard/${dashboardId}/file/${fileType}`);
    return response.data;
  },

  /**
   * Connect to N8N workflow
   */
  connectToN8N: async () => {
    const response = await api.post('/api/knowledge-base/connect-n8n');
    return response.data;
  },

  /**
   * Enable on Prism
   */
  enableOnPrism: async () => {
    const response = await api.post('/api/knowledge-base/enable-prism');
    return response.data;
  },
};

export default api;

