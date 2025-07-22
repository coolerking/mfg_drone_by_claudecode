import winston from 'winston';
import path from 'path';
import { config } from '@/config/index.js';

const { combine, timestamp, printf, colorize, errors, json, splat } = winston.format;

/**
 * 強化されたロギングシステム
 * - 構造化ログ形式
 * - パフォーマンス測定
 * - ログレベル動的変更
 * - ログローテーション
 * - メトリクス収集
 */

// カスタムメタデータ型
interface LogMeta {
  [key: string]: any;
  requestId?: string;
  userId?: string;
  operation?: string;
  duration?: number;
  error?: Error;
}

// カスタムログ形式
const consoleFormat = printf(({ level, message, timestamp, stack, requestId, operation, duration, ...meta }) => {
  const requestInfo = requestId ? `[${requestId}]` : '';
  const operationInfo = operation ? `{${operation}}` : '';
  const durationInfo = duration ? `(${duration}ms)` : '';
  const metaString = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : '';
  const stackString = stack ? `\n${stack}` : '';
  
  return `${timestamp} [${level}]${requestInfo}${operationInfo}${durationInfo}: ${message}${metaString}${stackString}`;
});

const fileFormat = combine(
  timestamp(),
  errors({ stack: true }),
  json(),
  printf(({ timestamp, level, message, ...meta }) => {
    return JSON.stringify({
      '@timestamp': timestamp,
      level,
      message,
      ...meta
    });
  })
);

// ログディレクトリの作成
function ensureLogDirectory(logPath: string): void {
  try {
    const { mkdirSync } = require('fs');
    const dir = path.dirname(logPath);
    mkdirSync(dir, { recursive: true });
  } catch (error) {
    console.warn(`ログディレクトリの作成に失敗しました: ${error}`);
  }
}

// ログファイルパス
const LOG_DIR = process.env.LOG_DIR || 'logs';
const errorLogPath = path.join(LOG_DIR, 'error.log');
const combinedLogPath = path.join(LOG_DIR, 'combined.log');
const accessLogPath = path.join(LOG_DIR, 'access.log');
const performanceLogPath = path.join(LOG_DIR, 'performance.log');

// ログディレクトリを確保
ensureLogDirectory(errorLogPath);

// ベースロガーの作成
export const logger = winston.createLogger({
  level: config.logLevel,
  defaultMeta: {
    service: 'mcp-drone-server',
    version: process.env.npm_package_version || '1.0.0',
    pid: process.pid,
  },
  format: combine(
    errors({ stack: true }),
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    splat()
  ),
  transports: [
    // コンソール出力
    new winston.transports.Console({
      format: combine(
        colorize({ all: true }),
        consoleFormat
      ),
    }),
    
    // エラーログファイル
    new winston.transports.File({
      filename: errorLogPath,
      level: 'error',
      format: fileFormat,
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 5,
      tailable: true,
    }),
    
    // 総合ログファイル
    new winston.transports.File({
      filename: combinedLogPath,
      format: fileFormat,
      maxsize: 50 * 1024 * 1024, // 50MB
      maxFiles: 10,
      tailable: true,
    }),
  ],
  
  // 未処理の例外やPromise拒否をキャッチ
  exceptionHandlers: [
    new winston.transports.File({ 
      filename: path.join(LOG_DIR, 'exceptions.log'),
      format: fileFormat,
    })
  ],
  rejectionHandlers: [
    new winston.transports.File({ 
      filename: path.join(LOG_DIR, 'rejections.log'),
      format: fileFormat,
    })
  ],
});

// アクセスログ用ロガー
export const accessLogger = winston.createLogger({
  level: 'info',
  format: combine(
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    fileFormat
  ),
  transports: [
    new winston.transports.File({
      filename: accessLogPath,
      maxsize: 20 * 1024 * 1024, // 20MB
      maxFiles: 5,
      tailable: true,
    }),
  ],
});

// パフォーマンスログ用ロガー
export const performanceLogger = winston.createLogger({
  level: 'info',
  format: combine(
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    fileFormat
  ),
  transports: [
    new winston.transports.File({
      filename: performanceLogPath,
      maxsize: 20 * 1024 * 1024, // 20MB
      maxFiles: 3,
      tailable: true,
    }),
  ],
});

/**
 * パフォーマンス測定用デコレータ/関数
 */
export function logPerformance(operation: string) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const startTime = Date.now();
      const requestId = this.requestId || generateRequestId();
      
      logger.debug(`${operation} 開始`, { operation, requestId, args: sanitizeArgs(args) });
      
      try {
        const result = await method.apply(this, args);
        const duration = Date.now() - startTime;
        
        logger.info(`${operation} 完了`, { operation, requestId, duration });
        performanceLogger.info('Operation completed', {
          operation,
          requestId,
          duration,
          success: true,
        });
        
        return result;
      } catch (error) {
        const duration = Date.now() - startTime;
        
        logger.error(`${operation} エラー`, { 
          operation, 
          requestId, 
          duration, 
          error: error instanceof Error ? error.message : error 
        });
        
        performanceLogger.error('Operation failed', {
          operation,
          requestId,
          duration,
          success: false,
          error: error instanceof Error ? error.message : error,
        });
        
        throw error;
      }
    };
  };
}

/**
 * タイマーオブジェクト
 */
export class Timer {
  private startTime: number;
  private operation: string;
  private requestId: string;

  constructor(operation: string, requestId?: string) {
    this.startTime = Date.now();
    this.operation = operation;
    this.requestId = requestId || generateRequestId();
    
    logger.debug(`Timer started: ${operation}`, { operation, requestId: this.requestId });
  }

  finish(message?: string): number {
    const duration = Date.now() - this.startTime;
    const logMessage = message || `${this.operation} completed`;
    
    logger.info(logMessage, { 
      operation: this.operation, 
      requestId: this.requestId, 
      duration 
    });
    
    performanceLogger.info('Timer finished', {
      operation: this.operation,
      requestId: this.requestId,
      duration,
      message: logMessage,
    });
    
    return duration;
  }

  finishWithError(error: Error, message?: string): number {
    const duration = Date.now() - this.startTime;
    const logMessage = message || `${this.operation} failed`;
    
    logger.error(logMessage, { 
      operation: this.operation, 
      requestId: this.requestId, 
      duration,
      error: error.message 
    });
    
    performanceLogger.error('Timer finished with error', {
      operation: this.operation,
      requestId: this.requestId,
      duration,
      message: logMessage,
      error: error.message,
    });
    
    return duration;
  }
}

/**
 * 構造化ロギング用のラッパー関数
 */
export const log = {
  debug: (message: string, meta?: LogMeta) => logger.debug(message, meta),
  info: (message: string, meta?: LogMeta) => logger.info(message, meta),
  warn: (message: string, meta?: LogMeta) => logger.warn(message, meta),
  error: (message: string, error?: Error | LogMeta, meta?: LogMeta) => {
    if (error instanceof Error) {
      logger.error(message, { error, ...meta });
    } else {
      logger.error(message, error);
    }
  },
  
  // 特定のコンテキスト用
  auth: (message: string, meta?: LogMeta) => logger.info(`[AUTH] ${message}`, meta),
  drone: (message: string, meta?: LogMeta) => logger.info(`[DRONE] ${message}`, meta),
  mcp: (message: string, meta?: LogMeta) => logger.info(`[MCP] ${message}`, meta),
  security: (message: string, meta?: LogMeta) => logger.warn(`[SECURITY] ${message}`, meta),
  
  // アクセスログ
  access: (message: string, meta?: LogMeta) => accessLogger.info(message, meta),
  
  // パフォーマンスログ
  performance: (message: string, meta?: LogMeta) => performanceLogger.info(message, meta),
};

/**
 * リクエストIDを生成
 */
function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 引数をサニタイズ（機密情報を除去）
 */
function sanitizeArgs(args: any[]): any[] {
  return args.map(arg => {
    if (typeof arg === 'object' && arg !== null) {
      return sanitizeObject(arg);
    }
    return arg;
  });
}

function sanitizeObject(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(sanitizeObject);
  }
  
  if (typeof obj === 'object' && obj !== null) {
    const sanitized: any = {};
    for (const [key, value] of Object.entries(obj)) {
      if (typeof key === 'string' && 
          (key.toLowerCase().includes('password') || 
           key.toLowerCase().includes('secret') || 
           key.toLowerCase().includes('token') ||
           key.toLowerCase().includes('key'))) {
        sanitized[key] = '***';
      } else if (typeof value === 'object') {
        sanitized[key] = sanitizeObject(value);
      } else {
        sanitized[key] = value;
      }
    }
    return sanitized;
  }
  
  return obj;
}

/**
 * ログレベルを動的に変更
 */
export function setLogLevel(level: string): void {
  logger.level = level;
  logger.info(`Log level changed to: ${level}`);
}

/**
 * ログファイルのクリーンアップ
 */
export function cleanupOldLogs(daysToKeep: number = 7): void {
  const fs = require('fs');
  const cutoffTime = Date.now() - (daysToKeep * 24 * 60 * 60 * 1000);
  
  try {
    const files = fs.readdirSync(LOG_DIR);
    for (const file of files) {
      const filePath = path.join(LOG_DIR, file);
      const stats = fs.statSync(filePath);
      
      if (stats.mtime.getTime() < cutoffTime) {
        fs.unlinkSync(filePath);
        logger.info(`Deleted old log file: ${file}`);
      }
    }
  } catch (error) {
    logger.error('Failed to cleanup old logs', { error });
  }
}

export default logger;