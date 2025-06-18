import { z } from 'zod';

export const ServerConfigSchema = z.object({
  server: z.object({
    name: z.string(),
    version: z.string(),
  }),
  backend: z.object({
    baseUrl: z.string().url(),
    timeout: z.number().positive(),
    retries: z.number().min(0),
    retryDelay: z.number().positive(),
    keepAlive: z.boolean(),
    maxSockets: z.number().positive(),
  }),
  websocket: z.object({
    enabled: z.boolean(),
    reconnectInterval: z.number().positive(),
    maxReconnectAttempts: z.number().positive(),
    pingInterval: z.number().positive(),
  }),
  logging: z.object({
    level: z.enum(['error', 'warn', 'info', 'debug']),
    format: z.enum(['json', 'pretty']),
    file: z.object({
      enabled: z.boolean(),
      filename: z.string(),
      maxSize: z.string(),
      maxFiles: z.number().positive(),
    }),
  }),
  performance: z.object({
    targetResponseTime: z.number().positive(),
    enableMetrics: z.boolean(),
    metricsInterval: z.number().positive(),
  }),
  debug: z.boolean(),
});

export type ServerConfig = z.infer<typeof ServerConfigSchema>;

export interface RuntimeConfig extends ServerConfig {
  environment: 'development' | 'production' | 'test';
  startTime: Date;
}

export interface LogContext {
  toolName?: string;
  requestId?: string;
  duration?: number;
  error?: string;
  [key: string]: unknown;
}

export interface PerformanceMetrics {
  timestamp: Date;
  toolName: string;
  duration: number;
  success: boolean;
  error?: string;
}