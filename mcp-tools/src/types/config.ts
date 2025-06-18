export interface ServerConfig {
  /**
   * FastAPI backend base URL
   */
  backendUrl: string;

  /**
   * HTTP request timeout in milliseconds
   */
  timeout: number;

  /**
   * Number of retry attempts for failed requests
   */
  retryAttempts: number;

  /**
   * Delay between retry attempts in milliseconds
   */
  retryDelay: number;

  /**
   * Enable debug logging
   */
  debug: boolean;

  /**
   * Log file path (optional)
   */
  logFile?: string;

  /**
   * Maximum log file size in bytes
   */
  maxLogSize: number;

  /**
   * Health check interval in milliseconds
   */
  healthCheckInterval: number;
}

export interface EnvironmentConfig {
  NODE_ENV?: string;
  BACKEND_URL?: string;
  DEBUG?: string;
  LOG_FILE?: string;
  TIMEOUT?: string;
  RETRY_ATTEMPTS?: string;
  RETRY_DELAY?: string;
  MAX_LOG_SIZE?: string;
  HEALTH_CHECK_INTERVAL?: string;
}

export const DEFAULT_CONFIG: ServerConfig = {
  backendUrl: 'http://localhost:8000',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
  debug: false,
  maxLogSize: 10 * 1024 * 1024, // 10MB
  healthCheckInterval: 30000, // 30 seconds
};