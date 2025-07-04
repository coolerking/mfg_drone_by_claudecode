import { test, expect } from '@playwright/test'

test.describe('認証フロー', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('ログイン画面の表示と認証フロー', async ({ page }) => {
    // ログイン画面にリダイレクトされることを確認
    await expect(page).toHaveURL('/login')
    
    // ログインフォームの要素が表示されていることを確認
    await expect(page.getByRole('heading', { name: 'ログイン' })).toBeVisible()
    await expect(page.getByLabel('ユーザー名')).toBeVisible()
    await expect(page.getByLabel('パスワード')).toBeVisible()
    await expect(page.getByRole('button', { name: 'ログイン' })).toBeVisible()
  })

  test('無効な認証情報でのログイン試行', async ({ page }) => {
    await page.goto('/login')
    
    // 無効な認証情報を入力
    await page.getByLabel('ユーザー名').fill('invalid')
    await page.getByLabel('パスワード').fill('invalid')
    await page.getByRole('button', { name: 'ログイン' }).click()
    
    // エラーメッセージが表示されることを確認
    await expect(page.getByText('ユーザー名またはパスワードが正しくありません')).toBeVisible()
  })

  test('有効な認証情報でのログイン', async ({ page }) => {
    await page.goto('/login')
    
    // 有効な認証情報を入力（デモ用）
    await page.getByLabel('ユーザー名').fill('admin')
    await page.getByLabel('パスワード').fill('password')
    await page.getByRole('button', { name: 'ログイン' }).click()
    
    // ダッシュボードにリダイレクトされることを確認
    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByRole('heading', { name: 'ダッシュボード' })).toBeVisible()
  })

  test('Remember Me機能', async ({ page }) => {
    await page.goto('/login')
    
    // Remember Me チェックボックスをクリック
    await page.getByLabel('ログイン状態を保持する').check()
    
    // ログイン実行
    await page.getByLabel('ユーザー名').fill('admin')
    await page.getByLabel('パスワード').fill('password')
    await page.getByRole('button', { name: 'ログイン' }).click()
    
    // ダッシュボードに移動
    await expect(page).toHaveURL('/dashboard')
    
    // ページをリロード
    await page.reload()
    
    // ログイン状態が維持されていることを確認
    await expect(page).toHaveURL('/dashboard')
  })

  test('ログアウト機能', async ({ page }) => {
    // まずログイン
    await page.goto('/login')
    await page.getByLabel('ユーザー名').fill('admin')
    await page.getByLabel('パスワード').fill('password')
    await page.getByRole('button', { name: 'ログイン' }).click()
    
    await expect(page).toHaveURL('/dashboard')
    
    // ユーザーメニューを開く
    await page.getByRole('button', { name: 'ユーザーメニュー' }).click()
    
    // ログアウトボタンをクリック
    await page.getByRole('menuitem', { name: 'ログアウト' }).click()
    
    // ログイン画面にリダイレクトされることを確認
    await expect(page).toHaveURL('/login')
  })

  test('パスワード強度インジケーター', async ({ page }) => {
    await page.goto('/login')
    
    const passwordInput = page.getByLabel('パスワード')
    
    // 弱いパスワード
    await passwordInput.fill('123')
    await expect(page.getByText('弱い')).toBeVisible()
    
    // 中程度のパスワード
    await passwordInput.fill('password123')
    await expect(page.getByText('中程度')).toBeVisible()
    
    // 強いパスワード
    await passwordInput.fill('StrongP@ssw0rd!')
    await expect(page.getByText('強い')).toBeVisible()
  })

  test('セキュリティ機能（試行回数制限）', async ({ page }) => {
    await page.goto('/login')
    
    // 3回連続で無効なログインを試行
    for (let i = 0; i < 3; i++) {
      await page.getByLabel('ユーザー名').fill('invalid')
      await page.getByLabel('パスワード').fill('invalid')
      await page.getByRole('button', { name: 'ログイン' }).click()
      
      await expect(page.getByText('ユーザー名またはパスワードが正しくありません')).toBeVisible()
    }
    
    // 4回目の試行でアカウントロックメッセージが表示されることを確認
    await page.getByLabel('ユーザー名').fill('invalid')
    await page.getByLabel('パスワード').fill('invalid')
    await page.getByRole('button', { name: 'ログイン' }).click()
    
    await expect(page.getByText('アカウントが一時的にロックされました')).toBeVisible()
  })

  test('レスポンシブデザイン（モバイル）', async ({ page }) => {
    // モバイルビューポートに設定
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/login')
    
    // モバイルでも適切に表示されることを確認
    await expect(page.getByRole('heading', { name: 'ログイン' })).toBeVisible()
    await expect(page.getByLabel('ユーザー名')).toBeVisible()
    await expect(page.getByLabel('パスワード')).toBeVisible()
    
    // ログインボタンが適切なサイズで表示されることを確認
    const loginButton = page.getByRole('button', { name: 'ログイン' })
    await expect(loginButton).toBeVisible()
    
    // タッチフレンドリーなサイズかを確認（最小44px）
    const buttonBox = await loginButton.boundingBox()
    expect(buttonBox?.height).toBeGreaterThanOrEqual(44)
  })
})