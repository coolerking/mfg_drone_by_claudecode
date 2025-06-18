/**
 * Tool Registry
 * 
 * Central registry for all MCP tools with validation and management
 */

import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// Import tool definitions
import { 
  droneConnectTool, 
  droneDisconnectTool, 
  droneStatusTool 
} from './connection.js';
import { 
  droneTakeoffTool, 
  droneLandTool, 
  droneEmergencyTool 
} from './flight.js';

class ToolRegistry {
  private tools: Map<string, Tool> = new Map();
  private schemas: Map<string, z.ZodSchema> = new Map();

  constructor() {
    this.registerTools();
  }

  /**
   * Register all available tools
   */
  private registerTools(): void {
    // Connection tools
    this.registerTool(droneConnectTool);
    this.registerTool(droneDisconnectTool);
    this.registerTool(droneStatusTool);

    // Flight control tools
    this.registerTool(droneTakeoffTool);
    this.registerTool(droneLandTool);
    this.registerTool(droneEmergencyTool);
  }

  /**
   * Register a single tool
   */
  private registerTool(tool: Tool): void {
    this.tools.set(tool.name, tool);
    
    // Create Zod schema from JSON schema for validation
    const zodSchema = this.jsonSchemaToZod(tool.inputSchema);
    this.schemas.set(tool.name, zodSchema);
  }

  /**
   * Convert JSON schema to Zod schema (simplified)
   */
  private jsonSchemaToZod(jsonSchema: any): z.ZodSchema {
    if (!jsonSchema || jsonSchema.type !== 'object') {
      return z.object({});
    }

    const shape: Record<string, z.ZodSchema> = {};
    
    if (jsonSchema.properties) {
      for (const [key, propSchema] of Object.entries(jsonSchema.properties as Record<string, any>)) {
        shape[key] = this.convertPropertyToZod(propSchema);
      }
    }

    let schema = z.object(shape);

    // Handle required fields
    if (jsonSchema.required && Array.isArray(jsonSchema.required)) {
      // Zod objects are required by default, so we need to make non-required fields optional
      const requiredFields = new Set(jsonSchema.required);
      const newShape: Record<string, z.ZodSchema> = {};
      
      for (const [key, zodSchema] of Object.entries(shape)) {
        newShape[key] = requiredFields.has(key) ? zodSchema : zodSchema.optional();
      }
      
      schema = z.object(newShape);
    } else {
      // If no required fields specified, make all fields optional
      const newShape: Record<string, z.ZodSchema> = {};
      for (const [key, zodSchema] of Object.entries(shape)) {
        newShape[key] = zodSchema.optional();
      }
      schema = z.object(newShape);
    }

    // Handle additionalProperties
    if (jsonSchema.additionalProperties === false) {
      schema = schema.strict();
    }

    return schema;
  }

  /**
   * Convert a property schema to Zod schema
   */
  private convertPropertyToZod(propSchema: any): z.ZodSchema {
    switch (propSchema.type) {
      case 'string':
        return z.string();
      case 'number':
        return z.number();
      case 'integer':
        return z.number().int();
      case 'boolean':
        return z.boolean();
      case 'array':
        return z.array(z.any());
      case 'object':
        return z.object({});
      default:
        return z.any();
    }
  }

  /**
   * Get all registered tools
   */
  getAllTools(): Tool[] {
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
   * Validate tool arguments against the tool's schema
   */
  validateArguments(toolName: string, args: unknown): Record<string, unknown> {
    const schema = this.schemas.get(toolName);
    if (!schema) {
      throw new Error(`Tool schema not found: ${toolName}`);
    }

    try {
      return schema.parse(args) as Record<string, unknown>;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const issues = error.issues.map(issue => `${issue.path.join('.')}: ${issue.message}`);
        throw new Error(`Invalid arguments for tool '${toolName}': ${issues.join(', ')}`);
      }
      throw error;
    }
  }

  /**
   * Get tool names by category
   */
  getToolsByCategory(): Record<string, string[]> {
    const categories: Record<string, string[]> = {
      connection: [],
      flight: [],
      movement: [],
      camera: [],
      sensors: [],
      tracking: [],
    };

    for (const tool of this.tools.values()) {
      if (tool.name.startsWith('drone_connect') || tool.name.startsWith('drone_disconnect') || tool.name.startsWith('drone_status')) {
        categories.connection.push(tool.name);
      } else if (tool.name.includes('takeoff') || tool.name.includes('land') || tool.name.includes('emergency')) {
        categories.flight.push(tool.name);
      } else if (tool.name.includes('move') || tool.name.includes('rotate')) {
        categories.movement.push(tool.name);
      } else if (tool.name.includes('camera') || tool.name.includes('stream')) {
        categories.camera.push(tool.name);
      } else if (tool.name.includes('sensor') || tool.name.includes('battery')) {
        categories.sensors.push(tool.name);
      } else if (tool.name.includes('track') || tool.name.includes('detect')) {
        categories.tracking.push(tool.name);
      }
    }

    return categories;
  }
}

// Export singleton instance
export const toolRegistry = new ToolRegistry();