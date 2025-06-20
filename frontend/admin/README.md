# MFG Drone Admin Frontend - Phase 5 完全版

管理者用フロントエンド: 高度制御機能・ミッションパッド対応・システム設定

## 🎯 概要

Tello EDU ドローンの自動追従撮影システムにおける包括的な管理者制御インターフェースです。  
Phase 5では高度制御機能、ミッションパッド対応、システム設定管理などの完全機能を提供します。

## ✨ 主要機能

### 🏠 ダッシュボード・システム監視
- **リアルタイム状態表示**: バッテリー・高度・温度・接続状態
- **ライブ映像表示**: ドローンカメラからのリアルタイムストリーミング
- **クイックコントロール**: ワンクリック操作（接続・離陸・着陸・緊急停止）
- **システムログ**: イベント・警告の履歴表示

### 🔗 ドローン制御・接続管理
- **接続管理**: Tello EDUとの接続・切断・状態監視
- **ネットワーク診断**: 接続状態・IP情報・信号強度確認
- **基本飛行制御**: 離陸・着陸・緊急停止
- **移動制御**: 6方向移動（前後左右上下）・回転制御

### 🎯 高度制御機能（Phase 5）
- **3D座標移動**: XYZ座標指定による精密移動（-500〜500cm）
- **曲線飛行**: 中間点・終点指定による滑らかな曲線軌道
- **リアルタイム制御**: バーチャルスティック・ゲームパッド対応
- **飛行軌跡可視化**: リアルタイム軌跡表示・経路記録

### 🗺️ ミッションパッド対応（Phase 5）
- **パッド検出制御**: 有効・無効・検出方向設定（下向き・前向き・両方）
- **パッド基準移動**: 8つのミッションパッド（1-8）を基準とした精密移動
- **状態監視**: 検出中パッドの可視化・距離情報表示
- **Tello EDU専用**: 高精度位置決め機能

### 📹 カメラ・映像制御
- **ライブストリーミング**: リアルタイム映像配信・品質調整
- **撮影機能**: 写真撮影・動画録画・ファイル管理
- **メディア管理**: 撮影済みファイル一覧・ダウンロード・削除
- **画質設定**: 解像度・ビットレート・FPS調整

### 🤖 AI物体追跡・モデル管理
- **物体追跡**: リアルタイム追跡・モード選択（中央維持・追従飛行）
- **モデル訓練**: 画像アップロード・AI学習・ドラッグ&ドロップ対応
- **モデル管理**: 訓練済みモデル一覧・精度表示・削除
- **検出可視化**: バウンディングボックス・信頼度表示

### 📊 センサー監視・データ表示
- **バッテリー監視**: 残量表示・警告アラート・プログレスバー
- **3D姿勢表示**: ピッチ・ロール・ヨー角のリアルタイム表示
- **環境データ**: 高度・温度・湿度・気圧・飛行時間
- **リアルタイム更新**: 2秒間隔の自動更新

### ⚙️ システム設定・管理（Phase 5）
- **WiFi設定**: SSID・パスワード設定・接続管理
- **飛行パラメータ**: 速度設定（1.0-15.0 m/s）・飛行制限
- **カスタムコマンド**: Tello SDKコマンド直接送信（上級者用）
- **セキュリティ**: アクセス制御・設定保護

## 🏗️ 技術仕様

### フロントエンド技術スタック
- **Web Framework**: Flask 3.0.0 + Jinja2
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **UI Design**: レスポンシブデザイン・日本語フォント（Noto Sans JP）
- **Real-time**: Server-Sent Events・WebSocket対応
- **Browser Support**: モダンブラウザ（Chrome、Firefox、Safari、Edge）

### バックエンドAPI統合
- **API Client**: Python requests + session管理
- **Endpoints**: 80+ API エンドポイント完全対応
- **Error Handling**: 包括的エラー処理・タイムアウト・リトライ
- **Type Safety**: Python type hints + JavaScript JSDoc

### アーキテクチャ設計
- **MVC Pattern**: routes/、services/、templates/ 分離
- **API Proxy**: バックエンドAPIへの統合プロキシ
- **SPA風UI**: ハッシュルーティング・Ajax ページ読み込み
- **Component Based**: 45+ 再利用可能UIコンポーネント

## 🚀 インストール・起動方法

### 1. 依存関係インストール

```bash
cd frontend/admin
pip install -r requirements.txt
```

### 2. 環境設定（オプション）

```bash
# .env ファイル作成
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
BACKEND_API_URL=http://localhost:8000
SECRET_KEY=your-secret-key
```

### 3. アプリケーション起動

```bash
python main.py
```

### 4. ブラウザでアクセス

```
http://localhost:5001
```

## 📱 使用方法

### 基本操作フロー

1. **システム起動・接続**
   - ブラウザでアクセス → ダッシュボード確認
   - 「ドローン接続」でTello EDUに接続
   - 接続状態・バッテリー残量を確認

2. **基本飛行操作**
   - 「飛行制御」で離陸・着陸
   - 「基本移動」でWASD・QE キーボード操作
   - 距離調整（20-500cm）・回転制御

3. **高度制御機能（Phase 5）**
   - 「高度制御」で3D座標移動・曲線飛行
   - バーチャルスティック・ゲームパッド制御
   - 飛行軌跡の可視化・記録

4. **ミッションパッド活用（Phase 5）**
   - 「ミッションパッド」で検出有効化
   - パッド基準での精密移動
   - 8つのパッド状態監視

5. **AI物体追跡**
   - 「AIモデル管理」で画像アップロード・モデル訓練
   - 「物体追跡」で追跡開始・モード選択
   - リアルタイム検出結果確認

6. **システム設定・管理**
   - 「設定管理」でWiFi・飛行速度設定
   - カスタムコマンド送信
   - システム情報確認

### キーボードショートカット

- **Ctrl + W**: 前進
- **Ctrl + A**: 左移動
- **Ctrl + S**: 後退
- **Ctrl + D**: 右移動
- **Ctrl + Q**: 上昇
- **Ctrl + E**: 下降
- **ESC**: 緊急停止

## 🎨 UI/UX 設計

### デザインシステム
- **カラーパレット**: CSS カスタムプロパティ管理
- **レスポンシブ**: Desktop・Tablet・Mobile 対応
- **日本語対応**: Noto Sans JP フォント統合
- **アクセシビリティ**: WCAG 2.1 準拠・色彩対比・キーボード操作

### レイアウト構成
```
ヘッダー（システム名・接続状態・緊急停止）
├── サイドバーナビゲーション
│   ├── システム監視（ダッシュボード・接続・センサー）
│   ├── ドローン制御（飛行・移動・高度制御・ミッションパッド）
│   ├── AI・追跡（カメラ・追跡・モデル管理）
│   └── システム設定
├── メインコンテンツエリア（各機能画面）
└── フッター（バージョン情報）
```

### インタラクション機能
- **リアルタイム更新**: センサーデータ・接続状態（2秒間隔）
- **視覚的フィードバック**: ローディング・プログレスバー・アラート
- **ドラッグ&ドロップ**: ファイルアップロード・UI操作
- **ゲームパッド対応**: リアルタイム制御・デッドゾーン適用

## 🧪 開発・テスト

### 開発モード起動

```bash
FLASK_DEBUG=True python main.py
```

### テスト実行

```bash
# 単体テスト
pytest tests/

# 特定テスト
pytest tests/test_api.py

# カバレッジ付き
pytest --cov=main tests/
```

### コード品質チェック

```bash
# フォーマット
black main.py

# リント
flake8 main.py

# 型チェック
mypy main.py
```

## 📊 API エンドポイント

### フロントエンド API
- `GET /` - メインページ
- `GET /health` - ヘルスチェック

### ドローン制御 API
- `POST /api/drone/connect` - 接続
- `POST /api/drone/disconnect` - 切断
- `POST /api/drone/takeoff` - 離陸
- `POST /api/drone/land` - 着陸
- `POST /api/drone/emergency` - 緊急停止

### 移動制御 API
- `POST /api/drone/move/{direction}` - 方向移動
- `POST /api/drone/rotate` - 回転
- `POST /api/drone/go_xyz` - 3D座標移動（Phase 5）
- `POST /api/drone/curve_xyz` - 曲線飛行（Phase 5）
- `POST /api/drone/rc_control` - リアルタイム制御（Phase 5）

### ミッションパッド API（Phase 5）
- `POST /api/mission_pad/enable` - 検出有効化
- `POST /api/mission_pad/disable` - 検出無効化
- `PUT /api/mission_pad/detection_direction` - 検出方向設定
- `POST /api/mission_pad/go_xyz` - パッド基準移動
- `GET /api/mission_pad/status` - パッド状態取得

### センサー・監視 API
- `GET /api/sensors/all` - 全センサーデータ
- `GET /api/drone/battery` - バッテリー残量
- `GET /api/drone/altitude` - 高度
- `GET /api/drone/temperature` - 温度
- `GET /api/drone/attitude` - 姿勢角

### カメラ・映像 API
- `POST /api/camera/stream/start` - ストリーミング開始
- `POST /api/camera/stream/stop` - ストリーミング停止
- `GET /api/camera/stream` - ライブ映像プロキシ
- `POST /api/camera/photo` - 写真撮影
- `POST /api/camera/recording/start` - 録画開始
- `POST /api/camera/recording/stop` - 録画停止

### AI・追跡 API
- `POST /api/tracking/start` - 追跡開始
- `POST /api/tracking/stop` - 追跡停止
- `GET /api/tracking/status` - 追跡状態
- `POST /api/model/train` - モデル訓練
- `GET /api/model/list` - モデル一覧
- `DELETE /api/model/{name}` - モデル削除

### 設定管理 API（Phase 5）
- `PUT /api/settings/wifi` - WiFi設定
- `PUT /api/settings/speed` - 飛行速度設定
- `POST /api/settings/command` - カスタムコマンド送信

## 🔧 設定・カスタマイズ

### 環境変数
- `FLASK_HOST`: サーバーホスト（デフォルト: 0.0.0.0）
- `FLASK_PORT`: サーバーポート（デフォルト: 5001）
- `FLASK_DEBUG`: デバッグモード（デフォルト: True）
- `BACKEND_API_URL`: バックエンドAPI URL（デフォルト: http://localhost:8000）
- `SECRET_KEY`: Flask セッションキー

### CSS カスタマイズ
CSS カスタムプロパティで簡単にテーマ変更可能:

```css
:root {
  --primary-color: #2563eb;
  --success-color: #22c55e;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
}
```

### JavaScript 設定
アプリケーション設定の調整:

```javascript
// リアルタイム更新間隔
this.updateInterval = setInterval(() => {
  this.updateSensorData();
}, 2000); // 2秒間隔

// APIタイムアウト
this.session.timeout = 10; // 10秒
```

## 🐛 トラブルシューティング

### よくある問題

**1. ドローンに接続できない**
```bash
# 接続確認
ping 192.168.10.1

# WiFi接続確認
# Tello-XXXXXXネットワークに接続されているか確認
```

**2. ライブ映像が表示されない**
- バックエンドAPIが起動しているか確認
- ストリーミングが開始されているか確認
- ブラウザのメディア権限を確認

**3. API エラーが発生する**
```bash
# バックエンドAPI確認
curl http://localhost:8000/health

# ログ確認
tail -f logs/admin.log
```

**4. リアルタイム更新が停止する**
- ネットワーク接続を確認
- ブラウザのコンソールでエラーを確認
- ページリロードで回復することが多い

### ログ出力
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 📈 性能・最適化

### パフォーマンス指標
- **ページ読み込み時間**: < 2秒
- **API レスポンス時間**: < 500ms
- **リアルタイム更新**: 2秒間隔
- **ライブ映像遅延**: < 200ms

### 最適化手法
- **非同期API呼び出し**: fetch + Promise.all
- **画像最適化**: WebP対応・レスポンシブ画像
- **CSS最適化**: ミニファイ・グリッドレイアウト
- **JavaScript最適化**: ES6+・モジュラー設計

## 🚀 本番運用

### 本番デプロイ

```bash
# Gunicorn での起動
gunicorn -w 4 -b 0.0.0.0:5001 main:app

# Docker での起動
docker build -t mfg-drone-admin .
docker run -p 5001:5001 mfg-drone-admin
```

### セキュリティ対策
- **HTTPS**: SSL/TLS証明書設定
- **認証**: ログイン機能・セッション管理
- **CSRF保護**: Flask-WTF CSRF トークン
- **入力検証**: 全API入力値検証

### 監視・ログ
- **アクセスログ**: Nginx + Flask ログ
- **エラー監視**: Sentry 統合
- **メトリクス**: Prometheus + Grafana
- **アラート**: Discord/Slack 通知

## 📚 関連ドキュメント

- [バックエンドAPI仕様](../backend/openapi.yaml)
- [システム全体設計](../../README.md)
- [一般ユーザー用フロントエンド](../user/README.md)
- [Tello EDU SDK リファレンス](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)

## 👥 開発チーム

- **Frontend開発**: Claude Code (Anthropic)
- **プロジェクト**: MFG Drone Team
- **ライセンス**: MIT License

## 📝 更新履歴

### v1.0.0 (Phase 5) - 2025-06-20
- ✅ 高度制御機能完全実装（3D座標・曲線飛行・リアルタイム制御）
- ✅ ミッションパッド対応（検出・移動・状態監視）
- ✅ システム設定管理（WiFi・飛行パラメータ・カスタムコマンド）
- ✅ 包括的UI/UXデザイン（レスポンシブ・日本語対応）
- ✅ 80+ APIエンドポイント統合
- ✅ ゲームパッド・キーボード操作対応
- ✅ 飛行軌跡可視化機能
- ✅ リアルタイム監視・アラートシステム

---

**🚁 MFG Drone Admin Frontend Phase 5 - 完全なドローン管理システムをお楽しみください！**