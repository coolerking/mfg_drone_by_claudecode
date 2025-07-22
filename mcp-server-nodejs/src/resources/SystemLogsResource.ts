import { BaseResource, type MCPResourceResponse } from './BaseResource.js';
import { logger } from '@/utils/logger.js';

/**
 * システムログリソース  
 * システムのログとイベント情報を提供
 */
export class SystemLogsResource extends BaseResource {
  private logBuffer: Array<{
    timestamp: string;
    level: string;
    message: string;
    source: string;
    metadata?: Record<string, unknown>;
  }>;
  private maxLogSize: number;

  constructor(droneService: any) {
    super(droneService, 'SystemLogsResource', 'mcp://system-logs');
    this.logBuffer = [];
    this.maxLogSize = 1000; // 最大1000件のログを保持
    
    this.initializeLogCapture();
  }

  getDescription(): string {
    return 'System logs and events from the MCP drone server including command execution, errors, and system activities.';
  }

  getUri(): string {
    return `${this.baseUri}/logs`;
  }

  getMimeType(): string {
    return 'application/json';
  }

  async getContents(): Promise<MCPResourceResponse> {
    try {
      logger.debug('Retrieving system logs resource');

      // 最近のシステム状態を取得
      let systemHealth;
      try {
        const healthResult = await this.droneService.performHealthCheck();
        systemHealth = healthResult;
      } catch (error) {
        systemHealth = { status: 'unknown', timestamp: new Date().toISOString(), error: 'Health check failed' };
      }

      // ログデータを整理
      const recentLogs = this.logBuffer.slice(-100); // 最新100件
      
      const logsByLevel = {
        error: this.logBuffer.filter(log => log.level === 'error').slice(-20),
        warn: this.logBuffer.filter(log => log.level === 'warn').slice(-20),
        info: this.logBuffer.filter(log => log.level === 'info').slice(-30),
        debug: this.logBuffer.filter(log => log.level === 'debug').slice(-30),
      };

      const resourceData = {
        timestamp: new Date().toISOString(),
        summary: {
          totalLogs: this.logBuffer.length,
          recentLogCount: recentLogs.length,
          errorCount: logsByLevel.error.length,
          warningCount: logsByLevel.warn.length,
          systemHealth: systemHealth.status,
        },
        recentLogs: recentLogs,
        logsByLevel: logsByLevel,
        systemHealth: systemHealth,
        logSources: this.getLogSources(),
      };

      return this.createJsonResponse(resourceData);
    } catch (error) {
      logger.error('Error retrieving system logs resource:', error);
      return this.handleError(error);
    }
  }

  /**
   * ログキャプチャを初期化
   */
  private initializeLogCapture(): void {
    // ログエントリを追加するメソッド
    this.addLogEntry('info', 'System logs resource initialized', 'SystemLogsResource');
  }

  /**
   * ログエントリを追加
   */
  public addLogEntry(
    level: string,
    message: string,
    source: string,
    metadata?: Record<string, unknown>
  ): void {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      source,
      ...(metadata && { metadata }),
    };

    this.logBuffer.push(entry);

    // バッファサイズ制限
    if (this.logBuffer.length > this.maxLogSize) {
      this.logBuffer = this.logBuffer.slice(-this.maxLogSize);
    }
  }

  /**
   * ログソース一覧を取得
   */
  private getLogSources(): Array<{ source: string; count: number; lastActivity: string }> {
    const sourceCounts = new Map<string, { count: number; lastActivity: string }>();
    
    for (const log of this.logBuffer) {
      const existing = sourceCounts.get(log.source);
      if (existing) {
        existing.count++;
        if (log.timestamp > existing.lastActivity) {
          existing.lastActivity = log.timestamp;
        }
      } else {
        sourceCounts.set(log.source, {
          count: 1,
          lastActivity: log.timestamp,
        });
      }
    }

    return Array.from(sourceCounts.entries()).map(([source, data]) => ({
      source,
      count: data.count,
      lastActivity: data.lastActivity,
    }));
  }

  /**
   * ログをクリア
   */
  public clearLogs(): void {
    this.logBuffer = [];
    this.addLogEntry('info', 'System logs cleared', 'SystemLogsResource');
  }
}