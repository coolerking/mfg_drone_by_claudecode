import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

/**
 * ドローン回転ツール
 * 指定されたドローンを回転させる
 */
export class RotateDroneTool extends BaseTool {
  constructor(droneService: any) {
    super(droneService, 'rotate_drone');
  }

  getDescription(): string {
    return 'Rotate a drone around its vertical axis (yaw). The drone must be flying to execute rotation commands.';
  }

  getInputSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        droneId: {
          type: 'string',
          description: 'The ID of the drone to rotate',
        },
        direction: {
          type: 'string',
          enum: ['clockwise', 'counterclockwise', 'cw', 'ccw'],
          description: 'Direction of rotation (clockwise or counterclockwise)',
        },
        angle: {
          type: 'number',
          description: 'Rotation angle in degrees',
          minimum: 10,
          maximum: 360,
        },
        speed: {
          type: 'number',
          description: 'Rotation speed in degrees per second (optional, default: 30)',
          minimum: 10,
          maximum: 100,
          default: 30,
        },
        absoluteHeading: {
          type: 'number',
          description: 'Target absolute heading in degrees (0-359, alternative to direction+angle)',
          minimum: 0,
          maximum: 359,
        },
      },
      required: ['droneId'],
      oneOf: [
        {
          required: ['direction', 'angle'],
        },
        {
          required: ['absoluteHeading'],
        },
      ],
    };
  }

  async execute(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    try {
      this.validateArgs(args, ['droneId']);
      const droneId = args!.droneId as string;
      
      logger.info(`Attempting to rotate drone: ${droneId}`, args);

      // ドローンの状態確認
      await this.validateAndGetDrone(droneId);

      // 飛行中かチェック
      const statuses = await this.droneService.getDroneStatus(droneId);
      const drone = statuses.find(d => d.id === droneId);
      
      if (drone && drone.status !== 'flying') {
        throw new Error(`Drone '${droneId}' must be flying to rotate (current status: ${drone.status})`);
      }

      // 回転パラメータの準備
      const params = this.prepareRotationParams(args!);

      // コマンド実行
      const result = await this.droneService.executeCommand(droneId, 'rotate', params);

      if (result.success) {
        const rotationDesc = this.getRotationDescription(params);
        return this.createSuccessResponse(
          `Drone '${droneId}' rotation initiated: ${rotationDesc}. ${result.message}`
        );
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      return this.createErrorResponse(error);
    }
  }

  /**
   * 回転パラメータを準備
   */
  private prepareRotationParams(args: Record<string, unknown>): Record<string, unknown> {
    const direction = args.direction as string;
    const angle = args.angle as number;
    const speed = args.speed as number || 30;
    const absoluteHeading = args.absoluteHeading as number;

    const params: Record<string, unknown> = { speed };

    // 絶対方位が指定されている場合
    if (absoluteHeading !== undefined) {
      params.absoluteHeading = absoluteHeading;
      params.mode = 'absolute';
    } 
    // 相対回転が指定されている場合
    else if (direction && angle) {
      params.direction = direction;
      params.angle = angle;
      params.mode = 'relative';

      // 方向を正規化
      if (direction === 'cw') {
        params.direction = 'clockwise';
      } else if (direction === 'ccw') {
        params.direction = 'counterclockwise';
      }

      // 時計回りの場合は正の角度、反時計回りの場合は負の角度
      if (params.direction === 'counterclockwise') {
        params.rotationAngle = -Math.abs(angle);
      } else {
        params.rotationAngle = Math.abs(angle);
      }
    } else {
      throw new Error('Either (direction and angle) or absoluteHeading must be specified');
    }

    return params;
  }

  /**
   * 回転内容の説明を生成
   */
  private getRotationDescription(params: Record<string, unknown>): string {
    if (params.mode === 'absolute') {
      return `turn to heading ${params.absoluteHeading}° at ${params.speed}°/s`;
    } else {
      const direction = params.direction === 'clockwise' ? 'clockwise' : 'counterclockwise';
      return `rotate ${direction} ${params.angle}° at ${params.speed}°/s`;
    }
  }
}