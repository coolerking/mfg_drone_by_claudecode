// API Response Types based on OpenAPI specification

export interface StatusResponse {
  success: boolean;
  message: string;
}

export interface ErrorResponse {
  error: string;
  code: ErrorCode;
  details?: Record<string, unknown>;
}

export type ErrorCode =
  | 'DRONE_NOT_CONNECTED'
  | 'DRONE_CONNECTION_FAILED'
  | 'INVALID_PARAMETER'
  | 'COMMAND_FAILED'
  | 'COMMAND_TIMEOUT'
  | 'NOT_FLYING'
  | 'ALREADY_FLYING'
  | 'STREAMING_NOT_STARTED'
  | 'STREAMING_ALREADY_STARTED'
  | 'MODEL_NOT_FOUND'
  | 'TRAINING_IN_PROGRESS'
  | 'FILE_TOO_LARGE'
  | 'UNSUPPORTED_FORMAT'
  | 'INTERNAL_ERROR';

export interface DroneStatus {
  connected: boolean;
  battery: number;
  height: number;
  temperature: number;
  flight_time: number;
  speed: number;
  barometer: number;
  distance_tof: number;
  acceleration: {
    x: number;
    y: number;
    z: number;
  };
  velocity: {
    x: number;
    y: number;
    z: number;
  };
  attitude: {
    pitch: number;
    roll: number;
    yaw: number;
  };
}

export interface BatteryResponse {
  battery: number;
}

export interface HeightResponse {
  height: number;
}

export interface TemperatureResponse {
  temperature: number;
}

export interface FlightTimeResponse {
  flight_time: number;
}

export interface BarometerResponse {
  barometer: number;
}

export interface DistanceTofResponse {
  distance_tof: number;
}

export interface AccelerationResponse {
  acceleration: {
    x: number;
    y: number;
    z: number;
  };
}

export interface VelocityResponse {
  velocity: {
    x: number;
    y: number;
    z: number;
  };
}

export interface AttitudeResponse {
  attitude: {
    pitch: number;
    roll: number;
    yaw: number;
  };
}

export interface MissionPadStatus {
  mission_pad_id: number;
  distance_x: number;
  distance_y: number;
  distance_z: number;
}

export interface TrackingStatus {
  is_tracking: boolean;
  target_object: string;
  target_detected: boolean;
  target_position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface ModelTrainResponse {
  task_id: string;
}

export interface ModelListResponse {
  models: Array<{
    name: string;
    created_at: string;
    accuracy: number;
  }>;
}

export interface CommandResponse {
  success: boolean;
  response: string;
}

// Request payload types
export interface MoveRequest {
  direction: 'up' | 'down' | 'left' | 'right' | 'forward' | 'back';
  distance: number;
}

export interface RotateRequest {
  direction: 'clockwise' | 'counter_clockwise';
  angle: number;
}

export interface FlipRequest {
  direction: 'left' | 'right' | 'forward' | 'back';
}

export interface GoXyzRequest {
  x: number;
  y: number;
  z: number;
  speed: number;
}

export interface CurveXyzRequest {
  x1: number;
  y1: number;
  z1: number;
  x2: number;
  y2: number;
  z2: number;
  speed: number;
}

export interface RcControlRequest {
  left_right_velocity: number;
  forward_backward_velocity: number;
  up_down_velocity: number;
  yaw_velocity: number;
}

export interface CameraSettingsRequest {
  resolution?: 'high' | 'low';
  fps?: 'high' | 'middle' | 'low';
  bitrate?: number;
}

export interface WiFiRequest {
  ssid: string;
  password: string;
}

export interface CommandRequest {
  command: string;
  timeout?: number;
  expect_response?: boolean;
}

export interface SpeedRequest {
  speed: number;
}

export interface MissionPadDetectionDirectionRequest {
  direction: 0 | 1 | 2;
}

export interface MissionPadGoXyzRequest {
  x: number;
  y: number;
  z: number;
  speed: number;
  mission_pad_id: number;
}

export interface TrackingStartRequest {
  target_object: string;
  tracking_mode?: 'center' | 'follow';
}