import React, { Component, ReactNode } from 'react'
import {
  Box,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Chip,
  Alert,
  Link,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  ErrorOutline as ErrorOutlineIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Home as HomeIcon,
  BugReport as BugReportIcon,
  ContentCopy as CopyIcon,
  Send as SendIcon,
} from '@mui/icons-material'

import { Button, StatusBadge } from '../index'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
  errorId: string | null
  retryCount: number
  lastErrorTime: number
}

// Error classification system
interface ErrorCategory {
  type: 'network' | 'runtime' | 'chunk' | 'permission' | 'unknown'
  severity: 'low' | 'medium' | 'high' | 'critical'
  recoverable: boolean
  userMessage: string
}

const classifyError = (error: Error): ErrorCategory => {
  const message = error.message.toLowerCase()
  const stack = error.stack?.toLowerCase() || ''

  // Network errors
  if (message.includes('fetch') || message.includes('network') || message.includes('load failed')) {
    return {
      type: 'network',
      severity: 'medium',
      recoverable: true,
      userMessage: 'ネットワーク接続に問題があります。インターネット接続を確認してください。',
    }
  }

  // Chunk loading errors (common in SPA)
  if (message.includes('chunk') || message.includes('loading css') || message.includes('loading module')) {
    return {
      type: 'chunk',
      severity: 'high',
      recoverable: true,
      userMessage: 'アプリケーションの更新中にエラーが発生しました。ページを再読み込みしてください。',
    }
  }

  // Permission errors
  if (message.includes('permission') || message.includes('forbidden') || message.includes('unauthorized')) {
    return {
      type: 'permission',
      severity: 'high',
      recoverable: false,
      userMessage: '操作権限がありません。ログインを確認するか、管理者にお問い合わせください。',
    }
  }

  // Runtime errors
  if (stack.includes('at ') || message.includes('undefined') || message.includes('null')) {
    return {
      type: 'runtime',
      severity: 'medium',
      recoverable: true,
      userMessage: 'プログラムの実行中にエラーが発生しました。しばらく待ってから再試行してください。',
    }
  }

  return {
    type: 'unknown',
    severity: 'high',
    recoverable: true,
    userMessage: '予期しないエラーが発生しました。問題が続く場合は管理者にお問い合わせください。',
  }
}

// Error reporting service
class ErrorReportingService {
  private static instance: ErrorReportingService
  private reports: Array<{ id: string; error: Error; errorInfo: React.ErrorInfo; timestamp: number; userAgent: string }> = []

  static getInstance(): ErrorReportingService {
    if (!ErrorReportingService.instance) {
      ErrorReportingService.instance = new ErrorReportingService()
    }
    return ErrorReportingService.instance
  }

  reportError(error: Error, errorInfo: React.ErrorInfo): string {
    const errorId = `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    const report = {
      id: errorId,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      errorInfo: {
        componentStack: errorInfo.componentStack,
      },
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: localStorage.getItem('userId') || 'anonymous',
    }

    // Store locally
    try {
      const existingReports = JSON.parse(localStorage.getItem('errorReports') || '[]')
      const updatedReports = [...existingReports, report].slice(-50) // Keep last 50 errors
      localStorage.setItem('errorReports', JSON.stringify(updatedReports))
    } catch (e) {
      console.warn('Failed to store error report locally:', e)
    }

    // In a real app, send to logging service
    console.error('Error Report:', report)
    
    return errorId
  }

  getStoredReports() {
    try {
      return JSON.parse(localStorage.getItem('errorReports') || '[]')
    } catch {
      return []
    }
  }
}

export class ErrorBoundary extends Component<Props, State> {
  private errorReporting = ErrorReportingService.getInstance()

  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: 0,
      lastErrorTime: 0,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      lastErrorTime: Date.now(),
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const errorId = this.errorReporting.reportError(error, errorInfo)
    
    this.setState({
      errorInfo,
      errorId,
    })

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo)

    console.group('🐛 ErrorBoundary Error Report')
    console.error('Error:', error)
    console.error('Error Info:', errorInfo)
    console.error('Error ID:', errorId)
    console.groupEnd()
  }

  handleRetry = () => {
    const now = Date.now()
    const timeSinceLastError = now - this.state.lastErrorTime
    
    // Prevent rapid retries
    if (timeSinceLastError < 1000) {
      return
    }

    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: prevState.retryCount + 1,
    }))
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  handleCopyError = async () => {
    if (!this.state.error) return

    const errorText = `
Error: ${this.state.error.message}
Error ID: ${this.state.errorId}
Stack: ${this.state.error.stack}
Component Stack: ${this.state.errorInfo?.componentStack}
Timestamp: ${new Date(this.state.lastErrorTime).toISOString()}
URL: ${window.location.href}
User Agent: ${navigator.userAgent}
    `.trim()

    try {
      await navigator.clipboard.writeText(errorText)
      // Show success message
    } catch (e) {
      console.warn('Failed to copy to clipboard:', e)
    }
  }

  handleSendReport = () => {
    // In a real app, this would send the error to support
    const reports = this.errorReporting.getStoredReports()
    console.log('Sending error reports:', reports)
    alert('エラーレポートが送信されました。（デモ機能）')
  }

  render() {
    if (this.state.hasError && this.state.error) {
      const errorCategory = classifyError(this.state.error)
      
      if (this.props.fallback) {
        return this.props.fallback
      }

      const severityColors = {
        low: 'info',
        medium: 'warning', 
        high: 'error',
        critical: 'error',
      } as const

      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '60vh',
            p: 3,
            backgroundColor: 'grey.50',
          }}
        >
          <Paper
            elevation={6}
            sx={{
              p: 4,
              maxWidth: 600,
              width: '100%',
              borderRadius: 2,
            }}
          >
            {/* Header */}
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <ErrorOutlineIcon
                sx={{
                  fontSize: 72,
                  color: 'error.main',
                  mb: 2,
                }}
              />
              
              <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
                申し訳ございません
              </Typography>
              
              <Typography variant="h6" color="text.secondary" paragraph>
                アプリケーションで問題が発生しました
              </Typography>
            </Box>

            {/* Error Classification */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <StatusBadge
                  status={errorCategory.severity === 'critical' ? 'error' : 'warning'}
                  variant="chip"
                  size="small"
                />
                <Chip
                  label={errorCategory.type.toUpperCase()}
                  color={severityColors[errorCategory.severity]}
                  size="small"
                  variant="outlined"
                />
                {this.state.errorId && (
                  <Chip
                    label={`ID: ${this.state.errorId.slice(-8)}`}
                    size="small"
                    variant="outlined"
                  />
                )}
              </Box>
              
              <Alert severity={severityColors[errorCategory.severity]} sx={{ mb: 2 }}>
                <Typography variant="body1">
                  {errorCategory.userMessage}
                </Typography>
              </Alert>
            </Box>

            {/* Retry Info */}
            {this.state.retryCount > 0 && (
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  再試行回数: {this.state.retryCount}回
                  {this.state.retryCount >= 3 && ' - 繰り返し発生する場合は管理者にお問い合わせください'}
                </Typography>
              </Alert>
            )}

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
              {errorCategory.recoverable && (
                <Button
                  variant="contained"
                  startIcon={<RefreshIcon />}
                  onClick={this.handleRetry}
                  color="primary"
                >
                  再試行
                </Button>
              )}
              
              <Button
                variant="outlined"
                startIcon={<HomeIcon />}
                onClick={this.handleGoHome}
              >
                ホームに戻る
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => window.location.reload()}
              >
                ページ再読み込み
              </Button>
            </Box>

            {/* Support Actions */}
            <Box sx={{ display: 'flex', gap: 1, mb: 3, justifyContent: 'center' }}>
              <Tooltip title="エラー情報をコピー">
                <IconButton onClick={this.handleCopyError} size="small">
                  <CopyIcon />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="エラーレポートを送信">
                <IconButton onClick={this.handleSendReport} size="small">
                  <SendIcon />
                </IconButton>
              </Tooltip>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {/* Technical Details Accordion */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <BugReportIcon fontSize="small" />
                  <Typography variant="subtitle2">技術的な詳細</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {/* Basic Error Info */}
                  <Box>
                    <Typography variant="caption" color="text.secondary" gutterBottom>
                      エラーメッセージ:
                    </Typography>
                    <Typography variant="body2" fontFamily="monospace" sx={{ 
                      backgroundColor: 'grey.100', 
                      p: 1, 
                      borderRadius: 1,
                      wordBreak: 'break-all',
                    }}>
                      {this.state.error.message}
                    </Typography>
                  </Box>

                  {/* Error ID and Timestamp */}
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        エラーID:
                      </Typography>
                      <Typography variant="body2" fontFamily="monospace">
                        {this.state.errorId}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        発生時刻:
                      </Typography>
                      <Typography variant="body2">
                        {new Date(this.state.lastErrorTime).toLocaleString('ja-JP')}
                      </Typography>
                    </Box>
                  </Box>

                  {/* Stack Trace (Development) */}
                  {process.env.NODE_ENV === 'development' && this.state.error.stack && (
                    <Box>
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        スタックトレース:
                      </Typography>
                      <Typography 
                        variant="caption" 
                        component="pre" 
                        sx={{ 
                          backgroundColor: 'grey.100',
                          p: 2,
                          borderRadius: 1,
                          fontSize: '0.75rem',
                          overflow: 'auto',
                          maxHeight: 200,
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        {this.state.error.stack}
                      </Typography>
                    </Box>
                  )}

                  {/* Component Stack (Development) */}
                  {process.env.NODE_ENV === 'development' && this.state.errorInfo?.componentStack && (
                    <Box>
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        コンポーネントスタック:
                      </Typography>
                      <Typography 
                        variant="caption" 
                        component="pre" 
                        sx={{ 
                          backgroundColor: 'grey.100',
                          p: 2,
                          borderRadius: 1,
                          fontSize: '0.75rem',
                          overflow: 'auto',
                          maxHeight: 200,
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        {this.state.errorInfo.componentStack}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>

            {/* Footer */}
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                問題が解決しない場合は、{' '}
                <Link href="mailto:support@example.com" color="primary">
                  サポートチーム
                </Link>
                {' '}までお問い合わせください。
              </Typography>
            </Box>
          </Paper>
        </Box>
      )
    }

    return this.props.children
  }
}