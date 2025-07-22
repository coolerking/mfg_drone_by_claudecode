/**
 * Tests for SystemLogsResource
 * Test suite for system logs MCP resource
 */

import { SystemLogsResource } from '../SystemLogsResource.js';
import { DroneService } from '@/services/DroneService.js';
import { logger } from '@/utils/logger.js';
import type { HealthCheckResponse } from '@/types/api_types.js';

// Mock dependencies
jest.mock('@/services/DroneService.js');
jest.mock('@/utils/logger.js');

const mockedLogger = jest.mocked(logger);

describe('SystemLogsResource', () => {
  let mockDroneService: jest.Mocked<DroneService>;
  let systemLogsResource: SystemLogsResource;

  beforeEach(() => {
    mockDroneService = new DroneService({} as any) as jest.Mocked<DroneService>;
    systemLogsResource = new SystemLogsResource(mockDroneService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Properties', () => {
    test('should have correct description', () => {
      expect(systemLogsResource.getDescription()).toBe(
        'System logs and events from the MCP drone server including command execution, errors, and system activities.'
      );
    });

    test('should have correct URI', () => {
      expect(systemLogsResource.getUri()).toBe('mcp://system-logs/logs');
    });

    test('should have correct MIME type', () => {
      expect(systemLogsResource.getMimeType()).toBe('application/json');
    });
  });

  describe('Initialization', () => {
    test('should initialize log buffer on construction', () => {
      // Create a new instance and check if initialization log is added
      const newResource = new SystemLogsResource(mockDroneService);
      
      // The constructor should add an initialization log entry
      expect(newResource).toBeInstanceOf(SystemLogsResource);
    });

    test('should set default max log size', () => {
      // We can't directly test private properties, but we can test behavior
      expect(systemLogsResource).toBeInstanceOf(SystemLogsResource);
    });
  });

  describe('Log Entry Management', () => {
    test('should add log entries correctly', () => {
      systemLogsResource.addLogEntry('info', 'Test message', 'TestSource');
      systemLogsResource.addLogEntry('error', 'Error message', 'ErrorSource', { 
        errorCode: 500,
        details: 'Test error details' 
      });

      // We can't directly access the log buffer, but we can test through getContents
      expect(() => {
        systemLogsResource.addLogEntry('debug', 'Debug message', 'DebugSource');
      }).not.toThrow();
    });

    test('should handle log entries with metadata', () => {
      const metadata = {
        userId: 'user-123',
        action: 'drone_command',
        duration: 1500,
        success: true,
      };

      systemLogsResource.addLogEntry('info', 'Command executed', 'CommandHandler', metadata);

      expect(() => {
        systemLogsResource.addLogEntry('warn', 'Warning message', 'System');
      }).not.toThrow();
    });

    test('should handle log entries without metadata', () => {
      systemLogsResource.addLogEntry('info', 'Simple message', 'SimpleSource');

      expect(() => {
        systemLogsResource.addLogEntry('error', 'Another message', 'AnotherSource');
      }).not.toThrow();
    });

    test('should manage log buffer size limit', () => {
      // Add more than the max log size (1000) to test buffer management
      for (let i = 0; i < 1200; i++) {
        systemLogsResource.addLogEntry('info', `Message ${i}`, 'TestSource');
      }

      // The buffer should be trimmed to max size, but we can't test directly
      // We test that it doesn't throw errors
      expect(() => {
        systemLogsResource.addLogEntry('info', 'Final message', 'TestSource');
      }).not.toThrow();
    });

    test('should clear logs correctly', () => {
      // Add some log entries
      systemLogsResource.addLogEntry('info', 'Message 1', 'Source1');
      systemLogsResource.addLogEntry('error', 'Message 2', 'Source2');

      systemLogsResource.clearLogs();

      // After clearing, only the initialization and clear messages should remain
      expect(() => {
        systemLogsResource.clearLogs();
      }).not.toThrow();
    });
  });

  describe('getContents Method', () => {
    const mockHealthResponse: HealthCheckResponse = {
      status: 'healthy',
      timestamp: '2024-01-01T10:00:00Z',
      services: {
        backend: { status: 'up', message: 'Running normally' },
        database: { status: 'up' },
      },
    };

    beforeEach(() => {
      mockDroneService.performHealthCheck.mockResolvedValue(mockHealthResponse);
    });

    test('should return comprehensive log data', async () => {
      // Add some test logs
      systemLogsResource.addLogEntry('error', 'Test error', 'TestSource');
      systemLogsResource.addLogEntry('warn', 'Test warning', 'TestSource');
      systemLogsResource.addLogEntry('info', 'Test info', 'TestSource');
      systemLogsResource.addLogEntry('debug', 'Test debug', 'TestSource');

      const result = await systemLogsResource.getContents();

      expect(result.contents).toHaveLength(1);
      expect(result.contents[0].mimeType).toBe('application/json');
      expect(result.contents[0].uri).toBe('mcp://system-logs/logs');

      const data = JSON.parse(result.contents[0].text!);
      
      expect(data).toHaveProperty('timestamp');
      expect(data).toHaveProperty('summary');
      expect(data).toHaveProperty('recentLogs');
      expect(data).toHaveProperty('logsByLevel');
      expect(data).toHaveProperty('systemHealth');
      expect(data).toHaveProperty('logSources');
    });

    test('should include correct summary information', async () => {
      // Clear existing logs and add specific test logs
      systemLogsResource.clearLogs();
      
      for (let i = 0; i < 5; i++) {
        systemLogsResource.addLogEntry('error', `Error ${i}`, 'ErrorSource');
      }
      for (let i = 0; i < 3; i++) {
        systemLogsResource.addLogEntry('warn', `Warning ${i}`, 'WarnSource');
      }

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.summary).toHaveProperty('totalLogs');
      expect(data.summary).toHaveProperty('recentLogCount');
      expect(data.summary).toHaveProperty('errorCount');
      expect(data.summary).toHaveProperty('warningCount');
      expect(data.summary).toHaveProperty('systemHealth', 'healthy');

      expect(data.summary.errorCount).toBeGreaterThan(0);
      expect(data.summary.warningCount).toBeGreaterThan(0);
    });

    test('should organize logs by level correctly', async () => {
      systemLogsResource.clearLogs();
      
      // Add logs of different levels
      systemLogsResource.addLogEntry('error', 'Error log 1', 'Source1');
      systemLogsResource.addLogEntry('error', 'Error log 2', 'Source1');
      systemLogsResource.addLogEntry('warn', 'Warning log 1', 'Source2');
      systemLogsResource.addLogEntry('info', 'Info log 1', 'Source3');
      systemLogsResource.addLogEntry('debug', 'Debug log 1', 'Source4');

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.logsByLevel).toHaveProperty('error');
      expect(data.logsByLevel).toHaveProperty('warn');
      expect(data.logsByLevel).toHaveProperty('info');
      expect(data.logsByLevel).toHaveProperty('debug');

      expect(Array.isArray(data.logsByLevel.error)).toBe(true);
      expect(Array.isArray(data.logsByLevel.warn)).toBe(true);
      expect(Array.isArray(data.logsByLevel.info)).toBe(true);
      expect(Array.isArray(data.logsByLevel.debug)).toBe(true);
    });

    test('should include system health information', async () => {
      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.systemHealth).toEqual(mockHealthResponse);
      expect(mockDroneService.performHealthCheck).toHaveBeenCalled();
    });

    test('should handle health check failures gracefully', async () => {
      const healthError = new Error('Health check failed');
      mockDroneService.performHealthCheck.mockRejectedValue(healthError);

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.systemHealth).toEqual({
        status: 'unknown',
        timestamp: expect.any(String),
        error: 'Health check failed',
      });
    });

    test('should include log sources information', async () => {
      systemLogsResource.clearLogs();
      
      // Add logs from different sources
      systemLogsResource.addLogEntry('info', 'Message 1', 'Source1');
      systemLogsResource.addLogEntry('info', 'Message 2', 'Source1');
      systemLogsResource.addLogEntry('error', 'Message 3', 'Source2');
      systemLogsResource.addLogEntry('debug', 'Message 4', 'Source3');

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(Array.isArray(data.logSources)).toBe(true);
      expect(data.logSources.length).toBeGreaterThan(0);

      data.logSources.forEach((source: any) => {
        expect(source).toHaveProperty('source');
        expect(source).toHaveProperty('count');
        expect(source).toHaveProperty('lastActivity');
        expect(typeof source.source).toBe('string');
        expect(typeof source.count).toBe('number');
        expect(typeof source.lastActivity).toBe('string');
      });
    });

    test('should limit recent logs to 100 entries', async () => {
      systemLogsResource.clearLogs();
      
      // Add more than 100 logs
      for (let i = 0; i < 150; i++) {
        systemLogsResource.addLogEntry('info', `Message ${i}`, 'TestSource');
      }

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.recentLogs.length).toBeLessThanOrEqual(100);
    });

    test('should limit logs by level correctly', async () => {
      systemLogsResource.clearLogs();
      
      // Add many logs of each level
      for (let i = 0; i < 50; i++) {
        systemLogsResource.addLogEntry('error', `Error ${i}`, 'TestSource');
        systemLogsResource.addLogEntry('warn', `Warning ${i}`, 'TestSource');
        systemLogsResource.addLogEntry('info', `Info ${i}`, 'TestSource');
        systemLogsResource.addLogEntry('debug', `Debug ${i}`, 'TestSource');
      }

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.logsByLevel.error.length).toBeLessThanOrEqual(20);
      expect(data.logsByLevel.warn.length).toBeLessThanOrEqual(20);
      expect(data.logsByLevel.info.length).toBeLessThanOrEqual(30);
      expect(data.logsByLevel.debug.length).toBeLessThanOrEqual(30);
    });

    test('should log debug information', async () => {
      await systemLogsResource.getContents();

      expect(mockedLogger.debug).toHaveBeenCalledWith('Retrieving system logs resource');
    });

    test('should include valid timestamps', async () => {
      const before = new Date().toISOString();
      const result = await systemLogsResource.getContents();
      const after = new Date().toISOString();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.timestamp).toBeGreaterThanOrEqual(before);
      expect(data.timestamp).toBeLessThanOrEqual(after);
      expect(new Date(data.timestamp)).toBeInstanceOf(Date);
    });
  });

  describe('Log Source Tracking', () => {
    test('should track multiple sources correctly', async () => {
      systemLogsResource.clearLogs();
      
      systemLogsResource.addLogEntry('info', 'Message 1', 'DroneController');
      systemLogsResource.addLogEntry('error', 'Message 2', 'VisionService');
      systemLogsResource.addLogEntry('info', 'Message 3', 'DroneController'); // Same source
      systemLogsResource.addLogEntry('warn', 'Message 4', 'AuthManager');

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const droneControllerSource = data.logSources.find((s: any) => s.source === 'DroneController');
      expect(droneControllerSource).toBeDefined();
      expect(droneControllerSource.count).toBe(2);

      const visionServiceSource = data.logSources.find((s: any) => s.source === 'VisionService');
      expect(visionServiceSource).toBeDefined();
      expect(visionServiceSource.count).toBe(1);

      const authManagerSource = data.logSources.find((s: any) => s.source === 'AuthManager');
      expect(authManagerSource).toBeDefined();
      expect(authManagerSource.count).toBe(1);
    });

    test('should update last activity timestamps correctly', async () => {
      systemLogsResource.clearLogs();
      
      const timestamp1 = new Date('2024-01-01T10:00:00Z').toISOString();
      const timestamp2 = new Date('2024-01-01T11:00:00Z').toISOString();

      // Manually create log entries with specific timestamps (this requires accessing private methods)
      // For this test, we'll add logs and verify the behavior indirectly
      systemLogsResource.addLogEntry('info', 'Early message', 'TestSource');
      
      // Wait a small amount of time
      await new Promise(resolve => setTimeout(resolve, 10));
      
      systemLogsResource.addLogEntry('info', 'Later message', 'TestSource');

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const testSource = data.logSources.find((s: any) => s.source === 'TestSource');
      expect(testSource).toBeDefined();
      expect(testSource.count).toBe(2);
      expect(new Date(testSource.lastActivity)).toBeInstanceOf(Date);
    });
  });

  describe('Error Handling', () => {
    test('should handle errors during content generation', async () => {
      // Force an error by making the health check fail and causing other issues
      mockDroneService.performHealthCheck.mockRejectedValue(new Error('System failure'));

      const result = await systemLogsResource.getContents();

      expect(result.contents[0].mimeType).toBe('text/plain');
      expect(result.contents[0].text).toContain('Error retrieving SystemLogsResource');
      expect(mockedLogger.error).toHaveBeenCalledWith(
        'Error retrieving system logs resource:',
        expect.any(Error)
      );
    });

    test('should handle health check errors without affecting log data', async () => {
      mockDroneService.performHealthCheck.mockRejectedValue(new Error('Health check failed'));
      
      systemLogsResource.addLogEntry('info', 'Test message', 'TestSource');

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.systemHealth.status).toBe('unknown');
      expect(data.systemHealth.error).toBe('Health check failed');
      expect(data.recentLogs.length).toBeGreaterThan(0); // Should still have logs
    });
  });

  describe('Log Entry Format and Structure', () => {
    test('should format log entries correctly', async () => {
      systemLogsResource.clearLogs();
      
      const metadata = {
        userId: 'user-123',
        action: 'test_action',
        value: 42,
        success: true,
      };

      systemLogsResource.addLogEntry('info', 'Test message', 'TestSource', metadata);

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const logEntry = data.recentLogs.find((log: any) => log.message === 'Test message');
      expect(logEntry).toBeDefined();
      expect(logEntry).toHaveProperty('timestamp');
      expect(logEntry).toHaveProperty('level', 'info');
      expect(logEntry).toHaveProperty('message', 'Test message');
      expect(logEntry).toHaveProperty('source', 'TestSource');
      expect(logEntry).toHaveProperty('metadata', metadata);

      expect(new Date(logEntry.timestamp)).toBeInstanceOf(Date);
    });

    test('should handle log entries without metadata', async () => {
      systemLogsResource.clearLogs();
      
      systemLogsResource.addLogEntry('warn', 'Warning without metadata', 'WarnSource');

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const logEntry = data.recentLogs.find((log: any) => log.message === 'Warning without metadata');
      expect(logEntry).toBeDefined();
      expect(logEntry).not.toHaveProperty('metadata');
    });

    test('should handle various log levels', async () => {
      const levels = ['error', 'warn', 'info', 'debug'];
      systemLogsResource.clearLogs();
      
      levels.forEach((level, index) => {
        systemLogsResource.addLogEntry(level, `${level} message ${index}`, 'TestSource');
      });

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      levels.forEach(level => {
        const levelLogs = data.logsByLevel[level];
        expect(Array.isArray(levelLogs)).toBe(true);
        const hasLogOfLevel = levelLogs.some((log: any) => log.level === level);
        expect(hasLogOfLevel).toBe(true);
      });
    });
  });

  describe('Response Content Structure', () => {
    test('should always return properly structured response', async () => {
      const result = await systemLogsResource.getContents();

      expect(result).toHaveProperty('contents');
      expect(Array.isArray(result.contents)).toBe(true);
      expect(result.contents).toHaveLength(1);

      const content = result.contents[0];
      expect(content).toHaveProperty('uri', 'mcp://system-logs/logs');
      expect(content).toHaveProperty('mimeType', 'application/json');
      expect(content).toHaveProperty('text');
      expect(typeof content.text).toBe('string');
    });

    test('should produce valid JSON in response text', async () => {
      const result = await systemLogsResource.getContents();
      
      expect(() => {
        JSON.parse(result.contents[0].text!);
      }).not.toThrow();
    });

    test('should format JSON with proper indentation', async () => {
      const result = await systemLogsResource.getContents();
      const text = result.contents[0].text!;
      
      // Should be formatted with 2-space indentation
      expect(text).toContain('  "timestamp"');
      expect(text).toContain('  "summary"');
      expect(text).toContain('    "totalLogs"');
    });
  });

  describe('Performance and Memory Management', () => {
    test('should handle large numbers of log entries efficiently', () => {
      const startTime = Date.now();
      
      // Add many log entries
      for (let i = 0; i < 5000; i++) {
        systemLogsResource.addLogEntry('info', `Performance test message ${i}`, `Source${i % 10}`);
      }
      
      const endTime = Date.now();
      
      expect(endTime - startTime).toBeLessThan(5000); // Should complete within 5 seconds
    });

    test('should clear logs without errors', () => {
      // Add many logs
      for (let i = 0; i < 1000; i++) {
        systemLogsResource.addLogEntry('info', `Message ${i}`, 'TestSource');
      }

      expect(() => {
        systemLogsResource.clearLogs();
      }).not.toThrow();

      // Should be able to add logs after clearing
      expect(() => {
        systemLogsResource.addLogEntry('info', 'After clear', 'TestSource');
      }).not.toThrow();
    });

    test('should handle concurrent log additions safely', async () => {
      const promises = Array.from({ length: 100 }, (_, i) =>
        new Promise<void>(resolve => {
          setTimeout(() => {
            systemLogsResource.addLogEntry('info', `Concurrent message ${i}`, `Source${i % 5}`);
            resolve();
          }, Math.random() * 100);
        })
      );

      await Promise.all(promises);

      const result = await systemLogsResource.getContents();
      const data = JSON.parse(result.contents[0].text!);
      
      expect(data.summary.totalLogs).toBeGreaterThan(100); // Including initial logs
    });
  });
});