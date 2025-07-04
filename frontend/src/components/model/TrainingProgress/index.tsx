import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  LinearProgress,
  Grid,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material'
import {
  Pause,
  PlayArrow,
  Stop,
  Refresh,
  TrendingUp,
  TrendingDown,
  Timeline,
  Speed,
  Assessment
} from '@mui/icons-material'
import { useState, useEffect } from 'react'
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
  ChartOptions
} from 'chart.js'
import { useNotification } from '@/hooks/useNotification'
import { modelApi, type TrainingJob } from '@/services/api/modelApi'
import { formatDistanceToNow } from 'date-fns'
import { ja } from 'date-fns/locale'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
)

interface TrainingProgressProps {
  open: boolean
  onClose: () => void
  trainingJob: TrainingJob
  onJobUpdate?: (job: TrainingJob) => void
}

export function TrainingProgress({ 
  open, 
  onClose, 
  trainingJob: initialJob,
  onJobUpdate 
}: TrainingProgressProps) {
  const { showNotification } = useNotification()
  const [trainingJob, setTrainingJob] = useState<TrainingJob>(initialJob)
  const [logs, setLogs] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    setTrainingJob(initialJob)
  }, [initialJob])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null
    
    if (open && autoRefresh && (trainingJob.status === 'running' || trainingJob.status === 'pending')) {
      interval = setInterval(() => {
        refreshJobStatus()
      }, 5000) // Refresh every 5 seconds
    }

    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [open, autoRefresh, trainingJob.status])

  const refreshJobStatus = async () => {
    try {
      const updatedJob = await modelApi.getTrainingJob(trainingJob.id)
      setTrainingJob(updatedJob)
      onJobUpdate?.(updatedJob)
    } catch (error) {
      console.error('Error refreshing job status:', error)
    }
  }

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const jobLogs = await modelApi.getTrainingLogs(trainingJob.id)
      setLogs(jobLogs)
    } catch (error) {
      console.error('Error fetching logs:', error)
      showNotification('error', 'ログの取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handlePauseResume = async () => {
    try {
      setLoading(true)
      
      if (trainingJob.status === 'running') {
        await modelApi.pauseTraining(trainingJob.id)
        showNotification('success', '学習を一時停止しました')
      } else if (trainingJob.status === 'paused') {
        await modelApi.resumeTraining(trainingJob.id)
        showNotification('success', '学習を再開しました')
      }
      
      await refreshJobStatus()
    } catch (error) {
      console.error('Error pausing/resuming training:', error)
      showNotification('error', '操作に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    try {
      setLoading(true)
      await modelApi.cancelTraining(trainingJob.id)
      showNotification('success', '学習をキャンセルしました')
      await refreshJobStatus()
    } catch (error) {
      console.error('Error cancelling training:', error)
      showNotification('error', 'キャンセルに失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: TrainingJob['status']) => {
    switch (status) {
      case 'running':
        return 'success'
      case 'pending':
        return 'warning'
      case 'completed':
        return 'success'
      case 'failed':
        return 'error'
      case 'cancelled':
        return 'default'
      default:
        return 'default'
    }
  }

  const getStatusText = (status: TrainingJob['status']) => {
    switch (status) {
      case 'running':
        return '実行中'
      case 'pending':
        return '待機中'
      case 'completed':
        return '完了'
      case 'failed':
        return '失敗'
      case 'cancelled':
        return 'キャンセル済み'
      default:
        return status
    }
  }

  const calculateETA = () => {
    if (!trainingJob.started_at || trainingJob.progress.progress === 0) {
      return ' 計算中...'
    }

    const startTime = new Date(trainingJob.started_at).getTime()
    const currentTime = Date.now()
    const elapsedTime = currentTime - startTime
    const remainingProgress = 100 - trainingJob.progress.progress
    const estimatedRemainingTime = (elapsedTime / trainingJob.progress.progress) * remainingProgress

    if (estimatedRemainingTime < 60000) {
      return '1分未満'
    } else if (estimatedRemainingTime < 3600000) {
      const minutes = Math.round(estimatedRemainingTime / 60000)
      return `約 ${minutes} 分`
    } else {
      const hours = Math.round(estimatedRemainingTime / 3600000 * 10) / 10
      return `約 ${hours} 時間`
    }
  }

  // Prepare chart data
  const chartData = {
    labels: trainingJob.metrics.map((_, index) => `Epoch ${index + 1}`),
    datasets: [
      {
        label: '学習Loss',
        data: trainingJob.metrics.map(m => m.train_loss),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.1
      },
      {
        label: '検証Loss',
        data: trainingJob.metrics.map(m => m.val_loss),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        tension: 0.1
      },
      {
        label: 'mAP@0.5',
        data: trainingJob.metrics.map(m => m.map50),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
        yAxisID: 'y1'
      }
    ]
  }

  const chartOptions: ChartOptions<'line'> = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'エポック'
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Loss'
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'mAP'
        },
        grid: {
          drawOnChartArea: false,
        },
      }
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '学習進捗メトリクス'
      }
    }
  }

  const latestMetrics = trainingJob.metrics[trainingJob.metrics.length - 1]

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { minHeight: '80vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6">
              学習進捗 - {trainingJob.model_id}
            </Typography>
            <Chip 
              label={getStatusText(trainingJob.status)} 
              color={getStatusColor(trainingJob.status)}
              size="small"
              sx={{ mt: 1 }}
            />
          </Box>
          
          <Box display="flex" gap={1}>
            <Tooltip title="自動更新">
              <IconButton 
                onClick={() => setAutoRefresh(!autoRefresh)}
                color={autoRefresh ? 'primary' : 'default'}
              >
                <Refresh />
              </IconButton>
            </Tooltip>
            
            {trainingJob.status === 'running' && (
              <Tooltip title="一時停止">
                <IconButton onClick={handlePauseResume} disabled={loading}>
                  <Pause />
                </IconButton>
              </Tooltip>
            )}
            
            {trainingJob.status === 'paused' && (
              <Tooltip title="再開">
                <IconButton onClick={handlePauseResume} disabled={loading}>
                  <PlayArrow />
                </IconButton>
              </Tooltip>
            )}
            
            {(trainingJob.status === 'running' || trainingJob.status === 'paused') && (
              <Tooltip title="キャンセル">
                <IconButton onClick={handleCancel} disabled={loading} color="error">
                  <Stop />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Grid container spacing={3}>
          {/* Progress Overview */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                進捗状況
              </Typography>
              
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">
                    エポック {trainingJob.progress.epoch} / {trainingJob.config.epochs}
                  </Typography>
                  <Typography variant="body2">
                    {trainingJob.progress.progress.toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={trainingJob.progress.progress} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    開始時刻
                  </Typography>
                  <Typography variant="body1">
                    {trainingJob.started_at 
                      ? formatDistanceToNow(new Date(trainingJob.started_at), { 
                          addSuffix: true, 
                          locale: ja 
                        })
                      : '未開始'
                    }
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    推定残り時間
                  </Typography>
                  <Typography variant="body1">
                    {trainingJob.status === 'running' ? calculateETA() : '-'}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    現在のLoss
                  </Typography>
                  <Typography variant="body1">
                    {latestMetrics ? latestMetrics.train_loss.toFixed(4) : '-'}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    現在のmAP
                  </Typography>
                  <Typography variant="body1">
                    {latestMetrics ? latestMetrics.map50.toFixed(3) : '-'}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Training Configuration */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                学習設定
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="モデルタイプ" 
                    secondary={trainingJob.config.model_type} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="バッチサイズ" 
                    secondary={trainingJob.config.batch_size} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="学習率" 
                    secondary={trainingJob.config.learning_rate} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="画像サイズ" 
                    secondary={`${trainingJob.config.image_size}x${trainingJob.config.image_size}`} 
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>

          {/* Latest Metrics */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                最新メトリクス
              </Typography>
              {latestMetrics ? (
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Precision" 
                      secondary={latestMetrics.precision.toFixed(3)} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Recall" 
                      secondary={latestMetrics.recall.toFixed(3)} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="mAP@0.5:0.95" 
                      secondary={latestMetrics.map50_95.toFixed(3)} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="検証Loss" 
                      secondary={latestMetrics.val_loss.toFixed(4)} 
                    />
                  </ListItem>
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  メトリクスデータがありません
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Training Chart */}
          {trainingJob.metrics.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  学習曲線
                </Typography>
                <Box height={400}>
                  <Line data={chartData} options={chartOptions} />
                </Box>
              </Paper>
            </Grid>
          )}

          {/* Metrics Table */}
          {trainingJob.metrics.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  詳細メトリクス
                </Typography>
                <TableContainer sx={{ maxHeight: 300 }}>
                  <Table stickyHeader size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>エポック</TableCell>
                        <TableCell align="right">学習Loss</TableCell>
                        <TableCell align="right">検証Loss</TableCell>
                        <TableCell align="right">mAP@0.5</TableCell>
                        <TableCell align="right">mAP@0.5:0.95</TableCell>
                        <TableCell align="right">Precision</TableCell>
                        <TableCell align="right">Recall</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {trainingJob.metrics.slice().reverse().map((metric, index) => (
                        <TableRow key={trainingJob.metrics.length - index}>
                          <TableCell component="th" scope="row">
                            {trainingJob.metrics.length - index}
                          </TableCell>
                          <TableCell align="right">{metric.train_loss.toFixed(4)}</TableCell>
                          <TableCell align="right">{metric.val_loss.toFixed(4)}</TableCell>
                          <TableCell align="right">{metric.map50.toFixed(3)}</TableCell>
                          <TableCell align="right">{metric.map50_95.toFixed(3)}</TableCell>
                          <TableCell align="right">{metric.precision.toFixed(3)}</TableCell>
                          <TableCell align="right">{metric.recall.toFixed(3)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            </Grid>
          )}

          {/* Error Message */}
          {trainingJob.status === 'failed' && trainingJob.error_message && (
            <Grid item xs={12}>
              <Alert severity="error">
                <Typography variant="body2">
                  学習に失敗しました: {trainingJob.error_message}
                </Typography>
              </Alert>
            </Grid>
          )}

          {/* Training Logs */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  学習ログ
                </Typography>
                <Button 
                  onClick={fetchLogs}
                  disabled={loading}
                  size="small"
                  startIcon={<Refresh />}
                >
                  更新
                </Button>
              </Box>
              
              <Box 
                sx={{ 
                  height: 200, 
                  overflow: 'auto', 
                  bgcolor: 'grey.100',
                  p: 1,
                  fontFamily: 'monospace',
                  fontSize: '0.8rem'
                }}
              >
                {logs.length > 0 ? (
                  logs.map((log, index) => (
                    <Typography 
                      key={index} 
                      variant="caption" 
                      component="div"
                      sx={{ whiteSpace: 'pre-wrap' }}
                    >
                      {log}
                    </Typography>
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    ログを取得するには「更新」ボタンをクリックしてください
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose}>
          閉じる
        </Button>
      </DialogActions>
    </Dialog>
  )
}