import { z } from 'zod';

// Configuration types
export const ConfigSchema = z.object({
  port: z.number().default(3001),
  backendUrl: z.string().default('http://localhost:8000'),
  logLevel: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  timeout: z.number().default(10000),
});

export type Config = z.infer<typeof ConfigSchema>;

// Drone status types
export const DroneStatusSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.enum(['connected', 'disconnected', 'flying', 'idle', 'error']),
  batteryLevel: z.number().min(0).max(100),
  position: z.object({
    x: z.number(),
    y: z.number(),
    z: z.number(),
  }).optional(),
  lastSeen: z.string().datetime(),
});

export type DroneStatus = z.infer<typeof DroneStatusSchema>;

// System status types
export const SystemStatusSchema = z.object({
  status: z.enum(['healthy', 'degraded', 'critical']),
  timestamp: z.string().datetime(),
  services: z.record(z.object({
    status: z.enum(['up', 'down', 'degraded']),
    lastCheck: z.string().datetime(),
    message: z.string().optional(),
  })),
  drones: z.array(DroneStatusSchema),
});

export type SystemStatus = z.infer<typeof SystemStatusSchema>;

// MCP tool request/response types
export const MCPToolRequestSchema = z.object({
  name: z.string(),
  arguments: z.record(z.unknown()).optional(),
});

export type MCPToolRequest = z.infer<typeof MCPToolRequestSchema>;

export const MCPToolResponseSchema = z.object({
  content: z.array(z.object({
    type: z.literal('text'),
    text: z.string(),
  })),
  isError: z.boolean().optional(),
});

export type MCPToolResponse = z.infer<typeof MCPToolResponseSchema>;

// Error types with enhanced error handling
export interface ErrorContext {
  timestamp: Date;
  requestId?: string;
  userId?: string;
  operation?: string;
  metadata?: Record<string, any>;
  stackTrace?: string;
  correlationId?: string;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    requestId?: string;
    correlationId?: string;
  };
  success: false;
}

export abstract class BaseError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly context: ErrorContext;
  public readonly retryable: boolean;
  public readonly userMessage: string;

  constructor(
    message: string,
    code: string,
    statusCode: number = 500,
    userMessage?: string,
    retryable: boolean = false,
    context?: Partial<ErrorContext>
  ) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
    this.retryable = retryable;
    this.userMessage = userMessage || message;
    this.context = {
      timestamp: new Date(),
      stackTrace: this.stack,
      ...context,
    };

    // Ensure proper prototype chain
    Object.setPrototypeOf(this, new.target.prototype);
  }

  public toJSON(): ErrorResponse {
    return {
      error: {
        code: this.code,
        message: this.userMessage,
        details: this.getDetails(),
        timestamp: this.context.timestamp.toISOString(),
        requestId: this.context.requestId,
        correlationId: this.context.correlationId,
      },
      success: false,
    };
  }

  public toLogFormat(): Record<string, any> {
    return {
      error: this.message,
      code: this.code,
      statusCode: this.statusCode,
      retryable: this.retryable,
      context: this.context,
    };
  }

  protected abstract getDetails(): any;
}

export class DroneError extends BaseError {
  constructor(
    message: string,
    code: string = 'DRONE_ERROR',
    statusCode: number = 500,
    userMessage?: string,
    public droneId?: string,
    public droneStatus?: string,
    context?: Partial<ErrorContext>
  ) {
    super(
      message, 
      code, 
      statusCode, 
      userMessage, 
      true, // Drone errors are usually retryable
      { ...context, metadata: { droneId, droneStatus, ...context?.metadata } }
    );
  }

  protected getDetails(): any {
    return {
      droneId: this.droneId,
      droneStatus: this.droneStatus,
    };
  }
}

export class ValidationError extends BaseError {
  constructor(
    message: string,
    public validationDetails?: unknown,
    userMessage?: string,
    context?: Partial<ErrorContext>
  ) {
    super(
      message, 
      'VALIDATION_ERROR', 
      400, 
      userMessage || '入力データが正しくありません', 
      false, 
      context
    );
    this.validationDetails = validationDetails;
  }

  protected getDetails(): any {
    return {
      validationDetails: this.validationDetails,
    };
  }
}

export class NetworkError extends BaseError {
  constructor(
    message: string,
    statusCode?: number,
    userMessage?: string,
    public endpoint?: string,
    public method?: string,
    context?: Partial<ErrorContext>
  ) {
    super(
      message,
      'NETWORK_ERROR',
      statusCode || 500,
      userMessage || 'ネットワークエラーが発生しました',
      true, // Network errors are usually retryable
      { ...context, metadata: { endpoint, method, ...context?.metadata } }
    );
  }

  protected getDetails(): any {
    return {
      endpoint: this.endpoint,
      method: this.method,
      statusCode: this.statusCode,
    };
  }
}

export class AuthenticationError extends BaseError {
  constructor(
    message: string,
    userMessage?: string,
    public authMethod?: string,
    context?: Partial<ErrorContext>
  ) {
    super(
      message,
      'AUTHENTICATION_ERROR',
      401,
      userMessage || '認証に失敗しました',
      false,
      { ...context, metadata: { authMethod, ...context?.metadata } }
    );
  }

  protected getDetails(): any {
    return {
      authMethod: this.authMethod,
    };
  }
}

export class AuthorizationError extends BaseError {
  constructor(
    message: string,
    userMessage?: string,
    public requiredPermission?: string,
    public userRole?: string,
    context?: Partial<ErrorContext>
  ) {
    super(
      message,
      'AUTHORIZATION_ERROR',
      403,
      userMessage || 'この操作を実行する権限がありません',
      false,
      { ...context, metadata: { requiredPermission, userRole, ...context?.metadata } }
    );
  }

  protected getDetails(): any {
    return {
      requiredPermission: this.requiredPermission,
      userRole: this.userRole,
    };
  }
}

export class ConfigurationError extends BaseError {
  constructor(
    message: string,
    userMessage?: string,
    public configKey?: string,
    public expectedType?: string,
    context?: Partial<ErrorContext>
  ) {
    super(
      message,
      'CONFIGURATION_ERROR',
      500,
      userMessage || '設定エラーが発生しました',
      false,
      { ...context, metadata: { configKey, expectedType, ...context?.metadata } }
    );
  }

  protected getDetails(): any {
    return {
      configKey: this.configKey,
      expectedType: this.expectedType,
    };
  }
}

export class TimeoutError extends BaseError {
  constructor(
    message: string,
    public timeoutMs: number,
    userMessage?: string,
    public operation?: string,
    context?: Partial<ErrorContext>
  ) {
    super(
      message,
      'TIMEOUT_ERROR',
      408,
      userMessage || 'タイムアウトしました',
      true,
      { ...context, metadata: { timeoutMs, operation, ...context?.metadata } }
    );
  }

  protected getDetails(): any {
    return {
      timeoutMs: this.timeoutMs,
      operation: this.operation,
    };
  }
}

export class RateLimitError extends BaseError {
  constructor(
    message: string,
    public limit: number,
    public windowMs: number,
    public retryAfterMs?: number,
    userMessage?: string,
    context?: Partial<ErrorContext>
  ) {
    super(
      message,
      'RATE_LIMIT_ERROR',
      429,
      userMessage || 'リクエストが多すぎます。しばらくお待ちください',
      true,
      { ...context, metadata: { limit, windowMs, retryAfterMs, ...context?.metadata } }
    );
  }

  protected getDetails(): any {
    return {
      limit: this.limit,
      windowMs: this.windowMs,
      retryAfterMs: this.retryAfterMs,
    };
  }
}

export class BusinessLogicError extends BaseError {
  constructor(
    message: string,
    code: string,
    userMessage?: string,
    public businessContext?: Record<string, any>,
    context?: Partial<ErrorContext>
  ) {
    super(
      message,
      code,
      422,
      userMessage || '処理を完了できませんでした',
      false,
      { ...context, metadata: { businessContext, ...context?.metadata } }
    );
  }

  protected getDetails(): any {
    return {
      businessContext: this.businessContext,
    };
  }
}

// Error type guards
export function isDroneError(error: Error): error is DroneError {
  return error instanceof DroneError;
}

export function isValidationError(error: Error): error is ValidationError {
  return error instanceof ValidationError;
}

export function isNetworkError(error: Error): error is NetworkError {
  return error instanceof NetworkError;
}

export function isAuthenticationError(error: Error): error is AuthenticationError {
  return error instanceof AuthenticationError;
}

export function isAuthorizationError(error: Error): error is AuthorizationError {
  return error instanceof AuthorizationError;
}

export function isRetryableError(error: Error): boolean {
  return error instanceof BaseError && error.retryable;
}

export function isClientError(error: Error): boolean {
  return error instanceof BaseError && error.statusCode >= 400 && error.statusCode < 500;
}

export function isServerError(error: Error): boolean {
  return error instanceof BaseError && error.statusCode >= 500;
}

// Error factory functions
export function createDroneError(message: string, droneId?: string): DroneError {
  return new DroneError(message, 'DRONE_ERROR', 500, undefined, droneId);
}

export function createValidationError(message: string, details?: unknown): ValidationError {
  return new ValidationError(message, details);
}

export function createNetworkError(message: string, endpoint?: string, method?: string): NetworkError {
  return new NetworkError(message, 500, undefined, endpoint, method);
}

export function createTimeoutError(operation: string, timeoutMs: number): TimeoutError {
  return new TimeoutError(
    `Operation '${operation}' timed out after ${timeoutMs}ms`,
    timeoutMs,
    undefined,
    operation
  );
}