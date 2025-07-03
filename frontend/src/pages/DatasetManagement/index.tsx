import { Box, Typography } from '@mui/material'

export function DatasetManagement() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        データセット管理
      </Typography>
      <Typography variant="body1" color="text.secondary">
        データセットの作成、編集、画像ラベリング機能（Phase 2で実装予定）
      </Typography>
    </Box>
  )
}