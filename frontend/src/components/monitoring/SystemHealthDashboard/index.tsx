/**
 * 統合システムヘルスダッシュボード
 * 全システムコンポーネントの健康状態を統合監視・可視化
 */

import React, { useState, useEffect, useMemo } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tab,
  Tabs,
  Alert,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  BugReport as BugReportIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Download as DownloadIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend
} from 'recharts'

// =============================================================================
// 型定義
// =============================================================================

interface SystemComponent {
  id: string
  name: string
  type: 'service' | 'database' | 'cache' | 'queue' | 'external'
  status: 'healthy' | 'warning' | 'critical' | 'unknown'
  uptime: number
  lastCheck: string
  metrics: {
    cpu?: number
    memory?: number
    disk?: number
    connections?: number
    responseTime?: number
    errorRate?: number
  }
  dependencies: string[]
  alerts: SystemAlert[]
}

interface SystemAlert {
  id: string
  level: 'info' | 'warning' | 'error' | 'critical'
  message: string
  timestamp: string
  component: string
  resolved: boolean
}

interface HealthMetric {
  timestamp: string
  overall: number
  frontend: number
  backend: number
  database: number
  network: number
}

interface PerformanceMetric {
  timestamp: string
  responseTime: number
  throughput: number
  errorRate: number
  activeUsers: number
}

// =============================================================================
// サンプルデータ生成
// =============================================================================

const generateHealthData = (hours: number = 24): HealthMetric[] => {
  return Array.from({ length: hours }, (_, i) => {
    const timestamp = new Date(Date.now() - (hours - i) * 60 * 60 * 1000).toISOString()
    const baseHealth = 85 + Math.random() * 15
    
    return {
      timestamp,
      overall: Math.min(100, baseHealth + Math.random() * 10),
      frontend: Math.min(100, baseHealth + Math.random() * 15),
      backend: Math.min(100, baseHealth + Math.random() * 10),
      database: Math.min(100, baseHealth + Math.random() * 8),
      network: Math.min(100, baseHealth + Math.random() * 12)
    }
  })
}

const generatePerformanceData = (hours: number = 24): PerformanceMetric[] => {
  return Array.from({ length: hours }, (_, i) => {
    const timestamp = new Date(Date.now() - (hours - i) * 60 * 60 * 1000).toISOString()
    const baseResponseTime = 200 + Math.random() * 300
    
    return {
      timestamp,
      responseTime: baseResponseTime,
      throughput: 50 + Math.random() * 100,
      errorRate: Math.random() * 5,
      activeUsers: 100 + Math.random() * 500
    }
  })
}

const generateSystemComponents = (): SystemComponent[] => {
  const components: Partial<SystemComponent>[] = [
    {
      id: 'frontend-app',
      name: 'フロントエンドアプリケーション',
      type: 'service',
      status: 'healthy',
      uptime: 99.8,
      metrics: { cpu: 15, memory: 45, responseTime: 150, errorRate: 0.1 }
    },
    {
      id: 'api-server',
      name: 'APIサーバー',
      type: 'service',
      status: 'healthy',
      uptime: 99.9,
      metrics: { cpu: 35, memory: 60, responseTime: 80, errorRate: 0.2, connections: 245 }
    },
    {
      id: 'database',
      name: 'PostgreSQL データベース',
      type: 'database',
      status: 'warning',
      uptime: 99.5,
      metrics: { cpu: 55, memory: 75, disk: 68, connections: 45, responseTime: 25 }
    },
    {
      id: 'redis-cache',
      name: 'Redis キャッシュ',
      type: 'cache',
      status: 'healthy',
      uptime: 99.9,
      metrics: { cpu: 8, memory: 25, connections: 120, responseTime: 5 }
    },
    {
      id: 'message-queue',
      name: 'メッセージキュー',
      type: 'queue',
      status: 'healthy',
      uptime: 99.7,
      metrics: { cpu: 12, memory: 30, connections: 15 }
    },
    {
      id: 'drone-service',
      name: 'ドローン制御サービス',
      type: 'service',
      status: 'critical',
      uptime: 95.2,
      metrics: { cpu: 85, memory: 90, responseTime: 500, errorRate: 5.2 }
    },
    {
      id: 'vision-ai',
      name: 'ビジョンAIサービス',
      type: 'service',
      status: 'warning',
      uptime: 98.1,
      metrics: { cpu: 78, memory: 85, responseTime: 1200, errorRate: 2.1 }
    },
    {
      id: 'file-storage',
      name: 'ファイルストレージ',
      type: 'external',
      status: 'healthy',
      uptime: 99.9,
      metrics: { disk: 45, responseTime: 120 }
    }
  ]

  return components.map((comp, index) => ({
    ...comp,
    lastCheck: new Date(Date.now() - Math.random() * 300000).toISOString(),
    dependencies: index > 0 ? [components[Math.floor(Math.random() * index)]?.id || ''] : [],
    alerts: generateAlertsForComponent(comp.id!, comp.status!)
  })) as SystemComponent[]
}

const generateAlertsForComponent = (componentId: string, status: string): SystemAlert[] => {
  const alertCount = status === 'critical' ? 3 : status === 'warning' ? 1 : 0
  
  return Array.from({ length: alertCount }, (_, i) => ({
    id: `alert-${componentId}-${i}`,
    level: status === 'critical' ? 'error' : 'warning',
    message: status === 'critical' 
      ? `${componentId} で重大なエラーが発生しています`
      : `${componentId} でパフォーマンスの問題が検出されました`,
    timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
    component: componentId,
    resolved: false
  })) as SystemAlert[]
}

// =============================================================================
// ステータス判定ユーティリティ
// =============================================================================

const getStatusColor = (status: string) => {
  switch (status) {
    case 'healthy': return '#4caf50'
    case 'warning': return '#ff9800'
    case 'critical': return '#f44336'
    default: return '#9e9e9e'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'healthy': return <CheckCircleIcon sx={{ color: '#4caf50' }} />
    case 'warning': return <WarningIcon sx={{ color: '#ff9800' }} />
    case 'critical': return <ErrorIcon sx={{ color: '#f44336' }} />
    default: return <CheckCircleIcon sx={{ color: '#9e9e9e' }} />
  }
}

const calculateOverallHealth = (components: SystemComponent[]): number => {
  const weights = { healthy: 100, warning: 70, critical: 30, unknown: 50 }
  const totalWeight = components.reduce((sum, comp) => sum + weights[comp.status], 0)
  return Math.round(totalWeight / components.length)
}

// =============================================================================
// コンポーネント実装
// =============================================================================

const SystemHealthDashboard: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(30000) // 30秒
  const [components, setComponents] = useState<SystemComponent[]>([])
  const [healthHistory, setHealthHistory] = useState<HealthMetric[]>([])
  const [performanceHistory, setPerformanceHistory] = useState<PerformanceMetric[]>([])
  const [alerts, setAlerts] = useState<SystemAlert[]>([])
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  // データ初期化
  useEffect(() => {
    refreshData()
  }, [])

  // 自動更新
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(refreshData, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval])

  const refreshData = async () => {
    setLoading(true)
    
    // シミュレート: APIからデータを取得
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newComponents = generateSystemComponents()
    const newHealthHistory = generateHealthData(48) // 48時間
    const newPerformanceHistory = generatePerformanceData(48)
    const allAlerts = newComponents.flatMap(comp => comp.alerts)
    
    setComponents(newComponents)
    setHealthHistory(newHealthHistory)
    setPerformanceHistory(newPerformanceHistory)
    setAlerts(allAlerts.filter(alert => !alert.resolved))
    setLoading(false)
  }

  // 統計データ計算
  const stats = useMemo(() => {
    const overallHealth = calculateOverallHealth(components)
    const criticalCount = components.filter(c => c.status === 'critical').length
    const warningCount = components.filter(c => c.status === 'warning').length
    const healthyCount = components.filter(c => c.status === 'healthy').length
    const avgUptime = components.reduce((sum, c) => sum + c.uptime, 0) / components.length
    const totalAlerts = alerts.filter(a => !a.resolved).length
    const criticalAlerts = alerts.filter(a => a.level === 'critical' && !a.resolved).length

    return {
      overallHealth,
      criticalCount,
      warningCount,
      healthyCount,
      avgUptime,
      totalAlerts,
      criticalAlerts
    }
  }, [components, alerts])

  const handleExportReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      summary: stats,
      components,
      alerts: alerts.filter(a => !a.resolved),
      healthHistory: healthHistory.slice(-24), // 直近24時間
      performanceHistory: performanceHistory.slice(-24)
    }
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `system-health-report-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // =============================================================================
  // オーバービューパネル
  // =============================================================================

  const OverviewPanel = () => (
    <Grid container spacing={3}>
      {/* 統計カード */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" color="primary">
                  {stats.overallHealth}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  総合ヘルススコア
                </Typography>
              </Box>
              <DashboardIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" color="error">
                  {stats.criticalCount}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  重大な問題
                </Typography>
              </Box>
              <ErrorIcon color="error" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" color="warning">
                  {stats.warningCount}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  警告
                </Typography>
              </Box>
              <WarningIcon color="warning" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" color="success">
                  {stats.avgUptime.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  平均稼働率
                </Typography>
              </Box>
              <TimelineIcon color="success" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* システムヘルス推移チャート */}
      <Grid item xs={12} lg={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              システムヘルス推移（48時間）
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={healthHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString('ja-JP', { 
                    month: 'short', 
                    day: 'numeric', 
                    hour: '2-digit' 
                  })}
                />
                <YAxis domain={[0, 100]} />
                <RechartsTooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString('ja-JP')}
                  formatter={(value: number) => [`${value.toFixed(1)}%`, '']}
                />
                <Area 
                  type="monotone" 
                  dataKey="overall" 
                  stackId="1" 
                  stroke="#2196f3" 
                  fill="#2196f3" 
                  fillOpacity={0.6}
                  name="総合"
                />
                <Area 
                  type="monotone" 
                  dataKey="frontend" 
                  stackId="2" 
                  stroke="#4caf50" 
                  fill="#4caf50" 
                  fillOpacity={0.6}
                  name="フロントエンド"
                />
                <Area 
                  type="monotone" 
                  dataKey="backend" 
                  stackId="3" 
                  stroke="#ff9800" 
                  fill="#ff9800" 
                  fillOpacity={0.6}
                  name="バックエンド"
                />
                <Area 
                  type="monotone" 
                  dataKey="database" 
                  stackId="4" 
                  stroke="#9c27b0" 
                  fill="#9c27b0" 
                  fillOpacity={0.6}
                  name="データベース"
                />
                <Legend />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* ステータス分布 */}
      <Grid item xs={12} lg={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              コンポーネントステータス分布
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: '正常', value: stats.healthyCount, color: '#4caf50' },
                    { name: '警告', value: stats.warningCount, color: '#ff9800' },
                    { name: '重大', value: stats.criticalCount, color: '#f44336' }
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {[
                    { name: '正常', value: stats.healthyCount, color: '#4caf50' },
                    { name: '警告', value: stats.warningCount, color: '#ff9800' },
                    { name: '重大', value: stats.criticalCount, color: '#f44336' }
                  ].map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* アクティブアラート */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                アクティブアラート ({stats.totalAlerts})
              </Typography>
              {stats.criticalAlerts > 0 && (
                <Chip 
                  label={`緊急: ${stats.criticalAlerts}件`} 
                  color="error" 
                  variant="filled" 
                />
              )}
            </Box>
            
            {alerts.length === 0 ? (
              <Alert severity="success">
                現在アクティブなアラートはありません
              </Alert>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>レベル</TableCell>
                      <TableCell>コンポーネント</TableCell>
                      <TableCell>メッセージ</TableCell>
                      <TableCell>発生時刻</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {alerts.slice(0, 10).map((alert) => (
                      <TableRow key={alert.id}>
                        <TableCell>
                          <Chip
                            label={alert.level}
                            color={alert.level === 'error' ? 'error' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{alert.component}</TableCell>
                        <TableCell>{alert.message}</TableCell>
                        <TableCell>
                          {new Date(alert.timestamp).toLocaleString('ja-JP')}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  // =============================================================================
  // コンポーネント詳細パネル
  // =============================================================================

  const ComponentsPanel = () => (
    <Grid container spacing={3}>
      {components.map((component) => (
        <Grid item xs={12} md={6} lg={4} key={component.id}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Box display="flex" alignItems="center" gap={1}>
                  {getStatusIcon(component.status)}
                  <Typography variant="h6" component="div">
                    {component.name}
                  </Typography>
                </Box>
                <Chip 
                  label={component.type} 
                  size="small" 
                  variant="outlined" 
                />
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  稼働率: {component.uptime.toFixed(1)}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={component.uptime} 
                  sx={{ mt: 1 }}
                />
              </Box>

              {/* メトリクス */}
              {component.metrics.cpu !== undefined && (
                <Box mb={1}>
                  <Typography variant="body2">
                    CPU: {component.metrics.cpu}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={component.metrics.cpu} 
                    color={component.metrics.cpu > 80 ? 'error' : component.metrics.cpu > 60 ? 'warning' : 'primary'}
                  />
                </Box>
              )}

              {component.metrics.memory !== undefined && (
                <Box mb={1}>
                  <Typography variant="body2">
                    メモリ: {component.metrics.memory}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={component.metrics.memory} 
                    color={component.metrics.memory > 80 ? 'error' : component.metrics.memory > 60 ? 'warning' : 'primary'}
                  />
                </Box>
              )}

              {component.metrics.responseTime !== undefined && (
                <Typography variant="body2" color="textSecondary">
                  応答時間: {component.metrics.responseTime}ms
                </Typography>
              )}

              {component.metrics.errorRate !== undefined && (
                <Typography variant="body2" color="textSecondary">
                  エラー率: {component.metrics.errorRate.toFixed(1)}%
                </Typography>
              )}

              <Typography variant="caption" display="block" mt={1}>
                最終チェック: {new Date(component.lastCheck).toLocaleString('ja-JP')}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  )

  // =============================================================================
  // パフォーマンスパネル
  // =============================================================================

  const PerformancePanel = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              システムパフォーマンス推移（48時間）
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={performanceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString('ja-JP', { 
                    month: 'short', 
                    day: 'numeric', 
                    hour: '2-digit' 
                  })}
                />
                <YAxis yAxisId="time" orientation="left" />
                <YAxis yAxisId="rate" orientation="right" />
                <RechartsTooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString('ja-JP')}
                />
                <Line 
                  yAxisId="time"
                  type="monotone" 
                  dataKey="responseTime" 
                  stroke="#2196f3" 
                  strokeWidth={2}
                  name="応答時間 (ms)"
                />
                <Line 
                  yAxisId="rate"
                  type="monotone" 
                  dataKey="errorRate" 
                  stroke="#f44336" 
                  strokeWidth={2}
                  name="エラー率 (%)"
                />
                <Line 
                  yAxisId="rate"
                  type="monotone" 
                  dataKey="throughput" 
                  stroke="#4caf50" 
                  strokeWidth={2}
                  name="スループット (req/s)"
                />
                <Legend />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  // =============================================================================
  // メインUI
  // =============================================================================

  return (
    <Box p={3}>
      {/* ヘッダー */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          システムヘルスダッシュボード
        </Typography>
        
        <Box display="flex" gap={1} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="自動更新"
          />
          
          <Tooltip title="今すぐ更新">
            <IconButton 
              onClick={refreshData} 
              disabled={loading}
              color="primary"
            >
              {loading ? <CircularProgress size={24} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>

          <Tooltip title="レポート出力">
            <IconButton onClick={handleExportReport} color="primary">
              <DownloadIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="設定">
            <IconButton onClick={() => setSettingsOpen(true)} color="primary">
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* ナビゲーションタブ */}
      <Box mb={3}>
        <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
          <Tab icon={<DashboardIcon />} label="オーバービュー" />
          <Tab icon={<SpeedIcon />} label="コンポーネント" />
          <Tab icon={<TimelineIcon />} label="パフォーマンス" />
        </Tabs>
      </Box>

      {/* パネル表示 */}
      {currentTab === 0 && <OverviewPanel />}
      {currentTab === 1 && <ComponentsPanel />}
      {currentTab === 2 && <PerformancePanel />}

      {/* 設定ダイアログ */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)}>
        <DialogTitle>ダッシュボード設定</DialogTitle>
        <DialogContent>
          <Box py={2}>
            <Typography gutterBottom>
              自動更新間隔: {refreshInterval / 1000}秒
            </Typography>
            {/* 設定オプションを追加可能 */}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>
            閉じる
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default SystemHealthDashboard