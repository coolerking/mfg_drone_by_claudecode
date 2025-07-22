import { z } from 'zod';
import { logger } from '@/utils/logger.js';

/**
 * 共通のバリデーション関数とスキーマ
 */

// 基本的なセキュリティ関連のバリデーション
export const CommonSecuritySchemas = {
  // ユーザー名: 3-50文字、英数字とアンダースコア、ハイフンのみ
  username: z.string()
    .min(3, 'ユーザー名は3文字以上である必要があります')
    .max(50, 'ユーザー名は50文字以下である必要があります')
    .regex(/^[a-zA-Z0-9_-]+$/, 'ユーザー名は英数字、アンダースコア、ハイフンのみ使用できます'),

  // パスワード: 8文字以上、大文字小文字数字特殊文字を含む
  password: z.string()
    .min(8, 'パスワードは8文字以上である必要があります')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, 
      'パスワードは大文字、小文字、数字、特殊文字を含む必要があります'),

  // メールアドレス
  email: z.string().email('有効なメールアドレスを入力してください'),

  // API キー名
  apiKeyName: z.string()
    .min(1, 'APIキー名は必須です')
    .max(100, 'APIキー名は100文字以下である必要があります')
    .regex(/^[a-zA-Z0-9_-\s]+$/, 'APIキー名は英数字、アンダースコア、ハイフン、スペースのみ使用できます'),

  // 権限
  permission: z.enum([
    'drone:read',
    'drone:control',
    'drone:connect',
    'drone:emergency',
    'vision:read',
    'vision:process',
    'system:read',
    'system:write',
    'admin',
  ]),

  // UUID
  uuid: z.string().uuid('有効なUUIDを指定してください'),

  // IPアドレス
  ipAddress: z.string().ip('有効なIPアドレスを指定してください'),
};

/**
 * 認証関連のバリデーションスキーマ
 */
export const AuthValidationSchemas = {
  // ログインリクエスト
  login: z.object({
    username: CommonSecuritySchemas.username,
    password: z.string().min(1, 'パスワードは必須です'),
  }),

  // ユーザー登録リクエスト
  register: z.object({
    username: CommonSecuritySchemas.username,
    password: CommonSecuritySchemas.password,
    email: CommonSecuritySchemas.email.optional(),
    role: z.enum(['admin', 'user', 'readonly']).default('user'),
  }),

  // パスワード変更リクエスト
  changePassword: z.object({
    currentPassword: z.string().min(1, '現在のパスワードは必須です'),
    newPassword: CommonSecuritySchemas.password,
    confirmPassword: z.string().min(1, 'パスワード確認は必須です'),
  }).refine((data) => data.newPassword === data.confirmPassword, {
    message: '新しいパスワードと確認パスワードが一致しません',
    path: ['confirmPassword'],
  }),
};

/**
 * API キー関連のバリデーションスキーマ
 */
export const ApiKeyValidationSchemas = {
  // API キー作成リクエスト
  create: z.object({
    name: CommonSecuritySchemas.apiKeyName,
    permissions: z.array(CommonSecuritySchemas.permission)
      .min(1, '少なくとも1つの権限を指定してください')
      .max(10, '権限は最大10個まで指定できます'),
    expiresInDays: z.number()
      .int('有効期限は整数で指定してください')
      .min(1, '有効期限は1日以上である必要があります')
      .max(365, '有効期限は365日以下である必要があります')
      .optional(),
  }),

  // API キー更新リクエスト
  update: z.object({
    keyId: CommonSecuritySchemas.uuid,
    name: CommonSecuritySchemas.apiKeyName.optional(),
    permissions: z.array(CommonSecuritySchemas.permission)
      .min(1, '少なくとも1つの権限を指定してください')
      .max(10, '権限は最大10個まで指定できます')
      .optional(),
    isActive: z.boolean().optional(),
  }),

  // API キー削除リクエスト
  delete: z.object({
    keyId: CommonSecuritySchemas.uuid,
  }),
};

/**
 * ドローン制御関連のバリデーションスキーマ
 */
export const DroneControlValidationSchemas = {
  // ドローン接続リクエスト
  connect: z.object({
    droneId: z.string()
      .min(1, 'ドローンIDは必須です')
      .max(50, 'ドローンIDは50文字以下である必要があります')
      .regex(/^[a-zA-Z0-9_-]+$/, 'ドローンIDは英数字、アンダースコア、ハイフンのみ使用できます'),
    ipAddress: CommonSecuritySchemas.ipAddress.optional(),
  }),

  // ドローン移動コマンド
  move: z.object({
    droneId: z.string().min(1, 'ドローンIDは必須です'),
    direction: z.enum(['forward', 'backward', 'left', 'right', 'up', 'down']),
    distance: z.number()
      .int('距離は整数で指定してください')
      .min(20, '移動距離は20cm以上である必要があります')
      .max(500, '移動距離は500cm以下である必要があります'),
  }),

  // ドローン回転コマンド
  rotate: z.object({
    droneId: z.string().min(1, 'ドローンIDは必須です'),
    direction: z.enum(['cw', 'ccw']),
    degrees: z.number()
      .int('角度は整数で指定してください')
      .min(1, '回転角度は1度以上である必要があります')
      .max(360, '回転角度は360度以下である必要があります'),
  }),

  // 写真撮影コマンド
  takePhoto: z.object({
    droneId: z.string().min(1, 'ドローンIDは必須です'),
    filename: z.string()
      .min(1, 'ファイル名は必須です')
      .max(100, 'ファイル名は100文字以下である必要があります')
      .regex(/^[a-zA-Z0-9_-]+\.(jpg|jpeg|png)$/i, 'ファイル名は英数字、アンダースコア、ハイフンのみ使用でき、.jpg、.jpeg、.png拡張子である必要があります')
      .optional(),
  }),
};

/**
 * システム関連のバリデーションスキーマ
 */
export const SystemValidationSchemas = {
  // ログレベル設定
  setLogLevel: z.object({
    level: z.enum(['debug', 'info', 'warn', 'error']),
  }),

  // 設定更新
  updateConfig: z.object({
    key: z.string()
      .min(1, '設定キーは必須です')
      .max(100, '設定キーは100文字以下である必要があります')
      .regex(/^[a-zA-Z][a-zA-Z0-9_.]*$/, '設定キーは英字で始まり、英数字、アンダースコア、ドットのみ使用できます'),
    value: z.union([z.string(), z.number(), z.boolean()]),
  }),
};

/**
 * バリデーションエラー詳細
 */
export interface ValidationErrorDetail {
  field: string;
  message: string;
  code: string;
  received?: unknown;
}

/**
 * バリデーション結果
 */
export interface ValidationResult<T> {
  success: boolean;
  data?: T;
  errors?: ValidationErrorDetail[];
}

/**
 * 汎用バリデーション関数
 */
export class Validators {
  /**
   * スキーマに対してデータをバリデーション
   */
  static validate<T>(schema: z.ZodSchema<T>, data: unknown): ValidationResult<T> {
    try {
      const result = schema.parse(data);
      return {
        success: true,
        data: result,
      };
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors: ValidationErrorDetail[] = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message,
          code: err.code,
          received: (err as any).received,
        }));

        logger.warn('Validation failed', {
          errors,
          originalData: data,
        });

        return {
          success: false,
          errors,
        };
      }

      logger.error('Unexpected validation error', { error, data });
      return {
        success: false,
        errors: [
          {
            field: 'unknown',
            message: 'バリデーション中に予期しないエラーが発生しました',
            code: 'unexpected_error',
          },
        ],
      };
    }
  }

  /**
   * 複数のスキーマに対してデータをバリデーション（OR条件）
   */
  static validateAny<T>(schemas: z.ZodSchema<T>[], data: unknown): ValidationResult<T> {
    const allErrors: ValidationErrorDetail[] = [];

    for (const schema of schemas) {
      const result = this.validate(schema, data);
      if (result.success) {
        return result;
      }
      if (result.errors) {
        allErrors.push(...result.errors);
      }
    }

    return {
      success: false,
      errors: allErrors,
    };
  }

  /**
   * サニタイゼーション（危険な文字の除去）
   */
  static sanitizeString(input: string): string {
    return input
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // スクリプトタグを削除
      .replace(/[<>]/g, '') // HTML タグを削除
      .replace(/['"]/g, ''); // クォートを削除
  }

  /**
   * SQL インジェクション対策の基本チェック
   */
  static validateSafeSqlInput(input: string): boolean {
    const dangerousPatterns = [
      /(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)/gi,
      /(--|\/\*|\*\/)/,
      /[';]/,
    ];

    return !dangerousPatterns.some(pattern => pattern.test(input));
  }

  /**
   * XSS 対策の基本チェック
   */
  static validateSafeHtmlInput(input: string): boolean {
    const dangerousPatterns = [
      /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi, // onload, onclick などのイベントハンドラ
      /<iframe\b[^>]*>/gi,
      /<object\b[^>]*>/gi,
      /<embed\b[^>]*>/gi,
    ];

    return !dangerousPatterns.some(pattern => pattern.test(input));
  }

  /**
   * ファイルパス traversal 対策
   */
  static validateSafeFilePath(filePath: string): boolean {
    const dangerousPatterns = [
      /\.\./,  // ディレクトリトラバーサル
      /^\//, // 絶対パス
      /[\0\r\n]/, // null文字や改行文字
    ];

    return !dangerousPatterns.some(pattern => pattern.test(filePath)) &&
           filePath.length > 0 &&
           filePath.length < 256; // パス長制限
  }
}

/**
 * リクエストバリデーションミドルウェア用のヘルパー
 */
export function createValidationMiddleware<T>(schema: z.ZodSchema<T>) {
  return (data: unknown): T => {
    const result = Validators.validate(schema, data);
    if (!result.success) {
      const errorMessages = result.errors?.map(err => `${err.field}: ${err.message}`).join(', ') || '不明なバリデーションエラー';
      throw new Error(`バリデーションエラー: ${errorMessages}`);
    }
    return result.data!;
  };
}

// プリセットのバリデーター
export const PresetValidators = {
  // 認証関連
  validateLogin: createValidationMiddleware(AuthValidationSchemas.login),
  validateRegister: createValidationMiddleware(AuthValidationSchemas.register),
  validateChangePassword: createValidationMiddleware(AuthValidationSchemas.changePassword),

  // API キー関連
  validateApiKeyCreate: createValidationMiddleware(ApiKeyValidationSchemas.create),
  validateApiKeyUpdate: createValidationMiddleware(ApiKeyValidationSchemas.update),
  validateApiKeyDelete: createValidationMiddleware(ApiKeyValidationSchemas.delete),

  // ドローン制御関連
  validateDroneConnect: createValidationMiddleware(DroneControlValidationSchemas.connect),
  validateDroneMove: createValidationMiddleware(DroneControlValidationSchemas.move),
  validateDroneRotate: createValidationMiddleware(DroneControlValidationSchemas.rotate),
  validateTakePhoto: createValidationMiddleware(DroneControlValidationSchemas.takePhoto),

  // システム関連
  validateSetLogLevel: createValidationMiddleware(SystemValidationSchemas.setLogLevel),
  validateUpdateConfig: createValidationMiddleware(SystemValidationSchemas.updateConfig),
};