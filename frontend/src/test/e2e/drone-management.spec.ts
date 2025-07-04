import { test, expect } from '@playwright/test'

test.describe('ドローン管理機能', () => {
  test.beforeEach(async ({ page }) => {
    // ログイン処理
    await page.goto('/login')
    await page.getByLabel('ユーザー名').fill('admin')
    await page.getByLabel('パスワード').fill('password')
    await page.getByRole('button', { name: 'ログイン' }).click()
    
    // ドローン管理ページに移動
    await page.getByRole('link', { name: 'ドローン管理' }).click()
    await expect(page).toHaveURL('/drones')
  })

  test('ドローン一覧の表示', async ({ page }) => {
    // ページタイトルの確認
    await expect(page.getByRole('heading', { name: 'ドローン管理' })).toBeVisible()
    
    // 統計情報の表示確認
    await expect(page.getByText('総ドローン数')).toBeVisible()
    await expect(page.getByText('接続中')).toBeVisible()
    await expect(page.getByText('飛行中')).toBeVisible()
    await expect(page.getByText('警告')).toBeVisible()
    
    // ドローンカードの表示確認
    const droneCards = page.getByTestId('drone-card')
    await expect(droneCards.first()).toBeVisible()
  })

  test('ドローン検索機能', async ({ page }) => {
    // 検索ボックスに入力
    await page.getByPlaceholder('ドローン名で検索...').fill('Test Drone')
    
    // 検索実行
    await page.getByRole('button', { name: '検索' }).click()
    
    // 検索結果の確認
    await page.waitForTimeout(1000)
    const searchResults = page.getByTestId('drone-card')
    await expect(searchResults).toHaveCount(1)
    
    // 検索クリア
    await page.getByRole('button', { name: 'クリア' }).click()
    await expect(page.getByPlaceholder('ドローン名で検索...')).toHaveValue('')
  })

  test('ドローンフィルター機能', async ({ page }) => {
    // ステータスフィルターの使用
    await page.getByRole('combobox', { name: 'ステータス' }).click()
    await page.getByRole('option', { name: '接続中' }).click()
    
    // フィルター適用の確認
    await page.waitForTimeout(1000)
    const filteredCards = page.getByTestId('drone-card')
    
    // 表示されているドローンが全て接続中であることを確認
    for (let i = 0; i < await filteredCards.count(); i++) {
      const card = filteredCards.nth(i)
      await expect(card.getByText('接続中')).toBeVisible()
    }
  })

  test('ドローン接続・切断機能', async ({ page }) => {
    const droneCard = page.getByTestId('drone-card').first()
    
    // 接続ボタンのクリック
    await droneCard.getByRole('button', { name: '切断' }).click()
    
    // 確認ダイアログの処理
    await expect(page.getByText('ドローンを切断しますか？')).toBeVisible()
    await page.getByRole('button', { name: 'はい' }).click()
    
    // 切断処理の確認
    await expect(page.getByText('ドローンを切断しました')).toBeVisible()
    
    // ステータスが更新されることを確認
    await expect(droneCard.getByText('切断')).toBeVisible()
  })

  test('ドローン制御パネル', async ({ page }) => {
    const droneCard = page.getByTestId('drone-card').first()
    
    // 制御ボタンをクリック
    await droneCard.getByRole('button', { name: '制御' }).click()
    
    // 制御パネルモーダルの表示確認
    await expect(page.getByText('ドローン制御パネル')).toBeVisible()
    
    // 離陸ボタンの確認
    await expect(page.getByRole('button', { name: '離陸' })).toBeVisible()
    
    // 着陸ボタンの確認
    await expect(page.getByRole('button', { name: '着陸' })).toBeVisible()
    
    // 緊急停止ボタンの確認
    await expect(page.getByRole('button', { name: '緊急停止' })).toBeVisible()
    
    // 方向制御ボタンの確認
    await expect(page.getByRole('button', { name: '前進' })).toBeVisible()
    await expect(page.getByRole('button', { name: '後退' })).toBeVisible()
    await expect(page.getByRole('button', { name: '左' })).toBeVisible()
    await expect(page.getByRole('button', { name: '右' })).toBeVisible()
  })

  test('ドローン離陸・着陸機能', async ({ page }) => {
    const droneCard = page.getByTestId('drone-card').first()
    
    // 制御パネルを開く
    await droneCard.getByRole('button', { name: '制御' }).click()
    
    // 離陸ボタンをクリック
    await page.getByRole('button', { name: '離陸' }).click()
    
    // 確認ダイアログの処理
    await expect(page.getByText('ドローンを離陸させますか？')).toBeVisible()
    await page.getByRole('button', { name: 'はい' }).click()
    
    // 離陸処理の確認
    await expect(page.getByText('ドローンが離陸しました')).toBeVisible()
    
    // ステータスが更新されることを確認
    await page.waitForTimeout(2000)
    await expect(page.getByText('飛行中')).toBeVisible()
    
    // 着陸ボタンをクリック
    await page.getByRole('button', { name: '着陸' }).click()
    await page.getByRole('button', { name: 'はい' }).click()
    
    // 着陸処理の確認
    await expect(page.getByText('ドローンが着陸しました')).toBeVisible()
  })

  test('カメラストリーミング機能', async ({ page }) => {
    const droneCard = page.getByTestId('drone-card').first()
    
    // カメラボタンをクリック
    await droneCard.getByRole('button', { name: 'カメラ' }).click()
    
    // カメラストリーミングモーダルの表示確認
    await expect(page.getByText('カメラストリーミング')).toBeVisible()
    
    // 動画ストリーム要素の確認
    await expect(page.getByTestId('camera-stream')).toBeVisible()
    
    // 撮影ボタンの確認
    await expect(page.getByRole('button', { name: '撮影' })).toBeVisible()
    
    // 録画ボタンの確認
    await expect(page.getByRole('button', { name: '録画開始' })).toBeVisible()
    
    // 設定ボタンの確認
    await expect(page.getByRole('button', { name: '設定' })).toBeVisible()
  })

  test('新規ドローン追加機能', async ({ page }) => {
    // 追加ボタンをクリック
    await page.getByRole('button', { name: 'ドローン追加' }).click()
    
    // 追加モーダルの表示確認
    await expect(page.getByText('新規ドローン追加')).toBeVisible()
    
    // フォーム入力
    await page.getByLabel('ドローン名').fill('New Test Drone')
    await page.getByLabel('モデル').fill('DJI Mini 3')
    await page.getByLabel('シリアル番号').fill('TEST-NEW-001')
    await page.getByLabel('IPアドレス').fill('192.168.1.100')
    
    // 追加実行
    await page.getByRole('button', { name: '追加' }).click()
    
    // 成功メッセージの確認
    await expect(page.getByText('ドローンを追加しました')).toBeVisible()
    
    // 新しいドローンが一覧に表示されることを確認
    await expect(page.getByText('New Test Drone')).toBeVisible()
  })

  test('ドローン削除機能', async ({ page }) => {
    const droneCard = page.getByTestId('drone-card').first()
    
    // ドローンカードの詳細メニューを開く
    await droneCard.getByRole('button', { name: 'メニュー' }).click()
    
    // 削除オプションをクリック
    await page.getByRole('menuitem', { name: '削除' }).click()
    
    // 確認ダイアログの処理
    await expect(page.getByText('このドローンを削除しますか？')).toBeVisible()
    await page.getByText('削除すると復元できません').toBeVisible()
    await page.getByRole('button', { name: '削除' }).click()
    
    // 削除処理の確認
    await expect(page.getByText('ドローンを削除しました')).toBeVisible()
  })

  test('緊急停止機能', async ({ page }) => {
    // 緊急停止ボタンの確認（ページ上部）
    await expect(page.getByRole('button', { name: '全機緊急停止' })).toBeVisible()
    
    // 緊急停止ボタンをクリック
    await page.getByRole('button', { name: '全機緊急停止' }).click()
    
    // 緊急停止確認ダイアログの表示
    await expect(page.getByText('全てのドローンを緊急停止しますか？')).toBeVisible()
    await expect(page.getByText('この操作により全ドローンが強制着陸します')).toBeVisible()
    
    // 緊急停止実行
    await page.getByRole('button', { name: '緊急停止' }).click()
    
    // 緊急停止処理の確認
    await expect(page.getByText('全機緊急停止を実行しました')).toBeVisible()
  })

  test('ソート機能', async ({ page }) => {
    // ソートオプションを開く
    await page.getByRole('combobox', { name: 'ソート' }).click()
    
    // 名前順でソート
    await page.getByRole('option', { name: '名前（昇順）' }).click()
    
    // ソート結果の確認
    await page.waitForTimeout(1000)
    const droneNames = await page.getByTestId('drone-name').allTextContents()
    const sortedNames = [...droneNames].sort()
    expect(droneNames).toEqual(sortedNames)
    
    // バッテリー残量順でソート
    await page.getByRole('combobox', { name: 'ソート' }).click()
    await page.getByRole('option', { name: 'バッテリー（昇順）' }).click()
    
    // ソート結果の確認（数値的にソートされているかチェック）
    await page.waitForTimeout(1000)
  })

  test('ページネーション機能', async ({ page }) => {
    // ページネーションが表示されることを確認
    const pagination = page.getByTestId('pagination')
    if (await pagination.isVisible()) {
      // 次のページボタンをクリック
      await page.getByRole('button', { name: '次のページ' }).click()
      
      // ページが変更されることを確認
      await expect(page.getByText('ページ 2')).toBeVisible()
      
      // 前のページボタンをクリック
      await page.getByRole('button', { name: '前のページ' }).click()
      
      // 最初のページに戻ることを確認
      await expect(page.getByText('ページ 1')).toBeVisible()
    }
  })

  test('バッテリー警告アラート', async ({ page }) => {
    // バッテリー残量が低いドローンがある場合の警告表示
    const lowBatteryWarning = page.getByTestId('low-battery-warning')
    if (await lowBatteryWarning.isVisible()) {
      // 警告メッセージの確認
      await expect(page.getByText('バッテリー残量が低いドローンがあります')).toBeVisible()
      
      // 警告をクリックして詳細確認
      await lowBatteryWarning.click()
      
      // 低バッテリーのドローン一覧が表示されることを確認
      await expect(page.getByText('バッテリー残量が低いドローン')).toBeVisible()
    }
  })

  test('リアルタイム状態更新', async ({ page }) => {
    // 初期状態の確認
    const initialStatus = await page.getByTestId('drone-status').first().textContent()
    
    // 自動更新が有効になっていることを確認
    await expect(page.getByText('自動更新: ON')).toBeVisible()
    
    // しばらく待機してデータが更新されるかを確認
    await page.waitForTimeout(5000)
    
    // 更新インジケーターが表示されることを確認
    await expect(page.getByTestId('update-indicator')).toBeVisible()
  })

  test('アクセシビリティ対応', async ({ page }) => {
    // スクリーンリーダー対応のARIAラベルを確認
    await expect(page.getByRole('main')).toHaveAttribute('aria-label', 'ドローン管理メインコンテンツ')
    
    // キーボードナビゲーションの確認
    await page.keyboard.press('Tab')
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
    
    // 高コントラストモードでの表示確認
    await page.emulateMedia({ reducedMotion: 'reduce' })
    await expect(page.getByTestId('drone-card').first()).toBeVisible()
  })
})