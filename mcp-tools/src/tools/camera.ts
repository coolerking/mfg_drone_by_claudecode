import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';

/**
 * Camera operation tools for video streaming and capture
 */
export class CameraTools {
  private client: FastAPIClient;
  private logger;

  constructor(client: FastAPIClient, logger: Logger) {
    this.client = client;
    this.logger = logger.createComponentLogger('CameraTools');
  }

  /**
   * Get all camera tools
   */
  getTools(): Tool[] {
    return [
      this.getCameraStreamStartTool(),
      this.getCameraStreamStopTool(),
      this.getCameraTakePhotoTool(),
      this.getCameraStartRecordingTool(),
      this.getCameraStopRecordingTool(),
      this.getCameraSettingsTool(),
    ];
  }

  /**
   * Tool: Start video streaming
   */
  private getCameraStreamStartTool(): Tool {
    return {
      name: 'camera_stream_start',
      description: 'Start video streaming from the drone camera. This enables real-time video feed from the drone.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Stop video streaming
   */
  private getCameraStreamStopTool(): Tool {
    return {
      name: 'camera_stream_stop',
      description: 'Stop video streaming from the drone camera. This disables the real-time video feed.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Take photo
   */
  private getCameraTakePhotoTool(): Tool {
    return {
      name: 'camera_take_photo',
      description: 'Capture a single photo with the drone camera. The photo will be saved on the drone or backend system.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Start video recording
   */
  private getCameraStartRecordingTool(): Tool {
    return {
      name: 'camera_start_recording',
      description: 'Start recording video to storage. This begins saving the video stream to a file.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Stop video recording
   */
  private getCameraStopRecordingTool(): Tool {
    return {
      name: 'camera_stop_recording',
      description: 'Stop recording video and save the file. This ends the current video recording session.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Configure camera settings
   */
  private getCameraSettingsTool(): Tool {
    return {
      name: 'camera_settings',
      description: 'Configure camera settings including resolution, frame rate, and bitrate for optimal video quality.',
      inputSchema: {
        type: 'object',
        properties: {
          resolution: {
            type: 'string',
            enum: ['high', 'low'],
            description: 'Video resolution setting',
          },
          fps: {
            type: 'string',
            enum: ['high', 'middle', 'low'],
            description: 'Frame rate setting',
          },
          bitrate: {
            type: 'integer',
            minimum: 1,
            maximum: 5,
            description: 'Video bitrate setting (1-5)',
          },
        },
        required: [],
      },
    };
  }

  /**
   * Execute camera tool
   */
  async executeTool(name: string, args: unknown): Promise<unknown> {
    this.logger.info(`Executing camera tool: ${name}`, { args });

    try {
      switch (name) {
        case 'camera_stream_start':
          return await this.executeStreamStart();
        case 'camera_stream_stop':
          return await this.executeStreamStop();
        case 'camera_take_photo':
          return await this.executeTakePhoto();
        case 'camera_start_recording':
          return await this.executeStartRecording();
        case 'camera_stop_recording':
          return await this.executeStopRecording();
        case 'camera_settings':
          return await this.executeSettings(args);
        default:
          throw new Error(`Unknown camera tool: ${name}`);
      }
    } catch (error) {
      this.logger.error(`Camera tool ${name} failed`, error);
      throw error;
    }
  }

  /**
   * Execute start video streaming
   */
  private async executeStreamStart(): Promise<unknown> {
    this.logger.info('Starting video stream...');
    
    // Check if drone is connected
    try {
      const status = await this.client.getStatus();
      if (!status.connected) {
        return {
          success: false,
          message: 'Cannot start video stream: Drone is not connected.',
          error: 'DRONE_NOT_CONNECTED',
        };
      }
    } catch (error) {
      this.logger.warn('Could not check drone status before starting stream', error);
    }

    const result = await this.client.startVideoStream();

    if (result.success) {
      this.logger.info('Video stream started successfully');
      return {
        success: true,
        message: 'Video streaming started successfully. Stream is now available.',
        data: {
          ...result,
          stream_info: {
            status: 'streaming',
            access_url: `${this.client['config']?.backendUrl || 'http://localhost:8000'}/camera/stream`,
          },
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Failed to start video stream',
        data: result,
      };
    }
  }

  /**
   * Execute stop video streaming
   */
  private async executeStreamStop(): Promise<unknown> {
    this.logger.info('Stopping video stream...');

    const result = await this.client.stopVideoStream();

    if (result.success) {
      this.logger.info('Video stream stopped successfully');
      return {
        success: true,
        message: 'Video streaming stopped successfully.',
        data: {
          ...result,
          stream_info: {
            status: 'stopped',
          },
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Failed to stop video stream',
        data: result,
      };
    }
  }

  /**
   * Execute take photo
   */
  private async executeTakePhoto(): Promise<unknown> {
    this.logger.info('Taking photo...');

    const result = await this.client.takePhoto();

    if (result.success) {
      this.logger.info('Photo captured successfully');
      return {
        success: true,
        message: 'Photo captured successfully.',
        data: {
          ...result,
          photo_info: {
            timestamp: new Date().toISOString(),
            status: 'captured',
          },
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Failed to take photo',
        data: result,
      };
    }
  }

  /**
   * Execute start video recording
   */
  private async executeStartRecording(): Promise<unknown> {
    this.logger.info('Starting video recording...');

    const result = await this.client.startVideoRecording();

    if (result.success) {
      this.logger.info('Video recording started successfully');
      return {
        success: true,
        message: 'Video recording started successfully.',
        data: {
          ...result,
          recording_info: {
            status: 'recording',
            started_at: new Date().toISOString(),
          },
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Failed to start video recording',
        data: result,
      };
    }
  }

  /**
   * Execute stop video recording
   */
  private async executeStopRecording(): Promise<unknown> {
    this.logger.info('Stopping video recording...');

    const result = await this.client.stopVideoRecording();

    if (result.success) {
      this.logger.info('Video recording stopped successfully');
      return {
        success: true,
        message: 'Video recording stopped and saved successfully.',
        data: {
          ...result,
          recording_info: {
            status: 'saved',
            stopped_at: new Date().toISOString(),
          },
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Failed to stop video recording',
        data: result,
      };
    }
  }

  /**
   * Execute camera settings update
   */
  private async executeSettings(args: unknown): Promise<unknown> {
    const schema = z.object({
      resolution: z.enum(['high', 'low']).optional(),
      fps: z.enum(['high', 'middle', 'low']).optional(),
      bitrate: z.number().int().min(1).max(5).optional(),
    });

    const params = schema.parse(args);
    this.logger.info('Updating camera settings', params);

    // Validate that at least one setting is provided
    if (!params.resolution && !params.fps && !params.bitrate) {
      return {
        success: false,
        message: 'At least one camera setting parameter is required (resolution, fps, or bitrate).',
        error: 'INVALID_PARAMETER',
      };
    }

    const result = await this.client.setCameraSettings(params);

    if (result.success) {
      this.logger.info('Camera settings updated successfully', params);
      return {
        success: true,
        message: 'Camera settings updated successfully.',
        data: {
          ...result,
          settings: params,
          updated_at: new Date().toISOString(),
        },
      };
    } else {
      return {
        success: false,
        message: result.message || 'Failed to update camera settings',
        data: result,
      };
    }
  }
}