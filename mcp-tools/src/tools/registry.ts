import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { Logger } from '../utils/logger';

export interface ToolDefinition {
  tool: Tool;
  handler: (args: any) => Promise<any>;
  validator?: z.ZodSchema;
  category: string;
  description: string;
  examples?: string[];
}

export interface ToolExecutionContext {
  toolName: string;
  args: any;
  startTime: Date;
  requestId: string;
}

export interface ToolExecutionResult {
  success: boolean;
  data?: any;
  error?: string;
  duration: number;
  toolName: string;
  timestamp: Date;
}

export class ToolRegistry {
  private tools: Map<string, ToolDefinition> = new Map();
  private logger: Logger;
  private executionCount: Map<string, number> = new Map();

  constructor() {
    this.logger = Logger.getInstance();
  }

  public registerTool(
    name: string,
    definition: ToolDefinition
  ): void {
    if (this.tools.has(name)) {
      throw new Error(`Tool '${name}' is already registered`);
    }

    // Validate tool definition
    this.validateToolDefinition(name, definition);

    this.tools.set(name, definition);
    this.executionCount.set(name, 0);

    this.logger.info(`Registered MCP tool: ${name}`, {
      category: definition.category,
      description: definition.description,
    });
  }

  private validateToolDefinition(name: string, definition: ToolDefinition): void {
    if (!definition.tool) {
      throw new Error(`Tool '${name}' missing tool definition`);
    }

    if (!definition.handler) {
      throw new Error(`Tool '${name}' missing handler function`);
    }

    if (!definition.category) {
      throw new Error(`Tool '${name}' missing category`);
    }

    if (!definition.description) {
      throw new Error(`Tool '${name}' missing description`);
    }

    if (definition.tool.name !== name) {
      throw new Error(`Tool name mismatch: expected '${name}', got '${definition.tool.name}'`);
    }
  }

  public unregisterTool(name: string): boolean {
    const removed = this.tools.delete(name);
    if (removed) {
      this.executionCount.delete(name);
      this.logger.info(`Unregistered MCP tool: ${name}`);
    }
    return removed;
  }

  public getTool(name: string): ToolDefinition | undefined {
    return this.tools.get(name);
  }

  public getAllTools(): Tool[] {
    return Array.from(this.tools.values()).map(def => def.tool);
  }

  public getToolsByCategory(category: string): Tool[] {
    return Array.from(this.tools.values())
      .filter(def => def.category === category)
      .map(def => def.tool);
  }

  public getCategories(): string[] {
    const categories = new Set<string>();
    this.tools.forEach(def => categories.add(def.category));
    return Array.from(categories);
  }

  public hasToolAccess(toolName: string): boolean {
    return this.tools.has(toolName);
  }

  public async executeTool(
    name: string,
    args: any = {}
  ): Promise<ToolExecutionResult> {
    const startTime = new Date();
    const requestId = this.generateRequestId();
    
    const context: ToolExecutionContext = {
      toolName: name,
      args,
      startTime,
      requestId,
    };

    this.logger.debug(`Executing tool: ${name}`, {
      requestId,
      args: this.logger.getLevel() === 'debug' ? args : undefined,
    });

    try {
      const toolDef = this.tools.get(name);
      if (!toolDef) {
        throw new Error(`Tool '${name}' not found`);
      }

      // Validate arguments if validator is provided
      if (toolDef.validator) {
        try {
          args = toolDef.validator.parse(args);
        } catch (validationError) {
          throw new Error(`Invalid arguments for tool '${name}': ${validationError}`);
        }
      }

      // Execute the tool
      const result = await toolDef.handler(args);
      const duration = Date.now() - startTime.getTime();

      // Update execution count
      const currentCount = this.executionCount.get(name) || 0;
      this.executionCount.set(name, currentCount + 1);

      const executionResult: ToolExecutionResult = {
        success: true,
        data: result,
        duration,
        toolName: name,
        timestamp: new Date(),
      };

      this.logger.logToolExecution(name, duration, true, undefined, {
        requestId,
        executionCount: currentCount + 1,
      });

      return executionResult;

    } catch (error) {
      const duration = Date.now() - startTime.getTime();
      const errorMessage = error instanceof Error ? error.message : String(error);

      const executionResult: ToolExecutionResult = {
        success: false,
        error: errorMessage,
        duration,
        toolName: name,
        timestamp: new Date(),
      };

      this.logger.logToolExecution(name, duration, false, errorMessage, {
        requestId,
      });

      return executionResult;
    }
  }

  private generateRequestId(): string {
    return `tool_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  public getToolExecutionStats(): Record<string, {
    count: number;
    registered: boolean;
    category: string;
    lastExecution?: Date;
  }> {
    const stats: Record<string, any> = {};

    this.tools.forEach((def, name) => {
      stats[name] = {
        count: this.executionCount.get(name) || 0,
        registered: true,
        category: def.category,
      };
    });

    return stats;
  }

  public getToolInfo(name: string): {
    tool: Tool;
    category: string;
    description: string;
    examples: string[];
    executionCount: number;
  } | null {
    const toolDef = this.tools.get(name);
    if (!toolDef) {
      return null;
    }

    return {
      tool: toolDef.tool,
      category: toolDef.category,
      description: toolDef.description,
      examples: toolDef.examples || [],
      executionCount: this.executionCount.get(name) || 0,
    };
  }

  public resetExecutionCounts(): void {
    this.executionCount.clear();
    this.tools.forEach((_, name) => {
      this.executionCount.set(name, 0);
    });
    this.logger.info('Tool execution counts reset');
  }

  public getRegisteredToolCount(): number {
    return this.tools.size;
  }

  public isValidToolName(name: string): boolean {
    return /^[a-zA-Z][a-zA-Z0-9_]*$/.test(name);
  }

  public validateToolArgs(toolName: string, args: any): { valid: boolean; error?: string } {
    const toolDef = this.tools.get(toolName);
    if (!toolDef) {
      return { valid: false, error: `Tool '${toolName}' not found` };
    }

    if (!toolDef.validator) {
      return { valid: true };
    }

    try {
      toolDef.validator.parse(args);
      return { valid: true };
    } catch (error) {
      return { 
        valid: false, 
        error: error instanceof Error ? error.message : 'Validation failed' 
      };
    }
  }

  public listTools(): Array<{
    name: string;
    category: string;
    description: string;
    executionCount: number;
  }> {
    return Array.from(this.tools.entries()).map(([name, def]) => ({
      name,
      category: def.category,
      description: def.description,
      executionCount: this.executionCount.get(name) || 0,
    }));
  }

  public clear(): void {
    this.tools.clear();
    this.executionCount.clear();
    this.logger.info('Tool registry cleared');
  }
}