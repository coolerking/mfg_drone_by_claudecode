# MFG Drone - 管理者用フロントエンド

Tello EDU ドローン自動追従撮影システムの管理者用Webインターフェースです。

## 概要

このフロントエンドアプリケーションは、ドローンの制御、カメラ・映像管理、センサー監視、物体追跡機能を包括的に提供します。

### 主要機能

- **🔗 ドローン接続管理**: Tello EDUドローンとの接続・切断制御
- **📹 カメラ・映像制御**: ライブストリーミング、写真撮影、動画録画
- **🎬 メディア管理**: 撮影したメディアファイルの管理・ダウンロード
- **📡 センサー監視**: バッテリー、高度、温度、姿勢データのリアルタイム監視  
- **⚙️ システム設定**: カメラ設定、API設定、システム情報

## インストール・セットアップ

### 1. 依存関係のインストール

```bash
cd frontend/admin
pip install -r requirements.txt
```

### 2. 環境変数設定（オプション）

`.env` ファイルを作成して設定を調整できます：

```bash
# バックエンドAPI URL（デフォルト: http://localhost:8000）
BACKEND_API_URL=http://192.168.1.100:8000

# セキュリティキー
SECRET_KEY=your-secret-key-here

# デバッグモード（開発時のみ）
FLASK_DEBUG=True
```

### 3. アプリケーション起動

```bash
python main.py
```

アプリケーションは `http://localhost:5001` で起動します。

## 使用方法

### 1. ドローン接続

1. Tello EDUドローンの電源を入れる
2. WiFiでTelloネットワークに接続
3. 「ドローン接続」画面で接続ボタンをクリック

### 2. カメラ・映像制御

1. ドローン接続後、「カメラ・映像」画面に移動
2. 「ストリーミング開始」でライブ映像を表示
3. 写真撮影・動画録画が可能
4. カメラ設定（解像度・FPS・ビットレート）を調整

### 3. メディア管理

- 撮影した写真・動画の一覧表示
- ファイルのダウンロード・削除
- ストレージ使用量の確認

### 4. センサー監視

- バッテリー残量、飛行高度、温度などのリアルタイム表示
- 警告状態の自動検知（バッテリー低下、温度異常など）
- 2秒間隔での自動更新

## API統合

このフロントエンドは以下のバックエンドAPIと連携します：

### ドローン制御API
- `POST /drone/connect` - ドローン接続
- `POST /drone/disconnect` - ドローン切断
- `GET /drone/status` - ドローン状態取得

### カメラAPI
- `POST /camera/stream/start` - ストリーミング開始
- `POST /camera/stream/stop` - ストリーミング停止
- `GET /camera/stream` - ライブストリーム取得
- `POST /camera/photo` - 写真撮影
- `POST /camera/video/start` - 録画開始
- `POST /camera/video/stop` - 録画停止
- `PUT /camera/settings` - カメラ設定変更

### センサーAPI
- `GET /drone/battery` - バッテリー残量
- `GET /drone/height` - 飛行高度
- `GET /drone/temperature` - 温度
- `GET /drone/flight_time` - 飛行時間

### フロントエンド内部API
- `GET /api/config` - 設定情報取得
- `GET /api/media` - メディアファイル一覧
- `DELETE /api/media/<filename>` - メディアファイル削除
- `GET /api/storage` - ストレージ情報

## 技術仕様

### フロントエンド技術
- **フレームワーク**: Flask 3.0.0
- **UI**: HTML5 + CSS3 + Vanilla JavaScript
- **スタイル**: カスタムCSS（レスポンシブデザイン）
- **フォント**: Noto Sans JP（日本語対応）
- **アーキテクチャ**: SPA（Single Page Application）風

### 対応ブラウザ
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### レスポンシブ対応
- デスクトップ（1920x1080以上推奨）
- タブレット（768px以上）
- モバイル（最小375px）

## ディレクトリ構造

```
frontend/admin/
├── main.py                 # Flask アプリケーション
├── requirements.txt        # Python依存関係
├── README.md              # このファイル
├── static/                # 静的ファイル
│   ├── css/
│   │   └── style.css      # メインスタイルシート
│   ├── js/
│   │   └── app.js         # JavaScript アプリケーション
│   ├── manifest.json      # PWAマニフェスト
│   ├── uploads/           # アップロードファイル
│   └── media/             # メディアファイル
├── templates/
│   └── admin.html         # メインHTMLテンプレート
└── tests/                 # テストファイル
```

## 開発・カスタマイズ

### CSS変数
スタイルは CSS カスタムプロパティで管理されており、`:root` セレクタで色やサイズを変更できます：

```css
:root {
  --primary-color: #2563eb;
  --sidebar-width: 280px;
  --header-height: 64px;
}
```

### JavaScript 設定
`app.js` の `DroneAdmin` クラスで動作をカスタマイズできます：

```javascript
class DroneAdmin {
  constructor() {
    this.apiBaseUrl = 'http://localhost:8000';
    this.updateInterval = 2000; // センサー更新間隔（ミリ秒）
  }
}
```

## トラブルシューティング

### 接続エラー
- バックエンドAPIが起動しているか確認
- ネットワーク設定を確認
- ブラウザの開発者ツールでエラーログを確認

### ストリーミングが表示されない
- ドローンが接続されているか確認
- カメラ設定を確認
- ブラウザでメディア許可が有効か確認

### メディアファイルが表示されない
- `static/media/` フォルダの権限確認
- ディスク容量の確認

## セキュリティ

### 推奨事項
- 本番環境では `SECRET_KEY` を必ず変更
- HTTPS での運用を推奨
- CORS設定を本番環境に合わせて調整
- メディアファイルのアクセス制御

### 制限事項
- 現在の実装では認証機能なし
- ローカルネットワーク内での使用を想定
- ファイルアップロードサイズ制限なし

## ライセンス

MIT License

## 更新履歴

### v1.0.0 (2025-06-20)
- 初回リリース
- ドローン接続・制御機能
- カメラ・メディア管理機能
- センサー監視機能
- レスポンシブWebデザイン
- 日本語完全対応

## サポート・お問い合わせ

技術的な問題や機能要望については、プロジェクトのIssueトラッカーをご利用ください。