import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Avatar,
  Badge,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Collapse,
  Alert as MuiAlert,
  Tooltip,
  Pagination,
  Stack
} from '@mui/material'
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  Close,
  Visibility,
  VisibilityOff,
  Delete,
  DeleteForever,
  Add,
  FilterList,
  Refresh,
  ExpandMore,
  ExpandLess,
  NotificationsActive,
  NotificationsOff
} from '@mui/icons-material'
import { format } from 'date-fns'
import { ja } from 'date-fns/locale'
import { dashboardApi } from '../../../services/api/dashboardApi'
import type { Alert } from '../../../types/common'
import type { AlertRule } from '../../../types/monitoring'
import { useNotification } from '../../common'

interface AlertPanelProps {
  refreshInterval?: number
  maxAlerts?: number
  showCreateButton?: boolean
  compact?: boolean
}

interface CreateAlertDialogProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

const CreateAlertDialog: React.FC<CreateAlertDialogProps> = ({
  open,
  onClose,
  onSuccess
}) => {
  const { showNotification } = useNotification()
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    type: 'info' as const,
    auto_dismiss: false
  })

  const handleSubmit = async () => {
    try {
      await dashboardApi.createAlert({
        type: formData.type,
        title: formData.title,
        message: formData.message
      })
      
      showNotification('アラートを作成しました', 'success')
      
      onSuccess()
      onClose()
      setFormData({ title: '', message: '', type: 'info', auto_dismiss: false })
    } catch (error) {
      console.error('Failed to create alert:', error)
      showNotification('アラートの作成に失敗しました', 'error')
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>新しいアラートを作成</DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          <FormControl fullWidth>
            <InputLabel>タイプ</InputLabel>
            <Select
              value={formData.type}
              label="タイプ"
              onChange={(e) => setFormData(prev => ({ 
                ...prev, 
                type: e.target.value as 'info' | 'warning' | 'error' | 'success'
              }))}
            >
              <MenuItem value="info">情報</MenuItem>
              <MenuItem value="warning">警告</MenuItem>
              <MenuItem value="error">エラー</MenuItem>
              <MenuItem value="success">成功</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            label="タイトル"
            fullWidth
            value={formData.title}
            onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            required
          />
          
          <TextField
            label="メッセージ"
            fullWidth
            multiline
            rows={3}
            value={formData.message}
            onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
            required
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>キャンセル</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          disabled={!formData.title || !formData.message}
        >
          作成
        </Button>
      </DialogActions>
    </Dialog>
  )
}

const getAlertIcon = (type: Alert['type']) => {
  switch (type) {
    case 'error':
      return <Error color="error" />
    case 'warning':
      return <Warning color="warning" />
    case 'success':
      return <CheckCircle color="success" />
    case 'info':
    default:
      return <Info color="info" />
  }
}

const getAlertColor = (type: Alert['type']): 'error' | 'warning' | 'success' | 'info' => {
  return type
}

interface AlertItemProps {
  alert: Alert
  onDismiss: (id: string) => void
  onDelete: (id: string) => void
  compact?: boolean
}

const AlertItem: React.FC<AlertItemProps> = ({ alert, onDismiss, onDelete, compact = false }) => {
  const [expanded, setExpanded] = useState(false)

  return (
    <ListItem
      divider
      sx={{
        opacity: alert.dismissed ? 0.6 : 1,
        bgcolor: alert.dismissed ? 'action.hover' : 'background.paper'
      }}
    >
      <ListItemIcon>
        <Badge invisible={alert.dismissed} variant="dot" color={getAlertColor(alert.type)}>
          {getAlertIcon(alert.type)}
        </Badge>
      </ListItemIcon>
      
      <ListItemText
        primary={
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="subtitle2" component="div">
              {alert.title}
            </Typography>
            <Chip
              label={alert.type === 'error' ? 'エラー' : 
                    alert.type === 'warning' ? '警告' : 
                    alert.type === 'success' ? '成功' : '情報'}
              size="small"
              color={getAlertColor(alert.type)}
              variant="outlined"
            />
            {alert.dismissed && (
              <Chip
                label="解除済み"
                size="small"
                color="default"
                variant="outlined"
              />
            )}
          </Box>
        }
        secondary={
          <Box>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                display: '-webkit-box',
                WebkitLineClamp: expanded ? 'none' : 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}
            >
              {alert.message}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              {format(new Date(alert.timestamp), 'yyyy/MM/dd HH:mm:ss', { locale: ja })}
            </Typography>
            {alert.message.length > 100 && (
              <Button
                size="small"
                onClick={() => setExpanded(!expanded)}
                startIcon={expanded ? <ExpandLess /> : <ExpandMore />}
                sx={{ mt: 1 }}
              >
                {expanded ? '折りたたむ' : '詳細を表示'}
              </Button>
            )}
          </Box>
        }
      />
      
      <ListItemSecondaryAction>
        <Box display="flex" gap={1}>
          {!alert.dismissed && (
            <Tooltip title="解除">
              <IconButton
                size="small"
                onClick={() => onDismiss(alert.id)}
                color="primary"
              >
                <VisibilityOff />
              </IconButton>
            </Tooltip>
          )}
          <Tooltip title="削除">
            <IconButton
              size="small"
              onClick={() => onDelete(alert.id)}
              color="error"
            >
              <Delete />
            </IconButton>
          </Tooltip>
        </Box>
      </ListItemSecondaryAction>
    </ListItem>
  )
}

export const AlertPanel: React.FC<AlertPanelProps> = ({
  refreshInterval = 30000,
  maxAlerts = 50,
  showCreateButton = true,
  compact = false
}) => {
  const { showNotification } = useNotification()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [currentTab, setCurrentTab] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [severityFilter, setSeverityFilter] = useState<Alert['type'] | ''>('')
  const [createDialogOpen, setCreateDialogOpen] = useState(false)

  const fetchAlerts = async () => {
    try {
      const response = await dashboardApi.getAlerts(
        page,
        maxAlerts,
        severityFilter || undefined,
        currentTab === 1 // dismissed tab
      )
      
      setAlerts(response.alerts)
      setTotalPages(response.total_pages)
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
      showNotification('アラートの取得に失敗しました', 'error')
      setIsLoading(false)
    }
  }

  const handleDismissAlert = async (alertId: string) => {
    try {
      await dashboardApi.dismissAlert(alertId)
      showNotification('アラートを解除しました', 'success')
      fetchAlerts()
    } catch (error) {
      console.error('Failed to dismiss alert:', error)
      showNotification('アラートの解除に失敗しました', 'error')
    }
  }

  const handleDeleteAlert = async (alertId: string) => {
    // Note: This would require a delete endpoint in the API
    try {
      // await dashboardApi.deleteAlert(alertId)
      showNotification('アラート削除機能は準備中です', 'info')
    } catch (error) {
      console.error('Failed to delete alert:', error)
      showNotification('アラートの削除に失敗しました', 'error')
    }
  }

  const handleDismissAll = async () => {
    try {
      const result = await dashboardApi.dismissAllAlerts()
      showNotification(`${result.dismissed_count}件のアラートを解除しました`, 'success')
      fetchAlerts()
    } catch (error) {
      console.error('Failed to dismiss all alerts:', error)
      showNotification('アラートの一括解除に失敗しました', 'error')
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
    setPage(1)
  }

  const handleRefresh = () => {
    setIsLoading(true)
    fetchAlerts()
  }

  useEffect(() => {
    fetchAlerts()
  }, [page, currentTab, severityFilter])

  useEffect(() => {
    const interval = setInterval(() => {
      if (currentTab === 0) { // Only auto-refresh active alerts
        fetchAlerts()
      }
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [refreshInterval, currentTab, page, severityFilter])

  const activeAlerts = alerts.filter(alert => !alert.dismissed)
  const dismissedAlerts = alerts.filter(alert => alert.dismissed)

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h2">
          アラート・通知
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Badge badgeContent={activeAlerts.length} color="error" max={99}>
            <NotificationsActive />
          </Badge>
          
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <InputLabel>フィルタ</InputLabel>
            <Select
              value={severityFilter}
              label="フィルタ"
              onChange={(e) => setSeverityFilter(e.target.value as Alert['type'] | '')}
            >
              <MenuItem value="">すべて</MenuItem>
              <MenuItem value="error">エラー</MenuItem>
              <MenuItem value="warning">警告</MenuItem>
              <MenuItem value="info">情報</MenuItem>
              <MenuItem value="success">成功</MenuItem>
            </Select>
          </FormControl>

          <Tooltip title="更新">
            <IconButton onClick={handleRefresh} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>

          {showCreateButton && (
            <Button
              variant="outlined"
              startIcon={<Add />}
              onClick={() => setCreateDialogOpen(true)}
              size="small"
            >
              作成
            </Button>
          )}
        </Box>
      </Box>

      <Card>
        <Tabs value={currentTab} onChange={handleTabChange} variant="fullWidth">
          <Tab
            label={
              <Badge badgeContent={activeAlerts.length} color="error" max={99}>
                アクティブ
              </Badge>
            }
          />
          <Tab
            label={
              <Badge badgeContent={dismissedAlerts.length} color="default" max={99}>
                解除済み
              </Badge>
            }
          />
        </Tabs>

        <CardContent sx={{ p: 0 }}>
          {alerts.length === 0 ? (
            <Box textAlign="center" py={4}>
              <NotificationsOff color="disabled" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                {currentTab === 0 ? 'アクティブなアラートはありません' : '解除済みアラートはありません'}
              </Typography>
            </Box>
          ) : (
            <>
              <List sx={{ p: 0 }}>
                {alerts.map((alert) => (
                  <AlertItem
                    key={alert.id}
                    alert={alert}
                    onDismiss={handleDismissAlert}
                    onDelete={handleDeleteAlert}
                    compact={compact}
                  />
                ))}
              </List>

              {currentTab === 0 && activeAlerts.length > 0 && (
                <Box p={2} borderTop="1px solid" borderColor="divider">
                  <Button
                    variant="outlined"
                    startIcon={<VisibilityOff />}
                    onClick={handleDismissAll}
                    fullWidth
                  >
                    すべて解除
                  </Button>
                </Box>
              )}

              {totalPages > 1 && (
                <Box display="flex" justifyContent="center" p={2}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(event, value) => setPage(value)}
                    color="primary"
                  />
                </Box>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <CreateAlertDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSuccess={fetchAlerts}
      />
    </Box>
  )
}

export default AlertPanel