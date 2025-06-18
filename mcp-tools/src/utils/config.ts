import * as fs from 'fs';
import * as path from 'path';
import { ServerConfigSchema, type ServerConfig, type RuntimeConfig } from '../types/config';

export class ConfigManager {
  private static instance: ConfigManager;
  private config: RuntimeConfig | null = null;

  private constructor() {}

  public static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  public loadConfig(environment?: string): RuntimeConfig {
    const env = environment || process.env.NODE_ENV || 'development';
    const configPath = this.getConfigPath(env);

    try {
      const rawConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      const parsedConfig = ServerConfigSchema.parse(rawConfig);

      // Override with environment variables
      const config: RuntimeConfig = {
        ...parsedConfig,
        environment: env as 'development' | 'production' | 'test',
        startTime: new Date(),
        backend: {
          ...parsedConfig.backend,
          baseUrl: process.env.BACKEND_URL || parsedConfig.backend.baseUrl,
          timeout: process.env.BACKEND_TIMEOUT 
            ? parseInt(process.env.BACKEND_TIMEOUT, 10) 
            : parsedConfig.backend.timeout,
        },
        logging: {
          ...parsedConfig.logging,
          level: (process.env.LOG_LEVEL as any) || parsedConfig.logging.level,
        },
        debug: process.env.DEBUG === 'true' || parsedConfig.debug,
      };

      this.config = config;
      return config;
    } catch (error) {
      throw new Error(`Failed to load configuration from ${configPath}: ${error}`);
    }
  }

  public getConfig(): RuntimeConfig {
    if (!this.config) {
      return this.loadConfig();
    }
    return this.config;
  }

  public updateConfig(updates: Partial<ServerConfig>): void {
    if (!this.config) {
      throw new Error('Configuration not loaded. Call loadConfig() first.');
    }

    this.config = {
      ...this.config,
      ...updates,
    };
  }

  private getConfigPath(environment: string): string {
    const configDir = path.join(__dirname, '../../config');
    const configFile = `${environment}.json`;
    const configPath = path.join(configDir, configFile);

    if (!fs.existsSync(configPath)) {
      throw new Error(`Configuration file not found: ${configPath}`);
    }

    return configPath;
  }

  public validateConfig(config: unknown): ServerConfig {
    return ServerConfigSchema.parse(config);
  }

  public getBackendUrl(): string {
    return this.getConfig().backend.baseUrl;
  }

  public getLogLevel(): string {
    return this.getConfig().logging.level;
  }

  public isDebugMode(): boolean {
    return this.getConfig().debug;
  }

  public getPerformanceTarget(): number {
    return this.getConfig().performance.targetResponseTime;
  }

  public isWebSocketEnabled(): boolean {
    return this.getConfig().websocket.enabled;
  }

  public getEnvironment(): string {
    return this.getConfig().environment;
  }
}