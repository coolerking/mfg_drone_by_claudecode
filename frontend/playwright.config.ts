import { defineConfig, devices } from '@playwright/test'

/**
 * 最適化されたPlaywright E2Eテスト設定
 * 環境別設定、プロジェクト別テスト、並列実行対応
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './src/test/e2e',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 1,
  /* Parallel workers configuration */
  workers: process.env.CI ? 4 : 2,
  /* Global timeout */
  timeout: 45 * 1000,
  expect: {
    /* Global expect timeout */
    timeout: 10 * 1000,
  },
  /* Reporter configuration */
  reporter: [
    ['html', { outputFolder: 'test-results/html-report', open: process.env.CI ? 'never' : 'on-failure' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ...(process.env.CI ? [['github']] : [])
  ],
  /* Global setup and teardown */
  globalSetup: require.resolve('./src/test/e2e/config/global-setup'),
  globalTeardown: require.resolve('./src/test/e2e/config/global-teardown'),
  /* Output directory */
  outputDir: 'test-results/',
  /* Shared settings for all projects */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    /* Action timeout */
    actionTimeout: 10 * 1000,
    /* Navigation timeout */
    navigationTimeout: 30 * 1000,
    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',
    /* Screenshots */
    screenshot: 'only-on-failure',
    /* Video recording */
    video: 'retain-on-failure',
    /* Locale and timezone */
    locale: 'ja-JP',
    timezoneId: 'Asia/Tokyo',
  },

  /* Configure projects for different test types and browsers */
  projects: [
    // Smoke tests - quick validation
    {
      name: 'smoke',
      testMatch: ['**/auth.spec.ts', '**/dashboard.spec.ts'],
      use: { ...devices['Desktop Chrome'] },
      retries: 0,
      timeout: 30 * 1000,
    },

    // Regression tests - core functionality
    {
      name: 'regression',
      testMatch: ['**/auth.spec.ts', '**/dashboard.spec.ts', '**/drone-management.spec.ts', '**/dataset-management.spec.ts', '**/model-management.spec.ts'],
      use: { ...devices['Desktop Chrome'] },
      retries: 1,
      timeout: 45 * 1000,
    },

    // Critical journey tests
    {
      name: 'critical',
      testMatch: '**/critical-journeys.spec.ts',
      use: { ...devices['Desktop Chrome'] },
      retries: 2,
      timeout: 60 * 1000,
    },

    // Performance tests
    {
      name: 'performance',
      testMatch: '**/performance-e2e.spec.ts',
      use: { 
        ...devices['Desktop Chrome'],
        // Performance monitoring settings
        launchOptions: {
          args: ['--enable-precise-memory-info']
        }
      },
      retries: 1,
      timeout: 90 * 1000,
    },

    // Accessibility tests
    {
      name: 'accessibility',
      testMatch: '**/accessibility-e2e.spec.ts',
      use: { ...devices['Desktop Chrome'] },
      retries: 1,
      timeout: 60 * 1000,
    },

    // Security tests
    {
      name: 'security',
      testMatch: '**/security-e2e.spec.ts',
      use: { ...devices['Desktop Chrome'] },
      retries: 2,
      timeout: 45 * 1000,
    },

    // Tracking control tests
    {
      name: 'tracking',
      testMatch: '**/tracking-control.spec.ts',
      use: { ...devices['Desktop Chrome'] },
      retries: 1,
      timeout: 60 * 1000,
    },

    // Cross-browser testing
    {
      name: 'firefox',
      testMatch: ['**/auth.spec.ts', '**/dashboard.spec.ts', '**/drone-management.spec.ts'],
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      testMatch: ['**/auth.spec.ts', '**/dashboard.spec.ts'],
      use: { ...devices['Desktop Safari'] },
    },

    // Mobile testing
    {
      name: 'mobile-chrome',
      testMatch: ['**/auth.spec.ts', '**/dashboard.spec.ts', '**/accessibility-e2e.spec.ts'],
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'mobile-safari',
      testMatch: ['**/auth.spec.ts', '**/dashboard.spec.ts'],
      use: { ...devices['iPhone 12'] },
    },

    // Full test suite (all tests, Chrome only)
    {
      name: 'full',
      testMatch: '**/*.spec.ts',
      use: { ...devices['Desktop Chrome'] },
      retries: 1,
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})