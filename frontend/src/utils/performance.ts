/**
 * パフォーマンス最適化ユーティリティ
 */

import React, { ComponentType, lazy, LazyExoticComponent } from 'react'
import { throttle, debounce } from 'lodash-es'

// =============================================================================
// Code Splitting Utilities
// =============================================================================

/**
 * 遅延読み込み可能なコンポーネントを作成
 */
export const createLazyComponent = <T extends ComponentType<any>>(
  importFunction: () => Promise<{ default: T }>
): LazyExoticComponent<T> => {
  return lazy(importFunction)
}

/**
 * ページコンポーネントの遅延読み込み
 */
export const lazyPageComponents = {
  Dashboard: createLazyComponent(() => import('../pages/Dashboard')),
  DroneManagement: createLazyComponent(() => import('../pages/DroneManagement')),
  DatasetManagement: createLazyComponent(() => import('../pages/DatasetManagement')),
  ModelManagement: createLazyComponent(() => import('../pages/ModelManagement')),
  SystemMonitoring: createLazyComponent(() => import('../pages/SystemMonitoring')),
  TrackingControl: createLazyComponent(() => import('../pages/TrackingControl')),
  Settings: createLazyComponent(() => import('../pages/Settings')),
}

// =============================================================================
// Memoization Utilities
// =============================================================================

/**
 * プロパティの浅い比較関数
 */
export const shallowEqual = (prev: Record<string, any>, next: Record<string, any>): boolean => {
  const prevKeys = Object.keys(prev)
  const nextKeys = Object.keys(next)

  if (prevKeys.length !== nextKeys.length) {
    return false
  }

  for (let key of prevKeys) {
    if (prev[key] !== next[key]) {
      return false
    }
  }

  return true
}

/**
 * カスタムメモ化関数作成
 */
export const createMemoizedSelector = <T, R>(
  selector: (state: T) => R,
  equalityFn: (a: R, b: R) => boolean = Object.is
) => {
  let lastArgs: T | undefined
  let lastResult: R

  return (state: T): R => {
    if (lastArgs === undefined || !equalityFn(selector(state), lastResult)) {
      lastArgs = state
      lastResult = selector(state)
    }
    return lastResult
  }
}

// =============================================================================
// Event Optimization
// =============================================================================

/**
 * スロットルされたイベントハンドラーを作成
 */
export const createThrottledHandler = <T extends (...args: any[]) => any>(
  handler: T,
  delay: number = 100
): T => {
  return throttle(handler, delay, { leading: true, trailing: false }) as T
}

/**
 * デバウンスされたイベントハンドラーを作成
 */
export const createDebouncedHandler = <T extends (...args: any[]) => any>(
  handler: T,
  delay: number = 300
): T => {
  return debounce(handler, delay) as T
}

/**
 * リサイズイベントの最適化
 */
export const createOptimizedResizeHandler = (
  callback: () => void,
  delay: number = 250
) => {
  const throttledCallback = throttle(callback, delay)
  
  let rafId: number | null = null
  
  return () => {
    if (rafId) {
      cancelAnimationFrame(rafId)
    }
    
    rafId = requestAnimationFrame(() => {
      throttledCallback()
      rafId = null
    })
  }
}

// =============================================================================
// Virtual Scrolling Utilities
// =============================================================================

/**
 * 仮想スクロール計算
 */
export interface VirtualScrollConfig {
  itemHeight: number
  containerHeight: number
  itemCount: number
  scrollTop: number
  overscan?: number
}

export interface VirtualScrollResult {
  startIndex: number
  endIndex: number
  visibleItems: number
  offsetY: number
  totalHeight: number
}

export const calculateVirtualScroll = (config: VirtualScrollConfig): VirtualScrollResult => {
  const { itemHeight, containerHeight, itemCount, scrollTop, overscan = 5 } = config
  
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
  const visibleItems = Math.ceil(containerHeight / itemHeight)
  const endIndex = Math.min(itemCount - 1, startIndex + visibleItems + overscan * 2)
  
  const offsetY = startIndex * itemHeight
  const totalHeight = itemCount * itemHeight
  
  return {
    startIndex,
    endIndex,
    visibleItems,
    offsetY,
    totalHeight
  }
}

// =============================================================================
// Image Optimization
// =============================================================================

/**
 * 画像の遅延読み込み
 */
export const createLazyImageLoader = () => {
  const imageCache = new Map<string, HTMLImageElement>()
  
  const loadImage = (src: string): Promise<HTMLImageElement> => {
    if (imageCache.has(src)) {
      return Promise.resolve(imageCache.get(src)!)
    }
    
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        imageCache.set(src, img)
        resolve(img)
      }
      img.onerror = reject
      img.src = src
    })
  }
  
  const preloadImages = (urls: string[]): Promise<HTMLImageElement[]> => {
    return Promise.all(urls.map(loadImage))
  }
  
  return { loadImage, preloadImages, cache: imageCache }
}

/**
 * WebPサポート検出
 */
export const supportsWebP = (): boolean => {
  const canvas = document.createElement('canvas')
  canvas.width = 1
  canvas.height = 1
  return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0
}

/**
 * 最適な画像フォーマットを選択
 */
export const getOptimalImageFormat = (url: string): string => {
  if (!url) return url
  
  const hasWebPSupport = supportsWebP()
  
  if (hasWebPSupport && !url.includes('.webp')) {
    // WebP対応の場合、URLを.webpに変換
    return url.replace(/\.(jpg|jpeg|png)$/i, '.webp')
  }
  
  return url
}

// =============================================================================
// Bundle Analysis
// =============================================================================

/**
 * 動的インポートのプリロード
 */
export const preloadRoute = (routeName: keyof typeof lazyPageComponents): void => {
  const component = lazyPageComponents[routeName]
  if (component) {
    // プリロードを実行（バックグラウンドでロード）
    component._payload?._result || import(`../pages/${routeName}`)
  }
}

/**
 * 重要なルートのプリロード
 */
export const preloadCriticalRoutes = (): void => {
  const criticalRoutes: (keyof typeof lazyPageComponents)[] = [
    'Dashboard',
    'DroneManagement'
  ]
  
  // 少し遅延してからプリロード（初期読み込み完了後）
  setTimeout(() => {
    criticalRoutes.forEach(preloadRoute)
  }, 2000)
}

// =============================================================================
// Memory Management
// =============================================================================

/**
 * メモリ使用量の監視
 */
export const getMemoryUsage = (): MemoryInfo | null => {
  if ('memory' in performance) {
    return (performance as any).memory
  }
  return null
}

/**
 * ガベージコレクション強制実行（デバッグ用）
 */
export const forceGarbageCollection = (): void => {
  if ('gc' in window) {
    (window as any).gc()
  }
}

/**
 * WeakMapベースのキャッシュ
 */
export class WeakCache<K extends object, V> {
  private cache = new WeakMap<K, V>()
  
  get(key: K): V | undefined {
    return this.cache.get(key)
  }
  
  set(key: K, value: V): void {
    this.cache.set(key, value)
  }
  
  has(key: K): boolean {
    return this.cache.has(key)
  }
  
  delete(key: K): boolean {
    return this.cache.delete(key)
  }
}

// =============================================================================
// Performance Monitoring
// =============================================================================

/**
 * パフォーマンスメトリクス
 */
export interface PerformanceMetrics {
  renderTime: number
  componentCount: number
  memoryUsage?: MemoryInfo
  timestamp: number
}

/**
 * レンダリング時間測定
 */
export const measureRenderTime = <T>(
  name: string,
  renderFunction: () => T
): { result: T; duration: number } => {
  const start = performance.now()
  const result = renderFunction()
  const duration = performance.now() - start
  
  // Performance API でマーク
  performance.mark(`${name}-start`)
  performance.mark(`${name}-end`)
  performance.measure(name, `${name}-start`, `${name}-end`)
  
  return { result, duration }
}

/**
 * フレームレート監視
 */
export class FrameRateMonitor {
  private frames: number[] = []
  private lastTime = performance.now()
  private rafId: number | null = null
  
  start(): void {
    const update = (currentTime: number) => {
      const delta = currentTime - this.lastTime
      this.frames.push(1000 / delta)
      
      // 直近60フレームのみ保持
      if (this.frames.length > 60) {
        this.frames.shift()
      }
      
      this.lastTime = currentTime
      this.rafId = requestAnimationFrame(update)
    }
    
    this.rafId = requestAnimationFrame(update)
  }
  
  stop(): void {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId)
      this.rafId = null
    }
  }
  
  getAverageFPS(): number {
    if (this.frames.length === 0) return 0
    
    const sum = this.frames.reduce((a, b) => a + b, 0)
    return sum / this.frames.length
  }
  
  getMinFPS(): number {
    return Math.min(...this.frames)
  }
  
  getMaxFPS(): number {
    return Math.max(...this.frames)
  }
}

// =============================================================================
// Worker Utilities
// =============================================================================

/**
 * Web Worker での重い処理の実行
 */
export const runInWorker = <T, R>(
  workerScript: string,
  data: T
): Promise<R> => {
  return new Promise((resolve, reject) => {
    const worker = new Worker(workerScript)
    
    worker.onmessage = (event) => {
      worker.terminate()
      resolve(event.data)
    }
    
    worker.onerror = (error) => {
      worker.terminate()
      reject(error)
    }
    
    worker.postMessage(data)
  })
}

/**
 * バックグラウンドでのデータ処理
 */
export const processDataInBackground = <T, R>(
  processor: (data: T) => R,
  data: T,
  batchSize: number = 100
): Promise<R[]> => {
  return new Promise((resolve) => {
    const results: R[] = []
    const dataArray = Array.isArray(data) ? data : [data]
    let index = 0
    
    const processBatch = () => {
      const endIndex = Math.min(index + batchSize, dataArray.length)
      
      for (let i = index; i < endIndex; i++) {
        results.push(processor(dataArray[i]))
      }
      
      index = endIndex
      
      if (index < dataArray.length) {
        requestIdleCallback(processBatch)
      } else {
        resolve(results)
      }
    }
    
    processBatch()
  })
}

// =============================================================================
// Export Default Performance Manager
// =============================================================================

export const PerformanceManager = {
  // Lazy loading
  createLazyComponent,
  lazyPageComponents,
  preloadRoute,
  preloadCriticalRoutes,
  
  // Memoization
  shallowEqual,
  createMemoizedSelector,
  
  // Event optimization
  createThrottledHandler,
  createDebouncedHandler,
  createOptimizedResizeHandler,
  
  // Virtual scrolling
  calculateVirtualScroll,
  
  // Image optimization
  createLazyImageLoader,
  supportsWebP,
  getOptimalImageFormat,
  
  // Memory management
  getMemoryUsage,
  forceGarbageCollection,
  WeakCache,
  
  // Performance monitoring
  measureRenderTime,
  FrameRateMonitor,
  
  // Worker utilities
  runInWorker,
  processDataInBackground,
}