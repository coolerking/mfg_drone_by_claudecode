import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import { logger } from '@/utils/logger.js';
import { ErrorHandler } from '@/utils/errors.js';
import { NetworkError, type DroneStatus, type SystemStatus } from '@/types/index.js';
import type { Config } from '@/types/index.js';

/**
 * バックエンドAPIクライアント
 * FastAPI バックエンドとの通信を担当
 */
export class BackendClient {
  private client: AxiosInstance;
  private config: Config;

  constructor(config: Config) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.backendUrl,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'MCP-Drone-Server/1.0.0',
      },
    });

    this.setupInterceptors();
  }

  /**
   * リクエスト・レスポンスインターセプターを設定
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        logger.debug(`Making request to: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        logger.error('Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        logger.debug(`Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        const statusCode = error.response?.status;
        const message = error.response?.data?.message || error.message;
        const networkError = ErrorHandler.fromHttpStatus(
          statusCode || 500,
          message
        );
        
        logger.error('Response error:', {
          url: error.config?.url,
          status: statusCode,
          message,
        });
        
        return Promise.reject(networkError);
      }
    );
  }

  /**
   * ドローンの状態を取得
   */
  async getDroneStatus(droneId?: string): Promise<DroneStatus[]> {
    try {
      const url = droneId ? `/api/drones/${droneId}/status` : '/api/drones/status';
      const response: AxiosResponse<DroneStatus | DroneStatus[]> = await this.client.get(url);
      
      const data = response.data;
      return Array.isArray(data) ? data : [data];
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getDroneStatus');
      throw handledError;
    }
  }

  /**
   * ドローンをスキャン
   */
  async scanDrones(): Promise<{ message: string; found: number }> {
    try {
      const response: AxiosResponse<{ message: string; found: number }> = 
        await this.client.post('/api/drones/scan');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.scanDrones');
      throw handledError;
    }
  }

  /**
   * システムの健全性をチェック
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response: AxiosResponse<{ status: string; timestamp: string }> = 
        await this.client.get('/api/system/health');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.healthCheck');
      throw handledError;
    }
  }

  /**
   * システム状態を取得
   */
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const response: AxiosResponse<SystemStatus> = await this.client.get('/api/system/status');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getSystemStatus');
      throw handledError;
    }
  }

  /**
   * ドローンコマンドを実行
   */
  async executeCommand(droneId: string, command: string, params?: Record<string, unknown>): Promise<{ success: boolean; message: string }> {
    try {
      const response: AxiosResponse<{ success: boolean; message: string }> = 
        await this.client.post(`/api/drones/${droneId}/command`, {
          command,
          params: params || {},
        });
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.executeCommand');
      throw handledError;
    }
  }

  /**
   * バックエンド接続をテスト
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      logger.info(`Backend connection successful: ${this.config.backendUrl}`);
      return true;
    } catch (error) {
      logger.error(`Backend connection failed: ${this.config.backendUrl}`, error);
      return false;
    }
  }
}