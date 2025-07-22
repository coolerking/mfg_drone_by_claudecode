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
      if (!isConnected) {\n        throw new Error('Backend connection failed');\n      }\n    });\n  }\n\n  /**\n   * ヘルスチェックテスト\n   */\n  async testHealthCheck(): Promise<void> {\n    await this.runTest('Health Check Test', async () => {\n      const health = await this.client.healthCheck();\n      if (!health.status) {\n        throw new Error('Health check returned no status');\n      }\n      if (!health.timestamp) {\n        throw new Error('Health check returned no timestamp');\n      }\n    });\n  }\n\n  /**\n   * システム状態テスト\n   */\n  async testSystemStatus(): Promise<void> {\n    await this.runTest('System Status Test', async () => {\n      const status = await this.client.getSystemStatus();\n      if (typeof status.cpu_usage !== 'number') {\n        throw new Error('Invalid system status format');\n      }\n    });\n  }\n\n  /**\n   * ドローン一覧取得テスト\n   */\n  async testGetDrones(): Promise<void> {\n    await this.runTest('Get Drones Test', async () => {\n      const drones = await this.client.getDrones();\n      if (!Array.isArray(drones)) {\n        throw new Error('Drones response is not an array');\n      }\n      logger.info(`Found ${drones.length} drone(s)`);\n    });\n  }\n\n  /**\n   * ドローンスキャンテスト\n   */\n  async testScanDrones(): Promise<void> {\n    await this.runTest('Scan Drones Test', async () => {\n      const result = await this.client.scanDrones();\n      if (typeof result.found !== 'number') {\n        throw new Error('Invalid scan result format');\n      }\n      logger.info(`Scan found ${result.found} drone(s): ${result.message}`);\n    });\n  }\n\n  /**\n   * データセット一覧取得テスト\n   */\n  async testGetDatasets(): Promise<void> {\n    await this.runTest('Get Datasets Test', async () => {\n      const datasets = await this.client.getDatasets();\n      if (!Array.isArray(datasets)) {\n        throw new Error('Datasets response is not an array');\n      }\n      logger.info(`Found ${datasets.length} dataset(s)`);\n    });\n  }\n\n  /**\n   * モデル一覧取得テスト\n   */\n  async testGetModels(): Promise<void> {\n    await this.runTest('Get Models Test', async () => {\n      const models = await this.client.getModels();\n      if (!Array.isArray(models)) {\n        throw new Error('Models response is not an array');\n      }\n      logger.info(`Found ${models.length} model(s)`);\n    });\n  }\n\n  /**\n   * 物体追跡状態取得テスト\n   */\n  async testGetTrackingStatus(): Promise<void> {\n    await this.runTest('Get Tracking Status Test', async () => {\n      const status = await this.client.getTrackingStatus();\n      if (typeof status.is_active !== 'boolean') {\n        throw new Error('Invalid tracking status format');\n      }\n      logger.info(`Tracking active: ${status.is_active}`);\n    });\n  }\n\n  /**\n   * ダッシュボード機能テスト\n   */\n  async testDashboardAPIs(): Promise<void> {\n    await this.runTest('Dashboard System Status Test', async () => {\n      const systemStatus = await this.client.getDashboardSystemStatus();\n      if (typeof systemStatus.cpu_usage !== 'number') {\n        throw new Error('Invalid dashboard system status format');\n      }\n    });\n\n    await this.runTest('Dashboard Drones Test', async () => {\n      const drones = await this.client.getDashboardDrones();\n      if (!Array.isArray(drones)) {\n        throw new Error('Dashboard drones response is not an array');\n      }\n      logger.info(`Dashboard shows ${drones.length} drone(s)`);\n    });\n  }\n\n  /**\n   * レスポンスタイム計測テスト\n   */\n  async testResponseTimes(): Promise<void> {\n    await this.runTest('Response Time Test', async () => {\n      const iterations = 5;\n      const times: number[] = [];\n\n      for (let i = 0; i < iterations; i++) {\n        const start = Date.now();\n        await this.client.healthCheck();\n        times.push(Date.now() - start);\n      }\n\n      const average = times.reduce((a, b) => a + b, 0) / times.length;\n      const max = Math.max(...times);\n      const min = Math.min(...times);\n\n      logger.info(`Response times - Avg: ${average.toFixed(1)}ms, Min: ${min}ms, Max: ${max}ms`);\n\n      if (average > 5000) {\n        throw new Error(`Average response time too slow: ${average.toFixed(1)}ms`);\n      }\n    });\n  }\n\n  /**\n   * エラーハンドリングテスト\n   */\n  async testErrorHandling(): Promise<void> {\n    await this.runTest('Error Handling Test', async () => {\n      try {\n        // 存在しないドローンIDでテスト\n        await this.client.getDroneStatus('non-existent-drone-id');\n        throw new Error('Expected error was not thrown');\n      } catch (error) {\n        if (error instanceof Error && error.message === 'Expected error was not thrown') {\n          throw error;\n        }\n        // エラーが正しく処理されることを確認\n        logger.info('Error handling working correctly');\n      }\n    });\n  }\n\n  /**\n   * 全テストを実行\n   */\n  async runAllTests(): Promise<void> {\n    logger.info(`🚀 Starting connection tests for backend: ${testConfig.backendUrl}`);\n    logger.info('='repeat(50));\n\n    // 基本接続テスト\n    await this.testBasicConnection();\n    await this.testHealthCheck();\n    await this.testSystemStatus();\n\n    // ドローン関連テスト\n    await this.testGetDrones();\n    await this.testScanDrones();\n\n    // ビジョン関連テスト\n    await this.testGetDatasets();\n    await this.testGetModels();\n    await this.testGetTrackingStatus();\n\n    // ダッシュボードテスト\n    await this.testDashboardAPIs();\n\n    // パフォーマンステスト\n    await this.testResponseTimes();\n\n    // エラーハンドリングテスト\n    await this.testErrorHandling();\n\n    // 結果表示\n    this.displayResults();\n  }\n\n  /**\n   * テスト結果を表示\n   */\n  private displayResults(): void {\n    logger.info('='repeat(50));\n    logger.info('📊 Test Results Summary');\n    logger.info('='repeat(50));\n\n    const passed = this.results.filter(r => r.passed).length;\n    const total = this.results.length;\n    const successRate = ((passed / total) * 100).toFixed(1);\n\n    logger.info(`✅ Passed: ${passed}/${total} (${successRate}%)`);\n    logger.info(`❌ Failed: ${total - passed}/${total}`);\n\n    if (passed < total) {\n      logger.info('\\n🔍 Failed Tests:');\n      this.results\n        .filter(r => !r.passed)\n        .forEach(r => {\n          logger.error(`  - ${r.name}: ${r.error}`);\n        });\n    }\n\n    const avgDuration = this.results.reduce((sum, r) => sum + r.duration, 0) / this.results.length;\n    logger.info(`\\n⏱️  Average test duration: ${avgDuration.toFixed(1)}ms`);\n\n    if (passed === total) {\n      logger.info('\\n🎉 All tests passed! Backend connection is healthy.');\n    } else {\n      logger.error('\\n⚠️  Some tests failed. Please check the backend configuration.');\n      process.exit(1);\n    }\n  }\n}\n\n// メイン実行関数\nasync function main(): Promise<void> {\n  const tester = new ConnectionTester();\n  \n  try {\n    await tester.runAllTests();\n  } catch (error) {\n    logger.error('Test execution failed:', error);\n    process.exit(1);\n  }\n}\n\n// コマンドライン実行時\nif (import.meta.url === `file://${process.argv[1]}`) {\n  main().catch(error => {\n    logger.error('Unhandled error:', error);\n    process.exit(1);\n  });\n}\n\nexport { ConnectionTester };