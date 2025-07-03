import { api } from './apiClient'
import type { UploadProgress } from '../../types/common'

export interface Dataset {
  id: string
  name: string
  description?: string
  type: 'training' | 'validation' | 'test'
  status: 'active' | 'processing' | 'archived'
  image_count: number
  label_count: number
  created_at: string
  updated_at: string
  size_bytes: number
  labels: string[]
}

export interface DatasetImage {
  id: string
  filename: string
  path: string
  size_bytes: number
  width: number
  height: number
  labels: ImageLabel[]
  uploaded_at: string
  labeled: boolean
}

export interface ImageLabel {
  id: string
  class_name: string
  bbox: {
    x: number
    y: number
    width: number
    height: number
  }
  confidence: number
  verified: boolean
}

export interface LabelingSession {
  id: string
  dataset_id: string
  user_id: string
  images_processed: number
  labels_created: number
  started_at: string
  completed_at?: string
}

export class VisionApiService {
  private basePath = '/vision'

  // Dataset management
  async getDatasets(): Promise<Dataset[]> {
    return api.get<Dataset[]>(`${this.basePath}/datasets`)
  }

  async getDataset(datasetId: string): Promise<Dataset> {
    return api.get<Dataset>(`${this.basePath}/datasets/${datasetId}`)
  }

  async createDataset(dataset: Omit<Dataset, 'id' | 'created_at' | 'updated_at' | 'image_count' | 'label_count' | 'size_bytes'>): Promise<Dataset> {
    return api.post<Dataset>(`${this.basePath}/datasets`, dataset)
  }

  async updateDataset(datasetId: string, updates: Partial<Dataset>): Promise<Dataset> {
    return api.patch<Dataset>(`${this.basePath}/datasets/${datasetId}`, updates)
  }

  async deleteDataset(datasetId: string): Promise<{ success: boolean }> {
    return api.delete(`${this.basePath}/datasets/${datasetId}`)
  }

  // Image management
  async getDatasetImages(
    datasetId: string,
    page = 1,
    limit = 20,
    labeled?: boolean
  ): Promise<{
    images: DatasetImage[]
    total: number
    page: number
    limit: number
    total_pages: number
  }> {
    return api.get(`${this.basePath}/datasets/${datasetId}/images`, {
      params: { page, limit, labeled }
    })
  }

  async uploadImages(
    datasetId: string,
    files: File[],
    onProgress?: (progress: UploadProgress) => void
  ): Promise<{ uploaded: number; failed: number; images: DatasetImage[] }> {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    return api.post(`${this.basePath}/datasets/${datasetId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = {
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage: Math.round((progressEvent.loaded * 100) / progressEvent.total)
          }
          onProgress(progress)
        }
      },
    })
  }

  async deleteImage(datasetId: string, imageId: string): Promise<{ success: boolean }> {
    return api.delete(`${this.basePath}/datasets/${datasetId}/images/${imageId}`)
  }

  async getImage(datasetId: string, imageId: string): Promise<DatasetImage> {
    return api.get<DatasetImage>(`${this.basePath}/datasets/${datasetId}/images/${imageId}`)
  }

  // Image labeling
  async getImageLabels(datasetId: string, imageId: string): Promise<ImageLabel[]> {
    return api.get<ImageLabel[]>(`${this.basePath}/datasets/${datasetId}/images/${imageId}/labels`)
  }

  async addImageLabel(
    datasetId: string,
    imageId: string,
    label: Omit<ImageLabel, 'id'>
  ): Promise<ImageLabel> {
    return api.post<ImageLabel>(`${this.basePath}/datasets/${datasetId}/images/${imageId}/labels`, label)
  }

  async updateImageLabel(
    datasetId: string,
    imageId: string,
    labelId: string,
    updates: Partial<ImageLabel>
  ): Promise<ImageLabel> {
    return api.patch<ImageLabel>(`${this.basePath}/datasets/${datasetId}/images/${imageId}/labels/${labelId}`, updates)
  }

  async deleteImageLabel(
    datasetId: string,
    imageId: string,
    labelId: string
  ): Promise<{ success: boolean }> {
    return api.delete(`${this.basePath}/datasets/${datasetId}/images/${imageId}/labels/${labelId}`)
  }

  // Auto-labeling
  async autoLabelDataset(
    datasetId: string,
    modelId: string,
    confidenceThreshold = 0.7
  ): Promise<{ job_id: string }> {
    return api.post(`${this.basePath}/datasets/${datasetId}/auto-label`, {
      model_id: modelId,
      confidence_threshold: confidenceThreshold
    })
  }

  async getAutoLabelStatus(jobId: string): Promise<{
    status: 'pending' | 'running' | 'completed' | 'failed'
    progress: number
    images_processed: number
    labels_created: number
    error?: string
  }> {
    return api.get(`${this.basePath}/auto-label/${jobId}/status`)
  }

  // Dataset statistics
  async getDatasetStatistics(datasetId: string): Promise<{
    total_images: number
    labeled_images: number
    unlabeled_images: number
    label_distribution: { [className: string]: number }
    average_labels_per_image: number
    dataset_size_mb: number
  }> {
    return api.get(`${this.basePath}/datasets/${datasetId}/statistics`)
  }

  // Export/Import
  async exportDataset(
    datasetId: string,
    format: 'yolo' | 'coco' | 'pascal_voc' = 'yolo'
  ): Promise<{ download_url: string }> {
    return api.post(`${this.basePath}/datasets/${datasetId}/export`, { format })
  }

  async importDataset(
    file: File,
    format: 'yolo' | 'coco' | 'pascal_voc',
    datasetName: string
  ): Promise<{ dataset_id: string; import_job_id: string }> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('format', format)
    formData.append('dataset_name', datasetName)

    return api.post(`${this.basePath}/datasets/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  }

  // Object detection and tracking
  async detectObjects(
    imageFile: File,
    modelId?: string
  ): Promise<{
    objects: Array<{
      class_name: string
      confidence: number
      bbox: { x: number; y: number; width: number; height: number }
    }>
    processing_time: number
  }> {
    const formData = new FormData()
    formData.append('image', imageFile)
    if (modelId) {
      formData.append('model_id', modelId)
    }

    return api.post(`${this.basePath}/detect`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  }

  async startObjectTracking(
    droneId: string,
    targetClass: string,
    modelId?: string
  ): Promise<{ success: boolean; tracking_id: string }> {
    return api.post(`${this.basePath}/tracking/start`, {
      drone_id: droneId,
      target_class: targetClass,
      model_id: modelId
    })
  }

  async stopObjectTracking(trackingId: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/tracking/${trackingId}/stop`)
  }

  async getTrackingStatus(trackingId: string): Promise<{
    status: 'active' | 'paused' | 'stopped'
    target_detected: boolean
    confidence: number
    bbox?: { x: number; y: number; width: number; height: number }
    drone_position?: { x: number; y: number; z: number }
  }> {
    return api.get(`${this.basePath}/tracking/${trackingId}/status`)
  }

  // Class management
  async getAvailableClasses(): Promise<string[]> {
    return api.get<string[]>(`${this.basePath}/classes`)
  }

  async addCustomClass(className: string, description?: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/classes`, {
      name: className,
      description
    })
  }

  async deleteCustomClass(className: string): Promise<{ success: boolean }> {
    return api.delete(`${this.basePath}/classes/${className}`)
  }
}

// Export singleton instance
export const visionApi = new VisionApiService()