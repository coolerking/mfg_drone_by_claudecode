import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { SecurityManager, type SecurityConfig } from '../security_manager.js';

describe('SecurityManager', () => {
  let securityManager: SecurityManager;
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
    // テスト用の環境変数を設定
    process.env.JWT_SECRET = 'test-secret-key-for-jwt-that-is-long-enough-to-be-secure-32-chars';
    process.env.JWT_EXPIRES_IN = '1h';
    process.env.BCRYPT_SALT_ROUNDS = '10'; // テスト時は高速化のため10に設定
    
    const testConfig: Partial<SecurityConfig> = {
      jwtSecret: process.env.JWT_SECRET,
      jwtExpiresIn: '1h',
      saltRounds: 10,
      rateLimitRequests: 5,
      rateLimitWindow: 60000, // 1分
      maxFailedAttempts: 3,
      lockoutDurationMs: 30000, // 30秒
    };
    
    securityManager = new SecurityManager(testConfig);
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('パスワード管理', () => {
    it('パスワードを正しくハッシュ化できること', async () => {
      const password = 'TestPassword123!';
      const hashedPassword = await securityManager.hashPassword(password);
      
      expect(hashedPassword).toBeDefined();
      expect(hashedPassword).not.toBe(password);
      expect(hashedPassword.length).toBeGreaterThan(50);
    });

    it('パスワードの検証が正しく動作すること', async () => {
      const password = 'TestPassword123!';
      const hashedPassword = await securityManager.hashPassword(password);
      
      const isValid = await securityManager.verifyPassword(password, hashedPassword);
      expect(isValid).toBe(true);
      
      const isInvalid = await securityManager.verifyPassword('WrongPassword', hashedPassword);
      expect(isInvalid).toBe(false);
    });
  });

  describe('JWT管理', () => {
    it('JWTトークンを正しく生成できること', () => {
      const payload = {
        userId: 'test-user-id',
        username: 'testuser',
        role: 'user' as const,
        permissions: ['drone:read', 'drone:control'],
      };

      const token = securityManager.generateJWT(payload);
      
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.').length).toBe(3); // JWT形式の確認
    });

    it('JWTトークンを正しく検証できること', () => {
      const payload = {
        userId: 'test-user-id',
        username: 'testuser',
        role: 'user' as const,
        permissions: ['drone:read', 'drone:control'],
      };

      const token = securityManager.generateJWT(payload);
      const decodedPayload = securityManager.verifyJWT(token);
      
      expect(decodedPayload).toBeDefined();
      expect(decodedPayload!.userId).toBe(payload.userId);
      expect(decodedPayload!.username).toBe(payload.username);
      expect(decodedPayload!.role).toBe(payload.role);
      expect(decodedPayload!.permissions).toEqual(payload.permissions);
      expect(decodedPayload!.iat).toBeDefined();
      expect(decodedPayload!.exp).toBeDefined();
    });

    it('無効なJWTトークンはnullを返すこと', () => {
      const invalidToken = 'invalid.jwt.token';
      const decodedPayload = securityManager.verifyJWT(invalidToken);
      
      expect(decodedPayload).toBeNull();
    });
  });

  describe('APIキー管理', () => {
    it('APIキーを正しく生成できること', () => {
      const name = 'test-api-key';
      const permissions = ['drone:read', 'vision:read'];
      
      const result = securityManager.generateApiKey(name, permissions);
      
      expect(result.key).toBeDefined();
      expect(result.keyInfo).toBeDefined();
      expect(result.keyInfo.name).toBe(name);
      expect(result.keyInfo.permissions).toEqual(permissions);
      expect(result.keyInfo.isActive).toBe(true);
      expect(result.keyInfo.createdAt).toBeInstanceOf(Date);
      expect(result.key.length).toBe(64); // デフォルトのキー長
    });

    it('APIキーを正しく検証できること', () => {
      const name = 'test-api-key';
      const permissions = ['drone:read', 'vision:read'];
      
      const result = securityManager.generateApiKey(name, permissions);
      const keyInfo = securityManager.verifyApiKey(result.key);
      
      expect(keyInfo).toBeDefined();
      expect(keyInfo!.name).toBe(name);
      expect(keyInfo!.permissions).toEqual(permissions);
      expect(keyInfo!.isActive).toBe(true);
      expect(keyInfo!.usageCount).toBe(1); // 検証により使用回数が増加
    });

    it('無効なAPIキーはnullを返すこと', () => {
      const invalidKey = 'invalid-api-key';
      const keyInfo = securityManager.verifyApiKey(invalidKey);
      
      expect(keyInfo).toBeNull();
    });

    it('期限切れのAPIキーはnullを返すこと', () => {
      const name = 'expired-api-key';
      const permissions = ['drone:read'];
      
      // 過去の日付で期限切れキーを作成
      const result = securityManager.generateApiKey(name, permissions, -1);
      const keyInfo = securityManager.verifyApiKey(result.key);
      
      expect(keyInfo).toBeNull();
    });
  });

  describe('レート制限', () => {
    it('制限内のリクエストは許可されること', () => {
      const identifier = 'test-user';
      
      const result = securityManager.checkRateLimit(identifier);
      
      expect(result.allowed).toBe(true);
      expect(result.remainingRequests).toBe(4); // 5 - 1 = 4
      expect(result.resetTime).toBeGreaterThan(Date.now());
    });

    it('制限を超えたリクエストは拒否されること', () => {
      const identifier = 'test-user';
      
      // 制限まで消費
      for (let i = 0; i < 5; i++) {
        securityManager.checkRateLimit(identifier);
      }
      
      // 制限を超えたリクエスト
      const result = securityManager.checkRateLimit(identifier);
      
      expect(result.allowed).toBe(false);
      expect(result.remainingRequests).toBe(0);
    });
  });

  describe('失敗した認証試行', () => {
    it('失敗回数を正しく記録できること', () => {
      const identifier = 'test-user';
      
      let result = securityManager.recordFailedAttempt(identifier);
      expect(result.isLocked).toBe(false);
      
      result = securityManager.recordFailedAttempt(identifier);
      expect(result.isLocked).toBe(false);
      
      result = securityManager.recordFailedAttempt(identifier);
      expect(result.isLocked).toBe(true);
      expect(result.lockedUntil).toBeDefined();
    });

    it('成功した認証でカウントがリセットされること', () => {
      const identifier = 'test-user';
      
      // 失敗を記録
      securityManager.recordFailedAttempt(identifier);
      securityManager.recordFailedAttempt(identifier);
      
      // 成功を記録
      securityManager.recordSuccessfulAttempt(identifier);
      
      // アカウントロック状態を確認
      const lockStatus = securityManager.isAccountLocked(identifier);
      expect(lockStatus.isLocked).toBe(false);
    });

    it('ロックアウト状態を正しく判定できること', () => {
      const identifier = 'test-user';
      
      // 制限回数まで失敗
      for (let i = 0; i < 3; i++) {
        securityManager.recordFailedAttempt(identifier);
      }
      
      const lockStatus = securityManager.isAccountLocked(identifier);
      expect(lockStatus.isLocked).toBe(true);
      expect(lockStatus.lockedUntil).toBeDefined();
    });
  });

  describe('権限チェック', () => {
    it('管理者権限は常に許可されること', () => {
      const adminPermissions = ['admin'];
      const requiredPermission = 'any-permission';
      
      const hasPermission = securityManager.hasPermission(adminPermissions, requiredPermission);
      expect(hasPermission).toBe(true);
    });

    it('適切な権限を持つユーザーは許可されること', () => {
      const userPermissions = ['drone:read', 'drone:control'];
      const requiredPermission = 'drone:read';
      
      const hasPermission = securityManager.hasPermission(userPermissions, requiredPermission);
      expect(hasPermission).toBe(true);
    });

    it('権限を持たないユーザーは拒否されること', () => {
      const userPermissions = ['drone:read'];
      const requiredPermission = 'drone:control';
      
      const hasPermission = securityManager.hasPermission(userPermissions, requiredPermission);
      expect(hasPermission).toBe(false);
    });
  });

  describe('セキュリティ統計', () => {
    it('セキュリティ統計を正しく取得できること', () => {
      // テストデータを作成
      securityManager.generateApiKey('key1', ['drone:read']);
      securityManager.generateApiKey('key2', ['vision:read'], -1); // 期限切れ
      securityManager.checkRateLimit('user1');
      securityManager.checkRateLimit('user1');
      securityManager.checkRateLimit('user1');
      securityManager.checkRateLimit('user1');
      securityManager.checkRateLimit('user1');
      securityManager.checkRateLimit('user1'); // レート制限違反
      securityManager.recordFailedAttempt('user2');
      securityManager.recordFailedAttempt('user2');
      securityManager.recordFailedAttempt('user2'); // ロックアウト
      
      const stats = securityManager.getSecurityStats();
      
      expect(stats.totalApiKeys).toBe(2);
      expect(stats.activeApiKeys).toBe(1); // 期限切れを除く
      expect(stats.rateLimitedClients).toBe(1);
      expect(stats.lockedAccounts).toBe(1);
    });
  });
});