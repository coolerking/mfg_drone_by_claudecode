import { 
  Box, 
  Grid, 
  Typography, 
  Paper, 
  useTheme,
  CircularProgress
} from '@mui/material'
import { 
  ModelTraining,
  Psychology,
  TrendingUp,
  Assignment
} from '@mui/icons-material'
import { Card } from '@/components/common'
import { modelApi, type Model } from '@/services/api/modelApi'
import { useEffect, useState } from 'react'

interface ModelStatsData {
  totalModels: number
  trainedModels: number
  trainingModels: number
  failedModels: number
  averageAccuracy: number
  bestAccuracy: number
  totalTrainingHours: number
  activeDeployments: number
}

interface ModelStatsProps {
  onStatsChange?: (stats: ModelStatsData) => void
  refreshTrigger?: number
}

export function ModelStats({ onStatsChange, refreshTrigger }: ModelStatsProps) {
  const theme = useTheme()
  const [stats, setStats] = useState<ModelStatsData>({
    totalModels: 0,
    trainedModels: 0,
    trainingModels: 0,
    failedModels: 0,
    averageAccuracy: 0,
    bestAccuracy: 0,
    totalTrainingHours: 0,
    activeDeployments: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch all models
      const models = await modelApi.getModels()
      
      // Calculate statistics
      const totalModels = models.length
      const trainedModels = models.filter(m => m.status === 'trained').length
      const trainingModels = models.filter(m => m.status === 'training').length
      const failedModels = models.filter(m => m.status === 'failed').length
      
      // Calculate accuracy statistics
      const trainedWithAccuracy = models.filter(m => m.status === 'trained' && m.accuracy !== undefined)
      const averageAccuracy = trainedWithAccuracy.length > 0 
        ? trainedWithAccuracy.reduce((sum, m) => sum + (m.accuracy || 0), 0) / trainedWithAccuracy.length
        : 0
      
      const bestAccuracy = models.reduce((max, m) => Math.max(max, m.accuracy || 0), 0)
      
      // Calculate total training hours
      const totalTrainingHours = models.reduce((sum, m) => sum + (m.training_time_hours || 0), 0)
      
      // For now, mock active deployments (would need to check deployment status)
      const activeDeployments = Math.floor(trainedModels * 0.3) // Mock: assume 30% are deployed
      
      const calculatedStats: ModelStatsData = {
        totalModels,
        trainedModels,
        trainingModels,
        failedModels,
        averageAccuracy,
        bestAccuracy,
        totalTrainingHours,
        activeDeployments
      }
      
      setStats(calculatedStats)
      onStatsChange?.(calculatedStats)
    } catch (err) {
      console.error('Error fetching model stats:', err)
      setError('統計データの取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [refreshTrigger])

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
        <Typography variant="body2" sx={{ ml: 2 }}>
          統計データを読み込み中...
        </Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Paper sx={{ p: 3, bgcolor: theme.palette.error.light, color: theme.palette.error.contrastText }}>
        <Typography variant="body1">{error}</Typography>
      </Paper>
    )
  }

  const statCards = [
    {
      title: '総モデル数',
      value: stats.totalModels,
      icon: Assignment,
      color: theme.palette.primary.main,
      bgColor: theme.palette.primary.light
    },
    {
      title: '学習済み',
      value: stats.trainedModels,
      icon: Psychology,
      color: theme.palette.success.main,
      bgColor: theme.palette.success.light
    },
    {
      title: '学習中',
      value: stats.trainingModels,
      icon: ModelTraining,
      color: theme.palette.warning.main,
      bgColor: theme.palette.warning.light,
      animated: stats.trainingModels > 0
    },
    {
      title: '失敗',
      value: stats.failedModels,
      icon: Assignment,
      color: theme.palette.error.main,
      bgColor: theme.palette.error.light
    }
  ]

  const performanceCards = [
    {
      title: '平均精度',
      value: `${stats.averageAccuracy.toFixed(1)}%`,
      icon: TrendingUp,
      color: theme.palette.info.main,
      bgColor: theme.palette.info.light
    },
    {
      title: '最高精度',
      value: `${stats.bestAccuracy.toFixed(1)}%`,
      icon: TrendingUp,
      color: theme.palette.success.main,
      bgColor: theme.palette.success.light
    },
    {
      title: '総学習時間',
      value: `${stats.totalTrainingHours.toFixed(1)}h`,
      icon: ModelTraining,
      color: theme.palette.secondary.main,
      bgColor: theme.palette.secondary.light
    },
    {
      title: 'デプロイ中',
      value: stats.activeDeployments,
      icon: Psychology,
      color: theme.palette.primary.main,
      bgColor: theme.palette.primary.light
    }
  ]

  return (
    <Box>
      {/* Model Count Statistics */}
      <Typography variant="h6" gutterBottom>
        モデル状況
      </Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              title={card.title}
              value={card.value}
              icon={card.icon}
              color={card.color}
              bgColor={card.bgColor}
              animated={card.animated}
            />
          </Grid>
        ))}
      </Grid>

      {/* Performance Statistics */}
      <Typography variant="h6" gutterBottom>
        性能指標
      </Typography>
      <Grid container spacing={2}>
        {performanceCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              title={card.title}
              value={card.value}
              icon={card.icon}
              color={card.color}
              bgColor={card.bgColor}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}