import { useState, useEffect } from 'react'
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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
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
} from '@mui/icons-material'

import { Card, StatCard, StatusBadge, Loading, Button } from '../../components/common'
import { useNotification } from '../../hooks/useNotification'

// Data interfaces
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
  battery: number
  lastSeen: string
}

interface AlertItem {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  timestamp: string
  dismissible?: boolean
}

interface ActivityItem {
  id: string
  type: 'drone' | 'dataset' | 'model' | 'tracking' | 'system'
  message: string
  timestamp: string
  icon: React.ReactNode
}

// Enhanced system metrics component
function SystemMetricsCard({ metrics, loading }: { metrics: SystemMetrics; loading: boolean }) {
  if (loading) {
    return (
      <Card title="システムメトリクス" loading />
    )
  }

  const getMetricColor = (value: number, thresholds = { warning: 70, error: 90 }) => {
    if (value >= thresholds.error) return 'error'
    if (value >= thresholds.warning) return 'warning'
    return 'success'
  }

  return (
    <Card title="システムメトリクス">
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* CPU Usage */}
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <SpeedIcon color="action" />
            <Typography variant="body2">CPU使用率</Typography>
            <Typography variant="body2" color={`${getMetricColor(metrics.cpu)}.main`} fontWeight="bold">
              {metrics.cpu}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={metrics.cpu}
            color={getMetricColor(metrics.cpu)}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Memory Usage */}
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <MemoryIcon color="action" />
            <Typography variant="body2">メモリ使用率</Typography>
            <Typography variant="body2" color={`${getMetricColor(metrics.memory)}.main`} fontWeight="bold">
              {metrics.memory}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={metrics.memory}
            color={getMetricColor(metrics.memory)}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Disk Usage */}
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <StorageIcon color="action" />
            <Typography variant="body2">ディスク使用率</Typography>
            <Typography variant="body2" color={`${getMetricColor(metrics.disk)}.main`} fontWeight="bold">
              {metrics.disk}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={metrics.disk}
            color={getMetricColor(metrics.disk)}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Network Status */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <NetworkIcon color="action" />
          <Typography variant="body2">ネットワーク</Typography>
          <StatusBadge status={metrics.network} variant="chip" size="small" />
        </Box>
      </Box>
    </Card>
  )
}

// Drone status list component
function DroneStatusCard({ drones, loading }: { drones: DroneStatus[]; loading: boolean }) {
  if (loading) {
    return (
      <Card title="ドローン状態" loading />
    )
  }

  return (
    <Card title="ドローン状態">
      <List dense>
        {drones.map((drone) => (
          <ListItem key={drone.id}>
            <ListItemIcon>
              <Avatar sx={{ width: 32, height: 32 }}>
                <FlightTakeoff fontSize="small" />
              </Avatar>
            </ListItemIcon>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" fontWeight="bold">
                    {drone.name}
                  </Typography>
                  <StatusBadge status={drone.status} variant="chip" size="small" />
                </Box>
              }
              secondary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="caption">
                    バッテリー: {drone.battery}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {drone.lastSeen}
                  </Typography>
                </Box>
              }
            />
          </ListItem>
        ))}
      </List>
    </Card>
  )
}

// Alert panel component
function AlertPanel({ alerts, onDismissAlert }: { alerts: AlertItem[]; onDismissAlert: (id: string) => void }) {
  if (alerts.length === 0) return null

  return (
    <Box sx={{ mb: 3 }}>
      {alerts.map((alert) => {
        const icons = {
          info: <InfoIcon />,
          warning: <WarningIcon />,
          error: <ErrorIcon />,
          success: <SuccessIcon />,
        }

        return (
          <Alert
            key={alert.id}
            severity={alert.type}
            icon={icons[alert.type]}
            action={
              alert.dismissible && (
                <IconButton
                  aria-label="close"
                  color="inherit"
                  size="small"
                  onClick={() => onDismissAlert(alert.id)}
                >
                  <CloseIcon fontSize="inherit" />
                </IconButton>
              )
            }
            sx={{ mb: 1 }}
          >
            <AlertTitle>{alert.title}</AlertTitle>
            {alert.message}
            <Typography variant="caption" display="block" sx={{ mt: 0.5, opacity: 0.8 }}>
              {alert.timestamp}
            </Typography>
          </Alert>
        )
      })}
    </Box>
  )
}

export function Dashboard() {
  // State management
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const { showSuccess, showError } = useNotification()

  // Demo data state
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    cpu: 45,
    memory: 78,
    disk: 52,
    network: 'normal',
  })

  const [drones, setDrones] = useState<DroneStatus[]>([
    {
      id: 'drone-1',
      name: 'Tello-01',
      status: 'connected',
      battery: 85,
      lastSeen: '2分前',
    },
    {
      id: 'drone-2',
      name: 'Tello-02',
      status: 'flying',
      battery: 67,
      lastSeen: '30秒前',
    },
    {
      id: 'drone-3',
      name: 'Tello-03',
      status: 'disconnected',
      battery: 15,
      lastSeen: '10分前',
    },
  ])

  const [alerts, setAlerts] = useState<AlertItem[]>([
    {
      id: 'alert-1',
      type: 'warning',
      title: 'バッテリー低下警告',
      message: 'Tello-03のバッテリーが15%を下回りました。充電が必要です。',
      timestamp: '5分前',
      dismissible: true,
    },
    {
      id: 'alert-2',
      type: 'info',
      title: '学習完了',
      message: 'データセット "人物検出_v2" の学習が正常に完了しました。',
      timestamp: '15分前',
      dismissible: true,
    },
  ])

  const [activities, setActivities] = useState<ActivityItem[]>([
    {
      id: 'activity-1',
      type: 'drone',
      message: 'ドローン "Tello-01" が接続されました',
      timestamp: '2分前',
      icon: <FlightTakeoff color="primary" />,
    },
    {
      id: 'activity-2',
      type: 'model',
      message: 'データセット "人物検出_v2" の学習が完了しました',
      timestamp: '15分前',
      icon: <Psychology color="secondary" />,
    },
    {
      id: 'activity-3',
      type: 'tracking',
      message: '追跡セッションが開始されました',
      timestamp: '1時間前',
      icon: <TrackChanges color="info" />,
    },
    {
      id: 'activity-4',
      type: 'dataset',
      message: '新しいデータセットがアップロードされました',
      timestamp: '2時間前',
      icon: <Folder color="success" />,
    },
  ])

  // Statistics calculation
  const connectedDrones = drones.filter(d => d.status === 'connected' || d.status === 'flying').length
  const offlineDrones = drones.filter(d => d.status === 'disconnected').length
  const activeTracks = drones.filter(d => d.status === 'flying').length

  // Auto-refresh functionality
  useEffect(() => {
    const interval = setInterval(() => {
      if (!refreshing) {
        updateData()
      }
    }, 30000) // Refresh every 30 seconds

    // Initial load
    setTimeout(() => {
      setLoading(false)
    }, 1500)

    return () => clearInterval(interval)
  }, [refreshing])

  const updateData = () => {
    // Simulate data updates with random variations
    setSystemMetrics(prev => ({
      cpu: Math.max(30, Math.min(95, prev.cpu + (Math.random() - 0.5) * 10)),
      memory: Math.max(50, Math.min(95, prev.memory + (Math.random() - 0.5) * 5)),
      disk: Math.max(40, Math.min(90, prev.disk + (Math.random() - 0.5) * 2)),
      network: Math.random() > 0.1 ? 'normal' : 'warning',
    }))

    setLastUpdated(new Date())
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
      updateData()
      showSuccess('データを更新しました')
    } catch (error) {
      showError('データの更新に失敗しました')
    } finally {
      setRefreshing(false)
    }
  }

  const handleDismissAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId))
  }

  if (loading) {
    return <Loading text="ダッシュボードを読み込んでいます..." />
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            ダッシュボード
          </Typography>
          <Typography variant="body1" color="text.secondary">
            システム全体の状況を確認できます
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="caption" color="text.secondary">
            最終更新: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <Button
            variant="outlined"
            size="small"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            loading={refreshing}
          >
            更新
          </Button>
        </Box>
      </Box>

      {/* Alerts */}
      <AlertPanel alerts={alerts} onDismissAlert={handleDismissAlert} />

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="接続ドローン数"
            value={connectedDrones}
            icon={<FlightTakeoff sx={{ fontSize: 40 }} />}
            change={{
              value: connectedDrones - offlineDrones,
              label: '前回比',
              positive: connectedDrones > offlineDrones,
            }}
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="データセット数"
            value={5}
            icon={<Folder sx={{ fontSize: 40 }} />}
            color="secondary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="学習済みモデル数"
            value={2}
            icon={<Psychology sx={{ fontSize: 40 }} />}
            color="info"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="アクティブ追跡数"
            value={activeTracks}
            icon={<TrackChanges sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <SystemMetricsCard metrics={systemMetrics} loading={false} />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <DroneStatusCard drones={drones} loading={false} />
        </Grid>
        
        <Grid item xs={12}>
          <Card title="最近のアクティビティ">
            <List>
              {activities.map((activity, index) => (
                <Box key={activity.id}>
                  <ListItem>
                    <ListItemIcon>{activity.icon}</ListItemIcon>
                    <ListItemText
                      primary={activity.message}
                      secondary={activity.timestamp}
                    />
                  </ListItem>
                  {index < activities.length - 1 && <Divider />}
                </Box>
              ))}
            </List>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}