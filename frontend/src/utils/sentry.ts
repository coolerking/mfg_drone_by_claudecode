/**
 * Sentry Error Tracking Integration
 * Provides comprehensive error tracking, performance monitoring, and user feedback collection
 */

import * as Sentry from '@sentry/react'
import { BrowserTracing } from '@sentry/tracing'
import { CaptureConsole } from '@sentry/integrations'

// Error tracking configuration
interface SentryConfig {
  dsn: string
  environment: string
  release: string
  sampleRate: number
  tracesSampleRate: number
  replaysSessionSampleRate: number
  replaysOnErrorSampleRate: number
}

// Environment configuration
const SENTRY_CONFIG: SentryConfig = {
  dsn: import.meta.env.VITE_SENTRY_DSN || '',
  environment: import.meta.env.MODE || 'development',
  release: import.meta.env.VITE_APP_VERSION || '1.0.0',
  sampleRate: import.meta.env.PROD ? 0.1 : 1.0, // 10% in production, 100% in development
  tracesSampleRate: import.meta.env.PROD ? 0.1 : 1.0,
  replaysSessionSampleRate: 0.1, // 10% of sessions will be recorded
  replaysOnErrorSampleRate: 1.0, // 100% of sessions with errors will be recorded
}

/**
 * Initialize Sentry error tracking
 */
export const initializeSentry = (): void => {
  // Only initialize if DSN is provided and not in test environment
  if (!SENTRY_CONFIG.dsn || import.meta.env.VITEST) {
    console.log('Sentry initialization skipped (no DSN or test environment)')
    return
  }

  Sentry.init({
    dsn: SENTRY_CONFIG.dsn,
    environment: SENTRY_CONFIG.environment,
    release: SENTRY_CONFIG.release,
    
    // Performance monitoring
    integrations: [
      new BrowserTracing({
        // Set up automatic route change tracking
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          React.useEffect,
          React.useLocation,
          React.useNavigationType,
          React.createRoutesFromChildren,
          React.matchRoutes
        ),
        // Track user interactions
        idleTimeout: 5000,
        markBackgroundTransactions: false,
        startTransactionOnLocationChange: true,
        startTransactionOnPageLoad: true,
      }),
      
      // Console integration for capturing console errors
      new CaptureConsole({
        levels: ['error', 'warn']
      }),
    ],

    // Sample rates
    sampleRate: SENTRY_CONFIG.sampleRate,
    tracesSampleRate: SENTRY_CONFIG.tracesSampleRate,

    // Session Replay
    replaysSessionSampleRate: SENTRY_CONFIG.replaysSessionSampleRate,
    replaysOnErrorSampleRate: SENTRY_CONFIG.replaysOnErrorSampleRate,

    // Performance monitoring
    enableTracing: true,

    // Debugging
    debug: !import.meta.env.PROD,
    
    // Before send hook for filtering and enriching events
    beforeSend(event) {
      // Don't send events from browser extensions
      if (event.request?.url?.includes('chrome-extension://') || 
          event.request?.url?.includes('moz-extension://')) {
        return null
      }

      // Filter out common development errors
      if (!import.meta.env.PROD) {
        const message = event.message || event.exception?.values?.[0]?.value || ''
        if (message.includes('ChunkLoadError') || 
            message.includes('Loading chunk') ||
            message.includes('ResizeObserver loop limit exceeded')) {
          return null
        }
      }

      return event
    },

    // Before send transaction hook
    beforeSendTransaction(transaction) {
      // Don't track very short transactions
      if (transaction.start_timestamp && transaction.timestamp) {
        const duration = transaction.timestamp - transaction.start_timestamp
        if (duration < 0.1) { // Less than 100ms
          return null
        }
      }

      return transaction
    },

    // Initial scope configuration
    initialScope: {
      tags: {
        component: 'frontend',
        framework: 'react',
        bundler: 'vite',
      },
      contexts: {
        app: {
          name: 'MFG Drone Frontend',
          version: SENTRY_CONFIG.release,
        },
        browser: {
          name: navigator.userAgent,
        }
      }
    },

    // Transport options
    transport: Sentry.makeBrowserOfflineTransport(Sentry.makeFetchTransport),
    
    // Offline support
    transportOptions: {
      // Buffer requests when offline
      bufferSize: 30,
    },

    // Security options
    allowUrls: [
      // Only allow errors from our domain(s)
      /^https?:\/\/[^/]+\.drone-system\.com/,
      /^https?:\/\/[^/]+\.localhost/,
      /^https?:\/\/127\.0\.0\.1/,
      /^https?:\/\/0\.0\.0\.0/,
    ],

    // Ignored errors
    ignoreErrors: [
      // Ignore browser extension errors
      'ResizeObserver loop limit exceeded',
      'Non-Error exception captured',
      'Non-Error promise rejection captured',
      // Ignore network errors that are not actionable
      'NetworkError',
      'Failed to fetch',
      'Load failed',
      // Ignore common browser quirks
      'Script error.',
      'Javascript error: Script error. on line 0',
    ],
  })

  // Set up user context if available
  updateUserContext()

  console.log(`Sentry initialized for ${SENTRY_CONFIG.environment} environment`)
}

/**
 * Update user context for error tracking
 */
export const updateUserContext = (user?: {
  id?: string
  email?: string
  username?: string
  role?: string
}): void => {
  Sentry.setUser({
    id: user?.id,
    email: user?.email,
    username: user?.username,
    role: user?.role,
  })
}

/**
 * Set custom context for error tracking
 */
export const setErrorContext = (key: string, context: Record<string, any>): void => {
  Sentry.setContext(key, context)
}

/**
 * Add breadcrumb for debugging
 */
export const addBreadcrumb = (
  message: string, 
  category: string = 'custom',
  level: 'debug' | 'info' | 'warning' | 'error' | 'fatal' = 'info',
  data?: Record<string, any>
): void => {
  Sentry.addBreadcrumb({
    message,
    category,
    level,
    data,
    timestamp: Date.now() / 1000,
  })
}

/**
 * Capture exception with additional context
 */
export const captureException = (
  error: Error,
  context?: {
    tags?: Record<string, string>
    extra?: Record<string, any>
    level?: 'error' | 'warning' | 'info' | 'debug'
    fingerprint?: string[]
  }
): string => {
  return Sentry.captureException(error, {
    tags: context?.tags,
    extra: context?.extra,
    level: context?.level || 'error',
    fingerprint: context?.fingerprint,
  })
}

/**
 * Capture message with context
 */
export const captureMessage = (
  message: string,
  level: 'error' | 'warning' | 'info' | 'debug' = 'info',
  context?: {
    tags?: Record<string, string>
    extra?: Record<string, any>
    fingerprint?: string[]
  }
): string => {
  return Sentry.captureMessage(message, {
    level,
    tags: context?.tags,
    extra: context?.extra,
    fingerprint: context?.fingerprint,
  })
}

/**
 * Start a performance transaction
 */
export const startTransaction = (
  name: string,
  op: string,
  description?: string
): Sentry.Transaction => {
  return Sentry.startTransaction({
    name,
    op,
    description,
  })
}

/**
 * Measure function performance
 */
export const measurePerformance = <T>(
  name: string,
  fn: () => T | Promise<T>,
  op: string = 'function'
): Promise<T> => {
  const transaction = startTransaction(name, op)
  
  try {
    const result = fn()
    
    if (result instanceof Promise) {
      return result
        .then((value) => {
          transaction.setStatus('ok')
          transaction.finish()
          return value
        })
        .catch((error) => {
          transaction.setStatus('internal_error')
          transaction.finish()
          throw error
        })
    } else {
      transaction.setStatus('ok')
      transaction.finish()
      return Promise.resolve(result)
    }
  } catch (error) {
    transaction.setStatus('internal_error')
    transaction.finish()
    throw error
  }
}

/**
 * Drone-specific error tracking
 */
export const capturedroneError = (
  error: Error,
  droneId: string,
  operation: string,
  additionalData?: Record<string, any>
): string => {
  return captureException(error, {
    tags: {
      component: 'drone',
      drone_id: droneId,
      operation,
    },
    extra: {
      drone_id: droneId,
      operation,
      ...additionalData,
    },
    fingerprint: [`drone-error-${operation}`, droneId],
  })
}

/**
 * Vision/AI-specific error tracking
 */
export const captureVisionError = (
  error: Error,
  modelId: string,
  operation: string,
  additionalData?: Record<string, any>
): string => {
  return captureException(error, {
    tags: {
      component: 'vision',
      model_id: modelId,
      operation,
    },
    extra: {
      model_id: modelId,
      operation,
      ...additionalData,
    },
    fingerprint: [`vision-error-${operation}`, modelId],
  })
}

/**
 * API error tracking
 */
export const captureAPIError = (
  error: Error,
  endpoint: string,
  method: string,
  statusCode?: number,
  additionalData?: Record<string, any>
): string => {
  return captureException(error, {
    tags: {
      component: 'api',
      endpoint,
      method,
      status_code: statusCode?.toString(),
    },
    extra: {
      endpoint,
      method,
      status_code: statusCode,
      ...additionalData,
    },
    fingerprint: [`api-error-${method}`, endpoint],
  })
}

/**
 * Performance monitoring for React components
 */
export const withSentryPerformance = <P extends object>(
  Component: React.ComponentType<P>,
  componentName: string
): React.ComponentType<P> => {
  return Sentry.withProfiler(Component, { name: componentName })
}

/**
 * Get last error ID for user feedback
 */
export const getLastErrorId = (): string | undefined => {
  return Sentry.lastEventId()
}

/**
 * Show user feedback dialog
 */
export const showUserFeedback = (options?: {
  eventId?: string
  user?: { name?: string; email?: string }
}): void => {
  const eventId = options?.eventId || getLastErrorId()
  if (eventId) {
    Sentry.showReportDialog({
      eventId,
      user: options?.user,
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
  }
}

/**
 * Cleanup Sentry (for testing)
 */
export const cleanup = (): void => {
  Sentry.getCurrentHub().getClient()?.close()
}

// Export Sentry for direct access if needed
export { Sentry }

// Default export
export default {
  initialize: initializeSentry,
  updateUser: updateUserContext,
  setContext: setErrorContext,
  addBreadcrumb,
  captureException,
  captureMessage,
  startTransaction,
  measurePerformance,
  captureDroneError: capturedroneError,
  captureVisionError,
  captureAPIError,
  withPerformance: withSentryPerformance,
  getLastErrorId,
  showUserFeedback,
  cleanup,
}