/**
 * TypeScript Type Definitions for MCP Drone Control Server
 * 
 * This module provides comprehensive type definitions for the MCP Drone Control Server API,
 * including natural language commands, drone operations, camera controls, and system monitoring.
 */

// ===================
// Core Types
// ===================

/**
 * HTTP methods supported by the API
 */
export type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

/**
 * Timestamp string in ISO 8601 format
 */
export type Timestamp = string;

/**
 * Drone ID string
 */
export type DroneId = string;

/**
 * Model ID string for AI/ML models
 */
export type ModelId = string;

/**
 * Operation ID string
 */
export type OperationId = string;

// ===================
// Client Configuration
// ===================

/**
 * MCP Client configuration
 */
export interface MCPClientConfig {
  /** Base URL of the MCP server */
  baseURL: string;
  /** API key for authentication */
  apiKey?: string;
  /** Bearer token for authentication */
  bearerToken?: string;
  /** Request timeout in milliseconds */
  timeout?: number;
}

// ===================
// Natural Language Commands
// ===================

/**
 * Natural language command request
 */
export interface NaturalLanguageCommand {
  /** The natural language command text */
  command: string;
  /** Additional context for command execution */
  context?: {
    /** Target drone ID */
    drone_id?: string;
    /** Language setting */
    language?: string;
    [key: string]: any;
  };
  /** Execution options */
  options?: {
    /** Require confirmation before execution */
    confirm_before_execution?: boolean;
    /** Dry run mode (don't actually execute) */
    dry_run?: boolean;
    [key: string]: any;
  };
}

/**
 * Batch command request
 */
export interface BatchCommand {
  /** Array of commands to execute */
  commands: NaturalLanguageCommand[];
  /** Execution mode */
  execution_mode?: 'sequential' | 'parallel';
  /** Stop execution on first error */
  stop_on_error?: boolean;
}

/**
 * Parsed command intent
 */
export interface ParsedIntent {
  /** The action to be performed */
  action: string;
  /** Extracted parameters */
  parameters: Record<string, any>;
  /** Confidence score (0-1) */
  confidence: number;
}

/**
 * Command execution details
 */
export interface ExecutionDetails {
  /** Backend API calls made */
  backend_calls: Array<{
    endpoint: string;
    method: HTTPMethod;
    status: number;
    response_time: number;
    [key: string]: any;
  }>;
  /** Total execution time in seconds */
  execution_time: number;
}

/**
 * Command execution response
 */
export interface CommandResponse {
  /** Success flag */
  success: boolean;
  /** Response message */
  message: string;
  /** Parsed intent information */
  parsed_intent?: ParsedIntent;
  /** Execution details */
  execution_details?: ExecutionDetails;
  /** Result data */
  result?: Record<string, any>;
  /** Response timestamp */
  timestamp: Timestamp;
}

/**
 * Batch command execution summary
 */
export interface BatchExecutionSummary {
  /** Total number of commands */
  total_commands: number;
  /** Number of successful commands */
  successful_commands: number;
  /** Number of failed commands */
  failed_commands: number;
  /** Total execution time in seconds */
  total_execution_time: number;
}

/**
 * Batch command execution response
 */
export interface BatchCommandResponse {
  /** Overall success flag */
  success: boolean;
  /** Overall response message */
  message: string;
  /** Individual command results */
  results: CommandResponse[];
  /** Execution summary */
  summary: BatchExecutionSummary;
  /** Response timestamp */
  timestamp: Timestamp;
}

// ===================
// Drone Management
// ===================

/**
 * Drone types
 */
export type DroneType = 'real' | 'dummy';

/**
 * Drone status values
 */
export type DroneStatus = 'available' | 'connected' | 'busy' | 'offline' | 'error';

/**
 * Connection status values
 */
export type ConnectionStatus = 'disconnected' | 'connected' | 'error';

/**
 * Flight status values
 */
export type FlightStatus = 'landed' | 'flying' | 'hovering' | 'landing' | 'taking_off';

/**
 * Drone information
 */
export interface DroneInfo {
  /** Unique drone identifier */
  id: DroneId;
  /** Human-readable drone name */
  name: string;
  /** Drone type */
  type: DroneType;
  /** Current status */
  status: DroneStatus;
  /** Available capabilities */
  capabilities: string[];
  /** Last seen timestamp */
  last_seen?: Timestamp;
}

/**
 * Drone list response
 */
export interface DroneListResponse {
  /** Array of drone information */
  drones: DroneInfo[];
  /** Total number of drones */
  count: number;
  /** Optional message */
  message?: string;
  /** Response timestamp */
  timestamp: Timestamp;
}

/**
 * Detailed drone status
 */
export interface DroneDetailedStatus {
  /** Connection status */
  connection_status: ConnectionStatus;
  /** Flight status */
  flight_status: FlightStatus;
  /** Battery level (0-100) */
  battery_level: number;
  /** Current height in cm */
  height: number;
  /** Temperature in Celsius */
  temperature: number;
  /** WiFi signal strength (0-100) */
  wifi_signal: number;
}

/**
 * Drone status response
 */
export interface DroneStatusResponse {
  /** Drone identifier */
  drone_id: DroneId;
  /** Detailed status information */
  status: DroneDetailedStatus;
  /** Optional status message */
  message?: string;
  /** Response timestamp */
  timestamp: Timestamp;
}

// ===================
// Drone Control Commands
// ===================

/**
 * Takeoff command parameters
 */
export interface TakeoffCommand {
  /** Target height in cm (20-300) */
  target_height?: number;
  /** Perform safety check before takeoff */
  safety_check?: boolean;
}

/**
 * Movement directions
 */
export type MovementDirection = 'up' | 'down' | 'left' | 'right' | 'forward' | 'back';

/**
 * Move command parameters
 */
export interface MoveCommand {
  /** Movement direction */
  direction: MovementDirection;
  /** Distance in cm (20-500) */
  distance: number;
  /** Speed in cm/s (10-100) */
  speed?: number;
}

/**
 * Rotation directions
 */
export type RotationDirection = 'clockwise' | 'counter_clockwise' | 'left' | 'right';

/**
 * Rotate command parameters
 */
export interface RotateCommand {
  /** Rotation direction */
  direction: RotationDirection;
  /** Angle in degrees (1-360) */
  angle: number;
}

/**
 * Altitude modes
 */
export type AltitudeMode = 'absolute' | 'relative';

/**
 * Altitude command parameters
 */
export interface AltitudeCommand {
  /** Target height in cm (20-300) */
  target_height: number;
  /** Altitude mode */
  mode?: AltitudeMode;
}

/**
 * Basic operation response
 */
export interface OperationResponse {
  /** Success flag */
  success: boolean;
  /** Response message */
  message: string;
  /** Operation identifier */
  operation_id?: OperationId;
  /** Execution time in seconds */
  execution_time?: number;
  /** Response timestamp */
  timestamp: Timestamp;
}

// ===================
// Camera & Photo Operations
// ===================

/**
 * Photo quality options
 */
export type PhotoQuality = 'high' | 'medium' | 'low';

/**
 * Photo command parameters
 */
export interface PhotoCommand {
  /** Photo filename */
  filename?: string;
  /** Photo quality */
  quality?: PhotoQuality;
  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * Photo information
 */
export interface PhotoInfo {
  /** Photo identifier */
  id: string;
  /** Filename */
  filename: string;
  /** File path */
  path: string;
  /** File size in bytes */
  size: number;
  /** Photo timestamp */
  timestamp: Timestamp;
}

/**
 * Photo response
 */
export interface PhotoResponse {
  /** Success flag */
  success: boolean;
  /** Response message */
  message: string;
  /** Photo information */
  photo?: PhotoInfo;
  /** Response timestamp */
  timestamp: Timestamp;
}

/**
 * Streaming actions
 */
export type StreamingAction = 'start' | 'stop';

/**
 * Streaming quality options
 */
export type StreamingQuality = 'high' | 'medium' | 'low';

/**
 * Streaming resolution options
 */
export type StreamingResolution = '720p' | '480p' | '360p';

/**
 * Streaming command parameters
 */
export interface StreamingCommand {
  /** Streaming action */
  action: StreamingAction;
  /** Streaming quality */
  quality?: StreamingQuality;
  /** Streaming resolution */
  resolution?: StreamingResolution;
}

// ===================
// Learning Data Collection
// ===================

/**
 * Capture positions for learning data
 */
export type CapturePosition = 'front' | 'back' | 'left' | 'right' | 'top' | 'bottom';

/**
 * Learning data collection command
 */
export interface LearningDataCommand {
  /** Name of the object to learn */
  object_name: string;
  /** Positions to capture from */
  capture_positions?: CapturePosition[];
  /** Movement distance in cm (20-100) */
  movement_distance?: number;
  /** Number of photos per position (1-10) */
  photos_per_position?: number;
  /** Dataset name */
  dataset_name?: string;
}

/**
 * Learning dataset information
 */
export interface LearningDataset {
  /** Dataset identifier */
  id: string;
  /** Dataset name */
  name: string;
  /** Number of images collected */
  image_count: number;
  /** Positions that were captured */
  positions_captured: string[];
}

/**
 * Learning data execution summary
 */
export interface LearningExecutionSummary {
  /** Total number of moves */
  total_moves: number;
  /** Total number of photos */
  total_photos: number;
  /** Total execution time in seconds */
  execution_time: number;
}

/**
 * Learning data collection response
 */
export interface LearningDataResponse {
  /** Success flag */
  success: boolean;
  /** Response message */
  message: string;
  /** Created dataset information */
  dataset?: LearningDataset;
  /** Execution summary */
  execution_summary?: LearningExecutionSummary;
  /** Response timestamp */
  timestamp: Timestamp;
}

// ===================
// Vision & AI Operations
// ===================

/**
 * Object detection command
 */
export interface DetectionCommand {
  /** Target drone ID */
  drone_id: DroneId;
  /** Model ID to use */
  model_id?: ModelId;
  /** Confidence threshold (0-1) */
  confidence_threshold?: number;
}

/**
 * Bounding box coordinates
 */
export interface BoundingBox {
  /** X coordinate */
  x: number;
  /** Y coordinate */
  y: number;
  /** Width */
  width: number;
  /** Height */
  height: number;
}

/**
 * Object detection result
 */
export interface DetectionResult {
  /** Object label */
  label: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Bounding box */
  bbox: BoundingBox;
}

/**
 * Object detection response
 */
export interface DetectionResponse {
  /** Success flag */
  success: boolean;
  /** Response message */
  message: string;
  /** Detection results */
  detections: DetectionResult[];
  /** Processing time in seconds */
  processing_time: number;
  /** Response timestamp */
  timestamp: Timestamp;
}

/**
 * Tracking actions
 */
export type TrackingAction = 'start' | 'stop';

/**
 * Object tracking command
 */
export interface TrackingCommand {
  /** Tracking action */
  action: TrackingAction;
  /** Target drone ID */
  drone_id: DroneId;
  /** Model ID to use */
  model_id?: ModelId;
  /** Follow distance in cm (50-500) */
  follow_distance?: number;
  /** Confidence threshold (0-1) */
  confidence_threshold?: number;
}

// ===================
// System Information
// ===================

/**
 * System health status
 */
export type SystemHealth = 'healthy' | 'degraded' | 'unhealthy';

/**
 * Server status
 */
export type ServerStatus = 'running' | 'stopped' | 'error';

/**
 * MCP server information
 */
export interface MCPServerInfo {
  /** Server status */
  status: ServerStatus;
  /** Uptime in seconds */
  uptime: number;
  /** Server version */
  version: string;
  /** Number of active connections */
  active_connections: number;
}

/**
 * Backend system information
 */
export interface BackendSystemInfo {
  /** Connection status */
  connection_status: ConnectionStatus;
  /** API endpoint URL */
  api_endpoint: string;
  /** Response time in milliseconds */
  response_time: number;
}

/**
 * System status response
 */
export interface SystemStatusResponse {
  /** MCP server information */
  mcp_server: MCPServerInfo;
  /** Backend system information */
  backend_system: BackendSystemInfo;
  /** Number of connected drones */
  connected_drones: number;
  /** Number of active operations */
  active_operations: number;
  /** Overall system health */
  system_health: SystemHealth;
  /** Response timestamp */
  timestamp: Timestamp;
}

/**
 * Health check status
 */
export type HealthStatus = 'healthy' | 'unhealthy';

/**
 * Individual health check result
 */
export type HealthCheckStatus = 'pass' | 'fail';

/**
 * Health check item
 */
export interface HealthCheck {
  /** Check name */
  name: string;
  /** Check status */
  status: HealthCheckStatus;
  /** Check message */
  message: string;
  /** Response time in milliseconds */
  response_time: number;
}

/**
 * Health check response
 */
export interface HealthResponse {
  /** Overall health status */
  status: HealthStatus;
  /** Individual health checks */
  checks: HealthCheck[];
  /** Response timestamp */
  timestamp: Timestamp;
}

// ===================
// Error Handling
// ===================

/**
 * Error codes used by the MCP API
 */
export type ErrorCode = 
  | 'DRONE_NOT_FOUND'
  | 'DRONE_NOT_READY'
  | 'DRONE_ALREADY_CONNECTED'
  | 'DRONE_UNAVAILABLE'
  | 'INVALID_COMMAND'
  | 'MODEL_NOT_FOUND'
  | 'TRACKING_ALREADY_ACTIVE'
  | 'INTERNAL_SERVER_ERROR'
  | 'AUTHENTICATION_FAILED'
  | 'AUTHORIZATION_FAILED'
  | 'RATE_LIMIT_EXCEEDED'
  | 'VALIDATION_ERROR'
  | 'TIMEOUT_ERROR'
  | 'NETWORK_ERROR'
  | 'UNKNOWN_ERROR';

/**
 * Error details
 */
export interface ErrorDetails {
  /** Parsing error details */
  parsing_error?: string;
  /** Suggested corrections */
  suggested_corrections?: string[];
  /** Original command that caused the error */
  original_command?: string;
  /** Additional error context */
  [key: string]: any;
}

/**
 * MCP API error response
 */
export interface MCPError {
  /** Error flag (always true) */
  error: boolean;
  /** Error code */
  error_code: ErrorCode;
  /** Error message */
  message: string;
  /** Additional error details */
  details?: ErrorDetails;
  /** Error timestamp */
  timestamp: Timestamp;
}

// ===================
// WebSocket Events
// ===================

/**
 * WebSocket event types
 */
export type WebSocketEventType = 
  | 'drone_connected'
  | 'drone_disconnected'
  | 'drone_status_changed'
  | 'command_executed'
  | 'operation_completed'
  | 'system_alert'
  | 'error_occurred';

/**
 * WebSocket event data
 */
export interface WebSocketEvent {
  /** Event type */
  type: WebSocketEventType;
  /** Event data */
  data: Record<string, any>;
  /** Event timestamp */
  timestamp: Timestamp;
}

// ===================
// Utility Types
// ===================

/**
 * API response wrapper
 */
export interface APIResponse<T> {
  /** Response data */
  data: T;
  /** Response status code */
  status: number;
  /** Response headers */
  headers: Record<string, string>;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  /** Page number (1-based) */
  page?: number;
  /** Page size */
  limit?: number;
  /** Sort field */
  sort?: string;
  /** Sort order */
  order?: 'asc' | 'desc';
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  /** Response data */
  data: T[];
  /** Total number of items */
  total: number;
  /** Current page */
  page: number;
  /** Page size */
  limit: number;
  /** Total pages */
  pages: number;
}

/**
 * Filter parameters
 */
export interface FilterParams {
  /** Filter by drone type */
  type?: DroneType;
  /** Filter by status */
  status?: DroneStatus;
  /** Filter by capability */
  capability?: string;
  /** Search query */
  search?: string;
}

// ===================
// Constants
// ===================

/**
 * Default configuration values
 */
export const DEFAULT_CONFIG: Partial<MCPClientConfig> = {
  timeout: 30000,
} as const;

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  // Natural Language Commands
  EXECUTE_COMMAND: '/mcp/command',
  EXECUTE_BATCH_COMMAND: '/mcp/command/batch',
  
  // Drone Query
  GET_DRONES: '/mcp/drones',
  GET_AVAILABLE_DRONES: '/mcp/drones/available',
  GET_DRONE_STATUS: (droneId: DroneId) => `/mcp/drones/${droneId}/status`,
  
  // Drone Control
  CONNECT_DRONE: (droneId: DroneId) => `/mcp/drones/${droneId}/connect`,
  DISCONNECT_DRONE: (droneId: DroneId) => `/mcp/drones/${droneId}/disconnect`,
  TAKEOFF_DRONE: (droneId: DroneId) => `/mcp/drones/${droneId}/takeoff`,
  LAND_DRONE: (droneId: DroneId) => `/mcp/drones/${droneId}/land`,
  MOVE_DRONE: (droneId: DroneId) => `/mcp/drones/${droneId}/move`,
  ROTATE_DRONE: (droneId: DroneId) => `/mcp/drones/${droneId}/rotate`,
  EMERGENCY_STOP: (droneId: DroneId) => `/mcp/drones/${droneId}/emergency`,
  SET_ALTITUDE: (droneId: DroneId) => `/mcp/drones/${droneId}/altitude`,
  
  // Camera
  TAKE_PHOTO: (droneId: DroneId) => `/mcp/drones/${droneId}/camera/photo`,
  CONTROL_STREAMING: (droneId: DroneId) => `/mcp/drones/${droneId}/camera/streaming`,
  COLLECT_LEARNING_DATA: (droneId: DroneId) => `/mcp/drones/${droneId}/learning/collect`,
  
  // Vision
  DETECT_OBJECTS: '/mcp/vision/detection',
  CONTROL_TRACKING: '/mcp/vision/tracking',
  
  // System
  GET_SYSTEM_STATUS: '/mcp/system/status',
  GET_HEALTH_CHECK: '/mcp/system/health',
} as const;

/**
 * WebSocket endpoints
 */
export const WEBSOCKET_ENDPOINTS = {
  EVENTS: '/ws',
} as const;

// ===================
// Type Guards
// ===================

/**
 * Type guard for MCP error responses
 */
export function isMCPError(response: any): response is MCPError {
  return response && typeof response === 'object' && response.error === true;
}

/**
 * Type guard for successful responses
 */
export function isSuccessResponse(response: any): response is { success: true } {
  return response && typeof response === 'object' && response.success === true;
}

/**
 * Type guard for drone info
 */
export function isDroneInfo(obj: any): obj is DroneInfo {
  return obj && typeof obj === 'object' && 
         typeof obj.id === 'string' && 
         typeof obj.name === 'string' && 
         ['real', 'dummy'].includes(obj.type);
}

/**
 * Type guard for command response
 */
export function isCommandResponse(obj: any): obj is CommandResponse {
  return obj && typeof obj === 'object' && 
         typeof obj.success === 'boolean' && 
         typeof obj.message === 'string' && 
         typeof obj.timestamp === 'string';
}

// ===================
// Validation Schemas
// ===================

/**
 * Validation constraints
 */
export const VALIDATION_CONSTRAINTS = {
  DRONE_ID: {
    pattern: /^[a-zA-Z0-9_-]+$/,
    maxLength: 50,
  },
  TARGET_HEIGHT: {
    min: 20,
    max: 300,
  },
  MOVE_DISTANCE: {
    min: 20,
    max: 500,
  },
  MOVE_SPEED: {
    min: 10,
    max: 100,
  },
  ROTATION_ANGLE: {
    min: 1,
    max: 360,
  },
  CONFIDENCE_THRESHOLD: {
    min: 0,
    max: 1,
  },
  FOLLOW_DISTANCE: {
    min: 50,
    max: 500,
  },
} as const;

// ===================
// Export All Types
// ===================

export default {
  // Core types
  HTTPMethod,
  Timestamp,
  DroneId,
  ModelId,
  OperationId,
  
  // Configuration
  MCPClientConfig,
  
  // Commands
  NaturalLanguageCommand,
  BatchCommand,
  CommandResponse,
  BatchCommandResponse,
  
  // Drones
  DroneInfo,
  DroneListResponse,
  DroneStatusResponse,
  
  // Control
  TakeoffCommand,
  MoveCommand,
  RotateCommand,
  AltitudeCommand,
  OperationResponse,
  
  // Camera
  PhotoCommand,
  PhotoResponse,
  StreamingCommand,
  LearningDataCommand,
  LearningDataResponse,
  
  // Vision
  DetectionCommand,
  DetectionResponse,
  TrackingCommand,
  
  // System
  SystemStatusResponse,
  HealthResponse,
  
  // Errors
  MCPError,
  ErrorCode,
  
  // WebSocket
  WebSocketEvent,
  
  // Constants
  DEFAULT_CONFIG,
  API_ENDPOINTS,
  WEBSOCKET_ENDPOINTS,
  VALIDATION_CONSTRAINTS,
  
  // Type guards
  isMCPError,
  isSuccessResponse,
  isDroneInfo,
  isCommandResponse,
};