/**
 * API Service for Resume Coach
 * Handles all HTTP requests to the backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 seconds
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add any auth tokens here if needed
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Resume endpoints
  async uploadResume(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.client.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  async getResume(resumeId: string) {
    return this.client.get(`/resume/${resumeId}`);
  }

  async deleteResume(resumeId: string) {
    return this.client.delete(`/resume/${resumeId}`);
  }

  async listResumes() {
    return this.client.get('/resume/');
  }

  // Analysis endpoints
  async createAnalysis(data: {
    resume_id: string;
    job_id?: string;
    job_description?: string;
    model_params?: {
      temperature?: number;
      max_tokens?: number;
    };
  }) {
    return this.client.post('/analysis/compare', data);
  }

  async getAnalysis(analysisId: string) {
    return this.client.get(`/analysis/${analysisId}`);
  }

  async regenerateAnalysis(analysisId: string, modelParams?: any) {
    return this.client.post(`/analysis/${analysisId}/regenerate`, modelParams);
  }

  async listAnalyses() {
    return this.client.get('/analysis/');
  }

  // Chat endpoints
  async sendChatMessage(data: {
    session_id: string;
    message: string;
    analysis_id: string;
  }) {
    return this.client.post('/chat/message', data);
  }

  async getChatHistory(sessionId: string) {
    return this.client.get(`/chat/history/${sessionId}`);
  }

  async clearChatSession(sessionId: string) {
    return this.client.delete(`/chat/session/${sessionId}`);
  }

  async listChatSessions() {
    return this.client.get('/chat/');
  }

  // Health check
  async healthCheck() {
    return this.client.get('/health', { baseURL: API_BASE_URL.replace('/api/v1', '') });
  }
}

export default new ApiService();
