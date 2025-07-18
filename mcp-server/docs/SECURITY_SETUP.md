# セキュリティ設定ガイド

## ⚠️ 重要なセキュリティ修正プログラム適用済み

この文書では、修正されたセキュリティ脆弱性と、システムを安全に設定する方法について説明します。

## 修正された脆弱性

### 1. ❌ ハードコードされたJWTシークレット(修正済み ✅)

**問題**： JWT シークレットが複数のファイルにハードコードされていた：
- `security_manager.py`: `jwt_secret: str = "your-secret-key"`
- MCP統合前の各種サーバーファイル

**修正**: 
- すべてのハードコードされたフォールバック値を削除
- 弱い/デフォルトの秘密を拒否する検証を追加した。
- JWT_SECRET環境変数を必須にした。
- 最小の長さの要件（32文字）を追加

### 2. ❌ ログイン認証がハードコードされていた (修正済み ✅)

**問題**: ログイン認証がMCP統合前のサーバーファイルにハードコードされていた:
```python
if username == "admin" and password == "admin123":
elif username == "operator" and password == "operator123":
```

**修正**:
- 環境変数ベースの認証に変更
- 複数のユーザータイプ（admin、operator、readonly）のサポートを追加。
- 適切なセキュリティ検証の実装
- アカウントロックアウトとレート制限の追加

## 必須環境変数

### 重要なセキュリティ設定（必須）

```bash
# JWTシークレット（必須 - 最小32文字）
JWT_SECRET=your-strong-jwt-secret-here-must-be-at-least-32-chars-long

# 少なくとも1人のユーザーを設定する必要があります：
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-admin-password

# オプション 追加ユーザー：
OPERATOR_USERNAME=your-operator-username
OPERATOR_PASSWORD=your-secure-operator-password

READONLY_USERNAME=your-readonly-username
READONLY_PASSWORD=your-secure-readonly-password
```

### オプション セキュリティ設定

```bash
# 動作環境（バリデーションの厳格さに影響する）
ENVIRONMENT=development  # or 'production'

# JWT 設定
JWT_EXPIRY_MINUTES=60

# アカウントセキュリティ
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION=15

# IP アドレスコントロール
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8  # comma-separated
BLOCKED_IPS=192.168.1.100,10.0.0.50    # comma-separated

# モニタリング
ENABLE_MONITORING=true
MONITORING_INTERVAL=30
ENABLE_AUDIT_LOGGING=true
```

## セキュリティ設定手順

### ステップ1：安全なシークレットの生成

```bash
# JWTシークレットを生成する（64文字以上を推奨）
openssl rand -base64 64

# Pythonを使った代替案
python -c "import secrets; print(secrets.token_urlsafe(64))"

# 安全なパスワードの生成
openssl rand -base64 32
```

### ステップ2：環境設定の作成

mcp-serverディレクトリに `.env` ファイルを作成する：

```bash
# example をコピーしてカスタマイズ
cp .env.example .env
#  .env を編集し、セキュリティ設定
```

### ステップ3: 設定の検証

```bash
# 設定のテスト
python start_mcp_server_unified.py --validate-config

# ヘルスチェックの実行
python start_mcp_server_unified.py --health-check
```

### ステップ4：セキュリティ実装のテスト

```bash
# セキュリティ検証テストの実行
cd tests
python test_security_fixes.py
```

## 実装されているセキュリティ機能

### ✅ 認証と認可
- 環境変数ベースのユーザー認証
- 複数レベルのセキュリティ・ロール（Admin、Operator、Read-only）
- JWT トークン・ベースの認証
- API キー認証
- 有効期限付きのセッション管理

### ✅ 保護メカニズム
- 試行失敗後のアカウントロックアウト
- ユーザー/IPごとのレート制限
- IP許可リスト/ブロックリストのサポート
- 入力検証とサニタイズ
- インジェクション攻撃に対する保護

### ✅ 監視と監査
- セキュリティイベントロギング
- 脅威分析とレポート
- リアルタイムのセキュリティ指標
- 試行失敗の追跡
- 包括的な監査証跡

### ✅ 構成の検証
- 必須のセキュリティ設定
- 弱いクレデンシャルの検出
- JWT 秘密強度の検証
- 環境固有の要件

## 本番環境への配備

### 本番環境での要件

1. **ENVIRONMENT=production** を設定する
2. **必要な環境変数** をすべて設定する
3. **強力でユニークな認証情報** を使用する
4. **IPアクセス制御** を有効にする
5. **SSL/TLSの設定（リバースプロキシ推奨）**
6. **セキュリティログ** を定期的に監視する

### 本番環境での推奨セットアップ

```bash
# Production 環境
ENVIRONMENT=production

# 強力なJWTシークレット（64文字以上）
JWT_SECRET=<generated-64-character-secret>

# 安全な管理者認証
ADMIN_USERNAME=<unique-admin-username>
ADMIN_PASSWORD=<strong-admin-password>

# オペレーター資格
OPERATOR_USERNAME=<unique-operator-username>
OPERATOR_PASSWORD=<strong-operator-password>

# IP制限
ALLOWED_IPS=10.0.0.0/8,192.168.0.0/16

# セキュリティ設定の強化
MAX_FAILED_ATTEMPTS=3
LOCKOUT_DURATION=30
JWT_EXPIRY_MINUTES=30

# フルモニタリング
ENABLE_MONITORING=true
ENABLE_AUDIT_LOGGING=true
```

## セキュリティテスト

### 完全なセキュリティ・テスト・スイートを実行する

```bash
# 全てのセキュリティフィックスをテストする
pytest tests/test_security_fixes.py -v

# 一般的な機能のテスト
pytest tests/test_phase5_integration.py -v
```

### 手動セキュリティテスト

1. **弱い JWT 秘密の拒否をテストする：
   ```bash
   JWT_SECRET="weak" python start_mcp_server_unified.py --validate-config
   # バリデーションエラーで失敗するはず
   ```

2. **不足している認証情報をテストする**：
   ```bash
   # 全てのユーザー環境バーを削除する
   python start_mcp_server_unified.py --validate-config
   # ユーザ設定エラーで失敗するはず
   ``` 

3. **認証エンドポイントのテスト**：
   ```bash
   # サーバを起動し、ログインをテストする
   curl -X POST http://localhost:8003/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "wrong"}'
   # 401 Unauthorized を返すべきである
   ```

## 以前のバージョンからの移行

以前のバージョンからハードコードされた認証情報でアップグレードする場合：

1. **サーバーを停止する**
2. 上記のように**環境変数を設定する**
3. `validate-config`で **設定をテストする**
4. **サーバーを再起動** して機能を確認する
5. ハードコードされた認証情報に依存していた **スクリプトを更新する**

## セキュリティ監視

### 監視すべき主な指標

- 認証の失敗
- アカウントのロックアウト
- レート制限違反
- 不審なIPアクティビティ
- セキュリティイベントの傾向

### 警告のしきい値

- **クリティカル**： 管理者ログイン試行失敗
- **高**： 複数のアカウントロックアウト
- **中**： レート制限違反
- **低**： 管理者ログイン成功


#サポートとセキュリティ報告

セキュリティ上の問題や質問については

1. **設定の問題**： このドキュメントをチェックしてください
2. **セキュリティの脆弱性**： 個人的にメンテナに報告してください。
3. **一般的な質問**： プロジェクトの課題追跡ツールを使ってください。

---

**⚠️ セキュリティに関する注意事項**： `.env`ファイルや実際の認証情報をバージョン管理にコミットしないでください！
