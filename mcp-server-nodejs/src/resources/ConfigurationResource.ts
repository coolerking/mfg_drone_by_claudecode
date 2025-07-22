import { BaseResource, type MCPResourceResponse } from './BaseResource.js';
import { logger } from '@/utils/logger.js';
import { type Config } from '@/types/index.js';

/**
 * 設定リソース
 * システム設定と機能情報を提供
 */
export class ConfigurationResource extends BaseResource {
  private config: Config;

  constructor(droneService: any, config: Config) {
    super(droneService, 'ConfigurationResource', 'mcp://configuration');
    this.config = config;
  }

  getDescription(): string {
    return 'System configuration, capabilities, and supported features of the MCP drone server.';
  }

  getUri(): string {
    return `${this.baseUri}/config`;
  }

  getMimeType(): string {
    return 'application/json';
  }

  async getContents(): Promise<MCPResourceResponse> {
    try {
      logger.debug('Retrieving configuration resource');

      // システム機能情報
      const capabilities = {
        tools: [
          'connect_drone',
          'takeoff_drone',
          'land_drone',
          'move_drone',
          'rotate_drone', 
          'take_photo',
          'execute_natural_language_command',
          'emergency_stop',
          'get_drone_status',
          'scan_drones',
          'health_check',
          'get_system_status',
        ],
        resources: [
          'drone_status',
          'system_logs',
          'configuration',
        ],
        supportedCommands: [
          'connect',
          'takeoff',
          'land',
          'move',
          'rotate',
          'take_photo',
          'emergency_stop',
        ],
        supportedLanguages: [
          'en',
          'ja',
        ],
        droneTypes: [
          'tello_edu',
          'simulation',
        ],
      };

      // 運用制限情報
      const limits = {
        movement: {
          maxDistance: 5.0, // meters
          minDistance: 0.2,
          maxSpeed: 3.0, // m/s
          minSpeed: 0.1,
        },
        rotation: {
          maxAngle: 360, // degrees
          minAngle: 10,
          maxSpeed: 100, // deg/s
          minSpeed: 10,
        },
        altitude: {
          max: 10.0, // meters
          min: 0.5,
          default: 1.2,
        },
        battery: {
          criticalLevel: 25, // percent
          lowLevel: 50,
          landingThreshold: 15,
        },
      };

      const resourceData = {
        timestamp: new Date().toISOString(),
        server: {
          name: 'MCP Drone Server',
          version: '1.0.0',
          protocol: 'MCP',
          language: 'TypeScript/Node.js',
        },
        configuration: {
          port: this.config.port,
          backendUrl: this.config.backendUrl,
          logLevel: this.config.logLevel,
          timeout: this.config.timeout,
        },
        capabilities,
        limits,
        apiEndpoints: {
          backend: this.config.backendUrl,
          health: `${this.config.backendUrl}/api/system/status`,
          drones: `${this.config.backendUrl}/api/drones`,
          commands: `${this.config.backendUrl}/api/drones/{id}/commands`,
        },
        documentation: {
          mcp: 'https://spec.modelcontextprotocol.io/',
          telloSdk: 'https://djitellopy.readthedocs.io/',
          project: 'https://github.com/coolerking/mfg_drone_by_claudecode',
        },
        supportInfo: {
          logLevel: this.config.logLevel,
          debugMode: this.config.logLevel === 'debug',
          healthCheckInterval: '30s',
          cacheTimeout: '30s',
        },
      };

      return this.createJsonResponse(resourceData);
    } catch (error) {
      logger.error('Error retrieving configuration resource:', error);
      return this.handleError(error);
    }
  }

  /**
   * 設定を更新（必要に応じて）
   */
  public updateConfig(newConfig: Partial<Config>): void {
    this.config = { ...this.config, ...newConfig };
    logger.info('Configuration updated', newConfig);
  }
}