import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tooltip,
  Slider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material'
import {
  ExpandMore,
  Save,
  Restore,
  Download,
  Upload,
  Delete,
  Warning,
  Security,
  Speed,
  Storage,
  Settings,
  Refresh,
  Edit,
  Add,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import type { SystemConfiguration, BackupInfo, MaintenanceTask } from '../../../types/monitoring'
import { useNotification } from '../../common'

interface SystemSettingsProps {
  onSettingsChange?: (settings: Record<string, any>) => void
}

const systemConfigSchema = z.object({
  max_concurrent_drones: z.number().min(1).max(20),
  auto_backup_enabled: z.boolean(),
  backup_interval_hours: z.number().min(1).max(168),
  log_retention_days: z.number().min(1).max(365),
  max_log_size_mb: z.number().min(10).max(1000),
  session_timeout_minutes: z.number().min(5).max(480),
  max_upload_size_mb: z.number().min(1).max(100),
  enable_telemetry: z.boolean(),
  debug_mode: z.boolean(),
  api_rate_limit: z.number().min(10).max(1000),
  websocket_heartbeat_interval: z.number().min(5).max(60),
  model_inference_timeout: z.number().min(1).max(30),
  drone_connection_timeout: z.number().min(5).max(60),
  auto_land_battery_level: z.number().min(5).max(30),
  max_flight_altitude: z.number().min(5).max(120),
  emergency_return_enabled: z.boolean()
})

type SystemConfigForm = z.infer<typeof systemConfigSchema>

interface ConfigSectionProps {
  title: string
  description: string
  icon: React.ReactNode
  children: React.ReactNode
}

const ConfigSection: React.FC<ConfigSectionProps> = ({ title, description, icon, children }) => (
  <Accordion>
    <AccordionSummary expandIcon={<ExpandMore />}>
      <Box display="flex" alignItems="center" gap={2}>
        {icon}
        <Box>
          <Typography variant="h6">{title}</Typography>
          <Typography variant="body2" color="text.secondary">
            {description}
          </Typography>
        </Box>
      </Box>
    </AccordionSummary>
    <AccordionDetails>
      {children}
    </AccordionDetails>
  </Accordion>
)

interface BackupManagementProps {
  backups: BackupInfo[]
  onCreateBackup: () => void
  onRestoreBackup: (backupId: string) => void
  onDeleteBackup: (backupId: string) => void
}

const BackupManagement: React.FC<BackupManagementProps> = ({
  backups,
  onCreateBackup,
  onRestoreBackup,
  onDeleteBackup
}) => {
  const formatFileSize = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`
  }

  return (
    <Box>
      <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
        <Typography variant="h6">バックアップ管理</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={onCreateBackup}
        >
          バックアップ作成
        </Button>
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>作成日時</TableCell>
              <TableCell>タイプ</TableCell>
              <TableCell>サイズ</TableCell>
              <TableCell>ステータス</TableCell>
              <TableCell>説明</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {backups.map((backup) => (
              <TableRow key={backup.id}>
                <TableCell>
                  <Typography variant="body2">
                    {new Date(backup.created_at).toLocaleDateString('ja-JP')}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(backup.created_at).toLocaleTimeString('ja-JP')}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={backup.type === 'manual' ? '手動' : 
                          backup.type === 'scheduled' ? '自動' : '緊急'}
                    size="small"
                    color={backup.type === 'emergency' ? 'error' : 'default'}
                  />
                </TableCell>
                <TableCell>{formatFileSize(backup.size_bytes)}</TableCell>
                <TableCell>
                  <Chip
                    label={backup.status === 'completed' ? '完了' : 
                          backup.status === 'in_progress' ? '進行中' : '失敗'}
                    size="small"
                    color={backup.status === 'completed' ? 'success' : 
                           backup.status === 'in_progress' ? 'info' : 'error'}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" noWrap>
                    {backup.description}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    {backup.download_url && (
                      <Tooltip title="ダウンロード">
                        <IconButton
                          size="small"
                          onClick={() => window.open(backup.download_url, '_blank')}
                        >
                          <Download />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="復元">
                      <IconButton
                        size="small"
                        onClick={() => onRestoreBackup(backup.id)}
                        disabled={backup.status !== 'completed'}
                      >
                        <Restore />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="削除">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => onDeleteBackup(backup.id)}
                      >
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

interface MaintenanceTasksProps {
  tasks: MaintenanceTask[]
  onRunTask: (taskId: string) => void
}

const MaintenanceTasks: React.FC<MaintenanceTasksProps> = ({ tasks, onRunTask }) => (
  <Box>
    <Typography variant="h6" gutterBottom>
      メンテナンスタスク
    </Typography>
    
    <Grid container spacing={2}>
      {tasks.map((task) => (
        <Grid item xs={12} md={6} key={task.id}>
          <Card variant="outlined">
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="start" mb={2}>
                <Typography variant="h6">{task.name}</Typography>
                <Chip
                  label={task.status === 'completed' ? '完了' : 
                        task.status === 'running' ? '実行中' : 
                        task.status === 'failed' ? '失敗' : '待機中'}
                  size="small"
                  color={task.status === 'completed' ? 'success' : 
                         task.status === 'running' ? 'info' : 
                         task.status === 'failed' ? 'error' : 'default'}
                />
              </Box>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {task.description}
              </Typography>
              
              {task.last_success && (
                <Typography variant="caption" color="text.secondary" display="block">
                  最終成功: {new Date(task.last_success).toLocaleString('ja-JP')}
                </Typography>
              )}
              
              {task.next_run && (
                <Typography variant="caption" color="text.secondary" display="block">
                  次回実行: {new Date(task.next_run).toLocaleString('ja-JP')}
                </Typography>
              )}
              
              <Box mt={2}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => onRunTask(task.id)}
                  disabled={task.status === 'running'}
                >
                  今すぐ実行
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  </Box>
)

// Mock data
const mockBackups: BackupInfo[] = [
  {
    id: '1',
    type: 'manual',
    size_bytes: 1024 * 1024 * 150,
    created_at: new Date().toISOString(),
    description: '手動バックアップ',
    included_components: ['database', 'config', 'logs'],
    status: 'completed',
    download_url: '#',
    expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
  }
]

const mockMaintenanceTasks: MaintenanceTask[] = [
  {
    id: '1',
    name: 'ログクリーンアップ',
    description: '30日以上古いログファイルを削除します',
    type: 'cleanup',
    status: 'pending',
    scheduled_at: new Date().toISOString(),
    last_success: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    next_run: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: '2',
    name: 'データベース最適化',
    description: 'データベースのインデックスを再構築し、パフォーマンスを向上させます',
    type: 'optimization',
    status: 'completed',
    scheduled_at: new Date().toISOString(),
    last_success: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    next_run: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
  }
]

export const SystemSettings: React.FC<SystemSettingsProps> = ({
  onSettingsChange
}) => {
  const { showNotification } = useNotification()
  const [currentTab, setCurrentTab] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [backups] = useState<BackupInfo[]>(mockBackups)
  const [maintenanceTasks] = useState<MaintenanceTask[]>(mockMaintenanceTasks)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  const defaultValues: SystemConfigForm = {
    max_concurrent_drones: 10,
    auto_backup_enabled: true,
    backup_interval_hours: 24,
    log_retention_days: 30,
    max_log_size_mb: 100,
    session_timeout_minutes: 60,
    max_upload_size_mb: 10,
    enable_telemetry: true,
    debug_mode: false,
    api_rate_limit: 100,
    websocket_heartbeat_interval: 30,
    model_inference_timeout: 10,
    drone_connection_timeout: 30,
    auto_land_battery_level: 15,
    max_flight_altitude: 30,
    emergency_return_enabled: true
  }

  const { control, handleSubmit, watch, reset, formState: { errors } } = useForm<SystemConfigForm>({
    resolver: zodResolver(systemConfigSchema),
    defaultValues
  })

  const watchedValues = watch()

  useEffect(() => {
    const subscription = watch((value, { name, type }) => {
      if (type === 'change') {
        setHasUnsavedChanges(true)
      }
    })
    return () => subscription.unsubscribe()
  }, [watch])

  const onSubmit = async (data: SystemConfigForm) => {
    setIsLoading(true)
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      console.log('Settings saved:', data)
      onSettingsChange?.(data)
      setHasUnsavedChanges(false)
      
      showNotification('設定を保存しました', 'success')
    } catch (error) {
      console.error('Failed to save settings:', error)
      showNotification('設定の保存に失敗しました', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    reset(defaultValues)
    setHasUnsavedChanges(false)
    showNotification('設定をリセットしました', 'info')
  }

  const handleCreateBackup = async () => {
    try {
      showNotification('バックアップを作成中...', 'info')
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      showNotification('バックアップを作成しました', 'success')
    } catch (error) {
      showNotification('バックアップの作成に失敗しました', 'error')
    }
  }

  const handleRestoreBackup = async (backupId: string) => {
    try {
      showNotification('バックアップを復元中...', 'info')
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 3000))
      showNotification('バックアップを復元しました', 'success')
    } catch (error) {
      showNotification('バックアップの復元に失敗しました', 'error')
    }
  }

  const handleDeleteBackup = async (backupId: string) => {
    try {
      showNotification('バックアップを削除しました', 'success')
    } catch (error) {
      showNotification('バックアップの削除に失敗しました', 'error')
    }
  }

  const handleRunMaintenanceTask = async (taskId: string) => {
    try {
      showNotification('メンテナンスタスクを実行中...', 'info')
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      showNotification('メンテナンスタスクが完了しました', 'success')
    } catch (error) {
      showNotification('メンテナンスタスクの実行に失敗しました', 'error')
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h1">
          システム設定
        </Typography>
        <Box display="flex" gap={2}>
          {hasUnsavedChanges && (
            <Alert severity="warning" sx={{ py: 0 }}>
              未保存の変更があります
            </Alert>
          )}
          <Button
            variant="outlined"
            startIcon={<Restore />}
            onClick={handleReset}
            disabled={isLoading}
          >
            リセット
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSubmit(onSubmit)}
            disabled={isLoading || !hasUnsavedChanges}
          >
            保存
          </Button>
        </Box>
      </Box>

      <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)} sx={{ mb: 3 }}>
        <Tab label="基本設定" />
        <Tab label="ドローン設定" />
        <Tab label="セキュリティ" />
        <Tab label="バックアップ" />
        <Tab label="メンテナンス" />
      </Tabs>

      <Box role="tabpanel" hidden={currentTab !== 0}>
        {currentTab === 0 && (
          <Box component="form" onSubmit={handleSubmit(onSubmit)}>
            <ConfigSection
              title="システム設定"
              description="基本的なシステム動作設定"
              icon={<Settings color="primary" />}
            >
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Controller
                    name="max_concurrent_drones"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="最大同時接続ドローン数"
                        type="number"
                        fullWidth
                        error={!!errors.max_concurrent_drones}
                        helperText={errors.max_concurrent_drones?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Controller
                    name="session_timeout_minutes"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="セッションタイムアウト（分）"
                        type="number"
                        fullWidth
                        error={!!errors.session_timeout_minutes}
                        helperText={errors.session_timeout_minutes?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Controller
                    name="max_upload_size_mb"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="最大アップロードサイズ（MB）"
                        type="number"
                        fullWidth
                        error={!!errors.max_upload_size_mb}
                        helperText={errors.max_upload_size_mb?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Controller
                    name="api_rate_limit"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="API レート制限（リクエスト/分）"
                        type="number"
                        fullWidth
                        error={!!errors.api_rate_limit}
                        helperText={errors.api_rate_limit?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Controller
                    name="enable_telemetry"
                    control={control}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="テレメトリデータ収集を有効にする"
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Controller
                    name="debug_mode"
                    control={control}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="デバッグモードを有効にする"
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </ConfigSection>

            <ConfigSection
              title="ログ設定"
              description="ログの保存と管理設定"
              icon={<Storage color="info" />}
            >
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Controller
                    name="log_retention_days"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="ログ保持期間（日）"
                        type="number"
                        fullWidth
                        error={!!errors.log_retention_days}
                        helperText={errors.log_retention_days?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Controller
                    name="max_log_size_mb"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="最大ログサイズ（MB）"
                        type="number"
                        fullWidth
                        error={!!errors.max_log_size_mb}
                        helperText={errors.max_log_size_mb?.message}
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </ConfigSection>
          </Box>
        )}
      </Box>

      <Box role="tabpanel" hidden={currentTab !== 1}>
        {currentTab === 1 && (
          <ConfigSection
            title="ドローン設定"
            description="ドローンの動作と安全設定"
            icon={<Speed color="secondary" />}
          >
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="drone_connection_timeout"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="接続タイムアウト（秒）"
                      type="number"
                      fullWidth
                      error={!!errors.drone_connection_timeout}
                      helperText={errors.drone_connection_timeout?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="auto_land_battery_level"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="自動着陸バッテリーレベル（%）"
                      type="number"
                      fullWidth
                      error={!!errors.auto_land_battery_level}
                      helperText={errors.auto_land_battery_level?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="max_flight_altitude"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="最大飛行高度（m）"
                      type="number"
                      fullWidth
                      error={!!errors.max_flight_altitude}
                      helperText={errors.max_flight_altitude?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="emergency_return_enabled"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch {...field} checked={field.value} />}
                      label="緊急帰還機能を有効にする"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </ConfigSection>
        )}
      </Box>

      <Box role="tabpanel" hidden={currentTab !== 2}>
        {currentTab === 2 && (
          <ConfigSection
            title="セキュリティ設定"
            description="認証とセキュリティ関連の設定"
            icon={<Security color="warning" />}
          >
            <Alert severity="info" sx={{ mb: 3 }}>
              セキュリティ設定の変更は慎重に行ってください。不適切な設定はシステムの安全性に影響を与える可能性があります。
            </Alert>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="websocket_heartbeat_interval"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="WebSocketハートビート間隔（秒）"
                      type="number"
                      fullWidth
                      error={!!errors.websocket_heartbeat_interval}
                      helperText={errors.websocket_heartbeat_interval?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="model_inference_timeout"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="モデル推論タイムアウト（秒）"
                      type="number"
                      fullWidth
                      error={!!errors.model_inference_timeout}
                      helperText={errors.model_inference_timeout?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>
          </ConfigSection>
        )}
      </Box>

      <Box role="tabpanel" hidden={currentTab !== 3}>
        {currentTab === 3 && (
          <Box>
            <ConfigSection
              title="自動バックアップ設定"
              description="システムの自動バックアップ設定"
              icon={<Download color="success" />}
            >
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Controller
                    name="auto_backup_enabled"
                    control={control}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="自動バックアップを有効にする"
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Controller
                    name="backup_interval_hours"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="バックアップ間隔（時間）"
                        type="number"
                        fullWidth
                        disabled={!watchedValues.auto_backup_enabled}
                        error={!!errors.backup_interval_hours}
                        helperText={errors.backup_interval_hours?.message}
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </ConfigSection>

            <Box mt={3}>
              <BackupManagement
                backups={backups}
                onCreateBackup={handleCreateBackup}
                onRestoreBackup={handleRestoreBackup}
                onDeleteBackup={handleDeleteBackup}
              />
            </Box>
          </Box>
        )}
      </Box>

      <Box role="tabpanel" hidden={currentTab !== 4}>
        {currentTab === 4 && (
          <MaintenanceTasks
            tasks={maintenanceTasks}
            onRunTask={handleRunMaintenanceTask}
          />
        )}
      </Box>
    </Box>
  )
}

export default SystemSettings