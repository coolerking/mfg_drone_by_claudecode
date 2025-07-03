import { useEffect, useCallback, useRef } from 'react'
import { useDispatch } from 'react-redux'
import type { AppDispatch } from '../store'
import { wsClient, type WebSocketEventHandlers } from '../services/websocket/wsClient'

// Custom hook for WebSocket connectivity and real-time updates
export const useWebSocket = () => {
  const dispatch = useDispatch<AppDispatch>()
  const listenersRef = useRef<Array<() => void>>([])

  // Clean up listeners on unmount
  useEffect(() => {
    const listeners = listenersRef.current

    return () => {
      listeners.forEach(unsubscribe => unsubscribe())
      listenersRef.current = []
    }
  }, [])

  // Subscribe to WebSocket events with automatic cleanup
  const subscribe = useCallback(<K extends keyof WebSocketEventHandlers>(
    event: K,
    handler: WebSocketEventHandlers[K]
  ) => {
    const unsubscribe = wsClient.on(event, handler)
    listenersRef.current.push(unsubscribe)
    return unsubscribe
  }, [])

  // Send drone command via WebSocket
  const sendDroneCommand = useCallback((
    droneId: string,
    command: string,
    parameters?: any
  ) => {
    wsClient.sendDroneCommand(droneId, command, parameters)
  }, [])

  // Start tracking via WebSocket
  const startTracking = useCallback((
    droneId: string,
    targetType?: string
  ) => {
    wsClient.startTracking(droneId, targetType)
  }, [])

  // Stop tracking via WebSocket
  const stopTracking = useCallback((droneId: string) => {
    wsClient.stopTracking(droneId)
  }, [])

  // Subscribe to camera stream
  const subscribeToCamera = useCallback((droneId: string) => {
    wsClient.subscribeToCamera(droneId)
  }, [])

  // Unsubscribe from camera stream
  const unsubscribeFromCamera = useCallback((droneId: string) => {
    wsClient.unsubscribeFromCamera(droneId)
  }, [])

  // Reconnect WebSocket manually
  const reconnect = useCallback(() => {
    wsClient.reconnect()
  }, [])

  return {
    // Connection status
    isConnected: wsClient.isConnected,
    connectionState: wsClient.connectionState,
    
    // Event subscription
    subscribe,
    
    // Drone control
    sendDroneCommand,
    startTracking,
    stopTracking,
    
    // Camera control
    subscribeToCamera,
    unsubscribeFromCamera,
    
    // Connection management
    reconnect,
    
    // Direct access to client (use sparingly)
    client: wsClient,
  }
}

// Hook for drone-specific WebSocket functionality
export const useDroneWebSocket = (droneId: string) => {
  const { subscribe, sendDroneCommand, subscribeToCamera, unsubscribeFromCamera } = useWebSocket()

  // Send command to this specific drone
  const sendCommand = useCallback((command: string, parameters?: any) => {
    sendDroneCommand(droneId, command, parameters)
  }, [droneId, sendDroneCommand])

  // Subscribe to this drone's status updates
  const subscribeToDroneStatus = useCallback((
    handler: (status: any) => void
  ) => {
    return subscribe('drone_status', (data) => {
      if (data.id === droneId || data.drone_id === droneId) {
        handler(data)
      }
    })
  }, [droneId, subscribe])

  // Subscribe to this drone's camera stream
  const subscribeToThisCamera = useCallback(() => {
    subscribeToCamera(droneId)
  }, [droneId, subscribeToCamera])

  // Unsubscribe from this drone's camera stream
  const unsubscribeFromThisCamera = useCallback(() => {
    unsubscribeFromCamera(droneId)
  }, [droneId, unsubscribeFromCamera])

  return {
    sendCommand,
    subscribeToDroneStatus,
    subscribeToCamera: subscribeToThisCamera,
    unsubscribeFromCamera: unsubscribeFromThisCamera,
  }
}

// Hook for system-wide WebSocket events
export const useSystemWebSocket = () => {
  const { subscribe } = useWebSocket()

  // Subscribe to system status updates
  const subscribeToSystemStatus = useCallback((
    handler: (status: any) => void
  ) => {
    return subscribe('system_status', handler)
  }, [subscribe])

  // Subscribe to alerts
  const subscribeToAlerts = useCallback((
    handler: (alert: any) => void
  ) => {
    return subscribe('alert', handler)
  }, [subscribe])

  // Subscribe to model training progress
  const subscribeToTrainingProgress = useCallback((
    handler: (progress: any) => void
  ) => {
    return subscribe('model_training_progress', handler)
  }, [subscribe])

  return {
    subscribeToSystemStatus,
    subscribeToAlerts,
    subscribeToTrainingProgress,
  }
}

// Hook for tracking-specific WebSocket functionality
export const useTrackingWebSocket = () => {
  const { subscribe, startTracking, stopTracking } = useWebSocket()

  // Subscribe to tracking status updates
  const subscribeToTrackingStatus = useCallback((
    handler: (status: any) => void
  ) => {
    return subscribe('tracking_status', handler)
  }, [subscribe])

  // Start tracking with WebSocket
  const startTrackingSession = useCallback((
    droneId: string,
    targetType?: string
  ) => {
    startTracking(droneId, targetType)
  }, [startTracking])

  // Stop tracking with WebSocket
  const stopTrackingSession = useCallback((droneId: string) => {
    stopTracking(droneId)
  }, [stopTracking])

  return {
    subscribeToTrackingStatus,
    startTracking: startTrackingSession,
    stopTracking: stopTrackingSession,
  }
}