import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { SecurityManager } from '../security_manager.js';
import { AuthManager } from '../auth_manager.js';

describe('AuthManager', () => {
  let securityManager: SecurityManager;
  let authManager: AuthManager;

  beforeEach(() => {
    const testConfig = {
      jwtSecret: 'test-secret-key-for-jwt-that-is-long-enough-to-be-secure-32-chars',
      jwtExpiresIn: '1h',
      saltRounds: 10,
      rateLimitRequests: 5,
      rateLimitWindow: 60000,
      maxFailedAttempts: 3,
      lockoutDurationMs: 30000,
    };
    
    securityManager = new SecurityManager(testConfig);
    authManager = new AuthManager(securityManager);
    
    // デフォルト管理者の初期化を待つ
    jest.setTimeout(10000);
  });

  describe('ユーザー認証', () => {
    it('有効な管理者クレデンシャルで認証が成功すること', async () => {
      const result = await authManager.authenticateUser('admin', 'Admin123!');
      
      expect(result.success).toBe(true);
      expect(result.token).toBeDefined();
      expect(result.payload).toBeDefined();
      expect(result.payload!.username).toBe('admin');
      expect(result.payload!.role).toBe('admin');
      expect(result.message).toBe('認証に成功しました');
    });

    it('無効なパスワードで認証が失敗すること', async () => {
      const result = await authManager.authenticateUser('admin', 'wrongpassword');
      
      expect(result.success).toBe(false);
      expect(result.token).toBeUndefined();
      expect(result.message).toBe('ユーザー名またはパスワードが正しくありません');
    });

    it('存在しないユーザーで認証が失敗すること', async () => {
      const result = await authManager.authenticateUser('nonexistent', 'password');
      
      expect(result.success).toBe(false);
      expect(result.token).toBeUndefined();
      expect(result.message).toBe('ユーザー名またはパスワードが正しくありません');
    });

    it('複数回の失敗でアカウントがロックされること', async () => {
      const username = 'admin';
      const wrongPassword = 'wrongpassword';

      // 3回失敗させる
      for (let i = 0; i < 3; i++) {
        await authManager.authenticateUser(username, wrongPassword);
      }

      // 4回目の試行
      const result = await authManager.authenticateUser(username, wrongPassword);
      
      expect(result.success).toBe(false);
      expect(result.message).toBe('アカウントがロックされています');
      expect(result.lockoutInfo).toBeDefined();
      expect(result.lockoutInfo!.isLocked).toBe(true);
    });

    it('有効なクレデンシャルによってログイン試行がリセットされること', async () => {
      const username = 'admin';
      const correctPassword = 'Admin123!';
      const wrongPassword = 'wrongpassword';

      // 2回失敗
      await authManager.authenticateUser(username, wrongPassword);
      await authManager.authenticateUser(username, wrongPassword);

      // 成功
      const successResult = await authManager.authenticateUser(username, correctPassword);
      expect(successResult.success).toBe(true);

      // 再度失敗してもロックされないことを確認
      const failResult = await authManager.authenticateUser(username, wrongPassword);
      expect(failResult.success).toBe(false);
      expect(failResult.message).not.toBe('アカウントがロックされています');
    });
  });

  describe('APIキー認証', () => {
    it('有効なAPIキーで認証が成功すること', () => {
      const keyResult = securityManager.generateApiKey('test-key', ['drone:read']);
      
      const authResult = authManager.authenticateApiKey(keyResult.key);
      
      expect(authResult.success).toBe(true);
      expect(authResult.payload).toBeDefined();
      expect(authResult.payload!.username).toBe('test-key');
      expect(authResult.payload!.permissions).toEqual(['drone:read']);
      expect(authResult.message).toBe('APIキー認証に成功しました');
    });

    it('無効なAPIキーで認証が失敗すること', () => {
      const result = authManager.authenticateApiKey('invalid-api-key');
      
      expect(result.success).toBe(false);
      expect(result.message).toBe('APIキーが無効です');
    });
  });

  describe('JWT認証', () => {
    it('有効なJWTトークンで認証が成功すること', () => {
      const payload = {
        userId: 'test-user',
        username: 'testuser',
        role: 'user' as const,
        permissions: ['drone:read'],
      };
      
      const token = securityManager.generateJWT(payload);
      const result = authManager.authenticateToken(token);
      
      expect(result.success).toBe(true);
      expect(result.payload).toBeDefined();
      expect(result.payload!.username).toBe('testuser');
      expect(result.message).toBe('トークン認証に成功しました');
    });

    it('無効なJWTトークンで認証が失敗すること', () => {
      const result = authManager.authenticateToken('invalid.jwt.token');
      
      expect(result.success).toBe(false);
      expect(result.message).toBe('トークンが無効または期限切れです');
    });
  });

  describe('認可機能', () => {
    it('管理者は全ての権限を持つこと', () => {
      const adminPayload = {
        userId: 'admin',
        username: 'admin',
        role: 'admin' as const,
        permissions: ['admin'],
        iat: Date.now(),
        exp: Date.now() + 3600,
      };

      const result = authManager.authorize(adminPayload, ['drone:control', 'system:write']);
      
      expect(result.authorized).toBe(true);
      expect(result.message).toBe('管理者権限で認可されました');
    });

    it('適切な権限を持つユーザーは認可されること', () => {
      const userPayload = {
        userId: 'user',
        username: 'testuser',
        role: 'user' as const,
        permissions: ['drone:read', 'drone:control'],
        iat: Date.now(),
        exp: Date.now() + 3600,
      };

      const result = authManager.authorize(userPayload, ['drone:read']);
      
      expect(result.authorized).toBe(true);
      expect(result.message).toBe('認可に成功しました');
    });

    it('権限不足のユーザーは認可が拒否されること', () => {
      const userPayload = {
        userId: 'user',
        username: 'testuser',
        role: 'user' as const,
        permissions: ['drone:read'],
        iat: Date.now(),
        exp: Date.now() + 3600,
      };

      const result = authManager.authorize(userPayload, ['system:write']);
      
      expect(result.authorized).toBe(false);
      expect(result.message).toBe('必要な権限がありません');
      expect(result.requiredPermissions).toEqual(['system:write']);
      expect(result.userPermissions).toEqual(['drone:read']);
    });
  });

  describe('ユーザー登録', () => {
    it('有効なユーザーデータで登録が成功すること', async () => {
      const userData = {
        username: 'newuser',
        password: 'NewPass123!',
        email: 'newuser@example.com',
        role: 'user' as const,
      };

      const result = await authManager.registerUser(userData);
      
      expect(result.success).toBe(true);
      expect(result.message).toBe('ユーザー登録に成功しました');

      // 登録したユーザーでログインできることを確認
      const loginResult = await authManager.authenticateUser('newuser', 'NewPass123!');
      expect(loginResult.success).toBe(true);
    });

    it('重複するユーザー名での登録が失敗すること', async () => {
      const userData = {
        username: 'admin', // 既存のユーザー名
        password: 'NewPass123!',
        email: 'admin2@example.com',
      };

      const result = await authManager.registerUser(userData);
      
      expect(result.success).toBe(false);
      expect(result.message).toBe('ユーザー名は既に使用されています');
    });
  });

  describe('パスワード変更', () => {
    beforeEach(async () => {
      // テスト用ユーザーを登録
      await authManager.registerUser({
        username: 'testuser',
        password: 'OldPass123!',
        email: 'test@example.com',
      });
    });

    it('有効な情報でパスワード変更が成功すること', async () => {
      const result = await authManager.changePassword(
        'testuser',
        'OldPass123!',
        'NewPass456@'
      );
      
      expect(result.success).toBe(true);
      expect(result.message).toBe('パスワードを変更しました');

      // 新しいパスワードでログインできることを確認
      const loginResult = await authManager.authenticateUser('testuser', 'NewPass456@');
      expect(loginResult.success).toBe(true);
    });

    it('現在のパスワードが間違っている場合は失敗すること', async () => {
      const result = await authManager.changePassword(
        'testuser',
        'WrongCurrentPassword',
        'NewPass456@'
      );
      
      expect(result.success).toBe(false);
      expect(result.message).toBe('現在のパスワードが正しくありません');
    });

    it('存在しないユーザーのパスワード変更は失敗すること', async () => {
      const result = await authManager.changePassword(
        'nonexistent',
        'SomePassword',
        'NewPass456@'
      );
      
      expect(result.success).toBe(false);
      expect(result.message).toBe('ユーザーが見つかりません');
    });
  });

  describe('ユーザー管理', () => {
    beforeEach(async () => {
      // テスト用ユーザーを登録
      await authManager.registerUser({
        username: 'user1',
        password: 'Password123!',
        email: 'user1@example.com',
        role: 'user',
      });
      
      await authManager.registerUser({
        username: 'readonly1',
        password: 'Password123!',
        email: 'readonly1@example.com',
        role: 'readonly',
      });
    });

    it('全ユーザーを取得できること', () => {
      const users = authManager.getAllUsers();
      
      expect(users.length).toBeGreaterThanOrEqual(3); // admin + 登録した2人
      
      const admin = users.find(u => u.username === 'admin');
      expect(admin).toBeDefined();
      expect(admin!.role).toBe('admin');
      expect(admin!.isActive).toBe(true);
      
      const user1 = users.find(u => u.username === 'user1');
      expect(user1).toBeDefined();
      expect(user1!.role).toBe('user');
    });

    it('特定のユーザー情報を取得できること', () => {
      const user = authManager.getUser('user1');
      
      expect(user).toBeDefined();
      expect(user!.username).toBe('user1');
      expect(user!.role).toBe('user');
      expect(user!.email).toBe('user1@example.com');
      expect(user!.isActive).toBe(true);
    });

    it('存在しないユーザーはnullを返すこと', () => {
      const user = authManager.getUser('nonexistent');
      expect(user).toBeNull();
    });

    it('ユーザーの有効/無効を切り替えできること', () => {
      const result = authManager.toggleUserStatus('user1', false);
      expect(result).toBe(true);

      const user = authManager.getUser('user1');
      expect(user!.isActive).toBe(false);

      // 無効化されたユーザーはログインできない
      const loginResult = authManager.authenticateUser('user1', 'Password123!');
      expect(loginResult).resolves.toEqual(expect.objectContaining({
        success: false,
        message: 'アカウントが無効化されています',
      }));
    });

    it('存在しないユーザーの状態変更はfalseを返すこと', () => {
      const result = authManager.toggleUserStatus('nonexistent', false);
      expect(result).toBe(false);
    });
  });
});