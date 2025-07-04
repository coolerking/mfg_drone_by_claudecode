import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  Tooltip,
  Fab,
  Menu,
  ListItemIcon,
  ListItemText
} from '@mui/material'
import {
  Add,
  Edit,
  Delete,
  Refresh,
  Settings,
  FullscreenExit,
  Fullscreen,
  DragIndicator,
  Timeline,
  Notifications,
  Visibility,
  Speed,
  Storage,
  Security,
  BugReport,
  TrendingUp,
  Assessment,
  MonitorHeart
} from '@mui/icons-material'
import { Line, Doughnut, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  BarElement
} from 'chart.js'
import SystemMetrics from '../SystemMetrics'
import AlertPanel from '../AlertPanel'
import LogViewer from '../LogViewer'
import { dashboardApi } from '../../../services/api/dashboardApi'
import type { MonitoringWidget, MetricData } from '../../../types/monitoring'
import { useNotification } from '../../common'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  BarElement
)

interface MonitoringDashboardProps {
  defaultLayout?: MonitoringWidget[]
  editable?: boolean
  refreshInterval?: number
}

interface AddWidgetDialogProps {
  open: boolean
  onClose: () => void
  onAdd: (widget: Omit<MonitoringWidget, 'id' | 'created_at' | 'updated_at'>) => void
}

const AddWidgetDialog: React.FC<AddWidgetDialogProps> = ({ open, onClose, onAdd }) => {
  const [widgetType, setWidgetType] = useState<MonitoringWidget['type']>('metric_chart')
  const [title, setTitle] = useState('')
  const [config, setConfig] = useState<any>({})

  const handleAdd = () => {
    if (!title) return

    onAdd({
      type: widgetType,
      title,
      config,
      position: { x: 0, y: 0 },
      size: { width: 4, height: 3 }
    })

    onClose()
    setTitle('')
    setConfig({})
  }

  const widgetTypes = [
    { value: 'metric_chart', label: 'メトリクスチャート', icon: <Timeline /> },
    { value: 'alert_panel', label: 'アラートパネル', icon: <Notifications /> },
    { value: 'health_status', label: 'ヘルス状態', icon: <MonitorHeart /> },
    { value: 'activity_feed', label: 'アクティビティフィード', icon: <Assessment /> },
    { value: 'log_stream', label: 'ログストリーム', icon: <BugReport /> }
  ]

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>ウィジェットを追加</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>ウィジェットタイプ</InputLabel>
                <Select
                  value={widgetType}
                  label="ウィジェットタイプ"
                  onChange={(e) => setWidgetType(e.target.value as MonitoringWidget['type'])}
                >
                  {widgetTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      <Box display="flex" alignItems="center" gap={1}>
                        {type.icon}
                        {type.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="ウィジェットタイトル"
                fullWidth
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </Grid>

            {widgetType === 'metric_chart' && (
              <>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>メトリクス</InputLabel>
                    <Select
                      value={config.metric || ''}
                      label="メトリクス"
                      onChange={(e) => setConfig(prev => ({ ...prev, metric: e.target.value }))}
                    >
                      <MenuItem value="cpu_usage">CPU使用率</MenuItem>
                      <MenuItem value="memory_usage">メモリ使用率</MenuItem>
                      <MenuItem value="disk_usage">ディスク使用率</MenuItem>
                      <MenuItem value="network_usage">ネットワーク使用量</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>チャートタイプ</InputLabel>
                    <Select
                      value={config.chart_type || 'line'}
                      label="チャートタイプ"
                      onChange={(e) => setConfig(prev => ({ ...prev, chart_type: e.target.value }))}
                    >
                      <MenuItem value="line">ライン</MenuItem>
                      <MenuItem value="area">エリア</MenuItem>
                      <MenuItem value="bar">バー</MenuItem>
                      <MenuItem value="doughnut">ドーナツ</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>時間範囲</InputLabel>
                    <Select
                      value={config.time_range || '1h'}
                      label="時間範囲"
                      onChange={(e) => setConfig(prev => ({ ...prev, time_range: e.target.value }))}
                    >
                      <MenuItem value="5m">5分</MenuItem>
                      <MenuItem value="15m">15分</MenuItem>
                      <MenuItem value="1h">1時間</MenuItem>
                      <MenuItem value="6h">6時間</MenuItem>
                      <MenuItem value="24h">24時間</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </>
            )}

            {(widgetType === 'alert_panel' || widgetType === 'log_stream') && (
              <Grid item xs={12}>
                <TextField
                  label="最大表示件数"
                  type="number"
                  fullWidth
                  value={config.max_items || 10}
                  onChange={(e) => setConfig(prev => ({ ...prev, max_items: parseInt(e.target.value) }))}
                />
              </Grid>
            )}
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>キャンセル</Button>
        <Button onClick={handleAdd} variant="contained" disabled={!title}>
          追加
        </Button>
      </DialogActions>
    </Dialog>
  )
}

interface WidgetProps {
  widget: MonitoringWidget
  onEdit?: (widget: MonitoringWidget) => void
  onDelete?: (widgetId: string) => void
  editable?: boolean
}

const WidgetComponent: React.FC<WidgetProps> = ({ widget, onEdit, onDelete, editable = false }) => {
  const [fullscreen, setFullscreen] = useState(false)
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWidgetData()
  }, [widget])

  const loadWidgetData = async () => {
    setLoading(true)
    try {
      switch (widget.type) {
        case 'metric_chart':
          // Mock metrics data
          const mockData = {
            labels: Array.from({ length: 12 }, (_, i) => `${i * 5}分前`),
            datasets: [{
              label: widget.config.metric || 'Metric',
              data: Array.from({ length: 12 }, () => Math.random() * 100),
              borderColor: '#1976d2',
              backgroundColor: 'rgba(25, 118, 210, 0.1)',
              fill: widget.config.chart_type === 'area'
            }]
          }
          setData(mockData)
          break
        default:
          setData(null)
      }
    } catch (error) {
      console.error('Failed to load widget data:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderWidgetContent = () => {
    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height={200}>
          <Typography>読み込み中...</Typography>
        </Box>
      )
    }

    switch (widget.type) {
      case 'metric_chart':
        if (!data) return <Typography>データがありません</Typography>
        
        const chartOptions = {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            title: { display: true, text: widget.title }
          },
          scales: {
            y: { beginAtZero: true, max: 100 }
          }
        }

        switch (widget.config.chart_type) {
          case 'doughnut':
            return (
              <Box height={250}>
                <Doughnut
                  data={{
                    labels: ['使用中', '空き'],
                    datasets: [{
                      data: [data.datasets[0].data[0], 100 - data.datasets[0].data[0]],
                      backgroundColor: ['#1976d2', '#e0e0e0']
                    }]
                  }}
                  options={{ responsive: true, maintainAspectRatio: false }}
                />
              </Box>
            )
          case 'bar':
            return (
              <Box height={250}>
                <Bar data={data} options={chartOptions} />
              </Box>
            )
          default:
            return (
              <Box height={250}>
                <Line data={data} options={chartOptions} />
              </Box>
            )
        }

      case 'alert_panel':
        return <AlertPanel compact maxAlerts={widget.config.max_items || 10} />

      case 'health_status':
        return (
          <Box>
            <Box display="flex" justifyContent="center" mb={2}>
              <Chip label="システム正常" color="success" size="large" />
            </Box>
            <Grid container spacing={1}>
              <Grid item xs={6}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">98%</Typography>
                  <Typography variant="caption">稼働率</Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary.main">42</Typography>
                  <Typography variant="caption">アクティブサービス</Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )

      case 'activity_feed':
        return (
          <Box>
            {Array.from({ length: widget.config.max_items || 5 }, (_, i) => (
              <Box key={i} display="flex" alignItems="center" gap={1} mb={1}>
                <Chip size="small" label={`アクティビティ ${i + 1}`} />
                <Typography variant="body2" color="text.secondary">
                  {new Date(Date.now() - i * 60000).toLocaleTimeString()}
                </Typography>
              </Box>
            ))}
          </Box>
        )

      case 'log_stream':
        return <LogViewer compact maxLogs={widget.config.max_items || 20} />

      default:
        return <Typography>未対応のウィジェットタイプ</Typography>
    }
  }

  return (
    <>
      <Card sx={{ height: '100%', position: 'relative' }}>
        {editable && (
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              display: 'flex',
              gap: 0.5,
              zIndex: 1
            }}
          >
            <IconButton size="small" onClick={() => setFullscreen(true)}>
              <Fullscreen fontSize="small" />
            </IconButton>
            <IconButton size="small" onClick={() => onEdit?.(widget)}>
              <Edit fontSize="small" />
            </IconButton>
            <IconButton size="small" onClick={() => onDelete?.(widget.id)} color="error">
              <Delete fontSize="small" />
            </IconButton>
          </Box>
        )}
        
        <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Typography variant="h6" gutterBottom noWrap>
            {widget.title}
          </Typography>
          <Box flexGrow={1}>
            {renderWidgetContent()}
          </Box>
        </CardContent>
      </Card>

      <Dialog
        open={fullscreen}
        onClose={() => setFullscreen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{ sx: { height: '80vh' } }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="between" alignItems="center">
            {widget.title}
            <IconButton onClick={() => setFullscreen(false)}>
              <FullscreenExit />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {renderWidgetContent()}
        </DialogContent>
      </Dialog>
    </>
  )
}

export const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({
  defaultLayout = [],
  editable = true,
  refreshInterval = 30000
}) => {
  const { showNotification } = useNotification()
  const [widgets, setWidgets] = useState<MonitoringWidget[]>(defaultLayout)
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [editMode, setEditMode] = useState(false)

  useEffect(() => {
    // Load user's dashboard layout
    loadDashboardLayout()
  }, [])

  const loadDashboardLayout = async () => {
    try {
      // Mock loading dashboard layout
      const mockWidgets: MonitoringWidget[] = [
        {
          id: '1',
          type: 'metric_chart',
          title: 'CPU使用率',
          config: { metric: 'cpu_usage', chart_type: 'line', time_range: '1h' },
          position: { x: 0, y: 0 },
          size: { width: 6, height: 3 },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: '2',
          type: 'metric_chart',
          title: 'メモリ使用率',
          config: { metric: 'memory_usage', chart_type: 'doughnut', time_range: '1h' },
          position: { x: 6, y: 0 },
          size: { width: 6, height: 3 },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: '3',
          type: 'health_status',
          title: 'システム状態',
          config: {},
          position: { x: 0, y: 3 },
          size: { width: 4, height: 3 },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: '4',
          type: 'alert_panel',
          title: '最新アラート',
          config: { max_items: 5 },
          position: { x: 4, y: 3 },
          size: { width: 8, height: 3 },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]
      setWidgets(mockWidgets)
    } catch (error) {
      console.error('Failed to load dashboard layout:', error)
      showNotification('ダッシュボードレイアウトの読み込みに失敗しました', 'error')
    }
  }

  const handleAddWidget = (widgetData: Omit<MonitoringWidget, 'id' | 'created_at' | 'updated_at'>) => {
    const newWidget: MonitoringWidget = {
      ...widgetData,
      id: Date.now().toString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    setWidgets(prev => [...prev, newWidget])
    showNotification('ウィジェットを追加しました', 'success')
  }

  const handleEditWidget = (widget: MonitoringWidget) => {
    // Implementation for editing widget
    showNotification('ウィジェット編集機能は準備中です', 'info')
  }

  const handleDeleteWidget = (widgetId: string) => {
    setWidgets(prev => prev.filter(w => w.id !== widgetId))
    showNotification('ウィジェットを削除しました', 'success')
  }

  const handleSaveLayout = async () => {
    try {
      // Mock saving layout
      await new Promise(resolve => setTimeout(resolve, 1000))
      showNotification('レイアウトを保存しました', 'success')
      setEditMode(false)
    } catch (error) {
      showNotification('レイアウトの保存に失敗しました', 'error')
    }
  }

  const handleResetLayout = () => {
    setWidgets([])
    showNotification('レイアウトをリセットしました', 'info')
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h1">
          監視ダッシュボード
        </Typography>
        
        {editable && (
          <Box display="flex" gap={1}>
            <Button
              variant={editMode ? 'contained' : 'outlined'}
              startIcon={<Edit />}
              onClick={() => setEditMode(!editMode)}
            >
              {editMode ? '編集完了' : '編集モード'}
            </Button>
            
            {editMode && (
              <>
                <Button
                  variant="outlined"
                  onClick={handleSaveLayout}
                >
                  保存
                </Button>
                <Button
                  variant="outlined"
                  color="warning"
                  onClick={handleResetLayout}
                >
                  リセット
                </Button>
              </>
            )}
          </Box>
        )}
      </Box>

      {editMode && (
        <Alert severity="info" sx={{ mb: 2 }}>
          編集モードです。ウィジェットの追加、編集、削除ができます。
        </Alert>
      )}

      <Grid container spacing={3}>
        {widgets.map((widget) => (
          <Grid item xs={12} md={6} lg={widget.size.width} key={widget.id}>
            <WidgetComponent
              widget={widget}
              onEdit={handleEditWidget}
              onDelete={handleDeleteWidget}
              editable={editMode}
            />
          </Grid>
        ))}
        
        {widgets.length === 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 6 }}>
                <Assessment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  ウィジェットがありません
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={3}>
                  ウィジェットを追加してダッシュボードをカスタマイズしましょう
                </Typography>
                {editable && (
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setAddDialogOpen(true)}
                  >
                    ウィジェットを追加
                  </Button>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {editable && (
        <Fab
          color="primary"
          aria-label="add widget"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={() => setAddDialogOpen(true)}
        >
          <Add />
        </Fab>
      )}

      <AddWidgetDialog
        open={addDialogOpen}
        onClose={() => setAddDialogOpen(false)}
        onAdd={handleAddWidget}
      />
    </Box>
  )
}

export default MonitoringDashboard