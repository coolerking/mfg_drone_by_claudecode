import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

/**
 * ドローン接続ツール
 * 指定されたドローンに接続を試行する
 */
export class ConnectDroneTool extends BaseTool {
  constructor(droneService: any) {
    super(droneService, 'connect_drone');
  }

  getDescription(): string {
    return 'Connect to a specific drone by ID. This establishes communication with the drone.';
  }

  getInputSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        droneId: {
          type: 'string',
          description: 'The ID of the drone to connect to',
        },
      },
      required: ['droneId'],
    };
  }

  async execute(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    try {
      this.validateArgs(args, ['droneId']);
      const droneId = args!.droneId as string;

      logger.info(`Attempting to connect to drone: ${droneId}`);

      // コマンド実行
      const result = await this.droneService.executeCommand(droneId, 'connect');

      if (result.success) {
        return this.createSuccessResponse(
          `Successfully connected to drone '${droneId}'. ${result.message}`
        );
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      return this.createErrorResponse(error);
    }
  }
}