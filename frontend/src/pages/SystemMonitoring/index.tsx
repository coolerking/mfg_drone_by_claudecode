import React, { useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper,
  useTheme,
  useMediaQuery
} from '@mui/material'
import {
  Dashboard,
  Assessment,
  Settings,
  Person,
  Notifications,
  BugReport
} from '@mui/icons-material'
import {
  MonitoringDashboard,
  SystemMetrics,
  AlertPanel,
  LogViewer,
  SystemSettings,
  UserPreferences
} from '../../components/monitoring'
import { useAuth } from '../../hooks/useAuth'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`system-monitoring-tabpanel-${index}`}
      aria-labelledby={`system-monitoring-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  )
}

const a11yProps = (index: number) => {
  return {
    id: `system-monitoring-tab-${index}`,
    'aria-controls': `system-monitoring-tabpanel-${index}`,
  }
}

export const SystemMonitoring: React.FC = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const { user } = useAuth()
  const [currentTab, setCurrentTab] = useState(0)

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  const tabs = [
    {
      label: 'ダッシュボード',
      icon: <Dashboard />,
      description: 'システム監視ダッシュボード'
    },
    {
      label: 'システムメトリクス',
      icon: <Assessment />,
      description: 'リアルタイムシステム指標'
    },
    {
      label: 'アラート',
      icon: <Notifications />,
      description: 'アラート・通知管理'
    },
    {
      label: 'ログ',
      icon: <BugReport />,
      description: 'ログ表示・フィルタリング'
    },
    {
      label: 'システム設定',
      icon: <Settings />,
      description: 'システム設定管理'
    },
    {
      label: 'ユーザー設定',
      icon: <Person />,
      description: 'ユーザー設定・環境設定'
    }
  ]

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          システム監視・管理
        </Typography>
        <Typography variant="body1" color="text.secondary">
          システムの状態監視、設定管理、ユーザー環境設定を行います
        </Typography>
      </Box>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          variant={isMobile ? 'scrollable' : 'fullWidth'}
          scrollButtons="auto"
          allowScrollButtonsMobile
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': {
              minHeight: 72,
              textTransform: 'none'
            }
          }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              icon={tab.icon}
              label={
                <Box textAlign="center">
                  <Typography variant="subtitle2" component="div">
                    {tab.label}
                  </Typography>
                  {!isMobile && (
                    <Typography variant="caption" color="text.secondary">
                      {tab.description}
                    </Typography>
                  )}
                </Box>
              }
              iconPosition="top"
              {...a11yProps(index)}
            />
          ))}
        </Tabs>

        <TabPanel value={currentTab} index={0}>
          <Box sx={{ p: 3 }}>
            <MonitoringDashboard
              editable={user?.role === 'admin'}
              refreshInterval={30000}
            />
          </Box>
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <Box sx={{ p: 3 }}>
            <SystemMetrics
              refreshInterval={30000}
              showCharts={true}
              compact={false}
            />
          </Box>
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <Box sx={{ p: 3 }}>
            <AlertPanel
              refreshInterval={30000}
              maxAlerts={50}
              showCreateButton={user?.role === 'admin'}
              compact={false}
            />
          </Box>
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <Box sx={{ p: 3 }}>
            <LogViewer
              refreshInterval={5000}
              maxLogs={100}
              realTime={false}
              compact={false}
            />
          </Box>
        </TabPanel>

        <TabPanel value={currentTab} index={4}>
          <Box sx={{ p: 3 }}>
            {user?.role === 'admin' ? (
              <SystemSettings
                onSettingsChange={(settings) => {
                  console.log('System settings changed:', settings)
                }}
              />
            ) : (
              <Box textAlign="center" py={4}>
                <Settings sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  アクセス権限がありません
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  システム設定にアクセスするには管理者権限が必要です
                </Typography>
              </Box>
            )}
          </Box>
        </TabPanel>

        <TabPanel value={currentTab} index={5}>
          <Box sx={{ p: 3 }}>
            <UserPreferences
              userId={user?.id || 'unknown'}
              onPreferencesChange={(preferences) => {
                console.log('User preferences changed:', preferences)
              }}
            />
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  )
}

export default SystemMonitoring