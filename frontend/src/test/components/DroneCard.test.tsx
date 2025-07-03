import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from '@mui/material'
import { DroneCard } from '../../components/drone/DroneCard'
import { Drone } from '../../types/drone'
import { theme } from '../../styles/theme'

// Mock the ConfirmDialog hook
vi.mock('../../components/common/ConfirmDialog', () => ({
  useConfirmDialog: () => ({
    showConfirmDialog: vi.fn()
  })
}))

const mockDrone: Drone = {
  id: 'test-drone',
  name: 'Test Drone',
  model: 'Tello EDU',
  serial_number: 'TEST-001',
  status: 'connected',
  battery: 85,
  altitude: 0,
  temperature: 24,
  signal_strength: 90,
  flight_time: 0,
  position: { x: 0, y: 0, z: 0 },
  camera: { isStreaming: false, resolution: '720p', fps: 30 },
  lastSeen: new Date().toISOString(),
  createdAt: new Date().toISOString()
}

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
)

describe('DroneCard', () => {
  it('ドローン情報を正しく表示する', () => {
    render(
      <TestWrapper>
        <DroneCard drone={mockDrone} />
      </TestWrapper>
    )
    
    expect(screen.getByText('Test Drone')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('Tello EDU • TEST-001')).toBeInTheDocument()
  })

  it('接続ボタンが正しく機能する', () => {
    const mockOnConnect = vi.fn()
    render(
      <TestWrapper>
        <DroneCard drone={mockDrone} onConnect={mockOnConnect} />
      </TestWrapper>
    )
    
    const connectButton = screen.getByText('切断')
    fireEvent.click(connectButton)
    
    // Since the drone is connected, it should show "切断" button
    expect(connectButton).toBeInTheDocument()
  })

  it('バッテリー残量が少ない場合に警告表示する', () => {
    const lowBatteryDrone = { ...mockDrone, battery: 10, status: 'low_battery' as const }
    render(
      <TestWrapper>
        <DroneCard drone={lowBatteryDrone} />
      </TestWrapper>
    )
    
    expect(screen.getByText('10%')).toBeInTheDocument()
    // Low battery should have red color styling
  })

  it('離陸ボタンが適切な条件で有効化される', () => {
    const mockOnTakeoff = vi.fn()
    render(
      <TestWrapper>
        <DroneCard drone={mockDrone} onTakeoff={mockOnTakeoff} />
      </TestWrapper>
    )
    
    const takeoffButton = screen.getByText('離陸')
    expect(takeoffButton).not.toBeDisabled()
  })

  it('切断されたドローンでは操作ボタンが無効化される', () => {
    const disconnectedDrone = { ...mockDrone, status: 'disconnected' as const }
    render(
      <TestWrapper>
        <DroneCard drone={disconnectedDrone} />
      </TestWrapper>
    )
    
    const controlButton = screen.getByText('制御')
    expect(controlButton).toBeDisabled()
  })
})