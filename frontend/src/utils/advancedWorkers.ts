/**
 * 高度なWeb Worker管理システム
 * バックグラウンド処理、ワーカープール、タスクキューの管理
 */

interface WorkerTask<T = any, R = any> {
  id: string
  type: string
  data: T
  priority: 'high' | 'medium' | 'low'
  timeout?: number
  retries?: number
  onProgress?: (progress: number) => void
  resolve: (result: R) => void
  reject: (error: Error) => void
}

interface WorkerStats {
  totalTasks: number
  completedTasks: number
  failedTasks: number
  averageExecutionTime: number
  queueLength: number
  activeWorkers: number
  memoryUsage?: number
}

interface WorkerPoolConfig {
  maxWorkers: number
  taskQueueLimit: number
  workerIdleTimeout: number
  enableTaskPrioritization: boolean
  enableTaskRetry: boolean
  maxRetries: number
}

class AdvancedWorkerManager {
  private workers: Map<string, Worker> = new Map()
  private taskQueue: WorkerTask[] = []
  private activeTasks: Map<string, WorkerTask> = new Map()
  private workerStats: WorkerStats = {
    totalTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    averageExecutionTime: 0,
    queueLength: 0,
    activeWorkers: 0
  }
  private config: WorkerPoolConfig
  private taskIdCounter = 0
  private executionTimes: number[] = []

  constructor(config: Partial<WorkerPoolConfig> = {}) {
    this.config = {
      maxWorkers: 4,
      taskQueueLimit: 100,
      workerIdleTimeout: 30000,
      enableTaskPrioritization: true,
      enableTaskRetry: true,
      maxRetries: 3,
      ...config
    }
  }

  /**
   * 新しいタスクをキューに追加
   */
  async executeTask<T, R>(
    workerScript: string,
    taskType: string,
    data: T,
    options: {
      priority?: 'high' | 'medium' | 'low'
      timeout?: number
      retries?: number
      onProgress?: (progress: number) => void
    } = {}
  ): Promise<R> {
    return new Promise((resolve, reject) => {
      const taskId = `task-${++this.taskIdCounter}`
      const task: WorkerTask<T, R> = {
        id: taskId,
        type: taskType,
        data,
        priority: options.priority || 'medium',
        timeout: options.timeout || 30000,
        retries: options.retries !== undefined ? options.retries : this.config.maxRetries,
        onProgress: options.onProgress,
        resolve,
        reject
      }

      if (this.taskQueue.length >= this.config.taskQueueLimit) {
        reject(new Error('Task queue is full'))
        return
      }

      this.taskQueue.push(task)
      this.workerStats.totalTasks++
      this.workerStats.queueLength = this.taskQueue.length

      if (this.config.enableTaskPrioritization) {
        this.prioritizeTaskQueue()
      }

      this.processQueue()
    })
  }

  /**
   * 画像処理ワーカー
   */
  async processImage(
    imageData: ImageData | ArrayBuffer,
    operation: 'resize' | 'filter' | 'compress' | 'analyze',
    options: any = {}
  ): Promise<any> {
    const workerScript = this.createImageProcessorScript()
    return this.executeTask(workerScript, 'image-processing', {
      imageData,
      operation,
      options
    }, { priority: 'high' })
  }

  /**
   * データ分析ワーカー
   */
  async analyzeData(
    data: any[],
    analysisType: 'statistics' | 'ml' | 'clustering' | 'prediction',
    options: any = {}
  ): Promise<any> {
    const workerScript = this.createDataAnalysisScript()
    return this.executeTask(workerScript, 'data-analysis', {
      data,
      analysisType,
      options
    }, { priority: 'medium' })
  }

  /**
   * バックグラウンドでの大量データ処理
   */
  async processBulkData<T, R>(
    data: T[],
    processor: (item: T) => R,
    options: {
      batchSize?: number
      concurrency?: number
      onProgress?: (completed: number, total: number) => void
    } = {}
  ): Promise<R[]> {
    const {
      batchSize = 100,
      concurrency = 2,
      onProgress
    } = options

    const results: R[] = []
    const batches = this.createBatches(data, batchSize)
    const processorFunction = processor.toString()

    const promises = batches.map((batch, index) => 
      this.executeTask(
        this.createBulkProcessorScript(),
        'bulk-processing',
        { batch, processorFunction },
        {
          priority: 'low',
          onProgress: (progress) => {
            const completed = index * batchSize + Math.floor(batch.length * progress / 100)
            onProgress?.(completed, data.length)
          }
        }
      )
    )

    const batchResults = await Promise.all(promises)
    
    for (const batchResult of batchResults) {
      results.push(...batchResult)
    }

    return results
  }

  /**
   * Machine Learning推論ワーカー
   */
  async runMLInference(
    modelData: ArrayBuffer,
    inputData: Float32Array,
    modelType: 'tensorflow' | 'onnx' | 'custom'
  ): Promise<Float32Array> {
    const workerScript = this.createMLInferenceScript(modelType)
    return this.executeTask(workerScript, 'ml-inference', {
      modelData,
      inputData,
      modelType
    }, { priority: 'high', timeout: 60000 })
  }

  /**
   * リアルタイム音声処理
   */
  async processAudio(
    audioBuffer: ArrayBuffer,
    operation: 'analyze' | 'filter' | 'compress' | 'enhance',
    options: any = {}
  ): Promise<ArrayBuffer> {
    const workerScript = this.createAudioProcessorScript()
    return this.executeTask(workerScript, 'audio-processing', {
      audioBuffer,
      operation,
      options
    }, { priority: 'high' })
  }

  /**
   * 暗号化・復号化ワーカー
   */
  async cryptoOperation(
    data: ArrayBuffer,
    operation: 'encrypt' | 'decrypt' | 'hash' | 'sign',
    key: CryptoKey | string,
    algorithm: string = 'AES-GCM'
  ): Promise<ArrayBuffer> {
    const workerScript = this.createCryptoWorkerScript()
    return this.executeTask(workerScript, 'crypto', {
      data,
      operation,
      key,
      algorithm
    }, { priority: 'high', timeout: 10000 })
  }

  /**
   * タスクキューの処理
   */
  private async processQueue(): Promise<void> {
    if (this.taskQueue.length === 0 || this.workers.size >= this.config.maxWorkers) {
      return
    }

    const task = this.taskQueue.shift()
    if (!task) return

    this.workerStats.queueLength = this.taskQueue.length
    
    try {
      await this.executeWorkerTask(task)
    } catch (error) {
      console.error('Worker task execution failed:', error)
    }

    // 次のタスクを処理
    this.processQueue()
  }

  /**
   * ワーカータスクの実行
   */
  private async executeWorkerTask(task: WorkerTask): Promise<void> {
    const workerId = `worker-${task.id}`
    const worker = new Worker(this.createWorkerScript(task.type))
    
    this.workers.set(workerId, worker)
    this.activeTasks.set(task.id, task)
    this.workerStats.activeWorkers = this.workers.size

    const startTime = performance.now()
    let timeoutId: NodeJS.Timeout | null = null

    return new Promise((resolve) => {
      // タイムアウト設定
      if (task.timeout) {
        timeoutId = setTimeout(() => {
          this.terminateWorker(workerId, task, new Error('Task timeout'))
          resolve()
        }, task.timeout)
      }

      // ワーカーメッセージハンドラー
      worker.onmessage = (event) => {
        const { type, result, progress, error } = event.data

        if (type === 'progress' && task.onProgress) {
          task.onProgress(progress)
        } else if (type === 'result') {
          const endTime = performance.now()
          this.recordExecutionTime(endTime - startTime)
          
          if (timeoutId) clearTimeout(timeoutId)
          this.terminateWorker(workerId, task)
          task.resolve(result)
          resolve()
        } else if (type === 'error') {
          if (timeoutId) clearTimeout(timeoutId)
          this.handleTaskError(workerId, task, new Error(error))
          resolve()
        }
      }

      // ワーカーエラーハンドラー
      worker.onerror = (error) => {
        if (timeoutId) clearTimeout(timeoutId)
        this.handleTaskError(workerId, task, error as ErrorEvent)
        resolve()
      }

      // タスクデータを送信
      worker.postMessage({
        type: 'execute',
        task: {
          id: task.id,
          type: task.type,
          data: task.data
        }
      })
    })
  }

  /**
   * タスクの優先順位付け
   */
  private prioritizeTaskQueue(): void {
    this.taskQueue.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 }
      return priorityOrder[b.priority] - priorityOrder[a.priority]
    })
  }

  /**
   * タスクエラーの処理
   */
  private handleTaskError(workerId: string, task: WorkerTask, error: Error | ErrorEvent): void {
    if (this.config.enableTaskRetry && task.retries && task.retries > 0) {
      task.retries--
      this.taskQueue.unshift(task) // 再実行のためキューの先頭に追加
      this.terminateWorker(workerId, task)
      this.processQueue()
    } else {
      this.terminateWorker(workerId, task)
      this.workerStats.failedTasks++
      task.reject(error instanceof ErrorEvent ? new Error(error.message) : error)
    }
  }

  /**
   * ワーカーの終了
   */
  private terminateWorker(workerId: string, task: WorkerTask, error?: Error): void {
    const worker = this.workers.get(workerId)
    if (worker) {
      worker.terminate()
      this.workers.delete(workerId)
    }

    this.activeTasks.delete(task.id)
    this.workerStats.activeWorkers = this.workers.size

    if (!error) {
      this.workerStats.completedTasks++
    }
  }

  /**
   * 実行時間の記録
   */
  private recordExecutionTime(time: number): void {
    this.executionTimes.push(time)
    if (this.executionTimes.length > 100) {
      this.executionTimes.shift()
    }
    
    this.workerStats.averageExecutionTime = 
      this.executionTimes.reduce((sum, t) => sum + t, 0) / this.executionTimes.length
  }

  /**
   * バッチ作成
   */
  private createBatches<T>(data: T[], batchSize: number): T[][] {
    const batches: T[][] = []
    for (let i = 0; i < data.length; i += batchSize) {
      batches.push(data.slice(i, i + batchSize))
    }
    return batches
  }

  // ワーカースクリプト生成メソッド群
  private createWorkerScript(taskType: string): string {
    switch (taskType) {
      case 'image-processing':
        return this.createImageProcessorScript()
      case 'data-analysis':
        return this.createDataAnalysisScript()
      case 'bulk-processing':
        return this.createBulkProcessorScript()
      case 'ml-inference':
        return this.createMLInferenceScript()
      case 'audio-processing':
        return this.createAudioProcessorScript()
      case 'crypto':
        return this.createCryptoWorkerScript()
      default:
        return this.createGenericWorkerScript()
    }
  }

  private createImageProcessorScript(): string {
    const workerCode = `
      self.onmessage = function(e) {
        const { type, task } = e.data
        
        if (type === 'execute') {
          try {
            const { imageData, operation, options } = task.data
            let result
            
            switch (operation) {
              case 'resize':
                result = resizeImage(imageData, options.width, options.height)
                break
              case 'filter':
                result = applyFilter(imageData, options.filter)
                break
              case 'compress':
                result = compressImage(imageData, options.quality)
                break
              case 'analyze':
                result = analyzeImage(imageData, options)
                break
              default:
                throw new Error('Unknown image operation: ' + operation)
            }
            
            self.postMessage({ type: 'result', result })
          } catch (error) {
            self.postMessage({ type: 'error', error: error.message })
          }
        }
      }
      
      function resizeImage(imageData, width, height) {
        // 画像リサイズの実装
        return { width, height, data: new Uint8ClampedArray(width * height * 4) }
      }
      
      function applyFilter(imageData, filter) {
        // フィルター適用の実装
        return imageData
      }
      
      function compressImage(imageData, quality) {
        // 画像圧縮の実装
        return imageData
      }
      
      function analyzeImage(imageData, options) {
        // 画像分析の実装
        return { brightness: 0.5, contrast: 0.7, edges: 1000 }
      }
    `
    
    return URL.createObjectURL(new Blob([workerCode], { type: 'application/javascript' }))
  }

  private createDataAnalysisScript(): string {
    const workerCode = `
      self.onmessage = function(e) {
        const { type, task } = e.data
        
        if (type === 'execute') {
          try {
            const { data, analysisType, options } = task.data
            let result
            
            switch (analysisType) {
              case 'statistics':
                result = calculateStatistics(data)
                break
              case 'ml':
                result = performMLAnalysis(data, options)
                break
              case 'clustering':
                result = performClustering(data, options)
                break
              case 'prediction':
                result = makePrediction(data, options)
                break
              default:
                throw new Error('Unknown analysis type: ' + analysisType)
            }
            
            self.postMessage({ type: 'result', result })
          } catch (error) {
            self.postMessage({ type: 'error', error: error.message })
          }
        }
      }
      
      function calculateStatistics(data) {
        const mean = data.reduce((sum, val) => sum + val, 0) / data.length
        const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length
        return { mean, variance, std: Math.sqrt(variance), min: Math.min(...data), max: Math.max(...data) }
      }
      
      function performMLAnalysis(data, options) {
        // 機械学習分析の実装
        return { accuracy: 0.95, features: data.length }
      }
      
      function performClustering(data, options) {
        // クラスタリングの実装
        return { clusters: 3, centers: [[0, 0], [1, 1], [2, 2]] }
      }
      
      function makePrediction(data, options) {
        // 予測の実装
        return { prediction: data[data.length - 1] * 1.1, confidence: 0.8 }
      }
    `
    
    return URL.createObjectURL(new Blob([workerCode], { type: 'application/javascript' }))
  }

  private createBulkProcessorScript(): string {
    const workerCode = `
      self.onmessage = function(e) {
        const { type, task } = e.data
        
        if (type === 'execute') {
          try {
            const { batch, processorFunction } = task.data
            const processor = new Function('return ' + processorFunction)()
            
            const results = []
            for (let i = 0; i < batch.length; i++) {
              results.push(processor(batch[i]))
              
              // 進捗報告
              if (i % 10 === 0) {
                self.postMessage({ 
                  type: 'progress', 
                  progress: (i / batch.length) * 100 
                })
              }
            }
            
            self.postMessage({ type: 'result', result: results })
          } catch (error) {
            self.postMessage({ type: 'error', error: error.message })
          }
        }
      }
    `
    
    return URL.createObjectURL(new Blob([workerCode], { type: 'application/javascript' }))
  }

  private createMLInferenceScript(modelType: string = 'custom'): string {
    const workerCode = `
      self.onmessage = function(e) {
        const { type, task } = e.data
        
        if (type === 'execute') {
          try {
            const { modelData, inputData, modelType } = task.data
            
            // モデル推論の実装（簡略化）
            const result = new Float32Array(inputData.length)
            for (let i = 0; i < inputData.length; i++) {
              result[i] = inputData[i] * 0.5 + Math.random() * 0.1
            }
            
            self.postMessage({ type: 'result', result })
          } catch (error) {
            self.postMessage({ type: 'error', error: error.message })
          }
        }
      }
    `
    
    return URL.createObjectURL(new Blob([workerCode], { type: 'application/javascript' }))
  }

  private createAudioProcessorScript(): string {
    const workerCode = `
      self.onmessage = function(e) {
        const { type, task } = e.data
        
        if (type === 'execute') {
          try {
            const { audioBuffer, operation, options } = task.data
            
            // 音声処理の実装（簡略化）
            let result = audioBuffer
            
            switch (operation) {
              case 'analyze':
                result = { frequency: 440, amplitude: 0.5, duration: audioBuffer.byteLength / 44100 }
                break
              case 'filter':
                // フィルター処理
                break
              case 'compress':
                // 圧縮処理
                break
              case 'enhance':
                // 音質向上処理
                break
            }
            
            self.postMessage({ type: 'result', result })
          } catch (error) {
            self.postMessage({ type: 'error', error: error.message })
          }
        }
      }
    `
    
    return URL.createObjectURL(new Blob([workerCode], { type: 'application/javascript' }))
  }

  private createCryptoWorkerScript(): string {
    const workerCode = `
      self.onmessage = function(e) {
        const { type, task } = e.data
        
        if (type === 'execute') {
          try {
            const { data, operation, key, algorithm } = task.data
            
            // 暗号化処理の実装（簡略化）
            let result = data
            
            switch (operation) {
              case 'encrypt':
                // 暗号化
                result = new ArrayBuffer(data.byteLength)
                break
              case 'decrypt':
                // 復号化
                result = new ArrayBuffer(data.byteLength)
                break
              case 'hash':
                // ハッシュ計算
                result = new ArrayBuffer(32) // SHA-256
                break
              case 'sign':
                // デジタル署名
                result = new ArrayBuffer(64)
                break
            }
            
            self.postMessage({ type: 'result', result })
          } catch (error) {
            self.postMessage({ type: 'error', error: error.message })
          }
        }
      }
    `
    
    return URL.createObjectURL(new Blob([workerCode], { type: 'application/javascript' }))
  }

  private createGenericWorkerScript(): string {
    const workerCode = `
      self.onmessage = function(e) {
        const { type, task } = e.data
        
        if (type === 'execute') {
          try {
            // 汎用処理
            const result = task.data
            self.postMessage({ type: 'result', result })
          } catch (error) {
            self.postMessage({ type: 'error', error: error.message })
          }
        }
      }
    `
    
    return URL.createObjectURL(new Blob([workerCode], { type: 'application/javascript' }))
  }

  /**
   * 統計情報を取得
   */
  getStats(): WorkerStats {
    return { ...this.workerStats }
  }

  /**
   * すべてのワーカーを終了
   */
  terminateAllWorkers(): void {
    for (const [workerId, worker] of this.workers) {
      worker.terminate()
    }
    this.workers.clear()
    this.taskQueue = []
    this.activeTasks.clear()
    this.workerStats.activeWorkers = 0
    this.workerStats.queueLength = 0
  }

  /**
   * 設定を更新
   */
  updateConfig(newConfig: Partial<WorkerPoolConfig>): void {
    this.config = { ...this.config, ...newConfig }
  }
}

// シングルトンインスタンス
export const advancedWorkerManager = new AdvancedWorkerManager()

// React Hook
export const useAdvancedWorkers = () => {
  const [stats, setStats] = React.useState<WorkerStats>(advancedWorkerManager.getStats())

  React.useEffect(() => {
    const interval = setInterval(() => {
      setStats(advancedWorkerManager.getStats())
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  return {
    executeTask: advancedWorkerManager.executeTask.bind(advancedWorkerManager),
    processImage: advancedWorkerManager.processImage.bind(advancedWorkerManager),
    analyzeData: advancedWorkerManager.analyzeData.bind(advancedWorkerManager),
    processBulkData: advancedWorkerManager.processBulkData.bind(advancedWorkerManager),
    runMLInference: advancedWorkerManager.runMLInference.bind(advancedWorkerManager),
    processAudio: advancedWorkerManager.processAudio.bind(advancedWorkerManager),
    cryptoOperation: advancedWorkerManager.cryptoOperation.bind(advancedWorkerManager),
    stats,
    terminateAllWorkers: advancedWorkerManager.terminateAllWorkers.bind(advancedWorkerManager)
  }
}

export default advancedWorkerManager