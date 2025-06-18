import * as winston from 'winston';
import * as path from 'path';
import * as fs from 'fs';
import { ConfigManager } from './config';
import type { LogContext, PerformanceMetrics } from '../types/config';

export class Logger {
  private static instance: Logger;
  private winston: winston.Logger;
  private config: ReturnType<ConfigManager['getConfig']>;

  private constructor() {
    this.config = ConfigManager.getInstance().getConfig();
    this.winston = this.createLogger();
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private createLogger(): winston.Logger {
    const { logging } = this.config;

    // Ensure log directory exists
    if (logging.file.enabled) {
      const logDir = path.dirname(logging.file.filename);
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }
    }

    // Create formats
    const formats = [winston.format.timestamp()];

    if (logging.format === 'json') {
      formats.push(winston.format.json());
    } else {
      formats.push(
        winston.format.colorize(),
        winston.format.printf(({ timestamp, level, message, ...meta }) => {
          const metaStr = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : '';
          return `${timestamp} [${level}] ${message}${metaStr}`;
        })
      );
    }

    // Create transports
    const transports: winston.transport[] = [
      new winston.transports.Console({
        level: logging.level,
        format: winston.format.combine(...formats),
      }),
    ];

    if (logging.file.enabled) {
      transports.push(
        new winston.transports.File({
          filename: logging.file.filename,
          level: logging.level,
          format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
          maxsize: this.parseSize(logging.file.maxSize),
          maxFiles: logging.file.maxFiles,
          tailable: true,
        })
      );
    }

    return winston.createLogger({
      level: logging.level,
      format: winston.format.combine(...formats),
      transports,
      exitOnError: false,
    });
  }

  private parseSize(sizeStr: string): number {
    const match = sizeStr.match(/^(\d+)([kmg]?)$/i);
    if (!match) {
      return 10 * 1024 * 1024; // Default 10MB
    }

    const [, num, unit] = match;
    const bytes = parseInt(num, 10);

    switch (unit.toLowerCase()) {
      case 'k':
        return bytes * 1024;
      case 'm':
        return bytes * 1024 * 1024;
      case 'g':
        return bytes * 1024 * 1024 * 1024;
      default:
        return bytes;
    }
  }

  public debug(message: string, context?: LogContext): void {
    this.winston.debug(message, context);
  }

  public info(message: string, context?: LogContext): void {
    this.winston.info(message, context);
  }

  public warn(message: string, context?: LogContext): void {
    this.winston.warn(message, context);
  }

  public error(message: string, error?: Error, context?: LogContext): void {
    this.winston.error(message, {
      ...context,
      error: error?.message,
      stack: error?.stack,
    });
  }

  public logToolExecution(
    toolName: string,
    duration: number,
    success: boolean,
    error?: string,
    context?: LogContext
  ): void {
    const level = success ? 'info' : 'error';
    const message = `Tool execution: ${toolName}`;

    this.winston.log(level, message, {
      ...context,
      toolName,
      duration,
      success,
      error,
      performance: duration > this.config.performance.targetResponseTime ? 'slow' : 'normal',
    });
  }

  public logPerformanceMetrics(metrics: PerformanceMetrics): void {
    this.winston.info('Performance metrics', {
      timestamp: metrics.timestamp.toISOString(),
      toolName: metrics.toolName,
      duration: metrics.duration,
      success: metrics.success,
      error: metrics.error,
      benchmark: metrics.duration <= this.config.performance.targetResponseTime ? 'pass' : 'fail',
    });
  }

  public logAPICall(
    method: string,
    url: string,
    duration: number,
    status: number,
    error?: string,
    context?: LogContext
  ): void {
    const success = status >= 200 && status < 300;
    const level = success ? 'debug' : 'error';

    this.winston.log(level, `API Call: ${method} ${url}`, {
      ...context,
      method,
      url,
      duration,
      status,
      success,
      error,
    });
  }

  public logWebSocketEvent(
    event: string,
    data?: unknown,
    error?: string,
    context?: LogContext
  ): void {
    const level = error ? 'error' : 'debug';

    this.winston.log(level, `WebSocket Event: ${event}`, {
      ...context,
      event,
      data: this.config.debug ? data : undefined,
      error,
    });
  }

  public createChildLogger(defaultContext: LogContext): Logger {
    const childLogger = Object.create(this);
    childLogger.defaultContext = defaultContext;
    return childLogger;
  }

  private defaultContext?: LogContext;

  private mergeContext(context?: LogContext): LogContext | undefined {
    if (!this.defaultContext && !context) {
      return undefined;
    }
    return { ...this.defaultContext, ...context };
  }

  public setLevel(level: string): void {
    this.winston.level = level;
  }

  public getLevel(): string {
    return this.winston.level;
  }

  public flush(): Promise<void> {
    return new Promise(resolve => {
      const transports = this.winston.transports;
      let pending = transports.length;

      if (pending === 0) {
        resolve();
        return;
      }

      transports.forEach(transport => {
        if (transport instanceof winston.transports.File) {
          transport.on('finish', () => {
            pending--;
            if (pending === 0) {
              resolve();
            }
          });
          transport.end();
        } else {
          pending--;
          if (pending === 0) {
            resolve();
          }
        }
      });
    });
  }
}