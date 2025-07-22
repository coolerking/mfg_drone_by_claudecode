import { describe, it, expect } from '@jest/globals';
import {
  Validators,
  PresetValidators,
  CommonSecuritySchemas,
  AuthValidationSchemas,
  ApiKeyValidationSchemas,
  DroneControlValidationSchemas,
  SystemValidationSchemas,
} from '../validators.js';

describe('Validators', () => {
  describe('CommonSecuritySchemas', () => {
    describe('username', () => {
      it('有効なユーザー名を受け入れること', () => {
        const validUsernames = [
          'testuser',
          'test_user',
          'test-user',
          'user123',
          'USER123',
          'user_123-test',
        ];

        for (const username of validUsernames) {
          const result = Validators.validate(CommonSecuritySchemas.username, username);
          expect(result.success).toBe(true);
          expect(result.data).toBe(username);
        }
      });

      it('無効なユーザー名を拒否すること', () => {
        const invalidUsernames = [
          'ab', // 短すぎる
          'a'.repeat(51), // 長すぎる
          'user@domain', // @は無効
          'user.name', // .は無効
          'user name', // スペースは無効
          '123user!', // !は無効
        ];

        for (const username of invalidUsernames) {
          const result = Validators.validate(CommonSecuritySchemas.username, username);
          expect(result.success).toBe(false);
          expect(result.errors).toBeDefined();
        }
      });
    });

    describe('password', () => {
      it('強力なパスワードを受け入れること', () => {
        const validPasswords = [
          'Password123!',
          'MyStr0ng@Pass',
          'C0mpl3x#Pwd',
          'Secure$Pass1',
        ];

        for (const password of validPasswords) {
          const result = Validators.validate(CommonSecuritySchemas.password, password);
          expect(result.success).toBe(true);
        }
      });

      it('弱いパスワードを拒否すること', () => {
        const invalidPasswords = [
          'weak', // 短すぎる
          'password', // 大文字なし、数字なし、特殊文字なし
          'PASSWORD123', // 小文字なし、特殊文字なし
          'Password', // 数字なし、特殊文字なし
          'password123', // 大文字なし、特殊文字なし
          'Password!', // 数字なし
        ];

        for (const password of invalidPasswords) {
          const result = Validators.validate(CommonSecuritySchemas.password, password);
          expect(result.success).toBe(false);
        }
      });
    });

    describe('email', () => {
      it('有効なメールアドレスを受け入れること', () => {
        const validEmails = [
          'test@example.com',
          'user.name@example.org',
          'user+tag@example.co.jp',
          'user123@sub.example.com',
        ];

        for (const email of validEmails) {
          const result = Validators.validate(CommonSecuritySchemas.email, email);
          expect(result.success).toBe(true);
        }
      });

      it('無効なメールアドレスを拒否すること', () => {
        const invalidEmails = [
          'invalid-email',
          '@example.com',
          'user@',
          'user@.com',
          'user space@example.com',
        ];

        for (const email of invalidEmails) {
          const result = Validators.validate(CommonSecuritySchemas.email, email);
          expect(result.success).toBe(false);
        }
      });
    });

    describe('apiKeyName', () => {
      it('有効なAPIキー名を受け入れること', () => {
        const validNames = [
          'My API Key',
          'api-key-1',
          'test_key',
          'API Key 123',
          'production-key',
        ];

        for (const name of validNames) {
          const result = Validators.validate(CommonSecuritySchemas.apiKeyName, name);
          expect(result.success).toBe(true);
        }
      });

      it('無効なAPIキー名を拒否すること', () => {
        const invalidNames = [
          '', // 空文字
          'a'.repeat(101), // 長すぎる
          'key@special', // @は無効
          'key#with#hash', // #は無効
        ];

        for (const name of invalidNames) {
          const result = Validators.validate(CommonSecuritySchemas.apiKeyName, name);
          expect(result.success).toBe(false);
        }
      });
    });

    describe('permission', () => {
      it('有効な権限を受け入れること', () => {
        const validPermissions = [
          'drone:read',
          'drone:control',
          'drone:connect',
          'drone:emergency',
          'vision:read',
          'vision:process',
          'system:read',
          'system:write',
          'admin',
        ];

        for (const permission of validPermissions) {
          const result = Validators.validate(CommonSecuritySchemas.permission, permission);
          expect(result.success).toBe(true);
        }
      });

      it('無効な権限を拒否すること', () => {
        const invalidPermissions = [
          'invalid:permission',
          'drone:invalid',
          'unknown',
          'admin:super',
        ];

        for (const permission of invalidPermissions) {
          const result = Validators.validate(CommonSecuritySchemas.permission, permission);
          expect(result.success).toBe(false);
        }
      });
    });
  });

  describe('AuthValidationSchemas', () => {
    describe('login', () => {
      it('有効なログインデータを受け入れること', () => {
        const validLogin = {
          username: 'testuser',
          password: 'password123',
        };

        const result = Validators.validate(AuthValidationSchemas.login, validLogin);
        expect(result.success).toBe(true);
        expect(result.data).toEqual(validLogin);
      });

      it('無効なログインデータを拒否すること', () => {
        const invalidLogins = [
          { username: 'ab', password: 'pass' }, // ユーザー名が短すぎる
          { username: 'user', password: '' }, // パスワードが空
          { username: '', password: 'password' }, // ユーザー名が空
          {}, // 必須フィールドなし
        ];

        for (const login of invalidLogins) {
          const result = Validators.validate(AuthValidationSchemas.login, login);
          expect(result.success).toBe(false);
        }
      });
    });

    describe('register', () => {
      it('有効な登録データを受け入れること', () => {
        const validRegister = {
          username: 'newuser',
          password: 'NewPass123!',
          email: 'user@example.com',
          role: 'user' as const,
        };

        const result = Validators.validate(AuthValidationSchemas.register, validRegister);
        expect(result.success).toBe(true);
        expect(result.data).toEqual(validRegister);
      });

      it('デフォルト値を適用すること', () => {
        const minimalRegister = {
          username: 'newuser',
          password: 'NewPass123!',
        };

        const result = Validators.validate(AuthValidationSchemas.register, minimalRegister);
        expect(result.success).toBe(true);
        expect(result.data!.role).toBe('user'); // デフォルト値
      });
    });

    describe('changePassword', () => {
      it('有効なパスワード変更データを受け入れること', () => {
        const validChange = {
          currentPassword: 'OldPass123!',
          newPassword: 'NewPass456@',
          confirmPassword: 'NewPass456@',
        };

        const result = Validators.validate(AuthValidationSchemas.changePassword, validChange);
        expect(result.success).toBe(true);
      });

      it('パスワード不一致を拒否すること', () => {
        const invalidChange = {
          currentPassword: 'OldPass123!',
          newPassword: 'NewPass456@',
          confirmPassword: 'DifferentPass789#',
        };

        const result = Validators.validate(AuthValidationSchemas.changePassword, invalidChange);
        expect(result.success).toBe(false);
      });
    });
  });

  describe('ApiKeyValidationSchemas', () => {
    describe('create', () => {
      it('有効なAPIキー作成データを受け入れること', () => {
        const validCreate = {
          name: 'Test API Key',
          permissions: ['drone:read', 'vision:read'],
          expiresInDays: 30,
        };

        const result = Validators.validate(ApiKeyValidationSchemas.create, validCreate);
        expect(result.success).toBe(true);
      });

      it('権限の数制限を適用すること', () => {
        const tooManyPermissions = {
          name: 'Test Key',
          permissions: Array(15).fill('drone:read'), // 10個を超える
        };

        const result = Validators.validate(ApiKeyValidationSchemas.create, tooManyPermissions);
        expect(result.success).toBe(false);
      });
    });
  });

  describe('DroneControlValidationSchemas', () => {
    describe('move', () => {
      it('有効な移動コマンドを受け入れること', () => {
        const validMove = {
          droneId: 'drone-001',
          direction: 'forward' as const,
          distance: 100,
        };

        const result = Validators.validate(DroneControlValidationSchemas.move, validMove);
        expect(result.success).toBe(true);
      });

      it('無効な距離を拒否すること', () => {
        const invalidMoves = [
          { droneId: 'drone-001', direction: 'forward', distance: 10 }, // 短すぎる
          { droneId: 'drone-001', direction: 'forward', distance: 600 }, // 長すぎる
          { droneId: 'drone-001', direction: 'forward', distance: 50.5 }, // 小数点
        ];

        for (const move of invalidMoves) {
          const result = Validators.validate(DroneControlValidationSchemas.move, move);
          expect(result.success).toBe(false);
        }
      });
    });

    describe('rotate', () => {
      it('有効な回転コマンドを受け入れること', () => {
        const validRotate = {
          droneId: 'drone-001',
          direction: 'cw' as const,
          degrees: 90,
        };

        const result = Validators.validate(DroneControlValidationSchemas.rotate, validRotate);
        expect(result.success).toBe(true);
      });

      it('無効な角度を拒否すること', () => {
        const invalidRotates = [
          { droneId: 'drone-001', direction: 'cw', degrees: 0 }, // 小さすぎる
          { droneId: 'drone-001', direction: 'cw', degrees: 400 }, // 大きすぎる
          { droneId: 'drone-001', direction: 'cw', degrees: 45.5 }, // 小数点
        ];

        for (const rotate of invalidRotates) {
          const result = Validators.validate(DroneControlValidationSchemas.rotate, rotate);
          expect(result.success).toBe(false);
        }
      });
    });

    describe('takePhoto', () => {
      it('有効な写真撮影コマンドを受け入れること', () => {
        const validPhoto = {
          droneId: 'drone-001',
          filename: 'photo001.jpg',
        };

        const result = Validators.validate(DroneControlValidationSchemas.takePhoto, validPhoto);
        expect(result.success).toBe(true);
      });

      it('無効なファイル名を拒否すること', () => {
        const invalidPhotos = [
          { droneId: 'drone-001', filename: 'photo.txt' }, // 無効な拡張子
          { droneId: 'drone-001', filename: 'photo with spaces.jpg' }, // スペース
          { droneId: 'drone-001', filename: 'photo@special.jpg' }, // 特殊文字
        ];

        for (const photo of invalidPhotos) {
          const result = Validators.validate(DroneControlValidationSchemas.takePhoto, photo);
          expect(result.success).toBe(false);
        }
      });
    });
  });

  describe('セキュリティヘルパー関数', () => {
    describe('sanitizeString', () => {
      it('危険な文字を除去すること', () => {
        const input = '<script>alert("xss")</script>Hello<script>World</script>';
        const sanitized = Validators.sanitizeString(input);
        expect(sanitized).toBe('HelloWorld');
      });

      it('HTMLタグを除去すること', () => {
        const input = 'Hello <b>World</b> <i>Test</i>';
        const sanitized = Validators.sanitizeString(input);
        expect(sanitized).toBe('Hello World Test');
      });

      it('クォートを除去すること', () => {
        const input = 'Hello "World" \'Test\'';
        const sanitized = Validators.sanitizeString(input);
        expect(sanitized).toBe('Hello World Test');
      });
    });

    describe('validateSafeSqlInput', () => {
      it('安全な入力を許可すること', () => {
        const safeInputs = [
          'normal text',
          'user123',
          'test-data',
          'data_value',
        ];

        for (const input of safeInputs) {
          const result = Validators.validateSafeSqlInput(input);
          expect(result).toBe(true);
        }
      });

      it('危険なSQL注入を検出すること', () => {
        const dangerousInputs = [
          'SELECT * FROM users',
          'DROP TABLE users',
          'admin\'--',
          '1; DROP TABLE users--',
          '/*comment*/',
        ];

        for (const input of dangerousInputs) {
          const result = Validators.validateSafeSqlInput(input);
          expect(result).toBe(false);
        }
      });
    });

    describe('validateSafeHtmlInput', () => {
      it('安全なHTMLを許可すること', () => {
        const safeInputs = [
          'normal text',
          'Hello world',
          'Text with numbers 123',
        ];

        for (const input of safeInputs) {
          const result = Validators.validateSafeHtmlInput(input);
          expect(result).toBe(true);
        }
      });

      it('危険なXSSを検出すること', () => {
        const dangerousInputs = [
          '<script>alert("xss")</script>',
          'javascript:alert("xss")',
          '<img onload="alert(1)">',
          '<iframe src="evil.com"></iframe>',
          '<object data="evil.swf"></object>',
        ];

        for (const input of dangerousInputs) {
          const result = Validators.validateSafeHtmlInput(input);
          expect(result).toBe(false);
        }
      });
    });

    describe('validateSafeFilePath', () => {
      it('安全なファイルパスを許可すること', () => {
        const safeInputs = [
          'file.txt',
          'folder/file.txt',
          'data/images/photo.jpg',
          'logs/app.log',
        ];

        for (const input of safeInputs) {
          const result = Validators.validateSafeFilePath(input);
          expect(result).toBe(true);
        }
      });

      it('危険なパストラバーサルを検出すること', () => {
        const dangerousInputs = [
          '../../../etc/passwd',
          '/etc/passwd',
          'file\0.txt',
          'file\r\n.txt',
          '',
          'a'.repeat(300), // 長すぎるパス
        ];

        for (const input of dangerousInputs) {
          const result = Validators.validateSafeFilePath(input);
          expect(result).toBe(false);
        }
      });
    });
  });

  describe('PresetValidators', () => {
    it('バリデーション成功時に正しいデータを返すこと', () => {
      const loginData = { username: 'testuser', password: 'password123' };
      const result = PresetValidators.validateLogin(loginData);
      
      expect(result).toEqual(loginData);
    });

    it('バリデーション失敗時にエラーをスローすること', () => {
      const invalidLoginData = { username: 'ab', password: '' };
      
      expect(() => PresetValidators.validateLogin(invalidLoginData)).toThrow('バリデーションエラー');
    });
  });
});