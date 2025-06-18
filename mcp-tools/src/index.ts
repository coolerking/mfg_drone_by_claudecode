#!/usr/bin/env node

import { MCPDroneServer } from './server.js';
import { ConfigManager } from './utils/config.js';
import { Logger } from './utils/logger.js';

/**
 * MFG Drone MCP Tools - Main Entry Point
 * 
 * This is the main entry point for the MCP (Model Context Protocol) server
 * that provides drone control tools for Claude and other AI systems.
 * 
 * Features:
 * - Complete drone control (connection, flight, movement, camera, sensors)
 * - Real-time WebSocket communication
 * - Performance monitoring and metrics
 * - Enhanced error handling and retry logic
 * - Production-ready logging and configuration
 */

async function main(): Promise<void> {
  let server: MCPDroneServer | null = null;
  
  try {
    // Load configuration
    const environment = process.env.NODE_ENV || 'development';
    const config = ConfigManager.getInstance().loadConfig(environment);
    const logger = Logger.getInstance();

    logger.info('🚁 Starting MFG Drone MCP Tools Server', {
      environment: config.environment,
      version: config.server.version,
      backendUrl: config.backend.baseUrl,
      websocketEnabled: config.websocket.enabled,
      logLevel: config.logging.level,
      performanceMonitoring: config.performance.enableMetrics,
    });

    // Validate environment
    if (!validateEnvironment()) {
      throw new Error('Environment validation failed');
    }

    // Create and initialize server
    server = new MCPDroneServer();
    await server.initialize();

    // Display startup information
    displayStartupInfo(server);

    // Start the server
    await server.run();

  } catch (error) {
    const logger = Logger.getInstance();
    logger.error('❌ Failed to start MCP Drone Server', error as Error);
    
    console.error('❌ Failed to start MCP Drone Server');
    console.error(error instanceof Error ? error.message : 'Unknown error');
    
    if (server) {
      try {
        // Attempt graceful cleanup
        await cleanup();
      } catch (cleanupError) {
        logger.error('Error during cleanup', cleanupError as Error);
      }
    }
    
    process.exit(1);
  }
}

function validateEnvironment(): boolean {
  const logger = Logger.getInstance();
  
  // Check Node.js version
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.substring(1).split('.')[0], 10);
  
  if (majorVersion < 18) {
    logger.error('Node.js version 18 or higher is required', {
      current: nodeVersion,
      required: '>=18.0.0',
    });
    return false;
  }

  // Check required environment variables
  const requiredEnvVars = [];
  const optionalEnvVars = [
    'BACKEND_URL',
    'LOG_LEVEL',
    'DEBUG',
    'NODE_ENV',
  ];

  for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
      logger.error(`Required environment variable missing: ${envVar}`);
      return false;
    }
  }

  // Log environment configuration
  logger.info('Environment validation passed', {
    nodeVersion,
    envVars: {
      set: optionalEnvVars.filter(v => process.env[v] !== undefined),
      missing: optionalEnvVars.filter(v => process.env[v] === undefined),
    },
  });

  return true;
}

function displayStartupInfo(server: MCPDroneServer): void {
  const logger = Logger.getInstance();
  const info = server.getServerInfo();
  
  console.log('\n🚁 MFG Drone MCP Tools Server');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`📊 Server: ${info.name} v${info.version}`);
  console.log(`🔧 Environment: ${info.environment}`);
  console.log(`🔗 Backend: ${info.backendUrl}`);
  console.log(`🛠️  Tools: ${info.toolCount} tools across ${info.categories.length} categories`);
  console.log(`📡 WebSocket: ${info.websocketEnabled ? (info.websocketConnected ? '✅ Connected' : '🔄 Enabled') : '❌ Disabled'}`);
  console.log(`📈 Performance: Monitoring ${info.websocketEnabled ? 'enabled' : 'disabled'}`);
  console.log('\n📋 Available Tool Categories:');
  info.categories.forEach(category => {
    console.log(`   • ${category}`);
  });
  console.log('\n🎯 Ready for Claude integration!');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  logger.info('Startup information displayed', {
    categories: info.categories,
    toolCount: info.toolCount,
  });
}

async function cleanup(): Promise<void> {
  const logger = Logger.getInstance();
  
  try {
    // Flush any remaining logs
    await logger.flush();
    
    logger.info('Cleanup completed');
  } catch (error) {
    console.error('Error during cleanup:', error);
  }
}

// Handle CLI arguments and help
function handleCliArguments(): void {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
🚁 MFG Drone MCP Tools Server

USAGE:
    node dist/index.js [OPTIONS]

OPTIONS:
    --help, -h          Show this help message
    --version, -v       Show version information
    --config <path>     Specify custom config file
    --log-level <level> Set log level (debug, info, warn, error)

ENVIRONMENT VARIABLES:
    NODE_ENV           Environment (development, production, test)
    BACKEND_URL        Drone backend API URL
    LOG_LEVEL          Logging level override
    DEBUG              Enable debug mode (true/false)

EXAMPLES:
    # Start with default configuration
    node dist/index.js

    # Start in production mode
    NODE_ENV=production node dist/index.js

    # Start with custom backend URL
    BACKEND_URL=http://192.168.1.100:8000 node dist/index.js

    # Start with debug logging
    LOG_LEVEL=debug DEBUG=true node dist/index.js

For more information, visit: https://github.com/coolerking/mfg_drone_by_claudecode
`);
    process.exit(0);
  }

  if (args.includes('--version') || args.includes('-v')) {
    const config = ConfigManager.getInstance().getConfig();
    console.log(`MFG Drone MCP Tools v${config.server.version}`);
    process.exit(0);
  }

  // Handle log level override
  const logLevelIndex = args.indexOf('--log-level');
  if (logLevelIndex !== -1 && args[logLevelIndex + 1]) {
    process.env.LOG_LEVEL = args[logLevelIndex + 1];
  }
}

// Main execution
if (require.main === module) {
  handleCliArguments();
  main().catch((error) => {
    console.error('❌ Unhandled error in main:', error);
    process.exit(1);
  });
}

export { MCPDroneServer };
export default main;