import { MCPTool } from './registry.js';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';

export const droneTakeoffTool: MCPTool = {
  name: 'drone_takeoff',
  description: 'Make the drone take off and hover at a safe altitude (80-120cm). The drone must be connected and on the ground.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false
  },
  async handler(args: {}, client: FastAPIClient, logger: Logger) {
    try {
      const response = await client.takeoff();
      
      if (response.success) {
        return {
          success: true,
          message: 'ドローンが正常に離陸しました。安全な高度でホバリングしています。',
          details: {
            status: 'flying',
            action: 'takeoff_completed',
            altitude: '約80-120cm',
            next_actions: ['移動操作', '着陸', '緊急停止が可能です']
          }
        };
      } else {
        return {
          success: false,
          message: `離陸に失敗しました: ${response.message}`,
          error: 'TAKEOFF_FAILED'
        };
      }
    } catch (error: any) {
      logger.error('Drone takeoff failed', error);
      
      if (error.response?.status === 409) {
        return {
          success: false,
          message: 'ドローンは既に飛行中です。',
          error: 'ALREADY_FLYING',
          suggestion: '着陸してから再度離陸するか、他の飛行操作を行ってください。'
        };
      }
      
      if (error.response?.status === 400) {
        return {
          success: false,
          message: '離陸条件が満たされていません。',
          error: 'TAKEOFF_CONDITIONS_NOT_MET',
          possible_causes: [
            'バッテリー残量不足',
            '障害物の検知',
            'ドローンの状態異常'
          ],
          suggestion: 'ドローンの状態を確認してください (drone_status)'
        };
      }
      
      return {
        success: false,
        message: `離陸中にエラーが発生しました: ${error.message}`,
        error: 'TAKEOFF_ERROR'
      };
    }
  }
};

export const droneLandTool: MCPTool = {
  name: 'drone_land',
  description: 'Make the drone land safely at its current position. The drone must be flying.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false
  },
  async handler(args: {}, client: FastAPIClient, logger: Logger) {
    try {
      const response = await client.land();
      
      if (response.success) {
        return {
          success: true,
          message: 'ドローンが正常に着陸しました。',
          details: {
            status: 'landed',
            action: 'landing_completed',
            next_actions: ['再離陸', '接続解除が可能です']
          }
        };
      } else {
        return {
          success: false,
          message: `着陸に失敗しました: ${response.message}`,
          error: 'LANDING_FAILED'
        };
      }
    } catch (error: any) {
      logger.error('Drone landing failed', error);
      
      if (error.response?.status === 409) {
        return {
          success: false,
          message: 'ドローンは飛行していないため着陸できません。',
          error: 'NOT_FLYING',
          suggestion: 'まず離陸してから着陸操作を行ってください。'
        };
      }
      
      return {
        success: false,
        message: `着陸中にエラーが発生しました: ${error.message}`,
        error: 'LANDING_ERROR'
      };
    }
  }
};

export const droneEmergencyTool: MCPTool = {
  name: 'drone_emergency',
  description: 'Emergency stop - immediately cuts all motors causing the drone to drop. Use only in emergency situations.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false
  },
  async handler(args: {}, client: FastAPIClient, logger: Logger) {
    try {
      const response = await client.emergency();
      
      if (response.success) {
        return {
          success: true,
          message: '緊急停止を実行しました。ドローンのモーターが停止しました。',
          details: {
            status: 'emergency_stopped',
            action: 'emergency_executed',
            warning: 'ドローンは落下します。安全を確認してください。',
            next_actions: ['ドローンの状態確認', '物理的な安全確認']
          }
        };
      } else {
        return {
          success: false,
          message: `緊急停止に失敗しました: ${response.message}`,
          error: 'EMERGENCY_FAILED'
        };
      }
    } catch (error: any) {
      logger.error('Drone emergency stop failed', error);
      return {
        success: false,
        message: `緊急停止中にエラーが発生しました: ${error.message}`,
        error: 'EMERGENCY_ERROR',
        warning: '緊急停止が失敗しました。物理的な安全確保を検討してください。'
      };
    }
  }
};

export const droneStopTool: MCPTool = {
  name: 'drone_stop',
  description: 'Stop the drone and hover at current position. The drone must be flying.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false
  },
  async handler(args: {}, client: FastAPIClient, logger: Logger) {
    try {
      const response = await client.stop();
      
      if (response.success) {
        return {
          success: true,
          message: 'ドローンを停止し、現在位置でホバリングしています。',
          details: {
            status: 'hovering',
            action: 'stop_completed',
            description: '全ての移動を停止し、安定したホバリング状態です',
            next_actions: ['移動操作', '着陸', '緊急停止が可能です']
          }
        };
      } else {
        return {
          success: false,
          message: `停止操作に失敗しました: ${response.message}`,
          error: 'STOP_FAILED'
        };
      }
    } catch (error: any) {
      logger.error('Drone stop failed', error);
      
      if (error.response?.status === 409) {
        return {
          success: false,
          message: 'ドローンは飛行していないため停止できません。',
          error: 'NOT_FLYING',
          suggestion: 'まず離陸してから停止操作を行ってください。'
        };
      }
      
      return {
        success: false,
        message: `停止操作中にエラーが発生しました: ${error.message}`,
        error: 'STOP_ERROR'
      };
    }
  }
};

export const droneGetHeightTool: MCPTool = {
  name: 'drone_get_height',
  description: 'Get the current flight height of the drone in centimeters.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false
  },
  async handler(args: {}, client: FastAPIClient, logger: Logger) {
    try {
      const response = await client.getHeight();
      
      const heightMeters = (response.height / 100).toFixed(1);
      const heightStatus = response.height < 50 ? '低高度' : 
                          response.height < 200 ? '通常高度' : '高高度';
      
      return {
        success: true,
        message: `ドローンの現在高度を取得しました。`,
        data: {
          height: response.height,
          height_cm: `${response.height}cm`,
          height_meters: `${heightMeters}m`,
          status: heightStatus,
          safe_range: response.height >= 30 && response.height <= 3000,
          warnings: response.height < 30 ? ['高度が低すぎます'] : 
                   response.height > 3000 ? ['高度が高すぎます'] : []
        }
      };
    } catch (error: any) {
      logger.error('Failed to get drone height', error);
      
      if (error.response?.status === 503) {
        return {
          success: false,
          message: 'ドローンが接続されていないため、高度を取得できません。',
          error: 'DRONE_NOT_CONNECTED',
          suggestion: 'まずドローンに接続してください (drone_connect)'
        };
      }
      
      return {
        success: false,
        message: `高度取得中にエラーが発生しました: ${error.message}`,
        error: 'HEIGHT_ERROR'
      };
    }
  }
};

export const flightTools = [
  droneTakeoffTool,
  droneLandTool,
  droneEmergencyTool,
  droneStopTool,
  droneGetHeightTool
];