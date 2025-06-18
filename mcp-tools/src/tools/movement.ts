import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';

/**
 * Movement control tools for drone positioning
 */
export class MovementTools {
  private client: FastAPIClient;
  private logger;

  constructor(client: FastAPIClient, logger: Logger) {
    this.client = client;
    this.logger = logger.createComponentLogger('MovementTools');
  }

  /**
   * Get all movement tools
   */
  getTools(): Tool[] {
    return [
      this.getDroneMoveTool(),
      this.getDroneRotateTool(),
      this.getDroneFlipTool(),
      this.getDroneGoXyzTool(),
      this.getDroneCurveTool(),
      this.getDroneRcControlTool(),
    ];
  }

  /**
   * Tool: Basic directional movement
   */
  private getDroneMoveTool(): Tool {
    return {
      name: 'drone_move',
      description: 'Move the drone in a specific direction by a specified distance. The drone must be flying to execute movement commands.',
      inputSchema: {
        type: 'object',
        properties: {
          direction: {
            type: 'string',
            enum: ['up', 'down', 'left', 'right', 'forward', 'back'],
            description: 'Direction to move the drone',
          },
          distance: {
            type: 'integer',
            minimum: 20,
            maximum: 500,
            description: 'Distance to move in centimeters (20-500cm)',
          },
        },
        required: ['direction', 'distance'],
      },
    };
  }

  /**
   * Tool: Rotate drone
   */
  private getDroneRotateTool(): Tool {
    return {
      name: 'drone_rotate',
      description: 'Rotate the drone clockwise or counter-clockwise by a specified angle.',
      inputSchema: {
        type: 'object',
        properties: {
          direction: {
            type: 'string',
            enum: ['clockwise', 'counter_clockwise'],
            description: 'Rotation direction',
          },
          angle: {
            type: 'integer',
            minimum: 1,
            maximum: 360,
            description: 'Rotation angle in degrees (1-360)',
          },
        },
        required: ['direction', 'angle'],
      },
    };
  }

  /**
   * Tool: Flip drone
   */
  private getDroneFlipTool(): Tool {
    return {
      name: 'drone_flip',
      description: 'Perform a flip maneuver in the specified direction. Warning: Requires sufficient space and battery.',
      inputSchema: {
        type: 'object',
        properties: {
          direction: {
            type: 'string',
            enum: ['left', 'right', 'forward', 'back'],
            description: 'Direction to flip',
          },
        },
        required: ['direction'],
      },
    };
  }

  /**
   * Tool: Go to XYZ coordinates
   */
  private getDroneGoXyzTool(): Tool {
    return {
      name: 'drone_go_xyz',
      description: 'Move the drone to specific XYZ coordinates relative to its current position.',
      inputSchema: {
        type: 'object',
        properties: {
          x: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'X coordinate in centimeters (-500 to 500)',
          },
          y: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'Y coordinate in centimeters (-500 to 500)',
          },
          z: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'Z coordinate in centimeters (-500 to 500)',
          },
          speed: {
            type: 'integer',
            minimum: 10,
            maximum: 100,
            description: 'Movement speed in cm/s (10-100)',
          },
        },
        required: ['x', 'y', 'z', 'speed'],
      },
    };
  }

  /**
   * Tool: Curve flight
   */
  private getDroneCurveTool(): Tool {
    return {
      name: 'drone_curve',
      description: 'Fly in a curve through a waypoint to a destination. Creates smooth curved flight path.',
      inputSchema: {
        type: 'object',
        properties: {
          x1: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'Waypoint X coordinate in centimeters',
          },
          y1: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'Waypoint Y coordinate in centimeters',
          },
          z1: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'Waypoint Z coordinate in centimeters',
          },
          x2: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'Destination X coordinate in centimeters',
          },
          y2: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'Destination Y coordinate in centimeters',
          },
          z2: {
            type: 'integer',
            minimum: -500,
            maximum: 500,
            description: 'Destination Z coordinate in centimeters',
          },
          speed: {
            type: 'integer',
            minimum: 10,
            maximum: 60,
            description: 'Flight speed in cm/s (10-60)',
          },
        },
        required: ['x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'speed'],
      },
    };
  }

  /**
   * Tool: RC Control (real-time)
   */
  private getDroneRcControlTool(): Tool {
    return {
      name: 'drone_rc_control',
      description: 'Send real-time RC control commands for precise movement control. Use for fine adjustments.',
      inputSchema: {
        type: 'object',
        properties: {
          left_right_velocity: {
            type: 'integer',
            minimum: -100,
            maximum: 100,
            description: 'Left/right velocity percentage (-100 to 100, negative = left)',
          },
          forward_backward_velocity: {
            type: 'integer',
            minimum: -100,
            maximum: 100,
            description: 'Forward/backward velocity percentage (-100 to 100, negative = backward)',
          },
          up_down_velocity: {
            type: 'integer',
            minimum: -100,
            maximum: 100,
            description: 'Up/down velocity percentage (-100 to 100, negative = down)',
          },
          yaw_velocity: {
            type: 'integer',
            minimum: -100,
            maximum: 100,
            description: 'Yaw rotation velocity percentage (-100 to 100, negative = counter-clockwise)',
          },
        },
        required: ['left_right_velocity', 'forward_backward_velocity', 'up_down_velocity', 'yaw_velocity'],
      },
    };
  }

  /**
   * Execute movement tool
   */
  async executeTool(name: string, args: unknown): Promise<unknown> {
    this.logger.info(`Executing movement tool: ${name}`, { args });

    try {
      switch (name) {
        case 'drone_move':
          return await this.executeMove(args);
        case 'drone_rotate':
          return await this.executeRotate(args);
        case 'drone_flip':
          return await this.executeFlip(args);
        case 'drone_go_xyz':
          return await this.executeGoXyz(args);
        case 'drone_curve':
          return await this.executeCurve(args);
        case 'drone_rc_control':
          return await this.executeRcControl(args);
        default:
          throw new Error(`Unknown movement tool: ${name}`);
      }
    } catch (error) {
      this.logger.error(`Movement tool ${name} failed`, error);
      throw error;
    }
  }

  /**
   * Execute basic move command
   */
  private async executeMove(args: unknown): Promise<unknown> {
    const schema = z.object({
      direction: z.enum(['up', 'down', 'left', 'right', 'forward', 'back']),
      distance: z.number().int().min(20).max(500),
    });

    const params = schema.parse(args);
    this.logger.info(`Moving ${params.direction} ${params.distance}cm`);

    const result = await this.client.move(params);

    if (result.success) {
      this.logger.info(`Movement completed: ${params.direction} ${params.distance}cm`);
      return {
        success: true,
        message: `Successfully moved ${params.direction} ${params.distance}cm`,
        data: {
          ...result,
          movement: params,
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Movement failed',
        data: result,
      };
    }
  }

  /**
   * Execute rotate command
   */
  private async executeRotate(args: unknown): Promise<unknown> {
    const schema = z.object({
      direction: z.enum(['clockwise', 'counter_clockwise']),
      angle: z.number().int().min(1).max(360),
    });

    const params = schema.parse(args);
    this.logger.info(`Rotating ${params.direction} ${params.angle} degrees`);

    const result = await this.client.rotate(params);

    if (result.success) {
      this.logger.info(`Rotation completed: ${params.direction} ${params.angle}°`);
      return {
        success: true,
        message: `Successfully rotated ${params.direction} ${params.angle} degrees`,
        data: {
          ...result,
          rotation: params,
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Rotation failed',
        data: result,
      };
    }
  }

  /**
   * Execute flip command
   */
  private async executeFlip(args: unknown): Promise<unknown> {
    const schema = z.object({
      direction: z.enum(['left', 'right', 'forward', 'back']),
    });

    const params = schema.parse(args);
    this.logger.info(`Performing flip: ${params.direction}`);

    // Check battery level before flip
    try {
      const battery = await this.client.getBattery();
      if (battery.battery < 30) {
        return {
          success: false,
          message: `Cannot perform flip: Battery too low (${battery.battery}%). Minimum 30% required for flip maneuvers.`,
          error: 'BATTERY_TOO_LOW',
          data: { battery: battery.battery },
        };
      }
    } catch (error) {
      this.logger.warn('Could not check battery before flip', error);
    }

    const result = await this.client.flip(params);

    if (result.success) {
      this.logger.info(`Flip completed: ${params.direction}`);
      return {
        success: true,
        message: `Successfully performed ${params.direction} flip`,
        data: {
          ...result,
          flip: params,
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Flip failed',
        data: result,
      };
    }
  }

  /**
   * Execute go to XYZ coordinates
   */
  private async executeGoXyz(args: unknown): Promise<unknown> {
    const schema = z.object({
      x: z.number().int().min(-500).max(500),
      y: z.number().int().min(-500).max(500),
      z: z.number().int().min(-500).max(500),
      speed: z.number().int().min(10).max(100),
    });

    const params = schema.parse(args);
    this.logger.info(`Moving to coordinates: (${params.x}, ${params.y}, ${params.z}) at ${params.speed}cm/s`);

    const result = await this.client.goXyz(params);

    if (result.success) {
      this.logger.info(`Coordinate movement completed`);
      return {
        success: true,
        message: `Successfully moved to coordinates (${params.x}, ${params.y}, ${params.z})`,
        data: {
          ...result,
          coordinates: params,
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Coordinate movement failed',
        data: result,
      };
    }
  }

  /**
   * Execute curve flight
   */
  private async executeCurve(args: unknown): Promise<unknown> {
    const schema = z.object({
      x1: z.number().int().min(-500).max(500),
      y1: z.number().int().min(-500).max(500),
      z1: z.number().int().min(-500).max(500),
      x2: z.number().int().min(-500).max(500),
      y2: z.number().int().min(-500).max(500),
      z2: z.number().int().min(-500).max(500),
      speed: z.number().int().min(10).max(60),
    });

    const params = schema.parse(args);
    this.logger.info(`Curve flight: waypoint(${params.x1}, ${params.y1}, ${params.z1}) to (${params.x2}, ${params.y2}, ${params.z2})`);

    const result = await this.client.curveXyz(params);

    if (result.success) {
      this.logger.info(`Curve flight completed`);
      return {
        success: true,
        message: `Successfully completed curve flight`,
        data: {
          ...result,
          curve: params,
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Curve flight failed',
        data: result,
      };
    }
  }

  /**
   * Execute RC control
   */
  private async executeRcControl(args: unknown): Promise<unknown> {
    const schema = z.object({
      left_right_velocity: z.number().int().min(-100).max(100),
      forward_backward_velocity: z.number().int().min(-100).max(100),
      up_down_velocity: z.number().int().min(-100).max(100),
      yaw_velocity: z.number().int().min(-100).max(100),
    });

    const params = schema.parse(args);
    this.logger.info(`RC control: LR=${params.left_right_velocity}, FB=${params.forward_backward_velocity}, UD=${params.up_down_velocity}, Yaw=${params.yaw_velocity}`);

    const result = await this.client.rcControl(params);

    if (result.success) {
      this.logger.info(`RC control command sent`);
      return {
        success: true,
        message: `RC control command sent successfully`,
        data: {
          ...result,
          rc_control: params,
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'RC control failed',
        data: result,
      };
    }
  }
}