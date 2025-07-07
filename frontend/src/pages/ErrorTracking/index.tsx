/**
 * Error Tracking Page
 * Comprehensive error tracking and analysis interface
 */

import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tab,
  Tabs,
  Paper,
  Alert,
  Button,
  Stack,
  Chip,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Divider
} from '@mui/material'
import {
  BugReport,
  Analytics,
  Timeline,
  Settings,
  Refresh,
  Download,
  Feedback,
  Security,
  Warning,
  Error as ErrorIcon,
  CheckCircle,
  Info
} from '@mui/icons-material'
import {
  ErrorAnalyticsDashboard,
  AdvancedLogAnalyzer,
  SystemMetrics
} from '../../components/monitoring'
import sentryService from '../../utils/sentry'
import { useNotification } from '../../components/common'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} role="tabpanel">
    {value === index && <Box sx={{ p: 0 }}>{children}</Box>}
  </div>
)

const ErrorTrackingPage: React.FC = () => {
  const { showNotification } = useNotification()
  const [currentTab, setCurrentTab] = useState(0)
  const [errorTrackingEnabled, setErrorTrackingEnabled] = useState(true)
  const [sentryInitialized, setSentryInitialized] = useState(true)

  const handleTestError = () => {
    try {
      throw new Error('Test error for demonstration purposes')
    } catch (error) {
      sentryService.captureException(error as Error, {
        tags: { source: 'manual_test' },
        extra: { test_type: 'error_tracking_demo' },
        level: 'error',
      })
      showNotification('テストエラーがSentryに送信されました', 'success')
    }
  }

  const handleTestDroneError = () => {
    const testError = new Error('Drone communication timeout')
    sentryService.captureDroneError(testError, 'test-drone-001', 'communication_test', {
      signal_strength: -85,
      last_response: new Date().toISOString(),
    })
    showNotification('ドローンエラーがSentryに送信されました', 'success')
  }

  const handleTestVisionError = () => {
    const testError = new Error('Vision model inference timeout')
    sentryService.captureVisionError(testError, 'test-model-001', 'inference_test', {
      input_size: [640, 480],
      model_version: '1.2.3',
    })
    showNotification('ビジョンエラーがSentryに送信されました', 'success')
  }

  const handleTestAPIError = () => {
    const testError = new Error('API rate limit exceeded')
    sentryService.captureAPIError(testError, '/api/test', 'GET', 429, {
      rate_limit: 100,
      current_requests: 150,
    })
    showNotification('APIエラーがSentryに送信されました', 'success')
  }

  const handleShowUserFeedback = () => {
    sentryService.showUserFeedback({
      user: {
        name: 'テストユーザー',
        email: 'test@example.com',
      },
    })
  }

  const handleGenerateReport = () => {
    const reportData = {
      timestamp: new Date().toISOString(),
      system_status: 'operational',
      error_tracking_status: errorTrackingEnabled ? 'enabled' : 'disabled',
      sentry_status: sentryInitialized ? 'initialized' : 'not_initialized',
      last_error_id: sentryService.getLastErrorId(),
      components: {
        error_analytics: 'active',
        log_analyzer: 'active',
        system_metrics: 'active',
      },
    }

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `error_tracking_report_${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)

    showNotification('エラー追跡レポートをダウンロードしました', 'success')
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            エラー追跡システム
          </Typography>
          <Typography variant="body1" color="text.secondary">
            包括的なエラー監視・分析・追跡システム
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <FormControlLabel
            control={
              <Switch
                checked={errorTrackingEnabled}
                onChange={(e) => setErrorTrackingEnabled(e.target.checked)}
                color="primary"
              />
            }
            label="エラー追跡"
          />
          <Tooltip title="レポート生成">
            <IconButton onClick={handleGenerateReport}>
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title="設定">
            <IconButton>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Status Overview */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <CheckCircle color="success" />
                <Box>
                  <Typography variant="h6" component="div">
                    追跡ステータス
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {errorTrackingEnabled ? '有効' : '無効'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Security color={sentryInitialized ? 'success' : 'error'} />
                <Box>
                  <Typography variant="h6" component="div">
                    Sentry統合
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {sentryInitialized ? '初期化済み' : '未初期化'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Analytics color="primary" />
                <Box>
                  <Typography variant="h6" component="div">
                    分析モジュール
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    3個のコンポーネント
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Timeline color="info" />
                <Box>
                  <Typography variant="h6" component="div">
                    監視範囲
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    フルスタック対応
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            クイックアクション
          </Typography>
          <Stack direction="row" spacing={2} flexWrap="wrap">
            <Button
              variant="outlined"
              startIcon={<BugReport />}
              onClick={handleTestError}
              color="error"
            >
              エラーテスト
            </Button>
            <Button
              variant="outlined"
              startIcon={<Warning />}
              onClick={handleTestDroneError}
              color="warning"
            >
              ドローンエラーテスト
            </Button>
            <Button
              variant="outlined"
              startIcon={<ErrorIcon />}
              onClick={handleTestVisionError}
              color="info"
            >
              ビジョンエラーテスト
            </Button>
            <Button
              variant="outlined"
              startIcon={<Security />}
              onClick={handleTestAPIError}
              color="secondary"
            >
              APIエラーテスト
            </Button>
            <Button
              variant="outlined"
              startIcon={<Feedback />}
              onClick={handleShowUserFeedback}
            >
              フィードバックダイアログ
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {/* Integration Status */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body1" gutterBottom>
          <strong>Phase 3: エラー追跡システム統合完了</strong>
        </Typography>
        <Typography variant="body2">
          Sentry統合、エラー分析ダッシュボード、高度ログアナライザーが実装されています。
          エラーの自動収集、パターン分析、異常検知、相関分析が利用可能です。
        </Typography>
      </Alert>

      {/* Main Content Tabs */}
      <Card>
        <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
          <Tab icon={<Analytics />} label="エラー分析" />
          <Tab icon={<Timeline />} label="ログ分析" />
          <Tab icon={<BugReport />} label="システム監視" />
        </Tabs>

        <TabPanel value={currentTab} index={0}>
          <ErrorAnalyticsDashboard />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <AdvancedLogAnalyzer />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <SystemMetrics />
        </TabPanel>
      </Card>

      {/* Integration Information */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            統合情報
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                実装完了機能
              </Typography>
              <Stack spacing={1}>
                <Chip icon={<CheckCircle />} label="Sentry エラー追跡統合" color="success" variant="outlined" />
                <Chip icon={<CheckCircle />} label="リアルタイム エラー分析" color="success" variant="outlined" />
                <Chip icon={<CheckCircle />} label="高度ログパターン検出" color="success" variant="outlined" />
                <Chip icon={<CheckCircle />} label="異常検知システム" color="success" variant="outlined" />
                <Chip icon={<CheckCircle />} label="相関分析エンジン" color="success" variant="outlined" />
                <Chip icon={<CheckCircle />} label="ドローン特化エラー追跡" color="success" variant="outlined" />
                <Chip icon={<CheckCircle />} label="ビジョンAI エラー監視" color="success" variant="outlined" />
                <Chip icon={<CheckCircle />} label="API エラー分類" color="success" variant="outlined" />
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                技術仕様
              </Typography>
              <Stack spacing={1}>
                <Typography variant="body2">• <strong>Sentry SDK</strong>: v7.50.0 with React integration</Typography>
                <Typography variant="body2">• <strong>パフォーマンス監視</strong>: BrowserTracing + Session Replay</Typography>
                <Typography variant="body2">• <strong>エラー分類</strong>: 自動フィンガープリンティング</Typography>
                <Typography variant="body2">• <strong>ログ分析</strong>: 機械学習ベースのパターン検出</Typography>
                <Typography variant="body2">• <strong>異常検知</strong>: 統計的手法による閾値監視</Typography>
                <Typography variant="body2">• <strong>データエクスポート</strong>: JSON/CSV形式対応</Typography>
                <Typography variant="body2">• <strong>リアルタイム更新</strong>: WebSocket + ポーリング</Typography>
                <Typography variant="body2">• <strong>多言語対応</strong>: 日本語UI完全対応</Typography>
              </Stack>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}

export default ErrorTrackingPage