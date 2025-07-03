import React from 'react'
import {
  Box,
  CircularProgress,
  LinearProgress,
  Typography,
  Skeleton,
  Paper,
} from '@mui/material'

export interface LoadingProps {
  type?: 'circular' | 'linear' | 'skeleton' | 'overlay'
  size?: 'small' | 'medium' | 'large'
  text?: string
  overlay?: boolean
  progress?: number // 0-100 for progress loading
}

export function Loading({
  type = 'circular',
  size = 'medium',
  text,
  overlay = false,
  progress,
}: LoadingProps) {
  const getSizeValue = () => {
    switch (size) {
      case 'small': return 24
      case 'large': return 60
      default: return 40
    }
  }

  const renderLoading = () => {
    switch (type) {
      case 'linear':
        return (
          <Box sx={{ width: '100%' }}>
            {text && (
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {text}
              </Typography>
            )}
            <LinearProgress 
              variant={progress !== undefined ? 'determinate' : 'indeterminate'}
              value={progress}
            />
            {progress !== undefined && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {Math.round(progress)}%
              </Typography>
            )}
          </Box>
        )
      
      case 'skeleton':
        return (
          <Box>
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="80%" />
            <Skeleton variant="rectangular" height={118} sx={{ mt: 1 }} />
          </Box>
        )
      
      case 'overlay':
        return (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 9999,
            }}
          >
            <Paper
              elevation={3}
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
              }}
            >
              <CircularProgress size={getSizeValue()} />
              {text && (
                <Typography variant="body2" color="text.secondary">
                  {text}
                </Typography>
              )}
            </Paper>
          </Box>
        )
      
      default: // circular
        return (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <CircularProgress 
              size={getSizeValue()}
              variant={progress !== undefined ? 'determinate' : 'indeterminate'}
              value={progress}
            />
            {text && (
              <Typography variant="body2" color="text.secondary">
                {text}
              </Typography>
            )}
          </Box>
        )
    }
  }

  if (overlay || type === 'overlay') {
    return renderLoading()
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        p: 2,
      }}
    >
      {renderLoading()}
    </Box>
  )
}

// Page-level loading component
export function PageLoading({ text = 'ページを読み込んでいます...' }: { text?: string }) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '50vh',
        gap: 2,
      }}
    >
      <CircularProgress size={48} />
      <Typography variant="body1" color="text.secondary">
        {text}
      </Typography>
    </Box>
  )
}

// Inline loading for buttons or small components
export function InlineLoading({ 
  size = 16, 
  color = 'inherit' 
}: { 
  size?: number
  color?: string 
}) {
  return (
    <CircularProgress 
      size={size} 
      sx={{ color, mr: 1 }}
    />
  )
}