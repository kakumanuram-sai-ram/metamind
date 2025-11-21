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
   * Process multiple dashboards
   */
  processMultipleDashboards: async (dashboardIds, extract = true, merge = true, buildKb = true) => {
    const response = await api.post('/api/dashboards/process-multiple', {
      dashboard_ids: dashboardIds,
      extract,
      merge,
      build_kb: buildKb,
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
};

export default api;

