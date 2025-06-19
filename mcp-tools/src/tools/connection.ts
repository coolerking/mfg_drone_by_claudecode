import { MCPTool } from './registry.js';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';

export const droneConnectTool: MCPTool = {
  name: 'drone_connect',
  description: 'Connect to the Tello EDU drone. This establishes communication with the drone and prepares it for flight operations.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false
  },
  async handler(args: {}, client: FastAPIClient, logger: Logger) {
    try {
      const response = await client.connect();
      
      if (response.success) {
        return {
          success: true,
          message: 'ドローンに正常に接続しました。飛行操作の準備が完了しています。',
          details: {
            connected: true,
            status: 'ready_for_flight'
          }
        };
      } else {
        return {
          success: false,
          message: `ドローンの接続に失敗しました: ${response.message}`,
          error: 'CONNECTION_FAILED'
        };
      }
    } catch (error: any) {
      logger.error('Drone connection failed', error);
      return {
        success: false,
        message: `ドローンの接続中にエラーが発生しました: ${error.message}`,
        error: 'CONNECTION_ERROR',
        details: {
          error_type: error.response?.status === 503 ? 'DRONE_NOT_AVAILABLE' : 'NETWORK_ERROR'
        }
      };
    }
  }
};

export const droneDisconnectTool: MCPTool = {
  name: 'drone_disconnect',
  description: 'Safely disconnect from the Tello EDU drone. This terminates communication and ensures the drone is in a safe state.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false
  },
  async handler(args: {}, client: FastAPIClient, logger: Logger) {
    try {
      const response = await client.disconnect();
      
      if (response.success) {
        return {
          success: true,
          message: 'ドローンから正常に切断しました。',
          details: {
            connected: false,
            status: 'disconnected'
          }
        };
      } else {
        return {
          success: false,
          message: `ドローンの切断に失敗しました: ${response.message}`,
          error: 'DISCONNECTION_FAILED'
        };
      }
    } catch (error: any) {
      logger.error('Drone disconnection failed', error);
      return {
        success: false,
        message: `ドローンの切断中にエラーが発生しました: ${error.message}`,
        error: 'DISCONNECTION_ERROR'
      };
    }
  }
};

export const droneStatusTool: MCPTool = {
  name: 'drone_status',
  description: 'Get comprehensive status information about the drone including battery, position, sensors, and flight state.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false
  },
  async handler(args: {}, client: FastAPIClient, logger: Logger) {
    try {
      const status = await client.getDroneStatus();
      
      // Format status for human readability
      const batteryStatus = status.battery > 30 ? '良好' : status.battery > 15 ? '注意' : '危険';
      const tempStatus = status.temperature < 60 ? '正常' : status.temperature < 80 ? '注意' : '警告';
      
      return {
        success: true,
        message: 'ドローンのステータスを正常に取得しました。',
        data: {
          connection: {
            connected: status.connected,
            status: status.connected ? '接続中' : '未接続'
          },
          battery: {
            level: status.battery,
            percentage: `${status.battery}%`,
            status: batteryStatus,
            warning: status.battery <= 15 ? 'バッテリー残量が少なくなっています。着陸を検討してください。' : null
          },
          position: {
            height: status.height,
            height_meters: `${(status.height / 100).toFixed(1)}m`
          },
          environment: {
            temperature: status.temperature,
            temperature_celsius: `${status.temperature}°C`,
            temperature_status: tempStatus,
            barometer: status.barometer,
            barometer_hpa: `${status.barometer.toFixed(1)} hPa`
          },
          flight_info: {
            flight_time: status.flight_time,
            flight_time_formatted: `${Math.floor(status.flight_time / 60)}分${status.flight_time % 60}秒`,
            current_speed: status.speed,
            distance_sensor: status.distance_tof
          },
          attitude: {
            pitch: status.attitude.pitch,
            roll: status.attitude.roll,
            yaw: status.attitude.yaw,
            description: `ピッチ: ${status.attitude.pitch}°, ロール: ${status.attitude.roll}°, ヨー: ${status.attitude.yaw}°`
          },
          velocity: {
            x: status.velocity.x,
            y: status.velocity.y,
            z: status.velocity.z,
            description: `X: ${status.velocity.x}cm/s, Y: ${status.velocity.y}cm/s, Z: ${status.velocity.z}cm/s`
          },
          acceleration: {
            x: status.acceleration.x,
            y: status.acceleration.y,
            z: status.acceleration.z,
            description: `X: ${status.acceleration.x}g, Y: ${status.acceleration.y}g, Z: ${status.acceleration.z}g`
          }
        }
      };
    } catch (error: any) {
      logger.error('Failed to get drone status', error);
      
      if (error.response?.status === 503) {
        return {
          success: false,
          message: 'ドローンが接続されていないため、ステータスを取得できません。',
          error: 'DRONE_NOT_CONNECTED',
          suggestion: 'まずドローンに接続してください (drone_connect)'
        };
      }
      
      return {
        success: false,
        message: `ドローンステータスの取得中にエラーが発生しました: ${error.message}`,
        error: 'STATUS_ERROR'
      };
    }
  }
};

export const connectionTools = [
  droneConnectTool,
  droneDisconnectTool,
  droneStatusTool
];