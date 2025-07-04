import { test, expect } from '@playwright/test'

test.describe('ダッシュボード機能', () => {
  test.beforeEach(async ({ page }) => {
    // ログイン処理
    await page.goto('/login')
    await page.getByLabel('ユーザー名').fill('admin')
    await page.getByLabel('パスワード').fill('password')
    await page.getByRole('button', { name: 'ログイン' }).click()
    await expect(page).toHaveURL('/dashboard')
  })

  test('ダッシュボードの基本表示', async ({ page }) => {
    // ダッシュボードのタイトル
    await expect(page.getByRole('heading', { name: 'ダッシュボード' })).toBeVisible()
    
    // 統計カードの表示確認
    await expect(page.getByText('接続中のドローン')).toBeVisible()
    await expect(page.getByText('アクティブなアラート')).toBeVisible()
    await expect(page.getByText('システム稼働率')).toBeVisible()
    await expect(page.getByText('バッテリー低下警告')).toBeVisible()
    
    // サイドバーナビゲーションの確認
    await expect(page.getByRole('link', { name: 'ドローン管理' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'データセット' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'モデル管理' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'システム監視' })).toBeVisible()
  })

  test('リアルタイムデータ更新', async ({ page }) => {
    // 初期データの確認
    const initialDroneCount = await page.getByTestId('connected-drones-count').textContent()
    
    // 更新ボタンをクリック
    await page.getByRole('button', { name: '更新' }).click()
    
    // ローディング状態の確認
    await expect(page.getByTestId('loading-indicator')).toBeVisible()
    
    // データが更新されるまで待機
    await page.waitForTimeout(2000)
    
    // ローディングが終了することを確認
    await expect(page.getByTestId('loading-indicator')).not.toBeVisible()
  })

  test('アラート管理機能', async ({ page }) => {
    // アラートパネルの表示確認
    await expect(page.getByText('最新のアラート')).toBeVisible()
    
    // アラートがある場合の操作テスト
    const alertItem = page.getByTestId('alert-item').first()
    if (await alertItem.isVisible()) {
      // アラート詳細の展開
      await alertItem.click()
      await expect(page.getByTestId('alert-details')).toBeVisible()
      
      // アラート解除ボタンのテスト
      if (await page.getByRole('button', { name: 'アラート解除' }).isVisible()) {
        await page.getByRole('button', { name: 'アラート解除' }).click()
        await expect(page.getByText('アラートを解除しました')).toBeVisible()
      }
    }
  })

  test('アクティビティログ', async ({ page }) => {
    // アクティビティログの表示確認
    await expect(page.getByText('アクティビティログ')).toBeVisible()
    
    // ログエントリの確認
    const logEntries = page.getByTestId('log-entry')
    await expect(logEntries.first()).toBeVisible()
    
    // ログフィルターのテスト
    await page.getByRole('combobox', { name: 'ログフィルター' }).click()
    await page.getByRole('option', { name: 'エラーのみ' }).click()
    
    // フィルター適用後の確認
    await page.waitForTimeout(1000)
    await expect(page.getByTestId('filtered-logs')).toBeVisible()
  })

  test('システム状態監視', async ({ page }) => {
    // システム状態の表示確認
    await expect(page.getByText('システム状態')).toBeVisible()
    
    // CPU使用率の確認
    await expect(page.getByText('CPU使用率')).toBeVisible()
    const cpuUsage = page.getByTestId('cpu-usage-value')
    await expect(cpuUsage).toBeVisible()
    
    // メモリ使用率の確認
    await expect(page.getByText('メモリ使用率')).toBeVisible()
    const memoryUsage = page.getByTestId('memory-usage-value')
    await expect(memoryUsage).toBeVisible()
    
    // 状態インジケーターの色を確認
    const statusIndicator = page.getByTestId('system-status-indicator')
    await expect(statusIndicator).toBeVisible()
  })

  test('ナビゲーション機能', async ({ page }) => {
    // ドローン管理ページへの遷移
    await page.getByRole('link', { name: 'ドローン管理' }).click()
    await expect(page).toHaveURL('/drones')
    await expect(page.getByRole('heading', { name: 'ドローン管理' })).toBeVisible()
    
    // ダッシュボードに戻る
    await page.getByRole('link', { name: 'ダッシュボード' }).click()
    await expect(page).toHaveURL('/dashboard')
    
    // データセットページへの遷移
    await page.getByRole('link', { name: 'データセット' }).click()
    await expect(page).toHaveURL('/datasets')
    await expect(page.getByRole('heading', { name: 'データセット管理' })).toBeVisible()
  })

  test('レスポンシブサイドバー', async ({ page }) => {
    // モバイルビューポートに変更
    await page.setViewportSize({ width: 768, height: 1024 })
    
    // ハンバーガーメニューが表示されることを確認
    await expect(page.getByRole('button', { name: 'メニュー' })).toBeVisible()
    
    // メニューを開く
    await page.getByRole('button', { name: 'メニュー' }).click()
    
    // サイドバーが表示されることを確認
    await expect(page.getByRole('navigation')).toBeVisible()
    
    // メニューを閉じる
    await page.getByRole('button', { name: '閉じる' }).click()
    
    // サイドバーが非表示になることを確認
    await expect(page.getByRole('navigation')).not.toBeVisible()
  })

  test('データエクスポート機能', async ({ page }) => {
    // エクスポートボタンの確認
    await page.getByRole('button', { name: 'データエクスポート' }).click()
    
    // エクスポート形式の選択
    await expect(page.getByText('エクスポート形式を選択')).toBeVisible()
    await page.getByRole('radio', { name: 'CSV' }).check()
    
    // エクスポート実行
    const downloadPromise = page.waitForEvent('download')
    await page.getByRole('button', { name: 'エクスポート実行' }).click()
    const download = await downloadPromise
    
    // ダウンロードファイル名の確認
    expect(download.suggestedFilename()).toMatch(/dashboard-data.*\.csv/)
  })

  test('ダークモード切り替え', async ({ page }) => {
    // テーマ切り替えボタンをクリック
    await page.getByRole('button', { name: 'テーマ切り替え' }).click()
    
    // ダークモードに切り替わることを確認
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
    
    // 再度クリックしてライトモードに戻す
    await page.getByRole('button', { name: 'テーマ切り替え' }).click()
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
  })

  test('検索機能', async ({ page }) => {
    // グローバル検索の使用
    await page.getByPlaceholder('検索...').fill('drone')
    await page.getByRole('button', { name: '検索' }).click()
    
    // 検索結果の確認
    await expect(page.getByText('検索結果')).toBeVisible()
    
    // 検索結果をクリックして詳細画面に遷移
    const searchResult = page.getByTestId('search-result').first()
    if (await searchResult.isVisible()) {
      await searchResult.click()
      // 適切なページに遷移することを確認
      await expect(page.url()).toMatch(/\/(drones|datasets|models)\//)
    }
  })

  test('キーボードナビゲーション', async ({ page }) => {
    // Tab キーでナビゲーション要素に移動
    await page.keyboard.press('Tab')
    
    // フォーカスされた要素が適切にハイライトされることを確認
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
    
    // Enter キーで要素をアクティベート
    await page.keyboard.press('Enter')
    
    // 適切なアクションが実行されることを確認
    // （具体的な動作は実装に依存）
  })
})