import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { ModelCard } from '@/components/model/ModelCard'
import { modelApi, type Model } from '@/services/api/modelApi'
import { useNotification } from '@/hooks/useNotification'
import { useConfirm } from '@/components/common'

// Mock dependencies
vi.mock('@/services/api/modelApi')
vi.mock('@/hooks/useNotification')
vi.mock('@/components/common')

const mockModelApi = modelApi as any
const mockUseNotification = useNotification as any
const mockUseConfirm = useConfirm as any

const mockModel: Model = {
  id: 'test-model-1',
  name: 'Test Model',
  description: 'Test model description',
  type: 'yolo',
  status: 'trained',
  version: '1.0.0',
  accuracy: 85.5,
  map_score: 0.782,
  precision: 0.856,
  recall: 0.743,
  f1_score: 0.795,
  training_dataset_id: 'dataset-1',
  validation_dataset_id: 'dataset-2',
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T12:00:00Z',
  file_size_mb: 45.2,
  classes: ['person', 'car', 'bicycle'],
  training_epochs: 100,
  training_time_hours: 2.5
}

const defaultProps = {
  model: mockModel,
  onUpdate: vi.fn(),
  onDelete: vi.fn(),
  onStartTraining: vi.fn(),
  onViewTraining: vi.fn(),
  onEvaluate: vi.fn(),
  onDeploy: vi.fn()
}

describe('ModelCard', () => {
  const mockShowNotification = vi.fn()
  const mockConfirm = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseNotification.mockReturnValue({
      showNotification: mockShowNotification
    })
    mockUseConfirm.mockReturnValue(mockConfirm)
  })

  it('モデル情報を正しく表示する', () => {
    render(<ModelCard {...defaultProps} />)

    expect(screen.getByText('Test Model')).toBeInTheDocument()
    expect(screen.getByText('Test model description')).toBeInTheDocument()
    expect(screen.getByText('YOLO')).toBeInTheDocument()
    expect(screen.getByText('精度: 85.5%')).toBeInTheDocument()
    expect(screen.getByText('mAP: 0.782')).toBeInTheDocument()
    expect(screen.getByText('F1: 0.795')).toBeInTheDocument()
    expect(screen.getByText('1.0.0')).toBeInTheDocument()
    expect(screen.getByText('45.2 MB')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('2.5時間')).toBeInTheDocument()
  })

  it('学習済みモデルで評価とデプロイボタンが表示される', () => {
    render(<ModelCard {...defaultProps} />)

    expect(screen.getByLabelText('評価実行')).toBeInTheDocument()
    expect(screen.getByLabelText('デプロイ')).toBeInTheDocument()
  })

  it('学習中モデルで学習進捗表示ボタンが表示される', () => {
    const trainingModel: Model = {
      ...mockModel,
      status: 'training'
    }

    render(<ModelCard {...defaultProps} model={trainingModel} />)

    expect(screen.getByLabelText('学習進捗表示')).toBeInTheDocument()
    expect(screen.queryByLabelText('評価実行')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('デプロイ')).not.toBeInTheDocument()
  })

  it('検出クラスを正しく表示する', () => {
    render(<ModelCard {...defaultProps} />)

    expect(screen.getByText('person')).toBeInTheDocument()
    expect(screen.getByText('car')).toBeInTheDocument()
    expect(screen.getByText('bicycle')).toBeInTheDocument()
    expect(screen.getByText('検出クラス (3)')).toBeInTheDocument()
  })

  it('多くのクラスがある場合は省略表示される', () => {
    const modelWithManyClasses: Model = {
      ...mockModel,
      classes: ['person', 'car', 'bicycle', 'truck', 'bus', 'motorcycle']
    }

    render(<ModelCard {...defaultProps} model={modelWithManyClasses} />)

    expect(screen.getByText('person')).toBeInTheDocument()
    expect(screen.getByText('car')).toBeInTheDocument()
    expect(screen.getByText('bicycle')).toBeInTheDocument()
    expect(screen.getByText('+3個')).toBeInTheDocument()
    expect(screen.getByText('検出クラス (6)')).toBeInTheDocument()
  })

  it('メニューボタンクリックでメニューが開く', async () => {
    render(<ModelCard {...defaultProps} />)

    const menuButton = screen.getByRole('button', { name: '' }) // More icon button
    fireEvent.click(menuButton)

    await waitFor(() => {
      expect(screen.getByText('編集')).toBeInTheDocument()
      expect(screen.getByText('複製')).toBeInTheDocument()
      expect(screen.getByText('エクスポート')).toBeInTheDocument()
      expect(screen.getByText('再学習')).toBeInTheDocument()
      expect(screen.getByText('削除')).toBeInTheDocument()
    })
  })

  it('削除ボタンクリック時に確認ダイアログが表示される', async () => {
    mockConfirm.mockResolvedValue(true)
    mockModelApi.deleteModel.mockResolvedValue({ success: true })

    render(<ModelCard {...defaultProps} />)

    const menuButton = screen.getByRole('button', { name: '' })
    fireEvent.click(menuButton)

    await waitFor(() => {
      expect(screen.getByText('削除')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('削除'))

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith(
        'モデル「Test Model」を削除しますか？',
        'この操作は取り消せません。'
      )
    })
  })

  it('削除が成功した場合、通知とコールバックが呼ばれる', async () => {
    mockConfirm.mockResolvedValue(true)
    mockModelApi.deleteModel.mockResolvedValue({ success: true })

    render(<ModelCard {...defaultProps} />)

    const menuButton = screen.getByRole('button', { name: '' })
    fireEvent.click(menuButton)

    await waitFor(() => {
      expect(screen.getByText('削除')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('削除'))

    await waitFor(() => {
      expect(mockModelApi.deleteModel).toHaveBeenCalledWith('test-model-1')
      expect(mockShowNotification).toHaveBeenCalledWith('success', 'モデルが削除されました')
      expect(defaultProps.onDelete).toHaveBeenCalledWith('test-model-1')
    })
  })

  it('複製ボタンクリック時にAPIが呼ばれる', async () => {
    const duplicatedModel: Model = {
      ...mockModel,
      id: 'test-model-2',
      name: 'Test Model (コピー)'
    }
    mockModelApi.duplicateModel.mockResolvedValue(duplicatedModel)

    render(<ModelCard {...defaultProps} />)

    const menuButton = screen.getByRole('button', { name: '' })
    fireEvent.click(menuButton)

    await waitFor(() => {
      expect(screen.getByText('複製')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('複製'))

    await waitFor(() => {
      expect(mockModelApi.duplicateModel).toHaveBeenCalledWith('test-model-1', 'Test Model (コピー)')
      expect(mockShowNotification).toHaveBeenCalledWith('success', 'モデルが複製されました')
      expect(defaultProps.onUpdate).toHaveBeenCalledWith(duplicatedModel)
    })
  })

  it('エクスポートボタンクリック時にダウンロードが開始される', async () => {
    const mockOpen = vi.fn()
    global.window.open = mockOpen

    mockModelApi.exportModel.mockResolvedValue({
      download_url: 'https://example.com/download/model.onnx'
    })

    render(<ModelCard {...defaultProps} />)

    const menuButton = screen.getByRole('button', { name: '' })
    fireEvent.click(menuButton)

    await waitFor(() => {
      expect(screen.getByText('エクスポート')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('エクスポート'))

    await waitFor(() => {
      expect(mockModelApi.exportModel).toHaveBeenCalledWith('test-model-1', 'onnx')
      expect(mockOpen).toHaveBeenCalledWith('https://example.com/download/model.onnx', '_blank')
      expect(mockShowNotification).toHaveBeenCalledWith('success', 'モデルのエクスポートを開始しました')
    })
  })

  it('デプロイボタンクリック時にAPIが呼ばれる', async () => {
    mockModelApi.deployModel.mockResolvedValue({
      success: true,
      endpoint_url: 'https://api.example.com/models/test-model-1'
    })

    render(<ModelCard {...defaultProps} />)

    const deployButton = screen.getByLabelText('デプロイ')
    fireEvent.click(deployButton)

    await waitFor(() => {
      expect(mockModelApi.deployModel).toHaveBeenCalledWith('test-model-1')
      expect(mockShowNotification).toHaveBeenCalledWith('success', 'モデルがデプロイされました')
      expect(defaultProps.onDeploy).toHaveBeenCalledWith(mockModel)
    })
  })

  it('評価ボタンクリック時にコールバックが呼ばれる', () => {
    render(<ModelCard {...defaultProps} />)

    const evaluateButton = screen.getByLabelText('評価実行')
    fireEvent.click(evaluateButton)

    expect(defaultProps.onEvaluate).toHaveBeenCalledWith(mockModel)
  })

  it('学習進捗表示ボタンクリック時にコールバックが呼ばれる', () => {
    const trainingModel: Model = {
      ...mockModel,
      status: 'training'
    }

    render(<ModelCard {...defaultProps} model={trainingModel} />)

    const viewTrainingButton = screen.getByLabelText('学習進捗表示')
    fireEvent.click(viewTrainingButton)

    expect(defaultProps.onViewTraining).toHaveBeenCalledWith(trainingModel)
  })

  it('APIエラー時にエラー通知が表示される', async () => {
    mockConfirm.mockResolvedValue(true)
    mockModelApi.deleteModel.mockRejectedValue(new Error('API Error'))

    render(<ModelCard {...defaultProps} />)

    const menuButton = screen.getByRole('button', { name: '' })
    fireEvent.click(menuButton)

    await waitFor(() => {
      expect(screen.getByText('削除')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('削除'))

    await waitFor(() => {
      expect(mockShowNotification).toHaveBeenCalledWith('error', 'モデルの削除に失敗しました')
    })
  })
})