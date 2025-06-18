/**
 * API types for communication with FastAPI backend
 * Based on the existing backend/models/responses.py structure
 */

// Base response interface
export interface BaseResponse {
  success: boolean;
  message: string;
  timestamp: string;
}

// Connection responses
export interface ConnectionResponse extends BaseResponse {
  connected: boolean;
}

// Flight control responses
export interface FlightResponse extends BaseResponse {
  /** Current flight state */
  state?: 'landed' | 'flying' | 'hovering' | 'emergency';
  /** Additional flight data */
  data?: Record<string, unknown>;
}

// Status response
export interface StatusResponse extends BaseResponse {
  data: {
    connected: boolean;
    flying: boolean;
    battery: number;
    height: number;
    temperature: number;
    attitude: {
      pitch: number;
      roll: number;
      yaw: number;
    };
    velocity: {
      x: number;
      y: number;
      z: number;
    };
    position: {
      x: number;
      y: number;
      z: number;
    };
  };
}

// Movement response
export interface MovementResponse extends BaseResponse {
  position?: {
    x: number;
    y: number;
    z: number;
  };
}

// Camera response
export interface CameraResponse extends BaseResponse {
  streaming?: boolean;
  resolution?: string;
  fps?: number;
}

// Sensor data response
export interface SensorResponse extends BaseResponse {
  data: {
    battery: number;
    height: number;
    temperature: number;
    barometer: number;
    time_of_flight: number;
    acceleration: {
      x: number;
      y: number;
      z: number;
    };
    attitude: {
      pitch: number;
      roll: number;
      yaw: number;
    };
    velocity: {
      x: number;
      y: number;
      z: number;
    };
  };
}

// Error response
export interface ErrorResponse {
  success: false;
  message: string;
  error_code?: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

// API client response union type
export type APIResponse = 
  | ConnectionResponse
  | FlightResponse
  | StatusResponse
  | MovementResponse
  | CameraResponse
  | SensorResponse
  | ErrorResponse;