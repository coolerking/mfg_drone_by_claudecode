import { PlaywrightTestConfig } from '@playwright/test';

/**
 * 高度なE2Eテスト設定・環境管理
 * 環境別設定、デバイス対応、パフォーマンス監視設定を提供
 */

export interface E2EConfig {
  baseURL: string;
  testDataDir: string;
  timeout: number;
  retries: number;
  workers: number;
  headless: boolean;
  slowMo: number;
  video: boolean;
  screenshots: boolean;
  trace: boolean;
  reporter: string[];
  auth: {
    username: string;
    password: string;
  };
  performance: {
    thresholds: {
      pageLoad: number;
      interaction: number;
      fcp: number;
      lcp: number;
      cls: number;
      fid: number;
    };
  };
  accessibility: {
    wcagLevel: 'AA' | 'AAA';
    includeWarnings: boolean;
    disableColorContrastCheck: boolean;
  };
  security: {
    checkXSS: boolean;
    checkCSRF: boolean;
    checkHeaders: boolean;
  };
}

// 環境別設定
export const environments = {
  development: {
    baseURL: 'http://localhost:3000',
    testDataDir: './test-data/dev',
    timeout: 30000,
    retries: 1,
    workers: 1,
    headless: false,
    slowMo: 100,
    video: false,
    screenshots: true,
    trace: true,
    reporter: ['html', 'json'],
    auth: {
      username: 'admin',
      password: 'admin123'
    },
    performance: {
      thresholds: {
        pageLoad: 5000,
        interaction: 2000,
        fcp: 2000,
        lcp: 4000,
        cls: 0.25,
        fid: 300
      }
    },
    accessibility: {
      wcagLevel: 'AA' as const,
      includeWarnings: true,
      disableColorContrastCheck: false
    },
    security: {
      checkXSS: true,
      checkCSRF: true,
      checkHeaders: true
    }
  },
  staging: {
    baseURL: 'https://staging.mfg-drone.com',
    testDataDir: './test-data/staging',
    timeout: 45000,
    retries: 2,
    workers: 2,
    headless: true,
    slowMo: 0,
    video: true,
    screenshots: true,
    trace: true,
    reporter: ['html', 'json', 'junit'],
    auth: {
      username: 'test_admin',
      password: 'staging_pass_123'
    },
    performance: {
      thresholds: {
        pageLoad: 4000,
        interaction: 1500,
        fcp: 1800,
        lcp: 3500,
        cls: 0.2,
        fid: 250
      }
    },
    accessibility: {
      wcagLevel: 'AA' as const,
      includeWarnings: false,
      disableColorContrastCheck: false
    },
    security: {
      checkXSS: true,
      checkCSRF: true,
      checkHeaders: true
    }
  },
  production: {
    baseURL: 'https://mfg-drone.com',
    testDataDir: './test-data/prod',
    timeout: 60000,
    retries: 3,
    workers: 4,
    headless: true,
    slowMo: 0,
    video: true,
    screenshots: true,
    trace: true,
    reporter: ['html', 'json', 'junit', 'allure-playwright'],
    auth: {
      username: process.env.PROD_TEST_USER || 'prod_test_user',
      password: process.env.PROD_TEST_PASS || 'prod_test_pass'
    },
    performance: {
      thresholds: {
        pageLoad: 3000,
        interaction: 1000,
        fcp: 1500,
        lcp: 2500,
        cls: 0.15,
        fid: 200
      }
    },
    accessibility: {
      wcagLevel: 'AA' as const,
      includeWarnings: false,
      disableColorContrastCheck: false
    },
    security: {
      checkXSS: true,
      checkCSRF: true,
      checkHeaders: true
    }
  }
};

// デバイス設定
export const devices = {
  desktop: {
    name: 'Desktop Chrome',
    use: {
      browserName: 'chromium',
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 1,
      isMobile: false,
      hasTouch: false,
      locale: 'ja-JP',
      timezoneId: 'Asia/Tokyo'
    }
  },
  tablet: {
    name: 'iPad',
    use: {
      browserName: 'webkit',
      viewport: { width: 1024, height: 768 },
      deviceScaleFactor: 2,
      isMobile: true,
      hasTouch: true,
      locale: 'ja-JP',
      timezoneId: 'Asia/Tokyo'
    }
  },
  mobile: {
    name: 'iPhone 12',
    use: {
      browserName: 'webkit',
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 3,
      isMobile: true,
      hasTouch: true,
      locale: 'ja-JP',
      timezoneId: 'Asia/Tokyo'
    }
  }
};

// プロジェクト設定
export const projects = {
  smoke: {
    name: 'Smoke Tests',
    testMatch: '**/smoke/**/*.spec.ts',
    retries: 0,
    timeout: 30000
  },
  regression: {
    name: 'Regression Tests',
    testMatch: ['**/auth.spec.ts', '**/dashboard.spec.ts', '**/drone-management.spec.ts'],
    retries: 1,
    timeout: 45000
  },
  critical: {
    name: 'Critical Journey Tests',
    testMatch: '**/critical-journeys.spec.ts',
    retries: 2,
    timeout: 60000
  },
  performance: {
    name: 'Performance Tests',
    testMatch: '**/performance-e2e.spec.ts',
    retries: 1,
    timeout: 90000
  },
  accessibility: {
    name: 'Accessibility Tests',
    testMatch: '**/accessibility-e2e.spec.ts',
    retries: 1,
    timeout: 60000
  },
  security: {
    name: 'Security Tests',
    testMatch: '**/security-e2e.spec.ts',
    retries: 2,
    timeout: 45000
  }
};

// 設定取得ユーティリティ
export function getConfig(): E2EConfig {
  const env = process.env.NODE_ENV || 'development';
  const envConfig = environments[env as keyof typeof environments];
  
  if (!envConfig) {
    throw new Error(`Unknown environment: ${env}`);
  }
  
  return envConfig;
}

// レポート設定
export const reporterConfig = {
  html: {
    outputFolder: 'test-results/html-report',
    open: process.env.CI ? 'never' : 'always'
  },
  json: {
    outputFile: 'test-results/results.json'
  },
  junit: {
    outputFile: 'test-results/junit.xml'
  },
  allure: {
    outputFolder: 'test-results/allure-results',
    detail: true,
    suiteTitle: 'MFG Drone E2E Tests'
  }
};

// パフォーマンス監視設定
export const performanceConfig = {
  metrics: {
    collect: ['FCP', 'LCP', 'CLS', 'FID', 'TTFB'],
    thresholds: {
      FCP: 2000,
      LCP: 2500,
      CLS: 0.15,
      FID: 200,
      TTFB: 600
    }
  },
  monitoring: {
    enabled: true,
    endpoint: process.env.PERFORMANCE_ENDPOINT || 'http://localhost:3001/metrics',
    interval: 5000
  }
};

// アクセシビリティ設定
export const accessibilityConfig = {
  rules: {
    'color-contrast': { enabled: true, level: 'AA' },
    'keyboard-navigation': { enabled: true },
    'aria-labels': { enabled: true },
    'focus-management': { enabled: true },
    'semantic-html': { enabled: true }
  },
  exclude: [
    // 除外するセレクター
    '.third-party-widget',
    '.legacy-component'
  ]
};

// セキュリティ設定
export const securityConfig = {
  xss: {
    enabled: true,
    payloads: [
      '<script>alert("XSS")</script>',
      'javascript:alert("XSS")',
      '<img src=x onerror=alert("XSS")>'
    ]
  },
  csrf: {
    enabled: true,
    tokenName: 'csrf-token',
    headerName: 'X-CSRF-Token'
  },
  headers: {
    required: [
      'X-Frame-Options',
      'X-Content-Type-Options',
      'X-XSS-Protection',
      'Content-Security-Policy',
      'Strict-Transport-Security'
    ]
  }
};

// テストデータ管理
export const testDataConfig = {
  users: {
    admin: {
      username: 'admin',
      password: 'admin123',
      role: 'administrator'
    },
    operator: {
      username: 'operator',
      password: 'operator123',
      role: 'operator'
    },
    viewer: {
      username: 'viewer',
      password: 'viewer123',
      role: 'viewer'
    }
  },
  drones: {
    test: {
      name: 'Test Drone',
      model: 'DJI Mini 3',
      serialNumber: 'TEST-001',
      batteryLevel: 85,
      status: 'idle'
    }
  },
  datasets: {
    test: {
      name: 'Test Dataset',
      description: 'Test dataset for E2E testing',
      type: 'object_detection',
      images: 100
    }
  },
  models: {
    test: {
      name: 'Test Model',
      description: 'Test model for E2E testing',
      algorithm: 'yolov8',
      framework: 'pytorch'
    }
  }
};

// 並列実行設定
export const parallelConfig = {
  maxWorkers: process.env.CI ? 4 : 2,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  timeout: 45000
};

// グローバル設定
export const globalConfig = {
  globalSetup: require.resolve('./global-setup'),
  globalTeardown: require.resolve('./global-teardown'),
  testDir: '../',
  outputDir: '../../../test-results',
  expect: {
    timeout: 10000
  },
  use: {
    actionTimeout: 10000,
    navigationTimeout: 30000,
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure'
  }
};

export default {
  getConfig,
  environments,
  devices,
  projects,
  reporterConfig,
  performanceConfig,
  accessibilityConfig,
  securityConfig,
  testDataConfig,
  parallelConfig,
  globalConfig
};