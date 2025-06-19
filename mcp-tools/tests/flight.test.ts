import { jest } from '@jest/globals';
import { FastAPIClient } from '../src/bridge/api-client.js';
import { Logger } from '../src/utils/logger.js';
import { 
  droneTakeoffTool, 
  droneLandTool, 
  droneEmergencyTool, 
  droneStopTool, 
  droneGetHeightTool 
} from '../src/tools/flight.js';
import { ServerConfig } from '../src/types/config.js';

describe('Flight Control Tools Tests', () => {
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

  describe('TC-FLT-001: 離陸成功', () => {
    it('should successfully take off', async () => {
      // Arrange
      const mockResponse = {
        success: true,
        message: 'Takeoff successful'
      };
      jest.spyOn(client, 'takeoff').mockResolvedValue(mockResponse);

      // Act
      const result = await droneTakeoffTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: true,
        message: 'ドローンが正常に離陸しました。安全な高度でホバリングしています。',
        details: {
          status: 'flying',
          action: 'takeoff_completed',
          altitude: '約80-120cm',
          next_actions: ['移動操作', '着陸', '緊急停止が可能です']
        }
      });
      expect(client.takeoff).toHaveBeenCalledTimes(1);
    });
  });

  describe('TC-FLT-002: 着陸成功', () => {
    it('should successfully land', async () => {
      // Arrange
      const mockResponse = {
        success: true,
        message: 'Landing successful'
      };
      jest.spyOn(client, 'land').mockResolvedValue(mockResponse);

      // Act
      const result = await droneLandTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: true,
        message: 'ドローンが正常に着陸しました。',
        details: {
          status: 'landed',
          action: 'landing_completed',
          next_actions: ['再離陸', '接続解除が可能です']
        }
      });
      expect(client.land).toHaveBeenCalledTimes(1);
    });
  });

  describe('TC-FLT-003: 緊急停止成功', () => {
    it('should successfully execute emergency stop', async () => {
      // Arrange
      const mockResponse = {
        success: true,
        message: 'Emergency stop executed'
      };
      jest.spyOn(client, 'emergency').mockResolvedValue(mockResponse);

      // Act
      const result = await droneEmergencyTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: true,
        message: '緊急停止を実行しました。ドローンのモーターが停止しました。',
        details: {
          status: 'emergency_stopped',
          action: 'emergency_executed',
          warning: 'ドローンは落下します。安全を確認してください。',
          next_actions: ['ドローンの状態確認', '物理的な安全確認']
        }
      });
      expect(client.emergency).toHaveBeenCalledTimes(1);
    });
  });

  describe('TC-FLT-004: ホバリング成功', () => {
    it('should successfully stop and hover', async () => {
      // Arrange
      const mockResponse = {
        success: true,
        message: 'Stop successful'
      };
      jest.spyOn(client, 'stop').mockResolvedValue(mockResponse);

      // Act
      const result = await droneStopTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: true,
        message: 'ドローンを停止し、現在位置でホバリングしています。',
        details: {
          status: 'hovering',
          action: 'stop_completed',
          description: '全ての移動を停止し、安定したホバリング状態です',
          next_actions: ['移動操作', '着陸', '緊急停止が可能です']
        }
      });
      expect(client.stop).toHaveBeenCalledTimes(1);
    });
  });

  describe('TC-FLT-005: 未接続での離陸試行', () => {
    it('should handle takeoff when drone not connected', async () => {
      // Arrange
      const mockError = {
        response: { status: 503 },
        message: 'Service unavailable'
      };
      jest.spyOn(client, 'takeoff').mockRejectedValue(mockError);

      // Act
      const result = await droneTakeoffTool.handler({}, client, logger);

      // Assert
      expect(result.success).toBe(false);
      expect(result.message).toContain('離陸中にエラーが発生しました');
      expect(result.error).toBe('TAKEOFF_ERROR');
      expect(logger.error).toHaveBeenCalledWith('Drone takeoff failed', mockError);
    });
  });

  describe('TC-FLT-006: 飛行中での離陸試行', () => {
    it('should handle takeoff when already flying', async () => {
      // Arrange
      const mockError = {
        response: { status: 409 },
        message: 'Already flying'
      };
      jest.spyOn(client, 'takeoff').mockRejectedValue(mockError);

      // Act
      const result = await droneTakeoffTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンは既に飛行中です。',
        error: 'ALREADY_FLYING',
        suggestion: '着陸してから再度離陸するか、他の飛行操作を行ってください。'
      });
    });
  });

  describe('TC-FLT-007: 着陸状態での着陸試行', () => {
    it('should handle land when not flying', async () => {
      // Arrange
      const mockError = {
        response: { status: 409 },
        message: 'Not flying'
      };
      jest.spyOn(client, 'land').mockRejectedValue(mockError);

      // Act
      const result = await droneLandTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンは飛行していないため着陸できません。',
        error: 'NOT_FLYING',
        suggestion: 'まず離陸してから着陸操作を行ってください。'
      });
    });
  });

  describe('TC-FLT-008: 低バッテリー時飛行試行', () => {
    it('should handle takeoff with low battery', async () => {
      // Arrange
      const mockError = {
        response: { status: 400 },
        message: 'Low battery'
      };
      jest.spyOn(client, 'takeoff').mockRejectedValue(mockError);

      // Act
      const result = await droneTakeoffTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: '離陸条件が満たされていません。',
        error: 'TAKEOFF_CONDITIONS_NOT_MET',
        possible_causes: [
          'バッテリー残量不足',
          '障害物の検知',
          'ドローンの状態異常'
        ],
        suggestion: 'ドローンの状態を確認してください (drone_status)'
      });
    });
  });

  describe('TC-FLT-009: 離陸コマンド失敗', () => {
    it('should handle takeoff command failure', async () => {
      // Arrange
      const mockResponse = {
        success: false,
        message: 'Takeoff command failed'
      };
      jest.spyOn(client, 'takeoff').mockResolvedValue(mockResponse);

      // Act
      const result = await droneTakeoffTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: '離陸に失敗しました: Takeoff command failed',
        error: 'TAKEOFF_FAILED'
      });
    });
  });

  describe('TC-FLT-010: 着陸コマンド失敗', () => {
    it('should handle landing command failure', async () => {
      // Arrange
      const mockResponse = {
        success: false,
        message: 'Landing command failed'
      };
      jest.spyOn(client, 'land').mockResolvedValue(mockResponse);

      // Act
      const result = await droneLandTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: '着陸に失敗しました: Landing command failed',
        error: 'LANDING_FAILED'
      });
    });
  });

  describe('TC-FLT-011: 緊急停止失敗', () => {
    it('should handle emergency stop failure', async () => {
      // Arrange
      const mockError = {
        message: 'Emergency stop failed'
      };
      jest.spyOn(client, 'emergency').mockRejectedValue(mockError);

      // Act
      const result = await droneEmergencyTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: '緊急停止中にエラーが発生しました: Emergency stop failed',
        error: 'EMERGENCY_ERROR',
        warning: '緊急停止が失敗しました。物理的な安全確保を検討してください。'
      });
      expect(logger.error).toHaveBeenCalledWith('Drone emergency stop failed', mockError);
    });
  });

  describe('TC-FLT-012: コマンドタイムアウト', () => {
    it('should handle command timeout', async () => {
      // Arrange
      const mockError = {
        response: { status: 408 },
        message: 'Request timeout'
      };
      jest.spyOn(client, 'takeoff').mockRejectedValue(mockError);

      // Act
      const result = await droneTakeoffTool.handler({}, client, logger);

      // Assert
      expect(result.success).toBe(false);
      expect(result.message).toContain('離陸中にエラーが発生しました');
      expect(result.error).toBe('TAKEOFF_ERROR');
    });
  });

  describe('Height Tests', () => {
    describe('TC-SEN-002: 飛行高度取得', () => {
      it('should get current flight height', async () => {
        // Arrange
        const mockResponse = { height: 150 };
        jest.spyOn(client, 'getHeight').mockResolvedValue(mockResponse);

        // Act
        const result = await droneGetHeightTool.handler({}, client, logger);

        // Assert
        expect(result).toEqual({
          success: true,
          message: 'ドローンの現在高度を取得しました。',
          data: {
            height: 150,
            height_cm: '150cm',
            height_meters: '1.5m',
            status: '通常高度',
            safe_range: true,
            warnings: []
          }
        });
      });
    });

    describe('TC-SEN-011: 高度境界値確認', () => {
      it('should handle low altitude warning', async () => {
        // Arrange
        const mockResponse = { height: 25 };
        jest.spyOn(client, 'getHeight').mockResolvedValue(mockResponse);

        // Act
        const result = await droneGetHeightTool.handler({}, client, logger);

        // Assert
        expect(result.data.status).toBe('低高度');
        expect(result.data.safe_range).toBe(false);
        expect(result.data.warnings).toEqual(['高度が低すぎます']);
      });

      it('should handle high altitude warning', async () => {
        // Arrange
        const mockResponse = { height: 3500 };
        jest.spyOn(client, 'getHeight').mockResolvedValue(mockResponse);

        // Act
        const result = await droneGetHeightTool.handler({}, client, logger);

        // Assert
        expect(result.data.status).toBe('高高度');
        expect(result.data.safe_range).toBe(false);
        expect(result.data.warnings).toEqual(['高度が高すぎます']);
      });

      it('should handle normal altitude', async () => {
        // Arrange
        const mockResponse = { height: 200 };
        jest.spyOn(client, 'getHeight').mockResolvedValue(mockResponse);

        // Act
        const result = await droneGetHeightTool.handler({}, client, logger);

        // Assert
        expect(result.data.status).toBe('高高度');
        expect(result.data.safe_range).toBe(true);
        expect(result.data.warnings).toEqual([]);
      });
    });

    it('should handle height request when drone not connected', async () => {
      // Arrange
      const mockError = {
        response: { status: 503 },
        message: 'Service unavailable'
      };
      jest.spyOn(client, 'getHeight').mockRejectedValue(mockError);

      // Act
      const result = await droneGetHeightTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンが接続されていないため、高度を取得できません。',
        error: 'DRONE_NOT_CONNECTED',
        suggestion: 'まずドローンに接続してください (drone_connect)'
      });
    });
  });

  describe('Stop/Hover Tests', () => {
    it('should handle stop when not flying', async () => {
      // Arrange
      const mockError = {
        response: { status: 409 },
        message: 'Not flying'
      };
      jest.spyOn(client, 'stop').mockRejectedValue(mockError);

      // Act
      const result = await droneStopTool.handler({}, client, logger);

      // Assert
      expect(result).toEqual({
        success: false,
        message: 'ドローンは飛行していないため停止できません。',
        error: 'NOT_FLYING',
        suggestion: 'まず離陸してから停止操作を行ってください。'
      });
    });
  });
});