import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Paper,
  Tab,
  Tabs,
  Alert,
  CircularProgress,
  Fab,
  Tooltip,
} from '@mui/material'
import {
  Add as AddIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  GetApp as ExportIcon,
} from '@mui/icons-material'
import {
  DatasetStats,
  DatasetCard,
  DatasetSearch,
  CreateDatasetModal,
  ImageUpload,
  ImageGallery,
} from '../../components/dataset'
import { useNotification } from '../../hooks/useNotification'
import { visionApi, Dataset, DatasetImage } from '../../services/api/visionApi'
import type { UploadProgress } from '../../types/common'

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
      id={`dataset-tabpanel-${index}`}
      aria-labelledby={`dataset-tab-${index}`}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  )
}

interface DatasetFilters {
  search: string
  status: string
  type: string
  labels: string[]
}

export function DatasetManagement() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [filteredDatasets, setFilteredDatasets] = useState<Dataset[]>([])
  const [selectedDatasetImages, setSelectedDatasetImages] = useState<DatasetImage[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [activeTab, setActiveTab] = useState(0)
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null)
  const [imagePage, setImagePage] = useState(1)
  const [totalImagePages, setTotalImagePages] = useState(1)
  const [filters, setFilters] = useState<DatasetFilters>({
    search: '',
    status: '',
    type: '',
    labels: [],
  })

  const { showNotification } = useNotification()

  // Load datasets on component mount
  useEffect(() => {
    loadDatasets()
  }, [])

  // Apply filters when datasets or filters change
  useEffect(() => {
    applyFilters()
  }, [datasets, filters])

  // Load selected dataset images when dataset changes
  useEffect(() => {
    if (selectedDataset && activeTab === 1) {
      loadDatasetImages(selectedDataset.id, imagePage)
    }
  }, [selectedDataset, activeTab, imagePage])

  const loadDatasets = async () => {
    try {
      setLoading(true)
      const datasetsData = await visionApi.getDatasets()
      setDatasets(datasetsData)
    } catch (error) {
      console.error('Failed to load datasets:', error)
      showNotification('データセットの読み込みに失敗しました', 'error')
    } finally {
      setLoading(false)
    }
  }

  const loadDatasetImages = async (datasetId: string, page: number = 1) => {
    try {
      const response = await visionApi.getDatasetImages(datasetId, page, 20)
      setSelectedDatasetImages(response.images)
      setTotalImagePages(response.total_pages)
    } catch (error) {
      console.error('Failed to load dataset images:', error)
      showNotification('画像の読み込みに失敗しました', 'error')
    }
  }

  const applyFilters = () => {
    let filtered = [...datasets]

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      filtered = filtered.filter(dataset =>
        dataset.name.toLowerCase().includes(searchLower) ||
        (dataset.description && dataset.description.toLowerCase().includes(searchLower))
      )
    }

    // Status filter
    if (filters.status) {
      filtered = filtered.filter(dataset => dataset.status === filters.status)
    }

    // Type filter
    if (filters.type) {
      filtered = filtered.filter(dataset => dataset.type === filters.type)
    }

    // Labels filter
    if (filters.labels.length > 0) {
      filtered = filtered.filter(dataset =>
        filters.labels.some(label => dataset.labels.includes(label))
      )
    }

    setFilteredDatasets(filtered)
  }

  const handleCreateDataset = async (datasetData: Omit<Dataset, 'id' | 'created_at' | 'updated_at' | 'image_count' | 'label_count' | 'size_bytes'>) => {
    try {
      const newDataset = await visionApi.createDataset(datasetData)
      setDatasets(prev => [newDataset, ...prev])
      showNotification(`データセット "${newDataset.name}" が作成されました`, 'success')
    } catch (error) {
      console.error('Failed to create dataset:', error)
      showNotification('データセットの作成に失敗しました', 'error')
      throw error
    }
  }

  const handleDatasetView = (datasetId: string) => {
    const dataset = datasets.find(d => d.id === datasetId)
    if (dataset) {
      setSelectedDataset(dataset)
      setActiveTab(1)
      setImagePage(1)
    }
  }

  const handleDatasetEdit = (datasetId: string) => {
    showNotification('データセット編集機能は今後実装予定です', 'info')
  }

  const handleDatasetExport = async (datasetId: string) => {
    try {
      const dataset = datasets.find(d => d.id === datasetId)
      showNotification(`データセット "${dataset?.name}" のエクスポートを開始しました`, 'info')
      
      const result = await visionApi.exportDataset(datasetId, 'yolo')
      
      // Create download link
      const link = document.createElement('a')
      link.href = result.download_url
      link.download = `${dataset?.name}_export.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      showNotification('エクスポートが完了しました', 'success')
    } catch (error) {
      console.error('Failed to export dataset:', error)
      showNotification('エクスポートに失敗しました', 'error')
    }
  }

  const handleDatasetDelete = async (datasetId: string) => {
    try {
      const dataset = datasets.find(d => d.id === datasetId)
      await visionApi.deleteDataset(datasetId)
      setDatasets(prev => prev.filter(d => d.id !== datasetId))
      
      if (selectedDataset?.id === datasetId) {
        setSelectedDataset(null)
        setActiveTab(0)
      }
      
      showNotification(`データセット "${dataset?.name}" が削除されました`, 'success')
    } catch (error) {
      console.error('Failed to delete dataset:', error)
      showNotification('データセットの削除に失敗しました', 'error')
    }
  }

  const handleImageUpload = async (files: File[], onProgress: (progress: UploadProgress) => void) => {
    if (!selectedDataset) {
      throw new Error('No dataset selected')
    }

    try {
      setUploading(true)
      const result = await visionApi.uploadImages(selectedDataset.id, files, onProgress)
      
      // Refresh dataset info and images
      await loadDatasets()
      await loadDatasetImages(selectedDataset.id, imagePage)
      
      showNotification(`${result.uploaded} 枚の画像がアップロードされました`, 'success')
      
      if (result.failed > 0) {
        showNotification(`${result.failed} 枚の画像のアップロードに失敗しました`, 'warning')
      }
    } catch (error) {
      console.error('Failed to upload images:', error)
      showNotification('画像のアップロードに失敗しました', 'error')
      throw error
    } finally {
      setUploading(false)
    }
  }

  const handleImageView = (imageId: string) => {
    showNotification('画像詳細表示機能は今後実装予定です', 'info')
  }

  const handleImageEdit = (imageId: string) => {
    showNotification('画像ラベリング機能は今後実装予定です', 'info')
  }

  const handleImageDelete = async (imageId: string) => {
    if (!selectedDataset) return

    try {
      await visionApi.deleteImage(selectedDataset.id, imageId)
      await loadDatasetImages(selectedDataset.id, imagePage)
      showNotification('画像が削除されました', 'success')
    } catch (error) {
      console.error('Failed to delete image:', error)
      showNotification('画像の削除に失敗しました', 'error')
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue)
  }

  const handleRefresh = () => {
    loadDatasets()
    if (selectedDataset && activeTab === 1) {
      loadDatasetImages(selectedDataset.id, imagePage)
    }
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          📁 データセット管理
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={loading}
          >
            更新
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateModalOpen(true)}
          >
            新規データセット
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="データセット一覧" />
          <Tab 
            label={selectedDataset ? `画像管理: ${selectedDataset.name}` : '画像管理'} 
            disabled={!selectedDataset}
          />
        </Tabs>
      </Box>

      {/* Tab Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {/* Dataset List Tab */}
        <TabPanel value={activeTab} index={0}>
          <Box display="flex" flexDirection="column" gap={3}>
            {/* Statistics */}
            <DatasetStats datasets={datasets} loading={loading} />

            {/* Search and Filters */}
            <Paper elevation={1} sx={{ p: 3 }}>
              <DatasetSearch
                datasets={datasets}
                filters={filters}
                onFiltersChange={setFilters}
              />
            </Paper>

            {/* Dataset Grid */}
            {loading ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            ) : filteredDatasets.length > 0 ? (
              <Grid container spacing={3}>
                {filteredDatasets.map((dataset) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={dataset.id}>
                    <DatasetCard
                      dataset={dataset}
                      onView={handleDatasetView}
                      onEdit={handleDatasetEdit}
                      onExport={handleDatasetExport}
                      onDelete={handleDatasetDelete}
                    />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Alert severity="info">
                <Typography variant="body1">
                  {filters.search || filters.status || filters.type || filters.labels.length > 0
                    ? 'フィルタ条件に一致するデータセットが見つかりません'
                    : 'データセットがありません。新しいデータセットを作成してください。'
                  }
                </Typography>
              </Alert>
            )}
          </Box>
        </TabPanel>

        {/* Image Management Tab */}
        <TabPanel value={activeTab} index={1}>
          {selectedDataset ? (
            <Box display="flex" flexDirection="column" gap={3}>
              {/* Dataset Info */}
              <Paper elevation={1} sx={{ p: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography variant="h5" gutterBottom>
                      {selectedDataset.name}
                    </Typography>
                    <Typography variant="body1" color="text.secondary" gutterBottom>
                      {selectedDataset.description}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedDataset.image_count} 枚の画像 • {selectedDataset.label_count} ラベル
                    </Typography>
                  </Box>
                  <Button
                    variant="outlined"
                    onClick={() => setActiveTab(0)}
                  >
                    データセット一覧に戻る
                  </Button>
                </Box>
              </Paper>

              {/* Image Upload */}
              <Paper elevation={1} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  画像アップロード
                </Typography>
                <ImageUpload
                  datasetId={selectedDataset.id}
                  onUpload={handleImageUpload}
                  disabled={uploading}
                />
              </Paper>

              {/* Image Gallery */}
              <Paper elevation={1} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  画像一覧
                </Typography>
                <ImageGallery
                  images={selectedDatasetImages}
                  page={imagePage}
                  totalPages={totalImagePages}
                  onPageChange={setImagePage}
                  onImageView={handleImageView}
                  onImageEdit={handleImageEdit}
                  onImageDelete={handleImageDelete}
                  selectable={true}
                />
              </Paper>
            </Box>
          ) : (
            <Alert severity="info">
              データセットを選択してください
            </Alert>
          )}
        </TabPanel>
      </Box>

      {/* Floating Action Button */}
      {activeTab === 0 && (
        <Fab
          color="primary"
          sx={{ position: 'fixed', bottom: 24, right: 24 }}
          onClick={() => setCreateModalOpen(true)}
        >
          <Tooltip title="新規データセット作成">
            <AddIcon />
          </Tooltip>
        </Fab>
      )}

      {/* Create Dataset Modal */}
      <CreateDatasetModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSubmit={handleCreateDataset}
        loading={uploading}
      />
    </Box>
  )
}