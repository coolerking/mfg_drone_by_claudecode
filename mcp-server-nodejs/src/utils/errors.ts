import { logger, log } from '@/utils/logger.js';
import { 
  BaseError,
  DroneError, 
  NetworkError, 
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  ConfigurationError,
  TimeoutError,
  RateLimitError,
  BusinessLogicError,
  ErrorContext,
  ErrorResponse,
  isRetryableError,
  isClientError,
  isServerError
} from '@/types/index.js';

/**
 * 強化されたエラーハンドリングユーティリティ
 * - 統一されたエラーログ記録
 * - エラー分類とルーティング
 * - リトライ戦略
 * - エラー回復機能
 * - メトリクス収集
 */

export interface RetryOptions {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  jitter: boolean;
}

export interface ErrorMetrics {
  errorType: string;
  errorCode: string;
  count: number;
  lastOccurrence: Date;
  isRetryable: boolean;
  averageRecoveryTime?: number;
}

export class ErrorHandler {
  private static errorMetrics = new Map<string, ErrorMetrics>();
  private static recoveryStrategies = new Map<string, (error: BaseError) => Promise<void>>();

  /**
   * エラーを包括的にハンドリング
   */
  static handleError(
    error: unknown, 
    context?: Partial<ErrorContext>
  ): BaseError {
    const handledError = this.normalizeError(error, context);
    
    // エラーをログに記録
    this.logError(handledError, context);
    
    // メトリクスを更新
    this.updateMetrics(handledError);
    
    // 回復戦略を試行
    this.attemptRecovery(handledError);
    
    return handledError;
  }

  /**
   * エラーを正規化してBaseErrorに変換
   */
  private static normalizeError(
    error: unknown, 
    context?: Partial<ErrorContext>
  ): BaseError {
    // 既にBaseErrorの場合はそのまま返す（コンテキストを追加）
    if (error instanceof BaseError) {
      if (context) {
        Object.assign(error.context, context);
      }
      return error;
    }

    // 通常のErrorの場合
    if (error instanceof Error) {
      return new BusinessLogicError(
        error.message,
        'UNKNOWN_ERROR',
        error.message,
        { originalError: error.constructor.name },
        context
      );
    }

    // その他の場合
    const message = error ? String(error) : 'Unknown error occurred';
    return new BusinessLogicError(
      message,
      'UNKNOWN_ERROR',
      '予期しないエラーが発生しました',
      { originalError: error },
      context
    );
  }

  /**
   * エラーをログに記録
   */
  private static logError(error: BaseError, context?: Partial<ErrorContext>): void {
    const logContext = {
      ...error.context,
      ...context,
      errorCode: error.code,
      statusCode: error.statusCode,
      retryable: error.retryable,
    };

    // ログレベルを決定
    if (error.statusCode >= 500) {
      log.error(error.message, error.toLogFormat());
    } else if (error.statusCode >= 400) {
      log.warn(error.message, logContext);
    } else {
      log.info(error.message, logContext);
    }
  }

  /**
   * エラーメトリクスを更新
   */
  private static updateMetrics(error: BaseError): void {
    const key = `${error.constructor.name}:${error.code}`;
    const existing = this.errorMetrics.get(key);
    
    if (existing) {
      existing.count++;
      existing.lastOccurrence = new Date();
    } else {
      this.errorMetrics.set(key, {
        errorType: error.constructor.name,
        errorCode: error.code,
        count: 1,
        lastOccurrence: new Date(),
        isRetryable: error.retryable,
      });
    }
  }

  /**
   * エラー回復を試行
   */
  private static async attemptRecovery(error: BaseError): Promise<void> {
    const strategy = this.recoveryStrategies.get(error.code);
    if (strategy) {
      try {
        const startTime = Date.now();
        await strategy(error);
        const recoveryTime = Date.now() - startTime;
        
        // 回復時間をメトリクスに記録
        const key = `${error.constructor.name}:${error.code}`;
        const metrics = this.errorMetrics.get(key);
        if (metrics) {
          metrics.averageRecoveryTime = metrics.averageRecoveryTime
            ? (metrics.averageRecoveryTime + recoveryTime) / 2
            : recoveryTime;
        }
        
        log.info(`Error recovery successful: ${error.code}`, { 
          recoveryTime, 
          errorCode: error.code 
        });
      } catch (recoveryError) {
        log.error(`Error recovery failed: ${error.code}`, { 
          recoveryError: recoveryError instanceof Error ? recoveryError.message : recoveryError 
        });
      }
    }
  }

  /**
   * 非同期処理のエラーを安全にハンドリング
   */
  static async safeAsync<T>(
    fn: () => Promise<T>,
    context?: Partial<ErrorContext>
  ): Promise<T | BaseError> {
    try {
      return await fn();
    } catch (error) {
      return this.handleError(error, context);
    }
  }

  /**
   * 同期処理のエラーを安全にハンドリング
   */
  static safe<T>(
    fn: () => T, 
    context?: Partial<ErrorContext>
  ): T | BaseError {
    try {
      return fn();
    } catch (error) {
      return this.handleError(error, context);
    }
  }

  /**
   * リトライ機能付きの非同期処理実行
   */
  static async withRetry<T>(
    fn: () => Promise<T>,
    options: Partial<RetryOptions> = {},
    context?: Partial<ErrorContext>
  ): Promise<T> {
    const retryOptions: RetryOptions = {
      maxAttempts: 3,
      baseDelay: 1000,
      maxDelay: 30000,
      backoffMultiplier: 2,
      jitter: true,
      ...options,
    };

    let lastError: BaseError | null = null;
    
    for (let attempt = 1; attempt <= retryOptions.maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = this.handleError(error, { 
          ...context, 
          metadata: { attempt, maxAttempts: retryOptions.maxAttempts } 
        });

        // 最後の試行でない場合、リトライ可能エラーなら再試行
        if (attempt < retryOptions.maxAttempts && isRetryableError(lastError)) {
          const delay = this.calculateDelay(attempt, retryOptions);
          log.warn(`Retrying in ${delay}ms (attempt ${attempt}/${retryOptions.maxAttempts})`, {
            errorCode: lastError.code,
            attempt,
            delay,
          });
          
          await this.sleep(delay);
          continue;
        }
        
        break;
      }
    }

    throw lastError;
  }

  /**
   * HTTPステータスコードから適切なエラーを作成
   */
  static fromHttpStatus(
    statusCode: number, 
    message?: string, 
    endpoint?: string,
    method?: string,
    context?: Partial<ErrorContext>
  ): BaseError {
    const defaultMessages: Record<number, string> = {
      400: 'Bad Request',
      401: 'Unauthorized', 
      403: 'Forbidden',
      404: 'Not Found',
      408: 'Request Timeout',
      409: 'Conflict',
      422: 'Unprocessable Entity',
      429: 'Too Many Requests',
      500: 'Internal Server Error',
      502: 'Bad Gateway',
      503: 'Service Unavailable',
      504: 'Gateway Timeout',
    };

    const errorMessage = message || defaultMessages[statusCode] || 'HTTP Error';
    
    // ステータスコードに応じて適切なエラータイプを選択
    switch (statusCode) {
      case 401:
        return new AuthenticationError(
          `HTTP ${statusCode}: ${errorMessage}`,
          undefined,
          method,
          context
        );
      case 403:
        return new AuthorizationError(
          `HTTP ${statusCode}: ${errorMessage}`,
          undefined,
          undefined,
          undefined,
          context
        );
      case 408:
      case 504:
        return new TimeoutError(
          `HTTP ${statusCode}: ${errorMessage}`,
          30000, // Default timeout
          undefined,
          endpoint,
          context
        );
      case 429:
        return new RateLimitError(
          `HTTP ${statusCode}: ${errorMessage}`,
          100, // Default limit
          60000, // Default window
          undefined,
          undefined,
          context
        );
      default:
        return new NetworkError(
          `HTTP ${statusCode}: ${errorMessage}`,
          statusCode,
          undefined,
          endpoint,
          method,
          context
        );
    }
  }

  /**
   * 回復戦略を登録
   */
  static registerRecoveryStrategy(
    errorCode: string, 
    strategy: (error: BaseError) => Promise<void>
  ): void {
    this.recoveryStrategies.set(errorCode, strategy);
    log.debug(`Recovery strategy registered for error code: ${errorCode}`);
  }

  /**
   * エラーメトリクスを取得
   */
  static getErrorMetrics(): Map<string, ErrorMetrics> {
    return new Map(this.errorMetrics);
  }

  /**
   * エラーメトリクスをクリア
   */
  static clearErrorMetrics(): void {
    this.errorMetrics.clear();
    log.info('Error metrics cleared');
  }

  /**
   * エラーを HTTP レスポンス形式に変換
   */
  static toHttpResponse(error: BaseError): ErrorResponse {
    return error.toJSON();
  }

  /**
   * エラーの重要度を判定
   */
  static getSeverity(error: BaseError): 'low' | 'medium' | 'high' | 'critical' {
    if (isServerError(error)) {
      return error.statusCode >= 500 ? 'critical' : 'high';
    }
    
    if (isClientError(error)) {
      return error.statusCode >= 400 && error.statusCode < 500 ? 'medium' : 'low';
    }
    
    return error.retryable ? 'medium' : 'high';
  }

  /**
   * エラーフィルタリング（機密情報の除去）
   */
  static sanitizeError(error: BaseError): BaseError {
    // 機密情報を含む可能性のあるフィールドをサニタイズ
    const sanitizedContext = { ...error.context };
    
    if (sanitizedContext.metadata) {
      sanitizedContext.metadata = this.sanitizeObject(sanitizedContext.metadata);
    }
    
    // 新しいエラーオブジェクトを作成（サニタイズされたコンテキスト付き）
    const ErrorClass = error.constructor as any;
    const sanitizedError = Object.create(ErrorClass.prototype);
    Object.assign(sanitizedError, error);
    sanitizedError.context = sanitizedContext;
    
    return sanitizedError;
  }

  /**
   * オブジェクトの機密情報をサニタイズ
   */
  private static sanitizeObject(obj: Record<string, any>): Record<string, any> {
    const sanitized: Record<string, any> = {};
    
    for (const [key, value] of Object.entries(obj)) {
      if (typeof key === 'string' && 
          (key.toLowerCase().includes('password') ||
           key.toLowerCase().includes('secret') ||
           key.toLowerCase().includes('token') ||
           key.toLowerCase().includes('key') ||
           key.toLowerCase().includes('auth'))) {
        sanitized[key] = '***';
      } else if (typeof value === 'object' && value !== null) {
        sanitized[key] = this.sanitizeObject(value);
      } else {
        sanitized[key] = value;
      }
    }
    
    return sanitized;
  }

  /**
   * リトライ遅延を計算
   */
  private static calculateDelay(attempt: number, options: RetryOptions): number {
    let delay = Math.min(
      options.baseDelay * Math.pow(options.backoffMultiplier, attempt - 1),
      options.maxDelay
    );
    
    if (options.jitter) {
      // ±25%のジッターを追加
      const jitterAmount = delay * 0.25;
      delay += (Math.random() * 2 - 1) * jitterAmount;
    }
    
    return Math.max(0, Math.floor(delay));
  }

  /**
   * 指定された時間だけ待機
   */
  private static sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// デフォルトの回復戦略を登録
ErrorHandler.registerRecoveryStrategy('NETWORK_ERROR', async (error) => {
  log.info('Attempting network recovery...', { errorCode: error.code });
  // ネットワーク接続の再確認など
});

ErrorHandler.registerRecoveryStrategy('TIMEOUT_ERROR', async (error) => {
  log.info('Attempting timeout recovery...', { errorCode: error.code });
  // タイムアウト値の調整など
});