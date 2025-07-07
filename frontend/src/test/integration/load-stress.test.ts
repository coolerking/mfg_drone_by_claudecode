/**
 * 負荷・ストレステスト統合テストスイート
 * システムの限界とパフォーマンス特性を検証
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'
import { rest } from 'msw'
import { apiSlice } from '../../store/api/apiSlice'
import { authSlice } from '../../store/slices/authSlice'
import { droneSlice } from '../../store/slices/droneSlice'
import { dashboardSlice } from '../../store/slices/dashboardSlice'

// =============================================================================
// パフォーマンス測定ユーティリティ
// =============================================================================

interface PerformanceMetrics {
  averageResponseTime: number
  minResponseTime: number
  maxResponseTime: number
  throughput: number
  errorRate: number
  memoryUsage: number
  cpuUsage: number
}

class PerformanceTester {
  private responseTimes: number[] = []
  private errors: number = 0
  private totalRequests: number = 0
  private startTime: number = 0
  private endTime: number = 0

  startTest(): void {
    this.responseTimes = []
    this.errors = 0
    this.totalRequests = 0
    this.startTime = performance.now()
  }

  recordRequest(responseTime: number, isError: boolean = false): void {
    this.responseTimes.push(responseTime)
    this.totalRequests++
    if (isError) {
      this.errors++
    }
  }

  endTest(): PerformanceMetrics {
    this.endTime = performance.now()
    const testDuration = (this.endTime - this.startTime) / 1000 // seconds

    return {
      averageResponseTime: this.responseTimes.reduce((a, b) => a + b, 0) / this.responseTimes.length,
      minResponseTime: Math.min(...this.responseTimes),
      maxResponseTime: Math.max(...this.responseTimes),
      throughput: this.totalRequests / testDuration,
      errorRate: (this.errors / this.totalRequests) * 100,
      memoryUsage: (performance as any).memory?.usedJSHeapSize || 0,
      cpuUsage: 0 // ブラウザでは正確なCPU使用率は取得できない
    }
  }
}

// =============================================================================
// MSWサーバーセットアップ（負荷テスト用）
// =============================================================================

let responseDelay = 0
let failureRate = 0

const createDelayedResponse = (data: any, delay: number = responseDelay) => {
  return new Promise(resolve => {
    setTimeout(() => {
      if (Math.random() < failureRate) {
        resolve([500, { error: 'Simulated server error' }])
      } else {
        resolve([200, data])
      }
    }, delay)
  })
}

const server = setupServer(
  // 大量データレスポンス用エンドポイント
  rest.get('/api/drones/bulk', async (req, res, ctx) => {
    const count = parseInt(req.url.searchParams.get('count') || '100')
    const drones = Array.from({ length: count }, (_, i) => ({
      id: `drone-${i}`,
      name: `Test Drone ${i}`,
      model: `Model-${i % 5}`,
      status: i % 3 === 0 ? 'connected' : i % 3 === 1 ? 'flying' : 'disconnected',
      battery: Math.floor(Math.random() * 100),
      position: {
        x: Math.random() * 1000,
        y: Math.random() * 1000,
        z: Math.random() * 100
      }
    }))

    const [status, data] = await createDelayedResponse(drones) as [number, any]
    return res(ctx.status(status), ctx.json(data))
  }),

  // 大量メトリクスデータ
  rest.get('/api/metrics/historical', async (req, res, ctx) => {
    const days = parseInt(req.url.searchParams.get('days') || '30')
    const points = days * 24 * 60 // 1分間隔のデータポイント
    
    const metrics = Array.from({ length: points }, (_, i) => {
      const timestamp = new Date(Date.now() - (points - i) * 60000).toISOString()
      return {
        timestamp,
        cpu_usage: 20 + Math.random() * 60 + Math.sin(i / 100) * 20,
        memory_usage: 30 + Math.random() * 40 + Math.sin(i / 200) * 15,
        disk_usage: 15 + Math.random() * 10 + i * 0.001,
        network_in: Math.random() * 100,
        network_out: Math.random() * 80
      }
    })

    const [status, data] = await createDelayedResponse(metrics) as [number, any]
    return res(ctx.status(status), ctx.json(data))
  }),

  // 並行リクエスト用エンドポイント
  rest.get('/api/concurrent-test/:id', async (req, res, ctx) => {
    const id = req.params.id
    const data = {
      id,
      timestamp: new Date().toISOString(),
      value: Math.random() * 1000
    }

    const [status, response] = await createDelayedResponse(data) as [number, any]
    return res(ctx.status(status), ctx.json(response))
  }),

  // メモリ負荷テスト用エンドポイント
  rest.get('/api/memory-stress', async (req, res, ctx) => {
    const size = parseInt(req.url.searchParams.get('size') || '1000')
    const largeData = {
      data: Array.from({ length: size }, (_, i) => ({
        id: i,
        content: 'A'.repeat(1000), // 1KB per item
        nested: {
          level1: {
            level2: {
              level3: Array.from({ length: 100 }, (_, j) => `item-${i}-${j}`)
            }
          }
        }
      }))
    }

    const [status, response] = await createDelayedResponse(largeData) as [number, any]
    return res(ctx.status(status), ctx.json(response))
  })
)

// =============================================================================
// テスト用ストア作成
// =============================================================================

const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      api: apiSlice.reducer,
      auth: authSlice.reducer,
      drone: droneSlice.reducer,
      dashboard: dashboardSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: false // 大量データテスト用
      }).concat(apiSlice.middleware),
    preloadedState: initialState,
  })
}

// =============================================================================
// 負荷・ストレステスト
// =============================================================================

describe('負荷・ストレステスト統合テスト', () => {
  let performanceTester: PerformanceTester

  beforeEach(() => {
    server.listen()
    performanceTester = new PerformanceTester()
    responseDelay = 0
    failureRate = 0
    
    // メモリ使用量をリセット
    if (global.gc) {
      global.gc()
    }
  })

  afterEach(() => {
    server.resetHandlers()
    vi.clearAllMocks()
  })

  afterAll(() => {
    server.close()
  })

  describe('負荷テスト', () => {
    it('大量ドローンデータの取得パフォーマンス', async () => {
      const store = createTestStore()
      const droneCount = 1000

      performanceTester.startTest()

      const startTime = performance.now()
      const action = store.dispatch(
        apiSlice.endpoints.getBulkDrones.initiate({ count: droneCount })
      )

      const result = await action
      const responseTime = performance.now() - startTime

      performanceTester.recordRequest(responseTime, result.error !== undefined)

      const metrics = performanceTester.endTest()

      expect(result.data).toHaveLength(droneCount)
      expect(metrics.averageResponseTime).toBeLessThan(5000) // 5秒以内
      expect(metrics.errorRate).toBe(0)

      console.log('大量ドローンデータ取得メトリクス:', metrics)
    })

    it('大量履歴メトリクスデータの処理パフォーマンス', async () => {
      const store = createTestStore()
      const days = 90 // 3ヶ月分のデータ

      performanceTester.startTest()

      const startTime = performance.now()
      const action = store.dispatch(
        apiSlice.endpoints.getHistoricalMetrics.initiate({ days })
      )

      const result = await action
      const responseTime = performance.now() - startTime

      performanceTester.recordRequest(responseTime, result.error !== undefined)

      const metrics = performanceTester.endTest()

      expect(result.data).toHaveLength(days * 24 * 60)
      expect(metrics.averageResponseTime).toBeLessThan(10000) // 10秒以内
      expect(metrics.errorRate).toBe(0)

      console.log('大量履歴データ取得メトリクス:', metrics)
    })

    it('並行リクエストの処理パフォーマンス', async () => {
      const store = createTestStore()
      const concurrentRequests = 50

      performanceTester.startTest()

      const promises = Array.from({ length: concurrentRequests }, async (_, i) => {
        const startTime = performance.now()
        
        try {
          const action = store.dispatch(
            apiSlice.endpoints.getConcurrentTest.initiate(i.toString())
          )
          
          const result = await action
          const responseTime = performance.now() - startTime
          
          performanceTester.recordRequest(responseTime, result.error !== undefined)
          
          return result
        } catch (error) {
          const responseTime = performance.now() - startTime
          performanceTester.recordRequest(responseTime, true)
          throw error
        }
      })

      const results = await Promise.all(promises)
      const metrics = performanceTester.endTest()

      expect(results).toHaveLength(concurrentRequests)
      expect(metrics.averageResponseTime).toBeLessThan(3000) // 3秒以内
      expect(metrics.throughput).toBeGreaterThan(10) // 10 req/sec以上
      expect(metrics.errorRate).toBeLessThan(5) // 5%未満のエラー率

      console.log('並行リクエスト処理メトリクス:', metrics)
    })

    it('段階的負荷増加テスト', async () => {
      const store = createTestStore()
      const loadLevels = [10, 25, 50, 100]
      const results: PerformanceMetrics[] = []

      for (const load of loadLevels) {
        performanceTester.startTest()

        const promises = Array.from({ length: load }, async (_, i) => {
          const startTime = performance.now()
          
          const action = store.dispatch(
            apiSlice.endpoints.getConcurrentTest.initiate(`load-${load}-${i}`)
          )
          
          const result = await action
          const responseTime = performance.now() - startTime
          
          performanceTester.recordRequest(responseTime, result.error !== undefined)
          
          return result
        })

        await Promise.all(promises)
        const metrics = performanceTester.endTest()
        results.push(metrics)

        console.log(`負荷レベル ${load}:`, metrics)

        // 負荷が増加してもパフォーマンスが著しく劣化しないことを確認
        expect(metrics.errorRate).toBeLessThan(10)
        expect(metrics.averageResponseTime).toBeLessThan(5000)
      }

      // パフォーマンス劣化の傾向を分析
      const responseTimes = results.map(r => r.averageResponseTime)
      const throughputs = results.map(r => r.throughput)

      console.log('応答時間の推移:', responseTimes)
      console.log('スループットの推移:', throughputs)
    })
  })

  describe('ストレステスト', () => {
    it('高レスポンス時間での動作確認', async () => {
      responseDelay = 2000 // 2秒の遅延
      const store = createTestStore()

      performanceTester.startTest()

      const startTime = performance.now()
      const action = store.dispatch(
        apiSlice.endpoints.getConcurrentTest.initiate('stress-delay')
      )

      const result = await action
      const responseTime = performance.now() - startTime

      performanceTester.recordRequest(responseTime, result.error !== undefined)

      const metrics = performanceTester.endTest()

      expect(result.data).toBeDefined()
      expect(metrics.averageResponseTime).toBeGreaterThan(2000)
      expect(metrics.errorRate).toBe(0)

      console.log('高レスポンス時間テストメトリクス:', metrics)
    })

    it('高エラー率環境での耐性確認', async () => {
      failureRate = 0.3 // 30%のエラー率
      const store = createTestStore()
      const requestCount = 20

      performanceTester.startTest()

      const promises = Array.from({ length: requestCount }, async (_, i) => {
        const startTime = performance.now()
        
        try {
          const action = store.dispatch(
            apiSlice.endpoints.getConcurrentTest.initiate(`stress-error-${i}`)
          )
          
          const result = await action
          const responseTime = performance.now() - startTime
          
          performanceTester.recordRequest(responseTime, result.error !== undefined)
          
          return result
        } catch (error) {
          const responseTime = performance.now() - startTime
          performanceTester.recordRequest(responseTime, true)
          return { error: true }
        }
      })

      const results = await Promise.all(promises)
      const metrics = performanceTester.endTest()

      expect(metrics.errorRate).toBeGreaterThan(25) // エラー率が設定値に近い
      expect(metrics.errorRate).toBeLessThan(35)

      const successfulResults = results.filter(r => !r.error)
      expect(successfulResults.length).toBeGreaterThan(0) // 一部のリクエストは成功

      console.log('高エラー率耐性テストメトリクス:', metrics)
    })

    it('メモリ負荷テスト', async () => {
      const store = createTestStore()
      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0

      performanceTester.startTest()

      // 大量のメモリを消費するデータを複数回取得
      for (let i = 0; i < 5; i++) {
        const startTime = performance.now()
        
        const action = store.dispatch(
          apiSlice.endpoints.getMemoryStress.initiate({ size: 1000 })
        )
        
        const result = await action
        const responseTime = performance.now() - startTime
        
        performanceTester.recordRequest(responseTime, result.error !== undefined)

        expect(result.data).toBeDefined()
        expect(result.data.data).toHaveLength(1000)
      }

      const metrics = performanceTester.endTest()
      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0
      const memoryIncrease = finalMemory - initialMemory

      console.log('メモリ負荷テストメトリクス:', metrics)
      console.log('メモリ使用量増加:', memoryIncrease, 'bytes')

      // メモリリークが発生していないことを確認
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024) // 50MB未満の増加
      expect(metrics.errorRate).toBe(0)
    })

    it('長時間実行ストレステスト', async () => {
      const store = createTestStore()
      const testDuration = 10000 // 10秒間
      const requestInterval = 200 // 200ms間隔

      performanceTester.startTest()

      const startTime = Date.now()
      let requestCount = 0

      while (Date.now() - startTime < testDuration) {
        const reqStartTime = performance.now()
        
        try {
          const action = store.dispatch(
            apiSlice.endpoints.getConcurrentTest.initiate(`long-${requestCount++}`)
          )
          
          const result = await action
          const responseTime = performance.now() - reqStartTime
          
          performanceTester.recordRequest(responseTime, result.error !== undefined)
        } catch (error) {
          const responseTime = performance.now() - reqStartTime
          performanceTester.recordRequest(responseTime, true)
        }

        await new Promise(resolve => setTimeout(resolve, requestInterval))
      }

      const metrics = performanceTester.endTest()

      expect(requestCount).toBeGreaterThan(30) // 最低30リクエスト
      expect(metrics.errorRate).toBeLessThan(5) // 5%未満のエラー率
      expect(metrics.averageResponseTime).toBeLessThan(2000) // 2秒以内

      console.log('長時間実行ストレステストメトリクス:', metrics)
      console.log('総リクエスト数:', requestCount)
    })
  })

  describe('リアルタイム性能監視', () => {
    it('WebSocket接続の負荷テスト', async () => {
      // WebSocket接続のモック
      const mockWebSocket = {
        send: vi.fn(),
        close: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn()
      }

      global.WebSocket = vi.fn(() => mockWebSocket) as any

      const connectionCount = 10
      const connections: any[] = []

      performanceTester.startTest()

      // 複数のWebSocket接続を確立
      for (let i = 0; i < connectionCount; i++) {
        const startTime = performance.now()
        
        try {
          const ws = new WebSocket('ws://localhost:8080/ws')
          connections.push(ws)
          
          const responseTime = performance.now() - startTime
          performanceTester.recordRequest(responseTime, false)
        } catch (error) {
          const responseTime = performance.now() - startTime
          performanceTester.recordRequest(responseTime, true)
        }
      }

      const metrics = performanceTester.endTest()

      expect(connections).toHaveLength(connectionCount)
      expect(metrics.errorRate).toBe(0)
      expect(metrics.averageResponseTime).toBeLessThan(100) // 100ms以内

      // 接続をクリーンアップ
      connections.forEach(ws => ws.close())

      console.log('WebSocket負荷テストメトリクス:', metrics)
    })

    it('リアルタイムデータストリームの処理', async () => {
      const store = createTestStore()
      const streamDuration = 5000 // 5秒間
      const dataInterval = 100 // 100ms間隔

      performanceTester.startTest()

      const startTime = Date.now()
      let dataPointCount = 0

      // リアルタイムデータストリームをシミュレート
      const streamInterval = setInterval(async () => {
        const reqStartTime = performance.now()
        
        try {
          const action = store.dispatch(
            apiSlice.endpoints.getCurrentMetrics.initiate()
          )
          
          const result = await action
          const responseTime = performance.now() - reqStartTime
          
          performanceTester.recordRequest(responseTime, result.error !== undefined)
          dataPointCount++
        } catch (error) {
          const responseTime = performance.now() - reqStartTime
          performanceTester.recordRequest(responseTime, true)
        }
      }, dataInterval)

      // ストリームテストを実行
      await new Promise(resolve => setTimeout(resolve, streamDuration))
      clearInterval(streamInterval)

      const metrics = performanceTester.endTest()

      expect(dataPointCount).toBeGreaterThan(40) // 最低40データポイント
      expect(metrics.errorRate).toBeLessThan(2) // 2%未満のエラー率
      expect(metrics.averageResponseTime).toBeLessThan(500) // 500ms以内

      console.log('リアルタイムストリーム処理メトリクス:', metrics)
      console.log('処理データポイント数:', dataPointCount)
    })
  })
})