import React from 'react'
import {
  Card as MuiCard,
  CardHeader,
  CardContent,
  CardActions,
  Avatar,
  IconButton,
  Typography,
  Box,
  Chip,
  Skeleton,
} from '@mui/material'
import MoreVertIcon from '@mui/icons-material/MoreVert'

export interface CardProps {
  title?: string
  subtitle?: string
  avatar?: React.ReactNode
  headerIcon?: React.ReactNode
  children?: React.ReactNode
  actions?: React.ReactNode
  status?: {
    label: string
    color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'
  }
  loading?: boolean
  onClick?: () => void
  elevation?: number
  variant?: 'elevation' | 'outlined'
}

export function Card({
  title,
  subtitle,
  avatar,
  headerIcon,
  children,
  actions,
  status,
  loading = false,
  onClick,
  elevation = 1,
  variant = 'elevation',
}: CardProps) {
  if (loading) {
    return (
      <MuiCard 
        elevation={elevation} 
        variant={variant}
        sx={{ 
          cursor: onClick ? 'pointer' : 'default',
          '&:hover': onClick ? { elevation: elevation + 1 } : {},
        }}
      >
        <CardHeader
          avatar={<Skeleton animation="wave" variant="circular" width={40} height={40} />}
          title={<Skeleton animation="wave" height={20} width="40%" />}
          subheader={<Skeleton animation="wave" height={16} width="60%" />}
        />
        <CardContent>
          <Skeleton animation="wave" height={80} />
        </CardContent>
      </MuiCard>
    )
  }

  const cardProps = {
    elevation,
    variant,
    onClick,
    sx: {
      cursor: onClick ? 'pointer' : 'default',
      transition: 'elevation 0.2s',
      '&:hover': onClick ? { 
        elevation: elevation + 2,
        transform: 'translateY(-2px)',
      } : {},
    },
  }

  return (
    <MuiCard {...cardProps}>
      {(title || subtitle || avatar || headerIcon || status) && (
        <CardHeader
          avatar={avatar && <Avatar>{avatar}</Avatar>}
          action={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {status && (
                <Chip
                  label={status.label}
                  color={status.color}
                  size="small"
                />
              )}
              {headerIcon && (
                <IconButton aria-label="settings">
                  {headerIcon}
                </IconButton>
              )}
            </Box>
          }
          title={title}
          subheader={subtitle}
        />
      )}
      
      {children && (
        <CardContent>
          {children}
        </CardContent>
      )}
      
      {actions && (
        <CardActions sx={{ justifyContent: 'flex-end' }}>
          {actions}
        </CardActions>
      )}
    </MuiCard>
  )
}

// Specialized card components
export function StatCard({
  title,
  value,
  change,
  icon,
  color = 'primary',
  loading = false,
}: {
  title: string
  value: string | number
  change?: {
    value: number
    label: string
    positive?: boolean
  }
  icon?: React.ReactNode
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
  loading?: boolean
}) {
  if (loading) {
    return (
      <Card loading />
    )
  }

  return (
    <Card>
      <Box sx={{ p: 3, textAlign: 'center' }}>
        {icon && (
          <Box sx={{ mb: 2, color: `${color}.main` }}>
            {icon}
          </Box>
        )}
        
        <Typography variant="h3" component="div" fontWeight="bold" color={`${color}.main`}>
          {value}
        </Typography>
        
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        
        {change && (
          <Chip
            label={`${change.positive ? '+' : ''}${change.value} ${change.label}`}
            color={change.positive ? 'success' : 'error'}
            size="small"
          />
        )}
      </Box>
    </Card>
  )
}