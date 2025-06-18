/**
 * Drone-specific types and interfaces
 * Based on Tello EDU capabilities and backend API structure
 */

// Drone connection state
export type DroneConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

// Drone flight state
export type DroneFlightState = 'landed' | 'taking_off' | 'flying' | 'hovering' | 'landing' | 'emergency';

// Movement direction
export type MovementDirection = 'forward' | 'backward' | 'left' | 'right' | 'up' | 'down';

// Rotation direction
export type RotationDirection = 'clockwise' | 'counterclockwise';

// Drone attitude (orientation)
export interface DroneAttitude {
  /** Pitch angle in degrees (-90 to 90) */
  pitch: number;
  /** Roll angle in degrees (-90 to 90) */
  roll: number;
  /** Yaw angle in degrees (-180 to 180) */
  yaw: number;
}

// Drone velocity
export interface DroneVelocity {
  /** Velocity in X direction (cm/s) */
  x: number;
  /** Velocity in Y direction (cm/s) */
  y: number;
  /** Velocity in Z direction (cm/s) */
  z: number;
}

// Drone position
export interface DronePosition {
  /** Position in X coordinate (cm) */
  x: number;
  /** Position in Y coordinate (cm) */
  y: number;
  /** Position in Z coordinate (cm) */
  z: number;
}

// Drone acceleration
export interface DroneAcceleration {
  /** Acceleration in X direction (cm/s²) */
  x: number;
  /** Acceleration in Y direction (cm/s²) */
  y: number;
  /** Acceleration in Z direction (cm/s²) */
  z: number;
}

// Complete drone status
export interface DroneStatus {
  /** Connection state */
  connectionState: DroneConnectionState;
  /** Flight state */
  flightState: DroneFlightState;
  /** Battery level (0-100) */
  battery: number;
  /** Height above ground (cm) */
  height: number;
  /** Temperature (°C) */
  temperature: number;
  /** Barometer reading (cm) */
  barometer: number;
  /** Time of flight sensor distance (cm) */
  timeOfFlight: number;
  /** Drone attitude */
  attitude: DroneAttitude;
  /** Drone velocity */
  velocity: DroneVelocity;
  /** Drone position */
  position: DronePosition;
  /** Drone acceleration */
  acceleration: DroneAcceleration;
  /** Last update timestamp */
  lastUpdate: string;
}

// Movement parameters
export interface MovementParams {
  /** Distance in cm (20-500) */
  distance?: number;
  /** Speed in cm/s (10-100) */
  speed?: number;
}

// Rotation parameters  
export interface RotationParams {
  /** Angle in degrees (1-360) */
  angle?: number;
  /** Speed in degrees/s (1-100) */
  speed?: number;
}

// Camera settings
export interface CameraSettings {
  /** Camera resolution */
  resolution?: '720p' | '480p';
  /** Frames per second */
  fps?: number;
  /** Bitrate for streaming */
  bitrate?: number;
}

// Mission pad coordinates
export interface MissionPadCoordinates {
  /** X coordinate (-500 to 500 cm) */
  x: number;
  /** Y coordinate (-500 to 500 cm) */
  y: number;
  /** Z coordinate (20-500 cm) */
  z: number;
  /** Speed (10-100 cm/s) */
  speed?: number;
  /** Mission pad ID (1-8) */
  missionPadId?: number;
}