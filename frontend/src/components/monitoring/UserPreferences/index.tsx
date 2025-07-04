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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Avatar,
  Divider,
  Alert,
  FormGroup,
  RadioGroup,
  Radio,
  FormLabel,
  Checkbox,
  IconButton,
  Tooltip,
  Stack,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material'
import {
  ExpandMore,
  Save,
  Restore,
  Palette,
  Language,
  Notifications,
  Camera,
  FlightTakeoff,
  ViewModule,
  Schedule,
  Person,
  Download,
  Upload,
  Delete,
  Edit,
  Visibility,
  VolumeUp,
  VolumeOff,
  DarkMode,
  LightMode,
  SettingsBrightness
} from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import type { UserPreferences as UserPreferencesType } from '../../../types/monitoring'
import { useNotification } from '../../common'

interface UserPreferencesProps {
  userId: string
  onPreferencesChange?: (preferences: Partial<UserPreferencesType>) => void
}

const userPreferencesSchema = z.object({
  theme: z.enum(['light', 'dark', 'auto']),
  language: z.enum(['ja', 'en']),
  timezone: z.string(),
  notification_settings: z.object({
    email_enabled: z.boolean(),
    push_enabled: z.boolean(),
    sound_enabled: z.boolean(),
    severity_filter: z.array(z.enum(['info', 'warning', 'error']))
  }),
  camera_settings: z.object({
    default_resolution: z.string(),
    default_fps: z.number().min(1).max(60),
    auto_record: z.boolean(),
    quality_preset: z.enum(['low', 'medium', 'high', 'ultra'])
  }),
  drone_settings: z.object({
    default_flight_height: z.number().min(1).max(100),
    max_flight_distance: z.number().min(10).max(500),
    auto_return_battery_level: z.number().min(5).max(50),
    emergency_action: z.enum(['land', 'return_home', 'hover'])
  }),
  table_settings: z.object({
    page_size: z.number().min(10).max(100),
    auto_refresh_interval: z.number().min(5).max(300),
    density: z.enum(['compact', 'standard', 'comfortable'])
  })
})

type UserPreferencesForm = z.infer<typeof userPreferencesSchema>

interface PreferenceSectionProps {
  title: string
  description: string
  icon: React.ReactNode
  children: React.ReactNode
}

const PreferenceSection: React.FC<PreferenceSectionProps> = ({ 
  title, 
  description, 
  icon, 
  children 
}) => (
  <Accordion defaultExpanded>
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

const resolutionOptions = [
  { value: '720p', label: '720p (1280x720)' },
  { value: '1080p', label: '1080p (1920x1080)' },
  { value: '4K', label: '4K (3840x2160)' }
]

const timezoneOptions = [
  { value: 'Asia/Tokyo', label: '日本標準時 (JST)' },
  { value: 'UTC', label: '協定世界時 (UTC)' },
  { value: 'America/New_York', label: '東部標準時 (EST)' },
  { value: 'Europe/London', label: 'グリニッジ標準時 (GMT)' }
]

export const UserPreferences: React.FC<UserPreferencesProps> = ({
  userId,
  onPreferencesChange
}) => {
  const { showNotification } = useNotification()
  const [isLoading, setIsLoading] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  const defaultValues: UserPreferencesForm = {
    theme: 'auto',
    language: 'ja',
    timezone: 'Asia/Tokyo',
    notification_settings: {
      email_enabled: true,
      push_enabled: true,
      sound_enabled: false,
      severity_filter: ['warning', 'error']
    },
    camera_settings: {
      default_resolution: '1080p',
      default_fps: 30,
      auto_record: false,
      quality_preset: 'high'
    },
    drone_settings: {
      default_flight_height: 20,
      max_flight_distance: 100,
      auto_return_battery_level: 20,
      emergency_action: 'land'
    },
    table_settings: {
      page_size: 20,
      auto_refresh_interval: 30,
      density: 'standard'
    }
  }

  const { control, handleSubmit, watch, reset, formState: { errors } } = useForm<UserPreferencesForm>({
    resolver: zodResolver(userPreferencesSchema),
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

  const onSubmit = async (data: UserPreferencesForm) => {
    setIsLoading(true)
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      console.log('User preferences saved:', data)
      onPreferencesChange?.(data)
      setHasUnsavedChanges(false)
      
      showNotification('ユーザー設定を保存しました', 'success')
    } catch (error) {
      console.error('Failed to save user preferences:', error)
      showNotification('ユーザー設定の保存に失敗しました', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    reset(defaultValues)
    setHasUnsavedChanges(false)
    showNotification('ユーザー設定をリセットしました', 'info')
  }

  const handleExportPreferences = () => {
    const dataStr = JSON.stringify(watchedValues, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `user-preferences-${userId}-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)

    showNotification('ユーザー設定をエクスポートしました', 'success')
  }

  const handleImportPreferences = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target?.result as string)
        // Validate imported data against schema
        const validated = userPreferencesSchema.parse(imported)
        reset(validated)
        setHasUnsavedChanges(true)
        
        showNotification('ユーザー設定をインポートしました', 'success')
      } catch (error) {
        console.error('Failed to import preferences:', error)
        showNotification('ユーザー設定のインポートに失敗しました', 'error')
      }
    }
    reader.readAsText(file)
    
    // Reset input value
    event.target.value = ''
  }

  const getThemeIcon = (theme: string) => {
    switch (theme) {
      case 'light':
        return <LightMode />
      case 'dark':
        return <DarkMode />
      default:
        return <SettingsBrightness />
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <Avatar>
            <Person />
          </Avatar>
          <Box>
            <Typography variant="h5" component="h1">
              ユーザー設定
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ユーザーID: {userId}
            </Typography>
          </Box>
        </Box>
        
        <Box display="flex" gap={2}>
          {hasUnsavedChanges && (
            <Alert severity="warning" sx={{ py: 0 }}>
              未保存の変更があります
            </Alert>
          )}
          <Button
            variant="outlined"
            startIcon={<Upload />}
            component="label"
          >
            インポート
            <input
              type="file"
              accept=".json"
              hidden
              onChange={handleImportPreferences}
            />
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleExportPreferences}
          >
            エクスポート
          </Button>
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

      <Box component="form" onSubmit={handleSubmit(onSubmit)}>
        <PreferenceSection
          title="外観設定"
          description="テーマ、言語、タイムゾーンの設定"
          icon={<Palette color="primary" />}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Controller
                name="theme"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <FormLabel>テーマ</FormLabel>
                    <RadioGroup {...field} row>
                      <FormControlLabel
                        value="light"
                        control={<Radio />}
                        label={
                          <Box display="flex" alignItems="center" gap={1}>
                            <LightMode fontSize="small" />
                            ライト
                          </Box>
                        }
                      />
                      <FormControlLabel
                        value="dark"
                        control={<Radio />}
                        label={
                          <Box display="flex" alignItems="center" gap={1}>
                            <DarkMode fontSize="small" />
                            ダーク
                          </Box>
                        }
                      />
                      <FormControlLabel
                        value="auto"
                        control={<Radio />}
                        label={
                          <Box display="flex" alignItems="center" gap={1}>
                            <SettingsBrightness fontSize="small" />
                            自動
                          </Box>
                        }
                      />
                    </RadioGroup>
                  </FormControl>
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Controller
                name="language"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>言語</InputLabel>
                    <Select {...field} label="言語">
                      <MenuItem value="ja">日本語</MenuItem>
                      <MenuItem value="en">English</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Controller
                name="timezone"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>タイムゾーン</InputLabel>
                    <Select {...field} label="タイムゾーン">
                      {timezoneOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
          </Grid>
        </PreferenceSection>

        <PreferenceSection
          title="通知設定"
          description="アラートと通知の受信設定"
          icon={<Notifications color="secondary" />}
        >
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                通知方法
              </Typography>
              <FormGroup row>
                <Controller
                  name="notification_settings.email_enabled"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Checkbox {...field} checked={field.value} />}
                      label="メール通知"
                    />
                  )}
                />
                <Controller
                  name="notification_settings.push_enabled"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Checkbox {...field} checked={field.value} />}
                      label="プッシュ通知"
                    />
                  )}
                />
                <Controller
                  name="notification_settings.sound_enabled"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Checkbox {...field} checked={field.value} />}
                      label="サウンド通知"
                    />
                  )}
                />
              </FormGroup>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                通知レベル
              </Typography>
              <FormGroup row>
                <Controller
                  name="notification_settings.severity_filter"
                  control={control}
                  render={({ field }) => (
                    <>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={field.value.includes('info')}
                            onChange={(e) => {
                              const newValue = e.target.checked
                                ? [...field.value, 'info']
                                : field.value.filter(v => v !== 'info')
                              field.onChange(newValue)
                            }}
                          />
                        }
                        label="情報"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={field.value.includes('warning')}
                            onChange={(e) => {
                              const newValue = e.target.checked
                                ? [...field.value, 'warning']
                                : field.value.filter(v => v !== 'warning')
                              field.onChange(newValue)
                            }}
                          />
                        }
                        label="警告"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={field.value.includes('error')}
                            onChange={(e) => {
                              const newValue = e.target.checked
                                ? [...field.value, 'error']
                                : field.value.filter(v => v !== 'error')
                              field.onChange(newValue)
                            }}
                          />
                        }
                        label="エラー"
                      />
                    </>
                  )}
                />
              </FormGroup>
            </Grid>
          </Grid>
        </PreferenceSection>

        <PreferenceSection
          title="カメラ設定"
          description="デフォルトのカメラ設定"
          icon={<Camera color="info" />}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Controller
                name="camera_settings.default_resolution"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>デフォルト解像度</InputLabel>
                    <Select {...field} label="デフォルト解像度">
                      {resolutionOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Controller
                name="camera_settings.quality_preset"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>品質プリセット</InputLabel>
                    <Select {...field} label="品質プリセット">
                      <MenuItem value="low">低品質</MenuItem>
                      <MenuItem value="medium">標準品質</MenuItem>
                      <MenuItem value="high">高品質</MenuItem>
                      <MenuItem value="ultra">最高品質</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography gutterBottom>
                フレームレート: {watchedValues.camera_settings.default_fps} FPS
              </Typography>
              <Controller
                name="camera_settings.default_fps"
                control={control}
                render={({ field }) => (
                  <Slider
                    {...field}
                    min={1}
                    max={60}
                    step={1}
                    marks={[
                      { value: 15, label: '15' },
                      { value: 30, label: '30' },
                      { value: 60, label: '60' }
                    ]}
                    valueLabelDisplay="auto"
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Controller
                name="camera_settings.auto_record"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={<Switch {...field} checked={field.value} />}
                    label="飛行時の自動録画"
                  />
                )}
              />
            </Grid>
          </Grid>
        </PreferenceSection>

        <PreferenceSection
          title="ドローン設定"
          description="ドローンの動作設定"
          icon={<FlightTakeoff color="warning" />}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Controller
                name="drone_settings.default_flight_height"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="デフォルト飛行高度（m）"
                    type="number"
                    fullWidth
                    error={!!errors.drone_settings?.default_flight_height}
                    helperText={errors.drone_settings?.default_flight_height?.message}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Controller
                name="drone_settings.max_flight_distance"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="最大飛行距離（m）"
                    type="number"
                    fullWidth
                    error={!!errors.drone_settings?.max_flight_distance}
                    helperText={errors.drone_settings?.max_flight_distance?.message}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Controller
                name="drone_settings.auto_return_battery_level"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="自動帰還バッテリーレベル（%）"
                    type="number"
                    fullWidth
                    error={!!errors.drone_settings?.auto_return_battery_level}
                    helperText={errors.drone_settings?.auto_return_battery_level?.message}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Controller
                name="drone_settings.emergency_action"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>緊急時の動作</InputLabel>
                    <Select {...field} label="緊急時の動作">
                      <MenuItem value="land">着陸</MenuItem>
                      <MenuItem value="return_home">ホームに帰還</MenuItem>
                      <MenuItem value="hover">ホバリング</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
          </Grid>
        </PreferenceSection>

        <PreferenceSection
          title="テーブル設定"
          description="データ表示とリフレッシュ設定"
          icon={<ViewModule color="success" />}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Controller
                name="table_settings.page_size"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="ページサイズ"
                    type="number"
                    fullWidth
                    error={!!errors.table_settings?.page_size}
                    helperText={errors.table_settings?.page_size?.message}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Controller
                name="table_settings.auto_refresh_interval"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="自動更新間隔（秒）"
                    type="number"
                    fullWidth
                    error={!!errors.table_settings?.auto_refresh_interval}
                    helperText={errors.table_settings?.auto_refresh_interval?.message}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Controller
                name="table_settings.density"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>表示密度</InputLabel>
                    <Select {...field} label="表示密度">
                      <MenuItem value="compact">コンパクト</MenuItem>
                      <MenuItem value="standard">標準</MenuItem>
                      <MenuItem value="comfortable">ゆったり</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
          </Grid>
        </PreferenceSection>
      </Box>
    </Box>
  )
}

export default UserPreferences