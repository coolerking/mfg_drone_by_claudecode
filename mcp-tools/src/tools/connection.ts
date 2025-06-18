/**
 * Connection tools for MCP server
 * Handles drone connection, disconnection, and status checking
 */

import { Tool } from '@modelcontextprotocol/sdk/types.js';

export const droneConnectTool: Tool = {
  name: 'drone_connect',
  description: 'Connect to the Tello EDU drone. This establishes communication with the drone and prepares it for flight operations.',
  inputSchema: {
    type: 'object',
    properties: {},
    required: [],
    additionalProperties: false,
  },
};

export const droneDisconnectTool: Tool = {
  name: 'drone_disconnect',
  description: 'Disconnect from the Tello EDU drone. This safely terminates the connection with the drone.',
  inputSchema: {
    type: 'object',
    properties: {},
    required: [],
    additionalProperties: false,
  },
};

export const droneStatusTool: Tool = {
  name: 'drone_status',
  description: 'Get the current status of the Tello EDU drone including connection state, flight state, battery level, position, and sensor data.',
  inputSchema: {
    type: 'object',
    properties: {},
    required: [],
    additionalProperties: false,
  },
};