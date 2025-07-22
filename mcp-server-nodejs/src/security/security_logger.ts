import winston from 'winston';
import { logger } from '@/utils/logger.js';
import { config } from '@/config/index.js';
import { promises as fs } from 'fs';
import { dirname } from 'path';

/**
 * セキュリティイベントタイプ
 */
export enum SecurityEventType {
  AUTH_SUCCESS = 'auth_success',
  AUTH_FAILURE = 'auth_failure',
  AUTH_LOCKOUT = 'auth_lockout',
  API_KEY_CREATED = 'api_key_created',
  API_KEY_USED = 'api_key_used',
  API_KEY_REVOKED = 'api_key_revoked',
  PERMISSION_DENIED = 'permission_denied',
  RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded',
  SUSPICIOUS_ACTIVITY = 'suspicious_activity',
  SECURITY_CONFIG_CHANGED = 'security_config_changed',
  DATA_ACCESS = 'data_access',
  SYSTEM_ACCESS = 'system_access',
}

/**
 * セキュリティログエントリ
 */
export interface SecurityLogEntry {
  timestamp: Date;
  eventType: SecurityEventType;
  userId?: string;
  username?: string;
  ipAddress?: string;
  userAgent?: string;
  resourceAccessed?: string;
  action?: string;
  success: boolean;
  details?: Record<string, unknown>;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

/**
 * セキュリティ監査ログ
 */
export interface SecurityAuditEntry {
  timestamp: Date;
  userId: string;
  username: string;
  action: string;
  resource: string;
  oldValue?: unknown;
  newValue?: unknown;
  ipAddress?: string;
  userAgent?: string;
}

/**
 * セキュリティメトリクス
 */
export interface SecurityMetrics {
  totalEvents: number;
  authSuccessCount: number;
  authFailureCount: number;
  lockoutCount: number;
  rateLimitViolations: number;
  suspiciousActivities: number;
  highRiskEvents: number;
  criticalRiskEvents: number;
  uniqueUsers: number;
  timeRange: {
    start: Date;
    end: Date;
  };
}

/**
 * セキュリティロガー
 * セキュリティイベントの詳細なログ記録と監査証跡の管理
 */
export class SecurityLogger {
  private securityLogger!: winston.Logger;
  private auditLogger!: winston.Logger;
  private logEntries: SecurityLogEntry[] = [];
  private auditEntries: SecurityAuditEntry[] = [];
  private readonly maxLogEntries: number = 10000;
  private readonly securityLogPath: string = 'logs/security.log';
  private readonly auditLogPath: string = 'logs/audit.log';

  constructor() {
    this.initializeLoggers();
    this.ensureLogDirectories();
  }

  /**
   * セキュリティ専用ロガーの初期化
   */
  private initializeLoggers(): void {
    const logFormat = winston.format.combine(
      winston.format.timestamp(),
      winston.format.json(),
      winston.format.printf(({ timestamp, level, message, ...meta }) => {
        return JSON.stringify({
          timestamp,
          level,
          message,
          ...meta,
        });
      })
    );

    // セキュリティイベントログ
    this.securityLogger = winston.createLogger({
      level: 'info',
      format: logFormat,
      transports: [
        new winston.transports.File({
          filename: this.securityLogPath,
          maxsize: 10 * 1024 * 1024, // 10MB
          maxFiles: 10,
          tailable: true,
        }),
        // 本番環境では外部SIEMシステムへの送信も検討
      ],
    });

    // 監査ログ
    this.auditLogger = winston.createLogger({
      level: 'info',
      format: logFormat,
      transports: [
        new winston.transports.File({
          filename: this.auditLogPath,
          maxsize: 10 * 1024 * 1024, // 10MB
          maxFiles: 20,
          tailable: true,
        }),
      ],
    });
  }

  /**
   * ログディレクトリの作成
   */
  private async ensureLogDirectories(): Promise<void> {
    try {
      await fs.mkdir(dirname(this.securityLogPath), { recursive: true });
      await fs.mkdir(dirname(this.auditLogPath), { recursive: true });
    } catch (error) {
      logger.error('Failed to create log directories', { error });
    }
  }

  /**
   * セキュリティイベントのログ記録
   */
  logSecurityEvent(
    eventType: SecurityEventType,
    success: boolean,
    context: {
      userId?: string;
      username?: string;
      ipAddress?: string;
      userAgent?: string;
      resourceAccessed?: string;
      action?: string;
      details?: Record<string, unknown>;
    } = {}
  ): void {
    const riskLevel = this.calculateRiskLevel(eventType, success, context);
    
    const entry: SecurityLogEntry = {
      timestamp: new Date(),
      eventType,
      success,
      riskLevel,
      ...context,
    };

    // メモリ内キャッシュに追加
    this.logEntries.push(entry);
    if (this.logEntries.length > this.maxLogEntries) {
      this.logEntries = this.logEntries.slice(-this.maxLogEntries);
    }

    // ファイルログに記録
    this.securityLogger.info('Security event', entry);

    // 高リスクイベントは即座にメインログにも記録
    if (riskLevel === 'high' || riskLevel === 'critical') {
      logger.warn('High-risk security event detected', entry);
    }

    // リアルタイム監視のためのイベント発行（実際の実装ではWebSocketや外部システムに通知）
    this.emitSecurityAlert(entry);
  }

  /**
   * 監査ログの記録
   */
  logAuditEvent(
    userId: string,
    username: string,
    action: string,
    resource: string,
    context: {
      oldValue?: unknown;
      newValue?: unknown;
      ipAddress?: string;
      userAgent?: string;
    } = {}
  ): void {
    const entry: SecurityAuditEntry = {
      timestamp: new Date(),
      userId,
      username,
      action,
      resource,
      ...context,
    };

    // メモリ内キャッシュに追加
    this.auditEntries.push(entry);
    if (this.auditEntries.length > this.maxLogEntries) {
      this.auditEntries = this.auditEntries.slice(-this.maxLogEntries);
    }

    // ファイルログに記録
    this.auditLogger.info('Audit event', entry);
  }

  /**
   * リスクレベルの計算
   */
  private calculateRiskLevel(
    eventType: SecurityEventType,
    success: boolean,
    context: Record<string, unknown>
  ): 'low' | 'medium' | 'high' | 'critical' {
    // クリティカルレベル
    if (eventType === SecurityEventType.AUTH_LOCKOUT || 
        eventType === SecurityEventType.SUSPICIOUS_ACTIVITY ||
        eventType === SecurityEventType.SECURITY_CONFIG_CHANGED) {
      return 'critical';
    }

    // ハイレベル
    if (!success && (
        eventType === SecurityEventType.AUTH_FAILURE ||
        eventType === SecurityEventType.PERMISSION_DENIED ||
        eventType === SecurityEventType.RATE_LIMIT_EXCEEDED
    )) {
      return 'high';
    }

    // 複数回の失敗は高リスク
    if (!success && context.details && 
        typeof (context.details as any).failureCount === 'number' && 
        (context.details as any).failureCount >= 3) {
      return 'high';
    }

    // ミディアムレベル
    if (eventType === SecurityEventType.API_KEY_CREATED ||
        eventType === SecurityEventType.API_KEY_REVOKED ||
        eventType === SecurityEventType.SYSTEM_ACCESS) {
      return 'medium';
    }

    // デフォルトは低リスク
    return 'low';
  }

  /**
   * セキュリティアラートの発行
   */
  private emitSecurityAlert(entry: SecurityLogEntry): void {
    if (entry.riskLevel === 'critical' || entry.riskLevel === 'high') {
      // 実際の実装では、Slack、メール、WebSocketなどで通知
      logger.error(`SECURITY ALERT: ${entry.eventType}`, {
        riskLevel: entry.riskLevel,
        userId: entry.userId,
        username: entry.username,
        ipAddress: entry.ipAddress,
        details: entry.details,
      });
    }
  }

  /**
   * セキュリティメトリクスの取得
   */
  getSecurityMetrics(timeRange?: { start: Date; end: Date }): SecurityMetrics {
    let filteredEntries = this.logEntries;
    
    if (timeRange) {
      filteredEntries = this.logEntries.filter(entry => 
        entry.timestamp >= timeRange.start && entry.timestamp <= timeRange.end
      );
    }

    const uniqueUsers = new Set(
      filteredEntries.filter(entry => entry.userId).map(entry => entry.userId)
    ).size;

    return {
      totalEvents: filteredEntries.length,
      authSuccessCount: filteredEntries.filter(e => 
        e.eventType === SecurityEventType.AUTH_SUCCESS
      ).length,
      authFailureCount: filteredEntries.filter(e => 
        e.eventType === SecurityEventType.AUTH_FAILURE
      ).length,
      lockoutCount: filteredEntries.filter(e => 
        e.eventType === SecurityEventType.AUTH_LOCKOUT
      ).length,
      rateLimitViolations: filteredEntries.filter(e => 
        e.eventType === SecurityEventType.RATE_LIMIT_EXCEEDED
      ).length,
      suspiciousActivities: filteredEntries.filter(e => 
        e.eventType === SecurityEventType.SUSPICIOUS_ACTIVITY
      ).length,
      highRiskEvents: filteredEntries.filter(e => 
        e.riskLevel === 'high'
      ).length,
      criticalRiskEvents: filteredEntries.filter(e => 
        e.riskLevel === 'critical'
      ).length,
      uniqueUsers,
      timeRange: timeRange || {
        start: new Date(Math.min(...filteredEntries.map(e => e.timestamp.getTime()))),
        end: new Date(Math.max(...filteredEntries.map(e => e.timestamp.getTime()))),
      },
    };
  }

  /**
   * セキュリティイベントの検索
   */
  searchSecurityEvents(filters: {
    eventType?: SecurityEventType;
    userId?: string;
    username?: string;
    riskLevel?: string;
    success?: boolean;
    timeRange?: { start: Date; end: Date };
  }): SecurityLogEntry[] {
    return this.logEntries.filter(entry => {
      if (filters.eventType && entry.eventType !== filters.eventType) return false;
      if (filters.userId && entry.userId !== filters.userId) return false;
      if (filters.username && entry.username !== filters.username) return false;
      if (filters.riskLevel && entry.riskLevel !== filters.riskLevel) return false;
      if (filters.success !== undefined && entry.success !== filters.success) return false;
      if (filters.timeRange) {
        if (entry.timestamp < filters.timeRange.start || 
            entry.timestamp > filters.timeRange.end) return false;
      }
      return true;
    });
  }

  /**
   * 監査ログの検索
   */
  searchAuditEvents(filters: {
    userId?: string;
    username?: string;
    action?: string;
    resource?: string;
    timeRange?: { start: Date; end: Date };
  }): SecurityAuditEntry[] {
    return this.auditEntries.filter(entry => {
      if (filters.userId && entry.userId !== filters.userId) return false;
      if (filters.username && entry.username !== filters.username) return false;
      if (filters.action && !entry.action.includes(filters.action)) return false;
      if (filters.resource && !entry.resource.includes(filters.resource)) return false;
      if (filters.timeRange) {
        if (entry.timestamp < filters.timeRange.start || 
            entry.timestamp > filters.timeRange.end) return false;
      }
      return true;
    });
  }

  /**
   * セキュリティレポートの生成
   */
  generateSecurityReport(timeRange?: { start: Date; end: Date }): {
    metrics: SecurityMetrics;
    topRisks: SecurityLogEntry[];
    recentAudits: SecurityAuditEntry[];
    recommendations: string[];
  } {
    const metrics = this.getSecurityMetrics(timeRange);
    const topRisks = this.searchSecurityEvents({ riskLevel: 'critical' })
      .concat(this.searchSecurityEvents({ riskLevel: 'high' }))
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 10);

    const recentAudits = this.auditEntries
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 20);

    const recommendations = this.generateRecommendations(metrics, topRisks);

    return {
      metrics,
      topRisks,
      recentAudits,
      recommendations,
    };
  }

  /**
   * セキュリティ推奨事項の生成
   */
  private generateRecommendations(metrics: SecurityMetrics, risks: SecurityLogEntry[]): string[] {
    const recommendations: string[] = [];

    if (metrics.authFailureCount > metrics.authSuccessCount * 0.1) {
      recommendations.push('認証失敗率が高いです。パスワードポリシーの見直しを検討してください。');
    }

    if (metrics.lockoutCount > 0) {
      recommendations.push('アカウントロックアウトが発生しています。不正アクセス対策を強化してください。');
    }

    if (metrics.rateLimitViolations > metrics.totalEvents * 0.05) {
      recommendations.push('レート制限違反が多発しています。制限値の調整を検討してください。');
    }

    if (metrics.criticalRiskEvents > 0) {
      recommendations.push('重大なセキュリティイベントが検出されています。即座に調査が必要です。');
    }

    if (risks.length > 10) {
      recommendations.push('高リスクイベントが頻発しています。セキュリティ監視の強化を推奨します。');
    }

    return recommendations;
  }
}

// デフォルトインスタンス
export const securityLogger = new SecurityLogger();