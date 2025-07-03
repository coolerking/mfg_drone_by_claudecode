import React from 'react'
import { Chip, Badge, Box, Typography } from '@mui/material'
import {
  CheckCircle as ConnectedIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  RadioButtonUnchecked as DisconnectedIcon,
  FlightTakeoff as FlyingIcon,
  FlightLand as LandedIcon,
  Battery20 as LowBatteryIcon,
  BatteryFull as FullBatteryIcon,
  Wifi as OnlineIcon,
  WifiOff as OfflineIcon,
} from '@mui/icons-material'

export type StatusType = 
  | 'connected' | 'disconnected' | 'error' | 'warning' | 'success'
  | 'flying' | 'landed' | 'takeoff' | 'landing'
  | 'online' | 'offline' | 'syncing'
  | 'low-battery' | 'medium-battery' | 'full-battery'

export interface StatusBadgeProps {
  status: StatusType
  label?: string
  variant?: 'chip' | 'dot' | 'icon'
  size?: 'small' | 'medium' | 'large'
  showIcon?: boolean
  pulse?: boolean
}

const statusConfig: Record<StatusType, {
  color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'
  icon: React.ReactNode
  defaultLabel: string
}> = {
  connected: {
    color: 'success',
    icon: <ConnectedIcon />,
    defaultLabel: '接続済み',
  },
  disconnected: {
    color: 'default',
    icon: <DisconnectedIcon />,
    defaultLabel: '未接続',
  },
  error: {
    color: 'error',
    icon: <ErrorIcon />,
    defaultLabel: 'エラー',
  },
  warning: {
    color: 'warning',
    icon: <WarningIcon />,
    defaultLabel: '警告',
  },
  success: {
    color: 'success',
    icon: <CheckCircleIcon />,
    defaultLabel: '成功',
  },
  flying: {
    color: 'primary',
    icon: <FlyingIcon />,
    defaultLabel: '飛行中',
  },
  landed: {
    color: 'default',
    icon: <LandedIcon />,
    defaultLabel: '着陸',
  },
  takeoff: {
    color: 'info',
    icon: <FlyingIcon />,
    defaultLabel: '離陸中',
  },
  landing: {
    color: 'warning',
    icon: <LandedIcon />,
    defaultLabel: '着陸中',
  },
  online: {
    color: 'success',
    icon: <OnlineIcon />,
    defaultLabel: 'オンライン',
  },
  offline: {
    color: 'error',
    icon: <OfflineIcon />,
    defaultLabel: 'オフライン',
  },
  syncing: {
    color: 'info',
    icon: <OnlineIcon />,
    defaultLabel: '同期中',
  },
  'low-battery': {
    color: 'error',
    icon: <LowBatteryIcon />,
    defaultLabel: 'バッテリー低',
  },
  'medium-battery': {
    color: 'warning',
    icon: <LowBatteryIcon />,
    defaultLabel: 'バッテリー中',
  },
  'full-battery': {
    color: 'success',
    icon: <FullBatteryIcon />,
    defaultLabel: 'バッテリー充分',
  },
}

export function StatusBadge({
  status,
  label,
  variant = 'chip',
  size = 'medium',
  showIcon = true,
  pulse = false,
}: StatusBadgeProps) {
  const config = statusConfig[status]
  const displayLabel = label || config.defaultLabel

  const pulseAnimation = pulse ? {
    animation: 'pulse 2s infinite',
    '@keyframes pulse': {
      '0%': { opacity: 1 },
      '50%': { opacity: 0.5 },
      '100%': { opacity: 1 },
    },
  } : {}

  switch (variant) {
    case 'dot':
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: size === 'small' ? 8 : size === 'large' ? 16 : 12,
              height: size === 'small' ? 8 : size === 'large' ? 16 : 12,
              borderRadius: '50%',
              backgroundColor: `${config.color}.main`,
              ...pulseAnimation,
            }}
          />
          <Typography 
            variant={size === 'small' ? 'caption' : 'body2'}
            color="text.secondary"
          >
            {displayLabel}
          </Typography>
        </Box>
      )

    case 'icon':
      return (
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 0.5,
            color: `${config.color}.main`,
            ...pulseAnimation,
          }}
        >
          {React.cloneElement(config.icon as React.ReactElement, {
            fontSize: size === 'small' ? 'small' : size === 'large' ? 'large' : 'medium',
          })}
          {label && (
            <Typography 
              variant={size === 'small' ? 'caption' : 'body2'}
              color="inherit"
            >
              {displayLabel}
            </Typography>
          )}
        </Box>
      )

    default: // chip
      return (
        <Chip
          label={displayLabel}
          color={config.color}
          size={size === 'large' ? 'medium' : 'small'}
          icon={showIcon ? config.icon as React.ReactElement : undefined}
          sx={{
            ...pulseAnimation,
            fontSize: size === 'small' ? '0.75rem' : size === 'large' ? '0.875rem' : '0.8125rem',
          }}
        />
      )
  }
}

// Notification badge for count indicators
export function NotificationBadge({
  count,
  max = 99,
  showZero = false,
  children,
}: {
  count: number
  max?: number
  showZero?: boolean
  children: React.ReactNode
}) {
  return (
    <Badge
      badgeContent={count}
      max={max}
      showZero={showZero}
      color="error"
    >
      {children}
    </Badge>
  )
}