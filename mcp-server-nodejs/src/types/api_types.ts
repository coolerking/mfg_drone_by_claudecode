import { z } from 'zod';

// ========================================
// Common API Types
// ========================================

export const SuccessResponseSchema = z.object({
  success: z.boolean().default(true),
  message: z.string(),
  timestamp: z.string().datetime(),
});

export type SuccessResponse = z.infer<typeof SuccessResponseSchema>;

export const ErrorResponseSchema = z.object({
  error: z.boolean().default(true),
  error_code: z.string(),
  message: z.string(),
  details: z.string().optional(),
  timestamp: z.string().datetime(),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

// ========================================
// Drone API Types
// ========================================

export const AttitudeSchema = z.object({
  pitch: z.number().min(-180).max(180),
  roll: z.number().min(-180).max(180),
  yaw: z.number().min(-180).max(180),
});

export type Attitude = z.infer<typeof AttitudeSchema>;

export const DroneSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.enum(['real', 'dummy']),
  ip_address: z.string().ip().optional(),
  status: z.enum(['disconnected', 'connected', 'flying', 'landed', 'error']),
  last_seen: z.string().datetime(),
});

export type Drone = z.infer<typeof DroneSchema>;

export const DroneStatusSchema = z.object({
  drone_id: z.string(),
  connection_status: z.enum(['disconnected', 'connected', 'error']),
  flight_status: z.enum(['landed', 'flying', 'hovering', 'landing', 'taking_off']),
  battery_level: z.number().min(0).max(100),
  flight_time: z.number().min(0),
  height: z.number().min(0),
  temperature: z.number(),
  speed: z.number().min(0),
  wifi_signal: z.number().min(0).max(100),
  attitude: AttitudeSchema.optional(),
  last_updated: z.string().datetime(),
});

export type DroneStatus = z.infer<typeof DroneStatusSchema>;

export const MoveCommandSchema = z.object({
  direction: z.enum(['up', 'down', 'left', 'right', 'forward', 'back']),
  distance: z.number().min(20).max(500),
});

export type MoveCommand = z.infer<typeof MoveCommandSchema>;

export const RotateCommandSchema = z.object({
  direction: z.enum(['clockwise', 'counter_clockwise']),
  angle: z.number().min(1).max(360),
});

export type RotateCommand = z.infer<typeof RotateCommandSchema>;

export const PhotoSchema = z.object({
  id: z.string(),
  filename: z.string(),
  path: z.string(),
  timestamp: z.string().datetime(),
  drone_id: z.string(),
  metadata: z.record(z.unknown()).optional(),
});

export type Photo = z.infer<typeof PhotoSchema>;

// ========================================
// Vision API Types
// ========================================

export const DatasetSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().optional(),
  image_count: z.number().min(0),
  labels: z.array(z.string()),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type Dataset = z.infer<typeof DatasetSchema>;

export const CreateDatasetRequestSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
});

export type CreateDatasetRequest = z.infer<typeof CreateDatasetRequestSchema>;

export const DatasetImageSchema = z.object({
  id: z.string(),
  filename: z.string(),
  path: z.string(),
  label: z.string(),
  dataset_id: z.string(),
  uploaded_at: z.string().datetime(),
});

export type DatasetImage = z.infer<typeof DatasetImageSchema>;

export const BoundingBoxSchema = z.object({
  x: z.number(),
  y: z.number(),
  width: z.number(),
  height: z.number(),
});

export type BoundingBox = z.infer<typeof BoundingBoxSchema>;

export const DetectionSchema = z.object({
  label: z.string(),
  confidence: z.number().min(0).max(1),
  bbox: BoundingBoxSchema,
});

export type Detection = z.infer<typeof DetectionSchema>;

export const DetectionRequestSchema = z.object({
  image: z.string(), // Base64 encoded
  model_id: z.string(),
  confidence_threshold: z.number().min(0).max(1).default(0.5),
});

export type DetectionRequest = z.infer<typeof DetectionRequestSchema>;

export const DetectionResultSchema = z.object({
  detections: z.array(DetectionSchema),
  processing_time: z.number(),
  model_id: z.string(),
});

export type DetectionResult = z.infer<typeof DetectionResultSchema>;

export const StartTrackingRequestSchema = z.object({
  model_id: z.string(),
  drone_id: z.string(),
  confidence_threshold: z.number().min(0).max(1).default(0.5),
  follow_distance: z.number().min(50).max(500).default(200),
});

export type StartTrackingRequest = z.infer<typeof StartTrackingRequestSchema>;

export const TrackingStatusSchema = z.object({
  is_active: z.boolean(),
  model_id: z.string().optional(),
  drone_id: z.string().optional(),
  target_detected: z.boolean(),
  target_position: BoundingBoxSchema.optional(),
  follow_distance: z.number().optional(),
  last_detection_time: z.string().datetime().optional(),
  started_at: z.string().datetime().optional(),
});

export type TrackingStatus = z.infer<typeof TrackingStatusSchema>;

// ========================================
// Model API Types
// ========================================

export const TrainingParamsSchema = z.object({
  epochs: z.number().min(1).max(1000).default(100),
  batch_size: z.number().min(1).max(64).default(16),
  learning_rate: z.number().min(0.00001).max(1).default(0.001),
  validation_split: z.number().min(0.1).max(0.5).default(0.2),
});

export type TrainingParams = z.infer<typeof TrainingParamsSchema>;

export const ModelSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().optional(),
  dataset_id: z.string(),
  model_type: z.enum(['yolo', 'ssd', 'faster_rcnn']),
  status: z.enum(['training', 'completed', 'failed']),
  accuracy: z.number().min(0).max(1).optional(),
  file_path: z.string().optional(),
  created_at: z.string().datetime(),
  trained_at: z.string().datetime().optional(),
});

export type Model = z.infer<typeof ModelSchema>;

export const TrainModelRequestSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  dataset_id: z.string(),
  model_type: z.enum(['yolo', 'ssd', 'faster_rcnn']).default('yolo'),
  training_params: TrainingParamsSchema.optional(),
});

export type TrainModelRequest = z.infer<typeof TrainModelRequestSchema>;

export const TrainingJobSchema = z.object({
  id: z.string(),
  model_name: z.string(),
  dataset_id: z.string(),
  status: z.enum(['queued', 'running', 'completed', 'failed', 'cancelled']),
  progress: z.number().min(0).max(100),
  current_epoch: z.number().min(0),
  total_epochs: z.number().min(1),
  loss: z.number().min(0).optional(),
  accuracy: z.number().min(0).max(1).optional(),
  estimated_remaining_time: z.number().min(0),
  started_at: z.string().datetime(),
  completed_at: z.string().datetime().optional(),
  error_message: z.string().optional(),
});

export type TrainingJob = z.infer<typeof TrainingJobSchema>;

// ========================================
// Dashboard API Types
// ========================================

export const SystemStatusSchema = z.object({
  cpu_usage: z.number().min(0).max(100),
  memory_usage: z.number().min(0).max(100),
  disk_usage: z.number().min(0).max(100),
  temperature: z.number(),
  connected_drones: z.number().min(0),
  active_tracking: z.number().min(0),
  running_training_jobs: z.number().min(0),
  uptime: z.number().min(0),
  last_updated: z.string().datetime(),
});

export type SystemStatus = z.infer<typeof SystemStatusSchema>;

// ========================================
// API Response Types
// ========================================

export const ScanDronesResponseSchema = z.object({
  message: z.string(),
  found: z.number().min(0),
});

export type ScanDronesResponse = z.infer<typeof ScanDronesResponseSchema>;

export const HealthCheckResponseSchema = z.object({
  status: z.string(),
  timestamp: z.string().datetime(),
});

export type HealthCheckResponse = z.infer<typeof HealthCheckResponseSchema>;

export const CommandResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
});

export type CommandResponse = z.infer<typeof CommandResponseSchema>;

// ========================================
// API Error Codes
// ========================================

export const API_ERROR_CODES = {
  INVALID_REQUEST: 'INVALID_REQUEST',
  INVALID_COMMAND: 'INVALID_COMMAND',
  DRONE_NOT_FOUND: 'DRONE_NOT_FOUND',
  DRONE_NOT_READY: 'DRONE_NOT_READY',
  DRONE_ALREADY_CONNECTED: 'DRONE_ALREADY_CONNECTED',
  DRONE_UNAVAILABLE: 'DRONE_UNAVAILABLE',
  DATASET_NOT_FOUND: 'DATASET_NOT_FOUND',
  MODEL_NOT_FOUND: 'MODEL_NOT_FOUND',
  JOB_NOT_FOUND: 'JOB_NOT_FOUND',
  TRACKING_ALREADY_ACTIVE: 'TRACKING_ALREADY_ACTIVE',
  INTERNAL_SERVER_ERROR: 'INTERNAL_SERVER_ERROR',
} as const;

export type ApiErrorCode = typeof API_ERROR_CODES[keyof typeof API_ERROR_CODES];

// ========================================
// Utility Types
// ========================================

export type ApiResponse<T> = {
  data: T;
  status: number;
  statusText: string;
};

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
};

export type FileUploadFormData = {
  file: File;
  label?: string;
};

// ========================================
// API Client Configuration
// ========================================

export const DefaultBackendConfigSchema = z.object({
  baseURL: z.string().url().default('http://localhost:8000'),
  timeout: z.number().positive().default(30000),
  retries: z.number().min(0).max(5).default(3),
  retryDelay: z.number().positive().default(1000),
});

export type DefaultBackendConfig = z.infer<typeof DefaultBackendConfigSchema>;