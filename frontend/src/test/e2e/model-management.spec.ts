import { test, expect } from '@playwright/test';
import { TestHelperFactory } from './helpers/test-helpers';

/**
 * モデル管理E2Eテスト
 * モデルの一覧、作成、学習、評価、デプロイ、バージョン管理機能をテスト
 */

test.describe('Model Management E2E Tests', () => {
  let helpers: ReturnType<typeof TestHelperFactory.createHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = TestHelperFactory.createHelpers(page);
    await helpers.auth.login();
    await helpers.navigation.navigateToPage('model-management');
  });

  test.afterEach(async ({ page }) => {
    await helpers.cleanup.cleanupTestData();
  });

  test.describe('Model List Operations', () => {
    test('should display model list correctly', async ({ page }) => {
      // モデル一覧の表示確認
      await helpers.component.waitForComponent('[data-testid="model-list"]');
      
      // ヘッダーの確認
      await expect(page.locator('[data-testid="page-title"]')).toHaveText('モデル管理');
      
      // タブの確認
      await expect(page.locator('[data-testid="models-tab"]')).toBeVisible();
      await expect(page.locator('[data-testid="training-jobs-tab"]')).toBeVisible();
      await expect(page.locator('[data-testid="deployments-tab"]')).toBeVisible();
      
      // 操作ボタンの確認
      await expect(page.locator('[data-testid="create-model-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="import-model-button"]')).toBeVisible();
      
      // 検索・フィルターの確認
      await expect(page.locator('[data-testid="model-search"]')).toBeVisible();
      await expect(page.locator('[data-testid="model-filter"]')).toBeVisible();
    });

    test('should display model cards with correct information', async ({ page }) => {
      // モデルカードの表示確認
      await helpers.component.waitForTable('[data-testid="model-grid"]');
      
      const modelCards = page.locator('[data-testid="model-card"]');
      if (await modelCards.count() > 0) {
        const firstCard = modelCards.first();
        
        // カードの基本情報
        await expect(firstCard.locator('[data-testid="model-name"]')).toBeVisible();
        await expect(firstCard.locator('[data-testid="model-algorithm"]')).toBeVisible();
        await expect(firstCard.locator('[data-testid="model-framework"]')).toBeVisible();
        await expect(firstCard.locator('[data-testid="model-status"]')).toBeVisible();
        await expect(firstCard.locator('[data-testid="model-accuracy"]')).toBeVisible();
        
        // アクションボタン
        await expect(firstCard.locator('[data-testid="view-model"]')).toBeVisible();
        await expect(firstCard.locator('[data-testid="train-model"]')).toBeVisible();
        await expect(firstCard.locator('[data-testid="deploy-model"]')).toBeVisible();
        await expect(firstCard.locator('[data-testid="delete-model"]')).toBeVisible();
      }
    });

    test('should handle empty model list', async ({ page }) => {
      // 空のモデルリストの表示確認
      await helpers.api.mockApiResponse('/api/models', { data: [], total: 0 });
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="empty-state"]');
      
      await expect(page.locator('[data-testid="empty-state"]')).toBeVisible();
      await expect(page.locator('[data-testid="empty-state"]')).toContainText('モデルがありません');
      await expect(page.locator('[data-testid="create-first-model-button"]')).toBeVisible();
    });
  });

  test.describe('Model Creation', () => {
    test('should create new model successfully', async ({ page }) => {
      // 新しいモデルの作成
      await page.click('[data-testid="create-model-button"]');
      
      // モーダルの確認
      await helpers.component.waitForComponent('[data-testid="create-model-modal"]');
      await expect(page.locator('[data-testid="modal-title"]')).toHaveText('新しいモデル');
      
      // フォームの入力
      const modelData = {
        'model-name': 'E2E Test Model',
        'model-description': 'E2E テスト用のモデル',
        'model-tags': 'test, e2e, automation'
      };
      
      await helpers.form.fillForm(modelData);
      await helpers.component.selectOption('[data-testid="model-algorithm"]', 'yolov8');
      await helpers.component.selectOption('[data-testid="model-framework"]', 'pytorch');
      
      // 保存ボタンのクリック
      await page.click('[data-testid="save-model-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/models', 'POST');
      
      // 成功メッセージの確認
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="success-message"]')).toContainText('モデルが作成されました');
      
      // 一覧に新しいモデルが表示されることを確認
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      await expect(page.locator('[data-testid="model-card"]').filter({ hasText: 'E2E Test Model' })).toBeVisible();
    });

    test('should validate required fields', async ({ page }) => {
      // 必須フィールドのバリデーション確認
      await page.click('[data-testid="create-model-button"]');
      await helpers.component.waitForComponent('[data-testid="create-model-modal"]');
      
      // 空のフォームで保存を試行
      await page.click('[data-testid="save-model-button"]');
      
      // エラーメッセージの確認
      await expect(page.locator('[data-testid="error-model-name"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-model-name"]')).toContainText('モデル名は必須です');
      
      await expect(page.locator('[data-testid="error-model-algorithm"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-model-algorithm"]')).toContainText('アルゴリズムは必須です');
      
      await expect(page.locator('[data-testid="error-model-framework"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-model-framework"]')).toContainText('フレームワークは必須です');
    });

    test('should configure advanced model settings', async ({ page }) => {
      // 高度なモデル設定の確認
      await page.click('[data-testid="create-model-button"]');
      await helpers.component.waitForComponent('[data-testid="create-model-modal"]');
      
      // 高度な設定タブのクリック
      await page.click('[data-testid="advanced-settings-tab"]');
      
      // 高度な設定項目の確認
      await expect(page.locator('[data-testid="batch-size-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="learning-rate-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="epochs-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="optimizer-select"]')).toBeVisible();
      
      // 設定値の入力
      await page.fill('[data-testid="batch-size-input"]', '16');
      await page.fill('[data-testid="learning-rate-input"]', '0.001');
      await page.fill('[data-testid="epochs-input"]', '100');
      await page.selectOption('[data-testid="optimizer-select"]', 'adam');
      
      // 基本設定タブに戻る
      await page.click('[data-testid="basic-settings-tab"]');
      
      // 基本情報の入力
      await helpers.form.fillForm({
        'model-name': 'Advanced Test Model',
        'model-description': 'Advanced settings test'
      });
      
      await helpers.component.selectOption('[data-testid="model-algorithm"]', 'yolov8');
      await helpers.component.selectOption('[data-testid="model-framework"]', 'pytorch');
      
      // 保存
      await page.click('[data-testid="save-model-button"]');
      
      // 成功確認
      await helpers.api.waitForApiCall('/api/models', 'POST');
      await expect(page.locator('[data-testid="success-message"]')).toContainText('モデルが作成されました');
    });
  });

  test.describe('Model Training', () => {
    test('should start model training successfully', async ({ page }) => {
      // モデル学習の開始
      const testModel = await helpers.data.createTestModel('Training Test Model');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      
      // 学習ボタンのクリック
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Training Test Model' })
        .locator('[data-testid="train-model"]').click();
      
      // 学習設定ダイアログの確認
      await helpers.component.waitForComponent('[data-testid="training-config-modal"]');
      await expect(page.locator('[data-testid="modal-title"]')).toHaveText('学習設定');
      
      // データセット選択
      await page.selectOption('[data-testid="training-dataset-select"]', 'test-dataset');
      
      // 学習パラメータの設定
      await page.fill('[data-testid="training-epochs"]', '10');
      await page.fill('[data-testid="training-batch-size"]', '8');
      
      // 学習開始
      await page.click('[data-testid="start-training-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/models/train', 'POST');
      
      // 学習ジョブ画面への遷移確認
      await expect(page.locator('[data-testid="training-progress"]')).toBeVisible();
      await expect(page.locator('[data-testid="training-status"]')).toContainText('学習中');
    });

    test('should display training progress', async ({ page }) => {
      // 学習進捗の表示確認
      await page.click('[data-testid="training-jobs-tab"]');
      
      await helpers.component.waitForComponent('[data-testid="training-jobs-list"]');
      
      // 学習ジョブカードの確認
      const jobCards = page.locator('[data-testid="training-job-card"]');
      if (await jobCards.count() > 0) {
        const firstJob = jobCards.first();
        
        // ジョブ情報の確認
        await expect(firstJob.locator('[data-testid="job-id"]')).toBeVisible();
        await expect(firstJob.locator('[data-testid="job-status"]')).toBeVisible();
        await expect(firstJob.locator('[data-testid="job-progress"]')).toBeVisible();
        await expect(firstJob.locator('[data-testid="job-duration"]')).toBeVisible();
        
        // 進捗バーの確認
        await expect(firstJob.locator('[data-testid="progress-bar"]')).toBeVisible();
        
        // アクションボタン
        await expect(firstJob.locator('[data-testid="view-job-details"]')).toBeVisible();
        await expect(firstJob.locator('[data-testid="stop-training"]')).toBeVisible();
      }
    });

    test('should view training details', async ({ page }) => {
      // 学習詳細の表示
      await page.click('[data-testid="training-jobs-tab"]');
      await helpers.component.waitForComponent('[data-testid="training-jobs-list"]');
      
      const jobCards = page.locator('[data-testid="training-job-card"]');
      if (await jobCards.count() > 0) {
        // 詳細表示ボタンのクリック
        await jobCards.first().locator('[data-testid="view-job-details"]').click();
        
        // 詳細ダイアログの確認
        await helpers.component.waitForComponent('[data-testid="training-details-modal"]');
        await expect(page.locator('[data-testid="modal-title"]')).toContainText('学習詳細');
        
        // 詳細情報の確認
        await expect(page.locator('[data-testid="training-metrics"]')).toBeVisible();
        await expect(page.locator('[data-testid="loss-chart"]')).toBeVisible();
        await expect(page.locator('[data-testid="accuracy-chart"]')).toBeVisible();
        await expect(page.locator('[data-testid="training-logs"]')).toBeVisible();
        
        // タブの確認
        await expect(page.locator('[data-testid="metrics-tab"]')).toBeVisible();
        await expect(page.locator('[data-testid="logs-tab"]')).toBeVisible();
        await expect(page.locator('[data-testid="config-tab"]')).toBeVisible();
      }
    });

    test('should stop training job', async ({ page }) => {
      // 学習ジョブの停止
      await page.click('[data-testid="training-jobs-tab"]');
      await helpers.component.waitForComponent('[data-testid="training-jobs-list"]');
      
      const jobCards = page.locator('[data-testid="training-job-card"]');
      if (await jobCards.count() > 0) {
        // 停止ボタンのクリック
        await jobCards.first().locator('[data-testid="stop-training"]').click();
        
        // 確認ダイアログの表示
        await helpers.component.waitForComponent('[data-testid="confirm-stop-dialog"]');
        await expect(page.locator('[data-testid="confirm-message"]')).toContainText('学習を停止しますか？');
        
        // 停止の確認
        await page.click('[data-testid="confirm-stop"]');
        
        // API呼び出しの確認
        await helpers.api.waitForApiCall('/api/training-jobs/stop', 'POST');
        
        // ステータス更新の確認
        await expect(page.locator('[data-testid="job-status"]')).toContainText('停止中');
      }
    });
  });

  test.describe('Model Evaluation', () => {
    test('should evaluate model performance', async ({ page }) => {
      // モデル評価の実行
      const testModel = await helpers.data.createTestModel('Evaluation Test Model');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      
      // モデルカードの詳細表示
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Evaluation Test Model' })
        .locator('[data-testid="view-model"]').click();
      
      // モデル詳細ページの確認
      await helpers.component.waitForComponent('[data-testid="model-details"]');
      
      // 評価タブのクリック
      await page.click('[data-testid="evaluation-tab"]');
      
      // 評価実行ボタンのクリック
      await page.click('[data-testid="run-evaluation-button"]');
      
      // 評価設定ダイアログの確認
      await helpers.component.waitForComponent('[data-testid="evaluation-config-modal"]');
      
      // テストデータセットの選択
      await page.selectOption('[data-testid="evaluation-dataset-select"]', 'test-dataset');
      
      // 評価開始
      await page.click('[data-testid="start-evaluation-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/models/evaluate', 'POST');
      
      // 評価結果の表示確認
      await expect(page.locator('[data-testid="evaluation-progress"]')).toBeVisible();
    });

    test('should display evaluation metrics', async ({ page }) => {
      // 評価メトリクスの表示確認
      const testModel = await helpers.data.createTestModel('Metrics Test Model');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Metrics Test Model' })
        .locator('[data-testid="view-model"]').click();
      
      await helpers.component.waitForComponent('[data-testid="model-details"]');
      await page.click('[data-testid="evaluation-tab"]');
      
      // メトリクスの表示確認
      await expect(page.locator('[data-testid="accuracy-metric"]')).toBeVisible();
      await expect(page.locator('[data-testid="precision-metric"]')).toBeVisible();
      await expect(page.locator('[data-testid="recall-metric"]')).toBeVisible();
      await expect(page.locator('[data-testid="f1-score-metric"]')).toBeVisible();
      
      // チャートの確認
      await expect(page.locator('[data-testid="confusion-matrix"]')).toBeVisible();
      await expect(page.locator('[data-testid="roc-curve"]')).toBeVisible();
      await expect(page.locator('[data-testid="precision-recall-curve"]')).toBeVisible();
    });

    test('should compare model versions', async ({ page }) => {
      // モデルバージョンの比較
      const testModel = await helpers.data.createTestModel('Compare Test Model');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Compare Test Model' })
        .locator('[data-testid="view-model"]').click();
      
      await helpers.component.waitForComponent('[data-testid="model-details"]');
      
      // バージョン比較タブのクリック
      await page.click('[data-testid="version-comparison-tab"]');
      
      // 比較するバージョンの選択
      await page.selectOption('[data-testid="version-1-select"]', 'v1.0');
      await page.selectOption('[data-testid="version-2-select"]', 'v1.1');
      
      // 比較実行
      await page.click('[data-testid="compare-versions-button"]');
      
      // 比較結果の表示確認
      await expect(page.locator('[data-testid="comparison-table"]')).toBeVisible();
      await expect(page.locator('[data-testid="metrics-comparison-chart"]')).toBeVisible();
    });
  });

  test.describe('Model Deployment', () => {
    test('should deploy model successfully', async ({ page }) => {
      // モデルのデプロイ
      const testModel = await helpers.data.createTestModel('Deploy Test Model');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      
      // デプロイボタンのクリック
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Deploy Test Model' })
        .locator('[data-testid="deploy-model"]').click();
      
      // デプロイ設定ダイアログの確認
      await helpers.component.waitForComponent('[data-testid="deployment-config-modal"]');
      await expect(page.locator('[data-testid="modal-title"]')).toHaveText('デプロイ設定');
      
      // デプロイ設定の入力
      await page.fill('[data-testid="deployment-name"]', 'Test Deployment');
      await page.selectOption('[data-testid="deployment-environment"]', 'staging');
      await page.fill('[data-testid="deployment-instances"]', '2');
      
      // デプロイ開始
      await page.click('[data-testid="start-deployment-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/models/deploy', 'POST');
      
      // 成功メッセージの確認
      await expect(page.locator('[data-testid="success-message"]')).toContainText('デプロイが開始されました');
    });

    test('should view deployment status', async ({ page }) => {
      // デプロイステータスの表示
      await page.click('[data-testid="deployments-tab"]');
      
      await helpers.component.waitForComponent('[data-testid="deployments-list"]');
      
      // デプロイメントカードの確認
      const deploymentCards = page.locator('[data-testid="deployment-card"]');
      if (await deploymentCards.count() > 0) {
        const firstDeployment = deploymentCards.first();
        
        // デプロイメント情報の確認
        await expect(firstDeployment.locator('[data-testid="deployment-name"]')).toBeVisible();
        await expect(firstDeployment.locator('[data-testid="deployment-status"]')).toBeVisible();
        await expect(firstDeployment.locator('[data-testid="deployment-environment"]')).toBeVisible();
        await expect(firstDeployment.locator('[data-testid="deployment-instances"]')).toBeVisible();
        
        // アクションボタン
        await expect(firstDeployment.locator('[data-testid="view-deployment"]')).toBeVisible();
        await expect(firstDeployment.locator('[data-testid="scale-deployment"]')).toBeVisible();
        await expect(firstDeployment.locator('[data-testid="stop-deployment"]')).toBeVisible();
      }
    });

    test('should scale deployment', async ({ page }) => {
      // デプロイメントのスケーリング
      await page.click('[data-testid="deployments-tab"]');
      await helpers.component.waitForComponent('[data-testid="deployments-list"]');
      
      const deploymentCards = page.locator('[data-testid="deployment-card"]');
      if (await deploymentCards.count() > 0) {
        // スケールボタンのクリック
        await deploymentCards.first().locator('[data-testid="scale-deployment"]').click();
        
        // スケール設定ダイアログの確認
        await helpers.component.waitForComponent('[data-testid="scale-deployment-modal"]');
        
        // インスタンス数の変更
        await page.fill('[data-testid="scale-instances"]', '4');
        
        // スケール実行
        await page.click('[data-testid="apply-scale-button"]');
        
        // API呼び出しの確認
        await helpers.api.waitForApiCall('/api/deployments/scale', 'PUT');
        
        // 成功メッセージの確認
        await expect(page.locator('[data-testid="success-message"]')).toContainText('スケールが適用されました');
      }
    });

    test('should stop deployment', async ({ page }) => {
      // デプロイメントの停止
      await page.click('[data-testid="deployments-tab"]');
      await helpers.component.waitForComponent('[data-testid="deployments-list"]');
      
      const deploymentCards = page.locator('[data-testid="deployment-card"]');
      if (await deploymentCards.count() > 0) {
        // 停止ボタンのクリック
        await deploymentCards.first().locator('[data-testid="stop-deployment"]').click();
        
        // 確認ダイアログの表示
        await helpers.component.waitForComponent('[data-testid="confirm-stop-deployment-dialog"]');
        await expect(page.locator('[data-testid="confirm-message"]')).toContainText('デプロイメントを停止しますか？');
        
        // 停止の確認
        await page.click('[data-testid="confirm-stop"]');
        
        // API呼び出しの確認
        await helpers.api.waitForApiCall('/api/deployments/stop', 'POST');
        
        // ステータス更新の確認
        await expect(page.locator('[data-testid="deployment-status"]')).toContainText('停止中');
      }
    });
  });

  test.describe('Model Search and Filter', () => {
    test('should search models by name', async ({ page }) => {
      // 名前による検索
      await helpers.data.createTestModel('Searchable Model');
      await helpers.data.createTestModel('Another Model');
      
      await page.reload();
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      
      // 検索
      await helpers.component.searchInTable('Searchable');
      
      // 結果の確認
      await expect(page.locator('[data-testid="model-card"]').filter({ hasText: 'Searchable Model' })).toBeVisible();
      await expect(page.locator('[data-testid="model-card"]').filter({ hasText: 'Another Model' })).not.toBeVisible();
    });

    test('should filter models by algorithm', async ({ page }) => {
      // アルゴリズムによるフィルタリング
      await helpers.component.waitForComponent('[data-testid="model-filter"]');
      
      // フィルターの適用
      await page.selectOption('[data-testid="model-filter"]', 'yolov8');
      
      // フィルター結果の確認
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      
      const cards = page.locator('[data-testid="model-card"]');
      const count = await cards.count();
      
      for (let i = 0; i < count; i++) {
        await expect(cards.nth(i).locator('[data-testid="model-algorithm"]')).toContainText('yolov8');
      }
    });

    test('should filter models by status', async ({ page }) => {
      // ステータスによるフィルタリング
      await page.selectOption('[data-testid="status-filter"]', 'trained');
      
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      
      const cards = page.locator('[data-testid="model-card"]');
      const count = await cards.count();
      
      for (let i = 0; i < count; i++) {
        await expect(cards.nth(i).locator('[data-testid="model-status"]')).toContainText('trained');
      }
    });
  });

  test.describe('Model Performance', () => {
    test('should load model list within performance threshold', async ({ page }) => {
      // パフォーマンステスト：モデル一覧の読み込み
      const loadTime = await helpers.performance.measurePageLoad('/model-management');
      
      expect(loadTime).toBeLessThan(3000); // 3秒以内
    });

    test('should handle real-time training updates efficiently', async ({ page }) => {
      // リアルタイム学習更新の効率的な処理
      await page.click('[data-testid="training-jobs-tab"]');
      await helpers.component.waitForComponent('[data-testid="training-jobs-list"]');
      
      // WebSocket接続の確認
      const wsConnected = await page.evaluate(() => {
        return new Promise((resolve) => {
          const ws = new WebSocket('ws://localhost:3001/training-updates');
          ws.onopen = () => resolve(true);
          ws.onerror = () => resolve(false);
          setTimeout(() => resolve(false), 5000);
        });
      });
      
      expect(wsConnected).toBeTruthy();
    });
  });
});