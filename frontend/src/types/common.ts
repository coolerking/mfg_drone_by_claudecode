// Common types used throughout the application

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface User {
  id: string
  username: string
  role: 'admin' | 'operator' | 'viewer'
  createdAt: string
  lastLogin?: string
}

export interface SystemStatus {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_usage: number
  uptime: number
  temperature?: number
}

export interface Alert {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  timestamp: string
  dismissed: boolean
}

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface NotificationOptions {
  type: NotificationType
  message: string
  duration?: number
  persistent?: boolean
}

// Authentication types
export interface AuthTokens {
  accessToken: string
  refreshToken: string
  expiresAt: number
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  user: User
  tokens: AuthTokens
}

// WebSocket event types
export interface WebSocketEvent {
  type: string
  data: any
  timestamp: string
}

// Drone status types (extending from drone.ts)
export interface DroneStatus {
  id: string
  name: string
  status: 'connected' | 'disconnected' | 'flying' | 'landed' | 'error' | 'battery_low'
  battery: number
  position?: {
    x: number
    y: number
    z: number
  }
  connection_quality: number
  last_seen: string
  flight_time?: number
  temperature?: number
}

// Tracking status types
export interface TrackingStatus {
  drone_id: string
  is_tracking: boolean
  target_detected: boolean
  target_type?: string
  confidence?: number
  tracking_quality: number
  last_detection?: string
  bbox?: {
    x: number
    y: number
    width: number
    height: number
  }
}

// Camera stream types
export interface CameraStreamConfig {
  resolution: string
  fps: number
  quality: number
  encoding: 'h264' | 'mjpeg'
}

// Model training types
export interface TrainingProgress {
  model_id: string
  progress: number
  epoch: number
  loss: number
  accuracy?: number
  estimated_time_remaining?: number
  status: 'running' | 'completed' | 'failed' | 'paused'
}

// File upload types
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

// Form validation types
export interface ValidationError {
  field: string
  message: string
}

export interface FormState<T> {
  data: T
  errors: ValidationError[]
  isValid: boolean
  isSubmitting: boolean
}