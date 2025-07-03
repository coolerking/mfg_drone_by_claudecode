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
} from '@mui/icons-material'

import { useAuth } from '../../../hooks/useAuth'

interface SidebarProps {
  onNavigate?: () => void
}

const navigation = [
  {
    name: 'ダッシュボード',
    path: '/dashboard',
    icon: DashboardIcon,
  },
  {
    name: 'ドローン管理',
    path: '/drones',
    icon: DroneIcon,
  },
  {
    name: 'データセット管理',
    path: '/datasets',
    icon: DatasetIcon,
  },
  {
    name: 'モデル管理',
    path: '/models',
    icon: ModelIcon,
  },
  {
    name: '追跡制御',
    path: '/tracking',
    icon: TrackingIcon,
  },
  {
    name: 'システム監視',
    path: '/monitoring',
    icon: MonitoringIcon,
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
                    },
                  }}
                >
                  <ListItemIcon>
                    <Icon />
                  </ListItemIcon>
                  <ListItemText primary={item.name} />
                </ListItemButton>
              </ListItem>
            )
          })}
        </List>
      </Box>

      {/* User info and logout */}
      <Box sx={{ p: 2 }}>
        <Divider sx={{ mb: 2 }} />
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            ログイン中
          </Typography>
          <Typography variant="subtitle2" fontWeight="bold">
            {user?.username || '管理者'}
          </Typography>
        </Box>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<LogoutIcon />}
          onClick={handleLogout}
          size="small"
        >
          ログアウト
        </Button>
      </Box>
    </Box>
  )
}