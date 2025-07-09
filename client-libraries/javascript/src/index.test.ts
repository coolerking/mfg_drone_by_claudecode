import { MCPClient, MCPClientError } from './index';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('MCPClient', () => {
  let client: MCPClient;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Create axios instance mock
    const mockAxiosInstance = {
      post: jest.fn(),
      get: jest.fn(),
      interceptors: {
        response: {
          use: jest.fn()
        }
      }
    };
    
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);
    
    client = new MCPClient({
      baseURL: 'http://localhost:8001',
      apiKey: 'test-key'
    });
  });

  describe('Constructor', () => {
    it('should create instance with config', () => {
      expect(client).toBeInstanceOf(MCPClient);
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'http://localhost:8001',
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'test-key'
        }
      });
    });

    it('should create instance with bearer token', () => {
      const clientWithToken = new MCPClient({
        baseURL: 'http://localhost:8001',
        bearerToken: 'test-token'
      });
      
      expect(clientWithToken).toBeInstanceOf(MCPClient);
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'http://localhost:8001',
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        }
      });
    });
  });

  describe('Natural Language Commands', () => {
    it('should execute command successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Command executed successfully',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const command = {
        command: 'ドローンAAに接続して'
      };

      const result = await client.executeCommand(command);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/command', command);
    });

    it('should execute batch command successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Batch command executed successfully',
          results: [],
          summary: {
            total_commands: 2,
            successful_commands: 2,
            failed_commands: 0,
            total_execution_time: 1.5
          },
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const batchCommand = {
        commands: [
          { command: 'ドローンAAに接続して' },
          { command: '離陸して' }
        ]
      };

      const result = await client.executeBatchCommand(batchCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/command/batch', batchCommand);
    });
  });

  describe('Drone Query APIs', () => {
    it('should get drones successfully', async () => {
      const mockResponse = {
        data: {
          drones: [
            {
              id: 'drone_001',
              name: 'Test Drone',
              type: 'real',
              status: 'available',
              capabilities: ['camera', 'movement']
            }
          ],
          count: 1,
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.get.mockResolvedValue(mockResponse);

      const result = await client.getDrones();
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.get).toHaveBeenCalledWith('/mcp/drones');
    });

    it('should get available drones successfully', async () => {
      const mockResponse = {
        data: {
          drones: [],
          count: 0,
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.get.mockResolvedValue(mockResponse);

      const result = await client.getAvailableDrones();
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.get).toHaveBeenCalledWith('/mcp/drones/available');
    });

    it('should get drone status successfully', async () => {
      const mockResponse = {
        data: {
          drone_id: 'drone_001',
          status: {
            connection_status: 'connected',
            flight_status: 'landed',
            battery_level: 85,
            height: 0,
            temperature: 25.5,
            wifi_signal: 90
          },
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.get.mockResolvedValue(mockResponse);

      const result = await client.getDroneStatus('drone_001');
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.get).toHaveBeenCalledWith('/mcp/drones/drone_001/status');
    });
  });

  describe('Drone Control APIs', () => {
    it('should connect drone successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Drone connected successfully',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const result = await client.connectDrone('drone_001');
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/connect');
    });

    it('should takeoff drone successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Drone takeoff successful',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const takeoffCommand = {
        target_height: 100,
        safety_check: true
      };

      const result = await client.takeoff('drone_001', takeoffCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/takeoff', takeoffCommand);
    });

    it('should move drone successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Drone moved successfully',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const moveCommand = {
        direction: 'forward' as const,
        distance: 100,
        speed: 50
      };

      const result = await client.moveDrone('drone_001', moveCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/move', moveCommand);
    });

    it('should rotate drone successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Drone rotated successfully',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const rotateCommand = {
        direction: 'clockwise' as const,
        angle: 90
      };

      const result = await client.rotateDrone('drone_001', rotateCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/rotate', rotateCommand);
    });

    it('should emergency stop drone successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Emergency stop executed',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const result = await client.emergencyStop('drone_001');
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/emergency');
    });

    it('should set altitude successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Altitude set successfully',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const altitudeCommand = {
        target_height: 150,
        mode: 'absolute' as const
      };

      const result = await client.setAltitude('drone_001', altitudeCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/altitude', altitudeCommand);
    });
  });

  describe('Camera APIs', () => {
    it('should take photo successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Photo taken successfully',
          photo: {
            id: 'photo_001',
            filename: 'photo.jpg',
            path: '/photos/photo.jpg',
            size: 1024,
            timestamp: '2023-01-01T00:00:00Z'
          },
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const photoCommand = {
        filename: 'test.jpg',
        quality: 'high' as const
      };

      const result = await client.takePhoto('drone_001', photoCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/camera/photo', photoCommand);
    });

    it('should control streaming successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Streaming started',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const streamingCommand = {
        action: 'start' as const,
        quality: 'high' as const,
        resolution: '720p' as const
      };

      const result = await client.controlStreaming('drone_001', streamingCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/camera/streaming', streamingCommand);
    });

    it('should collect learning data successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Learning data collected',
          dataset: {
            id: 'dataset_001',
            name: 'test_object',
            image_count: 12,
            positions_captured: ['front', 'back', 'left', 'right']
          },
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const learningCommand = {
        object_name: 'test_object',
        capture_positions: ['front', 'back', 'left', 'right'] as const,
        photos_per_position: 3
      };

      const result = await client.collectLearningData('drone_001', learningCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/drones/drone_001/learning/collect', learningCommand);
    });
  });

  describe('Vision APIs', () => {
    it('should detect objects successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Objects detected',
          detections: [
            {
              label: 'person',
              confidence: 0.95,
              bbox: {
                x: 100,
                y: 100,
                width: 50,
                height: 100
              }
            }
          ],
          processing_time: 0.5,
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const detectionCommand = {
        drone_id: 'drone_001',
        model_id: 'yolo_v8',
        confidence_threshold: 0.7
      };

      const result = await client.detectObjects(detectionCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/vision/detection', detectionCommand);
    });

    it('should control tracking successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Tracking started',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.post.mockResolvedValue(mockResponse);

      const trackingCommand = {
        action: 'start' as const,
        drone_id: 'drone_001',
        model_id: 'yolo_v8',
        follow_distance: 200
      };

      const result = await client.controlTracking(trackingCommand);
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.post).toHaveBeenCalledWith('/mcp/vision/tracking', trackingCommand);
    });
  });

  describe('System APIs', () => {
    it('should get system status successfully', async () => {
      const mockResponse = {
        data: {
          mcp_server: {
            status: 'running',
            uptime: 3600,
            version: '1.0.0',
            active_connections: 1
          },
          backend_system: {
            connection_status: 'connected',
            api_endpoint: 'http://backend:8000',
            response_time: 50
          },
          connected_drones: 1,
          active_operations: 0,
          system_health: 'healthy',
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.get.mockResolvedValue(mockResponse);

      const result = await client.getSystemStatus();
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.get).toHaveBeenCalledWith('/mcp/system/status');
    });

    it('should get health check successfully', async () => {
      const mockResponse = {
        data: {
          status: 'healthy',
          checks: [
            {
              name: 'database',
              status: 'pass',
              message: 'Database connection healthy',
              response_time: 10
            }
          ],
          timestamp: '2023-01-01T00:00:00Z'
        }
      };
      
      (client as any).client.get.mockResolvedValue(mockResponse);

      const result = await client.getHealthCheck();
      
      expect(result).toEqual(mockResponse.data);
      expect((client as any).client.get).toHaveBeenCalledWith('/mcp/system/health');
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors correctly', async () => {
      const errorResponse = {
        response: {
          data: {
            error: true,
            error_code: 'DRONE_NOT_FOUND',
            message: 'Drone not found',
            timestamp: '2023-01-01T00:00:00Z'
          }
        }
      };
      
      (client as any).client.get.mockRejectedValue(errorResponse);

      await expect(client.getDroneStatus('invalid_drone')).rejects.toThrow(MCPClientError);
    });
  });
});

describe('MCPClientError', () => {
  it('should create error with correct properties', () => {
    const errorData = {
      error: true,
      error_code: 'DRONE_NOT_FOUND',
      message: 'Drone not found',
      details: {
        suggested_corrections: ['Check drone ID']
      },
      timestamp: '2023-01-01T00:00:00Z'
    };

    const error = new MCPClientError(errorData);

    expect(error.name).toBe('MCPClientError');
    expect(error.message).toBe('Drone not found');
    expect(error.errorCode).toBe('DRONE_NOT_FOUND');
    expect(error.details).toEqual(errorData.details);
    expect(error.timestamp).toBe('2023-01-01T00:00:00Z');
  });
});