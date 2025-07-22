import { DroneService } from '@/services/DroneService.js';
import { logger } from '@/utils/logger.js';
import { ErrorHandler } from '@/utils/errors.js';
import { type MCPToolResponse } from '@/types/index.js';

/**
 * MCP ツールの基底クラス
 */
export abstract class BaseTool {
  protected droneService: DroneService;
  protected toolName: string;

  constructor(droneService: DroneService, toolName: string) {
    this.droneService = droneService;
    this.toolName = toolName;
  }

  /**
   * ツールの説明を取得
   */
  abstract getDescription(): string;

  /**
   * ツールの入力スキーマを取得
   */
  abstract getInputSchema(): Record<string, unknown>;

  /**
   * ツールを実行
   */
  abstract execute(args?: Record<string, unknown>): Promise<MCPToolResponse>;

  /**
   * エラーレスポンスを作成
   */
  protected createErrorResponse(error: unknown): MCPToolResponse {
    const handledError = ErrorHandler.handleError(error, `${this.toolName}.execute`);
    
    return {
      content: [
        {
          type: 'text',
          text: `Error in ${this.toolName}: ${handledError.message}`,
        },
      ],
      isError: true,
    };
  }

  /**
   * 成功レスポンスを作成
   */
  protected createSuccessResponse(message: string): MCPToolResponse {
    return {
      content: [
        {
          type: 'text',
          text: message,
        },
      ],
    };
  }

  /**
   * 引数を検証
   */
  protected validateArgs(args: Record<string, unknown> | undefined, requiredFields: string[]): void {
    if (!args) {
      throw new Error(`Missing required arguments: ${requiredFields.join(', ')}`);
    }

    for (const field of requiredFields) {
      if (args[field] === undefined || args[field] === null) {
        throw new Error(`Missing required argument: ${field}`);
      }
    }
  }

  /**
   * ドローンIDを検証・取得
   */
  protected async validateAndGetDrone(droneId: string): Promise<void> {
    if (!droneId || typeof droneId !== 'string') {
      throw new Error('Invalid drone ID provided');
    }

    // ドローンの存在確認
    const statuses = await this.droneService.getDroneStatus(droneId);
    const drone = statuses.find(d => d.id === droneId);
    
    if (!drone) {
      throw new Error(`Drone with ID '${droneId}' not found`);
    }

    if (drone.status === 'error') {
      throw new Error(`Drone '${droneId}' is in error state and cannot accept commands`);
    }

    if (drone.status === 'disconnected') {
      throw new Error(`Drone '${droneId}' is disconnected and cannot accept commands`);
    }
  }
}