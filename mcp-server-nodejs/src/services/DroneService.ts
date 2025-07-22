import { BackendClient } from '@/clients/BackendClient.js';
import { logger } from '@/utils/logger.js';
import { ErrorHandler } from '@/utils/errors.js';
import { DroneError, type DroneStatus, type SystemStatus } from '@/types/index.js';
import type { Config } from '@/types/index.js';

/**
 * ドローンサービス
 * ドローン関連のビジネスロジックを担当
 */
export class DroneService {
  private backendClient: BackendClient;
  private statusCache: Map<string, { data: DroneStatus; timestamp: number }>;
  private cacheTimeout: number;

  constructor(config: Config) {
    this.backendClient = new BackendClient(config);
    this.statusCache = new Map();
    this.cacheTimeout = 30000; // 30秒のキャッシュ
  }

  /**
   * ドローンの状態を取得（キャッシュ機能付き）
   */
  async getDroneStatus(droneId?: string): Promise<DroneStatus[]> {
    try {
      const cacheKey = droneId || 'all';
      const cached = this.statusCache.get(cacheKey);
      const now = Date.now();

      // キャッシュが有効な場合は返す
      if (cached && (now - cached.timestamp) < this.cacheTimeout) {
        logger.debug(`Returning cached drone status for: ${cacheKey}`);
        return [cached.data];
      }

      // バックエンドから取得
      const statuses = await this.backendClient.getDroneStatus(droneId);
      
      // キャッシュを更新
      if (statuses.length === 1 && droneId) {
        this.statusCache.set(cacheKey, {
          data: statuses[0],
          timestamp: now,
        });
      }

      logger.info(`Retrieved drone status for ${statuses.length} drone(s)`);
      return statuses;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'DroneService.getDroneStatus');
      throw handledError;
    }
  }

  /**
   * アクティブなドローンを取得
   */
  async getActiveDrones(): Promise<DroneStatus[]> {
    try {
      const allDrones = await this.getDroneStatus();
      const activeDrones = allDrones.filter(
        drone => ['connected', 'flying', 'idle'].includes(drone.status)
      );
      
      logger.info(`Found ${activeDrones.length} active drones`);
      return activeDrones;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'DroneService.getActiveDrones');
      throw handledError;
    }
  }

  /**
   * ドローンをスキャン
   */
  async scanForDrones(): Promise<{ message: string; found: number }> {
    try {
      logger.info('Starting drone scan...');
      const result = await this.backendClient.scanDrones();
      
      // スキャン後はキャッシュをクリア
      this.clearCache();
      
      logger.info(`Drone scan completed: ${result.message} (found: ${result.found})`);
      return result;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'DroneService.scanForDrones');
      throw handledError;
    }
  }

  /**
   * システム状態を取得
   */
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const status = await this.backendClient.getSystemStatus();
      logger.debug(`System status: ${status.status}`);
      return status;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'DroneService.getSystemStatus');
      throw handledError;
    }
  }

  /**
   * システムの健全性をチェック
   */
  async performHealthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const health = await this.backendClient.healthCheck();
      logger.debug(`Health check result: ${health.status}`);
      return health;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'DroneService.performHealthCheck');
      throw handledError;
    }
  }

  /**
   * ドローンコマンドを実行
   */
  async executeCommand(
    droneId: string,
    command: string,
    params?: Record<string, unknown>
  ): Promise<{ success: boolean; message: string }> {
    try {
      // コマンド実行前の検証
      await this.validateDroneCommand(droneId, command);

      logger.info(`Executing command '${command}' on drone ${droneId}`, { params });
      const result = await this.backendClient.executeCommand(droneId, command, params);

      // コマンド実行後はキャッシュをクリア
      this.clearCacheForDrone(droneId);

      logger.info(`Command execution result: ${result.message}`, {
        droneId,
        command,
        success: result.success,
      });

      return result;
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'DroneService.executeCommand');
      throw handledError;
    }
  }

  /**
   * ドローンコマンドの検証
   */
  private async validateDroneCommand(droneId: string, command: string): Promise<void> {
    // 危険なコマンドのチェック
    const dangerousCommands = ['emergency', 'land_immediate', 'reset'];
    if (dangerousCommands.includes(command)) {
      throw new DroneError(
        `Command '${command}' requires additional confirmation`,
        'DANGEROUS_COMMAND',
        400
      );
    }

    // ドローンの状態確認
    try {
      const statuses = await this.getDroneStatus(droneId);
      const drone = statuses.find(d => d.id === droneId);
      
      if (!drone) {
        throw new DroneError(`Drone ${droneId} not found`, 'DRONE_NOT_FOUND', 404);
      }

      if (drone.status === 'error') {
        throw new DroneError(
          `Drone ${droneId} is in error state`,
          'DRONE_ERROR_STATE',
          400
        );
      }

      if (drone.status === 'disconnected') {
        throw new DroneError(
          `Drone ${droneId} is disconnected`,
          'DRONE_DISCONNECTED',
          400
        );
      }
    } catch (error) {
      // 状態確認が失敗した場合でも、コマンド実行は継続する
      logger.warn(`Could not validate drone ${droneId} status:`, error);
    }
  }

  /**
   * キャッシュをクリア
   */
  private clearCache(): void {
    this.statusCache.clear();
    logger.debug('Drone status cache cleared');
  }

  /**
   * 特定のドローンのキャッシュをクリア
   */
  private clearCacheForDrone(droneId: string): void {
    this.statusCache.delete(droneId);
    this.statusCache.delete('all');
    logger.debug(`Cache cleared for drone: ${droneId}`);
  }

  /**
   * バックエンド接続テスト
   */
  async testBackendConnection(): Promise<boolean> {
    try {
      return await this.backendClient.testConnection();
    } catch (error) {
      logger.error('Backend connection test failed:', error);
      return false;
    }
  }
}