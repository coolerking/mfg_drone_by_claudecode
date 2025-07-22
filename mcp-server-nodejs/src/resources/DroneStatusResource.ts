import { BaseResource, type MCPResourceResponse } from './BaseResource.js';
import { logger } from '@/utils/logger.js';

/**
 * ドローン状態リソース
 * ドローンのリアルタイム状態情報を提供
 */
export class DroneStatusResource extends BaseResource {
  constructor(droneService: any) {
    super(droneService, 'DroneStatusResource', 'mcp://drone-status');
  }

  getDescription(): string {
    return 'Real-time status information for all connected drones including battery levels, positions, and operational states.';
  }

  getUri(): string {
    return `${this.baseUri}/status`;
  }

  getMimeType(): string {
    return 'application/json';
  }

  async getContents(): Promise<MCPResourceResponse> {
    try {
      logger.debug('Retrieving drone status resource');

      // 全てのドローンの状態を取得
      const allDrones = await this.droneService.getDroneStatus();
      
      // システム状態も取得
      const systemStatus = await this.droneService.getSystemStatus();
      
      // リソースデータを構築
      const resourceData = {
        timestamp: new Date().toISOString(),
        summary: {
          totalDrones: allDrones.length,
          connectedDrones: allDrones.filter(d => d.status === 'connected').length,
          flyingDrones: allDrones.filter(d => d.status === 'flying').length,
          idleDrones: allDrones.filter(d => d.status === 'idle').length,
          errorDrones: allDrones.filter(d => d.status === 'error').length,
          disconnectedDrones: allDrones.filter(d => d.status === 'disconnected').length,
        },
        drones: allDrones.map(drone => ({
          id: drone.id,
          name: drone.name,
          status: drone.status,
          batteryLevel: drone.batteryLevel,
          position: drone.position || null,
          lastSeen: drone.lastSeen,
          isActive: ['connected', 'flying', 'idle'].includes(drone.status),
          batteryStatus: this.getBatteryStatus(drone.batteryLevel),
        })),
        systemHealth: {
          status: systemStatus.status,
          services: Object.keys(systemStatus.services).map(service => ({
            name: service,
            status: systemStatus.services[service]?.status || 'unknown',
            lastCheck: systemStatus.services[service]?.lastCheck || new Date().toISOString(),
            message: systemStatus.services[service]?.message,
          })),
        },
      };

      return this.createJsonResponse(resourceData);
    } catch (error) {
      logger.error('Error retrieving drone status resource:', error);
      return this.handleError(error);
    }
  }

  /**
   * バッテリー状態の判定
   */
  private getBatteryStatus(batteryLevel?: number): string {
    if (batteryLevel === undefined) return 'unknown';
    
    if (batteryLevel >= 75) return 'high';
    if (batteryLevel >= 50) return 'medium';
    if (batteryLevel >= 25) return 'low';
    return 'critical';
  }
}