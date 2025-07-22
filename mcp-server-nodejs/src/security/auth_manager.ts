import { SecurityManager, type UserCredentials, type JWTPayload, type ApiKeyInfo } from './security_manager.js';
import { logger } from '@/utils/logger.js';
import { PresetValidators } from './validators.js';

/**
 * 認証結果
 */
export interface AuthResult {
  success: boolean;
  token?: string;
  payload?: JWTPayload;
  message?: string;
  lockoutInfo?: {
    isLocked: boolean;
    lockedUntil?: number;
  };
}

/**
 * 認可結果
 */
export interface AuthorizationResult {
  authorized: boolean;
  message?: string;
  requiredPermissions?: string[];
  userPermissions?: string[];
}

/**
 * 認証・認可マネージャー
 */
export class AuthManager {
  private securityManager: SecurityManager;
  private users: Map<string, UserCredentials & { hashedPassword: string }> = new Map();

  constructor(securityManager: SecurityManager) {
    this.securityManager = securityManager;
    this.initializeDefaultUsers();
  }

  /**
   * デフォルトユーザーの初期化
   */
  private async initializeDefaultUsers(): Promise<void> {
    const adminPassword = process.env.ADMIN_PASSWORD || 'Admin123!';
    const hashedPassword = await this.securityManager.hashPassword(adminPassword);

    this.users.set('admin', {
      username: 'admin',
      password: hashedPassword,
      hashedPassword,
      email: 'admin@localhost',
      role: 'admin',
      isActive: true,
    });

    if (process.env.ADMIN_PASSWORD !== adminPassword) {
      logger.warn('Using default admin password. Please set ADMIN_PASSWORD environment variable for production.');
    }

    logger.info('Default admin user initialized');
  }

  /**
   * ユーザー認証（パスワード認証）
   */
  async authenticateUser(username: string, password: string): Promise<AuthResult> {
    try {
      // 入力値バリデーション
      const loginData = PresetValidators.validateLogin({ username, password });

      // アカウントロックチェック
      const lockStatus = this.securityManager.isAccountLocked(username);
      if (lockStatus.isLocked) {
        logger.warn('Authentication attempt on locked account', { username, lockedUntil: lockStatus.lockedUntil });
        return {
          success: false,
          message: 'アカウントがロックされています',
          lockoutInfo: lockStatus,
        };
      }

      // ユーザー検索
      const user = this.users.get(username);
      if (!user) {
        logger.warn('Authentication failed: user not found', { username });
        this.securityManager.recordFailedAttempt(username);
        return {
          success: false,
          message: 'ユーザー名またはパスワードが正しくありません',
        };
      }

      // アクティブユーザーチェック
      if (!user.isActive) {
        logger.warn('Authentication failed: user inactive', { username });
        this.securityManager.recordFailedAttempt(username);
        return {
          success: false,
          message: 'アカウントが無効化されています',
        };
      }

      // パスワード検証
      const isPasswordValid = await this.securityManager.verifyPassword(password, user.hashedPassword);
      if (!isPasswordValid) {
        logger.warn('Authentication failed: invalid password', { username });
        const lockoutResult = this.securityManager.recordFailedAttempt(username);
        return {
          success: false,
          message: 'ユーザー名またはパスワードが正しくありません',
          lockoutInfo: lockoutResult,
        };
      }

      // 認証成功
      this.securityManager.recordSuccessfulAttempt(username);

      // JWT生成
      const permissions = this.getUserPermissions(user);
      const token = this.securityManager.generateJWT({
        userId: username, // 実際の実装ではUUIDを使用
        username: user.username,
        role: user.role,
        permissions,
      });

      logger.info('User authenticated successfully', { username, role: user.role });

      return {
        success: true,
        token,
        payload: {
          userId: username,
          username: user.username,
          role: user.role,
          permissions,
          iat: Math.floor(Date.now() / 1000),
          exp: Math.floor(Date.now() / 1000) + 3600, // 1時間後
        },
        message: '認証に成功しました',
      };

    } catch (error) {
      logger.error('Authentication error', { error, username });
      return {
        success: false,
        message: '認証中にエラーが発生しました',
      };
    }
  }

  /**
   * API キー認証
   */
  authenticateApiKey(apiKey: string): AuthResult {
    try {
      const keyInfo = this.securityManager.verifyApiKey(apiKey);
      if (!keyInfo) {
        logger.warn('API key authentication failed');
        return {
          success: false,
          message: 'APIキーが無効です',
        };
      }

      logger.info('API key authenticated successfully', {
        keyId: keyInfo.id,
        name: keyInfo.name,
        usageCount: keyInfo.usageCount,
      });

      return {
        success: true,
        payload: {
          userId: keyInfo.id,
          username: keyInfo.name,
          role: 'user', // API キーは基本的にユーザー権限
          permissions: keyInfo.permissions,
          iat: Math.floor(Date.now() / 1000),
          exp: Math.floor(Date.now() / 1000) + 3600,
        },
        message: 'APIキー認証に成功しました',
      };

    } catch (error) {
      logger.error('API key authentication error', { error });
      return {
        success: false,
        message: 'APIキー認証中にエラーが発生しました',
      };
    }
  }

  /**
   * JWT トークン認証
   */
  authenticateToken(token: string): AuthResult {
    try {
      const payload = this.securityManager.verifyJWT(token);
      if (!payload) {
        return {
          success: false,
          message: 'トークンが無効または期限切れです',
        };
      }

      return {
        success: true,
        token,
        payload,
        message: 'トークン認証に成功しました',
      };

    } catch (error) {
      logger.error('Token authentication error', { error });
      return {
        success: false,
        message: 'トークン認証中にエラーが発生しました',
      };
    }
  }

  /**
   * 権限の確認
   */
  authorize(userPayload: JWTPayload, requiredPermissions: string[]): AuthorizationResult {
    try {
      // 管理者は全権限を持つ
      if (userPayload.role === 'admin') {
        return {
          authorized: true,
          message: '管理者権限で認可されました',
        };
      }

      // 必要な権限をチェック
      const hasAllPermissions = requiredPermissions.every(permission =>
        this.securityManager.hasPermission(userPayload.permissions, permission)
      );

      if (hasAllPermissions) {
        logger.debug('Authorization successful', {
          userId: userPayload.userId,
          requiredPermissions,
          userPermissions: userPayload.permissions,
        });

        return {
          authorized: true,
          message: '認可に成功しました',
        };
      }

      logger.warn('Authorization failed: insufficient permissions', {
        userId: userPayload.userId,
        requiredPermissions,
        userPermissions: userPayload.permissions,
      });

      return {
        authorized: false,
        message: '必要な権限がありません',
        requiredPermissions,
        userPermissions: userPayload.permissions,
      };

    } catch (error) {
      logger.error('Authorization error', { error, userPayload });
      return {
        authorized: false,
        message: '認可中にエラーが発生しました',
      };
    }
  }

  /**
   * ユーザー登録
   */
  async registerUser(userData: {
    username: string;
    password: string;
    email?: string;
    role?: 'admin' | 'user' | 'readonly';
  }): Promise<AuthResult> {
    try {
      // 入力値バリデーション
      const validatedData = PresetValidators.validateRegister(userData);

      // 既存ユーザーチェック
      if (this.users.has(validatedData.username)) {
        return {
          success: false,
          message: 'ユーザー名は既に使用されています',
        };
      }

      // パスワードハッシュ化
      const hashedPassword = await this.securityManager.hashPassword(validatedData.password);

      // ユーザー作成
      const user: UserCredentials & { hashedPassword: string } = {
        username: validatedData.username,
        password: validatedData.password, // 平文は保存しない（型の整合性のため）
        hashedPassword,
        email: validatedData.email,
        role: validatedData.role || 'user',
        isActive: true,
      };

      this.users.set(validatedData.username, user);

      logger.info('User registered successfully', {
        username: validatedData.username,
        role: validatedData.role,
      });

      return {
        success: true,
        message: 'ユーザー登録に成功しました',
      };

    } catch (error) {
      logger.error('User registration error', { error, userData: { username: userData.username } });
      return {
        success: false,
        message: 'ユーザー登録中にエラーが発生しました',
      };
    }
  }

  /**
   * パスワード変更
   */
  async changePassword(username: string, currentPassword: string, newPassword: string): Promise<AuthResult> {
    try {
      // 入力値バリデーション
      const validatedData = PresetValidators.validateChangePassword({
        currentPassword,
        newPassword,
        confirmPassword: newPassword,
      });

      // ユーザー検索
      const user = this.users.get(username);
      if (!user) {
        return {
          success: false,
          message: 'ユーザーが見つかりません',
        };
      }

      // 現在のパスワード確認
      const isCurrentPasswordValid = await this.securityManager.verifyPassword(
        validatedData.currentPassword,
        user.hashedPassword
      );

      if (!isCurrentPasswordValid) {
        logger.warn('Password change failed: current password invalid', { username });
        return {
          success: false,
          message: '現在のパスワードが正しくありません',
        };
      }

      // 新しいパスワードをハッシュ化
      const newHashedPassword = await this.securityManager.hashPassword(validatedData.newPassword);

      // パスワード更新
      user.hashedPassword = newHashedPassword;
      this.users.set(username, user);

      logger.info('Password changed successfully', { username });

      return {
        success: true,
        message: 'パスワードを変更しました',
      };

    } catch (error) {
      logger.error('Password change error', { error, username });
      return {
        success: false,
        message: 'パスワード変更中にエラーが発生しました',
      };
    }
  }

  /**
   * ユーザーの権限を取得
   */
  private getUserPermissions(user: UserCredentials): string[] {
    switch (user.role) {
      case 'admin':
        return ['admin']; // 管理者は全権限

      case 'user':
        return [
          'drone:read',
          'drone:control',
          'drone:connect',
          'vision:read',
          'vision:process',
          'system:read',
        ];

      case 'readonly':
        return [
          'drone:read',
          'vision:read',
          'system:read',
        ];

      default:
        return [];
    }
  }

  /**
   * ユーザー一覧取得（管理者用）
   */
  getAllUsers(): Array<Omit<UserCredentials, 'password'>> {
    return Array.from(this.users.values()).map(user => ({
      username: user.username,
      email: user.email,
      role: user.role,
      isActive: user.isActive,
    }));
  }

  /**
   * ユーザー情報取得
   */
  getUser(username: string): Omit<UserCredentials, 'password'> | null {
    const user = this.users.get(username);
    if (!user) {
      return null;
    }

    return {
      username: user.username,
      email: user.email,
      role: user.role,
      isActive: user.isActive,
    };
  }

  /**
   * ユーザーの有効/無効切り替え
   */
  toggleUserStatus(username: string, isActive: boolean): boolean {
    const user = this.users.get(username);
    if (!user) {
      return false;
    }

    user.isActive = isActive;
    this.users.set(username, user);

    logger.info('User status toggled', { username, isActive });
    return true;
  }
}