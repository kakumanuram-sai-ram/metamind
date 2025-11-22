/**
 * API Service for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardAPI = {
  /**
   * Get list of all available dashboards
   */
  getDashboards: async () => {
    const response = await api.get('/api/dashboards');
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
    const response = await api.get('/api/progress');
    return response.data;
  },

  /**
   * Check if dashboard metadata exists
   */
  checkDashboardMetadataExists: async (dashboardId) => {
    try {
      const response = await api.get(`/api/dashboard/${dashboardId}/files`);
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
    const response = await api.get(`/api/dashboard/${dashboardId}/files`);
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

