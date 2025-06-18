// Drone-specific types for MCP tools

export interface DroneConnectionInfo {
  connected: boolean;
  ip?: string;
  port?: number;
  lastConnected?: string;
}

export interface FlightInfo {
  isFlying: boolean;
  altitude: number;
  battery: number;
  flightTime: number;
}

export interface DronePosition {
  x: number;
  y: number;
  z: number;
}

export interface DroneVelocity {
  x: number;
  y: number;
  z: number;
}

export interface DroneAttitude {
  pitch: number;
  roll: number;
  yaw: number;
}

export interface DroneAcceleration {
  x: number;
  y: number;
  z: number;
}

export interface CameraInfo {
  streaming: boolean;
  recording: boolean;
  resolution: 'high' | 'low';
  fps: 'high' | 'middle' | 'low';
  bitrate: number;
}

export interface MissionPadInfo {
  enabled: boolean;
  detectionDirection: 0 | 1 | 2;
  currentPadId: number;
  position: {
    x: number;
    y: number;
    z: number;
  };
}

export interface TrackingInfo {
  active: boolean;
  targetObject: string;
  detected: boolean;
  position?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  mode: 'center' | 'follow';
}

export interface DroneHealth {
  battery: number;
  temperature: number;
  barometer: number;
  tofDistance: number;
  flightTime: number;
  signal: 'strong' | 'medium' | 'weak' | 'none';
}

export interface DroneModel {
  name: string;
  accuracy: number;
  createdAt: string;
  trainingStatus: 'training' | 'completed' | 'failed';
}

// Tool parameter types
export interface BasicMoveParams {
  direction: 'up' | 'down' | 'left' | 'right' | 'forward' | 'back';
  distance: number;
}

export interface RotationParams {
  direction: 'clockwise' | 'counter_clockwise';
  angle: number;
}

export interface FlipParams {
  direction: 'left' | 'right' | 'forward' | 'back';
}

export interface AdvancedMoveParams {
  x: number;
  y: number;
  z: number;
  speed: number;
}

export interface CurveMoveParams {
  x1: number;
  y1: number;
  z1: number;
  x2: number;
  y2: number;
  z2: number;
  speed: number;
}

export interface RCControlParams {
  leftRight: number;
  forwardBackward: number;
  upDown: number;
  yaw: number;
}

export interface CameraSettingsParams {
  resolution?: 'high' | 'low';
  fps?: 'high' | 'middle' | 'low';
  bitrate?: number;
}

export interface TrackingParams {
  targetObject: string;
  mode?: 'center' | 'follow';
}

export interface CustomCommandParams {
  command: string;
  timeout?: number;
  expectResponse?: boolean;
}