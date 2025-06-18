/**
 * Flight control tools for MCP server
 * Handles basic flight operations: takeoff, landing, and emergency stop
 */

import { Tool } from '@modelcontextprotocol/sdk/types.js';

export const droneTakeoffTool: Tool = {
  name: 'drone_takeoff',
  description: 'Make the Tello EDU drone take off. The drone will automatically rise to a height of approximately 0.8-1.2 meters and hover.',
  inputSchema: {
    type: 'object',
    properties: {},
    required: [],
    additionalProperties: false,
  },
};

export const droneLandTool: Tool = {
  name: 'drone_land',
  description: 'Make the Tello EDU drone land safely. The drone will descend and land at its current position.',
  inputSchema: {
    type: 'object',
    properties: {},
    required: [],
    additionalProperties: false,
  },
};

export const droneEmergencyTool: Tool = {
  name: 'drone_emergency',
  description: 'Immediately stop all drone motors and make it drop. Use this ONLY in emergency situations as it will cause the drone to fall.',
  inputSchema: {
    type: 'object',
    properties: {},
    required: [],
    additionalProperties: false,
  },
};