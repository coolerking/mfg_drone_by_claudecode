/**
 * CI/CD品質チェック自動化システム
 * パイプライン統合・自動品質ゲート・レポート生成
 */

import { qualityReportGenerator, DetailedQualityReport } from './qualityReportGenerator'
import { 
  QualityConfig, 
  PIPELINE_CONFIG, 
  QualityGateValidator,
  QualityReport
} from '../test/config/quality-gates'

// =============================================================================
// 型定義
// =============================================================================

export interface CICDQualityResult {
  pipelineId: string
  stage: string
  status: 'success' | 'failure' | 'warning' | 'skipped'
  startTime: string
  endTime: string
  duration: number
  exitCode: number
  logs: string[]
  metrics: QualityMetrics
  artifacts: ArtifactInfo[]
  notifications: NotificationInfo[]
}

export interface QualityMetrics {
  coverage: CoverageMetrics
  performance: PerformanceMetrics
  accessibility: AccessibilityMetrics
  security: SecurityMetrics
  codeQuality: CodeQualityMetrics
  overall: OverallMetrics
}

export interface CoverageMetrics {
  lines: number
  functions: number
  branches: number
  statements: number
  threshold: number
  passed: boolean
  delta: number // 前回との差分
}

export interface PerformanceMetrics {
  bundleSize: number
  bundleThreshold: number
  webVitals: {
    FCP: number
    LCP: number
    FID: number
    CLS: number
  }
  thresholds: {
    FCP: number
    LCP: number
    FID: number
    CLS: number
  }
  passed: boolean
}

export interface AccessibilityMetrics {
  violations: number
  criticalViolations: number
  seriousViolations: number
  wcagLevel: string
  passed: boolean
}

export interface SecurityMetrics {
  vulnerabilities: number
  criticalVulnerabilities: number
  highVulnerabilities: number
  outdatedDependencies: number
  passed: boolean
}

export interface CodeQualityMetrics {
  eslintErrors: number
  eslintWarnings: number
  tsErrors: number
  complexity: number
  duplication: number
  passed: boolean
}

export interface OverallMetrics {
  score: number
  grade: string
  passed: boolean
  blockers: string[]
}

export interface ArtifactInfo {
  name: string
  path: string
  size: number
  type: 'coverage' | 'test-results' | 'performance' | 'accessibility' | 'security' | 'report'
  url?: string
  retention: number // days
}

export interface NotificationInfo {
  type: 'slack' | 'email' | 'github' | 'webhook'
  recipient: string
  subject: string
  message: string
  sent: boolean
  error?: string
}

export interface PipelineContext {
  pipelineId: string
  jobId: string
  stageName: string
  branch: string
  commit: string
  pullRequest?: string
  author: string
  triggeredBy: 'push' | 'pr' | 'schedule' | 'manual'
  environment: 'development' | 'staging' | 'production'
  isMain: boolean
  isPullRequest: boolean
}

// =============================================================================
// CI/CD品質チェッククラス
// =============================================================================

export class CICDQualityChecker {
  private static instance: CICDQualityChecker
  private context: PipelineContext | null = null
  private results: Map<string, CICDQualityResult> = new Map()

  public static getInstance(): CICDQualityChecker {
    if (!CICDQualityChecker.instance) {
      CICDQualityChecker.instance = new CICDQualityChecker()
    }
    return CICDQualityChecker.instance
  }

  // パイプライン初期化
  initializePipeline(context: PipelineContext): void {
    this.context = context
    this.results.clear()
    
    console.log(`🚀 CI/CD品質チェック開始`)
    console.log(`📋 Pipeline ID: ${context.pipelineId}`)
    console.log(`🌿 Branch: ${context.branch}`)
    console.log(`📝 Commit: ${context.commit}`)
    console.log(`🎯 Environment: ${context.environment}`)
  }

  // 全ステージ実行
  async runAllStages(): Promise<CICDQualityResult[]> {
    if (!this.context) {
      throw new Error('Pipeline context not initialized')
    }

    const stages = PIPELINE_CONFIG.stages
    const results: CICDQualityResult[] = []

    console.log(`📊 実行予定ステージ: ${stages.join(', ')}`)

    for (const stage of stages) {
      try {
        const result = await this.runStage(stage)
        results.push(result)
        
        // ステージが失敗した場合の処理
        if (result.status === 'failure') {
          console.error(`❌ ステージ ${stage} が失敗しました`)
          
          // 重要なステージの場合はパイプラインを停止
          if (this.isCriticalStage(stage)) {
            console.error(`🛑 重要ステージの失敗により、パイプラインを停止します`)
            break
          }
        }
        
        // 警告の場合は続行
        if (result.status === 'warning') {
          console.warn(`⚠️ ステージ ${stage} で警告が発生しました`)
        }

      } catch (error) {
        console.error(`💥 ステージ ${stage} で例外が発生しました:`, error)
        
        results.push({
          pipelineId: this.context.pipelineId,
          stage,
          status: 'failure',
          startTime: new Date().toISOString(),
          endTime: new Date().toISOString(),
          duration: 0,
          exitCode: 1,
          logs: [`Error: ${error}`],
          metrics: this.getEmptyMetrics(),
          artifacts: [],
          notifications: []
        })
        
        if (this.isCriticalStage(stage)) {
          break
        }
      }
    }

    // 最終レポート生成
    await this.generateFinalReport(results)

    return results
  }

  // 個別ステージ実行
  async runStage(stageName: string): Promise<CICDQualityResult> {
    const startTime = new Date()
    const logs: string[] = []
    let status: 'success' | 'failure' | 'warning' | 'skipped' = 'success'
    let exitCode = 0
    let metrics = this.getEmptyMetrics()
    let artifacts: ArtifactInfo[] = []

    logs.push(`🔄 ステージ ${stageName} 開始: ${startTime.toISOString()}`)

    try {
      switch (stageName) {
        case 'install':
          ({ status, exitCode, artifacts } = await this.runInstallStage(logs))
          break
        case 'lint':
          ({ status, exitCode, metrics, artifacts } = await this.runLintStage(logs))
          break
        case 'type-check':
          ({ status, exitCode, metrics, artifacts } = await this.runTypeCheckStage(logs))
          break
        case 'unit-test':
          ({ status, exitCode, metrics, artifacts } = await this.runUnitTestStage(logs))
          break
        case 'integration-test':
          ({ status, exitCode, metrics, artifacts } = await this.runIntegrationTestStage(logs))
          break
        case 'accessibility-test':
          ({ status, exitCode, metrics, artifacts } = await this.runAccessibilityTestStage(logs))
          break
        case 'e2e-test':
          ({ status, exitCode, metrics, artifacts } = await this.runE2ETestStage(logs))
          break
        case 'security-scan':
          ({ status, exitCode, metrics, artifacts } = await this.runSecurityScanStage(logs))
          break
        case 'performance-test':
          ({ status, exitCode, metrics, artifacts } = await this.runPerformanceTestStage(logs))
          break
        case 'build':
          ({ status, exitCode, artifacts } = await this.runBuildStage(logs))
          break
        default:
          logs.push(`⚠️ 未知のステージ: ${stageName}`)
          status = 'skipped'
      }
    } catch (error) {
      logs.push(`💥 ステージ実行中にエラーが発生: ${error}`)
      status = 'failure'
      exitCode = 1
    }

    const endTime = new Date()
    const duration = endTime.getTime() - startTime.getTime()

    logs.push(`${status === 'success' ? '✅' : status === 'failure' ? '❌' : '⚠️'} ステージ ${stageName} 完了: ${endTime.toISOString()} (${duration}ms)`)

    const result: CICDQualityResult = {
      pipelineId: this.context!.pipelineId,
      stage: stageName,
      status,
      startTime: startTime.toISOString(),
      endTime: endTime.toISOString(),
      duration,
      exitCode,
      logs,
      metrics,
      artifacts,
      notifications: []
    }

    this.results.set(stageName, result)

    // 通知送信
    if (status === 'failure' || (status === 'warning' && this.isCriticalStage(stageName))) {
      result.notifications = await this.sendNotifications(result)
    }

    return result
  }

  // =============================================================================
  // 個別ステージ実装
  // =============================================================================

  private async runInstallStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    artifacts: ArtifactInfo[]
  }> {
    logs.push('📦 依存関係のインストール開始')
    
    // シミュレート: npm install
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    logs.push('✅ 依存関係のインストール完了')
    
    return {
      status: 'success',
      exitCode: 0,
      artifacts: [
        {
          name: 'node_modules',
          path: './node_modules',
          size: 150000000, // 150MB
          type: 'report',
          retention: 1
        }
      ]
    }
  }

  private async runLintStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    metrics: QualityMetrics
    artifacts: ArtifactInfo[]
  }> {
    logs.push('🔍 ESLint実行開始')
    
    // シミュレート: ESLint実行
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    const eslintErrors = Math.floor(Math.random() * 3)
    const eslintWarnings = Math.floor(Math.random() * 10)
    
    logs.push(`📊 ESLint結果: エラー ${eslintErrors}件, 警告 ${eslintWarnings}件`)
    
    const passed = eslintErrors === 0 && eslintWarnings <= QualityConfig.CODE_QUALITY_METRICS.eslint.maxWarnings
    const status = eslintErrors > 0 ? 'failure' : eslintWarnings > 5 ? 'warning' : 'success'
    
    const metrics = this.getEmptyMetrics()
    metrics.codeQuality = {
      eslintErrors,
      eslintWarnings,
      tsErrors: 0,
      complexity: 6.5,
      duplication: 2.1,
      passed
    }
    
    return {
      status,
      exitCode: eslintErrors > 0 ? 1 : 0,
      metrics,
      artifacts: [
        {
          name: 'eslint-report.json',
          path: './reports/eslint-report.json',
          size: 25000,
          type: 'report',
          retention: 30
        }
      ]
    }
  }

  private async runTypeCheckStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    metrics: QualityMetrics
    artifacts: ArtifactInfo[]
  }> {
    logs.push('🔧 TypeScript型チェック開始')
    
    // シミュレート: TypeScript型チェック
    await new Promise(resolve => setTimeout(resolve, 4000))
    
    const tsErrors = Math.floor(Math.random() * 2)
    
    logs.push(`📊 TypeScript結果: エラー ${tsErrors}件`)
    
    const passed = tsErrors === 0
    const status = tsErrors > 0 ? 'failure' : 'success'
    
    const metrics = this.getEmptyMetrics()
    metrics.codeQuality.tsErrors = tsErrors
    metrics.codeQuality.passed = passed
    
    return {
      status,
      exitCode: tsErrors > 0 ? 1 : 0,
      metrics,
      artifacts: [
        {
          name: 'typescript-report.json',
          path: './reports/typescript-report.json',
          size: 15000,
          type: 'report',
          retention: 30
        }
      ]
    }
  }

  private async runUnitTestStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    metrics: QualityMetrics
    artifacts: ArtifactInfo[]
  }> {
    logs.push('🧪 ユニットテスト実行開始')
    
    // シミュレート: ユニットテスト実行
    await new Promise(resolve => setTimeout(resolve, 8000))
    
    const coverage = {
      lines: 85.7 + (Math.random() - 0.5) * 10,
      functions: 89.2 + (Math.random() - 0.5) * 8,
      branches: 78.5 + (Math.random() - 0.5) * 12,
      statements: 86.1 + (Math.random() - 0.5) * 9
    }
    
    const thresholds = QualityConfig.COVERAGE_THRESHOLDS.global
    const passed = coverage.lines >= thresholds.lines &&
                   coverage.functions >= thresholds.functions &&
                   coverage.branches >= thresholds.branches &&
                   coverage.statements >= thresholds.statements
    
    logs.push(`📊 カバレッジ: Lines ${coverage.lines.toFixed(1)}%, Functions ${coverage.functions.toFixed(1)}%, Branches ${coverage.branches.toFixed(1)}%, Statements ${coverage.statements.toFixed(1)}%`)
    logs.push(`🎯 カバレッジ目標: ${passed ? '達成' : '未達成'}`)
    
    const metrics = this.getEmptyMetrics()
    metrics.coverage = {
      lines: coverage.lines,
      functions: coverage.functions,
      branches: coverage.branches,
      statements: coverage.statements,
      threshold: thresholds.lines,
      passed,
      delta: Math.random() * 2 - 1 // -1 to +1
    }
    
    return {
      status: passed ? 'success' : 'failure',
      exitCode: passed ? 0 : 1,
      metrics,
      artifacts: [
        {
          name: 'coverage-report',
          path: './coverage',
          size: 1200000,
          type: 'coverage',
          retention: 30
        },
        {
          name: 'test-results.xml',
          path: './reports/test-results.xml',
          size: 45000,
          type: 'test-results',
          retention: 30
        }
      ]
    }
  }

  private async runIntegrationTestStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    metrics: QualityMetrics
    artifacts: ArtifactInfo[]
  }> {
    logs.push('🔗 統合テスト実行開始')
    
    // シミュレート: 統合テスト実行
    await new Promise(resolve => setTimeout(resolve, 12000))
    
    const passed = Math.random() > 0.1 // 90%の確率で成功
    
    logs.push(`📊 統合テスト結果: ${passed ? '成功' : '失敗'}`)
    
    return {
      status: passed ? 'success' : 'failure',
      exitCode: passed ? 0 : 1,
      metrics: this.getEmptyMetrics(),
      artifacts: [
        {
          name: 'integration-test-results.json',
          path: './reports/integration-test-results.json',
          size: 85000,
          type: 'test-results',
          retention: 30
        }
      ]
    }
  }

  private async runAccessibilityTestStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    metrics: QualityMetrics
    artifacts: ArtifactInfo[]
  }> {
    logs.push('♿ アクセシビリティテスト実行開始')
    
    // シミュレート: アクセシビリティテスト実行
    await new Promise(resolve => setTimeout(resolve, 6000))
    
    const violations = Math.floor(Math.random() * 8)
    const criticalViolations = Math.floor(violations * 0.2)
    const seriousViolations = Math.floor(violations * 0.4)
    
    const passed = criticalViolations === 0
    
    logs.push(`📊 アクセシビリティ結果: 違反 ${violations}件 (重大 ${criticalViolations}件, 深刻 ${seriousViolations}件)`)
    
    const metrics = this.getEmptyMetrics()
    metrics.accessibility = {
      violations,
      criticalViolations,
      seriousViolations,
      wcagLevel: 'AA',
      passed
    }
    
    return {
      status: passed ? 'success' : 'failure',
      exitCode: passed ? 0 : 1,
      metrics,
      artifacts: [
        {
          name: 'accessibility-report.json',
          path: './reports/accessibility-report.json',
          size: 35000,
          type: 'accessibility',
          retention: 30
        }
      ]
    }
  }

  private async runE2ETestStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    metrics: QualityMetrics
    artifacts: ArtifactInfo[]
  }> {
    logs.push('🎭 E2Eテスト実行開始')
    
    // シミュレート: E2Eテスト実行
    await new Promise(resolve => setTimeout(resolve, 25000))
    
    const passed = Math.random() > 0.15 // 85%の確率で成功
    
    logs.push(`📊 E2Eテスト結果: ${passed ? '成功' : '失敗'}`)
    
    return {
      status: passed ? 'success' : 'failure',
      exitCode: passed ? 0 : 1,
      metrics: this.getEmptyMetrics(),
      artifacts: [
        {
          name: 'playwright-report',
          path: './playwright-report',
          size: 2500000,
          type: 'test-results',
          retention: 14
        },
        {
          name: 'e2e-videos',
          path: './test-results',
          size: 15000000,
          type: 'test-results',
          retention: 7
        }
      ]
    }
  }

  private async runSecurityScanStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    metrics: QualityMetrics
    artifacts: ArtifactInfo[]
  }> {
    logs.push('🔒 セキュリティスキャン開始')
    
    // シミュレート: セキュリティスキャン実行
    await new Promise(resolve => setTimeout(resolve, 8000))
    
    const vulnerabilities = Math.floor(Math.random() * 5)
    const criticalVulns = Math.floor(vulnerabilities * 0.1)
    const highVulns = Math.floor(vulnerabilities * 0.3)
    const outdatedDeps = Math.floor(Math.random() * 15)
    
    const passed = criticalVulns === 0 && highVulns <= 2
    
    logs.push(`📊 セキュリティ結果: 脆弱性 ${vulnerabilities}件 (重大 ${criticalVulns}件, 高 ${highVulns}件), 古い依存関係 ${outdatedDeps}件`)
    
    const metrics = this.getEmptyMetrics()
    metrics.security = {
      vulnerabilities,
      criticalVulnerabilities: criticalVulns,
      highVulnerabilities: highVulns,
      outdatedDependencies: outdatedDeps,
      passed
    }
    
    return {
      status: passed ? 'success' : criticalVulns > 0 ? 'failure' : 'warning',
      exitCode: criticalVulns > 0 ? 1 : 0,
      metrics,
      artifacts: [
        {
          name: 'security-audit.json',
          path: './reports/security-audit.json',
          size: 55000,
          type: 'security',
          retention: 90
        }
      ]
    }
  }

  private async runPerformanceTestStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    metrics: QualityMetrics
    artifacts: ArtifactInfo[]
  }> {
    logs.push('⚡ パフォーマンステスト実行開始')
    
    // シミュレート: パフォーマンステスト実行
    await new Promise(resolve => setTimeout(resolve, 15000))
    
    const bundleSize = 1200000 + Math.floor(Math.random() * 300000) // 1.2-1.5MB
    const webVitals = {
      FCP: 1200 + Math.floor(Math.random() * 600),
      LCP: 2100 + Math.floor(Math.random() * 800),
      FID: 85 + Math.floor(Math.random() * 30),
      CLS: 0.08 + Math.random() * 0.04
    }
    
    const thresholds = QualityConfig.PERFORMANCE_THRESHOLDS
    const bundlePassed = bundleSize <= thresholds.bundleSize.total * 1024 // Convert KB to bytes
    const vitalsPassed = webVitals.FCP <= thresholds.webVitals.FCP &&
                        webVitals.LCP <= thresholds.webVitals.LCP &&
                        webVitals.FID <= thresholds.webVitals.FID &&
                        webVitals.CLS <= thresholds.webVitals.CLS
    
    const passed = bundlePassed && vitalsPassed
    
    logs.push(`📊 パフォーマンス結果:`)
    logs.push(`  バンドルサイズ: ${(bundleSize / 1024 / 1024).toFixed(2)}MB (${bundlePassed ? '✅' : '❌'})`)
    logs.push(`  FCP: ${webVitals.FCP}ms, LCP: ${webVitals.LCP}ms, FID: ${webVitals.FID}ms, CLS: ${webVitals.CLS.toFixed(3)} (${vitalsPassed ? '✅' : '❌'})`)
    
    const metrics = this.getEmptyMetrics()
    metrics.performance = {
      bundleSize,
      bundleThreshold: thresholds.bundleSize.total * 1024,
      webVitals,
      thresholds: thresholds.webVitals,
      passed
    }
    
    return {
      status: passed ? 'success' : 'failure',
      exitCode: passed ? 0 : 1,
      metrics,
      artifacts: [
        {
          name: 'lighthouse-report.html',
          path: './reports/lighthouse-report.html',
          size: 125000,
          type: 'performance',
          retention: 30
        },
        {
          name: 'performance-metrics.json',
          path: './reports/performance-metrics.json',
          size: 25000,
          type: 'performance',
          retention: 30
        }
      ]
    }
  }

  private async runBuildStage(logs: string[]): Promise<{
    status: 'success' | 'failure' | 'warning'
    exitCode: number
    artifacts: ArtifactInfo[]
  }> {
    logs.push('🏗️ ビルド実行開始')
    
    // シミュレート: ビルド実行
    await new Promise(resolve => setTimeout(resolve, 10000))
    
    const passed = Math.random() > 0.05 // 95%の確率で成功
    
    logs.push(`📊 ビルド結果: ${passed ? '成功' : '失敗'}`)
    
    return {
      status: passed ? 'success' : 'failure',
      exitCode: passed ? 0 : 1,
      artifacts: passed ? [
        {
          name: 'build',
          path: './dist',
          size: 2800000,
          type: 'report',
          retention: 30
        }
      ] : []
    }
  }

  // =============================================================================
  // ユーティリティメソッド
  // =============================================================================

  private isCriticalStage(stageName: string): boolean {
    const criticalStages = ['unit-test', 'security-scan', 'build']
    return criticalStages.includes(stageName)
  }

  private getEmptyMetrics(): QualityMetrics {
    return {
      coverage: {
        lines: 0,
        functions: 0,
        branches: 0,
        statements: 0,
        threshold: 0,
        passed: false,
        delta: 0
      },
      performance: {
        bundleSize: 0,
        bundleThreshold: 0,
        webVitals: { FCP: 0, LCP: 0, FID: 0, CLS: 0 },
        thresholds: { FCP: 0, LCP: 0, FID: 0, CLS: 0 },
        passed: false
      },
      accessibility: {
        violations: 0,
        criticalViolations: 0,
        seriousViolations: 0,
        wcagLevel: 'AA',
        passed: false
      },
      security: {
        vulnerabilities: 0,
        criticalVulnerabilities: 0,
        highVulnerabilities: 0,
        outdatedDependencies: 0,
        passed: false
      },
      codeQuality: {
        eslintErrors: 0,
        eslintWarnings: 0,
        tsErrors: 0,
        complexity: 0,
        duplication: 0,
        passed: false
      },
      overall: {
        score: 0,
        grade: 'F',
        passed: false,
        blockers: []
      }
    }
  }

  // 最終レポート生成
  private async generateFinalReport(results: CICDQualityResult[]): Promise<void> {
    if (!this.context) return

    console.log('📄 最終品質レポート生成中...')

    // 詳細品質レポート生成
    const detailedReport = await qualityReportGenerator.generateComprehensiveReport(
      this.context.environment,
      false // トレンドは含めない（CI/CDでは時間がかかるため）
    )

    // パイプライン結果をマージ
    const pipelineReport = {
      ...detailedReport,
      pipeline: {
        context: this.context,
        stages: results,
        summary: this.generatePipelineSummary(results)
      }
    }

    // レポート出力
    const reportJson = JSON.stringify(pipelineReport, null, 2)
    const reportHtml = await qualityReportGenerator.exportReport(detailedReport, 'html')

    // アーティファクトとして保存
    console.log('💾 レポートをアーティファクトとして保存中...')
    
    // 実際の実装では、ファイルシステムに保存
    // fs.writeFileSync('./reports/final-quality-report.json', reportJson)
    // fs.writeFileSync('./reports/final-quality-report.html', reportHtml)

    console.log('✅ 最終品質レポート生成完了')
  }

  private generatePipelineSummary(results: CICDQualityResult[]) {
    const total = results.length
    const success = results.filter(r => r.status === 'success').length
    const failure = results.filter(r => r.status === 'failure').length
    const warning = results.filter(r => r.status === 'warning').length
    const skipped = results.filter(r => r.status === 'skipped').length

    const totalDuration = results.reduce((sum, r) => sum + r.duration, 0)
    const overallStatus = failure > 0 ? 'failure' : warning > 0 ? 'warning' : 'success'

    return {
      total,
      success,
      failure,
      warning,
      skipped,
      totalDuration,
      overallStatus,
      failedStages: results.filter(r => r.status === 'failure').map(r => r.stage)
    }
  }

  // 通知送信
  private async sendNotifications(result: CICDQualityResult): Promise<NotificationInfo[]> {
    const notifications: NotificationInfo[] = []

    if (!this.context) return notifications

    // Slack通知
    if (process.env.SLACK_WEBHOOK_URL) {
      try {
        const slackMessage = this.generateSlackMessage(result)
        
        // 実際の実装では、Slack APIを呼び出し
        // await fetch(process.env.SLACK_WEBHOOK_URL, {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(slackMessage)
        // })

        notifications.push({
          type: 'slack',
          recipient: 'development-team',
          subject: `CI/CD Alert: ${result.stage} ${result.status}`,
          message: JSON.stringify(slackMessage),
          sent: true
        })
      } catch (error) {
        notifications.push({
          type: 'slack',
          recipient: 'development-team',
          subject: `CI/CD Alert: ${result.stage} ${result.status}`,
          message: '',
          sent: false,
          error: String(error)
        })
      }
    }

    // GitHub通知（PRコメント）
    if (this.context.isPullRequest && process.env.GITHUB_TOKEN) {
      try {
        const githubComment = this.generateGitHubComment(result)
        
        // 実際の実装では、GitHub API を呼び出し
        // await octokit.rest.issues.createComment({
        //   owner: 'owner',
        //   repo: 'repo',
        //   issue_number: parseInt(this.context.pullRequest!),
        //   body: githubComment
        // })

        notifications.push({
          type: 'github',
          recipient: `PR #${this.context.pullRequest}`,
          subject: `Quality Check: ${result.stage}`,
          message: githubComment,
          sent: true
        })
      } catch (error) {
        notifications.push({
          type: 'github',
          recipient: `PR #${this.context.pullRequest}`,
          subject: `Quality Check: ${result.stage}`,
          message: '',
          sent: false,
          error: String(error)
        })
      }
    }

    return notifications
  }

  private generateSlackMessage(result: CICDQualityResult) {
    const statusEmoji = result.status === 'success' ? '✅' : result.status === 'failure' ? '❌' : '⚠️'
    
    return {
      text: `${statusEmoji} CI/CD Pipeline Alert`,
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `*Pipeline:* ${this.context!.pipelineId}\n*Stage:* ${result.stage}\n*Status:* ${result.status}\n*Branch:* ${this.context!.branch}\n*Duration:* ${result.duration}ms`
          }
        }
      ]
    }
  }

  private generateGitHubComment(result: CICDQualityResult): string {
    const statusEmoji = result.status === 'success' ? '✅' : result.status === 'failure' ? '❌' : '⚠️'
    
    return `
## ${statusEmoji} Quality Check: ${result.stage}

**Status:** ${result.status}  
**Duration:** ${result.duration}ms  
**Pipeline:** ${this.context!.pipelineId}  

### Metrics
${this.formatMetricsForGitHub(result.metrics)}

### Logs
\`\`\`
${result.logs.slice(-10).join('\n')}
\`\`\`
`
  }

  private formatMetricsForGitHub(metrics: QualityMetrics): string {
    const lines: string[] = []
    
    if (metrics.coverage.lines > 0) {
      lines.push(`**Coverage:** ${metrics.coverage.lines.toFixed(1)}% (${metrics.coverage.passed ? '✅' : '❌'})`)
    }
    
    if (metrics.performance.bundleSize > 0) {
      lines.push(`**Bundle Size:** ${(metrics.performance.bundleSize / 1024 / 1024).toFixed(2)}MB (${metrics.performance.passed ? '✅' : '❌'})`)
    }
    
    if (metrics.accessibility.violations > 0) {
      lines.push(`**Accessibility:** ${metrics.accessibility.violations} violations (${metrics.accessibility.passed ? '✅' : '❌'})`)
    }
    
    if (metrics.security.vulnerabilities > 0) {
      lines.push(`**Security:** ${metrics.security.vulnerabilities} vulnerabilities (${metrics.security.passed ? '✅' : '❌'})`)
    }
    
    return lines.join('\n') || 'No metrics available'
  }
}

// エクスポート
export const cicdQualityChecker = CICDQualityChecker.getInstance()

// ユーティリティ関数
export const runCICDPipeline = async (context: PipelineContext): Promise<CICDQualityResult[]> => {
  cicdQualityChecker.initializePipeline(context)
  return cicdQualityChecker.runAllStages()
}

export const runCICDStage = async (
  context: PipelineContext,
  stageName: string
): Promise<CICDQualityResult> => {
  cicdQualityChecker.initializePipeline(context)
  return cicdQualityChecker.runStage(stageName)
}