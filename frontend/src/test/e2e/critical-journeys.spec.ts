import { test, expect } from '@playwright/test';
import { TestHelperFactory } from './helpers/test-helpers';

/**
 * クリティカルユーザージャーニーE2Eテスト
 * エンドツーエンドの重要なワークフローとビジネスクリティカルなシナリオをテスト
 */

test.describe('Critical User Journeys E2E Tests', () => {
  let helpers: ReturnType<typeof TestHelperFactory.createHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = TestHelperFactory.createHelpers(page);
  });

  test.afterEach(async ({ page }) => {
    await helpers.cleanup.cleanupTestData();
    await helpers.cleanup.clearLocalStorage();
  });

  test.describe('Complete Drone Operation Workflow', () => {
    test('should complete full drone setup to tracking workflow', async ({ page }) => {
      // 完全なドローン運用ワークフロー
      console.log('🚁 Starting complete drone operation workflow...');
      
      // 1. ログイン
      await helpers.auth.login();
      await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
      
      // 2. ドローンの追加
      await helpers.navigation.navigateToPage('drone-management');
      await page.click('[data-testid="add-drone-button"]');
      
      const droneData = {
        'drone-name': 'Critical Journey Drone',
        'drone-model': 'DJI Mini 3 Pro',
        'drone-serialNumber': 'CJ-001',
        'drone-batteryLevel': '95'
      };
      
      await helpers.form.fillForm(droneData);
      await page.click('[data-testid="save-drone-button"]');
      await helpers.api.waitForApiCall('/api/drones', 'POST');
      
      // ドローン追加成功の確認
      await expect(page.locator('[data-testid="success-message"]')).toContainText('ドローンが追加されました');
      
      // 3. データセットの作成
      await helpers.navigation.navigateToPage('dataset-management');
      await page.click('[data-testid="create-dataset-button"]');
      
      const datasetData = {
        'dataset-name': 'Critical Journey Dataset',
        'dataset-description': 'Critical journey test dataset',
        'dataset-tags': 'critical, test, automation'
      };
      
      await helpers.form.fillForm(datasetData);
      await helpers.component.selectOption('[data-testid="dataset-type"]', 'object_detection');
      await page.click('[data-testid="save-dataset-button"]');
      await helpers.api.waitForApiCall('/api/datasets', 'POST');
      
      // 4. モデルの作成
      await helpers.navigation.navigateToPage('model-management');
      await page.click('[data-testid="create-model-button"]');
      
      const modelData = {
        'model-name': 'Critical Journey Model',
        'model-description': 'Critical journey test model',
        'model-tags': 'critical, test'
      };
      
      await helpers.form.fillForm(modelData);
      await helpers.component.selectOption('[data-testid="model-algorithm"]', 'yolov8');
      await helpers.component.selectOption('[data-testid="model-framework"]', 'pytorch');
      await page.click('[data-testid="save-model-button"]');
      await helpers.api.waitForApiCall('/api/models', 'POST');
      
      // 5. モデル学習の開始
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Critical Journey Model' })
        .locator('[data-testid="train-model"]').click();
      
      await helpers.component.waitForComponent('[data-testid="training-config-modal"]');
      await page.selectOption('[data-testid="training-dataset-select"]', 'Critical Journey Dataset');
      await page.fill('[data-testid="training-epochs"]', '5');
      await page.click('[data-testid="start-training-button"]');
      await helpers.api.waitForApiCall('/api/models/train', 'POST');
      
      // 6. トラッキングの設定と開始
      await helpers.navigation.navigateToPage('tracking-control');
      await page.selectOption('[data-testid="drone-select"]', 'Critical Journey Drone');
      await page.selectOption('[data-testid="model-select"]', 'Critical Journey Model');
      
      // パラメータの調整
      await page.fill('[data-testid="confidence-threshold-slider"]', '0.7');
      await page.click('[data-testid="apply-parameters-button"]');
      
      // トラッキング開始
      await page.click('[data-testid="start-tracking-button"]');
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      
      // 7. 結果の確認
      await expect(page.locator('[data-testid="tracking-status"]')).toContainText('トラッキング中');
      await expect(page.locator('[data-testid="tracking-indicator"]')).toHaveClass(/active/);
      
      // 8. システム監視の確認
      await helpers.navigation.navigateToPage('system-monitoring');
      await expect(page.locator('[data-testid="system-status"]')).toContainText('正常');
      await expect(page.locator('[data-testid="active-drones-count"]')).toContainText('1');
      
      console.log('✅ Complete drone operation workflow completed successfully');
    });

    test('should handle full disaster recovery scenario', async ({ page }) => {
      // 災害復旧シナリオの完全テスト
      console.log('🆘 Starting disaster recovery scenario...');
      
      await helpers.auth.login();
      
      // 1. 通常運用状態の設定
      const testDrone = await helpers.data.createTestDrone('Disaster Test Drone');
      const testModel = await helpers.data.createTestModel('Disaster Test Model');
      
      // トラッキング開始
      await helpers.navigation.navigateToPage('tracking-control');
      await page.selectOption('[data-testid="drone-select"]', 'Disaster Test Drone');
      await page.selectOption('[data-testid="model-select"]', 'Disaster Test Model');
      await page.click('[data-testid="start-tracking-button"]');
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      
      // 2. システム障害のシミュレーション
      console.log('💥 Simulating system failure...');
      
      // API障害のシミュレーション
      await helpers.api.mockApiResponse('/api/tracking/status', {
        error: 'System failure',
        status: 'error'
      });
      
      await page.reload();
      
      // 3. 障害検出の確認
      await expect(page.locator('[data-testid="system-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-notification"]')).toContainText('システム障害が発生しました');
      
      // 4. 緊急停止の実行
      await page.click('[data-testid="emergency-stop-button"]');
      await helpers.component.waitForComponent('[data-testid="emergency-stop-dialog"]');
      await page.click('[data-testid="confirm-emergency-stop"]');
      
      // 5. 復旧手順の実行
      console.log('🔧 Starting recovery procedures...');
      
      // API復旧のシミュレーション
      await page.unroute('**/api/tracking/status');
      
      // システム監視での復旧確認
      await helpers.navigation.navigateToPage('system-monitoring');
      await page.click('[data-testid="system-check-button"]');
      
      // 6. 段階的復旧の確認
      await helpers.navigation.navigateToPage('drone-management');
      await expect(page.locator('[data-testid="drone-status"]')).toContainText('待機中');
      
      // ドローンの再初期化
      await page.locator('[data-testid="drone-card"]').filter({ hasText: 'Disaster Test Drone' })
        .locator('[data-testid="reconnect-drone"]').click();
      
      await helpers.api.waitForApiCall('/api/drones/reconnect', 'POST');
      
      // 7. 運用再開の確認
      await helpers.navigation.navigateToPage('tracking-control');
      await page.selectOption('[data-testid="drone-select"]', 'Disaster Test Drone');
      await page.selectOption('[data-testid="model-select"]', 'Disaster Test Model');
      await page.click('[data-testid="start-tracking-button"]');
      
      await expect(page.locator('[data-testid="tracking-status"]')).toContainText('トラッキング中');
      
      console.log('✅ Disaster recovery scenario completed successfully');
    });
  });

  test.describe('Data Processing Pipeline', () => {
    test('should complete data ingestion to model deployment pipeline', async ({ page }) => {
      // データ取り込みからモデルデプロイまでのパイプライン
      console.log('📊 Starting data processing pipeline...');
      
      await helpers.auth.login();
      
      // 1. データセット作成
      await helpers.navigation.navigateToPage('dataset-management');
      await page.click('[data-testid="create-dataset-button"]');
      
      const datasetData = {
        'dataset-name': 'Pipeline Test Dataset',
        'dataset-description': 'Pipeline test dataset',
        'dataset-tags': 'pipeline, test'
      };
      
      await helpers.form.fillForm(datasetData);
      await helpers.component.selectOption('[data-testid="dataset-type"]', 'object_detection');
      await page.click('[data-testid="save-dataset-button"]');
      await helpers.api.waitForApiCall('/api/datasets', 'POST');
      
      // 2. データの追加（シミュレーション）
      await helpers.component.waitForComponent('[data-testid="dataset-card"]');
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Pipeline Test Dataset' })
        .locator('[data-testid="view-dataset"]').click();
      
      await helpers.component.waitForComponent('[data-testid="image-gallery"]');
      await page.click('[data-testid="upload-images-button"]');
      
      // アップロードダイアログの確認
      await helpers.component.waitForComponent('[data-testid="upload-images-modal"]');
      await expect(page.locator('[data-testid="file-drop-area"]')).toBeVisible();
      
      // アップロード完了のシミュレーション
      await helpers.api.mockApiResponse('/api/datasets/upload', {
        uploaded: 50,
        status: 'success'
      });
      
      // 3. データの前処理
      await page.click('[data-testid="preprocess-data-button"]');
      await helpers.component.waitForComponent('[data-testid="preprocessing-config-modal"]');
      
      // 前処理設定
      await page.check('[data-testid="augmentation-enabled"]');
      await page.selectOption('[data-testid="resize-method"]', 'bilinear');
      await page.click('[data-testid="start-preprocessing-button"]');
      
      await helpers.api.waitForApiCall('/api/datasets/preprocess', 'POST');
      
      // 4. モデル作成と学習
      await helpers.navigation.navigateToPage('model-management');
      await page.click('[data-testid="create-model-button"]');
      
      const modelData = {
        'model-name': 'Pipeline Test Model',
        'model-description': 'Pipeline test model',
      };
      
      await helpers.form.fillForm(modelData);
      await helpers.component.selectOption('[data-testid="model-algorithm"]', 'yolov8');
      await helpers.component.selectOption('[data-testid="model-framework"]', 'pytorch');
      await page.click('[data-testid="save-model-button"]');
      await helpers.api.waitForApiCall('/api/models', 'POST');
      
      // 学習開始
      await helpers.component.waitForComponent('[data-testid="model-card"]');
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Pipeline Test Model' })
        .locator('[data-testid="train-model"]').click();
      
      await helpers.component.waitForComponent('[data-testid="training-config-modal"]');
      await page.selectOption('[data-testid="training-dataset-select"]', 'Pipeline Test Dataset');
      await page.fill('[data-testid="training-epochs"]', '3');
      await page.click('[data-testid="start-training-button"]');
      
      // 5. 学習進捗の監視
      await page.click('[data-testid="training-jobs-tab"]');
      await helpers.component.waitForComponent('[data-testid="training-jobs-list"]');
      
      // 学習完了のシミュレーション
      await helpers.api.mockApiResponse('/api/training-jobs/status', {
        status: 'completed',
        accuracy: 0.92,
        loss: 0.15
      });
      
      // 6. モデル評価
      await page.click('[data-testid="models-tab"]');
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Pipeline Test Model' })
        .locator('[data-testid="view-model"]').click();
      
      await helpers.component.waitForComponent('[data-testid="model-details"]');
      await page.click('[data-testid="evaluation-tab"]');
      await page.click('[data-testid="run-evaluation-button"]');
      
      // 評価完了の確認
      await expect(page.locator('[data-testid="evaluation-results"]')).toBeVisible();
      await expect(page.locator('[data-testid="accuracy-metric"]')).toContainText('92');
      
      // 7. モデルデプロイ
      await page.click('[data-testid="deploy-model-button"]');
      await helpers.component.waitForComponent('[data-testid="deployment-config-modal"]');
      
      await page.fill('[data-testid="deployment-name"]', 'Pipeline Test Deployment');
      await page.selectOption('[data-testid="deployment-environment"]', 'production');
      await page.click('[data-testid="start-deployment-button"]');
      
      await helpers.api.waitForApiCall('/api/models/deploy', 'POST');
      
      // 8. デプロイ状況の確認
      await page.click('[data-testid="deployments-tab"]');
      await helpers.component.waitForComponent('[data-testid="deployments-list"]');
      
      await expect(page.locator('[data-testid="deployment-card"]')
        .filter({ hasText: 'Pipeline Test Deployment' })).toBeVisible();
      
      console.log('✅ Data processing pipeline completed successfully');
    });

    test('should handle batch processing workflow', async ({ page }) => {
      // バッチ処理ワークフロー
      console.log('⏱️ Starting batch processing workflow...');
      
      await helpers.auth.login();
      
      // 1. 複数データセットの準備
      const datasets = [
        'Batch Dataset 1',
        'Batch Dataset 2',
        'Batch Dataset 3'
      ];
      
      for (const datasetName of datasets) {
        await helpers.data.createTestDataset(datasetName);
      }
      
      // 2. バッチジョブの設定
      await helpers.navigation.navigateToPage('dataset-management');
      await page.click('[data-testid="batch-operations-button"]');
      
      await helpers.component.waitForComponent('[data-testid="batch-operations-modal"]');
      
      // バッチ対象の選択
      for (const datasetName of datasets) {
        await page.check(`[data-testid="select-${datasetName}"]`);
      }
      
      // バッチ処理タイプの選択
      await page.selectOption('[data-testid="batch-operation-type"]', 'preprocessing');
      
      // 3. バッチ処理の実行
      await page.click('[data-testid="start-batch-button"]');
      await helpers.api.waitForApiCall('/api/datasets/batch-process', 'POST');
      
      // 4. 進捗監視
      await expect(page.locator('[data-testid="batch-progress"]')).toBeVisible();
      await expect(page.locator('[data-testid="batch-status"]')).toContainText('処理中');
      
      // 処理完了のシミュレーション
      await helpers.api.mockApiResponse('/api/batch-jobs/status', {
        status: 'completed',
        processed: 3,
        failed: 0
      });
      
      await page.waitForFunction(() => {
        const statusElement = document.querySelector('[data-testid="batch-status"]');
        return statusElement?.textContent?.includes('完了');
      }, { timeout: 10000 });
      
      // 5. 結果の確認
      await expect(page.locator('[data-testid="batch-results"]')).toBeVisible();
      await expect(page.locator('[data-testid="processed-count"]')).toContainText('3');
      await expect(page.locator('[data-testid="failed-count"]')).toContainText('0');
      
      console.log('✅ Batch processing workflow completed successfully');
    });
  });

  test.describe('Multi-user Collaboration', () => {
    test('should handle concurrent user operations', async ({ page, context }) => {
      // 複数ユーザーの同時操作
      console.log('👥 Starting multi-user collaboration test...');
      
      // 管理者ユーザーでログイン
      await helpers.auth.login('admin', 'admin123');
      
      // 1. 管理者が共有リソースを作成
      const sharedDataset = await helpers.data.createTestDataset('Shared Dataset');
      const sharedModel = await helpers.data.createTestModel('Shared Model');
      
      // 2. 新しいブラウザコンテキストで操作者ユーザーを作成
      const operatorPage = await context.newPage();
      const operatorHelpers = TestHelperFactory.createHelpers(operatorPage);
      
      await operatorHelpers.auth.login('operator', 'operator123');
      
      // 3. 同時にリソースにアクセス
      // 管理者：モデルの編集開始
      await helpers.navigation.navigateToPage('model-management');
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Shared Model' })
        .locator('[data-testid="edit-model"]').click();
      
      // 操作者：同じモデルの詳細表示
      await operatorHelpers.navigation.navigateToPage('model-management');
      await operatorPage.locator('[data-testid="model-card"]').filter({ hasText: 'Shared Model' })
        .locator('[data-testid="view-model"]').click();
      
      // 4. 競合状態の処理確認
      await helpers.component.waitForComponent('[data-testid="edit-model-modal"]');
      await page.fill('[data-testid="model-description"]', 'Updated by admin');
      
      // 操作者が同時に学習を開始しようとする
      await operatorPage.click('[data-testid="train-model-button"]');
      
      // 競合エラーの確認
      await expect(operatorPage.locator('[data-testid="conflict-error"]')).toBeVisible();
      await expect(operatorPage.locator('[data-testid="conflict-error"]'))
        .toContainText('他のユーザーが編集中です');
      
      // 5. 管理者が編集を完了
      await page.click('[data-testid="save-model-button"]');
      await helpers.api.waitForApiCall('/api/models', 'PUT');
      
      // 6. 操作者のリロード後の状態確認
      await operatorPage.reload();
      await operatorHelpers.component.waitForComponent('[data-testid="model-details"]');
      
      // 更新された内容の確認
      await expect(operatorPage.locator('[data-testid="model-description"]'))
        .toContainText('Updated by admin');
      
      await operatorPage.close();
      
      console.log('✅ Multi-user collaboration test completed successfully');
    });

    test('should handle role-based access control workflow', async ({ page, context }) => {
      // ロールベースアクセス制御ワークフロー
      console.log('🔐 Starting RBAC workflow test...');
      
      // 1. 管理者として全権限操作
      await helpers.auth.login('admin', 'admin123');
      
      // システム設定へのアクセス
      await helpers.navigation.navigateToPage('settings');
      await expect(page.locator('[data-testid="system-settings"]')).toBeVisible();
      await expect(page.locator('[data-testid="user-management"]')).toBeVisible();
      
      // ユーザー作成
      await page.click('[data-testid="add-user-button"]');
      await helpers.component.waitForComponent('[data-testid="add-user-modal"]');
      
      await helpers.form.fillForm({
        'user-name': 'Test Viewer',
        'user-email': 'viewer@test.com',
        'user-password': 'viewer123'
      });
      
      await page.selectOption('[data-testid="user-role"]', 'viewer');
      await page.click('[data-testid="save-user-button"]');
      
      // 2. 閲覧者としてログイン
      await helpers.auth.logout();
      
      const viewerPage = await context.newPage();
      const viewerHelpers = TestHelperFactory.createHelpers(viewerPage);
      
      await viewerHelpers.auth.login('viewer@test.com', 'viewer123');
      
      // 3. 権限制限の確認
      // ダッシュボードは表示可能
      await expect(viewerPage.locator('[data-testid="dashboard"]')).toBeVisible();
      
      // データセット管理：読み取り専用
      await viewerHelpers.navigation.navigateToPage('dataset-management');
      await expect(viewerPage.locator('[data-testid="dataset-list"]')).toBeVisible();
      await expect(viewerPage.locator('[data-testid="create-dataset-button"]')).not.toBeVisible();
      
      // モデル管理：読み取り専用
      await viewerHelpers.navigation.navigateToPage('model-management');
      await expect(viewerPage.locator('[data-testid="model-list"]')).toBeVisible();
      await expect(viewerPage.locator('[data-testid="create-model-button"]')).not.toBeVisible();
      
      // トラッキング制御：アクセス拒否
      await viewerHelpers.navigation.navigateToPage('tracking-control');
      await expect(viewerPage.locator('[data-testid="access-denied"]')).toBeVisible();
      
      // システム設定：アクセス拒否
      await viewerHelpers.navigation.navigateToPage('settings');
      await expect(viewerPage.locator('[data-testid="access-denied"]')).toBeVisible();
      
      await viewerPage.close();
      
      console.log('✅ RBAC workflow test completed successfully');
    });
  });

  test.describe('Performance Critical Scenarios', () => {
    test('should handle high-load concurrent operations', async ({ page }) => {
      // 高負荷同時操作の処理
      console.log('⚡ Starting high-load performance test...');
      
      await helpers.auth.login();
      
      // 1. 複数リソースの同時作成
      const createPromises = [];
      
      // 10個のデータセットを並列作成
      for (let i = 0; i < 10; i++) {
        createPromises.push(helpers.data.createTestDataset(`Load Test Dataset ${i}`));
      }
      
      // 5個のモデルを並列作成
      for (let i = 0; i < 5; i++) {
        createPromises.push(helpers.data.createTestModel(`Load Test Model ${i}`));
      }
      
      // 並列実行
      await Promise.all(createPromises);
      
      // 2. 大量データの一覧表示性能確認
      await helpers.navigation.navigateToPage('dataset-management');
      
      const listLoadTime = await helpers.performance.measurePageLoad('/dataset-management');
      expect(listLoadTime).toBeLessThan(5000); // 5秒以内
      
      // 仮想スクロールの動作確認
      await expect(page.locator('[data-testid="virtual-scroll"]')).toBeVisible();
      
      // 3. 検索性能の確認
      const searchTime = await helpers.performance.measureInteraction(
        '[data-testid="search-input"]', 
        'fill', 
        'Load Test Dataset 5'
      );
      expect(searchTime).toBeLessThan(2000); // 2秒以内
      
      // 4. 複数タブでの同時操作
      await helpers.navigation.navigateToPage('model-management');
      
      // バックグラウンドでの学習ジョブ監視
      await page.click('[data-testid="training-jobs-tab"]');
      
      // WebSocket接続の安定性確認
      const wsStable = await page.evaluate(() => {
        return new Promise((resolve) => {
          let messageCount = 0;
          const ws = new WebSocket('ws://localhost:3001/updates');
          
          ws.onmessage = () => {
            messageCount++;
            if (messageCount >= 5) {
              resolve(true);
            }
          };
          
          ws.onerror = () => resolve(false);
          setTimeout(() => resolve(messageCount >= 3), 10000);
        });
      });
      
      expect(wsStable).toBeTruthy();
      
      console.log('✅ High-load performance test completed successfully');
    });

    test('should maintain responsiveness during intensive operations', async ({ page }) => {
      // 集約的操作中の応答性維持
      console.log('🔄 Starting intensive operations responsiveness test...');
      
      await helpers.auth.login();
      
      // 1. 大容量データセットの処理開始
      await helpers.navigation.navigateToPage('dataset-management');
      const largeDataset = await helpers.data.createTestDataset('Large Dataset');
      
      // 大容量処理のシミュレーション
      await page.locator('[data-testid="dataset-card"]').filter({ hasText: 'Large Dataset' })
        .locator('[data-testid="view-dataset"]').click();
      
      await page.click('[data-testid="batch-process-button"]');
      await helpers.component.waitForComponent('[data-testid="batch-process-modal"]');
      
      // 処理開始
      await page.selectOption('[data-testid="process-type"]', 'heavy_augmentation');
      await page.click('[data-testid="start-process-button"]');
      
      // 2. バックグラウンド処理中のUI応答性確認
      // 他ページへの遷移が可能か確認
      const navigationTime = await helpers.performance.measurePageLoad('/drone-management');
      expect(navigationTime).toBeLessThan(3000); // 3秒以内
      
      // UI操作の応答性確認
      await page.click('[data-testid="add-drone-button"]');
      await helpers.component.waitForComponent('[data-testid="add-drone-modal"]');
      
      const modalOpenTime = Date.now();
      await expect(page.locator('[data-testid="add-drone-modal"]')).toBeVisible();
      const modalDisplayTime = Date.now() - modalOpenTime;
      
      expect(modalDisplayTime).toBeLessThan(1000); // 1秒以内でモーダル表示
      
      // 3. 処理状況の監視
      await helpers.navigation.navigateToPage('system-monitoring');
      
      // リアルタイム監視データの更新確認
      await expect(page.locator('[data-testid="cpu-usage"]')).toBeVisible();
      await expect(page.locator('[data-testid="memory-usage"]')).toBeVisible();
      await expect(page.locator('[data-testid="processing-jobs"]')).toBeVisible();
      
      // メトリクスの更新確認
      const initialCpuValue = await page.textContent('[data-testid="cpu-usage"]');
      
      await page.waitForFunction((initial) => {
        const current = document.querySelector('[data-testid="cpu-usage"]')?.textContent;
        return current !== initial;
      }, initialCpuValue, { timeout: 15000 });
      
      console.log('✅ Intensive operations responsiveness test completed successfully');
    });
  });

  test.describe('Error Recovery Scenarios', () => {
    test('should recover from complete system restart', async ({ page }) => {
      // システム完全再起動からの復旧
      console.log('🔄 Starting system restart recovery test...');
      
      await helpers.auth.login();
      
      // 1. 運用状態の構築
      const testDrone = await helpers.data.createTestDrone('Recovery Test Drone');
      const testModel = await helpers.data.createTestModel('Recovery Test Model');
      
      // トラッキング開始
      await helpers.navigation.navigateToPage('tracking-control');
      await page.selectOption('[data-testid="drone-select"]', 'Recovery Test Drone');
      await page.selectOption('[data-testid="model-select"]', 'Recovery Test Model');
      await page.click('[data-testid="start-tracking-button"]');
      
      // 2. システム再起動のシミュレーション
      console.log('🔄 Simulating system restart...');
      
      // セッション情報の保存
      const storageState = await page.context().storageState();
      
      // 全てのAPIルートを中断
      await page.route('**/api/**', route => route.abort());
      
      // ページリロード（再起動シミュレーション）
      await page.reload();
      
      // 3. 復旧プロセスの確認
      // 認証状態の復元確認
      await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
      
      // 再ログイン
      await helpers.auth.login();
      
      // APIルートの復元
      await page.unroute('**/api/**');
      
      // 4. 状態復旧の確認
      await helpers.navigation.navigateToPage('drone-management');
      
      // ドローンステータスの確認
      await expect(page.locator('[data-testid="drone-card"]')
        .filter({ hasText: 'Recovery Test Drone' })).toBeVisible();
      
      // 自動再接続の確認
      await page.click('[data-testid="refresh-status-button"]');
      await helpers.api.waitForApiCall('/api/drones/status', 'GET');
      
      // 5. トラッキング状態の復元
      await helpers.navigation.navigateToPage('tracking-control');
      
      // 前回の設定が保持されているか確認
      const droneSelection = await page.inputValue('[data-testid="drone-select"]');
      const modelSelection = await page.inputValue('[data-testid="model-select"]');
      
      // 設定が初期化されている場合は再設定
      if (!droneSelection || !modelSelection) {
        await page.selectOption('[data-testid="drone-select"]', 'Recovery Test Drone');
        await page.selectOption('[data-testid="model-select"]', 'Recovery Test Model');
      }
      
      // トラッキング再開
      await page.click('[data-testid="start-tracking-button"]');
      await expect(page.locator('[data-testid="tracking-status"]')).toContainText('トラッキング中');
      
      console.log('✅ System restart recovery test completed successfully');
    });

    test('should handle cascading failure recovery', async ({ page }) => {
      // カスケード障害からの復旧
      console.log('🌊 Starting cascading failure recovery test...');
      
      await helpers.auth.login();
      
      // 1. 複数システムの依存関係構築
      const testDrone = await helpers.data.createTestDrone('Cascade Test Drone');
      const testDataset = await helpers.data.createTestDataset('Cascade Test Dataset');
      const testModel = await helpers.data.createTestModel('Cascade Test Model');
      
      // 学習ジョブの開始
      await helpers.navigation.navigateToPage('model-management');
      await page.locator('[data-testid="model-card"]').filter({ hasText: 'Cascade Test Model' })
        .locator('[data-testid="train-model"]').click();
      
      await helpers.component.waitForComponent('[data-testid="training-config-modal"]');
      await page.selectOption('[data-testid="training-dataset-select"]', 'Cascade Test Dataset');
      await page.click('[data-testid="start-training-button"]');
      
      // 2. 段階的障害の発生
      console.log('💥 Triggering cascading failures...');
      
      // データベース接続エラー
      await helpers.api.mockApiResponse('/api/datasets/**', {
        error: 'Database connection failed',
        status: 503
      });
      
      // ストレージエラー
      await helpers.api.mockApiResponse('/api/models/storage/**', {
        error: 'Storage unavailable',
        status: 503
      });
      
      // 学習サービスエラー
      await helpers.api.mockApiResponse('/api/training/**', {
        error: 'Training service unavailable',
        status: 503
      });
      
      // 3. 障害の検出と表示
      await page.reload();
      
      // システム監視での障害検出
      await helpers.navigation.navigateToPage('system-monitoring');
      
      await expect(page.locator('[data-testid="system-alerts"]')).toBeVisible();
      await expect(page.locator('[data-testid="critical-alert"]')).toContainText('データベース接続エラー');
      await expect(page.locator('[data-testid="critical-alert"]')).toContainText('ストレージエラー');
      
      // 4. 段階的復旧手順
      console.log('🔧 Starting staged recovery...');
      
      // データベース復旧
      await page.unroute('**/api/datasets/**');
      await page.click('[data-testid="test-database-button"]');
      await expect(page.locator('[data-testid="database-status"]')).toContainText('正常');
      
      // ストレージ復旧
      await page.unroute('**/api/models/storage/**');
      await page.click('[data-testid="test-storage-button"]');
      await expect(page.locator('[data-testid="storage-status"]')).toContainText('正常');
      
      // 学習サービス復旧
      await page.unroute('**/api/training/**');
      await page.click('[data-testid="test-training-service-button"]');
      await expect(page.locator('[data-testid="training-service-status"]')).toContainText('正常');
      
      // 5. サービス再開の確認
      await helpers.navigation.navigateToPage('model-management');
      await page.click('[data-testid="training-jobs-tab"]');
      
      // 中断されたジョブの復旧確認
      await expect(page.locator('[data-testid="training-job-card"]')).toBeVisible();
      
      // ジョブ再開
      await page.locator('[data-testid="training-job-card"]').first()
        .locator('[data-testid="resume-job"]').click();
      
      await expect(page.locator('[data-testid="job-status"]')).toContainText('学習中');
      
      console.log('✅ Cascading failure recovery test completed successfully');
    });
  });
});