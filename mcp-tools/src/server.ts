import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { FastAPIClient } from './bridge/api-client.js';
import { ToolRegistry } from './tools/registry.js';
import { ConfigManager } from './utils/config.js';
import { Logger } from './utils/logger.js';
import { connectionTools } from './tools/connection.js';
import { flightTools } from './tools/flight.js';

export class MCPDroneServer {
  private server: Server;
  private client: FastAPIClient;
  private registry: ToolRegistry;
  private config: ConfigManager;
  private logger: Logger;

  constructor(configPath?: string) {
    this.config = new ConfigManager(configPath);
    this.config.validate();

    this.logger = new Logger(this.config.getConfig());
    this.client = new FastAPIClient(this.config.getConfig(), this.logger);
    this.registry = new ToolRegistry(this.client, this.logger);

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
    this.registerTools();
  }

  private setupHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools = this.registry.getAllTools();
      this.logger.debug(`Listed ${tools.length} tools`);
      return { tools };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        const result = await this.registry.executeTool(name, args || {});
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      } catch (error: any) {
        this.logger.error(`Tool execution error: ${name}`, error);
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: false,
                error: error.message,
                tool: name,
                timestamp: new Date().toISOString()
              }, null, 2)
            }
          ],
          isError: true
        };
      }
    });
  }

  private registerTools(): void {
    // Register connection tools
    connectionTools.forEach(tool => {
      this.registry.register(tool);
    });

    // Register flight tools
    flightTools.forEach(tool => {
      this.registry.register(tool);
    });

    this.logger.info(`Registered ${this.registry.getToolCount()} MCP tools`);
  }

  async start(): Promise<void> {
    const transport = new StdioServerTransport();
    
    this.logger.info('Starting MCP Drone Server', {
      tools: this.registry.getToolCount(),
      backend: this.config.getConfig().backendUrl
    });

    await this.server.connect(transport);
    this.logger.info('MCP Drone Server started successfully');
  }

  async stop(): Promise<void> {
    this.logger.info('Stopping MCP Drone Server');
    await this.server.close();
  }

  // Health check method for testing
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.healthCheck();
      return true;
    } catch (error) {
      this.logger.error('Health check failed', error);
      return false;
    }
  }

  // Get server info for testing
  getServerInfo(): {
    toolCount: number;
    tools: string[];
    config: any;
  } {
    return {
      toolCount: this.registry.getToolCount(),
      tools: this.registry.getAllTools().map(t => t.name),
      config: {
        backendUrl: this.config.getConfig().backendUrl,
        timeout: this.config.getConfig().timeout,
        retries: this.config.getConfig().retries
      }
    };
  }
}