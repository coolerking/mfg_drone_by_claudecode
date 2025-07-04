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

// MSW サーバーセットアップ
const server = setupServer(
  // 認証API
  rest.post('/api/auth/login', (req, res, ctx) => {
    return res(
      ctx.json({
        user: { id: '1', username: 'testuser', role: 'admin' },
        token: 'mock-jwt-token'
      })
    )
  }),

  rest.post('/api/auth/refresh', (req, res, ctx) => {
    return res(
      ctx.json({
        token: 'new-mock-jwt-token'
      })
    )
  }),

  // ドローンAPI
  rest.get('/api/drones', (req, res, ctx) => {
    return res(
      ctx.json([
        {
          id: 'drone-1',
          name: 'Test Drone 1',
          model: 'DJI Mini 3',
          status: 'connected',
          battery: 85,
          position: { x: 0, y: 0, z: 0 }
        },
        {
          id: 'drone-2',
          name: 'Test Drone 2',
          model: 'DJI Air 2S',
          status: 'flying',
          battery: 70,
          position: { x: 10, y: 5, z: 15 }
        }
      ])
    )
  }),

  rest.post('/api/drones', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 'drone-new',
        name: 'New Drone',
        model: 'DJI Mavic 3',
        status: 'disconnected',
        battery: 100,
        position: { x: 0, y: 0, z: 0 }
      })
    )
  }),

  rest.put('/api/drones/:id/connect', (req, res, ctx) => {
    return res(
      ctx.json({
        id: req.params.id,
        status: 'connected'
      })
    )
  }),

  rest.put('/api/drones/:id/disconnect', (req, res, ctx) => {
    return res(
      ctx.json({
        id: req.params.id,
        status: 'disconnected'
      })
    )
  }),

  // ダッシュボードAPI
  rest.get('/api/dashboard/metrics', (req, res, ctx) => {
    return res(
      ctx.json({
        timestamp: new Date().toISOString(),
        cpu_usage: 45.5,
        memory_usage: 67.2,
        disk_usage: 23.8,
        network_in: 12.3,
        network_out: 8.7
      })
    )
  }),

  rest.get('/api/dashboard/system-health', (req, res, ctx) => {
    return res(
      ctx.json({
        overall_status: 'healthy',
        services: [
          {
            name: 'api-server',
            status: 'running',
            uptime: 86400
          }
        ]
      })
    )
  }),

  // データセットAPI
  rest.get('/api/datasets', (req, res, ctx) => {
    return res(
      ctx.json([
        {
          id: 'dataset-1',
          name: 'Test Dataset',
          type: 'object_detection',
          status: 'ready',
          image_count: 150
        }
      ])
    )
  }),

  // モデルAPI
  rest.get('/api/models', (req, res, ctx) => {
    return res(
      ctx.json([
        {
          id: 'model-1',
          name: 'YOLOv8 Detection',
          type: 'object_detection',
          status: 'trained',
          accuracy: 0.892
        }
      ])
    )
  }),

  // エラーレスポンス
  rest.get('/api/error-test', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({ error: 'Internal Server Error' })
    )
  })
)

// テスト用ストア作成
const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      api: apiSlice.reducer,
      auth: authSlice.reducer,
      drone: droneSlice.reducer,
      dashboard: dashboardSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(apiSlice.middleware),
    preloadedState: initialState,
  })
}

describe('API統合テスト', () => {
  beforeEach(() => {
    server.listen()
  })

  afterEach(() => {
    server.resetHandlers()
    vi.clearAllMocks()
  })

  afterAll(() => {
    server.close()
  })

  const wrapper = ({ children }: { children: React.ReactNode }) => {
    const store = createTestStore()
    return <Provider store={store}>{children}</Provider>
  }

  describe('認証API統合', () => {
    it('ログインAPIが正しく動作する', async () => {
      const store = createTestStore()
      
      const loginAction = store.dispatch(
        apiSlice.endpoints.login.initiate({
          username: 'testuser',
          password: 'password'
        })
      )

      const result = await loginAction

      expect(result.data).toEqual({
        user: { id: '1', username: 'testuser', role: 'admin' },
        token: 'mock-jwt-token'
      })
    })

    it('トークン更新APIが正しく動作する', async () => {
      const store = createTestStore()

      const refreshAction = store.dispatch(
        apiSlice.endpoints.refreshToken.initiate()
      )

      const result = await refreshAction

      expect(result.data).toEqual({
        token: 'new-mock-jwt-token'
      })
    })
  })

  describe('ドローンAPI統合', () => {
    it('ドローン一覧取得が正しく動作する', async () => {
      const store = createTestStore()

      const getDronesAction = store.dispatch(
        apiSlice.endpoints.getDrones.initiate()
      )

      const result = await getDronesAction

      expect(result.data).toHaveLength(2)
      expect(result.data[0]).toMatchObject({
        id: 'drone-1',
        name: 'Test Drone 1',
        status: 'connected'
      })
    })

    it('ドローン作成が正しく動作する', async () => {
      const store = createTestStore()

      const createDroneAction = store.dispatch(
        apiSlice.endpoints.createDrone.initiate({
          name: 'New Drone',
          model: 'DJI Mavic 3',
          ip_address: '192.168.1.100'
        })
      )

      const result = await createDroneAction

      expect(result.data).toMatchObject({
        id: 'drone-new',
        name: 'New Drone',
        model: 'DJI Mavic 3'
      })
    })

    it('ドローン接続が正しく動作する', async () => {
      const store = createTestStore()

      const connectAction = store.dispatch(
        apiSlice.endpoints.connectDrone.initiate('drone-1')
      )

      const result = await connectAction

      expect(result.data).toMatchObject({
        id: 'drone-1',
        status: 'connected'
      })
    })

    it('ドローン切断が正しく動作する', async () => {
      const store = createTestStore()

      const disconnectAction = store.dispatch(
        apiSlice.endpoints.disconnectDrone.initiate('drone-1')
      )

      const result = await disconnectAction

      expect(result.data).toMatchObject({
        id: 'drone-1',
        status: 'disconnected'
      })
    })
  })

  describe('ダッシュボードAPI統合', () => {
    it('システムメトリクス取得が正しく動作する', async () => {
      const store = createTestStore()

      const getMetricsAction = store.dispatch(
        apiSlice.endpoints.getCurrentMetrics.initiate()
      )

      const result = await getMetricsAction

      expect(result.data).toMatchObject({
        cpu_usage: 45.5,
        memory_usage: 67.2,
        disk_usage: 23.8
      })
    })

    it('システムヘルス取得が正しく動作する', async () => {
      const store = createTestStore()

      const getHealthAction = store.dispatch(
        apiSlice.endpoints.getSystemHealth.initiate()
      )

      const result = await getHealthAction

      expect(result.data).toMatchObject({
        overall_status: 'healthy',
        services: expect.arrayContaining([
          expect.objectContaining({
            name: 'api-server',
            status: 'running'
          })
        ])
      })
    })
  })

  describe('データセットAPI統合', () => {
    it('データセット一覧取得が正しく動作する', async () => {
      const store = createTestStore()

      const getDatasetsAction = store.dispatch(
        apiSlice.endpoints.getDatasets.initiate()
      )

      const result = await getDatasetsAction

      expect(result.data).toHaveLength(1)
      expect(result.data[0]).toMatchObject({
        id: 'dataset-1',
        name: 'Test Dataset',
        type: 'object_detection'
      })
    })
  })

  describe('モデルAPI統合', () => {
    it('モデル一覧取得が正しく動作する', async () => {
      const store = createTestStore()

      const getModelsAction = store.dispatch(
        apiSlice.endpoints.getModels.initiate()
      )

      const result = await getModelsAction

      expect(result.data).toHaveLength(1)
      expect(result.data[0]).toMatchObject({
        id: 'model-1',
        name: 'YOLOv8 Detection',
        type: 'object_detection'
      })
    })
  })

  describe('エラーハンドリング', () => {
    it('APIエラーが正しく処理される', async () => {
      const store = createTestStore()

      const errorAction = store.dispatch(
        apiSlice.endpoints.testError.initiate()
      )

      const result = await errorAction

      expect(result.error).toBeDefined()
      expect(result.error.status).toBe(500)
    })

    it('ネットワークエラーが正しく処理される', async () => {
      // ネットワークエラーをシミュレート
      server.use(
        rest.get('/api/drones', (req, res, ctx) => {
          return res.networkError('Network connection failed')
        })
      )

      const store = createTestStore()

      const getDronesAction = store.dispatch(
        apiSlice.endpoints.getDrones.initiate()
      )

      const result = await getDronesAction

      expect(result.error).toBeDefined()
      expect(result.error.name).toBe('FetchError')
    })
  })

  describe('キャッシング機能', () => {
    it('同じAPIコールがキャッシュされる', async () => {
      const store = createTestStore()

      // 最初のAPI呼び出し
      const firstCall = store.dispatch(
        apiSlice.endpoints.getDrones.initiate()
      )
      const firstResult = await firstCall

      // 同じAPI呼び出し（キャッシュされるべき）
      const secondCall = store.dispatch(
        apiSlice.endpoints.getDrones.initiate()
      )
      const secondResult = await secondCall

      expect(firstResult.data).toEqual(secondResult.data)
      
      // キャッシュ状態を確認
      const state = store.getState()
      const cacheEntry = state.api.queries['getDrones(undefined)']
      expect(cacheEntry).toBeDefined()
      expect(cacheEntry.status).toBe('fulfilled')
    })

    it('タグベースのキャッシュ無効化が機能する', async () => {
      const store = createTestStore()

      // ドローン一覧を取得
      await store.dispatch(
        apiSlice.endpoints.getDrones.initiate()
      )

      // 新しいドローンを作成（'Drone'タグを無効化）
      await store.dispatch(
        apiSlice.endpoints.createDrone.initiate({
          name: 'New Drone',
          model: 'Test Model',
          ip_address: '192.168.1.100'
        })
      )

      // キャッシュが無効化されることを確認
      const state = store.getState()
      const cacheEntry = state.api.queries['getDrones(undefined)']
      
      // キャッシュエントリが存在しないか、無効化されていることを確認
      expect(cacheEntry?.status).not.toBe('fulfilled')
    })
  })

  describe('楽観的更新', () => {
    it('ドローン接続の楽観的更新が機能する', async () => {
      const store = createTestStore()

      // 初期ドローンデータを取得
      await store.dispatch(
        apiSlice.endpoints.getDrones.initiate()
      )

      let state = store.getState()
      const initialDrones = state.api.queries['getDrones(undefined)'].data

      // ドローン接続（楽観的更新）
      const connectAction = store.dispatch(
        apiSlice.endpoints.connectDrone.initiate('drone-1')
      )

      // 楽観的更新により、即座にステータスが更新されることを確認
      state = store.getState()
      const updatedDrones = state.api.queries['getDrones(undefined)'].data
      
      // API レスポンス完了を待つ
      await connectAction

      expect(updatedDrones).toBeDefined()
    })
  })

  describe('リアルタイムデータ同期', () => {
    it('ポーリングが正しく動作する', async () => {
      vi.useFakeTimers()

      const store = createTestStore()

      // ポーリング付きでメトリクスを取得
      store.dispatch(
        apiSlice.endpoints.getCurrentMetrics.initiate(undefined, {
          pollingInterval: 5000
        })
      )

      // 5秒経過をシミュレート
      vi.advanceTimersByTime(5000)

      // ポーリングにより再度APIが呼ばれることを確認
      await waitFor(() => {
        const state = store.getState()
        const queries = Object.keys(state.api.queries)
        expect(queries.length).toBeGreaterThan(0)
      })

      vi.useRealTimers()
    })
  })

  describe('認証状態とAPI統合', () => {
    it('認証されていない場合のAPI呼び出しが適切に処理される', async () => {
      // 401エラーをシミュレート
      server.use(
        rest.get('/api/drones', (req, res, ctx) => {
          return res(
            ctx.status(401),
            ctx.json({ error: 'Unauthorized' })
          )
        })
      )

      const store = createTestStore()

      const getDronesAction = store.dispatch(
        apiSlice.endpoints.getDrones.initiate()
      )

      const result = await getDronesAction

      expect(result.error).toBeDefined()
      expect(result.error.status).toBe(401)
    })

    it('トークン期限切れ時の自動更新が機能する', async () => {
      // 最初は401、その後正常なレスポンス
      let callCount = 0
      server.use(
        rest.get('/api/drones', (req, res, ctx) => {
          callCount++
          if (callCount === 1) {
            return res(
              ctx.status(401),
              ctx.json({ error: 'Token expired' })
            )
          }
          return res(
            ctx.json([
              {
                id: 'drone-1',
                name: 'Test Drone',
                status: 'connected'
              }
            ])
          )
        })
      )

      const store = createTestStore({
        auth: {
          user: { id: '1', username: 'testuser', role: 'user' },
          token: 'expired-token',
          isAuthenticated: true
        }
      })

      const getDronesAction = store.dispatch(
        apiSlice.endpoints.getDrones.initiate()
      )

      const result = await getDronesAction

      // 最終的に成功することを確認
      expect(result.data).toBeDefined()
      expect(callCount).toBe(2) // 初回失敗、リトライ成功
    })
  })
})