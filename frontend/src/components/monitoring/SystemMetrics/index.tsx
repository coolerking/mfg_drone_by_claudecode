import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  Switch,
  FormControlLabel
} from '@mui/material'
import {
  Memory,
  Storage,
  Speed,
  Thermostat,
  NetworkCheck,
  Refresh,
  Settings,
  TrendingUp,
  TrendingDown,
  Remove
} from '@mui/icons-material'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler
} from 'chart.js'
import { dashboardApi } from '../../../services/api/dashboardApi'
import type { PerformanceMetrics, SystemHealth } from '../../../services/api/dashboardApi'
import { useNotification } from '../../common'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
)

interface SystemMetricsProps {
  refreshInterval?: number
  showCharts?: boolean
  compact?: boolean
}

interface MetricCardProps {
  title: string
  value: number
  unit: string
  icon: React.ReactNode
  color: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
  trend?: 'up' | 'down' | 'stable'
  threshold?: { warning: number; critical: number }
  historicalData?: number[]
  showChart?: boolean
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  icon,
  color,
  trend,
  threshold,
  historicalData,
  showChart = false
}) => {
  const getStatusColor = (): 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success' => {
    if (!threshold) return color
    
    if (value >= threshold.critical) return 'error'
    if (value >= threshold.warning) return 'warning'
    return 'success'
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp fontSize="small" color="error" />
      case 'down':
        return <TrendingDown fontSize="small" color="success" />
      default:
        return <Remove fontSize="small" color="disabled" />
    }
  }

  const chartData = {
    labels: historicalData?.map((_, index) => `${index * 5}m`) || [],
    datasets: [
      {
        data: historicalData || [],
        borderColor: color === 'error' ? '#f44336' : color === 'warning' ? '#ff9800' : '#2196f3',
        backgroundColor: `${color === 'error' ? '#f44336' : color === 'warning' ? '#ff9800' : '#2196f3'}20`,
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    },
    scales: {
      x: { display: false },
      y: { display: false }
    }
  }

  return (
    <Card elevation={2} sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {icon}
            <Typography variant="h6" component="h3" color="text.secondary">
              {title}
            </Typography>
          </Box>
          {getTrendIcon()}
        </Box>
        
        <Box display="flex" alignItems="baseline" gap={1} mb={2}>
          <Typography variant="h4" component="div" color={`${getStatusColor()}.main`}>
            {value.toFixed(1)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {unit}
          </Typography>
        </Box>

        <LinearProgress
          variant="determinate"
          value={Math.min(value, 100)}
          color={getStatusColor()}
          sx={{ mb: 2 }}
        />

        {threshold && (
          <Box display="flex" gap={1} mb={2}>
            <Chip
              label={`Warning: ${threshold.warning}${unit}`}
              size="small"
              color="warning"
              variant="outlined"
            />
            <Chip
              label={`Critical: ${threshold.critical}${unit}`}
              size="small"
              color="error"
              variant="outlined"
            />
          </Box>
        )}

        {showChart && historicalData && historicalData.length > 0 && (
          <Box height={60}>
            <Line data={chartData} options={chartOptions} />
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export const SystemMetrics: React.FC<SystemMetricsProps> = ({
  refreshInterval = 30000,
  showCharts = true,
  compact = false
}) => {
  const { showNotification } = useNotification()
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [historicalData, setHistoricalData] = useState<PerformanceMetrics[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [settingsAnchor, setSettingsAnchor] = useState<null | HTMLElement>(null)

  const fetchCurrentMetrics = async () => {
    try {
      const [currentMetrics, systemHealth] = await Promise.all([
        dashboardApi.getCurrentMetrics(),
        dashboardApi.getSystemHealth()
      ])
      
      setMetrics(currentMetrics)
      setHealth(systemHealth)
      
      // Update historical data (keep last 12 data points for 1-hour history)
      setHistoricalData(prev => {
        const newData = [...prev, currentMetrics].slice(-12)
        return newData
      })
      
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to fetch system metrics:', error)
      showNotification('システムメトリクスの取得に失敗しました', 'error')
      setIsLoading(false)
    }
  }

  const handleRefresh = () => {
    setIsLoading(true)
    fetchCurrentMetrics()
  }

  const handleSettingsClick = (event: React.MouseEvent<HTMLElement>) => {
    setSettingsAnchor(event.currentTarget)
  }

  const handleSettingsClose = () => {
    setSettingsAnchor(null)
  }

  useEffect(() => {
    fetchCurrentMetrics()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchCurrentMetrics()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [refreshInterval, autoRefresh])

  if (isLoading || !metrics || !health) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          システムメトリクス
        </Typography>
        <Grid container spacing={2}>
          {[...Array(4)].map((_, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card>
                <CardContent>
                  <LinearProgress />
                  <Typography variant="h6" sx={{ mt: 2 }}>
                    読み込み中...
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    )
  }

  const getCpuHistoricalData = () => 
    historicalData.map(data => data.cpu_usage)

  const getMemoryHistoricalData = () => 
    historicalData.map(data => data.memory_usage)

  const getDiskHistoricalData = () => 
    historicalData.map(data => data.disk_usage)

  const getNetworkHistoricalData = () => 
    historicalData.map(data => data.network_in + data.network_out)

  const calculateTrend = (data: number[]): 'up' | 'down' | 'stable' => {
    if (data.length < 2) return 'stable'
    const recent = data.slice(-3).reduce((a, b) => a + b, 0) / 3
    const previous = data.slice(-6, -3).reduce((a, b) => a + b, 0) / 3
    const diff = recent - previous
    if (Math.abs(diff) < 2) return 'stable'
    return diff > 0 ? 'up' : 'down'
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6" component="h2">
          システムメトリクス
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip
            label={health.overall_status === 'healthy' ? '正常' : 
                  health.overall_status === 'warning' ? '警告' : '異常'}
            color={health.overall_status === 'healthy' ? 'success' : 
                   health.overall_status === 'warning' ? 'warning' : 'error'}
            size="small"
          />
          <Tooltip title="更新">
            <IconButton onClick={handleRefresh} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="設定">
            <IconButton onClick={handleSettingsClick}>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={compact ? 1 : 2}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="CPU使用率"
            value={metrics.cpu_usage}
            unit="%"
            icon={<Speed color="primary" />}
            color="primary"
            trend={calculateTrend(getCpuHistoricalData())}
            threshold={{ warning: 70, critical: 90 }}
            historicalData={showCharts ? getCpuHistoricalData() : undefined}
            showChart={showCharts}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="メモリ使用率"
            value={metrics.memory_usage}
            unit="%"
            icon={<Memory color="secondary" />}
            color="secondary"
            trend={calculateTrend(getMemoryHistoricalData())}
            threshold={{ warning: 80, critical: 95 }}
            historicalData={showCharts ? getMemoryHistoricalData() : undefined}
            showChart={showCharts}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="ディスク使用率"
            value={metrics.disk_usage}
            unit="%"
            icon={<Storage color="info" />}
            color="info"
            trend={calculateTrend(getDiskHistoricalData())}
            threshold={{ warning: 85, critical: 95 }}
            historicalData={showCharts ? getDiskHistoricalData() : undefined}
            showChart={showCharts}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="ネットワーク"
            value={metrics.network_in + metrics.network_out}
            unit="MB/s"
            icon={<NetworkCheck color="success" />}
            color="success"
            trend={calculateTrend(getNetworkHistoricalData())}
            historicalData={showCharts ? getNetworkHistoricalData() : undefined}
            showChart={showCharts}
          />
        </Grid>

        {metrics.temperature && (
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="CPU温度"
              value={metrics.temperature}
              unit="°C"
              icon={<Thermostat color="warning" />}
              color="warning"
              threshold={{ warning: 70, critical: 85 }}
            />
          </Grid>
        )}

        {metrics.gpu_usage && (
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="GPU使用率"
              value={metrics.gpu_usage}
              unit="%"
              icon={<Speed color="error" />}
              color="error"
              threshold={{ warning: 80, critical: 95 }}
            />
          </Grid>
        )}
      </Grid>

      <Menu
        anchorEl={settingsAnchor}
        open={Boolean(settingsAnchor)}
        onClose={handleSettingsClose}
      >
        <MenuItem>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="自動更新"
          />
        </MenuItem>
        <MenuItem>
          <FormControlLabel
            control={
              <Switch
                checked={showCharts}
                onChange={() => {/* Chart toggle handled by parent */}}
              />
            }
            label="チャート表示"
          />
        </MenuItem>
      </Menu>
    </Box>
  )
}

export default SystemMetrics