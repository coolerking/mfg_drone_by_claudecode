import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Chip,
  Typography,
  Alert,
} from '@mui/material'
import { LoadingButton } from '@mui/lab'
import { Add as AddIcon } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Dataset } from '../../../services/api/visionApi'

const createDatasetSchema = z.object({
  name: z.string().min(1, '名前は必須です').max(100, '名前は100文字以内で入力してください'),
  description: z.string().max(500, '説明は500文字以内で入力してください').optional(),
  type: z.enum(['training', 'validation', 'test'], {
    errorMap: () => ({ message: 'タイプを選択してください' }),
  }),
  labels: z.array(z.string()).min(1, '少なくとも1つのラベルを入力してください'),
})

type CreateDatasetForm = z.infer<typeof createDatasetSchema>

interface CreateDatasetModalProps {
  open: boolean
  onClose: () => void
  onSubmit: (data: Omit<Dataset, 'id' | 'created_at' | 'updated_at' | 'image_count' | 'label_count' | 'size_bytes'>) => Promise<void>
  loading?: boolean
}

export const CreateDatasetModal: React.FC<CreateDatasetModalProps> = ({
  open,
  onClose,
  onSubmit,
  loading = false,
}) => {
  const [labelInput, setLabelInput] = useState('')
  const [labels, setLabels] = useState<string[]>([])

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isValid },
  } = useForm<CreateDatasetForm>({
    resolver: zodResolver(createDatasetSchema),
    defaultValues: {
      name: '',
      description: '',
      type: 'training',
      labels: [],
    },
  })

  const handleClose = () => {
    reset()
    setLabels([])
    setLabelInput('')
    onClose()
  }

  const handleAddLabel = () => {
    const trimmedLabel = labelInput.trim()
    if (trimmedLabel && !labels.includes(trimmedLabel)) {
      const newLabels = [...labels, trimmedLabel]
      setLabels(newLabels)
      setValue('labels', newLabels, { shouldValidate: true })
      setLabelInput('')
    }
  }

  const handleRemoveLabel = (labelToRemove: string) => {
    const newLabels = labels.filter(label => label !== labelToRemove)
    setLabels(newLabels)
    setValue('labels', newLabels, { shouldValidate: true })
  }

  const handleLabelInputKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      handleAddLabel()
    }
  }

  const onFormSubmit = async (data: CreateDatasetForm) => {
    try {
      await onSubmit({
        name: data.name,
        description: data.description,
        type: data.type,
        status: 'active',
        labels: data.labels,
      })
      handleClose()
    } catch (error) {
      console.error('Failed to create dataset:', error)
    }
  }

  const getTypeText = (type: string) => {
    switch (type) {
      case 'training':
        return '学習用'
      case 'validation':
        return '検証用'
      case 'test':
        return 'テスト用'
      default:
        return type
    }
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        component: 'form',
        onSubmit: handleSubmit(onFormSubmit),
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <AddIcon />
          新規データセット作成
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Box display="flex" flexDirection="column" gap={3}>
          {/* Dataset Name */}
          <Controller
            name="name"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="データセット名"
                fullWidth
                required
                error={!!errors.name}
                helperText={errors.name?.message}
                placeholder="例: 人物検出 v1.0"
              />
            )}
          />

          {/* Description */}
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="説明"
                fullWidth
                multiline
                rows={3}
                error={!!errors.description}
                helperText={errors.description?.message}
                placeholder="データセットの詳細説明..."
              />
            )}
          />

          {/* Type */}
          <Controller
            name="type"
            control={control}
            render={({ field }) => (
              <FormControl fullWidth error={!!errors.type}>
                <InputLabel>タイプ</InputLabel>
                <Select {...field} label="タイプ">
                  <MenuItem value="training">{getTypeText('training')}</MenuItem>
                  <MenuItem value="validation">{getTypeText('validation')}</MenuItem>
                  <MenuItem value="test">{getTypeText('test')}</MenuItem>
                </Select>
                {errors.type && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                    {errors.type.message}
                  </Typography>
                )}
              </FormControl>
            )}
          />

          {/* Labels */}
          <Box>
            <Box display="flex" gap={1} mb={1}>
              <TextField
                label="ラベル追加"
                value={labelInput}
                onChange={(e) => setLabelInput(e.target.value)}
                onKeyPress={handleLabelInputKeyPress}
                size="small"
                sx={{ flexGrow: 1 }}
                placeholder="例: person, car, background"
                helperText="Enterキーまたは追加ボタンでラベルを追加"
              />
              <Button
                variant="outlined"
                onClick={handleAddLabel}
                disabled={!labelInput.trim() || labels.includes(labelInput.trim())}
                sx={{ whiteSpace: 'nowrap' }}
              >
                追加
              </Button>
            </Box>

            {/* Label Chips */}
            <Box display="flex" flexWrap="wrap" gap={1} mb={1}>
              {labels.map((label, index) => (
                <Chip
                  key={index}
                  label={label}
                  onDelete={() => handleRemoveLabel(label)}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>

            {errors.labels && (
              <Alert severity="error" sx={{ mt: 1 }}>
                {errors.labels.message}
              </Alert>
            )}

            {labels.length === 0 && (
              <Typography variant="caption" color="text.secondary">
                データセットに含めるオブジェクトのラベルを追加してください
              </Typography>
            )}
          </Box>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          キャンセル
        </Button>
        <LoadingButton
          type="submit"
          variant="contained"
          loading={loading}
          disabled={!isValid}
          startIcon={<AddIcon />}
        >
          作成
        </LoadingButton>
      </DialogActions>
    </Dialog>
  )
}