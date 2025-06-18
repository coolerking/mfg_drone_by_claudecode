import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { EnhancedFastAPIClient } from '../bridge/enhanced-api-client';
import type { ToolDefinition } from './registry';

// Validation schemas for connection tools
const EmptyArgsSchema = z.object({});

const ConnectionArgsSchema = z.object({
  timeout: z.number().optional(),
  retries: z.number().optional(),
});

// Create connection tools
export function createConnectionTools(apiClient: EnhancedFastAPIClient): ToolDefinition[] {
  return [
    {
      tool: {
        name: 'drone_connect',
        description: 'Connect to the Tello EDU drone. This establishes communication with the drone and prepares it for flight operations.',
        inputSchema: {
          type: 'object',
          properties: {
            timeout: {
              type: 'number',
              description: 'Connection timeout in milliseconds (optional)',
              minimum: 1000,
              maximum: 30000,
            },
            retries: {
              type: 'number',
              description: 'Number of connection attempts (optional)',
              minimum: 1,
              maximum: 5,
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof ConnectionArgsSchema>) => {
        try {
          const result = await apiClient.connect();
          
          return {
            success: result.success,
            message: result.success 
              ? '🔗 Drone connected successfully! Ready for flight operations.'
              : `❌ Connection failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            data: result.data,
            status: result.success ? 'connected' : 'disconnected',
            nextSteps: result.success 
              ? ['Check drone status with drone_status', 'Perform takeoff with drone_takeoff']
              : ['Check drone power and WiFi connection', 'Retry connection']
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Connection error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            troubleshooting: [
              'Ensure drone is powered on',
              'Check WiFi connection to drone',
              'Verify drone is in range',
              'Check for interference'
            ]
          };
        }
      },
      validator: ConnectionArgsSchema,
      category: 'connection',
      description: 'Establishes communication link with Tello EDU drone',
      examples: [
        'drone_connect() - Connect with default settings',
        'drone_connect({"timeout": 10000}) - Connect with 10 second timeout'
      ],
    },

    {
      tool: {
        name: 'drone_disconnect',
        description: 'Safely disconnect from the Tello EDU drone. This terminates the communication link and ensures proper shutdown.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof EmptyArgsSchema>) => {
        try {
          const result = await apiClient.disconnect();
          
          return {
            success: result.success,
            message: result.success 
              ? '🔌 Drone disconnected successfully. Communication terminated.'
              : `❌ Disconnection failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            data: result.data,
            status: 'disconnected',
            warning: result.success 
              ? 'Drone is no longer under remote control'
              : 'Manual intervention may be required'
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Disconnection error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            recommendation: 'Check drone status and power cycle if necessary'
          };
        }
      },
      validator: EmptyArgsSchema,
      category: 'connection',
      description: 'Safely terminates drone communication link',
      examples: [
        'drone_disconnect() - Safely disconnect from drone'
      ],
    },

    {
      tool: {
        name: 'drone_status',
        description: 'Get comprehensive drone status including connection state, battery level, flight status, and system health.',
        inputSchema: {
          type: 'object',
          properties: {
            detailed: {
              type: 'boolean',
              description: 'Whether to include detailed system information',
              default: false,
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { detailed?: boolean }) => {
        try {
          const result = await apiClient.getStatus();
          const healthStatus = apiClient.getHealthStatus();
          const performanceMetrics = apiClient.getPerformanceMetrics();
          
          const baseResponse = {
            success: result.success,
            message: result.success 
              ? '📊 Drone status retrieved successfully'
              : `❌ Status check failed: ${result.message}`,
            timestamp: new Date().toISOString(),
            status: result.data,
            connection: {
              healthy: healthStatus.isHealthy,
              lastCheck: healthStatus.lastCheck?.toISOString(),
            },
          };

          if (args.detailed) {
            return {
              ...baseResponse,
              performance: {
                averageResponseTime: Math.round(
                  Object.values(performanceMetrics).reduce((sum, m) => sum + m.avg, 0) / 
                  Math.max(Object.keys(performanceMetrics).length, 1)
                ),
                endpointMetrics: performanceMetrics,
              },
              systemHealth: {
                apiConnectivity: healthStatus.isHealthy ? 'good' : 'degraded',
                lastHealthCheck: healthStatus.lastCheck?.toISOString(),
              },
            };
          }

          return baseResponse;
        } catch (error) {
          return {
            success: false,
            message: `❌ Status check error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            recommendation: 'Check drone connection and try reconnecting if necessary'
          };
        }
      },
      validator: z.object({
        detailed: z.boolean().optional(),
      }),
      category: 'connection',
      description: 'Retrieves comprehensive drone status and health information',
      examples: [
        'drone_status() - Get basic drone status',
        'drone_status({"detailed": true}) - Get detailed status with performance metrics'
      ],
    },
  ];
}