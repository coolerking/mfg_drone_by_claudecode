import React from 'react'
import { Box, Card, CardContent, Typography, Grid } from '@mui/material'
import { 
  Flight,
  PowerOff,
  Warning,
  Battery20
} from '@mui/icons-material'
import { Drone, DroneStats as DroneStatsType } from '../../../types/drone'

interface DroneStatsProps {
  drones: Drone[]
}

interface StatCardProps {
  title: string
  value: number
  icon: React.ReactNode
  color: string
  subtitle?: string
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, subtitle }) => (
  <Card 
    sx={{ 
      height: '100%',
      background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
      border: `1px solid ${color}30`
    }}
  >
    <CardContent sx={{ textAlign: 'center', py: 3 }}>
      <Box 
        sx={{ 
          color: color,
          mb: 2,
          display: 'flex',
          justifyContent: 'center'
        }}
      >
        {icon}
      </Box>
      <Typography variant="h3" component="div" sx={{ color: color, fontWeight: 'bold' }}>
        {value}
      </Typography>
      <Typography variant="body1" color="text.primary" sx={{ mt: 1 }}>
        {title}
      </Typography>
      {subtitle && (
        <Typography variant="caption" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
)

export const DroneStats: React.FC<DroneStatsProps> = ({ drones }) => {
  const stats = React.useMemo(() => {
    const connectedDrones = drones.filter(d => 
      d.status === 'connected' || 
      d.status === 'flying' || 
      d.status === 'hovering' ||
      d.status === 'takeoff' ||
      d.status === 'landing'
    ).length

    const flyingDrones = drones.filter(d => 
      d.status === 'flying' || 
      d.status === 'takeoff' || 
      d.status === 'landing' ||
      d.status === 'hovering'
    ).length

    const offlineDrones = drones.filter(d => 
      d.status === 'disconnected'
    ).length

    const errorDrones = drones.filter(d => 
      d.status === 'error' ||
      d.status === 'low_battery' ||
      d.status === 'maintenance'
    ).length

    const lowBatteryDrones = drones.filter(d => 
      d.battery <= 20
    ).length

    return {
      totalDrones: drones.length,
      connectedDrones,
      flyingDrones,
      offlineDrones,
      errorDrones,
      lowBatteryDrones
    }
  }, [drones])

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        接続状況
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="オンライン"
            value={stats.connectedDrones}
            icon={<Flight fontSize="large" />}
            color="#4caf50"
            subtitle={`${stats.totalDrones}台中`}
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="飛行中"
            value={stats.flyingDrones}
            icon={<Flight fontSize="large" />}
            color="#2196f3"
            subtitle="アクティブ"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="オフライン"
            value={stats.offlineDrones}
            icon={<PowerOff fontSize="large" />}
            color="#9e9e9e"
            subtitle="切断済み"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            title="警告"
            value={stats.errorDrones}
            icon={<Warning fontSize="large" />}
            color="#ff9800"
            subtitle="要注意"
          />
        </Grid>
      </Grid>

      {/* Additional alerts */}
      {stats.lowBatteryDrones > 0 && (
        <Box mt={2}>
          <Card sx={{ backgroundColor: '#fff3e0', border: '1px solid #ff9800' }}>
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1}>
                <Battery20 sx={{ color: '#ff9800' }} />
                <Typography variant="body2">
                  <strong>{stats.lowBatteryDrones}台</strong>のドローンでバッテリー残量が少なくなっています
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  )
}