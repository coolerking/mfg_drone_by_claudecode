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