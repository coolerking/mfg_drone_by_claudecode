import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Stack,
  LinearProgress
} from '@mui/material'
import { Add, Search } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'

const addDroneSchema = z.object({
  name: z.string().min(1, 'ドローン名は必須です').max(50, 'ドローン名は50文字以内で入力してください'),
  model: z.string().min(1, 'モデルは必須です'),
  serial_number: z.string().min(1, 'シリアル番号は必須です'),
  ip_address: z.string().regex(
    /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
    '有効なIPアドレスを入力してください'
  ).optional(),
  description: z.string().max(200, '説明は200文字以内で入力してください').optional()
})

type AddDroneFormData = z.infer<typeof addDroneSchema>

interface AddDroneModalProps {
  open: boolean
  onClose: () => void
  onSubmit: (data: AddDroneFormData) => Promise<void>
  onScanNetwork?: () => Promise<any[]>
}

const droneModels = [
  'Tello EDU',
  'DJI Mini 2',
  'DJI Air 2S',
  'DJI Mavic 3',
  'その他'
]

export const AddDroneModal: React.FC<AddDroneModalProps> = ({
  open,
  onClose,
  onSubmit,
  onScanNetwork
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isScanning, setIsScanning] = useState(false)
  const [scanResults, setScanResults] = useState<any[]>([])
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    formState: { errors }
  } = useForm<AddDroneFormData>({
    resolver: zodResolver(addDroneSchema),
    defaultValues: {
      name: '',
      model: 'Tello EDU',
      serial_number: '',
      ip_address: '',
      description: ''
    }
  })

  const handleFormSubmit = async (data: AddDroneFormData) => {
    try {
      setIsSubmitting(true)
      setSubmitError(null)
      await onSubmit(data)
      reset()
      onClose()
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'ドローンの追加に失敗しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleScanNetwork = async () => {
    if (!onScanNetwork) return

    try {
      setIsScanning(true)
      const results = await onScanNetwork()
      setScanResults(results)
    } catch (error) {
      console.error('Network scan failed:', error)
    } finally {
      setIsScanning(false)
    }
  }

  const handleSelectScanResult = (result: any) => {
    setValue('name', result.name || `${result.model} - ${result.serial_number}`)
    setValue('model', result.model || 'Tello EDU')
    setValue('serial_number', result.serial_number || '')
    setValue('ip_address', result.ip_address || '')
    setScanResults([])
  }

  const handleClose = () => {
    if (!isSubmitting) {
      reset()
      setScanResults([])
      setSubmitError(null)
      onClose()
    }
  }

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { minHeight: '400px' }
      }}
    >
      <DialogTitle>ドローン追加</DialogTitle>
      
      <DialogContent>
        <Box component="form" sx={{ mt: 1 }}>
          <Stack spacing={3}>
            {/* Network Scan */}
            {onScanNetwork && (
              <Box>
                <Button
                  variant="outlined"
                  startIcon={<Search />}
                  onClick={handleScanNetwork}
                  disabled={isScanning || isSubmitting}
                  fullWidth
                >
                  {isScanning ? 'ネットワークをスキャン中...' : 'ネットワークをスキャン'}
                </Button>
                
                {isScanning && <LinearProgress sx={{ mt: 1 }} />}

                {scanResults.length > 0 && (
                  <Box mt={2}>
                    <Alert severity="success" sx={{ mb: 2 }}>
                      {scanResults.length}台のドローンが見つかりました
                    </Alert>
                    {scanResults.map((result, index) => (
                      <Button
                        key={index}
                        variant="outlined"
                        onClick={() => handleSelectScanResult(result)}
                        sx={{ mb: 1, mr: 1, textAlign: 'left' }}
                        size="small"
                      >
                        {result.name || `${result.model} - ${result.ip_address}`}
                      </Button>
                    ))}
                  </Box>
                )}
              </Box>
            )}

            {/* Manual Entry */}
            <Controller
              name="name"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="ドローン名"
                  placeholder="例: Tello EDU - Alpha"
                  error={!!errors.name}
                  helperText={errors.name?.message}
                  disabled={isSubmitting}
                  fullWidth
                  required
                />
              )}
            />

            <Controller
              name="model"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth required disabled={isSubmitting}>
                  <InputLabel>モデル</InputLabel>
                  <Select {...field} label="モデル">
                    {droneModels.map((model) => (
                      <MenuItem key={model} value={model}>
                        {model}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
            />

            <Controller
              name="serial_number"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="シリアル番号"
                  placeholder="例: TELLO-ABC123"
                  error={!!errors.serial_number}
                  helperText={errors.serial_number?.message}
                  disabled={isSubmitting}
                  fullWidth
                  required
                />
              )}
            />

            <Controller
              name="ip_address"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="IPアドレス（オプション）"
                  placeholder="例: 192.168.1.100"
                  error={!!errors.ip_address}
                  helperText={errors.ip_address?.message || 'WiFi接続時のIPアドレス'}
                  disabled={isSubmitting}
                  fullWidth
                />
              )}
            />

            <Controller
              name="description"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="説明（オプション）"
                  placeholder="ドローンの詳細情報や用途を入力..."
                  error={!!errors.description}
                  helperText={errors.description?.message}
                  disabled={isSubmitting}
                  multiline
                  rows={3}
                  fullWidth
                />
              )}
            />

            {submitError && (
              <Alert severity="error">
                {submitError}
              </Alert>
            )}
          </Stack>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button 
          onClick={handleClose}
          disabled={isSubmitting}
        >
          キャンセル
        </Button>
        <Button
          onClick={handleSubmit(handleFormSubmit)}
          variant="contained"
          disabled={isSubmitting}
          startIcon={isSubmitting ? undefined : <Add />}
        >
          {isSubmitting ? '追加中...' : 'ドローン追加'}
        </Button>
      </DialogActions>

      {isSubmitting && <LinearProgress />}
    </Dialog>
  )
}