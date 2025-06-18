import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ListPromptsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { ConfigManager } from './utils/config.js';
import { Logger } from './utils/logger.js';
import { ToolRegistry } from './tools/registry.js';
import { EnhancedFastAPIClient } from './bridge/enhanced-api-client.js';
import { WebSocketBridge } from './bridge/websocket-bridge.js';
import { MetricsCollector } from './bridge/metrics-collector.js';

// Tool imports
import { createConnectionTools } from './tools/connection.js';
import { createFlightTools } from './tools/flight.js';
import { createMovementTools } from './tools/movement.js';
import { createCameraTools } from './tools/camera.js';
import { createSensorTools } from './tools/sensors.js';

export class MCPDroneServer {
  private server: Server;
  private config: ReturnType<ConfigManager['getConfig']>;
  private logger: Logger;
  private toolRegistry: ToolRegistry;
  private apiClient: EnhancedFastAPIClient;
  private wsClient: WebSocketBridge | null = null;
  private metrics: MetricsCollector;
  private isInitialized: boolean = false;

  constructor() {
    this.config = ConfigManager.getInstance().getConfig();
    this.logger = Logger.getInstance();
    this.toolRegistry = new ToolRegistry();
    this.apiClient = new EnhancedFastAPIClient();
    this.metrics = new MetricsCollector();

    this.server = new Server(
      {
        name: this.config.server.name,
        version: this.config.server.version,
      },
      {
        capabilities: {
          tools: {},
          resources: {},
          prompts: {},
          logging: {},
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers(): void {
    // List tools handler
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools = this.toolRegistry.getAllTools();
      this.logger.debug(`Listed ${tools.length} tools`, {
        toolCount: tools.length,
        categories: this.toolRegistry.getCategories(),
      });

      return {
        tools: tools,
      };
    });

    // Call tool handler
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      const startTime = Date.now();

      this.logger.info(`Tool execution requested: ${name}`, {
        toolName: name,
        args: this.logger.getLevel() === 'debug' ? args : undefined,
      });

      try {
        // Execute the tool
        const result = await this.toolRegistry.executeTool(name, args);
        const duration = Date.now() - startTime;

        // Record metrics
        this.metrics.recordToolExecution(name, duration, result.success, result.error);

        // Log execution
        this.logger.logToolExecution(name, duration, result.success, result.error);

        if (result.success) {
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result.data, null, 2),
              },
            ],
          };
        } else {
          return {
            content: [
              {
                type: 'text',
                text: `Error: ${result.error}`,
              },
            ],
            isError: true,
          };
        }
      } catch (error) {
        const duration = Date.now() - startTime;
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';

        this.metrics.recordToolExecution(name, duration, false, errorMessage);
        this.logger.error(`Tool execution failed: ${name}`, error as Error);

        return {
          content: [
            {
              type: 'text',
              text: `Tool execution failed: ${errorMessage}`,
            },
          ],
          isError: true,
        };
      }
    });

    // List resources handler (for future resource support)
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [
          {
            uri: 'drone://status',
            name: 'Drone Status',
            description: 'Real-time drone status information',
            mimeType: 'application/json',
          },
          {
            uri: 'drone://metrics',
            name: 'Performance Metrics',
            description: 'MCP server performance metrics',
            mimeType: 'application/json',
          },
        ],
      };
    });

    // List prompts handler (for future prompt support)
    this.server.setRequestHandler(ListPromptsRequestSchema, async () => {
      return {
        prompts: [
          {
            name: 'flight_safety_check',
            description: 'Comprehensive pre-flight safety checklist',
            arguments: [
              {
                name: 'flight_type',
                description: 'Type of flight planned (manual, tracking, mission)',
                required: false,
              },
            ],
          },
          {
            name: 'emergency_procedures',
            description: 'Emergency response procedures and troubleshooting',
            arguments: [
              {
                name: 'emergency_type',
                description: 'Type of emergency (battery, connection, collision)',
                required: false,
              },
            ],
          },
        ],
      };
    });
  }

  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      this.logger.warn('MCP server already initialized');
      return;
    }

    try {
      this.logger.info('Initializing MCP Drone Server', {
        environment: this.config.environment,
        backendUrl: this.config.backend.baseUrl,
        websocketEnabled: this.config.websocket.enabled,
      });

      // Register all tools
      await this.registerTools();

      // Initialize WebSocket connection if enabled
      if (this.config.websocket.enabled) {
        await this.initializeWebSocket();
      }

      // Setup metrics collection
      this.setupMetricsCollection();

      // Setup graceful shutdown
      this.setupGracefulShutdown();

      this.isInitialized = true;
      this.logger.info('MCP Drone Server initialized successfully', {
        toolCount: this.toolRegistry.getRegisteredToolCount(),
        categories: this.toolRegistry.getCategories(),
      });

    } catch (error) {
      this.logger.error('Failed to initialize MCP server', error as Error);
      throw error;
    }
  }

  private async registerTools(): Promise<void> {
    try {
      // Connection tools
      const connectionTools = createConnectionTools(this.apiClient);
      connectionTools.forEach(toolDef => {
        this.toolRegistry.registerTool(toolDef.tool.name, toolDef);
      });

      // Flight control tools
      const flightTools = createFlightTools(this.apiClient);
      flightTools.forEach(toolDef => {
        this.toolRegistry.registerTool(toolDef.tool.name, toolDef);
      });

      // Movement tools
      const movementTools = createMovementTools(this.apiClient);
      movementTools.forEach(toolDef => {
        this.toolRegistry.registerTool(toolDef.tool.name, toolDef);
      });

      // Camera tools
      const cameraTools = createCameraTools(this.apiClient);
      cameraTools.forEach(toolDef => {
        this.toolRegistry.registerTool(toolDef.tool.name, toolDef);
      });

      // Sensor tools
      const sensorTools = createSensorTools(this.apiClient);
      sensorTools.forEach(toolDef => {
        this.toolRegistry.registerTool(toolDef.tool.name, toolDef);
      });

      this.logger.info('All tools registered successfully', {
        totalTools: this.toolRegistry.getRegisteredToolCount(),
        byCategory: this.getToolCountByCategory(),
      });

    } catch (error) {
      this.logger.error('Failed to register tools', error as Error);
      throw error;
    }
  }

  private async initializeWebSocket(): Promise<void> {
    try {
      this.wsClient = new WebSocketBridge();
      
      // Setup WebSocket event handlers
      this.wsClient.on('connected', () => {
        this.logger.info('WebSocket connected');
        this.metrics.recordWebSocketConnection();
      });

      this.wsClient.on('disconnected', (code, reason) => {
        this.logger.warn('WebSocket disconnected', { code, reason });
        this.metrics.recordWebSocketDisconnection();
      });

      this.wsClient.on('error', (error) => {
        this.logger.error('WebSocket error', error);
      });

      this.wsClient.on('message', (event) => {
        this.metrics.recordWebSocketMessage('received');
        this.logger.debug('WebSocket message received', { type: event.type });
      });

      // Attempt to connect
      await this.wsClient.connect();

    } catch (error) {
      this.logger.warn('WebSocket initialization failed, continuing without real-time features', error as Error);
      this.wsClient = null;
    }
  }

  private setupMetricsCollection(): void {
    if (!this.config.performance.enableMetrics) {
      return;
    }

    this.metrics.on('metrics', (snapshot) => {
      this.logger.debug('Performance metrics', snapshot);
      
      // Log warnings for performance issues
      if (snapshot.api.averageResponseTime > this.config.performance.targetResponseTime) {
        this.logger.warn('API performance degraded', {
          current: snapshot.api.averageResponseTime,
          target: this.config.performance.targetResponseTime,
        });
      }
    });

    this.logger.info('Metrics collection enabled', {
      interval: this.config.performance.metricsInterval,
      targetResponseTime: this.config.performance.targetResponseTime,
    });
  }

  private setupGracefulShutdown(): void {
    const shutdown = async (signal: string) => {
      this.logger.info(`Received ${signal}, shutting down gracefully...`);
      
      try {
        // Stop metrics collection
        this.metrics.stop();
        
        // Close WebSocket connection
        if (this.wsClient) {
          this.wsClient.destroy();
        }
        
        // Close API client connections
        this.apiClient.destroy();
        
        // Flush logs
        await this.logger.flush();
        
        this.logger.info('MCP Drone Server shutdown complete');
        process.exit(0);
      } catch (error) {
        this.logger.error('Error during shutdown', error as Error);
        process.exit(1);
      }
    };

    process.on('SIGINT', () => shutdown('SIGINT'));
    process.on('SIGTERM', () => shutdown('SIGTERM'));
    
    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      this.logger.error('Uncaught exception', error);
      shutdown('uncaughtException');
    });

    process.on('unhandledRejection', (reason, promise) => {
      this.logger.error('Unhandled rejection', new Error(String(reason)), {
        promise: promise.toString(),
      });
    });
  }

  private getToolCountByCategory(): Record<string, number> {
    const categories = this.toolRegistry.getCategories();
    const counts: Record<string, number> = {};
    
    categories.forEach(category => {
      counts[category] = this.toolRegistry.getToolsByCategory(category).length;
    });
    
    return counts;
  }

  public async run(): Promise<void> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    const transport = new StdioServerTransport();
    
    this.logger.info('Starting MCP Drone Server on stdio transport');
    
    await this.server.connect(transport);
    
    this.logger.info('MCP Drone Server is running and ready to accept requests');
  }

  // Public API for server management
  public getMetrics() {
    return this.metrics.getMetricsSnapshot();
  }

  public getToolStats() {
    return this.toolRegistry.getToolExecutionStats();
  }

  public getServerInfo() {
    return {
      name: this.config.server.name,
      version: this.config.server.version,
      environment: this.config.environment,
      uptime: this.metrics.getUptime(),
      toolCount: this.toolRegistry.getRegisteredToolCount(),
      categories: this.toolRegistry.getCategories(),
      websocketEnabled: this.config.websocket.enabled,
      websocketConnected: this.wsClient?.isConnected() || false,
      backendUrl: this.config.backend.baseUrl,
    };
  }

  public isHealthy(): boolean {
    return this.isInitialized && this.apiClient.getHealthStatus().isHealthy;
  }
}