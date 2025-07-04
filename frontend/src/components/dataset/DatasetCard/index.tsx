import React from 'react'
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
} from '@mui/material'
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  GetApp as ExportIcon,
  Delete as DeleteIcon,
  Image as ImageIcon,
  Label as LabelIcon,
} from '@mui/icons-material'
import { StatusBadge, useConfirm } from '../../common'
import { Dataset } from '../../../services/api/visionApi'

interface DatasetCardProps {
  dataset: Dataset
  onEdit?: (datasetId: string) => void
  onView?: (datasetId: string) => void
  onExport?: (datasetId: string) => void
  onDelete?: (datasetId: string) => void
}

export const DatasetCard: React.FC<DatasetCardProps> = ({
  dataset,
  onEdit,
  onView,
  onExport,
  onDelete,
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null)
  const { confirm, ConfirmDialog } = useConfirm()

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleDelete = async () => {
    const confirmed = await confirm({
      title: 'データセット削除',
      message: `データセット "${dataset.name}" を削除しますか？この操作は取り消せません。`,
      confirmText: '削除',
      cancelText: 'キャンセル',
      variant: 'error',
    })

    if (confirmed && onDelete) {
      onDelete(dataset.id)
    }
  }

  const formatFileSize = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success'
      case 'processing':
        return 'warning'
      case 'archived':
        return 'default'
      default:
        return 'default'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'アクティブ'
      case 'processing':
        return '処理中'
      case 'archived':
        return 'アーカイブ'
      default:
        return status
    }
  }

  return (
    <>
      <ConfirmDialog />
      <Card
        elevation={2}
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: 6,
          }
        }}
      >
        <CardContent sx={{ flexGrow: 1 }}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="h6" component="div" fontWeight="bold">
                📁 {dataset.name}
              </Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <StatusBadge 
                status={getStatusText(dataset.status)} 
                color={getStatusColor(dataset.status)} 
              />
              <IconButton size="small" onClick={handleMenuOpen}>
                <MoreVertIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Description */}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 2,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              minHeight: '2.5em',
            }}
          >
            {dataset.description || 'No description available'}
          </Typography>

          {/* Stats */}
          <Box display="flex" gap={2} mb={2}>
            <Box display="flex" alignItems="center" gap={0.5}>
              <ImageIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {dataset.image_count.toLocaleString()} 枚
              </Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={0.5}>
              <LabelIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {dataset.label_count.toLocaleString()} ラベル
              </Typography>
            </Box>
          </Box>

          {/* Labels */}
          <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
            {dataset.labels.slice(0, 3).map((label, index) => (
              <Chip
                key={index}
                label={label}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.75rem' }}
              />
            ))}
            {dataset.labels.length > 3 && (
              <Chip
                label={`+${dataset.labels.length - 3}`}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.75rem' }}
              />
            )}
          </Box>

          {/* File Size & Type */}
          <Box display="flex" justify-content="space-between" alignItems="center">
            <Typography variant="caption" color="text.secondary">
              {formatFileSize(dataset.size_bytes)}
            </Typography>
            <Chip
              label={dataset.type}
              size="small"
              variant="filled"
              color="primary"
              sx={{ fontSize: '0.7rem' }}
            />
          </Box>

          {/* Dates */}
          <Box mt={1}>
            <Typography variant="caption" color="text.secondary" display="block">
              作成日: {new Date(dataset.created_at).toLocaleDateString('ja-JP')}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              更新日: {new Date(dataset.updated_at).toLocaleDateString('ja-JP')}
            </Typography>
          </Box>
        </CardContent>

        <CardActions>
          <Button
            size="small"
            startIcon={<VisibilityIcon />}
            onClick={() => onView?.(dataset.id)}
          >
            表示
          </Button>
          <Button
            size="small"
            startIcon={<EditIcon />}
            onClick={() => onEdit?.(dataset.id)}
          >
            編集
          </Button>
        </CardActions>
      </Card>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => { onView?.(dataset.id); handleMenuClose() }}>
          <VisibilityIcon fontSize="small" sx={{ mr: 1 }} />
          表示
        </MenuItem>
        <MenuItem onClick={() => { onEdit?.(dataset.id); handleMenuClose() }}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          編集
        </MenuItem>
        <MenuItem onClick={() => { onExport?.(dataset.id); handleMenuClose() }}>
          <ExportIcon fontSize="small" sx={{ mr: 1 }} />
          エクスポート
        </MenuItem>
        <MenuItem onClick={() => { handleDelete(); handleMenuClose() }} sx={{ color: 'error.main' }}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          削除
        </MenuItem>
      </Menu>
    </>
  )
}