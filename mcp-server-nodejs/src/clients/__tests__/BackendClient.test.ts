/**
 * Tests for BackendClient
 * Comprehensive test suite for API communication with FastAPI backend
 */

import axios, { type AxiosInstance } from 'axios';
import { BackendClient } from '../BackendClient.js';
import { ErrorHandler } from '@/utils/errors.js';
import { logger } from '@/utils/logger.js';
import type { Config, DroneStatus, SystemStatus } from '@/types/index.js';
import type {
  Drone,
  MoveCommand,
  RotateCommand,
  Photo,
  Dataset,
  CreateDatasetRequest,
  ScanDronesResponse,
  HealthCheckResponse,
  CommandResponse,
  SuccessResponse,
} from '@/types/api_types.js';

// Mock dependencies
jest.mock('axios');
jest.mock('@/utils/logger.js');
jest.mock('@/utils/errors.js');

const mockedAxios = jest.mocked(axios);
const mockedLogger = jest.mocked(logger);
const mockedErrorHandler = jest.mocked(ErrorHandler);

describe('BackendClient', () => {
  let backendClient: BackendClient;
  let mockAxiosInstance: jest.Mocked<AxiosInstance>;
  
  const mockConfig: Config = {
    backendUrl: 'http://localhost:8000',
    timeout: 5000,
    logLevel: 'info',
    mcpPort: 3001,
    nlpConfidenceThreshold: 0.7,
  };

  beforeEach(() => {
    // Create mock axios instance
    mockAxiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
      delete: jest.fn(),
      put: jest.fn(),
      patch: jest.fn(),
      interceptors: {
        request: {
          use: jest.fn(),
          eject: jest.fn(),
        },
        response: {
          use: jest.fn(),
          eject: jest.fn(),
        },
      },
    } as any;

    mockedAxios.create.mockReturnValue(mockAxiosInstance);
    mockedErrorHandler.handleError.mockImplementation((error) => error);
    mockedErrorHandler.fromHttpStatus.mockImplementation((status, message) => 
      new Error(`HTTP ${status}: ${message}`)
    );

    backendClient = new BackendClient(mockConfig);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Constructor and Setup', () => {
    test('should create axios instance with correct config', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: mockConfig.backendUrl,
        timeout: mockConfig.timeout,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'MCP-Drone-Server/1.0.0',
        },
      });
    });

    test('should setup request and response interceptors', () => {
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });

    test('should have correct interceptor configuration', () => {
      // Verify request interceptor was called
      const requestInterceptorCall = mockAxiosInstance.interceptors.request.use.mock.calls[0];
      expect(requestInterceptorCall).toBeDefined();
      expect(typeof requestInterceptorCall[0]).toBe('function'); // success handler
      expect(typeof requestInterceptorCall[1]).toBe('function'); // error handler

      // Verify response interceptor was called
      const responseInterceptorCall = mockAxiosInstance.interceptors.response.use.mock.calls[0];
      expect(responseInterceptorCall).toBeDefined();
      expect(typeof responseInterceptorCall[0]).toBe('function'); // success handler
      expect(typeof responseInterceptorCall[1]).toBe('function'); // error handler
    });
  });

  describe('Drone Management APIs', () => {
    describe('getDrones', () => {
      test('should get drone list successfully', async () => {
        const mockDrones: Drone[] = [
          { id: 'drone-1', name: 'Test Drone 1', status: 'connected' },
          { id: 'drone-2', name: 'Test Drone 2', status: 'disconnected' },
        ];

        mockAxiosInstance.get.mockResolvedValue({ data: mockDrones });

        const result = await backendClient.getDrones();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/drones');
        expect(result).toEqual(mockDrones);
      });

      test('should handle error in getDrones', async () => {
        const mockError = new Error('Network error');
        mockAxiosInstance.get.mockRejectedValue(mockError);

        await expect(backendClient.getDrones()).rejects.toThrow();
        expect(mockedErrorHandler.handleError).toHaveBeenCalledWith(
          mockError,
          { operation: 'BackendClient.getDrones' }
        );
      });
    });

    describe('getDroneStatus', () => {
      test('should get status for all drones when no ID specified', async () => {
        const mockStatuses: DroneStatus[] = [
          global.createMockDroneStatus(),
          { ...global.createMockDroneStatus(), id: 'drone-2' },
        ];

        mockAxiosInstance.get.mockResolvedValue({ data: mockStatuses });

        const result = await backendClient.getDroneStatus();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/drones/status');
        expect(result).toEqual(mockStatuses);
      });

      test('should get status for specific drone when ID provided', async () => {
        const mockStatus: DroneStatus = global.createMockDroneStatus();
        mockAxiosInstance.get.mockResolvedValue({ data: mockStatus });

        const result = await backendClient.getDroneStatus('drone-1');

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/drones/drone-1/status');
        expect(result).toEqual([mockStatus]); // Should wrap single result in array
      });

      test('should handle array response correctly', async () => {
        const mockStatuses: DroneStatus[] = [global.createMockDroneStatus()];
        mockAxiosInstance.get.mockResolvedValue({ data: mockStatuses });

        const result = await backendClient.getDroneStatus();

        expect(result).toEqual(mockStatuses);
        expect(Array.isArray(result)).toBe(true);
      });
    });

    describe('connectDrone', () => {
      test('should connect to drone successfully', async () => {
        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Connected successfully',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.connectDrone('drone-1');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/drones/drone-1/connect');
        expect(result).toEqual(mockResponse);
      });

      test('should handle connection error', async () => {
        const mockError = new Error('Connection failed');
        mockAxiosInstance.post.mockRejectedValue(mockError);

        await expect(backendClient.connectDrone('drone-1')).rejects.toThrow();
        expect(mockedErrorHandler.handleError).toHaveBeenCalledWith(
          mockError,
          'BackendClient.connectDrone'
        );
      });
    });

    describe('disconnectDrone', () => {
      test('should disconnect from drone successfully', async () => {
        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Disconnected successfully',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.disconnectDrone('drone-1');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/drones/drone-1/disconnect');
        expect(result).toEqual(mockResponse);
      });
    });

    describe('Flight Control APIs', () => {
      test('should takeoff drone successfully', async () => {
        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Takeoff completed',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.takeoffDrone('drone-1');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/drones/drone-1/takeoff');
        expect(result).toEqual(mockResponse);
      });

      test('should land drone successfully', async () => {
        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Landing completed',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.landDrone('drone-1');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/drones/drone-1/land');
        expect(result).toEqual(mockResponse);
      });

      test('should move drone with command', async () => {
        const moveCommand: MoveCommand = {
          direction: 'forward',
          distance: 100,
        };

        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Movement completed',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.moveDrone('drone-1', moveCommand);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/drones/drone-1/move',
          moveCommand
        );
        expect(result).toEqual(mockResponse);
      });

      test('should rotate drone with command', async () => {
        const rotateCommand: RotateCommand = {
          direction: 'clockwise',
          angle: 90,
        };

        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Rotation completed',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.rotateDrone('drone-1', rotateCommand);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/drones/drone-1/rotate',
          rotateCommand
        );
        expect(result).toEqual(mockResponse);
      });

      test('should execute emergency stop', async () => {
        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Emergency stop executed',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.emergencyStopDrone('drone-1');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/drones/drone-1/emergency');
        expect(result).toEqual(mockResponse);
      });
    });

    describe('scanDrones', () => {
      test('should scan for drones successfully', async () => {
        const mockResponse: ScanDronesResponse = {
          drones: ['drone-1', 'drone-2'],
          count: 2,
          message: 'Scan completed',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.scanDrones();

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/drones/scan');
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('Camera APIs', () => {
    describe('Camera Streaming', () => {
      test('should start camera stream', async () => {
        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Streaming started',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.startCameraStream('drone-1');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/drones/drone-1/camera/stream/start'
        );
        expect(result).toEqual(mockResponse);
      });

      test('should stop camera stream', async () => {
        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Streaming stopped',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.stopCameraStream('drone-1');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/drones/drone-1/camera/stream/stop'
        );
        expect(result).toEqual(mockResponse);
      });
    });

    describe('takePhoto', () => {
      test('should take photo successfully', async () => {
        const mockPhoto: Photo = {
          id: 'photo-1',
          filename: 'photo_20240101_120000.jpg',
          url: '/api/photos/photo-1',
          timestamp: new Date().toISOString(),
          metadata: {
            drone_id: 'drone-1',
            resolution: '1920x1080',
            quality: 'high',
          },
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockPhoto });

        const result = await backendClient.takePhoto('drone-1');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/drones/drone-1/camera/photo');
        expect(result).toEqual(mockPhoto);
      });
    });
  });

  describe('System APIs', () => {
    describe('healthCheck', () => {
      test('should perform health check successfully', async () => {
        const mockResponse: HealthCheckResponse = {
          status: 'healthy',
          timestamp: new Date().toISOString(),
          services: {
            database: { status: 'up', message: 'Connected' },
            backend: { status: 'up', message: 'Running' },
          },
        };

        mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.healthCheck();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/system/health');
        expect(result).toEqual(mockResponse);
      });
    });

    describe('getSystemStatus', () => {
      test('should get system status successfully', async () => {
        const mockStatus: SystemStatus = global.createMockSystemStatus();

        mockAxiosInstance.get.mockResolvedValue({ data: mockStatus });

        const result = await backendClient.getSystemStatus();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/system/status');
        expect(result).toEqual(mockStatus);
      });
    });

    describe('executeCommand', () => {
      test('should execute command with parameters', async () => {
        const mockResponse: CommandResponse = {
          success: true,
          result: { status: 'completed', data: 'Command executed' },
          message: 'Command completed successfully',
        };

        const params = { param1: 'value1', param2: 42 };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.executeCommand('drone-1', 'test_command', params);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/drones/drone-1/command',
          {
            command: 'test_command',
            params,
          }
        );
        expect(result).toEqual(mockResponse);
      });

      test('should execute command without parameters', async () => {
        const mockResponse: CommandResponse = {
          success: true,
          result: { status: 'completed' },
          message: 'Command completed',
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.executeCommand('drone-1', 'simple_command');

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/api/drones/drone-1/command',
          {
            command: 'simple_command',
            params: {},
          }
        );
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('Vision APIs', () => {
    describe('Dataset Management', () => {
      test('should get datasets successfully', async () => {
        const mockDatasets: Dataset[] = [
          {
            id: 'dataset-1',
            name: 'Test Dataset',
            description: 'Test dataset for object detection',
            created_at: new Date().toISOString(),
            image_count: 100,
            labels: ['person', 'car'],
          },
        ];

        mockAxiosInstance.get.mockResolvedValue({ data: mockDatasets });

        const result = await backendClient.getDatasets();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/vision/datasets');
        expect(result).toEqual(mockDatasets);
      });

      test('should create dataset successfully', async () => {
        const createRequest: CreateDatasetRequest = {
          name: 'New Dataset',
          description: 'A new dataset for training',
          labels: ['person', 'vehicle'],
        };

        const mockDataset: Dataset = {
          id: 'dataset-2',
          ...createRequest,
          created_at: new Date().toISOString(),
          image_count: 0,
        };

        mockAxiosInstance.post.mockResolvedValue({ data: mockDataset });

        const result = await backendClient.createDataset(createRequest);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/vision/datasets', createRequest);
        expect(result).toEqual(mockDataset);
      });

      test('should delete dataset successfully', async () => {
        const mockResponse: SuccessResponse = {
          success: true,
          message: 'Dataset deleted successfully',
        };

        mockAxiosInstance.delete.mockResolvedValue({ data: mockResponse });

        const result = await backendClient.deleteDataset('dataset-1');

        expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/api/vision/datasets/dataset-1');
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('Dashboard APIs', () => {
    test('should get dashboard drones', async () => {
      const mockDrones: DroneStatus[] = [
        global.createMockDroneStatus(),
        { ...global.createMockDroneStatus(), id: 'drone-2' },
      ];

      mockAxiosInstance.get.mockResolvedValue({ data: mockDrones });

      const result = await backendClient.getDashboardDrones();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/dashboard/drones');
      expect(result).toEqual(mockDrones);
    });

    test('should get dashboard system status', async () => {
      const mockStatus: SystemStatus = global.createMockSystemStatus();

      mockAxiosInstance.get.mockResolvedValue({ data: mockStatus });

      const result = await backendClient.getDashboardSystemStatus();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/dashboard/system');
      expect(result).toEqual(mockStatus);
    });
  });

  describe('Connection Testing', () => {
    describe('testConnection', () => {
      test('should return true when health check succeeds', async () => {
        const mockHealthResponse: HealthCheckResponse = {
          status: 'healthy',
          timestamp: new Date().toISOString(),
          services: {},
        };

        mockAxiosInstance.get.mockResolvedValue({ data: mockHealthResponse });

        const result = await backendClient.testConnection();

        expect(result).toBe(true);
        expect(mockedLogger.info).toHaveBeenCalledWith(
          `Backend connection successful: ${mockConfig.backendUrl}`
        );
      });

      test('should return false when health check fails', async () => {
        const mockError = new Error('Connection failed');
        mockAxiosInstance.get.mockRejectedValue(mockError);

        const result = await backendClient.testConnection();

        expect(result).toBe(false);
        expect(mockedLogger.error).toHaveBeenCalledWith(
          `Backend connection failed: ${mockConfig.backendUrl}`,
          mockError
        );
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle network errors correctly', async () => {
      const networkError = new Error('Network Error');
      mockAxiosInstance.get.mockRejectedValue(networkError);

      await expect(backendClient.getDrones()).rejects.toThrow();
      expect(mockedErrorHandler.handleError).toHaveBeenCalledWith(
        networkError,
        { operation: 'BackendClient.getDrones' }
      );
    });

    test('should handle timeout errors correctly', async () => {
      const timeoutError = { code: 'ECONNABORTED', message: 'timeout of 5000ms exceeded' };
      mockAxiosInstance.get.mockRejectedValue(timeoutError);

      await expect(backendClient.getDrones()).rejects.toThrow();
      expect(mockedErrorHandler.handleError).toHaveBeenCalled();
    });

    test('should handle HTTP error responses correctly', async () => {
      const httpError = {
        response: {
          status: 404,
          data: { message: 'Not Found' },
        },
        config: { url: '/api/drones' },
      };
      mockAxiosInstance.get.mockRejectedValue(httpError);

      await expect(backendClient.getDrones()).rejects.toThrow();
      expect(mockedErrorHandler.handleError).toHaveBeenCalled();
    });
  });

  describe('Request Interceptor', () => {
    test('should log debug information on request', () => {
      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][0];
      
      const mockConfig = {
        method: 'GET',
        url: '/api/drones',
      };

      const result = requestInterceptor(mockConfig);

      expect(result).toBe(mockConfig);
      expect(mockedLogger.debug).toHaveBeenCalledWith('Making request to: GET /api/drones');
    });

    test('should handle request errors', () => {
      const requestErrorInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][1];
      const mockError = new Error('Request setup error');

      expect(() => requestErrorInterceptor(mockError)).rejects.toEqual(mockError);
      expect(mockedLogger.error).toHaveBeenCalledWith('Request error:', mockError);
    });
  });

  describe('Response Interceptor', () => {
    test('should log debug information on response', () => {
      const responseInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][0];
      
      const mockResponse = {
        status: 200,
        config: { url: '/api/drones' },
        data: {},
      };

      const result = responseInterceptor(mockResponse);

      expect(result).toBe(mockResponse);
      expect(mockedLogger.debug).toHaveBeenCalledWith('Response: 200 /api/drones');
    });

    test('should handle response errors with proper error formatting', () => {
      const responseErrorInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      
      const mockError = {
        response: {
          status: 500,
          data: { message: 'Internal Server Error' },
        },
        config: { url: '/api/drones' },
        message: 'Network Error',
      };

      mockedErrorHandler.fromHttpStatus.mockReturnValue(
        new Error('HTTP 500: Internal Server Error')
      );

      expect(() => responseErrorInterceptor(mockError)).rejects.toThrow();
      
      expect(mockedErrorHandler.fromHttpStatus).toHaveBeenCalledWith(
        500,
        'Internal Server Error'
      );
      
      expect(mockedLogger.error).toHaveBeenCalledWith('Response error:', {
        url: '/api/drones',
        status: 500,
        message: 'Internal Server Error',
      });
    });

    test('should handle response errors without status code', () => {
      const responseErrorInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      
      const mockError = {
        message: 'Network Error',
        config: { url: '/api/drones' },
      };

      mockedErrorHandler.fromHttpStatus.mockReturnValue(
        new Error('HTTP 500: Network Error')
      );

      expect(() => responseErrorInterceptor(mockError)).rejects.toThrow();
      
      expect(mockedErrorHandler.fromHttpStatus).toHaveBeenCalledWith(
        500,
        'Network Error'
      );
    });
  });

  describe('Multipart Form Data Handling', () => {
    test('should handle FormData for image uploads', async () => {
      const mockFormData = new FormData();
      mockFormData.append('file', new Blob(['test']), 'test.jpg');

      const mockResponse = {
        id: 'image-1',
        filename: 'test.jpg',
        dataset_id: 'dataset-1',
      };

      mockAxiosInstance.post.mockResolvedValue({ data: mockResponse });

      const result = await backendClient.addImageToDataset('dataset-1', mockFormData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/api/vision/datasets/dataset-1/images',
        mockFormData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      expect(result).toEqual(mockResponse);
    });
  });
});