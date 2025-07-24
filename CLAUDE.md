# プロジェクト概要
このプロジェクトは、Tello EDU ドローンを使用した自動追従撮影システムを実現するためのWebアプリケーションです。実機制御とシミュレーション機能を統合し、手動制御から自動追従まで対応する包括的なドローン制御プラットフォームです。

## 主要機能
- **手動制御**: Web UIによるドローンの手動操作
- **物体追跡**: AI（YOLOv8）による物体検出・追跡・自動追従
- **実機統合**: Tello EDU実機とシミュレーション環境の統合制御
- **Webダッシュボード**: リアルタイム監視・制御インターフェース
- **MCPサーバー**: Claude統合による自然言語ドローン制御

# 技術スタック

## バックエンド
- **言語**: Python 3.9+
- **フレームワーク**: FastAPI 0.104.1+
- **データベース**: PostgreSQL 13+ (推奨), Redis 6+ (キャッシュ)
- **ドローン制御**: djitellopy 2.5.0 (Tello EDU SDK)
- **AI・画像処理**: OpenCV 4.8.1+, YOLOv8 (ultralytics 8.0.196+)
- **WebSocket**: FastAPI WebSocket支援

## フロントエンド
- **言語**: TypeScript 4.9+
- **フレームワーク**: React 18.2+
- **UIライブラリ**: Material-UI 5.11+
- **状態管理**: Redux Toolkit 1.9+
- **ビルドツール**: Vite 4.1+
- **テスト**: Vitest, Playwright

## MCPサーバー
- **Node.js版（推奨）**: TypeScript 5.0+, @modelcontextprotocol/sdk
- **Python版（レガシー）**: Python 3.9+, FastAPI
- **機能**: 自然言語処理、Claude統合、バックエンドAPI連携

## インフラ・運用
- **コンテナ**: Docker, Docker Compose
- **リバースプロキシ**: nginx
- **監視**: Prometheus, Grafana
- **CI/CD**: GitHub Actions

# 開発環境セットアップ

## 前提条件
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose（本番環境用）
- Tello EDU ドローン（実機テスト用、オプション）

## 基本セットアップ手順

### 1. リポジトリクローン
```bash
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode
```

### 2. バックエンドセットアップ
```bash
cd backend
pip install -r requirements.txt

# 設定ファイル作成
cp config/drone_config.yaml.example config/drone_config.yaml

# 環境変数設定
export DRONE_MODE=auto
export TELLO_AUTO_DETECT=true
export LOG_LEVEL=INFO

# サーバー起動
python start_api_server.py
```

### 3. フロントエンドセットアップ
```bash
cd frontend
npm install
npm run dev
```

### 4. MCPサーバーセットアップ

**Node.js版（推奨・メイン開発対象）**：
```bash
cd mcp-server-nodejs
npm install
npm run build
npm start

# 開発モード（ホットリロード）
npm run dev

# またはnpxで直接実行
npx mcp-drone-server-nodejs
```


## Docker環境
```bash
# 開発環境
docker-compose -f docker-compose.dev.yml up

# 本番環境
docker-compose -f docker-compose.prod.yml up
```

# よく使うコマンド

## 開発・テスト
```bash
# バックエンドテスト
cd backend && python -m pytest tests/

# フロントエンドテスト
cd frontend && npm test

# E2Eテスト
cd frontend && npm run test:e2e

# 包括的テスト
cd backend && python -m pytest tests/test_phase6_real_simulation_switching.py -v
```

## ビルド・デプロイ
```bash
# バックエンドビルド
cd backend && docker build -t mfg-drone-backend .

# フロントエンドビルド
cd frontend && npm run build

# プロダクションビルド
cd frontend && npm run build:prod
```

## 実機制御テスト
```bash
# シミュレーションモード
export DRONE_MODE=simulation && python backend/start_api_server.py

# 実機モード
export DRONE_MODE=real && python backend/start_api_server.py

# 自動モード（実機検出→フォールバック）
export DRONE_MODE=auto && python backend/start_api_server.py
```

## 監視・デバッグ
```bash
# ログ確認
tail -f backend/logs/app.log

# システム状態確認
curl http://localhost:8000/api/system/status

# ドローン検出
curl -X POST http://localhost:8000/api/drones/scan
```

# コーディング規約

## Python（バックエンド・MCP）
- **コーディング標準**: PEP8準拠
- **型ヒント**: 必須（Python 3.9+ type hints）
- **import順序**: 標準→サードパーティ→ローカル
- **ネーミング**: スネークケース（snake_case）
- **async/await**: 非同期処理は async/await を使用
- **例外処理**: 適切な例外型を使用、ログ出力必須

## TypeScript（フロントエンド）
- **コーディング標準**: ESLint設定準拠
- **型定義**: 厳密な型定義（any型の使用禁止）
- **変数名**: キャメルケース（camelCase）
- **import/export**: ES Modules使用
- **コンポーネント**: 関数コンポーネント + フック
- **状態管理**: Redux Toolkit使用

## 共通ルール
- **コメント**: 複雑なロジックには日本語コメント
- **関数**: 単一責任の原則、適切なサイズ
- **エラーハンドリング**: 適切なエラーメッセージ、ログ出力
- **テスト**: 新機能には必ず単体テスト追加
- **セキュリティ**: 認証・認可、入力値検証必須

# ワークフロー

## 開発プロセス
1. **課題・機能要求**: GitHub Issues で課題報告・機能要求
2. **ブランチ作成**: `feature/機能名` または `fix/バグ名`
3. **開発実装**: コーディング規約に従って実装
4. **テスト**: 単体テスト・統合テスト実行
5. **プルリクエスト**: レビュー必須、テスト結果報告
6. **レビュー**: コードレビュー、動作確認
7. **マージ**: mainブランチへのマージ

## Git運用
- **mainブランチ**: 本番環境対応コード
- **developブランチ**: 開発統合ブランチ
- **featureブランチ**: 機能開発用
- **hotfixブランチ**: 緊急修正用
- **プルリクエスト必須**: mainブランチへの直接push禁止
- **レビュー必須**: 最低1名のレビュー・承認が必要

## テスト戦略
- **単体テスト**: 全パブリック関数、カバレッジ80%以上
- **統合テスト**: API・UI統合、実機なしテスト
- **E2Eテスト**: 主要ユーザージャーニー
- **パフォーマンステスト**: 負荷テスト、メモリリークチェック
- **セキュリティテスト**: 認証・認可、入力値検証

# プロジェクト構造

## ディレクトリ構成
```
mfg_drone_by_claudecode/
├── backend/                    # バックエンドAPI
│   ├── api_server/            # FastAPIアプリケーション
│   ├── src/                   # シミュレーションシステム
│   ├── tests/                 # テストスイート
│   ├── config/               # 設定ファイル
│   └── docs/                 # ドキュメント
├── frontend/                   # フロントエンドアプリケーション
│   ├── src/                   # Reactアプリケーション
│   ├── tests/                 # テストスイート
│   └── docs/                 # フロントエンド仕様
├── mcp-server/                # MCPサーバー（Python版・レガシー）
│   ├── src/                   # MCPサーバーコード
│   └── tests/                # テスト
├── mcp-server-nodejs/         # MCPサーバー（Node.js版・推奨）
│   ├── src/                   # TypeScriptソースコード
│   ├── dist/                 # コンパイル済みJavaScript
│   ├── Dockerfile           # Dockerコンテナ設定
│   └── package.json         # Node.js依存関係
├── shared/                    # 共有リソース
│   ├── api-specs/            # OpenAPI仕様
│   └── config/               # 共通設定
└── tests/                     # 統合テスト
```

## 重要なファイル
- **backend/api_server/main.py**: FastAPIメインアプリケーション
- **backend/config/drone_config.yaml**: ドローン設定
- **frontend/src/main.tsx**: Reactアプリケーションエントリーポイント
- **shared/api-specs/backend-api.yaml**: バックエンドAPI仕様
- **docker-compose.yml**: 本番環境Docker設定

# Claude Codeへの指示

## 基本方針
- **すべての応答は日本語で行う**
- **既存のコーディング規約を必ず守る**
- **テストコードも含めて実装する**
- **セキュリティを考慮した実装を行う**

## README.md と CLAUDE.md の運用の違い

### README.md
- **対象**: 一般ユーザー・開発者・プロジェクト評価者
- **目的**: プロジェクトの概要理解、導入検討、基本的な使用方法
- **内容**: 
  - プロジェクトの魅力的な紹介
  - インストール手順
  - 基本的な使用方法
  - 技術仕様
  - 貢献方法
  - ライセンス情報

### CLAUDE.md
- **対象**: Claude Code AI アシスタント
- **目的**: 効率的な開発支援、コード品質向上
- **内容**:
  - プロジェクトの技術的詳細
  - 開発環境セットアップ
  - コーディング規約
  - 開発ワークフロー
  - よく使うコマンド
  - Claude Code向けの具体的な指示

## 開発時の注意事項

### 実機制御関連
- **実機がない環境**: 自動的にシミュレーションモードにフォールバック
- **DRONE_MODE環境変数**: auto, simulation, real の3つのモード
- **接続テスト**: 実機制御前に必ず接続確認を実行

### API開発
- **OpenAPI仕様**: 変更時は必ず shared/api-specs/ を更新
- **バージョン管理**: 破壊的変更時はバージョン番号を更新
- **エラーハンドリング**: 適切なHTTPステータスコードとエラーメッセージ

### フロントエンド開発
- **レスポンシブデザイン**: モバイル・タブレット対応
- **アクセシビリティ**: WAI-ARIA準拠
- **パフォーマンス**: Code Splitting、Lazy Loading活用

### テスト
- **実機なしテスト**: 基本的に実機なしでテスト可能な設計
- **モックデータ**: tests/fixtures/ にテスト用データを配置
- **CI/CD**: GitHub Actions での自動テスト実行

## 追加情報
- **Phase 6完了**: 実機統合・ハイブリッド運用対応済み
- **継続的改善**: パフォーマンス・セキュリティ・ユーザビリティの向上
- **実機テスト**: Tello EDU実機での動作確認推奨
- **ドキュメント**: 実装時にはドキュメントも同時更新