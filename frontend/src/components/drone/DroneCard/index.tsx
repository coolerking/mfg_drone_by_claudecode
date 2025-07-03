import React from 'react'
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip, 
  IconButton, 
  LinearProgress,
  Button,
  Stack,
  Grid
} from '@mui/material'
import { 
  Flight,
  FlightTakeoff,
  FlightLand,
  Videocam,
  Warning,
  Settings,
  Delete,
  PowerOff,
  Power
} from '@mui/icons-material'
import { Drone, DroneStatus } from '../../../types/drone'
import { StatusBadge } from '../../common/StatusBadge'
import { useConfirmDialog } from '../../common/ConfirmDialog'
import { formatDistanceToNow } from 'date-fns'
import { ja } from 'date-fns/locale'

interface DroneCardProps {
  drone: Drone
  onConnect?: (droneId: string) => void
  onDisconnect?: (droneId: string) => void
  onTakeoff?: (droneId: string) => void
  onLand?: (droneId: string) => void
  onEmergencyStop?: (droneId: string) => void
  onStartStream?: (droneId: string) => void
  onStopStream?: (droneId: string) => void
  onControl?: (droneId: string) => void
  onDelete?: (droneId: string) => void
  onSettings?: (droneId: string) => void
}

const getStatusColor = (status: DroneStatus): 'success' | 'error' | 'warning' | 'info' => {
  switch (status) {
    case 'connected':
    case 'hovering':
      return 'success'
    case 'disconnected':
    case 'error':
    case 'maintenance':
      return 'error'
    case 'low_battery':
      return 'warning'
    case 'flying':
    case 'takeoff':
    case 'landing':
      return 'info'
    default:
      return 'info'
  }
}

const getBatteryColor = (battery: number): string => {
  if (battery > 50) return '#4caf50'
  if (battery > 20) return '#ff9800'
  return '#f44336'
}

const getStatusIcon = (status: DroneStatus) => {
  switch (status) {
    case 'flying':
      return <Flight />
    case 'takeoff':
      return <FlightTakeoff />
    case 'landing':
      return <FlightLand />
    case 'error':
    case 'low_battery':
      return <Warning />
    default:
      return <Flight />
  }
}

export const DroneCard: React.FC<DroneCardProps> = ({
  drone,
  onConnect,
  onDisconnect,
  onTakeoff,
  onLand,
  onEmergencyStop,
  onStartStream,
  onStopStream,
  onControl,
  onDelete,
  onSettings
}) => {
  const { showConfirmDialog } = useConfirmDialog()

  const handleConnect = () => {
    if (drone.status === 'connected') {
      showConfirmDialog({
        title: 'ドローン切断',
        message: `${drone.name}を切断しますか？`,
        onConfirm: () => onDisconnect?.(drone.id)
      })
    } else {
      onConnect?.(drone.id)
    }
  }

  const handleEmergencyStop = () => {
    showConfirmDialog({
      title: '緊急停止',
      message: `${drone.name}を緊急停止させますか？\nこの操作は即座に実行されます。`,
      onConfirm: () => onEmergencyStop?.(drone.id),
      confirmText: '緊急停止',
      confirmColor: 'error'
    })
  }

  const handleDelete = () => {
    showConfirmDialog({
      title: 'ドローン削除',
      message: `${drone.name}を削除しますか？\nこの操作は取り消せません。`,
      onConfirm: () => onDelete?.(drone.id),
      confirmText: '削除',
      confirmColor: 'error'
    })
  }

  const isConnected = drone.status === 'connected' || 
                     drone.status === 'flying' || 
                     drone.status === 'hovering' ||
                     drone.status === 'takeoff' ||
                     drone.status === 'landing'

  const canTakeoff = isConnected && 
                     drone.status !== 'flying' && 
                     drone.status !== 'takeoff' &&
                     drone.battery > 15

  const canLand = drone.status === 'flying' || 
                  drone.status === 'hovering' ||
                  drone.status === 'takeoff'

  const lastSeenTime = formatDistanceToNow(new Date(drone.lastSeen), {
    addSuffix: true,
    locale: ja
  })

  return (
    <Card 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        border: drone.status === 'error' ? '2px solid #f44336' : 
                drone.status === 'low_battery' ? '2px solid #ff9800' : 'none'
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h6" component="h3" noWrap>
              {drone.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {drone.model} • {drone.serial_number}
            </Typography>
          </Box>
          <StatusBadge 
            status={drone.status} 
            color={getStatusColor(drone.status)}
            icon={getStatusIcon(drone.status)}
          />
        </Box>

        {/* Metrics Grid */}
        <Grid container spacing={2} mb={2}>
          <Grid item xs={6}>
            <Box textAlign="center">
              <Typography variant="h4" sx={{ color: getBatteryColor(drone.battery) }}>
                {drone.battery}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                バッテリー
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={drone.battery} 
                sx={{ 
                  mt: 0.5,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getBatteryColor(drone.battery)
                  }
                }}
              />
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box textAlign="center">
              <Typography variant="h4">
                {drone.altitude}m
              </Typography>
              <Typography variant="caption" color="text.secondary">
                高度
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box textAlign="center">
              <Typography variant="body1">
                {drone.temperature}°C
              </Typography>
              <Typography variant="caption" color="text.secondary">
                温度
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box textAlign="center">
              <Typography variant="body1">
                {drone.signal_strength}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                信号強度
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Last Seen */}
        <Typography variant="caption" color="text.secondary">
          最終接続: {lastSeenTime}
        </Typography>

        {/* Action Buttons */}
        <Box mt={2}>
          <Stack spacing={1}>
            {/* Primary Actions */}
            <Stack direction="row" spacing={1}>
              <Button
                variant={isConnected ? "outlined" : "contained"}
                color={isConnected ? "error" : "primary"}
                startIcon={isConnected ? <PowerOff /> : <Power />}
                onClick={handleConnect}
                size="small"
                fullWidth
              >
                {isConnected ? '切断' : '接続'}
              </Button>
              
              {isConnected && (
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<FlightTakeoff />}
                  onClick={() => onTakeoff?.(drone.id)}
                  disabled={!canTakeoff}
                  size="small"
                  fullWidth
                >
                  離陸
                </Button>
              )}
              
              {canLand && (
                <Button
                  variant="contained"
                  color="warning"
                  startIcon={<FlightLand />}
                  onClick={() => onLand?.(drone.id)}
                  size="small"
                  fullWidth
                >
                  着陸
                </Button>
              )}
            </Stack>

            {/* Secondary Actions */}
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                startIcon={<Settings />}
                onClick={() => onControl?.(drone.id)}
                disabled={!isConnected}
                size="small"
              >
                制御
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<Videocam />}
                onClick={() => {
                  if (drone.camera?.isStreaming) {
                    onStopStream?.(drone.id)
                  } else {
                    onStartStream?.(drone.id)
                  }
                }}
                disabled={!isConnected}
                size="small"
              >
                {drone.camera?.isStreaming ? 'カメラ停止' : 'カメラ'}
              </Button>
            </Stack>

            {/* Emergency Actions */}
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                color="error"
                onClick={handleEmergencyStop}
                disabled={!isConnected}
                size="small"
                fullWidth
              >
                緊急停止
              </Button>
            </Stack>
          </Stack>
        </Box>
      </CardContent>

      {/* Settings & Delete */}
      <Box 
        position="absolute" 
        top={8} 
        right={8}
        display="flex"
        gap={0.5}
      >
        <IconButton
          size="small"
          onClick={() => onSettings?.(drone.id)}
          sx={{ backgroundColor: 'rgba(255,255,255,0.8)' }}
        >
          <Settings fontSize="small" />
        </IconButton>
        <IconButton
          size="small"
          onClick={handleDelete}
          sx={{ backgroundColor: 'rgba(255,255,255,0.8)' }}
        >
          <Delete fontSize="small" color="error" />
        </IconButton>
      </Box>
    </Card>
  )
}