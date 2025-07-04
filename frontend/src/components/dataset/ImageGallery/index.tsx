import React, { useState } from 'react'
import {
  Box,
  Grid,
  Card,
  CardMedia,
  CardActions,
  IconButton,
  Checkbox,
  Typography,
  Pagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material'
import {
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Label as LabelIcon,
  CheckCircle as CheckedIcon,
  RadioButtonUnchecked as UncheckedIcon,
  MoreVert as MoreVertIcon,
  Download as DownloadIcon,
} from '@mui/icons-material'
import { DatasetImage } from '../../../services/api/visionApi'

interface ImageGalleryProps {
  images: DatasetImage[]
  loading?: boolean
  page: number
  totalPages: number
  onPageChange: (page: number) => void
  onImageSelect?: (imageId: string) => void
  onImageView?: (imageId: string) => void
  onImageEdit?: (imageId: string) => void
  onImageDelete?: (imageId: string) => void
  onBulkAction?: (action: string, imageIds: string[]) => void
  selectable?: boolean
  selectedImages?: string[]
  onSelectionChange?: (selectedIds: string[]) => void
}

export const ImageGallery: React.FC<ImageGalleryProps> = ({
  images,
  loading = false,
  page,
  totalPages,
  onPageChange,
  onImageSelect,
  onImageView,
  onImageEdit,
  onImageDelete,
  onBulkAction,
  selectable = false,
  selectedImages = [],
  onSelectionChange,
}) => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date')
  const [filterLabeled, setFilterLabeled] = useState<'all' | 'labeled' | 'unlabeled'>('all')
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [selectedImageId, setSelectedImageId] = useState<string | null>(null)

  const handleImageSelection = (imageId: string) => {
    if (!selectable || !onSelectionChange) return

    const newSelection = selectedImages.includes(imageId)
      ? selectedImages.filter(id => id !== imageId)
      : [...selectedImages, imageId]
    
    onSelectionChange(newSelection)
  }

  const handleSelectAll = () => {
    if (!selectable || !onSelectionChange) return

    if (selectedImages.length === images.length) {
      onSelectionChange([])
    } else {
      onSelectionChange(images.map(img => img.id))
    }
  }

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, imageId: string) => {
    setAnchorEl(event.currentTarget)
    setSelectedImageId(imageId)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
    setSelectedImageId(null)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getImageUrl = (image: DatasetImage) => {
    // In a real app, this would construct the proper image URL
    return `/api/datasets/${image.id}/thumbnail`
  }

  const isAllSelected = selectable && selectedImages.length === images.length && images.length > 0
  const isIndeterminate = selectable && selectedImages.length > 0 && selectedImages.length < images.length

  // Filter and sort images
  let filteredImages = [...images]
  
  if (filterLabeled !== 'all') {
    filteredImages = filteredImages.filter(img => 
      filterLabeled === 'labeled' ? img.labeled : !img.labeled
    )
  }

  filteredImages.sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.filename.localeCompare(b.filename)
      case 'size':
        return b.size_bytes - a.size_bytes
      case 'date':
      default:
        return new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime()
    }
  })

  return (
    <Box>
      {/* Controls */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Box display="flex" alignItems="center" gap={2}>
          {selectable && images.length > 0 && (
            <Box display="flex" alignItems="center" gap={1}>
              <Checkbox
                checked={isAllSelected}
                indeterminate={isIndeterminate}
                onChange={handleSelectAll}
              />
              <Typography variant="body2">
                {selectedImages.length > 0 
                  ? `${selectedImages.length} 件選択中`
                  : '全て選択'
                }
              </Typography>
            </Box>
          )}

          <Typography variant="body2" color="text.secondary">
            {filteredImages.length} 件の画像
          </Typography>
        </Box>

        <Box display="flex" gap={2}>
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <InputLabel>フィルタ</InputLabel>
            <Select
              value={filterLabeled}
              label="フィルタ"
              onChange={(e) => setFilterLabeled(e.target.value as any)}
            >
              <MenuItem value="all">全て</MenuItem>
              <MenuItem value="labeled">ラベル済み</MenuItem>
              <MenuItem value="unlabeled">未ラベル</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 100 }}>
            <InputLabel>ソート</InputLabel>
            <Select
              value={sortBy}
              label="ソート"
              onChange={(e) => setSortBy(e.target.value as any)}
            >
              <MenuItem value="date">日付</MenuItem>
              <MenuItem value="name">名前</MenuItem>
              <MenuItem value="size">サイズ</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Bulk Actions */}
      {selectable && selectedImages.length > 0 && onBulkAction && (
        <Box mb={2} p={2} bgcolor="action.selected" borderRadius={1}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2">
              {selectedImages.length} 件の画像が選択されています
            </Typography>
            <Box display="flex" gap={1}>
              <Chip
                label="ラベル編集"
                size="small"
                onClick={() => onBulkAction('edit-labels', selectedImages)}
                clickable
              />
              <Chip
                label="削除"
                size="small"
                color="error"
                onClick={() => onBulkAction('delete', selectedImages)}
                clickable
              />
            </Box>
          </Box>
        </Box>
      )}

      {/* Image Grid */}
      <Grid container spacing={2}>
        {filteredImages.map((image) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={image.id}>
            <Card
              sx={{
                position: 'relative',
                height: 300,
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 4,
                }
              }}
              onClick={() => onImageSelect?.(image.id)}
            >
              {/* Selection Checkbox */}
              {selectable && (
                <Checkbox
                  checked={selectedImages.includes(image.id)}
                  onChange={() => handleImageSelection(image.id)}
                  sx={{
                    position: 'absolute',
                    top: 8,
                    left: 8,
                    zIndex: 1,
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  }}
                  onClick={(e) => e.stopPropagation()}
                />
              )}

              {/* Label Status */}
              <Chip
                label={image.labeled ? `${image.labels.length} ラベル` : '未ラベル'}
                size="small"
                color={image.labeled ? 'success' : 'default'}
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  zIndex: 1,
                }}
              />

              {/* Image */}
              <CardMedia
                component="img"
                height="200"
                image={getImageUrl(image)}
                alt={image.filename}
                sx={{
                  objectFit: 'cover',
                  backgroundColor: 'grey.100',
                }}
                onError={(e) => {
                  // Fallback for broken images
                  const target = e.target as HTMLImageElement
                  target.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20fill%3D%22%23CCC%22%20height%3D%22200%22%20viewBox%3D%220%200%2024%2024%22%20width%3D%22200%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cpath%20d%3D%22M0%200h24v24H0z%22%20fill%3D%22none%22/%3E%3Cpath%20d%3D%22M21%2019V5c0-1.1-.9-2-2-2H5c-1.1%200-2%20.9-2%202v14c0%201.1.9%202%202%202h14c1.1%200%202-.9%202-2zM8.5%2013.5l2.5%203.01L14.5%2012l4.5%206H5l3.5-4.5z%22/%3E%3C/svg%3E'
                }}
              />

              {/* Image Info */}
              <Box p={1}>
                <Typography
                  variant="body2"
                  fontWeight="bold"
                  sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {image.filename}
                </Typography>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">
                    {formatFileSize(image.size_bytes)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {image.width} × {image.height}
                  </Typography>
                </Box>
              </Box>

              {/* Actions */}
              <CardActions sx={{ position: 'absolute', bottom: 0, right: 0 }}>
                <Tooltip title="表示">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation()
                      onImageView?.(image.id)
                    }}
                  >
                    <ViewIcon />
                  </IconButton>
                </Tooltip>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleMenuOpen(e, image.id)
                  }}
                >
                  <MoreVertIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Pagination */}
      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={4}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, newPage) => onPageChange(newPage)}
            color="primary"
            size="large"
          />
        </Box>
      )}

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => { onImageView?.(selectedImageId!); handleMenuClose() }}>
          <ListItemIcon>
            <ViewIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>表示</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => { onImageEdit?.(selectedImageId!); handleMenuClose() }}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>ラベル編集</ListItemText>
        </MenuItem>
        <MenuItem>
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>ダウンロード</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => { onImageDelete?.(selectedImageId!); handleMenuClose() }}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>削除</ListItemText>
        </MenuItem>
      </Menu>

      {/* Empty State */}
      {filteredImages.length === 0 && !loading && (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight={200}
          textAlign="center"
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            画像が見つかりません
          </Typography>
          <Typography variant="body2" color="text.secondary">
            フィルタ条件を変更するか、新しい画像をアップロードしてください
          </Typography>
        </Box>
      )}
    </Box>
  )
}