import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  type CallToolRequest,
  type ListToolsRequest,
  type ListResourcesRequest,
  type ReadResourceRequest,
} from '@modelcontextprotocol/sdk/types.js';
import { DroneService } from '@/services/DroneService.js';
import { logger } from '@/utils/logger.js';
import { ErrorHandler } from '@/utils/errors.js';
import { type Config, type MCPToolResponse } from '@/types/index.js';
import { TOOL_MAP, type ToolName } from '@/tools/index.js';
import { 
  DroneStatusResource,
  SystemLogsResource,
  ConfigurationResource,
} from '@/resources/index.js';

/**
 * MCP ドローンサーバー
 * Model Context Protocol を実装してドローン制御機能を提供
 */
export class MCPDroneServer {
  private server: Server;
  private droneService: DroneService;
  private config: Config;
  private isRunning: boolean = false;
  private tools: Map<string, any>;
  private resources: Map<string, any>;

  constructor(config: Config) {
    this.config = config;
    this.droneService = new DroneService(config);
    this.tools = new Map();
    this.resources = new Map();
    
    this.server = new Server(
      {
        name: 'mcp-drone-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {},
        },
      }
    );

    this.initializeToolsAndResources();
    this.setupHandlers();
  }

  /**
   * ツールとリソースを初期化
   */
  private initializeToolsAndResources(): void {
    // ツールを初期化
    for (const [toolName, ToolClass] of Object.entries(TOOL_MAP)) {
      const toolInstance = new ToolClass(this.droneService);
      this.tools.set(toolName, toolInstance);
      logger.debug(`Initialized tool: ${toolName}`);
    }

    // リソースを初期化
    const droneStatusResource = new DroneStatusResource(this.droneService);
    const systemLogsResource = new SystemLogsResource(this.droneService);
    const configurationResource = new ConfigurationResource(this.droneService, this.config);

    this.resources.set('drone_status', droneStatusResource);
    this.resources.set('system_logs', systemLogsResource);
    this.resources.set('configuration', configurationResource);

    logger.info(`Initialized ${this.tools.size} tools and ${this.resources.size} resources`);
  }

  /**
   * MCPハンドラーを設定
   */
  private setupHandlers(): void {
    // List tools handler
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      logger.debug('Received list tools request');
      
      const tools = [];
      
      // 新しいツール（Phase 2で追加）
      for (const [toolName, toolInstance] of this.tools.entries()) {
        tools.push({
          name: toolName,
          description: toolInstance.getDescription(),
          inputSchema: toolInstance.getInputSchema(),
        });
      }
      
      // 既存のレガシーツール（Phase 1からの継承）
      tools.push(
        {
          name: 'get_drone_status',
          description: 'Get the current status of drones. Optionally specify a drone ID.',
          inputSchema: {
            type: 'object',
            properties: {
              droneId: {
                type: 'string',
                description: 'Optional drone ID to get status for specific drone',
              },
            },
          },
        },
        {
          name: 'scan_drones',
          description: 'Scan for available drones on the network.',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'health_check',
          description: 'Check the health status of the drone system.',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'get_system_status',
          description: 'Get comprehensive system status including all services and drones.',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        }
      );
      
      logger.debug(`Returning ${tools.length} tools`);
      return { tools };
    });

    // List resources handler
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      logger.debug('Received list resources request');
      
      const resources = [];
      for (const [resourceName, resourceInstance] of this.resources.entries()) {
        resources.push({
          uri: resourceInstance.getUri(),
          name: resourceName,
          description: resourceInstance.getDescription(),
          mimeType: resourceInstance.getMimeType(),
        });
      }
      
      logger.debug(`Returning ${resources.length} resources`);
      return { resources };
    });

    // Read resource handler
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const uri = request.params.uri;
      logger.debug(`Reading resource: ${uri}`);
      
      // リソースURI からリソース名を抽出
      for (const [resourceName, resourceInstance] of this.resources.entries()) {
        if (resourceInstance.getUri() === uri) {
          const contents = await resourceInstance.getContents();
          return contents;
        }
      }
      
      throw new Error(`Resource not found: ${uri}`);
    });

    // Call tool handler
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      logger.info(`Received tool call: ${request.params.name}`);
      return await this.handleToolCall(request);
    });
  }

  /**
   * ツール呼び出しを処理
   */
  private async handleToolCall(request: CallToolRequest): Promise<MCPToolResponse> {
    try {
      const { name, arguments: args } = request.params;

      // 新しいツール（Phase 2）を優先してチェック
      if (this.tools.has(name)) {
        const toolInstance = this.tools.get(name);
        logger.debug(`Executing Phase 2 tool: ${name}`);
        return await toolInstance.execute(args);
      }

      // レガシーツール（Phase 1）のフォールバック
      switch (name) {
        case 'get_drone_status':
          return await this.handleGetDroneStatus(args);
        
        case 'scan_drones':
          return await this.handleScanDrones();
        
        case 'health_check':
          return await this.handleHealthCheck();
        
        case 'get_system_status':
          return await this.handleGetSystemStatus();
        
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'MCPDroneServer.handleToolCall');
      
      return {
        content: [
          {
            type: 'text',
            text: `Error: ${handledError.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  /**
   * ドローン状態取得ツール
   */
  private async handleGetDroneStatus(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    const droneId = args?.droneId as string | undefined;
    const statuses = await this.droneService.getDroneStatus(droneId);
    
    const statusText = statuses
      .map(status => {
        const batteryInfo = status.batteryLevel !== undefined ? 
          ` (Battery: ${status.batteryLevel}%)` : '';
        const positionInfo = status.position ? 
          ` at (${status.position.x}, ${status.position.y}, ${status.position.z})` : '';
        
        return `Drone ${status.name} (${status.id}): ${status.status}${batteryInfo}${positionInfo} - Last seen: ${status.lastSeen}`;
      })
      .join('\n');

    return {
      content: [
        {
          type: 'text',
          text: statuses.length > 0 ? statusText : 'No drones found.',
        },
      ],
    };
  }

  /**
   * ドローンスキャンツール
   */
  private async handleScanDrones(): Promise<MCPToolResponse> {
    const result = await this.droneService.scanForDrones();
    
    return {
      content: [
        {
          type: 'text',
          text: `${result.message} Found ${result.found} drone(s).`,
        },
      ],
    };
  }

  /**
   * ヘルスチェックツール
   */
  private async handleHealthCheck(): Promise<MCPToolResponse> {
    const health = await this.droneService.performHealthCheck();
    
    return {
      content: [
        {
          type: 'text',
          text: `System health: ${health.status} (checked at ${health.timestamp})`,
        },
      ],
    };
  }

  /**
   * システム状態取得ツール
   */
  private async handleGetSystemStatus(): Promise<MCPToolResponse> {
    const status = await this.droneService.getSystemStatus();
    
    const serviceStatus = Object.entries(status.services)
      .map(([service, info]) => `${service}: ${info.status}${info.message ? ` (${info.message})` : ''}`)
      .join('\n');
    
    const droneCount = status.drones.length;
    const activeDroneCount = status.drones.filter(d => 
      ['connected', 'flying', 'idle'].includes(d.status)
    ).length;
    
    const statusText = [
      `System Status: ${status.status} (${status.timestamp})`,
      '',
      'Services:',
      serviceStatus,
      '',
      `Drones: ${activeDroneCount}/${droneCount} active`,
    ].join('\n');
    
    return {
      content: [
        {
          type: 'text',
          text: statusText,
        },
      ],
    };
  }

  /**
   * サーバーを開始
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      logger.warn('MCP server is already running');
      return;
    }

    try {
      // バックエンド接続テスト
      const connected = await this.droneService.testBackendConnection();
      if (!connected) {
        logger.warn('Backend connection test failed, but continuing to start server');
      }

      // Transport setup
      const transport = new StdioServerTransport();
      
      logger.info('Starting MCP Drone Server...');
      await this.server.connect(transport);
      
      this.isRunning = true;
      logger.info('MCP Drone Server started successfully');
      
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'MCPDroneServer.start');
      throw handledError;
    }
  }

  /**
   * サーバーを停止
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      logger.warn('MCP server is not running');
      return;
    }

    try {
      logger.info('Stopping MCP Drone Server...');
      await this.server.close();
      this.isRunning = false;
      logger.info('MCP Drone Server stopped successfully');
    } catch (error) {
      const handledError = ErrorHandler.handleError(error, 'MCPDroneServer.stop');
      throw handledError;
    }
  }

  /**
   * サーバーの実行状態を取得
   */
  isServerRunning(): boolean {
    return this.isRunning;
  }
}