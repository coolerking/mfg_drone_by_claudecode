/**
 * Frontend Monitoring and Analytics System
 * Provides comprehensive monitoring for performance, errors, and user behavior
 */

// Core Web Vitals and Performance Monitoring
interface PerformanceMetrics {
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
}

interface ErrorMetadata {
  userAgent: string;
  url: string;
  timestamp: string;
  userId?: string;
  sessionId: string;
  buildVersion?: string;
}

interface UserAction {
  action: string;
  category: string;
  label?: string;
  value?: number;
  timestamp: string;
  sessionId: string;
}

class FrontendMonitoring {
  private sessionId: string;
  private buildVersion: string;
  private isEnabled: boolean;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.buildVersion = __APP_VERSION__ || '1.0.0';
    this.isEnabled = __PROD__ || false;
    
    if (this.isEnabled) {
      this.initializeMonitoring();
    }
  }

  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private initializeMonitoring(): void {
    // Initialize Core Web Vitals monitoring
    this.observeWebVitals();
    
    // Initialize error tracking
    this.initializeErrorTracking();
    
    // Initialize performance observer
    this.initializePerformanceObserver();
    
    // Initialize user behavior tracking
    this.initializeUserTracking();

    // Initialize offline/online status tracking
    this.initializeConnectionTracking();
  }

  private observeWebVitals(): void {
    // Observe Largest Contentful Paint
    this.observeLCP();
    
    // Observe First Input Delay
    this.observeFID();
    
    // Observe Cumulative Layout Shift
    this.observeCLS();
    
    // Observe First Contentful Paint
    this.observeFCP();
  }

  private observeLCP(): void {
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        this.reportMetric('lcp', entry.startTime, {
          element: (entry as any).element?.tagName || 'unknown',
          url: entry.name || window.location.href
        });
      }
    }).observe({ entryTypes: ['largest-contentful-paint'] });
  }

  private observeFID(): void {
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        this.reportMetric('fid', (entry as any).processingStart - entry.startTime, {
          eventType: (entry as any).name,
          target: (entry as any).target?.tagName || 'unknown'
        });
      }
    }).observe({ entryTypes: ['first-input'] });
  }

  private observeCLS(): void {
    let clsValue = 0;
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
        }
      }
      this.reportMetric('cls', clsValue);
    }).observe({ entryTypes: ['layout-shift'] });
  }

  private observeFCP(): void {
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          this.reportMetric('fcp', entry.startTime);
        }
      }
    }).observe({ entryTypes: ['paint'] });
  }

  private initializeErrorTracking(): void {
    // Global error handler
    window.addEventListener('error', (event) => {
      this.reportError(event.error, {
        type: 'javascript',
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.reportError(new Error(event.reason), {
        type: 'promise',
        reason: event.reason,
      });
    });

    // React error boundary support
    const originalConsoleError = console.error;
    console.error = (...args) => {
      if (args[0]?.includes?.('React') || args[0]?.includes?.('react')) {
        this.reportError(new Error(args.join(' ')), {
          type: 'react',
          arguments: args,
        });
      }
      originalConsoleError.apply(console, args);
    };
  }

  private initializePerformanceObserver(): void {
    // Navigation timing
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        
        this.reportMetric('ttfb', navigation.responseStart - navigation.requestStart);
        this.reportMetric('domContentLoaded', navigation.domContentLoadedEventEnd - navigation.navigationStart);
        this.reportMetric('loadComplete', navigation.loadEventEnd - navigation.navigationStart);
      }, 0);
    });

    // Resource timing
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        const resource = entry as PerformanceResourceTiming;
        
        if (resource.duration > 1000) { // Report slow resources (>1s)
          this.reportMetric('slowResource', resource.duration, {
            name: resource.name,
            type: resource.initiatorType,
            size: resource.transferSize,
          });
        }
      }
    }).observe({ entryTypes: ['resource'] });
  }

  private initializeUserTracking(): void {
    // Track page views
    this.trackPageView();

    // Track route changes (for SPA)
    let currentPath = window.location.pathname;
    const observer = new MutationObserver(() => {
      if (window.location.pathname !== currentPath) {
        currentPath = window.location.pathname;
        this.trackPageView();
      }
    });
    observer.observe(document, { subtree: true, childList: true });

    // Track user interactions
    ['click', 'scroll', 'resize'].forEach(eventType => {
      window.addEventListener(eventType, this.throttle((event) => {
        this.trackUserAction({
          action: eventType,
          category: 'interaction',
          label: (event.target as HTMLElement)?.tagName || 'window',
          timestamp: new Date().toISOString(),
          sessionId: this.sessionId,
        });
      }, 1000));
    });
  }

  private initializeConnectionTracking(): void {
    // Track online/offline status
    window.addEventListener('online', () => {
      this.trackUserAction({
        action: 'connectionRestored',
        category: 'connection',
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId,
      });
    });

    window.addEventListener('offline', () => {
      this.trackUserAction({
        action: 'connectionLost',
        category: 'connection',
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId,
      });
    });

    // Track connection quality
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      this.reportMetric('connectionType', 0, {
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
      });
    }
  }

  private throttle<T extends (...args: any[]) => any>(
    func: T, 
    delay: number
  ): (...args: Parameters<T>) => void {
    let timeoutId: NodeJS.Timeout;
    let lastExecTime = 0;
    
    return (...args: Parameters<T>) => {
      const currentTime = Date.now();
      
      if (currentTime - lastExecTime > delay) {
        func(...args);
        lastExecTime = currentTime;
      } else {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          func(...args);
          lastExecTime = Date.now();
        }, delay);
      }
    };
  }

  // Public API methods
  public reportError(error: Error, metadata: Record<string, any> = {}): void {
    if (!this.isEnabled) return;

    const errorData = {
      message: error.message,
      stack: error.stack,
      name: error.name,
      metadata: {
        ...metadata,
        ...this.getErrorMetadata(),
      },
    };

    // Send to backend monitoring endpoint
    this.sendToBackend('/api/monitoring/errors', errorData);
    
    // Also log to console in development
    if (!__PROD__) {
      console.error('Frontend Error:', errorData);
    }
  }

  public reportMetric(name: string, value: number, labels: Record<string, any> = {}): void {
    if (!this.isEnabled) return;

    const metricData = {
      name,
      value,
      labels: {
        ...labels,
        sessionId: this.sessionId,
        buildVersion: this.buildVersion,
        userAgent: navigator.userAgent,
        url: window.location.href,
      },
      timestamp: new Date().toISOString(),
    };

    this.sendToBackend('/api/monitoring/metrics', metricData);
  }

  public trackPageView(): void {
    if (!this.isEnabled) return;

    const pageData = {
      path: window.location.pathname,
      search: window.location.search,
      referrer: document.referrer,
      title: document.title,
      sessionId: this.sessionId,
      timestamp: new Date().toISOString(),
    };

    this.sendToBackend('/api/monitoring/pageviews', pageData);
  }

  public trackUserAction(action: UserAction): void {
    if (!this.isEnabled) return;

    this.sendToBackend('/api/monitoring/actions', action);
  }

  public trackDroneOperation(operation: string, droneId: string, success: boolean, duration?: number): void {
    this.trackUserAction({
      action: operation,
      category: 'drone',
      label: droneId,
      value: duration,
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
    });

    this.reportMetric('droneOperation', success ? 1 : 0, {
      operation,
      droneId,
      duration,
    });
  }

  public trackModelOperation(operation: string, modelId: string, success: boolean): void {
    this.trackUserAction({
      action: operation,
      category: 'model',
      label: modelId,
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
    });

    this.reportMetric('modelOperation', success ? 1 : 0, {
      operation,
      modelId,
    });
  }

  private getErrorMetadata(): ErrorMetadata {
    return {
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
      buildVersion: this.buildVersion,
    };
  }

  private async sendToBackend(endpoint: string, data: any): Promise<void> {
    try {
      // Use sendBeacon for reliability, fallback to fetch
      if (navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        navigator.sendBeacon(endpoint, blob);
      } else {
        await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
          keepalive: true,
        });
      }
    } catch (error) {
      // Silently fail to avoid monitoring errors causing app errors
      if (!__PROD__) {
        console.warn('Failed to send monitoring data:', error);
      }
    }
  }

  // Cleanup method
  public destroy(): void {
    // Remove event listeners and cleanup resources
    // Implementation depends on specific cleanup needs
  }
}

// Singleton instance
export const monitoring = new FrontendMonitoring();

// Export utilities for React components
export const useMonitoring = () => {
  return {
    reportError: monitoring.reportError.bind(monitoring),
    reportMetric: monitoring.reportMetric.bind(monitoring),
    trackUserAction: monitoring.trackUserAction.bind(monitoring),
    trackDroneOperation: monitoring.trackDroneOperation.bind(monitoring),
    trackModelOperation: monitoring.trackModelOperation.bind(monitoring),
  };
};

export default monitoring;