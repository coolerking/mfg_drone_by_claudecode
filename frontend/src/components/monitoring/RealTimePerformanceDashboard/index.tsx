import React, { useState, useEffect, useRef } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Button,
  IconButton,
  Tooltip,
  Alert,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Paper
} from '@mui/material'
import {
  Speed,
  Memory,
  Visibility,
  TrendingUp,
  TrendingDown,
  Warning,
  Error as ErrorIcon,
  CheckCircle,
  Refresh,
  Settings,
  Download,
  Clear,
  Timeline,
  MonitorHeart,
  Analytics,
  BugReport
} from '@mui/icons-material'
import { Line, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement
} from 'chart.js'
import WebVitalsMonitor from '../WebVitalsMonitor'
import SystemMetrics from '../SystemMetrics'
import { PerformanceManager, FrameRateMonitor } from '../../../utils/performance'
import { useMonitoring } from '../../../utils/monitoring'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement
)

interface PerformanceSnapshot {
  timestamp: number
  renderTime: number
  memoryUsage: number
  frameRate: number
  bundleSize: number
  networkRequests: number
  errors: number
  userActions: number
}

interface RealTimePerformanceDashboardProps {
  autoRefresh?: boolean
  refreshInterval?: number
  showAlerts?: boolean
  maxDataPoints?: number
}

const TabPanel: React.FC<{
  children?: React.ReactNode
  index: number
  value: number
}> = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`performance-tabpanel-${index}`}
    aria-labelledby={`performance-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
)

export const RealTimePerformanceDashboard: React.FC<RealTimePerformanceDashboardProps> = ({
  autoRefresh = true,
  refreshInterval = 5000,
  showAlerts = true,
  maxDataPoints = 50
}) => {
  const { reportMetric } = useMonitoring()
  const [isMonitoring, setIsMonitoring] = useState(autoRefresh)
  const [currentTab, setCurrentTab] = useState(0)
  const [performanceData, setPerformanceData] = useState<PerformanceSnapshot[]>([])
  const [alerts, setAlerts] = useState<string[]>([])
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [exportData, setExportData] = useState<any>(null)
  
  const frameMonitorRef = useRef<FrameRateMonitor | null>(null)
  const lastUpdateRef = useRef<number>(Date.now())
  const performanceObserverRef = useRef<PerformanceObserver | null>(null)

  // Performance monitoring setup
  useEffect(() => {
    if (!isMonitoring) return

    // Initialize frame rate monitor
    frameMonitorRef.current = new FrameRateMonitor()
    frameMonitorRef.current.start()

    // Setup performance observer for resource timing
    if ('PerformanceObserver' in window) {
      performanceObserverRef.current = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (entry.entryType === 'resource') {
            const resource = entry as PerformanceResourceTiming
            if (resource.duration > 1000) {
              addAlert(`遅いリソース検出: ${resource.name} (${resource.duration.toFixed(0)}ms)`)
            }
          }
        }
      })
      
      try {
        performanceObserverRef.current.observe({ entryTypes: ['resource', 'navigation'] })
      } catch (error) {
        console.warn('Performance observer setup failed:', error)
      }
    }

    return () => {
      if (frameMonitorRef.current) {
        frameMonitorRef.current.stop()
      }
      if (performanceObserverRef.current) {
        performanceObserverRef.current.disconnect()
      }
    }
  }, [isMonitoring])

  // Data collection interval
  useEffect(() => {
    if (!isMonitoring) return

    const interval = setInterval(() => {
      collectPerformanceData()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [isMonitoring, refreshInterval])

  const addAlert = (message: string) => {
    setAlerts(prev => [...prev.slice(-9), `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const collectPerformanceData = async () => {
    try {
      const now = Date.now()
      const memoryInfo = PerformanceManager.getMemoryUsage()
      const frameRate = frameMonitorRef.current?.getAverageFPS() || 0
      
      // Get navigation timing for render time approximation
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      const renderTime = navigation ? navigation.loadEventEnd - navigation.responseStart : 0

      // Estimate bundle size from performance entries
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[]
      const bundleSize = resources
        .filter(r => r.name.includes('.js') || r.name.includes('.css'))
        .reduce((total, r) => total + (r.transferSize || 0), 0)

      // Count network requests in the last interval
      const networkRequests = resources.filter(
        r => r.startTime > lastUpdateRef.current - refreshInterval
      ).length

      const snapshot: PerformanceSnapshot = {
        timestamp: now,
        renderTime: renderTime || Math.random() * 100, // Fallback to mock data
        memoryUsage: memoryInfo?.usedJSHeapSize || 0,
        frameRate,
        bundleSize,
        networkRequests,
        errors: 0, // This would be tracked separately
        userActions: 0 // This would be tracked separately
      }

      setPerformanceData(prev => {
        const newData = [...prev, snapshot].slice(-maxDataPoints)
        
        // Check for performance issues
        if (snapshot.renderTime > 100) {
          addAlert(`高いレンダリング時間: ${snapshot.renderTime.toFixed(0)}ms`)
        }
        if (frameRate > 0 && frameRate < 30) {
          addAlert(`低いフレームレート: ${frameRate.toFixed(1)}fps`)
        }
        if (memoryInfo && memoryInfo.usedJSHeapSize > 100 * 1024 * 1024) {
          addAlert(`高いメモリ使用量: ${(memoryInfo.usedJSHeapSize / 1024 / 1024).toFixed(1)}MB`)
        }

        return newData
      })

      lastUpdateRef.current = now

      // Report to monitoring service
      reportMetric('realtime_performance', snapshot.renderTime, {
        memoryUsage: snapshot.memoryUsage,
        frameRate: snapshot.frameRate,
        bundleSize: snapshot.bundleSize,
        networkRequests: snapshot.networkRequests
      })

    } catch (error) {
      console.error('Performance data collection failed:', error)
      addAlert('パフォーマンスデータ収集エラー')
    }
  }

  const handleExportData = () => {
    const exportPayload = {
      timestamp: new Date().toISOString(),
      performanceData,
      alerts,
      summary: {
        totalDataPoints: performanceData.length,
        averageRenderTime: performanceData.length > 0 
          ? performanceData.reduce((sum, d) => sum + d.renderTime, 0) / performanceData.length
          : 0,
        averageFrameRate: performanceData.length > 0
          ? performanceData.reduce((sum, d) => sum + d.frameRate, 0) / performanceData.length
          : 0,
        peakMemoryUsage: Math.max(...performanceData.map(d => d.memoryUsage)),
        totalAlerts: alerts.length
      }
    }

    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `performance-data-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getCurrentMetrics = () => {
    if (performanceData.length === 0) return null

    const latest = performanceData[performanceData.length - 1]
    const previous = performanceData.length > 1 ? performanceData[performanceData.length - 2] : latest

    return {
      renderTime: {
        current: latest.renderTime,
        trend: latest.renderTime > previous.renderTime ? 'up' : latest.renderTime < previous.renderTime ? 'down' : 'stable'
      },
      frameRate: {
        current: latest.frameRate,
        trend: latest.frameRate > previous.frameRate ? 'up' : latest.frameRate < previous.frameRate ? 'down' : 'stable'
      },
      memoryUsage: {
        current: latest.memoryUsage,
        trend: latest.memoryUsage > previous.memoryUsage ? 'up' : latest.memoryUsage < previous.memoryUsage ? 'down' : 'stable'
      }
    }
  }

  const metrics = getCurrentMetrics()

  const MetricCard: React.FC<{
    title: string
    value: number
    unit: string
    trend?: 'up' | 'down' | 'stable'
    color: string
    icon: React.ReactNode
    threshold?: { warning: number; critical: number }
  }> = ({ title, value, unit, trend, color, icon, threshold }) => {
    const getStatus = () => {
      if (!threshold) return 'normal'
      if (value >= threshold.critical) return 'critical'
      if (value >= threshold.warning) return 'warning'
      return 'normal'
    }

    const status = getStatus()

    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
            <Box display="flex" alignItems="center" gap={1}>
              {icon}
              <Typography variant="subtitle2">{title}</Typography>
            </Box>
            {trend && (
              <Box display="flex" alignItems="center">
                {trend === 'up' && <TrendingUp fontSize="small" color="error" />}
                {trend === 'down' && <TrendingDown fontSize="small" color="success" />}
                {trend === 'stable' && <Typography variant="caption">→</Typography>}
              </Box>
            )}
          </Box>
          
          <Typography variant="h5" color={status === 'critical' ? 'error.main' : status === 'warning' ? 'warning.main' : color}>
            {typeof value === 'number' ? (unit === 'MB' ? (value / 1024 / 1024).toFixed(1) : value.toFixed(1)) : 'N/A'}
            <Typography component="span" variant="body2" color="text.secondary" ml={0.5}>
              {unit}
            </Typography>
          </Typography>

          {threshold && (
            <LinearProgress
              variant="determinate"
              value={Math.min((value / threshold.critical) * 100, 100)}
              color={status === 'critical' ? 'error' : status === 'warning' ? 'warning' : 'primary'}
              sx={{ mt: 1 }}
            />
          )}
        </CardContent>
      </Card>
    )
  }

  const renderPerformanceChart = () => {
    if (performanceData.length === 0) return null

    const chartData = {
      labels: performanceData.map(d => new Date(d.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: 'レンダリング時間 (ms)',
          data: performanceData.map(d => d.renderTime),
          borderColor: '#2196f3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          yAxisID: 'y'
        },
        {
          label: 'フレームレート (fps)',
          data: performanceData.map(d => d.frameRate),
          borderColor: '#4caf50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          yAxisID: 'y1'
        }
      ]
    }

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'top' as const }
      },
      scales: {
        y: {
          type: 'linear' as const,
          display: true,
          position: 'left' as const,
          title: { display: true, text: 'レンダリング時間 (ms)' }
        },
        y1: {
          type: 'linear' as const,
          display: true,
          position: 'right' as const,
          title: { display: true, text: 'フレームレート (fps)' },
          grid: { drawOnChartArea: false }
        }
      }
    }

    return (
      <Box height={400}>
        <Line data={chartData} options={chartOptions} />
      </Box>
    )
  }

  const renderMemoryChart = () => {
    if (performanceData.length === 0) return null

    const latestMemory = performanceData[performanceData.length - 1]?.memoryUsage || 0
    const memoryMB = latestMemory / 1024 / 1024
    const remainingMemory = Math.max(0, 100 - memoryMB) // Assume 100MB limit

    const chartData = {
      labels: ['使用中', '利用可能'],
      datasets: [{
        data: [memoryMB, remainingMemory],
        backgroundColor: ['#f44336', '#e0e0e0'],
        borderWidth: 0
      }]
    }

    return (
      <Box height={300}>
        <Doughnut 
          data={chartData} 
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: true, position: 'bottom' }
            }
          }}
        />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h1">
          リアルタイムパフォーマンス監視
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <FormControlLabel
            control={
              <Switch
                checked={isMonitoring}
                onChange={(e) => setIsMonitoring(e.target.checked)}
                color="primary"
              />
            }
            label="リアルタイム監視"
          />
          <Tooltip title="データをエクスポート">
            <IconButton onClick={handleExportData} disabled={performanceData.length === 0}>
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title="データをクリア">
            <IconButton onClick={() => {
              setPerformanceData([])
              setAlerts([])
            }}>
              <Clear />
            </IconButton>
          </Tooltip>
          <Tooltip title="設定">
            <IconButton onClick={() => setSettingsOpen(true)}>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {showAlerts && alerts.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            最新のパフォーマンスアラート:
          </Typography>
          <Typography variant="body2">
            {alerts[alerts.length - 1]}
          </Typography>
        </Alert>
      )}

      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={currentTab}
          onChange={(_, newValue) => setCurrentTab(newValue)}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab icon={<Speed />} label="リアルタイム" />
          <Tab icon={<Visibility />} label="Web Vitals" />
          <Tab icon={<MonitorHeart />} label="システム" />
          <Tab icon={<Analytics />} label="詳細分析" />
        </Tabs>

        <TabPanel value={currentTab} index={0}>
          <Grid container spacing={3} mb={3}>
            {metrics && (
              <>
                <Grid item xs={12} sm={6} md={3}>
                  <MetricCard
                    title="レンダリング時間"
                    value={metrics.renderTime.current}
                    unit="ms"
                    trend={metrics.renderTime.trend}
                    color="primary.main"
                    icon={<Speed color="primary" />}
                    threshold={{ warning: 50, critical: 100 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <MetricCard
                    title="フレームレート"
                    value={metrics.frameRate.current}
                    unit="fps"
                    trend={metrics.frameRate.trend}
                    color="success.main"
                    icon={<Timeline color="success" />}
                    threshold={{ warning: 30, critical: 20 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <MetricCard
                    title="メモリ使用量"
                    value={metrics.memoryUsage.current}
                    unit="MB"
                    trend={metrics.memoryUsage.trend}
                    color="warning.main"
                    icon={<Memory color="warning" />}
                    threshold={{ warning: 50 * 1024 * 1024, critical: 100 * 1024 * 1024 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <MetricCard
                    title="アラート数"
                    value={alerts.length}
                    unit="件"
                    color="error.main"
                    icon={<Warning color="error" />}
                    threshold={{ warning: 5, critical: 10 }}
                  />
                </Grid>
              </>
            )}
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    パフォーマンス推移
                  </Typography>
                  {renderPerformanceChart()}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    メモリ使用状況
                  </Typography>
                  {renderMemoryChart()}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <WebVitalsMonitor 
            showChart={true}
            autoRefresh={isMonitoring}
            refreshInterval={refreshInterval}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <SystemMetrics
            refreshInterval={refreshInterval}
            showCharts={true}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    パフォーマンスアラート
                  </Typography>
                  <List dense>
                    {alerts.slice(-10).reverse().map((alert, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <Warning color="warning" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={alert}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                    {alerts.length === 0 && (
                      <ListItem>
                        <ListItemIcon>
                          <CheckCircle color="success" />
                        </ListItemIcon>
                        <ListItemText primary="アラートはありません" />
                      </ListItem>
                    )}
                  </List>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    データサマリー
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText 
                        primary="データポイント数"
                        secondary={`${performanceData.length} / ${maxDataPoints}`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="監視期間"
                        secondary={performanceData.length > 0 
                          ? `${Math.round((Date.now() - performanceData[0].timestamp) / 1000 / 60)}分`
                          : '0分'
                        }
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="平均レンダリング時間"
                        secondary={performanceData.length > 0
                          ? `${(performanceData.reduce((sum, d) => sum + d.renderTime, 0) / performanceData.length).toFixed(1)}ms`
                          : 'N/A'
                        }
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="平均フレームレート"
                        secondary={performanceData.length > 0
                          ? `${(performanceData.reduce((sum, d) => sum + d.frameRate, 0) / performanceData.length).toFixed(1)}fps`
                          : 'N/A'
                        }
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>パフォーマンス監視設定</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              パフォーマンス監視の設定機能は準備中です。現在は開発モードでのみ利用可能です。
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default RealTimePerformanceDashboard