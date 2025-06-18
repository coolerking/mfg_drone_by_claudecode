import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';
import { ConnectionTools } from './connection.js';
import { FlightTools } from './flight.js';
import { MovementTools } from './movement.js';
import { CameraTools } from './camera.js';
import { SensorTools } from './sensors.js';

/**
 * Tool execution interface
 */
interface ToolExecutor {
  executeTool(name: string, args: unknown): Promise<unknown>;
}

/**
 * Tool registry that manages all MCP tools
 */
export class ToolRegistry {
  private tools: Map<string, Tool> = new Map();
  private executors: Map<string, ToolExecutor> = new Map();
  private logger;

  private connectionTools: ConnectionTools;
  private flightTools: FlightTools;
  private movementTools: MovementTools;
  private cameraTools: CameraTools;
  private sensorTools: SensorTools;

  constructor(client: FastAPIClient, logger: Logger) {
    this.logger = logger.createComponentLogger('ToolRegistry');

    // Initialize tool categories
    this.connectionTools = new ConnectionTools(client, logger);
    this.flightTools = new FlightTools(client, logger);
    this.movementTools = new MovementTools(client, logger);
    this.cameraTools = new CameraTools(client, logger);
    this.sensorTools = new SensorTools(client, logger);

    // Register all tools
    this.registerTools();
  }

  /**
   * Register all tools from different categories
   */
  private registerTools(): void {
    this.logger.info('Registering MCP tools...');

    // Register connection tools
    this.registerToolCategory('connection', this.connectionTools, this.connectionTools.getTools());

    // Register flight tools
    this.registerToolCategory('flight', this.flightTools, this.flightTools.getTools());

    // Register movement tools
    this.registerToolCategory('movement', this.movementTools, this.movementTools.getTools());

    // Register camera tools
    this.registerToolCategory('camera', this.cameraTools, this.cameraTools.getTools());

    // Register sensor tools
    this.registerToolCategory('sensors', this.sensorTools, this.sensorTools.getTools());

    this.logger.info(`Successfully registered ${this.tools.size} MCP tools`, {
      tool_count: this.tools.size,
      categories: {
        connection: this.connectionTools.getTools().length,
        flight: this.flightTools.getTools().length,
        movement: this.movementTools.getTools().length,
        camera: this.cameraTools.getTools().length,
        sensors: this.sensorTools.getTools().length,
      },
    });
  }

  /**
   * Register tools from a specific category
   */
  private registerToolCategory(
    category: string,
    executor: ToolExecutor,
    tools: Tool[]
  ): void {
    this.logger.debug(`Registering ${category} tools`, { count: tools.length });

    for (const tool of tools) {
      if (this.tools.has(tool.name)) {
        throw new Error(`Tool '${tool.name}' is already registered`);
      }

      this.tools.set(tool.name, tool);
      this.executors.set(tool.name, executor);

      this.logger.debug(`Registered tool: ${tool.name}`, {
        category,
        description: tool.description,
      });
    }
  }

  /**
   * Get all registered tools
   */
  getTools(): Tool[] {
    return Array.from(this.tools.values());
  }

  /**
   * Get a specific tool by name
   */
  getTool(name: string): Tool | undefined {
    return this.tools.get(name);
  }

  /**
   * Check if a tool exists
   */
  hasTool(name: string): boolean {
    return this.tools.has(name);
  }

  /**
   * Execute a tool by name
   */
  async executeTool(name: string, args: unknown): Promise<unknown> {
    this.logger.info(`Executing tool: ${name}`, { args });

    const tool = this.tools.get(name);
    if (!tool) {
      const error = `Tool '${name}' not found`;
      this.logger.error(error);
      throw new Error(error);
    }

    const executor = this.executors.get(name);
    if (!executor) {
      const error = `Executor for tool '${name}' not found`;
      this.logger.error(error);
      throw new Error(error);
    }

    try {
      const startTime = Date.now();
      const result = await executor.executeTool(name, args);
      const duration = Date.now() - startTime;

      this.logger.info(`Tool execution completed: ${name}`, {
        duration_ms: duration,
        success: result && typeof result === 'object' && 'success' in result ? result.success : true,
      });

      return result;
    } catch (error) {
      this.logger.error(`Tool execution failed: ${name}`, error);
      
      // Wrap the error in a standardized format
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        error: 'TOOL_EXECUTION_ERROR',
        tool: name,
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Get tools by category
   */
  getToolsByCategory(): Record<string, Tool[]> {
    const categories: Record<string, Tool[]> = {
      connection: this.connectionTools.getTools(),
      flight: this.flightTools.getTools(),
      movement: this.movementTools.getTools(),
      camera: this.cameraTools.getTools(),
      sensors: this.sensorTools.getTools(),
    };

    return categories;
  }

  /**
   * Get tool statistics
   */
  getToolStats(): {
    total: number;
    categories: Record<string, number>;
    tools: string[];
  } {
    const categories = this.getToolsByCategory();
    const stats = {
      total: this.tools.size,
      categories: Object.fromEntries(
        Object.entries(categories).map(([category, tools]) => [category, tools.length])
      ),
      tools: Array.from(this.tools.keys()).sort(),
    };

    return stats;
  }

  /**
   * Validate tool arguments against schema
   */
  validateToolArgs(name: string, args: unknown): { valid: boolean; errors?: string[] } {
    const tool = this.tools.get(name);
    if (!tool) {
      return { valid: false, errors: [`Tool '${name}' not found`] };
    }

    // Basic validation - in a production system, you'd use a proper JSON schema validator
    try {
      // This is a simplified validation - you might want to use ajv or similar
      if (tool.inputSchema.required && Array.isArray(tool.inputSchema.required)) {
        const requiredFields = tool.inputSchema.required;
        const providedArgs = args as Record<string, unknown> || {};
        
        for (const field of requiredFields) {
          if (!(field in providedArgs)) {
            return { valid: false, errors: [`Required field '${field}' is missing`] };
          }
        }
      }

      return { valid: true };
    } catch (error) {
      return { 
        valid: false, 
        errors: [`Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`] 
      };
    }
  }

  /**
   * Get tool usage statistics (placeholder for future implementation)
   */
  getUsageStats(): Record<string, { calls: number; errors: number; avgDuration: number }> {
    // This would be implemented with proper metrics collection
    // For now, return empty stats
    return {};
  }
}