/**
 * Configuration types for the MCP Drone Server
 */

export interface BackendConfig {
  /** Base URL for the FastAPI backend */
  url: string;
  /** API timeout in milliseconds */
  timeout: number;
  /** Maximum number of retry attempts */
  retries: number;
  /** Retry delay in milliseconds */
  retryDelay: number;
  /** Health check interval in milliseconds */
  healthCheckInterval: number;
}

export interface LoggingConfig {
  /** Log level (debug, info, warn, error) */
  level: 'debug' | 'info' | 'warn' | 'error';
  /** Enable structured logging */
  structured: boolean;
  /** Log file path (optional) */
  file?: string;
}

export interface ServerConfig {
  /** Environment (development, production, test) */
  environment: 'development' | 'production' | 'test';
  /** Backend API configuration */
  backend: BackendConfig;
  /** Logging configuration */
  logging: LoggingConfig;
}

export interface EnvironmentVariables {
  NODE_ENV?: string;
  MCP_BACKEND_URL?: string;
  MCP_BACKEND_TIMEOUT?: string;
  MCP_LOG_LEVEL?: string;
  MCP_LOG_FILE?: string;
}