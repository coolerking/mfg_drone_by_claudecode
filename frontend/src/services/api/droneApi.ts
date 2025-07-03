import { api } from './apiClient'
import type { DroneStatus } from '../../types/common'
import type { Drone, DroneCommand, FlightPlan } from '../../types/drone'

export class DroneApiService {
  private basePath = '/drones'

  // Get all drones
  async getDrones(): Promise<Drone[]> {
    return api.get<Drone[]>(this.basePath)
  }

  // Get drone by ID
  async getDrone(droneId: string): Promise<Drone> {
    return api.get<Drone>(`${this.basePath}/${droneId}`)
  }

  // Get drone status
  async getDroneStatus(droneId: string): Promise<DroneStatus> {
    return api.get<DroneStatus>(`${this.basePath}/${droneId}/status`)
  }

  // Connect to drone
  async connectDrone(droneId: string): Promise<{ success: boolean; message: string }> {
    return api.post(`${this.basePath}/${droneId}/connect`)
  }

  // Disconnect from drone
  async disconnectDrone(droneId: string): Promise<{ success: boolean; message: string }> {
    return api.post(`${this.basePath}/${droneId}/disconnect`)
  }

  // Send command to drone
  async sendCommand(
    droneId: string, 
    command: DroneCommand
  ): Promise<{ success: boolean; message: string }> {
    return api.post(`${this.basePath}/${droneId}/command`, command)
  }

  // Takeoff
  async takeoff(droneId: string): Promise<{ success: boolean; message: string }> {
    return this.sendCommand(droneId, { type: 'takeoff' })
  }

  // Land
  async land(droneId: string): Promise<{ success: boolean; message: string }> {
    return this.sendCommand(droneId, { type: 'land' })
  }

  // Emergency stop
  async emergencyStop(droneId: string): Promise<{ success: boolean; message: string }> {
    return this.sendCommand(droneId, { type: 'emergency' })
  }

  // Move drone
  async move(
    droneId: string,
    direction: 'up' | 'down' | 'left' | 'right' | 'forward' | 'back',
    distance: number
  ): Promise<{ success: boolean; message: string }> {
    return this.sendCommand(droneId, {
      type: 'move',
      parameters: { direction, distance }
    })
  }

  // Rotate drone
  async rotate(
    droneId: string,
    direction: 'clockwise' | 'counter_clockwise',
    angle: number
  ): Promise<{ success: boolean; message: string }> {
    return this.sendCommand(droneId, {
      type: 'rotate',
      parameters: { direction, angle }
    })
  }

  // Set speed
  async setSpeed(
    droneId: string,
    speed: number
  ): Promise<{ success: boolean; message: string }> {
    return this.sendCommand(droneId, {
      type: 'set_speed',
      parameters: { speed }
    })
  }

  // Start video stream
  async startVideoStream(droneId: string): Promise<{ success: boolean; stream_url?: string }> {
    return api.post(`${this.basePath}/${droneId}/camera/start`)
  }

  // Stop video stream
  async stopVideoStream(droneId: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/${droneId}/camera/stop`)
  }

  // Get camera settings
  async getCameraSettings(droneId: string): Promise<any> {
    return api.get(`${this.basePath}/${droneId}/camera/settings`)
  }

  // Update camera settings
  async updateCameraSettings(droneId: string, settings: any): Promise<{ success: boolean }> {
    return api.put(`${this.basePath}/${droneId}/camera/settings`, settings)
  }

  // Execute flight plan
  async executeFlightPlan(
    droneId: string, 
    flightPlan: FlightPlan
  ): Promise<{ success: boolean; execution_id: string }> {
    return api.post(`${this.basePath}/${droneId}/flight-plan`, flightPlan)
  }

  // Get flight logs
  async getFlightLogs(
    droneId: string,
    limit = 50,
    offset = 0
  ): Promise<any[]> {
    return api.get(`${this.basePath}/${droneId}/logs`, {
      params: { limit, offset }
    })
  }

  // Calibrate drone
  async calibrate(droneId: string): Promise<{ success: boolean; message: string }> {
    return api.post(`${this.basePath}/${droneId}/calibrate`)
  }

  // Get drone battery info
  async getBatteryInfo(droneId: string): Promise<{
    percentage: number
    voltage: number
    temperature: number
    time_remaining: number
  }> {
    return api.get(`${this.basePath}/${droneId}/battery`)
  }

  // Get drone telemetry
  async getTelemetry(droneId: string): Promise<{
    position: { x: number; y: number; z: number }
    velocity: { x: number; y: number; z: number }
    rotation: { pitch: number; roll: number; yaw: number }
    acceleration: { x: number; y: number; z: number }
    timestamp: string
  }> {
    return api.get(`${this.basePath}/${droneId}/telemetry`)
  }
}

// Export singleton instance
export const droneApi = new DroneApiService()