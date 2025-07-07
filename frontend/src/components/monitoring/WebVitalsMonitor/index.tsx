import React, { useState, useEffect, useRef } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel
} from '@mui/material'
import {
  Speed,
  TrendingUp,
  TrendingDown,
  Remove,
  Info,
  Warning,
  Error as ErrorIcon,
  Refresh,
  ExpandMore,
  ExpandLess,
  Visibility,
  Mouse,
  Apps,
  Assessment
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
import { monitoring, useMonitoring } from '../../../utils/monitoring'

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

interface WebVitalMetric {
  name: string
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
  threshold: { good: number; poor: number }
  unit: string
  icon: React.ReactNode
  description: string
}

interface WebVitalsData {
  fcp: number
  lcp: number
  fid: number
  cls: number
  ttfb: number
  timestamp: number
}

interface WebVitalsMonitorProps {
  showChart?: boolean
  autoRefresh?: boolean
  refreshInterval?: number
  compact?: boolean
}

const getRating = (value: number, thresholds: { good: number; poor: number }): 'good' | 'needs-improvement' | 'poor' => {
  if (value <= thresholds.good) return 'good'
  if (value <= thresholds.poor) return 'needs-improvement'
  return 'poor'
}

const getRatingColor = (rating: string) => {
  switch (rating) {
    case 'good': return 'success'
    case 'needs-improvement': return 'warning'
    case 'poor': return 'error'
    default: return 'info'
  }
}

const WebVitalCard: React.FC<{
  metric: WebVitalMetric
  historicalData?: number[]
  showChart?: boolean
  compact?: boolean
}> = ({ metric, historicalData, showChart = false, compact = false }) => {
  const [expanded, setExpanded] = useState(false)

  const chartData = {
    labels: historicalData?.map((_, index) => `${index * 30}s`) || [],
    datasets: [
      {
        data: historicalData || [],
        borderColor: metric.rating === 'good' ? '#4caf50' : metric.rating === 'needs-improvement' ? '#ff9800' : '#f44336',
        backgroundColor: `${metric.rating === 'good' ? '#4caf50' : metric.rating === 'needs-improvement' ? '#ff9800' : '#f44336'}20`,
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
      tooltip: {
        callbacks: {
          label: (context: any) => `${metric.name}: ${context.parsed.y.toFixed(2)}${metric.unit}`
        }
      }
    },
    scales: {
      x: { display: false },
      y: { 
        display: false,
        min: 0,
        max: metric.threshold.poor * 1.2
      }
    }
  }

  return (
    <Card elevation={2} sx={{ height: compact ? 'auto' : '100%' }}>
      <CardContent sx={{ pb: compact ? 1 : 2 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Box display="flex" alignItems="center" gap={1}>
            {metric.icon}
            <Typography variant={compact ? "body2" : "h6"} component="h3" color="text.secondary">
              {metric.name}
            </Typography>
          </Box>
          <Chip
            size="small"
            label={metric.rating === 'good' ? '良好' : metric.rating === 'needs-improvement' ? '改善要' : '要対応'}
            color={getRatingColor(metric.rating) as any}
          />
        </Box>
        
        <Box display="flex" alignItems="baseline" gap={1} mb={1}>
          <Typography variant={compact ? "h6" : "h4"} component="div" color={`${getRatingColor(metric.rating)}.main`}>
            {metric.value.toFixed(metric.unit === 'ms' ? 0 : 3)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {metric.unit}
          </Typography>
        </Box>

        <LinearProgress
          variant="determinate"
          value={Math.min((metric.value / metric.threshold.poor) * 100, 100)}
          color={getRatingColor(metric.rating) as any}
          sx={{ mb: 1 }}
        />

        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="caption" color="success.main">
            良好: ≤{metric.threshold.good}{metric.unit}
          </Typography>
          <Typography variant="caption" color="error.main">
            要対応: >{metric.threshold.poor}{metric.unit}
          </Typography>
        </Box>

        {!compact && (
          <Box>
            <IconButton size="small" onClick={() => setExpanded(!expanded)}>
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
            
            <Collapse in={expanded}>
              <Typography variant="body2" color="text.secondary" mb={2}>
                {metric.description}
              </Typography>
              
              {showChart && historicalData && historicalData.length > 0 && (
                <Box height={100} mb={2}>
                  <Line data={chartData} options={chartOptions} />
                </Box>
              )}
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Info fontSize="small" color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="良好" 
                    secondary={`≤${metric.threshold.good}${metric.unit}`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Warning fontSize="small" color="warning" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="改善必要" 
                    secondary={`${metric.threshold.good + (metric.unit === 'ms' ? 1 : 0.001)}-${metric.threshold.poor}${metric.unit}`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <ErrorIcon fontSize="small" color="error" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="要対応" 
                    secondary={`>${metric.threshold.poor}${metric.unit}`}
                  />
                </ListItem>
              </List>
            </Collapse>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export const WebVitalsMonitor: React.FC<WebVitalsMonitorProps> = ({
  showChart = true,
  autoRefresh = true,
  refreshInterval = 30000,
  compact = false
}) => {
  const { reportMetric } = useMonitoring()
  const [vitalsData, setVitalsData] = useState<WebVitalsData[]>([])
  const [currentVitals, setCurrentVitals] = useState<WebVitalsData | null>(null)
  const [isCollecting, setIsCollecting] = useState(autoRefresh)
  const observersRef = useRef<PerformanceObserver[]>([])

  const createWebVitalMetrics = (data: WebVitalsData): WebVitalMetric[] => [
    {
      name: 'FCP',
      value: data.fcp,
      rating: getRating(data.fcp, { good: 1800, poor: 3000 }),
      threshold: { good: 1800, poor: 3000 },
      unit: 'ms',
      icon: <Visibility color="primary" />,
      description: 'First Contentful Paint - ページの最初のコンテンツが表示されるまでの時間'
    },
    {
      name: 'LCP',
      value: data.lcp,
      rating: getRating(data.lcp, { good: 2500, poor: 4000 }),
      threshold: { good: 2500, poor: 4000 },
      unit: 'ms',
      icon: <Apps color="secondary" />,
      description: 'Largest Contentful Paint - 最大のコンテンツが表示されるまでの時間'
    },
    {
      name: 'FID',
      value: data.fid,
      rating: getRating(data.fid, { good: 100, poor: 300 }),
      threshold: { good: 100, poor: 300 },
      unit: 'ms',
      icon: <Mouse color="info" />,
      description: 'First Input Delay - 最初のユーザー操作への応答時間'
    },
    {
      name: 'CLS',
      value: data.cls,
      rating: getRating(data.cls, { good: 0.1, poor: 0.25 }),
      threshold: { good: 0.1, poor: 0.25 },
      unit: '',
      icon: <Assessment color="warning" />,
      description: 'Cumulative Layout Shift - ページの視覚的安定性の指標'
    },
    {
      name: 'TTFB',
      value: data.ttfb,
      rating: getRating(data.ttfb, { good: 800, poor: 1800 }),
      threshold: { good: 800, poor: 1800 },
      unit: 'ms',
      icon: <Speed color="error" />,
      description: 'Time to First Byte - サーバーからの最初の応答時間'
    }
  ]

  const initializeWebVitalsCollection = () => {
    // Clear existing observers
    observersRef.current.forEach(observer => observer.disconnect())
    observersRef.current = []

    let currentData: Partial<WebVitalsData> = {
      timestamp: Date.now()
    }

    // FCP Observer
    try {
      const fcpObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (entry.name === 'first-contentful-paint') {
            currentData.fcp = entry.startTime
            reportMetric('fcp', entry.startTime)
            updateCurrentVitals(currentData)
          }
        }
      })
      fcpObserver.observe({ entryTypes: ['paint'] })
      observersRef.current.push(fcpObserver)
    } catch (error) {
      console.warn('FCP observer not supported:', error)
    }

    // LCP Observer
    try {
      const lcpObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          currentData.lcp = entry.startTime
          reportMetric('lcp', entry.startTime)
          updateCurrentVitals(currentData)
        }
      })
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })
      observersRef.current.push(lcpObserver)
    } catch (error) {
      console.warn('LCP observer not supported:', error)
    }

    // FID Observer
    try {
      const fidObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          const fidValue = (entry as any).processingStart - entry.startTime
          currentData.fid = fidValue
          reportMetric('fid', fidValue)
          updateCurrentVitals(currentData)
        }
      })
      fidObserver.observe({ entryTypes: ['first-input'] })
      observersRef.current.push(fidObserver)
    } catch (error) {
      console.warn('FID observer not supported:', error)
    }

    // CLS Observer
    try {
      let clsValue = 0
      const clsObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value
            currentData.cls = clsValue
            reportMetric('cls', clsValue)
            updateCurrentVitals(currentData)
          }
        }
      })
      clsObserver.observe({ entryTypes: ['layout-shift'] })
      observersRef.current.push(clsObserver)
    } catch (error) {
      console.warn('CLS observer not supported:', error)
    }

    // TTFB from Navigation Timing
    if (performance.getEntriesByType) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      if (navigation) {
        const ttfb = navigation.responseStart - navigation.requestStart
        currentData.ttfb = ttfb
        reportMetric('ttfb', ttfb)
        updateCurrentVitals(currentData)
      }
    }
  }

  const updateCurrentVitals = (data: Partial<WebVitalsData>) => {
    if (data.fcp !== undefined || data.lcp !== undefined || data.fid !== undefined || 
        data.cls !== undefined || data.ttfb !== undefined) {
      
      const completeData: WebVitalsData = {
        fcp: data.fcp || 0,
        lcp: data.lcp || 0,
        fid: data.fid || 0,
        cls: data.cls || 0,
        ttfb: data.ttfb || 0,
        timestamp: data.timestamp || Date.now()
      }
      
      setCurrentVitals(completeData)
      
      // Add to historical data (keep last 20 measurements)
      setVitalsData(prev => {
        const newData = [...prev, completeData].slice(-20)
        return newData
      })
    }
  }

  const handleToggleCollection = () => {
    if (isCollecting) {
      observersRef.current.forEach(observer => observer.disconnect())
      observersRef.current = []
    } else {
      initializeWebVitalsCollection()
    }
    setIsCollecting(!isCollecting)
  }

  const handleRefresh = () => {
    if (isCollecting) {
      observersRef.current.forEach(observer => observer.disconnect())
      observersRef.current = []
      initializeWebVitalsCollection()
    }
  }

  useEffect(() => {
    if (isCollecting) {
      initializeWebVitalsCollection()
    }

    return () => {
      observersRef.current.forEach(observer => observer.disconnect())
    }
  }, [isCollecting])

  useEffect(() => {
    if (!autoRefresh || !isCollecting) return

    const interval = setInterval(() => {
      handleRefresh()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, isCollecting, refreshInterval])

  if (!currentVitals) {
    return (
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h2">
            Core Web Vitals監視
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={isCollecting}
                onChange={handleToggleCollection}
                color="primary"
              />
            }
            label="データ収集"
          />
        </Box>
        
        <Alert severity="info">
          Core Web Vitalsデータを収集中です。ページの操作を行ってください。
        </Alert>
      </Box>
    )
  }

  const metrics = createWebVitalMetrics(currentVitals)
  const overallRating = metrics.filter(m => m.rating === 'good').length >= 4 ? 'good' : 
                       metrics.filter(m => m.rating === 'poor').length >= 2 ? 'poor' : 'needs-improvement'

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6" component="h2">
          Core Web Vitals監視
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip
            label={overallRating === 'good' ? '良好' : overallRating === 'needs-improvement' ? '改善要' : '要対応'}
            color={getRatingColor(overallRating) as any}
            size="small"
          />
          <FormControlLabel
            control={
              <Switch
                checked={isCollecting}
                onChange={handleToggleCollection}
                color="primary"
              />
            }
            label="データ収集"
          />
          <Tooltip title="更新">
            <IconButton onClick={handleRefresh} disabled={!isCollecting}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={compact ? 1 : 2}>
        {metrics.map((metric) => (
          <Grid item xs={12} sm={6} md={compact ? 4 : 2.4} key={metric.name}>
            <WebVitalCard
              metric={metric}
              historicalData={vitalsData.map(data => data[metric.name.toLowerCase() as keyof WebVitalsData] as number)}
              showChart={showChart}
              compact={compact}
            />
          </Grid>
        ))}
      </Grid>

      {vitalsData.length > 0 && showChart && !compact && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            パフォーマンス推移
          </Typography>
          <Card>
            <CardContent>
              <Box height={300}>
                <Line
                  data={{
                    labels: vitalsData.map((_, index) => `測定${index + 1}`),
                    datasets: metrics.map((metric) => ({
                      label: metric.name,
                      data: vitalsData.map(data => data[metric.name.toLowerCase() as keyof WebVitalsData] as number),
                      borderColor: metric.rating === 'good' ? '#4caf50' : metric.rating === 'needs-improvement' ? '#ff9800' : '#f44336',
                      backgroundColor: `${metric.rating === 'good' ? '#4caf50' : metric.rating === 'needs-improvement' ? '#ff9800' : '#f44336'}20`,
                      borderWidth: 2,
                      fill: false,
                      tension: 0.4
                    }))
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: true, position: 'top' },
                      tooltip: {
                        callbacks: {
                          label: (context: any) => {
                            const metric = metrics[context.datasetIndex]
                            return `${metric.name}: ${context.parsed.y.toFixed(metric.unit === 'ms' ? 0 : 3)}${metric.unit}`
                          }
                        }
                      }
                    },
                    scales: {
                      y: { beginAtZero: true }
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  )
}

export default WebVitalsMonitor