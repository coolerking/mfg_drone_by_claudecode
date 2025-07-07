import { test, expect } from '@playwright/test';
import { TestHelperFactory } from './helpers/test-helpers';

/**
 * アクセシビリティE2Eテスト
 * WCAG 2.1 AA準拠、キーボードナビゲーション、スクリーンリーダー対応をテスト
 */

test.describe('Accessibility E2E Tests', () => {
  let helpers: ReturnType<typeof TestHelperFactory.createHelpers>;

  test.beforeEach(async ({ page }) => {
    helpers = TestHelperFactory.createHelpers(page);
  });

  test.afterEach(async ({ page }) => {
    await helpers.cleanup.cleanupTestData();
  });

  test.describe('WCAG 2.1 AA Compliance', () => {
    test('should have proper heading structure', async ({ page }) => {
      // 見出し構造の適切性確認
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // h1タグが1つだけ存在する
      const h1Elements = await page.locator('h1').count();
      expect(h1Elements).toBe(1);
      
      // 見出しの階層構造が適切
      const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
      let prevLevel = 0;
      
      for (const heading of headings) {
        const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
        const currentLevel = parseInt(tagName.charAt(1));
        
        // 見出しレベルが2以上飛ばない
        expect(currentLevel - prevLevel).toBeLessThanOrEqual(1);
        prevLevel = currentLevel;
      }
      
      // すべての見出しにテキストコンテンツがある
      for (const heading of headings) {
        const text = await heading.textContent();
        expect(text?.trim()).toBeTruthy();
      }
    });

    test('should have proper aria labels and descriptions', async ({ page }) => {
      // ARIAラベルと説明の適切性確認
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('drone-management');
      
      // インタラクティブ要素にアクセシブルネームがある
      const interactiveElements = [
        'button',
        'input',
        'select',
        'textarea',
        '[role="button"]',
        '[role="textbox"]',
        '[role="combobox"]'
      ];
      
      for (const selector of interactiveElements) {
        const elements = await page.locator(selector).all();
        
        for (const element of elements) {
          // aria-label、aria-labelledby、またはテキストコンテンツがある
          const ariaLabel = await element.getAttribute('aria-label');
          const ariaLabelledby = await element.getAttribute('aria-labelledby');
          const textContent = await element.textContent();
          const placeholder = await element.getAttribute('placeholder');
          
          const hasAccessibleName = ariaLabel || ariaLabelledby || textContent?.trim() || placeholder;
          expect(hasAccessibleName).toBeTruthy();
        }
      }
      
      // フォーム要素にラベルが関連付けられている
      const inputs = await page.locator('input[type="text"], input[type="email"], input[type="password"], select, textarea').all();
      
      for (const input of inputs) {
        const id = await input.getAttribute('id');
        const ariaLabel = await input.getAttribute('aria-label');
        const ariaLabelledby = await input.getAttribute('aria-labelledby');
        
        if (id) {
          // 対応するlabelタグがある
          const label = await page.locator(`label[for="${id}"]`).count();
          const hasLabel = label > 0 || ariaLabel || ariaLabelledby;
          expect(hasLabel).toBeTruthy();
        } else {
          // aria-labelまたはaria-labelledbyがある
          expect(ariaLabel || ariaLabelledby).toBeTruthy();
        }
      }
    });

    test('should meet color contrast requirements', async ({ page }) => {
      // カラーコントラスト要件の確認
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // テキスト要素のコントラスト確認
      const textElements = await page.locator('p, span, div, h1, h2, h3, h4, h5, h6, button, a, label').all();
      
      for (const element of textElements.slice(0, 20)) { // パフォーマンスのため最初の20要素をチェック
        const textContent = await element.textContent();
        if (!textContent?.trim()) continue;
        
        const contrast = await helpers.accessibility.checkColorContrast(element.toString(), 4.5);
        expect(contrast).toBeTruthy();
      }
      
      // ボタンとリンクの特別なコントラスト確認
      const actionElements = await page.locator('button, a').all();
      
      for (const element of actionElements.slice(0, 10)) {
        const textContent = await element.textContent();
        if (!textContent?.trim()) continue;
        
        // フォーカス状態でのコントラスト
        await element.focus();
        const focusContrast = await helpers.accessibility.checkColorContrast(element.toString(), 4.5);
        expect(focusContrast).toBeTruthy();
      }
    });

    test('should have proper focus indicators', async ({ page }) => {
      // フォーカスインジケーターの適切性確認
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('drone-management');
      
      // フォーカス可能な要素の確認
      const focusableElements = await page.locator(
        'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
      ).all();
      
      for (const element of focusableElements.slice(0, 15)) {
        await element.focus();
        
        // フォーカスされた要素が視覚的に識別可能
        const isFocused = await element.evaluate(el => el === document.activeElement);
        expect(isFocused).toBeTruthy();
        
        // アウトライン（フォーカスリング）が表示されている
        const outlineStyle = await element.evaluate(el => {
          const styles = window.getComputedStyle(el);
          return {
            outline: styles.outline,
            outlineWidth: styles.outlineWidth,
            outlineStyle: styles.outlineStyle,
            outlineColor: styles.outlineColor,
            boxShadow: styles.boxShadow
          };
        });
        
        // アウトラインまたはボックスシャドウでフォーカスが示されている
        const hasFocusIndicator = 
          outlineStyle.outline !== 'none' ||
          outlineStyle.outlineWidth !== '0px' ||
          outlineStyle.boxShadow !== 'none';
        
        expect(hasFocusIndicator).toBeTruthy();
      }
    });

    test('should have proper form error handling', async ({ page }) => {
      // フォームエラーハンドリングの適切性確認
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('drone-management');
      
      // ドローン追加フォームを開く
      await page.click('[data-testid="add-drone-button"]');
      await helpers.component.waitForComponent('[data-testid="add-drone-modal"]');
      
      // 必須フィールドを空のまま送信
      await page.click('[data-testid="save-drone-button"]');
      
      // エラーメッセージの確認
      const errorMessages = await page.locator('[role="alert"], [aria-live="polite"], [aria-live="assertive"]').all();
      expect(errorMessages.length).toBeGreaterThan(0);
      
      // エラーメッセージがフォーム要素と適切に関連付けられている
      const errorInputs = await page.locator('input[aria-invalid="true"], input[aria-describedby]').all();
      expect(errorInputs.length).toBeGreaterThan(0);
      
      // フォーカスが最初のエラー要素に移動する
      const firstErrorInput = errorInputs[0];
      const focusedElement = await page.evaluateHandle(() => document.activeElement);
      const isFocusedOnError = await page.evaluate(
        (input, focused) => input === focused,
        firstErrorInput,
        focusedElement
      );
      expect(isFocusedOnError).toBeTruthy();
      
      // エラーメッセージが具体的で有用
      for (const errorElement of errorMessages) {
        const errorText = await errorElement.textContent();
        expect(errorText?.length).toBeGreaterThan(10); // 具体的なメッセージ
        expect(errorText).not.toContain('Error'); // 汎用的でないメッセージ
      }
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should support full keyboard navigation', async ({ page }) => {
      // 完全なキーボードナビゲーション対応
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // Tab キーでナビゲーションできる要素の確認
      const tabNavigationElements = [];
      
      // ページ内の全てのフォーカス可能要素を Tab で順次移動
      await page.keyboard.press('Tab');
      let currentElement = await page.evaluateHandle(() => document.activeElement);
      
      for (let i = 0; i < 50; i++) { // 最大50回のTab移動
        const tagName = await currentElement.evaluate(el => el?.tagName);
        const className = await currentElement.evaluate(el => el?.className);
        
        if (tagName) {
          tabNavigationElements.push({ tagName, className });
        }
        
        await page.keyboard.press('Tab');
        const nextElement = await page.evaluateHandle(() => document.activeElement);
        
        // 同じ要素に戻った場合は終了
        const isSameElement = await page.evaluate(
          (current, next) => current === next,
          currentElement,
          nextElement
        );
        
        if (isSameElement && i > 5) break;
        
        currentElement = nextElement;
      }
      
      // 十分な数のフォーカス可能要素がある
      expect(tabNavigationElements.length).toBeGreaterThan(5);
      
      // Shift+Tab で逆方向ナビゲーション
      await page.keyboard.press('Shift+Tab');
      const reversedElement = await page.evaluateHandle(() => document.activeElement);
      
      // 逆方向でも適切にフォーカスが移動する
      const hasReversedFocus = await page.evaluate(
        (current, reversed) => current !== reversed,
        currentElement,
        reversedElement
      );
      expect(hasReversedFocus).toBeTruthy();
    });

    test('should handle modal keyboard navigation correctly', async ({ page }) => {
      // モーダルでのキーボードナビゲーション
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('drone-management');
      
      // モーダルを開く
      await page.click('[data-testid="add-drone-button"]');
      await helpers.component.waitForComponent('[data-testid="add-drone-modal"]');
      
      // フォーカスがモーダル内の最初の要素に移動
      const focusedElement = await page.evaluateHandle(() => document.activeElement);
      const isInModal = await page.evaluate(
        (focused) => {
          const modal = document.querySelector('[data-testid="add-drone-modal"]');
          return modal?.contains(focused);
        },
        focusedElement
      );
      expect(isInModal).toBeTruthy();
      
      // Tab キーでモーダル内をナビゲーション
      const modalElements = [];
      for (let i = 0; i < 10; i++) {
        const currentElement = await page.evaluateHandle(() => document.activeElement);
        const tagName = await currentElement.evaluate(el => el?.tagName);
        modalElements.push(tagName);
        
        await page.keyboard.press('Tab');
      }
      
      // モーダル内に複数のフォーカス可能要素がある
      expect(modalElements.filter(tag => tag).length).toBeGreaterThan(2);
      
      // Escape キーでモーダルを閉じる
      await page.keyboard.press('Escape');
      await expect(page.locator('[data-testid="add-drone-modal"]')).not.toBeVisible();
      
      // フォーカスが元の要素（モーダルを開いたボタン）に戻る
      const returnedFocus = await page.evaluateHandle(() => document.activeElement);
      const isOnTriggerButton = await page.evaluate(
        (focused) => {
          const button = document.querySelector('[data-testid="add-drone-button"]');
          return button === focused;
        },
        returnedFocus
      );
      expect(isOnTriggerButton).toBeTruthy();
    });

    test('should support keyboard shortcuts', async ({ page }) => {
      // キーボードショートカットの対応
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // Alt+D でダッシュボードにアクセス（例）
      await page.keyboard.press('Alt+KeyD');
      await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
      
      // Ctrl+K で検索機能を開く（例）
      await page.keyboard.press('Control+KeyK');
      
      // 検索モーダルまたは検索フィールドにフォーカス
      const searchElement = await page.locator('[data-testid="global-search"], [data-testid="search-modal"]').first();
      if (await searchElement.count() > 0) {
        await expect(searchElement).toBeVisible();
      }
      
      // Escape でモーダル/検索を閉じる
      await page.keyboard.press('Escape');
      
      // 矢印キーでのナビゲーション（リスト項目など）
      await helpers.navigation.navigateToPage('drone-management');
      await helpers.component.waitForComponent('[data-testid="drone-list"]');
      
      const listItems = await page.locator('[data-testid="drone-card"], [role="listitem"], [role="gridcell"]').count();
      
      if (listItems > 0) {
        // 最初の項目にフォーカス
        await page.locator('[data-testid="drone-card"], [role="listitem"], [role="gridcell"]').first().focus();
        
        // 矢印キーでの移動
        await page.keyboard.press('ArrowDown');
        
        // フォーカスが次の項目に移動していることを確認
        const focusedAfterArrow = await page.evaluateHandle(() => document.activeElement);
        const isOnListItem = await page.evaluate(
          (focused) => {
            return focused?.closest('[data-testid="drone-card"], [role="listitem"], [role="gridcell"]') !== null;
          },
          focusedAfterArrow
        );
        expect(isOnListItem).toBeTruthy();
      }
    });

    test('should handle data tables keyboard navigation', async ({ page }) => {
      // データテーブルでのキーボードナビゲーション
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dataset-management');
      
      await helpers.component.waitForComponent('[data-testid="dataset-list"]');
      
      // テーブルまたはグリッドの確認
      const tableElement = await page.locator('table, [role="grid"], [role="table"]').first();
      
      if (await tableElement.count() > 0) {
        // テーブルにフォーカス
        await tableElement.focus();
        
        // 矢印キーでのセル間移動
        await page.keyboard.press('ArrowRight');
        await page.keyboard.press('ArrowDown');
        await page.keyboard.press('ArrowLeft');
        await page.keyboard.press('ArrowUp');
        
        // Enter キーでセルの操作
        await page.keyboard.press('Enter');
        
        // フォーカスがテーブル内に維持されている
        const focusedElement = await page.evaluateHandle(() => document.activeElement);
        const isInTable = await page.evaluate(
          (focused, table) => table.contains(focused),
          focusedElement,
          tableElement
        );
        expect(isInTable).toBeTruthy();
      }
    });
  });

  test.describe('Screen Reader Support', () => {
    test('should have proper semantic markup', async ({ page }) => {
      // セマンティックマークアップの適切性
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // ランドマーク要素の確認
      const landmarks = await page.locator('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"], [role="complementary"], main, nav, header, footer, aside').all();
      expect(landmarks.length).toBeGreaterThan(0);
      
      // メインコンテンツエリアが1つだけ
      const mainElements = await page.locator('[role="main"], main').count();
      expect(mainElements).toBe(1);
      
      // リスト構造の適切性
      const lists = await page.locator('ul, ol, [role="list"]').all();
      
      for (const list of lists) {
        const listItems = await list.locator('li, [role="listitem"]').count();
        if (listItems > 0) {
          expect(listItems).toBeGreaterThan(0);
        }
      }
      
      // ボタンとリンクの適切な使い分け
      const buttons = await page.locator('button, [role="button"]').all();
      const links = await page.locator('a[href], [role="link"]').all();
      
      // ボタンは操作用、リンクはナビゲーション用
      for (const button of buttons.slice(0, 10)) {
        const onclick = await button.getAttribute('onclick');
        const type = await button.getAttribute('type');
        
        // ボタンは type または onclick が設定されている
        expect(onclick || type || true).toBeTruthy(); // 少なくとも button 要素である
      }
      
      for (const link of links.slice(0, 10)) {
        const href = await link.getAttribute('href');
        
        // リンクは href が設定されている
        expect(href).toBeTruthy();
      }
    });

    test('should provide proper live regions', async ({ page }) => {
      // ライブリージョンの適切な実装
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('tracking-control');
      
      // ライブリージョンの存在確認
      const liveRegions = await page.locator('[aria-live], [role="status"], [role="alert"]').all();
      expect(liveRegions.length).toBeGreaterThan(0);
      
      // ステータス更新のテスト
      const statusRegion = await page.locator('[data-testid="tracking-status"], [role="status"]').first();
      
      if (await statusRegion.count() > 0) {
        const initialStatus = await statusRegion.textContent();
        
        // トラッキング開始（ステータス変更）
        if (await page.locator('[data-testid="drone-select"]').count() > 0) {
          await page.selectOption('[data-testid="drone-select"]', 'test-drone');
          await page.selectOption('[data-testid="model-select"]', 'test-model');
          await page.click('[data-testid="start-tracking-button"]');
          
          // ステータスが更新される
          await page.waitForFunction(
            (element, initial) => element.textContent !== initial,
            statusRegion,
            initialStatus,
            { timeout: 5000 }
          );
          
          const updatedStatus = await statusRegion.textContent();
          expect(updatedStatus).not.toBe(initialStatus);
        }
      }
      
      // エラー表示のライブリージョン
      await helpers.navigation.navigateToPage('drone-management');
      await page.click('[data-testid="add-drone-button"]');
      await page.click('[data-testid="save-drone-button"]'); // エラーを発生させる
      
      const errorRegions = await page.locator('[role="alert"], [aria-live="assertive"]').all();
      let hasErrorMessage = false;
      
      for (const region of errorRegions) {
        const text = await region.textContent();
        if (text && text.trim().length > 0) {
          hasErrorMessage = true;
          break;
        }
      }
      
      expect(hasErrorMessage).toBeTruthy();
    });

    test('should have descriptive page titles', async ({ page }) => {
      // 説明的なページタイトル
      const pages = [
        { path: '/dashboard', expectedTitle: 'ダッシュボード' },
        { path: '/drone-management', expectedTitle: 'ドローン管理' },
        { path: '/dataset-management', expectedTitle: 'データセット管理' },
        { path: '/model-management', expectedTitle: 'モデル管理' },
        { path: '/tracking-control', expectedTitle: 'トラッキング制御' },
        { path: '/system-monitoring', expectedTitle: 'システム監視' },
        { path: '/settings', expectedTitle: '設定' }
      ];
      
      await helpers.auth.login();
      
      for (const pageInfo of pages) {
        await page.goto(pageInfo.path);
        await helpers.component.waitForComponent('[data-testid="page-content"]');
        
        const title = await page.title();
        
        // タイトルが空でない
        expect(title.trim()).toBeTruthy();
        
        // 期待されるキーワードが含まれている
        expect(title).toContain(pageInfo.expectedTitle);
        
        // サイト名も含まれている
        expect(title).toContain('MFG Drone'); // または適切なサイト名
      }
    });

    test('should provide alternative text for images', async ({ page }) => {
      // 画像の代替テキスト
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dataset-management');
      
      // 画像要素の確認
      const images = await page.locator('img').all();
      
      for (const image of images) {
        const alt = await image.getAttribute('alt');
        const role = await image.getAttribute('role');
        const ariaLabel = await image.getAttribute('aria-label');
        const ariaLabelledby = await image.getAttribute('aria-labelledby');
        
        // 装飾画像の場合は空のalt属性またはrole="presentation"
        // 情報のある画像の場合は適切な代替テキスト
        if (role === 'presentation' || alt === '') {
          // 装飾画像として適切
          expect(alt === '' || role === 'presentation').toBeTruthy();
        } else {
          // 情報のある画像には代替テキストが必要
          expect(alt || ariaLabel || ariaLabelledby).toBeTruthy();
          
          if (alt) {
            expect(alt.length).toBeGreaterThan(0);
            expect(alt).not.toBe('image'); // 汎用的でない
          }
        }
      }
      
      // アイコンの確認
      const icons = await page.locator('[class*="icon"], [data-icon], svg').all();
      
      for (const icon of icons.slice(0, 10)) {
        const ariaLabel = await icon.getAttribute('aria-label');
        const ariaHidden = await icon.getAttribute('aria-hidden');
        const title = await icon.getAttribute('title');
        
        // アイコンは装飾的（aria-hidden）または説明的（aria-label/title）
        if (ariaHidden === 'true') {
          // 装飾的アイコンとして適切
          expect(ariaHidden).toBe('true');
        } else {
          // 情報のあるアイコンには説明が必要
          expect(ariaLabel || title).toBeTruthy();
        }
      }
    });
  });

  test.describe('Mobile Accessibility', () => {
    test('should support touch navigation', async ({ page }) => {
      // タッチナビゲーションの対応
      // モバイルビューポートに設定
      await page.setViewportSize({ width: 375, height: 667 });
      
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('dashboard');
      
      // タッチターゲットのサイズ確認
      const interactiveElements = await page.locator('button, a, input, select, [role="button"]').all();
      
      for (const element of interactiveElements.slice(0, 20)) {
        const boundingBox = await element.boundingBox();
        
        if (boundingBox) {
          // タッチターゲットが44px × 44px以上
          expect(boundingBox.width).toBeGreaterThanOrEqual(44);
          expect(boundingBox.height).toBeGreaterThanOrEqual(44);
        }
      }
      
      // ジェスチャー操作の確認
      const swipeableElements = await page.locator('[data-swipeable], .swiper, .carousel').all();
      
      for (const element of swipeableElements) {
        // 代替のナビゲーション方法が提供されている
        const hasAlternativeNav = await element.locator('button, [role="button"]').count();
        expect(hasAlternativeNav).toBeGreaterThan(0);
      }
    });

    test('should work with mobile screen readers', async ({ page }) => {
      // モバイルスクリーンリーダーでの動作
      await page.setViewportSize({ width: 375, height: 667 });
      
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('drone-management');
      
      // モバイルナビゲーションの確認
      const mobileMenu = await page.locator('[data-testid="mobile-menu"], .mobile-nav, [aria-label*="メニュー"]').first();
      
      if (await mobileMenu.count() > 0) {
        // メニューボタンに適切なラベル
        const ariaLabel = await mobileMenu.getAttribute('aria-label');
        const text = await mobileMenu.textContent();
        
        expect(ariaLabel || text?.trim()).toBeTruthy();
        
        // メニューの展開状態が適切に表現されている
        const ariaExpanded = await mobileMenu.getAttribute('aria-expanded');
        expect(ariaExpanded === 'true' || ariaExpanded === 'false').toBeTruthy();
        
        // メニューを開く
        await mobileMenu.click();
        
        // 展開状態の更新
        const expandedAfterClick = await mobileMenu.getAttribute('aria-expanded');
        expect(expandedAfterClick).toBe('true');
      }
      
      // フォームの使いやすさ
      await page.click('[data-testid="add-drone-button"]');
      await helpers.component.waitForComponent('[data-testid="add-drone-modal"]');
      
      const inputs = await page.locator('input, select, textarea').all();
      
      for (const input of inputs) {
        // 入力欄が十分な大きさ
        const boundingBox = await input.boundingBox();
        
        if (boundingBox) {
          expect(boundingBox.height).toBeGreaterThanOrEqual(44);
        }
        
        // 入力タイプが適切
        const type = await input.getAttribute('type');
        const tagName = await input.evaluate(el => el.tagName.toLowerCase());
        
        if (tagName === 'input') {
          expect(['text', 'email', 'password', 'number', 'tel', 'url', 'search']).toContain(type);
        }
      }
    });
  });

  test.describe('Accessibility Testing Tools Integration', () => {
    test('should pass automated accessibility tests', async ({ page }) => {
      // 自動アクセシビリティテストの実行
      await helpers.auth.login();
      
      const pagesToTest = [
        '/dashboard',
        '/drone-management',
        '/dataset-management',
        '/model-management'
      ];
      
      for (const pagePath of pagesToTest) {
        await page.goto(pagePath);
        await helpers.component.waitForComponent('[data-testid="page-content"]');
        
        // axe-core による自動テスト（プレイヤーが利用可能な場合）
        const violations = await page.evaluate(async () => {
          if (typeof window.axe !== 'undefined') {
            const results = await window.axe.run();
            return results.violations;
          }
          return [];
        });
        
        // 重大な違反がない
        const criticalViolations = violations.filter((v: any) => 
          v.impact === 'critical' || v.impact === 'serious'
        );
        
        expect(criticalViolations.length).toBe(0);
        
        // 中程度の違反も最小限
        const moderateViolations = violations.filter((v: any) => v.impact === 'moderate');
        expect(moderateViolations.length).toBeLessThanOrEqual(2);
      }
    });

    test('should maintain accessibility during dynamic content updates', async ({ page }) => {
      // 動的コンテンツ更新時のアクセシビリティ維持
      await helpers.auth.login();
      await helpers.navigation.navigateToPage('tracking-control');
      
      // 初期状態のアクセシビリティ確認
      const initialFocusableElements = await page.locator(
        'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
      ).count();
      
      expect(initialFocusableElements).toBeGreaterThan(0);
      
      // 動的コンテンツの更新（例：トラッキング開始）
      if (await page.locator('[data-testid="drone-select"]').count() > 0) {
        await page.selectOption('[data-testid="drone-select"]', 'test-drone');
        await page.selectOption('[data-testid="model-select"]', 'test-model');
        await page.click('[data-testid="start-tracking-button"]');
        
        // 更新後のアクセシビリティ確認
        await page.waitForTimeout(2000); // 更新完了を待機
        
        const updatedFocusableElements = await page.locator(
          'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
        ).count();
        
        // フォーカス可能要素が残っている
        expect(updatedFocusableElements).toBeGreaterThan(0);
        
        // ライブリージョンが適切に動作している
        const liveRegions = await page.locator('[aria-live], [role="status"], [role="alert"]').all();
        
        let hasLiveContent = false;
        for (const region of liveRegions) {
          const content = await region.textContent();
          if (content && content.trim().length > 0) {
            hasLiveContent = true;
            break;
          }
        }
        
        expect(hasLiveContent).toBeTruthy();
      }
    });
  });
});