import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Paper,
  Chip,
  Alert,
  AlertTitle,
  IconButton,
  LinearProgress,
  Divider,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Tooltip,
  Card,
  CardContent,
  CardHeader
} from '@mui/material'
import {
  FlightTakeoff,
  Folder,
  Psychology,
  TrackChanges,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Wifi as NetworkIcon,
  Close as CloseIcon,
  Monitor,
  Timeline,
  Analytics,
  TrendingUp
} from '@mui/icons-material'

import { StatCard, StatusBadge, Loading, Button } from '../../components/common'
import { 
  WebVitalsMonitor, 
  RealTimePerformanceDashboard, 
  withPerformanceMonitor,
  usePerformanceTracking 
} from '../../components/monitoring'
import { useNotification } from '../../hooks/useNotification'
import { dashboardApi } from '../../services/api/dashboardApi'

// 既存のインターフェース
interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  network: 'normal' | 'warning' | 'error'
}

interface DroneStatus {
  id: string
  name: string
  status: 'connected' | 'disconnected' | 'flying' | 'error'
  lastUpdate: string
  battery?: number
  location?: { lat: number; lng: number }
}

interface RecentActivity {
  id: string
  type: 'flight' | 'data' | 'model' | 'system'
  message: string
  timestamp: string
  severity: 'info' | 'warning' | 'error' | 'success'
}

interface DashboardData {
  systemMetrics: SystemMetrics
  droneStatuses: DroneStatus[]
  recentActivities: RecentActivity[]
  summary: {
    totalDrones: number
    activeDrones: number
    totalDatasets: number
    activeModels: number
  }
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`dashboard-tabpanel-${index}`}
    aria-labelledby={`dashboard-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
)

const EnhancedDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentTab, setCurrentTab] = useState(0)
  const [performanceMode, setPerformanceMode] = useState(__DEV__)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval] = useState(30000) // 30秒
  
  const { showNotification } = useNotification()
  const { trackRender, trackUserAction } = usePerformanceTracking('Dashboard')

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const startTime = performance.now()
      const dashboardData = await dashboardApi.getDashboardData()
      const endTime = performance.now()
      
      // パフォーマンス追跡
      trackUserAction('data_fetch', endTime - startTime)
      
      setData(dashboardData)
      trackRender({ dataLoaded: true, itemCount: dashboardData.droneStatuses.length })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'データの取得に失敗しました'
      setError(errorMessage)
      showNotification(errorMessage, 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchDashboardData()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval])

  const handleRefresh = () => {
    trackUserAction('manual_refresh')
    fetchDashboardData()
  }

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    trackUserAction('tab_change', undefined)
    setCurrentTab(newValue)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'flying':
        return 'success'
      case 'disconnected':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'default'
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'flight':
        return <FlightTakeoff />
      case 'data':
        return <Folder />
      case 'model':
        return <Psychology />
      case 'system':
        return <SpeedIcon />
      default:
        return <InfoIcon />
    }
  }

  const getActivityColor = (severity: string) => {
    switch (severity) {
      case 'success':
        return 'success'
      case 'warning':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'info'
    }
  }

  if (loading && !data) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Loading />
      </Box>
    )
  }

  if (error && !data) {
    return (
      <Box p={3}>
        <Alert severity="error">
          <AlertTitle>エラー</AlertTitle>
          {error}
          <Box mt={2}>
            <Button variant="contained" onClick={handleRefresh} startIcon={<RefreshIcon />}>
              再試行
            </Button>
          </Box>
        </Alert>
      </Box>
    )
  }

  if (!data) {
    return (
      <Box p={3}>
        <Alert severity="info">
          <AlertTitle>データなし</AlertTitle>
          ダッシュボードデータがありません
        </Alert>
      </Box>
    )
  }

  return (
    <Box>
      {/* ヘッダー */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          ダッシュボード
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <FormControlLabel
            control={
              <Switch
                checked={performanceMode}
                onChange={(e) => setPerformanceMode(e.target.checked)}
                color="primary"
              />
            }
            label="パフォーマンス監視"
          />
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                color="primary"
              />
            }
            label="自動更新"
          />
          <Tooltip title="データを更新">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* タブナビゲーション */}
      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab icon={<Analytics />} label="概要" />
          <Tab icon={<Monitor />} label="システム監視" />
          {performanceMode && <Tab icon={<Timeline />} label="パフォーマンス" />}
          {performanceMode && <Tab icon={<TrendingUp />} label="リアルタイム監視" />}
        </Tabs>

        {/* 概要タブ */}
        <TabPanel value={currentTab} index={0}>
          {/* サマリーカード */}
          <Grid container spacing={3} mb={3}>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="総ドローン数"
                value={data.summary.totalDrones}
                icon={<FlightTakeoff />}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="アクティブドローン"
                value={data.summary.activeDrones}
                icon={<FlightTakeoff />}
                color="success"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="データセット数"
                value={data.summary.totalDatasets}
                icon={<Folder />}
                color="info"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="アクティブモデル"
                value={data.summary.activeModels}
                icon={<Psychology />}
                color="warning"
              />
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            {/* システムメトリクス */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="システムメトリクス" />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <SpeedIcon color="primary" />
                          <Typography>CPU使用率</Typography>
                        </Box>
                        <Typography variant="h6">{data.systemMetrics.cpu}%</Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={data.systemMetrics.cpu}
                        color={data.systemMetrics.cpu > 80 ? 'error' : 'primary'}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <MemoryIcon color="secondary" />
                          <Typography>メモリ使用率</Typography>
                        </Box>
                        <Typography variant="h6">{data.systemMetrics.memory}%</Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={data.systemMetrics.memory}
                        color={data.systemMetrics.memory > 80 ? 'error' : 'secondary'}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <StorageIcon color="info" />
                          <Typography>ディスク使用率</Typography>
                        </Box>
                        <Typography variant="h6">{data.systemMetrics.disk}%</Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={data.systemMetrics.disk}
                        color={data.systemMetrics.disk > 80 ? 'error' : 'info'}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box display="flex" alignItems="center" gap={1}>
                          <NetworkIcon color="success" />
                          <Typography>ネットワーク</Typography>
                        </Box>
                        <StatusBadge status={data.systemMetrics.network} />
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* ドローンステータス */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="ドローンステータス" />
                <CardContent>
                  <Box maxHeight="300px" overflow="auto">
                    {data.droneStatuses.map((drone) => (
                      <Box key={drone.id} mb={2}>
                        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                          <Typography variant="subtitle1">{drone.name}</Typography>
                          <Chip
                            label={drone.status}
                            color={getStatusColor(drone.status) as any}
                            size="small"
                          />
                        </Box>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Typography variant="body2" color="text.secondary">
                            最終更新: {drone.lastUpdate}
                          </Typography>
                          {drone.battery !== undefined && (
                            <Typography variant="body2" color="text.secondary">
                              バッテリー: {drone.battery}%
                            </Typography>
                          )}
                        </Box>
                        {drone !== data.droneStatuses[data.droneStatuses.length - 1] && (
                          <Divider sx={{ mt: 1 }} />
                        )}
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* 最近のアクティビティ */}
            <Grid item xs={12}>
              <Card>
                <CardHeader title="最近のアクティビティ" />
                <CardContent>
                  <Box maxHeight="400px" overflow="auto">
                    {data.recentActivities.map((activity) => (
                      <Box key={activity.id} mb={2}>
                        <Box display="flex" alignItems="flex-start" gap={2}>
                          <Box color={`${getActivityColor(activity.severity)}.main`}>
                            {getActivityIcon(activity.type)}
                          </Box>
                          <Box flexGrow={1}>
                            <Typography variant="body1">{activity.message}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {activity.timestamp}
                            </Typography>
                          </Box>
                          <Chip
                            label={activity.type}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                        {activity !== data.recentActivities[data.recentActivities.length - 1] && (
                          <Divider sx={{ mt: 1 }} />
                        )}
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* システム監視タブ */}
        <TabPanel value={currentTab} index={1}>
          <Box>
            <Typography variant="h6" gutterBottom>
              詳細システム監視
            </Typography>
            {/* SystemMetrics コンポーネントがここに表示される */}
            <Typography variant="body2" color="text.secondary">
              詳細なシステム監視コンポーネントが表示されます
            </Typography>
          </Box>
        </TabPanel>

        {/* パフォーマンスタブ */}
        {performanceMode && (
          <TabPanel value={currentTab} index={2}>
            <WebVitalsMonitor
              showChart={true}
              autoRefresh={autoRefresh}
              refreshInterval={10000}
            />
          </TabPanel>
        )}

        {/* リアルタイム監視タブ */}
        {performanceMode && (
          <TabPanel value={currentTab} index={3}>
            <RealTimePerformanceDashboard
              autoRefresh={autoRefresh}
              refreshInterval={5000}
              showAlerts={true}
            />
          </TabPanel>
        )}
      </Paper>
    </Box>
  )
}

// パフォーマンス監視でラップ
export default withPerformanceMonitor(EnhancedDashboard, {
  enabled: true,
  showAlert: __DEV__,
  slowRenderThreshold: 100,
  logToConsole: __DEV__,
  sendMetrics: true
})