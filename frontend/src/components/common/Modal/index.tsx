import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  Box,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { Button } from '../Button'

export interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  actions?: React.ReactNode
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  fullScreen?: boolean
  showCloseButton?: boolean
  closeOnBackdropClick?: boolean
  loading?: boolean
}

export function Modal({
  open,
  onClose,
  title,
  children,
  actions,
  maxWidth = 'sm',
  fullScreen = false,
  showCloseButton = true,
  closeOnBackdropClick = true,
  loading = false,
}: ModalProps) {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  
  const shouldBeFullScreen = fullScreen || isMobile

  const handleBackdropClick = () => {
    if (closeOnBackdropClick && !loading) {
      onClose()
    }
  }

  const handleClose = () => {
    if (!loading) {
      onClose()
    }
  }

  return (
    <Dialog
      open={open}
      onClose={handleBackdropClick}
      maxWidth={maxWidth}
      fullWidth
      fullScreen={shouldBeFullScreen}
      sx={{
        '& .MuiDialog-paper': {
          borderRadius: shouldBeFullScreen ? 0 : 2,
        },
      }}
    >
      {title && (
        <DialogTitle sx={{ m: 0, p: 2, pr: showCloseButton ? 6 : 2 }}>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          {showCloseButton && (
            <IconButton
              aria-label="close"
              onClick={handleClose}
              disabled={loading}
              sx={{
                position: 'absolute',
                right: 8,
                top: 8,
                color: (theme) => theme.palette.grey[500],
              }}
            >
              <CloseIcon />
            </IconButton>
          )}
        </DialogTitle>
      )}
      
      <DialogContent dividers={Boolean(title)}>
        <Box sx={{ minHeight: 100 }}>
          {children}
        </Box>
      </DialogContent>
      
      {actions && (
        <DialogActions sx={{ p: 2 }}>
          {actions}
        </DialogActions>
      )}
    </Dialog>
  )
}

// Predefined action sets
export function ModalActions({
  onCancel,
  onConfirm,
  cancelText = 'キャンセル',
  confirmText = 'OK',
  confirmColor = 'primary',
  loading = false,
  disabled = false,
}: {
  onCancel?: () => void
  onConfirm?: () => void
  cancelText?: string
  confirmText?: string
  confirmColor?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
  loading?: boolean
  disabled?: boolean
}) {
  return (
    <>
      {onCancel && (
        <Button
          onClick={onCancel}
          disabled={loading}
          variant="outlined"
        >
          {cancelText}
        </Button>
      )}
      {onConfirm && (
        <Button
          onClick={onConfirm}
          color={confirmColor}
          variant="contained"
          loading={loading}
          disabled={disabled}
        >
          {confirmText}
        </Button>
      )}
    </>
  )
}