import { jest } from '@jest/globals';
import { MCPDroneServer } from '../src/server.js';

// Mock the FastAPIClient
jest.mock('../src/bridge/api-client.js');

describe('MCP Drone Server Integration Tests', () => {
  let server: MCPDroneServer;

  beforeEach(() => {
    // Set test environment variables
    process.env.BACKEND_URL = 'http://localhost:8000';
    process.env.DEBUG = 'false';
    process.env.LOG_LEVEL = 'error';
    
    server = new MCPDroneServer();
  });

  afterEach(async () => {
    if (server) {
      await server.stop();
    }
    jest.clearAllMocks();
  });

  describe('TC-SYS-001: ヘルスチェック正常実行', () => {
    it('should initialize server with correct configuration', () => {
      // Act
      const serverInfo = server.getServerInfo();

      // Assert
      expect(serverInfo.toolCount).toBeGreaterThan(0);
      expect(serverInfo.config.backendUrl).toBe('http://localhost:8000');
      expect(serverInfo.config.timeout).toBeDefined();
      expect(serverInfo.config.retries).toBeDefined();
    });
  });

  describe('Tool Registration Tests', () => {
    it('should register all connection tools', () => {
      // Act
      const serverInfo = server.getServerInfo();

      // Assert
      expect(serverInfo.tools).toContain('drone_connect');
      expect(serverInfo.tools).toContain('drone_disconnect');
      expect(serverInfo.tools).toContain('drone_status');
    });

    it('should register all flight control tools', () => {
      // Act
      const serverInfo = server.getServerInfo();

      // Assert
      expect(serverInfo.tools).toContain('drone_takeoff');
      expect(serverInfo.tools).toContain('drone_land');
      expect(serverInfo.tools).toContain('drone_emergency');
      expect(serverInfo.tools).toContain('drone_stop');
      expect(serverInfo.tools).toContain('drone_get_height');
    });

    it('should have correct total tool count', () => {
      // Act
      const serverInfo = server.getServerInfo();

      // Assert
      expect(serverInfo.toolCount).toBe(8); // 3 connection + 5 flight tools
    });
  });

  describe('Configuration Tests', () => {
    it('should load configuration from environment variables', () => {
      // Arrange
      process.env.BACKEND_URL = 'http://test:9000';
      process.env.TIMEOUT = '3000';
      process.env.RETRIES = '5';

      // Act
      const testServer = new MCPDroneServer();
      const config = testServer.getServerInfo().config;

      // Assert
      expect(config.backendUrl).toBe('http://test:9000');
      expect(config.timeout).toBe(3000);
      expect(config.retries).toBe(5);

      // Cleanup
      testServer.stop();
    });

    it('should use default configuration when environment variables not set', () => {
      // Arrange
      delete process.env.BACKEND_URL;
      delete process.env.TIMEOUT;
      delete process.env.RETRIES;

      // Act
      const testServer = new MCPDroneServer();
      const config = testServer.getServerInfo().config;

      // Assert
      expect(config.backendUrl).toBe('http://localhost:8000'); // Default from setup
      expect(config.timeout).toBeDefined();
      expect(config.retries).toBeDefined();

      // Cleanup
      testServer.stop();
    });
  });

  describe('TC-SYS-002: システム障害時エラーハンドリング', () => {
    it('should handle configuration validation errors', () => {
      // Arrange
      process.env.TIMEOUT = '-1'; // Invalid timeout

      // Act & Assert
      expect(() => {
        new MCPDroneServer();
      }).toThrow('Timeout must be positive');
    });

    it('should handle invalid transport type', () => {
      // Arrange
      process.env.TRANSPORT = 'invalid';

      // Act & Assert
      expect(() => {
        new MCPDroneServer();
      }).toThrow('Invalid transport type');
    });
  });

  describe('Performance Tests', () => {
    describe('TC-PERF-001: API応答時間確認', () => {
      it('should initialize server quickly', () => {
        // Arrange
        const startTime = Date.now();

        // Act
        const testServer = new MCPDroneServer();

        // Assert
        const duration = Date.now() - startTime;
        expect(duration).toBeLessThan(1000); // Should initialize in less than 1 second

        // Cleanup
        testServer.stop();
      });
    });

    describe('TC-PERF-006: メモリ使用量確認', () => {
      it('should not leak memory during normal operation', () => {
        // Arrange
        const initialMemory = process.memoryUsage().heapUsed;

        // Act
        const testServer = new MCPDroneServer();
        const serverInfo = testServer.getServerInfo();

        // Assert
        const finalMemory = process.memoryUsage().heapUsed;
        const memoryIncrease = finalMemory - initialMemory;
        
        // Should not use excessive memory (less than 50MB for basic initialization)
        expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);

        // Cleanup
        testServer.stop();
      });
    });
  });

  describe('Error Handling Tests', () => {
    it('should handle server startup with invalid backend URL', () => {
      // Arrange
      process.env.BACKEND_URL = 'invalid-url';

      // Act & Assert
      expect(() => {
        new MCPDroneServer();
      }).not.toThrow(); // Should not throw during initialization
    });
  });

  describe('Tool Execution Integration', () => {
    it('should be able to retrieve tool information', () => {
      // Act
      const serverInfo = server.getServerInfo();

      // Assert
      expect(Array.isArray(serverInfo.tools)).toBe(true);
      expect(serverInfo.tools.length).toBeGreaterThan(0);
      expect(typeof serverInfo.toolCount).toBe('number');
    });
  });
});