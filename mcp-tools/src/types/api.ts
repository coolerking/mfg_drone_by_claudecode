import { z } from 'zod';

// Basic response schemas
export const StatusResponseSchema = z.object({
  success: z.boolean(),
  message: z.string()
});

export const ErrorResponseSchema = z.object({
  error: z.string(),
  code: z.enum([
    'DRONE_NOT_CONNECTED',
    'DRONE_CONNECTION_FAILED',
    'INVALID_PARAMETER',
    'COMMAND_FAILED',
    'COMMAND_TIMEOUT',
    'NOT_FLYING',
    'ALREADY_FLYING',
    'STREAMING_NOT_STARTED',
    'STREAMING_ALREADY_STARTED',
    'MODEL_NOT_FOUND',
    'TRAINING_IN_PROGRESS',
    'FILE_TOO_LARGE',
    'UNSUPPORTED_FORMAT',
    'INTERNAL_ERROR'
  ]),
  details: z.record(z.unknown()).optional()
});

// Drone status schema
export const DroneStatusSchema = z.object({
  connected: z.boolean(),
  battery: z.number().min(0).max(100),
  height: z.number().min(0).max(3000),
  temperature: z.number().min(0).max(90),
  flight_time: z.number().min(0),
  speed: z.number(),
  barometer: z.number(),
  distance_tof: z.number(),
  acceleration: z.object({
    x: z.number(),
    y: z.number(),
    z: z.number()
  }),
  velocity: z.object({
    x: z.number(),
    y: z.number(),
    z: z.number()
  }),
  attitude: z.object({
    pitch: z.number().min(-180).max(180),
    roll: z.number().min(-180).max(180),
    yaw: z.number().min(-180).max(180)
  })
});

// Request schemas
export const MoveRequestSchema = z.object({
  direction: z.enum(['up', 'down', 'left', 'right', 'forward', 'back']),
  distance: z.number().min(20).max(500)
});

export const RotateRequestSchema = z.object({
  direction: z.enum(['clockwise', 'counter_clockwise']),
  angle: z.number().min(1).max(360)
});

export const FlipRequestSchema = z.object({
  direction: z.enum(['left', 'right', 'forward', 'back'])
});

export const GoXYZRequestSchema = z.object({
  x: z.number().min(-500).max(500),
  y: z.number().min(-500).max(500),
  z: z.number().min(-500).max(500),
  speed: z.number().min(10).max(100)
});

export const CurveXYZRequestSchema = z.object({
  x1: z.number().min(-500).max(500),
  y1: z.number().min(-500).max(500),
  z1: z.number().min(-500).max(500),
  x2: z.number().min(-500).max(500),
  y2: z.number().min(-500).max(500),
  z2: z.number().min(-500).max(500),
  speed: z.number().min(10).max(60)
});

export const RCControlRequestSchema = z.object({
  left_right_velocity: z.number().min(-100).max(100),
  forward_backward_velocity: z.number().min(-100).max(100),
  up_down_velocity: z.number().min(-100).max(100),
  yaw_velocity: z.number().min(-100).max(100)
});

export const CameraSettingsRequestSchema = z.object({
  resolution: z.enum(['high', 'low']).optional(),
  fps: z.enum(['high', 'middle', 'low']).optional(),
  bitrate: z.number().min(1).max(5).optional()
});

export const WiFiRequestSchema = z.object({
  ssid: z.string().max(32),
  password: z.string().max(64)
});

export const SpeedRequestSchema = z.object({
  speed: z.number().min(1.0).max(15.0)
});

export const CommandRequestSchema = z.object({
  command: z.string(),
  timeout: z.number().min(1).max(30).default(7),
  expect_response: z.boolean().default(true)
});

export const MissionPadDirectionRequestSchema = z.object({
  direction: z.enum([0, 1, 2])
});

export const MissionPadGoXYZRequestSchema = z.object({
  x: z.number().min(-500).max(500),
  y: z.number().min(-500).max(500),
  z: z.number().min(-500).max(500),
  speed: z.number().min(10).max(100),
  mission_pad_id: z.number().min(1).max(8)
});

export const TrackingStartRequestSchema = z.object({
  target_object: z.string(),
  tracking_mode: z.enum(['center', 'follow']).default('center')
});

// Type exports
export type StatusResponse = z.infer<typeof StatusResponseSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
export type DroneStatus = z.infer<typeof DroneStatusSchema>;
export type MoveRequest = z.infer<typeof MoveRequestSchema>;
export type RotateRequest = z.infer<typeof RotateRequestSchema>;
export type FlipRequest = z.infer<typeof FlipRequestSchema>;
export type GoXYZRequest = z.infer<typeof GoXYZRequestSchema>;
export type CurveXYZRequest = z.infer<typeof CurveXYZRequestSchema>;
export type RCControlRequest = z.infer<typeof RCControlRequestSchema>;
export type CameraSettingsRequest = z.infer<typeof CameraSettingsRequestSchema>;
export type WiFiRequest = z.infer<typeof WiFiRequestSchema>;
export type SpeedRequest = z.infer<typeof SpeedRequestSchema>;
export type CommandRequest = z.infer<typeof CommandRequestSchema>;
export type MissionPadDirectionRequest = z.infer<typeof MissionPadDirectionRequestSchema>;
export type MissionPadGoXYZRequest = z.infer<typeof MissionPadGoXYZRequestSchema>;
export type TrackingStartRequest = z.infer<typeof TrackingStartRequestSchema>;