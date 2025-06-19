import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ServerConfig } from '../types/config.js';
import { Logger } from '../utils/logger.js';
import {
  StatusResponse,
  ErrorResponse,
  DroneStatus,
  MoveRequest,
  RotateRequest,
  FlipRequest,
  GoXYZRequest,
  CurveXYZRequest,
  RCControlRequest,
  CameraSettingsRequest,
  WiFiRequest,
  SpeedRequest,
  CommandRequest,
  MissionPadDirectionRequest,
  MissionPadGoXYZRequest,
  TrackingStartRequest
} from '../types/api.js';
import { MissionPadStatus, TrackingStatus, ModelListResponse } from '../types/drone.js';

export class FastAPIClient {
  private client: AxiosInstance;
  private logger: Logger;
  private config: ServerConfig;

  constructor(config: ServerConfig, logger: Logger) {
    this.config = config;
    this.logger = logger;
    
    this.client = axios.create({
      baseURL: config.backendUrl,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        this.logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
          data: config.data,
          params: config.params
        });
        return config;
      },
      (error) => {
        this.logger.error('API Request Error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        this.logger.debug(`API Response: ${response.status} ${response.config.url}`, {
          data: response.data
        });
        return response;
      },
      (error) => {
        this.logger.error('API Response Error', {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message
        });
        return Promise.reject(error);
      }
    );
  }

  private async retryRequest<T>(
    requestFn: () => Promise<AxiosResponse<T>>,
    retries: number = this.config.retries
  ): Promise<T> {
    let lastError: any;

    for (let i = 0; i <= retries; i++) {
      try {
        const response = await requestFn();
        return response.data;
      } catch (error: any) {
        lastError = error;
        
        if (i < retries) {
          const delay = Math.pow(2, i) * 1000; // Exponential backoff
          this.logger.warn(`Request failed, retrying in ${delay}ms (attempt ${i + 1}/${retries + 1})`, {
            error: error.message
          });
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError;
  }

  // System endpoints
  async healthCheck(): Promise<{ status: string }> {
    return this.retryRequest(() => this.client.get('/health'));
  }

  // Connection endpoints
  async connect(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/connect'));
  }

  async disconnect(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/disconnect'));
  }

  // Flight control endpoints
  async takeoff(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/takeoff'));
  }

  async land(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/land'));
  }

  async emergency(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/emergency'));
  }

  async stop(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/stop'));
  }

  // Movement endpoints
  async move(request: MoveRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/move', request));
  }

  async rotate(request: RotateRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/rotate', request));
  }

  async flip(request: FlipRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/flip', request));
  }

  // Advanced movement endpoints
  async goXYZ(request: GoXYZRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/go_xyz', request));
  }

  async curveXYZ(request: CurveXYZRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/curve_xyz', request));
  }

  async rcControl(request: RCControlRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/drone/rc_control', request));
  }

  // Camera endpoints
  async startVideoStream(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/camera/stream/start'));
  }

  async stopVideoStream(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/camera/stream/stop'));
  }

  async takePhoto(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/camera/photo'));
  }

  async startVideoRecording(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/camera/video/start'));
  }

  async stopVideoRecording(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/camera/video/stop'));
  }

  async setCameraSettings(request: CameraSettingsRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.put('/camera/settings', request));
  }

  // Sensor endpoints
  async getDroneStatus(): Promise<DroneStatus> {
    return this.retryRequest(() => this.client.get('/drone/status'));
  }

  async getBattery(): Promise<{ battery: number }> {
    return this.retryRequest(() => this.client.get('/drone/battery'));
  }

  async getHeight(): Promise<{ height: number }> {
    return this.retryRequest(() => this.client.get('/drone/height'));
  }

  async getTemperature(): Promise<{ temperature: number }> {
    return this.retryRequest(() => this.client.get('/drone/temperature'));
  }

  async getFlightTime(): Promise<{ flight_time: number }> {
    return this.retryRequest(() => this.client.get('/drone/flight_time'));
  }

  async getBarometer(): Promise<{ barometer: number }> {
    return this.retryRequest(() => this.client.get('/drone/barometer'));
  }

  async getDistanceTof(): Promise<{ distance_tof: number }> {
    return this.retryRequest(() => this.client.get('/drone/distance_tof'));
  }

  async getAcceleration(): Promise<{ acceleration: { x: number; y: number; z: number } }> {
    return this.retryRequest(() => this.client.get('/drone/acceleration'));
  }

  async getVelocity(): Promise<{ velocity: { x: number; y: number; z: number } }> {
    return this.retryRequest(() => this.client.get('/drone/velocity'));
  }

  async getAttitude(): Promise<{ attitude: { pitch: number; roll: number; yaw: number } }> {
    return this.retryRequest(() => this.client.get('/drone/attitude'));
  }

  // Settings endpoints
  async setWiFi(request: WiFiRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.put('/drone/wifi', request));
  }

  async setSpeed(request: SpeedRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.put('/drone/speed', request));
  }

  async sendCommand(request: CommandRequest): Promise<{ success: boolean; response: string }> {
    return this.retryRequest(() => this.client.post('/drone/command', request));
  }

  // Mission pad endpoints
  async enableMissionPad(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/mission_pad/enable'));
  }

  async disableMissionPad(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/mission_pad/disable'));
  }

  async setMissionPadDirection(request: MissionPadDirectionRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.put('/mission_pad/detection_direction', request));
  }

  async goToMissionPad(request: MissionPadGoXYZRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/mission_pad/go_xyz', request));
  }

  async getMissionPadStatus(): Promise<MissionPadStatus> {
    return this.retryRequest(() => this.client.get('/mission_pad/status'));
  }

  // Tracking endpoints
  async startTracking(request: TrackingStartRequest): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/tracking/start', request));
  }

  async stopTracking(): Promise<StatusResponse> {
    return this.retryRequest(() => this.client.post('/tracking/stop'));
  }

  async getTrackingStatus(): Promise<TrackingStatus> {
    return this.retryRequest(() => this.client.get('/tracking/status'));
  }

  // Model management endpoints
  async getModelList(): Promise<ModelListResponse> {
    return this.retryRequest(() => this.client.get('/model/list'));
  }
}