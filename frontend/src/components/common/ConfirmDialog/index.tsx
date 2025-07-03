import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  useTheme,
} from '@mui/material'
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  HelpOutline as QuestionIcon,
} from '@mui/icons-material'
import { Button } from '../Button'

export interface ConfirmDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'warning' | 'error' | 'info' | 'question'
  loading?: boolean
  confirmColor?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
}

const variantConfig = {
  warning: {
    icon: WarningIcon,
    color: '#ff9800',
    confirmColor: 'warning' as const,
  },
  error: {
    icon: ErrorIcon,
    color: '#f44336',
    confirmColor: 'error' as const,
  },
  info: {
    icon: InfoIcon,
    color: '#2196f3',
    confirmColor: 'info' as const,
  },
  question: {
    icon: QuestionIcon,
    color: '#9c27b0',
    confirmColor: 'primary' as const,
  },
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = '実行',
  cancelText = 'キャンセル',
  variant = 'question',
  loading = false,
  confirmColor,
}: ConfirmDialogProps) {
  const theme = useTheme()
  const config = variantConfig[variant]
  const Icon = config.icon
  const finalConfirmColor = confirmColor || config.confirmColor

  const handleConfirm = () => {
    onConfirm()
  }

  const handleCancel = () => {
    if (!loading) {
      onClose()
    }
  }

  const defaultTitles = {
    warning: '警告',
    error: 'エラー',
    info: '確認',
    question: '確認',
  }

  return (
    <Dialog
      open={open}
      onClose={handleCancel}
      maxWidth="sm"
      fullWidth
      sx={{
        '& .MuiDialog-paper': {
          borderRadius: 2,
        },
      }}
    >
      <DialogTitle sx={{ pb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Icon sx={{ color: config.color }} />
          <Typography variant="h6">
            {title || defaultTitles[variant]}
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
          {message}
        </Typography>
      </DialogContent>
      
      <DialogActions sx={{ p: 3, gap: 1 }}>
        <Button
          onClick={handleCancel}
          disabled={loading}
          variant="outlined"
          size="large"
        >
          {cancelText}
        </Button>
        
        <Button
          onClick={handleConfirm}
          color={finalConfirmColor}
          variant="contained"
          loading={loading}
          size="large"
          autoFocus
        >
          {confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

// Hook for easier usage
export function useConfirmDialog() {
  const [dialogState, setDialogState] = React.useState<{
    open: boolean
    config: Omit<ConfirmDialogProps, 'open' | 'onClose' | 'onConfirm'> | null
    onConfirm?: () => void
  }>({
    open: false,
    config: null,
    onConfirm: undefined,
  })

  const showConfirm = React.useCallback((
    config: Omit<ConfirmDialogProps, 'open' | 'onClose' | 'onConfirm'>,
    onConfirm: () => void
  ) => {
    setDialogState({
      open: true,
      config,
      onConfirm,
    })
  }, [])

  const hideConfirm = React.useCallback(() => {
    setDialogState(prev => ({
      ...prev,
      open: false,
    }))
  }, [])

  const handleConfirm = React.useCallback(() => {
    dialogState.onConfirm?.()
    hideConfirm()
  }, [dialogState.onConfirm, hideConfirm])

  const ConfirmDialogComponent = React.useCallback(() => {
    if (!dialogState.config) return null

    return (
      <ConfirmDialog
        {...dialogState.config}
        open={dialogState.open}
        onClose={hideConfirm}
        onConfirm={handleConfirm}
      />
    )
  }, [dialogState, hideConfirm, handleConfirm])

  return {
    showConfirm,
    hideConfirm,
    ConfirmDialog: ConfirmDialogComponent,
  }
}