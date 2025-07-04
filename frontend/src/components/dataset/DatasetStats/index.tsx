import React from 'react'
import { Box, Grid, Paper, Typography, CircularProgress } from '@mui/material'
import { Dataset } from '../../../services/api/visionApi'

interface DatasetStatsProps {
  datasets: Dataset[]
  loading?: boolean
}

interface StatCardProps {
  title: string
  value: number
  icon: string
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color = 'primary' }) => {
  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        textAlign: 'center',
        height: '100%',
        borderLeft: 4,
        borderLeftColor: `${color}.main`,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        }
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
        <Typography variant="h3" component="span" sx={{ mr: 1 }}>
          {icon}
        </Typography>
        <Typography
          variant="h4"
          component="div"
          color={`${color}.main`}
          fontWeight="bold"
        >
          {value.toLocaleString()}
        </Typography>
      </Box>
      <Typography variant="body2" color="text.secondary" fontWeight="medium">
        {title}
      </Typography>
    </Paper>
  )
}

export const DatasetStats: React.FC<DatasetStatsProps> = ({ datasets, loading }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={120}>
        <CircularProgress />
      </Box>
    )
  }

  const totalDatasets = datasets.length
  const totalImages = datasets.reduce((sum, dataset) => sum + dataset.image_count, 0)
  const activeDatasets = datasets.filter(dataset => dataset.status === 'active').length
  const processingDatasets = datasets.filter(dataset => dataset.status === 'processing').length

  const stats = [
    {
      title: 'データセット数',
      value: totalDatasets,
      icon: '📁',
      color: 'primary' as const,
    },
    {
      title: '総画像数',
      value: totalImages,
      icon: '🖼️',
      color: 'secondary' as const,
    },
    {
      title: 'アクティブ',
      value: activeDatasets,
      icon: '✅',
      color: 'success' as const,
    },
    {
      title: '処理中',
      value: processingDatasets,
      icon: '⚙️',
      color: 'warning' as const,
    },
  ]

  return (
    <Grid container spacing={3}>
      {stats.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <StatCard {...stat} />
        </Grid>
      ))}
    </Grid>
  )
}