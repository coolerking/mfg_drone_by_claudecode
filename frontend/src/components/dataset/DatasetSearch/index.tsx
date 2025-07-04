import React from 'react'
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  InputAdornment,
  SelectChangeEvent,
} from '@mui/material'
import {
  Search as SearchIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import { Dataset } from '../../../services/api/visionApi'

interface DatasetFilters {
  search: string
  status: string
  type: string
  labels: string[]
}

interface DatasetSearchProps {
  datasets: Dataset[]
  filters: DatasetFilters
  onFiltersChange: (filters: DatasetFilters) => void
}

export const DatasetSearch: React.FC<DatasetSearchProps> = ({
  datasets,
  filters,
  onFiltersChange,
}) => {
  // Extract unique values for filter options
  const availableStatuses = Array.from(new Set(datasets.map(d => d.status)))
  const availableTypes = Array.from(new Set(datasets.map(d => d.type)))
  const availableLabels = Array.from(new Set(datasets.flatMap(d => d.labels)))

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({
      ...filters,
      search: event.target.value,
    })
  }

  const handleStatusChange = (event: SelectChangeEvent<string>) => {
    onFiltersChange({
      ...filters,
      status: event.target.value,
    })
  }

  const handleTypeChange = (event: SelectChangeEvent<string>) => {
    onFiltersChange({
      ...filters,
      type: event.target.value,
    })
  }

  const handleLabelToggle = (label: string) => {
    const newLabels = filters.labels.includes(label)
      ? filters.labels.filter(l => l !== label)
      : [...filters.labels, label]
    
    onFiltersChange({
      ...filters,
      labels: newLabels,
    })
  }

  const clearFilters = () => {
    onFiltersChange({
      search: '',
      status: '',
      type: '',
      labels: [],
    })
  }

  const hasActiveFilters = filters.search || filters.status || filters.type || filters.labels.length > 0

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

  const getTypeText = (type: string) => {
    switch (type) {
      case 'training':
        return '学習用'
      case 'validation':
        return '検証用'
      case 'test':
        return 'テスト用'
      default:
        return type
    }
  }

  return (
    <Box>
      {/* Search and Status/Type Filters */}
      <Box display="flex" gap={2} mb={2} flexWrap="wrap">
        <TextField
          label="データセット名で検索"
          variant="outlined"
          size="small"
          value={filters.search}
          onChange={handleSearchChange}
          sx={{ minWidth: 250, flexGrow: 1 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>ステータス</InputLabel>
          <Select
            value={filters.status}
            label="ステータス"
            onChange={handleStatusChange}
          >
            <MenuItem value="">全て</MenuItem>
            {availableStatuses.map(status => (
              <MenuItem key={status} value={status}>
                {getStatusText(status)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>タイプ</InputLabel>
          <Select
            value={filters.type}
            label="タイプ"
            onChange={handleTypeChange}
          >
            <MenuItem value="">全て</MenuItem>
            {availableTypes.map(type => (
              <MenuItem key={type} value={type}>
                {getTypeText(type)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {hasActiveFilters && (
          <Chip
            label="フィルタクリア"
            variant="outlined"
            onClick={clearFilters}
            onDelete={clearFilters}
            deleteIcon={<ClearIcon />}
            sx={{ ml: 1 }}
          />
        )}
      </Box>

      {/* Label Filters */}
      {availableLabels.length > 0 && (
        <Box>
          <Box mb={1}>
            <span style={{ fontSize: '0.875rem', color: '#666' }}>ラベルでフィルタ:</span>
          </Box>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {availableLabels.slice(0, 10).map(label => (
              <Chip
                key={label}
                label={label}
                variant={filters.labels.includes(label) ? 'filled' : 'outlined'}
                color={filters.labels.includes(label) ? 'primary' : 'default'}
                size="small"
                onClick={() => handleLabelToggle(label)}
                sx={{ cursor: 'pointer' }}
              />
            ))}
            {availableLabels.length > 10 && (
              <Chip
                label={`+${availableLabels.length - 10} more`}
                variant="outlined"
                size="small"
                sx={{ cursor: 'default' }}
              />
            )}
          </Box>
        </Box>
      )}
    </Box>
  )
}