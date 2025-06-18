import { EventEmitter } from 'events';
import { ConfigManager } from '../utils/config';
import { Logger } from '../utils/logger';
import type { PerformanceMetrics } from '../types/config';

export interface SystemMetrics {
  timestamp: Date;
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  cpu: {
    usage: number;
  };
  uptime: number;
}

export interface APIMetrics {
  endpoint: string;
  method: string;
  responseTime: number;
  statusCode: number;
  success: boolean;
  timestamp: Date;
}

export interface WebSocketMetrics {
  messagesReceived: number;
  messagesSent: number;
  connectionUptime: number;
  reconnections: number;
  latency: number;
  timestamp: Date;
}

export interface MetricsSnapshot {
  system: SystemMetrics;
  api: {
    totalRequests: number;
    averageResponseTime: number;
    errorRate: number;
    slowRequests: number;
    endpoints: Record<string, {
      count: number;
      averageTime: number;
      errorCount: number;
      lastRequest: Date;
    }>;
  };
  websocket: WebSocketMetrics;
  performance: {
    toolExecutions: number;
    averageToolTime: number;
    failedTools: number;
    toolsOverTarget: number;
  };
}

export class MetricsCollector extends EventEmitter {
  private config: ReturnType<ConfigManager['getConfig']>;
  private logger: Logger;
  private startTime: Date;
  private metricsInterval: NodeJS.Timer | null = null;
  
  // Metrics storage
  private apiMetrics: APIMetrics[] = [];
  private performanceMetrics: PerformanceMetrics[] = [];
  private wsMetrics: WebSocketMetrics | null = null;
  
  // Counters
  private wsMessagesReceived: number = 0;
  private wsMessagesSent: number = 0;
  private wsReconnections: number = 0;
  private wsConnectionStartTime: Date | null = null;

  constructor() {
    super();
    this.config = ConfigManager.getInstance().getConfig();
    this.logger = Logger.getInstance();
    this.startTime = new Date();
    
    if (this.config.performance.enableMetrics) {
      this.startMetricsCollection();
    }
  }

  private startMetricsCollection(): void {
    this.metricsInterval = setInterval(() => {
      this.collectAndEmitMetrics();
    }, this.config.performance.metricsInterval);

    this.logger.info('Metrics collection started', {
      interval: this.config.performance.metricsInterval,
    });
  }

  private async collectAndEmitMetrics(): Promise<void> {
    try {
      const snapshot = await this.getMetricsSnapshot();
      this.emit('metrics', snapshot);
      
      // Log performance warnings
      if (snapshot.api.averageResponseTime > this.config.performance.targetResponseTime) {
        this.logger.warn('API performance degraded', {
          current: snapshot.api.averageResponseTime,
          target: this.config.performance.targetResponseTime,
        });
      }

      if (snapshot.api.errorRate > 0.1) { // 10% error rate
        this.logger.warn('High API error rate detected', {
          errorRate: snapshot.api.errorRate,
          totalRequests: snapshot.api.totalRequests,
        });
      }

      if (snapshot.system.memory.percentage > 80) {
        this.logger.warn('High memory usage detected', {
          usage: snapshot.system.memory.percentage,
        });
      }

    } catch (error) {
      this.logger.error('Failed to collect metrics', error as Error);
    }
  }

  public recordAPICall(
    endpoint: string,
    method: string,
    responseTime: number,
    statusCode: number,
    success: boolean
  ): void {
    const metric: APIMetrics = {
      endpoint,
      method,
      responseTime,
      statusCode,
      success,
      timestamp: new Date(),
    };

    this.apiMetrics.push(metric);
    
    // Keep only last 1000 metrics to prevent memory issues
    if (this.apiMetrics.length > 1000) {
      this.apiMetrics = this.apiMetrics.slice(-1000);
    }

    // Log slow requests immediately
    if (responseTime > this.config.performance.targetResponseTime) {
      this.logger.warn('Slow API request detected', {
        endpoint,
        method,
        responseTime,
        target: this.config.performance.targetResponseTime,
      });
    }
  }

  public recordToolExecution(
    toolName: string,
    duration: number,
    success: boolean,
    error?: string
  ): void {
    const metric: PerformanceMetrics = {
      timestamp: new Date(),
      toolName,
      duration,
      success,
      error,
    };

    this.performanceMetrics.push(metric);
    
    // Keep only last 500 tool executions
    if (this.performanceMetrics.length > 500) {
      this.performanceMetrics = this.performanceMetrics.slice(-500);
    }

    this.logger.logPerformanceMetrics(metric);
  }

  public recordWebSocketMessage(type: 'sent' | 'received'): void {
    if (type === 'sent') {
      this.wsMessagesSent++;
    } else {
      this.wsMessagesReceived++;
    }
  }

  public recordWebSocketConnection(): void {
    this.wsConnectionStartTime = new Date();
  }

  public recordWebSocketReconnection(): void {
    this.wsReconnections++;
  }

  public recordWebSocketDisconnection(): void {
    this.wsConnectionStartTime = null;
  }

  private getSystemMetrics(): SystemMetrics {
    const memUsage = process.memoryUsage();
    const uptime = process.uptime();

    return {
      timestamp: new Date(),
      memory: {
        used: memUsage.heapUsed,
        total: memUsage.heapTotal,
        percentage: (memUsage.heapUsed / memUsage.heapTotal) * 100,
      },
      cpu: {
        usage: process.cpuUsage().user / 1000000, // Convert to seconds
      },
      uptime,
    };
  }

  private getAPIMetricsAggregated() {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    
    // Filter metrics from last hour
    const recentMetrics = this.apiMetrics.filter(m => m.timestamp >= oneHourAgo);
    
    if (recentMetrics.length === 0) {
      return {
        totalRequests: 0,
        averageResponseTime: 0,
        errorRate: 0,
        slowRequests: 0,
        endpoints: {},
      };
    }

    const totalRequests = recentMetrics.length;
    const successfulRequests = recentMetrics.filter(m => m.success).length;
    const averageResponseTime = recentMetrics.reduce((sum, m) => sum + m.responseTime, 0) / totalRequests;
    const errorRate = (totalRequests - successfulRequests) / totalRequests;
    const slowRequests = recentMetrics.filter(m => m.responseTime > this.config.performance.targetResponseTime).length;

    // Group by endpoint
    const endpoints: Record<string, any> = {};
    recentMetrics.forEach(metric => {
      const key = `${metric.method} ${metric.endpoint}`;
      if (!endpoints[key]) {
        endpoints[key] = {
          count: 0,
          totalTime: 0,
          errorCount: 0,
          lastRequest: metric.timestamp,
        };
      }

      endpoints[key].count++;
      endpoints[key].totalTime += metric.responseTime;
      if (!metric.success) {
        endpoints[key].errorCount++;
      }
      if (metric.timestamp > endpoints[key].lastRequest) {
        endpoints[key].lastRequest = metric.timestamp;
      }
    });

    // Calculate averages
    Object.keys(endpoints).forEach(key => {
      endpoints[key].averageTime = endpoints[key].totalTime / endpoints[key].count;
      delete endpoints[key].totalTime;
    });

    return {
      totalRequests,
      averageResponseTime,
      errorRate,
      slowRequests,
      endpoints,
    };
  }

  private getWebSocketMetrics(): WebSocketMetrics {
    const connectionUptime = this.wsConnectionStartTime 
      ? (Date.now() - this.wsConnectionStartTime.getTime()) / 1000 
      : 0;

    return {
      messagesReceived: this.wsMessagesReceived,
      messagesSent: this.wsMessagesSent,
      connectionUptime,
      reconnections: this.wsReconnections,
      latency: 0, // Would need to implement ping/pong timing
      timestamp: new Date(),
    };
  }

  private getPerformanceMetricsAggregated() {
    const recentMetrics = this.performanceMetrics.filter(
      m => m.timestamp >= new Date(Date.now() - 60 * 60 * 1000) // Last hour
    );

    if (recentMetrics.length === 0) {
      return {
        toolExecutions: 0,
        averageToolTime: 0,
        failedTools: 0,
        toolsOverTarget: 0,
      };
    }

    const toolExecutions = recentMetrics.length;
    const averageToolTime = recentMetrics.reduce((sum, m) => sum + m.duration, 0) / toolExecutions;
    const failedTools = recentMetrics.filter(m => !m.success).length;
    const toolsOverTarget = recentMetrics.filter(m => m.duration > this.config.performance.targetResponseTime).length;

    return {
      toolExecutions,
      averageToolTime,
      failedTools,
      toolsOverTarget,
    };
  }

  public async getMetricsSnapshot(): Promise<MetricsSnapshot> {
    return {
      system: this.getSystemMetrics(),
      api: this.getAPIMetricsAggregated(),
      websocket: this.getWebSocketMetrics(),
      performance: this.getPerformanceMetricsAggregated(),
    };
  }

  public getDetailedToolMetrics(): Record<string, {
    count: number;
    averageTime: number;
    successRate: number;
    lastExecution: Date;
  }> {
    const toolStats: Record<string, any> = {};

    this.performanceMetrics.forEach(metric => {
      if (!toolStats[metric.toolName]) {
        toolStats[metric.toolName] = {
          count: 0,
          totalTime: 0,
          successCount: 0,
          lastExecution: metric.timestamp,
        };
      }

      const stats = toolStats[metric.toolName];
      stats.count++;
      stats.totalTime += metric.duration;
      if (metric.success) {
        stats.successCount++;
      }
      if (metric.timestamp > stats.lastExecution) {
        stats.lastExecution = metric.timestamp;
      }
    });

    // Calculate averages and rates
    Object.keys(toolStats).forEach(toolName => {
      const stats = toolStats[toolName];
      stats.averageTime = stats.totalTime / stats.count;
      stats.successRate = stats.successCount / stats.count;
      delete stats.totalTime;
      delete stats.successCount;
    });

    return toolStats;
  }

  public resetMetrics(): void {
    this.apiMetrics = [];
    this.performanceMetrics = [];
    this.wsMessagesReceived = 0;
    this.wsMessagesSent = 0;
    this.wsReconnections = 0;
    this.wsConnectionStartTime = null;
    this.startTime = new Date();

    this.logger.info('Metrics reset');
  }

  public getUptime(): number {
    return (Date.now() - this.startTime.getTime()) / 1000;
  }

  public stop(): void {
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval);
      this.metricsInterval = null;
    }
    this.logger.info('Metrics collection stopped');
  }

  public destroy(): void {
    this.stop();
    this.removeAllListeners();
  }
}