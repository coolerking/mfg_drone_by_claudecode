import fs from 'fs';
import path from 'path';
import { z } from 'zod';
import { EventEmitter } from 'events';
import { logger } from '@/utils/logger.js';
import { ValidationError } from '@/types/index.js';
import { config as baseConfig } from './index.js';

/**
 * 高度な設定管理システム
 * - 動的設定の読み込み・保存
 * - 設定変更の監視と通知
 * - 環境別設定のオーバーライド
 * - ホットリロード機能
 */

// 拡張設定スキーマ
export const ExtendedConfigSchema = z.object({
  // 基本設定
  port: z.number().min(1).max(65535).default(3001),
  backendUrl: z.string().url().default('http://localhost:8000'),
  logLevel: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  timeout: z.number().min(1000).max(60000).default(10000),
  
  // MCP固有設定
  mcp: z.object({
    maxConnections: z.number().min(1).max(1000).default(100),
    heartbeatInterval: z.number().min(1000).max(30000).default(30000),
    retryAttempts: z.number().min(0).max(10).default(3),
    retryDelay: z.number().min(1000).max(10000).default(2000),
  }).default({}),
  
  // ドローン設定
  drone: z.object({
    maxDrones: z.number().min(1).max(50).default(5),
    commandTimeout: z.number().min(1000).max(30000).default(10000),
    batteryWarningLevel: z.number().min(0).max(100).default(20),
    autoLandOnLowBattery: z.boolean().default(true),
  }).default({}),
  
  // セキュリティ設定
  security: z.object({
    enableAuthentication: z.boolean().default(true),
    jwtSecret: z.string().optional(),
    tokenExpiration: z.string().default('1h'),
    rateLimitRequests: z.number().min(1).max(10000).default(100),
    rateLimitWindow: z.number().min(1000).max(3600000).default(60000), // 1 minute
  }).default({}),
  
  // ロギング設定
  logging: z.object({
    enableFileLogging: z.boolean().default(true),
    maxLogFiles: z.number().min(1).max(100).default(10),
    maxLogSize: z.string().default('10MB'),
    logDirectory: z.string().default('./logs'),
  }).default({}),
  
  // パフォーマンス設定
  performance: z.object({
    enableMetrics: z.boolean().default(true),
    metricsInterval: z.number().min(1000).max(300000).default(30000), // 30 seconds
    enableCaching: z.boolean().default(true),
    cacheTimeout: z.number().min(1000).max(3600000).default(300000), // 5 minutes
  }).default({}),
});

export type ExtendedConfig = z.infer<typeof ExtendedConfigSchema>;

/**
 * 設定管理クラス
 */
class SettingsManager extends EventEmitter {
  private config: ExtendedConfig;
  private configPath: string;
  private watchers: Map<string, fs.FSWatcher> = new Map();
  private _isLoaded = false;

  constructor(configPath?: string) {
    super();
    this.configPath = configPath || path.join(process.cwd(), 'config.json');
    this.config = this.getDefaultConfig();
  }

  /**
   * デフォルト設定を取得
   */
  private getDefaultConfig(): ExtendedConfig {
    try {
      // 基本設定から値を継承
      const defaultConfig = ExtendedConfigSchema.parse({
        port: baseConfig.port,
        backendUrl: baseConfig.backendUrl,
        logLevel: baseConfig.logLevel,
        timeout: baseConfig.timeout,
      });
      return defaultConfig;
    } catch (error) {
      logger.warn('デフォルト設定の適用中にエラーが発生しました', { error });
      return ExtendedConfigSchema.parse({});
    }
  }

  /**
   * 設定を初期化・読み込み
   */
  async initialize(): Promise<void> {
    try {
      await this.loadConfiguration();
      this.setupConfigWatcher();
      this._isLoaded = true;
      this.emit('initialized', this.config);
      logger.info('設定管理システムが初期化されました', { 
        configPath: this.configPath,
        config: this.getSafeConfig()
      });
    } catch (error) {
      logger.error('設定初期化エラー', { error });
      throw new ValidationError('Failed to initialize settings', error);
    }
  }

  /**
   * 設定ファイルを読み込み
   */
  private async loadConfiguration(): Promise<void> {
    if (!fs.existsSync(this.configPath)) {
      logger.info('設定ファイルが存在しません。デフォルト設定を作成します', { path: this.configPath });
      await this.saveConfiguration();
      return;
    }

    try {
      const configData = JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
      this.config = ExtendedConfigSchema.parse(configData);
      logger.info('設定ファイルを読み込みました', { path: this.configPath });
    } catch (error) {
      logger.error('設定ファイル読み込みエラー', { error, path: this.configPath });
      throw new ValidationError('Failed to load configuration', error);
    }
  }

  /**
   * 設定ファイルを保存
   */
  private async saveConfiguration(): Promise<void> {
    try {
      const configDir = path.dirname(this.configPath);
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }

      fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
      logger.debug('設定ファイルを保存しました', { path: this.configPath });
    } catch (error) {
      logger.error('設定ファイル保存エラー', { error, path: this.configPath });
      throw new Error('Failed to save configuration');
    }
  }

  /**
   * 設定ファイル変更監視を設定
   */
  private setupConfigWatcher(): void {
    if (this.watchers.has(this.configPath)) {
      return;
    }

    try {
      const watcher = fs.watch(this.configPath, { persistent: false }, async (eventType) => {
        if (eventType === 'change') {
          logger.info('設定ファイル変更を検出しました。リロードします...');
          await this.reloadConfiguration();
        }
      });

      this.watchers.set(this.configPath, watcher);
      logger.debug('設定ファイル監視を開始しました', { path: this.configPath });
    } catch (error) {
      logger.warn('設定ファイル監視の設定に失敗しました', { error, path: this.configPath });
    }
  }

  /**
   * 設定をリロード
   */
  async reloadConfiguration(): Promise<void> {
    try {
      const oldConfig = { ...this.config };
      await this.loadConfiguration();
      this.emit('configChanged', this.config, oldConfig);
      logger.info('設定が正常にリロードされました');
    } catch (error) {
      logger.error('設定リロードエラー', { error });
      this.emit('configError', error);
    }
  }

  /**
   * 設定値を取得
   */
  get<K extends keyof ExtendedConfig>(key: K): ExtendedConfig[K] {
    if (!this._isLoaded) {
      logger.warn('設定がまだ初期化されていません');
    }
    return this.config[key];
  }

  /**
   * 設定値を更新
   */
  async set<K extends keyof ExtendedConfig>(key: K, value: ExtendedConfig[K]): Promise<void> {
    const oldValue = this.config[key];
    this.config[key] = value;

    try {
      // 設定を検証
      ExtendedConfigSchema.parse(this.config);
      await this.saveConfiguration();
      this.emit('configUpdated', key, value, oldValue);
      logger.info('設定が更新されました', { key, value: this.sanitizeValue(key, value) });
    } catch (error) {
      // エラーが発生した場合は元の値に戻す
      this.config[key] = oldValue;
      logger.error('設定更新エラー', { error, key });
      throw new ValidationError('Failed to update configuration', error);
    }
  }

  /**
   * 複数の設定値を一括更新
   */
  async updateMultiple(updates: Partial<ExtendedConfig>): Promise<void> {
    const oldConfig = { ...this.config };
    
    try {
      // 新しい設定をマージ
      const newConfig = { ...this.config, ...updates };
      
      // 設定を検証
      const validatedConfig = ExtendedConfigSchema.parse(newConfig);
      this.config = validatedConfig;
      
      await this.saveConfiguration();
      this.emit('configUpdated', 'multiple', updates, oldConfig);
      logger.info('複数の設定が更新されました', { 
        keys: Object.keys(updates),
        values: this.sanitizeObject(updates)
      });
    } catch (error) {
      // エラーが発生した場合は元の設定に戻す
      this.config = oldConfig;
      logger.error('設定一括更新エラー', { error });
      throw new ValidationError('Failed to update multiple configurations', error);
    }
  }

  /**
   * 全設定を取得
   */
  getAll(): ExtendedConfig {
    return { ...this.config };
  }

  /**
   * 安全な設定取得（機密情報をマスク）
   */
  getSafeConfig(): Partial<ExtendedConfig> {
    const safeConfig = { ...this.config };
    if (safeConfig.security?.jwtSecret) {
      safeConfig.security.jwtSecret = '***';
    }
    return safeConfig;
  }

  /**
   * 設定をリセット
   */
  async reset(): Promise<void> {
    this.config = this.getDefaultConfig();
    await this.saveConfiguration();
    this.emit('configReset', this.config);
    logger.info('設定がデフォルト値にリセットされました');
  }

  /**
   * 環境変数から設定をオーバーライド
   */
  applyEnvironmentOverrides(): void {
    const overrides: Partial<ExtendedConfig> = {};

    // 環境変数のマッピング
    const envMapping = {
      MCP_PORT: 'port',
      BACKEND_URL: 'backendUrl',
      LOG_LEVEL: 'logLevel',
      TIMEOUT: 'timeout',
      JWT_SECRET: 'security.jwtSecret',
      MAX_CONNECTIONS: 'mcp.maxConnections',
      MAX_DRONES: 'drone.maxDrones',
      BATTERY_WARNING_LEVEL: 'drone.batteryWarningLevel',
    };

    for (const [envVar, configPath] of Object.entries(envMapping)) {
      const value = process.env[envVar];
      if (value !== undefined) {
        this.setNestedValue(overrides, configPath, this.parseEnvValue(value));
      }
    }

    if (Object.keys(overrides).length > 0) {
      Object.assign(this.config, overrides);
      logger.info('環境変数による設定オーバーライドを適用しました', { 
        overrides: this.sanitizeObject(overrides)
      });
    }
  }

  /**
   * ネストした設定値を設定
   */
  private setNestedValue(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    let current = obj;
    
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current)) {
        current[key] = {};
      }
      current = current[key];
    }
    
    current[keys[keys.length - 1]] = value;
  }

  /**
   * 環境変数値をパース
   */
  private parseEnvValue(value: string): any {
    // 数値
    if (/^\d+$/.test(value)) {
      return parseInt(value, 10);
    }
    
    // ブール値
    if (value.toLowerCase() === 'true') return true;
    if (value.toLowerCase() === 'false') return false;
    
    // 文字列
    return value;
  }

  /**
   * 機密情報をサニタイズ
   */
  private sanitizeValue(key: string, value: any): any {
    if (typeof key === 'string' && key.toLowerCase().includes('secret')) {
      return '***';
    }
    return value;
  }

  /**
   * オブジェクトの機密情報をサニタイズ
   */
  private sanitizeObject(obj: any): any {
    const sanitized = { ...obj };
    for (const [key, value] of Object.entries(sanitized)) {
      if (typeof key === 'string' && key.toLowerCase().includes('secret')) {
        sanitized[key] = '***';
      } else if (typeof value === 'object' && value !== null) {
        sanitized[key] = this.sanitizeObject(value);
      }
    }
    return sanitized;
  }

  /**
   * リソースのクリーンアップ
   */
  async cleanup(): Promise<void> {
    // ファイル監視を停止
    for (const [path, watcher] of this.watchers) {
      watcher.close();
      logger.debug('設定ファイル監視を停止しました', { path });
    }
    this.watchers.clear();

    // イベントリスナーを削除
    this.removeAllListeners();
    
    this._isLoaded = false;
    logger.info('設定管理システムがクリーンアップされました');
  }

  /**
   * 初期化状態を確認
   */
  get isLoaded(): boolean {
    return this._isLoaded;
  }
}

// シングルトンインスタンス
let settingsManager: SettingsManager | null = null;

/**
 * 設定管理シングルトンを取得
 */
export function getSettingsManager(configPath?: string): SettingsManager {
  if (!settingsManager) {
    settingsManager = new SettingsManager(configPath);
  }
  return settingsManager;
}

/**
 * 設定管理を初期化
 */
export async function initializeSettings(configPath?: string): Promise<SettingsManager> {
  const manager = getSettingsManager(configPath);
  if (!manager.isLoaded) {
    await manager.initialize();
    manager.applyEnvironmentOverrides();
  }
  return manager;
}

// デフォルトエクスポート
export default SettingsManager;