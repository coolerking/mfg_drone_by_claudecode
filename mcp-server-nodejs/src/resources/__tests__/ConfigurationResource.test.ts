/**
 * Tests for ConfigurationResource
 * Test suite for configuration MCP resource
 */

import { ConfigurationResource } from '../ConfigurationResource.js';
import { DroneService } from '@/services/DroneService.js';
import { logger } from '@/utils/logger.js';
import type { Config } from '@/types/index.js';

// Mock dependencies
jest.mock('@/services/DroneService.js');
jest.mock('@/utils/logger.js');

const mockedLogger = jest.mocked(logger);

describe('ConfigurationResource', () => {
  let mockDroneService: jest.Mocked<DroneService>;
  let configurationResource: ConfigurationResource;
  
  const mockConfig: Config = {
    port: 3001,
    backendUrl: 'http://localhost:8000',
    logLevel: 'info',
    timeout: 10000,
    mcpPort: 3001,
    nlpConfidenceThreshold: 0.7,
  };

  beforeEach(() => {
    mockDroneService = new DroneService({} as any) as jest.Mocked<DroneService>;
    configurationResource = new ConfigurationResource(mockDroneService, mockConfig);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Properties', () => {
    test('should have correct description', () => {
      expect(configurationResource.getDescription()).toBe(
        'System configuration, capabilities, and supported features of the MCP drone server.'
      );
    });

    test('should have correct URI', () => {
      expect(configurationResource.getUri()).toBe('mcp://configuration/config');
    });

    test('should have correct MIME type', () => {
      expect(configurationResource.getMimeType()).toBe('application/json');
    });
  });

  describe('getContents Method', () => {
    test('should return comprehensive configuration data', async () => {
      const result = await configurationResource.getContents();

      expect(result.contents).toHaveLength(1);
      expect(result.contents[0].mimeType).toBe('application/json');
      expect(result.contents[0].uri).toBe('mcp://configuration/config');

      const data = JSON.parse(result.contents[0].text!);
      
      expect(data).toHaveProperty('timestamp');
      expect(data).toHaveProperty('server');
      expect(data).toHaveProperty('configuration');
      expect(data).toHaveProperty('capabilities');
      expect(data).toHaveProperty('limits');
      expect(data).toHaveProperty('apiEndpoints');
      expect(data).toHaveProperty('documentation');
      expect(data).toHaveProperty('supportInfo');
    });

    test('should include correct server information', async () => {
      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.server).toEqual({
        name: 'MCP Drone Server',
        version: '1.0.0',
        protocol: 'MCP',
        language: 'TypeScript/Node.js',
      });
    });

    test('should include current configuration settings', async () => {
      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.configuration).toEqual({
        port: mockConfig.port,
        backendUrl: mockConfig.backendUrl,
        logLevel: mockConfig.logLevel,
        timeout: mockConfig.timeout,
      });
    });

    test('should include comprehensive capabilities list', async () => {
      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.capabilities).toHaveProperty('tools');
      expect(data.capabilities).toHaveProperty('resources');
      expect(data.capabilities).toHaveProperty('supportedCommands');
      expect(data.capabilities).toHaveProperty('supportedLanguages');
      expect(data.capabilities).toHaveProperty('droneTypes');

      // Check tools
      const expectedTools = [
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
      ];
      expect(data.capabilities.tools).toEqual(expectedTools);

      // Check resources
      expect(data.capabilities.resources).toEqual([
        'drone_status',
        'system_logs',
        'configuration',
      ]);

      // Check supported commands
      expect(data.capabilities.supportedCommands).toEqual([
        'connect',
        'takeoff',
        'land',
        'move',
        'rotate',
        'take_photo',
        'emergency_stop',
      ]);

      // Check supported languages
      expect(data.capabilities.supportedLanguages).toEqual(['en', 'ja']);

      // Check drone types
      expect(data.capabilities.droneTypes).toEqual(['tello_edu', 'simulation']);
    });

    test('should include operational limits', async () => {
      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.limits).toHaveProperty('movement');
      expect(data.limits).toHaveProperty('rotation');
      expect(data.limits).toHaveProperty('altitude');
      expect(data.limits).toHaveProperty('battery');

      // Check movement limits
      expect(data.limits.movement).toEqual({
        maxDistance: 5.0,
        minDistance: 0.2,
        maxSpeed: 3.0,
        minSpeed: 0.1,
      });

      // Check rotation limits
      expect(data.limits.rotation).toEqual({
        maxAngle: 360,
        minAngle: 10,
        maxSpeed: 100,
        minSpeed: 10,
      });

      // Check altitude limits
      expect(data.limits.altitude).toEqual({
        max: 10.0,
        min: 0.5,
        default: 1.2,
      });

      // Check battery limits
      expect(data.limits.battery).toEqual({
        criticalLevel: 25,
        lowLevel: 50,
        landingThreshold: 15,
      });
    });

    test('should include API endpoints', async () => {
      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.apiEndpoints).toEqual({
        backend: mockConfig.backendUrl,
        health: `${mockConfig.backendUrl}/api/system/status`,
        drones: `${mockConfig.backendUrl}/api/drones`,
        commands: `${mockConfig.backendUrl}/api/drones/{id}/commands`,
      });
    });

    test('should include documentation links', async () => {
      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.documentation).toEqual({
        mcp: 'https://spec.modelcontextprotocol.io/',
        telloSdk: 'https://djitellopy.readthedocs.io/',
        project: 'https://github.com/coolerking/mfg_drone_by_claudecode',
      });
    });

    test('should include support information', async () => {
      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.supportInfo).toEqual({
        logLevel: mockConfig.logLevel,
        debugMode: false, // logLevel is 'info', not 'debug'
        healthCheckInterval: '30s',
        cacheTimeout: '30s',
      });
    });

    test('should set debugMode correctly for debug log level', async () => {
      const debugConfig: Config = { ...mockConfig, logLevel: 'debug' };
      const debugConfigResource = new ConfigurationResource(mockDroneService, debugConfig);

      const result = await debugConfigResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.supportInfo.debugMode).toBe(true);
      expect(data.supportInfo.logLevel).toBe('debug');
    });

    test('should log debug information', async () => {
      await configurationResource.getContents();

      expect(mockedLogger.debug).toHaveBeenCalledWith('Retrieving configuration resource');
    });

    test('should include valid timestamp', async () => {
      const before = new Date().toISOString();
      const result = await configurationResource.getContents();
      const after = new Date().toISOString();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.timestamp).toBeGreaterThanOrEqual(before);
      expect(data.timestamp).toBeLessThanOrEqual(after);
      expect(new Date(data.timestamp)).toBeInstanceOf(Date);
    });
  });

  describe('Configuration Updates', () => {
    test('should update configuration and log changes', () => {
      const updates: Partial<Config> = {
        logLevel: 'debug',
        timeout: 15000,
      };

      configurationResource.updateConfig(updates);

      expect(mockedLogger.info).toHaveBeenCalledWith('Configuration updated', updates);
    });

    test('should reflect updated configuration in response', async () => {
      const updates: Partial<Config> = {
        logLevel: 'debug',
        timeout: 15000,
        backendUrl: 'http://updated.example.com:8001',
      };

      configurationResource.updateConfig(updates);

      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.configuration.logLevel).toBe('debug');
      expect(data.configuration.timeout).toBe(15000);
      expect(data.configuration.backendUrl).toBe('http://updated.example.com:8001');
      expect(data.supportInfo.debugMode).toBe(true);
    });

    test('should preserve original config values for partial updates', async () => {
      const updates: Partial<Config> = {
        logLevel: 'warn',
      };

      configurationResource.updateConfig(updates);

      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.configuration.logLevel).toBe('warn');
      expect(data.configuration.port).toBe(mockConfig.port); // Preserved
      expect(data.configuration.backendUrl).toBe(mockConfig.backendUrl); // Preserved
      expect(data.configuration.timeout).toBe(mockConfig.timeout); // Preserved
    });

    test('should handle empty update objects', () => {
      const originalConfig = { ...mockConfig };
      configurationResource.updateConfig({});

      expect(mockedLogger.info).toHaveBeenCalledWith('Configuration updated', {});
      
      // Configuration should remain unchanged
      // Note: we can't directly access the private config, so we test through getContents
    });

    test('should update API endpoints when backend URL changes', async () => {
      const newBackendUrl = 'https://api.example.com:9000';
      configurationResource.updateConfig({ backendUrl: newBackendUrl });

      const result = await configurationResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.apiEndpoints).toEqual({
        backend: newBackendUrl,
        health: `${newBackendUrl}/api/system/status`,
        drones: `${newBackendUrl}/api/drones`,
        commands: `${newBackendUrl}/api/drones/{id}/commands`,
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle errors during content generation', async () => {
      // Create a resource that will throw an error during getContents
      const errorConfig = null as any; // This should cause an error when accessed
      const errorResource = new ConfigurationResource(mockDroneService, errorConfig);

      const result = await errorResource.getContents();

      expect(result.contents[0].mimeType).toBe('text/plain');
      expect(result.contents[0].text).toContain('Error retrieving ConfigurationResource');
      expect(mockedLogger.error).toHaveBeenCalledWith(
        'Error retrieving configuration resource:',
        expect.any(Error)
      );
    });

    test('should handle malformed config gracefully', async () => {
      const malformedConfig = {
        port: 'invalid', // Should be number
        backendUrl: null,  // Should be string
        logLevel: 'invalid-level',
        timeout: 'not-a-number',
      } as any;

      const malformedResource = new ConfigurationResource(mockDroneService, malformedConfig);

      // Should not throw during construction
      expect(malformedResource).toBeInstanceOf(ConfigurationResource);

      // May throw during content generation, which should be handled
      const result = await malformedResource.getContents();
      
      // Either succeeds with malformed data or fails gracefully
      expect(result).toHaveProperty('contents');
      expect(Array.isArray(result.contents)).toBe(true);
    });
  });

  describe('Response Content Structure', () => {
    test('should always return properly structured response', async () => {
      const result = await configurationResource.getContents();

      expect(result).toHaveProperty('contents');
      expect(Array.isArray(result.contents)).toBe(true);
      expect(result.contents).toHaveLength(1);

      const content = result.contents[0];
      expect(content).toHaveProperty('uri', 'mcp://configuration/config');
      expect(content).toHaveProperty('mimeType', 'application/json');
      expect(content).toHaveProperty('text');
      expect(typeof content.text).toBe('string');
    });

    test('should produce valid JSON in response text', async () => {
      const result = await configurationResource.getContents();
      
      expect(() => {
        JSON.parse(result.contents[0].text!);
      }).not.toThrow();
    });

    test('should format JSON with proper indentation', async () => {
      const result = await configurationResource.getContents();
      const text = result.contents[0].text!;
      
      // Should be formatted with 2-space indentation
      expect(text).toContain('  "timestamp"');
      expect(text).toContain('  "server"');
      expect(text).toContain('    "name"');
    });
  });

  describe('Configuration Value Types and Validation', () => {
    test('should handle different log levels correctly', async () => {
      const logLevels: Array<Config['logLevel']> = ['debug', 'info', 'warn', 'error'];

      for (const logLevel of logLevels) {
        const testConfig = { ...mockConfig, logLevel };
        const testResource = new ConfigurationResource(mockDroneService, testConfig);

        const result = await testResource.getContents();
        const data = JSON.parse(result.contents[0].text!);

        expect(data.configuration.logLevel).toBe(logLevel);
        expect(data.supportInfo.logLevel).toBe(logLevel);
        expect(data.supportInfo.debugMode).toBe(logLevel === 'debug');
      }
    });

    test('should handle various port numbers', async () => {
      const ports = [80, 443, 3000, 3001, 8080, 8443, 65535];

      for (const port of ports) {
        const testConfig = { ...mockConfig, port };
        const testResource = new ConfigurationResource(mockDroneService, testConfig);

        const result = await testResource.getContents();
        const data = JSON.parse(result.contents[0].text!);

        expect(data.configuration.port).toBe(port);
      }
    });

    test('should handle different backend URLs', async () => {
      const urls = [
        'http://localhost:8000',
        'https://api.example.com',
        'http://192.168.1.100:9000',
        'https://secure-api.domain.org:8443/path',
      ];

      for (const backendUrl of urls) {
        const testConfig = { ...mockConfig, backendUrl };
        const testResource = new ConfigurationResource(mockDroneService, testConfig);

        const result = await testResource.getContents();
        const data = JSON.parse(result.contents[0].text!);

        expect(data.configuration.backendUrl).toBe(backendUrl);
        expect(data.apiEndpoints.backend).toBe(backendUrl);
        expect(data.apiEndpoints.health).toBe(`${backendUrl}/api/system/status`);
      }
    });

    test('should handle different timeout values', async () => {
      const timeouts = [1000, 5000, 10000, 30000, 60000];

      for (const timeout of timeouts) {
        const testConfig = { ...mockConfig, timeout };
        const testResource = new ConfigurationResource(mockDroneService, testConfig);

        const result = await testResource.getContents();
        const data = JSON.parse(result.contents[0].text!);

        expect(data.configuration.timeout).toBe(timeout);
      }
    });
  });

  describe('Immutability and Thread Safety', () => {
    test('should not modify original config object', () => {
      const originalConfig = { ...mockConfig };
      
      configurationResource.updateConfig({
        logLevel: 'debug',
        port: 9999,
      });

      expect(mockConfig).toEqual(originalConfig);
    });

    test('should handle concurrent reads safely', async () => {
      const promises = Array.from({ length: 10 }, () => 
        configurationResource.getContents()
      );

      const results = await Promise.all(promises);

      results.forEach(result => {
        expect(result.contents[0].mimeType).toBe('application/json');
        const data = JSON.parse(result.contents[0].text!);
        expect(data).toHaveProperty('server');
        expect(data).toHaveProperty('configuration');
      });
    });

    test('should handle concurrent updates and reads', async () => {
      const updates = [
        { logLevel: 'debug' as const },
        { port: 4001 },
        { timeout: 20000 },
        { backendUrl: 'http://updated.com' },
      ];

      const updatePromises = updates.map((update, index) =>
        new Promise(resolve => {
          setTimeout(() => {
            configurationResource.updateConfig(update);
            resolve(undefined);
          }, index * 10);
        })
      );

      const readPromises = Array.from({ length: 5 }, (_, index) =>
        new Promise(resolve => {
          setTimeout(async () => {
            const result = await configurationResource.getContents();
            resolve(result);
          }, index * 15);
        })
      );

      await Promise.all([...updatePromises, ...readPromises]);

      // Final state should reflect all updates
      const finalResult = await configurationResource.getContents();
      const data = JSON.parse(finalResult.contents[0].text!);
      
      expect(data.configuration.logLevel).toBe('debug');
      expect(data.configuration.port).toBe(4001);
      expect(data.configuration.timeout).toBe(20000);
      expect(data.configuration.backendUrl).toBe('http://updated.com');
    });
  });
});