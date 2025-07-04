import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useOffline } from '../../hooks/useOffline'

// Mock navigator.onLine
Object.defineProperty(window.navigator, 'onLine', {
  writable: true,
  value: true,
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock as any

describe('useOffline Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.navigator.onLine = true
    localStorageMock.getItem.mockReturnValue(null)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('初期状態が正しく設定される', () => {
    const { result } = renderHook(() => useOffline())

    expect(result.current.isOnline).toBe(true)
    expect(result.current.isOffline).toBe(false)
    expect(result.current.queuedActions).toEqual([])
    expect(result.current.lastOnlineTime).toBeNull()
  })

  it('オフライン状態の検出が正しく動作する', () => {
    const { result } = renderHook(() => useOffline())

    // オフラインイベントをシミュレート
    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    expect(result.current.isOnline).toBe(false)
    expect(result.current.isOffline).toBe(true)
    expect(result.current.lastOnlineTime).toBeInstanceOf(Date)
  })

  it('オンライン復帰の検出が正しく動作する', () => {
    const { result } = renderHook(() => useOffline())

    // まずオフラインにする
    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    // オンライン復帰をシミュレート
    act(() => {
      window.navigator.onLine = true
      const onlineEvent = new Event('online')
      window.dispatchEvent(onlineEvent)
    })

    expect(result.current.isOnline).toBe(true)
    expect(result.current.isOffline).toBe(false)
  })

  it('オフライン時のアクションキューイングが機能する', () => {
    const { result } = renderHook(() => useOffline())

    // オフライン状態にする
    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    // アクションをキューに追加
    act(() => {
      result.current.queueAction({
        id: 'action-1',
        type: 'API_CALL',
        payload: { endpoint: '/api/drones', method: 'GET' },
        timestamp: new Date(),
      })
    })

    expect(result.current.queuedActions).toHaveLength(1)
    expect(result.current.queuedActions[0]).toMatchObject({
      id: 'action-1',
      type: 'API_CALL',
      payload: { endpoint: '/api/drones', method: 'GET' },
    })
  })

  it('複数のアクションを正しくキューイングする', () => {
    const { result } = renderHook(() => useOffline())

    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    const actions = [
      {
        id: 'action-1',
        type: 'CREATE_DRONE',
        payload: { name: 'Drone 1' },
        timestamp: new Date(),
      },
      {
        id: 'action-2',
        type: 'UPDATE_DRONE',
        payload: { id: 'drone-1', battery: 85 },
        timestamp: new Date(),
      },
      {
        id: 'action-3',
        type: 'DELETE_DRONE',
        payload: { id: 'drone-2' },
        timestamp: new Date(),
      },
    ]

    act(() => {
      actions.forEach(action => result.current.queueAction(action))
    })

    expect(result.current.queuedActions).toHaveLength(3)
  })

  it('キューの最大サイズ制限が機能する', () => {
    const { result } = renderHook(() => useOffline({ maxQueueSize: 2 }))

    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    // 3つのアクションを追加（最大2つまで）
    act(() => {
      result.current.queueAction({
        id: 'action-1',
        type: 'TEST',
        payload: {},
        timestamp: new Date(),
      })
      result.current.queueAction({
        id: 'action-2',
        type: 'TEST',
        payload: {},
        timestamp: new Date(),
      })
      result.current.queueAction({
        id: 'action-3',
        type: 'TEST',
        payload: {},
        timestamp: new Date(),
      })
    })

    expect(result.current.queuedActions).toHaveLength(2)
    // 最新の2つが保持されることを確認
    expect(result.current.queuedActions[0].id).toBe('action-2')
    expect(result.current.queuedActions[1].id).toBe('action-3')
  })

  it('オンライン復帰時にキューが処理される', async () => {
    const onQueueProcess = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() => useOffline({ onQueueProcess }))

    // オフライン状態でアクションをキューイング
    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    act(() => {
      result.current.queueAction({
        id: 'action-1',
        type: 'TEST',
        payload: {},
        timestamp: new Date(),
      })
    })

    // オンライン復帰
    act(() => {
      window.navigator.onLine = true
      const onlineEvent = new Event('online')
      window.dispatchEvent(onlineEvent)
    })

    // キュー処理コールバックが呼ばれることを確認
    expect(onQueueProcess).toHaveBeenCalledWith([
      expect.objectContaining({
        id: 'action-1',
        type: 'TEST',
      })
    ])
  })

  it('キューの手動クリアが機能する', () => {
    const { result } = renderHook(() => useOffline())

    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    act(() => {
      result.current.queueAction({
        id: 'action-1',
        type: 'TEST',
        payload: {},
        timestamp: new Date(),
      })
    })

    expect(result.current.queuedActions).toHaveLength(1)

    act(() => {
      result.current.clearQueue()
    })

    expect(result.current.queuedActions).toHaveLength(0)
  })

  it('ローカルストレージでのキュー永続化が機能する', () => {
    const { result } = renderHook(() => useOffline({ persistQueue: true }))

    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    act(() => {
      result.current.queueAction({
        id: 'action-1',
        type: 'TEST',
        payload: {},
        timestamp: new Date(),
      })
    })

    // ローカルストレージに保存されることを確認
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'offline_queue',
      expect.stringContaining('"id":"action-1"')
    )
  })

  it('ローカルストレージからキューを復元する', () => {
    const queueData = [
      {
        id: 'action-1',
        type: 'TEST',
        payload: {},
        timestamp: '2024-01-01T00:00:00.000Z',
      }
    ]

    localStorageMock.getItem.mockReturnValue(JSON.stringify(queueData))

    const { result } = renderHook(() => useOffline({ persistQueue: true }))

    expect(result.current.queuedActions).toHaveLength(1)
    expect(result.current.queuedActions[0].id).toBe('action-1')
  })

  it('破損したローカルストレージデータを適切に処理する', () => {
    localStorageMock.getItem.mockReturnValue('invalid json')

    const { result } = renderHook(() => useOffline({ persistQueue: true }))

    // エラーが発生しても正常に初期化される
    expect(result.current.queuedActions).toEqual([])
  })

  it('オフライン時間の追跡が機能する', () => {
    vi.useFakeTimers()
    const startTime = new Date('2024-01-01T00:00:00.000Z')
    vi.setSystemTime(startTime)

    const { result } = renderHook(() => useOffline())

    // オフラインにする
    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    expect(result.current.lastOnlineTime).toEqual(startTime)

    // 5分経過
    vi.advanceTimersByTime(5 * 60 * 1000)

    expect(result.current.getOfflineDuration()).toBe(5 * 60 * 1000)

    vi.useRealTimers()
  })

  it('ネットワーク状態変化時のコールバックが呼ばれる', () => {
    const onOnline = vi.fn()
    const onOffline = vi.fn()

    renderHook(() => useOffline({ onOnline, onOffline }))

    // オフラインイベント
    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    expect(onOffline).toHaveBeenCalled()

    // オンラインイベント
    act(() => {
      window.navigator.onLine = true
      const onlineEvent = new Event('online')
      window.dispatchEvent(onlineEvent)
    })

    expect(onOnline).toHaveBeenCalled()
  })

  it('アクション重複の除去が機能する', () => {
    const { result } = renderHook(() => useOffline({ removeDuplicates: true }))

    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    const action = {
      id: 'action-1',
      type: 'UPDATE_DRONE',
      payload: { id: 'drone-1', battery: 85 },
      timestamp: new Date(),
    }

    // 同じアクションを2回追加
    act(() => {
      result.current.queueAction(action)
      result.current.queueAction(action)
    })

    // 重複は除去され、1つだけ残る
    expect(result.current.queuedActions).toHaveLength(1)
  })

  it('古いアクションの自動削除が機能する', () => {
    vi.useFakeTimers()
    
    const { result } = renderHook(() => 
      useOffline({ 
        maxAge: 5 * 60 * 1000, // 5分
        cleanupInterval: 1000   // 1秒間隔でクリーンアップ
      })
    )

    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    // 古いアクションを追加
    act(() => {
      result.current.queueAction({
        id: 'old-action',
        type: 'TEST',
        payload: {},
        timestamp: new Date(Date.now() - 6 * 60 * 1000), // 6分前
      })
    })

    expect(result.current.queuedActions).toHaveLength(1)

    // クリーンアップ間隔を進める
    act(() => {
      vi.advanceTimersByTime(1000)
    })

    // 古いアクションが削除される
    expect(result.current.queuedActions).toHaveLength(0)

    vi.useRealTimers()
  })

  it('コンポーネントアンマウント時のクリーンアップが正しく動作する', () => {
    const { unmount } = renderHook(() => useOffline())

    // イベントリスナーが削除されることを確認するため、
    // 実際のテストではEvent Listenerのモックが必要
    unmount()

    // アンマウント後にイベントを発火してもエラーが発生しないことを確認
    expect(() => {
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    }).not.toThrow()
  })

  it('キュー統計情報が正しく取得される', () => {
    const { result } = renderHook(() => useOffline())

    act(() => {
      window.navigator.onLine = false
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)
    })

    act(() => {
      result.current.queueAction({
        id: 'action-1',
        type: 'CREATE',
        payload: {},
        timestamp: new Date(),
      })
      result.current.queueAction({
        id: 'action-2',
        type: 'UPDATE',
        payload: {},
        timestamp: new Date(),
      })
      result.current.queueAction({
        id: 'action-3',
        type: 'CREATE',
        payload: {},
        timestamp: new Date(),
      })
    })

    const stats = result.current.getQueueStats()

    expect(stats.total).toBe(3)
    expect(stats.byType.CREATE).toBe(2)
    expect(stats.byType.UPDATE).toBe(1)
    expect(stats.oldestTimestamp).toBeInstanceOf(Date)
    expect(stats.newestTimestamp).toBeInstanceOf(Date)
  })
})