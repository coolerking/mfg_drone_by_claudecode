import { Box, Typography } from '@mui/material'

export function ModelManagement() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        モデル管理
      </Typography>
      <Typography variant="body1" color="text.secondary">
        機械学習モデルの学習、評価、管理機能（Phase 2で実装予定）
      </Typography>
    </Box>
  )
}