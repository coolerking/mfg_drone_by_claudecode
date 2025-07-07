import { chromium, FullConfig } from '@playwright/test';
import { getConfig } from './e2e-config';

/**
 * グローバルセットアップ・初期化
 * テスト実行前の共通設定と環境準備を行う
 */

async function globalSetup(config: FullConfig) {
  const e2eConfig = getConfig();
  
  console.log('🚀 Starting E2E Test Suite Global Setup...');
  console.log(`📍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🌐 Base URL: ${e2eConfig.baseURL}`);
  
  // 1. 環境健全性チェック
  await checkEnvironmentHealth(e2eConfig);
  
  // 2. 認証設定の準備
  await setupAuthentication(e2eConfig);
  
  // 3. テストデータの準備
  await setupTestData(e2eConfig);
  
  // 4. パフォーマンス監視の初期化
  await initializePerformanceMonitoring(e2eConfig);
  
  // 5. レポートディレクトリの準備
  await setupReportingDirectories();
  
  console.log('✅ Global Setup Completed Successfully');
}

/**
 * 環境健全性チェック
 */
async function checkEnvironmentHealth(config: any) {
  console.log('🔍 Checking Environment Health...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // ヘルスチェックエンドポイントの確認
    console.log(`📡 Checking health endpoint: ${config.baseURL}/health`);
    const response = await page.goto(`${config.baseURL}/health`, {
      timeout: 30000,
      waitUntil: 'networkidle'
    });
    
    if (!response || response.status() !== 200) {
      console.log(`⚠️  Health check failed, trying main page: ${config.baseURL}`);
      const mainResponse = await page.goto(config.baseURL, {
        timeout: 30000,
        waitUntil: 'networkidle'
      });
      
      if (!mainResponse || mainResponse.status() !== 200) {
        throw new Error(`❌ Application is not accessible at ${config.baseURL}`);
      }
    }
    
    console.log('✅ Environment Health Check Passed');
  } catch (error) {
    console.error('❌ Environment Health Check Failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

/**
 * 認証設定の準備
 */
async function setupAuthentication(config: any) {
  console.log('🔐 Setting up Authentication...');
  
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // 管理者アカウントでログイン
    console.log('👤 Logging in as admin user...');
    await page.goto(`${config.baseURL}/login`);
    
    // ログインフォームの確認
    await page.waitForSelector('[data-testid="username"]', { timeout: 10000 });
    await page.waitForSelector('[data-testid="password"]', { timeout: 10000 });
    
    // 認証情報の入力
    await page.fill('[data-testid="username"]', config.auth.username);
    await page.fill('[data-testid="password"]', config.auth.password);
    await page.click('[data-testid="login-button"]');
    
    // ログイン成功の確認
    await page.waitForURL(`${config.baseURL}/dashboard`, { timeout: 30000 });
    
    // 認証状態の保存
    const storageState = await context.storageState();
    const fs = require('fs');
    const path = require('path');
    
    const authDir = path.join(process.cwd(), 'test-results', 'auth');
    if (!fs.existsSync(authDir)) {
      fs.mkdirSync(authDir, { recursive: true });
    }
    
    fs.writeFileSync(
      path.join(authDir, 'admin-auth.json'),
      JSON.stringify(storageState, null, 2)
    );
    
    console.log('✅ Authentication Setup Completed');
  } catch (error) {
    console.error('❌ Authentication Setup Failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

/**
 * テストデータの準備
 */
async function setupTestData(config: any) {
  console.log('📊 Setting up Test Data...');
  
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
        // ローカルストレージの復元
        const localStorage = storageState.origins[0]?.localStorage || [];
        localStorage.forEach(({ name, value }: any) => {
          window.localStorage.setItem(name, value);
        });
      });
    }
    
    // テストデータの作成
    await setupTestDrones(page, config);
    await setupTestDatasets(page, config);
    await setupTestModels(page, config);
    
    console.log('✅ Test Data Setup Completed');
  } catch (error) {
    console.error('❌ Test Data Setup Failed:', error);
    // テストデータの設定に失敗してもテスト実行は継続
    console.log('⚠️  Continuing without test data setup');
  } finally {
    await browser.close();
  }
}

/**
 * テストドローンの設定
 */
async function setupTestDrones(page: any, config: any) {
  console.log('🚁 Setting up test drones...');
  
  try {
    await page.goto(`${config.baseURL}/drone-management`);
    
    // 既存のテストドローンをクリーンアップ
    const existingDrones = await page.locator('[data-testid="drone-card"]').filter({ 
      hasText: 'Test Drone' 
    });
    
    const count = await existingDrones.count();
    for (let i = 0; i < count; i++) {
      try {
        await existingDrones.nth(0).locator('[data-testid="delete-drone"]').click();
        await page.click('[data-testid="confirm-delete"]');
        await page.waitForTimeout(1000);
      } catch (error) {
        console.log('⚠️  Could not delete existing test drone');
      }
    }
    
    // 新しいテストドローンの作成
    await page.click('[data-testid="add-drone-button"]');
    await page.fill('[data-testid="drone-name"]', 'Test Drone Global');
    await page.fill('[data-testid="drone-model"]', 'DJI Mini 3');
    await page.fill('[data-testid="drone-serialNumber"]', 'GLOBAL-001');
    await page.fill('[data-testid="drone-batteryLevel"]', '85');
    await page.click('[data-testid="save-drone-button"]');
    
    await page.waitForResponse(response => 
      response.url().includes('/api/drones') && 
      (response.status() === 200 || response.status() === 201)
    );
    
    console.log('✅ Test drones setup completed');
  } catch (error) {
    console.log('⚠️  Test drones setup failed:', error);
  }
}

/**
 * テストデータセットの設定
 */
async function setupTestDatasets(page: any, config: any) {
  console.log('📂 Setting up test datasets...');
  
  try {
    await page.goto(`${config.baseURL}/dataset-management`);
    
    // 既存のテストデータセットをクリーンアップ
    const existingDatasets = await page.locator('[data-testid="dataset-card"]').filter({ 
      hasText: 'Test Dataset' 
    });
    
    const count = await existingDatasets.count();
    for (let i = 0; i < count; i++) {
      try {
        await existingDatasets.nth(0).locator('[data-testid="delete-dataset"]').click();
        await page.click('[data-testid="confirm-delete"]');
        await page.waitForTimeout(1000);
      } catch (error) {
        console.log('⚠️  Could not delete existing test dataset');
      }
    }
    
    // 新しいテストデータセットの作成
    await page.click('[data-testid="create-dataset-button"]');
    await page.fill('[data-testid="dataset-name"]', 'Test Dataset Global');
    await page.fill('[data-testid="dataset-description"]', 'Global test dataset');
    await page.selectOption('[data-testid="dataset-type"]', 'object_detection');
    await page.fill('[data-testid="dataset-tags"]', 'test, global');
    await page.click('[data-testid="save-dataset-button"]');
    
    await page.waitForResponse(response => 
      response.url().includes('/api/datasets') && 
      (response.status() === 200 || response.status() === 201)
    );
    
    console.log('✅ Test datasets setup completed');
  } catch (error) {
    console.log('⚠️  Test datasets setup failed:', error);
  }
}

/**
 * テストモデルの設定
 */
async function setupTestModels(page: any, config: any) {
  console.log('🤖 Setting up test models...');
  
  try {
    await page.goto(`${config.baseURL}/model-management`);
    
    // 既存のテストモデルをクリーンアップ
    const existingModels = await page.locator('[data-testid="model-card"]').filter({ 
      hasText: 'Test Model' 
    });
    
    const count = await existingModels.count();
    for (let i = 0; i < count; i++) {
      try {
        await existingModels.nth(0).locator('[data-testid="delete-model"]').click();
        await page.click('[data-testid="confirm-delete"]');
        await page.waitForTimeout(1000);
      } catch (error) {
        console.log('⚠️  Could not delete existing test model');
      }
    }
    
    // 新しいテストモデルの作成
    await page.click('[data-testid="create-model-button"]');
    await page.fill('[data-testid="model-name"]', 'Test Model Global');
    await page.fill('[data-testid="model-description"]', 'Global test model');
    await page.selectOption('[data-testid="model-algorithm"]', 'yolov8');
    await page.selectOption('[data-testid="model-framework"]', 'pytorch');
    await page.click('[data-testid="save-model-button"]');
    
    await page.waitForResponse(response => 
      response.url().includes('/api/models') && 
      (response.status() === 200 || response.status() === 201)
    );
    
    console.log('✅ Test models setup completed');
  } catch (error) {
    console.log('⚠️  Test models setup failed:', error);
  }
}

/**
 * パフォーマンス監視の初期化
 */
async function initializePerformanceMonitoring(config: any) {
  console.log('📈 Initializing Performance Monitoring...');
  
  try {
    // パフォーマンスログディレクトリの作成
    const fs = require('fs');
    const path = require('path');
    
    const perfDir = path.join(process.cwd(), 'test-results', 'performance');
    if (!fs.existsSync(perfDir)) {
      fs.mkdirSync(perfDir, { recursive: true });
    }
    
    // パフォーマンスログファイルの初期化
    const perfLogPath = path.join(perfDir, 'performance.log');
    fs.writeFileSync(perfLogPath, `Performance Test Started: ${new Date().toISOString()}\n`);
    
    console.log('✅ Performance Monitoring Initialized');
  } catch (error) {
    console.error('❌ Performance Monitoring Initialization Failed:', error);
    // パフォーマンス監視の初期化失敗してもテスト実行は継続
  }
}

/**
 * レポートディレクトリの準備
 */
async function setupReportingDirectories() {
  console.log('📁 Setting up Reporting Directories...');
  
  try {
    const fs = require('fs');
    const path = require('path');
    
    const directories = [
      'test-results/html-report',
      'test-results/json-report',
      'test-results/junit-report',
      'test-results/allure-results',
      'test-results/screenshots',
      'test-results/videos',
      'test-results/traces',
      'test-results/performance',
      'test-results/accessibility',
      'test-results/security',
      'test-results/auth'
    ];
    
    directories.forEach(dir => {
      const fullPath = path.join(process.cwd(), dir);
      if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
      }
    });
    
    console.log('✅ Reporting Directories Setup Completed');
  } catch (error) {
    console.error('❌ Reporting Directories Setup Failed:', error);
  }
}

export default globalSetup;