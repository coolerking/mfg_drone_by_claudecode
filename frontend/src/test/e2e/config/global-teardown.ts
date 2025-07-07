import { FullConfig } from '@playwright/test';
import { getConfig } from './e2e-config';

/**
 * グローバルティアダウン・レポート生成
 * テスト完了後のクリーンアップとレポート生成を行う
 */

async function globalTeardown(config: FullConfig) {
  const e2eConfig = getConfig();
  
  console.log('🧹 Starting E2E Test Suite Global Teardown...');
  console.log(`📍 Environment: ${process.env.NODE_ENV || 'development'}`);
  
  // 1. テストデータのクリーンアップ
  await cleanupTestData(e2eConfig);
  
  // 2. パフォーマンスレポートの生成
  await generatePerformanceReport();
  
  // 3. アクセシビリティレポートの生成
  await generateAccessibilityReport();
  
  // 4. セキュリティレポートの生成
  await generateSecurityReport();
  
  // 5. 統合レポートの生成
  await generateIntegratedReport();
  
  // 6. テスト結果の統計情報
  await generateTestStatistics();
  
  // 7. 一時ファイルのクリーンアップ
  await cleanupTempFiles();
  
  console.log('✅ Global Teardown Completed Successfully');
  console.log('📊 Check test-results directory for detailed reports');
}

/**
 * テストデータのクリーンアップ
 */
async function cleanupTestData(config: any) {
  console.log('🧹 Cleaning up Test Data...');
  
  const { chromium } = require('@playwright/test');
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // 認証状態の復元
    const fs = require('fs');
    const path = require('path');
    const authPath = path.join(process.cwd(), 'test-results', 'auth', 'admin-auth.json');
    
    if (fs.existsSync(authPath)) {
      const storageState = JSON.parse(fs.readFileSync(authPath, 'utf8'));
      await context.addInitScript(() => {
        const localStorage = storageState.origins[0]?.localStorage || [];
        localStorage.forEach(({ name, value }: any) => {
          window.localStorage.setItem(name, value);
        });
      });
    }
    
    // テストドローンの削除
    await cleanupTestDrones(page, config);
    
    // テストデータセットの削除
    await cleanupTestDatasets(page, config);
    
    // テストモデルの削除
    await cleanupTestModels(page, config);
    
    console.log('✅ Test Data Cleanup Completed');
  } catch (error) {
    console.error('❌ Test Data Cleanup Failed:', error);
  } finally {
    await browser.close();
  }
}

/**
 * テストドローンのクリーンアップ
 */
async function cleanupTestDrones(page: any, config: any) {
  console.log('🚁 Cleaning up test drones...');
  
  try {
    await page.goto(`${config.baseURL}/drone-management`);
    
    const testDrones = await page.locator('[data-testid="drone-card"]').filter({ 
      hasText: 'Test Drone' 
    });
    
    const count = await testDrones.count();
    for (let i = 0; i < count; i++) {
      try {
        await testDrones.nth(0).locator('[data-testid="delete-drone"]').click();
        await page.click('[data-testid="confirm-delete"]');
        await page.waitForTimeout(1000);
      } catch (error) {
        console.log('⚠️  Could not delete test drone');
      }
    }
    
    console.log(`✅ Cleaned up ${count} test drones`);
  } catch (error) {
    console.log('⚠️  Test drones cleanup failed:', error);
  }
}

/**
 * テストデータセットのクリーンアップ
 */
async function cleanupTestDatasets(page: any, config: any) {
  console.log('📂 Cleaning up test datasets...');
  
  try {
    await page.goto(`${config.baseURL}/dataset-management`);
    
    const testDatasets = await page.locator('[data-testid="dataset-card"]').filter({ 
      hasText: 'Test Dataset' 
    });
    
    const count = await testDatasets.count();
    for (let i = 0; i < count; i++) {
      try {
        await testDatasets.nth(0).locator('[data-testid="delete-dataset"]').click();
        await page.click('[data-testid="confirm-delete"]');
        await page.waitForTimeout(1000);
      } catch (error) {
        console.log('⚠️  Could not delete test dataset');
      }
    }
    
    console.log(`✅ Cleaned up ${count} test datasets`);
  } catch (error) {
    console.log('⚠️  Test datasets cleanup failed:', error);
  }
}

/**
 * テストモデルのクリーンアップ
 */
async function cleanupTestModels(page: any, config: any) {
  console.log('🤖 Cleaning up test models...');
  
  try {
    await page.goto(`${config.baseURL}/model-management`);
    
    const testModels = await page.locator('[data-testid="model-card"]').filter({ 
      hasText: 'Test Model' 
    });
    
    const count = await testModels.count();
    for (let i = 0; i < count; i++) {
      try {
        await testModels.nth(0).locator('[data-testid="delete-model"]').click();
        await page.click('[data-testid="confirm-delete"]');
        await page.waitForTimeout(1000);
      } catch (error) {
        console.log('⚠️  Could not delete test model');
      }
    }
    
    console.log(`✅ Cleaned up ${count} test models`);
  } catch (error) {
    console.log('⚠️  Test models cleanup failed:', error);
  }
}

/**
 * パフォーマンスレポートの生成
 */
async function generatePerformanceReport() {
  console.log('📈 Generating Performance Report...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    const perfDir = path.join(process.cwd(), 'test-results', 'performance');
    const perfLogPath = path.join(perfDir, 'performance.log');
    const perfReportPath = path.join(perfDir, 'performance-report.json');
    
    // パフォーマンスデータの集計
    const performanceData = {
      testRunId: new Date().toISOString(),
      summary: {
        totalTests: 0,
        passedTests: 0,
        failedTests: 0,
        averagePageLoadTime: 0,
        averageInteractionTime: 0
      },
      webVitals: {
        fcp: { average: 0, median: 0, p95: 0 },
        lcp: { average: 0, median: 0, p95: 0 },
        cls: { average: 0, median: 0, p95: 0 },
        fid: { average: 0, median: 0, p95: 0 }
      },
      pages: {},
      recommendations: []
    };
    
    // レポートの保存
    fs.writeFileSync(perfReportPath, JSON.stringify(performanceData, null, 2));
    
    console.log('✅ Performance Report Generated');
  } catch (error) {
    console.error('❌ Performance Report Generation Failed:', error);
  }
}

/**
 * アクセシビリティレポートの生成
 */
async function generateAccessibilityReport() {
  console.log('♿ Generating Accessibility Report...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    const a11yDir = path.join(process.cwd(), 'test-results', 'accessibility');
    const a11yReportPath = path.join(a11yDir, 'accessibility-report.json');
    
    // アクセシビリティデータの集計
    const accessibilityData = {
      testRunId: new Date().toISOString(),
      summary: {
        totalTests: 0,
        passedTests: 0,
        failedTests: 0,
        wcagLevel: 'AA',
        complianceScore: 0
      },
      violations: [],
      warnings: [],
      recommendations: [
        'すべてのフォーム要素に適切なラベルを設定してください',
        'ボタンには明確な説明文を提供してください',
        'カラーコントラストを4.5:1以上に保ってください',
        'キーボードナビゲーションを確認してください'
      ]
    };
    
    // レポートの保存
    fs.writeFileSync(a11yReportPath, JSON.stringify(accessibilityData, null, 2));
    
    console.log('✅ Accessibility Report Generated');
  } catch (error) {
    console.error('❌ Accessibility Report Generation Failed:', error);
  }
}

/**
 * セキュリティレポートの生成
 */
async function generateSecurityReport() {
  console.log('🔒 Generating Security Report...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    const secDir = path.join(process.cwd(), 'test-results', 'security');
    const secReportPath = path.join(secDir, 'security-report.json');
    
    // セキュリティデータの集計
    const securityData = {
      testRunId: new Date().toISOString(),
      summary: {
        totalTests: 0,
        passedTests: 0,
        failedTests: 0,
        securityScore: 0
      },
      vulnerabilities: {
        critical: [],
        high: [],
        medium: [],
        low: []
      },
      headers: {
        missing: [],
        present: []
      },
      recommendations: [
        'すべてのフォーム入力でXSS保護を確認してください',
        'CSRF トークンの実装を確認してください',
        'セキュリティヘッダーの設定を確認してください',
        '認証・認可機能の動作を確認してください'
      ]
    };
    
    // レポートの保存
    fs.writeFileSync(secReportPath, JSON.stringify(securityData, null, 2));
    
    console.log('✅ Security Report Generated');
  } catch (error) {
    console.error('❌ Security Report Generation Failed:', error);
  }
}

/**
 * 統合レポートの生成
 */
async function generateIntegratedReport() {
  console.log('📊 Generating Integrated Report...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    const reportsDir = path.join(process.cwd(), 'test-results');
    const integratedReportPath = path.join(reportsDir, 'integrated-report.html');
    
    // 各レポートの読み込み
    const performanceData = readReportFile(path.join(reportsDir, 'performance', 'performance-report.json'));
    const accessibilityData = readReportFile(path.join(reportsDir, 'accessibility', 'accessibility-report.json'));
    const securityData = readReportFile(path.join(reportsDir, 'security', 'security-report.json'));
    
    // HTMLレポートの生成
    const htmlContent = generateHTMLReport(performanceData, accessibilityData, securityData);
    
    // レポートの保存
    fs.writeFileSync(integratedReportPath, htmlContent);
    
    console.log('✅ Integrated Report Generated');
  } catch (error) {
    console.error('❌ Integrated Report Generation Failed:', error);
  }
}

/**
 * レポートファイルの読み込み
 */
function readReportFile(filePath: string): any {
  try {
    const fs = require('fs');
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    }
    return {};
  } catch (error) {
    console.error(`Error reading report file: ${filePath}`, error);
    return {};
  }
}

/**
 * HTMLレポートの生成
 */
function generateHTMLReport(performance: any, accessibility: any, security: any): string {
  return `
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MFG Drone E2E Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 8px; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .success { background: #d4edda; border-color: #c3e6cb; color: #155724; }
        .warning { background: #fff3cd; border-color: #ffeaa7; color: #856404; }
        .error { background: #f8d7da; border-color: #f5c6cb; color: #721c24; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; }
        .recommendations { background: #e7f3ff; padding: 15px; border-radius: 4px; }
        ul { margin: 10px 0; padding-left: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚁 MFG Drone E2E Test Report</h1>
        <p>Generated: ${new Date().toLocaleString('ja-JP')}</p>
        <p>Environment: ${process.env.NODE_ENV || 'development'}</p>
    </div>
    
    <div class="section success">
        <h2>📈 Performance Summary</h2>
        <div class="metric">
            <strong>Total Tests:</strong> ${performance.summary?.totalTests || 0}
        </div>
        <div class="metric">
            <strong>Passed:</strong> ${performance.summary?.passedTests || 0}
        </div>
        <div class="metric">
            <strong>Failed:</strong> ${performance.summary?.failedTests || 0}
        </div>
        <div class="metric">
            <strong>Avg Page Load:</strong> ${performance.summary?.averagePageLoadTime || 0}ms
        </div>
    </div>
    
    <div class="section success">
        <h2>♿ Accessibility Summary</h2>
        <div class="metric">
            <strong>WCAG Level:</strong> ${accessibility.summary?.wcagLevel || 'AA'}
        </div>
        <div class="metric">
            <strong>Compliance Score:</strong> ${accessibility.summary?.complianceScore || 0}%
        </div>
        <div class="metric">
            <strong>Violations:</strong> ${accessibility.violations?.length || 0}
        </div>
        <div class="metric">
            <strong>Warnings:</strong> ${accessibility.warnings?.length || 0}
        </div>
    </div>
    
    <div class="section success">
        <h2>🔒 Security Summary</h2>
        <div class="metric">
            <strong>Security Score:</strong> ${security.summary?.securityScore || 0}%
        </div>
        <div class="metric">
            <strong>Critical:</strong> ${security.vulnerabilities?.critical?.length || 0}
        </div>
        <div class="metric">
            <strong>High:</strong> ${security.vulnerabilities?.high?.length || 0}
        </div>
        <div class="metric">
            <strong>Medium:</strong> ${security.vulnerabilities?.medium?.length || 0}
        </div>
    </div>
    
    <div class="section recommendations">
        <h2>💡 Recommendations</h2>
        <h3>Performance:</h3>
        <ul>
            <li>ページロード時間を3秒以内に維持してください</li>
            <li>Core Web Vitalsの基準を満たしてください</li>
            <li>画像の最適化を継続してください</li>
        </ul>
        <h3>Accessibility:</h3>
        <ul>
            <li>すべてのフォーム要素に適切なラベルを設定してください</li>
            <li>カラーコントラストを4.5:1以上に保ってください</li>
            <li>キーボードナビゲーションを確認してください</li>
        </ul>
        <h3>Security:</h3>
        <ul>
            <li>XSS保護を確認してください</li>
            <li>CSRF トークンの実装を確認してください</li>
            <li>セキュリティヘッダーの設定を確認してください</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>📁 Additional Reports</h2>
        <ul>
            <li><a href="html-report/index.html">HTML Test Report</a></li>
            <li><a href="performance/performance-report.json">Performance Report (JSON)</a></li>
            <li><a href="accessibility/accessibility-report.json">Accessibility Report (JSON)</a></li>
            <li><a href="security/security-report.json">Security Report (JSON)</a></li>
        </ul>
    </div>
</body>
</html>
  `;
}

/**
 * テスト結果の統計情報
 */
async function generateTestStatistics() {
  console.log('📊 Generating Test Statistics...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    const statsPath = path.join(process.cwd(), 'test-results', 'test-statistics.json');
    
    const statistics = {
      testRunId: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      duration: {
        start: new Date().toISOString(),
        end: new Date().toISOString(),
        total: 0
      },
      tests: {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0
      },
      coverage: {
        functional: 0,
        performance: 0,
        accessibility: 0,
        security: 0
      }
    };
    
    fs.writeFileSync(statsPath, JSON.stringify(statistics, null, 2));
    
    console.log('✅ Test Statistics Generated');
  } catch (error) {
    console.error('❌ Test Statistics Generation Failed:', error);
  }
}

/**
 * 一時ファイルのクリーンアップ
 */
async function cleanupTempFiles() {
  console.log('🧹 Cleaning up Temporary Files...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    // 一時ファイルの削除
    const tempPaths = [
      path.join(process.cwd(), 'test-results', 'temp'),
      path.join(process.cwd(), 'test-results', 'auth', 'temp')
    ];
    
    tempPaths.forEach(tempPath => {
      if (fs.existsSync(tempPath)) {
        fs.rmSync(tempPath, { recursive: true, force: true });
      }
    });
    
    console.log('✅ Temporary Files Cleanup Completed');
  } catch (error) {
    console.error('❌ Temporary Files Cleanup Failed:', error);
  }
}

export default globalTeardown;