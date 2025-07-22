import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import { logger } from '@/utils/logger.js';
import { ErrorHandler } from '@/utils/errors.js';
import { NetworkError, type DroneStatus, type SystemStatus } from '@/types/index.js';
import type { Config } from '@/types/index.js';
import type {
  Drone,
  MoveCommand,
  RotateCommand,
  Photo,
  Dataset,
  CreateDatasetRequest,
  DatasetImage,
  DetectionRequest,
  DetectionResult,
  StartTrackingRequest,
  TrackingStatus,
  Model,
  TrainModelRequest,
  TrainingJob,
  ScanDronesResponse,
  HealthCheckResponse,
  CommandResponse,
  SuccessResponse,
  ErrorResponse,
  FileUploadFormData,
} from '@/types/api_types.js';

/**
 * バックエンドAPIクライアント
 * FastAPI バックエンドとの通信を担当
 */
export class BackendClient {
  private client: AxiosInstance;
  private config: Config;

  constructor(config: Config) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.backendUrl,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'MCP-Drone-Server/1.0.0',
      },
    });

    this.setupInterceptors();
  }

  /**
   * リクエスト・レスポンスインターセプターを設定
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        logger.debug(`Making request to: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        logger.error('Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        logger.debug(`Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        const statusCode = error.response?.status;
        const message = error.response?.data?.message || error.message;
        const networkError = ErrorHandler.fromHttpStatus(
          statusCode || 500,
          message
        );
        
        logger.error('Response error:', {
          url: error.config?.url,
          status: statusCode,
          message,
        });
        
        return Promise.reject(networkError);
      }
    );
  }

  // ========================================
  // Drone Management APIs
  // ========================================

  /**
   * ドローン一覧を取得
   */
  async getDrones(): Promise<Drone[]> {
    try {
      const response: AxiosResponse<Drone[]> = await this.client.get('/api/drones');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getDrones');
      throw handledError;
    }
  }

  /**
   * ドローンの状態を取得
   */
  async getDroneStatus(droneId?: string): Promise<DroneStatus[]> {
    try {
      const url = droneId ? `/api/drones/${droneId}/status` : '/api/drones/status';
      const response: AxiosResponse<DroneStatus | DroneStatus[]> = await this.client.get(url);
      
      const data = response.data;
      return Array.isArray(data) ? data : [data];
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getDroneStatus');
      throw handledError;
    }
  }

  /**
   * ドローンに接続
   */
  async connectDrone(droneId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/connect`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.connectDrone');
      throw handledError;
    }
  }

  /**
   * ドローンから切断
   */
  async disconnectDrone(droneId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/disconnect`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.disconnectDrone');
      throw handledError;
    }
  }

  /**
   * ドローンを離陸
   */
  async takeoffDrone(droneId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/takeoff`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.takeoffDrone');
      throw handledError;
    }
  }

  /**
   * ドローンを着陸
   */
  async landDrone(droneId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/land`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.landDrone');
      throw handledError;
    }
  }

  /**
   * ドローンを移動
   */
  async moveDrone(droneId: string, command: MoveCommand): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/move`, command);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.moveDrone');
      throw handledError;
    }
  }

  /**
   * ドローンを回転
   */
  async rotateDrone(droneId: string, command: RotateCommand): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/rotate`, command);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.rotateDrone');
      throw handledError;
    }
  }

  /**
   * ドローンを緊急停止
   */
  async emergencyStopDrone(droneId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/emergency`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.emergencyStopDrone');
      throw handledError;
    }
  }

  /**
   * ドローンをスキャン
   */
  async scanDrones(): Promise<ScanDronesResponse> {
    try {
      const response: AxiosResponse<ScanDronesResponse> = 
        await this.client.post('/api/drones/scan');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.scanDrones');
      throw handledError;
    }
  }

  // ========================================
  // Camera APIs
  // ========================================

  /**
   * カメラストリーミング開始
   */
  async startCameraStream(droneId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/camera/stream/start`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.startCameraStream');
      throw handledError;
    }
  }

  /**
   * カメラストリーミング停止
   */
  async stopCameraStream(droneId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post(`/api/drones/${droneId}/camera/stream/stop`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.stopCameraStream');
      throw handledError;
    }
  }

  /**
   * 写真撮影
   */
  async takePhoto(droneId: string): Promise<Photo> {
    try {
      const response: AxiosResponse<Photo> = 
        await this.client.post(`/api/drones/${droneId}/camera/photo`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.takePhoto');
      throw handledError;
    }
  }

  // ========================================
  // System APIs
  // ========================================

  /**
   * システムの健全性をチェック
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response: AxiosResponse<HealthCheckResponse> = 
        await this.client.get('/api/system/health');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.healthCheck');
      throw handledError;
    }
  }

  /**
   * システム状態を取得
   */
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const response: AxiosResponse<SystemStatus> = await this.client.get('/api/system/status');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getSystemStatus');
      throw handledError;
    }
  }

  /**
   * ドローンコマンドを実行
   */
  async executeCommand(droneId: string, command: string, params?: Record<string, unknown>): Promise<CommandResponse> {
    try {
      const response: AxiosResponse<CommandResponse> = 
        await this.client.post(`/api/drones/${droneId}/command`, {
          command,
          params: params || {},
        });
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.executeCommand');
      throw handledError;
    }
  }

  // ========================================
  // Vision APIs
  // ========================================

  /**
   * データセット一覧を取得
   */
  async getDatasets(): Promise<Dataset[]> {
    try {
      const response: AxiosResponse<Dataset[]> = await this.client.get('/api/vision/datasets');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getDatasets');
      throw handledError;
    }
  }

  /**
   * データセットを作成
   */
  async createDataset(request: CreateDatasetRequest): Promise<Dataset> {
    try {
      const response: AxiosResponse<Dataset> = 
        await this.client.post('/api/vision/datasets', request);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.createDataset');
      throw handledError;
    }
  }

  /**
   * データセット詳細を取得
   */
  async getDataset(datasetId: string): Promise<Dataset> {
    try {
      const response: AxiosResponse<Dataset> = 
        await this.client.get(`/api/vision/datasets/${datasetId}`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getDataset');
      throw handledError;
    }
  }

  /**
   * データセットを削除
   */
  async deleteDataset(datasetId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.delete(`/api/vision/datasets/${datasetId}`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.deleteDataset');
      throw handledError;
    }
  }

  /**
   * データセットに画像を追加
   */
  async addImageToDataset(datasetId: string, formData: FormData): Promise<DatasetImage> {
    try {
      const response: AxiosResponse<DatasetImage> = 
        await this.client.post(`/api/vision/datasets/${datasetId}/images`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.addImageToDataset');
      throw handledError;
    }
  }

  /**
   * 物体検出を実行
   */
  async detectObjects(request: DetectionRequest): Promise<DetectionResult> {
    try {
      const response: AxiosResponse<DetectionResult> = 
        await this.client.post('/api/vision/detection', request);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.detectObjects');
      throw handledError;
    }
  }

  /**
   * 物体追跡を開始
   */
  async startTracking(request: StartTrackingRequest): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post('/api/vision/tracking/start', request);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.startTracking');
      throw handledError;
    }
  }

  /**
   * 物体追跡を停止
   */
  async stopTracking(): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.post('/api/vision/tracking/stop');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.stopTracking');
      throw handledError;
    }
  }

  /**
   * 物体追跡の状態を取得
   */
  async getTrackingStatus(): Promise<TrackingStatus> {
    try {
      const response: AxiosResponse<TrackingStatus> = 
        await this.client.get('/api/vision/tracking/status');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getTrackingStatus');
      throw handledError;
    }
  }

  // ========================================
  // Model Management APIs
  // ========================================

  /**
   * モデル一覧を取得
   */
  async getModels(): Promise<Model[]> {
    try {
      const response: AxiosResponse<Model[]> = await this.client.get('/api/models');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getModels');
      throw handledError;
    }
  }

  /**
   * モデル学習を開始
   */
  async trainModel(request: TrainModelRequest): Promise<TrainingJob> {
    try {
      const response: AxiosResponse<TrainingJob> = 
        await this.client.post('/api/models', request);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.trainModel');
      throw handledError;
    }
  }

  /**
   * モデル詳細を取得
   */
  async getModel(modelId: string): Promise<Model> {
    try {
      const response: AxiosResponse<Model> = 
        await this.client.get(`/api/models/${modelId}`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getModel');
      throw handledError;
    }
  }

  /**
   * モデルを削除
   */
  async deleteModel(modelId: string): Promise<SuccessResponse> {
    try {
      const response: AxiosResponse<SuccessResponse> = 
        await this.client.delete(`/api/models/${modelId}`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.deleteModel');
      throw handledError;
    }
  }

  /**
   * 学習ジョブの状況を取得
   */
  async getTrainingJob(jobId: string): Promise<TrainingJob> {
    try {
      const response: AxiosResponse<TrainingJob> = 
        await this.client.get(`/api/models/training/${jobId}`);
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getTrainingJob');
      throw handledError;
    }
  }

  // ========================================
  // Dashboard APIs
  // ========================================

  /**
   * ダッシュボード用ドローン群状態を取得
   */
  async getDashboardDrones(): Promise<DroneStatus[]> {
    try {
      const response: AxiosResponse<DroneStatus[]> = 
        await this.client.get('/api/dashboard/drones');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getDashboardDrones');
      throw handledError;
    }
  }

  /**
   * ダッシュボード用システム状態を取得
   */
  async getDashboardSystemStatus(): Promise<SystemStatus> {
    try {
      const response: AxiosResponse<SystemStatus> = 
        await this.client.get('/api/dashboard/system');
      return response.data;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'BackendClient.getDashboardSystemStatus');
      throw handledError;
    }
  }

  /**
   * バックエンド接続をテスト
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      logger.info(`Backend connection successful: ${this.config.backendUrl}`);
      return true;
    } catch (error) {
      logger.error(`Backend connection failed: ${this.config.backendUrl}`, error);
      return false;
    }
  }
}