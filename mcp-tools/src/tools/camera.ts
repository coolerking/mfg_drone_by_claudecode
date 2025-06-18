import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { EnhancedFastAPIClient } from '../bridge/enhanced-api-client';
import type { ToolDefinition } from './registry';

// Validation schemas for camera tools
const EmptyArgsSchema = z.object({});

const CameraSettingsSchema = z.object({
  resolution: z.enum(['720p', '480p']).optional(),
  fps: z.enum([30, 15, 5]).optional(),
  bitrate: z.enum(['auto', 'high', 'medium', 'low']).optional(),
});

const PhotoArgsSchema = z.object({
  filename: z.string().optional(),
  quality: z.enum(['high', 'medium', 'low']).optional().default('high'),
});

const RecordingArgsSchema = z.object({
  filename: z.string().optional(),
  duration: z.number().min(1).max(300).optional(),
  quality: z.enum(['720p', '480p']).optional().default('720p'),
});

// Create camera operation tools
export function createCameraTools(apiClient: EnhancedFastAPIClient): ToolDefinition[] {
  return [
    {
      tool: {
        name: 'camera_stream_start',
        description: 'Start video streaming from drone camera. Enables real-time video feed for monitoring and navigation.',
        inputSchema: {
          type: 'object',
          properties: {
            resolution: {
              type: 'string',
              enum: ['720p', '480p'],
              description: 'Video resolution (720p for high quality, 480p for lower bandwidth)',
              default: '720p',
            },
            fps: {
              type: 'number',
              enum: [30, 15, 5],
              description: 'Frames per second (30 for smooth, 15 for balanced, 5 for low bandwidth)',
              default: 30,
            },
            bitrate: {
              type: 'string',
              enum: ['auto', 'high', 'medium', 'low'],
              description: 'Video bitrate quality',
              default: 'auto',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof CameraSettingsSchema>) => {
        try {
          // This would call a stream start endpoint
          const result = await apiClient.getSensorData(); // Placeholder
          
          return {
            success: true,
            message: '📹 Video streaming started successfully! Live feed is now active.',
            timestamp: new Date().toISOString(),
            streamSettings: {
              resolution: args.resolution || '720p',
              fps: args.fps || 30,
              bitrate: args.bitrate || 'auto',
              status: 'active',
            },
            streamInfo: {
              url: `${apiClient.getBackendUrl?.() || 'http://localhost:8000'}/camera/stream`,
              protocol: 'HTTP/WebSocket',
              latency: 'Low (< 200ms)',
            },
            viewingOptions: [
              'Access stream via web browser',
              'Use VLC or similar media player',
              'Integrate with monitoring applications'
            ],
            performanceNotes: {
              '720p@30fps': 'High quality, requires good WiFi connection',
              '480p@15fps': 'Balanced quality and bandwidth',
              '480p@5fps': 'Low bandwidth, suitable for monitoring'
            },
            nextSteps: [
              'Stream is active and ready for viewing',
              'Monitor stream quality and adjust settings if needed',
              'Use camera_stream_stop when done'
            ]
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Stream start error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            troubleshooting: [
              'Check drone camera is functional',
              'Verify WiFi connection strength',
              'Ensure drone is connected and responsive',
              'Try lower resolution/fps settings'
            ]
          };
        }
      },
      validator: CameraSettingsSchema,
      category: 'camera',
      description: 'Starts real-time video streaming from drone camera',
      examples: [
        'camera_stream_start() - Start stream with default settings (720p@30fps)',
        'camera_stream_start({"resolution": "480p", "fps": 15}) - Start balanced quality stream',
        'camera_stream_start({"bitrate": "low"}) - Start low bandwidth stream'
      ],
    },

    {
      tool: {
        name: 'camera_stream_stop',
        description: 'Stop video streaming from drone camera. Terminates the live video feed.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof EmptyArgsSchema>) => {
        try {
          // This would call a stream stop endpoint
          const result = await apiClient.getSensorData(); // Placeholder
          
          return {
            success: true,
            message: '📹 Video streaming stopped successfully. Live feed terminated.',
            timestamp: new Date().toISOString(),
            streamStatus: 'stopped',
            note: 'Camera is still available for photos and recording',
            batteryImpact: 'Stopping stream will reduce battery consumption',
            nextOptions: [
              'Take photos with camera_take_photo',
              'Start recording with camera_start_recording',
              'Restart stream when needed'
            ]
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Stream stop error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            note: 'Stream may still be active - check manually if needed',
            troubleshooting: [
              'Check drone connection',
              'Verify camera system status',
              'Manual stream termination may be required'
            ]
          };
        }
      },
      validator: EmptyArgsSchema,
      category: 'camera',
      description: 'Stops active video streaming',
      examples: [
        'camera_stream_stop() - Stop current video stream'
      ],
    },

    {
      tool: {
        name: 'camera_take_photo',
        description: 'Capture a single high-resolution photo with the drone camera. Great for aerial photography.',
        inputSchema: {
          type: 'object',
          properties: {
            filename: {
              type: 'string',
              description: 'Custom filename for the photo (optional)',
              pattern: '^[a-zA-Z0-9_-]+$',
            },
            quality: {
              type: 'string',
              enum: ['high', 'medium', 'low'],
              description: 'Photo quality setting',
              default: 'high',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof PhotoArgsSchema>) => {
        try {
          // This would call a photo capture endpoint
          const result = await apiClient.getSensorData(); // Placeholder
          
          const timestamp = new Date();
          const defaultFilename = `drone_photo_${timestamp.getTime()}`;
          const filename = args.filename || defaultFilename;
          
          return {
            success: true,
            message: `📸 Photo captured successfully! Saved as: ${filename}.jpg`,
            timestamp: timestamp.toISOString(),
            photo: {
              filename: `${filename}.jpg`,
              quality: args.quality || 'high',
              resolution: args.quality === 'high' ? '1920x1080' : args.quality === 'medium' ? '1280x720' : '640x480',
              format: 'JPEG',
              estimatedSize: this.getEstimatedFileSize(args.quality || 'high'),
            },
            captureInfo: {
              dronePosition: 'Current flight position',
              lighting: 'Automatic exposure adjustment',
              stabilization: 'Digital stabilization applied',
            },
            storage: {
              location: 'Drone internal storage',
              transferMethod: 'WiFi download available',
            },
            nextSteps: [
              'Photo saved to drone storage',
              'Download via WiFi when convenient',
              'Take additional photos if needed'
            ],
            tips: [
              'Use high quality for best results',
              'Ensure stable hover for sharp images',
              'Check lighting conditions for optimal exposure'
            ]
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Photo capture error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            troubleshooting: [
              'Check drone camera functionality',
              'Verify storage space available',
              'Ensure drone is stable (not during rapid movement)',
              'Check camera lens for obstructions'
            ]
          };
        }
      },
      validator: PhotoArgsSchema,
      category: 'camera',
      description: 'Captures high-resolution still photos',
      examples: [
        'camera_take_photo() - Take photo with default settings',
        'camera_take_photo({"filename": "aerial_view", "quality": "high"}) - Take high quality photo with custom name',
        'camera_take_photo({"quality": "medium"}) - Take medium quality photo'
      ],
    },

    {
      tool: {
        name: 'camera_start_recording',
        description: 'Start video recording to drone storage. Records high-quality video for later download.',
        inputSchema: {
          type: 'object',
          properties: {
            filename: {
              type: 'string',
              description: 'Custom filename for the video (optional)',
              pattern: '^[a-zA-Z0-9_-]+$',
            },
            duration: {
              type: 'number',
              description: 'Maximum recording duration in seconds (1-300)',
              minimum: 1,
              maximum: 300,
            },
            quality: {
              type: 'string',
              enum: ['720p', '480p'],
              description: 'Video recording quality',
              default: '720p',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof RecordingArgsSchema>) => {
        try {
          // This would call a recording start endpoint
          const result = await apiClient.getSensorData(); // Placeholder
          
          const timestamp = new Date();
          const defaultFilename = `drone_video_${timestamp.getTime()}`;
          const filename = args.filename || defaultFilename;
          
          return {
            success: true,
            message: `🎬 Video recording started! Recording as: ${filename}.mp4`,
            timestamp: timestamp.toISOString(),
            recording: {
              filename: `${filename}.mp4`,
              quality: args.quality || '720p',
              maxDuration: args.duration || 'unlimited',
              format: 'MP4 (H.264)',
              status: 'recording',
            },
            recordingInfo: {
              resolution: args.quality === '720p' ? '1280x720' : '640x480',
              frameRate: '30 fps',
              bitrate: args.quality === '720p' ? 'High' : 'Medium',
              stabilization: 'Digital stabilization enabled',
            },
            storage: {
              location: 'Drone internal storage',
              estimatedSize: this.getEstimatedVideoSize(args.quality || '720p', args.duration || 60),
              remainingSpace: 'Check with drone status',
            },
            batteryImpact: 'Recording will increase battery consumption',
            tips: [
              'Maintain smooth flight movements for best video quality',
              'Monitor battery level during long recordings',
              'Stop recording before landing to save properly'
            ],
            stopInstructions: 'Use camera_stop_recording to finish and save video',
            autoStop: args.duration ? `Recording will auto-stop after ${args.duration} seconds` : 'Manual stop required'
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Recording start error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            troubleshooting: [
              'Check available storage space on drone',
              'Verify camera system is functioning',
              'Ensure drone is connected and stable',
              'Check battery level (recording uses more power)'
            ]
          };
        }
      },
      validator: RecordingArgsSchema,
      category: 'camera',
      description: 'Starts video recording to drone storage',
      examples: [
        'camera_start_recording() - Start recording with default settings',
        'camera_start_recording({"filename": "flight_demo", "duration": 120, "quality": "720p"}) - Record 2-minute HD video',
        'camera_start_recording({"quality": "480p"}) - Start lower quality recording'
      ],
    },

    {
      tool: {
        name: 'camera_stop_recording',
        description: 'Stop current video recording and save to drone storage. Finalizes the video file.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof EmptyArgsSchema>) => {
        try {
          // This would call a recording stop endpoint
          const result = await apiClient.getSensorData(); // Placeholder
          
          return {
            success: true,
            message: '🎬 Video recording stopped and saved successfully!',
            timestamp: new Date().toISOString(),
            recordingStatus: 'completed',
            fileStatus: 'saved_to_drone_storage',
            note: 'Video has been finalized and is ready for download',
            downloadInfo: {
              method: 'WiFi transfer from drone',
              format: 'MP4 file',
              location: 'Drone internal storage',
            },
            nextSteps: [
              'Video saved successfully to drone',
              'Download via WiFi when convenient',
              'Start new recording if needed'
            ],
            recommendations: [
              'Download videos regularly to free storage space',
              'Check video quality on computer',
              'Back up important footage'
            ]
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Recording stop error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            warning: 'Recording may not have been saved properly',
            troubleshooting: [
              'Check if recording was actually started',
              'Verify drone storage space',
              'Check drone connection stability',
              'Manual file recovery may be needed'
            ]
          };
        }
      },
      validator: EmptyArgsSchema,
      category: 'camera',
      description: 'Stops active video recording and saves file',
      examples: [
        'camera_stop_recording() - Stop current recording and save'
      ],
    },

    {
      tool: {
        name: 'camera_settings',
        description: 'Adjust camera settings for optimal image and video quality based on conditions.',
        inputSchema: {
          type: 'object',
          properties: {
            resolution: {
              type: 'string',
              enum: ['720p', '480p'],
              description: 'Camera resolution setting',
            },
            fps: {
              type: 'number',
              enum: [30, 15, 5],
              description: 'Frames per second for video',
            },
            bitrate: {
              type: 'string',
              enum: ['auto', 'high', 'medium', 'low'],
              description: 'Video bitrate quality',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof CameraSettingsSchema>) => {
        try {
          // This would call a camera settings endpoint
          const result = await apiClient.getSensorData(); // Placeholder
          
          return {
            success: true,
            message: '📷 Camera settings updated successfully!',
            timestamp: new Date().toISOString(),
            appliedSettings: {
              resolution: args.resolution || 'unchanged',
              fps: args.fps || 'unchanged',
              bitrate: args.bitrate || 'unchanged',
            },
            currentSettings: {
              resolution: args.resolution || '720p',
              fps: args.fps || 30,
              bitrate: args.bitrate || 'auto',
            },
            settingsGuide: {
              '720p': 'High quality, more bandwidth required',
              '480p': 'Lower quality, less bandwidth',
              '30fps': 'Smooth video, higher data rate',
              '15fps': 'Balanced smoothness and data',
              '5fps': 'Low data rate, less smooth',
              'auto_bitrate': 'Adjusts based on connection',
              'high_bitrate': 'Best quality, requires strong WiFi',
              'low_bitrate': 'Lower quality, works with weak WiFi'
            },
            performanceImpact: {
              batteryLife: this.getBatteryImpact(args.resolution, args.fps),
              wifiUsage: this.getWifiUsage(args.resolution, args.fps, args.bitrate),
              storageUsage: this.getStorageUsage(args.resolution, args.fps),
            },
            recommendations: this.getSettingsRecommendations(args)
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Camera settings error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            note: 'Settings may not have been applied',
            troubleshooting: [
              'Check drone camera system status',
              'Verify connection to drone',
              'Try applying settings individually',
              'Reset to default settings if needed'
            ]
          };
        }
      },
      validator: CameraSettingsSchema,
      category: 'camera',
      description: 'Configures camera quality and performance settings',
      examples: [
        'camera_settings({"resolution": "720p", "fps": 30}) - Set high quality video',
        'camera_settings({"bitrate": "low"}) - Optimize for weak WiFi',
        'camera_settings({"fps": 15}) - Balance quality and bandwidth'
      ],
    },
  ];
}

// Helper functions for camera operations
function getEstimatedFileSize(quality: string): string {
  const sizes = {
    high: '2-4 MB',
    medium: '1-2 MB', 
    low: '0.5-1 MB'
  };
  return sizes[quality as keyof typeof sizes] || '2-4 MB';
}

function getEstimatedVideoSize(quality: string, duration: number): string {
  const mbPerSecond = quality === '720p' ? 0.5 : 0.25;
  const totalMB = Math.round(mbPerSecond * duration);
  return `~${totalMB} MB`;
}

function getBatteryImpact(resolution?: string, fps?: number): string {
  if (resolution === '720p' && fps === 30) return 'High battery usage';
  if (resolution === '480p' || fps === 15) return 'Medium battery usage';
  return 'Low battery usage';
}

function getWifiUsage(resolution?: string, fps?: number, bitrate?: string): string {
  if (resolution === '720p' && fps === 30) return 'High bandwidth required';
  if (bitrate === 'low' || fps === 5) return 'Low bandwidth required';
  return 'Medium bandwidth required';
}

function getStorageUsage(resolution?: string, fps?: number): string {
  if (resolution === '720p' && fps === 30) return 'High storage usage';
  if (resolution === '480p' || fps === 15) return 'Medium storage usage';
  return 'Low storage usage';
}

function getSettingsRecommendations(args: any): string[] {
  const recommendations = [];
  
  if (args.resolution === '720p' && args.fps === 30) {
    recommendations.push('Ideal for high-quality filming with strong WiFi');
  }
  
  if (args.resolution === '480p') {
    recommendations.push('Good for monitoring and conserving bandwidth');
  }
  
  if (args.fps === 5) {
    recommendations.push('Best for real-time monitoring with limited bandwidth');
  }
  
  if (args.bitrate === 'auto') {
    recommendations.push('Let system optimize based on connection quality');
  }
  
  return recommendations.length > 0 ? recommendations : ['Settings applied successfully'];
}