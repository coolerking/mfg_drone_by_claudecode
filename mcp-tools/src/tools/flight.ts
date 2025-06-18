import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { EnhancedFastAPIClient } from '../bridge/enhanced-api-client';
import type { ToolDefinition } from './registry';

// Validation schemas for flight tools
const EmptyArgsSchema = z.object({});

const HeightArgsSchema = z.object({
  unit: z.enum(['cm', 'm']).optional().default('cm'),
});

// Create flight control tools
export function createFlightTools(apiClient: EnhancedFastAPIClient): ToolDefinition[] {
  return [
    {
      tool: {
        name: 'drone_takeoff',
        description: 'Make the drone take off and hover at approximately 0.8-1.2 meters height. Drone must be connected before takeoff.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof EmptyArgsSchema>) => {
        try {
          const result = await apiClient.takeoff();
          
          return {
            success: result.success,
            message: result.success 
              ? '🚁 Takeoff successful! Drone is now hovering and ready for flight commands.'
              : `❌ Takeoff failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            data: result.data,
            flightStatus: result.success ? 'flying' : 'grounded',
            safetyReminder: result.success 
              ? 'Drone is now airborne. Maintain visual contact and be ready to land if needed.'
              : undefined,
            nextSteps: result.success 
              ? ['Use movement commands for flight control', 'Monitor battery level', 'Land safely when done']
              : ['Check drone status', 'Ensure sufficient battery', 'Retry takeoff if safe']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Takeoff error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            flightStatus: 'grounded',
            troubleshooting: [
              'Check drone connection status',
              'Ensure sufficient battery (>20%)',
              'Verify clear takeoff area',
              'Check for propeller obstructions'
            ]
          };
        }
      },
      validator: EmptyArgsSchema,
      category: 'flight',
      description: 'Initiates automatic takeoff to hovering position',
      examples: [
        'drone_takeoff() - Take off and hover at safe height'
      ],
    },

    {
      tool: {
        name: 'drone_land',
        description: 'Make the drone land safely at its current position. This is the safest way to end flight operations.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof EmptyArgsSchema>) => {
        try {
          const result = await apiClient.land();
          
          return {
            success: result.success,
            message: result.success 
              ? '🛬 Landing successful! Drone is now safely on the ground.'
              : `❌ Landing failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            data: result.data,
            flightStatus: result.success ? 'grounded' : 'unknown',
            safetyNote: result.success 
              ? 'Drone has landed safely. Props have stopped spinning.'
              : 'Landing may not be complete. Check drone visually.',
            nextSteps: result.success 
              ? ['Flight operations complete', 'Disconnect from drone if done', 'Check battery for next flight']
              : ['Verify drone position', 'Use emergency stop if needed', 'Manual intervention may be required']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Landing error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            flightStatus: 'unknown',
            emergencyAction: 'Consider using drone_emergency if drone is unresponsive',
            troubleshooting: [
              'Check drone connection',
              'Verify landing area is clear',
              'Use emergency stop if necessary',
              'Manual recovery may be needed'
            ]
          };
        }
      },
      validator: EmptyArgsSchema,
      category: 'flight',
      description: 'Initiates safe landing procedure',
      examples: [
        'drone_land() - Land drone safely at current position'
      ],
    },

    {
      tool: {
        name: 'drone_emergency',
        description: 'EMERGENCY STOP: Immediately stops all motors and makes the drone drop. Use only in emergency situations when normal landing is not possible.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof EmptyArgsSchema>) => {
        try {
          const result = await apiClient.emergency();
          
          return {
            success: result.success,
            message: result.success 
              ? '🚨 EMERGENCY STOP ACTIVATED! Motors stopped immediately.'
              : `❌ Emergency stop failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            data: result.data,
            flightStatus: 'emergency_stopped',
            criticalWarning: result.success 
              ? 'DRONE HAS DROPPED! Check for damage before next use.'
              : 'Emergency stop may have failed. Manual intervention required.',
            immediateActions: result.success 
              ? ['Check drone for physical damage', 'Ensure area is safe', 'Power cycle drone before next use']
              : ['Manually power off drone', 'Ensure area safety', 'Contact technical support'],
            note: 'Emergency stop causes drone to drop immediately without controlled landing'
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Emergency stop error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            flightStatus: 'unknown',
            criticalAction: 'MANUALLY POWER OFF DRONE IMMEDIATELY',
            emergencyContacts: 'Contact technical support or experienced operator'
          };
        }
      },
      validator: EmptyArgsSchema,
      category: 'flight',
      description: 'Emergency motor stop - drone will drop immediately',
      examples: [
        'drone_emergency() - Emergency stop all motors (USE WITH CAUTION)'
      ],
    },

    {
      tool: {
        name: 'drone_stop',
        description: 'Stop drone movement and enter hover mode at current position. Different from emergency stop - this maintains flight.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof EmptyArgsSchema>) => {
        try {
          // Using move with zero distance to stop movement
          const result = await apiClient.move('up', 0);
          
          return {
            success: result.success,
            message: result.success 
              ? '⏹️ Drone stopped and hovering at current position.'
              : `❌ Stop command failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            data: result.data,
            flightStatus: result.success ? 'hovering' : 'unknown',
            position: 'Maintaining current altitude and position',
            nextSteps: result.success 
              ? ['Drone is stable and ready for next command', 'Use movement commands or land safely']
              : ['Check drone status', 'Try alternative control method']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Stop command error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            flightStatus: 'unknown',
            recommendation: 'Check drone connection and consider landing if unresponsive'
          };
        }
      },
      validator: EmptyArgsSchema,
      category: 'flight',
      description: 'Stops drone movement and maintains hover at current position',
      examples: [
        'drone_stop() - Stop movement and hover in place'
      ],
    },

    {
      tool: {
        name: 'drone_get_height',
        description: 'Get the current height/altitude of the drone above ground level.',
        inputSchema: {
          type: 'object',
          properties: {
            unit: {
              type: 'string',
              enum: ['cm', 'm'],
              description: 'Unit for height measurement (cm or m)',
              default: 'cm',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof HeightArgsSchema>) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data) {
            throw new Error(result.message || 'No sensor data available');
          }

          const heightCm = result.data.height || 0;
          const heightInUnit = args.unit === 'm' ? heightCm / 100 : heightCm;

          return {
            success: true,
            message: `📏 Current drone height: ${heightInUnit.toFixed(args.unit === 'm' ? 2 : 0)}${args.unit}`,
            timestamp: new Date().toISOString(),
            height: {
              value: heightInUnit,
              unit: args.unit,
              rawCm: heightCm,
            },
            status: this.getHeightStatus(heightCm),
            safetyInfo: this.getHeightSafetyInfo(heightCm),
            data: result.data
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Height measurement error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            recommendation: 'Check drone connection and sensor functionality'
          };
        }
      },
      validator: HeightArgsSchema,
      category: 'flight',
      description: 'Measures current drone altitude above ground',
      examples: [
        'drone_get_height() - Get height in centimeters',
        'drone_get_height({"unit": "m"}) - Get height in meters'
      ],
    },
  ];
}

// Helper functions for height analysis
function getHeightStatus(heightCm: number): string {
  if (heightCm < 30) return 'very_low';
  if (heightCm < 100) return 'low';
  if (heightCm < 300) return 'normal';
  if (heightCm < 500) return 'high';
  return 'very_high';
}

function getHeightSafetyInfo(heightCm: number): {
  level: 'safe' | 'caution' | 'warning';
  message: string;
} {
  if (heightCm < 30) {
    return {
      level: 'warning',
      message: 'Very low altitude - risk of ground collision. Consider gaining altitude.'
    };
  }
  if (heightCm < 50) {
    return {
      level: 'caution',
      message: 'Low altitude - be aware of obstacles and ground proximity.'
    };
  }
  if (heightCm > 400) {
    return {
      level: 'warning',
      message: 'High altitude - regulatory limits may apply. Consider descending.'
    };
  }
  return {
    level: 'safe',
    message: 'Altitude is within safe operating range.'
  };
}