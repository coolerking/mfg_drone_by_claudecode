/**
 * Configuration management utilities
 * Loads configuration from files and environment variables
 */

import { readFile } from 'fs/promises';
import { resolve } from 'path';
import { ServerConfig, EnvironmentVariables } from '../types/config.js';
import { logger } from './logger.js';

const DEFAULT_CONFIG: ServerConfig = {
  environment: 'development',
  backend: {
    url: 'http://localhost:8000',
    timeout: 30000,
    retries: 3,
    retryDelay: 1000,
    healthCheckInterval: 30000,
  },
  logging: {
    level: 'info',
    structured: true,
  },
};

/**
 * Load configuration from file and environment variables
 */
export async function loadConfig(): Promise<ServerConfig> {
  const env = process.env.NODE_ENV || 'development';
  
  // Load base configuration
  let config: ServerConfig = { ...DEFAULT_CONFIG };
  
  try {
    // Try to load environment-specific config file
    const configPath = resolve(process.cwd(), 'config', `${env}.json`);
    const configFile = await readFile(configPath, 'utf-8');
    const fileConfig = JSON.parse(configFile) as Partial<ServerConfig>;
    
    // Merge configurations
    config = mergeConfig(config, fileConfig);
    logger.debug('Configuration loaded from file', { configPath });
  } catch (error) {
    logger.warn('Could not load config file, using defaults', { 
      environment: env, 
      error: error instanceof Error ? error.message : String(error) 
    });
  }
  
  // Apply environment variable overrides
  config = applyEnvironmentOverrides(config);
  
  // Validate configuration
  validateConfig(config);
  
  return config;
}

/**
 * Merge two configuration objects
 */
function mergeConfig(base: ServerConfig, override: Partial<ServerConfig>): ServerConfig {
  return {
    environment: override.environment || base.environment,
    backend: {
      ...base.backend,
      ...override.backend,
    },
    logging: {
      ...base.logging,
      ...override.logging,
    },
  };
}

/**
 * Apply environment variable overrides
 */
function applyEnvironmentOverrides(config: ServerConfig): ServerConfig {
  const env = process.env as EnvironmentVariables;
  
  const overrides: Partial<ServerConfig> = {};
  
  if (env.NODE_ENV) {
    overrides.environment = env.NODE_ENV as 'development' | 'production' | 'test';
  }
  
  if (env.MCP_BACKEND_URL) {
    overrides.backend = {
      ...config.backend,
      url: env.MCP_BACKEND_URL,
    };
  }
  
  if (env.MCP_BACKEND_TIMEOUT) {
    const timeout = parseInt(env.MCP_BACKEND_TIMEOUT, 10);
    if (!isNaN(timeout)) {
      overrides.backend = {
        ...config.backend,
        ...overrides.backend,
        timeout,
      };
    }
  }
  
  if (env.MCP_LOG_LEVEL) {
    overrides.logging = {
      ...config.logging,
      level: env.MCP_LOG_LEVEL as 'debug' | 'info' | 'warn' | 'error',
    };
  }
  
  if (env.MCP_LOG_FILE) {
    overrides.logging = {
      ...config.logging,
      ...overrides.logging,
      file: env.MCP_LOG_FILE,
    };
  }
  
  return mergeConfig(config, overrides);
}

/**
 * Validate configuration values
 */
function validateConfig(config: ServerConfig): void {
  // Validate environment
  if (!['development', 'production', 'test'].includes(config.environment)) {
    throw new Error(`Invalid environment: ${config.environment}`);
  }
  
  // Validate backend URL
  try {
    new URL(config.backend.url);
  } catch {
    throw new Error(`Invalid backend URL: ${config.backend.url}`);
  }
  
  // Validate timeout
  if (config.backend.timeout <= 0) {
    throw new Error(`Invalid timeout: ${config.backend.timeout}`);
  }
  
  // Validate retries
  if (config.backend.retries < 0) {
    throw new Error(`Invalid retries: ${config.backend.retries}`);
  }
  
  // Validate log level
  if (!['debug', 'info', 'warn', 'error'].includes(config.logging.level)) {
    throw new Error(`Invalid log level: ${config.logging.level}`);
  }
}