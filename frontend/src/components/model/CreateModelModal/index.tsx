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
  Chip,
  Grid,
  FormHelperText,
  Autocomplete
} from '@mui/material'
import { LoadingButton } from '@mui/lab'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'
import { useNotification } from '@/hooks/useNotification'
import { modelApi, type Model } from '@/services/api/modelApi'

const createModelSchema = z.object({
  name: z.string()
    .min(1, 'モデル名は必須です')
    .max(100, 'モデル名は100文字以内で入力してください')
    .regex(/^[a-zA-Z0-9_\-\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+$/, '無効な文字が含まれています'),
  description: z.string()
    .max(500, '説明は500文字以内で入力してください')
    .optional(),
  type: z.enum(['yolo', 'custom', 'pretrained']),
  version: z.string()
    .min(1, 'バージョンは必須です')
    .regex(/^\d+\.\d+\.\d+$/, 'バージョンは x.y.z 形式で入力してください'),
  classes: z.array(z.string())
    .min(1, '少なくとも1つのクラスを指定してください')
    .max(100, 'クラス数は100個以下にしてください'),
  training_epochs: z.number()
    .min(1, 'エポック数は1以上で指定してください')
    .max(1000, 'エポック数は1000以下で指定してください')
})

type CreateModelFormData = z.infer<typeof createModelSchema>

interface CreateModelModalProps {
  open: boolean
  onClose: () => void
  onSuccess: (model: Model) => void
}

const predefinedClasses = [
  'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
  'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
  'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
  'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
  'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
  'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
  'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
  'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
  'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
  'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
  'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
  'toothbrush'
]

export function CreateModelModal({ open, onClose, onSuccess }: CreateModelModalProps) {
  const { showNotification } = useNotification()
  const [loading, setLoading] = useState(false)

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
    setValue
  } = useForm<CreateModelFormData>({
    resolver: zodResolver(createModelSchema),
    defaultValues: {
      name: '',
      description: '',
      type: 'yolo',
      version: '1.0.0',
      classes: [],
      training_epochs: 50
    }
  })

  const watchedType = watch('type')

  const handleClose = () => {
    reset()
    onClose()
  }

  const onSubmit = async (data: CreateModelFormData) => {
    try {
      setLoading(true)
      
      const modelData = {
        name: data.name,
        description: data.description,
        type: data.type,
        status: 'training' as const,
        version: data.version,
        classes: data.classes,
        training_epochs: data.training_epochs
      }

      const newModel = await modelApi.createModel(modelData)
      
      showNotification('success', 'モデルが作成されました')
      onSuccess(newModel)
      handleClose()
    } catch (error) {
      console.error('Error creating model:', error)
      showNotification('error', 'モデルの作成に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleAddClass = (newClass: string) => {
    const currentClasses = watch('classes')
    if (newClass && !currentClasses.includes(newClass)) {
      setValue('classes', [...currentClasses, newClass])
    }
  }

  const handleRemoveClass = (classToRemove: string) => {
    const currentClasses = watch('classes')
    setValue('classes', currentClasses.filter(c => c !== classToRemove))
  }

  const getTypeDescription = (type: Model['type']) => {
    switch (type) {
      case 'yolo':
        return 'YOLOv8ベースの物体検出モデル。リアルタイム検出に最適。'
      case 'custom':
        return 'カスタムアーキテクチャのモデル。特殊用途向け。'
      case 'pretrained':
        return '事前学習済みモデル。すぐに使用可能。'
      default:
        return ''
    }
  }

  const getRecommendedEpochs = (type: Model['type']) => {
    switch (type) {
      case 'yolo':
        return 100
      case 'custom':
        return 50
      case 'pretrained':
        return 20
      default:
        return 50
    }
  }

  const handleTypeChange = (newType: Model['type']) => {
    setValue('training_epochs', getRecommendedEpochs(newType))
  }

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' }
      }}
    >
      <DialogTitle>
        新規モデル作成
      </DialogTitle>
      
      <DialogContent>
        <Box component="form" noValidate sx={{ mt: 1 }}>
          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                基本情報
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <Controller
                name="name"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="モデル名"
                    error={!!errors.name}
                    helperText={errors.name?.message}
                    placeholder="例: YOLO_PersonDetection_v1"
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Controller
                name="version"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="バージョン"
                    error={!!errors.version}
                    helperText={errors.version?.message}
                    placeholder="1.0.0"
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    multiline
                    rows={3}
                    label="説明（任意）"
                    error={!!errors.description}
                    helperText={errors.description?.message}
                    placeholder="このモデルの目的や特徴を説明してください..."
                  />
                )}
              />
            </Grid>

            {/* Model Configuration */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                モデル設定
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Controller
                name="type"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.type}>
                    <InputLabel>モデルタイプ</InputLabel>
                    <Select
                      {...field}
                      label="モデルタイプ"
                      onChange={(e) => {
                        field.onChange(e)
                        handleTypeChange(e.target.value as Model['type'])
                      }}
                    >
                      <MenuItem value="yolo">YOLO</MenuItem>
                      <MenuItem value="custom">カスタム</MenuItem>
                      <MenuItem value="pretrained">事前学習済み</MenuItem>
                    </Select>
                    {errors.type && (
                      <FormHelperText>{errors.type.message}</FormHelperText>
                    )}
                  </FormControl>
                )}
              />
              {watchedType && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {getTypeDescription(watchedType)}
                </Typography>
              )}
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Controller
                name="training_epochs"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    type="number"
                    label="学習エポック数"
                    error={!!errors.training_epochs}
                    helperText={errors.training_epochs?.message || `推奨: ${getRecommendedEpochs(watchedType)}エポック`}
                    inputProps={{ min: 1, max: 1000 }}
                    onChange={(e) => field.onChange(parseInt(e.target.value, 10))}
                  />
                )}
              />
            </Grid>

            {/* Classes Configuration */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                検出クラス設定
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Controller
                name="classes"
                control={control}
                render={({ field }) => (
                  <Autocomplete
                    multiple
                    freeSolo
                    options={predefinedClasses}
                    value={field.value}
                    onChange={(_, newValue) => {
                      field.onChange(newValue)
                    }}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option}
                          {...getTagProps({ index })}
                          key={index}
                        />
                      ))
                    }
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="検出クラス"
                        placeholder="クラス名を入力またはリストから選択"
                        error={!!errors.classes}
                        helperText={errors.classes?.message || '物体検出で検出したいクラス名を指定してください'}
                      />
                    )}
                  />
                )}
              />
            </Grid>
            
            {watch('classes').length > 0 && (
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  選択されたクラス ({watch('classes').length}個):
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                  {watch('classes').map((className, index) => (
                    <Chip
                      key={index}
                      label={className}
                      onDelete={() => handleRemoveClass(className)}
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                  ))}
                </Box>
              </Grid>
            )}
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
          作成
        </LoadingButton>
      </DialogActions>
    </Dialog>
  )
}