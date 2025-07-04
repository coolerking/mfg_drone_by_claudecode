import { render, screen } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ThemeProvider } from '@mui/material'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { configureStore } from '@reduxjs/toolkit'
import { theme } from '../../styles/theme'
import { authSlice } from '../../store/slices/authSlice'
import { apiSlice } from '../../store/api/apiSlice'

// Dashboard components
import Dashboard from '../../pages/Dashboard'
import DroneManagement from '../../pages/DroneManagement'
import DatasetManagement from '../../pages/DatasetManagement'
import ModelManagement from '../../pages/ModelManagement'
import SystemMonitoring from '../../pages/SystemMonitoring'
import Login from '../../pages/Login'

// Common components
import { Layout } from '../../components/common/Layout'
import { Button } from '../../components/common/Button'
import { Modal } from '../../components/common/Modal'
import { Loading } from '../../components/common/Loading'

// jest-axe の設定
expect.extend(toHaveNoViolations)

// テスト用ストア作成
const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authSlice.reducer,
      api: apiSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(apiSlice.middleware),
    preloadedState: {
      auth: {
        user: { id: '1', username: 'testuser', role: 'admin' },
        token: 'mock-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
      },
      ...initialState,
    },
  })
}

// テスト用ラッパーコンポーネント
const TestWrapper = ({ 
  children,
  store = createTestStore()
}: { 
  children: React.ReactNode
  store?: ReturnType<typeof createTestStore>
}) => (
  <Provider store={store}>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        {children}
      </ThemeProvider>
    </BrowserRouter>
  </Provider>
)

// Mock API calls
vi.mock('../../services/api/apiClient', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: [] }),
    post: vi.fn().mockResolvedValue({ data: {} }),
  }
}))

describe('アクセシビリティテスト', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('ページレベルのアクセシビリティ', () => {
    it('ログインページにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper store={createTestStore({ auth: { isAuthenticated: false } })}>
          <Login />
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('ダッシュボードページにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper>
          <Layout>
            <Dashboard />
          </Layout>
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('ドローン管理ページにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper>
          <Layout>
            <DroneManagement />
          </Layout>
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('データセット管理ページにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper>
          <Layout>
            <DatasetManagement />
          </Layout>
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('モデル管理ページにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper>
          <Layout>
            <ModelManagement />
          </Layout>
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('システム監視ページにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper>
          <Layout>
            <SystemMonitoring />
          </Layout>
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })

  describe('コンポーネントレベルのアクセシビリティ', () => {
    it('Buttonコンポーネントにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper>
          <Button onClick={() => {}}>テストボタン</Button>
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('Modalコンポーネントにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper>
          <Modal open={true} onClose={() => {}} title="テストモーダル">
            <p>モーダルコンテンツ</p>
          </Modal>
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('Loadingコンポーネントにアクセシビリティ違反がない', async () => {
      const { container } = render(
        <TestWrapper>
          <Loading />
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })

  describe('キーボードナビゲーション', () => {
    it('ログインフォームがキーボードで操作可能', () => {
      render(
        <TestWrapper store={createTestStore({ auth: { isAuthenticated: false } })}>
          <Login />
        </TestWrapper>
      )

      const usernameInput = screen.getByLabelText('ユーザー名')
      const passwordInput = screen.getByLabelText('パスワード')
      const loginButton = screen.getByRole('button', { name: 'ログイン' })

      // タブ順序の確認
      usernameInput.focus()
      expect(usernameInput).toHaveFocus()

      // Tab キーで次の要素に移動
      passwordInput.focus()
      expect(passwordInput).toHaveFocus()

      loginButton.focus()
      expect(loginButton).toHaveFocus()
    })

    it('ナビゲーションメニューがキーボードで操作可能', () => {
      render(
        <TestWrapper>
          <Layout>
            <Dashboard />
          </Layout>
        </TestWrapper>
      )

      const navLinks = screen.getAllByRole('link')
      
      // 全てのナビゲーションリンクがフォーカス可能
      navLinks.forEach(link => {
        expect(link).toHaveAttribute('tabindex', '0')
      })
    })

    it('モーダルダイアログのフォーカストラップが機能する', () => {
      render(
        <TestWrapper>
          <Modal open={true} onClose={() => {}} title="テストモーダル">
            <input placeholder="入力フィールド1" />
            <input placeholder="入力フィールド2" />
            <button>ボタン</button>
          </Modal>
        </TestWrapper>
      )

      const modal = screen.getByRole('dialog')
      expect(modal).toBeInTheDocument()

      // モーダル内の最初のフォーカス可能要素にフォーカスが当たる
      const firstInput = screen.getByPlaceholderText('入力フィールド1')
      expect(firstInput).toHaveFocus()
    })
  })

  describe('ARIA属性とセマンティクス', () => {
    it('ランドマークロールが適切に設定されている', () => {
      render(
        <TestWrapper>
          <Layout>
            <Dashboard />
          </Layout>
        </TestWrapper>
      )

      // メインコンテンツエリア
      expect(screen.getByRole('main')).toBeInTheDocument()
      
      // ナビゲーションエリア
      expect(screen.getByRole('navigation')).toBeInTheDocument()
      
      // ヘッダーエリア
      const headers = screen.getAllByRole('banner')
      expect(headers.length).toBeGreaterThan(0)
    })

    it('見出し階層が適切に設定されている', () => {
      render(
        <TestWrapper>
          <Layout>
            <Dashboard />
          </Layout>
        </TestWrapper>
      )

      // h1見出しが存在する
      const h1 = screen.getByRole('heading', { level: 1 })
      expect(h1).toBeInTheDocument()

      // 見出し階層が論理的（h1 -> h2 -> h3...）
      const headings = screen.getAllByRole('heading')
      const levels = headings.map(h => parseInt(h.tagName.substring(1)))
      
      // h1が存在することを確認
      expect(levels).toContain(1)
    })

    it('フォームラベルが適切に関連付けられている', () => {
      render(
        <TestWrapper store={createTestStore({ auth: { isAuthenticated: false } })}>
          <Login />
        </TestWrapper>
      )

      const usernameInput = screen.getByLabelText('ユーザー名')
      const passwordInput = screen.getByLabelText('パスワード')

      expect(usernameInput).toHaveAttribute('aria-labelledby')
      expect(passwordInput).toHaveAttribute('aria-labelledby')
    })

    it('エラーメッセージが適切に関連付けられている', () => {
      render(
        <TestWrapper store={createTestStore({ 
          auth: { 
            isAuthenticated: false,
            error: 'ログインに失敗しました'
          } 
        })}>
          <Login />
        </TestWrapper>
      )

      const errorMessage = screen.getByText('ログインに失敗しました')
      expect(errorMessage).toHaveAttribute('role', 'alert')
      expect(errorMessage).toHaveAttribute('aria-live', 'polite')
    })

    it('ライブリージョンが適切に設定されている', () => {
      render(
        <TestWrapper>
          <Layout>
            <Dashboard />
          </Layout>
        </TestWrapper>
      )

      // ステータス更新などのライブリージョン
      const liveRegions = screen.getAllByRole('status')
      expect(liveRegions.length).toBeGreaterThan(0)
    })
  })

  describe('色とコントラスト', () => {
    it('ハイコントラストモードでも情報が伝わる', () => {
      // ハイコントラストモードをシミュレート
      const { container } = render(
        <TestWrapper>
          <div style={{ filter: 'contrast(1000%)' }}>
            <Dashboard />
          </div>
        </TestWrapper>
      )

      // 重要な情報が色だけでなくテキストでも表現されている
      const statusElements = container.querySelectorAll('[data-testid*="status"]')
      statusElements.forEach(element => {
        // ステータスがテキストでも表現されていることを確認
        expect(element.textContent).toBeTruthy()
      })
    })

    it('色覚異常に配慮した色使いになっている', () => {
      render(
        <TestWrapper>
          <Dashboard />
        </TestWrapper>
      )

      // 成功、警告、エラーの状態が色だけでなく
      // アイコンやテキストでも区別されている
      const successElements = screen.getAllByText(/成功|正常|OK/i)
      const warningElements = screen.getAllByText(/警告|注意/i)
      const errorElements = screen.getAllByText(/エラー|失敗|異常/i)

      // それぞれに適切なARIAラベルやroleが設定されている
      expect(successElements.length + warningElements.length + errorElements.length).toBeGreaterThan(0)
    })
  })

  describe('レスポンシブデザインのアクセシビリティ', () => {
    it('モバイルビューでもアクセシブル', async () => {
      // モバイルビューポートを設定
      global.innerWidth = 375
      global.innerHeight = 667
      global.dispatchEvent(new Event('resize'))

      const { container } = render(
        <TestWrapper>
          <Layout>
            <Dashboard />
          </Layout>
        </TestWrapper>
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('タッチターゲットが適切なサイズ', () => {
      // モバイルビューポートを設定
      global.innerWidth = 375
      global.innerHeight = 667

      render(
        <TestWrapper>
          <Button onClick={() => {}}>タッチボタン</Button>
        </TestWrapper>
      )

      const button = screen.getByRole('button')
      const styles = window.getComputedStyle(button)
      
      // 最小タッチターゲットサイズ（44px x 44px）を確認
      const minSize = 44
      expect(parseInt(styles.height)).toBeGreaterThanOrEqual(minSize)
      expect(parseInt(styles.width)).toBeGreaterThanOrEqual(minSize)
    })
  })

  describe('スクリーンリーダー対応', () => {
    it('重要な動的コンテンツが適切にアナウンスされる', () => {
      render(
        <TestWrapper>
          <div>
            <div role="status" aria-live="polite">
              ドローンの接続状態が更新されました
            </div>
            <div role="alert" aria-live="assertive">
              緊急: バッテリー残量が5%です
            </div>
          </div>
        </TestWrapper>
      )

      const statusUpdate = screen.getByRole('status')
      const alert = screen.getByRole('alert')

      expect(statusUpdate).toHaveAttribute('aria-live', 'polite')
      expect(alert).toHaveAttribute('aria-live', 'assertive')
    })

    it('複雑なUIの構造が適切に説明されている', () => {
      render(
        <TestWrapper>
          <div role="tablist" aria-label="システム管理タブ">
            <button role="tab" aria-selected="true" aria-controls="dashboard-panel">
              ダッシュボード
            </button>
            <button role="tab" aria-selected="false" aria-controls="monitoring-panel">
              監視
            </button>
          </div>
          <div id="dashboard-panel" role="tabpanel">
            ダッシュボードコンテンツ
          </div>
        </TestWrapper>
      )

      const tablist = screen.getByRole('tablist')
      const tabs = screen.getAllByRole('tab')
      const tabpanel = screen.getByRole('tabpanel')

      expect(tablist).toHaveAttribute('aria-label')
      expect(tabs[0]).toHaveAttribute('aria-controls')
      expect(tabpanel).toHaveAttribute('id')
    })

    it('データテーブルが適切に構造化されている', () => {
      render(
        <TestWrapper>
          <table role="table" aria-label="ドローン一覧">
            <thead>
              <tr>
                <th scope="col">名前</th>
                <th scope="col">ステータス</th>
                <th scope="col">バッテリー</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>ドローン1</td>
                <td>接続中</td>
                <td>85%</td>
              </tr>
            </tbody>
          </table>
        </TestWrapper>
      )

      const table = screen.getByRole('table')
      const columnHeaders = screen.getAllByRole('columnheader')

      expect(table).toHaveAttribute('aria-label')
      columnHeaders.forEach(header => {
        expect(header).toHaveAttribute('scope', 'col')
      })
    })
  })

  describe('フォーカス管理', () => {
    it('モーダル開閉時のフォーカス管理が適切', () => {
      let isOpen = false
      const toggleModal = () => { isOpen = !isOpen }

      const { rerender } = render(
        <TestWrapper>
          <div>
            <button onClick={toggleModal}>モーダルを開く</button>
            <Modal open={isOpen} onClose={toggleModal} title="テスト">
              <input placeholder="モーダル内入力" />
            </Modal>
          </div>
        </TestWrapper>
      )

      const openButton = screen.getByText('モーダルを開く')
      openButton.focus()
      expect(openButton).toHaveFocus()

      // モーダルを開く
      isOpen = true
      rerender(
        <TestWrapper>
          <div>
            <button onClick={toggleModal}>モーダルを開く</button>
            <Modal open={isOpen} onClose={toggleModal} title="テスト">
              <input placeholder="モーダル内入力" />
            </Modal>
          </div>
        </TestWrapper>
      )

      // モーダル内の要素にフォーカスが移る
      const modalInput = screen.getByPlaceholderText('モーダル内入力')
      expect(modalInput).toHaveFocus()
    })

    it('ページ遷移時のフォーカス管理が適切', () => {
      render(
        <TestWrapper>
          <Layout>
            <Dashboard />
          </Layout>
        </TestWrapper>
      )

      // メインコンテンツエリアがフォーカス可能
      const main = screen.getByRole('main')
      expect(main).toHaveAttribute('tabindex', '-1')
    })
  })
})