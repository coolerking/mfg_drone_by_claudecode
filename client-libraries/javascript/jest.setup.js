// Jest setup file for MCP Client SDK

// Mock WebSocket
global.WebSocket = jest.fn().mockImplementation(() => ({
  on: jest.fn(),
  close: jest.fn(),
  send: jest.fn(),
}));

// Mock console methods in tests
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
};

// Set up test environment variables
process.env.NODE_ENV = 'test';