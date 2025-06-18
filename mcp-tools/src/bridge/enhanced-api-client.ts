import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ConfigManager } from '../utils/config';
import { Logger } from '../utils/logger';
import type { BaseAPIResponse, HealthCheck, DroneEventUnion } from '../types/api';

export interface RetryConfig {
  attempts: number;
  delay: number;
  backoffFactor: number;
  maxDelay: number;
  retryCondition: (error: AxiosError) => boolean;
}

export interface ConnectionPoolConfig {
  maxSockets: number;
  keepAlive: boolean;
  keepAliveMsecs: number;
  timeout: number;
}

export class EnhancedFastAPIClient {
  private client: AxiosInstance;
  private config: ReturnType<ConfigManager['getConfig']>;
  private logger: Logger;
  private healthCheckInterval: NodeJS.Timer | null = null;
  private isHealthy: boolean = false;
  private lastHealthCheck: Date | null = null;
  private performanceMetrics: Map<string, number[]> = new Map();

  constructor() {
    this.config = ConfigManager.getInstance().getConfig();
    this.logger = Logger.getInstance();
    this.client = this.createAxiosInstance();
    this.startHealthMonitoring();
  }

  private createAxiosInstance(): AxiosInstance {
    const { backend } = this.config;

    const instance = axios.create({
      baseURL: backend.baseUrl,
      timeout: backend.timeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'MFG-Drone-MCP-Tools/1.0.0',
      },
      // Connection pooling configuration
      httpAgent: this.createHttpAgent(),
      httpsAgent: this.createHttpAgent(),
    });

    // Request interceptor for logging and metrics
    instance.interceptors.request.use(
      (config) => {
        const requestId = this.generateRequestId();
        config.metadata = { 
          startTime: Date.now(), 
          requestId,
          endpoint: `${config.method?.toUpperCase()} ${config.url}`,
        };
        
        this.logger.debug(`API Request: ${config.metadata.endpoint}`, {
          requestId,
          url: config.url,
          method: config.method,
        });
        
        return config;
      },
      (error) => {
        this.logger.error('Request interceptor error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for logging and metrics
    instance.interceptors.response.use(
      (response) => {
        const { metadata } = response.config;
        const duration = Date.now() - metadata.startTime;
        
        this.recordPerformanceMetric(metadata.endpoint, duration);
        
        this.logger.logAPICall(
          response.config.method?.toUpperCase() || 'UNKNOWN',
          response.config.url || '',
          duration,
          response.status,
          undefined,
          { requestId: metadata.requestId }
        );
        
        return response;
      },
      (error: AxiosError) => {
        const { metadata } = error.config || {};
        const duration = metadata ? Date.now() - metadata.startTime : 0;
        
        if (metadata) {
          this.recordPerformanceMetric(metadata.endpoint, duration, false);
        }
        
        this.logger.logAPICall(
          error.config?.method?.toUpperCase() || 'UNKNOWN',
          error.config?.url || '',
          duration,
          error.response?.status || 0,
          error.message,
          { requestId: metadata?.requestId }
        );
        
        return Promise.reject(error);
      }
    );

    return instance;
  }

  private createHttpAgent(): any {
    // This would normally import http/https agents, but for now return undefined
    // In a real implementation, you'd configure connection pooling here
    return undefined;
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private recordPerformanceMetric(endpoint: string, duration: number, success: boolean = true): void {
    if (!this.performanceMetrics.has(endpoint)) {
      this.performanceMetrics.set(endpoint, []);
    }
    
    const metrics = this.performanceMetrics.get(endpoint)!;
    metrics.push(duration);
    
    // Keep only last 100 measurements
    if (metrics.length > 100) {
      metrics.shift();
    }
    
    // Log slow requests
    if (duration > this.config.performance.targetResponseTime) {
      this.logger.warn(`Slow API request detected: ${endpoint}`, {
        duration,
        target: this.config.performance.targetResponseTime,
        success,
      });
    }
  }

  private async retryRequest<T>(
    requestFn: () => Promise<AxiosResponse<T>>,
    retryConfig?: Partial<RetryConfig>
  ): Promise<AxiosResponse<T>> {
    const config: RetryConfig = {
      attempts: this.config.backend.retries,
      delay: this.config.backend.retryDelay,
      backoffFactor: 2,
      maxDelay: 30000,
      retryCondition: (error: AxiosError) => {
        // Retry on network errors or 5xx responses
        return !error.response || (error.response.status >= 500 && error.response.status < 600);
      },
      ...retryConfig,
    };

    let lastError: AxiosError;
    let delay = config.delay;

    for (let attempt = 1; attempt <= config.attempts; attempt++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error as AxiosError;
        
        if (attempt === config.attempts || !config.retryCondition(lastError)) {
          throw lastError;
        }

        this.logger.warn(`Request failed, retrying (${attempt}/${config.attempts})`, {
          error: lastError.message,
          delay,
          attempt,
        });

        await this.sleep(delay);
        delay = Math.min(delay * config.backoffFactor, config.maxDelay);
      }
    }

    throw lastError!;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Connection management
  public async connect(): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.post<BaseAPIResponse>('/drone/connect');
      return response;
    }).then(response => response.data);
  }

  public async disconnect(): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.post<BaseAPIResponse>('/drone/disconnect');
      return response;
    }).then(response => response.data);
  }

  public async getStatus(): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.get<BaseAPIResponse>('/drone/status');
      return response;
    }).then(response => response.data);
  }

  // Flight control
  public async takeoff(): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.post<BaseAPIResponse>('/drone/takeoff');
      return response;
    }, { attempts: 1 }).then(response => response.data); // No retry for critical flight commands
  }

  public async land(): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.post<BaseAPIResponse>('/drone/land');
      return response;
    }, { attempts: 1 }).then(response => response.data);
  }

  public async emergency(): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.post<BaseAPIResponse>('/drone/emergency');
      return response;
    }, { attempts: 1 }).then(response => response.data);
  }

  // Movement control
  public async move(direction: string, distance: number): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.post<BaseAPIResponse>('/drone/move', {
        direction,
        distance,
      });
      return response;
    }).then(response => response.data);
  }

  public async rotate(direction: string, angle: number): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.post<BaseAPIResponse>('/drone/rotate', {
        direction,
        angle,
      });
      return response;
    }).then(response => response.data);
  }

  // Sensor data
  public async getSensorData(): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.get<BaseAPIResponse>('/drone/sensors');
      return response;
    }).then(response => response.data);
  }

  public async getBattery(): Promise<BaseAPIResponse> {
    return this.retryRequest(async () => {
      const response = await this.client.get<BaseAPIResponse>('/drone/battery');
      return response;
    }).then(response => response.data);
  }

  // Health monitoring
  public async healthCheck(): Promise<HealthCheck> {
    try {
      const response = await this.client.get<HealthCheck>('/health', { timeout: 5000 });
      this.isHealthy = response.data.status === 'healthy';
      this.lastHealthCheck = new Date();
      return response.data;
    } catch (error) {
      this.isHealthy = false;
      this.lastHealthCheck = new Date();
      throw error;
    }
  }

  private startHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }

    this.healthCheckInterval = setInterval(async () => {
      try {
        await this.healthCheck();
        if (this.isHealthy) {
          this.logger.debug('Health check passed');
        }
      } catch (error) {
        this.logger.warn('Health check failed', { error: (error as Error).message });
      }
    }, 30000); // Check every 30 seconds
  }

  public getHealthStatus(): { isHealthy: boolean; lastCheck: Date | null } {
    return {
      isHealthy: this.isHealthy,
      lastCheck: this.lastHealthCheck,
    };
  }

  public getPerformanceMetrics(): Record<string, { avg: number; min: number; max: number; count: number }> {
    const result: Record<string, { avg: number; min: number; max: number; count: number }> = {};
    
    this.performanceMetrics.forEach((durations, endpoint) => {
      const avg = durations.reduce((sum, d) => sum + d, 0) / durations.length;
      const min = Math.min(...durations);
      const max = Math.max(...durations);
      
      result[endpoint] = { avg, min, max, count: durations.length };
    });
    
    return result;
  }

  public resetMetrics(): void {
    this.performanceMetrics.clear();
  }

  public destroy(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }
}