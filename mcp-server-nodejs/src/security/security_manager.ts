import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { logger } from '@/utils/logger.js';
import { z } from 'zod';

/**
 * セキュリティ設定
 */
export const SecurityConfigSchema = z.object({
  jwtSecret: z.string().min(32, 'JWT secret must be at least 32 characters'),
  jwtExpiresIn: z.string().default('1h'),
  apiKeyLength: z.number().min(32).default(64),
  saltRounds: z.number().min(10).max(15).default(12),
  rateLimitRequests: z.number().default(100),
  rateLimitWindow: z.number().default(900000), // 15 minutes in milliseconds
  enableApiKeyAuth: z.boolean().default(true),
  enableJwtAuth: z.boolean().default(true),
  maxFailedAttempts: z.number().default(5),
  lockoutDurationMs: z.number().default(300000), // 5 minutes
});

export type SecurityConfig = z.infer<typeof SecurityConfigSchema>;

/**
 * ユーザー認証情報
 */
export const UserCredentialsSchema = z.object({
  username: z.string().min(3).max(50),
  password: z.string().min(8),
  email: z.string().email().optional(),
  role: z.enum(['admin', 'user', 'readonly']).default('user'),
  isActive: z.boolean().default(true),
});

export type UserCredentials = z.infer<typeof UserCredentialsSchema>;

/**
 * JWT ペイロード
 */
export const JWTPayloadSchema = z.object({
  userId: z.string(),
  username: z.string(),
  role: z.enum(['admin', 'user', 'readonly']),
  permissions: z.array(z.string()),
  iat: z.number(),
  exp: z.number(),
});

export type JWTPayload = z.infer<typeof JWTPayloadSchema>;

/**
 * API キー情報
 */
export const ApiKeyInfoSchema = z.object({
  id: z.string(),
  keyHash: z.string(),
  name: z.string(),
  permissions: z.array(z.string()),
  createdAt: z.date(),
  expiresAt: z.date().optional(),
  isActive: z.boolean().default(true),
  lastUsed: z.date().optional(),
  usageCount: z.number().default(0),
});

export type ApiKeyInfo = z.infer<typeof ApiKeyInfoSchema>;

/**
 * レート制限情報
 */
interface RateLimitInfo {
  count: number;
  resetTime: number;
  isBlocked: boolean;
}

/**
 * セキュリティマネージャー
 * 認証、認可、APIキー管理、レート制限を担当
 */
export class SecurityManager {
  private config: SecurityConfig;
  private apiKeys: Map<string, ApiKeyInfo> = new Map();
  private rateLimitMap: Map<string, RateLimitInfo> = new Map();
  private failedAttempts: Map<string, { count: number; lockedUntil?: number }> = new Map();

  constructor(config: Partial<SecurityConfig> = {}) {
    // デフォルト値を環境変数で上書き
    const defaultConfig = {
      jwtSecret: process.env.JWT_SECRET || crypto.randomBytes(64).toString('hex'),
      jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1h',
      apiKeyLength: parseInt(process.env.API_KEY_LENGTH || '64'),
      saltRounds: parseInt(process.env.BCRYPT_SALT_ROUNDS || '12'),
      rateLimitRequests: parseInt(process.env.RATE_LIMIT_REQUESTS || '100'),
      rateLimitWindow: parseInt(process.env.RATE_LIMIT_WINDOW || '900000'),
      enableApiKeyAuth: process.env.ENABLE_API_KEY_AUTH !== 'false',
      enableJwtAuth: process.env.ENABLE_JWT_AUTH !== 'false',
      maxFailedAttempts: parseInt(process.env.MAX_FAILED_ATTEMPTS || '5'),
      lockoutDurationMs: parseInt(process.env.LOCKOUT_DURATION_MS || '300000'),
    };

    this.config = SecurityConfigSchema.parse({ ...defaultConfig, ...config });

    if (process.env.JWT_SECRET && process.env.JWT_SECRET.length < 32) {
      logger.warn('JWT_SECRET should be at least 32 characters for security');
    }

    logger.info('SecurityManager initialized', {
      jwtAuthEnabled: this.config.enableJwtAuth,
      apiKeyAuthEnabled: this.config.enableApiKeyAuth,
      rateLimitRequests: this.config.rateLimitRequests,
      rateLimitWindow: this.config.rateLimitWindow,
    });
  }

  /**
   * パスワードのハッシュ化
   */
  async hashPassword(password: string): Promise<string> {
    try {
      return await bcrypt.hash(password, this.config.saltRounds);
    } catch (error) {
      logger.error('Password hashing failed', { error });
      throw new Error('Password hashing failed');
    }
  }

  /**
   * パスワードの検証
   */
  async verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
    try {
      return await bcrypt.compare(password, hashedPassword);
    } catch (error) {
      logger.error('Password verification failed', { error });
      return false;
    }
  }

  /**
   * JWT トークンの生成
   */
  generateJWT(payload: Omit<JWTPayload, 'iat' | 'exp'>): string {
    try {
      const jwtPayload = {
        ...payload,
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + this.parseJwtExpiresIn(this.config.jwtExpiresIn),
      };

      return jwt.sign(jwtPayload, this.config.jwtSecret, {
        expiresIn: this.config.jwtExpiresIn,
      } as any);
    } catch (error) {
      logger.error('JWT generation failed', { error });
      throw new Error('JWT generation failed');
    }
  }

  /**
   * JWT トークンの検証
   */
  verifyJWT(token: string): JWTPayload | null {
    try {
      const decoded = jwt.verify(token, this.config.jwtSecret) as any;
      return JWTPayloadSchema.parse(decoded);
    } catch (error) {
      if (error instanceof jwt.JsonWebTokenError) {
        logger.warn('Invalid JWT token', { error: error.message });
      } else if (error instanceof jwt.TokenExpiredError) {
        logger.warn('JWT token expired', { error: error.message });
      } else {
        logger.error('JWT verification failed', { error });
      }
      return null;
    }
  }

  /**
   * API キーの生成
   */
  generateApiKey(name: string, permissions: string[], expiresInDays?: number): { key: string; keyInfo: ApiKeyInfo } {
    try {
      const key = crypto.randomBytes(this.config.apiKeyLength / 2).toString('hex');
      const keyHash = crypto.createHash('sha256').update(key).digest('hex');
      
      const expiresAt = expiresInDays 
        ? new Date(Date.now() + expiresInDays * 24 * 60 * 60 * 1000)
        : undefined;

      const keyInfo: ApiKeyInfo = {
        id: crypto.randomUUID(),
        keyHash,
        name,
        permissions,
        createdAt: new Date(),
        expiresAt,
        isActive: true,
        usageCount: 0,
      };

      // メモリに保存（実際の実装ではデータベースに保存する）
      this.apiKeys.set(keyHash, keyInfo);

      logger.info('API key generated', {
        keyId: keyInfo.id,
        name: keyInfo.name,
        permissions: keyInfo.permissions,
        expiresAt: keyInfo.expiresAt,
      });

      return { key, keyInfo };
    } catch (error) {
      logger.error('API key generation failed', { error });
      throw new Error('API key generation failed');
    }
  }

  /**
   * API キーの検証
   */
  verifyApiKey(key: string): ApiKeyInfo | null {
    try {
      const keyHash = crypto.createHash('sha256').update(key).digest('hex');
      const keyInfo = this.apiKeys.get(keyHash);

      if (!keyInfo) {
        logger.warn('API key not found', { keyHash: keyHash.substring(0, 8) + '...' });
        return null;
      }

      if (!keyInfo.isActive) {
        logger.warn('API key is inactive', { keyId: keyInfo.id });
        return null;
      }

      if (keyInfo.expiresAt && keyInfo.expiresAt < new Date()) {
        logger.warn('API key is expired', { keyId: keyInfo.id, expiresAt: keyInfo.expiresAt });
        return null;
      }

      // 使用統計を更新
      keyInfo.lastUsed = new Date();
      keyInfo.usageCount++;

      return keyInfo;
    } catch (error) {
      logger.error('API key verification failed', { error });
      return null;
    }
  }

  /**
   * レート制限のチェック
   */
  checkRateLimit(identifier: string): { allowed: boolean; remainingRequests: number; resetTime: number } {
    const now = Date.now();
    const rateLimitInfo = this.rateLimitMap.get(identifier);

    if (!rateLimitInfo || now > rateLimitInfo.resetTime) {
      // 新しいウィンドウまたは期限切れ
      const newRateLimitInfo: RateLimitInfo = {
        count: 1,
        resetTime: now + this.config.rateLimitWindow,
        isBlocked: false,
      };
      this.rateLimitMap.set(identifier, newRateLimitInfo);
      
      return {
        allowed: true,
        remainingRequests: this.config.rateLimitRequests - 1,
        resetTime: newRateLimitInfo.resetTime,
      };
    }

    if (rateLimitInfo.count >= this.config.rateLimitRequests) {
      rateLimitInfo.isBlocked = true;
      logger.warn('Rate limit exceeded', { identifier, count: rateLimitInfo.count });
      
      return {
        allowed: false,
        remainingRequests: 0,
        resetTime: rateLimitInfo.resetTime,
      };
    }

    rateLimitInfo.count++;
    
    return {
      allowed: true,
      remainingRequests: this.config.rateLimitRequests - rateLimitInfo.count,
      resetTime: rateLimitInfo.resetTime,
    };
  }

  /**
   * 失敗した認証試行の記録
   */
  recordFailedAttempt(identifier: string): { isLocked: boolean; lockedUntil?: number } {
    const now = Date.now();
    const attempts = this.failedAttempts.get(identifier) || { count: 0 };

    // ロックアウト期間が過ぎている場合はリセット
    if (attempts.lockedUntil && now > attempts.lockedUntil) {
      attempts.count = 0;
      delete attempts.lockedUntil;
    }

    attempts.count++;

    if (attempts.count >= this.config.maxFailedAttempts) {
      attempts.lockedUntil = now + this.config.lockoutDurationMs;
      logger.warn('Account locked due to repeated failed attempts', {
        identifier,
        attempts: attempts.count,
        lockedUntil: attempts.lockedUntil,
      });
    }

    this.failedAttempts.set(identifier, attempts);

    return {
      isLocked: attempts.count >= this.config.maxFailedAttempts,
      ...(attempts.lockedUntil !== undefined && { lockedUntil: attempts.lockedUntil })
    };
  }

  /**
   * 成功した認証試行の記録
   */
  recordSuccessfulAttempt(identifier: string): void {
    this.failedAttempts.delete(identifier);
    logger.debug('Successful authentication recorded', { identifier });
  }

  /**
   * アカウントがロックされているかチェック
   */
  isAccountLocked(identifier: string): { isLocked: boolean; lockedUntil?: number } {
    const now = Date.now();
    const attempts = this.failedAttempts.get(identifier);

    if (!attempts || !attempts.lockedUntil) {
      return { isLocked: false };
    }

    if (now > attempts.lockedUntil) {
      // ロックアウト期間が過ぎた場合はクリア
      this.failedAttempts.delete(identifier);
      return { isLocked: false };
    }

    return { isLocked: true, lockedUntil: attempts.lockedUntil };
  }

  /**
   * 権限のチェック
   */
  hasPermission(userPermissions: string[], requiredPermission: string): boolean {
    return userPermissions.includes('admin') || userPermissions.includes(requiredPermission);
  }

  /**
   * セキュリティ統計の取得
   */
  getSecurityStats(): {
    totalApiKeys: number;
    activeApiKeys: number;
    rateLimitedClients: number;
    lockedAccounts: number;
  } {
    const activeApiKeys = Array.from(this.apiKeys.values()).filter(key => 
      key.isActive && (!key.expiresAt || key.expiresAt > new Date())
    ).length;

    const rateLimitedClients = Array.from(this.rateLimitMap.values()).filter(rl => 
      rl.isBlocked && Date.now() < rl.resetTime
    ).length;

    const lockedAccounts = Array.from(this.failedAttempts.values()).filter(attempt => 
      attempt.lockedUntil && Date.now() < attempt.lockedUntil
    ).length;

    return {
      totalApiKeys: this.apiKeys.size,
      activeApiKeys,
      rateLimitedClients,
      lockedAccounts,
    };
  }

  /**
   * JWT有効期限の解析
   */
  private parseJwtExpiresIn(expiresIn: string): number {
    const match = expiresIn.match(/^(\d+)([smhd])$/);
    if (!match) {
      return 3600; // デフォルト: 1時間
    }

    const amount = match[1];
    const unit = match[2];
    const value = parseInt(amount || '0', 10);

    switch (unit) {
      case 's': return value;
      case 'm': return value * 60;
      case 'h': return value * 3600;
      case 'd': return value * 86400;
      default: return 3600;
    }
  }
}

// デフォルトインスタンス
export const securityManager = new SecurityManager();