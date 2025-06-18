/**
 * FastAPI Client
 * 
 * HTTP client for communicating with the MFG Drone Backend API
 * Provides methods for all drone operations with error handling and retries
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { BackendConfig } from '../types/config.js';
import { 
  BaseResponse, 
  ConnectionResponse, 
  FlightResponse, 
  StatusResponse,
  ErrorResponse 
} from '../types/api.js';
import { logger } from '../utils/logger.js';

export class FastAPIClient {
  private client: AxiosInstance;
  private config: BackendConfig;
  private healthCheckTimer?: NodeJS.Timeout;

  constructor(config: BackendConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.url,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    // Setup request/response interceptors
    this.setupInterceptors();
  }

  /**
   * Initialize the API client
   */
  async initialize(): Promise<void> {
    try {
      // Test connection to backend
      await this.healthCheck();
      logger.info('FastAPI client connected successfully', { 
        baseURL: this.config.url 
      });

      // Start periodic health checks
      this.startHealthCheck();
    } catch (error) {
      logger.error('Failed to initialize FastAPI client', error);
      throw error;
    }
  }

  /**
   * Close the API client and cleanup resources
   */
  async close(): Promise<void> {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = undefined;
    }
    logger.info('FastAPI client closed');
  }

  /**
   * Setup axios interceptors for logging and error handling
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        logger.debug('API request', {
          method: config.method?.toUpperCase(),
          url: config.url,
          baseURL: config.baseURL,
        });
        return config;
      },
      (error) => {
        logger.error('API request error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        logger.debug('API response', {
          status: response.status,
          url: response.config.url,
          success: response.data?.success,
        });
        return response;
      },
      (error: AxiosError) => {
        logger.error('API response error', {
          status: error.response?.status,
          url: error.config?.url,
          message: error.message,
        });
        return Promise.reject(this.normalizeError(error));
      }
    );
  }

  /**
   * Normalize axios errors to consistent format
   */
  private normalizeError(error: AxiosError): Error {
    if (error.response?.data && typeof error.response.data === 'object') {
      const errorData = error.response.data as ErrorResponse;
      return new Error(errorData.message || 'API request failed');
    }
    
    if (error.code === 'ECONNREFUSED') {
      return new Error('Cannot connect to backend server');
    }
    
    if (error.code === 'ECONNABORTED') {
      return new Error('Request timeout');
    }
    
    return new Error(error.message || 'Unknown API error');
  }

  /**
   * Execute request with retry logic
   */
  private async executeWithRetry<T>(
    operation: () => Promise<T>,
    retries = this.config.retries
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      if (retries > 0) {
        logger.warn('API request failed, retrying...', {
          retriesLeft: retries,
          error: error instanceof Error ? error.message : String(error),
        });
        
        await this.delay(this.config.retryDelay);
        return this.executeWithRetry(operation, retries - 1);
      }
      throw error;
    }
  }

  /**
   * Delay utility for retries
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Health check
   */
  private async healthCheck(): Promise<void> {
    const response = await this.client.get('/health');
    if (response.status !== 200) {
      throw new Error(`Health check failed with status: ${response.status}`);
    }
  }

  /**
   * Start periodic health checks
   */
  private startHealthCheck(): void {
    this.healthCheckTimer = setInterval(async () => {
      try {
        await this.healthCheck();
        logger.debug('Health check passed');
      } catch (error) {
        logger.warn('Health check failed', error);
      }
    }, this.config.healthCheckInterval);
  }

  // Connection API methods
  async connect(): Promise<ConnectionResponse> {
    return this.executeWithRetry(async () => {
      const response = await this.client.post<ConnectionResponse>('/drone/connect');
      return response.data;
    });
  }

  async disconnect(): Promise<ConnectionResponse> {
    return this.executeWithRetry(async () => {
      const response = await this.client.post<ConnectionResponse>('/drone/disconnect');
      return response.data;
    });
  }

  async getStatus(): Promise<StatusResponse> {
    return this.executeWithRetry(async () => {
      const response = await this.client.get<StatusResponse>('/drone/status');
      return response.data;
    });
  }

  // Flight control API methods
  async takeoff(): Promise<FlightResponse> {
    return this.executeWithRetry(async () => {
      const response = await this.client.post<FlightResponse>('/flight/takeoff');
      return response.data;
    });
  }

  async land(): Promise<FlightResponse> {
    return this.executeWithRetry(async () => {
      const response = await this.client.post<FlightResponse>('/flight/land');
      return response.data;
    });
  }

  async emergency(): Promise<FlightResponse> {
    return this.executeWithRetry(async () => {
      const response = await this.client.post<FlightResponse>('/flight/emergency');
      return response.data;
    });
  }
}