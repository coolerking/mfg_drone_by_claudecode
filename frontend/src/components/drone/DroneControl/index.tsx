import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Grid,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Stack,
  Divider,
  Alert
} from '@mui/material'
import {
  FlightTakeoff,
  FlightLand,
  ArrowUpward,
  ArrowDownward,
  ArrowForward,
  ArrowBack,
  TurnLeft,
  TurnRight,
  RotateLeft,
  RotateRight,
  Stop,
  Home,
  Speed
} from '@mui/icons-material'
import { Drone } from '../../../types/drone'
import { useConfirmDialog } from '../../common/ConfirmDialog'

interface DroneControlProps {
  drone: Drone
  onTakeoff?: () => void
  onLand?: () => void
  onEmergencyStop?: () => void
  onMove?: (direction: 'up' | 'down' | 'left' | 'right' | 'forward' | 'back', distance: number) => void
  onRotate?: (direction: 'clockwise' | 'counter_clockwise', angle: number) => void
  onSetSpeed?: (speed: number) => void
  onReturnHome?: () => void
}

export const DroneControl: React.FC<DroneControlProps> = ({
  drone,
  onTakeoff,
  onLand,
  onEmergencyStop,
  onMove,
  onRotate,
  onSetSpeed,
  onReturnHome
}) => {
  const [moveDistance, setMoveDistance] = useState<number>(50)
  const [rotateAngle, setRotateAngle] = useState<number>(90)
  const [speed, setSpeed] = useState<number>(50)
  const { showConfirmDialog } = useConfirmDialog()

  const isFlying = drone.status === 'flying' || 
                   drone.status === 'hovering' ||
                   drone.status === 'takeoff' ||
                   drone.status === 'landing'

  const isConnected = drone.status === 'connected' || isFlying

  const canTakeoff = isConnected && 
                     drone.status !== 'flying' && 
                     drone.status !== 'takeoff' &&
                     drone.battery > 15

  const canLand = drone.status === 'flying' || 
                  drone.status === 'hovering' ||
                  drone.status === 'takeoff'

  const canMove = isFlying && drone.status !== 'takeoff' && drone.status !== 'landing'

  const handleEmergencyStop = () => {
    showConfirmDialog({
      title: '緊急停止',
      message: `${drone.name}を緊急停止させますか？\nドローンは即座に着陸を開始します。`,
      onConfirm: () => onEmergencyStop?.(),
      confirmText: '緊急停止',
      confirmColor: 'error'
    })
  }

  const handleMove = (direction: 'up' | 'down' | 'left' | 'right' | 'forward' | 'back') => {
    onMove?.(direction, moveDistance)
  }

  const handleRotate = (direction: 'clockwise' | 'counter_clockwise') => {
    onRotate?.(direction, rotateAngle)
  }

  const handleSpeedChange = () => {
    onSetSpeed?.(speed)
  }

  const getStatusAlert = () => {
    if (drone.battery <= 20) {
      return (
        <Alert severity="warning" sx={{ mb: 2 }}>
          バッテリー残量が少なくなっています ({drone.battery}%)
        </Alert>
      )
    }
    if (!isConnected) {
      return (
        <Alert severity="error" sx={{ mb: 2 }}>
          ドローンが接続されていません
        </Alert>
      )
    }
    return null
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {drone.name} - 手動制御
      </Typography>

      {getStatusAlert()}

      <Grid container spacing={2}>
        {/* Basic Controls */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                基本操作
              </Typography>
              
              <Stack spacing={2}>
                <Box display="flex" gap={1}>
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<FlightTakeoff />}
                    onClick={onTakeoff}
                    disabled={!canTakeoff}
                    fullWidth
                  >
                    離陸
                  </Button>
                  <Button
                    variant="contained"
                    color="warning"
                    startIcon={<FlightLand />}
                    onClick={onLand}
                    disabled={!canLand}
                    fullWidth
                  >
                    着陸
                  </Button>
                </Box>

                <Button
                  variant="outlined"
                  startIcon={<Home />}
                  onClick={onReturnHome}
                  disabled={!canMove}
                  fullWidth
                >
                  ホームに戻る
                </Button>

                <Button
                  variant="contained"
                  color="error"
                  startIcon={<Stop />}
                  onClick={handleEmergencyStop}
                  disabled={!isConnected}
                  fullWidth
                >
                  緊急停止
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Movement Controls */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                移動制御
              </Typography>

              {/* Distance Setting */}
              <Box mb={2}>
                <Typography variant="body2" gutterBottom>
                  移動距離: {moveDistance}cm
                </Typography>
                <Slider
                  value={moveDistance}
                  onChange={(_, value) => setMoveDistance(value as number)}
                  min={20}
                  max={500}
                  step={10}
                  marks={[
                    { value: 20, label: '20cm' },
                    { value: 100, label: '100cm' },
                    { value: 300, label: '300cm' },
                    { value: 500, label: '500cm' }
                  ]}
                  disabled={!canMove}
                />
              </Box>

              {/* Directional Controls */}
              <Grid container spacing={1} sx={{ mb: 2 }}>
                <Grid item xs={12} display="flex" justifyContent="center">
                  <IconButton
                    onClick={() => handleMove('forward')}
                    disabled={!canMove}
                    size="large"
                    sx={{ backgroundColor: '#e3f2fd' }}
                  >
                    <ArrowUpward />
                  </IconButton>
                </Grid>
                
                <Grid item xs={4} display="flex" justifyContent="center">
                  <IconButton
                    onClick={() => handleMove('left')}
                    disabled={!canMove}
                    size="large"
                    sx={{ backgroundColor: '#e3f2fd' }}
                  >
                    <ArrowBack />
                  </IconButton>
                </Grid>
                <Grid item xs={4} display="flex" justifyContent="center">
                  <IconButton
                    onClick={() => handleMove('up')}
                    disabled={!canMove}
                    size="large"
                    sx={{ backgroundColor: '#e8f5e8' }}
                  >
                    <TurnLeft sx={{ transform: 'rotate(90deg)' }} />
                  </IconButton>
                </Grid>
                <Grid item xs={4} display="flex" justifyContent="center">
                  <IconButton
                    onClick={() => handleMove('right')}
                    disabled={!canMove}
                    size="large"
                    sx={{ backgroundColor: '#e3f2fd' }}
                  >
                    <ArrowForward />
                  </IconButton>
                </Grid>
                
                <Grid item xs={12} display="flex" justifyContent="center">
                  <IconButton
                    onClick={() => handleMove('back')}
                    disabled={!canMove}
                    size="large"
                    sx={{ backgroundColor: '#e3f2fd' }}
                  >
                    <ArrowDownward />
                  </IconButton>
                </Grid>
              </Grid>

              {/* Up/Down Controls */}
              <Box display="flex" gap={1} mb={2}>
                <Button
                  variant="outlined"
                  startIcon={<ArrowUpward />}
                  onClick={() => handleMove('up')}
                  disabled={!canMove}
                  fullWidth
                >
                  上昇
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ArrowDownward />}
                  onClick={() => handleMove('down')}
                  disabled={!canMove}
                  fullWidth
                >
                  下降
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Rotation Controls */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                回転制御
              </Typography>

              <Box mb={2}>
                <Typography variant="body2" gutterBottom>
                  回転角度: {rotateAngle}°
                </Typography>
                <Slider
                  value={rotateAngle}
                  onChange={(_, value) => setRotateAngle(value as number)}
                  min={15}
                  max={360}
                  step={15}
                  marks={[
                    { value: 15, label: '15°' },
                    { value: 90, label: '90°' },
                    { value: 180, label: '180°' },
                    { value: 360, label: '360°' }
                  ]}
                  disabled={!canMove}
                />
              </Box>

              <Box display="flex" gap={1}>
                <Button
                  variant="outlined"
                  startIcon={<RotateLeft />}
                  onClick={() => handleRotate('counter_clockwise')}
                  disabled={!canMove}
                  fullWidth
                >
                  左回転
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RotateRight />}
                  onClick={() => handleRotate('clockwise')}
                  disabled={!canMove}
                  fullWidth
                >
                  右回転
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Speed Control */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                速度制御
              </Typography>

              <Box mb={2}>
                <Typography variant="body2" gutterBottom>
                  飛行速度: {speed}%
                </Typography>
                <Slider
                  value={speed}
                  onChange={(_, value) => setSpeed(value as number)}
                  min={10}
                  max={100}
                  step={10}
                  marks={[
                    { value: 10, label: '低速' },
                    { value: 50, label: '標準' },
                    { value: 100, label: '高速' }
                  ]}
                  disabled={!isConnected}
                />
              </Box>

              <Button
                variant="contained"
                startIcon={<Speed />}
                onClick={handleSpeedChange}
                disabled={!isConnected}
                fullWidth
              >
                速度設定を適用
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}