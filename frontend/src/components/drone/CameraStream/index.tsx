import React, { useRef, useEffect, useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Stack,
  Chip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material'
import {
  Videocam,
  VideocamOff,
  Camera,
  Fullscreen,
  FullscreenExit,
  Settings,
  Circle
} from '@mui/icons-material'
import { Drone } from '../../../types/drone'

interface CameraStreamProps {
  drone: Drone
  onStartStream?: () => void
  onStopStream?: () => void
  onTakePhoto?: () => void
  onUpdateSettings?: (settings: CameraSettings) => void
}

interface CameraSettings {
  resolution: string
  fps: number
  quality: number
}

export const CameraStream: React.FC<CameraStreamProps> = ({
  drone,
  onStartStream,
  onStopStream,
  onTakePhoto,
  onUpdateSettings
}) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const [settings, setSettings] = useState<CameraSettings>({
    resolution: '720p',
    fps: 30,
    quality: 80
  })

  const isStreaming = drone.camera?.isStreaming || false
  const streamUrl = drone.camera?.streamUrl
  const isConnected = drone.status === 'connected' || 
                     drone.status === 'flying' || 
                     drone.status === 'hovering'

  useEffect(() => {
    if (isStreaming && streamUrl && videoRef.current) {
      setConnectionStatus('connecting')
      const video = videoRef.current
      
      // Setup video stream
      video.src = streamUrl
      video.onloadstart = () => setConnectionStatus('connecting')
      video.oncanplay = () => setConnectionStatus('connected')
      video.onerror = () => setConnectionStatus('disconnected')
      
      video.play().catch(error => {
        console.error('Video playback failed:', error)
        setConnectionStatus('disconnected')
      })
    }
  }, [isStreaming, streamUrl])

  const handleToggleStream = () => {
    if (isStreaming) {
      onStopStream?.()
      setConnectionStatus('disconnected')
    } else {
      onStartStream?.()
    }
  }

  const handleFullscreen = () => {
    if (!videoRef.current) return

    if (!isFullscreen) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen()
        setIsFullscreen(true)
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
        setIsFullscreen(false)
      }
    }
  }

  const handleTakePhoto = () => {
    onTakePhoto?.()
    // Show brief flash effect
    if (videoRef.current) {
      const flash = document.createElement('div')
      flash.style.position = 'absolute'
      flash.style.top = '0'
      flash.style.left = '0'
      flash.style.width = '100%'
      flash.style.height = '100%'
      flash.style.backgroundColor = 'white'
      flash.style.opacity = '0.8'
      flash.style.zIndex = '1000'
      flash.style.pointerEvents = 'none'
      
      videoRef.current.parentElement?.appendChild(flash)
      setTimeout(() => flash.remove(), 200)
    }
  }

  const handleSettingsChange = (field: keyof CameraSettings, value: any) => {
    const newSettings = { ...settings, [field]: value }
    setSettings(newSettings)
    onUpdateSettings?.(newSettings)
  }

  const getConnectionStatusChip = () => {
    switch (connectionStatus) {
      case 'connecting':
        return <Chip label="接続中..." color="warning" size="small" />
      case 'connected':
        return <Chip label="ライブ" color="success" size="small" icon={<Circle />} />
      case 'disconnected':
        return <Chip label="切断" color="error" size="small" />
    }
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            {drone.name} - カメラ映像
          </Typography>
          {getConnectionStatusChip()}
        </Box>

        {!isConnected && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            ドローンが接続されていません
          </Alert>
        )}

        {/* Video Stream */}
        <Box 
          position="relative" 
          mb={2}
          sx={{ 
            backgroundColor: '#000',
            borderRadius: 1,
            overflow: 'hidden',
            aspectRatio: '16/9'
          }}
        >
          {isStreaming ? (
            <video
              ref={videoRef}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain'
              }}
              controls={false}
              muted
              playsInline
            />
          ) : (
            <Box
              display="flex"
              alignItems="center"
              justifyContent="center"
              height="100%"
              color="white"
            >
              <Stack alignItems="center" spacing={2}>
                <VideocamOff fontSize="large" />
                <Typography variant="body2">
                  カメラストリームが停止中
                </Typography>
              </Stack>
            </Box>
          )}

          {/* Video Controls Overlay */}
          {isStreaming && (
            <Box
              position="absolute"
              bottom={8}
              right={8}
              display="flex"
              gap={1}
            >
              <IconButton
                size="small"
                onClick={handleTakePhoto}
                sx={{ 
                  backgroundColor: 'rgba(0,0,0,0.5)',
                  color: 'white',
                  '&:hover': { backgroundColor: 'rgba(0,0,0,0.7)' }
                }}
              >
                <Camera />
              </IconButton>
              <IconButton
                size="small"
                onClick={handleFullscreen}
                sx={{ 
                  backgroundColor: 'rgba(0,0,0,0.5)',
                  color: 'white',
                  '&:hover': { backgroundColor: 'rgba(0,0,0,0.7)' }
                }}
              >
                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
              </IconButton>
            </Box>
          )}

          {/* Recording Indicator */}
          {isRecording && (
            <Box
              position="absolute"
              top={8}
              left={8}
              display="flex"
              alignItems="center"
              gap={1}
              sx={{
                backgroundColor: 'rgba(255,0,0,0.8)',
                color: 'white',
                px: 1,
                py: 0.5,
                borderRadius: 1
              }}
            >
              <Circle sx={{ fontSize: 8, animation: 'blink 1s infinite' }} />
              <Typography variant="caption">REC</Typography>
            </Box>
          )}
        </Box>

        {/* Stream Controls */}
        <Stack spacing={2}>
          <Box display="flex" gap={1}>
            <Button
              variant={isStreaming ? "outlined" : "contained"}
              color={isStreaming ? "error" : "primary"}
              startIcon={isStreaming ? <VideocamOff /> : <Videocam />}
              onClick={handleToggleStream}
              disabled={!isConnected}
              fullWidth
            >
              {isStreaming ? 'ストリーム停止' : 'ストリーム開始'}
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<Camera />}
              onClick={handleTakePhoto}
              disabled={!isStreaming}
            >
              撮影
            </Button>
          </Box>

          {/* Camera Settings */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              カメラ設定
            </Typography>
            <Stack direction="row" spacing={2}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>解像度</InputLabel>
                <Select
                  value={settings.resolution}
                  label="解像度"
                  onChange={(e) => handleSettingsChange('resolution', e.target.value)}
                  disabled={!isConnected}
                >
                  <MenuItem value="480p">480p</MenuItem>
                  <MenuItem value="720p">720p</MenuItem>
                  <MenuItem value="1080p">1080p</MenuItem>
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 100 }}>
                <InputLabel>FPS</InputLabel>
                <Select
                  value={settings.fps}
                  label="FPS"
                  onChange={(e) => handleSettingsChange('fps', e.target.value)}
                  disabled={!isConnected}
                >
                  <MenuItem value={15}>15 FPS</MenuItem>
                  <MenuItem value={30}>30 FPS</MenuItem>
                  <MenuItem value={60}>60 FPS</MenuItem>
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 100 }}>
                <InputLabel>品質</InputLabel>
                <Select
                  value={settings.quality}
                  label="品質"
                  onChange={(e) => handleSettingsChange('quality', e.target.value)}
                  disabled={!isConnected}
                >
                  <MenuItem value={50}>低品質</MenuItem>
                  <MenuItem value={80}>標準</MenuItem>
                  <MenuItem value={100}>高品質</MenuItem>
                </Select>
              </FormControl>
            </Stack>
          </Box>
        </Stack>
      </CardContent>

      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
        `}
      </style>
    </Card>
  )
}