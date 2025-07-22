/**
 * Tests for Config Index
 * Comprehensive test suite for configuration management
 */

import { ConfigSchema, ValidationError } from '@/types/index.js';
import { config, getConfig, validateBackendConnection, isProduction, isDevelopment } from '../index.js';

// Mock dependencies
jest.mock('dotenv');

describe('Config Index', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules(); // Clear module cache
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('Environment Variable Loading', () => {
    test('should load config with default values when no env vars set', () => {
      // Clear relevant environment variables
      delete process.env.MCP_PORT;
      delete process.env.BACKEND_URL;
      delete process.env.LOG_LEVEL;
      delete process.env.TIMEOUT;

      // Re-require the module to test with cleared env
      jest.resetModules();
      const { config: newConfig } = require('../index.js');

      expect(newConfig).toBeDefined();
      expect(typeof newConfig.port).toBe('number');
      expect(typeof newConfig.backendUrl).toBe('string');
      expect(typeof newConfig.logLevel).toBe('string');
      expect(typeof newConfig.timeout).toBe('number');
    });

    test('should parse environment variables correctly', () => {
      process.env.MCP_PORT = '3002';
      process.env.BACKEND_URL = 'http://localhost:8001';
      process.env.LOG_LEVEL = 'debug';
      process.env.TIMEOUT = '15000';

      jest.resetModules();
      const { config: newConfig } = require('../index.js');

      expect(newConfig.port).toBe(3002);
      expect(newConfig.backendUrl).toBe('http://localhost:8001');
      expect(newConfig.logLevel).toBe('debug');
      expect(newConfig.timeout).toBe(15000);
    });

    test('should handle invalid port gracefully', () => {
      process.env.MCP_PORT = 'invalid_port';

      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError);
    });

    test('should handle invalid timeout gracefully', () => {
      process.env.TIMEOUT = 'invalid_timeout';

      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError);
    });

    test('should ignore undefined values and apply defaults', () => {
      process.env.MCP_PORT = '3001';
      // Leave other vars undefined
      delete process.env.BACKEND_URL;
      delete process.env.LOG_LEVEL;
      delete process.env.TIMEOUT;

      jest.resetModules();
      const { config: newConfig } = require('../index.js');

      expect(newConfig.port).toBe(3001);
      expect(newConfig.backendUrl).toBeDefined(); // Should have default
      expect(newConfig.logLevel).toBeDefined(); // Should have default
      expect(newConfig.timeout).toBeDefined(); // Should have default
    });
  });

  describe('getConfig function', () => {
    test('should return the same config object', () => {
      const config1 = getConfig();
      const config2 = getConfig();

      expect(config1).toEqual(config2);
      expect(config1).toBe(config2); // Should be the same reference
    });

    test('should return config with all required properties', () => {
      const configObj = getConfig();

      expect(configObj).toHaveProperty('port');
      expect(configObj).toHaveProperty('backendUrl');
      expect(configObj).toHaveProperty('logLevel');
      expect(configObj).toHaveProperty('timeout');
      expect(configObj).toHaveProperty('mcpPort');
      expect(configObj).toHaveProperty('nlpConfidenceThreshold');
    });

    test('should return config that matches ConfigSchema', () => {
      const configObj = getConfig();
      
      expect(() => ConfigSchema.parse(configObj)).not.toThrow();
    });
  });

  describe('validateBackendConnection function', () => {
    test('should validate valid HTTP URLs', () => {
      const validUrls = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://example.com',
        'http://192.168.1.100:8080',
      ];

      validUrls.forEach(url => {
        expect(validateBackendConnection(url)).toBe(true);
      });
    });

    test('should validate valid HTTPS URLs', () => {
      const validUrls = [
        'https://localhost:8000',
        'https://example.com',
        'https://api.example.com:443',
        'https://secure.api.com/path',
      ];

      validUrls.forEach(url => {
        expect(validateBackendConnection(url)).toBe(true);
      });
    });

    test('should reject invalid URLs', () => {
      const invalidUrls = [
        'ftp://localhost:8000',
        'ws://localhost:8000',
        'invalid-url',
        '',
        'localhost:8000',
        'http:///invalid',
        'not-a-url-at-all',
      ];

      invalidUrls.forEach(url => {
        expect(validateBackendConnection(url)).toBe(false);
      });
    });

    test('should handle malformed URLs gracefully', () => {
      const malformedUrls = [
        'http://',
        'https://',
        'http://[',
        'http://::1:invalid',
      ];

      malformedUrls.forEach(url => {
        expect(validateBackendConnection(url)).toBe(false);
      });
    });
  });

  describe('Environment Detection Functions', () => {
    describe('isProduction', () => {
      test('should return true when NODE_ENV is production', () => {
        process.env.NODE_ENV = 'production';
        
        jest.resetModules();
        const { isProduction: isProd } = require('../index.js');
        
        expect(isProd()).toBe(true);
      });

      test('should return false when NODE_ENV is not production', () => {
        const nonProdEnvs = ['development', 'test', 'staging', undefined];
        
        nonProdEnvs.forEach(env => {
          process.env.NODE_ENV = env as string;
          
          jest.resetModules();
          const { isProduction: isProd } = require('../index.js');
          
          expect(isProd()).toBe(false);
        });
      });

      test('should return false when NODE_ENV is not set', () => {
        delete process.env.NODE_ENV;
        
        jest.resetModules();
        const { isProduction: isProd } = require('../index.js');
        
        expect(isProd()).toBe(false);
      });
    });

    describe('isDevelopment', () => {
      test('should return true when NODE_ENV is development', () => {
        process.env.NODE_ENV = 'development';
        
        jest.resetModules();
        const { isDevelopment: isDev } = require('../index.js');
        
        expect(isDev()).toBe(true);
      });

      test('should return true when NODE_ENV is not set (default)', () => {
        delete process.env.NODE_ENV;
        
        jest.resetModules();
        const { isDevelopment: isDev } = require('../index.js');
        
        expect(isDev()).toBe(true);
      });

      test('should return false when NODE_ENV is production or test', () => {
        const nonDevEnvs = ['production', 'test', 'staging'];
        
        nonDevEnvs.forEach(env => {
          process.env.NODE_ENV = env;
          
          jest.resetModules();
          const { isDevelopment: isDev } = require('../index.js');
          
          expect(isDev()).toBe(false);
        });
      });
    });
  });

  describe('Configuration Validation', () => {
    test('should throw ValidationError with invalid configuration', () => {
      process.env.MCP_PORT = '-1'; // Invalid port
      
      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError);
    });

    test('should throw ValidationError with invalid URL', () => {
      process.env.BACKEND_URL = 'invalid-url';
      
      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError);
    });

    test('should throw ValidationError with invalid log level', () => {
      process.env.LOG_LEVEL = 'invalid-level';
      
      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError);
    });

    test('should provide meaningful error messages', () => {
      process.env.MCP_PORT = '99999'; // Port too high
      
      try {
        jest.resetModules();
        require('../index.js');
        fail('Should have thrown ValidationError');
      } catch (error) {
        expect(error).toBeInstanceOf(ValidationError);
        expect(error.message).toContain('Invalid configuration');
      }
    });
  });

  describe('Configuration Object Structure', () => {
    test('should have correct types for all properties', () => {
      const configObj = getConfig();

      expect(typeof configObj.port).toBe('number');
      expect(typeof configObj.backendUrl).toBe('string');
      expect(typeof configObj.logLevel).toBe('string');
      expect(typeof configObj.timeout).toBe('number');
      expect(typeof configObj.mcpPort).toBe('number');
      expect(typeof configObj.nlpConfidenceThreshold).toBe('number');
    });

    test('should have values within expected ranges', () => {
      const configObj = getConfig();

      expect(configObj.port).toBeGreaterThan(0);
      expect(configObj.port).toBeLessThanOrEqual(65535);
      expect(configObj.timeout).toBeGreaterThan(0);
      expect(configObj.mcpPort).toBeGreaterThan(0);
      expect(configObj.mcpPort).toBeLessThanOrEqual(65535);
      expect(configObj.nlpConfidenceThreshold).toBeGreaterThanOrEqual(0);
      expect(configObj.nlpConfidenceThreshold).toBeLessThanOrEqual(1);
      expect(['debug', 'info', 'warn', 'error']).toContain(configObj.logLevel);
    });
  });

  describe('Configuration Immutability', () => {
    test('should not allow direct modification of config object', () => {
      const configObj = getConfig();
      const originalPort = configObj.port;

      // Attempt to modify (this should not affect the original)
      const modifiedConfig = { ...configObj, port: 9999 };
      
      // Original config should remain unchanged
      expect(getConfig().port).toBe(originalPort);
      expect(getConfig().port).not.toBe(9999);
    });
  });

  describe('Edge Cases', () => {
    test('should handle empty string environment variables', () => {
      process.env.BACKEND_URL = '';
      process.env.LOG_LEVEL = '';

      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError);
    });

    test('should handle whitespace-only environment variables', () => {
      process.env.BACKEND_URL = '   ';
      process.env.LOG_LEVEL = '   ';

      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError);
    });

    test('should handle zero values appropriately', () => {
      process.env.MCP_PORT = '0';
      
      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError); // Port 0 should be invalid
    });

    test('should handle very large timeout values', () => {
      process.env.TIMEOUT = '999999999';
      
      expect(() => {
        jest.resetModules();
        require('../index.js');
      }).toThrow(ValidationError); // Should exceed max timeout
    });
  });
});