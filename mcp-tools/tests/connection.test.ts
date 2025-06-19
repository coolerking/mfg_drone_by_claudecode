import { jest } from '@jest/globals';
import { FastAPIClient } from '../src/bridge/api-client.js';
import { Logger } from '../src/utils/logger.js';
import { droneConnectTool, droneDisconnectTool, droneStatusTool } from '../src/tools/connection.js';
import { ServerConfig } from '../src/types/config.js';

// Mock axios
jest.mock('axios');

describe('Connection Tools Tests', () => {
  let client: FastAPIClient;
  let logger: Logger;
  let mockConfig: ServerConfig;

  beforeEach(() => {
    mockConfig = {
      backendUrl: 'http://localhost:8000',
      timeout: 5000,
      retries: 2,
      debug: false,
      logLevel: 'error'
    };
    
    logger = new Logger(mockConfig);
    client = new FastAPIClient(mockConfig, logger);

    // Mock logger methods
    jest.spyOn(logger, 'debug').mockImplementation();
    jest.spyOn(logger, 'info').mockImplementation();
    jest.spyOn(logger, 'warn').mockImplementation();
    jest.spyOn(logger, 'error').mockImplementation();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('TC-CON-001: ドローン接続成功', () => {
    it('should successfully connect to drone', async () => {
      // Arrange
      const mockResponse = {
        success: true,
        message: 'Connected successfully'
      };
      jest.spyOn(client, 'connect').mockResolvedValue(mockResponse);

      // Act
      const result = await droneConnectTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: true,
        message: 'ドローンに正常に接続しました。飛行操作の準備が完了しています。',
        details: {
          connected: true,
          status: 'ready_for_flight'
        }
      });
      expect(client.connect).toHaveBeenCalledTimes(1);
    });
  });

  describe('TC-CON-002: ドローン切断成功', () => {
    it('should successfully disconnect from drone', async () => {
      // Arrange
      const mockResponse = {
        success: true,
        message: 'Disconnected successfully'
      };
      jest.spyOn(client, 'disconnect').mockResolvedValue(mockResponse);

      // Act
      const result = await droneDisconnectTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: true,
        message: 'ドローンから正常に切断しました。',
        details: {
          connected: false,
          status: 'disconnected'
        }
      });
      expect(client.disconnect).toHaveBeenCalledTimes(1);
    });
  });

  describe('TC-CON-003: 接続失敗（ドローン電源OFF）', () => {
    it('should handle connection failure when drone is powered off', async () => {
      // Arrange
      const mockError = {
        response: { status: 503 },
        message: 'Service unavailable'
      };
      jest.spyOn(client, 'connect').mockRejectedValue(mockError);

      // Act
      const result = await droneConnectTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンの接続中にエラーが発生しました: Service unavailable',
        error: 'CONNECTION_ERROR',
        details: {
          error_type: 'DRONE_NOT_AVAILABLE'
        }
      });
      expect(logger.error).toHaveBeenCalledWith('Drone connection failed', mockError);
    });
  });

  describe('TC-CON-004: 重複接続試行', () => {
    it('should handle duplicate connection attempts', async () => {
      // Arrange
      const mockResponse = {
        success: false,
        message: 'Already connected'
      };
      jest.spyOn(client, 'connect').mockResolvedValue(mockResponse);

      // Act
      const result = await droneConnectTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンの接続に失敗しました: Already connected',
        error: 'CONNECTION_FAILED'
      });
    });
  });

  describe('TC-CON-005: 未接続状態での切断試行', () => {
    it('should handle disconnection when not connected', async () => {
      // Arrange
      const mockResponse = {
        success: false,
        message: 'Not connected'
      };
      jest.spyOn(client, 'disconnect').mockResolvedValue(mockResponse);

      // Act
      const result = await droneDisconnectTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンの切断に失敗しました: Not connected',
        error: 'DISCONNECTION_FAILED'
      });
    });
  });

  describe('TC-CON-006: 接続タイムアウト', () => {
    it('should handle connection timeout', async () => {
      // Arrange
      const mockError = {
        response: { status: 408 },
        message: 'Request timeout'
      };
      jest.spyOn(client, 'connect').mockRejectedValue(mockError);

      // Act
      const result = await droneConnectTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンの接続中にエラーが発生しました: Request timeout',
        error: 'CONNECTION_ERROR',
        details: {
          error_type: 'NETWORK_ERROR'
        }
      });
    });
  });

  describe('TC-CON-007: ネットワーク断絶での操作', () => {
    it('should handle network disconnection', async () => {
      // Arrange
      const mockError = {
        message: 'Network Error',
        code: 'ECONNREFUSED'
      };
      jest.spyOn(client, 'connect').mockRejectedValue(mockError);

      // Act
      const result = await droneConnectTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンの接続中にエラーが発生しました: Network Error',
        error: 'CONNECTION_ERROR',
        details: {
          error_type: 'NETWORK_ERROR'
        }
      });
    });
  });

  describe('Drone Status Tests', () => {
    describe('TC-SEN-001: バッテリー残量取得 (via status)', () => {
      it('should get comprehensive drone status including battery', async () => {
        // Arrange
        const mockStatus = {
          connected: true,
          battery: 85,
          height: 120,
          temperature: 45,
          flight_time: 300,
          speed: 15.5,
          barometer: 1013.25,
          distance_tof: 500,
          acceleration: { x: 0.1, y: 0.2, z: 9.8 },
          velocity: { x: 10, y: 5, z: 0 },
          attitude: { pitch: 2, roll: -1, yaw: 45 }
        };
        jest.spyOn(client, 'getDroneStatus').mockResolvedValue(mockStatus);

        // Act
        const result = await droneStatusTool.handler({}, client, logger);

        // Assert
        expect(result.success).toBe(true);
        expect(result.data.battery.level).toBe(85);
        expect(result.data.battery.status).toBe('良好');
        expect(result.data.battery.warning).toBeNull();
        expect(result.data.connection.connected).toBe(true);
        expect(result.data.position.height_meters).toBe('1.2m');
        expect(result.data.environment.temperature_status).toBe('正常');
      });
    });

    describe('TC-SEN-010: バッテリー境界値確認', () => {
      it('should handle low battery warning (15%)', async () => {
        // Arrange
        const mockStatus = {
          connected: true,
          battery: 15,
          height: 120,
          temperature: 45,
          flight_time: 300,
          speed: 15.5,
          barometer: 1013.25,
          distance_tof: 500,
          acceleration: { x: 0.1, y: 0.2, z: 9.8 },
          velocity: { x: 10, y: 5, z: 0 },
          attitude: { pitch: 2, roll: -1, yaw: 45 }
        };
        jest.spyOn(client, 'getDroneStatus').mockResolvedValue(mockStatus);

        // Act
        const result = await droneStatusTool.handler({}, client, logger);

        // Assert
        expect(result.data.battery.status).toBe('危険');
        expect(result.data.battery.warning).toBe('バッテリー残量が少なくなっています。着陸を検討してください。');
      });

      it('should handle medium battery warning (25%)', async () => {
        // Arrange
        const mockStatus = {
          connected: true,
          battery: 25,
          height: 120,
          temperature: 45,
          flight_time: 300,
          speed: 15.5,
          barometer: 1013.25,
          distance_tof: 500,
          acceleration: { x: 0.1, y: 0.2, z: 9.8 },
          velocity: { x: 10, y: 5, z: 0 },
          attitude: { pitch: 2, roll: -1, yaw: 45 }
        };
        jest.spyOn(client, 'getDroneStatus').mockResolvedValue(mockStatus);

        // Act
        const result = await droneStatusTool.handler({}, client, logger);

        // Assert
        expect(result.data.battery.status).toBe('注意');
        expect(result.data.battery.warning).toBeNull();
      });
    });

    describe('TC-SEN-019: 未接続でのセンサー読み取り', () => {
      it('should handle status request when drone not connected', async () => {
        // Arrange
        const mockError = {
          response: { status: 503 },
          message: 'Service unavailable'
        };
        jest.spyOn(client, 'getDroneStatus').mockRejectedValue(mockError);

        // Act
        const result = await droneStatusTool.handler({}, client, logger);

        // Assert
        expect(result).toEqual({
          success: false,
          message: 'ドローンが接続されていないため、ステータスを取得できません。',
          error: 'DRONE_NOT_CONNECTED',
          suggestion: 'まずドローンに接続してください (drone_connect)'
        });
      });
    });
  });

  describe('Performance Tests', () => {
    describe('TC-PERF-001: API応答時間確認', () => {
      it('should complete connection within 100ms', async () => {
        // Arrange
        const mockResponse = { success: true, message: 'Connected' };
        jest.spyOn(client, 'connect').mockResolvedValue(mockResponse);
        
        const startTime = Date.now();

        // Act
        await droneConnectTool.handler({}, client, logger);
        
        // Assert
        const duration = Date.now() - startTime;
        expect(duration).toBeLessThan(100);
      });
    });

    describe('TC-PERF-002: 連続コマンド処理時間', () => {
      it('should handle 10 consecutive API calls efficiently', async () => {
        // Arrange
        const mockResponse = { success: true, message: 'Status OK' };
        jest.spyOn(client, 'getDroneStatus').mockResolvedValue({
          connected: true,
          battery: 85,
          height: 120,
          temperature: 45,
          flight_time: 300,
          speed: 15.5,
          barometer: 1013.25,
          distance_tof: 500,
          acceleration: { x: 0.1, y: 0.2, z: 9.8 },
          velocity: { x: 10, y: 5, z: 0 },
          attitude: { pitch: 2, roll: -1, yaw: 45 }
        });

        const startTime = Date.now();

        // Act
        const promises = Array(10).fill(null).map(() => 
          droneStatusTool.handler({}, client, logger)
        );
        await Promise.all(promises);

        // Assert
        const duration = Date.now() - startTime;
        const averageTime = duration / 10;
        expect(averageTime).toBeLessThan(100);
      });
    });
  });
});