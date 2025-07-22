import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

/**
 * 写真撮影ツール
 * 指定されたドローンで写真を撮影する
 */
export class TakePhotoTool extends BaseTool {
  constructor(droneService: any) {
    super(droneService, 'take_photo');
  }

  getDescription(): string {
    return 'Take a photo with the drone camera. The drone must be connected (does not need to be flying).';
  }

  getInputSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        droneId: {
          type: 'string',
          description: 'The ID of the drone to take photo with',
        },
        filename: {
          type: 'string',
          description: 'Custom filename for the photo (optional, will auto-generate if not provided)',
          pattern: '^[a-zA-Z0-9_-]+$',
        },
        quality: {
          type: 'string',
          enum: ['high', 'medium', 'low'],
          description: 'Photo quality setting (optional, default: high)',
          default: 'high',
        },
        format: {
          type: 'string',
          enum: ['jpg', 'png'],
          description: 'Photo format (optional, default: jpg)',
          default: 'jpg',
        },
        timestamp: {
          type: 'boolean',
          description: 'Whether to include timestamp in filename (optional, default: true)',
          default: true,
        },
        metadata: {
          type: 'object',
          description: 'Additional metadata to store with photo (optional)',
          properties: {
            location: { type: 'string' },
            description: { type: 'string' },
            tags: {
              type: 'array',
              items: { type: 'string' },
            },
          },
        },
      },
      required: ['droneId'],
    };
  }

  async execute(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    try {
      this.validateArgs(args, ['droneId']);
      const droneId = args!.droneId as string;
      
      logger.info(`Taking photo with drone: ${droneId}`, args);

      // ドローンの状態確認
      await this.validateAndGetDrone(droneId);

      // 撮影パラメータの準備
      const params = this.preparePhotoParams(args!);

      // コマンド実行
      const result = await this.droneService.executeCommand(droneId, 'take_photo', params);

      if (result.success) {
        const photoInfo = this.getPhotoDescription(params, result);
        return this.createSuccessResponse(
          `Photo taken successfully with drone '${droneId}'. ${photoInfo}${result.message ? ` ${result.message}` : ''}`
        );
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      return this.createErrorResponse(error);
    }
  }

  /**
   * 撮影パラメータを準備
   */
  private preparePhotoParams(args: Record<string, unknown>): Record<string, unknown> {
    const filename = args.filename as string;
    const quality = args.quality as string || 'high';
    const format = args.format as string || 'jpg';
    const timestamp = args.timestamp as boolean !== false; // default true
    const metadata = args.metadata as Record<string, unknown>;

    const params: Record<string, unknown> = {
      quality,
      format,
      timestamp,
    };

    // カスタムファイル名が指定されている場合
    if (filename) {
      params.filename = filename;
    }

    // メタデータが指定されている場合
    if (metadata) {
      params.metadata = metadata;
    }

    // タイムスタンプを含むファイル名を生成
    if (!filename && timestamp) {
      const now = new Date().toISOString().replace(/[:.]/g, '-');
      params.generatedFilename = `photo_${now}.${format}`;
    }

    return params;
  }

  /**
   * 撮影情報の説明を生成
   */
  private getPhotoDescription(params: Record<string, unknown>, result?: any): string {
    const parts: string[] = [];
    
    if (params.filename) {
      parts.push(`Filename: ${params.filename}.${params.format}`);
    } else if (params.generatedFilename) {
      parts.push(`Filename: ${params.generatedFilename}`);
    }
    
    parts.push(`Quality: ${params.quality}`);
    parts.push(`Format: ${params.format}`);

    if (params.metadata) {
      const metadata = params.metadata as Record<string, unknown>;
      if (metadata.location) {
        parts.push(`Location: ${metadata.location}`);
      }
      if (metadata.description) {
        parts.push(`Description: ${metadata.description}`);
      }
      if (metadata.tags && Array.isArray(metadata.tags)) {
        parts.push(`Tags: ${metadata.tags.join(', ')}`);
      }
    }

    // バックエンドから返されたファイルパス情報があれば追加
    if (result && result.data && result.data.filepath) {
      parts.push(`Saved to: ${result.data.filepath}`);
    }

    return parts.join(', ');
  }
}