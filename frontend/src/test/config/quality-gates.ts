/**
 * 品質ゲート設定
 */

// =============================================================================
// Test Coverage Thresholds
// =============================================================================

export const COVERAGE_THRESHOLDS = {
  global: {
    branches: 80,
    functions: 90,
    lines: 90,
    statements: 90
  },
  // コンポーネント別の細かい設定
  components: {
    'src/components/common/**/*.tsx': {
      branches: 85,
      functions: 95,
      lines: 95,
      statements: 95
    },
    'src/hooks/**/*.ts': {
      branches: 90,
      functions: 95,
      lines: 95,
      statements: 95
    },
    'src/utils/**/*.ts': {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90
    },
    'src/services/**/*.ts': {
      branches: 80,
      functions: 85,
      lines: 85,
      statements: 85
    }
  }
}

// =============================================================================
// Performance Benchmarks
// =============================================================================

export const PERFORMANCE_THRESHOLDS = {
  // Bundle size limits (KB)
  bundleSize: {
    main: 500,
    vendor: 1000,
    total: 1500
  },
  
  // Core Web Vitals
  webVitals: {
    FCP: 1800, // First Contentful Paint (ms)
    LCP: 2500, // Largest Contentful Paint (ms)
    FID: 100,  // First Input Delay (ms)
    CLS: 0.1,  // Cumulative Layout Shift
    TTFB: 800  // Time to First Byte (ms)
  },
  
  // Component render times (ms)
  renderTimes: {
    Dashboard: 50,
    DroneManagement: 100,
    DatasetManagement: 100,
    ModelManagement: 100,
    SystemMonitoring: 75
  },
  
  // Memory usage (MB)
  memoryUsage: {
    initial: 50,
    afterNavigation: 100,
    afterHeavyOperation: 150
  }
}

// =============================================================================
// Accessibility Standards
// =============================================================================

export const ACCESSIBILITY_REQUIREMENTS = {
  // WCAG 2.1 compliance level
  wcagLevel: 'AA',
  
  // axe-core rules configuration
  axeRules: {
    // Critical violations that must be fixed
    critical: [
      'keyboard',
      'aria-required-attr',
      'aria-valid-attr-value',
      'button-name',
      'form-field-multiple-labels',
      'heading-order',
      'image-alt',
      'input-button-name',
      'input-image-alt',
      'label',
      'link-name'
    ],
    
    // Important violations that should be fixed
    important: [
      'color-contrast',
      'focus-order-semantics',
      'landmark-one-main',
      'page-has-heading-one',
      'region',
      'skip-link'
    ],
    
    // Violations to monitor but not fail builds
    monitor: [
      'duplicate-id',
      'html-has-lang',
      'landmark-unique',
      'meta-viewport'
    ]
  },
  
  // Color contrast ratios
  colorContrast: {
    normal: 4.5,
    large: 3.0
  },
  
  // Touch target minimum size (px)
  touchTargetSize: 44
}

// =============================================================================
// Security Requirements
// =============================================================================

export const SECURITY_REQUIREMENTS = {
  // Dependencies security
  vulnerabilities: {
    allowedSeverity: ['low'], // Only low severity vulnerabilities allowed
    maxCount: 5,              // Maximum 5 low severity vulnerabilities
    excludePatterns: [
      'dev-dependencies',     // Exclude dev dependencies from security scan
      'prototype-pollution'   // Allow prototype pollution in specific cases
    ]
  },
  
  // Code security
  codeRules: {
    noConsoleLog: true,       // No console.log in production
    noDebugger: true,         // No debugger statements
    noEval: true,             // No eval() usage
    noInnerHTML: true,        // No innerHTML usage (XSS prevention)
    requireCSP: true,         // Require Content Security Policy
    requireSRI: true          // Require Subresource Integrity
  },
  
  // Authentication security
  auth: {
    tokenExpiration: 15 * 60 * 1000, // 15 minutes
    refreshThreshold: 5 * 60 * 1000,  // Refresh when 5 minutes remaining
    maxLoginAttempts: 3,              // Maximum login attempts
    lockoutDuration: 15 * 60 * 1000   // Account lockout duration
  }
}

// =============================================================================
// Code Quality Metrics
// =============================================================================

export const CODE_QUALITY_METRICS = {
  // ESLint rules severity
  eslint: {
    maxWarnings: 10,
    maxErrors: 0,
    rules: {
      'complexity': ['error', { max: 10 }],
      'max-depth': ['error', { max: 4 }],
      'max-lines': ['error', { max: 300 }],
      'max-lines-per-function': ['error', { max: 50 }],
      'max-params': ['error', { max: 5 }]
    }
  },
  
  // TypeScript strict mode
  typescript: {
    strict: true,
    noImplicitAny: true,
    noImplicitReturns: true,
    noUnusedLocals: true,
    noUnusedParameters: true
  },
  
  // Code duplication
  duplication: {
    maxDuplicateLines: 50,
    minDuplicateTokens: 100
  }
}

// =============================================================================
// E2E Test Requirements
// =============================================================================

export const E2E_REQUIREMENTS = {
  // Browser support matrix
  browsers: [
    'chromium',
    'firefox',
    'webkit'
  ],
  
  // Viewport sizes to test
  viewports: [
    { width: 1920, height: 1080 }, // Desktop
    { width: 1366, height: 768 },  // Laptop
    { width: 768, height: 1024 },  // Tablet
    { width: 375, height: 667 }    // Mobile
  ],
  
  // Critical user journeys that must pass
  criticalJourneys: [
    'user-login',
    'drone-connection',
    'emergency-stop',
    'camera-streaming',
    'dataset-upload',
    'model-training-start'
  ],
  
  // Performance thresholds for E2E tests
  performance: {
    maxPageLoadTime: 3000,    // Maximum page load time (ms)
    maxActionResponseTime: 1000, // Maximum response time for user actions (ms)
    maxMemoryUsage: 100       // Maximum memory usage during tests (MB)
  }
}

// =============================================================================
// CI/CD Pipeline Configuration
// =============================================================================

export const PIPELINE_CONFIG = {
  // Build stages that must pass
  stages: [
    'install',
    'lint',
    'type-check',
    'unit-test',
    'integration-test',
    'accessibility-test',
    'e2e-test',
    'security-scan',
    'performance-test',
    'build'
  ],
  
  // Parallel execution groups
  parallel: {
    test: ['unit-test', 'integration-test'],
    quality: ['lint', 'type-check', 'accessibility-test'],
    security: ['security-scan', 'dependency-check']
  },
  
  // Retry configuration
  retry: {
    'e2e-test': 2,
    'performance-test': 1,
    'flaky-test': 3
  },
  
  // Artifacts to preserve
  artifacts: [
    'coverage/',
    'test-results/',
    'playwright-report/',
    'build/',
    'performance-report.json',
    'accessibility-report.json'
  ]
}

// =============================================================================
// Quality Gate Validator
// =============================================================================

export interface QualityReport {
  coverage: {
    passed: boolean
    actual: typeof COVERAGE_THRESHOLDS.global
    required: typeof COVERAGE_THRESHOLDS.global
  }
  performance: {
    passed: boolean
    metrics: any
    thresholds: typeof PERFORMANCE_THRESHOLDS
  }
  accessibility: {
    passed: boolean
    violations: any[]
    requirements: typeof ACCESSIBILITY_REQUIREMENTS
  }
  security: {
    passed: boolean
    vulnerabilities: any[]
    requirements: typeof SECURITY_REQUIREMENTS
  }
  overall: {
    passed: boolean
    score: number // 0-100
    grade: 'A' | 'B' | 'C' | 'D' | 'F'
  }
}

export class QualityGateValidator {
  static validateCoverage(coverageData: any): boolean {
    const { global } = COVERAGE_THRESHOLDS
    
    return (
      coverageData.branches >= global.branches &&
      coverageData.functions >= global.functions &&
      coverageData.lines >= global.lines &&
      coverageData.statements >= global.statements
    )
  }
  
  static validatePerformance(performanceData: any): boolean {
    const { webVitals, bundleSize } = PERFORMANCE_THRESHOLDS
    
    return (
      performanceData.FCP <= webVitals.FCP &&
      performanceData.LCP <= webVitals.LCP &&
      performanceData.FID <= webVitals.FID &&
      performanceData.CLS <= webVitals.CLS &&
      performanceData.bundleSize <= bundleSize.total
    )
  }
  
  static validateAccessibility(axeResults: any[]): boolean {
    const criticalViolations = axeResults.filter(result =>
      ACCESSIBILITY_REQUIREMENTS.axeRules.critical.includes(result.id)
    )
    
    return criticalViolations.length === 0
  }
  
  static validateSecurity(securityData: any): boolean {
    const { vulnerabilities } = SECURITY_REQUIREMENTS
    const highSeverityVulns = securityData.filter((vuln: any) =>
      !vulnerabilities.allowedSeverity.includes(vuln.severity)
    )
    
    return highSeverityVulns.length === 0
  }
  
  static generateReport(
    coverage: any,
    performance: any,
    accessibility: any[],
    security: any[]
  ): QualityReport {
    const coveragePassed = this.validateCoverage(coverage)
    const performancePassed = this.validatePerformance(performance)
    const accessibilityPassed = this.validateAccessibility(accessibility)
    const securityPassed = this.validateSecurity(security)
    
    const passedCount = [
      coveragePassed,
      performancePassed,
      accessibilityPassed,
      securityPassed
    ].filter(Boolean).length
    
    const score = (passedCount / 4) * 100
    const grade = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F'
    
    return {
      coverage: {
        passed: coveragePassed,
        actual: coverage,
        required: COVERAGE_THRESHOLDS.global
      },
      performance: {
        passed: performancePassed,
        metrics: performance,
        thresholds: PERFORMANCE_THRESHOLDS
      },
      accessibility: {
        passed: accessibilityPassed,
        violations: accessibility,
        requirements: ACCESSIBILITY_REQUIREMENTS
      },
      security: {
        passed: securityPassed,
        vulnerabilities: security,
        requirements: SECURITY_REQUIREMENTS
      },
      overall: {
        passed: passedCount === 4,
        score,
        grade
      }
    }
  }
}

// =============================================================================
// Export Configuration
// =============================================================================

export const QualityConfig = {
  COVERAGE_THRESHOLDS,
  PERFORMANCE_THRESHOLDS,
  ACCESSIBILITY_REQUIREMENTS,
  SECURITY_REQUIREMENTS,
  CODE_QUALITY_METRICS,
  E2E_REQUIREMENTS,
  PIPELINE_CONFIG,
  QualityGateValidator
}