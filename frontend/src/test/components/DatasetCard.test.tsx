import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import { DatasetCard } from '../../components/dataset/DatasetCard'
import { Dataset } from '../../services/api/visionApi'

// Mock the ConfirmDialog hook
vi.mock('../../components/common/ConfirmDialog', () => ({
  useConfirm: () => vi.fn(() => Promise.resolve(true)),
  ConfirmDialog: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

const mockDataset: Dataset = {
  id: 'dataset-1',
  name: 'Test Dataset',
  description: 'This is a test dataset',
  type: 'training',
  status: 'active',
  image_count: 100,
  label_count: 50,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-02T00:00:00Z',
  size_bytes: 1024 * 1024 * 10, // 10MB
  labels: ['person', 'car', 'bicycle'],
}

describe('DatasetCard', () => {
  const mockOnEdit = vi.fn()
  const mockOnView = vi.fn()
  const mockOnExport = vi.fn()
  const mockOnDelete = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dataset information correctly', () => {
    render(
      <DatasetCard
        dataset={mockDataset}
        onEdit={mockOnEdit}
        onView={mockOnView}
        onExport={mockOnExport}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText('📁 Test Dataset')).toBeInTheDocument()
    expect(screen.getByText('This is a test dataset')).toBeInTheDocument()
    expect(screen.getByText('100 枚')).toBeInTheDocument()
    expect(screen.getByText('50 ラベル')).toBeInTheDocument()
    expect(screen.getByText('アクティブ')).toBeInTheDocument()
    expect(screen.getByText('training')).toBeInTheDocument()
  })

  it('displays labels correctly', () => {
    render(
      <DatasetCard
        dataset={mockDataset}
        onEdit={mockOnEdit}
        onView={mockOnView}
        onExport={mockOnExport}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText('person')).toBeInTheDocument()
    expect(screen.getByText('car')).toBeInTheDocument()
    expect(screen.getByText('bicycle')).toBeInTheDocument()
  })

  it('calls onView when view button is clicked', () => {
    render(
      <DatasetCard
        dataset={mockDataset}
        onEdit={mockOnEdit}
        onView={mockOnView}
        onExport={mockOnExport}
        onDelete={mockOnDelete}
      />
    )

    fireEvent.click(screen.getByText('表示'))
    expect(mockOnView).toHaveBeenCalledWith('dataset-1')
  })

  it('calls onEdit when edit button is clicked', () => {
    render(
      <DatasetCard
        dataset={mockDataset}
        onEdit={mockOnEdit}
        onView={mockOnView}
        onExport={mockOnExport}
        onDelete={mockOnDelete}
      />
    )

    fireEvent.click(screen.getByText('編集'))
    expect(mockOnEdit).toHaveBeenCalledWith('dataset-1')
  })

  it('formats file size correctly', () => {
    render(
      <DatasetCard
        dataset={mockDataset}
        onEdit={mockOnEdit}
        onView={mockOnView}
        onExport={mockOnExport}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText('10 MB')).toBeInTheDocument()
  })

  it('shows correct status color for different statuses', () => {
    const processingDataset = { ...mockDataset, status: 'processing' as const }
    
    const { rerender } = render(
      <DatasetCard
        dataset={processingDataset}
        onEdit={mockOnEdit}
        onView={mockOnView}
        onExport={mockOnExport}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText('処理中')).toBeInTheDocument()

    const archivedDataset = { ...mockDataset, status: 'archived' as const }
    rerender(
      <DatasetCard
        dataset={archivedDataset}
        onEdit={mockOnEdit}
        onView={mockOnView}
        onExport={mockOnExport}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText('アーカイブ')).toBeInTheDocument()
  })

  it('handles many labels correctly', () => {
    const datasetWithManyLabels = {
      ...mockDataset,
      labels: ['label1', 'label2', 'label3', 'label4', 'label5'],
    }

    render(
      <DatasetCard
        dataset={datasetWithManyLabels}
        onEdit={mockOnEdit}
        onView={mockOnView}
        onExport={mockOnExport}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText('label1')).toBeInTheDocument()
    expect(screen.getByText('label2')).toBeInTheDocument()
    expect(screen.getByText('label3')).toBeInTheDocument()
    expect(screen.getByText('+2')).toBeInTheDocument()
  })
})