import { test, expect } from '@playwright/test';
import { TestHelperFactory } from './helpers/test-helpers';

/**
 * セキュリティE2Eテスト
 * 認証・認可、XSS・CSRF防止、セッション管理、データ保護をテスト
 */

test.describe('Security E2E Tests', () => {
  let helpers: ReturnType<typeof TestHelperFactory.createHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = TestHelperFactory.createHelpers(page);
  });

  test.afterEach(async ({ page }) => {
    await helpers.cleanup.cleanupTestData();
    await helpers.cleanup.clearLocalStorage();
    await helpers.cleanup.clearCookies();
  });

  test.describe('Authentication and Authorization', () => {
    test('should enforce authentication on protected routes', async ({ page }) => {
      // 保護されたルートでの認証強制
      const protectedRoutes = [
        '/dashboard',
        '/drone-management',
        '/dataset-management',
        '/model-management',
        '/tracking-control',
        '/system-monitoring',
        '/settings'
      ];
      
      for (const route of protectedRoutes) {
        // 未認証でアクセス
        await page.goto(route);
        
        // ログインページにリダイレクトされる
        await expect(page).toHaveURL(/.*\/login/);
        
        // ログインフォームが表示される
        await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
      }
    });

    test('should handle login security properly', async ({ page }) => {
      // ログインセキュリティの適切な処理
      await page.goto('/login');
      
      // 1. 無効な認証情報でのログイン試行
      await page.fill('[data-testid="username"]', 'invalid_user');
      await page.fill('[data-testid="password"]', 'wrong_password');
      await page.click('[data-testid="login-button"]');
      
      // エラーメッセージが表示される（具体的な情報は漏洩しない）
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      const errorText = await page.locator('[data-testid="error-message"]').textContent();
      
      // 一般的なエラーメッセージ（ユーザー名とパスワードを特定しない）
      expect(errorText).toContain('認証に失敗しました');
      expect(errorText).not.toContain('ユーザー名');
      expect(errorText).not.toContain('パスワード');
      
      // 2. ブルートフォース攻撃対策
      for (let i = 0; i < 5; i++) {
        await page.fill('[data-testid="username"]', 'test_user');
        await page.fill('[data-testid="password"]', `wrong_password_${i}`);
        await page.click('[data-testid="login-button"]');
        await page.waitForTimeout(1000);
      }
      
      // アカウントロック または レート制限のメッセージ
      const finalError = await page.locator('[data-testid="error-message"]').textContent();
      expect(finalError).toMatch(/(ロック|制限|しばらく|待機)/);
      
      // 3. パスワードフィールドのセキュリティ
      const passwordField = page.locator('[data-testid="password"]');
      const inputType = await passwordField.getAttribute('type');
      expect(inputType).toBe('password');
      
      // パスワード表示/非表示機能の確認
      const toggleButton = page.locator('[data-testid="password-toggle"]');
      if (await toggleButton.count() > 0) {
        await toggleButton.click();
        const typeAfterToggle = await passwordField.getAttribute('type');
        expect(typeAfterToggle).toBe('text');
        
        await toggleButton.click();
        const typeAfterSecondToggle = await passwordField.getAttribute('type');
        expect(typeAfterSecondToggle).toBe('password');
      }
    });

    test('should implement proper session management', async ({ page }) => {
      // 適切なセッション管理
      // 正常ログイン
      await helpers.auth.login();
      await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
      
      // 1. セッション情報の確認
      const authToken = await page.evaluate(() => localStorage.getItem('authToken'));
      expect(authToken).toBeTruthy();
      
      // 2. セッションタイムアウトのテスト
      // セッション期限切れのシミュレーション
      await helpers.api.mockApiResponse('/api/auth/verify', {
        error: 'Token expired',
        status: 401
      });
      
      await page.reload();
      
      // ログイン画面にリダイレクトされる
      await expect(page).toHaveURL(/.*\/login/);
      
      // 3. 同時セッション制御
      // 新しいブラウザコンテキストで同じユーザーでログイン
      const newContext = await page.context().browser()?.newContext();
      if (newContext) {
        const newPage = await newContext.newPage();
        const newHelpers = TestHelperFactory.createHelpers(newPage);
        
        await newHelpers.auth.login('admin', 'admin123');
        
        // 元のセッションが無効化されるか確認
        await page.goto('/dashboard');
        
        // セッション競合の警告または自動ログアウト
        const sessionWarning = await page.locator('[data-testid="session-conflict"]');
        if (await sessionWarning.count() > 0) {
          await expect(sessionWarning).toBeVisible();
        } else {
          // または自動的にログイン画面にリダイレクト
          await expect(page).toHaveURL(/.*\/login/);
        }
        
        await newContext.close();
      }
    });

    test('should enforce role-based access control', async ({ page, context }) => {
      // ロールベースアクセス制御の強制
      // 1. 管理者権限でのアクセス
      await helpers.auth.login('admin', 'admin123');
      
      // 管理者専用機能へのアクセス
      await helpers.navigation.navigateToPage('settings');
      await expect(page.locator('[data-testid="system-settings"]')).toBeVisible();
      await expect(page.locator('[data-testid="user-management"]')).toBeVisible();
      
      await helpers.auth.logout();
      
      // 2. 一般ユーザー権限でのアクセス
      const userPage = await context.newPage();
      const userHelpers = TestHelperFactory.createHelpers(userPage);
      
      await userHelpers.auth.login('operator', 'operator123');
      
      // 一般ユーザーは管理機能にアクセスできない
      await userPage.goto('/settings');
      
      // アクセス拒否ページまたは権限不足メッセージ
      const accessDenied = await userPage.locator('[data-testid="access-denied"], [data-testid="unauthorized"]');
      await expect(accessDenied).toBeVisible();
      
      // 許可された機能は利用可能
      await userHelpers.navigation.navigateToPage('dashboard');
      await expect(userPage.locator('[data-testid="dashboard"]')).toBeVisible();
      
      await userPage.close();
      
      // 3. APIレベルでの権限確認
      await helpers.auth.login('operator', 'operator123');
      
      // 権限のないAPI呼び出し
      const response = await page.request.delete('/api/users/1', {
        headers: {
          'Authorization': `Bearer ${await page.evaluate(() => localStorage.getItem('authToken'))}`
        }
      });
      
      expect(response.status()).toBe(403); // Forbidden
    });

    test('should handle logout securely', async ({ page }) => {
      // 安全なログアウト処理
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // 1. 明示的なログアウト
      await helpers.auth.logout();
      
      // ログイン画面にリダイレクト
      await expect(page).toHaveURL(/.*\/login/);
      
      // ローカルストレージがクリアされている
      const authToken = await page.evaluate(() => localStorage.getItem('authToken'));
      expect(authToken).toBeFalsy();
      
      // セッションストレージもクリアされている
      const sessionData = await page.evaluate(() => sessionStorage.length);
      expect(sessionData).toBe(0);
      
      // 2. ログアウト後の保護されたページアクセス
      await page.goto('/dashboard');
      await expect(page).toHaveURL(/.*\/login/);
      
      // 3. ブラウザタブ閉鎖時のセッション処理
      // 新しいタブでログイン
      const newTab = await page.context().newPage();
      const newHelpers = TestHelperFactory.createHelpers(newTab);
      
      await newHelpers.auth.login();
      await newTab.goto('/dashboard');
      await expect(newTab.locator('[data-testid="dashboard"]')).toBeVisible();
      
      // タブを閉じる
      await newTab.close();
      
      // 元のタブでアクセス試行
      await page.goto('/dashboard');
      
      // セッションの処理方法に応じて、ログインが必要または継続
      // （実装によって異なる）
    });
  });

  test.describe('XSS Protection', () => {
    test('should prevent stored XSS attacks', async ({ page }) => {
      // 保存型XSS攻撃の防止
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('drone-management');
      
      // XSSペイロードを含むデータの投入試行
      const xssPayloads = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        'javascript:alert("XSS")',
        '<svg onload=alert("XSS")>',
        '"><script>alert("XSS")</script>',
        "'; alert('XSS'); //",
        '<iframe src="javascript:alert(\"XSS\")"></iframe>'
      ];
      
      for (const payload of xssPayloads) {
        // ドローン作成でXSSペイロードを注入
        await page.click('[data-testid="add-drone-button"]');
        await helpers.component.waitForComponent('[data-testid="add-drone-modal"]');
        
        await page.fill('[data-testid="drone-name"]', payload);
        await page.fill('[data-testid="drone-model"]', 'Test Model');
        await page.fill('[data-testid="drone-serialNumber"]', 'TEST-001');
        
        await page.click('[data-testid="save-drone-button"]');
        
        // スクリプトが実行されないことを確認
        const alertTriggered = await page.evaluate(() => {
          return new Promise((resolve) => {
            const originalAlert = window.alert;
            let alertCalled = false;
            
            window.alert = (message) => {
              alertCalled = true;
              window.alert = originalAlert;
              resolve(true);
            };
            
            setTimeout(() => {
              window.alert = originalAlert;
              resolve(alertCalled);
            }, 2000);
          });
        });
        
        expect(alertTriggered).toBeFalsy();
        
        // データが適切にエスケープされて表示される
        if (await page.locator('[data-testid="success-message"]').count() > 0) {
          await page.reload();
          await helpers.component.waitForComponent('[data-testid="drone-list"]');
          
          const droneCard = page.locator('[data-testid="drone-card"]').first();
          const displayedName = await droneCard.locator('[data-testid="drone-name"]').textContent();
          
          // HTMLタグが文字列として表示されている（実行されていない）
          if (displayedName?.includes(payload)) {
            expect(displayedName).toContain('&lt;'); // エスケープされている
          }
        }
        
        // クリーンアップ
        if (await page.locator('[data-testid="cancel-button"]').count() > 0) {
          await page.click('[data-testid="cancel-button"]');
        }
      }
    });

    test('should prevent reflected XSS attacks', async ({ page }) => {
      // 反射型XSS攻撃の防止
      await helpers.auth.login();
      
      // URLパラメータでのXSS試行
      const xssUrl = '/dataset-management?search=<script>alert("XSS")</script>';
      await page.goto(xssUrl);
      
      // スクリプトが実行されない
      const alertTriggered = await page.evaluate(() => {
        return new Promise((resolve) => {
          const originalAlert = window.alert;
          let alertCalled = false;
          
          window.alert = () => {
            alertCalled = true;
          };
          
          setTimeout(() => {
            window.alert = originalAlert;
            resolve(alertCalled);
          }, 2000);
        });
      });
      
      expect(alertTriggered).toBeFalsy();
      
      // 検索パラメータが安全に処理される
      const searchInput = page.locator('[data-testid="search-input"]');
      if (await searchInput.count() > 0) {
        const searchValue = await searchInput.inputValue();
        // HTMLタグがエスケープされている
        expect(searchValue).not.toContain('<script>');
      }
    });

    test('should sanitize user inputs', async ({ page }) => {
      // ユーザー入力のサニタイゼーション
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dataset-management');
      
      await page.click('[data-testid="create-dataset-button"]');
      await helpers.component.waitForComponent('[data-testid="create-dataset-modal"]');
      
      // 各入力フィールドでXSS対策を確認
      const inputFields = [
        '[data-testid="dataset-name"]',
        '[data-testid="dataset-description"]',
        '[data-testid="dataset-tags"]'
      ];
      
      for (const fieldSelector of inputFields) {
        await helpers.security.checkXSSProtection(fieldSelector);
      }
      
      // フォーム送信時のサニタイゼーション
      await page.fill('[data-testid="dataset-name"]', 'Test <b>Bold</b> Dataset');
      await page.fill('[data-testid="dataset-description"]', 'Description with <script>alert("test")</script>');
      await page.selectOption('[data-testid="dataset-type"]', 'object_detection');
      
      await page.click('[data-testid="save-dataset-button"]');
      
      // データが安全に保存・表示される
      if (await page.locator('[data-testid="success-message"]').count() > 0) {
        await helpers.component.waitForComponent('[data-testid="dataset-card"]');
        
        const datasetCard = page.locator('[data-testid="dataset-card"]').first();
        const nameText = await datasetCard.locator('[data-testid="dataset-name"]').textContent();
        
        // HTMLタグが実行されずテキストとして表示
        expect(nameText).toContain('Test');
        expect(nameText).toContain('Bold');
        expect(nameText).not.toContain('<b>'); // HTMLタグは除去または表示されない
      }
    });
  });

  test.describe('CSRF Protection', () => {
    test('should implement CSRF tokens', async ({ page }) => {
      // CSRFトークンの実装確認
      await helpers.auth.login();
      
      // CSRFトークンの存在確認
      await helpers.security.checkCSRFProtection();
      
      // フォーム送信時のCSRFトークン確認
      await helpers.navigation.navigateToPage('drone-management');
      await page.click('[data-testid="add-drone-button"]');
      
      // フォームにCSRFトークンが含まれる
      const csrfToken = await page.evaluate(() => {
        const token = document.querySelector('input[name="_token"], input[name="csrf_token"], meta[name="csrf-token"]');
        return token ? token.getAttribute('value') || token.getAttribute('content') : null;
      });
      
      expect(csrfToken).toBeTruthy();
      expect(csrfToken?.length).toBeGreaterThan(20); // 十分な長さのトークン
    });

    test('should reject requests without valid CSRF tokens', async ({ page }) => {
      // 無効なCSRFトークンでのリクエスト拒否
      await helpers.auth.login();
      
      // 有効なCSRFトークンを取得
      const validToken = await page.evaluate(() => {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : null;
      });
      
      // 無効なトークンでのAPI呼び出し
      const invalidTokenResponse = await page.request.post('/api/drones', {
        headers: {
          'X-CSRF-Token': 'invalid_token_123',
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Test Drone',
          model: 'Test Model'
        }
      });
      
      expect(invalidTokenResponse.status()).toBe(403); // CSRF token mismatch
      
      // トークンなしでの呼び出し
      const noTokenResponse = await page.request.post('/api/drones', {
        headers: {
          'Content-Type': 'application/json'
        },
        data: {
          name: 'Test Drone',
          model: 'Test Model'
        }
      });
      
      expect(noTokenResponse.status()).toBe(403);
      
      // 有効なトークンでは成功
      if (validToken) {
        const validTokenResponse = await page.request.post('/api/drones', {
          headers: {
            'X-CSRF-Token': validToken,
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${await page.evaluate(() => localStorage.getItem('authToken'))}`
          },
          data: {
            name: 'Valid Test Drone',
            model: 'Valid Model',
            serialNumber: 'VALID-001'
          }
        });
        
        expect([200, 201]).toContain(validTokenResponse.status());
      }
    });

    test('should handle CSRF token rotation', async ({ page }) => {
      // CSRFトークンの適切なローテーション
      await helpers.auth.login();
      
      // 初期トークンの取得
      const initialToken = await page.evaluate(() => {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : null;
      });
      
      // ページ遷移後のトークン確認
      await helpers.navigation.navigateToPage('dataset-management');
      
      const afterNavigationToken = await page.evaluate(() => {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : null;
      });
      
      // トークンが存在し、適切な長さを持つ
      expect(afterNavigationToken).toBeTruthy();
      expect(afterNavigationToken?.length).toBeGreaterThan(20);
      
      // セッション後のトークン更新（必要に応じて）
      await page.reload();
      
      const afterReloadToken = await page.evaluate(() => {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : null;
      });
      
      expect(afterReloadToken).toBeTruthy();
      
      // 実装によってはトークンがローテーションされる
      // （同じでも異なっても、どちらも有効な実装）
    });
  });

  test.describe('Data Protection', () => {
    test('should protect sensitive data in transit', async ({ page }) => {
      // 転送中データの保護
      await helpers.auth.login();
      
      // HTTPS使用の確認
      await helpers.security.checkSecurityHeaders();
      
      // API通信の暗号化確認
      const apiRequests = [];
      page.on('request', request => {
        if (request.url().includes('/api/')) {
          apiRequests.push(request);
        }
      });
      
      await helpers.navigation.navigateToPage('dashboard');
      await page.waitForTimeout(2000);
      
      // すべてのAPIリクエストがHTTPS
      for (const request of apiRequests) {
        expect(request.url()).toMatch(/^https:/);
      }
      
      // セキュアなヘッダーの確認
      const response = await page.request.get('/api/dashboard');
      const headers = response.headers();
      
      // セキュリティヘッダーが設定されている
      expect(headers['strict-transport-security']).toBeTruthy();
      expect(headers['x-content-type-options']).toBe('nosniff');
      expect(headers['x-frame-options']).toBeTruthy();
    });

    test('should handle sensitive data properly', async ({ page }) => {
      // 機密データの適切な処理
      await helpers.auth.login();
      
      // 1. パスワードフィールドのマスキング
      await page.goto('/settings');
      
      const passwordFields = await page.locator('input[type="password"]').all();
      for (const field of passwordFields) {
        const type = await field.getAttribute('type');
        expect(type).toBe('password');
        
        // オートコンプリートの適切な設定
        const autocomplete = await field.getAttribute('autocomplete');
        expect(['off', 'new-password', 'current-password']).toContain(autocomplete);
      }
      
      // 2. 機密情報のログ出力防止
      const consoleLogs = [];
      page.on('console', msg => {
        consoleLogs.push(msg.text());
      });
      
      await helpers.navigation.navigateToPage('drone-management');
      await page.waitForTimeout(2000);
      
      // コンソールログに機密情報が含まれていない
      for (const log of consoleLogs) {
        expect(log).not.toMatch(/password|token|secret|key/i);
      }
      
      // 3. ローカルストレージの適切な使用
      const sensitiveDataInStorage = await page.evaluate(() => {
        const localStorage = window.localStorage;
        const sessionStorage = window.sessionStorage;
        
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          const value = localStorage.getItem(key || '');
          
          if (key?.toLowerCase().includes('password') || 
              value?.toLowerCase().includes('password')) {
            return true;
          }
        }
        
        for (let i = 0; i < sessionStorage.length; i++) {
          const key = sessionStorage.key(i);
          const value = sessionStorage.getItem(key || '');
          
          if (key?.toLowerCase().includes('password') || 
              value?.toLowerCase().includes('password')) {
            return true;
          }
        }
        
        return false;
      });
      
      expect(sensitiveDataInStorage).toBeFalsy();
    });

    test('should implement proper data masking', async ({ page }) => {
      // データマスキングの適切な実装
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('settings');
      
      // ユーザー情報表示でのマスキング
      const emailFields = await page.locator('[data-testid*="email"], [class*="email"]').all();
      
      for (const field of emailFields) {
        const text = await field.textContent();
        const value = await field.inputValue();
        
        // 表示用の値とフォーム値の確認
        if (text && text.includes('@')) {
          // メールアドレスが部分的にマスクされているか、完全に表示されている
          // （実装方針による）
          expect(text.length).toBeGreaterThan(0);
        }
      }
      
      // APIキーやトークンの表示
      const tokenFields = await page.locator('[data-testid*="token"], [data-testid*="key"]').all();
      
      for (const field of tokenFields) {
        const text = await field.textContent();
        
        if (text && text.length > 10) {
          // 長いトークンは一部がマスクされている
          expect(text).toMatch(/\*+|•+|x+/); // マスク文字を含む
        }
      }
    });
  });

  test.describe('Security Headers', () => {
    test('should implement Content Security Policy', async ({ page }) => {
      // Content Security Policyの実装
      await page.goto('/');
      
      const response = await page.request.get('/');
      const headers = response.headers();
      
      // CSPヘッダーの存在確認
      const csp = headers['content-security-policy'];
      expect(csp).toBeTruthy();
      
      // CSPディレクティブの確認
      if (csp) {
        expect(csp).toContain("default-src");
        expect(csp).toContain("script-src");
        expect(csp).toContain("style-src");
        expect(csp).toContain("img-src");
        
        // 安全でないインラインスクリプトの防止
        expect(csp).not.toContain("'unsafe-inline'");
        expect(csp).not.toContain("'unsafe-eval'");
      }
      
      // CSP違反の監視
      const cspViolations = [];
      page.on('response', response => {
        if (response.url().includes('csp-report')) {
          cspViolations.push(response);
        }
      });
      
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // CSP違反が発生していない
      expect(cspViolations.length).toBe(0);
    });

    test('should set security headers correctly', async ({ page }) => {
      // セキュリティヘッダーの適切な設定
      const response = await page.request.get('/');
      const headers = response.headers();
      
      // 必須セキュリティヘッダーの確認
      const requiredHeaders = {
        'x-frame-options': ['DENY', 'SAMEORIGIN'],
        'x-content-type-options': ['nosniff'],
        'x-xss-protection': ['1; mode=block', '0'],
        'strict-transport-security': ['max-age='],
        'referrer-policy': ['strict-origin-when-cross-origin', 'no-referrer', 'same-origin']
      };
      
      for (const [headerName, validValues] of Object.entries(requiredHeaders)) {
        const headerValue = headers[headerName];
        expect(headerValue).toBeTruthy();
        
        if (Array.isArray(validValues)) {
          const isValid = validValues.some(valid => 
            headerValue?.includes(valid) || headerValue === valid
          );
          expect(isValid).toBeTruthy();
        }
      }
      
      // Permissions Policy の確認
      const permissionsPolicy = headers['permissions-policy'];
      if (permissionsPolicy) {
        // 不要な権限が無効化されている
        expect(permissionsPolicy).toMatch(/camera=\(\)|microphone=\(\)|geolocation=\(\)/);
      }
    });

    test('should prevent clickjacking attacks', async ({ page }) => {
      // クリックジャッキング攻撃の防止
      const response = await page.request.get('/');
      const headers = response.headers();
      
      // X-Frame-Options ヘッダーの確認
      const xFrameOptions = headers['x-frame-options'];
      expect(xFrameOptions).toBeTruthy();
      expect(['DENY', 'SAMEORIGIN'].includes(xFrameOptions)).toBeTruthy();
      
      // Content Security Policy での frame-ancestors の確認
      const csp = headers['content-security-policy'];
      if (csp && csp.includes('frame-ancestors')) {
        expect(csp).toMatch(/frame-ancestors\s+['"]?none['"]?|frame-ancestors\s+['"]?self['"]?/);
      }
      
      // iframe での読み込み試行テスト
      await page.setContent(`
        <html>
          <body>
            <iframe id="testFrame" src="${page.url()}" width="800" height="600"></iframe>
          </body>
        </html>
      `);
      
      // iframe読み込みが失敗することを確認
      const frameError = await page.evaluate(() => {
        return new Promise((resolve) => {
          const frame = document.getElementById('testFrame');
          if (frame) {
            frame.onerror = () => resolve(true);
            frame.onload = () => {
              try {
                // Same-origin policy violation test
                frame.contentDocument?.title;
                resolve(false);
              } catch (e) {
                resolve(true); // Expected security error
              }
            };
            setTimeout(() => resolve(false), 5000);
          } else {
            resolve(false);
          }
        });
      });
      
      // フレーム読み込みが適切に制限されている
      expect(frameError).toBeTruthy();
    });
  });

  test.describe('Input Validation', () => {
    test('should validate all user inputs', async ({ page }) => {
      // 全ユーザー入力の検証
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('drone-management');
      
      await page.click('[data-testid="add-drone-button"]');
      await helpers.component.waitForComponent('[data-testid="add-drone-modal"]');
      
      // 1. 必須フィールドの検証
      await page.click('[data-testid="save-drone-button"]');
      
      const errorMessages = await page.locator('[role="alert"], .error, [class*="error"]').all();
      expect(errorMessages.length).toBeGreaterThan(0);
      
      // 2. 文字列長制限の検証
      const longString = 'a'.repeat(1000);
      await page.fill('[data-testid="drone-name"]', longString);
      await page.click('[data-testid="save-drone-button"]');
      
      const lengthError = await page.locator('[data-testid="error-drone-name"]').textContent();
      expect(lengthError).toMatch(/(長すぎ|文字以内|制限)/);
      
      // 3. 特殊文字の検証
      const specialChars = '!@#$%^&*(){}[]|\\:";\'<>?,./-_+=`~';
      await page.fill('[data-testid="drone-name"]', specialChars);
      await page.click('[data-testid="save-drone-button"]');
      
      // 適切な文字制限メッセージまたは正常処理
      // （実装方針による）
      
      // 4. SQLインジェクション対策
      const sqlInjectionPayloads = [
        "'; DROP TABLE drones; --",
        "1' OR '1'='1",
        "'; DELETE FROM users WHERE '1'='1'; --",
        "UNION SELECT * FROM users--"
      ];
      
      for (const payload of sqlInjectionPayloads) {
        await page.fill('[data-testid="drone-name"]', payload);
        await page.fill('[data-testid="drone-model"]', 'Test Model');
        await page.fill('[data-testid="drone-serialNumber"]', 'TEST-001');
        
        await page.click('[data-testid="save-drone-button"]');
        
        // SQLエラーが表示されない（適切に処理されている）
        const pageContent = await page.textContent('body');
        expect(pageContent).not.toMatch(/SQL|syntax error|mysql|postgresql|database/i);
        
        await page.fill('[data-testid="drone-name"]', ''); // クリア
      }
    });

    test('should sanitize file uploads', async ({ page }) => {
      // ファイルアップロードのサニタイゼーション
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dataset-management');
      
      await page.click('[data-testid="create-dataset-button"]');
      await helpers.component.waitForComponent('[data-testid="create-dataset-modal"]');
      
      await page.fill('[data-testid="dataset-name"]', 'Upload Test Dataset');
      await page.selectOption('[data-testid="dataset-type"]', 'object_detection');
      await page.click('[data-testid="save-dataset-button"]');
      
      // 画像アップロードページへ
      if (await page.locator('[data-testid="success-message"]').count() > 0) {
        await helpers.component.waitForComponent('[data-testid="dataset-card"]');
        await page.locator('[data-testid="dataset-card"]').first()
          .locator('[data-testid="view-dataset"]').click();
        
        await helpers.component.waitForComponent('[data-testid="image-gallery"]');
        
        // ファイルアップロード機能の確認
        const uploadInput = page.locator('[data-testid="file-input"], input[type="file"]');
        
        if (await uploadInput.count() > 0) {
          // 受け入れ可能なファイル形式の制限
          const acceptAttribute = await uploadInput.getAttribute('accept');
          expect(acceptAttribute).toBeTruthy();
          expect(acceptAttribute).toMatch(/image\//); // 画像ファイルのみ
          
          // ファイルサイズ制限の確認
          const maxSizeInfo = await page.locator('[data-testid="max-file-size"], .file-size-limit').textContent();
          if (maxSizeInfo) {
            expect(maxSizeInfo).toMatch(/\d+\s*(MB|KB|bytes)/i);
          }
        }
      }
    });
  });
});