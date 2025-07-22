import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

/**
 * ドローン離陸ツール
 * 指定されたドローンを離陸させる
 */
export class TakeoffDroneTool extends BaseTool {
  constructor(droneService: any) {
    super(droneService, 'takeoff_drone');
  }

  getDescription(): string {
    return 'Take off a drone. The drone must be connected and on the ground.';
  }

  getInputSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        droneId: {
          type: 'string',
          description: 'The ID of the drone to take off',
        },
        altitude: {
          type: 'number',
          description: 'Target altitude in meters (optional, default: 1.2m)',
          minimum: 0.5,
          maximum: 10.0,
        },
      },
      required: ['droneId'],
    };
  }

  async execute(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    try {
      this.validateArgs(args, ['droneId']);
      const droneId = args!.droneId as string;
      const altitude = args!.altitude as number || 1.2;

      logger.info(`Attempting takeoff for drone: ${droneId} at altitude: ${altitude}m`);

      // ドローンの状態確認
      await this.validateAndGetDrone(droneId);

      // コマンドパラメータ
      const params = { altitude };

      // コマンド実行
      const result = await this.droneService.executeCommand(droneId, 'takeoff', params);

      if (result.success) {
        return this.createSuccessResponse(
          `Drone '${droneId}' took off successfully to ${altitude}m altitude. ${result.message}`
        );
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      return this.createErrorResponse(error);
    }
  }
}