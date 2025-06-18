import { z } from 'zod';

// Drone Status Types
export enum DroneStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  READY = 'ready',
  FLYING = 'flying',
  LANDING = 'landing',
  ERROR = 'error',
  EMERGENCY = 'emergency',
}

export enum FlightMode {
  MANUAL = 'manual',
  HOVER = 'hover',
  TRACKING = 'tracking',
  MISSION = 'mission',
  RETURN_HOME = 'return_home',
}

// Drone Capabilities
export interface DroneCapabilities {
  maxSpeed: number;
  maxHeight: number;
  maxDistance: number;
  batteryCapacity: number;
  cameraResolutions: string[];
  supportedCommands: string[];
  sensorTypes: string[];
}

// Flight Information
export const FlightInfoSchema = z.object({
  status: z.nativeEnum(DroneStatus),
  mode: z.nativeEnum(FlightMode),
  position: z.object({
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
  battery: z.number().min(0).max(100),
  temperature: z.number(),
  height: z.number(),
  flightTime: z.number(),
  isFlying: z.boolean(),
});

export type FlightInfo = z.infer<typeof FlightInfoSchema>;

// Command Result Types
export interface CommandResult {
  success: boolean;
  message: string;
  data?: unknown;
  duration: number;
  timestamp: Date;
}

export interface FlightCommand {
  id: string;
  type: string;
  parameters: Record<string, unknown>;
  timestamp: Date;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  result?: CommandResult;
}

// Safety Limits
export interface SafetyLimits {
  maxHeight: number;
  maxDistance: number;
  minBattery: number;
  maxWindSpeed: number;
  operatingTemperatureRange: {
    min: number;
    max: number;
  };
}

// Emergency Response
export interface EmergencyState {
  isActive: boolean;
  type: 'low_battery' | 'connection_lost' | 'manual_stop' | 'sensor_failure' | 'collision_detected';
  triggeredAt: Date;
  actions: string[];
  resolved: boolean;
  resolvedAt?: Date;
}

// Telemetry Data
export interface TelemetryData {
  timestamp: Date;
  flightInfo: FlightInfo;
  sensors: {
    battery: number;
    temperature: number;
    barometer: number;
    tof: number;
    acceleration: { x: number; y: number; z: number };
    gyroscope: { x: number; y: number; z: number };
  };
  camera: {
    isStreaming: boolean;
    isRecording: boolean;
    resolution: string;
    fps: number;
  };
  network: {
    signalStrength: number;
    latency: number;
    packetsLost: number;
  };
}

// Mission Planning
export interface Waypoint {
  id: string;
  position: { x: number; y: number; z: number };
  action: 'hover' | 'photo' | 'video_start' | 'video_stop' | 'rotate';
  parameters?: Record<string, unknown>;
  duration?: number;
}

export interface Mission {
  id: string;
  name: string;
  waypoints: Waypoint[];
  safetyChecks: boolean;
  autoReturn: boolean;
  estimatedDuration: number;
  status: 'draft' | 'ready' | 'executing' | 'completed' | 'aborted';
}

// Video Stream Types
export interface VideoStreamInfo {
  isActive: boolean;
  resolution: string;
  fps: number;
  bitrate: string;
  url?: string;
  latency: number;
  packetsDropped: number;
}

// Performance Metrics
export interface DronePerformanceMetrics {
  timestamp: Date;
  responseTime: number;
  commandSuccess: boolean;
  batteryDrain: number;
  temperatureVariation: number;
  signalQuality: number;
  flightStability: number;
}