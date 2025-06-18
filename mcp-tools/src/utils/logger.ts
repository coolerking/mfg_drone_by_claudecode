import { writeFileSync, appendFileSync, existsSync, statSync, unlinkSync } from 'fs';
import { ServerConfig } from '../types/config.js';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: unknown;
  component?: string;
}

export class Logger {
  private config: ServerConfig;
  private logFile?: string;

  constructor(config: ServerConfig) {
    this.config = config;
    this.logFile = config.logFile;
  }

  /**
   * Log debug message
   */
  debug(message: string, data?: unknown, component?: string): void {
    if (this.config.debug) {
      this.log('debug', message, data, component);
    }
  }

  /**
   * Log info message
   */
  info(message: string, data?: unknown, component?: string): void {
    this.log('info', message, data, component);
  }

  /**
   * Log warning message
   */
  warn(message: string, data?: unknown, component?: string): void {
    this.log('warn', message, data, component);
  }

  /**
   * Log error message
   */
  error(message: string, error?: unknown, component?: string): void {
    const errorData = this.formatError(error);
    this.log('error', message, errorData, component);
  }

  /**
   * Core logging method
   */
  private log(level: LogLevel, message: string, data?: unknown, component?: string): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      component,
    };

    // Console output
    this.logToConsole(entry);

    // File output
    if (this.logFile) {
      this.logToFile(entry);
    }
  }

  /**
   * Log to console with colors
   */
  private logToConsole(entry: LogEntry): void {
    const colors = {
      debug: '\x1b[36m', // Cyan
      info: '\x1b[32m',  // Green
      warn: '\x1b[33m',  // Yellow
      error: '\x1b[31m', // Red
    };
    const reset = '\x1b[0m';

    const color = colors[entry.level];
    const prefix = entry.component ? `[${entry.component}] ` : '';
    const dataStr = entry.data ? ` ${JSON.stringify(entry.data)}` : '';

    const output = `${color}${entry.timestamp} [${entry.level.toUpperCase()}] ${prefix}${entry.message}${dataStr}${reset}`;

    if (entry.level === 'error') {
      console.error(output);
    } else if (entry.level === 'warn') {
      console.warn(output);
    } else {
      console.log(output);
    }
  }

  /**
   * Log to file as JSON
   */
  private logToFile(entry: LogEntry): void {
    if (!this.logFile) return;

    try {
      // Check file size and rotate if needed
      this.rotateLogFile();

      const logLine = JSON.stringify(entry) + '\n';
      appendFileSync(this.logFile, logLine, 'utf-8');
    } catch (error) {
      console.error('Failed to write to log file:', error);
    }
  }

  /**
   * Rotate log file if it exceeds max size
   */
  private rotateLogFile(): void {
    if (!this.logFile || !existsSync(this.logFile)) return;

    const stats = statSync(this.logFile);
    if (stats.size >= this.config.maxLogSize) {
      const backupFile = `${this.logFile}.${Date.now()}`;
      try {
        // Move current log to backup
        const content = require('fs').readFileSync(this.logFile);
        writeFileSync(backupFile, content);
        
        // Clear current log file
        writeFileSync(this.logFile, '', 'utf-8');
        
        this.info(`Log file rotated. Backup created: ${backupFile}`, undefined, 'Logger');
      } catch (error) {
        console.error('Failed to rotate log file:', error);
      }
    }
  }

  /**
   * Format error object for logging
   */
  private formatError(error: unknown): unknown {
    if (error instanceof Error) {
      return {
        name: error.name,
        message: error.message,
        stack: error.stack,
      };
    }
    return error;
  }

  /**
   * Create component-specific logger
   */
  createComponentLogger(component: string): ComponentLogger {
    return new ComponentLogger(this, component);
  }
}

/**
 * Component-specific logger that automatically adds component name
 */
export class ComponentLogger {
  constructor(private logger: Logger, private component: string) {}

  debug(message: string, data?: unknown): void {
    this.logger.debug(message, data, this.component);
  }

  info(message: string, data?: unknown): void {
    this.logger.info(message, data, this.component);
  }

  warn(message: string, data?: unknown): void {
    this.logger.warn(message, data, this.component);
  }

  error(message: string, error?: unknown): void {
    this.logger.error(message, error, this.component);
  }
}