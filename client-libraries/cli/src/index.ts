#!/usr/bin/env node

/**
 * MCP Drone CLI
 * Command Line Interface for MCP Drone Control Server
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import { table } from 'table';
import axios, { AxiosInstance } from 'axios';
import WebSocket from 'ws';
import * as yaml from 'yaml';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

// Configuration interface
interface Config {
  baseURL: string;
  apiKey?: string;
  bearerToken?: string;
  timeout?: number;
}

// CLI Client class
class MCPCliClient {
  private client: AxiosInstance;
  private config: Config;
  private ws: WebSocket | null = null;

  constructor(config: Config) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey && { 'X-API-Key': config.apiKey }),
        ...(config.bearerToken && { 'Authorization': `Bearer ${config.bearerToken}` }),
      },
    });
  }

  async request(method: string, endpoint: string, data?: any) {
    try {
      const response = await this.client.request({
        method,
        url: endpoint,
        data,
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(`API Error: ${error.response.data.message || error.response.statusText}`);
      }
      throw error;
    }
  }

  async executeCommand(command: string, options: any = {}) {
    return await this.request('POST', '/mcp/command', {
      command,
      context: options.context,
      options: options.options,
    });
  }

  async executeBatchCommand(commands: string[], options: any = {}) {
    return await this.request('POST', '/mcp/command/batch', {
      commands: commands.map(cmd => ({ command: cmd })),
      execution_mode: options.mode || 'sequential',
      stop_on_error: options.stopOnError !== false,
    });
  }

  async getDrones() {
    return await this.request('GET', '/mcp/drones');
  }

  async getAvailableDrones() {
    return await this.request('GET', '/mcp/drones/available');
  }

  async getDroneStatus(droneId: string) {
    return await this.request('GET', `/mcp/drones/${droneId}/status`);
  }

  async connectDrone(droneId: string) {
    return await this.request('POST', `/mcp/drones/${droneId}/connect`);
  }

  async disconnectDrone(droneId: string) {
    return await this.request('POST', `/mcp/drones/${droneId}/disconnect`);
  }

  async takeoff(droneId: string, height?: number) {
    const data = height ? { target_height: height } : {};
    return await this.request('POST', `/mcp/drones/${droneId}/takeoff`, data);
  }

  async land(droneId: string) {
    return await this.request('POST', `/mcp/drones/${droneId}/land`);
  }

  async moveDrone(droneId: string, direction: string, distance: number, speed?: number) {
    const data = {
      direction,
      distance,
      ...(speed && { speed }),
    };
    return await this.request('POST', `/mcp/drones/${droneId}/move`, data);
  }

  async rotateDrone(droneId: string, direction: string, angle: number) {
    return await this.request('POST', `/mcp/drones/${droneId}/rotate`, {
      direction,
      angle,
    });
  }

  async emergencyStop(droneId: string) {
    return await this.request('POST', `/mcp/drones/${droneId}/emergency`);
  }

  async setAltitude(droneId: string, height: number, mode: string = 'absolute') {
    return await this.request('POST', `/mcp/drones/${droneId}/altitude`, {
      target_height: height,
      mode,
    });
  }

  async takePhoto(droneId: string, filename?: string, quality?: string) {
    const data = {
      ...(filename && { filename }),
      ...(quality && { quality }),
    };
    return await this.request('POST', `/mcp/drones/${droneId}/camera/photo`, data);
  }

  async controlStreaming(droneId: string, action: string, quality?: string, resolution?: string) {
    const data = {
      action,
      ...(quality && { quality }),
      ...(resolution && { resolution }),
    };
    return await this.request('POST', `/mcp/drones/${droneId}/camera/streaming`, data);
  }

  async detectObjects(droneId: string, modelId?: string, threshold?: number) {
    const data = {
      drone_id: droneId,
      ...(modelId && { model_id: modelId }),
      ...(threshold && { confidence_threshold: threshold }),
    };
    return await this.request('POST', '/mcp/vision/detection', data);
  }

  async controlTracking(action: string, droneId: string, modelId?: string, distance?: number) {
    const data = {
      action,
      drone_id: droneId,
      ...(modelId && { model_id: modelId }),
      ...(distance && { follow_distance: distance }),
    };
    return await this.request('POST', '/mcp/vision/tracking', data);
  }

  async getSystemStatus() {
    return await this.request('GET', '/mcp/system/status');
  }

  async getHealthCheck() {
    return await this.request('GET', '/mcp/system/health');
  }

  connectWebSocket(onMessage?: (data: any) => void) {
    const wsUrl = this.config.baseURL.replace(/^http/, 'ws') + '/ws';
    this.ws = new WebSocket(wsUrl);

    this.ws.on('open', () => {
      console.log(chalk.green('WebSocket connected'));
    });

    this.ws.on('message', (data) => {
      try {
        const parsed = JSON.parse(data.toString());
        if (onMessage) {
          onMessage(parsed);
        } else {
          console.log('Received:', parsed);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    });

    this.ws.on('error', (error) => {
      console.error(chalk.red('WebSocket error:'), error);
    });

    this.ws.on('close', () => {
      console.log(chalk.yellow('WebSocket disconnected'));
    });
  }

  disconnectWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Configuration management
class ConfigManager {
  private configPath: string;

  constructor() {
    this.configPath = path.join(os.homedir(), '.mcp-drone-cli.yaml');
  }

  load(): Config {
    if (fs.existsSync(this.configPath)) {
      const content = fs.readFileSync(this.configPath, 'utf8');
      return yaml.parse(content);
    }
    return {
      baseURL: 'http://localhost:3001',
      timeout: 30000,
    };
  }

  save(config: Config) {
    const content = yaml.stringify(config);
    fs.writeFileSync(this.configPath, content);
  }
}

// Utility functions
function formatTable(data: any[], headers: string[]): string {
  const rows = [headers, ...data.map(row => headers.map(header => row[header] || ''))];
  return table(rows);
}

function formatResponse(response: any): string {
  if (response.success) {
    return chalk.green(`✓ ${response.message}`);
  } else {
    return chalk.red(`✗ ${response.message}`);
  }
}

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString();
}

// Command implementations
async function configureCommand() {
  const configManager = new ConfigManager();
  const currentConfig = configManager.load();

  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'baseURL',
      message: 'MCP Server URL:',
      default: currentConfig.baseURL,
    },
    {
      type: 'input',
      name: 'apiKey',
      message: 'API Key (optional):',
      default: currentConfig.apiKey,
    },
    {
      type: 'input',
      name: 'bearerToken',
      message: 'Bearer Token (optional):',
      default: currentConfig.bearerToken,
    },
    {
      type: 'number',
      name: 'timeout',
      message: 'Request timeout (ms):',
      default: currentConfig.timeout || 30000,
    },
  ]);

  const newConfig = {
    baseURL: answers.baseURL,
    ...(answers.apiKey && { apiKey: answers.apiKey }),
    ...(answers.bearerToken && { bearerToken: answers.bearerToken }),
    timeout: answers.timeout,
  };

  configManager.save(newConfig);
  console.log(chalk.green('Configuration saved successfully!'));
}

async function executeNaturalLanguageCommand(command: string, options: any) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora('Executing command...').start();

  try {
    const response = await client.executeCommand(command, {
      context: options.context ? JSON.parse(options.context) : undefined,
      options: {
        dry_run: options.dryRun || false,
        confirm_before_execution: options.confirm || false,
      },
    });

    spinner.stop();
    
    console.log(formatResponse(response));
    
    if (response.parsed_intent) {
      console.log('\\nParsed Intent:');
      console.log(`  Action: ${response.parsed_intent.action}`);
      console.log(`  Confidence: ${(response.parsed_intent.confidence * 100).toFixed(1)}%`);
      
      if (response.parsed_intent.parameters) {
        console.log('  Parameters:', JSON.stringify(response.parsed_intent.parameters, null, 2));
      }
    }

    if (response.execution_details) {
      console.log('\\nExecution Details:');
      console.log(`  Backend calls: ${response.execution_details.backend_calls?.length || 0}`);
      console.log(`  Execution time: ${response.execution_details.execution_time || 0}s`);
    }
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function executeBatchCommand(commands: string[], options: any) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora('Executing batch commands...').start();

  try {
    const response = await client.executeBatchCommand(commands, {
      mode: options.mode || 'sequential',
      stopOnError: options.stopOnError !== false,
    });

    spinner.stop();
    
    console.log(formatResponse(response));
    
    if (response.summary) {
      console.log('\\nSummary:');
      console.log(`  Total commands: ${response.summary.total_commands}`);
      console.log(`  Successful: ${response.summary.successful_commands}`);
      console.log(`  Failed: ${response.summary.failed_commands}`);
      console.log(`  Total time: ${response.summary.total_execution_time}s`);
    }

    if (response.results && options.verbose) {
      console.log('\\nDetailed Results:');
      response.results.forEach((result: any, index: number) => {
        console.log(`  ${index + 1}. ${formatResponse(result)}`);
      });
    }
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function listDrones(options: any) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora('Fetching drones...').start();

  try {
    const response = options.available 
      ? await client.getAvailableDrones() 
      : await client.getDrones();
    
    spinner.stop();

    if (response.drones.length === 0) {
      console.log(chalk.yellow('No drones found.'));
      return;
    }

    console.log(formatTable(response.drones, ['id', 'name', 'type', 'status']));
    console.log(`\\nTotal: ${response.count} drones`);
    console.log(`Last updated: ${formatTimestamp(response.timestamp)}`);
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function getDroneStatus(droneId: string) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Fetching status for drone ${droneId}...`).start();

  try {
    const response = await client.getDroneStatus(droneId);
    spinner.stop();

    console.log(chalk.blue(`\\nDrone ${droneId} Status:`));
    console.log(`  Connection: ${response.status.connection_status}`);
    console.log(`  Flight: ${response.status.flight_status}`);
    console.log(`  Battery: ${response.status.battery_level}%`);
    console.log(`  Height: ${response.status.height}cm`);
    console.log(`  Temperature: ${response.status.temperature}°C`);
    console.log(`  WiFi Signal: ${response.status.wifi_signal}%`);
    console.log(`  Last updated: ${formatTimestamp(response.timestamp)}`);
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function connectDrone(droneId: string) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Connecting to drone ${droneId}...`).start();

  try {
    const response = await client.connectDrone(droneId);
    spinner.stop();
    console.log(formatResponse(response));
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function disconnectDrone(droneId: string) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Disconnecting from drone ${droneId}...`).start();

  try {
    const response = await client.disconnectDrone(droneId);
    spinner.stop();
    console.log(formatResponse(response));
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function takeoffDrone(droneId: string, height?: number) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Taking off drone ${droneId}...`).start();

  try {
    const response = await client.takeoff(droneId, height);
    spinner.stop();
    console.log(formatResponse(response));
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function landDrone(droneId: string) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Landing drone ${droneId}...`).start();

  try {
    const response = await client.land(droneId);
    spinner.stop();
    console.log(formatResponse(response));
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function moveDrone(droneId: string, direction: string, distance: number, speed?: number) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Moving drone ${droneId} ${direction} ${distance}cm...`).start();

  try {
    const response = await client.moveDrone(droneId, direction, distance, speed);
    spinner.stop();
    console.log(formatResponse(response));
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function rotateDrone(droneId: string, direction: string, angle: number) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Rotating drone ${droneId} ${direction} ${angle}°...`).start();

  try {
    const response = await client.rotateDrone(droneId, direction, angle);
    spinner.stop();
    console.log(formatResponse(response));
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function emergencyStop(droneId: string) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Emergency stop for drone ${droneId}...`).start();

  try {
    const response = await client.emergencyStop(droneId);
    spinner.stop();
    console.log(formatResponse(response));
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function takePhoto(droneId: string, filename?: string, quality?: string) {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora(`Taking photo with drone ${droneId}...`).start();

  try {
    const response = await client.takePhoto(droneId, filename, quality);
    spinner.stop();
    console.log(formatResponse(response));
    
    if (response.photo) {
      console.log(`\\nPhoto saved:`);
      console.log(`  Filename: ${response.photo.filename}`);
      console.log(`  Path: ${response.photo.path}`);
      console.log(`  Size: ${response.photo.size} bytes`);
    }
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function getSystemStatus() {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora('Fetching system status...').start();

  try {
    const response = await client.getSystemStatus();
    spinner.stop();

    console.log(chalk.blue('\\nSystem Status:'));
    console.log(`  MCP Server: ${response.mcp_server.status}`);
    console.log(`  Backend: ${response.backend_system.connection_status}`);
    console.log(`  Connected Drones: ${response.connected_drones}`);
    console.log(`  Active Operations: ${response.active_operations}`);
    console.log(`  Health: ${response.system_health}`);
    console.log(`  Uptime: ${response.mcp_server.uptime}s`);
    console.log(`  Version: ${response.mcp_server.version}`);
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function getHealthCheck() {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  const spinner = ora('Performing health check...').start();

  try {
    const response = await client.getHealthCheck();
    spinner.stop();

    console.log(chalk.blue('\\nHealth Check:'));
    console.log(`  Status: ${response.status}`);
    
    if (response.checks.length > 0) {
      console.log('\\nChecks:');
      response.checks.forEach((check: any) => {
        const icon = check.status === 'pass' ? '✓' : '✗';
        const color = check.status === 'pass' ? chalk.green : chalk.red;
        console.log(`  ${color(icon)} ${check.name}: ${check.message} (${check.response_time}ms)`);
      });
    }
  } catch (error: any) {
    spinner.stop();
    console.error(chalk.red('Error:'), error.message);
    process.exit(1);
  }
}

async function watchEvents() {
  const configManager = new ConfigManager();
  const config = configManager.load();
  const client = new MCPCliClient(config);

  console.log(chalk.blue('Connecting to WebSocket...'));
  
  client.connectWebSocket((data) => {
    console.log(`[${new Date().toISOString()}] ${chalk.yellow('Event:')} ${JSON.stringify(data, null, 2)}`);
  });

  // Keep the process alive
  process.on('SIGINT', () => {
    console.log(chalk.yellow('\\nDisconnecting WebSocket...'));
    client.disconnectWebSocket();
    process.exit(0);
  });

  // Wait indefinitely
  await new Promise(() => {});
}

// Main CLI setup
const program = new Command();

program
  .name('mcp-drone')
  .description('CLI for MCP Drone Control Server')
  .version('1.0.0');

// Configuration
program
  .command('configure')
  .description('Configure MCP CLI settings')
  .action(configureCommand);

// Natural Language Commands
program
  .command('exec <command>')
  .description('Execute natural language command')
  .option('-c, --context <context>', 'Context as JSON string')
  .option('-d, --dry-run', 'Dry run mode')
  .option('--confirm', 'Confirm before execution')
  .action(executeNaturalLanguageCommand);

program
  .command('batch <commands...>')
  .description('Execute multiple natural language commands')
  .option('-m, --mode <mode>', 'Execution mode (sequential|parallel)', 'sequential')
  .option('--no-stop-on-error', 'Continue on error')
  .option('-v, --verbose', 'Verbose output')
  .action(executeBatchCommand);

// Drone Management
program
  .command('drones')
  .description('List drones')
  .option('-a, --available', 'Show only available drones')
  .action(listDrones);

program
  .command('status <droneId>')
  .description('Get drone status')
  .action(getDroneStatus);

program
  .command('connect <droneId>')
  .description('Connect to drone')
  .action(connectDrone);

program
  .command('disconnect <droneId>')
  .description('Disconnect from drone')
  .action(disconnectDrone);

// Flight Control
program
  .command('takeoff <droneId>')
  .description('Takeoff drone')
  .option('-h, --height <height>', 'Target height in cm', parseInt)
  .action(takeoffDrone);

program
  .command('land <droneId>')
  .description('Land drone')
  .action(landDrone);

program
  .command('move <droneId> <direction> <distance>')
  .description('Move drone')
  .option('-s, --speed <speed>', 'Speed in cm/s', parseInt)
  .action(moveDrone);

program
  .command('rotate <droneId> <direction> <angle>')
  .description('Rotate drone')
  .action(rotateDrone);

program
  .command('emergency <droneId>')
  .description('Emergency stop drone')
  .action(emergencyStop);

// Camera
program
  .command('photo <droneId>')
  .description('Take photo')
  .option('-f, --filename <filename>', 'Photo filename')
  .option('-q, --quality <quality>', 'Photo quality (high|medium|low)')
  .action(takePhoto);

// System
program
  .command('system')
  .description('Get system status')
  .action(getSystemStatus);

program
  .command('health')
  .description('Get health check')
  .action(getHealthCheck);

program
  .command('watch')
  .description('Watch real-time events')
  .action(watchEvents);

// Parse arguments
program.parse();