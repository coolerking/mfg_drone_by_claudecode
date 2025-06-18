import { readFileSync, existsSync } from 'fs';
import { ServerConfig, EnvironmentConfig, DEFAULT_CONFIG } from '../types/config.js';

/**
 * Load configuration from JSON file and environment variables
 */
export function loadConfig(configPath?: string): ServerConfig {
  let config = { ...DEFAULT_CONFIG };

  // Load from JSON file if provided
  if (configPath && existsSync(configPath)) {
    try {
      const fileConfig = JSON.parse(readFileSync(configPath, 'utf-8'));
      config = { ...config, ...fileConfig };
    } catch (error) {
      console.warn(`Failed to load config file ${configPath}:`, error);
    }
  }

  // Override with environment variables
  const envConfig = loadFromEnvironment();
  config = { ...config, ...envConfig };

  // Validate configuration
  validateConfig(config);

  return config;
}

/**
 * Load configuration from environment variables
 */
function loadFromEnvironment(): Partial<ServerConfig> {
  const env = process.env as EnvironmentConfig;
  const config: Partial<ServerConfig> = {};

  if (env.BACKEND_URL) {
    config.backendUrl = env.BACKEND_URL;
  }

  if (env.DEBUG) {
    config.debug = env.DEBUG.toLowerCase() === 'true';
  }

  if (env.LOG_FILE) {
    config.logFile = env.LOG_FILE;
  }

  if (env.TIMEOUT) {
    const timeout = parseInt(env.TIMEOUT, 10);
    if (!isNaN(timeout) && timeout > 0) {
      config.timeout = timeout;
    }
  }

  if (env.RETRY_ATTEMPTS) {
    const retryAttempts = parseInt(env.RETRY_ATTEMPTS, 10);
    if (!isNaN(retryAttempts) && retryAttempts >= 0) {
      config.retryAttempts = retryAttempts;
    }
  }

  if (env.RETRY_DELAY) {
    const retryDelay = parseInt(env.RETRY_DELAY, 10);
    if (!isNaN(retryDelay) && retryDelay >= 0) {
      config.retryDelay = retryDelay;
    }
  }

  if (env.MAX_LOG_SIZE) {
    const maxLogSize = parseInt(env.MAX_LOG_SIZE, 10);
    if (!isNaN(maxLogSize) && maxLogSize > 0) {
      config.maxLogSize = maxLogSize;
    }
  }

  if (env.HEALTH_CHECK_INTERVAL) {
    const healthCheckInterval = parseInt(env.HEALTH_CHECK_INTERVAL, 10);
    if (!isNaN(healthCheckInterval) && healthCheckInterval > 0) {
      config.healthCheckInterval = healthCheckInterval;
    }
  }

  return config;
}

/**
 * Validate configuration values
 */
function validateConfig(config: ServerConfig): void {
  if (!config.backendUrl) {
    throw new Error('Backend URL is required');
  }

  if (!isValidUrl(config.backendUrl)) {
    throw new Error('Invalid backend URL format');
  }

  if (config.timeout <= 0) {
    throw new Error('Timeout must be positive');
  }

  if (config.retryAttempts < 0) {
    throw new Error('Retry attempts must be non-negative');
  }

  if (config.retryDelay < 0) {
    throw new Error('Retry delay must be non-negative');
  }

  if (config.maxLogSize <= 0) {
    throw new Error('Max log size must be positive');
  }

  if (config.healthCheckInterval <= 0) {
    throw new Error('Health check interval must be positive');
  }
}

/**
 * Check if URL is valid
 */
function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Get configuration for specific environment
 */
export function getConfigForEnvironment(env: string = 'development'): string {
  const configFiles = {
    development: './config/development.json',
    production: './config/production.json',
    test: './config/test.json',
  };

  return configFiles[env as keyof typeof configFiles] || configFiles.development;
}