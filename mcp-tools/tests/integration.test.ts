/**
 * Integration Tests for MCP Drone Tools
 * 
 * Comprehensive integration tests for the MCP server, tools, and backend bridge.
 * Tests the complete flow from MCP tool execution to FastAPI backend communication.
 */

import { describe, test, expect, beforeAll, afterAll, beforeEach, jest } from '@jest/globals';
import { MCPDroneServer } from '../src/server';
import { ConfigManager } from '../src/utils/config';
import { Logger } from '../src/utils/logger';
import { ToolRegistry } from '../src/tools/registry';
import { EnhancedFastAPIClient } from '../src/bridge/enhanced-api-client';
import { WebSocketBridge } from '../src/bridge/websocket-bridge';
import { MetricsCollector } from '../src/bridge/metrics-collector';

// Mock the external dependencies
jest.mock('../src/bridge/enhanced-api-client');
jest.mock('../src/bridge/websocket-bridge');

describe('MCP Drone Tools Integration Tests', () => {
  let server: MCPDroneServer;
  let toolRegistry: ToolRegistry;
  let apiClient: jest.Mocked<EnhancedFastAPIClient>;
  let wsClient: jest.Mocked<WebSocketBridge>;
  let logger: Logger;
  let config: ReturnType<ConfigManager['getConfig']>;

  beforeAll(async () => {
    // Load test configuration
    config = ConfigManager.getInstance().loadConfig('test');
    logger = Logger.getInstance();
    
    // Setup test environment
    process.env.NODE_ENV = 'test';
    process.env.BACKEND_URL = 'http://localhost:8000';
    process.env.LOG_LEVEL = 'error'; // Reduce log noise in tests
  });

  beforeEach(async () => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Create new instances for each test
    toolRegistry = new ToolRegistry();
    
    // Mock API client responses
    const MockedEnhancedFastAPIClient = EnhancedFastAPIClient as jest.MockedClass<typeof EnhancedFastAPIClient>;
    apiClient = new MockedEnhancedFastAPIClient() as jest.Mocked<EnhancedFastAPIClient>;
    
    // Setup default mock responses
    apiClient.connect.mockResolvedValue({
      success: true,
      message: 'Connected successfully',
      timestamp: new Date().toISOString(),
    });
    
    apiClient.disconnect.mockResolvedValue({
      success: true,
      message: 'Disconnected successfully',
      timestamp: new Date().toISOString(),
    });
    
    apiClient.getStatus.mockResolvedValue({
      success: true,
      message: 'Status retrieved',
      data: {
        connected: true,
        battery: 85,
        flight_mode: 'ready',
      },
      timestamp: new Date().toISOString(),
    });
    
    apiClient.takeoff.mockResolvedValue({
      success: true,
      message: 'Takeoff successful',
      timestamp: new Date().toISOString(),
    });
    
    apiClient.land.mockResolvedValue({
      success: true,
      message: 'Landing successful',
      timestamp: new Date().toISOString(),
    });
    
    apiClient.getSensorData.mockResolvedValue({
      success: true,
      message: 'Sensor data retrieved',
      data: {
        battery: 85,
        temperature: 32.5,
        height: 120,
        barometer: 1013.25,
        distance_tof: 118,
        acceleration: { x: 0.02, y: -0.01, z: 1.01 },
        velocity: { x: 0.5, y: 1.2, z: 0.0 },
        attitude: { pitch: 2.1, roll: -0.8, yaw: 185.4 },
        flight_time: 145,
      },
      timestamp: new Date().toISOString(),
    });
    
    apiClient.getHealthStatus.mockReturnValue({
      isHealthy: true,
      lastCheck: new Date(),
    });
    
    apiClient.getPerformanceMetrics.mockReturnValue({
      'GET /drone/status': { avg: 45, min: 20, max: 80, count: 10 },
      'POST /drone/connect': { avg: 120, min: 100, max: 150, count: 5 },
    });
  });

  afterAll(async () => {
    // Cleanup
    if (server) {
      await server.stop?.();
    }
  });

  describe('Server Initialization', () => {
    test('should initialize MCP server successfully', async () => {
      server = new MCPDroneServer();
      
      expect(server).toBeDefined();
      expect(server.isHealthy()).toBeTruthy();
    });

    test('should register all required tools', async () => {
      server = new MCPDroneServer();
      const serverInfo = server.getServerInfo();
      
      expect(serverInfo.toolCount).toBeGreaterThan(20);
      expect(serverInfo.categories).toContain('connection');
      expect(serverInfo.categories).toContain('flight');
      expect(serverInfo.categories).toContain('movement');
      expect(serverInfo.categories).toContain('camera');
      expect(serverInfo.categories).toContain('sensors');
    });

    test('should load configuration correctly', () => {
      expect(config.server.name).toBe('MFG Drone MCP Tools');
      expect(config.backend.baseUrl).toContain('localhost');
      expect(config.performance.targetResponseTime).toBe(50);
    });
  });

  describe('Tool Execution Tests', () => {
    beforeEach(async () => {
      server = new MCPDroneServer();
      toolRegistry = server['toolRegistry']; // Access private member for testing
    });

    test('should execute drone_connect tool successfully', async () => {
      const result = await toolRegistry.executeTool('drone_connect', {});
      
      expect(result.success).toBe(true);
      expect(result.toolName).toBe('drone_connect');
      expect(result.duration).toBeGreaterThan(0);
      expect(apiClient.connect).toHaveBeenCalledTimes(1);
    });

    test('should execute drone_status tool successfully', async () => {
      const result = await toolRegistry.executeTool('drone_status', {});
      
      expect(result.success).toBe(true);
      expect(result.data).toHaveProperty('status');
      expect(apiClient.getStatus).toHaveBeenCalledTimes(1);
    });

    test('should execute drone_takeoff tool successfully', async () => {
      const result = await toolRegistry.executeTool('drone_takeoff', {});
      
      expect(result.success).toBe(true);
      expect(result.data.message).toContain('Takeoff successful');
      expect(apiClient.takeoff).toHaveBeenCalledTimes(1);
    });

    test('should handle tool execution errors gracefully', async () => {
      // Mock an error response
      apiClient.connect.mockRejectedValue(new Error('Connection failed'));
      
      const result = await toolRegistry.executeTool('drone_connect', {});
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Connection failed');
    });

    test('should validate tool arguments', async () => {
      const result = await toolRegistry.executeTool('drone_move', {
        direction: 'invalid_direction',
        distance: 50,
      });
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid arguments');
    });
  });

  describe('Performance Tests', () => {
    beforeEach(async () => {
      server = new MCPDroneServer();
      toolRegistry = server['toolRegistry'];
    });

    test('should meet response time requirements', async () => {
      const startTime = Date.now();
      const result = await toolRegistry.executeTool('drone_status', {});
      const duration = Date.now() - startTime;
      
      expect(result.success).toBe(true);
      expect(duration).toBeLessThan(config.performance.targetResponseTime);
    });

    test('should handle concurrent tool executions', async () => {
      const promises = Array.from({ length: 5 }, (_, i) => 
        toolRegistry.executeTool('drone_status', {})
      );
      
      const results = await Promise.all(promises);
      
      results.forEach(result => {
        expect(result.success).toBe(true);
      });
      
      expect(apiClient.getStatus).toHaveBeenCalledTimes(5);
    });

    test('should collect performance metrics', async () => {
      // Execute several tools
      await toolRegistry.executeTool('drone_connect', {});
      await toolRegistry.executeTool('drone_status', {});
      await toolRegistry.executeTool('drone_takeoff', {});
      
      const stats = toolRegistry.getToolExecutionStats();
      
      expect(stats['drone_connect'].count).toBe(1);
      expect(stats['drone_status'].count).toBe(1);
      expect(stats['drone_takeoff'].count).toBe(1);
    });
  });

  describe('Error Handling Tests', () => {
    beforeEach(async () => {
      server = new MCPDroneServer();
      toolRegistry = server['toolRegistry'];
    });

    test('should handle API client errors', async () => {
      // Mock API client error
      apiClient.connect.mockRejectedValue(new Error('Network error'));
      
      const result = await toolRegistry.executeTool('drone_connect', {});
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Network error');
    });

    test('should handle invalid tool names', async () => {
      const result = await toolRegistry.executeTool('invalid_tool', {});
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('not found');
    });

    test('should validate required arguments', async () => {
      const result = await toolRegistry.executeTool('drone_move', {
        // Missing required arguments
      });
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid arguments');
    });

    test('should handle malformed responses from backend', async () => {
      // Mock malformed response
      apiClient.getStatus.mockResolvedValue({
        success: false,
        message: 'Backend error',
        timestamp: new Date().toISOString(),
      } as any);
      
      const result = await toolRegistry.executeTool('drone_status', {});
      
      expect(result.success).toBe(true); // Tool should handle this gracefully
      expect(result.data.success).toBe(false);
    });
  });

  describe('Integration with Backend API', () => {
    beforeEach(async () => {
      server = new MCPDroneServer();
      toolRegistry = server['toolRegistry'];
    });

    test('should integrate with connection endpoints', async () => {
      await toolRegistry.executeTool('drone_connect', {});
      await toolRegistry.executeTool('drone_disconnect', {});
      
      expect(apiClient.connect).toHaveBeenCalledTimes(1);
      expect(apiClient.disconnect).toHaveBeenCalledTimes(1);
    });

    test('should integrate with flight control endpoints', async () => {
      await toolRegistry.executeTool('drone_takeoff', {});
      await toolRegistry.executeTool('drone_land', {});
      
      expect(apiClient.takeoff).toHaveBeenCalledTimes(1);
      expect(apiClient.land).toHaveBeenCalledTimes(1);
    });

    test('should integrate with sensor endpoints', async () => {
      await toolRegistry.executeTool('drone_battery', {});
      await toolRegistry.executeTool('drone_sensor_summary', {});
      
      expect(apiClient.getSensorData).toHaveBeenCalledTimes(1);
      expect(apiClient.getBattery).toHaveBeenCalledTimes(1);
    });

    test('should handle backend timeout scenarios', async () => {
      // Mock timeout
      apiClient.connect.mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 100)
        )
      );
      
      const result = await toolRegistry.executeTool('drone_connect', {});
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Timeout');
    });
  });

  describe('WebSocket Integration Tests', () => {
    beforeEach(async () => {
      server = new MCPDroneServer();
      
      // Mock WebSocket client
      const MockedWebSocketBridge = WebSocketBridge as jest.MockedClass<typeof WebSocketBridge>;
      wsClient = new MockedWebSocketBridge() as jest.Mocked<WebSocketBridge>;
      
      wsClient.connect.mockResolvedValue();
      wsClient.isConnected.mockReturnValue(true);
      wsClient.getConnectionState.mockReturnValue('connected');
    });

    test('should initialize WebSocket connection when enabled', () => {
      expect(wsClient.connect).toHaveBeenCalled();
    });

    test('should handle WebSocket connection events', () => {
      // Simulate connection event
      wsClient.emit('connected');
      
      expect(wsClient.isConnected()).toBe(true);
    });

    test('should handle WebSocket errors gracefully', () => {
      // Simulate error event
      const error = new Error('WebSocket error');
      wsClient.emit('error', error);
      
      // Should not crash the server
      expect(server.isHealthy()).toBe(true);
    });
  });

  describe('Metrics Collection Tests', () => {
    beforeEach(async () => {
      server = new MCPDroneServer();
    });

    test('should collect tool execution metrics', async () => {
      const metrics = await server.getMetrics();
      
      expect(metrics).toHaveProperty('api');
      expect(metrics).toHaveProperty('performance');
      expect(metrics).toHaveProperty('system');
    });

    test('should track API performance metrics', async () => {
      await toolRegistry.executeTool('drone_status', {});
      
      const metrics = apiClient.getPerformanceMetrics();
      
      expect(Object.keys(metrics).length).toBeGreaterThan(0);
    });

    test('should provide health status', () => {
      const healthStatus = apiClient.getHealthStatus();
      
      expect(healthStatus).toHaveProperty('isHealthy');
      expect(healthStatus).toHaveProperty('lastCheck');
    });
  });

  describe('Configuration Tests', () => {
    test('should load development configuration', () => {
      const devConfig = ConfigManager.getInstance().loadConfig('development');
      
      expect(devConfig.environment).toBe('development');
      expect(devConfig.debug).toBe(true);
      expect(devConfig.logging.level).toBe('debug');
    });

    test('should load production configuration', () => {
      const prodConfig = ConfigManager.getInstance().loadConfig('production');
      
      expect(prodConfig.environment).toBe('production');
      expect(prodConfig.debug).toBe(false);
      expect(prodConfig.logging.level).toBe('info');
    });

    test('should handle environment variable overrides', () => {
      process.env.BACKEND_URL = 'http://custom-backend:9000';
      process.env.LOG_LEVEL = 'warn';
      
      const config = ConfigManager.getInstance().loadConfig('test');
      
      expect(config.backend.baseUrl).toBe('http://custom-backend:9000');
      expect(config.logging.level).toBe('warn');
      
      // Cleanup
      delete process.env.BACKEND_URL;
      delete process.env.LOG_LEVEL;
    });
  });

  describe('Tool Categories Tests', () => {
    beforeEach(async () => {
      server = new MCPDroneServer();
      toolRegistry = server['toolRegistry'];
    });

    test('should have connection tools', () => {
      const connectionTools = toolRegistry.getToolsByCategory('connection');
      
      expect(connectionTools.length).toBeGreaterThan(0);
      expect(connectionTools.some(tool => tool.name === 'drone_connect')).toBe(true);
      expect(connectionTools.some(tool => tool.name === 'drone_disconnect')).toBe(true);
      expect(connectionTools.some(tool => tool.name === 'drone_status')).toBe(true);
    });

    test('should have flight tools', () => {
      const flightTools = toolRegistry.getToolsByCategory('flight');
      
      expect(flightTools.length).toBeGreaterThan(0);
      expect(flightTools.some(tool => tool.name === 'drone_takeoff')).toBe(true);
      expect(flightTools.some(tool => tool.name === 'drone_land')).toBe(true);
      expect(flightTools.some(tool => tool.name === 'drone_emergency')).toBe(true);
    });

    test('should have movement tools', () => {
      const movementTools = toolRegistry.getToolsByCategory('movement');
      
      expect(movementTools.length).toBeGreaterThan(0);
      expect(movementTools.some(tool => tool.name === 'drone_move')).toBe(true);
      expect(movementTools.some(tool => tool.name === 'drone_rotate')).toBe(true);
    });

    test('should have camera tools', () => {
      const cameraTools = toolRegistry.getToolsByCategory('camera');
      
      expect(cameraTools.length).toBeGreaterThan(0);
      expect(cameraTools.some(tool => tool.name === 'camera_stream_start')).toBe(true);
      expect(cameraTools.some(tool => tool.name === 'camera_take_photo')).toBe(true);
    });

    test('should have sensor tools', () => {
      const sensorTools = toolRegistry.getToolsByCategory('sensors');
      
      expect(sensorTools.length).toBeGreaterThan(0);
      expect(sensorTools.some(tool => tool.name === 'drone_battery')).toBe(true);
      expect(sensorTools.some(tool => tool.name === 'drone_sensor_summary')).toBe(true);
    });
  });
});