import { useLocation, useNavigate } from 'react-router-dom'
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Button,
  Badge,
  Avatar,
  Chip,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  FlightTakeoff as DroneIcon,
  Folder as DatasetIcon,
  Psychology as ModelIcon,
  TrackChanges as TrackingIcon,
  Monitoring as MonitoringIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
} from '@mui/icons-material'

import { useAuth } from '../../../hooks/useAuth'
import { StatusBadge, NotificationBadge } from '../StatusBadge'

interface SidebarProps {
  onNavigate?: () => void
}

interface NavigationItem {
  name: string
  path: string
  icon: React.ComponentType
  badge?: number
  status?: 'normal' | 'warning' | 'error'
}

// Demo data - in real app, this would come from API/state
const getNavigationData = (): NavigationItem[] => [
  {
    name: 'ダッシュボード',
    path: '/dashboard',
    icon: DashboardIcon,
  },
  {
    name: 'ドローン管理',
    path: '/drones',
    icon: DroneIcon,
    badge: 3, // number of connected drones
    status: 'normal',
  },
  {
    name: 'データセット管理',
    path: '/datasets',
    icon: DatasetIcon,
    badge: 5, // number of datasets
  },
  {
    name: 'モデル管理',
    path: '/models',
    icon: ModelIcon,
    badge: 2, // number of trained models
  },
  {
    name: '追跡制御',
    path: '/tracking',
    icon: TrackingIcon,
    status: 'normal', // tracking status
  },
  {
    name: 'システム監視',
    path: '/monitoring',
    icon: MonitoringIcon,
    badge: 1, // number of alerts
    status: 'warning',
  },
  {
    name: '設定',
    path: '/settings',
    icon: SettingsIcon,
  },
]

export function Sidebar({ onNavigate }: SidebarProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const navigation = getNavigationData()

  const handleNavigate = (path: string) => {
    navigate(path)
    onNavigate?.()
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
    onNavigate?.()
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
          🚁 MFGドローン
        </Typography>
        <Typography variant="caption" color="text.secondary">
          管理システム v1.0
        </Typography>
        
        {/* System status indicator */}
        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <StatusBadge 
            status="online" 
            variant="dot" 
            size="small"
            pulse
          />
          <Typography variant="caption" color="text.secondary">
            システム正常
          </Typography>
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List sx={{ pt: 2 }}>
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <ListItem key={item.name} disablePadding sx={{ px: 1 }}>
                <ListItemButton
                  selected={isActive}
                  onClick={() => handleNavigate(item.path)}
                  sx={{
                    borderRadius: 1,
                    mx: 1,
                    '&.Mui-selected': {
                      backgroundColor: 'primary.main',
                      color: 'white',
                      '&:hover': {
                        backgroundColor: 'primary.dark',
                      },
                      '& .MuiListItemIcon-root': {
                        color: 'white',
                      },
                      '& .MuiBadge-badge': {
                        backgroundColor: 'white',
                        color: 'primary.main',
                      },
                    },
                  }}
                >
                  <ListItemIcon>
                    {item.badge !== undefined ? (
                      <NotificationBadge count={item.badge}>
                        <Icon />
                      </NotificationBadge>
                    ) : (
                      <Icon />
                    )}
                  </ListItemIcon>
                  
                  <ListItemText 
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography>{item.name}</Typography>
                        {item.status && item.status !== 'normal' && (
                          <StatusBadge 
                            status={item.status === 'warning' ? 'warning' : 'error'}
                            variant="dot"
                            size="small"
                          />
                        )}
                      </Box>
                    }
                  />
                </ListItemButton>
              </ListItem>
            )
          })}
        </List>
      </Box>

      {/* User info and logout */}
      <Box sx={{ p: 2 }}>
        <Divider sx={{ mb: 2 }} />
        
        {/* Enhanced user profile section */}
        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <PersonIcon />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle2" fontWeight="bold">
              {user?.username || '管理者'}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <StatusBadge 
                status="online" 
                variant="dot" 
                size="small"
              />
              <Typography variant="caption" color="text.secondary">
                オンライン
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Quick stats */}
        <Box sx={{ mb: 3, display: 'flex', gap: 1 }}>
          <Chip
            label="3台接続"
            size="small"
            color="success"
            variant="outlined"
          />
          <Chip
            label="1件アラート"
            size="small"
            color="warning"
            variant="outlined"
          />
        </Box>

        <Button
          fullWidth
          variant="outlined"
          startIcon={<LogoutIcon />}
          onClick={handleLogout}
          size="small"
          sx={{
            borderColor: 'grey.300',
            color: 'text.secondary',
            '&:hover': {
              borderColor: 'error.main',
              color: 'error.main',
              backgroundColor: 'error.light',
            },
          }}
        >
          ログアウト
        </Button>
      </Box>
    </Box>
  )
}