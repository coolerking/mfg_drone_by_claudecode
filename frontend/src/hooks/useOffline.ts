import { useState, useEffect, useCallback } from 'react'
import { useNotification } from './useNotification'

export interface OfflineData {
  id: string
  type: 'create' | 'update' | 'delete'
  endpoint: string
  data: any
  timestamp: number
  retries: number
}

export interface CachedData {
  [key: string]: {
    data: any
    timestamp: number
    expiry: number
  }
}

class OfflineStorageService {
  private static instance: OfflineStorageService
  private readonly OFFLINE_QUEUE_KEY = 'offline_queue'
  private readonly CACHED_DATA_KEY = 'cached_data'
  private readonly MAX_CACHE_SIZE = 50 // MB
  private readonly DEFAULT_CACHE_TTL = 5 * 60 * 1000 // 5 minutes

  static getInstance(): OfflineStorageService {
    if (!OfflineStorageService.instance) {
      OfflineStorageService.instance = new OfflineStorageService()
    }
    return OfflineStorageService.instance
  }

  // Offline queue management
  addToOfflineQueue(operation: Omit<OfflineData, 'id' | 'timestamp' | 'retries'>): string {
    const id = `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const item: OfflineData = {
      id,
      timestamp: Date.now(),
      retries: 0,
      ...operation,
    }

    try {
      const queue = this.getOfflineQueue()
      queue.push(item)
      localStorage.setItem(this.OFFLINE_QUEUE_KEY, JSON.stringify(queue))
      return id
    } catch (error) {
      console.warn('Failed to add to offline queue:', error)
      return id
    }
  }

  getOfflineQueue(): OfflineData[] {
    try {
      const queue = localStorage.getItem(this.OFFLINE_QUEUE_KEY)
      return queue ? JSON.parse(queue) : []
    } catch {
      return []
    }
  }

  removeFromOfflineQueue(id: string): void {
    try {
      const queue = this.getOfflineQueue()
      const filtered = queue.filter(item => item.id !== id)
      localStorage.setItem(this.OFFLINE_QUEUE_KEY, JSON.stringify(filtered))
    } catch (error) {
      console.warn('Failed to remove from offline queue:', error)
    }
  }

  updateQueueItemRetries(id: string): void {
    try {
      const queue = this.getOfflineQueue()
      const updated = queue.map(item => 
        item.id === id ? { ...item, retries: item.retries + 1 } : item
      )
      localStorage.setItem(this.OFFLINE_QUEUE_KEY, JSON.stringify(updated))
    } catch (error) {
      console.warn('Failed to update queue item:', error)
    }
  }

  clearOfflineQueue(): void {
    try {
      localStorage.removeItem(this.OFFLINE_QUEUE_KEY)
    } catch (error) {
      console.warn('Failed to clear offline queue:', error)
    }
  }

  // Cache management
  cacheData(key: string, data: any, ttl: number = this.DEFAULT_CACHE_TTL): void {
    try {
      const cachedData = this.getCachedData()
      const expiry = Date.now() + ttl

      cachedData[key] = {
        data,
        timestamp: Date.now(),
        expiry,
      }

      // Check cache size and clean if necessary
      this.cleanCache(cachedData)
      localStorage.setItem(this.CACHED_DATA_KEY, JSON.stringify(cachedData))
    } catch (error) {
      console.warn('Failed to cache data:', error)
    }
  }

  getCachedItem(key: string): any | null {
    try {
      const cachedData = this.getCachedData()
      const item = cachedData[key]

      if (!item) return null
      if (Date.now() > item.expiry) {
        delete cachedData[key]
        localStorage.setItem(this.CACHED_DATA_KEY, JSON.stringify(cachedData))
        return null
      }

      return item.data
    } catch {
      return null
    }
  }

  private getCachedData(): CachedData {
    try {
      const cached = localStorage.getItem(this.CACHED_DATA_KEY)
      return cached ? JSON.parse(cached) : {}
    } catch {
      return {}
    }
  }

  private cleanCache(cachedData: CachedData): void {
    const now = Date.now()
    const entries = Object.entries(cachedData)

    // Remove expired entries
    const nonExpired = entries.filter(([, item]) => now < item.expiry)

    // If still too many entries, remove oldest ones
    const maxEntries = 100
    if (nonExpired.length > maxEntries) {
      nonExpired.sort(([, a], [, b]) => b.timestamp - a.timestamp)
      nonExpired.splice(maxEntries)
    }

    // Rebuild cache object
    Object.keys(cachedData).forEach(key => delete cachedData[key])
    nonExpired.forEach(([key, item]) => {
      cachedData[key] = item
    })
  }

  // Cache size estimation (rough)
  getCacheSize(): number {
    try {
      const cachedData = localStorage.getItem(this.CACHED_DATA_KEY)
      return cachedData ? new Blob([cachedData]).size / 1024 / 1024 : 0 // MB
    } catch {
      return 0
    }
  }

  clearCache(): void {
    try {
      localStorage.removeItem(this.CACHED_DATA_KEY)
    } catch (error) {
      console.warn('Failed to clear cache:', error)
    }
  }
}

export function useOffline() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [syncInProgress, setSyncInProgress] = useState(false)
  const [offlineQueue, setOfflineQueue] = useState<OfflineData[]>([])
  const { showSuccess, showError, showInfo } = useNotification()
  
  const offlineService = OfflineStorageService.getInstance()

  // Network status detection
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      showSuccess('インターネット接続が復旧しました')
      // Auto-sync when back online
      syncOfflineData()
    }

    const handleOffline = () => {
      setIsOnline(false)
      showInfo('オフラインモードになりました。データは一時保存されます。')
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Load offline queue on mount
  useEffect(() => {
    const queue = offlineService.getOfflineQueue()
    setOfflineQueue(queue)
  }, [])

  // Add operation to offline queue
  const addOfflineOperation = useCallback((operation: Omit<OfflineData, 'id' | 'timestamp' | 'retries'>) => {
    const id = offlineService.addToOfflineQueue(operation)
    const queue = offlineService.getOfflineQueue()
    setOfflineQueue(queue)
    return id
  }, [])

  // Sync offline data when back online
  const syncOfflineData = useCallback(async () => {
    if (!isOnline || syncInProgress) return

    setSyncInProgress(true)
    const queue = offlineService.getOfflineQueue()
    
    if (queue.length === 0) {
      setSyncInProgress(false)
      return
    }

    showInfo(`${queue.length}件のオフラインデータを同期中...`)

    let successCount = 0
    let failureCount = 0

    for (const item of queue) {
      try {
        // Simulate API call - in real app, would use actual API client
        const response = await fetch(item.endpoint, {
          method: item.type === 'create' ? 'POST' : 
                 item.type === 'update' ? 'PUT' : 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
          body: item.data ? JSON.stringify(item.data) : undefined,
        })

        if (response.ok) {
          offlineService.removeFromOfflineQueue(item.id)
          successCount++
        } else {
          throw new Error(`HTTP ${response.status}`)
        }
      } catch (error) {
        console.warn(`Failed to sync offline item ${item.id}:`, error)
        
        // Retry logic
        if (item.retries < 3) {
          offlineService.updateQueueItemRetries(item.id)
        } else {
          // Remove after max retries
          offlineService.removeFromOfflineQueue(item.id)
          failureCount++
        }
      }
    }

    // Update local queue state
    const updatedQueue = offlineService.getOfflineQueue()
    setOfflineQueue(updatedQueue)

    // Show sync results
    if (successCount > 0) {
      showSuccess(`${successCount}件のデータを同期しました`)
    }
    if (failureCount > 0) {
      showError(`${failureCount}件のデータの同期に失敗しました`)
    }

    setSyncInProgress(false)
  }, [isOnline, syncInProgress, showSuccess, showError, showInfo])

  // Cache management functions
  const cacheData = useCallback((key: string, data: any, ttl?: number) => {
    offlineService.cacheData(key, data, ttl)
  }, [])

  const getCachedData = useCallback((key: string) => {
    return offlineService.getCachedItem(key)
  }, [])

  const clearCache = useCallback(() => {
    offlineService.clearCache()
    showSuccess('キャッシュをクリアしました')
  }, [showSuccess])

  const clearOfflineQueue = useCallback(() => {
    offlineService.clearOfflineQueue()
    setOfflineQueue([])
    showSuccess('オフラインキューをクリアしました')
  }, [showSuccess])

  // Get cache statistics
  const getCacheStats = useCallback(() => {
    return {
      size: offlineService.getCacheSize(),
      queueLength: offlineQueue.length,
    }
  }, [offlineQueue.length])

  return {
    // Status
    isOnline,
    isOffline: !isOnline,
    syncInProgress,
    offlineQueue,
    
    // Operations
    addOfflineOperation,
    syncOfflineData,
    
    // Cache management
    cacheData,
    getCachedData,
    clearCache,
    clearOfflineQueue,
    getCacheStats,
  }
}