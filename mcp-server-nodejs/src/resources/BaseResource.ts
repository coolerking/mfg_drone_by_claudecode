import { DroneService } from '@/services/DroneService.js';
import { logger } from '@/utils/logger.js';
import { ErrorHandler } from '@/utils/errors.js';

/**
 * MCPリソースのレスポンス型
 */
export interface MCPResourceResponse {
  contents: Array<{
    uri: string;
    mimeType: string;
    text?: string;
    blob?: string;
  }>;
}

/**
 * MCP リソースの基底クラス
 */
export abstract class BaseResource {
  protected droneService: DroneService;
  protected resourceName: string;
  protected baseUri: string;

  constructor(droneService: DroneService, resourceName: string, baseUri: string) {
    this.droneService = droneService;
    this.resourceName = resourceName;
    this.baseUri = baseUri;
  }

  /**
   * リソースの説明を取得
   */
  abstract getDescription(): string;

  /**
   * リソースのURIを取得
   */
  abstract getUri(): string;

  /**
   * リソースのMIMEタイプを取得
   */
  abstract getMimeType(): string;

  /**
   * リソースの内容を取得
   */
  abstract getContents(): Promise<MCPResourceResponse>;

  /**
   * エラー処理
   */
  protected handleError(error: unknown): MCPResourceResponse {
    const handledError = ErrorHandler.handleError(error, { operation: `${this.resourceName}.getContents` });
    
    return {
      contents: [
        {
          uri: this.getUri(),
          mimeType: 'text/plain',
          text: `Error retrieving ${this.resourceName}: ${handledError.message}`,
        },
      ],
    };
  }

  /**
   * JSON形式でレスポンスを作成
   */
  protected createJsonResponse(data: unknown): MCPResourceResponse {
    return {
      contents: [
        {
          uri: this.getUri(),
          mimeType: 'application/json',
          text: JSON.stringify(data, null, 2),
        },
      ],
    };
  }

  /**
   * テキスト形式でレスポンスを作成
   */
  protected createTextResponse(text: string): MCPResourceResponse {
    return {
      contents: [
        {
          uri: this.getUri(),
          mimeType: 'text/plain',
          text,
        },
      ],
    };
  }

  /**
   * HTML形式でレスポンスを作成
   */
  protected createHtmlResponse(html: string): MCPResourceResponse {
    return {
      contents: [
        {
          uri: this.getUri(),
          mimeType: 'text/html',
          text: html,
        },
      ],
    };
  }
}