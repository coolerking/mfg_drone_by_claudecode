import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { SnackbarProvider } from 'notistack'
import { useNotification } from '../../hooks/useNotification'

// Mock notistack
const mockEnqueueSnackbar = vi.fn()
const mockCloseSnackbar = vi.fn()

vi.mock('notistack', async () => {
  const actual = await vi.importActual('notistack')
  return {
    ...actual,
    useSnackbar: () => ({
      enqueueSnackbar: mockEnqueueSnackbar,
      closeSnackbar: mockCloseSnackbar,
    }),
  }
})

describe('useNotification Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <SnackbarProvider maxSnack={3}>
      {children}
    </SnackbarProvider>
  )

  it('成功通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showSuccess('操作が成功しました')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('操作が成功しました', {
      variant: 'success',
      autoHideDuration: 4000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('エラー通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showError('エラーが発生しました')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('エラーが発生しました', {
      variant: 'error',
      autoHideDuration: 6000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('警告通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showWarning('警告: バッテリー残量が少なくなっています')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('警告: バッテリー残量が少なくなっています', {
      variant: 'warning',
      autoHideDuration: 5000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('情報通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showInfo('新しいドローンが接続されました')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('新しいドローンが接続されました', {
      variant: 'info',
      autoHideDuration: 4000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('カスタムオプション付きの通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    const customOptions = {
      autoHideDuration: 8000,
      persist: true,
      action: 'カスタムアクション',
    }

    act(() => {
      result.current.showNotification('カスタム通知', 'success', customOptions)
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('カスタム通知', {
      variant: 'success',
      autoHideDuration: 8000,
      persist: true,
      action: 'カスタムアクション',
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('通知の削除が正しく動作する', () => {
    mockEnqueueSnackbar.mockReturnValue('notification-key-123')
    
    const { result } = renderHook(() => useNotification(), { wrapper })

    let notificationKey: string

    act(() => {
      notificationKey = result.current.showSuccess('削除予定の通知')
    })

    act(() => {
      result.current.dismissNotification(notificationKey)
    })

    expect(mockCloseSnackbar).toHaveBeenCalledWith('notification-key-123')
  })

  it('全通知の削除が正しく動作する', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.dismissAll()
    })

    expect(mockCloseSnackbar).toHaveBeenCalledWith()
  })

  it('ドローン関連の通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showDroneConnected('Test Drone')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('ドローン "Test Drone" が接続されました', {
      variant: 'success',
      autoHideDuration: 4000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('ドローン切断通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showDroneDisconnected('Test Drone')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('ドローン "Test Drone" が切断されました', {
      variant: 'warning',
      autoHideDuration: 5000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('バッテリー警告通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showBatteryWarning('Test Drone', 15)
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('ドローン "Test Drone" のバッテリー残量が15%になりました', {
      variant: 'warning',
      autoHideDuration: 8000,
      persist: true,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('学習完了通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showTrainingCompleted('YOLOv8 Object Detection')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('モデル "YOLOv8 Object Detection" の学習が完了しました', {
      variant: 'success',
      autoHideDuration: 6000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('学習失敗通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showTrainingFailed('YOLOv8 Object Detection', 'データセットが見つかりません')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('モデル "YOLOv8 Object Detection" の学習が失敗しました: データセットが見つかりません', {
      variant: 'error',
      autoHideDuration: 8000,
      persist: true,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('API エラー通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    const apiError = {
      message: 'ネットワークエラー',
      status: 500,
      code: 'NETWORK_ERROR'
    }

    act(() => {
      result.current.showApiError(apiError)
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('API エラー (500): ネットワークエラー', {
      variant: 'error',
      autoHideDuration: 6000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('ファイルアップロード成功通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showUploadSuccess('image.jpg', 5)
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('ファイル "image.jpg" を含む5個のファイルがアップロードされました', {
      variant: 'success',
      autoHideDuration: 4000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('ファイルアップロード失敗通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showUploadError(['image1.jpg', 'image2.jpg'])
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('ファイルのアップロードに失敗しました: image1.jpg, image2.jpg', {
      variant: 'error',
      autoHideDuration: 6000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('システムメンテナンス通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showSystemMaintenance('2024-01-15 02:00')
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('システムメンテナンス予定: 2024-01-15 02:00', {
      variant: 'info',
      autoHideDuration: 10000,
      persist: true,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('オフライン通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showOfflineNotification()
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('インターネット接続が切断されました', {
      variant: 'warning',
      persist: true,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('オンライン復帰通知が正しく表示される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showOnlineNotification()
    })

    expect(mockEnqueueSnackbar).toHaveBeenCalledWith('インターネット接続が復旧しました', {
      variant: 'success',
      autoHideDuration: 3000,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
    })
  })

  it('通知履歴が正しく管理される', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showSuccess('テスト通知 1')
      result.current.showError('テスト通知 2')
      result.current.showWarning('テスト通知 3')
    })

    expect(result.current.notificationHistory).toHaveLength(3)
    expect(result.current.notificationHistory[0]).toMatchObject({
      message: 'テスト通知 1',
      variant: 'success',
      timestamp: expect.any(Date),
    })
  })

  it('通知履歴がクリアされる', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showSuccess('テスト通知')
      result.current.clearHistory()
    })

    expect(result.current.notificationHistory).toHaveLength(0)
  })

  it('重複通知の抑制が機能する', () => {
    const { result } = renderHook(() => useNotification(), { wrapper })

    act(() => {
      result.current.showSuccess('重複テスト', { preventDuplicate: true })
      result.current.showSuccess('重複テスト', { preventDuplicate: true })
    })

    // 1回だけ呼ばれることを確認
    expect(mockEnqueueSnackbar).toHaveBeenCalledTimes(1)
  })
})