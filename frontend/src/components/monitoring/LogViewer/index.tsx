import React, { useState, useEffect, useRef } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Collapse,
  Alert,
  Pagination,
  Stack,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Switch,
  FormControlLabel,
  Badge
} from '@mui/material'
import {
  Search,
  FilterList,
  Refresh,
  Download,
  Clear,
  ExpandMore,
  ExpandLess,
  PlayArrow,
  Pause,
  Settings,
  Visibility,
  Error,
  Warning,
  Info,
  BugReport,
  Security,
  Speed
} from '@mui/icons-material'
import { DateTimePicker } from '@mui/x-date-pickers'
import { format } from 'date-fns'
import { ja } from 'date-fns/locale'
import type { LogEntry, LogFilter } from '../../../types/monitoring'
import { useNotification } from '../../common'

interface LogViewerProps {
  refreshInterval?: number
  maxLogs?: number
  realTime?: boolean
  compact?: boolean
}

interface LogDetailDialogProps {
  open: boolean
  log: LogEntry | null
  onClose: () => void
}

const LogDetailDialog: React.FC<LogDetailDialogProps> = ({ open, log, onClose }) => {
  if (!log) return null

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>ログ詳細</DialogTitle>
      <DialogContent>
        <Stack spacing={2}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                label="タイムスタンプ"
                value={format(new Date(log.timestamp), 'yyyy/MM/dd HH:mm:ss.SSS', { locale: ja })}
                fullWidth
                variant="outlined"
                InputProps={{ readOnly: true }}
              />
            </Grid>
            <Grid item xs={3}>
              <TextField
                label="レベル"
                value={log.level}
                fullWidth
                variant="outlined"
                InputProps={{ readOnly: true }}
              />
            </Grid>
            <Grid item xs={3}>
              <TextField
                label="ソース"
                value={log.source}
                fullWidth
                variant="outlined"
                InputProps={{ readOnly: true }}
              />
            </Grid>
          </Grid>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                label="カテゴリ"
                value={log.category}
                fullWidth
                variant="outlined"
                InputProps={{ readOnly: true }}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                label="ユーザーID"
                value={log.user_id || '不明'}
                fullWidth
                variant="outlined"
                InputProps={{ readOnly: true }}
              />
            </Grid>
          </Grid>

          <TextField
            label="メッセージ"
            value={log.message}
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            InputProps={{ readOnly: true }}
          />

          {log.details && Object.keys(log.details).length > 0 && (
            <TextField
              label="詳細"
              value={JSON.stringify(log.details, null, 2)}
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              InputProps={{ readOnly: true }}
            />
          )}

          {log.stack_trace && (
            <TextField
              label="スタックトレース"
              value={log.stack_trace}
              fullWidth
              multiline
              rows={6}
              variant="outlined"
              InputProps={{ readOnly: true }}
            />
          )}

          {log.context && Object.keys(log.context).length > 0 && (
            <TextField
              label="コンテキスト"
              value={JSON.stringify(log.context, null, 2)}
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              InputProps={{ readOnly: true }}
            />
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>閉じる</Button>
      </DialogActions>
    </Dialog>
  )
}

const getLevelIcon = (level: LogEntry['level']) => {
  switch (level) {
    case 'critical':
    case 'error':
      return <Error color="error" fontSize="small" />
    case 'warning':
      return <Warning color="warning" fontSize="small" />
    case 'info':
      return <Info color="info" fontSize="small" />
    case 'debug':
      return <BugReport color="action" fontSize="small" />
    default:
      return <Info color="action" fontSize="small" />
  }
}

const getLevelColor = (level: LogEntry['level']): 'error' | 'warning' | 'info' | 'default' => {
  switch (level) {
    case 'critical':
    case 'error':
      return 'error'
    case 'warning':
      return 'warning'
    case 'info':
      return 'info'
    default:
      return 'default'
  }
}

const getCategoryIcon = (category: LogEntry['category']) => {
  switch (category) {
    case 'security':
      return <Security fontSize="small" />
    case 'performance':
      return <Speed fontSize="small" />
    case 'drone':
      return <BugReport fontSize="small" />
    default:
      return <Info fontSize="small" />
  }
}

// Mock data for development (replace with actual API call)
const generateMockLogs = (count: number): LogEntry[] => {
  const levels: LogEntry['level'][] = ['debug', 'info', 'warning', 'error', 'critical']
  const categories: LogEntry['category'][] = ['system', 'drone', 'vision', 'api', 'security', 'performance']
  const sources = ['api-server', 'drone-controller', 'vision-processor', 'web-frontend', 'database', 'auth-service']
  
  return Array.from({ length: count }, (_, i) => ({
    id: `log-${i}`,
    timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
    level: levels[Math.floor(Math.random() * levels.length)],
    source: sources[Math.floor(Math.random() * sources.length)],
    category: categories[Math.floor(Math.random() * categories.length)],
    message: `ログメッセージ ${i + 1}: これはサンプルログメッセージです`,
    details: Math.random() > 0.7 ? { key: 'value', count: i } : undefined,
    user_id: Math.random() > 0.5 ? `user-${Math.floor(Math.random() * 10)}` : undefined,
    session_id: `session-${Math.floor(Math.random() * 100)}`,
    request_id: `req-${Math.floor(Math.random() * 1000)}`,
    context: { component: 'test', action: 'sample' }
  }))
}

export const LogViewer: React.FC<LogViewerProps> = ({
  refreshInterval = 5000,
  maxLogs = 100,
  realTime = false,
  compact = false
}) => {
  const { showNotification } = useNotification()
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState<LogFilter>({})
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [page, setPage] = useState(1)
  const [logsPerPage] = useState(20)
  const [isRealTime, setIsRealTime] = useState(realTime)
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())
  const [filtersExpanded, setFiltersExpanded] = useState(false)
  const tableContainerRef = useRef<HTMLDivElement>(null)

  const fetchLogs = async () => {
    try {
      // Mock implementation - replace with actual API call
      const mockLogs = generateMockLogs(maxLogs)
      setLogs(mockLogs)
      setIsLoading(false)
      
      if (isRealTime && tableContainerRef.current) {
        // Auto-scroll to bottom for real-time logs
        tableContainerRef.current.scrollTop = tableContainerRef.current.scrollHeight
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error)
      showNotification('ログの取得に失敗しました', 'error')
      setIsLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = logs

    // Level filter
    if (filters.level && filters.level.length > 0) {
      filtered = filtered.filter(log => filters.level!.includes(log.level))
    }

    // Category filter
    if (filters.category && filters.category.length > 0) {
      filtered = filtered.filter(log => filters.category!.includes(log.category))
    }

    // Source filter
    if (filters.source && filters.source.length > 0) {
      filtered = filtered.filter(log => filters.source!.includes(log.source))
    }

    // Search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(log =>
        log.message.toLowerCase().includes(query) ||
        log.source.toLowerCase().includes(query) ||
        (log.user_id && log.user_id.toLowerCase().includes(query))
      )
    }

    // Time range filter
    if (filters.start_time) {
      filtered = filtered.filter(log => log.timestamp >= filters.start_time!)
    }
    if (filters.end_time) {
      filtered = filtered.filter(log => log.timestamp <= filters.end_time!)
    }

    // Sort by timestamp (newest first)
    filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

    setFilteredLogs(filtered)
  }

  const handleClearFilters = () => {
    setFilters({})
    setSearchQuery('')
    setPage(1)
  }

  const handleExport = () => {
    const csvContent = filteredLogs.map(log => [
      log.timestamp,
      log.level,
      log.source,
      log.category,
      log.message.replace(/"/g, '""'),
      log.user_id || '',
      log.session_id || ''
    ].join(',')).join('\n')

    const header = 'Timestamp,Level,Source,Category,Message,User ID,Session ID\n'
    const blob = new Blob([header + csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `logs_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`
    a.click()
    URL.revokeObjectURL(url)

    showNotification('ログをエクスポートしました', 'success')
  }

  const handleRowClick = (log: LogEntry) => {
    setSelectedLog(log)
    setDetailDialogOpen(true)
  }

  const handleExpandRow = (logId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(logId)) {
      newExpanded.delete(logId)
    } else {
      newExpanded.add(logId)
    }
    setExpandedRows(newExpanded)
  }

  useEffect(() => {
    fetchLogs()
  }, [])

  useEffect(() => {
    if (!isRealTime) return

    const interval = setInterval(() => {
      fetchLogs()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [refreshInterval, isRealTime])

  useEffect(() => {
    applyFilters()
  }, [logs, filters, searchQuery])

  const paginatedLogs = filteredLogs.slice(
    (page - 1) * logsPerPage,
    page * logsPerPage
  )

  const totalPages = Math.ceil(filteredLogs.length / logsPerPage)

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h2">
          ログビューア
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Badge badgeContent={filteredLogs.length} color="primary" max={9999}>
            <Button
              startIcon={<FilterList />}
              onClick={() => setFiltersExpanded(!filtersExpanded)}
              variant="outlined"
              size="small"
            >
              フィルタ
            </Button>
          </Badge>
          
          <FormControlLabel
            control={
              <Switch
                checked={isRealTime}
                onChange={(e) => setIsRealTime(e.target.checked)}
                size="small"
              />
            }
            label="リアルタイム"
          />

          <Tooltip title="更新">
            <IconButton onClick={fetchLogs} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>

          <Tooltip title="エクスポート">
            <IconButton onClick={handleExport} disabled={filteredLogs.length === 0}>
              <Download />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Card>
        <Collapse in={filtersExpanded}>
          <CardContent sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="ログを検索..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: <Search color="action" />
                  }}
                />
              </Grid>

              <Grid item xs={6} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>レベル</InputLabel>
                  <Select
                    multiple
                    value={filters.level || []}
                    label="レベル"
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      level: e.target.value as LogEntry['level'][] 
                    }))}
                  >
                    <MenuItem value="debug">デバッグ</MenuItem>
                    <MenuItem value="info">情報</MenuItem>
                    <MenuItem value="warning">警告</MenuItem>
                    <MenuItem value="error">エラー</MenuItem>
                    <MenuItem value="critical">クリティカル</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={6} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>カテゴリ</InputLabel>
                  <Select
                    multiple
                    value={filters.category || []}
                    label="カテゴリ"
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      category: e.target.value as LogEntry['category'][] 
                    }))}
                  >
                    <MenuItem value="system">システム</MenuItem>
                    <MenuItem value="drone">ドローン</MenuItem>
                    <MenuItem value="vision">ビジョン</MenuItem>
                    <MenuItem value="api">API</MenuItem>
                    <MenuItem value="security">セキュリティ</MenuItem>
                    <MenuItem value="performance">パフォーマンス</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={6} md={2}>
                <DateTimePicker
                  label="開始時刻"
                  value={filters.start_time ? new Date(filters.start_time) : null}
                  onChange={(date) => setFilters(prev => ({ 
                    ...prev, 
                    start_time: date?.toISOString() 
                  }))}
                  slotProps={{ textField: { size: 'small', fullWidth: true } }}
                />
              </Grid>

              <Grid item xs={6} md={2}>
                <Button
                  variant="outlined"
                  startIcon={<Clear />}
                  onClick={handleClearFilters}
                  fullWidth
                >
                  クリア
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Collapse>

        <TableContainer
          ref={tableContainerRef}
          sx={{ maxHeight: compact ? 400 : 600 }}
        >
          <Table stickyHeader size={compact ? 'small' : 'medium'}>
            <TableHead>
              <TableRow>
                <TableCell width={20}></TableCell>
                <TableCell>タイムスタンプ</TableCell>
                <TableCell>レベル</TableCell>
                <TableCell>カテゴリ</TableCell>
                <TableCell>ソース</TableCell>
                <TableCell>メッセージ</TableCell>
                <TableCell>ユーザー</TableCell>
                <TableCell width={50}>詳細</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedLogs.map((log) => (
                <React.Fragment key={log.id}>
                  <TableRow
                    hover
                    onClick={() => handleRowClick(log)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={(e) => handleExpandRow(log.id, e)}
                      >
                        {expandedRows.has(log.id) ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {format(new Date(log.timestamp), 'MM/dd HH:mm:ss', { locale: ja })}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getLevelIcon(log.level)}
                        label={log.level}
                        size="small"
                        color={getLevelColor(log.level)}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getCategoryIcon(log.category)}
                        label={log.category}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{log.source}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          maxWidth: 300,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {log.message}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {log.user_id || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleRowClick(log)}>
                        <Visibility fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                  
                  <TableRow>
                    <TableCell colSpan={8} sx={{ py: 0 }}>
                      <Collapse in={expandedRows.has(log.id)}>
                        <Box sx={{ py: 2, pl: 4, bgcolor: 'action.hover' }}>
                          <Typography variant="body2" gutterBottom>
                            <strong>完全メッセージ:</strong> {log.message}
                          </Typography>
                          {log.details && (
                            <Typography variant="body2" gutterBottom>
                              <strong>詳細:</strong> {JSON.stringify(log.details)}
                            </Typography>
                          )}
                          <Typography variant="caption" color="text.secondary">
                            セッションID: {log.session_id} | リクエストID: {log.request_id}
                          </Typography>
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {totalPages > 1 && (
          <Box display="flex" justifyContent="center" p={2}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(event, value) => setPage(value)}
              color="primary"
            />
          </Box>
        )}
      </Card>

      <LogDetailDialog
        open={detailDialogOpen}
        log={selectedLog}
        onClose={() => setDetailDialogOpen(false)}
      />
    </Box>
  )
}

export default LogViewer