/**
 * セキュリティミドルウェア
 * MCP サーバーとの統合用のミドルウェア関数
 */

import { createDefaultSecurityContext, SecurityEventType } from './index.js';
import type { JWTPayload, AuthResult } from './index.js';

/**
 * セキュリティコンテキスト
 */
export interface SecurityContext {
  userId?: string;
  username?: string;
  role?: string;
  permissions?: string[];
  ipAddress?: string;
  userAgent?: string;
}

/**
 * リクエストコンテキスト
 */
export interface RequestContext {
  toolName?: string;
  arguments?: unknown;
  clientInfo?: {
    ipAddress?: string;
    userAgent?: string;
  };
}

/**
 * セキュリティミドルウェアクラス
 */
export class SecurityMiddleware {
  private securityContext: any;

  constructor() {
    this.securityContext = createDefaultSecurityContext();
  }

  /**
   * 認証ミドルウェア
   */
  async authenticate(authHeader: string): Promise<{ success: boolean; context?: SecurityContext; message?: string }> {
    try {
      if (!authHeader) {
        this.securityContext.logEvent(SecurityEventType.AUTH_FAILURE, false, {
          reason: 'missing_auth_header'
        });
        return { success: false, message: '認証情報が提供されていません' };
      }

      let authResult: AuthResult;

      // Bearer トークン認証
      if (authHeader.startsWith('Bearer ')) {
        const token = authHeader.substring(7);
        authResult = this.securityContext.authenticate({ type: 'token', token });
      }
      // API キー認証
      else if (authHeader.startsWith('ApiKey ')) {
        const apiKey = authHeader.substring(7);
        authResult = this.securityContext.authenticate({ type: 'apikey', key: apiKey });
      }
      // Basic認証（ユーザー名/パスワード）
      else if (authHeader.startsWith('Basic ')) {
        const base64Credentials = authHeader.substring(6);
        const credentials = Buffer.from(base64Credentials, 'base64').toString('ascii');
        const [username, password] = credentials.split(':');
        authResult = await this.securityContext.authenticate({ type: 'password', username, password });
      }
      else {
        this.securityContext.logEvent(SecurityEventType.AUTH_FAILURE, false, {
          reason: 'invalid_auth_type'
        });
        return { success: false, message: 'サポートされていない認証形式です' };
      }

      if (!authResult.success) {
        this.securityContext.logEvent(SecurityEventType.AUTH_FAILURE, false, {
          reason: authResult.message
        });
        return { success: false, message: authResult.message || '認証に失敗しました' };
      }

      const payload = authResult.payload as JWTPayload;
      const context: SecurityContext = {
        userId: payload.userId,
        username: payload.username,
        role: payload.role,
        permissions: payload.permissions,
      };

      this.securityContext.logEvent(SecurityEventType.AUTH_SUCCESS, true, {
        userId: payload.userId,
        username: payload.username,
        role: payload.role
      });

      return { success: true, context };

    } catch (error) {
      this.securityContext.logEvent(SecurityEventType.AUTH_FAILURE, false, {
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      return { success: false, message: '認証中にエラーが発生しました' };
    }
  }

  /**
   * 認可ミドルウェア
   */
  async authorize(
    securityContext: SecurityContext, 
    requiredPermissions: string[],
    requestContext?: RequestContext
  ): Promise<{ authorized: boolean; message?: string }> {
    try {
      if (!securityContext.permissions) {
        this.securityContext.logEvent(SecurityEventType.PERMISSION_DENIED, false, {
          userId: securityContext.userId,
          requiredPermissions,
          reason: 'no_permissions'
        });
        return { authorized: false, message: '権限情報が不足しています' };
      }

      const payload = securityContext as any;
      const authResult = this.securityContext.authorize(payload, requiredPermissions);

      if (!authResult.authorized) {
        this.securityContext.logEvent(SecurityEventType.PERMISSION_DENIED, false, {
          userId: securityContext.userId,
          username: securityContext.username,
          requiredPermissions,
          userPermissions: securityContext.permissions,
          resource: requestContext?.toolName
        });
        return { authorized: false, message: authResult.message };
      }

      // 監査ログ記録
      if (requestContext?.toolName) {
        this.securityContext.logAudit(
          securityContext.userId || '',
          securityContext.username || '',
          'TOOL_ACCESS',
          requestContext.toolName,
          {
            arguments: requestContext.arguments,
            ipAddress: securityContext.ipAddress,
            userAgent: securityContext.userAgent
          }
        );
      }

      return { authorized: true };

    } catch (error) {
      this.securityContext.logEvent(SecurityEventType.PERMISSION_DENIED, false, {
        userId: securityContext.userId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      return { authorized: false, message: '認可チェック中にエラーが発生しました' };
    }
  }

  /**
   * レート制限ミドルウェア
   */
  async checkRateLimit(identifier: string): Promise<{ allowed: boolean; message?: string }> {
    try {
      const rateLimitResult = this.securityContext.checkRateLimit(identifier);
      
      if (!rateLimitResult.allowed) {
        this.securityContext.logEvent(SecurityEventType.RATE_LIMIT_EXCEEDED, false, {
          identifier,
          resetTime: rateLimitResult.resetTime
        });
        return { 
          allowed: false, 
          message: `レート制限に達しました。${new Date(rateLimitResult.resetTime).toISOString()} 後に再試行してください。`
        };
      }

      return { allowed: true };

    } catch (error) {
      return { allowed: false, message: 'レート制限チェック中にエラーが発生しました' };
    }
  }

  /**
   * セキュリティログ記録
   */
  logSecurityEvent(
    eventType: SecurityEventType,
    success: boolean,
    context: SecurityContext,
    details?: Record<string, unknown>
  ): void {
    this.securityContext.logEvent(eventType, success, {
      userId: context.userId,
      username: context.username,
      ipAddress: context.ipAddress,
      userAgent: context.userAgent,
      details
    });
  }

  /**
   * セキュリティ統計取得
   */
  getSecurityStats(): any {
    return this.securityContext.securityManager.getSecurityStats();
  }

  /**
   * セキュリティレポート生成
   */
  generateSecurityReport(): any {
    return this.securityContext.logger.generateSecurityReport();
  }
}

// デフォルトインスタンス
export const securityMiddleware = new SecurityMiddleware();