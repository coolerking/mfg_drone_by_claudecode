import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

/**
 * 緊急停止ツール
 * 指定されたドローンを緊急停止させる
 */
export class EmergencyStopTool extends BaseTool {
  constructor(droneService: any) {
    super(droneService, 'emergency_stop');
  }

  getDescription(): string {
    return 'Emergency stop command for immediate drone shutdown. This will stop all drone movement and land immediately for safety.';
  }

  getInputSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        droneId: {
          type: 'string',
          description: 'The ID of the drone to emergency stop',
        },
        reason: {
          type: 'string',
          description: 'Reason for emergency stop (optional, for logging)',
        },
        force: {
          type: 'boolean',
          description: 'Force emergency stop even if drone is in error state (default: true)',
          default: true,
        },
      },
      required: ['droneId'],
    };
  }

  async execute(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    try {
      this.validateArgs(args, ['droneId']);
      const droneId = args!.droneId as string;
      const reason = args!.reason as string || 'Manual emergency stop request';
      const force = args!.force as boolean !== false; // default true

      logger.warn(`Emergency stop requested for drone: ${droneId}. Reason: ${reason}`);

      // 緊急停止の場合は通常の状態確認をスキップする場合がある
      if (!force) {
        await this.validateAndGetDrone(droneId);
      } else {
        logger.info(`Force flag set, skipping drone validation for emergency stop`);
      }

      // 緊急停止パラメータ
      const params: Record<string, unknown> = {
        reason,
        force,
        timestamp: new Date().toISOString(),
      };

      // コマンド実行
      const result = await this.droneService.executeCommand(droneId, 'emergency_stop', params);

      if (result.success) {
        return this.createSuccessResponse(
          `🚨 Emergency stop executed for drone '${droneId}'. All operations halted. Reason: ${reason}. ${result.message}`
        );
      } else {
        // 緊急停止が失敗した場合でも、安全のため成功として扱うかログを記録
        logger.error(`Emergency stop command failed for drone ${droneId}: ${result.message}`);
        
        // 失敗でも緊急停止が試行されたことをレスポンスに含める
        return {
          content: [
            {
              type: 'text',
              text: `🚨 Emergency stop attempted for drone '${droneId}' but backend reported failure: ${result.message}. Please verify drone status manually and take appropriate safety measures.`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      // 緊急停止の場合は、エラーでも試行したことをログに記録
      logger.error(`Emergency stop execution failed for drone ${args?.droneId}:`, error);
      
      return {
        content: [
          {
            type: 'text',
            text: `🚨 Emergency stop execution failed for drone '${args?.droneId}': ${error instanceof Error ? error.message : String(error)}. Please manually verify drone safety and take appropriate action.`,
          },
        ],
        isError: true,
      };
    }
  }
}