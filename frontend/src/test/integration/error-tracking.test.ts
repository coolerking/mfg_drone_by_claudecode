/**
 * Error Tracking System Integration Tests
 * Tests for Sentry integration, error analytics, and log analysis
 */

import { describe, it, expect, beforeEach, afterEach, vi, Mock } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { store } from '../../store'
import sentryService from '../../utils/sentry'
import ErrorAnalyticsDashboard from '../../components/monitoring/ErrorAnalyticsDashboard'
import AdvancedLogAnalyzer from '../../components/monitoring/AdvancedLogAnalyzer'

// Mock Sentry
vi.mock('@sentry/react', () => ({
  init: vi.fn(),
  captureException: vi.fn(),
  captureMessage: vi.fn(),
  addBreadcrumb: vi.fn(),
  setUser: vi.fn(),
  setContext: vi.fn(),
  startTransaction: vi.fn(() => ({
    setStatus: vi.fn(),
    finish: vi.fn(),
  })),
  withProfiler: vi.fn((component) => component),
  lastEventId: vi.fn(() => 'test-event-id'),
  showReportDialog: vi.fn(),
  getCurrentHub: vi.fn(() => ({
    getClient: vi.fn(() => ({
      close: vi.fn(),
    })),
  })),
}))

vi.mock('@sentry/tracing', () => ({
  BrowserTracing: vi.fn(() => ({})),
}))

vi.mock('@sentry/integrations', () => ({
  CaptureConsole: vi.fn(() => ({})),
}))

// Mock environment variables
Object.defineProperty(import.meta, 'env', {
  value: {
    VITE_SENTRY_DSN: 'https://test@sentry.io/test',
    VITE_APP_VERSION: '1.0.0-test',
    MODE: 'test',
    PROD: false,
    VITEST: true,
  },
})

// Mock notifications
const mockShowNotification = vi.fn()
vi.mock('../../components/common', () => ({
  useNotification: () => ({
    showNotification: mockShowNotification,
  }),
}))

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <Provider store={store}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </Provider>
)

describe('Error Tracking System Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset console methods
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    vi.spyOn(console, 'log').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Sentry Integration', () => {
    it('should initialize Sentry with correct configuration', () => {
      const { init } = require('@sentry/react')
      
      sentryService.initialize()

      expect(init).toHaveBeenCalledWith(
        expect.objectContaining({
          dsn: 'https://test@sentry.io/test',
          environment: 'test',
          release: '1.0.0-test',
          sampleRate: 1.0,
          tracesSampleRate: 1.0,
          debug: true,
        })
      )
    })

    it('should skip initialization when no DSN is provided', () => {
      // Temporarily remove DSN
      const originalDsn = import.meta.env.VITE_SENTRY_DSN
      delete import.meta.env.VITE_SENTRY_DSN

      const { init } = require('@sentry/react')
      sentryService.initialize()

      expect(init).not.toHaveBeenCalled()
      expect(console.log).toHaveBeenCalledWith('Sentry initialization skipped (no DSN or test environment)')

      // Restore DSN
      import.meta.env.VITE_SENTRY_DSN = originalDsn
    })

    it('should skip initialization in test environment', () => {
      const { init } = require('@sentry/react')
      
      // VITEST is true, so it should skip
      sentryService.initialize()
      
      expect(init).not.toHaveBeenCalled()
      expect(console.log).toHaveBeenCalledWith('Sentry initialization skipped (no DSN or test environment)')
    })

    it('should capture exceptions with context', () => {
      const { captureException } = require('@sentry/react')
      const testError = new Error('Test error')
      
      sentryService.captureException(testError, {
        tags: { component: 'test' },
        extra: { action: 'test-action' },
        level: 'error',
      })

      expect(captureException).toHaveBeenCalledWith(testError, {
        tags: { component: 'test' },
        extra: { action: 'test-action' },
        level: 'error',
        fingerprint: undefined,
      })
    })

    it('should capture messages with context', () => {
      const { captureMessage } = require('@sentry/react')
      
      sentryService.captureMessage('Test message', 'warning', {
        tags: { source: 'test' },
        extra: { details: 'test-details' },
      })

      expect(captureMessage).toHaveBeenCalledWith('Test message', {
        level: 'warning',
        tags: { source: 'test' },
        extra: { details: 'test-details' },
        fingerprint: undefined,
      })
    })

    it('should add breadcrumbs', () => {
      const { addBreadcrumb } = require('@sentry/react')
      
      sentryService.addBreadcrumb('Test breadcrumb', 'navigation', 'info', { page: 'test' })

      expect(addBreadcrumb).toHaveBeenCalledWith({
        message: 'Test breadcrumb',
        category: 'navigation',
        level: 'info',
        data: { page: 'test' },
        timestamp: expect.any(Number),
      })
    })

    it('should update user context', () => {
      const { setUser } = require('@sentry/react')
      
      sentryService.updateUser({
        id: 'test-user',
        email: 'test@example.com',
        username: 'testuser',
        role: 'admin',
      })

      expect(setUser).toHaveBeenCalledWith({
        id: 'test-user',
        email: 'test@example.com',
        username: 'testuser',
        role: 'admin',
      })
    })

    it('should set custom context', () => {
      const { setContext } = require('@sentry/react')
      
      sentryService.setContext('test-context', { key: 'value' })

      expect(setContext).toHaveBeenCalledWith('test-context', { key: 'value' })
    })

    it('should capture drone-specific errors', () => {
      const { captureException } = require('@sentry/react')
      const testError = new Error('Drone communication error')
      
      sentryService.captureDroneError(testError, 'drone-001', 'takeoff', { altitude: 100 })

      expect(captureException).toHaveBeenCalledWith(testError, {
        tags: {
          component: 'drone',
          drone_id: 'drone-001',
          operation: 'takeoff',
        },
        extra: {
          drone_id: 'drone-001',
          operation: 'takeoff',
          altitude: 100,
        },
        fingerprint: ['drone-error-takeoff', 'drone-001'],
      })
    })

    it('should capture vision-specific errors', () => {
      const { captureException } = require('@sentry/react')
      const testError = new Error('Vision model inference failed')
      
      sentryService.captureVisionError(testError, 'model-001', 'inference', { accuracy: 0.85 })

      expect(captureException).toHaveBeenCalledWith(testError, {
        tags: {
          component: 'vision',
          model_id: 'model-001',
          operation: 'inference',
        },
        extra: {
          model_id: 'model-001',
          operation: 'inference',
          accuracy: 0.85,
        },
        fingerprint: ['vision-error-inference', 'model-001'],
      })
    })

    it('should capture API errors', () => {
      const { captureException } = require('@sentry/react')
      const testError = new Error('API request failed')
      
      sentryService.captureAPIError(testError, '/api/drones', 'GET', 500, { retry_count: 3 })

      expect(captureException).toHaveBeenCalledWith(testError, {
        tags: {
          component: 'api',
          endpoint: '/api/drones',
          method: 'GET',
          status_code: '500',
        },
        extra: {
          endpoint: '/api/drones',
          method: 'GET',
          status_code: 500,
          retry_count: 3,
        },
        fingerprint: ['api-error-GET', '/api/drones'],
      })
    })

    it('should start and finish transactions', () => {
      const mockTransaction = {
        setStatus: vi.fn(),
        finish: vi.fn(),
      }
      const { startTransaction } = require('@sentry/react')
      startTransaction.mockReturnValue(mockTransaction)
      
      const transaction = sentryService.startTransaction('test-transaction', 'function', 'Test function')

      expect(startTransaction).toHaveBeenCalledWith({
        name: 'test-transaction',
        op: 'function',
        description: 'Test function',
      })
      expect(transaction).toBe(mockTransaction)
    })

    it('should measure performance of synchronous functions', async () => {
      const mockTransaction = {
        setStatus: vi.fn(),
        finish: vi.fn(),
      }
      const { startTransaction } = require('@sentry/react')
      startTransaction.mockReturnValue(mockTransaction)
      
      const testFunction = vi.fn(() => 'result')
      const result = await sentryService.measurePerformance('test-measure', testFunction)

      expect(startTransaction).toHaveBeenCalledWith({
        name: 'test-measure',
        op: 'function',
        description: undefined,
      })
      expect(testFunction).toHaveBeenCalled()
      expect(result).toBe('result')
      expect(mockTransaction.setStatus).toHaveBeenCalledWith('ok')
      expect(mockTransaction.finish).toHaveBeenCalled()
    })

    it('should measure performance of asynchronous functions', async () => {
      const mockTransaction = {
        setStatus: vi.fn(),
        finish: vi.fn(),
      }
      const { startTransaction } = require('@sentry/react')
      startTransaction.mockReturnValue(mockTransaction)
      
      const testFunction = vi.fn(() => Promise.resolve('async-result'))
      const result = await sentryService.measurePerformance('test-async', testFunction)

      expect(testFunction).toHaveBeenCalled()
      expect(result).toBe('async-result')
      expect(mockTransaction.setStatus).toHaveBeenCalledWith('ok')
      expect(mockTransaction.finish).toHaveBeenCalled()
    })

    it('should handle errors in measured functions', async () => {
      const mockTransaction = {
        setStatus: vi.fn(),
        finish: vi.fn(),
      }
      const { startTransaction } = require('@sentry/react')
      startTransaction.mockReturnValue(mockTransaction)
      
      const testError = new Error('Function error')
      const testFunction = vi.fn(() => { throw testError })

      await expect(sentryService.measurePerformance('test-error', testFunction)).rejects.toThrow('Function error')
      
      expect(mockTransaction.setStatus).toHaveBeenCalledWith('internal_error')
      expect(mockTransaction.finish).toHaveBeenCalled()
    })

    it('should show user feedback dialog', () => {
      const { showReportDialog, lastEventId } = require('@sentry/react')
      lastEventId.mockReturnValue('test-event-id')
      
      sentryService.showUserFeedback({
        user: { name: 'Test User', email: 'test@example.com' }
      })

      expect(showReportDialog).toHaveBeenCalledWith({
        eventId: 'test-event-id',
        user: { name: 'Test User', email: 'test@example.com' },
        lang: 'ja',
        title: 'エラーレポート',
        subtitle: 'エラーに関する詳細情報をお聞かせください',
        subtitle2: 'お客様の情報は問題解決のためにのみ使用されます',
        labelName: 'お名前',
        labelEmail: 'メールアドレス',
        labelComments: 'コメント（何をしていた時にエラーが発生しましたか？）',
        labelClose: '閉じる',
        labelSubmit: '送信',
        errorGeneric: 'レポートの送信中にエラーが発生しました。',
        errorFormEntry: '一部の項目が無効です。確認してもう一度お試しください。',
        successMessage: 'フィードバックが送信されました。ありがとうございます！',
      })
    })
  })

  describe('Error Analytics Dashboard', () => {
    it('should render error analytics dashboard', () => {
      render(
        <TestWrapper>
          <ErrorAnalyticsDashboard />
        </TestWrapper>
      )

      expect(screen.getByText('エラー分析ダッシュボード')).toBeInTheDocument()
    })

    it('should show loading state initially', () => {
      render(
        <TestWrapper>
          <ErrorAnalyticsDashboard />
        </TestWrapper>
      )

      expect(screen.getByText('エラーデータを読み込み中...')).toBeInTheDocument()
    })

    it('should handle time range changes', async () => {
      render(
        <TestWrapper>
          <ErrorAnalyticsDashboard />
        </TestWrapper>
      )

      // Wait for initial load
      await waitFor(() => {
        expect(screen.queryByText('エラーデータを読み込み中...')).not.toBeInTheDocument()
      })

      const timeRangeSelect = screen.getByLabelText('期間')
      fireEvent.mouseDown(timeRangeSelect)
      
      const sevenDaysOption = screen.getByText('7日間')
      fireEvent.click(sevenDaysOption)

      // Should trigger data refetch
      expect(mockShowNotification).not.toHaveBeenCalledWith(expect.stringContaining('失敗'), 'error')
    })

    it('should export error data', async () => {
      // Mock URL.createObjectURL and document.createElement
      const mockCreateObjectURL = vi.fn(() => 'mock-url')
      const mockRevokeObjectURL = vi.fn()
      const mockClick = vi.fn()
      const mockAppendChild = vi.fn()
      const mockRemoveChild = vi.fn()

      Object.defineProperty(window, 'URL', {
        value: {
          createObjectURL: mockCreateObjectURL,
          revokeObjectURL: mockRevokeObjectURL,
        },
      })

      const mockAnchor = {
        href: '',
        download: '',
        click: mockClick,
      }

      vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(mockAppendChild)
      vi.spyOn(document.body, 'removeChild').mockImplementation(mockRemoveChild)

      render(
        <TestWrapper>
          <ErrorAnalyticsDashboard />
        </TestWrapper>
      )

      // Wait for component to load
      await waitFor(() => {
        expect(screen.queryByText('エラーデータを読み込み中...')).not.toBeInTheDocument()
      })

      const exportButton = screen.getByLabelText('エクスポート')
      fireEvent.click(exportButton)

      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('mock-url')
      expect(mockShowNotification).toHaveBeenCalledWith('エラーデータをエクスポートしました', 'success')
    })

    it('should handle refresh action', async () => {
      render(
        <TestWrapper>
          <ErrorAnalyticsDashboard />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.queryByText('エラーデータを読み込み中...')).not.toBeInTheDocument()
      })

      const refreshButton = screen.getByLabelText('更新')
      fireEvent.click(refreshButton)

      // Should not show error notification
      expect(mockShowNotification).not.toHaveBeenCalledWith(expect.stringContaining('失敗'), 'error')
    })
  })

  describe('Advanced Log Analyzer', () => {
    it('should render advanced log analyzer', () => {
      render(
        <TestWrapper>
          <AdvancedLogAnalyzer />
        </TestWrapper>
      )

      expect(screen.getByText('高度ログアナライザー')).toBeInTheDocument()
    })

    it('should show loading state initially', () => {
      render(
        <TestWrapper>
          <AdvancedLogAnalyzer />
        </TestWrapper>
      )

      expect(screen.getByText('ログデータを読み込み中...')).toBeInTheDocument()
    })

    it('should handle auto analysis toggle', async () => {
      render(
        <TestWrapper>
          <AdvancedLogAnalyzer />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.queryByText('ログデータを読み込み中...')).not.toBeInTheDocument()
      })

      const autoAnalysisSwitch = screen.getByLabelText('自動分析')
      expect(autoAnalysisSwitch).toBeChecked()

      fireEvent.click(autoAnalysisSwitch)
      expect(autoAnalysisSwitch).not.toBeChecked()
    })

    it('should handle analysis depth changes', async () => {
      render(
        <TestWrapper>
          <AdvancedLogAnalyzer />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.queryByText('ログデータを読み込み中...')).not.toBeInTheDocument()
      })

      const analysisDepthSlider = screen.getByRole('slider')
      expect(analysisDepthSlider).toHaveValue('2') // Default depth

      fireEvent.change(analysisDepthSlider, { target: { value: '3' } })
      expect(analysisDepthSlider).toHaveValue('3')
    })

    it('should trigger manual analysis', async () => {
      render(
        <TestWrapper>
          <AdvancedLogAnalyzer />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.queryByText('ログデータを読み込み中...')).not.toBeInTheDocument()
      })

      const analysisButton = screen.getByLabelText('分析実行')
      fireEvent.click(analysisButton)

      expect(mockShowNotification).toHaveBeenCalledWith('ログ分析を開始します...', 'info')
    })

    it('should export analysis results', async () => {
      // Mock URL.createObjectURL and document.createElement
      const mockCreateObjectURL = vi.fn(() => 'mock-url')
      const mockRevokeObjectURL = vi.fn()
      const mockClick = vi.fn()

      Object.defineProperty(window, 'URL', {
        value: {
          createObjectURL: mockCreateObjectURL,
          revokeObjectURL: mockRevokeObjectURL,
        },
      })

      const mockAnchor = {
        href: '',
        download: '',
        click: mockClick,
      }

      vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor as any)

      render(
        <TestWrapper>
          <AdvancedLogAnalyzer />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.queryByText('ログデータを読み込み中...')).not.toBeInTheDocument()
      })

      // Wait for auto analysis to complete
      await waitFor(() => {
        expect(screen.queryByText('パターン分析中...')).not.toBeInTheDocument()
      }, { timeout: 10000 })

      const exportButton = screen.getByLabelText('エクスポート')
      fireEvent.click(exportButton)

      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('mock-url')
      expect(mockShowNotification).toHaveBeenCalledWith('分析結果をエクスポートしました', 'success')
    })

    it('should switch between analysis tabs', async () => {
      render(
        <TestWrapper>
          <AdvancedLogAnalyzer />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.queryByText('ログデータを読み込み中...')).not.toBeInTheDocument()
      })

      // Default tab should be log trend
      const patternTab = screen.getByText('パターン分析')
      fireEvent.click(patternTab)

      // Should show pattern analysis content
      await waitFor(() => {
        expect(screen.getByText('検出されたパターン')).toBeInTheDocument()
      })

      const anomalyTab = screen.getByText('異常検知')
      fireEvent.click(anomalyTab)

      // Should show anomaly detection content
      await waitFor(() => {
        expect(screen.getByText('検出された異常')).toBeInTheDocument()
      })
    })
  })

  describe('Error Boundary Integration', () => {
    it('should capture React errors automatically', () => {
      const { captureException } = require('@sentry/react')
      
      // Mock a React component that throws an error
      const ErrorComponent = () => {
        throw new Error('React component error')
      }

      const originalConsoleError = console.error
      console.error = vi.fn() // Suppress error boundary logs

      try {
        render(
          <TestWrapper>
            <ErrorComponent />
          </TestWrapper>
        )
      } catch (error) {
        // Expected to throw
      }

      console.error = originalConsoleError

      // Should capture the React error
      expect(captureException).toHaveBeenCalled()
    })
  })

  describe('Performance Monitoring Integration', () => {
    it('should track component performance with Sentry profiler', () => {
      const { withProfiler } = require('@sentry/react')
      
      const TestComponent = () => <div>Test Component</div>
      const ProfiledComponent = sentryService.withPerformance(TestComponent, 'TestComponent')

      expect(withProfiler).toHaveBeenCalledWith(TestComponent, { name: 'TestComponent' })
    })
  })
})

describe('Error Tracking Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should filter out browser extension errors', () => {
    const { init } = require('@sentry/react')
    
    // Initialize Sentry to get the beforeSend function
    sentryService.initialize()
    
    const initCall = init.mock.calls[init.mock.calls.length - 1]
    const config = initCall[0]
    const beforeSend = config.beforeSend

    // Test browser extension URL filtering
    const extensionEvent = {
      request: { url: 'chrome-extension://abc123/script.js' }
    }

    expect(beforeSend(extensionEvent)).toBeNull()

    const mozExtensionEvent = {
      request: { url: 'moz-extension://abc123/script.js' }
    }

    expect(beforeSend(mozExtensionEvent)).toBeNull()
  })

  it('should filter out development errors in non-production', () => {
    const { init } = require('@sentry/react')
    
    // Set non-production environment
    const originalProd = import.meta.env.PROD
    import.meta.env.PROD = false
    
    sentryService.initialize()
    
    const initCall = init.mock.calls[init.mock.calls.length - 1]
    const config = initCall[0]
    const beforeSend = config.beforeSend

    // Test development error filtering
    const chunkError = {
      message: 'ChunkLoadError: Loading chunk 5 failed'
    }

    expect(beforeSend(chunkError)).toBeNull()

    const loadingError = {
      exception: {
        values: [{
          value: 'Loading chunk failed'
        }]
      }
    }

    expect(beforeSend(loadingError)).toBeNull()

    // Restore original value
    import.meta.env.PROD = originalProd
  })

  it('should pass through valid errors', () => {
    const { init } = require('@sentry/react')
    
    sentryService.initialize()
    
    const initCall = init.mock.calls[init.mock.calls.length - 1]
    const config = initCall[0]
    const beforeSend = config.beforeSend

    const validError = {
      message: 'Valid application error',
      request: { url: 'https://myapp.com/page' }
    }

    expect(beforeSend(validError)).toBe(validError)
  })

  it('should filter out short transactions', () => {
    const { init } = require('@sentry/react')
    
    sentryService.initialize()
    
    const initCall = init.mock.calls[init.mock.calls.length - 1]
    const config = initCall[0]
    const beforeSendTransaction = config.beforeSendTransaction

    const shortTransaction = {
      start_timestamp: 1000,
      timestamp: 1000.05 // 50ms duration
    }

    expect(beforeSendTransaction(shortTransaction)).toBeNull()

    const longTransaction = {
      start_timestamp: 1000,
      timestamp: 1000.5 // 500ms duration
    }

    expect(beforeSendTransaction(longTransaction)).toBe(longTransaction)
  })
})