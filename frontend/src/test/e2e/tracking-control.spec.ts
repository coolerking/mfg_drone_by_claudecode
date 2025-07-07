import { test, expect } from '@playwright/test';
import { TestHelperFactory } from './helpers/test-helpers';

/**
 * トラッキング制御E2Eテスト
 * リアルタイム物体追跡、追跡パラメータ調整、ログ機能をテスト
 */

test.describe('Tracking Control E2E Tests', () => {
  let helpers: ReturnType<typeof TestHelperFactory.createHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = TestHelperFactory.createHelpers(page);
    await helpers.auth.login();
    await helpers.navigation.navigateToPage('tracking-control');
  });

  test.afterEach(async ({ page }) => {
    await helpers.cleanup.cleanupTestData();
  });

  test.describe('Tracking Interface Layout', () => {
    test('should display tracking control interface correctly', async ({ page }) => {
      // トラッキング制御インターフェースの表示確認
      await helpers.component.waitForComponent('[data-testid="tracking-control-panel"]');
      
      // ヘッダーの確認
      await expect(page.locator('[data-testid="page-title"]')).toHaveText('トラッキング制御');
      
      // メインセクションの確認
      await expect(page.locator('[data-testid="camera-stream-section"]')).toBeVisible();
      await expect(page.locator('[data-testid="tracking-controls-section"]')).toBeVisible();
      await expect(page.locator('[data-testid="tracking-parameters-section"]')).toBeVisible();
      await expect(page.locator('[data-testid="tracking-status-section"]')).toBeVisible();
      
      // カメラストリームエリア
      await expect(page.locator('[data-testid="camera-stream-container"]')).toBeVisible();
      await expect(page.locator('[data-testid="stream-overlay"]')).toBeVisible();
      
      // 制御ボタン
      await expect(page.locator('[data-testid="start-tracking-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="stop-tracking-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="emergency-stop-button"]')).toBeVisible();
    });

    test('should display camera stream correctly', async ({ page }) => {
      // カメラストリームの表示確認
      await helpers.component.waitForComponent('[data-testid="camera-stream"]');
      
      // ストリーム要素の確認
      await expect(page.locator('[data-testid="video-stream"]')).toBeVisible();
      await expect(page.locator('[data-testid="stream-controls"]')).toBeVisible();
      
      // ストリーム制御ボタン
      await expect(page.locator('[data-testid="play-stream-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="pause-stream-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="fullscreen-button"]')).toBeVisible();
      
      // ストリーム情報
      await expect(page.locator('[data-testid="stream-resolution"]')).toBeVisible();
      await expect(page.locator('[data-testid="stream-fps"]')).toBeVisible();
      await expect(page.locator('[data-testid="stream-latency"]')).toBeVisible();
    });

    test('should display tracking parameters panel', async ({ page }) => {
      // トラッキングパラメータパネルの表示確認
      await helpers.component.waitForComponent('[data-testid="tracking-parameters"]');
      
      // パラメータコントロール
      await expect(page.locator('[data-testid="confidence-threshold-slider"]')).toBeVisible();
      await expect(page.locator('[data-testid="iou-threshold-slider"]')).toBeVisible();
      await expect(page.locator('[data-testid="max-objects-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="tracking-algorithm-select"]')).toBeVisible();
      
      // デフォルト値の確認
      const confidenceValue = await page.inputValue('[data-testid="confidence-threshold-slider"]');
      expect(parseFloat(confidenceValue)).toBeGreaterThan(0);
      
      const iouValue = await page.inputValue('[data-testid="iou-threshold-slider"]');
      expect(parseFloat(iouValue)).toBeGreaterThan(0);
    });
  });

  test.describe('Tracking Operations', () => {
    test('should start tracking successfully', async ({ page }) => {
      // トラッキングの開始
      await helpers.component.waitForComponent('[data-testid="tracking-control-panel"]');
      
      // ドローンが選択されていることを確認
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      
      // モデルが選択されていることを確認
      await page.selectOption('[data-testid="model-select"]', 'test-tracking-model');
      
      // トラッキング開始ボタンのクリック
      await page.click('[data-testid="start-tracking-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      
      // トラッキング状態の確認
      await expect(page.locator('[data-testid="tracking-status"]')).toContainText('トラッキング中');
      await expect(page.locator('[data-testid="tracking-indicator"]')).toHaveClass(/active/);
      
      // ボタン状態の変更確認
      await expect(page.locator('[data-testid="start-tracking-button"]')).toBeDisabled();
      await expect(page.locator('[data-testid="stop-tracking-button"]')).toBeEnabled();
    });

    test('should stop tracking successfully', async ({ page }) => {
      // トラッキングの停止
      // まずトラッキングを開始
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.selectOption('[data-testid="model-select"]', 'test-tracking-model');
      await page.click('[data-testid="start-tracking-button"]');
      
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      await expect(page.locator('[data-testid="tracking-status"]')).toContainText('トラッキング中');
      
      // トラッキング停止
      await page.click('[data-testid="stop-tracking-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/tracking/stop', 'POST');
      
      // 停止状態の確認
      await expect(page.locator('[data-testid="tracking-status"]')).toContainText('停止');
      await expect(page.locator('[data-testid="tracking-indicator"]')).not.toHaveClass(/active/);
      
      // ボタン状態の確認
      await expect(page.locator('[data-testid="start-tracking-button"]')).toBeEnabled();
      await expect(page.locator('[data-testid="stop-tracking-button"]')).toBeDisabled();
    });

    test('should handle emergency stop', async ({ page }) => {
      // 緊急停止の処理
      // トラッキング開始
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.selectOption('[data-testid="model-select"]', 'test-tracking-model');
      await page.click('[data-testid="start-tracking-button"]');
      
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      
      // 緊急停止ボタンのクリック
      await page.click('[data-testid="emergency-stop-button"]');
      
      // 確認ダイアログの表示
      await helpers.component.waitForComponent('[data-testid="emergency-stop-dialog"]');
      await expect(page.locator('[data-testid="emergency-message"]')).toContainText('緊急停止を実行しますか？');
      
      // 緊急停止の確認
      await page.click('[data-testid="confirm-emergency-stop"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/tracking/emergency-stop', 'POST');
      
      // 緊急停止状態の確認
      await expect(page.locator('[data-testid="tracking-status"]')).toContainText('緊急停止');
      await expect(page.locator('[data-testid="emergency-indicator"]')).toBeVisible();
    });

    test('should validate tracking prerequisites', async ({ page }) => {
      // トラッキング前提条件のバリデーション
      await helpers.component.waitForComponent('[data-testid="tracking-control-panel"]');
      
      // ドローンとモデルが未選択の状態でトラッキング開始を試行
      await page.click('[data-testid="start-tracking-button"]');
      
      // エラーメッセージの確認
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-message"]')).toContainText('ドローンとモデルを選択してください');
      
      // ドローンのみ選択
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.click('[data-testid="start-tracking-button"]');
      
      // モデル未選択エラー
      await expect(page.locator('[data-testid="error-message"]')).toContainText('トラッキングモデルを選択してください');
    });
  });

  test.describe('Parameter Adjustment', () => {
    test('should adjust confidence threshold', async ({ page }) => {
      // 信頼度閾値の調整
      await helpers.component.waitForComponent('[data-testid="confidence-threshold-slider"]');
      
      // 初期値の確認
      const initialValue = await page.inputValue('[data-testid="confidence-threshold-slider"]');
      
      // 値の変更
      await page.fill('[data-testid="confidence-threshold-slider"]', '0.8');
      
      // 変更の適用
      await page.click('[data-testid="apply-parameters-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/tracking/parameters', 'PUT');
      
      // 値の表示確認
      await expect(page.locator('[data-testid="confidence-value-display"]')).toContainText('0.8');
      
      // 成功メッセージの確認
      await expect(page.locator('[data-testid="success-message"]')).toContainText('パラメータが更新されました');
    });

    test('should adjust IoU threshold', async ({ page }) => {
      // IoU閾値の調整
      await helpers.component.waitForComponent('[data-testid="iou-threshold-slider"]');
      
      // 値の変更
      await page.fill('[data-testid="iou-threshold-slider"]', '0.5');
      
      // 変更の適用
      await page.click('[data-testid="apply-parameters-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/tracking/parameters', 'PUT');
      
      // 値の表示確認
      await expect(page.locator('[data-testid="iou-value-display"]')).toContainText('0.5');
    });

    test('should change tracking algorithm', async ({ page }) => {
      // トラッキングアルゴリズムの変更
      await helpers.component.waitForComponent('[data-testid="tracking-algorithm-select"]');
      
      // アルゴリズムの変更
      await page.selectOption('[data-testid="tracking-algorithm-select"]', 'deepsort');
      
      // 変更の適用
      await page.click('[data-testid="apply-parameters-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/tracking/parameters', 'PUT');
      
      // アルゴリズム表示の確認
      await expect(page.locator('[data-testid="current-algorithm"]')).toContainText('DeepSORT');
    });

    test('should reset parameters to default', async ({ page }) => {
      // パラメータのデフォルト値へのリセット
      await helpers.component.waitForComponent('[data-testid="tracking-parameters"]');
      
      // パラメータを変更
      await page.fill('[data-testid="confidence-threshold-slider"]', '0.9');
      await page.fill('[data-testid="iou-threshold-slider"]', '0.3');
      
      // リセットボタンのクリック
      await page.click('[data-testid="reset-parameters-button"]');
      
      // 確認ダイアログの表示
      await helpers.component.waitForComponent('[data-testid="reset-confirm-dialog"]');
      await expect(page.locator('[data-testid="reset-message"]')).toContainText('パラメータをデフォルト値にリセットしますか？');
      
      // リセットの確認
      await page.click('[data-testid="confirm-reset"]');
      
      // デフォルト値の確認
      await expect(page.locator('[data-testid="confidence-value-display"]')).toContainText('0.5');
      await expect(page.locator('[data-testid="iou-value-display"]')).toContainText('0.45');
    });
  });

  test.describe('Real-time Tracking Display', () => {
    test('should display tracking results on stream', async ({ page }) => {
      // ストリーム上でのトラッキング結果表示
      await helpers.component.waitForComponent('[data-testid="camera-stream"]');
      
      // トラッキング開始
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.selectOption('[data-testid="model-select"]', 'test-tracking-model');
      await page.click('[data-testid="start-tracking-button"]');
      
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      
      // トラッキング結果オーバーレイの確認
      await expect(page.locator('[data-testid="tracking-overlay"]')).toBeVisible();
      
      // バウンディングボックスの表示確認（モックデータの場合）
      await expect(page.locator('[data-testid="bounding-boxes"]')).toBeVisible();
      
      // オブジェクトIDとラベルの表示確認
      await expect(page.locator('[data-testid="object-labels"]')).toBeVisible();
    });

    test('should update tracking statistics in real-time', async ({ page }) => {
      // リアルタイム統計情報の更新
      await helpers.component.waitForComponent('[data-testid="tracking-statistics"]');
      
      // 統計表示要素の確認
      await expect(page.locator('[data-testid="detected-objects-count"]')).toBeVisible();
      await expect(page.locator('[data-testid="tracked-objects-count"]')).toBeVisible();
      await expect(page.locator('[data-testid="fps-display"]')).toBeVisible();
      await expect(page.locator('[data-testid="processing-time"]')).toBeVisible();
      
      // トラッキング開始後の統計更新確認
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.selectOption('[data-testid="model-select"]', 'test-tracking-model');
      await page.click('[data-testid="start-tracking-button"]');
      
      // WebSocket更新の確認（モック環境）
      await page.waitForFunction(() => {
        const fpsElement = document.querySelector('[data-testid="fps-display"]');
        return fpsElement && fpsElement.textContent !== '0';
      }, { timeout: 10000 });
    });

    test('should handle tracking interruptions gracefully', async ({ page }) => {
      // トラッキング中断の優雅な処理
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.selectOption('[data-testid="model-select"]', 'test-tracking-model');
      await page.click('[data-testid="start-tracking-button"]');
      
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      
      // 接続中断のシミュレーション
      await helpers.api.mockApiResponse('/api/tracking/status', {
        error: 'Connection lost',
        status: 'interrupted'
      });
      
      // 中断状態の表示確認
      await expect(page.locator('[data-testid="connection-status"]')).toContainText('接続中断');
      await expect(page.locator('[data-testid="reconnect-button"]')).toBeVisible();
      
      // 再接続の試行
      await page.click('[data-testid="reconnect-button"]');
      
      // 再接続処理の確認
      await expect(page.locator('[data-testid="reconnecting-indicator"]')).toBeVisible();
    });
  });

  test.describe('Tracking History and Logs', () => {
    test('should display tracking history', async ({ page }) => {
      // トラッキング履歴の表示
      await page.click('[data-testid="history-tab"]');
      
      await helpers.component.waitForComponent('[data-testid="tracking-history"]');
      
      // 履歴テーブルの確認
      await expect(page.locator('[data-testid="history-table"]')).toBeVisible();
      
      // テーブルヘッダーの確認
      await expect(page.locator('[data-testid="history-table"] thead')).toContainText('開始時刻');
      await expect(page.locator('[data-testid="history-table"] thead')).toContainText('終了時刻');
      await expect(page.locator('[data-testid="history-table"] thead')).toContainText('ドローン');
      await expect(page.locator('[data-testid="history-table"] thead')).toContainText('検出数');
      await expect(page.locator('[data-testid="history-table"] thead')).toContainText('ステータス');
      
      // 履歴エントリの確認
      const historyRows = page.locator('[data-testid="history-row"]');
      if (await historyRows.count() > 0) {
        await expect(historyRows.first().locator('[data-testid="history-start-time"]')).toBeVisible();
        await expect(historyRows.first().locator('[data-testid="history-drone"]')).toBeVisible();
        await expect(historyRows.first().locator('[data-testid="history-status"]')).toBeVisible();
      }
    });

    test('should filter tracking history', async ({ page }) => {
      // トラッキング履歴のフィルタリング
      await page.click('[data-testid="history-tab"]');
      await helpers.component.waitForComponent('[data-testid="tracking-history"]');
      
      // フィルターコントロールの確認
      await expect(page.locator('[data-testid="history-date-filter"]')).toBeVisible();
      await expect(page.locator('[data-testid="history-drone-filter"]')).toBeVisible();
      await expect(page.locator('[data-testid="history-status-filter"]')).toBeVisible();
      
      // 日付フィルターの適用
      await page.fill('[data-testid="history-date-from"]', '2024-01-01');
      await page.fill('[data-testid="history-date-to"]', '2024-12-31');
      
      // ドローンフィルターの適用
      await page.selectOption('[data-testid="history-drone-filter"]', 'test-drone-1');
      
      // フィルター適用
      await page.click('[data-testid="apply-history-filter"]');
      
      // フィルター結果の確認
      await helpers.api.waitForApiCall('/api/tracking/history', 'GET');
      await helpers.component.waitForTable('[data-testid="history-table"]');
    });

    test('should export tracking history', async ({ page }) => {
      // トラッキング履歴のエクスポート
      await page.click('[data-testid="history-tab"]');
      await helpers.component.waitForComponent('[data-testid="tracking-history"]');
      
      // エクスポートボタンのクリック
      await page.click('[data-testid="export-history-button"]');
      
      // エクスポート設定ダイアログの確認
      await helpers.component.waitForComponent('[data-testid="export-history-modal"]');
      
      // エクスポート形式の選択
      await page.selectOption('[data-testid="export-format-select"]', 'csv');
      
      // 期間の選択
      await page.selectOption('[data-testid="export-period-select"]', 'last_month');
      
      // エクスポート実行
      await page.click('[data-testid="export-button"]');
      
      // API呼び出しの確認
      await helpers.api.waitForApiCall('/api/tracking/history/export', 'POST');
      
      // 成功メッセージの確認
      await expect(page.locator('[data-testid="success-message"]')).toContainText('履歴のエクスポートが完了しました');
    });

    test('should display real-time tracking logs', async ({ page }) => {
      // リアルタイムトラッキングログの表示
      await page.click('[data-testid="logs-tab"]');
      
      await helpers.component.waitForComponent('[data-testid="tracking-logs"]');
      
      // ログ表示エリアの確認
      await expect(page.locator('[data-testid="log-container"]')).toBeVisible();
      await expect(page.locator('[data-testid="log-level-filter"]')).toBeVisible();
      await expect(page.locator('[data-testid="clear-logs-button"]')).toBeVisible();
      
      // ログレベルフィルターの確認
      await expect(page.locator('[data-testid="log-level-filter"] option[value="info"]')).toBeVisible();
      await expect(page.locator('[data-testid="log-level-filter"] option[value="warning"]')).toBeVisible();
      await expect(page.locator('[data-testid="log-level-filter"] option[value="error"]')).toBeVisible();
      
      // ログエントリの確認
      const logEntries = page.locator('[data-testid="log-entry"]');
      if (await logEntries.count() > 0) {
        await expect(logEntries.first().locator('[data-testid="log-timestamp"]')).toBeVisible();
        await expect(logEntries.first().locator('[data-testid="log-level"]')).toBeVisible();
        await expect(logEntries.first().locator('[data-testid="log-message"]')).toBeVisible();
      }
    });
  });

  test.describe('Performance and Error Handling', () => {
    test('should maintain stable frame rate during tracking', async ({ page }) => {
      // トラッキング中のフレームレート安定性
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.selectOption('[data-testid="model-select"]', 'test-tracking-model');
      await page.click('[data-testid="start-tracking-button"]');
      
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      
      // フレームレートの監視
      await page.waitForFunction(() => {
        const fpsElement = document.querySelector('[data-testid="fps-display"]');
        const fps = parseFloat(fpsElement?.textContent || '0');
        return fps >= 15; // 最低15FPS
      }, { timeout: 30000 });
      
      // 処理時間の確認
      const processingTime = await page.textContent('[data-testid="processing-time"]');
      const timeMs = parseFloat(processingTime?.replace('ms', '') || '0');
      expect(timeMs).toBeLessThan(100); // 100ms以内
    });

    test('should handle camera stream errors', async ({ page }) => {
      // カメラストリームエラーの処理
      await helpers.component.waitForComponent('[data-testid="camera-stream"]');
      
      // ストリームエラーのシミュレーション
      await helpers.api.mockApiResponse('/api/camera/stream', {
        error: 'Camera not available',
        status: 'error'
      });
      
      await page.reload();
      
      // エラー表示の確認
      await expect(page.locator('[data-testid="stream-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="stream-error"]')).toContainText('カメラに接続できません');
      
      // 再接続ボタンの確認
      await expect(page.locator('[data-testid="reconnect-camera-button"]')).toBeVisible();
    });

    test('should handle model loading errors', async ({ page }) => {
      // モデル読み込みエラーの処理
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.selectOption('[data-testid="model-select"]', 'invalid-model');
      
      // モデルエラーのシミュレーション
      await helpers.api.mockApiResponse('/api/models/invalid-model', {
        error: 'Model not found',
        status: 404
      });
      
      await page.click('[data-testid="start-tracking-button"]');
      
      // エラーメッセージの確認
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-message"]')).toContainText('モデルの読み込みに失敗しました');
    });

    test('should recover from network interruptions', async ({ page }) => {
      // ネットワーク中断からの復旧
      await page.selectOption('[data-testid="drone-select"]', 'test-drone-1');
      await page.selectOption('[data-testid="model-select"]', 'test-tracking-model');
      await page.click('[data-testid="start-tracking-button"]');
      
      await helpers.api.waitForApiCall('/api/tracking/start', 'POST');
      
      // ネットワーク中断のシミュレーション
      await page.route('**/api/tracking/**', route => route.abort());
      
      // 中断状態の確認
      await expect(page.locator('[data-testid="connection-status"]')).toContainText('接続中断');
      
      // ネットワーク復旧のシミュレーション
      await page.unroute('**/api/tracking/**');
      
      // 自動再接続の確認
      await page.waitForFunction(() => {
        const statusElement = document.querySelector('[data-testid="connection-status"]');
        return statusElement?.textContent?.includes('接続済み');
      }, { timeout: 15000 });
    });
  });
});