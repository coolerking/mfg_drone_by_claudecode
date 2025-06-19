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

export interface DroneAcceleration {
  x: number;
  y: number;
  z: number;
}

export interface DroneAttitude {
  pitch: number;
  roll: number;
  yaw: number;
}

export interface DroneSensorData {
  battery: number;
  height: number;
  temperature: number;
  flight_time: number;
  barometer: number;
  distance_tof: number;
  acceleration: DroneAcceleration;
  velocity: DroneVelocity;
  attitude: DroneAttitude;
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
  target_position?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface ModelInfo {
  name: string;
  created_at: string;
  accuracy: number;
}

export interface ModelListResponse {
  models: ModelInfo[];
}

export type DroneDirection = 'up' | 'down' | 'left' | 'right' | 'forward' | 'back';
export type RotationDirection = 'clockwise' | 'counter_clockwise';
export type FlipDirection = 'left' | 'right' | 'forward' | 'back';
export type CameraResolution = 'high' | 'low';
export type CameraFPS = 'high' | 'middle' | 'low';
export type TrackingMode = 'center' | 'follow';
export type MissionPadDetectionDirection = 0 | 1 | 2;