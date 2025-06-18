import { z } from 'zod';

// Base API Response Schema
export const BaseAPIResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  timestamp: z.string().optional(),
  data: z.unknown().optional(),
});

export type BaseAPIResponse = z.infer<typeof BaseAPIResponseSchema>;

// Connection API Types
export const ConnectionStatusSchema = z.object({
  connected: z.boolean(),
  drone_ip: z.string().optional(),
  connection_time: z.string().optional(),
  signal_strength: z.number().optional(),
});

export type ConnectionStatus = z.infer<typeof ConnectionStatusSchema>;

// Sensor Data Types
export const SensorDataSchema = z.object({
  battery: z.number().min(0).max(100),
  temperature: z.number(),
  height: z.number(),
  barometer: z.number(),
  distance_tof: z.number(),
  acceleration: z.object({
    x: z.number(),
    y: z.number(),
    z: z.number(),
  }),
  velocity: z.object({
    x: z.number(),
    y: z.number(),
    z: z.number(),
  }),
  attitude: z.object({
    pitch: z.number(),
    roll: z.number(),
    yaw: z.number(),
  }),
  flight_time: z.number(),
});

export type SensorData = z.infer<typeof SensorDataSchema>;

// Movement Parameters
export const MovementParamsSchema = z.object({
  direction: z.enum(['left', 'right', 'forward', 'back', 'up', 'down']),
  distance: z.number().min(20).max(500),
});

export const RotationParamsSchema = z.object({
  direction: z.enum(['cw', 'ccw']),
  angle: z.number().min(1).max(360),
});

export const XYZParamsSchema = z.object({
  x: z.number().min(-500).max(500),
  y: z.number().min(-500).max(500),
  z: z.number().min(-500).max(500),
  speed: z.number().min(10).max(100),
});

export const CurveParamsSchema = z.object({
  x1: z.number().min(-500).max(500),
  y1: z.number().min(-500).max(500),
  z1: z.number().min(-500).max(500),
  x2: z.number().min(-500).max(500),
  y2: z.number().min(-500).max(500),
  z2: z.number().min(-500).max(500),
  speed: z.number().min(10).max(60),
});

export const RCControlParamsSchema = z.object({
  left_right_velocity: z.number().min(-100).max(100),
  forward_backward_velocity: z.number().min(-100).max(100),
  up_down_velocity: z.number().min(-100).max(100),
  yaw_velocity: z.number().min(-100).max(100),
});

// Camera Types
export const CameraSettingsSchema = z.object({
  resolution: z.enum(['720p', '480p']).optional(),
  fps: z.enum([30, 15, 5]).optional(),
  bitrate: z.enum(['auto', 'high', 'medium', 'low']).optional(),
});

export type CameraSettings = z.infer<typeof CameraSettingsSchema>;

// Error Types
export interface APIError extends Error {
  code: string;
  status?: number;
  details?: Record<string, unknown>;
}

// Health Check Types
export const HealthCheckSchema = z.object({
  status: z.enum(['healthy', 'degraded', 'unhealthy']),
  services: z.record(z.string(), z.object({
    status: z.enum(['up', 'down', 'degraded']),
    responseTime: z.number().optional(),
    lastCheck: z.string(),
    error: z.string().optional(),
  })),
  uptime: z.number(),
  version: z.string(),
});

export type HealthCheck = z.infer<typeof HealthCheckSchema>;

// WebSocket Event Types
export interface DroneEvent {
  type: 'status_change' | 'sensor_update' | 'video_frame' | 'error' | 'warning';
  timestamp: string;
  data: unknown;
}

export interface StatusChangeEvent extends DroneEvent {
  type: 'status_change';
  data: {
    previous: string;
    current: string;
    reason?: string;
  };
}

export interface SensorUpdateEvent extends DroneEvent {
  type: 'sensor_update';
  data: SensorData;
}

export interface VideoFrameEvent extends DroneEvent {
  type: 'video_frame';
  data: {
    frame: string; // base64 encoded
    timestamp: string;
    format: 'jpeg' | 'png';
  };
}

export interface ErrorEvent extends DroneEvent {
  type: 'error';
  data: {
    message: string;
    code: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
  };
}

export type DroneEventUnion = StatusChangeEvent | SensorUpdateEvent | VideoFrameEvent | ErrorEvent;