// System monitoring and management components
export { default as SystemMetrics } from './SystemMetrics'
export { default as AlertPanel } from './AlertPanel'
export { default as LogViewer } from './LogViewer'
export { default as SystemSettings } from './SystemSettings'
export { default as UserPreferences } from './UserPreferences'
export { default as MonitoringDashboard } from './MonitoringDashboard'

// Performance monitoring components
export { default as WebVitalsMonitor } from './WebVitalsMonitor'
export { default as RealTimePerformanceDashboard } from './RealTimePerformanceDashboard'
export { 
  default as withPerformanceMonitor,
  usePerformanceTracking,
  PerformanceDebugger
} from './PerformanceMonitorHOC'

// Error tracking and analysis components
export { default as ErrorAnalyticsDashboard } from './ErrorAnalyticsDashboard'
export { default as AdvancedLogAnalyzer } from './AdvancedLogAnalyzer'

// System health monitoring components
export { default as SystemHealthDashboard } from './SystemHealthDashboard'

// Re-export types
export type {
  SystemConfiguration,
  UserPreferences as UserPreferencesType,
  SystemHealth,
  HealthComponent,
  HealthRecommendation,
  LogEntry,
  LogFilter,
  AlertRule,
  MonitoringWidget,
  MetricQuery,
  MetricData,
  ExportConfig,
  ImportConfig,
  BackupInfo,
  MaintenanceTask
} from '../../types/monitoring'