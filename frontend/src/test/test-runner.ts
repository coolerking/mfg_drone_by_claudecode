#!/usr/bin/env node

/**
 * 包括的テスト実行スクリプト
 */

import { spawn, exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'
import path from 'path'
import { QualityConfig, QualityGateValidator } from './config/quality-gates'

const execAsync = promisify(exec)

// =============================================================================
// Test Runner Configuration
// =============================================================================

interface TestRunConfig {
  coverage: boolean
  e2e: boolean
  accessibility: boolean
  performance: boolean
  security: boolean
  parallel: boolean
  watch: boolean
  reporter: 'default' | 'json' | 'html' | 'ci'
  bail: boolean
}

const DEFAULT_CONFIG: TestRunConfig = {
  coverage: true,
  e2e: false,
  accessibility: true,
  performance: false,
  security: true,
  parallel: true,
  watch: false,
  reporter: 'default',
  bail: false
}

// =============================================================================
// Test Runner Class
// =============================================================================

export class TestRunner {
  private config: TestRunConfig
  private results: any = {}
  private startTime: number = Date.now()

  constructor(config: Partial<TestRunConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
  }

  async run(): Promise<void> {
    console.log('🚀 MFG Drone Frontend Test Suite Started')
    console.log('='.repeat(50))
    
    try {
      await this.printEnvironmentInfo()
      
      if (this.config.parallel) {
        await this.runTestsInParallel()
      } else {
        await this.runTestsSequentially()
      }
      
      await this.generateQualityReport()
      await this.printSummary()
      
      const success = this.validateQualityGates()
      process.exit(success ? 0 : 1)
      
    } catch (error) {
      console.error('❌ Test execution failed:', error)
      process.exit(1)
    }
  }

  private async printEnvironmentInfo(): Promise<void> {
    console.log('📋 Environment Information')
    console.log('-'.repeat(30))
    
    try {
      const { stdout: nodeVersion } = await execAsync('node --version')
      const { stdout: npmVersion } = await execAsync('npm --version')
      
      console.log(`Node.js: ${nodeVersion.trim()}`)
      console.log(`npm: ${npmVersion.trim()}`)
      console.log(`Platform: ${process.platform}`)
      console.log(`Architecture: ${process.arch}`)
      console.log(`Memory: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`)
      console.log('')
    } catch (error) {
      console.warn('⚠️ Could not gather environment info')
    }
  }

  private async runTestsInParallel(): Promise<void> {
    console.log('🏃‍♂️ Running tests in parallel...')
    
    const testPromises: Promise<any>[] = []
    
    // Unit and Integration Tests
    testPromises.push(this.runUnitTests())
    
    // Static Analysis
    if (this.config.accessibility) {
      testPromises.push(this.runAccessibilityTests())
    }
    
    if (this.config.security) {
      testPromises.push(this.runSecurityTests())
    }
    
    // Wait for parallel tests to complete
    const results = await Promise.allSettled(testPromises)
    
    // Handle failed tests
    const failed = results.filter(result => result.status === 'rejected')
    if (failed.length > 0 && this.config.bail) {
      throw new Error(`${failed.length} test suites failed`)
    }
    
    // Run sequential tests
    if (this.config.e2e) {
      await this.runE2ETests()
    }
    
    if (this.config.performance) {
      await this.runPerformanceTests()
    }
  }

  private async runTestsSequentially(): Promise<void> {
    console.log('📋 Running tests sequentially...')
    
    await this.runUnitTests()
    
    if (this.config.accessibility) {
      await this.runAccessibilityTests()
    }
    
    if (this.config.security) {
      await this.runSecurityTests()
    }
    
    if (this.config.e2e) {
      await this.runE2ETests()
    }
    
    if (this.config.performance) {
      await this.runPerformanceTests()
    }
  }

  private async runUnitTests(): Promise<void> {
    console.log('🧪 Running unit and integration tests...')
    
    const args = ['run', 'test']
    
    if (this.config.coverage) {
      args.push('--coverage')
    }
    
    if (this.config.watch) {
      args.push('--watch')
    }
    
    if (this.config.reporter === 'json') {
      args.push('--reporter=json')
    }
    
    try {
      const { stdout, stderr } = await execAsync(`npm ${args.join(' ')}`)
      
      if (this.config.coverage) {
        this.results.coverage = await this.parseCoverageReport()
      }
      
      console.log('✅ Unit tests completed')
      
    } catch (error) {
      console.error('❌ Unit tests failed:', error)
      if (this.config.bail) throw error
      this.results.unitTests = { passed: false, error }
    }
  }

  private async runE2ETests(): Promise<void> {
    console.log('🎭 Running E2E tests...')
    
    try {
      const { stdout } = await execAsync('npm run test:e2e')
      
      this.results.e2e = {
        passed: true,
        output: stdout
      }
      
      console.log('✅ E2E tests completed')
      
    } catch (error) {
      console.error('❌ E2E tests failed:', error)
      if (this.config.bail) throw error
      this.results.e2e = { passed: false, error }
    }
  }

  private async runAccessibilityTests(): Promise<void> {
    console.log('♿ Running accessibility tests...')
    
    try {
      // Run specific accessibility test suite
      const { stdout } = await execAsync('npm run test -- --testPathPattern=accessibility')
      
      this.results.accessibility = {
        passed: true,
        violations: [], // Parse from actual axe results
        output: stdout
      }
      
      console.log('✅ Accessibility tests completed')
      
    } catch (error) {
      console.error('❌ Accessibility tests failed:', error)
      if (this.config.bail) throw error
      this.results.accessibility = { passed: false, error }
    }
  }

  private async runSecurityTests(): Promise<void> {
    console.log('🔒 Running security tests...')
    
    try {
      // Run npm audit
      const { stdout: auditOutput } = await execAsync('npm audit --json')
      const auditData = JSON.parse(auditOutput)
      
      this.results.security = {
        passed: auditData.metadata.vulnerabilities.total === 0,
        vulnerabilities: auditData.vulnerabilities || [],
        audit: auditData
      }
      
      console.log('✅ Security scan completed')
      
    } catch (error) {
      console.error('❌ Security scan failed:', error)
      if (this.config.bail) throw error
      this.results.security = { passed: false, error }
    }
  }

  private async runPerformanceTests(): Promise<void> {
    console.log('⚡ Running performance tests...')
    
    try {
      // Build the application first
      await execAsync('npm run build')
      
      // Analyze bundle size
      const bundleStats = await this.analyzeBundleSize()
      
      this.results.performance = {
        passed: bundleStats.totalSize <= QualityConfig.PERFORMANCE_THRESHOLDS.bundleSize.total * 1024,
        bundleSize: bundleStats,
        metrics: {}
      }
      
      console.log('✅ Performance tests completed')
      
    } catch (error) {
      console.error('❌ Performance tests failed:', error)
      if (this.config.bail) throw error
      this.results.performance = { passed: false, error }
    }
  }

  private async parseCoverageReport(): Promise<any> {
    try {
      const coveragePath = path.join(process.cwd(), 'coverage', 'coverage-summary.json')
      const coverageData = await fs.readFile(coveragePath, 'utf-8')
      return JSON.parse(coverageData)
    } catch (error) {
      console.warn('⚠️ Could not parse coverage report')
      return null
    }
  }

  private async analyzeBundleSize(): Promise<any> {
    try {
      const distPath = path.join(process.cwd(), 'dist')
      const files = await fs.readdir(distPath, { recursive: true })
      
      let totalSize = 0
      const fileStats: any[] = []
      
      for (const file of files) {
        const filePath = path.join(distPath, file as string)
        const stats = await fs.stat(filePath)
        
        if (stats.isFile()) {
          totalSize += stats.size
          fileStats.push({
            path: file,
            size: stats.size,
            sizeKB: Math.round(stats.size / 1024)
          })
        }
      }
      
      return {
        totalSize: Math.round(totalSize / 1024), // KB
        files: fileStats.sort((a, b) => b.size - a.size)
      }
    } catch (error) {
      console.warn('⚠️ Could not analyze bundle size')
      return { totalSize: 0, files: [] }
    }
  }

  private async generateQualityReport(): Promise<void> {
    console.log('📊 Generating quality report...')
    
    const qualityReport = QualityGateValidator.generateReport(
      this.results.coverage?.total || {},
      this.results.performance || {},
      this.results.accessibility?.violations || [],
      this.results.security?.vulnerabilities || []
    )
    
    this.results.qualityReport = qualityReport
    
    // Save report to file
    const reportPath = path.join(process.cwd(), 'test-results', 'quality-report.json')
    await fs.mkdir(path.dirname(reportPath), { recursive: true })
    await fs.writeFile(reportPath, JSON.stringify(qualityReport, null, 2))
    
    console.log(`📄 Quality report saved to: ${reportPath}`)
  }

  private validateQualityGates(): boolean {
    const report = this.results.qualityReport
    
    if (!report) {
      console.warn('⚠️ No quality report available')
      return false
    }
    
    if (report.overall.passed) {
      console.log(`🎉 All quality gates passed! Score: ${report.overall.score}/100 (${report.overall.grade})`)
      return true
    } else {
      console.error(`❌ Quality gates failed! Score: ${report.overall.score}/100 (${report.overall.grade})`)
      
      // Print specific failures
      if (!report.coverage.passed) {
        console.error('   - Coverage requirements not met')
      }
      if (!report.performance.passed) {
        console.error('   - Performance thresholds exceeded')
      }
      if (!report.accessibility.passed) {
        console.error('   - Accessibility violations found')
      }
      if (!report.security.passed) {
        console.error('   - Security vulnerabilities detected')
      }
      
      return false
    }
  }

  private async printSummary(): Promise<void> {
    const duration = Date.now() - this.startTime
    
    console.log('')
    console.log('📋 Test Execution Summary')
    console.log('='.repeat(50))
    console.log(`Duration: ${Math.round(duration / 1000)}s`)
    console.log(`Memory Usage: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`)
    
    // Print test results
    Object.entries(this.results).forEach(([key, result]) => {
      if (key === 'qualityReport') return
      
      const passed = (result as any)?.passed ?? false
      const icon = passed ? '✅' : '❌'
      console.log(`${icon} ${key}: ${passed ? 'PASSED' : 'FAILED'}`)
    })
    
    if (this.results.qualityReport) {
      const { overall } = this.results.qualityReport
      const icon = overall.passed ? '🎉' : '❌'
      console.log(`${icon} Overall Quality Score: ${overall.score}/100 (${overall.grade})`)
    }
    
    console.log('='.repeat(50))
  }
}

// =============================================================================
// CLI Interface
// =============================================================================

export const runTests = async (config?: Partial<TestRunConfig>): Promise<void> => {
  const runner = new TestRunner(config)
  await runner.run()
}

// Export for use in other scripts
export { TestRunConfig, QualityConfig, QualityGateValidator }

// If run directly from command line
if (require.main === module) {
  const args = process.argv.slice(2)
  const config: Partial<TestRunConfig> = {}
  
  // Parse command line arguments
  if (args.includes('--coverage')) config.coverage = true
  if (args.includes('--no-coverage')) config.coverage = false
  if (args.includes('--e2e')) config.e2e = true
  if (args.includes('--no-e2e')) config.e2e = false
  if (args.includes('--accessibility')) config.accessibility = true
  if (args.includes('--no-accessibility')) config.accessibility = false
  if (args.includes('--performance')) config.performance = true
  if (args.includes('--security')) config.security = true
  if (args.includes('--watch')) config.watch = true
  if (args.includes('--bail')) config.bail = true
  if (args.includes('--sequential')) config.parallel = false
  
  runTests(config).catch((error) => {
    console.error('Test execution failed:', error)
    process.exit(1)
  })
}