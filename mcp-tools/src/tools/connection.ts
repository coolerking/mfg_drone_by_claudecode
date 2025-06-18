import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';

/**
 * Connection tools for drone connectivity management
 */
export class ConnectionTools {
  private client: FastAPIClient;
  private logger;

  constructor(client: FastAPIClient, logger: Logger) {
    this.client = client;
    this.logger = logger.createComponentLogger('ConnectionTools');
  }

  /**
   * Get all connection tools
   */
  getTools(): Tool[] {
    return [
      this.getDroneConnectTool(),
      this.getDroneDisconnectTool(),
      this.getDroneStatusTool(),
    ];
  }

  /**
   * Tool: Connect to drone
   */
  private getDroneConnectTool(): Tool {
    return {
      name: 'drone_connect',
      description: 'Connect to the Tello EDU drone. This establishes communication with the drone and prepares it for flight operations.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Disconnect from drone
   */
  private getDroneDisconnectTool(): Tool {
    return {
      name: 'drone_disconnect',
      description: 'Safely disconnect from the Tello EDU drone. This terminates the communication link with the drone.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get drone status
   */
  private getDroneStatusTool(): Tool {
    return {
      name: 'drone_status',
      description: 'Get comprehensive status information from the drone including connection state, battery, sensors, and flight data.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Execute connection tool
   */
  async executeTool(name: string, args: unknown): Promise<unknown> {
    this.logger.info(`Executing connection tool: ${name}`, { args });

    try {
      switch (name) {
        case 'drone_connect':
          return await this.executeConnect();
        case 'drone_disconnect':
          return await this.executeDisconnect();
        case 'drone_status':
          return await this.executeStatus();
        default:
          throw new Error(`Unknown connection tool: ${name}`);
      }
    } catch (error) {
      this.logger.error(`Connection tool ${name} failed`, error);
      throw error;
    }
  }

  /**
   * Execute connect command
   */
  private async executeConnect(): Promise<unknown> {
    this.logger.info('Connecting to drone...');
    
    const result = await this.client.connect();
    
    if (result.success) {
      this.logger.info('Successfully connected to drone');
      return {
        success: true,
        message: 'Successfully connected to Tello EDU drone',
        data: result,
      };
    } else {
      this.logger.warn('Failed to connect to drone', result);
      return {
        success: false,
        message: result.message || 'Failed to connect to drone',
        data: result,
      };
    }
  }

  /**
   * Execute disconnect command
   */
  private async executeDisconnect(): Promise<unknown> {
    this.logger.info('Disconnecting from drone...');
    
    const result = await this.client.disconnect();
    
    if (result.success) {
      this.logger.info('Successfully disconnected from drone');
      return {
        success: true,
        message: 'Successfully disconnected from drone',
        data: result,
      };
    } else {
      this.logger.warn('Failed to disconnect from drone', result);
      return {
        success: false,
        message: result.message || 'Failed to disconnect from drone',
        data: result,
      };
    }
  }

  /**
   * Execute status command
   */
  private async executeStatus(): Promise<unknown> {
    this.logger.info('Getting drone status...');
    
    const status = await this.client.getStatus();
    
    this.logger.info('Retrieved drone status', {
      connected: status.connected,
      battery: status.battery,
      height: status.height,
    });
    
    return {
      success: true,
      message: 'Successfully retrieved drone status',
      data: {
        connection: {
          connected: status.connected,
        },
        battery: {
          level: status.battery,
          status: this.getBatteryStatus(status.battery),
        },
        flight: {
          height: status.height,
          flight_time: status.flight_time,
        },
        environment: {
          temperature: status.temperature,
          barometer: status.barometer,
          distance_tof: status.distance_tof,
        },
        sensors: {
          acceleration: status.acceleration,
          velocity: status.velocity,
          attitude: status.attitude,
        },
        summary: this.generateStatusSummary(status),
      },
    };
  }

  /**
   * Get battery status description
   */
  private getBatteryStatus(battery: number): string {
    if (battery >= 50) return 'Good';
    if (battery >= 30) return 'Medium';
    if (battery >= 15) return 'Low';
    return 'Critical';
  }

  /**
   * Generate human-readable status summary
   */
  private generateStatusSummary(status: any): string {
    const parts = [];
    
    if (status.connected) {
      parts.push('🟢 Connected');
    } else {
      parts.push('🔴 Disconnected');
    }
    
    parts.push(`🔋 Battery: ${status.battery}%`);
    
    if (status.height > 0) {
      parts.push(`✈️ Flying at ${status.height}cm`);
    } else {
      parts.push('🛬 On ground');
    }
    
    parts.push(`🌡️ Temperature: ${status.temperature}°C`);
    
    return parts.join(' | ');
  }
}