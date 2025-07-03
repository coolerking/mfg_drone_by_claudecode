import { Box, Typography, Grid, Paper, Chip } from '@mui/material'
import {
  FlightTakeoff,
  Folder,
  Psychology,
  TrackChanges,
} from '@mui/icons-material'

interface StatCardProps {
  title: string
  value: number
  icon: React.ReactNode
  status?: {
    online?: number
    offline?: number
  }
}

function StatCard({ title, value, icon, status }: StatCardProps) {
  return (
    <Paper sx={{ p: 3, textAlign: 'center' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
        {icon}
        <Typography variant="h3" sx={{ ml: 1, fontWeight: 'bold' }}>
          {value}
        </Typography>
      </Box>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        {title}
      </Typography>
      {status && (
        <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'center' }}>
          {status.online !== undefined && (
            <Chip
              label={`${status.online} オンライン`}
              color="success"
              size="small"
            />
          )}
          {status.offline !== undefined && (
            <Chip
              label={`${status.offline} オフライン`}
              color="default"
              size="small"
            />
          )}
        </Box>
      )}
    </Paper>
  )
}

export function Dashboard() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        ダッシュボード
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        システム全体の状況を確認できます
      </Typography>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="接続ドローン数"
            value={3}
            icon={<FlightTakeoff color="primary" sx={{ fontSize: 40 }} />}
            status={{ online: 2, offline: 1 }}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="データセット数"
            value={5}
            icon={<Folder color="primary" sx={{ fontSize: 40 }} />}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="学習済みモデル数"
            value={2}
            icon={<Psychology color="primary" sx={{ fontSize: 40 }} />}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="アクティブ追跡数"
            value={1}
            icon={<TrackChanges color="primary" sx={{ fontSize: 40 }} />}
          />
        </Grid>
      </Grid>

      {/* System Status */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              システム状態
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography>CPU使用率</Typography>
                <Typography color="success.main">45%</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography>メモリ使用率</Typography>
                <Typography color="warning.main">78%</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography>ディスク使用率</Typography>
                <Typography color="success.main">52%</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography>ネットワーク</Typography>
                <Chip label="正常" color="success" size="small" />
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              最近のアクティビティ
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="body2">
                  ドローン "Tello-01" が接続されました
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  2分前
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2">
                  データセット "人物検出_v2" の学習が完了しました
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  15分前
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2">
                  追跡セッションが開始されました
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  1時間前
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}