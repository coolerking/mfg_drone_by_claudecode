#!/usr/bin/env node

import { readFileSync } from 'fs';
import { resolve } from 'path';
import { loadConfig, getConfigForEnvironment } from './utils/config.js';
import { MCPDroneServer } from './server.js';

/**
 * Main entry point for MCP Drone Server
 */
async function main(): Promise<void> {
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);
    const configPath = args.find(arg => arg.startsWith('--config='))?.split('=')[1];
    const environment = process.env.NODE_ENV || 'development';
    
    // Load configuration
    const defaultConfigPath = configPath || getConfigForEnvironment(environment);
    const config = loadConfig(defaultConfigPath);

    // Create and start server
    const server = new MCPDroneServer(config);
    
    // Handle graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\nReceived SIGINT, shutting down gracefully...');
      try {
        await server.stop();
        process.exit(0);
      } catch (error) {
        console.error('Error during shutdown:', error);
        process.exit(1);
      }
    });

    process.on('SIGTERM', async () => {
      console.log('\nReceived SIGTERM, shutting down gracefully...');
      try {
        await server.stop();
        process.exit(0);
      } catch (error) {
        console.error('Error during shutdown:', error);
        process.exit(1);
      }
    });

    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      console.error('Uncaught Exception:', error);
      process.exit(1);
    });

    process.on('unhandledRejection', (reason, promise) => {
      console.error('Unhandled Rejection at:', promise, 'reason:', reason);
      process.exit(1);
    });

    // Start the server
    await server.start();
    
  } catch (error) {
    console.error('Failed to start MCP Drone Server:', error);
    process.exit(1);
  }
}

// Show help if requested
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log(`
MFG Drone MCP Tools Server

Usage: node dist/index.js [options]

Options:
  --config=<path>   Path to configuration file
  --help, -h        Show this help message

Environment Variables:
  NODE_ENV          Environment (development|production) [default: development]
  BACKEND_URL       FastAPI backend URL [default: http://localhost:8000]
  DEBUG             Enable debug logging [default: false]
  LOG_FILE          Path to log file (optional)
  TIMEOUT           HTTP request timeout in ms [default: 30000]
  RETRY_ATTEMPTS    Number of retry attempts [default: 3]
  RETRY_DELAY       Delay between retries in ms [default: 1000]

Examples:
  # Start with default configuration
  node dist/index.js

  # Start with custom config file
  node dist/index.js --config=./config/production.json

  # Start with environment variables
  BACKEND_URL=http://192.168.1.100:8000 DEBUG=true node dist/index.js

Configuration:
  The server loads configuration from:
  1. Default values
  2. JSON configuration file (if specified)
  3. Environment variables (override file settings)

  Configuration files should be in JSON format:
  {
    "backendUrl": "http://localhost:8000",
    "timeout": 30000,
    "retryAttempts": 3,
    "retryDelay": 1000,
    "debug": false,
    "logFile": "./logs/mcp-drone.log",
    "maxLogSize": 10485760,
    "healthCheckInterval": 30000
  }

Available Tools:
  Connection:
    - drone_connect           Connect to Tello EDU drone
    - drone_disconnect        Disconnect from drone
    - drone_status            Get comprehensive drone status

  Flight Control:
    - drone_takeoff           Takeoff and hover
    - drone_land              Land safely
    - drone_emergency         Emergency stop (drops drone!)
    - drone_stop              Stop movement and hover
    - drone_get_height        Get current flight height

  Movement:
    - drone_move              Basic directional movement
    - drone_rotate            Rotate clockwise/counter-clockwise
    - drone_flip              Perform flip maneuver
    - drone_go_xyz            Move to XYZ coordinates
    - drone_curve             Curved flight path
    - drone_rc_control        Real-time RC control

  Camera:
    - camera_stream_start     Start video streaming
    - camera_stream_stop      Stop video streaming
    - camera_take_photo       Capture photo
    - camera_start_recording  Start video recording
    - camera_stop_recording   Stop video recording
    - camera_settings         Configure camera settings

  Sensors:
    - drone_battery           Get battery level
    - drone_temperature       Get drone temperature
    - drone_flight_time       Get cumulative flight time
    - drone_barometer         Get barometric pressure
    - drone_distance_tof      Get ToF sensor distance
    - drone_acceleration      Get acceleration data
    - drone_velocity          Get velocity data
    - drone_attitude          Get attitude (pitch/roll/yaw)
    - drone_sensor_summary    Get comprehensive sensor data

For more information, visit: https://github.com/coolerking/mfg_drone_by_claudecode
`);
  process.exit(0);
}

// Show version if requested
if (process.argv.includes('--version') || process.argv.includes('-v')) {
  try {
    const packageJson = JSON.parse(readFileSync(resolve(process.cwd(), 'package.json'), 'utf-8'));
    console.log(`MFG Drone MCP Tools v${packageJson.version}`);
  } catch {
    console.log('MFG Drone MCP Tools v1.0.0');
  }
  process.exit(0);
}

// Start the server
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});