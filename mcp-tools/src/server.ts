/**
 * MCP Drone Server
 * 
 * Core MCP server implementation that handles tool registration,
 * request processing, and communication with the FastAPI backend.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
  CallToolResult,
  ListToolsResult,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

import { FastAPIClient } from './bridge/api-client.js';
import { toolRegistry } from './tools/registry.js';
import { ServerConfig } from './types/config.js';
import { logger } from './utils/logger.js';

export class MCPDroneServer {
  private server: Server;
  private transport: StdioServerTransport;
  private apiClient: FastAPIClient;
  private config: ServerConfig;
  private isInitialized = false;

  constructor(config: ServerConfig) {
    this.config = config;
    this.server = new Server(
      {
        name: 'mfg-drone-mcp-server',
        version: '1.0.0',
        description: 'MCP server for MFG Drone Backend API integration',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.transport = new StdioServerTransport();
    this.apiClient = new FastAPIClient(config.backend);
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) {
      logger.warn('Server already initialized');
      return;
    }

    try {
      // Initialize API client
      await this.apiClient.initialize();
      logger.info('FastAPI client initialized');

      // Register MCP handlers
      this.registerHandlers();
      logger.info('MCP handlers registered');

      // Connect server to transport
      await this.server.connect(this.transport);
      logger.info('MCP server connected to transport');

      this.isInitialized = true;
      logger.info('MCP Drone Server initialization complete');
    } catch (error) {
      logger.error('Failed to initialize MCP server:', error);
      throw error;
    }
  }

  async shutdown(): Promise<void> {
    if (!this.isInitialized) {
      return;
    }

    try {
      await this.server.close();
      await this.apiClient.close();
      logger.info('MCP Drone Server shutdown complete');
    } catch (error) {
      logger.error('Error during shutdown:', error);
      throw error;
    }
  }

  private registerHandlers(): void {
    // Handle tool listing
    this.server.setRequestHandler(ListToolsRequestSchema, async (): Promise<ListToolsResult> => {
      logger.debug('Handling list_tools request');
      return {
        tools: toolRegistry.getAllTools(),
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request): Promise<CallToolResult> => {
      const { name, arguments: args } = request.params;
      
      logger.info('Handling tool call', { toolName: name, arguments: args });

      try {
        // Get the tool from registry
        const tool = toolRegistry.getTool(name);
        if (!tool) {
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Tool '${name}' not found`
          );
        }

        // Validate arguments using the tool's schema
        const validatedArgs = toolRegistry.validateArguments(name, args);

        // Execute the tool
        const result = await this.executeToolCall(name, validatedArgs);

        logger.info('Tool call completed successfully', { toolName: name });
        return result;
      } catch (error) {
        logger.error('Tool call failed', { toolName: name, error });
        
        if (error instanceof McpError) {
          throw error;
        }
        
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    });
  }

  private async executeToolCall(toolName: string, args: Record<string, unknown>): Promise<CallToolResult> {
    // Route tool calls to appropriate handlers
    switch (toolName) {
      // Connection tools
      case 'drone_connect':
        return this.handleDroneConnect(args);
      case 'drone_disconnect':
        return this.handleDroneDisconnect(args);
      case 'drone_status':
        return this.handleDroneStatus(args);

      // Flight control tools
      case 'drone_takeoff':
        return this.handleDroneTakeoff(args);
      case 'drone_land':
        return this.handleDroneLand(args);
      case 'drone_emergency':
        return this.handleDroneEmergency(args);

      default:
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Tool handler not implemented: ${toolName}`
        );
    }
  }

  // Connection tool handlers
  private async handleDroneConnect(args: Record<string, unknown>): Promise<CallToolResult> {
    try {
      const response = await this.apiClient.connect();
      return {
        content: [
          {
            type: 'text',
            text: `Drone connection ${response.success ? 'successful' : 'failed'}: ${response.message}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to connect to drone: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async handleDroneDisconnect(args: Record<string, unknown>): Promise<CallToolResult> {
    try {
      const response = await this.apiClient.disconnect();
      return {
        content: [
          {
            type: 'text',
            text: `Drone disconnection ${response.success ? 'successful' : 'failed'}: ${response.message}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to disconnect from drone: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async handleDroneStatus(args: Record<string, unknown>): Promise<CallToolResult> {
    try {
      const response = await this.apiClient.getStatus();
      return {
        content: [
          {
            type: 'text',
            text: `Drone status: ${JSON.stringify(response.data, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to get drone status: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  // Flight control tool handlers
  private async handleDroneTakeoff(args: Record<string, unknown>): Promise<CallToolResult> {
    try {
      const response = await this.apiClient.takeoff();
      return {
        content: [
          {
            type: 'text',
            text: `Takeoff ${response.success ? 'successful' : 'failed'}: ${response.message}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to takeoff: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async handleDroneLand(args: Record<string, unknown>): Promise<CallToolResult> {
    try {
      const response = await this.apiClient.land();
      return {
        content: [
          {
            type: 'text',
            text: `Landing ${response.success ? 'successful' : 'failed'}: ${response.message}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to land: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async handleDroneEmergency(args: Record<string, unknown>): Promise<CallToolResult> {
    try {
      const response = await this.apiClient.emergency();
      return {
        content: [
          {
            type: 'text',
            text: `Emergency stop ${response.success ? 'activated' : 'failed'}: ${response.message}`,
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to execute emergency stop: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }
}