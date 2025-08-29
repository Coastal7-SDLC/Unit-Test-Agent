import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const analysisAPI = {
  // Start repository analysis
  startAnalysis: async (data) => {
    const response = await api.post('/analyze', data);
    return response.data;
  },

  // Get task status
  getTaskStatus: async (taskId) => {
    const response = await api.get(`/status/${taskId}`);
    return response.data;
  },

  // Get analysis results
  getAnalysisResults: async (taskId) => {
    const response = await api.get(`/results/${taskId}`);
    return response.data;
  },

  // Download test files
  downloadTestFiles: async (taskId) => {
    const response = await api.get(`/download/${taskId}/tests`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Download coverage report
  downloadCoverageReport: async (taskId) => {
    const response = await api.get(`/download/${taskId}/coverage`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
