import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { SecurityLogger, SecurityEventType } from '../security_logger.js';

describe('SecurityLogger', () => {
  let securityLogger: SecurityLogger;

  beforeEach(() => {
    securityLogger = new SecurityLogger();
    jest.clearAllMocks();
  });

  describe('セキュリティイベントログ', () => {
    it('認証成功イベントをログ記録できること', () => {
      const context = {
        userId: 'user123',
        username: 'testuser',
        ipAddress: '192.168.1.100',
        userAgent: 'Mozilla/5.0...',
      };

      securityLogger.logSecurityEvent(
        SecurityEventType.AUTH_SUCCESS,
        true,
        context
      );

      const metrics = securityLogger.getSecurityMetrics();
      expect(metrics.totalEvents).toBe(1);
      expect(metrics.authSuccessCount).toBe(1);
      expect(metrics.authFailureCount).toBe(0);
    });

    it('認証失敗イベントをログ記録できること', () => {
      const context = {
        userId: 'user123',
        username: 'testuser',
        ipAddress: '192.168.1.100',
        details: { reason: 'invalid password' },
      };

      securityLogger.logSecurityEvent(
        SecurityEventType.AUTH_FAILURE,
        false,
        context
      );

      const metrics = securityLogger.getSecurityMetrics();
      expect(metrics.totalEvents).toBe(1);
      expect(metrics.authFailureCount).toBe(1);
      expect(metrics.authSuccessCount).toBe(0);
    });

    it('高リスクイベントを適切に分類できること', () => {
      securityLogger.logSecurityEvent(
        SecurityEventType.SUSPICIOUS_ACTIVITY,
        false,
        { userId: 'user123', details: { threat: 'brute force' } }
      );

      const metrics = securityLogger.getSecurityMetrics();
      expect(metrics.criticalRiskEvents).toBe(1);
    });

    it('複数回の失敗を高リスクとして分類できること', () => {
      securityLogger.logSecurityEvent(
        SecurityEventType.AUTH_FAILURE,
        false,
        { 
          userId: 'user123',
          details: { failureCount: 5 }
        }
      );

      const metrics = securityLogger.getSecurityMetrics();
      expect(metrics.highRiskEvents).toBe(1);
    });
  });

  describe('監査ログ', () => {
    it('監査イベントをログ記録できること', () => {
      securityLogger.logAuditEvent(
        'user123',
        'testuser',
        'UPDATE_CONFIG',
        'drone_settings',
        {
          oldValue: { maxSpeed: 10 },
          newValue: { maxSpeed: 15 },
          ipAddress: '192.168.1.100',
        }
      );

      const auditEvents = securityLogger.searchAuditEvents({
        userId: 'user123',
      });

      expect(auditEvents.length).toBe(1);
      expect(auditEvents[0].action).toBe('UPDATE_CONFIG');
      expect(auditEvents[0].resource).toBe('drone_settings');
    });
  });

  describe('セキュリティメトリクス', () => {
    beforeEach(() => {
      // テストデータを作成
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_SUCCESS, true, { userId: 'user1' });
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_SUCCESS, true, { userId: 'user2' });
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_FAILURE, false, { userId: 'user1' });
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_LOCKOUT, false, { userId: 'user1' });
      securityLogger.logSecurityEvent(SecurityEventType.RATE_LIMIT_EXCEEDED, false, { userId: 'user3' });
      securityLogger.logSecurityEvent(SecurityEventType.SUSPICIOUS_ACTIVITY, false, { userId: 'user4' });
    });

    it('基本的なメトリクスを正しく計算できること', () => {
      const metrics = securityLogger.getSecurityMetrics();

      expect(metrics.totalEvents).toBe(6);
      expect(metrics.authSuccessCount).toBe(2);
      expect(metrics.authFailureCount).toBe(1);
      expect(metrics.lockoutCount).toBe(1);
      expect(metrics.rateLimitViolations).toBe(1);
      expect(metrics.suspiciousActivities).toBe(1);
      expect(metrics.uniqueUsers).toBe(4);
    });

    it('時間範囲でフィルタリングできること', () => {
      const now = new Date();
      const oneHourAgo = new Date(now.getTime() - 3600000);
      const oneHourLater = new Date(now.getTime() + 3600000);

      const metrics = securityLogger.getSecurityMetrics({
        start: oneHourAgo,
        end: oneHourLater,
      });

      expect(metrics.totalEvents).toBe(6); // 全て現在時刻で作成されているため
    });
  });

  describe('イベント検索', () => {
    beforeEach(() => {
      // 検索用のテストデータを作成
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_SUCCESS, true, {
        userId: 'user1',
        username: 'alice',
      });

      securityLogger.logSecurityEvent(SecurityEventType.AUTH_FAILURE, false, {
        userId: 'user2',
        username: 'bob',
      });

      securityLogger.logSecurityEvent(SecurityEventType.API_KEY_USED, true, {
        userId: 'user1',
        username: 'alice',
      });
    });

    it('イベントタイプでフィルタリングできること', () => {
      const events = securityLogger.searchSecurityEvents({
        eventType: SecurityEventType.AUTH_SUCCESS,
      });

      expect(events.length).toBe(1);
      expect(events[0].eventType).toBe(SecurityEventType.AUTH_SUCCESS);
      expect(events[0].username).toBe('alice');
    });

    it('ユーザーIDでフィルタリングできること', () => {
      const events = securityLogger.searchSecurityEvents({
        userId: 'user1',
      });

      expect(events.length).toBe(2);
      expect(events.every(e => e.userId === 'user1')).toBe(true);
    });

    it('成功/失敗でフィルタリングできること', () => {
      const successEvents = securityLogger.searchSecurityEvents({
        success: true,
      });

      const failureEvents = securityLogger.searchSecurityEvents({
        success: false,
      });

      expect(successEvents.length).toBe(2);
      expect(failureEvents.length).toBe(1);
    });

    it('複数の条件で組み合わせフィルタリングできること', () => {
      const events = securityLogger.searchSecurityEvents({
        userId: 'user1',
        success: true,
      });

      expect(events.length).toBe(2);
      expect(events.every(e => e.userId === 'user1' && e.success === true)).toBe(true);
    });
  });

  describe('監査ログ検索', () => {
    beforeEach(() => {
      // 検索用のテストデータを作成
      securityLogger.logAuditEvent(
        'user1',
        'alice',
        'CREATE_USER',
        'users',
        { newValue: { username: 'newuser' } }
      );

      securityLogger.logAuditEvent(
        'user2',
        'bob',
        'UPDATE_CONFIG',
        'drone_settings',
        { 
          oldValue: { speed: 10 },
          newValue: { speed: 15 }
        }
      );

      securityLogger.logAuditEvent(
        'user1',
        'alice',
        'DELETE_USER',
        'users',
        { oldValue: { username: 'olduser' } }
      );
    });

    it('ユーザーIDでフィルタリングできること', () => {
      const events = securityLogger.searchAuditEvents({
        userId: 'user1',
      });

      expect(events.length).toBe(2);
      expect(events.every(e => e.userId === 'user1')).toBe(true);
    });

    it('アクションでフィルタリングできること', () => {
      const events = securityLogger.searchAuditEvents({
        action: 'USER',
      });

      expect(events.length).toBe(2); // CREATE_USER, DELETE_USER
    });

    it('リソースでフィルタリングできること', () => {
      const events = securityLogger.searchAuditEvents({
        resource: 'users',
      });

      expect(events.length).toBe(2);
      expect(events.every(e => e.resource === 'users')).toBe(true);
    });
  });

  describe('セキュリティレポート', () => {
    beforeEach(() => {
      // レポート用のテストデータを作成
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_SUCCESS, true, { userId: 'user1' });
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_FAILURE, false, { userId: 'user2' });
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_FAILURE, false, { userId: 'user2' });
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_LOCKOUT, false, { userId: 'user2' });
      securityLogger.logSecurityEvent(SecurityEventType.SUSPICIOUS_ACTIVITY, false, { userId: 'user3' });

      securityLogger.logAuditEvent('user1', 'alice', 'CREATE_API_KEY', 'api_keys');
      securityLogger.logAuditEvent('user2', 'bob', 'UPDATE_SETTINGS', 'system');
    });

    it('包括的なセキュリティレポートを生成できること', () => {
      const report = securityLogger.generateSecurityReport();

      expect(report.metrics).toBeDefined();
      expect(report.topRisks).toBeDefined();
      expect(report.recentAudits).toBeDefined();
      expect(report.recommendations).toBeDefined();

      expect(report.metrics.totalEvents).toBe(5);
      expect(report.topRisks.length).toBeGreaterThan(0);
      expect(report.recentAudits.length).toBe(2);
    });

    it('適切な推奨事項を生成できること', () => {
      const report = securityLogger.generateSecurityReport();

      expect(report.recommendations).toContain(
        expect.stringContaining('アカウントロックアウトが発生しています')
      );
      expect(report.recommendations).toContain(
        expect.stringContaining('重大なセキュリティイベントが検出されています')
      );
    });

    it('リスクイベントを優先度順にソートできること', () => {
      const report = securityLogger.generateSecurityReport();

      // 最新のイベントが最初に来ることを確認
      expect(report.topRisks.length).toBeGreaterThan(1);
      
      // 時系列で降順にソートされていることを確認
      for (let i = 1; i < report.topRisks.length; i++) {
        expect(report.topRisks[i-1].timestamp.getTime())
          .toBeGreaterThanOrEqual(report.topRisks[i].timestamp.getTime());
      }
    });
  });

  describe('リスクレベル計算', () => {
    it('クリティカルイベントを正しく分類できること', () => {
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_LOCKOUT, false, {});
      securityLogger.logSecurityEvent(SecurityEventType.SUSPICIOUS_ACTIVITY, false, {});
      securityLogger.logSecurityEvent(SecurityEventType.SECURITY_CONFIG_CHANGED, true, {});

      const events = securityLogger.searchSecurityEvents({});
      const criticalEvents = events.filter(e => e.riskLevel === 'critical');
      
      expect(criticalEvents.length).toBe(3);
    });

    it('高リスクイベントを正しく分類できること', () => {
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_FAILURE, false, {});
      securityLogger.logSecurityEvent(SecurityEventType.PERMISSION_DENIED, false, {});
      securityLogger.logSecurityEvent(SecurityEventType.RATE_LIMIT_EXCEEDED, false, {});

      const events = securityLogger.searchSecurityEvents({});
      const highRiskEvents = events.filter(e => e.riskLevel === 'high');
      
      expect(highRiskEvents.length).toBe(3);
    });

    it('中リスクイベントを正しく分類できること', () => {
      securityLogger.logSecurityEvent(SecurityEventType.API_KEY_CREATED, true, {});
      securityLogger.logSecurityEvent(SecurityEventType.SYSTEM_ACCESS, true, {});

      const events = securityLogger.searchSecurityEvents({});
      const mediumRiskEvents = events.filter(e => e.riskLevel === 'medium');
      
      expect(mediumRiskEvents.length).toBe(2);
    });

    it('低リスクイベントを正しく分類できること', () => {
      securityLogger.logSecurityEvent(SecurityEventType.AUTH_SUCCESS, true, {});
      securityLogger.logSecurityEvent(SecurityEventType.API_KEY_USED, true, {});

      const events = securityLogger.searchSecurityEvents({});
      const lowRiskEvents = events.filter(e => e.riskLevel === 'low');
      
      expect(lowRiskEvents.length).toBe(2);
    });
  });
});