import { Box, Typography } from '@mui/material'

export function DroneManagement() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        ドローン管理
      </Typography>
      <Typography variant="body1" color="text.secondary">
        ドローンの接続、制御、監視を行います（Phase 2で実装予定）
      </Typography>
    </Box>
  )
}