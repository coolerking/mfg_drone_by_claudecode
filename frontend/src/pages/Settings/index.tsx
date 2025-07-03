import { Box, Typography } from '@mui/material'

export function Settings() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        設定
      </Typography>
      <Typography variant="body1" color="text.secondary">
        システム設定、ユーザー設定機能（Phase 4で実装予定）
      </Typography>
    </Box>
  )
}