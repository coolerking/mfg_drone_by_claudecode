/**
 * MCP Drone Client SDK
 * JavaScript/TypeScript SDK for MCP Drone Control Server
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import WebSocket from 'ws';

// Types
export interface MCPClientConfig {
  baseURL: string;
  apiKey?: string;
  bearerToken?: string;
  timeout?: number;
}

export interface NaturalLanguageCommand {
  command: string;
  context?: {
    drone_id?: string;
    language?: string;
  };
  options?: {
    confirm_before_execution?: boolean;
    dry_run?: boolean;
  };
}

export interface BatchCommand {
  commands: NaturalLanguageCommand[];
  execution_mode?: 'sequential' | 'parallel';
  stop_on_error?: boolean;
}

export interface CommandResponse {
  success: boolean;
  message: string;
  parsed_intent?: {
    action: string;
    parameters: any;
    confidence: number;
  };
  execution_details?: {
    backend_calls: any[];
    execution_time: number;
  };
  result?: any;
  timestamp: string;
}

export interface BatchCommandResponse {
  success: boolean;
  message: string;
  results: CommandResponse[];
  summary: {
    total_commands: number;
    successful_commands: number;
    failed_commands: number;
    total_execution_time: number;
  };
  timestamp: string;
}

export interface DroneInfo {
  id: string;
  name: string;
  type: 'real' | 'dummy';
  status: 'available' | 'connected' | 'busy' | 'offline' | 'error';
  capabilities: string[];
  last_seen?: string;
}

export interface DroneListResponse {
  drones: DroneInfo[];
  count: number;
  message?: string;
  timestamp: string;
}

export interface DroneStatusResponse {
  drone_id: string;
  status: {
    connection_status: 'disconnected' | 'connected' | 'error';
    flight_status: 'landed' | 'flying' | 'hovering' | 'landing' | 'taking_off';
    battery_level: number;
    height: number;
    temperature: number;
    wifi_signal: number;
  };
  message?: string;
  timestamp: string;
}

export interface TakeoffCommand {
  target_height?: number;
  safety_check?: boolean;
}

export interface MoveCommand {
  direction: 'up' | 'down' | 'left' | 'right' | 'forward' | 'back';
  distance: number;
  speed?: number;
}

export interface RotateCommand {
  direction: 'clockwise' | 'counter_clockwise' | 'left' | 'right';
  angle: number;
}

export interface AltitudeCommand {
  target_height: number;
  mode?: 'absolute' | 'relative';
}

export interface PhotoCommand {
  filename?: string;
  quality?: 'high' | 'medium' | 'low';
  metadata?: any;
}

export interface StreamingCommand {
  action: 'start' | 'stop';
  quality?: 'high' | 'medium' | 'low';
  resolution?: '720p' | '480p' | '360p';
}

export interface LearningDataCommand {
  object_name: string;
  capture_positions?: ('front' | 'back' | 'left' | 'right' | 'top' | 'bottom')[];
  movement_distance?: number;
  photos_per_position?: number;
  dataset_name?: string;
}

export interface DetectionCommand {
  drone_id: string;
  model_id?: string;
  confidence_threshold?: number;
}

export interface TrackingCommand {
  action: 'start' | 'stop';
  drone_id: string;
  model_id?: string;
  follow_distance?: number;
  confidence_threshold?: number;
}

export interface OperationResponse {
  success: boolean;
  message: string;
  operation_id?: string;
  execution_time?: number;
  timestamp: string;
}

export interface PhotoResponse {
  success: boolean;
  message: string;
  photo?: {
    id: string;
    filename: string;
    path: string;
    size: number;
    timestamp: string;
  };
  timestamp: string;
}

export interface LearningDataResponse {
  success: boolean;
  message: string;
  dataset?: {
    id: string;
    name: string;
    image_count: number;
    positions_captured: string[];
  };
  execution_summary?: {
    total_moves: number;
    total_photos: number;
    execution_time: number;
  };
  timestamp: string;
}

export interface DetectionResponse {
  success: boolean;
  message: string;
  detections: {
    label: string;
    confidence: number;
    bbox: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  }[];
  processing_time: number;
  timestamp: string;
}

export interface SystemStatusResponse {
  mcp_server: {
    status: 'running' | 'stopped' | 'error';
    uptime: number;
    version: string;
    active_connections: number;
  };
  backend_system: {
    connection_status: 'connected' | 'disconnected' | 'error';
    api_endpoint: string;
    response_time: number;
  };
  connected_drones: number;
  active_operations: number;
  system_health: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  checks: {
    name: string;
    status: 'pass' | 'fail';
    message: string;
    response_time: number;
  }[];
  timestamp: string;
}

export interface MCPError {
  error: boolean;
  error_code: string;
  message: string;
  details?: {
    parsing_error?: string;
    suggested_corrections?: string[];
    original_command?: string;
  };
  timestamp: string;
}

/**
 * MCP Drone Client SDK
 */
export class MCPClient {
  private client: AxiosInstance;
  private ws: WebSocket | null = null;
  private config: MCPClientConfig;

  constructor(config: MCPClientConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey && { 'X-API-Key': config.apiKey }),
        ...(config.bearerToken && { 'Authorization': `Bearer ${config.bearerToken}` })
      }
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.data) {
          throw new MCPClientError(error.response.data);
        }
        throw error;
      }
    );
  }

  // Natural Language Commands
  async executeCommand(command: NaturalLanguageCommand): Promise<CommandResponse> {
    const response = await this.client.post<CommandResponse>('/mcp/command', command);
    return response.data;
  }

  async executeBatchCommand(batchCommand: BatchCommand): Promise<BatchCommandResponse> {
    const response = await this.client.post<BatchCommandResponse>('/mcp/command/batch', batchCommand);
    return response.data;
  }

  // Drone Query APIs
  async getDrones(): Promise<DroneListResponse> {
    const response = await this.client.get<DroneListResponse>('/mcp/drones');
    return response.data;
  }

  async getAvailableDrones(): Promise<DroneListResponse> {
    const response = await this.client.get<DroneListResponse>('/mcp/drones/available');
    return response.data;
  }

  async getDroneStatus(droneId: string): Promise<DroneStatusResponse> {
    const response = await this.client.get<DroneStatusResponse>(`/mcp/drones/${droneId}/status`);
    return response.data;
  }

  // Drone Control APIs
  async connectDrone(droneId: string): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/connect`);
    return response.data;
  }

  async disconnectDrone(droneId: string): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/disconnect`);
    return response.data;
  }

  async takeoff(droneId: string, command?: TakeoffCommand): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/takeoff`, command);
    return response.data;
  }

  async land(droneId: string): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/land`);
    return response.data;
  }

  async moveDrone(droneId: string, command: MoveCommand): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/move`, command);
    return response.data;
  }

  async rotateDrone(droneId: string, command: RotateCommand): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/rotate`, command);
    return response.data;
  }

  async emergencyStop(droneId: string): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/emergency`);
    return response.data;
  }

  async setAltitude(droneId: string, command: AltitudeCommand): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/altitude`, command);
    return response.data;
  }

  // Camera APIs
  async takePhoto(droneId: string, command?: PhotoCommand): Promise<PhotoResponse> {
    const response = await this.client.post<PhotoResponse>(`/mcp/drones/${droneId}/camera/photo`, command);
    return response.data;
  }

  async controlStreaming(droneId: string, command: StreamingCommand): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>(`/mcp/drones/${droneId}/camera/streaming`, command);
    return response.data;
  }

  async collectLearningData(droneId: string, command: LearningDataCommand): Promise<LearningDataResponse> {
    const response = await this.client.post<LearningDataResponse>(`/mcp/drones/${droneId}/learning/collect`, command);
    return response.data;
  }

  // Vision APIs
  async detectObjects(command: DetectionCommand): Promise<DetectionResponse> {
    const response = await this.client.post<DetectionResponse>('/mcp/vision/detection', command);
    return response.data;
  }

  async controlTracking(command: TrackingCommand): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>('/mcp/vision/tracking', command);
    return response.data;
  }

  // System APIs
  async getSystemStatus(): Promise<SystemStatusResponse> {
    const response = await this.client.get<SystemStatusResponse>('/mcp/system/status');
    return response.data;
  }

  async getHealthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/mcp/system/health');
    return response.data;
  }

  // WebSocket Connection
  connectWebSocket(onMessage?: (data: any) => void, onError?: (error: Error) => void): void {
    const wsUrl = this.config.baseURL.replace(/^http/, 'ws') + '/ws';
    this.ws = new WebSocket(wsUrl);

    this.ws.on('open', () => {
      console.log('WebSocket connected');
    });

    this.ws.on('message', (data) => {
      try {
        const parsed = JSON.parse(data.toString());
        onMessage?.(parsed);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    });

    this.ws.on('error', (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    });

    this.ws.on('close', () => {
      console.log('WebSocket disconnected');
    });
  }

  disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // Utility Methods
  async waitForOperation(operationId: string, maxWaitTime: number = 30000): Promise<boolean> {
    const startTime = Date.now();
    while (Date.now() - startTime < maxWaitTime) {
      try {
        // This would need to be implemented based on the actual API
        // For now, just simulate a delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        return true;
      } catch (error) {
        // Continue waiting
      }
    }
    return false;
  }
}

/**
 * Custom error class for MCP Client
 */
export class MCPClientError extends Error {
  public readonly errorCode: string;
  public readonly details?: any;
  public readonly timestamp: string;

  constructor(errorData: MCPError) {
    super(errorData.message);
    this.name = 'MCPClientError';
    this.errorCode = errorData.error_code;
    this.details = errorData.details;
    this.timestamp = errorData.timestamp;
  }
}

// Export default
export default MCPClient;