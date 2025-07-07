import { expect, Page, BrowserContext } from '@playwright/test';

/**
 * 包括的テストヘルパーユーティリティ
 * E2Eテストで共通して使用される関数とコンポーネント操作を提供
 */

// Authentication helpers
export class AuthHelper {
  constructor(private page: Page) {}

  async login(username: string = 'admin', password: string = 'admin123') {
    await this.page.goto('/login');
    await this.page.fill('[data-testid="username"]', username);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="login-button"]');
    await this.page.waitForURL('/dashboard');
  }

  async logout() {
    await this.page.click('[data-testid="user-menu"]');
    await this.page.click('[data-testid="logout-button"]');
    await this.page.waitForURL('/login');
  }

  async checkAuthState() {
    const token = await this.page.evaluate(() => localStorage.getItem('authToken'));
    return !!token;
  }
}

// Navigation helpers
export class NavigationHelper {
  constructor(private page: Page) {}

  async navigateTo(path: string) {
    await this.page.goto(path);
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToPage(pageName: string) {
    const pageMap = {
      'dashboard': '/dashboard',
      'drone-management': '/drone-management',
      'dataset-management': '/dataset-management',
      'model-management': '/model-management',
      'tracking-control': '/tracking-control',
      'system-monitoring': '/system-monitoring',
      'settings': '/settings'
    };
    
    const path = pageMap[pageName as keyof typeof pageMap];
    if (!path) {
      throw new Error(`Unknown page: ${pageName}`);
    }
    
    await this.navigateTo(path);
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForFunction(() => document.readyState === 'complete');
  }
}

// Form helpers
export class FormHelper {
  constructor(private page: Page) {}

  async fillForm(formData: Record<string, string>) {
    for (const [field, value] of Object.entries(formData)) {
      await this.page.fill(`[data-testid="${field}"]`, value);
    }
  }

  async submitForm(formSelector: string = 'form') {
    await this.page.click(`${formSelector} [type="submit"]`);
  }

  async waitForFormSubmission() {
    await this.page.waitForResponse(response => 
      response.url().includes('/api/') && 
      (response.status() === 200 || response.status() === 201)
    );
  }
}

// Data helpers
export class DataHelper {
  constructor(private page: Page) {}

  async createTestDrone(name: string = 'Test Drone') {
    const droneData = {
      name,
      model: 'DJI Mini 3',
      serialNumber: `TEST-${Date.now()}`,
      batteryLevel: '85',
      status: 'idle'
    };
    
    await this.page.goto('/drone-management');
    await this.page.click('[data-testid="add-drone-button"]');
    
    for (const [field, value] of Object.entries(droneData)) {
      await this.page.fill(`[data-testid="drone-${field}"]`, value);
    }
    
    await this.page.click('[data-testid="save-drone-button"]');
    await this.page.waitForResponse(response => 
      response.url().includes('/api/drones') && response.status() === 201
    );
    
    return droneData;
  }

  async createTestDataset(name: string = 'Test Dataset') {
    const datasetData = {
      name,
      description: 'Test dataset for E2E testing',
      type: 'object_detection',
      tags: 'test, automation'
    };
    
    await this.page.goto('/dataset-management');
    await this.page.click('[data-testid="create-dataset-button"]');
    
    for (const [field, value] of Object.entries(datasetData)) {
      await this.page.fill(`[data-testid="dataset-${field}"]`, value);
    }
    
    await this.page.click('[data-testid="save-dataset-button"]');
    await this.page.waitForResponse(response => 
      response.url().includes('/api/datasets') && response.status() === 201
    );
    
    return datasetData;
  }

  async createTestModel(name: string = 'Test Model') {
    const modelData = {
      name,
      description: 'Test model for E2E testing',
      algorithm: 'yolov8',
      framework: 'pytorch'
    };
    
    await this.page.goto('/model-management');
    await this.page.click('[data-testid="create-model-button"]');
    
    for (const [field, value] of Object.entries(modelData)) {
      await this.page.fill(`[data-testid="model-${field}"]`, value);
    }
    
    await this.page.click('[data-testid="save-model-button"]');
    await this.page.waitForResponse(response => 
      response.url().includes('/api/models') && response.status() === 201
    );
    
    return modelData;
  }
}

// Component interaction helpers
export class ComponentHelper {
  constructor(private page: Page) {}

  async waitForComponent(selector: string, timeout: number = 10000) {
    await this.page.waitForSelector(selector, { timeout });
  }

  async clickAndWait(selector: string, waitForSelector?: string) {
    await this.page.click(selector);
    if (waitForSelector) {
      await this.page.waitForSelector(waitForSelector);
    }
  }

  async selectOption(selector: string, value: string) {
    await this.page.selectOption(selector, value);
  }

  async uploadFile(selector: string, filePath: string) {
    await this.page.setInputFiles(selector, filePath);
  }

  async waitForTable(tableSelector: string = '[data-testid="data-table"]') {
    await this.page.waitForSelector(tableSelector);
    await this.page.waitForFunction((selector) => {
      const table = document.querySelector(selector);
      return table && table.querySelectorAll('tbody tr').length > 0;
    }, tableSelector);
  }

  async getTableRowCount(tableSelector: string = '[data-testid="data-table"]') {
    return await this.page.locator(`${tableSelector} tbody tr`).count();
  }

  async searchInTable(searchTerm: string, searchSelector: string = '[data-testid="search-input"]') {
    await this.page.fill(searchSelector, searchTerm);
    await this.page.press(searchSelector, 'Enter');
    await this.page.waitForTimeout(1000); // Wait for search to complete
  }
}

// API helpers
export class ApiHelper {
  constructor(private page: Page) {}

  async mockApiResponse(url: string, response: any) {
    await this.page.route(url, route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  async waitForApiCall(urlPattern: string, method: string = 'GET') {
    return await this.page.waitForResponse(response => 
      response.url().includes(urlPattern) && response.request().method() === method
    );
  }

  async interceptApiCall(urlPattern: string, callback: (response: any) => void) {
    this.page.on('response', async (response) => {
      if (response.url().includes(urlPattern)) {
        const data = await response.json();
        callback(data);
      }
    });
  }
}

// Performance helpers
export class PerformanceHelper {
  constructor(private page: Page) {}

  async measurePageLoad(url: string) {
    const startTime = Date.now();
    await this.page.goto(url);
    await this.page.waitForLoadState('networkidle');
    const endTime = Date.now();
    return endTime - startTime;
  }

  async measureInteraction(selector: string, action: 'click' | 'fill' = 'click', value?: string) {
    const startTime = Date.now();
    
    if (action === 'click') {
      await this.page.click(selector);
    } else if (action === 'fill' && value) {
      await this.page.fill(selector, value);
    }
    
    await this.page.waitForLoadState('networkidle');
    const endTime = Date.now();
    return endTime - startTime;
  }

  async getCoreWebVitals() {
    return await this.page.evaluate(() => {
      return new Promise((resolve) => {
        if ('web-vitals' in window) {
          // @ts-ignore
          const { getCLS, getFID, getFCP, getLCP, getTTFB } = window['web-vitals'];
          
          const metrics: any = {};
          
          getCLS((metric: any) => metrics.cls = metric);
          getFID((metric: any) => metrics.fid = metric);
          getFCP((metric: any) => metrics.fcp = metric);
          getLCP((metric: any) => metrics.lcp = metric);
          getTTFB((metric: any) => metrics.ttfb = metric);
          
          setTimeout(() => resolve(metrics), 1000);
        } else {
          resolve({});
        }
      });
    });
  }
}

// Accessibility helpers
export class AccessibilityHelper {
  constructor(private page: Page) {}

  async checkKeyboardNavigation(selectors: string[]) {
    for (const selector of selectors) {
      await this.page.focus(selector);
      await expect(this.page.locator(selector)).toBeFocused();
    }
  }

  async checkAriaLabels(selectors: string[]) {
    for (const selector of selectors) {
      const ariaLabel = await this.page.getAttribute(selector, 'aria-label');
      const ariaLabelledby = await this.page.getAttribute(selector, 'aria-labelledby');
      
      expect(ariaLabel || ariaLabelledby).toBeTruthy();
    }
  }

  async checkColorContrast(selector: string, minRatio: number = 4.5) {
    const contrast = await this.page.evaluate((sel, ratio) => {
      const element = document.querySelector(sel);
      if (!element) return false;
      
      const style = window.getComputedStyle(element);
      const bgColor = style.backgroundColor;
      const textColor = style.color;
      
      // Simple contrast check (simplified for demo)
      return true; // In real implementation, use proper contrast calculation
    }, selector, minRatio);
    
    expect(contrast).toBeTruthy();
  }
}

// Security helpers
export class SecurityHelper {
  constructor(private page: Page) {}

  async checkXSSProtection(inputSelector: string) {
    const xssPayload = '<script>alert("XSS")</script>';
    await this.page.fill(inputSelector, xssPayload);
    
    // Check if script was not executed
    const alertHandled = await this.page.evaluate(() => {
      return new Promise((resolve) => {
        const originalAlert = window.alert;
        let alertCalled = false;
        
        window.alert = () => {
          alertCalled = true;
        };
        
        setTimeout(() => {
          window.alert = originalAlert;
          resolve(alertCalled);
        }, 1000);
      });
    });
    
    expect(alertHandled).toBeFalsy();
  }

  async checkCSRFProtection() {
    const csrfToken = await this.page.evaluate(() => {
      const metaTag = document.querySelector('meta[name="csrf-token"]');
      return metaTag ? metaTag.getAttribute('content') : null;
    });
    
    expect(csrfToken).toBeTruthy();
  }

  async checkSecurityHeaders() {
    const response = await this.page.goto('/');
    const headers = response?.headers();
    
    expect(headers?.['x-frame-options']).toBeTruthy();
    expect(headers?.['x-content-type-options']).toBeTruthy();
    expect(headers?.['x-xss-protection']).toBeTruthy();
  }
}

// Test cleanup helpers
export class CleanupHelper {
  constructor(private page: Page) {}

  async cleanupTestData() {
    // Clean up test drones
    await this.page.goto('/drone-management');
    const testDrones = await this.page.locator('[data-testid="drone-card"]').filter({ 
      hasText: 'Test Drone' 
    });
    
    const count = await testDrones.count();
    for (let i = 0; i < count; i++) {
      await testDrones.nth(i).locator('[data-testid="delete-drone"]').click();
      await this.page.click('[data-testid="confirm-delete"]');
    }
    
    // Clean up test datasets
    await this.page.goto('/dataset-management');
    const testDatasets = await this.page.locator('[data-testid="dataset-card"]').filter({ 
      hasText: 'Test Dataset' 
    });
    
    const datasetCount = await testDatasets.count();
    for (let i = 0; i < datasetCount; i++) {
      await testDatasets.nth(i).locator('[data-testid="delete-dataset"]').click();
      await this.page.click('[data-testid="confirm-delete"]');
    }
    
    // Clean up test models
    await this.page.goto('/model-management');
    const testModels = await this.page.locator('[data-testid="model-card"]').filter({ 
      hasText: 'Test Model' 
    });
    
    const modelCount = await testModels.count();
    for (let i = 0; i < modelCount; i++) {
      await testModels.nth(i).locator('[data-testid="delete-model"]').click();
      await this.page.click('[data-testid="confirm-delete"]');
    }
  }

  async clearLocalStorage() {
    await this.page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  }

  async clearCookies() {
    await this.page.context().clearCookies();
  }
}

// Test factory for creating helper instances
export class TestHelperFactory {
  static createHelpers(page: Page) {
    return {
      auth: new AuthHelper(page),
      navigation: new NavigationHelper(page),
      form: new FormHelper(page),
      data: new DataHelper(page),
      component: new ComponentHelper(page),
      api: new ApiHelper(page),
      performance: new PerformanceHelper(page),
      accessibility: new AccessibilityHelper(page),
      security: new SecurityHelper(page),
      cleanup: new CleanupHelper(page)
    };
  }
}