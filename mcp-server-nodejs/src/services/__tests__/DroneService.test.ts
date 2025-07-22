import { jest } from '@jest/globals';
import { DroneService } from '../DroneService.js';
import { DroneError } from '@/types/index.js';
import type { Config } from '@/types/index.js';

// Mock dependencies
jest.mock('@/clients/BackendClient.js');
jest.mock('@/utils/logger.js');

const mockConfig: Config = {
  port: 3001,
  backendUrl: 'http://localhost:8000',
  logLevel: 'error',
  timeout: 5000,
};

describe('DroneService', () => {
  let droneService: DroneService;
  let mockBackendClient: any;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock BackendClient
    const { BackendClient } = require('@/clients/BackendClient.js');
    mockBackendClient = {
      getDroneStatus: jest.fn(),
      scanDrones: jest.fn(),
      healthCheck: jest.fn(),
      getSystemStatus: jest.fn(),
      executeCommand: jest.fn(),
      testConnection: jest.fn(),
    };
    
    BackendClient.mockImplementation(() => mockBackendClient);
    
    droneService = new DroneService(mockConfig);
  });

  describe('constructor', () => {
    it('should create DroneService instance', () => {
      expect(droneService).toBeInstanceOf(DroneService);
    });
  });

  describe('getDroneStatus', () => {
    it('should return drone status from backend', async () => {
      const mockStatus = global.createMockDroneStatus();
      mockBackendClient.getDroneStatus.mockResolvedValue([mockStatus]);

      const result = await droneService.getDroneStatus();

      expect(result).toEqual([mockStatus]);
      expect(mockBackendClient.getDroneStatus).toHaveBeenCalledWith(undefined);
    });

    it('should return specific drone status when droneId provided', async () => {
      const mockStatus = global.createMockDroneStatus();
      mockBackendClient.getDroneStatus.mockResolvedValue([mockStatus]);

      const result = await droneService.getDroneStatus('test-drone-1');

      expect(result).toEqual([mockStatus]);
      expect(mockBackendClient.getDroneStatus).toHaveBeenCalledWith('test-drone-1');
    });

    it('should handle backend errors', async () => {
      mockBackendClient.getDroneStatus.mockRejectedValue(new Error('Backend error'));

      await expect(droneService.getDroneStatus()).rejects.toThrow();
    });

    it('should use cache for repeated requests', async () => {
      const mockStatus = global.createMockDroneStatus();
      mockBackendClient.getDroneStatus.mockResolvedValue([mockStatus]);

      // First call
      await droneService.getDroneStatus('test-drone-1');
      
      // Second call (should use cache)
      await droneService.getDroneStatus('test-drone-1');

      // Backend should only be called once due to caching
      expect(mockBackendClient.getDroneStatus).toHaveBeenCalledTimes(1);
    });
  });

  describe('getActiveDrones', () => {
    it('should filter active drones', async () => {
      const mockStatuses = [
        { ...global.createMockDroneStatus(), id: 'drone-1', status: 'connected' },
        { ...global.createMockDroneStatus(), id: 'drone-2', status: 'disconnected' },
        { ...global.createMockDroneStatus(), id: 'drone-3', status: 'flying' },
      ] as const;
      
      mockBackendClient.getDroneStatus.mockResolvedValue(mockStatuses);

      const result = await droneService.getActiveDrones();

      expect(result).toHaveLength(2);
      expect(result.map(d => d.id)).toEqual(['drone-1', 'drone-3']);
    });
  });

  describe('scanForDrones', () => {
    it('should scan for drones successfully', async () => {
      const mockResult = { message: 'Scan completed', found: 2 };
      mockBackendClient.scanDrones.mockResolvedValue(mockResult);

      const result = await droneService.scanForDrones();

      expect(result).toEqual(mockResult);
      expect(mockBackendClient.scanDrones).toHaveBeenCalled();
    });

    it('should handle scan errors', async () => {
      mockBackendClient.scanDrones.mockRejectedValue(new Error('Scan failed'));

      await expect(droneService.scanForDrones()).rejects.toThrow();
    });
  });

  describe('getSystemStatus', () => {
    it('should return system status', async () => {
      const mockStatus = global.createMockSystemStatus();
      mockBackendClient.getSystemStatus.mockResolvedValue(mockStatus);

      const result = await droneService.getSystemStatus();

      expect(result).toEqual(mockStatus);
      expect(mockBackendClient.getSystemStatus).toHaveBeenCalled();
    });
  });

  describe('performHealthCheck', () => {
    it('should perform health check', async () => {
      const mockHealth = { status: 'healthy', timestamp: new Date().toISOString() };
      mockBackendClient.healthCheck.mockResolvedValue(mockHealth);

      const result = await droneService.performHealthCheck();

      expect(result).toEqual(mockHealth);
      expect(mockBackendClient.healthCheck).toHaveBeenCalled();
    });
  });

  describe('executeCommand', () => {
    it('should execute command successfully', async () => {
      const mockStatus = global.createMockDroneStatus();
      mockBackendClient.getDroneStatus.mockResolvedValue([mockStatus]);
      mockBackendClient.executeCommand.mockResolvedValue({
        success: true,
        message: 'Command executed',
      });

      const result = await droneService.executeCommand('test-drone-1', 'takeoff');

      expect(result.success).toBe(true);
      expect(mockBackendClient.executeCommand).toHaveBeenCalledWith(
        'test-drone-1',
        'takeoff',
        {}
      );
    });

    it('should validate dangerous commands', async () => {
      const mockStatus = global.createMockDroneStatus();
      mockBackendClient.getDroneStatus.mockResolvedValue([mockStatus]);

      await expect(
        droneService.executeCommand('test-drone-1', 'emergency')
      ).rejects.toThrow(DroneError);
    });

    it('should validate drone exists', async () => {
      mockBackendClient.getDroneStatus.mockResolvedValue([]);

      await expect(
        droneService.executeCommand('nonexistent-drone', 'takeoff')
      ).rejects.toThrow(DroneError);
    });

    it('should validate drone is not in error state', async () => {
      const errorDrone = { ...global.createMockDroneStatus(), status: 'error' };
      mockBackendClient.getDroneStatus.mockResolvedValue([errorDrone]);

      await expect(
        droneService.executeCommand('test-drone-1', 'takeoff')
      ).rejects.toThrow(DroneError);
    });

    it('should validate drone is not disconnected', async () => {
      const disconnectedDrone = { ...global.createMockDroneStatus(), status: 'disconnected' };
      mockBackendClient.getDroneStatus.mockResolvedValue([disconnectedDrone]);

      await expect(
        droneService.executeCommand('test-drone-1', 'takeoff')
      ).rejects.toThrow(DroneError);
    });
  });

  describe('testBackendConnection', () => {
    it('should return true when connection succeeds', async () => {
      mockBackendClient.testConnection.mockResolvedValue(true);

      const result = await droneService.testBackendConnection();

      expect(result).toBe(true);
    });

    it('should return false when connection fails', async () => {
      mockBackendClient.testConnection.mockResolvedValue(false);

      const result = await droneService.testBackendConnection();

      expect(result).toBe(false);
    });

    it('should handle connection errors gracefully', async () => {
      mockBackendClient.testConnection.mockRejectedValue(new Error('Connection error'));

      const result = await droneService.testBackendConnection();

      expect(result).toBe(false);
    });
  });
});