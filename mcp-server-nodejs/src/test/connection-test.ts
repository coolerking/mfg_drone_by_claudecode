#!/usr/bin/env tsx

/**
 * バックエンドAPI接続テストスクリプト
 * 
 * このスクリプトは、MCPサーバーのBackendClientが
 * Pythonバックエンドと正しく連携できるかをテストします。
 */

import { BackendClient } from '@/clients/BackendClient.js';
import { logger } from '@/utils/logger.js';
import { Config } from '@/types/index.js';

// テスト設定
const testConfig: Config = {
  port: 3001,
  backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
  logLevel: process.env.LOG_LEVEL as any || 'info',
  timeout: parseInt(process.env.TIMEOUT || '10000', 10),
};

// テスト結果集計
interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
  duration: number;
}

class ConnectionTester {
  private client: BackendClient;
  private results: TestResult[] = [];

  constructor() {
    this.client = new BackendClient(testConfig);
  }

  /**
   * 個別テストを実行
   */
  private async runTest(name: string, testFn: () => Promise<void>): Promise<void> {
    const startTime = Date.now();
    try {
      await testFn();
      const duration = Date.now() - startTime;
      this.results.push({ name, passed: true, duration });
      logger.info(`✅ ${name} - ${duration}ms`);
    } catch (error) {
      const duration = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : String(error);
      this.results.push({ name, passed: false, error: errorMessage, duration });
      logger.error(`❌ ${name} - ${duration}ms: ${errorMessage}`);
    }
  }

  /**
   * 基本接続テスト
   */
  async testBasicConnection(): Promise<void> {
    await this.runTest('Basic Connection Test', async () => {
      const isConnected = await this.client.testConnection();
      if (!isConnected) {
        throw new Error('Backend connection failed');
      }
    });
  }

  /**
   * ヘルスチェックテスト
   */
  async testHealthCheck(): Promise<void> {
    await this.runTest('Health Check Test', async () => {
      const health = await this.client.healthCheck();
      if (!health.status) {
        throw new Error('Health check returned no status');
      }
      if (!health.timestamp) {
        throw new Error('Health check returned no timestamp');
      }
    });
  }

  /**
   * システム状態テスト
   */
  async testSystemStatus(): Promise<void> {
    await this.runTest('System Status Test', async () => {
      const status = await this.client.getSystemStatus();
      if (!status.status || !status.timestamp) {
        throw new Error('Invalid system status format');
      }
    });
  }

  /**
   * ドローン一覧取得テスト
   */
  async testGetDrones(): Promise<void> {
    await this.runTest('Get Drones Test', async () => {
      const drones = await this.client.getDrones();
      if (!Array.isArray(drones)) {
        throw new Error('Drones response is not an array');
      }
      logger.info(`Found ${drones.length} drone(s)`);
    });
  }

  /**
   * ドローンスキャンテスト
   */
  async testScanDrones(): Promise<void> {
    await this.runTest('Scan Drones Test', async () => {
      const result = await this.client.scanDrones();
      if (typeof result.found !== 'number') {
        throw new Error('Invalid scan result format');
      }
      logger.info(`Scan found ${result.found} drone(s): ${result.message}`);
    });
  }

  /**
   * データセット一覧取得テスト
   */
  async testGetDatasets(): Promise<void> {
    await this.runTest('Get Datasets Test', async () => {
      const datasets = await this.client.getDatasets();
      if (!Array.isArray(datasets)) {
        throw new Error('Datasets response is not an array');
      }
      logger.info(`Found ${datasets.length} dataset(s)`);
    });
  }

  /**
   * モデル一覧取得テスト
   */
  async testGetModels(): Promise<void> {
    await this.runTest('Get Models Test', async () => {
      const models = await this.client.getModels();
      if (!Array.isArray(models)) {
        throw new Error('Models response is not an array');
      }
      logger.info(`Found ${models.length} model(s)`);
    });
  }

  /**
   * 物体追跡状態取得テスト
   */
  async testGetTrackingStatus(): Promise<void> {
    await this.runTest('Get Tracking Status Test', async () => {
      const status = await this.client.getTrackingStatus();
      if (typeof status.is_active !== 'boolean') {
        throw new Error('Invalid tracking status format');
      }
      logger.info(`Tracking active: ${status.is_active}`);
    });
  }

  /**
   * ダッシュボード機能テスト
   */
  async testDashboardAPIs(): Promise<void> {
    await this.runTest('Dashboard System Status Test', async () => {
      const systemStatus = await this.client.getDashboardSystemStatus();
      if (!systemStatus.status || !systemStatus.timestamp) {
        throw new Error('Invalid dashboard system status format');
      }
    });

    await this.runTest('Dashboard Drones Test', async () => {
      const drones = await this.client.getDashboardDrones();
      if (!Array.isArray(drones)) {
        throw new Error('Dashboard drones response is not an array');
      }
      logger.info(`Dashboard shows ${drones.length} drone(s)`);
    });
  }

  /**
   * レスポンスタイム計測テスト
   */
  async testResponseTimes(): Promise<void> {
    await this.runTest('Response Time Test', async () => {
      const iterations = 5;
      const times: number[] = [];

      for (let i = 0; i < iterations; i++) {
        const start = Date.now();
        await this.client.healthCheck();
        times.push(Date.now() - start);
      }

      const average = times.reduce((a, b) => a + b, 0) / times.length;
      const max = Math.max(...times);
      const min = Math.min(...times);

      logger.info(`Response times - Avg: ${average.toFixed(1)}ms, Min: ${min}ms, Max: ${max}ms`);

      if (average > 5000) {
        throw new Error(`Average response time too slow: ${average.toFixed(1)}ms`);
      }
    });
  }

  /**
   * エラーハンドリングテスト
   */
  async testErrorHandling(): Promise<void> {
    await this.runTest('Error Handling Test', async () => {
      try {
        // 存在しないドローンIDでテスト
        await this.client.getDroneStatus('non-existent-drone-id');
        throw new Error('Expected error was not thrown');
      } catch (error) {
        if (error instanceof Error && error.message === 'Expected error was not thrown') {
          throw error;
        }
        // エラーが正しく処理されることを確認
        logger.info('Error handling working correctly');
      }
    });
  }

  /**
   * 全テストを実行
   */
  async runAllTests(): Promise<void> {
    logger.info(`🚀 Starting connection tests for backend: ${testConfig.backendUrl}`);
    logger.info('='.repeat(50));

    // 基本接続テスト
    await this.testBasicConnection();
    await this.testHealthCheck();
    await this.testSystemStatus();

    // ドローン関連テスト
    await this.testGetDrones();
    await this.testScanDrones();

    // ビジョン関連テスト
    await this.testGetDatasets();
    await this.testGetModels();
    await this.testGetTrackingStatus();

    // ダッシュボードテスト
    await this.testDashboardAPIs();

    // パフォーマンステスト
    await this.testResponseTimes();

    // エラーハンドリングテスト
    await this.testErrorHandling();

    // 結果表示
    this.displayResults();
  }

  /**
   * テスト結果を表示
   */
  private displayResults(): void {
    logger.info('='.repeat(50));
    logger.info('📊 Test Results Summary');
    logger.info('='.repeat(50));

    const passed = this.results.filter(r => r.passed).length;
    const total = this.results.length;
    const successRate = ((passed / total) * 100).toFixed(1);

    logger.info(`✅ Passed: ${passed}/${total} (${successRate}%)`);
    logger.info(`❌ Failed: ${total - passed}/${total}`);

    if (passed < total) {
      logger.info('\n🔍 Failed Tests:');
      this.results
        .filter(r => !r.passed)
        .forEach(r => {
          logger.error(`  - ${r.name}: ${r.error}`);
        });
    }

    const avgDuration = this.results.reduce((sum, r) => sum + r.duration, 0) / this.results.length;
    logger.info(`\n⏱️  Average test duration: ${avgDuration.toFixed(1)}ms`);

    if (passed === total) {
      logger.info('\n🎉 All tests passed! Backend connection is healthy.');
    } else {
      logger.error('\n⚠️  Some tests failed. Please check the backend configuration.');
      process.exit(1);
    }
  }
}

// メイン実行関数
async function main(): Promise<void> {
  const tester = new ConnectionTester();
  
  try {
    await tester.runAllTests();
  } catch (error) {
    logger.error('Test execution failed:', error);
    process.exit(1);
  }
}

// コマンドライン実行時
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    logger.error('Unhandled error:', error);
    process.exit(1);
  });
}

export { ConnectionTester };