#!/usr/bin/env node

import { config } from '@/config/index.js';
import { logger } from '@/utils/logger.js';
import { MCPDroneServer } from '@/server/MCPDroneServer.js';

const server = new MCPDroneServer(config);

// Graceful shutdown handling
const gracefulShutdown = async (): Promise<void> => {
  logger.info('Shutting down MCP Drone Server...');
  try {
    await server.stop();
    logger.info('MCP Drone Server stopped gracefully');
    process.exit(0);
  } catch (error) {
    logger.error('Error during shutdown:', error);
    process.exit(1);
  }
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

// Start the server
async function main(): Promise<void> {
  try {
    logger.info('Starting MCP Drone Server...');
    await server.start();
    logger.info(`MCP Drone Server started successfully on port ${config.port}`);
  } catch (error) {
    logger.error('Failed to start MCP Drone Server:', error);
    process.exit(1);
  }
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

main().catch((error) => {
  logger.error('Main function error:', error);
  process.exit(1);
});