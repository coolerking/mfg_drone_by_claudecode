import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useWebSocket } from '../../hooks/useWebSocket'
import { io } from 'socket.io-client'

// Mock socket.io-client
vi.mock('socket.io-client', () => ({
  io: vi.fn(),
}))

// Mock socket instance
const mockSocket = {
  connected: false,
  connect: vi.fn(),
  disconnect: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  emit: vi.fn(),
  removeAllListeners: vi.fn(),
}

describe('useWebSocket Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(io).mockReturnValue(mockSocket as any)
    mockSocket.connected = false
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('初期状態が正しく設定される', () => {
    const { result } = renderHook(() => useWebSocket('http://localhost:3001'))

    expect(result.current.isConnected).toBe(false)
    expect(result.current.error).toBeNull()
    expect(typeof result.current.sendMessage).toBe('function')
    expect(typeof result.current.connect).toBe('function')
    expect(typeof result.current.disconnect).toBe('function')
  })

  it('WebSocket接続が正しく初期化される', () => {
    renderHook(() => useWebSocket('http://localhost:3001'))

    expect(io).toHaveBeenCalledWith('http://localhost:3001', {
      autoConnect: false,
      transports: ['websocket'],
      upgrade: false,
      rememberUpgrade: false,
    })
  })

  it('接続機能が正しく動作する', () => {
    const { result } = renderHook(() => useWebSocket('http://localhost:3001'))

    act(() => {
      result.current.connect()
    })

    expect(mockSocket.connect).toHaveBeenCalled()
  })

  it('切断機能が正しく動作する', () => {
    const { result } = renderHook(() => useWebSocket('http://localhost:3001'))

    act(() => {
      result.current.disconnect()
    })

    expect(mockSocket.disconnect).toHaveBeenCalled()
  })

  it('メッセージ送信機能が正しく動作する', () => {
    const { result } = renderHook(() => useWebSocket('http://localhost:3001'))
    const testEvent = 'test-event'
    const testData = { message: 'test' }

    act(() => {
      result.current.sendMessage(testEvent, testData)
    })

    expect(mockSocket.emit).toHaveBeenCalledWith(testEvent, testData)
  })

  it('接続状態の変化が正しく追跡される', () => {
    const { result } = renderHook(() => useWebSocket('http://localhost:3001'))

    // connect イベントのハンドラーを取得
    const connectHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'connect'
    )?.[1]

    expect(connectHandler).toBeDefined()

    // 接続イベントをシミュレート
    act(() => {
      mockSocket.connected = true
      connectHandler?.()
    })

    expect(result.current.isConnected).toBe(true)
  })

  it('切断状態の変化が正しく追跡される', () => {
    const { result } = renderHook(() => useWebSocket('http://localhost:3001'))

    // 最初に接続状態にする
    act(() => {
      mockSocket.connected = true
    })

    // disconnect イベントのハンドラーを取得
    const disconnectHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'disconnect'
    )?.[1]

    expect(disconnectHandler).toBeDefined()

    // 切断イベントをシミュレート
    act(() => {
      mockSocket.connected = false
      disconnectHandler?.('transport close')
    })

    expect(result.current.isConnected).toBe(false)
  })

  it('エラーハンドリングが正しく動作する', () => {
    const { result } = renderHook(() => useWebSocket('http://localhost:3001'))

    // error イベントのハンドラーを取得
    const errorHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'connect_error'
    )?.[1]

    expect(errorHandler).toBeDefined()

    const testError = new Error('Connection failed')

    // エラーイベントをシミュレート
    act(() => {
      errorHandler?.(testError)
    })

    expect(result.current.error).toBe('Connection failed')
    expect(result.current.isConnected).toBe(false)
  })

  it('カスタムイベントリスナーが正しく登録される', () => {
    const eventHandlers = {
      'drone-status': vi.fn(),
      'system-alert': vi.fn(),
    }

    renderHook(() => useWebSocket('http://localhost:3001', { eventHandlers }))

    // カスタムイベントハンドラーが登録されることを確認
    expect(mockSocket.on).toHaveBeenCalledWith('drone-status', eventHandlers['drone-status'])
    expect(mockSocket.on).toHaveBeenCalledWith('system-alert', eventHandlers['system-alert'])
  })

  it('再接続機能が正しく動作する', () => {
    const { result } = renderHook(() => 
      useWebSocket('http://localhost:3001', { 
        autoReconnect: true,
        reconnectAttempts: 3,
        reconnectDelay: 1000
      })
    )

    // 接続エラーをシミュレート
    const errorHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'connect_error'
    )?.[1]

    act(() => {
      errorHandler?.(new Error('Connection failed'))
    })

    // 再接続が試行されることを確認
    expect(result.current.reconnectAttempts).toBe(1)
  })

  it('自動再接続が無効な場合、再接続を試行しない', () => {
    const { result } = renderHook(() => 
      useWebSocket('http://localhost:3001', { 
        autoReconnect: false 
      })
    )

    // 接続エラーをシミュレート
    const errorHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'connect_error'
    )?.[1]

    act(() => {
      errorHandler?.(new Error('Connection failed'))
    })

    // 再接続が試行されないことを確認
    expect(result.current.reconnectAttempts).toBe(0)
  })

  it('最大再接続回数に達したら再接続を停止する', () => {
    const { result } = renderHook(() => 
      useWebSocket('http://localhost:3001', { 
        autoReconnect: true,
        reconnectAttempts: 2,
        reconnectDelay: 100
      })
    )

    const errorHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'connect_error'
    )?.[1]

    // 最大回数まで再接続を試行
    act(() => {
      errorHandler?.(new Error('Connection failed'))
    })
    act(() => {
      errorHandler?.(new Error('Connection failed'))
    })
    act(() => {
      errorHandler?.(new Error('Connection failed'))
    })

    expect(result.current.reconnectAttempts).toBe(2)
    expect(result.current.error).toContain('最大再接続回数に達しました')
  })

  it('ドローンステータス更新イベントが正しく処理される', () => {
    const onDroneStatusUpdate = vi.fn()
    
    renderHook(() => 
      useWebSocket('http://localhost:3001', {
        eventHandlers: {
          'drone-status-update': onDroneStatusUpdate
        }
      })
    )

    // drone-status-update イベントのハンドラーを取得
    const statusHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'drone-status-update'
    )?.[1]

    const droneStatus = {
      droneId: 'drone-001',
      status: 'flying',
      battery: 75,
      position: { x: 10, y: 20, z: 30 }
    }

    // イベントをシミュレート
    act(() => {
      statusHandler?.(droneStatus)
    })

    expect(onDroneStatusUpdate).toHaveBeenCalledWith(droneStatus)
  })

  it('システムアラートイベントが正しく処理される', () => {
    const onSystemAlert = vi.fn()
    
    renderHook(() => 
      useWebSocket('http://localhost:3001', {
        eventHandlers: {
          'system-alert': onSystemAlert
        }
      })
    )

    // system-alert イベントのハンドラーを取得
    const alertHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'system-alert'
    )?.[1]

    const alertData = {
      id: 'alert-001',
      type: 'warning',
      message: 'Low battery detected',
      droneId: 'drone-001'
    }

    // イベントをシミュレート
    act(() => {
      alertHandler?.(alertData)
    })

    expect(onSystemAlert).toHaveBeenCalledWith(alertData)
  })

  it('学習進捗更新イベントが正しく処理される', () => {
    const onTrainingProgress = vi.fn()
    
    renderHook(() => 
      useWebSocket('http://localhost:3001', {
        eventHandlers: {
          'training-progress': onTrainingProgress
        }
      })
    )

    const progressHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'training-progress'
    )?.[1]

    const progressData = {
      modelId: 'model-001',
      epoch: 10,
      totalEpochs: 100,
      loss: 0.245,
      accuracy: 0.892
    }

    act(() => {
      progressHandler?.(progressData)
    })

    expect(onTrainingProgress).toHaveBeenCalledWith(progressData)
  })

  it('コンポーネントアンマウント時にクリーンアップが実行される', () => {
    const { unmount } = renderHook(() => useWebSocket('http://localhost:3001'))

    // アンマウント実行
    unmount()

    // イベントリスナーが削除されることを確認
    expect(mockSocket.removeAllListeners).toHaveBeenCalled()
    expect(mockSocket.disconnect).toHaveBeenCalled()
  })

  it('URLが変更された場合に再接続される', () => {
    const { rerender } = renderHook(
      ({ url }) => useWebSocket(url),
      { initialProps: { url: 'http://localhost:3001' } }
    )

    // URL変更
    rerender({ url: 'http://localhost:3002' })

    // 新しいURLで再接続されることを確認
    expect(io).toHaveBeenCalledWith('http://localhost:3002', expect.any(Object))
  })

  it('接続状態のハートビート機能が動作する', () => {
    vi.useFakeTimers()

    renderHook(() => 
      useWebSocket('http://localhost:3001', {
        heartbeat: true,
        heartbeatInterval: 5000
      })
    )

    // 接続状態にする
    act(() => {
      mockSocket.connected = true
    })

    // ハートビート間隔を進める
    act(() => {
      vi.advanceTimersByTime(5000)
    })

    // pingメッセージが送信されることを確認
    expect(mockSocket.emit).toHaveBeenCalledWith('ping')

    vi.useRealTimers()
  })

  it('メッセージキューが接続時に送信される', () => {
    const { result } = renderHook(() => useWebSocket('http://localhost:3001'))

    // 未接続時にメッセージ送信
    act(() => {
      result.current.sendMessage('test-event', { data: 'test' })
    })

    // メッセージは送信されない（キューに入る）
    expect(mockSocket.emit).not.toHaveBeenCalled()

    // 接続状態にする
    const connectHandler = mockSocket.on.mock.calls.find(
      call => call[0] === 'connect'
    )?.[1]

    act(() => {
      mockSocket.connected = true
      connectHandler?.()
    })

    // キューされたメッセージが送信される
    expect(mockSocket.emit).toHaveBeenCalledWith('test-event', { data: 'test' })
  })
})