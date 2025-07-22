import dotenv from 'dotenv';
import { ConfigSchema, type Config } from '@/types/index.js';
import { ValidationError } from '@/types/index.js';

// Load environment variables
dotenv.config();

/**
 * 環境変数から設定を読み込む
 */
function loadConfig(): Config {
  const configData = {
    port: process.env.MCP_PORT ? parseInt(process.env.MCP_PORT, 10) : undefined,
    backendUrl: process.env.BACKEND_URL,
    logLevel: process.env.LOG_LEVEL,
    timeout: process.env.TIMEOUT ? parseInt(process.env.TIMEOUT, 10) : undefined,
  };

  // Remove undefined values to let zod apply defaults
  const cleanConfig = Object.fromEntries(
    Object.entries(configData).filter(([, value]) => value !== undefined)
  );

  try {
    return ConfigSchema.parse(cleanConfig);
  } catch (error) {
    throw new ValidationError('Invalid configuration', error);
  }
}

// Export the validated configuration
export const config = loadConfig();

// Type-safe configuration accessor
export function getConfig(): Config {
  return config;
}

// Configuration validation helpers
export function validateBackendConnection(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}

export function isProduction(): boolean {
  return process.env.NODE_ENV === 'production';
}

export function isDevelopment(): boolean {
  return process.env.NODE_ENV === 'development' || !process.env.NODE_ENV;
}