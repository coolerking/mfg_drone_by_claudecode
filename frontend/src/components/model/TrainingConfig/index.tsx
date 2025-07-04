import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Box,
  Typography,
  Grid,
  FormControlLabel,
  Switch,
  Slider,
  Paper,
  Divider,
  Alert,
  FormHelperText,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import { LoadingButton } from '@mui/lab'
import { ExpandMore, Info, TuneSharp } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState, useEffect } from 'react'
import { useNotification } from '@/hooks/useNotification'
import { modelApi, type Model, type TrainingConfig as TrainingConfigType } from '@/services/api/modelApi'
import { visionApi } from '@/services/api/visionApi'

const trainingConfigSchema = z.object({
  dataset_id: z.string().min(1, '学習データセットは必須です'),
  validation_dataset_id: z.string().optional(),
  model_type: z.enum(['yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x']),
  epochs: z.number().min(1, 'エポック数は1以上で指定してください').max(1000, 'エポック数は1000以下で指定してください'),
  batch_size: z.number().min(1, 'バッチサイズは1以上で指定してください').max(64, 'バッチサイズは64以下で指定してください'),
  learning_rate: z.number().min(0.0001, '学習率は0.0001以上で指定してください').max(1, '学習率は1以下で指定してください'),
  image_size: z.number().min(320, '画像サイズは320以上で指定してください').max(1280, '画像サイズは1280以下で指定してください'),
  patience: z.number().min(1, 'Patienceは1以上で指定してください').max(100, 'Patienceは100以下で指定してください'),
  save_period: z.number().min(1, '保存間隔は1以上で指定してください').max(100, '保存間隔は100以下で指定してください'),
  augment: z.boolean(),
  mosaic: z.boolean(),
  mixup: z.boolean(),
  copy_paste: z.boolean()
})

type TrainingConfigFormData = z.infer<typeof trainingConfigSchema>

interface TrainingConfigModalProps {
  open: boolean
  onClose: () => void
  onStartTraining: (modelName: string, config: TrainingConfigType) => void
  model?: Model
}

interface Dataset {
  id: string
  name: string
  image_count: number
  status: string
}

const modelTypeInfo = {
  yolov8n: { name: 'YOLOv8 Nano', size: '6MB', speed: '最速', accuracy: '低' },
  yolov8s: { name: 'YOLOv8 Small', size: '22MB', speed: '高速', accuracy: '中' },
  yolov8m: { name: 'YOLOv8 Medium', size: '52MB', speed: '中', accuracy: '高' },
  yolov8l: { name: 'YOLOv8 Large', size: '88MB', speed: '低', accuracy: '非常に高' },
  yolov8x: { name: 'YOLOv8 Extra Large', size: '136MB', speed: '最低', accuracy: '最高' }
}

export function TrainingConfig({ open, onClose, onStartTraining, model }: TrainingConfigModalProps) {
  const { showNotification } = useNotification()
  const [loading, setLoading] = useState(false)
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [estimatedTime, setEstimatedTime] = useState<string>('')

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
    setValue
  } = useForm<TrainingConfigFormData>({
    resolver: zodResolver(trainingConfigSchema),
    defaultValues: {
      dataset_id: '',
      validation_dataset_id: '',
      model_type: 'yolov8s',
      epochs: 100,
      batch_size: 16,
      learning_rate: 0.01,
      image_size: 640,
      patience: 50,
      save_period: 10,
      augment: true,
      mosaic: true,
      mixup: false,
      copy_paste: false
    }
  })

  const watchedValues = watch()

  useEffect(() => {
    if (open) {
      fetchDatasets()
    }
  }, [open])

  useEffect(() => {
    // Estimate training time based on configuration
    const epochs = watchedValues.epochs
    const batchSize = watchedValues.batch_size
    const imageSize = watchedValues.image_size
    const modelType = watchedValues.model_type

    // Simple estimation formula (this would be more sophisticated in real implementation)
    const baseTimePerEpoch = (imageSize / 640) * (batchSize / 16) * 
      (modelType === 'yolov8n' ? 1 : modelType === 'yolov8s' ? 1.5 : 
       modelType === 'yolov8m' ? 2.5 : modelType === 'yolov8l' ? 4 : 6)

    const totalMinutes = epochs * baseTimePerEpoch
    
    if (totalMinutes < 60) {
      setEstimatedTime(`約 ${Math.round(totalMinutes)} 分`)
    } else if (totalMinutes < 1440) {
      const hours = Math.round(totalMinutes / 60 * 10) / 10
      setEstimatedTime(`約 ${hours} 時間`)
    } else {
      const days = Math.round(totalMinutes / 1440 * 10) / 10
      setEstimatedTime(`約 ${days} 日`)
    }
  }, [watchedValues.epochs, watchedValues.batch_size, watchedValues.image_size, watchedValues.model_type])

  const fetchDatasets = async () => {
    try {
      const response = await visionApi.getDatasets()
      setDatasets(response.filter(d => d.status === 'ready'))
    } catch (error) {
      console.error('Error fetching datasets:', error)
      showNotification('error', 'データセットの取得に失敗しました')
    }
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  const onSubmit = async (data: TrainingConfigFormData) => {
    try {
      setLoading(true)
      
      const modelName = model ? `${model.name}_retrained_${Date.now()}` : `new_model_${Date.now()}`
      
      await onStartTraining(modelName, data)
      
      showNotification('success', '学習を開始しました')
      handleClose()
    } catch (error) {
      console.error('Error starting training:', error)
      showNotification('error', '学習の開始に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const getRecommendedBatchSize = (modelType: TrainingConfigFormData['model_type']) => {
    switch (modelType) {
      case 'yolov8n':
        return 32
      case 'yolov8s':
        return 16
      case 'yolov8m':
        return 8
      case 'yolov8l':
        return 4
      case 'yolov8x':
        return 2
      default:
        return 16
    }
  }

  const handleModelTypeChange = (newType: TrainingConfigFormData['model_type']) => {
    setValue('batch_size', getRecommendedBatchSize(newType))
  }

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { minHeight: '80vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <TuneSharp />
          学習設定
          {model && (
            <Typography variant="body2" color="text.secondary">
              - {model.name}
            </Typography>
          )}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box component="form" noValidate sx={{ mt: 1 }}>
          <Grid container spacing={3}>
            {/* Dataset Selection */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                データセット設定
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Controller
                name="dataset_id"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.dataset_id}>
                    <InputLabel>学習データセット *</InputLabel>
                    <Select
                      {...field}
                      label="学習データセット *"
                    >
                      {datasets.map((dataset) => (
                        <MenuItem key={dataset.id} value={dataset.id}>
                          {dataset.name} ({dataset.image_count} 枚)
                        </MenuItem>
                      ))}
                    </Select>
                    {errors.dataset_id && (
                      <FormHelperText>{errors.dataset_id.message}</FormHelperText>
                    )}
                  </FormControl>
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Controller
                name="validation_dataset_id"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>検証データセット（任意）</InputLabel>
                    <Select
                      {...field}
                      label="検証データセット（任意）"
                    >
                      <MenuItem value="">なし</MenuItem>
                      {datasets.map((dataset) => (
                        <MenuItem key={dataset.id} value={dataset.id}>
                          {dataset.name} ({dataset.image_count} 枚)
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>

            {/* Model Configuration */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                モデル設定
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Controller
                name="model_type"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.model_type}>
                    <InputLabel>YOLOモデルタイプ</InputLabel>
                    <Select
                      {...field}
                      label="YOLOモデルタイプ"
                      onChange={(e) => {
                        field.onChange(e)
                        handleModelTypeChange(e.target.value as TrainingConfigFormData['model_type'])
                      }}
                    >
                      {Object.entries(modelTypeInfo).map(([value, info]) => (
                        <MenuItem key={value} value={value}>
                          <Box>
                            <Typography>{info.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              サイズ: {info.size} | 速度: {info.speed} | 精度: {info.accuracy}
                            </Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                    {errors.model_type && (
                      <FormHelperText>{errors.model_type.message}</FormHelperText>
                    )}
                  </FormControl>
                )}
              />
            </Grid>

            {/* Training Parameters */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                学習パラメータ
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Controller
                name="epochs"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    type="number"
                    label="エポック数"
                    error={!!errors.epochs}
                    helperText={errors.epochs?.message || '推奨: 100-300'}
                    inputProps={{ min: 1, max: 1000 }}
                    onChange={(e) => field.onChange(parseInt(e.target.value, 10))}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Controller
                name="batch_size"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    type="number"
                    label="バッチサイズ"
                    error={!!errors.batch_size}
                    helperText={errors.batch_size?.message || `推奨: ${getRecommendedBatchSize(watchedValues.model_type)}`}
                    inputProps={{ min: 1, max: 64 }}
                    onChange={(e) => field.onChange(parseInt(e.target.value, 10))}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Controller
                name="learning_rate"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    type="number"
                    label="学習率"
                    error={!!errors.learning_rate}
                    helperText={errors.learning_rate?.message || '推奨: 0.01'}
                    inputProps={{ min: 0.0001, max: 1, step: 0.001 }}
                    onChange={(e) => field.onChange(parseFloat(e.target.value))}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                画像サイズ: {watchedValues.image_size}px
              </Typography>
              <Controller
                name="image_size"
                control={control}
                render={({ field }) => (
                  <Slider
                    {...field}
                    min={320}
                    max={1280}
                    step={32}
                    valueLabelDisplay="auto"
                    marks={[
                      { value: 320, label: '320' },
                      { value: 640, label: '640' },
                      { value: 1280, label: '1280' }
                    ]}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={3}>
              <Controller
                name="patience"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    type="number"
                    label="Patience"
                    error={!!errors.patience}
                    helperText={errors.patience?.message || '早期終了の忍耐度'}
                    inputProps={{ min: 1, max: 100 }}
                    onChange={(e) => field.onChange(parseInt(e.target.value, 10))}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={3}>
              <Controller
                name="save_period"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    type="number"
                    label="保存間隔"
                    error={!!errors.save_period}
                    helperText={errors.save_period?.message || 'エポック間隔'}
                    inputProps={{ min: 1, max: 100 }}
                    onChange={(e) => field.onChange(parseInt(e.target.value, 10))}
                  />
                )}
              />
            </Grid>

            {/* Data Augmentation */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">データ拡張設定</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Controller
                        name="augment"
                        control={control}
                        render={({ field }) => (
                          <FormControlLabel
                            control={<Switch {...field} checked={field.value} />}
                            label="基本的なデータ拡張"
                          />
                        )}
                      />
                      <Typography variant="caption" display="block" color="text.secondary">
                        回転、反転、色調変更などの基本的な拡張
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Controller
                        name="mosaic"
                        control={control}
                        render={({ field }) => (
                          <FormControlLabel
                            control={<Switch {...field} checked={field.value} />}
                            label="Mosaic拡張"
                          />
                        )}
                      />
                      <Typography variant="caption" display="block" color="text.secondary">
                        4つの画像を1つにまとめる拡張技法
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Controller
                        name="mixup"
                        control={control}
                        render={({ field }) => (
                          <FormControlLabel
                            control={<Switch {...field} checked={field.value} />}
                            label="MixUp拡張"
                          />
                        )}
                      />
                      <Typography variant="caption" display="block" color="text.secondary">
                        2つの画像を混合する拡張技法
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Controller
                        name="copy_paste"
                        control={control}
                        render={({ field }) => (
                          <FormControlLabel
                            control={<Switch {...field} checked={field.value} />}
                            label="Copy-Paste拡張"
                          />
                        )}
                      />
                      <Typography variant="caption" display="block" color="text.secondary">
                        物体をコピーして他の画像に貼り付ける拡張
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Training Summary */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="h6" gutterBottom>
                  学習設定サマリー
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2">
                      <strong>モデル:</strong> {modelTypeInfo[watchedValues.model_type].name}
                    </Typography>
                    <Typography variant="body2">
                      <strong>推定学習時間:</strong> {estimatedTime}
                    </Typography>
                    <Typography variant="body2">
                      <strong>画像サイズ:</strong> {watchedValues.image_size}x{watchedValues.image_size}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2">
                      <strong>エポック数:</strong> {watchedValues.epochs}
                    </Typography>
                    <Typography variant="body2">
                      <strong>バッチサイズ:</strong> {watchedValues.batch_size}
                    </Typography>
                    <Typography variant="body2">
                      <strong>学習率:</strong> {watchedValues.learning_rate}
                    </Typography>
                  </Grid>
                </Grid>
                
                {estimatedTime && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      推定学習時間: {estimatedTime}
                      <br />
                      実際の時間はハードウェア性能やデータセットサイズによって変動します。
                    </Typography>
                  </Alert>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={handleClose} disabled={loading}>
          キャンセル
        </Button>
        <LoadingButton
          onClick={handleSubmit(onSubmit)}
          loading={loading}
          variant="contained"
          disabled={loading}
        >
          学習開始
        </LoadingButton>
      </DialogActions>
    </Dialog>
  )
}