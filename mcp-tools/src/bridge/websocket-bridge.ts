import WebSocket from 'ws';
import { EventEmitter } from 'events';
import { ConfigManager } from '../utils/config';
import { Logger } from '../utils/logger';
import type { DroneEventUnion, SensorData, VideoFrameEvent } from '../types/api';

export interface WebSocketBridgeEvents {
  connected: () => void;
  disconnected: (code: number, reason: string) => void;
  error: (error: Error) => void;
  sensorData: (data: SensorData) => void;
  videoFrame: (frame: VideoFrameEvent) => void;
  statusChange: (event: DroneEventUnion) => void;
  message: (event: DroneEventUnion) => void;
}

export declare interface WebSocketBridge {
  on<U extends keyof WebSocketBridgeEvents>(
    event: U,
    listener: WebSocketBridgeEvents[U]
  ): this;
  
  emit<U extends keyof WebSocketBridgeEvents>(
    event: U,
    ...args: Parameters<WebSocketBridgeEvents[U]>
  ): boolean;
}

export class WebSocketBridge extends EventEmitter {
  private ws: WebSocket | null = null;
  private config: ReturnType<ConfigManager['getConfig']>;
  private logger: Logger;
  private reconnectAttempts: number = 0;
  private reconnectTimer: NodeJS.Timer | null = null;
  private pingTimer: NodeJS.Timer | null = null;
  private isConnecting: boolean = false;
  private isDestroyed: boolean = false;

  constructor() {
    super();
    this.config = ConfigManager.getInstance().getConfig();
    this.logger = Logger.getInstance();
  }

  public async connect(): Promise<void> {
    if (this.isDestroyed) {
      throw new Error('WebSocket bridge has been destroyed');
    }

    if (!this.config.websocket.enabled) {
      this.logger.warn('WebSocket is disabled in configuration');
      return;
    }

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.logger.debug('WebSocket already connected');
      return;
    }

    if (this.isConnecting) {
      this.logger.debug('WebSocket connection already in progress');
      return;
    }

    this.isConnecting = true;

    try {
      const wsUrl = this.buildWebSocketUrl();
      this.logger.info(`Connecting to WebSocket: ${wsUrl}`);

      this.ws = new WebSocket(wsUrl, {
        handshakeTimeout: 10000,
        perMessageDeflate: false,
      });

      await this.setupWebSocketHandlers();
      await this.waitForConnection();

      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.startPingInterval();

      this.logger.info('WebSocket connected successfully');
      this.emit('connected');
    } catch (error) {
      this.isConnecting = false;
      this.logger.error('WebSocket connection failed', error as Error);
      this.scheduleReconnect();
      throw error;
    }
  }

  private buildWebSocketUrl(): string {
    const baseUrl = this.config.backend.baseUrl;
    const wsUrl = baseUrl.replace(/^http/, 'ws');
    return `${wsUrl}/ws/mcp-bridge`;
  }

  private setupWebSocketHandlers(): void {
    if (!this.ws) return;

    this.ws.on('open', () => {
      this.logger.logWebSocketEvent('connection_opened');
    });

    this.ws.on('close', (code: number, reason: Buffer) => {
      const reasonStr = reason.toString();
      this.logger.logWebSocketEvent('connection_closed', { code, reason: reasonStr });
      
      this.cleanup();
      this.emit('disconnected', code, reasonStr);
      
      if (!this.isDestroyed && code !== 1000) { // Not a normal closure
        this.scheduleReconnect();
      }
    });

    this.ws.on('error', (error: Error) => {
      this.logger.logWebSocketEvent('error', undefined, error.message);
      this.emit('error', error);
    });

    this.ws.on('message', (data: WebSocket.Data) => {
      try {
        const message = JSON.parse(data.toString()) as DroneEventUnion;
        this.handleMessage(message);
      } catch (error) {
        this.logger.error('Failed to parse WebSocket message', error as Error, {
          data: data.toString(),
        });
      }
    });

    this.ws.on('ping', (data: Buffer) => {
      this.logger.debug('Received ping, sending pong');
      this.ws?.pong(data);
    });

    this.ws.on('pong', () => {
      this.logger.debug('Received pong');
    });
  }

  private async waitForConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.ws) {
        reject(new Error('WebSocket not initialized'));
        return;
      }

      const timeout = setTimeout(() => {
        reject(new Error('WebSocket connection timeout'));
      }, 10000);

      this.ws.once('open', () => {
        clearTimeout(timeout);
        resolve();
      });

      this.ws.once('error', (error) => {
        clearTimeout(timeout);
        reject(error);
      });
    });
  }

  private handleMessage(message: DroneEventUnion): void {
    this.logger.logWebSocketEvent('message_received', {
      type: message.type,
      timestamp: message.timestamp,
    });

    this.emit('message', message);

    switch (message.type) {
      case 'sensor_update':
        this.emit('sensorData', message.data);
        break;
      case 'video_frame':
        this.emit('videoFrame', message);
        break;
      case 'status_change':
        this.emit('statusChange', message);
        break;
      case 'error':
        this.logger.error(`Drone error received via WebSocket: ${message.data.message}`, undefined, {
          code: message.data.code,
          severity: message.data.severity,
        });
        break;
      default:
        this.logger.debug('Unknown message type received', { type: (message as any).type });
    }
  }

  private startPingInterval(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
    }

    this.pingTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.ping();
        this.logger.debug('Sent ping to server');
      }
    }, this.config.websocket.pingInterval);
  }

  private scheduleReconnect(): void {
    if (this.isDestroyed || this.reconnectAttempts >= this.config.websocket.maxReconnectAttempts) {
      this.logger.error('Max reconnection attempts reached or bridge destroyed');
      return;
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    const delay = this.config.websocket.reconnectInterval * Math.pow(2, this.reconnectAttempts);
    this.reconnectAttempts++;

    this.logger.info(`Scheduling WebSocket reconnection attempt ${this.reconnectAttempts}`, {
      delay,
      maxAttempts: this.config.websocket.maxReconnectAttempts,
    });

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch((error) => {
        this.logger.error('Reconnection attempt failed', error);
      });
    }, delay);
  }

  public disconnect(): void {
    this.logger.info('Disconnecting WebSocket');
    
    this.cleanup();
    
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.close(1000, 'Client disconnect');
    }
  }

  private cleanup(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  public send(message: any): boolean {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      this.logger.warn('Cannot send message: WebSocket not connected');
      return false;
    }

    try {
      const data = JSON.stringify(message);
      this.ws.send(data);
      this.logger.logWebSocketEvent('message_sent', { type: message.type });
      return true;
    } catch (error) {
      this.logger.error('Failed to send WebSocket message', error as Error);
      return false;
    }
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  public getConnectionState(): string {
    if (!this.ws) return 'not_initialized';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }

  public getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }

  // Async generator for streaming sensor data
  public async* streamSensorData(): AsyncGenerator<SensorData, void, unknown> {
    if (!this.isConnected()) {
      await this.connect();
    }

    const sensorDataQueue: SensorData[] = [];
    let resolveNext: ((value: IteratorResult<SensorData>) => void) | null = null;

    const handler = (data: SensorData) => {
      if (resolveNext) {
        resolveNext({ value: data, done: false });
        resolveNext = null;
      } else {
        sensorDataQueue.push(data);
      }
    };

    this.on('sensorData', handler);

    try {
      while (true) {
        if (sensorDataQueue.length > 0) {
          yield sensorDataQueue.shift()!;
        } else {
          yield await new Promise<SensorData>((resolve) => {
            resolveNext = (result) => {
              if (!result.done) resolve(result.value);
            };
          });
        }
      }
    } finally {
      this.off('sensorData', handler);
    }
  }

  // Async generator for streaming video frames
  public async* streamVideoFrames(): AsyncGenerator<VideoFrameEvent, void, unknown> {
    if (!this.isConnected()) {
      await this.connect();
    }

    const frameQueue: VideoFrameEvent[] = [];
    let resolveNext: ((value: IteratorResult<VideoFrameEvent>) => void) | null = null;

    const handler = (frame: VideoFrameEvent) => {
      if (resolveNext) {
        resolveNext({ value: frame, done: false });
        resolveNext = null;
      } else {
        // Keep only the latest 5 frames to prevent memory issues
        frameQueue.push(frame);
        if (frameQueue.length > 5) {
          frameQueue.shift();
        }
      }
    };

    this.on('videoFrame', handler);

    try {
      while (true) {
        if (frameQueue.length > 0) {
          yield frameQueue.shift()!;
        } else {
          yield await new Promise<VideoFrameEvent>((resolve) => {
            resolveNext = (result) => {
              if (!result.done) resolve(result.value);
            };
          });
        }
      }
    } finally {
      this.off('videoFrame', handler);
    }
  }

  public destroy(): void {
    this.logger.info('Destroying WebSocket bridge');
    this.isDestroyed = true;
    this.disconnect();
    this.removeAllListeners();
  }
}