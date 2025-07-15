# ドローン制御フロントエンド

Tello EDU ドローン制御システムのためのモダンなReact Webアプリケーション

## 概要（Description）

MFG Drone Frontend は、Tello EDU ドローンを使った自動追従撮影システムのフロントエンドWebアプリケーションです。React 18とTypeScriptで構築され、直感的なWebインターフェースを通じてドローン制御、リアルタイム映像表示、物体追跡設定、システム監視機能を提供します。Material-UIによるモダンなUIデザインと、WebSocketを活用したリアルタイム通信により、効率的で使いやすいドローン制御体験を実現します。

## 目次（Table of Contents）

- [概要（Description）](#概要description)
- [インストール方法（Installation）](#インストール方法installation)
- [使い方（Usage）](#使い方usage)
- [動作環境・要件（Requirements）](#動作環境要件requirements)
- [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
- [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## インストール方法（Installation）

### 前提条件

- Node.js 18.x 以上
- npm または yarn

### 基本セットアップ

```bash
# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev
```

開発サーバーは http://localhost:3000 で起動します。

### 環境変数設定

```bash
# .env.local ファイルを作成
cp .env.example .env.local

# 必要な環境変数を設定
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_NODE_ENV=development
```

### Docker環境での起動

```bash
# 開発環境
docker build --target development -t mfg-drone-frontend:dev .
docker run -p 3000:3000 -v $(pwd):/app mfg-drone-frontend:dev

# 本番環境
docker build --target production -t mfg-drone-frontend:prod .
docker run -p 80:80 mfg-drone-frontend:prod
```

## 使い方（Usage）

### 開発用コマンド

```bash
# 開発サーバー起動
npm run dev

# プロダクションビルド
npm run build

# プレビューサーバー起動
npm run preview

# テスト実行
npm run test

# テストUIモード
npm run test:ui

# カバレッジ付きテスト
npm run test:coverage

# 型チェック
npm run type-check

# Lint実行
npm run lint

# Lint自動修正
npm run lint:fix
```

### 基本的な操作

1. **ドローン接続**: ダッシュボードでドローンとの接続を確立
2. **手動制御**: 制御パネルでドローンの手動操作
3. **映像確認**: リアルタイム映像ストリームの表示
4. **物体追跡**: AI物体検出と自動追従の設定
5. **システム監視**: ドローンステータスとシステム健全性の確認

### API接続設定

バックエンドAPIとの接続は以下の通り設定されます：

- 開発環境: `http://localhost:8000`
- WebSocket: `ws://localhost:8000`
- プロキシ設定: `vite.config.ts` で自動設定

## 動作環境・要件（Requirements）

### システム要件

- **Node.js**: 18.x以上
- **ブラウザ**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **メモリ**: 4GB以上推奨
- **ネットワーク**: インターネット接続（開発時）

### 必須依存関係

- **React**: 18.2+ (UIフレームワーク)
- **TypeScript**: 4.9+ (型安全性)
- **Material-UI**: 5.11+ (UIコンポーネント)
- **Redux Toolkit**: 1.9+ (状態管理)
- **Vite**: 4.1+ (ビルドツール)
- **React Router**: 6.8+ (ルーティング)

### 開発・テスト依存関係

- **Vitest**: 単体テストフレームワーク
- **React Testing Library**: React コンポーネントテスト
- **Playwright**: E2Eテストフレームワーク
- **ESLint**: コード品質管理
- **Prettier**: コードフォーマット

### ネットワーク要件

- **バックエンドAPI**: ポート8000での通信
- **WebSocket**: リアルタイム通信（ws://localhost:8000）
- **ファイアウォール**: 開発時は localhost 通信許可

## ディレクトリ構成（Directory Structure）

```
frontend/
├── src/                        # ソースコード
│   ├── components/            # 再利用可能UIコンポーネント
│   │   ├── common/           # 共通コンポーネント
│   │   ├── dataset/          # データセット・画像管理コンポーネント
│   │   ├── drone/            # ドローン関連コンポーネント
│   │   ├── model/            # AI・モデル管理コンポーネント
│   │   └── monitoring/       # システム監視・分析コンポーネント
│   ├── pages/                 # ページコンポーネント
│   │   ├── Dashboard/        # メインダッシュボード
│   │   ├── DroneManagement/  # ドローン管理画面
│   │   ├── DatasetManagement/ # データセット管理画面
│   │   ├── ModelManagement/  # モデル管理画面
│   │   ├── TrackingControl/  # 追跡制御画面
│   │   ├── SystemMonitoring/ # システム監視画面
│   │   ├── ErrorTracking/    # エラー追跡画面
│   │   ├── Settings/         # 設定画面
│   │   └── Login/            # ログイン画面
│   ├── hooks/                 # カスタムReactフック
│   │   ├── useAuth.ts        # 認証関連フック
│   │   ├── useNotification.ts # 通知機能フック
│   │   ├── useOffline.ts     # オフライン対応フック
│   │   └── useWebSocket.ts   # WebSocket通信フック
│   ├── services/              # 外部サービス・API
│   │   ├── api/              # API関連
│   │   │   ├── apiClient.ts  # APIクライアント
│   │   │   ├── droneApi.ts   # ドローンAPI
│   │   │   ├── modelApi.ts   # モデルAPI
│   │   │   ├── visionApi.ts  # 映像・AI機能API
│   │   │   └── dashboardApi.ts # ダッシュボードAPI
│   │   └── websocket/        # WebSocket管理
│   │       └── wsClient.ts   # WebSocketクライアント
│   ├── store/                 # Redux状態管理
│   │   ├── index.ts          # ストア設定
│   │   ├── api/              # API関連状態管理
│   │   │   └── apiSlice.ts   # RTK Query APIスライス
│   │   └── slices/           # 各機能の状態管理
│   │       ├── authSlice.ts  # 認証状態管理
│   │       ├── droneSlice.ts # ドローン状態管理
│   │       └── dashboardSlice.ts # ダッシュボード状態管理
│   ├── types/                 # TypeScript型定義
│   │   ├── common.ts         # 共通型定義
│   │   ├── drone.ts          # ドローン関連型
│   │   └── monitoring.ts     # 監視・分析関連型
│   │   └── api.ts            # API関連型
│   ├── utils/                 # ユーティリティ関数
│   │   ├── constants.ts      # 定数定義
│   │   ├── helpers.ts        # ヘルパー関数
│   │   └── validation.ts     # バリデーション
│   ├── styles/                # スタイル関連
│   │   ├── globals.css       # グローバルスタイル
│   │   └── theme.ts          # Material-UIテーマ
│   ├── App.tsx               # メインアプリケーション
│   ├── main.tsx              # エントリーポイント
│   └── vite-env.d.ts         # Vite型定義
├── src/test/                   # テストファイル
│   ├── components/           # コンポーネントテスト
│   ├── hooks/                # フックテスト
│   ├── e2e/                  # E2Eテスト
│   └── setup.ts              # テストセットアップ
├── public/                     # 静的ファイル
│   ├── favicon.ico           # ファビコン
│   └── index.html            # HTMLテンプレート
├── Dockerfile                 # Docker設定
├── vite.config.ts            # Vite設定
├── tsconfig.json             # TypeScript設定
├── package.json              # 依存関係
├── eslint.config.js          # ESLint設定
├── playwright.config.ts      # Playwright設定
└── vitest.config.ts          # Vitest設定
```

## 更新履歴（Changelog/History）

### Phase 6: 実機統合対応（最新）
- **実機ドローン対応**: Tello EDU実機との統合制御UI
- **リアルタイム制御**: WebSocketによる即座のドローン応答
- **ステータス監視**: 実機・シミュレーション状態の統合表示
- **フォールバック表示**: 接続エラー時の適切なユーザー通知
- **設定UI**: 動作モード切り替えの直感的な設定画面

### Phase 5: Webダッシュボード機能
- **統合ダッシュボード**: 包括的なシステム監視画面
- **リアルタイム監視**: WebSocketによるライブデータ表示
- **アラート表示**: システム異常の即座通知
- **パフォーマンス監視**: システム負荷・メトリクス表示

### Phase 4: プロダクション対応
- **認証システム**: セキュアなAPI Key認証画面
- **セキュリティ強化**: 入力値検証・セキュリティヘッダー対応
- **エラーハンドリング**: 包括的なエラー表示・回復機能
- **パフォーマンス最適化**: コード分割・遅延読み込み

### Phase 3: ビジョン & AI機能
- **物体検出UI**: YOLOv8、SSD、Faster R-CNN設定画面
- **自動追跡制御**: リアルタイム物体追跡・追従設定
- **データセット管理**: 学習データ作成・管理画面
- **モデル管理**: ML学習ジョブ監視・制御インターフェース

### Phase 2: 高度制御 & リアルタイム通信
- **WebSocket統合**: 双方向リアルタイム通信
- **映像ストリーミング**: ライブカメラ映像表示
- **並行制御UI**: 複数ドローン同時制御画面
- **パフォーマンス監視**: リアルタイム状態表示

### Phase 1: 基盤UI実装
- **基本制御パネル**: ドローン接続・離着陸・移動制御
- **3D可視化**: ドローン位置・軌跡の3D表示
- **状態監視**: リアルタイムステータス表示
- **レスポンシブデザイン**: モバイル・デスクトップ対応

---

**ライセンス**: MIT License - 詳細は[LICENSE](../LICENSE)ファイルを参照してください。