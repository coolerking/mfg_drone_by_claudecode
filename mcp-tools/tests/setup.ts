import { jest } from '@jest/globals';

// Global test configuration
global.console = {
  ...console,
  // Uncomment to suppress console output during tests
  // log: jest.fn(),
  // debug: jest.fn(),
  // info: jest.fn(),
  // warn: jest.fn(),
  // error: jest.fn(),
};

// Mock environment variables for tests
process.env.NODE_ENV = 'test';
process.env.BACKEND_URL = 'http://localhost:8000';
process.env.DEBUG = 'false';
process.env.LOG_LEVEL = 'error';

// Increase test timeout for integration tests
jest.setTimeout(10000);

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
});

export {};