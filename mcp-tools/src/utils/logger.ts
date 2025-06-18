/**
 * Logging utility with structured logging support
 * Provides consistent logging across the MCP server
 */

import { writeFile, appendFile } from 'fs/promises';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  metadata?: Record<string, unknown>;
  service: string;
}

class Logger {
  private logLevel: LogLevel = 'info';
  private structured = true;
  private logFile?: string;
  private readonly service = 'mcp-drone-server';

  /**
   * Set the logging configuration
   */
  configure(level: LogLevel, structured = true, logFile?: string): void {
    this.logLevel = level;
    this.structured = structured;
    this.logFile = logFile;
  }

  /**
   * Log a debug message
   */
  debug(message: string, metadata?: Record<string, unknown>): void {
    this.log('debug', message, metadata);
  }

  /**
   * Log an info message
   */
  info(message: string, metadata?: Record<string, unknown>): void {
    this.log('info', message, metadata);
  }

  /**
   * Log a warning message
   */
  warn(message: string, metadata?: Record<string, unknown>): void {
    this.log('warn', message, metadata);
  }

  /**
   * Log an error message
   */
  error(message: string, error?: unknown, metadata?: Record<string, unknown>): void {
    const errorMetadata = { ...metadata };
    
    if (error instanceof Error) {
      errorMetadata.error = {
        name: error.name,
        message: error.message,
        stack: error.stack,
      };
    } else if (error !== undefined) {
      errorMetadata.error = error;
    }
    
    this.log('error', message, errorMetadata);
  }

  /**
   * Internal logging method
   */
  private log(level: LogLevel, message: string, metadata?: Record<string, unknown>): void {
    if (!this.shouldLog(level)) {
      return;
    }

    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      metadata,
      service: this.service,
    };

    // Console output
    this.outputToConsole(logEntry);

    // File output (if configured)
    if (this.logFile) {
      this.outputToFile(logEntry).catch(fileError => {
        console.error('Failed to write to log file:', fileError);
      });
    }
  }

  /**
   * Check if the message should be logged based on current log level
   */
  private shouldLog(level: LogLevel): boolean {
    const levels: Record<LogLevel, number> = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3,
    };

    return levels[level] >= levels[this.logLevel];
  }

  /**
   * Output log entry to console
   */
  private outputToConsole(entry: LogEntry): void {
    if (this.structured) {
      // Structured JSON logging
      const output = JSON.stringify(entry);
      
      switch (entry.level) {
        case 'debug':
          console.debug(output);
          break;
        case 'info':
          console.info(output);
          break;
        case 'warn':
          console.warn(output);
          break;
        case 'error':
          console.error(output);
          break;
      }
    } else {
      // Human-readable logging
      const timestamp = entry.timestamp;
      const level = entry.level.toUpperCase().padEnd(5);
      const message = entry.message;
      const metadata = entry.metadata ? ` ${JSON.stringify(entry.metadata)}` : '';
      
      const output = `${timestamp} [${level}] ${message}${metadata}`;
      
      switch (entry.level) {
        case 'debug':
          console.debug(output);
          break;
        case 'info':
          console.info(output);
          break;
        case 'warn':
          console.warn(output);
          break;
        case 'error':
          console.error(output);
          break;
      }
    }
  }

  /**
   * Output log entry to file
   */
  private async outputToFile(entry: LogEntry): Promise<void> {
    if (!this.logFile) {
      return;
    }

    const logLine = JSON.stringify(entry) + '\n';
    
    try {
      await appendFile(this.logFile, logLine, 'utf-8');
    } catch (error) {
      // If append fails, try to create the file
      if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
        await writeFile(this.logFile, logLine, 'utf-8');
      } else {
        throw error;
      }
    }
  }
}

// Export singleton logger instance
export const logger = new Logger();