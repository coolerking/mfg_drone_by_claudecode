import {
  Box,
  Typography,
  Grid,
  Fab,
  Container,
  Pagination,
  Alert,
  CircularProgress,
  Paper,
  Tabs,
  Tab,
  Button,
  Menu,
  MenuItem,
  Breadcrumbs,
  Link
} from '@mui/material'
import {
  Add,
  PlayArrow,
  CloudDownload,
  MoreVert,
  Home,
  School
} from '@mui/icons-material'
import { useState, useEffect, useMemo } from 'react'
import { useNotification } from '@/hooks/useNotification'
import { useWebSocket } from '@/hooks/useWebSocket'
import { modelApi, type Model, type TrainingJob, type TrainingConfig as TrainingConfigType } from '@/services/api/modelApi'
import {
  ModelStats,
  ModelCard,
  ModelSearch,
  CreateModelModal,
  TrainingConfig,
  TrainingProgress,
  type ModelFilters,
  type ModelSortConfig
} from '@/components/model'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`model-tabpanel-${index}`}
      aria-labelledby={`model-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

function a11yProps(index: number) {
  return {
    id: `model-tab-${index}`,
    'aria-controls': `model-tabpanel-${index}`,
  }
}

export function ModelManagement() {
  const { showNotification } = useNotification()
  const { isConnected } = useWebSocket()
  
  // State
  const [models, setModels] = useState<Model[]>([])
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  
  // UI State
  const [currentTab, setCurrentTab] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(12)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  
  // Modal State
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [trainingConfigOpen, setTrainingConfigOpen] = useState(false)
  const [trainingProgressOpen, setTrainingProgressOpen] = useState(false)
  const [selectedModel, setSelectedModel] = useState<Model | null>(null)
  const [selectedTrainingJob, setSelectedTrainingJob] = useState<TrainingJob | null>(null)
  
  // Search and Filter State
  const [filters, setFilters] = useState<ModelFilters>({
    search: '',
    status: 'all',
    type: 'all',
    minAccuracy: 0,
    maxAccuracy: 100,
    hasClasses: [],
    dateRange: 'all'
  })
  
  const [sortConfig, setSortConfig] = useState<ModelSortConfig>({
    field: 'updated_at',
    direction: 'desc'
  })

  // Data fetching
  useEffect(() => {
    fetchData()
  }, [refreshTrigger])

  useEffect(() => {
    // Auto-refresh training jobs every 30 seconds
    const interval = setInterval(() => {
      fetchTrainingJobs()
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [modelsData, trainingJobsData] = await Promise.all([
        modelApi.getModels(),
        modelApi.getTrainingJobs()
      ])
      
      setModels(modelsData)
      setTrainingJobs(trainingJobsData)
    } catch (err) {
      console.error('Error fetching data:', err)
      setError('データの取得に失敗しました')
      showNotification('error', 'データの取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const fetchTrainingJobs = async () => {
    try {
      const jobsData = await modelApi.getTrainingJobs()
      setTrainingJobs(jobsData)
    } catch (err) {
      console.error('Error fetching training jobs:', err)
    }
  }

  // Filter and sort models
  const filteredAndSortedModels = useMemo(() => {
    let filtered = models

    // Apply filters
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      filtered = filtered.filter(model =>
        model.name.toLowerCase().includes(searchLower) ||
        (model.description && model.description.toLowerCase().includes(searchLower))
      )
    }

    if (filters.status !== 'all') {
      filtered = filtered.filter(model => model.status === filters.status)
    }

    if (filters.type !== 'all') {
      filtered = filtered.filter(model => model.type === filters.type)
    }

    if (filters.minAccuracy > 0 || filters.maxAccuracy < 100) {
      filtered = filtered.filter(model => {
        const accuracy = model.accuracy || 0
        return accuracy >= filters.minAccuracy && accuracy <= filters.maxAccuracy
      })
    }

    if (filters.hasClasses.length > 0) {
      filtered = filtered.filter(model =>
        filters.hasClasses.every(className =>
          model.classes.includes(className)
        )
      )
    }

    if (filters.dateRange !== 'all') {
      const now = new Date()
      const cutoffDate = new Date()
      
      switch (filters.dateRange) {
        case 'last7days':
          cutoffDate.setDate(now.getDate() - 7)
          break
        case 'last30days':
          cutoffDate.setDate(now.getDate() - 30)
          break
        case 'last90days':
          cutoffDate.setDate(now.getDate() - 90)
          break
      }
      
      filtered = filtered.filter(model =>
        new Date(model.created_at) >= cutoffDate
      )
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any = a[sortConfig.field]
      let bValue: any = b[sortConfig.field]

      // Handle null/undefined values
      if (aValue == null) aValue = 0
      if (bValue == null) bValue = 0

      // Convert dates to timestamps for comparison
      if (sortConfig.field === 'created_at' || sortConfig.field === 'updated_at') {
        aValue = new Date(aValue).getTime()
        bValue = new Date(bValue).getTime()
      }

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1
      }
      return 0
    })

    return filtered
  }, [models, filters, sortConfig])

  // Pagination
  const paginatedModels = useMemo(() => {
    const startIndex = (page - 1) * pageSize
    return filteredAndSortedModels.slice(startIndex, startIndex + pageSize)
  }, [filteredAndSortedModels, page, pageSize])

  const totalPages = Math.ceil(filteredAndSortedModels.length / pageSize)

  // Get all available classes for filtering
  const availableClasses = useMemo(() => {
    const classSet = new Set<string>()
    models.forEach(model => {
      model.classes.forEach(className => classSet.add(className))
    })
    return Array.from(classSet).sort()
  }, [models])

  // Event handlers
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
    setPage(1) // Reset to first page when changing tabs
  }

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value)
  }

  const handleModelCreate = (newModel: Model) => {
    setModels(prev => [newModel, ...prev])
    setRefreshTrigger(prev => prev + 1)
  }

  const handleModelUpdate = (updatedModel: Model) => {
    setModels(prev => prev.map(model => 
      model.id === updatedModel.id ? updatedModel : model
    ))
  }

  const handleModelDelete = (modelId: string) => {
    setModels(prev => prev.filter(model => model.id !== modelId))
  }

  const handleStartTraining = async (modelName: string, config: TrainingConfigType) => {
    try {
      const result = await modelApi.startTraining(modelName, config)
      showNotification('success', '学習を開始しました')
      setRefreshTrigger(prev => prev + 1)
      setTrainingConfigOpen(false)
      setSelectedModel(null)
    } catch (error) {
      console.error('Error starting training:', error)
      showNotification('error', '学習の開始に失敗しました')
      throw error
    }
  }

  const handleViewTraining = (model: Model) => {
    const job = trainingJobs.find(j => j.model_id === model.id && j.status === 'running')
    if (job) {
      setSelectedTrainingJob(job)
      setTrainingProgressOpen(true)
    }
  }

  const handleTrainingJobUpdate = (updatedJob: TrainingJob) => {
    setTrainingJobs(prev => prev.map(job =>
      job.id === updatedJob.id ? updatedJob : job
    ))
  }

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleDownloadPretrainedModels = () => {
    // This would open a dialog to browse and download pretrained models
    showNotification('info', '事前学習済みモデルブラウザは開発中です')
    handleMenuClose()
  }

  const runningTrainingJobs = trainingJobs.filter(job => 
    job.status === 'running' || job.status === 'pending'
  )

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ ml: 2 }}>
            モデルデータを読み込み中...
          </Typography>
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={() => setRefreshTrigger(prev => prev + 1)}>
          再試行
        </Button>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link href="/dashboard" color="inherit" display="flex" alignItems="center">
          <Home sx={{ mr: 0.5 }} fontSize="inherit" />
          ダッシュボード
        </Link>
        <Typography color="text.primary" display="flex" alignItems="center">
          <School sx={{ mr: 0.5 }} fontSize="inherit" />
          モデル管理
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          モデル管理
        </Typography>
        
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<MoreVert />}
            onClick={handleMenuOpen}
          >
            その他
          </Button>
          
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateModalOpen(true)}
          >
            新規モデル作成
          </Button>
        </Box>
      </Box>

      {/* Running Training Jobs Alert */}
      {runningTrainingJobs.length > 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {runningTrainingJobs.length} 件の学習ジョブが実行中です。
          {runningTrainingJobs.map(job => (
            <Button
              key={job.id}
              size="small"
              onClick={() => {
                setSelectedTrainingJob(job)
                setTrainingProgressOpen(true)
              }}
              sx={{ ml: 1 }}
            >
              {job.model_id} を表示
            </Button>
          ))}
        </Alert>
      )}

      {/* WebSocket Status */}
      {!isConnected && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          リアルタイム更新が無効です。学習進捗の自動更新が利用できません。
        </Alert>
      )}

      {/* Statistics */}
      <ModelStats 
        onStatsChange={() => {}} 
        refreshTrigger={refreshTrigger}
      />

      {/* Tabs */}
      <Paper sx={{ mt: 3 }}>
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="モデル一覧" {...a11yProps(0)} />
          <Tab label="学習ジョブ" {...a11yProps(1)} />
        </Tabs>

        {/* Models Tab */}
        <TabPanel value={currentTab} index={0}>
          {/* Search and Filters */}
          <ModelSearch
            filters={filters}
            sortConfig={sortConfig}
            onFiltersChange={setFilters}
            onSortChange={setSortConfig}
            availableClasses={availableClasses}
            totalResults={filteredAndSortedModels.length}
          />

          {/* Models Grid */}
          {paginatedModels.length > 0 ? (
            <>
              <Grid container spacing={3}>
                {paginatedModels.map((model) => (
                  <Grid item xs={12} md={6} lg={4} key={model.id}>
                    <ModelCard
                      model={model}
                      onUpdate={handleModelUpdate}
                      onDelete={handleModelDelete}
                      onStartTraining={(model) => {
                        setSelectedModel(model)
                        setTrainingConfigOpen(true)
                      }}
                      onViewTraining={handleViewTraining}
                      onEvaluate={(model) => {
                        showNotification('info', 'モデル評価機能は開発中です')
                      }}
                      onDeploy={handleModelUpdate}
                    />
                  </Grid>
                ))}
              </Grid>

              {/* Pagination */}
              {totalPages > 1 && (
                <Box display="flex" justifyContent="center" mt={4}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={handlePageChange}
                    color="primary"
                    size="large"
                  />
                </Box>
              )}
            </>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                モデルが見つかりません
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                フィルタ条件を変更するか、新しいモデルを作成してください。
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setCreateModalOpen(true)}
              >
                新規モデル作成
              </Button>
            </Paper>
          )}
        </TabPanel>

        {/* Training Jobs Tab */}
        <TabPanel value={currentTab} index={1}>
          {trainingJobs.length > 0 ? (
            <Grid container spacing={2}>
              {trainingJobs.map((job) => (
                <Grid item xs={12} key={job.id}>
                  <Paper sx={{ p: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="h6">
                          {job.model_id}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {job.status === 'running' ? '実行中' : 
                           job.status === 'completed' ? '完了' : 
                           job.status === 'failed' ? '失敗' : 
                           job.status === 'cancelled' ? 'キャンセル済み' : '待機中'}
                          {job.status === 'running' && (
                            <span> - {job.progress.progress.toFixed(1)}% (エポック {job.progress.epoch})</span>
                          )}
                        </Typography>
                      </Box>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => {
                          setSelectedTrainingJob(job)
                          setTrainingProgressOpen(true)
                        }}
                      >
                        詳細表示
                      </Button>
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                学習ジョブがありません
              </Typography>
              <Typography variant="body2" color="text.secondary">
                モデルの学習を開始すると、ここに表示されます。
              </Typography>
            </Paper>
          )}
        </TabPanel>
      </Paper>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="新規学習開始"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setTrainingConfigOpen(true)}
      >
        <PlayArrow />
      </Fab>

      {/* Modals */}
      <CreateModelModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSuccess={handleModelCreate}
      />

      <TrainingConfig
        open={trainingConfigOpen}
        onClose={() => {
          setTrainingConfigOpen(false)
          setSelectedModel(null)
        }}
        onStartTraining={handleStartTraining}
        model={selectedModel || undefined}
      />

      {selectedTrainingJob && (
        <TrainingProgress
          open={trainingProgressOpen}
          onClose={() => {
            setTrainingProgressOpen(false)
            setSelectedTrainingJob(null)
          }}
          trainingJob={selectedTrainingJob}
          onJobUpdate={handleTrainingJobUpdate}
        />
      )}

      {/* Additional Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleDownloadPretrainedModels}>
          <CloudDownload sx={{ mr: 1 }} fontSize="small" />
          事前学習済みモデル
        </MenuItem>
      </Menu>
    </Container>
  )
}