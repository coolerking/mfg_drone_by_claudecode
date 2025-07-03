import { api } from './apiClient'
import type { TrainingProgress } from '../../types/common'

export interface Model {
  id: string
  name: string
  description?: string
  type: 'yolo' | 'custom' | 'pretrained'
  status: 'trained' | 'training' | 'failed' | 'archived'
  version: string
  accuracy?: number
  map_score?: number
  precision?: number
  recall?: number
  f1_score?: number
  training_dataset_id?: string
  validation_dataset_id?: string
  created_at: string
  updated_at: string
  file_size_mb: number
  classes: string[]
  training_epochs: number
  training_time_hours?: number
}

export interface TrainingConfig {
  dataset_id: string
  validation_dataset_id?: string
  model_type: 'yolov8n' | 'yolov8s' | 'yolov8m' | 'yolov8l' | 'yolov8x'
  epochs: number
  batch_size: number
  learning_rate: number
  image_size: number
  patience: number
  save_period: number
  augment: boolean
  mosaic: boolean
  mixup: boolean
  copy_paste: boolean
}

export interface TrainingJob {
  id: string
  model_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: TrainingProgress
  config: TrainingConfig
  started_at?: string
  completed_at?: string
  error_message?: string
  metrics: {
    epoch: number
    train_loss: number
    val_loss: number
    map50: number
    map50_95: number
    precision: number
    recall: number
  }[]
}

export interface ModelEvaluation {
  model_id: string
  dataset_id: string
  accuracy: number
  map_score: number
  precision: number
  recall: number
  f1_score: number
  class_metrics: {
    [className: string]: {
      precision: number
      recall: number
      f1_score: number
      ap: number
    }
  }
  confusion_matrix: number[][]
  evaluation_time: number
}

export interface ModelInference {
  model_id: string
  input_type: 'image' | 'video' | 'stream'
  results: {
    objects: Array<{
      class_name: string
      confidence: number
      bbox: { x: number; y: number; width: number; height: number }
    }>
    processing_time: number
    image_size: { width: number; height: number }
  }
}

export class ModelApiService {
  private basePath = '/models'

  // Model management
  async getModels(): Promise<Model[]> {
    return api.get<Model[]>(this.basePath)
  }

  async getModel(modelId: string): Promise<Model> {
    return api.get<Model>(`${this.basePath}/${modelId}`)
  }

  async createModel(model: Omit<Model, 'id' | 'created_at' | 'updated_at' | 'file_size_mb'>): Promise<Model> {
    return api.post<Model>(this.basePath, model)
  }

  async updateModel(modelId: string, updates: Partial<Model>): Promise<Model> {
    return api.patch<Model>(`${this.basePath}/${modelId}`, updates)
  }

  async deleteModel(modelId: string): Promise<{ success: boolean }> {
    return api.delete(`${this.basePath}/${modelId}`)
  }

  async duplicateModel(modelId: string, newName: string): Promise<Model> {
    return api.post<Model>(`${this.basePath}/${modelId}/duplicate`, { name: newName })
  }

  // Model training
  async startTraining(
    modelName: string,
    config: TrainingConfig
  ): Promise<{ model_id: string; job_id: string }> {
    return api.post(`${this.basePath}/train`, {
      name: modelName,
      config
    })
  }

  async getTrainingJob(jobId: string): Promise<TrainingJob> {
    return api.get<TrainingJob>(`${this.basePath}/training/${jobId}`)
  }

  async getTrainingJobs(modelId?: string): Promise<TrainingJob[]> {
    const params = modelId ? { model_id: modelId } : {}
    return api.get<TrainingJob[]>(`${this.basePath}/training`, { params })
  }

  async pauseTraining(jobId: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/training/${jobId}/pause`)
  }

  async resumeTraining(jobId: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/training/${jobId}/resume`)
  }

  async cancelTraining(jobId: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/training/${jobId}/cancel`)
  }

  async getTrainingLogs(jobId: string): Promise<string[]> {
    return api.get<string[]>(`${this.basePath}/training/${jobId}/logs`)
  }

  async getTrainingMetrics(jobId: string): Promise<TrainingJob['metrics']> {
    return api.get(`${this.basePath}/training/${jobId}/metrics`)
  }

  // Model evaluation
  async evaluateModel(
    modelId: string,
    datasetId: string,
    confidenceThreshold = 0.5,
    iouThreshold = 0.5
  ): Promise<{ evaluation_id: string }> {
    return api.post(`${this.basePath}/${modelId}/evaluate`, {
      dataset_id: datasetId,
      confidence_threshold: confidenceThreshold,
      iou_threshold: iouThreshold
    })
  }

  async getEvaluation(evaluationId: string): Promise<ModelEvaluation> {
    return api.get<ModelEvaluation>(`${this.basePath}/evaluation/${evaluationId}`)
  }

  async getModelEvaluations(modelId: string): Promise<ModelEvaluation[]> {
    return api.get<ModelEvaluation[]>(`${this.basePath}/${modelId}/evaluations`)
  }

  // Model inference
  async predictImage(
    modelId: string,
    imageFile: File,
    confidenceThreshold = 0.5
  ): Promise<ModelInference['results']> {
    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('confidence', confidenceThreshold.toString())

    return api.post(`${this.basePath}/${modelId}/predict`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  }

  async predictBatch(
    modelId: string,
    imageFiles: File[],
    confidenceThreshold = 0.5
  ): Promise<{ batch_id: string }> {
    const formData = new FormData()
    imageFiles.forEach((file) => {
      formData.append('images', file)
    })
    formData.append('confidence', confidenceThreshold.toString())

    return api.post(`${this.basePath}/${modelId}/predict/batch`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  }

  async getBatchResults(batchId: string): Promise<{
    status: 'pending' | 'processing' | 'completed' | 'failed'
    results: ModelInference['results'][]
    progress: number
  }> {
    return api.get(`${this.basePath}/prediction/batch/${batchId}`)
  }

  // Model deployment
  async deployModel(modelId: string): Promise<{ success: boolean; endpoint_url: string }> {
    return api.post(`${this.basePath}/${modelId}/deploy`)
  }

  async undeployModel(modelId: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/${modelId}/undeploy`)
  }

  async getModelStatus(modelId: string): Promise<{
    deployed: boolean
    endpoint_url?: string
    last_used?: string
    usage_count: number
  }> {
    return api.get(`${this.basePath}/${modelId}/status`)
  }

  // Model export/import
  async exportModel(
    modelId: string,
    format: 'onnx' | 'tensorrt' | 'torchscript' = 'onnx'
  ): Promise<{ download_url: string }> {
    return api.post(`${this.basePath}/${modelId}/export`, { format })
  }

  async importModel(
    modelFile: File,
    name: string,
    description?: string
  ): Promise<{ model_id: string; import_job_id: string }> {
    const formData = new FormData()
    formData.append('model_file', modelFile)
    formData.append('name', name)
    if (description) {
      formData.append('description', description)
    }

    return api.post(`${this.basePath}/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  }

  // Model versioning
  async getModelVersions(modelId: string): Promise<{
    versions: Array<{
      version: string
      created_at: string
      accuracy?: number
      is_active: boolean
    }>
  }> {
    return api.get(`${this.basePath}/${modelId}/versions`)
  }

  async setActiveVersion(modelId: string, version: string): Promise<{ success: boolean }> {
    return api.post(`${this.basePath}/${modelId}/versions/${version}/activate`)
  }

  async deleteVersion(modelId: string, version: string): Promise<{ success: boolean }> {
    return api.delete(`${this.basePath}/${modelId}/versions/${version}`)
  }

  // Model benchmarking
  async benchmarkModel(
    modelId: string,
    deviceType: 'cpu' | 'gpu' = 'cpu'
  ): Promise<{
    benchmark_id: string
  }> {
    return api.post(`${this.basePath}/${modelId}/benchmark`, { device: deviceType })
  }

  async getBenchmarkResults(benchmarkId: string): Promise<{
    status: 'running' | 'completed' | 'failed'
    fps: number
    latency_ms: number
    memory_usage_mb: number
    cpu_usage_percent: number
    gpu_usage_percent?: number
  }> {
    return api.get(`${this.basePath}/benchmark/${benchmarkId}`)
  }

  // Pretrained models
  async getPretrainedModels(): Promise<Array<{
    name: string
    description: string
    size_mb: number
    accuracy: number
    supported_classes: string[]
  }>> {
    return api.get(`${this.basePath}/pretrained`)
  }

  async downloadPretrainedModel(
    modelName: string,
    customName?: string
  ): Promise<{ model_id: string; download_job_id: string }> {
    return api.post(`${this.basePath}/pretrained/${modelName}/download`, {
      custom_name: customName
    })
  }
}

// Export singleton instance
export const modelApi = new ModelApiService()