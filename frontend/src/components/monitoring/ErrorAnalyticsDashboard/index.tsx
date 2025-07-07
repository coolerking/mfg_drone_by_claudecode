/**
 * Error Analytics Dashboard Component
 * Provides comprehensive error tracking, analysis, and visualization
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
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import {
  Error as ErrorIcon,
  Warning,
  TrendingUp,
  TrendingDown,
  Refresh,
  FilterList,
  Download,
  Visibility,
  ExpandMore,
  BugReport,
  Security,
  Api,
  Speed,
  Memory,
  Psychology,
  Search,
  Timeline,
  Analytics,
  Settings,
  Feedback
} from '@mui/icons-material'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
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
  ArcElement,
  Filler
} from 'chart.js'
import { format, subDays, startOfDay } from 'date-fns'
import { ja } from 'date-fns/locale'
import { sentryService } from '../../../utils/sentry'
import { useNotification } from '../../common'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  Filler
)

// Error data interfaces
interface ErrorEvent {
  id: string
  timestamp: string
  message: string
  type: string
  level: 'error' | 'warning' | 'info' | 'debug'
  component: string
  user_id?: string
  session_id: string
  url: string
  stack_trace?: string
  context?: Record<string, any>
  tags?: Record<string, string>
  count: number
  first_seen: string
  last_seen: string
  status: 'unresolved' | 'resolved' | 'ignored'
}

interface ErrorMetrics {
  total_errors: number
  total_users_affected: number
  error_rate: number
  resolution_rate: number
  avg_time_to_resolve: number
  trend_24h: number
  trend_7d: number
}

interface ErrorPattern {
  pattern: string
  count: number
  percentage: number
  components: string[]
  first_seen: string
  last_seen: string
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

const ErrorAnalyticsDashboard: React.FC = () => {
  const { showNotification } = useNotification()
  const [currentTab, setCurrentTab] = useState(0)
  const [errors, setErrors] = useState<ErrorEvent[]>([])
  const [metrics, setMetrics] = useState<ErrorMetrics | null>(null)
  const [patterns, setPatterns] = useState<ErrorPattern[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('24h')
  const [levelFilter, setLevelFilter] = useState<string[]>([])
  const [componentFilter, setComponentFilter] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedError, setSelectedError] = useState<ErrorEvent | null>(null)
  const [errorDetailOpen, setErrorDetailOpen] = useState(false)

  // Mock data generation (replace with actual API calls)
  const generateMockErrors = (): ErrorEvent[] => {
    const components = ['drone', 'vision', 'api', 'ui', 'websocket']
    const types = ['TypeError', 'NetworkError', 'ReferenceError', 'SyntaxError', 'CustomError']
    const levels: ErrorEvent['level'][] = ['error', 'warning', 'info', 'debug']
    
    return Array.from({ length: 50 }, (_, i) => ({
      id: `error-${i}`,
      timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      message: `Error message ${i + 1}: Something went wrong in the system`,
      type: types[Math.floor(Math.random() * types.length)],
      level: levels[Math.floor(Math.random() * levels.length)],
      component: components[Math.floor(Math.random() * components.length)],
      user_id: Math.random() > 0.5 ? `user-${Math.floor(Math.random() * 10)}` : undefined,
      session_id: `session-${Math.floor(Math.random() * 100)}`,
      url: `https://drone-system.com/page-${Math.floor(Math.random() * 10)}`,
      stack_trace: Math.random() > 0.7 ? `Error stack trace for error ${i}` : undefined,
      context: { action: 'test-action', component: 'test-component' },
      tags: { environment: 'production', version: '1.0.0' },
      count: Math.floor(Math.random() * 20) + 1,
      first_seen: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      last_seen: new Date(Date.now() - Math.random() * 1 * 24 * 60 * 60 * 1000).toISOString(),
      status: ['unresolved', 'resolved', 'ignored'][Math.floor(Math.random() * 3)] as any,
    }))
  }

  const generateMockMetrics = (): ErrorMetrics => ({
    total_errors: 127,
    total_users_affected: 23,
    error_rate: 2.3,
    resolution_rate: 78.5,
    avg_time_to_resolve: 4.2,
    trend_24h: -12.5,
    trend_7d: 8.7,
  })

  const generateMockPatterns = (): ErrorPattern[] => [
    {
      pattern: 'Network timeout in drone communication',
      count: 23,
      percentage: 18.1,
      components: ['drone', 'websocket'],
      first_seen: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      last_seen: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    },
    {
      pattern: 'Vision model inference failure',
      count: 18,
      percentage: 14.2,
      components: ['vision', 'api'],
      first_seen: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      last_seen: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    },
    {
      pattern: 'UI component render error',
      count: 15,
      percentage: 11.8,
      components: ['ui'],
      first_seen: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      last_seen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
  ]

  const fetchErrorData = async () => {
    try {
      setIsLoading(true)
      
      // Mock API calls - replace with actual Sentry API integration
      const [errorData, metricsData, patternsData] = await Promise.all([
        Promise.resolve(generateMockErrors()),
        Promise.resolve(generateMockMetrics()),
        Promise.resolve(generateMockPatterns()),
      ])
      
      setErrors(errorData)
      setMetrics(metricsData)
      setPatterns(patternsData)
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to fetch error data:', error)
      showNotification('エラーデータの取得に失敗しました', 'error')
      setIsLoading(false)
    }
  }

  const filteredErrors = useMemo(() => {
    let filtered = errors

    // Level filter
    if (levelFilter.length > 0) {
      filtered = filtered.filter(error => levelFilter.includes(error.level))
    }

    // Component filter
    if (componentFilter.length > 0) {
      filtered = filtered.filter(error => componentFilter.includes(error.component))
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(error =>
        error.message.toLowerCase().includes(query) ||
        error.type.toLowerCase().includes(query) ||
        error.component.toLowerCase().includes(query)
      )
    }

    return filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  }, [errors, levelFilter, componentFilter, searchQuery])

  const errorTrendData = useMemo(() => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = startOfDay(subDays(new Date(), 6 - i))
      const dayErrors = errors.filter(error => {
        const errorDate = startOfDay(new Date(error.timestamp))
        return errorDate.getTime() === date.getTime()
      })
      return {
        date: format(date, 'MM/dd', { locale: ja }),
        count: dayErrors.length,
      }
    })

    return {
      labels: last7Days.map(d => d.date),
      datasets: [
        {
          label: 'エラー発生数',
          data: last7Days.map(d => d.count),
          borderColor: '#f44336',
          backgroundColor: '#f4433620',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
        },
      ],
    }
  }, [errors])

  const componentErrorData = useMemo(() => {
    const componentCounts = errors.reduce((acc, error) => {
      acc[error.component] = (acc[error.component] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      labels: Object.keys(componentCounts),
      datasets: [
        {
          data: Object.values(componentCounts),
          backgroundColor: [
            '#f44336',
            '#ff9800',
            '#ffeb3b',
            '#4caf50',
            '#2196f3',
            '#9c27b0',
          ],
          borderWidth: 1,
        },
      ],
    }
  }, [errors])

  const getErrorIcon = (level: ErrorEvent['level']) => {
    switch (level) {
      case 'error':
        return <ErrorIcon color="error" fontSize="small" />
      case 'warning':
        return <Warning color="warning" fontSize="small" />
      default:
        return <BugReport color="action" fontSize="small" />
    }
  }

  const getComponentIcon = (component: string) => {
    switch (component) {
      case 'drone':
        return <Speed fontSize="small" />
      case 'vision':
        return <Psychology fontSize="small" />
      case 'api':
        return <Api fontSize="small" />
      case 'security':
        return <Security fontSize="small" />
      default:
        return <Memory fontSize="small" />
    }
  }

  const handleErrorClick = (error: ErrorEvent) => {
    setSelectedError(error)
    setErrorDetailOpen(true)
  }

  const handleExportData = () => {
    const csvContent = filteredErrors.map(error => [
      error.timestamp,
      error.level,
      error.component,
      error.type,
      error.message.replace(/"/g, '""'),
      error.user_id || '',
      error.count,
    ].join(',')).join('\n')

    const header = 'Timestamp,Level,Component,Type,Message,User ID,Count\n'
    const blob = new Blob([header + csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `error_analytics_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`
    a.click()
    URL.revokeObjectURL(url)

    showNotification('エラーデータをエクスポートしました', 'success')
  }

  useEffect(() => {
    fetchErrorData()
  }, [timeRange])

  if (isLoading || !metrics) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          エラー分析ダッシュボード
        </Typography>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>
          エラーデータを読み込み中...
        </Typography>
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6" component="h2">
          エラー分析ダッシュボード
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
              <MenuItem value="24h">24時間</MenuItem>
              <MenuItem value="7d">7日間</MenuItem>
              <MenuItem value="30d">30日間</MenuItem>
            </Select>
          </FormControl>
          <Tooltip title="更新">
            <IconButton onClick={fetchErrorData} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="エクスポート">
            <IconButton onClick={handleExportData}>
              <Download />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Metrics Overview */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                総エラー数
              </Typography>
              <Typography variant="h4" component="div" color="error.main">
                {metrics.total_errors}
              </Typography>
              <Box display="flex" alignItems="center" gap={1}>
                {metrics.trend_24h < 0 ? (
                  <TrendingDown color="success" fontSize="small" />
                ) : (
                  <TrendingUp color="error" fontSize="small" />
                )}
                <Typography variant="caption" color={metrics.trend_24h < 0 ? 'success.main' : 'error.main'}>
                  {Math.abs(metrics.trend_24h)}% (24h)
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                影響ユーザー
              </Typography>
              <Typography variant="h4" component="div" color="warning.main">
                {metrics.total_users_affected}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                ユニークユーザー
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                エラー率
              </Typography>
              <Typography variant="h4" component="div" color="error.main">
                {metrics.error_rate}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                全リクエスト中
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                解決率
              </Typography>
              <Typography variant="h4" component="div" color="success.main">
                {metrics.resolution_rate}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                過去30日間
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                平均解決時間
              </Typography>
              <Typography variant="h4" component="div" color="info.main">
                {metrics.avg_time_to_resolve}h
              </Typography>
              <Typography variant="caption" color="text.secondary">
                時間
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                週間傾向
              </Typography>
              <Typography variant="h4" component="div" color={metrics.trend_7d < 0 ? 'success.main' : 'error.main'}>
                {metrics.trend_7d > 0 ? '+' : ''}{metrics.trend_7d}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                7日間比較
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Card>
        <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
          <Tab icon={<Timeline />} label="エラー推移" />
          <Tab icon={<Analytics />} label="エラー一覧" />
          <Tab icon={<BugReport />} label="パターン分析" />
          <Tab icon={<Settings />} label="設定" />
        </Tabs>

        <TabPanel value={currentTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Typography variant="h6" gutterBottom>
                エラー発生推移（7日間）
              </Typography>
              <Box height={400}>
                <Line
                  data={errorTrendData}
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
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                コンポーネント別エラー
              </Typography>
              <Box height={400}>
                <Doughnut
                  data={componentErrorData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' },
                    },
                  }}
                />
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          {/* Filters */}
          <Box mb={3}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="エラーを検索..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: <Search color="action" />
                  }}
                />
              </Grid>
              <Grid item xs={6} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>レベル</InputLabel>
                  <Select
                    multiple
                    value={levelFilter}
                    label="レベル"
                    onChange={(e) => setLevelFilter(e.target.value as string[])}
                  >
                    <MenuItem value="error">エラー</MenuItem>
                    <MenuItem value="warning">警告</MenuItem>
                    <MenuItem value="info">情報</MenuItem>
                    <MenuItem value="debug">デバッグ</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>コンポーネント</InputLabel>
                  <Select
                    multiple
                    value={componentFilter}
                    label="コンポーネント"
                    onChange={(e) => setComponentFilter(e.target.value as string[])}
                  >
                    <MenuItem value="drone">ドローン</MenuItem>
                    <MenuItem value="vision">ビジョン</MenuItem>
                    <MenuItem value="api">API</MenuItem>
                    <MenuItem value="ui">UI</MenuItem>
                    <MenuItem value="websocket">WebSocket</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>

          {/* Error List */}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>レベル</TableCell>
                  <TableCell>タイムスタンプ</TableCell>
                  <TableCell>コンポーネント</TableCell>
                  <TableCell>タイプ</TableCell>
                  <TableCell>メッセージ</TableCell>
                  <TableCell>発生回数</TableCell>
                  <TableCell>ステータス</TableCell>
                  <TableCell>詳細</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredErrors.slice(0, 20).map((error) => (
                  <TableRow key={error.id} hover>
                    <TableCell>
                      <Chip
                        icon={getErrorIcon(error.level)}
                        label={error.level}
                        size="small"
                        color={error.level === 'error' ? 'error' : error.level === 'warning' ? 'warning' : 'default'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {format(new Date(error.timestamp), 'MM/dd HH:mm', { locale: ja })}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getComponentIcon(error.component)}
                        label={error.component}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{error.type}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          maxWidth: 300,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {error.message}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Badge badgeContent={error.count} color="error">
                        <Typography variant="body2">{error.count}</Typography>
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={error.status}
                        size="small"
                        color={error.status === 'resolved' ? 'success' : error.status === 'ignored' ? 'default' : 'error'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleErrorClick(error)}>
                        <Visibility fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <Typography variant="h6" gutterBottom>
            エラーパターン分析
          </Typography>
          <Stack spacing={2}>
            {patterns.map((pattern, index) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center" gap={2} width="100%">
                    <Typography variant="body1" sx={{ flexGrow: 1 }}>
                      {pattern.pattern}
                    </Typography>
                    <Chip label={`${pattern.count}回`} color="error" size="small" />
                    <Chip label={`${pattern.percentage}%`} color="default" size="small" />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        影響コンポーネント
                      </Typography>
                      <Stack direction="row" spacing={1}>
                        {pattern.components.map((component) => (
                          <Chip
                            key={component}
                            icon={getComponentIcon(component)}
                            label={component}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Stack>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        期間
                      </Typography>
                      <Typography variant="body2">
                        {format(new Date(pattern.first_seen), 'yyyy/MM/dd HH:mm', { locale: ja })} - {' '}
                        {format(new Date(pattern.last_seen), 'yyyy/MM/dd HH:mm', { locale: ja })}
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <Typography variant="h6" gutterBottom>
            エラー追跡設定
          </Typography>
          <Stack spacing={3}>
            <Alert severity="info">
              Sentryとの統合設定を行い、エラーの自動収集と分析を設定できます。
            </Alert>
            
            <Button
              variant="outlined"
              startIcon={<Feedback />}
              onClick={() => sentryService.showUserFeedback()}
            >
              ユーザーフィードバックダイアログを表示
            </Button>

            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={handleExportData}
            >
              エラーデータをエクスポート
            </Button>
          </Stack>
        </TabPanel>
      </Card>

      {/* Error Detail Dialog */}
      <Dialog
        open={errorDetailOpen}
        onClose={() => setErrorDetailOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>エラー詳細</DialogTitle>
        <DialogContent>
          {selectedError && (
            <Stack spacing={2}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label="タイムスタンプ"
                    value={format(new Date(selectedError.timestamp), 'yyyy/MM/dd HH:mm:ss', { locale: ja })}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={3}>
                  <TextField
                    label="レベル"
                    value={selectedError.level}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={3}>
                  <TextField
                    label="コンポーネント"
                    value={selectedError.component}
                    fullWidth
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
              </Grid>

              <TextField
                label="エラータイプ"
                value={selectedError.type}
                fullWidth
                variant="outlined"
                InputProps={{ readOnly: true }}
              />

              <TextField
                label="メッセージ"
                value={selectedError.message}
                fullWidth
                multiline
                rows={3}
                variant="outlined"
                InputProps={{ readOnly: true }}
              />

              {selectedError.stack_trace && (
                <TextField
                  label="スタックトレース"
                  value={selectedError.stack_trace}
                  fullWidth
                  multiline
                  rows={6}
                  variant="outlined"
                  InputProps={{ readOnly: true }}
                />
              )}

              {selectedError.context && (
                <TextField
                  label="コンテキスト"
                  value={JSON.stringify(selectedError.context, null, 2)}
                  fullWidth
                  multiline
                  rows={4}
                  variant="outlined"
                  InputProps={{ readOnly: true }}
                />
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setErrorDetailOpen(false)}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ErrorAnalyticsDashboard