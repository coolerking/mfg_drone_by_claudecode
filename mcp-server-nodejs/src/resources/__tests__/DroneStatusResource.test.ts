/**
 * Tests for DroneStatusResource
 * Test suite for drone status MCP resource
 */

import { DroneStatusResource } from '../DroneStatusResource.js';
import { DroneService } from '@/services/DroneService.js';
import { logger } from '@/utils/logger.js';
import type { DroneStatus, SystemStatus } from '@/types/index.js';

// Mock dependencies
jest.mock('@/services/DroneService.js');
jest.mock('@/utils/logger.js');

const mockedLogger = jest.mocked(logger);

describe('DroneStatusResource', () => {
  let mockDroneService: jest.Mocked<DroneService>;
  let droneStatusResource: DroneStatusResource;

  beforeEach(() => {
    mockDroneService = new DroneService({} as any) as jest.Mocked<DroneService>;
    droneStatusResource = new DroneStatusResource(mockDroneService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Properties', () => {
    test('should have correct description', () => {
      expect(droneStatusResource.getDescription()).toBe(
        'Real-time status information for all connected drones including battery levels, positions, and operational states.'
      );
    });

    test('should have correct URI', () => {
      expect(droneStatusResource.getUri()).toBe('mcp://drone-status/status');
    });

    test('should have correct MIME type', () => {
      expect(droneStatusResource.getMimeType()).toBe('application/json');
    });
  });

  describe('getContents Method', () => {
    const mockDrones: DroneStatus[] = [
      {
        id: 'drone-1',
        name: 'Test Drone 1',
        status: 'connected',
        batteryLevel: 85,
        position: { x: 1.0, y: 2.0, z: 1.5 },
        lastSeen: '2024-01-01T10:00:00Z',
      },
      {
        id: 'drone-2',
        name: 'Test Drone 2',
        status: 'flying',
        batteryLevel: 65,
        position: { x: -1.0, y: 1.5, z: 2.0 },
        lastSeen: '2024-01-01T10:01:00Z',
      },
      {
        id: 'drone-3',
        name: 'Test Drone 3',
        status: 'idle',
        batteryLevel: 45,
        position: { x: 0, y: 0, z: 0 },
        lastSeen: '2024-01-01T09:58:00Z',
      },
      {
        id: 'drone-4',
        name: 'Test Drone 4',
        status: 'error',
        batteryLevel: 15,
        position: { x: 0, y: 0, z: 0 },
        lastSeen: '2024-01-01T09:55:00Z',
      },
      {
        id: 'drone-5',
        name: 'Test Drone 5',
        status: 'disconnected',
        batteryLevel: 0,
        lastSeen: '2024-01-01T09:50:00Z',
      },
    ];

    const mockSystemStatus: SystemStatus = global.createMockSystemStatus();

    beforeEach(() => {
      mockDroneService.getDroneStatus.mockResolvedValue(mockDrones);
      mockDroneService.getSystemStatus.mockResolvedValue(mockSystemStatus);
    });

    test('should return comprehensive drone status data', async () => {
      const result = await droneStatusResource.getContents();

      expect(result.contents).toHaveLength(1);
      expect(result.contents[0].mimeType).toBe('application/json');
      expect(result.contents[0].uri).toBe('mcp://drone-status/status');

      const data = JSON.parse(result.contents[0].text!);
      
      expect(data).toHaveProperty('timestamp');
      expect(data).toHaveProperty('summary');
      expect(data).toHaveProperty('drones');
      expect(data).toHaveProperty('systemHealth');
    });

    test('should calculate correct summary statistics', async () => {
      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.summary).toEqual({
        totalDrones: 5,
        connectedDrones: 1,
        flyingDrones: 1,
        idleDrones: 1,
        errorDrones: 1,
        disconnectedDrones: 1,
      });
    });

    test('should include detailed drone information', async () => {
      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.drones).toHaveLength(5);
      
      const drone1 = data.drones.find((d: any) => d.id === 'drone-1');
      expect(drone1).toEqual({
        id: 'drone-1',
        name: 'Test Drone 1',
        status: 'connected',
        batteryLevel: 85,
        position: { x: 1.0, y: 2.0, z: 1.5 },
        lastSeen: '2024-01-01T10:00:00Z',
        isActive: true,
        batteryStatus: 'high',
      });

      const drone4 = data.drones.find((d: any) => d.id === 'drone-4');
      expect(drone4.batteryStatus).toBe('critical');
      expect(drone4.isActive).toBe(false);

      const drone5 = data.drones.find((d: any) => d.id === 'drone-5');
      expect(drone5.position).toBe(null);
    });

    test('should include system health information', async () => {
      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.systemHealth).toHaveProperty('status', 'healthy');
      expect(data.systemHealth).toHaveProperty('services');
      expect(Array.isArray(data.systemHealth.services)).toBe(true);

      const backendService = data.systemHealth.services.find((s: any) => s.name === 'backend');
      expect(backendService).toEqual({
        name: 'backend',
        status: 'up',
        lastCheck: mockSystemStatus.services.backend.lastCheck,
        message: 'Service is running normally',
      });
    });

    test('should log debug information', async () => {
      await droneStatusResource.getContents();

      expect(mockedLogger.debug).toHaveBeenCalledWith('Retrieving drone status resource');
    });

    test('should handle drones without position', async () => {
      const dronesWithoutPosition = mockDrones.map(drone => ({
        ...drone,
        position: undefined,
      }));

      mockDroneService.getDroneStatus.mockResolvedValue(dronesWithoutPosition);

      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      data.drones.forEach((drone: any) => {
        expect(drone.position).toBe(null);
      });
    });

    test('should handle empty drone list', async () => {
      mockDroneService.getDroneStatus.mockResolvedValue([]);

      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.summary).toEqual({
        totalDrones: 0,
        connectedDrones: 0,
        flyingDrones: 0,
        idleDrones: 0,
        errorDrones: 0,
        disconnectedDrones: 0,
      });
      expect(data.drones).toEqual([]);
    });
  });

  describe('Battery Status Logic', () => {
    test('should correctly classify battery levels', async () => {
      const testDrones: DroneStatus[] = [
        { id: 'high', name: 'High Battery', status: 'connected', batteryLevel: 85, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'medium', name: 'Medium Battery', status: 'connected', batteryLevel: 65, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'low', name: 'Low Battery', status: 'connected', batteryLevel: 35, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'critical', name: 'Critical Battery', status: 'connected', batteryLevel: 15, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'unknown', name: 'Unknown Battery', status: 'connected', lastSeen: '2024-01-01T10:00:00Z' },
      ];

      mockDroneService.getDroneStatus.mockResolvedValue(testDrones);
      mockDroneService.getSystemStatus.mockResolvedValue(global.createMockSystemStatus());

      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const batteryStatuses = data.drones.map((drone: any) => ({
        id: drone.id,
        batteryStatus: drone.batteryStatus
      }));

      expect(batteryStatuses).toEqual([
        { id: 'high', batteryStatus: 'high' },
        { id: 'medium', batteryStatus: 'medium' },
        { id: 'low', batteryStatus: 'low' },
        { id: 'critical', batteryStatus: 'critical' },
        { id: 'unknown', batteryStatus: 'unknown' },
      ]);
    });

    test('should handle edge cases for battery levels', async () => {
      const edgeCaseDrones: DroneStatus[] = [
        { id: 'edge-75', name: 'Edge 75%', status: 'connected', batteryLevel: 75, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'edge-50', name: 'Edge 50%', status: 'connected', batteryLevel: 50, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'edge-25', name: 'Edge 25%', status: 'connected', batteryLevel: 25, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'edge-0', name: 'Edge 0%', status: 'connected', batteryLevel: 0, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'edge-100', name: 'Edge 100%', status: 'connected', batteryLevel: 100, lastSeen: '2024-01-01T10:00:00Z' },
      ];

      mockDroneService.getDroneStatus.mockResolvedValue(edgeCaseDrones);
      mockDroneService.getSystemStatus.mockResolvedValue(global.createMockSystemStatus());

      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const batteryStatuses = data.drones.map((drone: any) => ({
        batteryLevel: drone.batteryLevel,
        batteryStatus: drone.batteryStatus
      }));

      expect(batteryStatuses).toEqual([
        { batteryLevel: 75, batteryStatus: 'high' },
        { batteryLevel: 50, batteryStatus: 'medium' },
        { batteryLevel: 25, batteryStatus: 'low' },
        { batteryLevel: 0, batteryStatus: 'critical' },
        { batteryLevel: 100, batteryStatus: 'high' },
      ]);
    });
  });

  describe('Drone Activity Classification', () => {
    test('should correctly identify active drones', async () => {
      const allStatusDrones: DroneStatus[] = [
        { id: 'connected', name: 'Connected', status: 'connected', batteryLevel: 50, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'flying', name: 'Flying', status: 'flying', batteryLevel: 50, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'idle', name: 'Idle', status: 'idle', batteryLevel: 50, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'error', name: 'Error', status: 'error', batteryLevel: 50, lastSeen: '2024-01-01T10:00:00Z' },
        { id: 'disconnected', name: 'Disconnected', status: 'disconnected', batteryLevel: 50, lastSeen: '2024-01-01T10:00:00Z' },
      ];

      mockDroneService.getDroneStatus.mockResolvedValue(allStatusDrones);
      mockDroneService.getSystemStatus.mockResolvedValue(global.createMockSystemStatus());

      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const activities = data.drones.map((drone: any) => ({
        status: drone.status,
        isActive: drone.isActive
      }));

      expect(activities).toEqual([
        { status: 'connected', isActive: true },
        { status: 'flying', isActive: true },
        { status: 'idle', isActive: true },
        { status: 'error', isActive: false },
        { status: 'disconnected', isActive: false },
      ]);
    });
  });

  describe('Error Handling', () => {
    test('should handle getDroneStatus errors', async () => {
      const error = new Error('Failed to get drone status');
      mockDroneService.getDroneStatus.mockRejectedValue(error);

      const result = await droneStatusResource.getContents();

      expect(result.contents[0].mimeType).toBe('text/plain');
      expect(result.contents[0].text).toContain('Error retrieving DroneStatusResource');
      expect(mockedLogger.error).toHaveBeenCalledWith(
        'Error retrieving drone status resource:',
        error
      );
    });

    test('should handle getSystemStatus errors', async () => {
      mockDroneService.getDroneStatus.mockResolvedValue([]);
      mockDroneService.getSystemStatus.mockRejectedValue(new Error('System status failed'));

      const result = await droneStatusResource.getContents();

      expect(result.contents[0].mimeType).toBe('text/plain');
      expect(result.contents[0].text).toContain('Error retrieving DroneStatusResource');
    });

    test('should handle partial errors gracefully', async () => {
      // When getDroneStatus succeeds but getSystemStatus fails
      mockDroneService.getDroneStatus.mockResolvedValue([global.createMockDroneStatus()]);
      mockDroneService.getSystemStatus.mockRejectedValue(new Error('Partial error'));

      const result = await droneStatusResource.getContents();

      // Should still fail and return error response
      expect(result.contents[0].mimeType).toBe('text/plain');
      expect(result.contents[0].text).toContain('Error retrieving DroneStatusResource');
    });
  });

  describe('Data Transformation and Formatting', () => {
    test('should format timestamps correctly', async () => {
      const mockTimestamp = '2024-01-01T10:00:00.000Z';
      const drones = [
        { id: 'test', name: 'Test', status: 'connected', batteryLevel: 50, lastSeen: mockTimestamp }
      ];
      
      mockDroneService.getDroneStatus.mockResolvedValue(drones);
      mockDroneService.getSystemStatus.mockResolvedValue(global.createMockSystemStatus());

      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      expect(data.drones[0].lastSeen).toBe(mockTimestamp);
      expect(new Date(data.timestamp)).toBeInstanceOf(Date);
    });

    test('should handle missing optional fields', async () => {
      const minimalDrones: DroneStatus[] = [
        {
          id: 'minimal',
          name: 'Minimal Drone',
          status: 'connected',
          lastSeen: '2024-01-01T10:00:00Z',
          // Missing batteryLevel and position
        },
      ];

      mockDroneService.getDroneStatus.mockResolvedValue(minimalDrones);
      mockDroneService.getSystemStatus.mockResolvedValue(global.createMockSystemStatus());

      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const drone = data.drones[0];
      expect(drone.batteryLevel).toBeUndefined();
      expect(drone.position).toBe(null);
      expect(drone.batteryStatus).toBe('unknown');
    });

    test('should handle services with missing information', async () => {
      const systemStatusWithMissingServices: SystemStatus = {
        ...global.createMockSystemStatus(),
        services: {
          backend: {
            status: 'up' as const,
            lastCheck: '2024-01-01T10:00:00Z',
            message: 'Running normally',
          },
          database: {
            status: 'down' as const,
            lastCheck: '2024-01-01T09:59:00Z',
            // Missing message
          },
          incomplete: {
            // Missing status and lastCheck
          } as any,
        },
      };

      mockDroneService.getDroneStatus.mockResolvedValue([]);
      mockDroneService.getSystemStatus.mockResolvedValue(systemStatusWithMissingServices);

      const result = await droneStatusResource.getContents();
      const data = JSON.parse(result.contents[0].text!);

      const services = data.systemHealth.services;
      
      const backendService = services.find((s: any) => s.name === 'backend');
      expect(backendService.message).toBe('Running normally');
      
      const databaseService = services.find((s: any) => s.name === 'database');
      expect(databaseService.message).toBeUndefined();
      
      const incompleteService = services.find((s: any) => s.name === 'incomplete');
      expect(incompleteService.status).toBe('unknown');
      expect(new Date(incompleteService.lastCheck)).toBeInstanceOf(Date);
    });
  });

  describe('Response Content Structure', () => {
    test('should always return properly structured response', async () => {
      mockDroneService.getDroneStatus.mockResolvedValue([]);
      mockDroneService.getSystemStatus.mockResolvedValue(global.createMockSystemStatus());

      const result = await droneStatusResource.getContents();

      expect(result).toHaveProperty('contents');
      expect(Array.isArray(result.contents)).toBe(true);
      expect(result.contents).toHaveLength(1);

      const content = result.contents[0];
      expect(content).toHaveProperty('uri', 'mcp://drone-status/status');
      expect(content).toHaveProperty('mimeType', 'application/json');
      expect(content).toHaveProperty('text');
      expect(typeof content.text).toBe('string');
    });

    test('should produce valid JSON in response text', async () => {
      mockDroneService.getDroneStatus.mockResolvedValue([global.createMockDroneStatus()]);
      mockDroneService.getSystemStatus.mockResolvedValue(global.createMockSystemStatus());

      const result = await droneStatusResource.getContents();
      
      expect(() => {
        JSON.parse(result.contents[0].text!);
      }).not.toThrow();
    });
  });

  describe('Performance and Scale', () => {
    test('should handle large number of drones', async () => {
      const largeDroneList: DroneStatus[] = Array.from({ length: 1000 }, (_, i) => ({
        id: `drone-${i}`,
        name: `Test Drone ${i}`,
        status: ['connected', 'flying', 'idle', 'error', 'disconnected'][i % 5] as any,
        batteryLevel: Math.floor(Math.random() * 100),
        position: { x: i, y: i * 2, z: 1.5 },
        lastSeen: new Date(Date.now() - i * 1000).toISOString(),
      }));

      mockDroneService.getDroneStatus.mockResolvedValue(largeDroneList);
      mockDroneService.getSystemStatus.mockResolvedValue(global.createMockSystemStatus());

      const startTime = Date.now();
      const result = await droneStatusResource.getContents();
      const endTime = Date.now();

      expect(endTime - startTime).toBeLessThan(5000); // Should complete within 5 seconds
      
      const data = JSON.parse(result.contents[0].text!);
      expect(data.summary.totalDrones).toBe(1000);
      expect(data.drones).toHaveLength(1000);
    });
  });
});