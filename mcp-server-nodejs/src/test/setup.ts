import { jest } from '@jest/globals';

// Global test setup
beforeAll(() => {
  // Suppress console.log during tests
  jest.spyOn(console, 'log').mockImplementation(() => {});
  jest.spyOn(console, 'info').mockImplementation(() => {});
  jest.spyOn(console, 'warn').mockImplementation(() => {});
  jest.spyOn(console, 'error').mockImplementation(() => {});
});

afterAll(() => {
  // Restore console methods
  jest.restoreAllMocks();
});

// Mock environment variables for tests
process.env.NODE_ENV = 'test';
process.env.MCP_PORT = '3001';
process.env.BACKEND_URL = 'http://localhost:8000';
process.env.LOG_LEVEL = 'error'; // Reduce log noise during tests
process.env.TIMEOUT = '5000';

// Global test utilities
global.createMockDroneStatus = () => ({
  id: 'test-drone-1',
  name: 'Test Drone',
  status: 'connected' as const,
  batteryLevel: 85,
  position: { x: 0, y: 0, z: 0 },
  lastSeen: new Date().toISOString(),
});

global.createMockSystemStatus = () => ({
  status: 'healthy' as const,
  timestamp: new Date().toISOString(),
  services: {
    backend: {
      status: 'up' as const,
      lastCheck: new Date().toISOString(),
      message: 'Service is running normally',
    },
    database: {
      status: 'up' as const,
      lastCheck: new Date().toISOString(),
    },
  },
  drones: [global.createMockDroneStatus()],
});

// Type declarations for global test utilities
declare global {
  var createMockDroneStatus: () => import('../types/index.js').DroneStatus;
  var createMockSystemStatus: () => import('../types/index.js').SystemStatus;
}