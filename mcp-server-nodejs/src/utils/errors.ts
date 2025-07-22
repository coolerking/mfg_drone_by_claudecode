import { logger } from '@/utils/logger.js';
import { DroneError, NetworkError, ValidationError } from '@/types/index.js';

/**
 * エラーハンドリングユーティリティ
 */
export class ErrorHandler {
  /**
   * エラーをログに記録し、適切な形式に変換する
   */
  static handleError(error: unknown, context?: string): Error {
    const contextPrefix = context ? `[${context}] ` : '';

    if (error instanceof DroneError) {
      logger.error(`${contextPrefix}Drone Error: ${error.message}`, {
        code: error.code,
        statusCode: error.statusCode,
        stack: error.stack,
      });
      return error;
    }

    if (error instanceof NetworkError) {
      logger.error(`${contextPrefix}Network Error: ${error.message}`, {
        statusCode: error.statusCode,
        stack: error.stack,
      });
      return error;
    }

    if (error instanceof ValidationError) {
      logger.error(`${contextPrefix}Validation Error: ${error.message}`, {
        details: error.details,
        stack: error.stack,
      });
      return error;
    }

    if (error instanceof Error) {
      logger.error(`${contextPrefix}Error: ${error.message}`, {
        stack: error.stack,
      });
      return error;
    }

    // Unknown error type
    const unknownError = new Error(`${contextPrefix}Unknown error: ${String(error)}`);
    logger.error(unknownError.message, { originalError: error });
    return unknownError;
  }

  /**
   * 非同期処理のエラーを安全にハンドリングする
   */
  static async safeAsync<T>(
    fn: () => Promise<T>,
    context?: string
  ): Promise<T | Error> {
    try {
      return await fn();
    } catch (error) {
      return ErrorHandler.handleError(error, context);
    }
  }

  /**
   * 同期処理のエラーを安全にハンドリングする
   */
  static safe<T>(fn: () => T, context?: string): T | Error {
    try {
      return fn();
    } catch (error) {
      return ErrorHandler.handleError(error, context);
    }
  }

  /**
   * HTTPステータスコードからエラーを作成する
   */
  static fromHttpStatus(statusCode: number, message?: string): NetworkError {
    const defaultMessages: Record<number, string> = {
      400: 'Bad Request',
      401: 'Unauthorized',
      403: 'Forbidden',
      404: 'Not Found',
      500: 'Internal Server Error',
      502: 'Bad Gateway',
      503: 'Service Unavailable',
      504: 'Gateway Timeout',
    };

    const errorMessage = message || defaultMessages[statusCode] || 'HTTP Error';
    return new NetworkError(`HTTP ${statusCode}: ${errorMessage}`, statusCode);
  }

  /**
   * エラーがリトライ可能かどうかを判定する
   */
  static isRetryable(error: Error): boolean {
    if (error instanceof NetworkError) {
      // 5xx系エラーや特定の4xx系エラーはリトライ可能
      return (
        (error.statusCode !== undefined && error.statusCode >= 500) ||
        error.statusCode === 408 || // Request Timeout
        error.statusCode === 429    // Too Many Requests
      );
    }

    if (error instanceof DroneError) {
      // ドローン固有のリトライ可能エラー
      return ['TIMEOUT', 'CONNECTION_LOST', 'TEMPORARY_FAILURE'].includes(error.code);
    }

    return false;
  }
}