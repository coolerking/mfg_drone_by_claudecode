// Drone-related type definitions

export interface Drone {
  id: string
  name: string
  model: string
  serial_number: string
  status: DroneStatus
  battery: number
  altitude: number
  temperature: number
  signal_strength: number
  flight_time: number
  position?: Position3D
  camera?: CameraInfo
  lastSeen: string
  createdAt: string
}

export type DroneStatus = 
  | 'connected'
  | 'disconnected' 
  | 'flying'
  | 'landing'
  | 'takeoff'
  | 'hovering'
  | 'error'
  | 'low_battery'
  | 'maintenance'

export interface Position3D {
  x: number
  y: number
  z: number
  heading?: number
}

export interface CameraInfo {
  isStreaming: boolean
  resolution: string
  fps: number
  streamUrl?: string
}

export interface DroneCommand {
  droneId: string
  command: DroneCommandType
  parameters?: DroneCommandParameters
}

export type DroneCommandType =
  | 'takeoff'
  | 'land'
  | 'emergency_stop'
  | 'move'
  | 'rotate'
  | 'hover'
  | 'return_home'
  | 'start_camera'
  | 'stop_camera'
  | 'take_photo'

export interface DroneCommandParameters {
  direction?: 'up' | 'down' | 'left' | 'right' | 'forward' | 'back'
  distance?: number
  angle?: number
  speed?: number
  duration?: number
}

export interface DroneStats {
  totalDrones: number
  connectedDrones: number
  flyingDrones: number
  errorDrones: number
}

export interface FlightLog {
  id: string
  droneId: string
  startTime: string
  endTime?: string
  duration: number
  maxAltitude: number
  totalDistance: number
  batteryUsed: number
  commands: DroneCommand[]
  status: 'active' | 'completed' | 'aborted' | 'error'
}