import { Box, Typography } from '@mui/material'

export function TrackingControl() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        追跡制御
      </Typography>
      <Typography variant="body1" color="text.secondary">
        物体追跡の開始、停止、設定機能（Phase 3で実装予定）
      </Typography>
    </Box>
  )
}