import { BaseTool } from './BaseTool.js';
import { ConnectDroneTool } from './ConnectDroneTool.js';
import { TakeoffDroneTool } from './TakeoffDroneTool.js';
import { LandDroneTool } from './LandDroneTool.js';
import { MoveDroneTool } from './MoveDroneTool.js';
import { RotateDroneTool } from './RotateDroneTool.js';
import { TakePhotoTool } from './TakePhotoTool.js';
import { ExecuteNaturalLanguageCommandTool } from './ExecuteNaturalLanguageCommandTool.js';
import { EmergencyStopTool } from './EmergencyStopTool.js';

export {
  BaseTool,
  ConnectDroneTool,
  TakeoffDroneTool,
  LandDroneTool,
  MoveDroneTool,
  RotateDroneTool,
  TakePhotoTool,
  ExecuteNaturalLanguageCommandTool,
  EmergencyStopTool,
};

/**
 * 利用可能な全てのMCPツールのリスト
 */
export const ALL_TOOLS = [
  ConnectDroneTool,
  TakeoffDroneTool,
  LandDroneTool,
  MoveDroneTool,
  RotateDroneTool,
  TakePhotoTool,
  ExecuteNaturalLanguageCommandTool,
  EmergencyStopTool,
] as const;

/**
 * ツール名とクラスのマッピング
 */
export const TOOL_MAP = {
  connect_drone: ConnectDroneTool,
  takeoff_drone: TakeoffDroneTool,
  land_drone: LandDroneTool,
  move_drone: MoveDroneTool,
  rotate_drone: RotateDroneTool,
  take_photo: TakePhotoTool,
  execute_natural_language_command: ExecuteNaturalLanguageCommandTool,
  emergency_stop: EmergencyStopTool,
} as const;

export type ToolName = keyof typeof TOOL_MAP;