import React, { forwardRef } from 'react'
import { Button as MuiButton, ButtonProps as MuiButtonProps, CircularProgress } from '@mui/material'

export interface ButtonProps extends Omit<MuiButtonProps, 'children'> {
  children: React.ReactNode
  loading?: boolean
  loadingText?: string
  icon?: React.ReactNode
  confirmRequired?: boolean
  confirmText?: string
  onConfirm?: () => void
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    children, 
    loading = false, 
    loadingText, 
    icon, 
    disabled, 
    onClick,
    confirmRequired = false,
    confirmText = '実行してもよろしいですか？',
    onConfirm,
    ...props 
  }, ref) => {
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      if (confirmRequired) {
        if (window.confirm(confirmText)) {
          onConfirm?.()
          onClick?.(event)
        }
      } else {
        onClick?.(event)
      }
    }

    const isDisabled = disabled || loading

    return (
      <MuiButton
        ref={ref}
        disabled={isDisabled}
        onClick={handleClick}
        startIcon={loading ? <CircularProgress size={16} /> : icon}
        {...props}
      >
        {loading ? (loadingText || ' 処理中...') : children}
      </MuiButton>
    )
  }
)

Button.displayName = 'Button'