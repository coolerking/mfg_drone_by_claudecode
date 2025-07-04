import { renderHook, act, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { useAuth } from '../../hooks/useAuth'
import { authSlice } from '../../store/slices/authSlice'

// Create a test store
const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authSlice.reducer,
    },
    preloadedState: {
      auth: {
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        ...initialState,
      },
    },
  })
}

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock as any

// Mock API calls
vi.mock('../../services/api/apiClient', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  }
}))

describe('useAuth Hook', () => {
  let store: ReturnType<typeof createTestStore>

  beforeEach(() => {
    store = createTestStore()
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <Provider store={store}>{children}</Provider>
  )

  it('初期状態が正しく設定される', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.user).toBeNull()
    expect(result.current.token).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('ローカルストレージからトークンを復元する', () => {
    const mockToken = 'mock-jwt-token'
    const mockUser = { id: '1', username: 'testuser', role: 'user' }
    
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'auth_token') return mockToken
      if (key === 'auth_user') return JSON.stringify(mockUser)
      return null
    })

    store = createTestStore({
      token: mockToken,
      user: mockUser,
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.token).toBe(mockToken)
    expect(result.current.user).toEqual(mockUser)
    expect(result.current.isAuthenticated).toBe(true)
  })

  it('ログイン機能が正しく動作する', async () => {
    const mockApiResponse = {
      user: { id: '1', username: 'testuser', role: 'user' },
      token: 'new-jwt-token',
    }

    const { apiClient } = await import('../../services/api/apiClient')
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockApiResponse })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.login('testuser', 'password')
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toEqual(mockApiResponse.user)
      expect(result.current.token).toBe(mockApiResponse.token)
    })

    // ローカルストレージに保存されることを確認
    expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', mockApiResponse.token)
    expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(mockApiResponse.user))
  })

  it('ログイン失敗時にエラーが設定される', async () => {
    const mockError = new Error('Invalid credentials')
    
    const { apiClient } = await import('../../services/api/apiClient')
    vi.mocked(apiClient.post).mockRejectedValueOnce(mockError)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.login('invalid', 'credentials')
    })

    await waitFor(() => {
      expect(result.current.error).toBe('ユーザー名またはパスワードが正しくありません')
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  it('ログアウト機能が正しく動作する', () => {
    store = createTestStore({
      token: 'existing-token',
      user: { id: '1', username: 'testuser', role: 'user' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    act(() => {
      result.current.logout()
    })

    expect(result.current.user).toBeNull()
    expect(result.current.token).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)

    // ローカルストレージがクリアされることを確認
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
  })

  it('トークンの自動更新が機能する', async () => {
    const mockRefreshResponse = {
      token: 'refreshed-token',
      user: { id: '1', username: 'testuser', role: 'user' },
    }

    const { apiClient } = await import('../../services/api/apiClient')
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockRefreshResponse })

    store = createTestStore({
      token: 'old-token',
      user: { id: '1', username: 'testuser', role: 'user' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.refreshToken()
    })

    await waitFor(() => {
      expect(result.current.token).toBe(mockRefreshResponse.token)
    })

    expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', mockRefreshResponse.token)
  })

  it('トークンの有効性チェックが機能する', () => {
    // 有効なトークン（JWTモック）
    const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjk5OTk5OTk5OTl9.Lrx-3L6E6wy2L3EjQJKQYWZWQ3X8wQ3g3-6pV2E3Nmc'
    
    store = createTestStore({
      token: validToken,
      user: { id: '1', username: 'testuser', role: 'user' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.isTokenValid()).toBe(true)
  })

  it('無効なトークンが検出される', () => {
    // 期限切れのトークン
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid'
    
    store = createTestStore({
      token: expiredToken,
      user: { id: '1', username: 'testuser', role: 'user' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.isTokenValid()).toBe(false)
  })

  it('権限チェック機能が正しく動作する', () => {
    store = createTestStore({
      token: 'valid-token',
      user: { id: '1', username: 'admin', role: 'admin' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.hasRole('admin')).toBe(true)
    expect(result.current.hasRole('user')).toBe(true)
    expect(result.current.hasRole('superadmin')).toBe(false)
  })

  it('ユーザー権限の階層が正しく処理される', () => {
    store = createTestStore({
      token: 'valid-token',
      user: { id: '1', username: 'user', role: 'user' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.hasRole('user')).toBe(true)
    expect(result.current.hasRole('admin')).toBe(false)
  })

  it('Remember Me 機能が正しく動作する', async () => {
    const mockApiResponse = {
      user: { id: '1', username: 'testuser', role: 'user' },
      token: 'new-jwt-token',
    }

    const { apiClient } = await import('../../services/api/apiClient')
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockApiResponse })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.login('testuser', 'password', true) // Remember Me = true
    })

    // 永続化されることを確認
    expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_remember', 'true')
  })

  it('自動ログアウトタイマーが機能する', async () => {
    vi.useFakeTimers()
    
    store = createTestStore({
      token: 'valid-token',
      user: { id: '1', username: 'testuser', role: 'user' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    // 15分（900秒）経過をシミュレート
    act(() => {
      vi.advanceTimersByTime(900 * 1000)
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(false)
    })

    vi.useRealTimers()
  })

  it('ユーザー情報の更新が機能する', async () => {
    const updatedUser = { id: '1', username: 'updateduser', role: 'admin' }
    
    const { apiClient } = await import('../../services/api/apiClient')
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: updatedUser })

    store = createTestStore({
      token: 'valid-token',
      user: { id: '1', username: 'testuser', role: 'user' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.updateUserInfo()
    })

    await waitFor(() => {
      expect(result.current.user).toEqual(updatedUser)
    })

    expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(updatedUser))
  })

  it('ネットワークエラー時の処理が正しく動作する', async () => {
    const networkError = new Error('Network Error')
    
    const { apiClient } = await import('../../services/api/apiClient')
    vi.mocked(apiClient.post).mockRejectedValueOnce(networkError)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.login('testuser', 'password')
    })

    await waitFor(() => {
      expect(result.current.error).toBe('ネットワークエラーが発生しました')
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  it('複数タブでの同期が機能する', () => {
    store = createTestStore({
      token: 'valid-token',
      user: { id: '1', username: 'testuser', role: 'user' },
      isAuthenticated: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    // 他のタブでログアウトが発生したことをシミュレート
    act(() => {
      // StorageEventをシミュレート
      const storageEvent = new StorageEvent('storage', {
        key: 'auth_token',
        oldValue: 'valid-token',
        newValue: null,
      })
      window.dispatchEvent(storageEvent)
    })

    expect(result.current.isAuthenticated).toBe(false)
  })
})