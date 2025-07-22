import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

/**
 * ドローン移動ツール
 * 指定されたドローンを相対座標で移動させる
 */
export class MoveDroneTool extends BaseTool {
  constructor(droneService: any) {
    super(droneService, 'move_drone');
  }

  getDescription(): string {
    return 'Move a drone in 3D space using relative coordinates. The drone must be flying to execute movement commands.';
  }

  getInputSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        droneId: {
          type: 'string',
          description: 'The ID of the drone to move',
        },
        direction: {
          type: 'string',
          enum: ['forward', 'backward', 'left', 'right', 'up', 'down'],
          description: 'Direction to move the drone',
        },
        distance: {
          type: 'number',
          description: 'Distance to move in meters',
          minimum: 0.2,
          maximum: 5.0,
        },
        x: {
          type: 'number',
          description: 'X-axis movement in meters (optional, for precise control)',
          minimum: -5.0,
          maximum: 5.0,
        },
        y: {
          type: 'number',
          description: 'Y-axis movement in meters (optional, for precise control)',
          minimum: -5.0,
          maximum: 5.0,
        },
        z: {
          type: 'number',
          description: 'Z-axis movement in meters (optional, for precise control)',
          minimum: -5.0,
          maximum: 5.0,
        },
        speed: {
          type: 'number',
          description: 'Movement speed in m/s (optional, default: 1.0)',
          minimum: 0.1,
          maximum: 3.0,
          default: 1.0,
        },
      },
      required: ['droneId'],
      oneOf: [
        {
          required: ['direction', 'distance'],
        },
        {
          anyOf: [
            { required: ['x'] },
            { required: ['y'] },
            { required: ['z'] },
          ],
        },
      ],
    };
  }

  async execute(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    try {
      this.validateArgs(args, ['droneId']);
      const droneId = args!.droneId as string;
      
      logger.info(`Attempting to move drone: ${droneId}`, args);

      // ドローンの状態確認
      await this.validateAndGetDrone(droneId);

      // 飛行中かチェック
      const statuses = await this.droneService.getDroneStatus(droneId);
      const drone = statuses.find(d => d.id === droneId);
      
      if (drone && drone.status !== 'flying') {
        throw new Error(`Drone '${droneId}' must be flying to move (current status: ${drone.status})`);
      }

      // 移動パラメータの準備
      const params = this.prepareMovementParams(args!);

      // コマンド実行
      const result = await this.droneService.executeCommand(droneId, 'move', params);

      if (result.success) {
        const movementDesc = this.getMovementDescription(params);
        return this.createSuccessResponse(
          `Drone '${droneId}' movement initiated: ${movementDesc}. ${result.message}`
        );
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      return this.createErrorResponse(error);
    }
  }

  /**
   * 移動パラメータを準備
   */
  private prepareMovementParams(args: Record<string, unknown>): Record<string, unknown> {
    const direction = args.direction as string;
    const distance = args.distance as number;
    const x = args.x as number;
    const y = args.y as number;
    const z = args.z as number;
    const speed = args.speed as number || 1.0;

    const params: Record<string, unknown> = { speed };

    // 方向と距離が指定されている場合
    if (direction && distance) {
      params.direction = direction;
      params.distance = distance;
      
      // 方向を座標に変換
      switch (direction) {
        case 'forward':
          params.y = distance;
          break;
        case 'backward':
          params.y = -distance;
          break;
        case 'right':
          params.x = distance;
          break;
        case 'left':
          params.x = -distance;
          break;
        case 'up':
          params.z = distance;
          break;
        case 'down':
          params.z = -distance;
          break;
      }
    }

    // 直接座標が指定されている場合
    if (x !== undefined) params.x = x;
    if (y !== undefined) params.y = y;
    if (z !== undefined) params.z = z;

    // 少なくとも一つの移動軸が必要
    if (!params.x && !params.y && !params.z) {
      throw new Error('At least one movement axis (x, y, z) or direction with distance must be specified');
    }

    return params;
  }

  /**
   * 移動内容の説明を生成
   */
  private getMovementDescription(params: Record<string, unknown>): string {
    const parts: string[] = [];
    
    if (params.direction && params.distance) {
      parts.push(`${params.direction} ${params.distance}m`);
    } else {
      if (params.x) parts.push(`X: ${params.x}m`);
      if (params.y) parts.push(`Y: ${params.y}m`);
      if (params.z) parts.push(`Z: ${params.z}m`);
    }
    
    if (params.speed) {
      parts.push(`at ${params.speed}m/s`);
    }

    return parts.join(', ');
  }
}