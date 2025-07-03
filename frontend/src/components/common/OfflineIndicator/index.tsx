import React from 'react'
import {
  Box,
  Chip,
  Badge,
  IconButton,
  Drawer,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  LinearProgress,
  Alert,
  Tooltip,
  Fab,
} from '@mui/material'
import {
  CloudOff as OfflineIcon,
  Cloud as OnlineIcon,
  Sync as SyncIcon,
  Storage as StorageIcon,
  Delete as DeleteIcon,
  Schedule as QueueIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'

import { useOffline } from '../../../hooks/useOffline'
import { Button, StatusBadge } from '../index'

interface OfflineIndicatorProps {
  compact?: boolean
  showDetails?: boolean
  position?: 'fixed' | 'static'
}

export function OfflineIndicator({ 
  compact = false, 
  showDetails = false,
  position = 'static' 
}: OfflineIndicatorProps) {
  const {
    isOnline,
    isOffline,
    syncInProgress,
    offlineQueue,
    syncOfflineData,
    clearCache,
    clearOfflineQueue,
    getCacheStats,
  } = useOffline()

  const [drawerOpen, setDrawerOpen] = React.useState(false)
  const cacheStats = getCacheStats()

  const handleSync = () => {
    syncOfflineData()
  }

  const handleClearCache = () => {
    clearCache()
  }

  const handleClearQueue = () => {
    clearOfflineQueue()
  }

  if (compact) {
    return (
      <Tooltip title={isOnline ? 'オンライン' : 'オフライン'}>
        <StatusBadge
          status={isOnline ? 'online' : 'offline'}
          variant="dot"
          size="small"
          pulse={!isOnline}
        />
      </Tooltip>
    )
  }

  if (position === 'fixed') {
    return (
      <>
        {/* Floating Action Button for Offline Status */}
        {(isOffline || offlineQueue.length > 0) && (
          <Fab
            color={isOffline ? 'error' : 'primary'}
            size="medium"
            onClick={() => setDrawerOpen(true)}
            sx={{
              position: 'fixed',
              bottom: 16,
              right: 16,
              zIndex: 1000,
            }}
          >
            <Badge badgeContent={offlineQueue.length} color="error">
              {isOffline ? <OfflineIcon /> : <QueueIcon />}
            </Badge>
          </Fab>
        )}

        {/* Offline Status Drawer */}
        <Drawer
          anchor="bottom"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          PaperProps={{
            sx: {
              maxHeight: '50vh',
              borderTopLeftRadius: 16,
              borderTopRightRadius: 16,
            },
          }}
        >
          <OfflineDetails
            isOnline={isOnline}
            syncInProgress={syncInProgress}
            offlineQueue={offlineQueue}
            cacheStats={cacheStats}
            onSync={handleSync}
            onClearCache={handleClearCache}
            onClearQueue={handleClearQueue}
            onClose={() => setDrawerOpen(false)}
          />
        </Drawer>
      </>
    )
  }

  // Inline display
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <StatusBadge
        status={isOnline ? 'online' : 'offline'}
        label={isOnline ? 'オンライン' : 'オフライン'}
        variant="chip"
        size="small"
        pulse={!isOnline}
      />

      {offlineQueue.length > 0 && (
        <Badge badgeContent={offlineQueue.length} color="warning">
          <Chip
            icon={<QueueIcon />}
            label="同期待ち"
            size="small"
            color="warning"
            variant="outlined"
          />
        </Badge>
      )}

      {syncInProgress && (
        <Chip
          icon={<SyncIcon />}
          label="同期中"
          size="small"
          color="info"
          variant="outlined"
        />
      )}

      {showDetails && (
        <IconButton
          size="small"
          onClick={() => setDrawerOpen(true)}
          disabled={isOnline && offlineQueue.length === 0}
        >
          <InfoIcon fontSize="small" />
        </IconButton>
      )}
    </Box>
  )
}

interface OfflineDetailsProps {
  isOnline: boolean
  syncInProgress: boolean
  offlineQueue: any[]
  cacheStats: { size: number; queueLength: number }
  onSync: () => void
  onClearCache: () => void
  onClearQueue: () => void
  onClose: () => void
}

function OfflineDetails({
  isOnline,
  syncInProgress,
  offlineQueue,
  cacheStats,
  onSync,
  onClearCache,
  onClearQueue,
  onClose,
}: OfflineDetailsProps) {
  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">オフライン状態</Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Connection Status */}
      <Alert
        severity={isOnline ? 'success' : 'warning'}
        icon={isOnline ? <OnlineIcon /> : <OfflineIcon />}
        sx={{ mb: 2 }}
      >
        <Typography variant="body2">
          {isOnline 
            ? 'インターネットに接続されています' 
            : 'オフラインモードです。データは一時保存されます。'}
        </Typography>
      </Alert>

      {/* Sync Progress */}
      {syncInProgress && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>
            データを同期中...
          </Typography>
          <LinearProgress />
        </Box>
      )}

      {/* Statistics */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          統計情報
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon>
              <QueueIcon color="action" />
            </ListItemIcon>
            <ListItemText
              primary="同期待ちアイテム"
              secondary={`${cacheStats.queueLength}件`}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <StorageIcon color="action" />
            </ListItemIcon>
            <ListItemText
              primary="キャッシュサイズ"
              secondary={`${cacheStats.size.toFixed(2)} MB`}
            />
          </ListItem>
        </List>
      </Box>

      {/* Offline Queue */}
      {offlineQueue.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            同期待ちアイテム
          </Typography>
          <List dense sx={{ maxHeight: 200, overflow: 'auto' }}>
            {offlineQueue.map((item, index) => (
              <React.Fragment key={item.id}>
                <ListItem>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={item.type.toUpperCase()}
                          size="small"
                          color={
                            item.type === 'create' ? 'success' :
                            item.type === 'update' ? 'info' : 'error'
                          }
                          variant="outlined"
                        />
                        <Typography variant="body2">
                          {item.endpoint}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                        <Typography variant="caption">
                          {new Date(item.timestamp).toLocaleString()}
                        </Typography>
                        {item.retries > 0 && (
                          <Typography variant="caption" color="warning.main">
                            再試行: {item.retries}回
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < offlineQueue.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Box>
      )}

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        {isOnline && offlineQueue.length > 0 && (
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={onSync}
            disabled={syncInProgress}
            loading={syncInProgress}
            size="small"
          >
            今すぐ同期
          </Button>
        )}

        {offlineQueue.length > 0 && (
          <Button
            variant="outlined"
            startIcon={<DeleteIcon />}
            onClick={onClearQueue}
            color="warning"
            size="small"
          >
            キューをクリア
          </Button>
        )}

        {cacheStats.size > 0 && (
          <Button
            variant="outlined"
            startIcon={<StorageIcon />}
            onClick={onClearCache}
            size="small"
          >
            キャッシュをクリア
          </Button>
        )}
      </Box>
    </Box>
  )
}

// Hook for easy integration
export function useOfflineIndicator() {
  const offline = useOffline()
  
  return {
    ...offline,
    OfflineIndicator: (props: Omit<OfflineIndicatorProps, 'isOnline' | 'offlineQueue'>) => (
      <OfflineIndicator {...props} />
    ),
  }
}