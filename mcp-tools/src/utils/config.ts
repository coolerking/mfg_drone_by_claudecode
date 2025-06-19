import * as fs from 'fs';
import * as path from 'path';
import { ServerConfig, MCPServerConfig, defaultConfig, defaultMCPConfig } from '../types/config.js';

export class ConfigManager {
  private config: MCPServerConfig;

  constructor(configPath?: string) {
    this.config = this.loadConfig(configPath);
  }

  private loadConfig(configPath?: string): MCPServerConfig {
    let fileConfig: Partial<MCPServerConfig> = {};

    // Load from file if path provided
    if (configPath && fs.existsSync(configPath)) {
      try {
        const fileContent = fs.readFileSync(configPath, 'utf-8');
        fileConfig = JSON.parse(fileContent);
      } catch (error) {
        console.warn(`Failed to load config from ${configPath}:`, error);
      }
    } else {
      // Try to load from default locations
      const defaultPaths = [
        path.join(process.cwd(), 'config', 'development.json'),
        path.join(process.cwd(), 'config', 'production.json'),
        path.join(process.cwd(), 'mcp-config.json')
      ];

      for (const defaultPath of defaultPaths) {
        if (fs.existsSync(defaultPath)) {
          try {
            const fileContent = fs.readFileSync(defaultPath, 'utf-8');
            fileConfig = JSON.parse(fileContent);
            break;
          } catch (error) {
            console.warn(`Failed to load config from ${defaultPath}:`, error);
          }
        }
      }
    }

    // Load from environment variables
    const envConfig: Partial<MCPServerConfig> = {};
    if (process.env.BACKEND_URL) envConfig.backendUrl = process.env.BACKEND_URL;
    if (process.env.TIMEOUT) envConfig.timeout = parseInt(process.env.TIMEOUT, 10);
    if (process.env.RETRIES) envConfig.retries = parseInt(process.env.RETRIES, 10);
    if (process.env.DEBUG) envConfig.debug = process.env.DEBUG === 'true';
    if (process.env.LOG_LEVEL) envConfig.logLevel = process.env.LOG_LEVEL as any;
    if (process.env.LOG_FILE) envConfig.logFile = process.env.LOG_FILE;
    if (process.env.TRANSPORT) envConfig.transport = process.env.TRANSPORT as any;
    if (process.env.PORT) envConfig.port = parseInt(process.env.PORT, 10);
    if (process.env.HOST) envConfig.host = process.env.HOST;

    // Merge configurations: default < file < environment
    return {
      ...defaultMCPConfig,
      ...fileConfig,
      ...envConfig
    };
  }

  public getConfig(): MCPServerConfig {
    return { ...this.config };
  }

  public updateConfig(updates: Partial<MCPServerConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  public validate(): void {
    const config = this.config;
    
    if (!config.backendUrl) {
      throw new Error('Backend URL is required');
    }

    if (config.timeout <= 0) {
      throw new Error('Timeout must be positive');
    }

    if (config.retries < 0) {
      throw new Error('Retries must be non-negative');
    }

    if (!['stdio', 'websocket', 'http'].includes(config.transport)) {
      throw new Error('Invalid transport type');
    }

    if ((config.transport === 'websocket' || config.transport === 'http') && !config.port) {
      throw new Error('Port is required for websocket/http transport');
    }
  }
}