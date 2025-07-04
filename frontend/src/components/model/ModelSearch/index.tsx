import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  InputAdornment,
  Collapse,
  Grid,
  Paper,
  Typography,
  Slider
} from '@mui/material'
import {
  Search,
  FilterList,
  Clear,
  ExpandMore,
  ExpandLess,
  Sort
} from '@mui/icons-material'
import { useState } from 'react'
import type { Model } from '@/services/api/modelApi'

export interface ModelFilters {
  search: string
  status: Model['status'] | 'all'
  type: Model['type'] | 'all'
  minAccuracy: number
  maxAccuracy: number
  hasClasses: string[]
  dateRange: 'all' | 'last7days' | 'last30days' | 'last90days'
}

export interface ModelSortConfig {
  field: 'name' | 'created_at' | 'updated_at' | 'accuracy' | 'file_size_mb' | 'training_time_hours'
  direction: 'asc' | 'desc'
}

interface ModelSearchProps {
  filters: ModelFilters
  sortConfig: ModelSortConfig
  onFiltersChange: (filters: ModelFilters) => void
  onSortChange: (sort: ModelSortConfig) => void
  availableClasses: string[]
  totalResults: number
}

export function ModelSearch({
  filters,
  sortConfig,
  onFiltersChange,
  onSortChange,
  availableClasses,
  totalResults
}: ModelSearchProps) {
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)

  const handleFilterChange = (key: keyof ModelFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value
    })
  }

  const handleClearFilters = () => {
    onFiltersChange({
      search: '',
      status: 'all',
      type: 'all',
      minAccuracy: 0,
      maxAccuracy: 100,
      hasClasses: [],
      dateRange: 'all'
    })
  }

  const handleSortChange = (field: ModelSortConfig['field']) => {
    const newDirection = 
      sortConfig.field === field && sortConfig.direction === 'asc' 
        ? 'desc' 
        : 'asc'
    
    onSortChange({
      field,
      direction: newDirection
    })
  }

  const getActiveFiltersCount = () => {
    let count = 0
    if (filters.search) count++
    if (filters.status !== 'all') count++
    if (filters.type !== 'all') count++
    if (filters.minAccuracy > 0 || filters.maxAccuracy < 100) count++
    if (filters.hasClasses.length > 0) count++
    if (filters.dateRange !== 'all') count++
    return count
  }

  const handleClassToggle = (className: string) => {
    const currentClasses = filters.hasClasses
    const newClasses = currentClasses.includes(className)
      ? currentClasses.filter(c => c !== className)
      : [...currentClasses, className]
    
    handleFilterChange('hasClasses', newClasses)
  }

  const sortOptions = [
    { value: 'name', label: '名前' },
    { value: 'created_at', label: '作成日' },
    { value: 'updated_at', label: '更新日' },
    { value: 'accuracy', label: '精度' },
    { value: 'file_size_mb', label: 'ファイルサイズ' },
    { value: 'training_time_hours', label: '学習時間' }
  ]

  return (
    <Box>
      {/* Main Search Bar */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="モデル名、説明で検索..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
                endAdornment: filters.search && (
                  <InputAdornment position="end">
                    <IconButton 
                      size="small" 
                      onClick={() => handleFilterChange('search', '')}
                    >
                      <Clear />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
          </Grid>
          
          <Grid item xs={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>ステータス</InputLabel>
              <Select
                value={filters.status}
                label="ステータス"
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <MenuItem value="all">すべて</MenuItem>
                <MenuItem value="trained">学習済み</MenuItem>
                <MenuItem value="training">学習中</MenuItem>
                <MenuItem value="failed">失敗</MenuItem>
                <MenuItem value="archived">アーカイブ</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>タイプ</InputLabel>
              <Select
                value={filters.type}
                label="タイプ"
                onChange={(e) => handleFilterChange('type', e.target.value)}
              >
                <MenuItem value="all">すべて</MenuItem>
                <MenuItem value="yolo">YOLO</MenuItem>
                <MenuItem value="custom">カスタム</MenuItem>
                <MenuItem value="pretrained">事前学習済み</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={6} md={1.5}>
            <FormControl fullWidth size="small">
              <InputLabel>並び順</InputLabel>
              <Select
                value={sortConfig.field}
                label="並び順"
                onChange={(e) => handleSortChange(e.target.value as ModelSortConfig['field'])}
              >
                {sortOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={6} md={0.5}>
            <Tooltip title={`${sortConfig.direction === 'asc' ? '昇順' : '降順'}`}>
              <IconButton 
                onClick={() => onSortChange({
                  ...sortConfig,
                  direction: sortConfig.direction === 'asc' ? 'desc' : 'asc'
                })}
              >
                <Sort 
                  sx={{ 
                    transform: sortConfig.direction === 'desc' ? 'rotate(180deg)' : 'none',
                    transition: 'transform 0.2s'
                  }} 
                />
              </IconButton>
            </Tooltip>
          </Grid>
        </Grid>

        {/* Filter Controls */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <IconButton
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              size="small"
            >
              <FilterList />
              {getActiveFiltersCount() > 0 && (
                <Chip 
                  label={getActiveFiltersCount()} 
                  size="small" 
                  color="primary"
                  sx={{ ml: 1, minWidth: 24, height: 20 }}
                />
              )}
            </IconButton>
            <Typography variant="body2" color="text.secondary">
              {showAdvancedFilters ? '詳細フィルタを隠す' : '詳細フィルタを表示'}
            </Typography>
            
            {getActiveFiltersCount() > 0 && (
              <Tooltip title="フィルタをクリア">
                <IconButton size="small" onClick={handleClearFilters}>
                  <Clear />
                </IconButton>
              </Tooltip>
            )}
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            {totalResults} 件のモデル
          </Typography>
        </Box>
      </Paper>

      {/* Advanced Filters */}
      <Collapse in={showAdvancedFilters}>
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            詳細フィルタ
          </Typography>
          
          <Grid container spacing={3}>
            {/* Accuracy Range */}
            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                精度範囲: {filters.minAccuracy}% - {filters.maxAccuracy}%
              </Typography>
              <Slider
                value={[filters.minAccuracy, filters.maxAccuracy]}
                onChange={(_, newValue) => {
                  const [min, max] = newValue as number[]
                  handleFilterChange('minAccuracy', min)
                  handleFilterChange('maxAccuracy', max)
                }}
                valueLabelDisplay="auto"
                min={0}
                max={100}
                step={1}
                marks={[
                  { value: 0, label: '0%' },
                  { value: 50, label: '50%' },
                  { value: 100, label: '100%' }
                ]}
              />
            </Grid>

            {/* Date Range */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>作成日範囲</InputLabel>
                <Select
                  value={filters.dateRange}
                  label="作成日範囲"
                  onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                >
                  <MenuItem value="all">すべて</MenuItem>
                  <MenuItem value="last7days">過去7日間</MenuItem>
                  <MenuItem value="last30days">過去30日間</MenuItem>
                  <MenuItem value="last90days">過去90日間</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Available Classes */}
            {availableClasses.length > 0 && (
              <Grid item xs={12}>
                <Typography variant="body2" gutterBottom>
                  検出クラス
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {availableClasses.map((className) => (
                    <Chip
                      key={className}
                      label={className}
                      onClick={() => handleClassToggle(className)}
                      color={filters.hasClasses.includes(className) ? 'primary' : 'default'}
                      variant={filters.hasClasses.includes(className) ? 'filled' : 'outlined'}
                      size="small"
                      clickable
                    />
                  ))}
                </Box>
              </Grid>
            )}
          </Grid>
        </Paper>
      </Collapse>

      {/* Active Filters Display */}
      {getActiveFiltersCount() > 0 && (
        <Box mb={2}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            アクティブなフィルタ:
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {filters.search && (
              <Chip
                label={`検索: ${filters.search}`}
                onDelete={() => handleFilterChange('search', '')}
                size="small"
              />
            )}
            {filters.status !== 'all' && (
              <Chip
                label={`ステータス: ${filters.status}`}
                onDelete={() => handleFilterChange('status', 'all')}
                size="small"
              />
            )}
            {filters.type !== 'all' && (
              <Chip
                label={`タイプ: ${filters.type}`}
                onDelete={() => handleFilterChange('type', 'all')}
                size="small"
              />
            )}
            {(filters.minAccuracy > 0 || filters.maxAccuracy < 100) && (
              <Chip
                label={`精度: ${filters.minAccuracy}%-${filters.maxAccuracy}%`}
                onDelete={() => {
                  handleFilterChange('minAccuracy', 0)
                  handleFilterChange('maxAccuracy', 100)
                }}
                size="small"
              />
            )}
            {filters.dateRange !== 'all' && (
              <Chip
                label={`期間: ${filters.dateRange}`}
                onDelete={() => handleFilterChange('dateRange', 'all')}
                size="small"
              />
            )}
            {filters.hasClasses.map((className) => (
              <Chip
                key={className}
                label={`クラス: ${className}`}
                onDelete={() => handleClassToggle(className)}
                size="small"
              />
            ))}
          </Box>
        </Box>
      )}
    </Box>
  )
}