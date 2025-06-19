import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';

export interface MCPTool extends Tool {
  handler: (args: any, client: FastAPIClient, logger: Logger) => Promise<any>;
}

export class ToolRegistry {
  private tools: Map<string, MCPTool> = new Map();
  private client: FastAPIClient;
  private logger: Logger;

  constructor(client: FastAPIClient, logger: Logger) {
    this.client = client;
    this.logger = logger;
  }

  register(tool: MCPTool): void {
    this.tools.set(tool.name, tool);
    this.logger.debug(`Registered tool: ${tool.name}`);
  }

  unregister(name: string): void {
    this.tools.delete(name);
    this.logger.debug(`Unregistered tool: ${name}`);
  }

  getTool(name: string): MCPTool | undefined {
    return this.tools.get(name);
  }

  getAllTools(): Tool[] {
    return Array.from(this.tools.values()).map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema
    }));
  }

  async executeTool(name: string, args: any): Promise<any> {
    const tool = this.tools.get(name);
    if (!tool) {
      throw new Error(`Tool not found: ${name}`);
    }

    try {
      this.logger.info(`Executing tool: ${name}`, { args });
      const startTime = Date.now();
      
      const result = await tool.handler(args, this.client, this.logger);
      
      const duration = Date.now() - startTime;
      this.logger.info(`Tool executed successfully: ${name}`, { 
        duration: `${duration}ms`,
        success: true 
      });
      
      return result;
    } catch (error: any) {
      this.logger.error(`Tool execution failed: ${name}`, {
        error: error.message,
        args
      });
      throw error;
    }
  }

  getToolCount(): number {
    return this.tools.size;
  }

  hasTool(name: string): boolean {
    return this.tools.has(name);
  }
}