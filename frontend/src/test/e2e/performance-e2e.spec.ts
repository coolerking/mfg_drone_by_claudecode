import { test, expect } from '@playwright/test';
import { TestHelperFactory } from './helpers/test-helpers';

/**
 * パフォーマンスE2Eテスト
 * Core Web Vitals、ページロード時間、操作応答時間、メモリ使用量をテスト
 */

test.describe('Performance E2E Tests', () => {
  let helpers: ReturnType<typeof TestHelperFactory.createHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = TestHelperFactory.createHelpers(page);
  });

  test.afterEach(async ({ page }) => {
    await helpers.cleanup.cleanupTestData();
  });

  test.describe('Core Web Vitals', () => {
    test('should meet Core Web Vitals thresholds for dashboard', async ({ page }) => {
      // ダッシュボードのCore Web Vitals測定
      await helpers.auth.login();
      
      // ページロード前にパフォーマンス監視を開始
      await page.addInitScript(() => {
        window.performanceMetrics = {
          fcp: 0,
          lcp: 0,
          cls: 0,
          fid: 0,
          ttfb: 0
        };
        
        // Performance Observer for Core Web Vitals
        if ('PerformanceObserver' in window) {
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (entry.entryType === 'paint' && entry.name === 'first-contentful-paint') {
                window.performanceMetrics.fcp = entry.startTime;
              }
              if (entry.entryType === 'largest-contentful-paint') {
                window.performanceMetrics.lcp = entry.startTime;
              }
              if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
                window.performanceMetrics.cls += entry.value;
              }
            }
          }).observe({ entryTypes: ['paint', 'largest-contentful-paint', 'layout-shift'] });
          
          // FID measurement
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (entry.processingStart && entry.startTime) {
                window.performanceMetrics.fid = entry.processingStart - entry.startTime;
              }
            }
          }).observe({ entryTypes: ['first-input'] });
        }
      });
      
      // ダッシュボードにナビゲート
      const startTime = Date.now();
      await helpers.navigation.navigateToPage('dashboard');
      await helpers.component.waitForComponent('[data-testid="dashboard"]');
      const loadTime = Date.now() - startTime;
      
      // Core Web Vitalsの取得
      const vitals = await helpers.performance.getCoreWebVitals();
      
      // ページロード時間の検証
      expect(loadTime).toBeLessThan(3000); // 3秒以内
      
      // Core Web Vitalsの検証
      if (vitals.fcp) {
        expect(vitals.fcp.value).toBeLessThan(2000); // FCP: 2秒以内
      }
      
      if (vitals.lcp) {
        expect(vitals.lcp.value).toBeLessThan(2500); // LCP: 2.5秒以内
      }
      
      if (vitals.cls !== undefined) {
        expect(vitals.cls.value).toBeLessThan(0.1); // CLS: 0.1未満
      }
      
      if (vitals.fid) {
        expect(vitals.fid.value).toBeLessThan(100); // FID: 100ms未満
      }
    });

    test('should maintain performance on data-heavy pages', async ({ page }) => {
      // データ量の多いページでのパフォーマンス維持
      await helpers.auth.login();
      
      // 大量データのモック
      const largeDataset = Array.from({ length: 500 }, (_, i) => ({
        id: i,
        name: `Dataset ${i}`,
        type: 'object_detection',
        imageCount: Math.floor(Math.random() * 1000),
        createdAt: new Date().toISOString()
      }));
      
      await helpers.api.mockApiResponse('/api/datasets', {
        data: largeDataset,
        total: 500
      });
      
      // データセット管理ページの読み込み
      const startTime = Date.now();
      await helpers.navigation.navigateToPage('dataset-management');
      await helpers.component.waitForComponent('[data-testid="dataset-list"]');
      const loadTime = Date.now() - startTime;
      
      // 大量データでも5秒以内で読み込み完了
      expect(loadTime).toBeLessThan(5000);
      
      // 仮想スクロールの動作確認
      await expect(page.locator('[data-testid="virtual-scroll"]')).toBeVisible();
      
      // スクロールパフォーマンスの確認
      const scrollStartTime = Date.now();
      for (let i = 0; i < 10; i++) {
        await page.mouse.wheel(0, 500);
        await page.waitForTimeout(100);
      }
      const scrollTime = Date.now() - scrollStartTime;
      
      // スクロール応答性の確認（1秒以内で10回スクロール）
      expect(scrollTime).toBeLessThan(1000);
    });

    test('should optimize image loading performance', async ({ page }) => {
      // 画像読み込みパフォーマンスの最適化確認
      await helpers.auth.login();
      
      // 大量画像データのモック
      const imageDataset = {
        id: 1,
        name: 'Image Performance Test',
        images: Array.from({ length: 100 }, (_, i) => ({
          id: i,
          url: `https://picsum.photos/300/200?random=${i}`,
          thumbnail: `https://picsum.photos/150/100?random=${i}`,
          labels: [`object_${i % 10}`]
        }))
      };
      
      await helpers.api.mockApiResponse('/api/datasets/1', imageDataset);
      
      // 画像ギャラリーページの読み込み
      await page.goto('/dataset-management/1/images');
      await helpers.component.waitForComponent('[data-testid="image-gallery"]');
      
      // 遅延読み込みの確認
      const lazyImages = page.locator('[data-testid="lazy-image"]');
      const visibleImages = page.locator('[data-testid="lazy-image"]:visible');
      
      // 最初は一部の画像のみ表示されている
      const totalImages = await lazyImages.count();
      const initialVisibleImages = await visibleImages.count();
      
      expect(totalImages).toBeGreaterThan(initialVisibleImages);
      
      // スクロールによる段階的読み込み
      await page.mouse.wheel(0, 1000);
      await page.waitForTimeout(1000);
      
      const afterScrollVisibleImages = await visibleImages.count();
      expect(afterScrollVisibleImages).toBeGreaterThan(initialVisibleImages);
      
      // 画像読み込み時間の確認
      const imageLoadTime = await page.evaluate(() => {
        return new Promise((resolve) => {
          const images = document.querySelectorAll('img[data-testid="lazy-image"]');
          let loadedCount = 0;
          const startTime = Date.now();
          
          images.forEach(img => {
            if (img.complete) {
              loadedCount++;
            } else {
              img.onload = () => {
                loadedCount++;
                if (loadedCount === images.length) {
                  resolve(Date.now() - startTime);
                }
              };
            }
          });
          
          if (loadedCount === images.length) {
            resolve(Date.now() - startTime);
          }
          
          setTimeout(() => resolve(Date.now() - startTime), 10000);
        });
      });
      
      // 画像読み込みは10秒以内
      expect(imageLoadTime).toBeLessThan(10000);
    });
  });

  test.describe('Page Load Performance', () => {
    test('should load all main pages within threshold', async ({ page }) => {
      // 全メインページの読み込み時間確認
      await helpers.auth.login();
      
      const pages = [
        { name: 'dashboard', path: '/dashboard', threshold: 3000 },
        { name: 'drone-management', path: '/drone-management', threshold: 4000 },
        { name: 'dataset-management', path: '/dataset-management', threshold: 4000 },
        { name: 'model-management', path: '/model-management', threshold: 4000 },
        { name: 'tracking-control', path: '/tracking-control', threshold: 5000 },
        { name: 'system-monitoring', path: '/system-monitoring', threshold: 3000 },
        { name: 'settings', path: '/settings', threshold: 2000 }
      ];
      
      for (const pageInfo of pages) {
        console.log(`Testing ${pageInfo.name} page load performance...`);
        
        const loadTime = await helpers.performance.measurePageLoad(pageInfo.path);
        
        expect(loadTime).toBeLessThan(pageInfo.threshold);
        console.log(`${pageInfo.name}: ${loadTime}ms (threshold: ${pageInfo.threshold}ms)`);
        
        // ページの主要要素が表示されることを確認
        await expect(page.locator('[data-testid="page-content"]')).toBeVisible();
      }
    });

    test('should handle cold start performance', async ({ page }) => {
      // コールドスタート時のパフォーマンス
      // ブラウザキャッシュをクリア
      await page.context().clearCookies();
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      
      // 初回アクセス時の読み込み時間
      const coldStartTime = await helpers.performance.measurePageLoad('/login');
      
      // コールドスタートでも5秒以内
      expect(coldStartTime).toBeLessThan(5000);
      
      // ログイン処理
      await helpers.auth.login();
      
      // ダッシュボードの初回読み込み
      const dashboardColdTime = await helpers.performance.measurePageLoad('/dashboard');
      
      // 初回ダッシュボード読み込みは6秒以内
      expect(dashboardColdTime).toBeLessThan(6000);
      
      // キャッシュ効果の確認（2回目のアクセス）
      const dashboardWarmTime = await helpers.performance.measurePageLoad('/dashboard');
      
      // キャッシュ後は初回より速い
      expect(dashboardWarmTime).toBeLessThan(dashboardColdTime);
      
      // ウォームアクセスは3秒以内
      expect(dashboardWarmTime).toBeLessThan(3000);
    });

    test('should optimize bundle loading', async ({ page }) => {
      // バンドル読み込みの最適化確認
      const resourceLoadTimes = [];
      
      page.on('response', response => {
        if (response.url().includes('.js') || response.url().includes('.css')) {
          const timing = response.timing();
          resourceLoadTimes.push({
            url: response.url(),
            size: response.headers()['content-length'],
            loadTime: timing.responseEnd - timing.responseStart
          });
        }
      });
      
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // バンドルサイズの確認
      const jsResources = resourceLoadTimes.filter(r => r.url.includes('.js'));
      const cssResources = resourceLoadTimes.filter(r => r.url.includes('.css'));
      
      // メインバンドルサイズが適切な範囲内
      const mainBundle = jsResources.find(r => r.url.includes('main') || r.url.includes('index'));
      if (mainBundle && mainBundle.size) {
        const sizeKB = parseInt(mainBundle.size) / 1024;
        expect(sizeKB).toBeLessThan(500); // 500KB以下
      }
      
      // リソース読み込み時間
      jsResources.forEach(resource => {
        expect(resource.loadTime).toBeLessThan(2000); // 2秒以内
      });
      
      cssResources.forEach(resource => {
        expect(resource.loadTime).toBeLessThan(1000); // 1秒以内
      });
    });
  });

  test.describe('Interaction Performance', () => {
    test('should respond quickly to user interactions', async ({ page }) => {
      // ユーザー操作への応答性能
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('drone-management');
      
      // ボタンクリック応答時間
      const buttonClickTime = await helpers.performance.measureInteraction('[data-testid="add-drone-button"]');
      expect(buttonClickTime).toBeLessThan(500); // 500ms以内
      
      // モーダル表示応答時間
      await expect(page.locator('[data-testid="add-drone-modal"]')).toBeVisible({ timeout: 1000 });
      
      await page.click('[data-testid="cancel-button"]');
      
      // フォーム入力応答時間
      await helpers.navigation.navigateToPage('dataset-management');
      await page.click('[data-testid="create-dataset-button"]');
      
      const inputStartTime = Date.now();
      await page.fill('[data-testid="dataset-name"]', 'Performance Test Dataset');
      const inputTime = Date.now() - inputStartTime;
      
      expect(inputTime).toBeLessThan(200); // 200ms以内
      
      // 検索機能応答時間
      await page.click('[data-testid="cancel-button"]');
      await helpers.component.waitForComponent('[data-testid="dataset-list"]');
      
      const searchTime = await helpers.performance.measureInteraction(
        '[data-testid="search-input"]', 
        'fill', 
        'test'
      );
      expect(searchTime).toBeLessThan(1000); // 1秒以内
    });

    test('should handle rapid successive interactions', async ({ page }) => {
      // 連続操作の処理性能
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('tracking-control');
      
      // パラメータスライダーの連続調整
      const slider = page.locator('[data-testid="confidence-threshold-slider"]');
      
      const rapidInteractionStart = Date.now();
      
      // 10回連続でスライダーを調整
      for (let i = 0; i < 10; i++) {
        const value = (0.5 + (i * 0.05)).toString();
        await slider.fill(value);
        await page.waitForTimeout(50); // 50ms間隔
      }
      
      const rapidInteractionTime = Date.now() - rapidInteractionStart;
      
      // 連続操作は2秒以内で完了
      expect(rapidInteractionTime).toBeLessThan(2000);
      
      // 最終値が正しく反映されている
      const finalValue = await slider.inputValue();
      expect(parseFloat(finalValue)).toBeCloseTo(0.95, 1);
      
      // UI がフリーズしていないことを確認
      const uiResponsive = await page.evaluate(() => {
        return document.readyState === 'complete';
      });
      expect(uiResponsive).toBeTruthy();
    });

    test('should maintain performance during real-time updates', async ({ page }) => {
      // リアルタイム更新中のパフォーマンス維持
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('system-monitoring');
      
      // リアルタイム更新の開始
      await page.click('[data-testid="start-monitoring-button"]');
      
      // フレームレート測定の開始
      const frameRates = [];
      let frameCount = 0;
      let lastTime = Date.now();
      
      // 10秒間フレームレートを監視
      const monitoringPromise = new Promise((resolve) => {
        const interval = setInterval(async () => {
          frameCount++;
          const currentTime = Date.now();
          const deltaTime = currentTime - lastTime;
          
          if (deltaTime >= 1000) {
            const fps = frameCount * 1000 / deltaTime;
            frameRates.push(fps);
            frameCount = 0;
            lastTime = currentTime;
            
            if (frameRates.length >= 10) {
              clearInterval(interval);
              resolve(frameRates);
            }
          }
        }, 16); // ~60fps
      });
      
      // リアルタイム更新中にUI操作
      await page.click('[data-testid="settings-tab"]');
      await page.click('[data-testid="monitoring-tab"]');
      
      const measuredFrameRates = await monitoringPromise;
      
      // 平均フレームレートが30fps以上
      const avgFrameRate = measuredFrameRates.reduce((sum, rate) => sum + rate, 0) / measuredFrameRates.length;
      expect(avgFrameRate).toBeGreaterThan(30);
      
      // フレームレートの安定性（標準偏差が小さい）
      const variance = measuredFrameRates.reduce((sum, rate) => {
        return sum + Math.pow(rate - avgFrameRate, 2);
      }, 0) / measuredFrameRates.length;
      const standardDeviation = Math.sqrt(variance);
      
      expect(standardDeviation).toBeLessThan(10); // フレームレートの変動が10fps以内
    });
  });

  test.describe('Memory Performance', () => {
    test('should manage memory efficiently', async ({ page }) => {
      // メモリ効率的な管理
      await helpers.auth.login();
      
      // 初期メモリ使用量の測定
      const initialMemory = await page.evaluate(() => {
        return performance.memory ? {
          used: performance.memory.usedJSHeapSize,
          total: performance.memory.totalJSHeapSize,
          limit: performance.memory.jsHeapSizeLimit
        } : null;
      });
      
      if (!initialMemory) {
        console.log('Memory API not available, skipping memory tests');
        return;
      }
      
      // 複数ページの閲覧でメモリ使用量を監視
      const pages = [
        'dashboard',
        'drone-management',
        'dataset-management',
        'model-management',
        'tracking-control'
      ];
      
      const memoryReadings = [];
      
      for (const pageName of pages) {
        await helpers.navigation.navigateToPage(pageName);
        await helpers.component.waitForComponent('[data-testid="page-content"]');
        await page.waitForTimeout(2000); // ページが安定するまで待機
        
        const memory = await page.evaluate(() => {
          return performance.memory ? {
            used: performance.memory.usedJSHeapSize,
            total: performance.memory.totalJSHeapSize
          } : null;
        });
        
        if (memory) {
          memoryReadings.push({
            page: pageName,
            used: memory.used,
            total: memory.total
          });
        }
      }
      
      // メモリ使用量の分析
      const maxMemoryUsed = Math.max(...memoryReadings.map(r => r.used));
      const minMemoryUsed = Math.min(...memoryReadings.map(r => r.used));
      
      // メモリ使用量が100MB以下
      expect(maxMemoryUsed).toBeLessThan(100 * 1024 * 1024);
      
      // メモリリークがないことを確認（ページ間での使用量増加が50MB以下）
      const memoryIncrease = maxMemoryUsed - minMemoryUsed;
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);
    });

    test('should handle memory-intensive operations', async ({ page }) => {
      // メモリ集約的操作の処理
      await helpers.auth.login();
      
      // 大量データの処理
      const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        name: `Large Item ${i}`,
        data: 'x'.repeat(1000) // 1KB のダミーデータ
      }));
      
      await helpers.api.mockApiResponse('/api/large-dataset', {
        data: largeDataset,
        total: 1000
      });
      
      const beforeMemory = await page.evaluate(() => {
        return performance.memory ? performance.memory.usedJSHeapSize : 0;
      });
      
      // 大量データページの読み込み
      await page.goto('/dataset-management');
      await helpers.component.waitForComponent('[data-testid="dataset-list"]');
      
      // データ処理完了まで待機
      await page.waitForTimeout(5000);
      
      const afterMemory = await page.evaluate(() => {
        return performance.memory ? performance.memory.usedJSHeapSize : 0;
      });
      
      const memoryIncrease = afterMemory - beforeMemory;
      
      // メモリ増加が30MB以下
      expect(memoryIncrease).toBeLessThan(30 * 1024 * 1024);
      
      // ガベージコレクション後のメモリ確認
      await page.evaluate(() => {
        if (window.gc) {
          window.gc();
        }
      });
      
      await page.waitForTimeout(2000);
      
      const afterGCMemory = await page.evaluate(() => {
        return performance.memory ? performance.memory.usedJSHeapSize : 0;
      });
      
      // GC後にメモリが解放されている
      expect(afterGCMemory).toBeLessThan(afterMemory);
    });
  });

  test.describe('Network Performance', () => {
    test('should optimize API request performance', async ({ page }) => {
      // API リクエストパフォーマンス最適化
      const apiRequests = [];
      
      page.on('response', response => {
        if (response.url().includes('/api/')) {
          apiRequests.push({
            url: response.url(),
            method: response.request().method(),
            status: response.status(),
            timing: response.timing(),
            size: response.headers()['content-length']
          });
        }
      });
      
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // ダッシュボード読み込み完了まで待機
      await helpers.component.waitForComponent('[data-testid="dashboard"]');
      await page.waitForTimeout(3000);
      
      // API リクエストの分析
      const getRequests = apiRequests.filter(req => req.method === 'GET');
      
      // 並列リクエストの効率性確認
      const concurrentRequests = apiRequests.filter(req => {
        const requestTime = req.timing.requestStart;
        return apiRequests.some(other => 
          other !== req && 
          Math.abs(other.timing.requestStart - requestTime) < 100
        );
      });
      
      expect(concurrentRequests.length).toBeGreaterThan(0); // 並列実行されている
      
      // レスポンス時間の確認
      getRequests.forEach(request => {
        const responseTime = request.timing.responseEnd - request.timing.requestStart;
        expect(responseTime).toBeLessThan(2000); // 2秒以内
      });
      
      // レスポンスサイズの確認
      getRequests.forEach(request => {
        if (request.size) {
          const sizeKB = parseInt(request.size) / 1024;
          expect(sizeKB).toBeLessThan(1024); // 1MB以下
        }
      });
    });

    test('should handle network latency gracefully', async ({ page }) => {
      // ネットワーク遅延の適切な処理
      // 遅延シミュレーション
      await page.route('**/api/**', async route => {
        await new Promise(resolve => setTimeout(resolve, 1000)); // 1秒遅延
        route.continue();
      });
      
      await helpers.auth.login();
      
      const loadStartTime = Date.now();
      await helpers.navigation.navigateToPage('drone-management');
      
      // ローディングインジケーターの表示確認
      await expect(page.locator('[data-testid="loading-indicator"]')).toBeVisible();
      
      // ページ読み込み完了
      await helpers.component.waitForComponent('[data-testid="drone-list"]');
      const totalLoadTime = Date.now() - loadStartTime;
      
      // 遅延があってもタイムアウトしない（10秒以内）
      expect(totalLoadTime).toBeLessThan(10000);
      
      // ローディング状態の適切な管理
      await expect(page.locator('[data-testid="loading-indicator"]')).not.toBeVisible();
    });

    test('should implement effective caching strategy', async ({ page }) => {
      // 効果的なキャッシュ戦略の実装確認
      const requestCounts = new Map();
      
      page.on('request', request => {
        const url = request.url();
        if (url.includes('/api/')) {
          const count = requestCounts.get(url) || 0;
          requestCounts.set(url, count + 1);
        }
      });
      
      await helpers.auth.login();
      
      // 最初のダッシュボード読み込み
      await helpers.navigation.navigateToPage('dashboard');
      await helpers.component.waitForComponent('[data-testid="dashboard"]');
      
      const firstLoadRequests = new Map(requestCounts);
      
      // 他のページに移動
      await helpers.navigation.navigateToPage('drone-management');
      await helpers.component.waitForComponent('[data-testid="drone-list"]');
      
      // ダッシュボードに再訪問
      await helpers.navigation.navigateToPage('dashboard');
      await helpers.component.waitForComponent('[data-testid="dashboard"]');
      
      // キャッシュ効果の確認
      let cachedRequests = 0;
      let uncachedRequests = 0;
      
      requestCounts.forEach((count, url) => {
        const firstLoadCount = firstLoadRequests.get(url) || 0;
        if (count === firstLoadCount) {
          cachedRequests++;
        } else {
          uncachedRequests++;
        }
      });
      
      // キャッシュされたリクエストが存在する
      expect(cachedRequests).toBeGreaterThan(0);
      
      // キャッシュ率が50%以上
      const cacheRate = cachedRequests / (cachedRequests + uncachedRequests);
      expect(cacheRate).toBeGreaterThan(0.5);
    });
  });
});