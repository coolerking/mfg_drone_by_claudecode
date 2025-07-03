import React, { useState } from 'react'
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  IconButton,
  InputAdornment,
  Button
} from '@mui/material'
import { Search, Clear, Refresh } from '@mui/icons-material'
import { DroneStatus } from '../../../types/drone'

interface DroneSearchProps {
  searchTerm: string
  statusFilter: DroneStatus | 'all'
  sortBy: 'name' | 'status' | 'battery' | 'lastSeen'
  sortOrder: 'asc' | 'desc'
  onSearchChange: (searchTerm: string) => void
  onStatusFilterChange: (status: DroneStatus | 'all') => void
  onSortChange: (sortBy: string, sortOrder: 'asc' | 'desc') => void
  onRefresh?: () => void
  totalResults?: number
}

const statusOptions: { value: DroneStatus | 'all', label: string, color?: string }[] = [
  { value: 'all', label: '全て' },
  { value: 'connected', label: 'オンライン', color: '#4caf50' },
  { value: 'flying', label: '飛行中', color: '#2196f3' },
  { value: 'hovering', label: 'ホバリング', color: '#00bcd4' },
  { value: 'disconnected', label: 'オフライン', color: '#9e9e9e' },
  { value: 'error', label: 'エラー', color: '#f44336' },
  { value: 'low_battery', label: 'バッテリー低下', color: '#ff9800' },
  { value: 'maintenance', label: 'メンテナンス', color: '#795548' }
]

const sortOptions = [
  { value: 'name', label: '名前' },
  { value: 'status', label: 'ステータス' },
  { value: 'battery', label: 'バッテリー' },
  { value: 'lastSeen', label: '最終接続' }
]

export const DroneSearch: React.FC<DroneSearchProps> = ({
  searchTerm,
  statusFilter,
  sortBy,
  sortOrder,
  onSearchChange,
  onStatusFilterChange,
  onSortChange,
  onRefresh,
  totalResults
}) => {
  const [localSearchTerm, setLocalSearchTerm] = useState(searchTerm)

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearchChange(localSearchTerm)
  }

  const handleClearSearch = () => {
    setLocalSearchTerm('')
    onSearchChange('')
  }

  const handleSortChange = (field: string) => {
    if (field === sortBy) {
      // Toggle sort order if same field
      onSortChange(field, sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      // Default to ascending for new field
      onSortChange(field, 'asc')
    }
  }

  const getActiveFilters = () => {
    const filters = []
    if (searchTerm) {
      filters.push({
        label: `検索: "${searchTerm}"`,
        onDelete: () => {
          setLocalSearchTerm('')
          onSearchChange('')
        }
      })
    }
    if (statusFilter !== 'all') {
      const statusOption = statusOptions.find(opt => opt.value === statusFilter)
      filters.push({
        label: `ステータス: ${statusOption?.label}`,
        onDelete: () => onStatusFilterChange('all')
      })
    }
    return filters
  }

  const activeFilters = getActiveFilters()

  return (
    <Box>
      {/* Search and Filter Controls */}
      <Stack spacing={2} mb={2}>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
          {/* Search Field */}
          <Box component="form" onSubmit={handleSearchSubmit} sx={{ flex: '1 1 300px' }}>
            <TextField
              fullWidth
              placeholder="ドローン名、モデル、シリアル番号で検索..."
              value={localSearchTerm}
              onChange={(e) => setLocalSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
                endAdornment: localSearchTerm && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={handleClearSearch}
                      edge="end"
                    >
                      <Clear />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
          </Box>

          {/* Status Filter */}
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>ステータス</InputLabel>
            <Select
              value={statusFilter}
              label="ステータス"
              onChange={(e) => onStatusFilterChange(e.target.value as DroneStatus | 'all')}
            >
              {statusOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  <Box display="flex" alignItems="center" gap={1}>
                    {option.color && (
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: option.color
                        }}
                      />
                    )}
                    {option.label}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Sort Control */}
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>並び順</InputLabel>
            <Select
              value={`${sortBy}_${sortOrder}`}
              label="並び順"
              onChange={(e) => {
                const [field, order] = e.target.value.split('_')
                onSortChange(field, order as 'asc' | 'desc')
              }}
            >
              {sortOptions.map((option) => (
                <React.Fragment key={option.value}>
                  <MenuItem value={`${option.value}_asc`}>
                    {option.label} (昇順)
                  </MenuItem>
                  <MenuItem value={`${option.value}_desc`}>
                    {option.label} (降順)
                  </MenuItem>
                </React.Fragment>
              ))}
            </Select>
          </FormControl>

          {/* Refresh Button */}
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={onRefresh}
            sx={{ minWidth: 120 }}
          >
            更新
          </Button>
        </Box>

        {/* Active Filters */}
        {activeFilters.length > 0 && (
          <Box>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {activeFilters.map((filter, index) => (
                <Chip
                  key={index}
                  label={filter.label}
                  onDelete={filter.onDelete}
                  variant="outlined"
                  size="small"
                />
              ))}
            </Stack>
          </Box>
        )}

        {/* Results Count */}
        {typeof totalResults === 'number' && (
          <Box>
            <Chip
              label={`${totalResults}件のドローンが見つかりました`}
              variant="filled"
              color="primary"
              size="small"
            />
          </Box>
        )}
      </Stack>
    </Box>
  )
}