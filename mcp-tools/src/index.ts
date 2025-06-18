#!/usr/bin/env node

/**
 * MFG Drone MCP Server
 * 
 * This is the main entry point for the MCP (Model Context Protocol) server
 * that enables Claude to interact with the MFG Drone Backend API.
 * 
 * The server provides MCP tools for:
 * - Drone connection management
 * - Flight control (takeoff, landing, emergency)
 * - Movement control (basic and advanced)
 * - Camera operations (streaming, capture)
 * - Sensor data access (battery, altitude, attitude)
 * - Object tracking and AI model management
 */

import { MCPDroneServer } from './server.js';
import { loadConfig } from './utils/config.js';
import { logger } from './utils/logger.js';

async function main(): Promise<void> {
  try {
    logger.info('Starting MFG Drone MCP Server...');
    
    // Load configuration
    const config = await loadConfig();
    logger.info('Configuration loaded successfully', { 
      environment: config.environment,
      backendUrl: config.backend.url 
    });

    // Initialize and start the MCP server
    const server = new MCPDroneServer(config);
    await server.initialize();
    
    logger.info('MCP server initialized successfully');
    logger.info('Server ready to handle MCP tool requests');

    // Handle graceful shutdown
    process.on('SIGINT', async () => {
      logger.info('Received SIGINT, shutting down gracefully...');
      await server.shutdown();
      process.exit(0);
    });

    process.on('SIGTERM', async () => {
      logger.info('Received SIGTERM, shutting down gracefully...');
      await server.shutdown();
      process.exit(0);
    });

  } catch (error) {
    logger.error('Failed to start MCP server:', error);
    process.exit(1);
  }
}

// Start the server
main().catch(error => {
  console.error('Unhandled error:', error);
  process.exit(1);
});