import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';

/**
 * Flight control tools for basic drone operations
 */
export class FlightTools {
  private client: FastAPIClient;
  private logger;

  constructor(client: FastAPIClient, logger: Logger) {
    this.client = client;
    this.logger = logger.createComponentLogger('FlightTools');
  }

  /**
   * Get all flight control tools
   */
  getTools(): Tool[] {
    return [
      this.getDroneTakeoffTool(),
      this.getDroneLandTool(),
      this.getDroneEmergencyTool(),
      this.getDroneStopTool(),
      this.getDroneGetHeightTool(),
    ];
  }

  /**
   * Tool: Takeoff drone
   */
  private getDroneTakeoffTool(): Tool {
    return {
      name: 'drone_takeoff',
      description: 'Command the drone to takeoff and hover at approximately 0.8-1.2 meters height. The drone must be connected before takeoff.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Land drone
   */
  private getDroneLandTool(): Tool {
    return {
      name: 'drone_land',
      description: 'Command the drone to land safely at its current position. The drone must be flying to execute this command.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Emergency stop
   */
  private getDroneEmergencyTool(): Tool {
    return {
      name: 'drone_emergency',
      description: 'EMERGENCY STOP: Immediately stop all motors and drop the drone. Use only in emergency situations. This will cause the drone to fall!',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Stop/Hover
   */
  private getDroneStopTool(): Tool {
    return {
      name: 'drone_stop',
      description: 'Stop current movement and hover in place. This command makes the drone hold its current position.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get current height
   */
  private getDroneGetHeightTool(): Tool {
    return {
      name: 'drone_get_height',
      description: 'Get the current flight height of the drone in centimeters.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Execute flight control tool
   */
  async executeTool(name: string, args: unknown): Promise<unknown> {
    this.logger.info(`Executing flight tool: ${name}`, { args });

    try {
      switch (name) {
        case 'drone_takeoff':
          return await this.executeTakeoff();
        case 'drone_land':
          return await this.executeLand();
        case 'drone_emergency':
          return await this.executeEmergency();
        case 'drone_stop':
          return await this.executeStop();
        case 'drone_get_height':
          return await this.executeGetHeight();
        default:
          throw new Error(`Unknown flight tool: ${name}`);
      }
    } catch (error) {
      this.logger.error(`Flight tool ${name} failed`, error);
      throw error;
    }
  }

  /**
   * Execute takeoff command
   */
  private async executeTakeoff(): Promise<unknown> {
    this.logger.info('Initiating drone takeoff...');
    
    // Check connection status first
    try {
      const status = await this.client.getStatus();
      if (!status.connected) {
        return {
          success: false,
          message: 'Cannot takeoff: Drone is not connected. Please connect first.',
          error: 'DRONE_NOT_CONNECTED',
        };
      }
      
      if (status.height > 10) {
        return {
          success: false,
          message: `Drone is already flying at ${status.height}cm height.`,
          error: 'ALREADY_FLYING',
          data: { current_height: status.height },
        };
      }
    } catch (error) {
      this.logger.warn('Could not check drone status before takeoff', error);
    }
    
    const result = await this.client.takeoff();
    
    if (result.success) {
      this.logger.info('Drone takeoff successful');
      
      // Get height after takeoff
      try {
        const heightData = await this.client.getHeight();
        return {
          success: true,
          message: 'Takeoff successful! Drone is now hovering.',
          data: {
            result,
            height: heightData.height,
            status: 'flying',
          },
        };
      } catch (error) {
        return {
          success: true,
          message: 'Takeoff successful! Drone is now hovering.',
          data: result,
        };
      }
    } else {
      this.logger.warn('Drone takeoff failed', result);
      return {
        success: false,
        message: result.message || 'Failed to takeoff',
        data: result,
      };
    }
  }

  /**
   * Execute land command
   */
  private async executeLand(): Promise<unknown> {
    this.logger.info('Initiating drone landing...');
    
    // Check if drone is flying
    try {
      const status = await this.client.getStatus();
      if (status.height <= 10) {
        return {
          success: false,
          message: 'Drone is already on the ground.',
          error: 'NOT_FLYING',
          data: { current_height: status.height },
        };
      }
    } catch (error) {
      this.logger.warn('Could not check drone status before landing', error);
    }
    
    const result = await this.client.land();
    
    if (result.success) {
      this.logger.info('Drone landing successful');
      return {
        success: true,
        message: 'Landing successful! Drone has safely landed.',
        data: {
          result,
          status: 'landed',
        },
      };
    } else {
      this.logger.warn('Drone landing failed', result);
      return {
        success: false,
        message: result.message || 'Failed to land',
        data: result,
      };
    }
  }

  /**
   * Execute emergency stop command
   */
  private async executeEmergency(): Promise<unknown> {
    this.logger.warn('EMERGENCY STOP initiated!');
    
    const result = await this.client.emergency();
    
    if (result.success) {
      this.logger.warn('Emergency stop executed - drone motors stopped');
      return {
        success: true,
        message: '⚠️  EMERGENCY STOP executed! All motors stopped. Drone has dropped.',
        data: {
          result,
          status: 'emergency_stopped',
          warning: 'Check drone for damage before next use',
        },
      };
    } else {
      this.logger.error('Emergency stop failed', result);
      return {
        success: false,
        message: 'Failed to execute emergency stop',
        data: result,
      };
    }
  }

  /**
   * Execute stop/hover command
   */
  private async executeStop(): Promise<unknown> {
    this.logger.info('Commanding drone to stop and hover...');
    
    const result = await this.client.stop();
    
    if (result.success) {
      this.logger.info('Drone is now hovering in place');
      
      // Get current height and status
      try {
        const heightData = await this.client.getHeight();
        return {
          success: true,
          message: 'Drone stopped and is hovering in place.',
          data: {
            result,
            height: heightData.height,
            status: 'hovering',
          },
        };
      } catch (error) {
        return {
          success: true,
          message: 'Drone stopped and is hovering in place.',
          data: result,
        };
      }
    } else {
      this.logger.warn('Stop command failed', result);
      return {
        success: false,
        message: result.message || 'Failed to stop drone',
        data: result,
      };
    }
  }

  /**
   * Execute get height command
   */
  private async executeGetHeight(): Promise<unknown> {
    this.logger.info('Getting drone height...');
    
    const heightData = await this.client.getHeight();
    
    this.logger.info(`Drone height: ${heightData.height}cm`);
    
    return {
      success: true,
      message: `Current drone height: ${heightData.height}cm`,
      data: {
        height: heightData.height,
        height_meters: (heightData.height / 100).toFixed(2),
        flight_status: heightData.height > 10 ? 'flying' : 'on_ground',
      },
    };
  }
}