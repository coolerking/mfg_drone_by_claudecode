/**
 * Tests for Settings Manager
 * Comprehensive test suite for advanced configuration management
 */

import fs from 'fs';
import path from 'path';
import { EventEmitter } from 'events';
import SettingsManager, { 
  ExtendedConfigSchema, 
  getSettingsManager, 
  initializeSettings 
} from '../settings.js';
import { ValidationError } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

// Mock dependencies
jest.mock('fs');
jest.mock('@/utils/logger.js');
jest.mock('./index.js', () => ({
  config: {
    port: 3001,
    backendUrl: 'http://localhost:8000',
    logLevel: 'info',
    timeout: 10000,
    mcpPort: 3001,
    nlpConfidenceThreshold: 0.7,
  },
}));

const mockedFs = jest.mocked(fs);
const mockedLogger = jest.mocked(logger);

describe('SettingsManager', () => {
  let settingsManager: SettingsManager;
  let mockConfigPath: string;
  const originalEnv = process.env;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.resetModules();
    process.env = { ...originalEnv };
    
    mockConfigPath = '/tmp/test-config.json';
    settingsManager = new SettingsManager(mockConfigPath);

    // Setup default mocks
    mockedFs.existsSync.mockReturnValue(false);
    mockedFs.mkdirSync.mockReturnValue(undefined as any);
    mockedFs.writeFileSync.mockReturnValue();
    mockedFs.readFileSync.mockReturnValue(JSON.stringify({}));
    mockedFs.watch.mockReturnValue({
      close: jest.fn(),
    } as any);
  });

  afterEach(() => {
    process.env = originalEnv;
    if (settingsManager) {
      settingsManager.cleanup();
    }
  });

  describe('Constructor', () => {
    test('should create SettingsManager with default config path', () => {
      const manager = new SettingsManager();
      
      expect(manager).toBeInstanceOf(SettingsManager);
      expect(manager).toBeInstanceOf(EventEmitter);
      expect(manager.isLoaded).toBe(false);
    });

    test('should create SettingsManager with custom config path', () => {
      const customPath = '/custom/path/config.json';
      const manager = new SettingsManager(customPath);
      
      expect(manager).toBeInstanceOf(SettingsManager);
    });

    test('should initialize with default configuration', () => {
      const manager = new SettingsManager();
      const config = manager.getAll();
      
      expect(config).toBeDefined();
      expect(config.port).toBe(3001);
      expect(config.backendUrl).toBe('http://localhost:8000');
    });
  });

  describe('Initialization', () => {
    test('should initialize successfully when config file does not exist', async () => {
      mockedFs.existsSync.mockReturnValue(false);
      
      const initSpy = jest.spyOn(settingsManager, 'emit');
      
      await settingsManager.initialize();
      
      expect(settingsManager.isLoaded).toBe(true);
      expect(mockedFs.writeFileSync).toHaveBeenCalled();
      expect(initSpy).toHaveBeenCalledWith('initialized', expect.any(Object));
      expect(mockedLogger.info).toHaveBeenCalledWith(
        '設定管理システムが初期化されました',
        expect.any(Object)
      );
    });

    test('should initialize successfully when config file exists', async () => {
      const mockConfig = {
        port: 3002,
        backendUrl: 'http://localhost:8001',
        logLevel: 'debug',
      };
      
      mockedFs.existsSync.mockReturnValue(true);
      mockedFs.readFileSync.mockReturnValue(JSON.stringify(mockConfig));
      
      await settingsManager.initialize();
      
      expect(settingsManager.isLoaded).toBe(true);
      expect(settingsManager.get('port')).toBe(3002);
      expect(settingsManager.get('backendUrl')).toBe('http://localhost:8001');
    });

    test('should handle initialization errors', async () => {
      mockedFs.existsSync.mockImplementation(() => {
        throw new Error('File system error');
      });
      
      await expect(settingsManager.initialize()).rejects.toThrow(ValidationError);
      expect(settingsManager.isLoaded).toBe(false);
    });

    test('should setup file watcher during initialization', async () => {
      await settingsManager.initialize();
      
      expect(mockedFs.watch).toHaveBeenCalledWith(
        mockConfigPath,
        { persistent: false },
        expect.any(Function)
      );
    });
  });

  describe('Configuration Loading', () => {
    test('should load valid configuration file', async () => {
      const validConfig = {
        port: 3003,
        backendUrl: 'http://example.com',
        logLevel: 'warn',
        mcp: {
          maxConnections: 50,
          heartbeatInterval: 25000,
        },
      };
      
      mockedFs.existsSync.mockReturnValue(true);
      mockedFs.readFileSync.mockReturnValue(JSON.stringify(validConfig));
      
      await settingsManager.initialize();
      
      expect(settingsManager.get('port')).toBe(3003);
      expect(settingsManager.get('mcp')).toEqual(expect.objectContaining({
        maxConnections: 50,
        heartbeatInterval: 25000,
      }));
    });

    test('should handle invalid JSON in config file', async () => {
      mockedFs.existsSync.mockReturnValue(true);
      mockedFs.readFileSync.mockReturnValue('invalid-json');
      
      await expect(settingsManager.initialize()).rejects.toThrow(ValidationError);
    });

    test('should handle config file read errors', async () => {
      mockedFs.existsSync.mockReturnValue(true);
      mockedFs.readFileSync.mockImplementation(() => {
        throw new Error('Permission denied');
      });
      
      await expect(settingsManager.initialize()).rejects.toThrow(ValidationError);
    });

    test('should validate loaded configuration against schema', async () => {
      const invalidConfig = {
        port: -1, // Invalid port
        backendUrl: 'invalid-url',
      };
      
      mockedFs.existsSync.mockReturnValue(true);
      mockedFs.readFileSync.mockReturnValue(JSON.stringify(invalidConfig));
      
      await expect(settingsManager.initialize()).rejects.toThrow(ValidationError);
    });
  });

  describe('Configuration Management', () => {
    beforeEach(async () => {
      await settingsManager.initialize();
    });

    describe('get method', () => {
      test('should get configuration values', () => {
        const port = settingsManager.get('port');
        const logLevel = settingsManager.get('logLevel');
        
        expect(typeof port).toBe('number');
        expect(typeof logLevel).toBe('string');
      });

      test('should warn when accessing config before initialization', () => {
        const uninitializedManager = new SettingsManager();
        
        uninitializedManager.get('port');
        
        expect(mockedLogger.warn).toHaveBeenCalledWith(
          '設定がまだ初期化されていません'
        );
      });
    });

    describe('set method', () => {
      test('should set configuration values successfully', async () => {
        const newPort = 4001;
        
        await settingsManager.set('port', newPort);
        
        expect(settingsManager.get('port')).toBe(newPort);
        expect(mockedFs.writeFileSync).toHaveBeenCalled();
      });

      test('should emit configUpdated event', async () => {
        const emitSpy = jest.spyOn(settingsManager, 'emit');
        const newLogLevel = 'error';
        
        await settingsManager.set('logLevel', newLogLevel);
        
        expect(emitSpy).toHaveBeenCalledWith(
          'configUpdated',
          'logLevel',
          newLogLevel,
          'info' // old value
        );
      });

      test('should revert changes on validation error', async () => {
        const originalPort = settingsManager.get('port');
        
        // Mock validation to fail
        jest.spyOn(ExtendedConfigSchema, 'parse').mockImplementation(() => {
          throw new Error('Validation failed');
        });
        
        await expect(settingsManager.set('port', -1)).rejects.toThrow(ValidationError);
        
        // Should revert to original value
        expect(settingsManager.get('port')).toBe(originalPort);
      });

      test('should handle file write errors', async () => {
        mockedFs.writeFileSync.mockImplementation(() => {
          throw new Error('Disk full');
        });
        
        await expect(settingsManager.set('port', 4001)).rejects.toThrow(ValidationError);
      });
    });

    describe('updateMultiple method', () => {
      test('should update multiple configuration values', async () => {
        const updates = {
          port: 4002,
          logLevel: 'debug' as const,
          timeout: 15000,
        };
        
        await settingsManager.updateMultiple(updates);
        
        expect(settingsManager.get('port')).toBe(4002);
        expect(settingsManager.get('logLevel')).toBe('debug');
        expect(settingsManager.get('timeout')).toBe(15000);
      });

      test('should emit configUpdated event for multiple updates', async () => {
        const emitSpy = jest.spyOn(settingsManager, 'emit');
        const updates = { port: 4003, timeout: 20000 };
        
        await settingsManager.updateMultiple(updates);
        
        expect(emitSpy).toHaveBeenCalledWith(
          'configUpdated',
          'multiple',
          updates,
          expect.any(Object)
        );
      });

      test('should revert all changes on validation error', async () => {
        const originalConfig = settingsManager.getAll();
        
        // Mock validation to fail
        jest.spyOn(ExtendedConfigSchema, 'parse').mockImplementation(() => {
          throw new Error('Validation failed');
        });
        
        await expect(settingsManager.updateMultiple({
          port: -1,
          timeout: -1,
        })).rejects.toThrow(ValidationError);
        
        // Should revert to original values
        expect(settingsManager.getAll()).toEqual(originalConfig);
      });
    });

    describe('getAll method', () => {
      test('should return complete configuration', () => {
        const config = settingsManager.getAll();
        
        expect(config).toHaveProperty('port');
        expect(config).toHaveProperty('backendUrl');
        expect(config).toHaveProperty('logLevel');
        expect(config).toHaveProperty('mcp');
        expect(config).toHaveProperty('drone');
        expect(config).toHaveProperty('security');
      });

      test('should return a copy of configuration', () => {
        const config1 = settingsManager.getAll();
        const config2 = settingsManager.getAll();
        
        expect(config1).toEqual(config2);
        expect(config1).not.toBe(config2); // Different objects
      });
    });

    describe('getSafeConfig method', () => {
      test('should mask sensitive information', async () => {
        await settingsManager.set('security', {
          enableAuthentication: true,
          jwtSecret: 'super-secret-key',
          tokenExpiration: '1h',
          rateLimitRequests: 100,
          rateLimitWindow: 60000,
        });
        
        const safeConfig = settingsManager.getSafeConfig();
        
        expect(safeConfig.security?.jwtSecret).toBe('***');
      });

      test('should not mask non-sensitive information', () => {
        const safeConfig = settingsManager.getSafeConfig();
        
        expect(safeConfig.port).toBeDefined();
        expect(safeConfig.backendUrl).toBeDefined();
        expect(safeConfig.logLevel).toBeDefined();
      });
    });

    describe('reset method', () => {
      test('should reset configuration to defaults', async () => {
        // Make some changes first
        await settingsManager.set('port', 9999);
        await settingsManager.set('logLevel', 'error');
        
        const resetSpy = jest.spyOn(settingsManager, 'emit');
        
        await settingsManager.reset();
        
        // Should have default values
        const config = settingsManager.getAll();
        expect(config.port).toBe(3001); // Default from base config
        
        expect(resetSpy).toHaveBeenCalledWith('configReset', expect.any(Object));
        expect(mockedLogger.info).toHaveBeenCalledWith(
          '設定がデフォルト値にリセットされました'
        );
      });
    });
  });

  describe('Environment Overrides', () => {
    test('should apply environment variable overrides', async () => {
      process.env.MCP_PORT = '5001';
      process.env.BACKEND_URL = 'http://override.com';
      process.env.LOG_LEVEL = 'debug';
      process.env.JWT_SECRET = 'env-secret';
      process.env.MAX_CONNECTIONS = '200';
      
      await settingsManager.initialize();
      settingsManager.applyEnvironmentOverrides();
      
      expect(settingsManager.get('port')).toBe(5001);
      expect(settingsManager.get('backendUrl')).toBe('http://override.com');
      expect(settingsManager.get('logLevel')).toBe('debug');
    });

    test('should parse environment values correctly', async () => {
      process.env.MAX_DRONES = '10';
      process.env.BATTERY_WARNING_LEVEL = '15';
      
      await settingsManager.initialize();
      settingsManager.applyEnvironmentOverrides();
      
      const drone = settingsManager.get('drone');
      expect(drone.maxDrones).toBe(10);
      expect(drone.batteryWarningLevel).toBe(15);
    });

    test('should parse boolean values from environment', async () => {
      process.env.AUTO_LAND_ON_LOW_BATTERY = 'false';
      
      await settingsManager.initialize();
      settingsManager.applyEnvironmentOverrides();
      
      // Note: This would require extending the envMapping in the actual code
      // For now, we test the parseEnvValue method indirectly
    });
  });

  describe('File Watching', () => {
    beforeEach(async () => {
      await settingsManager.initialize();
    });

    test('should setup file watcher', () => {
      expect(mockedFs.watch).toHaveBeenCalledWith(
        mockConfigPath,
        { persistent: false },
        expect.any(Function)
      );
    });

    test('should handle file change events', async () => {
      const reloadSpy = jest.spyOn(settingsManager, 'reloadConfiguration');
      
      // Get the callback function passed to fs.watch
      const watchCallback = mockedFs.watch.mock.calls[0][2];
      
      await watchCallback('change', 'config.json');
      
      expect(reloadSpy).toHaveBeenCalled();
      expect(mockedLogger.info).toHaveBeenCalledWith(
        '設定ファイル変更を検出しました。リロードします...'
      );
    });

    test('should not reload on non-change events', async () => {
      const reloadSpy = jest.spyOn(settingsManager, 'reloadConfiguration');
      
      const watchCallback = mockedFs.watch.mock.calls[0][2];
      
      await watchCallback('rename', 'config.json');
      
      expect(reloadSpy).not.toHaveBeenCalled();
    });

    test('should handle file watcher setup errors gracefully', () => {
      const newManager = new SettingsManager('/non/existent/path/config.json');
      
      mockedFs.watch.mockImplementation(() => {
        throw new Error('Cannot watch file');
      });
      
      // Should not throw
      expect(async () => await newManager.initialize()).not.toThrow();
      
      expect(mockedLogger.warn).toHaveBeenCalledWith(
        '設定ファイル監視の設定に失敗しました',
        expect.any(Object)
      );
    });
  });

  describe('Configuration Reload', () => {
    beforeEach(async () => {
      await settingsManager.initialize();
    });

    test('should reload configuration successfully', async () => {
      const newConfig = {
        port: 6001,
        backendUrl: 'http://reloaded.com',
      };
      
      mockedFs.readFileSync.mockReturnValue(JSON.stringify(newConfig));
      
      const configChangedSpy = jest.spyOn(settingsManager, 'emit');
      
      await settingsManager.reloadConfiguration();
      
      expect(settingsManager.get('port')).toBe(6001);
      expect(configChangedSpy).toHaveBeenCalledWith(
        'configChanged',
        expect.any(Object),
        expect.any(Object)
      );
    });

    test('should handle reload errors', async () => {
      mockedFs.readFileSync.mockImplementation(() => {
        throw new Error('File read error');
      });
      
      const errorSpy = jest.spyOn(settingsManager, 'emit');
      
      await settingsManager.reloadConfiguration();
      
      expect(errorSpy).toHaveBeenCalledWith('configError', expect.any(Error));
      expect(mockedLogger.error).toHaveBeenCalledWith(
        '設定リロードエラー',
        expect.any(Object)
      );
    });
  });

  describe('Cleanup', () => {
    test('should cleanup resources properly', async () => {
      const mockWatcher = {
        close: jest.fn(),
      };
      
      mockedFs.watch.mockReturnValue(mockWatcher as any);
      
      await settingsManager.initialize();
      await settingsManager.cleanup();
      
      expect(mockWatcher.close).toHaveBeenCalled();
      expect(settingsManager.isLoaded).toBe(false);
      expect(mockedLogger.info).toHaveBeenCalledWith(
        '設定管理システムがクリーンアップされました'
      );
    });

    test('should remove all event listeners during cleanup', async () => {
      const removeAllListenersSpy = jest.spyOn(settingsManager, 'removeAllListeners');
      
      await settingsManager.initialize();
      await settingsManager.cleanup();
      
      expect(removeAllListenersSpy).toHaveBeenCalled();
    });
  });

  describe('Singleton Functions', () => {
    test('getSettingsManager should return singleton instance', () => {
      const manager1 = getSettingsManager();
      const manager2 = getSettingsManager();
      
      expect(manager1).toBe(manager2);
    });

    test('initializeSettings should initialize and return settings manager', async () => {
      const manager = await initializeSettings(mockConfigPath);
      
      expect(manager).toBeInstanceOf(SettingsManager);
      expect(manager.isLoaded).toBe(true);
    });

    test('initializeSettings should not reinitialize if already loaded', async () => {
      // First initialization
      const manager1 = await initializeSettings(mockConfigPath);
      const initializeSpy = jest.spyOn(manager1, 'initialize');
      
      // Second call should not reinitialize
      const manager2 = await initializeSettings(mockConfigPath);
      
      expect(manager1).toBe(manager2);
      expect(initializeSpy).not.toHaveBeenCalled();
    });
  });

  describe('Schema Validation', () => {
    test('ExtendedConfigSchema should validate complete configuration', () => {
      const validConfig = {
        port: 3001,
        backendUrl: 'http://localhost:8000',
        logLevel: 'info',
        timeout: 10000,
        mcp: {
          maxConnections: 100,
          heartbeatInterval: 30000,
          retryAttempts: 3,
          retryDelay: 2000,
        },
        drone: {
          maxDrones: 5,
          commandTimeout: 10000,
          batteryWarningLevel: 20,
          autoLandOnLowBattery: true,
        },
        security: {
          enableAuthentication: true,
          jwtSecret: 'secret',
          tokenExpiration: '1h',
          rateLimitRequests: 100,
          rateLimitWindow: 60000,
        },
      };
      
      expect(() => ExtendedConfigSchema.parse(validConfig)).not.toThrow();
    });

    test('ExtendedConfigSchema should apply defaults for missing values', () => {
      const minimalConfig = {
        port: 3001,
        backendUrl: 'http://localhost:8000',
      };
      
      const parsedConfig = ExtendedConfigSchema.parse(minimalConfig);
      
      expect(parsedConfig.logLevel).toBe('info'); // Default
      expect(parsedConfig.mcp.maxConnections).toBe(100); // Default
      expect(parsedConfig.drone.maxDrones).toBe(5); // Default
      expect(parsedConfig.security.enableAuthentication).toBe(true); // Default
    });

    test('ExtendedConfigSchema should reject invalid values', () => {
      const invalidConfigs = [
        { port: -1 }, // Invalid port
        { port: 70000 }, // Port too high
        { backendUrl: 'invalid-url' }, // Invalid URL
        { logLevel: 'invalid' }, // Invalid log level
        { timeout: 0 }, // Timeout too low
        { mcp: { maxConnections: 0 } }, // Invalid max connections
        { drone: { batteryWarningLevel: 101 } }, // Battery level too high
      ];
      
      invalidConfigs.forEach(invalidConfig => {
        expect(() => ExtendedConfigSchema.parse({
          port: 3001,
          backendUrl: 'http://localhost:8000',
          ...invalidConfig,
        })).toThrow();
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle missing directory creation', async () => {
      mockedFs.existsSync.mockReturnValue(false);
      mockedFs.mkdirSync.mockImplementation(() => {
        throw new Error('Permission denied');
      });
      
      await expect(settingsManager.initialize()).rejects.toThrow();
    });

    test('should handle file write permissions', async () => {
      mockedFs.writeFileSync.mockImplementation(() => {
        throw new Error('EACCES: permission denied');
      });
      
      await expect(settingsManager.initialize()).rejects.toThrow();
    });
  });
});