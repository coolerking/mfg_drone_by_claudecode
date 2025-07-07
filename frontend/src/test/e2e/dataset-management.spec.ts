import { test, expect } from '@playwright/test';
import { TestHelperFactory } from './helpers/test-helpers';

/**
 * データセット管理E2Eテスト
 * データセットの一覧、作成、編集、削除、検索、インポート/エクスポート機能をテスト
 */

test.describe('Dataset Management E2E Tests', () => {
  let helpers: ReturnType<typeof TestHelperFactory.createHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = TestHelperFactory.createHelpers(page);
    await helpers.auth.login();
    await helpers.navigation.navigateToPage('dataset-management');
  });

  test.afterEach(async ({ page }) => {
    await helpers.cleanup.cleanupTestData();
  });

  test.describe('Dataset List Operations', () => {
    test('should display dataset list correctly', async ({ page }) => {
      // データセット一覧の表示確認
      await helpers.component.waitForComponent('[data-testid="dataset-list"]');
      
      // ヘッダーの確認
      await expect(page.locator('[data-testid="page-title"]')).toHaveText('データセット管理');
      
      // 操作ボタンの確認
      await expect(page.locator('[data-testid="create-dataset-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="import-dataset-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="export-dataset-button"]')).toBeVisible();
      
      // 検索フィールドの確認
      await expect(page.locator('[data-testid="dataset-search"]')).toBeVisible();
      await expect(page.locator('[data-testid="dataset-filter"]')).toBeVisible();
    });

    test('should handle empty dataset list', async ({ page }) => {
      // 空のデータセットリストの表示確認
      await helpers.api.mockApiResponse('/api/datasets', { data: [], total: 0 });
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="empty-state"]');
      
      await expect(page.locator('[data-testid="empty-state"]')).toBeVisible();
      await expect(page.locator('[data-testid="empty-state"]')).toContainText('データセットがありません');
    });

    test('should display dataset cards with correct information', async ({ page }) => {
      // データセットカードの表示確認
      await helpers.component.waitForTable('[data-testid="dataset-grid"]');
      
      const datasetCards = page.locator('[data-testid="dataset-card"]');
      const firstCard = datasetCards.first();
      
      // カードの基本情報
      await expect(firstCard.locator('[data-testid="dataset-name"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="dataset-type"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="dataset-image-count"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="dataset-created-date"]')).toBeVisible();
      
      // アクションボタン
      await expect(firstCard.locator('[data-testid="view-dataset"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="edit-dataset"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="delete-dataset"]')).toBeVisible();
    });
  });

  test.describe('Dataset Creation', () => {
    test('should create new dataset successfully', async ({ page }) => {
      // 新しいデータセットの作成
      await page.click('[data-testid="create-dataset-button"]');
      
      // モーダルの確認
      await helpers.component.waitForComponent('[data-testid="create-dataset-modal"]');
      await expect(page.locator('[data-testid="modal-title"]')).toHaveText('新しいデータセット');
      
      // フォームの入力
      const datasetData = {
        'dataset-name': 'E2E Test Dataset',
        'dataset-description': 'E2E テスト用のデータセット',
        'dataset-tags': 'test, e2e, automation'
      };
      
      await helpers.form.fillForm(datasetData);
      await helpers.component.selectOption('[data-testid="dataset-type"]', 'object_detection');
      
      // 保存ボタンのクリック
      await page.click('[data-testid="save-dataset-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/datasets', 'POST');
      
      // 成功メッセージの確認
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="success-message"]')).toContainText('データセットが作成されました');
      
      // 一覧に新しいデータセットが表示されることを確認
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      await expect(page.locator('[data-testid="dataset-card"]').filter({ hasText: 'E2E Test Dataset' })).toBeVisible();
    });

    test('should validate required fields', async ({ page }) => {
      // 必須フィールドのバリデーション確認
      await page.click('[data-testid="create-dataset-button"]');
      await helpers.component.waitForComponent('[data-testid="create-dataset-modal"]');
      
      // 空のフォームで保存を試行
      await page.click('[data-testid="save-dataset-button"]');
      
      // エラーメッセージの確認
      await expect(page.locator('[data-testid="error-dataset-name"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-dataset-name"]')).toContainText('データセット名は必須です');
      
      await expect(page.locator('[data-testid="error-dataset-type"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-dataset-type"]')).toContainText('データセットタイプは必須です');
    });

    test('should handle dataset creation failure', async ({ page }) => {
      // データセット作成の失敗ケース
      await page.click('[data-testid="create-dataset-button"]');
      await helpers.component.waitForComponent('[data-testid="create-dataset-modal"]');
      
      // API エラーのモック
      await helpers.api.mockApiResponse('/api/datasets', {
        error: 'Dataset creation failed',
        statusCode: 500
      });
      
      // フォームの入力
      await helpers.form.fillForm({
        'dataset-name': 'Failed Dataset',
        'dataset-description': 'This should fail'
      });
      
      await page.click('[data-testid="save-dataset-button"]');
      
      // エラーメッセージの確認
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-message"]')).toContainText('データセットの作成に失敗しました');
    });
  });

  test.describe('Dataset Editing', () => {
    test('should edit existing dataset', async ({ page }) => {
      // 既存データセットの編集
      const testDataset = await helpers.data.createTestDataset('Edit Test Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      // 編集ボタンのクリック
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Edit Test Dataset' })
        .locator('[data-testid="edit-dataset"]').click();
      
      // 編集モーダルの確認
      await helpers.component.waitForComponent('[data-testid="edit-dataset-modal"]');
      await expect(page.locator('[data-testid="modal-title"]')).toHaveText('データセットの編集');
      
      // フォームの値が設定されていることを確認
      await expect(page.locator('[data-testid="dataset-name"]')).toHaveValue('Edit Test Dataset');
      
      // 値の変更
      await page.fill('[data-testid="dataset-name"]', 'Updated Test Dataset');
      await page.fill('[data-testid="dataset-description"]', 'Updated description');
      
      // 保存
      await page.click('[data-testid="save-dataset-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/datasets', 'PUT');
      
      // 更新確認
      await expect(page.locator('[data-testid="success-message"]')).toContainText('データセットが更新されました');
    });

    test('should cancel dataset editing', async ({ page }) => {
      // データセット編集のキャンセル
      const testDataset = await helpers.data.createTestDataset('Cancel Edit Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Cancel Edit Dataset' })
        .locator('[data-testid="edit-dataset"]').click();
      
      await helpers.component.waitForComponent('[data-testid="edit-dataset-modal"]');
      
      // 値の変更
      await page.fill('[data-testid="dataset-name"]', 'Changed Name');
      
      // キャンセル
      await page.click('[data-testid="cancel-button"]');
      
      // モーダルが閉じることを確認
      await expect(page.locator('[data-testid="edit-dataset-modal"]')).not.toBeVisible();
      
      // 元の値が保持されていることを確認
      await expect(page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Cancel Edit Dataset' })).toBeVisible();
    });
  });

  test.describe('Dataset Deletion', () => {
    test('should delete dataset with confirmation', async ({ page }) => {
      // データセットの削除
      const testDataset = await helpers.data.createTestDataset('Delete Test Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      // 削除ボタンのクリック
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Delete Test Dataset' })
        .locator('[data-testid="delete-dataset"]').click();
      
      // 確認ダイアログの表示
      await helpers.component.waitForComponent('[data-testid="confirm-delete-dialog"]');
      await expect(page.locator('[data-testid="confirm-message"]')).toContainText('このデータセットを削除しますか？');
      
      // 削除の確認
      await page.click('[data-testid="confirm-delete"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/datasets', 'DELETE');
      
      // 削除確認
      await expect(page.locator('[data-testid="success-message"]')).toContainText('データセットが削除されました');
      
      // 一覧から削除されることを確認
      await expect(page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Delete Test Dataset' })).not.toBeVisible();
    });

    test('should cancel dataset deletion', async ({ page }) => {
      // データセット削除のキャンセル
      const testDataset = await helpers.data.createTestDataset('Cancel Delete Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Cancel Delete Dataset' })
        .locator('[data-testid="delete-dataset"]').click();
      
      await helpers.component.waitForComponent('[data-testid="confirm-delete-dialog"]');
      
      // キャンセル
      await page.click('[data-testid="cancel-delete"]');
      
      // ダイアログが閉じることを確認
      await expect(page.locator('[data-testid="confirm-delete-dialog"]')).not.toBeVisible();
      
      // データセットが残っていることを確認
      await expect(page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Cancel Delete Dataset' })).toBeVisible();
    });
  });

  test.describe('Dataset Search and Filter', () => {
    test('should search datasets by name', async ({ page }) => {
      // 検索機能のテスト
      await helpers.data.createTestDataset('Searchable Dataset');
      await helpers.data.createTestDataset('Another Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      // 検索
      await helpers.component.searchInTable('Searchable');
      
      // 結果の確認
      await expect(page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Searchable Dataset' })).toBeVisible();
      await expect(page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Another Dataset' })).not.toBeVisible();
    });

    test('should filter datasets by type', async ({ page }) => {
      // タイプによるフィルタリング
      await helpers.component.waitForComponent('[data-testid="dataset-filter"]');
      
      // フィルターの適用
      await page.selectOption('[data-testid="dataset-filter"]', 'object_detection');
      
      // フィルター結果の確認
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      // すべてのカードが指定されたタイプであることを確認
      const cards = page.locator('[data-testid="dataset-card"]');
      const count = await cards.count();
      
      for (let i = 0; i < count; i++) {
        await expect(cards.nth(i).locator('[data-testid="dataset-type"]')).toContainText('object_detection');
      }
    });

    test('should handle no search results', async ({ page }) => {
      // 検索結果なしのケース
      await helpers.component.waitForComponent('[data-testid="dataset-list"]');
      
      // 存在しないデータセットを検索
      await helpers.component.searchInTable('NonExistentDataset');
      
      // 結果なしの表示確認
      await expect(page.locator('[data-testid="no-results"]')).toBeVisible();
      await expect(page.locator('[data-testid="no-results"]')).toContainText('検索結果がありません');
    });
  });

  test.describe('Dataset Import/Export', () => {
    test('should open import dialog', async ({ page }) => {
      // インポートダイアログの表示
      await page.click('[data-testid="import-dataset-button"]');
      
      await helpers.component.waitForComponent('[data-testid="import-dataset-modal"]');
      await expect(page.locator('[data-testid="modal-title"]')).toHaveText('データセットのインポート');
      
      // インポートフォームの確認
      await expect(page.locator('[data-testid="import-file-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="import-format-select"]')).toBeVisible();
      await expect(page.locator('[data-testid="import-button"]')).toBeVisible();
    });

    test('should validate import file format', async ({ page }) => {
      // インポートファイル形式のバリデーション
      await page.click('[data-testid="import-dataset-button"]');
      await helpers.component.waitForComponent('[data-testid="import-dataset-modal"]');
      
      // 不正なファイル形式でのインポート試行
      await page.click('[data-testid="import-button"]');
      
      // エラーメッセージの確認
      await expect(page.locator('[data-testid="error-import-file"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-import-file"]')).toContainText('インポートファイルを選択してください');
    });

    test('should export dataset', async ({ page }) => {
      // データセットのエクスポート
      const testDataset = await helpers.data.createTestDataset('Export Test Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      // エクスポートボタンのクリック
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Export Test Dataset' })
        .locator('[data-testid="export-dataset"]').click();
      
      // エクスポートダイアログの確認
      await helpers.component.waitForComponent('[data-testid="export-dataset-modal"]');
      await expect(page.locator('[data-testid="modal-title"]')).toHaveText('データセットのエクスポート');
      
      // エクスポート形式の選択
      await page.selectOption('[data-testid="export-format-select"]', 'json');
      
      // エクスポート実行
      await page.click('[data-testid="export-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/datasets/export', 'POST');
      
      // 成功メッセージの確認
      await expect(page.locator('[data-testid="success-message"]')).toContainText('エクスポートが完了しました');
    });
  });

  test.describe('Dataset Image Management', () => {
    test('should view dataset images', async ({ page }) => {
      // データセット画像の表示
      const testDataset = await helpers.data.createTestDataset('Image Test Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      // 詳細表示ボタンのクリック
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Image Test Dataset' })
        .locator('[data-testid="view-dataset"]').click();
      
      // 画像ギャラリーの確認
      await helpers.component.waitForComponent('[data-testid="image-gallery"]');
      await expect(page.locator('[data-testid="gallery-title"]')).toContainText('Image Test Dataset');
      
      // 画像アップロードボタンの確認
      await expect(page.locator('[data-testid="upload-images-button"]')).toBeVisible();
      
      // 画像一覧の確認
      await expect(page.locator('[data-testid="image-grid"]')).toBeVisible();
    });

    test('should upload images to dataset', async ({ page }) => {
      // データセットへの画像アップロード
      const testDataset = await helpers.data.createTestDataset('Upload Test Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Upload Test Dataset' })
        .locator('[data-testid="view-dataset"]').click();
      
      await helpers.component.waitForComponent('[data-testid="image-gallery"]');
      
      // アップロードボタンのクリック
      await page.click('[data-testid="upload-images-button"]');
      
      // アップロードダイアログの確認
      await helpers.component.waitForComponent('[data-testid="upload-images-modal"]');
      await expect(page.locator('[data-testid="modal-title"]')).toHaveText('画像のアップロード');
      
      // ファイル選択エリアの確認
      await expect(page.locator('[data-testid="file-drop-area"]')).toBeVisible();
      await expect(page.locator('[data-testid="file-input"]')).toBeVisible();
    });

    test('should label images', async ({ page }) => {
      // 画像のラベリング
      const testDataset = await helpers.data.createTestDataset('Label Test Dataset');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Label Test Dataset' })
        .locator('[data-testid="view-dataset"]').click();
      
      await helpers.component.waitForComponent('[data-testid="image-gallery"]');
      
      // 画像が存在する場合のラベリング
      const images = page.locator('[data-testid="image-item"]');
      const imageCount = await images.count();
      
      if (imageCount > 0) {
        // 最初の画像をクリック
        await images.first().click();
        
        // ラベリングツールの確認
        await helpers.component.waitForComponent('[data-testid="labeling-tool"]');
        await expect(page.locator('[data-testid="labeling-canvas"]')).toBeVisible();
        await expect(page.locator('[data-testid="label-list"]')).toBeVisible();
      }
    });
  });

  test.describe('Dataset Performance', () => {
    test('should load dataset list within performance threshold', async ({ page }) => {
      // パフォーマンステスト：データセット一覧の読み込み
      const loadTime = await helpers.performance.measurePageLoad('/dataset-management');
      
      expect(loadTime).toBeLessThan(3000); // 3秒以内
    });

    test('should handle large dataset lists efficiently', async ({ page }) => {
      // 大量データセットの効率的な処理
      const largeDatasetList = Array.from({ length: 100 }, (_, i) => ({
        id: i,
        name: `Dataset ${i}`,
        type: 'object_detection',
        imageCount: Math.floor(Math.random() * 1000)
      }));
      
      await helpers.api.mockApiResponse('/api/datasets', { data: largeDatasetList, total: 100 });
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="dataset-list"]');
      
      // 仮想スクロールの確認
      await expect(page.locator('[data-testid="virtual-scroll"]')).toBeVisible();
      
      // 検索性能の確認
      const searchTime = await helpers.performance.measureInteraction('[data-testid="search-input"]', 'fill', 'Dataset 50');
      expect(searchTime).toBeLessThan(1000); // 1秒以内
    });
  });
});