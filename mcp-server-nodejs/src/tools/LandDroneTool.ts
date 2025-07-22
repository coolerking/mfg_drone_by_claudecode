import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

/**
 * ドローン着陸ツール
 * 指定されたドローンを着陸させる
 */
export class LandDroneTool extends BaseTool {
  constructor(droneService: any) {
    super(droneService, 'land_drone');
  }

  getDescription(): string {
    return 'Land a drone safely. The drone must be flying to execute this command.';
  }

  getInputSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        droneId: {
          type: 'string',
          description: 'The ID of the drone to land',
        },
        immediate: {
          type: 'boolean',
          description: 'Whether to land immediately (emergency land) or safely (default: false)',
          default: false,
        },
      },
      required: ['droneId'],
    };
  }

  async execute(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    try {
      this.validateArgs(args, ['droneId']);
      const droneId = args!.droneId as string;
      const immediate = args!.immediate as boolean || false;

      logger.info(`Attempting ${immediate ? 'immediate' : 'safe'} landing for drone: ${droneId}`);

      // ドローンの状態確認
      await this.validateAndGetDrone(droneId);

      // 飛行中かチェック
      const statuses = await this.droneService.getDroneStatus(droneId);
      const drone = statuses.find(d => d.id === droneId);
      
      if (drone && drone.status !== 'flying') {
        logger.warn(`Drone '${droneId}' is not flying (status: ${drone.status}), but proceeding with land command`);
      }

      // コマンドパラメータ
      const params = { immediate };

      // コマンド実行
      const result = await this.droneService.executeCommand(droneId, 'land', params);

      if (result.success) {
        const landingType = immediate ? 'Emergency landing' : 'Safe landing';
        return this.createSuccessResponse(
          `${landingType} initiated for drone '${droneId}'. ${result.message}`
        );
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      return this.createErrorResponse(error);
    }
  }
}