import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

import { ServerConfig } from './types/config.js';
import { Logger } from './utils/logger.js';
import { FastAPIClient } from './bridge/api-client.js';
import { ToolRegistry } from './tools/registry.js';

/**
 * MCP Drone Server - Main server class for MCP tools
 */
export class MCPDroneServer {
  private server: Server;
  private config: ServerConfig;
  private logger: Logger;
  private client: FastAPIClient;
  private toolRegistry: ToolRegistry;

  constructor(config: ServerConfig) {
    this.config = config;
    this.logger = new Logger(config);
    this.logger.info('Initializing MCP Drone Server', { config: this.sanitizeConfig(config) });

    // Initialize FastAPI client
    this.client = new FastAPIClient(config, this.logger);

    // Initialize tool registry
    this.toolRegistry = new ToolRegistry(this.client, this.logger);

    // Initialize MCP server
    this.server = new Server(
      {
        name: 'mfg-drone-mcp-tools',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  /**
   * Setup MCP server handlers
   */
  private setupHandlers(): void {
    this.logger.info('Setting up MCP server handlers...');

    // List tools handler
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      this.logger.debug('Handling list_tools request');
      
      const tools = this.toolRegistry.getTools();
      const stats = this.toolRegistry.getToolStats();
      
      this.logger.info(`Listing ${tools.length} available tools`, stats);
      
      return {
        tools: tools,
      };
    });

    // Call tool handler
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      this.logger.info(`Handling call_tool request: ${name}`, { 
        tool: name, 
        args: this.sanitizeArgs(args) 
      });

      try {
        // Validate tool exists
        if (!this.toolRegistry.hasTool(name)) {
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Tool '${name}' not found`
          );
        }

        // Validate arguments
        const validation = this.toolRegistry.validateToolArgs(name, args);
        if (!validation.valid) {
          throw new McpError(
            ErrorCode.InvalidParams,
            `Invalid arguments for tool '${name}': ${validation.errors?.join(', ')}`
          );
        }

        // Execute tool
        const result = await this.toolRegistry.executeTool(name, args);
        
        this.logger.info(`Tool execution completed: ${name}`, { 
          success: result && typeof result === 'object' && 'success' in result ? result.success : true 
        });

        return {
          content: [
            {
              type: 'text',
              text: this.formatToolResult(name, result),
            },
          ],
        };
      } catch (error) {
        this.logger.error(`Tool execution error: ${name}`, error);

        if (error instanceof McpError) {
          throw error;
        }

        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    });

    this.logger.info('MCP server handlers setup completed');
  }

  /**
   * Start the MCP server
   */
  async start(): Promise<void> {
    this.logger.info('Starting MCP Drone Server...');

    try {
      // Verify backend connection
      await this.verifyBackendConnection();

      // Setup transport
      const transport = new StdioServerTransport();
      
      // Connect server to transport
      await this.server.connect(transport);

      this.logger.info('MCP Drone Server started successfully', {
        tools_count: this.toolRegistry.getToolStats().total,
        backend_url: this.config.backendUrl,
      });

      // Log available tools
      const categories = this.toolRegistry.getToolsByCategory();
      for (const [category, tools] of Object.entries(categories)) {
        this.logger.info(`${category} tools:`, {
          tools: tools.map(t => t.name),
        });
      }
    } catch (error) {
      this.logger.error('Failed to start MCP Drone Server', error);
      throw error;
    }
  }

  /**
   * Stop the MCP server
   */
  async stop(): Promise<void> {
    this.logger.info('Stopping MCP Drone Server...');

    try {
      await this.server.close();
      this.client.stopHealthCheck();
      this.logger.info('MCP Drone Server stopped successfully');
    } catch (error) {
      this.logger.error('Error stopping MCP Drone Server', error);
      throw error;
    }
  }

  /**
   * Verify backend connection
   */
  private async verifyBackendConnection(): Promise<void> {
    this.logger.info('Verifying backend connection...');

    try {
      const health = await this.client.checkHealth();
      this.logger.info('Backend connection verified', { health });
    } catch (error) {
      this.logger.warn('Backend connection verification failed', error);
      // Don't throw here - allow server to start even if backend is not available
      // This allows for development scenarios where backend might start later
    }
  }

  /**
   * Format tool result for MCP response
   */
  private formatToolResult(toolName: string, result: unknown): string {
    try {
      if (result && typeof result === 'object' && 'success' in result) {
        const toolResult = result as {
          success: boolean;
          message: string;
          data?: unknown;
          error?: string;
        };

        if (toolResult.success) {
          let output = `✅ ${toolResult.message}`;
          
          if (toolResult.data) {
            output += '\n\n📊 Data:\n```json\n' + JSON.stringify(toolResult.data, null, 2) + '\n```';
          }
          
          return output;
        } else {
          let output = `❌ ${toolResult.message}`;
          
          if (toolResult.error) {
            output += `\n\n🔍 Error Code: ${toolResult.error}`;
          }
          
          if (toolResult.data) {
            output += '\n\n📋 Details:\n```json\n' + JSON.stringify(toolResult.data, null, 2) + '\n```';
          }
          
          return output;
        }
      } else {
        return `✅ Tool '${toolName}' executed successfully\n\n📊 Result:\n` + JSON.stringify(result, null, 2);
      }
    } catch (error) {
      return `⚠️ Tool '${toolName}' executed but result formatting failed: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }

  /**
   * Sanitize configuration for logging (remove sensitive data)
   */
  private sanitizeConfig(config: ServerConfig): Partial<ServerConfig> {
    return {
      backendUrl: config.backendUrl,
      timeout: config.timeout,
      retryAttempts: config.retryAttempts,
      retryDelay: config.retryDelay,
      debug: config.debug,
      healthCheckInterval: config.healthCheckInterval,
      // Omit potentially sensitive fields like logFile path
    };
  }

  /**
   * Sanitize arguments for logging (remove potentially sensitive data)
   */
  private sanitizeArgs(args: unknown): unknown {
    if (args && typeof args === 'object') {
      const sanitized = { ...args } as Record<string, unknown>;
      
      // Remove potentially sensitive fields
      const sensitiveFields = ['password', 'token', 'key', 'secret'];
      for (const field of sensitiveFields) {
        if (field in sanitized) {
          sanitized[field] = '[REDACTED]';
        }
      }
      
      return sanitized;
    }
    
    return args;
  }

  /**
   * Get server statistics
   */
  getStats(): {
    server: {
      uptime: number;
      tools: number;
    };
    config: Partial<ServerConfig>;
    tools: ReturnType<ToolRegistry['getToolStats']>;
  } {
    return {
      server: {
        uptime: process.uptime(),
        tools: this.toolRegistry.getToolStats().total,
      },
      config: this.sanitizeConfig(this.config),
      tools: this.toolRegistry.getToolStats(),
    };
  }
}