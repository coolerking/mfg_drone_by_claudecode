/**
 * Advanced Log Analyzer Component
 * Provides sophisticated log collection, analysis, and pattern detection
 */

import React, { useState, useEffect, useMemo, useRef } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Paper,
  Alert,
  Divider,
  Stack,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Badge,
  LinearProgress,
  Switch,
  FormControlLabel,
  Slider,
  Autocomplete,
  TreeView,
  TreeItem,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import {
  Search,
  FilterList,
  Refresh,
  Download,
  Analytics,
  Timeline,
  Pattern,
  Memory,
  Storage,
  Speed,
  Security,
  BugReport,
  Warning,
  Error as ErrorIcon,
  Info,
  ExpandMore,
  ExpandLess,
  PlayArrow,
  Pause,
  Settings,
  Visibility,
  TrendingUp,
  TrendingDown,
  Remove,
  ChevronRight,
  AutoGraph,
  DataUsage,
  Psychology
} from '@mui/icons-material'
import { Line, Bar, Heatmap } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler
} from 'chart.js'
import { format, subHours, subDays, startOfHour, startOfDay } from 'date-fns'
import { ja } from 'date-fns/locale'
import { useNotification } from '../../common'
import type { LogEntry } from '../../../types/monitoring'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
)

// Enhanced log interfaces
interface LogPattern {
  id: string
  pattern: string
  regex: string
  count: number
  percentage: number
  first_seen: string
  last_seen: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  category: string
  similar_logs: string[]
  trend: 'increasing' | 'decreasing' | 'stable'
}

interface LogCorrelation {
  id: string
  event_a: string
  event_b: string
  correlation_strength: number
  time_window: number
  occurrences: number
  pattern_type: 'sequence' | 'concurrent' | 'causal'
}

interface LogAnomalies {
  id: string
  timestamp: string
  anomaly_type: 'frequency' | 'pattern' | 'value' | 'sequence'
  severity: number
  description: string
  affected_logs: string[]
  context: Record<string, any>
}

interface LogAnalysisResult {
  patterns: LogPattern[]
  correlations: LogCorrelation[]
  anomalies: LogAnomalies[]
  insights: {
    total_entries: number
    unique_sources: number
    error_rate: number
    performance_issues: number
    security_events: number
    trend_analysis: Record<string, number>
  }
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} role="tabpanel">
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
)

const AdvancedLogAnalyzer: React.FC = () => {
  const { showNotification } = useNotification()
  const [currentTab, setCurrentTab] = useState(0)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [analysisResult, setAnalysisResult] = useState<LogAnalysisResult | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [timeRange, setTimeRange] = useState('24h')
  const [analysisDepth, setAnalysisDepth] = useState(2) // 1: Basic, 2: Advanced, 3: Deep
  const [autoAnalysis, setAutoAnalysis] = useState(true)
  const [selectedPattern, setSelectedPattern] = useState<LogPattern | null>(null)
  const [patternDetailOpen, setPatternDetailOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [levelFilter, setLevelFilter] = useState<string[]>([])
  const [sourceFilter, setSourceFilter] = useState<string[]>([])
  const intervalRef = useRef<NodeJS.Timeout>()

  // Mock data generation for development
  const generateMockLogs = (count: number): LogEntry[] => {
    const levels: LogEntry['level'][] = ['debug', 'info', 'warning', 'error', 'critical']
    const categories: LogEntry['category'][] = ['system', 'drone', 'vision', 'api', 'security', 'performance']
    const sources = ['api-server', 'drone-controller', 'vision-processor', 'web-frontend', 'database', 'auth-service']
    const patterns = [
      'Database connection timeout',
      'Vision model inference completed',
      'Drone battery level critical',
      'User authentication failed',
      'API rate limit exceeded',
      'Memory usage warning',
      'Network latency spike detected',
      'Cache miss ratio high',
      'SSL certificate expiring',
      'Backup process completed'
    ]
    
    return Array.from({ length: count }, (_, i) => {
      const basePattern = patterns[Math.floor(Math.random() * patterns.length)]
      const level = levels[Math.floor(Math.random() * levels.length)]
      const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
      
      return {
        id: `log-${i}`,
        timestamp,
        level,
        source: sources[Math.floor(Math.random() * sources.length)],
        category: categories[Math.floor(Math.random() * categories.length)],
        message: `${basePattern} - ID: ${i + 1000}`,
        details: Math.random() > 0.7 ? { 
          request_id: `req-${i}`,
          user_id: `user-${Math.floor(Math.random() * 100)}`,
          duration: Math.floor(Math.random() * 5000),
          status_code: Math.random() > 0.8 ? 500 : 200
        } : undefined,
        user_id: Math.random() > 0.5 ? `user-${Math.floor(Math.random() * 10)}` : undefined,
        session_id: `session-${Math.floor(Math.random() * 100)}`,
        request_id: `req-${Math.floor(Math.random() * 1000)}`,
        context: { 
          component: sources[Math.floor(Math.random() * sources.length)], 
          action: 'sample-action',
          environment: 'production'
        }
      }
    })
  }

  const generateMockAnalysisResult = (logs: LogEntry[]): LogAnalysisResult => {
    const patterns: LogPattern[] = [
      {
        id: 'pattern-1',
        pattern: 'Database connection timeout',
        regex: '/Database.*timeout/i',
        count: 45,
        percentage: 12.3,
        first_seen: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        last_seen: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        severity: 'high',
        category: 'database',
        similar_logs: ['db-timeout-001', 'db-timeout-002'],
        trend: 'increasing'
      },
      {
        id: 'pattern-2',
        pattern: 'Authentication failure',
        regex: '/auth.*fail/i',
        count: 23,
        percentage: 6.2,
        first_seen: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        last_seen: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        severity: 'critical',
        category: 'security',
        similar_logs: ['auth-fail-001', 'auth-fail-002'],
        trend: 'stable'
      },
      {
        id: 'pattern-3',
        pattern: 'Memory usage warning',
        regex: '/memory.*warning/i',
        count: 18,
        percentage: 4.9,
        first_seen: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        last_seen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        severity: 'medium',
        category: 'performance',
        similar_logs: ['mem-warn-001', 'mem-warn-002'],
        trend: 'decreasing'
      }
    ]

    const correlations: LogCorrelation[] = [
      {
        id: 'corr-1',
        event_a: 'Database connection timeout',
        event_b: 'API response delay',
        correlation_strength: 0.87,
        time_window: 300, // 5 minutes
        occurrences: 15,
        pattern_type: 'causal'
      },
      {
        id: 'corr-2',
        event_a: 'Memory usage warning',
        event_b: 'Performance degradation',
        correlation_strength: 0.73,
        time_window: 600, // 10 minutes
        occurrences: 8,
        pattern_type: 'concurrent'
      }
    ]

    const anomalies: LogAnomalies[] = [
      {
        id: 'anom-1',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        anomaly_type: 'frequency',
        severity: 0.85,
        description: 'Unusual spike in error logs detected',
        affected_logs: ['log-1', 'log-2', 'log-3'],
        context: { spike_factor: 3.2, normal_rate: 0.5 }
      },
      {
        id: 'anom-2',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        anomaly_type: 'pattern',
        severity: 0.67,
        description: 'New error pattern not seen before',
        affected_logs: ['log-4', 'log-5'],
        context: { pattern: 'SSL handshake failure', first_occurrence: true }
      }
    ]

    const insights = {
      total_entries: logs.length,
      unique_sources: new Set(logs.map(log => log.source)).size,
      error_rate: logs.filter(log => log.level === 'error' || log.level === 'critical').length / logs.length * 100,
      performance_issues: logs.filter(log => log.category === 'performance').length,
      security_events: logs.filter(log => log.category === 'security').length,
      trend_analysis: {
        'last_hour': Math.floor(Math.random() * 50),
        'last_6h': Math.floor(Math.random() * 200),
        'last_24h': Math.floor(Math.random() * 800),
      }
    }

    return { patterns, correlations, anomalies, insights }
  }

  const fetchLogs = async () => {
    try {
      setIsLoading(true)
      // Mock API call - replace with actual implementation
      const mockLogs = generateMockLogs(500)
      setLogs(mockLogs)
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to fetch logs:', error)
      showNotification('ログデータの取得に失敗しました', 'error')
      setIsLoading(false)
    }
  }

  const runAnalysis = async () => {
    if (logs.length === 0) return

    try {
      setIsAnalyzing(true)
      showNotification('ログ分析を開始します...', 'info')
      
      // Simulate analysis delay based on depth
      const analysisDelay = analysisDepth * 2000
      await new Promise(resolve => setTimeout(resolve, analysisDelay))
      
      // Mock analysis - replace with actual implementation
      const result = generateMockAnalysisResult(logs)
      setAnalysisResult(result)
      
      showNotification(`分析完了: ${result.patterns.length}個のパターンを検出`, 'success')
      setIsAnalyzing(false)
    } catch (error) {
      console.error('Analysis failed:', error)
      showNotification('ログ分析に失敗しました', 'error')
      setIsAnalyzing(false)
    }
  }

  const logTrendData = useMemo(() => {
    if (!logs.length) return null

    const last24Hours = Array.from({ length: 24 }, (_, i) => {
      const hour = startOfHour(subHours(new Date(), 23 - i))
      const hourLogs = logs.filter(log => {
        const logHour = startOfHour(new Date(log.timestamp))
        return logHour.getTime() === hour.getTime()
      })
      return {
        hour: format(hour, 'HH:mm', { locale: ja }),
        count: hourLogs.length,
        errors: hourLogs.filter(log => log.level === 'error' || log.level === 'critical').length,
        warnings: hourLogs.filter(log => log.level === 'warning').length,
      }
    })

    return {
      labels: last24Hours.map(d => d.hour),
      datasets: [
        {
          label: '総ログ数',
          data: last24Hours.map(d => d.count),
          borderColor: '#2196f3',
          backgroundColor: '#2196f320',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
        },
        {
          label: 'エラー',
          data: last24Hours.map(d => d.errors),
          borderColor: '#f44336',
          backgroundColor: '#f4433620',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
        },
        {
          label: '警告',
          data: last24Hours.map(d => d.warnings),
          borderColor: '#ff9800',
          backgroundColor: '#ff980020',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
        },
      ],
    }
  }, [logs])

  const severityDistribution = useMemo(() => {
    if (!analysisResult) return null

    const severityCounts = analysisResult.patterns.reduce((acc, pattern) => {
      acc[pattern.severity] = (acc[pattern.severity] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      labels: Object.keys(severityCounts),
      datasets: [
        {
          data: Object.values(severityCounts),
          backgroundColor: ['#f44336', '#ff9800', '#ffeb3b', '#4caf50'],
          borderWidth: 1,
        },
      ],
    }
  }, [analysisResult])

  const getTrendIcon = (trend: LogPattern['trend']) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp color="error" fontSize="small" />
      case 'decreasing':
        return <TrendingDown color="success" fontSize="small" />
      default:
        return <Remove color="disabled" fontSize="small" />
    }
  }

  const getSeverityColor = (severity: LogPattern['severity']) => {
    switch (severity) {
      case 'critical':
        return 'error'
      case 'high':
        return 'warning'
      case 'medium':
        return 'info'
      default:
        return 'default'
    }
  }

  const handlePatternClick = (pattern: LogPattern) => {
    setSelectedPattern(pattern)
    setPatternDetailOpen(true)
  }

  const exportAnalysisResult = () => {
    if (!analysisResult) return

    const exportData = {
      analysis_timestamp: new Date().toISOString(),
      time_range: timeRange,
      analysis_depth: analysisDepth,
      insights: analysisResult.insights,
      patterns: analysisResult.patterns,
      correlations: analysisResult.correlations,
      anomalies: analysisResult.anomalies,
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `log_analysis_${format(new Date(), 'yyyyMMdd_HHmmss')}.json`
    a.click()
    URL.revokeObjectURL(url)

    showNotification('分析結果をエクスポートしました', 'success')
  }

  useEffect(() => {
    fetchLogs()
  }, [timeRange])

  useEffect(() => {
    if (logs.length > 0 && autoAnalysis) {
      runAnalysis()
    }
  }, [logs, analysisDepth, autoAnalysis])

  useEffect(() => {
    if (autoAnalysis) {
      intervalRef.current = setInterval(() => {
        fetchLogs()
      }, 30000) // Refresh every 30 seconds

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
        }
      }
    }
  }, [autoAnalysis])

  if (isLoading) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          高度ログアナライザー
        </Typography>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>
          ログデータを読み込み中...
        </Typography>
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6" component="h2">
          高度ログアナライザー
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>期間</InputLabel>
            <Select
              value={timeRange}
              label="期間"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="1h">1時間</MenuItem>
              <MenuItem value="6h">6時間</MenuItem>
              <MenuItem value="24h">24時間</MenuItem>
              <MenuItem value="7d">7日間</MenuItem>
            </Select>
          </FormControl>
          
          <FormControlLabel
            control={
              <Switch
                checked={autoAnalysis}
                onChange={(e) => setAutoAnalysis(e.target.checked)}
                size="small"
              />
            }
            label="自動分析"
          />

          <Tooltip title="分析実行">
            <IconButton onClick={runAnalysis} disabled={isAnalyzing || logs.length === 0}>
              <Analytics />
            </IconButton>
          </Tooltip>

          <Tooltip title="更新">
            <IconButton onClick={fetchLogs} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>

          <Tooltip title="エクスポート">
            <IconButton onClick={exportAnalysisResult} disabled={!analysisResult}>
              <Download />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Analysis Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            分析設定
          </Typography>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <Typography gutterBottom>分析深度</Typography>
              <Slider
                value={analysisDepth}
                onChange={(e, newValue) => setAnalysisDepth(newValue as number)}
                min={1}
                max={3}
                step={1}
                marks={[
                  { value: 1, label: '基本' },
                  { value: 2, label: '詳細' },
                  { value: 3, label: '深層' },
                ]}
                disabled={isAnalyzing}
              />
            </Grid>
            <Grid item xs={12} md={8}>
              {analysisResult && (
                <Grid container spacing={2}>
                  <Grid item xs={3}>
                    <Typography variant="h6" color="primary.main">
                      {analysisResult.insights.total_entries}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      総ログ数
                    </Typography>
                  </Grid>
                  <Grid item xs={3}>
                    <Typography variant="h6" color="error.main">
                      {analysisResult.patterns.length}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      検出パターン
                    </Typography>
                  </Grid>
                  <Grid item xs={3}>
                    <Typography variant="h6" color="warning.main">
                      {analysisResult.anomalies.length}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      異常検知
                    </Typography>
                  </Grid>
                  <Grid item xs={3}>
                    <Typography variant="h6" color="success.main">
                      {analysisResult.insights.error_rate.toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      エラー率
                    </Typography>
                  </Grid>
                </Grid>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
          <Tab icon={<Timeline />} label="ログ推移" />
          <Tab icon={<Pattern />} label="パターン分析" />
          <Tab icon={<Psychology />} label="異常検知" />
          <Tab icon={<AutoGraph />} label="相関分析" />
        </Tabs>

        <TabPanel value={currentTab} index={0}>
          {logTrendData && (
            <Box>
              <Typography variant="h6" gutterBottom>
                ログ発生推移（24時間）
              </Typography>
              <Box height={400}>
                <Line
                  data={logTrendData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'top' },
                      title: { display: false },
                    },
                    scales: {
                      y: { beginAtZero: true },
                    },
                  }}
                />
              </Box>
            </Box>
          )}
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          {isAnalyzing ? (
            <Box textAlign="center" py={4}>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body1">
                パターン分析中... (深度: {analysisDepth})
              </Typography>
            </Box>
          ) : analysisResult ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                検出されたパターン ({analysisResult.patterns.length}件)
              </Typography>
              <Stack spacing={2}>
                {analysisResult.patterns.map((pattern) => (
                  <Card key={pattern.id} variant="outlined">
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Typography variant="h6">{pattern.pattern}</Typography>
                          <Chip
                            label={pattern.severity}
                            color={getSeverityColor(pattern.severity) as any}
                            size="small"
                          />
                          {getTrendIcon(pattern.trend)}
                        </Box>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip label={`${pattern.count}回`} variant="outlined" />
                          <Chip label={`${pattern.percentage}%`} variant="outlined" />
                          <IconButton size="small" onClick={() => handlePatternClick(pattern)}>
                            <Visibility fontSize="small" />
                          </IconButton>
                        </Box>
                      </Box>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            カテゴリ: {pattern.category}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            最終発生: {format(new Date(pattern.last_seen), 'MM/dd HH:mm', { locale: ja })}
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </Box>
          ) : (
            <Alert severity="info">
              ログパターンの分析を実行してください
            </Alert>
          )}
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          {isAnalyzing ? (
            <Box textAlign="center" py={4}>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body1">
                異常検知分析中...
              </Typography>
            </Box>
          ) : analysisResult ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                検出された異常 ({analysisResult.anomalies.length}件)
              </Typography>
              <Stack spacing={2}>
                {analysisResult.anomalies.map((anomaly) => (
                  <Alert
                    key={anomaly.id}
                    severity={anomaly.severity > 0.7 ? 'error' : anomaly.severity > 0.4 ? 'warning' : 'info'}
                  >
                    <Typography variant="h6" gutterBottom>
                      {anomaly.description}
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      タイプ: {anomaly.anomaly_type} | 深刻度: {(anomaly.severity * 100).toFixed(0)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      検出時刻: {format(new Date(anomaly.timestamp), 'yyyy/MM/dd HH:mm:ss', { locale: ja })}
                    </Typography>
                  </Alert>
                ))}
              </Stack>
            </Box>
          ) : (
            <Alert severity="info">
              異常検知の分析を実行してください
            </Alert>
          )}
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          {isAnalyzing ? (
            <Box textAlign="center" py={4}>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body1">
                相関分析中...
              </Typography>
            </Box>
          ) : analysisResult ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                イベント相関分析 ({analysisResult.correlations.length}件)
              </Typography>
              <Stack spacing={2}>
                {analysisResult.correlations.map((correlation) => (
                  <Card key={correlation.id} variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {correlation.event_a} ⟷ {correlation.event_b}
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            相関強度: <strong>{(correlation.correlation_strength * 100).toFixed(0)}%</strong>
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            パターンタイプ: <strong>{correlation.pattern_type}</strong>
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            時間窓: <strong>{correlation.time_window}秒</strong>
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            発生回数: <strong>{correlation.occurrences}回</strong>
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </Box>
          ) : (
            <Alert severity="info">
              相関分析を実行してください
            </Alert>
          )}
        </TabPanel>
      </Card>

      {/* Pattern Detail Dialog */}
      <Dialog
        open={patternDetailOpen}
        onClose={() => setPatternDetailOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>パターン詳細</DialogTitle>
        <DialogContent>
          {selectedPattern && (
            <Stack spacing={2}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label="パターン"
                    value={selectedPattern.pattern}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={3}>
                  <TextField
                    label="重要度"
                    value={selectedPattern.severity}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={3}>
                  <TextField
                    label="傾向"
                    value={selectedPattern.trend}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
              </Grid>

              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <TextField
                    label="発生回数"
                    value={selectedPattern.count}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    label="割合"
                    value={`${selectedPattern.percentage}%`}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    label="カテゴリ"
                    value={selectedPattern.category}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
              </Grid>

              <TextField
                label="正規表現"
                value={selectedPattern.regex}
                fullWidth
                variant="outlined"
                InputProps={{ readOnly: true }}
              />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label="初回発生"
                    value={format(new Date(selectedPattern.first_seen), 'yyyy/MM/dd HH:mm:ss', { locale: ja })}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="最終発生"
                    value={format(new Date(selectedPattern.last_seen), 'yyyy/MM/dd HH:mm:ss', { locale: ja })}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
              </Grid>

              <TextField
                label="類似ログ"
                value={selectedPattern.similar_logs.join(', ')}
                fullWidth
                multiline
                rows={2}
                variant="outlined"
                InputProps={{ readOnly: true }}
              />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPatternDetailOpen(false)}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default AdvancedLogAnalyzer