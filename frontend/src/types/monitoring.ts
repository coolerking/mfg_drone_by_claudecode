// System monitoring and settings types

export interface SystemConfiguration {
  id: string
  name: string
  value: string | number | boolean
  type: 'string' | 'number' | 'boolean' | 'json'
  category: 'system' | 'drone' | 'vision' | 'performance' | 'security'
  description: string
  required: boolean
  default_value: string | number | boolean
  validation_rule?: string
  updated_at: string
  updated_by: string
}

export interface UserPreferences {
  user_id: string
  theme: 'light' | 'dark' | 'auto'
  language: 'ja' | 'en'
  timezone: string
  dashboard_layout: {
    widgets: Array<{
      id: string
      type: string
      position: { x: number; y: number }
      size: { width: number; height: number }
      config: Record<string, any>
    }>
  }
  notification_settings: {
    email_enabled: boolean
    push_enabled: boolean
    sound_enabled: boolean
    severity_filter: ('info' | 'warning' | 'error')[]
  }
  camera_settings: {
    default_resolution: string
    default_fps: number
    auto_record: boolean
    quality_preset: 'low' | 'medium' | 'high' | 'ultra'
  }
  drone_settings: {
    default_flight_height: number
    max_flight_distance: number
    auto_return_battery_level: number
    emergency_action: 'land' | 'return_home' | 'hover'
  }
  table_settings: {
    page_size: number
    auto_refresh_interval: number
    density: 'compact' | 'standard' | 'comfortable'
  }
  created_at: string
  updated_at: string
}

export interface SystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical'
  score: number
  last_check: string
  components: {
    database: HealthComponent
    file_system: HealthComponent
    network: HealthComponent
    services: HealthComponent[]
    hardware: {
      cpu: HealthComponent
      memory: HealthComponent
      disk: HealthComponent
      temperature?: HealthComponent
      gpu?: HealthComponent
    }
  }
  recommendations: HealthRecommendation[]
}

export interface HealthComponent {
  name: string
  status: 'healthy' | 'warning' | 'critical'
  value: number
  unit: string
  threshold_warning: number
  threshold_critical: number
  message: string
  last_check: string
}

export interface HealthRecommendation {
  type: 'performance' | 'maintenance' | 'security' | 'capacity'
  severity: 'low' | 'medium' | 'high'
  title: string
  description: string
  action: string
  impact: string
}

export interface LogEntry {
  id: string
  timestamp: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
  source: string
  category: 'system' | 'drone' | 'vision' | 'api' | 'security' | 'performance'
  message: string
  details?: Record<string, any>
  user_id?: string
  session_id?: string
  request_id?: string
  drone_id?: string
  model_id?: string
  stack_trace?: string
  context: Record<string, any>
}

export interface LogFilter {
  level?: ('debug' | 'info' | 'warning' | 'error' | 'critical')[]
  source?: string[]
  category?: ('system' | 'drone' | 'vision' | 'api' | 'security' | 'performance')[]
  start_time?: string
  end_time?: string
  search_query?: string
  user_id?: string
  drone_id?: string
  limit?: number
  offset?: number
}

export interface AlertRule {
  id: string
  name: string
  description: string
  enabled: boolean
  severity: 'info' | 'warning' | 'error'
  condition: {
    metric: string
    operator: '>' | '<' | '>=' | '<=' | '==' | '!='
    threshold: number
    duration_minutes: number
  }
  actions: {
    notify_users: string[]
    email_enabled: boolean
    webhook_url?: string
    auto_resolve: boolean
  }
  created_at: string
  updated_at: string
  last_triggered?: string
  trigger_count: number
}

export interface MonitoringWidget {
  id: string
  type: 'metric_chart' | 'alert_panel' | 'health_status' | 'activity_feed' | 'drone_map' | 'log_stream'
  title: string
  config: {
    metric?: string
    time_range?: string
    chart_type?: 'line' | 'area' | 'bar' | 'doughnut' | 'gauge'
    refresh_interval?: number
    filters?: Record<string, any>
    display_options?: Record<string, any>
  }
  position: { x: number; y: number }
  size: { width: number; height: number }
  created_at: string
  updated_at: string
}

export interface MetricQuery {
  metric: string
  aggregation: 'avg' | 'sum' | 'min' | 'max' | 'count'
  time_range: '5m' | '15m' | '1h' | '6h' | '24h' | '7d' | '30d'
  interval: '1m' | '5m' | '15m' | '1h' | '1d'
  filters?: Record<string, any>
  group_by?: string[]
}

export interface MetricData {
  metric: string
  values: Array<{
    timestamp: string
    value: number
    labels?: Record<string, string>
  }>
  unit: string
  description: string
}

export interface ExportConfig {
  type: 'logs' | 'metrics' | 'alerts' | 'configuration' | 'full_backup'
  format: 'json' | 'csv' | 'xlsx' | 'pdf'
  filters?: Record<string, any>
  time_range?: {
    start: string
    end: string
  }
  compression: boolean
  include_sensitive_data: boolean
}

export interface ImportConfig {
  type: 'configuration' | 'user_preferences' | 'alert_rules' | 'dashboard_layout'
  merge_strategy: 'overwrite' | 'merge' | 'skip_existing'
  validate_schema: boolean
  backup_existing: boolean
}

export interface BackupInfo {
  id: string
  type: 'manual' | 'scheduled' | 'emergency'
  size_bytes: number
  created_at: string
  description: string
  included_components: string[]
  status: 'completed' | 'in_progress' | 'failed'
  download_url?: string
  expires_at: string
}

export interface MaintenanceTask {
  id: string
  name: string
  description: string
  type: 'cleanup' | 'optimization' | 'backup' | 'health_check' | 'update'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  scheduled_at: string
  started_at?: string
  completed_at?: string
  duration_seconds?: number
  result?: {
    success: boolean
    message: string
    details: Record<string, any>
  }
  next_run?: string
  last_success?: string
}