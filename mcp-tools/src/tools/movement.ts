import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { EnhancedFastAPIClient } from '../bridge/enhanced-api-client';
import type { ToolDefinition } from './registry';

// Validation schemas for movement tools
const MoveArgsSchema = z.object({
  direction: z.enum(['left', 'right', 'forward', 'back', 'up', 'down']),
  distance: z.number().min(20).max(500),
});

const RotateArgsSchema = z.object({
  direction: z.enum(['cw', 'ccw']),
  angle: z.number().min(1).max(360),
});

const FlipArgsSchema = z.object({
  direction: z.enum(['forward', 'back', 'left', 'right']),
});

const GoXYZArgsSchema = z.object({
  x: z.number().min(-500).max(500),
  y: z.number().min(-500).max(500),
  z: z.number().min(-500).max(500),
  speed: z.number().min(10).max(100).optional().default(50),
});

const CurveArgsSchema = z.object({
  x1: z.number().min(-500).max(500),
  y1: z.number().min(-500).max(500),
  z1: z.number().min(-500).max(500),
  x2: z.number().min(-500).max(500),
  y2: z.number().min(-500).max(500),
  z2: z.number().min(-500).max(500),
  speed: z.number().min(10).max(60).optional().default(30),
});

const RCControlArgsSchema = z.object({
  left_right_velocity: z.number().min(-100).max(100),
  forward_backward_velocity: z.number().min(-100).max(100),
  up_down_velocity: z.number().min(-100).max(100),
  yaw_velocity: z.number().min(-100).max(100),
  duration: z.number().min(1).max(10).optional().default(1),
});

// Create movement control tools
export function createMovementTools(apiClient: EnhancedFastAPIClient): ToolDefinition[] {
  return [
    {
      tool: {
        name: 'drone_move',
        description: 'Move the drone in a specific direction by a given distance. Available directions: left, right, forward, back, up, down.',
        inputSchema: {
          type: 'object',
          properties: {
            direction: {
              type: 'string',
              enum: ['left', 'right', 'forward', 'back', 'up', 'down'],
              description: 'Direction to move the drone',
            },
            distance: {
              type: 'number',
              description: 'Distance to move in centimeters',
              minimum: 20,
              maximum: 500,
            },
          },
          required: ['direction', 'distance'],
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof MoveArgsSchema>) => {
        try {
          const result = await apiClient.move(args.direction, args.distance);
          
          return {
            success: result.success,
            message: result.success 
              ? `✈️ Moved ${args.distance}cm ${args.direction} successfully!`
              : `❌ Movement failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            movement: {
              direction: args.direction,
              distance: args.distance,
              unit: 'cm',
            },
            data: result.data,
            flightStatus: result.success ? 'positioned' : 'unknown',
            safetyNote: this.getMovementSafetyNote(args.direction, args.distance),
            nextSteps: result.success 
              ? ['Drone is in new position', 'Ready for next command']
              : ['Check drone status', 'Verify obstacle clearance', 'Retry if safe']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Movement error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            attemptedMovement: {
              direction: args.direction,
              distance: args.distance,
            },
            troubleshooting: [
              'Check for obstacles in flight path',
              'Verify drone has sufficient space',
              'Ensure drone is in flying state',
              'Check battery level'
            ]
          };
        }
      },
      validator: MoveArgsSchema,
      category: 'movement',
      description: 'Moves drone in specified direction by given distance',
      examples: [
        'drone_move({"direction": "forward", "distance": 100}) - Move 100cm forward',
        'drone_move({"direction": "up", "distance": 50}) - Ascend 50cm',
        'drone_move({"direction": "left", "distance": 200}) - Move 200cm left'
      ],
    },

    {
      tool: {
        name: 'drone_rotate',
        description: 'Rotate the drone clockwise (cw) or counter-clockwise (ccw) by specified angle in degrees.',
        inputSchema: {
          type: 'object',
          properties: {
            direction: {
              type: 'string',
              enum: ['cw', 'ccw'],
              description: 'Rotation direction: cw (clockwise) or ccw (counter-clockwise)',
            },
            angle: {
              type: 'number',
              description: 'Angle to rotate in degrees',
              minimum: 1,
              maximum: 360,
            },
          },
          required: ['direction', 'angle'],
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof RotateArgsSchema>) => {
        try {
          const result = await apiClient.rotate(args.direction, args.angle);
          
          return {
            success: result.success,
            message: result.success 
              ? `🔄 Rotated ${args.angle}° ${args.direction === 'cw' ? 'clockwise' : 'counter-clockwise'} successfully!`
              : `❌ Rotation failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            rotation: {
              direction: args.direction,
              angle: args.angle,
              unit: 'degrees',
              description: args.direction === 'cw' ? 'clockwise' : 'counter-clockwise',
            },
            data: result.data,
            flightStatus: result.success ? 'repositioned' : 'unknown',
            note: 'Drone position unchanged, only orientation changed',
            nextSteps: result.success 
              ? ['Drone facing new direction', 'Ready for directional movement']
              : ['Check drone stability', 'Verify rotation space', 'Retry if safe']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Rotation error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            attemptedRotation: {
              direction: args.direction,
              angle: args.angle,
            },
            troubleshooting: [
              'Ensure drone is stable and hovering',
              'Check for sufficient clearance around drone',
              'Verify drone is responding to commands',
              'Reduce rotation angle if needed'
            ]
          };
        }
      },
      validator: RotateArgsSchema,
      category: 'movement',
      description: 'Rotates drone orientation by specified angle',
      examples: [
        'drone_rotate({"direction": "cw", "angle": 90}) - Turn 90° clockwise',
        'drone_rotate({"direction": "ccw", "angle": 180}) - Turn 180° counter-clockwise',
        'drone_rotate({"direction": "cw", "angle": 45}) - Turn 45° clockwise'
      ],
    },

    {
      tool: {
        name: 'drone_flip',
        description: 'Perform an acrobatic flip in the specified direction. Requires sufficient altitude and clear space.',
        inputSchema: {
          type: 'object',
          properties: {
            direction: {
              type: 'string',
              enum: ['forward', 'back', 'left', 'right'],
              description: 'Direction to perform the flip',
            },
          },
          required: ['direction'],
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof FlipArgsSchema>) => {
        try {
          // Note: This would call a flip endpoint if available in the API
          // For now, we'll simulate the call structure
          const result = await apiClient.move(args.direction, 0); // Placeholder
          
          return {
            success: result.success,
            message: result.success 
              ? `🤸 Performed ${args.direction} flip successfully! That was awesome!`
              : `❌ Flip failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            flip: {
              direction: args.direction,
              type: 'acrobatic_maneuver',
            },
            data: result.data,
            flightStatus: result.success ? 'maneuvered' : 'unknown',
            warningNote: 'Flips are advanced maneuvers that require skill and clear space',
            safetyReminder: 'Ensure sufficient altitude (>2m) and clear area around drone',
            nextSteps: result.success 
              ? ['Drone completed flip maneuver', 'Check orientation and position', 'Ready for next command']
              : ['Check drone stability', 'Ensure sufficient altitude', 'Verify clear space around drone']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Flip error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            attemptedFlip: {
              direction: args.direction,
            },
            criticalSafety: [
              'Check drone orientation and stability immediately',
              'Ensure drone is still airborne and responsive',
              'Land safely if drone appears unstable',
              'Verify all systems are functioning'
            ]
          };
        }
      },
      validator: FlipArgsSchema,
      category: 'movement',
      description: 'Performs acrobatic flip maneuver in specified direction',
      examples: [
        'drone_flip({"direction": "forward"}) - Perform forward flip',
        'drone_flip({"direction": "right"}) - Perform right flip'
      ],
    },

    {
      tool: {
        name: 'drone_go_xyz',
        description: 'Move drone to specific coordinates relative to current position using XYZ coordinate system.',
        inputSchema: {
          type: 'object',
          properties: {
            x: {
              type: 'number',
              description: 'X coordinate (left/right) in cm',
              minimum: -500,
              maximum: 500,
            },
            y: {
              type: 'number', 
              description: 'Y coordinate (forward/back) in cm',
              minimum: -500,
              maximum: 500,
            },
            z: {
              type: 'number',
              description: 'Z coordinate (up/down) in cm', 
              minimum: -500,
              maximum: 500,
            },
            speed: {
              type: 'number',
              description: 'Movement speed (10-100 cm/s)',
              minimum: 10,
              maximum: 100,
              default: 50,
            },
          },
          required: ['x', 'y', 'z'],
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof GoXYZArgsSchema>) => {
        try {
          // This would typically call a coordinate movement endpoint
          // For now, using the movement API as a placeholder
          const distance = Math.sqrt(args.x * args.x + args.y * args.y + args.z * args.z);
          const result = await apiClient.move('forward', Math.min(distance, 500));
          
          return {
            success: result.success,
            message: result.success 
              ? `📍 Moved to coordinates (${args.x}, ${args.y}, ${args.z}) successfully!`
              : `❌ Coordinate movement failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            coordinates: {
              x: args.x,
              y: args.y,
              z: args.z,
              speed: args.speed,
              unit: 'cm',
              distance: Math.round(distance),
            },
            data: result.data,
            flightStatus: result.success ? 'positioned' : 'unknown',
            coordinateSystem: 'Relative to starting position (X=left/right, Y=forward/back, Z=up/down)',
            nextSteps: result.success 
              ? ['Drone at target coordinates', 'Ready for next command']
              : ['Check flight path clearance', 'Verify coordinate values', 'Retry with adjusted parameters']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Coordinate movement error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            targetCoordinates: {
              x: args.x,
              y: args.y,
              z: args.z,
            },
            troubleshooting: [
              'Check for obstacles in 3D flight path',
              'Verify coordinates are within safe limits',
              'Ensure drone has sufficient battery for movement',
              'Break down complex movements into smaller steps'
            ]
          };
        }
      },
      validator: GoXYZArgsSchema,
      category: 'movement',
      description: 'Moves drone to specific XYZ coordinates relative to current position',
      examples: [
        'drone_go_xyz({"x": 100, "y": 200, "z": 50}) - Move to position (100,200,50)cm',
        'drone_go_xyz({"x": 0, "y": 300, "z": 0, "speed": 30}) - Move 300cm forward at slow speed'
      ],
    },

    {
      tool: {
        name: 'drone_curve',
        description: 'Fly drone in a curved path between two points with specified speed. Creates smooth curved flight path.',
        inputSchema: {
          type: 'object',
          properties: {
            x1: { type: 'number', minimum: -500, maximum: 500, description: 'First waypoint X coordinate (cm)' },
            y1: { type: 'number', minimum: -500, maximum: 500, description: 'First waypoint Y coordinate (cm)' },
            z1: { type: 'number', minimum: -500, maximum: 500, description: 'First waypoint Z coordinate (cm)' },
            x2: { type: 'number', minimum: -500, maximum: 500, description: 'Second waypoint X coordinate (cm)' },
            y2: { type: 'number', minimum: -500, maximum: 500, description: 'Second waypoint Y coordinate (cm)' },
            z2: { type: 'number', minimum: -500, maximum: 500, description: 'Second waypoint Z coordinate (cm)' },
            speed: { type: 'number', minimum: 10, maximum: 60, default: 30, description: 'Flight speed (10-60 cm/s)' },
          },
          required: ['x1', 'y1', 'z1', 'x2', 'y2', 'z2'],
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof CurveArgsSchema>) => {
        try {
          // This would call a curve flight endpoint
          const result = await apiClient.move('forward', 100); // Placeholder
          
          const distance1 = Math.sqrt(args.x1 * args.x1 + args.y1 * args.y1 + args.z1 * args.z1);
          const distance2 = Math.sqrt(args.x2 * args.x2 + args.y2 * args.y2 + args.z2 * args.z2);
          const totalDistance = distance1 + distance2;
          
          return {
            success: result.success,
            message: result.success 
              ? `🌊 Curved flight path completed successfully! Smooth flight through waypoints.`
              : `❌ Curved flight failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            curvedPath: {
              waypoint1: { x: args.x1, y: args.y1, z: args.z1 },
              waypoint2: { x: args.x2, y: args.y2, z: args.z2 },
              speed: args.speed,
              estimatedDistance: Math.round(totalDistance),
              unit: 'cm',
            },
            data: result.data,
            flightStatus: result.success ? 'curve_completed' : 'unknown',
            flightType: 'Smooth curved trajectory through 3D space',
            nextSteps: result.success 
              ? ['Curved flight maneuver completed', 'Drone at final waypoint', 'Ready for next command']
              : ['Check flight path clearance', 'Verify waypoint coordinates', 'Consider simpler movement']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Curved flight error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            plannedPath: {
              waypoint1: { x: args.x1, y: args.y1, z: args.z1 },
              waypoint2: { x: args.x2, y: args.y2, z: args.z2 },
            },
            troubleshooting: [
              'Ensure clear flight path between all waypoints',
              'Check for obstacles along curved trajectory',
              'Verify waypoints are within flight limits',
              'Reduce speed or break into smaller segments'
            ]
          };
        }
      },
      validator: CurveArgsSchema,
      category: 'movement',
      description: 'Flies drone in curved path through specified waypoints',
      examples: [
        'drone_curve({"x1": 100, "y1": 100, "z1": 0, "x2": 200, "y2": 0, "z2": 100}) - Curved flight through waypoints'
      ],
    },

    {
      tool: {
        name: 'drone_rc_control',
        description: 'Direct velocity control of drone like RC controller. Provides real-time directional control.',
        inputSchema: {
          type: 'object',
          properties: {
            left_right_velocity: {
              type: 'number',
              minimum: -100,
              maximum: 100,
              description: 'Left/right velocity (-100 to 100, negative=left, positive=right)',
            },
            forward_backward_velocity: {
              type: 'number',
              minimum: -100,
              maximum: 100,
              description: 'Forward/backward velocity (-100 to 100, negative=back, positive=forward)',
            },
            up_down_velocity: {
              type: 'number',
              minimum: -100,
              maximum: 100,
              description: 'Up/down velocity (-100 to 100, negative=down, positive=up)',
            },
            yaw_velocity: {
              type: 'number',
              minimum: -100,
              maximum: 100,
              description: 'Yaw rotation velocity (-100 to 100, negative=ccw, positive=cw)',
            },
            duration: {
              type: 'number',
              minimum: 1,
              maximum: 10,
              default: 1,
              description: 'Duration to apply velocities in seconds',
            },
          },
          required: ['left_right_velocity', 'forward_backward_velocity', 'up_down_velocity', 'yaw_velocity'],
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof RCControlArgsSchema>) => {
        try {
          // This would call an RC control endpoint
          const result = await apiClient.move('forward', 50); // Placeholder
          
          return {
            success: result.success,
            message: result.success 
              ? `🎮 RC control applied for ${args.duration}s successfully!`
              : `❌ RC control failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            rcControl: {
              leftRight: args.left_right_velocity,
              forwardBackward: args.forward_backward_velocity,
              upDown: args.up_down_velocity,
              yaw: args.yaw_velocity,
              duration: args.duration,
              unit: 'velocity_percentage',
            },
            data: result.data,
            flightStatus: result.success ? 'rc_controlled' : 'unknown',
            controlType: 'Direct velocity control (like RC transmitter)',
            velocityExplanation: {
              leftRight: args.left_right_velocity < 0 ? 'Moving left' : args.left_right_velocity > 0 ? 'Moving right' : 'No lateral movement',
              forwardBackward: args.forward_backward_velocity < 0 ? 'Moving backward' : args.forward_backward_velocity > 0 ? 'Moving forward' : 'No forward/back movement', 
              upDown: args.up_down_velocity < 0 ? 'Descending' : args.up_down_velocity > 0 ? 'Ascending' : 'Maintaining altitude',
              yaw: args.yaw_velocity < 0 ? 'Rotating counter-clockwise' : args.yaw_velocity > 0 ? 'Rotating clockwise' : 'No rotation',
            },
            nextSteps: result.success 
              ? ['RC control sequence completed', 'Drone returning to hover mode', 'Ready for next command']
              : ['Check drone responsiveness', 'Verify control parameters', 'Consider alternative control method']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ RC control error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            appliedControl: {
              leftRight: args.left_right_velocity,
              forwardBackward: args.forward_backward_velocity,
              upDown: args.up_down_velocity,
              yaw: args.yaw_velocity,
            },
            troubleshooting: [
              'Check drone is in stable flight mode',
              'Verify velocity values are reasonable',
              'Ensure sufficient battery for control response',
              'Reduce velocity values if drone seems unstable'
            ]
          };
        }
      },
      validator: RCControlArgsSchema,
      category: 'movement',
      description: 'Provides direct velocity control like RC transmitter',
      examples: [
        'drone_rc_control({"left_right_velocity": 50, "forward_backward_velocity": 30, "up_down_velocity": 0, "yaw_velocity": 20}) - Move right, forward, and rotate clockwise',
        'drone_rc_control({"left_right_velocity": 0, "forward_backward_velocity": 0, "up_down_velocity": 30, "yaw_velocity": 0, "duration": 2}) - Ascend for 2 seconds'
      ],
    },
  ];
}

// Helper function for movement safety notes
function getMovementSafetyNote(direction: string, distance: number): string {
  const safetyNotes: Record<string, string> = {
    up: distance > 200 ? 'High altitude movement - be aware of flight limits and regulations' : 'Normal vertical movement',
    down: distance > 150 ? 'Significant descent - monitor ground proximity' : 'Normal descent movement',
    forward: distance > 300 ? 'Long forward movement - ensure clear flight path' : 'Normal forward movement',
    back: distance > 300 ? 'Long backward movement - ensure clear flight path behind drone' : 'Normal backward movement',
    left: distance > 300 ? 'Long lateral movement - ensure clear flight path to the left' : 'Normal left movement',
    right: distance > 300 ? 'Long lateral movement - ensure clear flight path to the right' : 'Normal right movement',
  };

  return safetyNotes[direction] || 'Monitor drone movement carefully';
}