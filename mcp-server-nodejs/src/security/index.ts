/**
 * セキュリティモジュール
 * 認証、認可、API キー管理、バリデーション、セキュリティログを提供
 */

// セキュリティマネージャー
export {
  SecurityManager,
  securityManager,
  type SecurityConfig,
  type UserCredentials,
  type JWTPayload,
  type ApiKeyInfo,
  SecurityConfigSchema,
  UserCredentialsSchema,
  JWTPayloadSchema,
  ApiKeyInfoSchema,
} from './security_manager.js';

// 認証・認可マネージャー
export {
  AuthManager,
  type AuthResult,
  type AuthorizationResult,
} from './auth_manager.js';

// 内部用インポート
import { SecurityManager } from './security_manager.js';
import { AuthManager } from './auth_manager.js';
import { SecurityLogger } from './security_logger.js';

// バリデーション
export {
  Validators,
  PresetValidators,
  CommonSecuritySchemas,
  AuthValidationSchemas,
  ApiKeyValidationSchemas,
  DroneControlValidationSchemas,
  SystemValidationSchemas,
  createValidationMiddleware,
  type ValidationResult,
  type ValidationErrorDetail,
} from './validators.js';

// セキュリティログ
export {
  SecurityLogger,
  securityLogger,
  SecurityEventType,
  type SecurityLogEntry,
  type SecurityAuditEntry,
  type SecurityMetrics,
} from './security_logger.js';

// セキュリティミドルウェア
export {
  SecurityMiddleware,
  securityMiddleware,
  type SecurityContext,
  type RequestContext,
} from './middleware.js';

// セキュリティミドルウェア用の汎用関数
export function createSecurityContext(
  secManager: any,
  authManager: any,
  logger: any
) {
  return {
    securityManager: secManager,
    authManager,
    logger,
    
    // 認証チェック
    async authenticate(credentials: { type: 'password'; username: string; password: string } | 
                                 { type: 'apikey'; key: string } | 
                                 { type: 'token'; token: string }) {
      switch (credentials.type) {
        case 'password':
          return await authManager.authenticateUser(credentials.username, credentials.password);
        case 'apikey':
          return authManager.authenticateApiKey(credentials.key);
        case 'token':
          return authManager.authenticateToken(credentials.token);
        default:
          throw new Error('Unknown authentication type');
      }
    },

    // 認可チェック
    authorize(userPayload: any, requiredPermissions: string[]) {
      return authManager.authorize(userPayload, requiredPermissions);
    },

    // レート制限チェック
    checkRateLimit(identifier: string) {
      return secManager.checkRateLimit(identifier);
    },

    // セキュリティイベントログ
    logEvent(eventType: any, success: boolean, context: any = {}) {
      logger.logSecurityEvent(eventType, success, context);
    },

    // 監査ログ
    logAudit(userId: string, username: string, action: string, resource: string, context: any = {}) {
      logger.logAuditEvent(userId, username, action, resource, context);
    },
  };
}

// デフォルトセキュリティコンテキストを作成するヘルパー関数
export function createDefaultSecurityContext() {
  const secManager = new SecurityManager();
  const authManager = new AuthManager(secManager);
  const logger = new SecurityLogger();
  
  return createSecurityContext(secManager, authManager, logger);
}