import React, { useCallback, useState } from 'react'
import {
  Box,
  Typography,
  Button,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Alert,
  Chip,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Image as ImageIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import { UploadProgress } from '../../../types/common'

interface FileWithProgress {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
}

interface ImageUploadProps {
  datasetId: string
  onUpload: (files: File[], onProgress: (progress: UploadProgress) => void) => Promise<void>
  onUploadComplete?: (uploadedCount: number, failedCount: number) => void
  maxFiles?: number
  maxFileSize?: number // in bytes
  accept?: Record<string, string[]>
  multiple?: boolean
  disabled?: boolean
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  datasetId,
  onUpload,
  onUploadComplete,
  maxFiles = 100,
  maxFileSize = 10 * 1024 * 1024, // 10MB default
  accept = {
    'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
  },
  multiple = true,
  disabled = false,
}) => {
  const [files, setFiles] = useState<FileWithProgress[]>([])
  const [uploading, setUploading] = useState(false)
  const [totalProgress, setTotalProgress] = useState(0)

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      console.warn('Some files were rejected:', rejectedFiles)
    }

    // Add accepted files to the list
    const newFiles: FileWithProgress[] = acceptedFiles.map(file => ({
      file,
      progress: 0,
      status: 'pending'
    }))

    setFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple,
    disabled: disabled || uploading,
    maxFiles,
    maxSize: maxFileSize,
  })

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const clearAll = () => {
    setFiles([])
    setTotalProgress(0)
  }

  const startUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    setTotalProgress(0)

    try {
      const filesToUpload = files.filter(f => f.status === 'pending').map(f => f.file)
      
      if (filesToUpload.length === 0) {
        setUploading(false)
        return
      }

      // Update status to uploading
      setFiles(prev => prev.map(f => 
        f.status === 'pending' ? { ...f, status: 'uploading' } : f
      ))

      let completedFiles = 0
      const totalFiles = filesToUpload.length

      const onProgress = (progress: UploadProgress) => {
        const overallProgress = (completedFiles / totalFiles * 100) + (progress.percentage / totalFiles)
        setTotalProgress(Math.min(overallProgress, 100))
      }

      await onUpload(filesToUpload, onProgress)

      // Mark all files as completed
      setFiles(prev => prev.map(f => 
        f.status === 'uploading' ? { ...f, status: 'completed', progress: 100 } : f
      ))

      setTotalProgress(100)
      onUploadComplete?.(filesToUpload.length, 0)

    } catch (error) {
      console.error('Upload failed:', error)
      
      // Mark files as error
      setFiles(prev => prev.map(f => 
        f.status === 'uploading' ? { 
          ...f, 
          status: 'error', 
          error: error instanceof Error ? error.message : 'Upload failed'
        } : f
      ))

      onUploadComplete?.(0, files.filter(f => f.status === 'uploading').length)
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckIcon color="success" />
      case 'error':
        return <ErrorIcon color="error" />
      case 'uploading':
        return <UploadIcon color="primary" />
      default:
        return <ImageIcon color="action" />
    }
  }

  const pendingFiles = files.filter(f => f.status === 'pending')
  const hasFiles = files.length > 0
  const canUpload = pendingFiles.length > 0 && !uploading

  return (
    <Box>
      {/* Drop Zone */}
      <Box
        {...getRootProps()}
        sx={{
          border: 2,
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderStyle: 'dashed',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: disabled || uploading ? 'not-allowed' : 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'transparent',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: disabled || uploading ? 'grey.300' : 'primary.main',
            backgroundColor: disabled || uploading ? 'transparent' : 'action.hover',
          }
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        
        {isDragActive ? (
          <Typography variant="h6" color="primary">
            ファイルをドロップしてください
          </Typography>
        ) : (
          <>
            <Typography variant="h6" gutterBottom>
              画像をドラッグ&ドロップ
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              または、クリックしてファイルを選択
            </Typography>
            <Typography variant="caption" color="text.secondary">
              最大 {maxFiles} ファイル、{formatFileSize(maxFileSize)} まで
            </Typography>
          </>
        )}
      </Box>

      {/* Upload Progress */}
      {uploading && (
        <Box mt={2}>
          <Typography variant="body2" gutterBottom>
            アップロード中... {Math.round(totalProgress)}%
          </Typography>
          <LinearProgress variant="determinate" value={totalProgress} />
        </Box>
      )}

      {/* File List */}
      {hasFiles && (
        <Box mt={3}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              選択されたファイル ({files.length})
            </Typography>
            <Box display="flex" gap={1}>
              {canUpload && (
                <Button
                  variant="contained"
                  startIcon={<UploadIcon />}
                  onClick={startUpload}
                  disabled={uploading}
                >
                  アップロード開始
                </Button>
              )}
              <Button
                variant="outlined"
                onClick={clearAll}
                disabled={uploading}
              >
                全てクリア
              </Button>
            </Box>
          </Box>

          {/* Summary Stats */}
          <Box display="flex" gap={1} mb={2}>
            <Chip 
              label={`待機中: ${pendingFiles.length}`} 
              size="small" 
              color="default" 
            />
            <Chip 
              label={`完了: ${files.filter(f => f.status === 'completed').length}`} 
              size="small" 
              color="success" 
            />
            <Chip 
              label={`エラー: ${files.filter(f => f.status === 'error').length}`} 
              size="small" 
              color="error" 
            />
          </Box>

          <List dense>
            {files.map((fileWithProgress, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <IconButton
                    edge="end"
                    onClick={() => removeFile(index)}
                    disabled={uploading && fileWithProgress.status === 'uploading'}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  {getStatusIcon(fileWithProgress.status)}
                </ListItemIcon>
                <ListItemText
                  primary={fileWithProgress.file.name}
                  secondary={
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        {formatFileSize(fileWithProgress.file.size)}
                      </Typography>
                      {fileWithProgress.error && (
                        <Typography variant="caption" color="error" display="block">
                          エラー: {fileWithProgress.error}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Help Text */}
      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          サポートされている形式: JPEG, PNG, GIF, BMP, WebP
        </Typography>
      </Alert>
    </Box>
  )
}