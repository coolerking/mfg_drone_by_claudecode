import { api } from './apiClient'
import type { SystemStatus, Alert } from '../../types/common'

export interface DashboardStats {
  drones: {
    total: number
    connected: number
    flying: number
    battery_low: number
  }
  datasets: {
    total: number
    images: number
    labeled_images: number
    processing: number
  }
  models: {
    total: number
    training: number
    deployed: number
    average_accuracy: number
  }
  system: {
    uptime: number
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    active_sessions: number
  }
}

export interface PerformanceMetrics {
  timestamp: string
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_in: number
  network_out: number
  temperature?: number
  gpu_usage?: number
  gpu_memory?: number
}

export interface ActivityLog {
  id: string
  timestamp: string
  user_id: string
  user_name: string
  action: string
  resource_type: 'drone' | 'dataset' | 'model' | 'system'
  resource_id?: string
  details: string
  ip_address: string
  user_agent: string
}

export interface DroneActivity {
  drone_id: string
  drone_name: string
  activities: Array<{
    timestamp: string
    event: 'takeoff' | 'landing' | 'move' | 'rotate' | 'emergency' | 'connect' | 'disconnect'
    details: string
    flight_time?: number
    battery_before?: number
    battery_after?: number
  }>
}

export interface SystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical'
  services: Array<{
    name: string
    status: 'running' | 'stopped' | 'error'
    uptime: number
    memory_usage: number
    cpu_usage: number
    last_check: string
  }>
  database: {
    status: 'connected' | 'disconnected'
    response_time_ms: number
    connections: number
    size_mb: number
  }
  storage: {
    total_gb: number
    used_gb: number
    available_gb: number
    usage_percent: number
  }
}

export class DashboardApiService {
  private basePath = '/dashboard'

  // Overview statistics
  async getDashboardStats(): Promise<DashboardStats> {
    return api.get<DashboardStats>(`${this.basePath}/stats`)
  }

  async getSystemStatus(): Promise<SystemStatus> {
    return api.get<SystemStatus>(`${this.basePath}/system-status`)
  }

  async getSystemHealth(): Promise<SystemHealth> {
    return api.get<SystemHealth>(`${this.basePath}/health`)
  }

  // Performance metrics
  async getPerformanceMetrics(
    timeRange: '1h' | '6h' | '24h' | '7d' | '30d' = '24h',
    interval: '1m' | '5m' | '15m' | '1h' | '1d' = '5m'
  ): Promise<PerformanceMetrics[]> {
    return api.get<PerformanceMetrics[]>(`${this.basePath}/metrics`, {
      params: { time_range: timeRange, interval }
    })
  }

  async getCurrentMetrics(): Promise<PerformanceMetrics> {
    return api.get<PerformanceMetrics>(`${this.basePath}/metrics/current`)
  }

  // Activity logs
  async getActivityLogs(
    page = 1,
    limit = 50,
    filter?: {
      user_id?: string
      resource_type?: string
      start_date?: string
      end_date?: string
    }
  ): Promise<{
    logs: ActivityLog[]
    total: number
    page: number
    limit: number
    total_pages: number
  }> {
    return api.get(`${this.basePath}/activity`, {
      params: { page, limit, ...filter }
    })
  }

  async getDroneActivity(
    droneId: string,
    timeRange: '1h' | '6h' | '24h' | '7d' = '24h'
  ): Promise<DroneActivity> {
    return api.get<DroneActivity>(`${this.basePath}/drones/${droneId}/activity`, {
      params: { time_range: timeRange }
    })
  }

  async getAllDroneActivities(
    timeRange: '1h' | '6h' | '24h' | '7d' = '24h'
  ): Promise<DroneActivity[]> {
    return api.get<DroneActivity[]>(`${this.basePath}/drones/activities`, {
      params: { time_range: timeRange }
    })
  }

  // Alerts and notifications
  async getAlerts(
    page = 1,
    limit = 20,
    severity?: 'info' | 'warning' | 'error',
    dismissed?: boolean
  ): Promise<{
    alerts: Alert[]
    total: number
    page: number
    limit: number
    total_pages: number
  }> {
    return api.get(`${this.basePath}/alerts`, {
      params: { page, limit, severity, dismissed }
    })
  }

  async dismissAlert(alertId: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/alerts/${alertId}/dismiss`)
  }

  async dismissAllAlerts(): Promise<{ success: boolean; dismissed_count: number }> {
    return api.post(`${this.basePath}/alerts/dismiss-all`)
  }

  async createAlert(alert: Omit<Alert, 'id' | 'timestamp' | 'dismissed'>): Promise<Alert> {
    return api.post<Alert>(`${this.basePath}/alerts`, alert)
  }

  // Training overview
  async getTrainingOverview(): Promise<{
    active_jobs: number
    queued_jobs: number
    completed_today: number
    failed_today: number
    total_training_time_hours: number
    average_accuracy: number
    recent_jobs: Array<{
      job_id: string
      model_name: string
      progress: number
      status: string
      started_at: string
    }>
  }> {
    return api.get(`${this.basePath}/training`)
  }

  // Resource usage analytics
  async getResourceUsage(
    timeRange: '1h' | '6h' | '24h' | '7d' | '30d' = '24h'
  ): Promise<{
    cpu: { average: number; peak: number }
    memory: { average: number; peak: number }
    disk: { used_gb: number; total_gb: number; growth_rate_gb_per_day: number }
    network: { total_in_gb: number; total_out_gb: number }
    gpu?: { average: number; peak: number }
  }> {
    return api.get(`${this.basePath}/resources`, {
      params: { time_range: timeRange }
    })
  }

  // Fleet statistics
  async getFleetStatistics(): Promise<{
    total_flight_time_hours: number
    total_distance_km: number
    average_battery_life: number
    successful_missions: number
    failed_missions: number
    maintenance_required: number
    fleet_utilization_percent: number
    popular_flight_areas: Array<{
      area: string
      flight_count: number
      total_time_hours: number
    }>
  }> {
    return api.get(`${this.basePath}/fleet`)
  }

  // Model performance analytics
  async getModelPerformance(): Promise<{
    total_predictions: number
    average_inference_time_ms: number
    accuracy_distribution: { [range: string]: number }
    popular_classes: Array<{
      class_name: string
      detection_count: number
      average_confidence: number
    }>
    model_usage: Array<{
      model_id: string
      model_name: string
      prediction_count: number
      last_used: string
    }>
  }> {
    return api.get(`${this.basePath}/models`)
  }

  // Data insights
  async getDataInsights(): Promise<{
    dataset_growth: Array<{
      date: string
      images_added: number
      cumulative_images: number
    }>
    labeling_progress: Array<{
      dataset_id: string
      dataset_name: string
      total_images: number
      labeled_images: number
      progress_percent: number
    }>
    class_distribution: { [className: string]: number }
    annotation_quality: {
      verified_labels: number
      unverified_labels: number
      quality_score: number
    }
  }> {
    return api.get(`${this.basePath}/data`)
  }

  // Export dashboard data
  async exportDashboardData(
    type: 'stats' | 'metrics' | 'logs' | 'alerts',
    format: 'json' | 'csv' = 'json',
    timeRange?: string
  ): Promise<{ download_url: string }> {
    return api.post(`${this.basePath}/export`, {
      type,
      format,
      time_range: timeRange
    })
  }

  // Cleanup and maintenance
  async cleanupOldLogs(daysToKeep = 30): Promise<{ deleted_count: number }> {
    return api.post(`${this.basePath}/cleanup/logs`, { days_to_keep: daysToKeep })
  }

  async cleanupOldMetrics(daysToKeep = 90): Promise<{ deleted_count: number }> {
    return api.post(`${this.basePath}/cleanup/metrics`, { days_to_keep: daysToKeep })
  }

  async optimizeDatabase(): Promise<{ success: boolean; time_taken_ms: number }> {
    return api.post(`${this.basePath}/maintenance/optimize-db`)
  }
}

// Export singleton instance
export const dashboardApi = new DashboardApiService()