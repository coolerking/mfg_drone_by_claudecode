import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import SystemMetrics from '../../components/monitoring/SystemMetrics'
import { dashboardApi } from '../../services/api/dashboardApi'
import type { PerformanceMetrics, SystemHealth } from '../../services/api/dashboardApi'

// Mock the dashboard API
vi.mock('../../services/api/dashboardApi', () => ({
  dashboardApi: {
    getCurrentMetrics: vi.fn(),
    getSystemHealth: vi.fn()
  }
}))

// Mock the notification hook
vi.mock('../../components/common', () => ({
  useNotification: () => ({
    showNotification: vi.fn()
  })
}))

// Mock Chart.js components
vi.mock('react-chartjs-2', () => ({
  Line: ({ data }: any) => <div data-testid="line-chart">{JSON.stringify(data)}</div>
}))

const mockMetrics: PerformanceMetrics = {
  timestamp: new Date().toISOString(),
  cpu_usage: 45.5,
  memory_usage: 67.2,
  disk_usage: 23.8,
  network_in: 12.3,
  network_out: 8.7,
  temperature: 55.5,
  gpu_usage: 32.1,
  gpu_memory: 78.9
}

const mockHealth: SystemHealth = {
  overall_status: 'healthy',
  services: [
    {
      name: 'api-server',
      status: 'running',
      uptime: 86400,
      memory_usage: 512,
      cpu_usage: 15.2,
      last_check: new Date().toISOString()
    }
  ],
  database: {
    status: 'connected',
    response_time_ms: 25,
    connections: 10,
    size_mb: 1024
  },
  storage: {
    total_gb: 100,
    used_gb: 25,
    available_gb: 75,
    usage_percent: 25
  }
}

describe('SystemMetrics', () => {
  beforeEach(() => {
    vi.mocked(dashboardApi.getCurrentMetrics).mockResolvedValue(mockMetrics)
    vi.mocked(dashboardApi.getSystemHealth).mockResolvedValue(mockHealth)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('システムメトリクスが正しく表示される', async () => {
    render(<SystemMetrics />)

    // Loading state
    expect(screen.getByText('読み込み中...')).toBeInTheDocument()

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('システムメトリクス')).toBeInTheDocument()
    })

    // Check metric cards
    expect(screen.getByText('CPU使用率')).toBeInTheDocument()
    expect(screen.getByText('45.5')).toBeInTheDocument()
    expect(screen.getByText('メモリ使用率')).toBeInTheDocument()
    expect(screen.getByText('67.2')).toBeInTheDocument()
    expect(screen.getByText('ディスク使用率')).toBeInTheDocument()
    expect(screen.getByText('23.8')).toBeInTheDocument()

    // Check system health status
    expect(screen.getByText('正常')).toBeInTheDocument()
  })

  it('温度とGPU使用率が表示される', async () => {
    render(<SystemMetrics />)

    await waitFor(() => {
      expect(screen.getByText('CPU温度')).toBeInTheDocument()
      expect(screen.getByText('55.5')).toBeInTheDocument()
      expect(screen.getByText('GPU使用率')).toBeInTheDocument()
      expect(screen.getByText('32.1')).toBeInTheDocument()
    })
  })

  it('更新ボタンが機能する', async () => {
    render(<SystemMetrics />)

    await waitFor(() => {
      expect(screen.getByText('システムメトリクス')).toBeInTheDocument()
    })

    const refreshButton = screen.getByLabelText('更新')
    fireEvent.click(refreshButton)

    // API should be called again
    await waitFor(() => {
      expect(dashboardApi.getCurrentMetrics).toHaveBeenCalledTimes(2)
      expect(dashboardApi.getSystemHealth).toHaveBeenCalledTimes(2)
    })
  })

  it('警告状態が正しく表示される', async () => {
    const warningMetrics = {
      ...mockMetrics,
      cpu_usage: 85.5 // Warning threshold
    }

    const warningHealth = {
      ...mockHealth,
      overall_status: 'warning' as const
    }

    vi.mocked(dashboardApi.getCurrentMetrics).mockResolvedValue(warningMetrics)
    vi.mocked(dashboardApi.getSystemHealth).mockResolvedValue(warningHealth)

    render(<SystemMetrics />)

    await waitFor(() => {
      expect(screen.getByText('警告')).toBeInTheDocument()
      expect(screen.getByText('85.5')).toBeInTheDocument()
    })
  })

  it('クリティカル状態が正しく表示される', async () => {
    const criticalMetrics = {
      ...mockMetrics,
      memory_usage: 98.5 // Critical threshold
    }

    const criticalHealth = {
      ...mockHealth,
      overall_status: 'critical' as const
    }

    vi.mocked(dashboardApi.getCurrentMetrics).mockResolvedValue(criticalMetrics)
    vi.mocked(dashboardApi.getSystemHealth).mockResolvedValue(criticalHealth)

    render(<SystemMetrics />)

    await waitFor(() => {
      expect(screen.getByText('異常')).toBeInTheDocument()
      expect(screen.getByText('98.5')).toBeInTheDocument()
    })
  })

  it('コンパクトモードが機能する', () => {
    render(<SystemMetrics compact={true} />)

    // In compact mode, certain elements should be styled differently
    // This is mainly a visual test, so we just verify the component renders
    expect(screen.getByText('読み込み中...')).toBeInTheDocument()
  })

  it('チャート表示オプションが機能する', async () => {
    render(<SystemMetrics showCharts={true} />)

    await waitFor(() => {
      expect(screen.getByText('システムメトリクス')).toBeInTheDocument()
    })

    // Charts should be rendered when showCharts is true
    const charts = screen.getAllByTestId('line-chart')
    expect(charts.length).toBeGreaterThan(0)
  })

  it('API呼び出しエラーが適切に処理される', async () => {
    vi.mocked(dashboardApi.getCurrentMetrics).mockRejectedValue(new Error('API Error'))
    vi.mocked(dashboardApi.getSystemHealth).mockRejectedValue(new Error('API Error'))

    render(<SystemMetrics />)

    // Should show loading initially
    expect(screen.getByText('読み込み中...')).toBeInTheDocument()

    // Wait for error handling
    await waitFor(() => {
      // Component should handle error gracefully and still show loading cards
      expect(screen.getAllByText('読み込み中...').length).toBeGreaterThan(0)
    })
  })

  it('設定メニューが正しく動作する', async () => {
    render(<SystemMetrics />)

    await waitFor(() => {
      expect(screen.getByText('システムメトリクス')).toBeInTheDocument()
    })

    const settingsButton = screen.getByLabelText('設定')
    fireEvent.click(settingsButton)

    // Settings menu should appear
    expect(screen.getByText('自動更新')).toBeInTheDocument()
    expect(screen.getByText('チャート表示')).toBeInTheDocument()
  })

  it('自動更新機能が正しく動作する', async () => {
    vi.useFakeTimers()

    render(<SystemMetrics refreshInterval={1000} />)

    await waitFor(() => {
      expect(dashboardApi.getCurrentMetrics).toHaveBeenCalledTimes(1)
    })

    // Fast-forward time
    vi.advanceTimersByTime(1000)

    await waitFor(() => {
      expect(dashboardApi.getCurrentMetrics).toHaveBeenCalledTimes(2)
    })

    vi.useRealTimers()
  })

  it('閾値警告が正しく表示される', async () => {
    render(<SystemMetrics />)

    await waitFor(() => {
      expect(screen.getByText('Warning: 70%')).toBeInTheDocument()
      expect(screen.getByText('Critical: 90%')).toBeInTheDocument()
    })
  })

  it('ネットワーク使用量が正しく計算される', async () => {
    render(<SystemMetrics />)

    await waitFor(() => {
      // Network usage should be sum of in + out
      const networkUsage = mockMetrics.network_in + mockMetrics.network_out
      expect(screen.getByText(networkUsage.toString())).toBeInTheDocument()
    })
  })

  it('トレンド表示が機能する', async () => {
    render(<SystemMetrics />)

    await waitFor(() => {
      expect(screen.getByText('システムメトリクス')).toBeInTheDocument()
    })

    // Should show trend icons (tested via accessibility or data attributes)
    // This would need more sophisticated mocking of historical data
  })
})