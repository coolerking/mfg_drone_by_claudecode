import { BaseResource } from './BaseResource.js';
import { DroneStatusResource } from './DroneStatusResource.js';
import { SystemLogsResource } from './SystemLogsResource.js';
import { ConfigurationResource } from './ConfigurationResource.js';

export {
  BaseResource,
  DroneStatusResource,
  SystemLogsResource,
  ConfigurationResource,
};

/**
 * 利用可能な全てのMCPリソースのリスト
 */
export const ALL_RESOURCES = [
  DroneStatusResource,
  SystemLogsResource,
  ConfigurationResource,
] as const;

/**
 * リソース名とクラスのマッピング
 */
export const RESOURCE_MAP = {
  drone_status: DroneStatusResource,
  system_logs: SystemLogsResource,
  configuration: ConfigurationResource,
} as const;

export type ResourceName = keyof typeof RESOURCE_MAP;