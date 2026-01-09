/**
 * API Service for Resume Coach
 * Handles all HTTP requests to the backend
 */
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { logger } from './logger';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    logger.info('Initializing API Service', { baseURL: API_BASE_URL });
    
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 seconds
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const method = config.method?.toUpperCase();
        const url = config.url;
        logger.info(`→ ${method} ${url}`);
        logger.debug('Request config', { 
          headers: config.headers,
          timeout: config.timeout,
          dataSize: config.data ? JSON.stringify(config.data).length : 0
        });
        
        // Store start time for duration calculation
        (config as any).metadata = { startTime: Date.now() };
        
        return config;
      },
      (error) => {
        logger.error('Request error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        const duration = Date.now() - ((response.config as any).metadata?.startTime || Date.now());
        const method = response.config.method?.toUpperCase();
        const url = response.config.url;
        
        logger.info(`← ✓ ${method} ${url} - ${response.status} (${duration}ms)`);
        logger.debug('Response data', { 
          status: response.status,
          dataSize: JSON.stringify(response.data).length
        });
        
        return response;
      },
      (error: AxiosError) => {
        const duration = Date.now() - ((error.config as any)?.metadata?.startTime || Date.now());
        const method = error.config?.method?.toUpperCase();
        const url = error.config?.url;
        
        logger.error(`← ✗ ${method} ${url} - ${error.response?.status || 'NETWORK ERROR'} (${duration}ms)`, {
          message: error.message,
          response: error.response?.data
        });
        
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
    logger.info('Starting resume analysis', { 
      resume_id: data.resume_id,
      job_description_length: data.job_description?.length || 0
    });
    
    const startTime = Date.now();
    
    try {
      // Longer timeout for analysis - local LLMs can take 3-5 minutes
      const response = await this.client.post('/analysis/compare', data, {
        timeout: 300000, // 5 minutes
      });
      
      const duration = (Date.now() - startTime) / 1000;
      logger.info(`Analysis completed in ${duration.toFixed(2)}s`, {
        match_score: response.data.summary?.match_score,
        overall_fit: response.data.summary?.overall_fit
      });
      
      return response;
    } catch (error: any) {
      const duration = (Date.now() - startTime) / 1000;
      logger.error(`Analysis failed after ${duration.toFixed(2)}s`, {
        error: error.message,
        response: error.response?.data
      });
      throw error;
    }
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
