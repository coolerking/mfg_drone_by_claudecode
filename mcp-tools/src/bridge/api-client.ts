import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { ServerConfig } from '../types/config.js';
import { Logger } from '../utils/logger.js';
import {
  StatusResponse,
  ErrorResponse,
  DroneStatus,
  BatteryResponse,
  HeightResponse,
  TemperatureResponse,
  FlightTimeResponse,
  BarometerResponse,
  DistanceTofResponse,
  AccelerationResponse,
  VelocityResponse,
  AttitudeResponse,
  MissionPadStatus,
  TrackingStatus,
  ModelListResponse,
  ModelTrainResponse,
  CommandResponse,
  MoveRequest,
  RotateRequest,
  FlipRequest,
  GoXyzRequest,
  CurveXyzRequest,
  RcControlRequest,
  CameraSettingsRequest,
  WiFiRequest,
  CommandRequest,
  SpeedRequest,
  MissionPadDetectionDirectionRequest,
  MissionPadGoXyzRequest,
  TrackingStartRequest,
} from '../types/api.js';

export class FastAPIClient {
  private client: AxiosInstance;
  private logger;
  private config: ServerConfig;
  private healthCheckTimer?: NodeJS.Timeout;

  constructor(config: ServerConfig, logger: Logger) {
    this.config = config;
    this.logger = logger.createComponentLogger('FastAPIClient');
    
    this.client = axios.create({
      baseURL: config.backendUrl,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'MFG-Drone-MCP-Tools/1.0.0',
      },
    });

    this.setupInterceptors();
    this.startHealthCheck();
  }

  /**
   * Setup request/response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        this.logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
          data: config.data,
          params: config.params,
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
          data: response.data,
        });
        return response;
      },
      (error) => {
        this.logger.error('API Response Error', {
          status: error.response?.status,
          data: error.response?.data,
          url: error.config?.url,
        });
        return Promise.reject(error);
      }
    );
  }

  /**
   * Start periodic health checks
   */
  private startHealthCheck(): void {
    this.healthCheckTimer = setInterval(async () => {
      try {
        await this.checkHealth();
      } catch (error) {
        this.logger.warn('Health check failed', error);
      }
    }, this.config.healthCheckInterval);
  }

  /**
   * Stop health checks
   */
  stopHealthCheck(): void {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = undefined;
    }
  }

  /**
   * Generic request method with retry logic
   */
  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: unknown
  ): Promise<T> {
    let lastError: unknown;

    for (let attempt = 1; attempt <= this.config.retryAttempts + 1; attempt++) {
      try {
        const response: AxiosResponse<T> = await this.client.request({
          method,
          url,
          data,
        });
        return response.data;
      } catch (error) {
        lastError = error;
        
        if (attempt <= this.config.retryAttempts) {
          this.logger.warn(`Request failed (attempt ${attempt}), retrying in ${this.config.retryDelay}ms`, {
            url,
            error: this.formatError(error),
          });
          await this.delay(this.config.retryDelay);
        }
      }
    }

    throw this.createMCPError(lastError);
  }

  /**
   * Delay utility for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Format error for logging
   */
  private formatError(error: unknown): unknown {
    if (axios.isAxiosError(error)) {
      return {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
      };
    }
    return error;
  }

  /**
   * Create MCP-compatible error
   */
  private createMCPError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const response = error.response;
      if (response?.data && typeof response.data === 'object' && 'error' in response.data) {
        const apiError = response.data as ErrorResponse;
        return new Error(`API Error: ${apiError.error} (${apiError.code})`);
      }
      return new Error(`HTTP ${response?.status}: ${error.message}`);
    }
    return error instanceof Error ? error : new Error(String(error));
  }

  // System APIs
  async checkHealth(): Promise<{ status: string }> {
    return this.request('GET', '/health');
  }

  // Connection APIs
  async connect(): Promise<StatusResponse> {
    return this.request('POST', '/drone/connect');
  }

  async disconnect(): Promise<StatusResponse> {
    return this.request('POST', '/drone/disconnect');
  }

  async getStatus(): Promise<DroneStatus> {
    return this.request('GET', '/drone/status');
  }

  // Flight Control APIs
  async takeoff(): Promise<StatusResponse> {
    return this.request('POST', '/drone/takeoff');
  }

  async land(): Promise<StatusResponse> {
    return this.request('POST', '/drone/land');
  }

  async emergency(): Promise<StatusResponse> {
    return this.request('POST', '/drone/emergency');
  }

  async stop(): Promise<StatusResponse> {
    return this.request('POST', '/drone/stop');
  }

  // Movement APIs
  async move(params: MoveRequest): Promise<StatusResponse> {
    return this.request('POST', '/drone/move', params);
  }

  async rotate(params: RotateRequest): Promise<StatusResponse> {
    return this.request('POST', '/drone/rotate', params);
  }

  async flip(params: FlipRequest): Promise<StatusResponse> {
    return this.request('POST', '/drone/flip', params);
  }

  // Advanced Movement APIs
  async goXyz(params: GoXyzRequest): Promise<StatusResponse> {
    return this.request('POST', '/drone/go_xyz', params);
  }

  async curveXyz(params: CurveXyzRequest): Promise<StatusResponse> {
    return this.request('POST', '/drone/curve_xyz', params);
  }

  async rcControl(params: RcControlRequest): Promise<StatusResponse> {
    return this.request('POST', '/drone/rc_control', params);
  }

  // Camera APIs
  async startVideoStream(): Promise<StatusResponse> {
    return this.request('POST', '/camera/stream/start');
  }

  async stopVideoStream(): Promise<StatusResponse> {
    return this.request('POST', '/camera/stream/stop');
  }

  async takePhoto(): Promise<StatusResponse> {
    return this.request('POST', '/camera/photo');
  }

  async startVideoRecording(): Promise<StatusResponse> {
    return this.request('POST', '/camera/video/start');
  }

  async stopVideoRecording(): Promise<StatusResponse> {
    return this.request('POST', '/camera/video/stop');
  }

  async setCameraSettings(params: CameraSettingsRequest): Promise<StatusResponse> {
    return this.request('PUT', '/camera/settings', params);
  }

  // Sensor APIs
  async getBattery(): Promise<BatteryResponse> {
    return this.request('GET', '/drone/battery');
  }

  async getHeight(): Promise<HeightResponse> {
    return this.request('GET', '/drone/height');
  }

  async getTemperature(): Promise<TemperatureResponse> {
    return this.request('GET', '/drone/temperature');
  }

  async getFlightTime(): Promise<FlightTimeResponse> {
    return this.request('GET', '/drone/flight_time');
  }

  async getBarometer(): Promise<BarometerResponse> {
    return this.request('GET', '/drone/barometer');
  }

  async getDistanceTof(): Promise<DistanceTofResponse> {
    return this.request('GET', '/drone/distance_tof');
  }

  async getAcceleration(): Promise<AccelerationResponse> {
    return this.request('GET', '/drone/acceleration');
  }

  async getVelocity(): Promise<VelocityResponse> {
    return this.request('GET', '/drone/velocity');
  }

  async getAttitude(): Promise<AttitudeResponse> {
    return this.request('GET', '/drone/attitude');
  }

  // Settings APIs
  async setWiFi(params: WiFiRequest): Promise<StatusResponse> {
    return this.request('PUT', '/drone/wifi', params);
  }

  async sendCommand(params: CommandRequest): Promise<CommandResponse> {
    return this.request('POST', '/drone/command', params);
  }

  async setSpeed(params: SpeedRequest): Promise<StatusResponse> {
    return this.request('PUT', '/drone/speed', params);
  }

  // Mission Pad APIs
  async enableMissionPad(): Promise<StatusResponse> {
    return this.request('POST', '/mission_pad/enable');
  }

  async disableMissionPad(): Promise<StatusResponse> {
    return this.request('POST', '/mission_pad/disable');
  }

  async setMissionPadDetectionDirection(params: MissionPadDetectionDirectionRequest): Promise<StatusResponse> {
    return this.request('PUT', '/mission_pad/detection_direction', params);
  }

  async goXyzMissionPad(params: MissionPadGoXyzRequest): Promise<StatusResponse> {
    return this.request('POST', '/mission_pad/go_xyz', params);
  }

  async getMissionPadStatus(): Promise<MissionPadStatus> {
    return this.request('GET', '/mission_pad/status');
  }

  // Object Tracking APIs
  async startTracking(params: TrackingStartRequest): Promise<StatusResponse> {
    return this.request('POST', '/tracking/start', params);
  }

  async stopTracking(): Promise<StatusResponse> {
    return this.request('POST', '/tracking/stop');
  }

  async getTrackingStatus(): Promise<TrackingStatus> {
    return this.request('GET', '/tracking/status');
  }

  // Model Management APIs
  async trainModel(formData: FormData): Promise<ModelTrainResponse> {
    return this.request('POST', '/model/train');
  }

  async listModels(): Promise<ModelListResponse> {
    return this.request('GET', '/model/list');
  }
}