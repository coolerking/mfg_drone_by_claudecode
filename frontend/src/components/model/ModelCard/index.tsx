import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  LinearProgress,
  Tooltip,
  useTheme
} from '@mui/material'
import {
  MoreVert,
  PlayArrow,
  Pause,
  Stop,
  Download,
  Delete,
  Edit,
  Assessment,
  CloudUpload,
  FileCopy,
  Speed,
  Psychology
} from '@mui/icons-material'
import { useState } from 'react'
import { StatusBadge } from '@/components/common'
import { useConfirm } from '@/components/common'
import { useNotification } from '@/hooks/useNotification'
import { modelApi, type Model } from '@/services/api/modelApi'
import { formatDistanceToNow } from 'date-fns'
import { ja } from 'date-fns/locale'

interface ModelCardProps {
  model: Model
  onUpdate?: (model: Model) => void
  onDelete?: (modelId: string) => void
  onStartTraining?: (model: Model) => void
  onViewTraining?: (model: Model) => void
  onEvaluate?: (model: Model) => void
  onDeploy?: (model: Model) => void
}

export function ModelCard({
  model,
  onUpdate,
  onDelete,
  onStartTraining,
  onViewTraining,
  onEvaluate,
  onDeploy
}: ModelCardProps) {
  const theme = useTheme()
  const { showNotification } = useNotification()
  const confirm = useConfirm()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [loading, setLoading] = useState(false)

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const getStatusColor = (status: Model['status']) => {
    switch (status) {
      case 'trained':
        return 'success'
      case 'training':
        return 'warning'
      case 'failed':
        return 'error'
      case 'archived':
        return 'default'
      default:
        return 'default'
    }
  }

  const getStatusIcon = (status: Model['status']) => {
    switch (status) {
      case 'trained':
        return <Psychology />
      case 'training':
        return <PlayArrow />
      case 'failed':
        return <Stop />
      case 'archived':
        return <FileCopy />
      default:
        return null
    }
  }

  const getTypeColor = (type: Model['type']) => {
    switch (type) {
      case 'yolo':
        return theme.palette.primary.main
      case 'custom':
        return theme.palette.secondary.main
      case 'pretrained':
        return theme.palette.info.main
      default:
        return theme.palette.grey[500]
    }
  }

  const handleDelete = async () => {
    const confirmed = await confirm(
      `モデル「${model.name}」を削除しますか？`,
      'この操作は取り消せません。'
    )
    
    if (confirmed) {
      try {
        setLoading(true)
        await modelApi.deleteModel(model.id)
        showNotification('success', 'モデルが削除されました')
        onDelete?.(model.id)
      } catch (error) {
        console.error('Error deleting model:', error)
        showNotification('error', 'モデルの削除に失敗しました')
      } finally {
        setLoading(false)
        handleMenuClose()
      }
    }
  }

  const handleDuplicate = async () => {
    try {
      setLoading(true)
      const duplicatedModel = await modelApi.duplicateModel(model.id, `${model.name} (コピー)`)
      showNotification('success', 'モデルが複製されました')
      onUpdate?.(duplicatedModel)
    } catch (error) {
      console.error('Error duplicating model:', error)
      showNotification('error', 'モデルの複製に失敗しました')
    } finally {
      setLoading(false)
      handleMenuClose()
    }
  }

  const handleExport = async () => {
    try {
      setLoading(true)
      const result = await modelApi.exportModel(model.id, 'onnx')
      // Trigger download
      window.open(result.download_url, '_blank')
      showNotification('success', 'モデルのエクスポートを開始しました')
    } catch (error) {
      console.error('Error exporting model:', error)
      showNotification('error', 'モデルのエクスポートに失敗しました')
    } finally {
      setLoading(false)
      handleMenuClose()
    }
  }

  const handleDeploy = async () => {
    try {
      setLoading(true)
      await modelApi.deployModel(model.id)
      showNotification('success', 'モデルがデプロイされました')
      onDeploy?.(model)
    } catch (error) {
      console.error('Error deploying model:', error)
      showNotification('error', 'モデルのデプロイに失敗しました')
    } finally {
      setLoading(false)
      handleMenuClose()
    }
  }

  const formatFileSize = (sizeInMB: number) => {
    if (sizeInMB < 1) {
      return `${(sizeInMB * 1024).toFixed(0)} KB`
    }
    if (sizeInMB < 1024) {
      return `${sizeInMB.toFixed(1)} MB`
    }
    return `${(sizeInMB / 1024).toFixed(1)} GB`
  }

  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        position: 'relative',
        '&:hover': {
          boxShadow: theme.shadows[8]
        }
      }}
    >
      {loading && (
        <LinearProgress 
          sx={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            zIndex: 1 
          }} 
        />
      )}
      
      <CardContent sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h6" component="h3" gutterBottom>
              {model.name}
            </Typography>
            <Box display="flex" gap={1} mb={1}>
              <StatusBadge 
                status={model.status} 
                color={getStatusColor(model.status)}
                icon={getStatusIcon(model.status)}
              />
              <Chip 
                label={model.type.toUpperCase()} 
                size="small"
                sx={{ 
                  bgcolor: getTypeColor(model.type),
                  color: 'white',
                  fontWeight: 'bold'
                }}
              />
            </Box>
          </Box>
          
          <IconButton onClick={handleMenuOpen} size="small">
            <MoreVert />
          </IconButton>
        </Box>

        {/* Description */}
        {model.description && (
          <Typography variant="body2" color="text.secondary" paragraph>
            {model.description}
          </Typography>
        )}

        {/* Performance Metrics */}
        {model.status === 'trained' && (
          <Box mb={2}>
            <Typography variant="subtitle2" gutterBottom>
              性能指標
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {model.accuracy !== undefined && (
                <Chip 
                  label={`精度: ${model.accuracy.toFixed(1)}%`} 
                  size="small" 
                  color="success"
                  variant="outlined"
                />
              )}
              {model.map_score !== undefined && (
                <Chip 
                  label={`mAP: ${model.map_score.toFixed(3)}`} 
                  size="small" 
                  color="info"
                  variant="outlined"
                />
              )}
              {model.f1_score !== undefined && (
                <Chip 
                  label={`F1: ${model.f1_score.toFixed(3)}`} 
                  size="small" 
                  color="secondary"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>
        )}

        {/* Model Info */}
        <Box display="flex" flexDirection="column" gap={1}>
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              バージョン:
            </Typography>
            <Typography variant="body2">
              {model.version}
            </Typography>
          </Box>
          
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              ファイルサイズ:
            </Typography>
            <Typography variant="body2">
              {formatFileSize(model.file_size_mb)}
            </Typography>
          </Box>
          
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              学習エポック:
            </Typography>
            <Typography variant="body2">
              {model.training_epochs}
            </Typography>
          </Box>
          
          {model.training_time_hours && (
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                学習時間:
              </Typography>
              <Typography variant="body2">
                {model.training_time_hours.toFixed(1)}時間
              </Typography>
            </Box>
          )}
          
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              作成日:
            </Typography>
            <Typography variant="body2">
              {formatDistanceToNow(new Date(model.created_at), { 
                addSuffix: true, 
                locale: ja 
              })}
            </Typography>
          </Box>
        </Box>

        {/* Classes */}
        {model.classes.length > 0 && (
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              検出クラス ({model.classes.length})
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={0.5}>
              {model.classes.slice(0, 3).map((className, index) => (
                <Chip 
                  key={index}
                  label={className} 
                  size="small" 
                  variant="outlined"
                />
              ))}
              {model.classes.length > 3 && (
                <Chip 
                  label={`+${model.classes.length - 3}個`} 
                  size="small" 
                  variant="outlined"
                  color="default"
                />
              )}
            </Box>
          </Box>
        )}
      </CardContent>

      {/* Actions */}
      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
        <Box>
          {model.status === 'trained' && (
            <>
              <Tooltip title="評価実行">
                <IconButton 
                  onClick={() => onEvaluate?.(model)}
                  color="info"
                  size="small"
                >
                  <Assessment />
                </IconButton>
              </Tooltip>
              <Tooltip title="デプロイ">
                <IconButton 
                  onClick={handleDeploy}
                  color="success"
                  size="small"
                >
                  <CloudUpload />
                </IconButton>
              </Tooltip>
            </>
          )}
          {model.status === 'training' && (
            <Tooltip title="学習進捗表示">
              <IconButton 
                onClick={() => onViewTraining?.(model)}
                color="warning"
                size="small"
              >
                <PlayArrow />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        
        <Typography variant="caption" color="text.secondary">
          {model.id.slice(-8)}
        </Typography>
      </CardActions>

      {/* Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => { onUpdate?.(model); handleMenuClose() }}>
          <Edit sx={{ mr: 1 }} fontSize="small" />
          編集
        </MenuItem>
        
        <MenuItem onClick={handleDuplicate}>
          <FileCopy sx={{ mr: 1 }} fontSize="small" />
          複製
        </MenuItem>
        
        {model.status === 'trained' && (
          <MenuItem onClick={handleExport}>
            <Download sx={{ mr: 1 }} fontSize="small" />
            エクスポート
          </MenuItem>
        )}
        
        {model.status !== 'training' && (
          <MenuItem onClick={() => { onStartTraining?.(model); handleMenuClose() }}>
            <PlayArrow sx={{ mr: 1 }} fontSize="small" />
            再学習
          </MenuItem>
        )}
        
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <Delete sx={{ mr: 1 }} fontSize="small" />
          削除
        </MenuItem>
      </Menu>
    </Card>
  )
}