import { io, Socket } from 'socket.io-client'
import type { 
  DroneStatus, 
  SystemStatus, 
  TrackingStatus,
  WebSocketEvent 
} from '../../types/common'
import { getStoredTokens } from '../api/apiClient'

// WebSocket URL configuration
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

// Event types for type safety
export type WebSocketEventHandlers = {
  'drone_status': (data: DroneStatus) => void
  'system_status': (data: SystemStatus) => void
  'tracking_status': (data: TrackingStatus) => void
  'alert': (data: any) => void
  'model_training_progress': (data: any) => void
  'error': (error: any) => void
  'connect': () => void
  'disconnect': () => void
  'reconnect': () => void
}

class WebSocketClient {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private eventHandlers: Map<string, Set<Function>> = new Map()

  constructor() {
    this.connect()
  }

  private connect(): void {
    const tokens = getStoredTokens()
    
    this.socket = io(WS_BASE_URL, {
      auth: {
        token: tokens?.accessToken || '',
      },
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      timeout: 10000,
    })

    this.setupEventListeners()
  }

  private setupEventListeners(): void {
    if (!this.socket) return

    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.emit('connect')
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.emit('disconnect')
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.handleReconnection()
    })

    this.socket.on('reconnect', () => {
      console.log('WebSocket reconnected')
      this.emit('reconnect')
    })

    // Data events
    this.socket.on('drone_status', (data: DroneStatus) => {
      this.emit('drone_status', data)
    })

    this.socket.on('system_status', (data: SystemStatus) => {
      this.emit('system_status', data)
    })

    this.socket.on('tracking_status', (data: TrackingStatus) => {
      this.emit('tracking_status', data)
    })

    this.socket.on('alert', (data: any) => {
      this.emit('alert', data)
    })

    this.socket.on('model_training_progress', (data: any) => {
      this.emit('model_training_progress', data)
    })

    this.socket.on('error', (error: any) => {
      console.error('WebSocket error:', error)
      this.emit('error', error)
    })
  }

  private handleReconnection(): void {
    this.reconnectAttempts++
    if (this.reconnectAttempts > this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
    
    setTimeout(() => {
      this.connect()
    }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts))
  }

  // Event subscription methods
  on<K extends keyof WebSocketEventHandlers>(
    event: K,
    handler: WebSocketEventHandlers[K]
  ): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set())
    }
    
    this.eventHandlers.get(event)!.add(handler)

    // Return unsubscribe function
    return () => {
      const handlers = this.eventHandlers.get(event)
      if (handlers) {
        handlers.delete(handler)
        if (handlers.size === 0) {
          this.eventHandlers.delete(event)
        }
      }
    }
  }

  off<K extends keyof WebSocketEventHandlers>(
    event: K,
    handler?: WebSocketEventHandlers[K]
  ): void {
    const handlers = this.eventHandlers.get(event)
    if (!handlers) return

    if (handler) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.eventHandlers.delete(event)
      }
    } else {
      this.eventHandlers.delete(event)
    }
  }

  private emit(event: string, data?: any): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in WebSocket event handler for '${event}':`, error)
        }
      })
    }
  }

  // Command sending methods
  sendDroneCommand(droneId: string, command: string, parameters?: any): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected, cannot send drone command')
      return
    }

    this.socket.emit('drone_command', {
      drone_id: droneId,
      command,
      parameters,
      timestamp: new Date().toISOString(),
    })
  }

  startTracking(droneId: string, targetType?: string): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected, cannot start tracking')
      return
    }

    this.socket.emit('start_tracking', {
      drone_id: droneId,
      target_type: targetType,
      timestamp: new Date().toISOString(),
    })
  }

  stopTracking(droneId: string): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected, cannot stop tracking')
      return
    }

    this.socket.emit('stop_tracking', {
      drone_id: droneId,
      timestamp: new Date().toISOString(),
    })
  }

  subscribeToCamera(droneId: string): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected, cannot subscribe to camera')
      return
    }

    this.socket.emit('subscribe_camera', { drone_id: droneId })
  }

  unsubscribeFromCamera(droneId: string): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected, cannot unsubscribe from camera')
      return
    }

    this.socket.emit('unsubscribe_camera', { drone_id: droneId })
  }

  // Connection status
  get isConnected(): boolean {
    return this.socket?.connected || false
  }

  get connectionState(): string {
    if (!this.socket) return 'disconnected'
    return this.socket.connected ? 'connected' : 'disconnected'
  }

  // Cleanup
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.eventHandlers.clear()
  }

  // Reconnect manually
  reconnect(): void {
    this.disconnect()
    this.connect()
  }
}

// Export singleton instance
export const wsClient = new WebSocketClient()

// Hook for React components
export const useWebSocket = () => {
  return {
    client: wsClient,
    isConnected: wsClient.isConnected,
    connectionState: wsClient.connectionState,
  }
}