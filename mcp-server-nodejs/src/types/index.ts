import { z } from 'zod';

// Configuration types
export const ConfigSchema = z.object({
  port: z.number().default(3001),
  backendUrl: z.string().default('http://localhost:8000'),
  logLevel: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  timeout: z.number().default(10000),
});

export type Config = z.infer<typeof ConfigSchema>;

// Drone status types
export const DroneStatusSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.enum(['connected', 'disconnected', 'flying', 'idle', 'error']),
  batteryLevel: z.number().min(0).max(100),
  position: z.object({
    x: z.number(),
    y: z.number(),
    z: z.number(),
  }).optional(),
  lastSeen: z.string().datetime(),
});

export type DroneStatus = z.infer<typeof DroneStatusSchema>;

// System status types
export const SystemStatusSchema = z.object({
  status: z.enum(['healthy', 'degraded', 'critical']),
  timestamp: z.string().datetime(),
  services: z.record(z.object({
    status: z.enum(['up', 'down', 'degraded']),
    lastCheck: z.string().datetime(),
    message: z.string().optional(),
  })),
  drones: z.array(DroneStatusSchema),
});

export type SystemStatus = z.infer<typeof SystemStatusSchema>;

// MCP tool request/response types
export const MCPToolRequestSchema = z.object({
  name: z.string(),
  arguments: z.record(z.unknown()).optional(),
});

export type MCPToolRequest = z.infer<typeof MCPToolRequestSchema>;

export const MCPToolResponseSchema = z.object({
  content: z.array(z.object({
    type: z.literal('text'),
    text: z.string(),
  })),
  isError: z.boolean().optional(),
});

export type MCPToolResponse = z.infer<typeof MCPToolResponseSchema>;

// Error types
export class DroneError extends Error {
  constructor(
    message: string,
    public code: string = 'DRONE_ERROR',
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'DroneError';
  }
}

export class ValidationError extends Error {
  constructor(
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class NetworkError extends Error {
  constructor(
    message: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'NetworkError';
  }
}