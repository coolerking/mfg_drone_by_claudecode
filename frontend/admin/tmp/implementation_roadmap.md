# 管理用フロントエンド 実装ロードマップ

## 実装優先度とスケジュール

### フェーズ1: 基盤構築（1-2日）

#### 高優先度 ⭐⭐⭐
- [x] 設計文書作成
- [ ] Flask アプリケーション基盤作成
- [ ] Blueprint による機能分割実装
- [ ] APIクライアント基底クラス実装
- [ ] 基本レイアウト・ナビゲーション構築

#### 実装手順
1. **app.py の作成**
   ```python
   # メインアプリケーションファイル
   # Flask-SocketIO統合
   # Blueprint登録
   ```

2. **config.py の実装**
   ```python
   # 環境別設定管理
   # バックエンドAPI URL設定
   # セキュリティ設定
   ```

3. **blueprints/ ディレクトリ作成**
   ```
   blueprints/
   ├── dashboard.py     # ダッシュボード
   ├── drone_control.py # ドローン制御
   ├── model_training.py # モデル訓練  
   ├── tracking.py      # 追跡制御
   └── settings.py      # 設定管理
   ```

4. **基本テンプレート作成**
   ```
   templates/
   ├── base.html           # 基底テンプレート
   ├── dashboard.html      # ダッシュボード
   ├── drone_control.html  # ドローン制御画面
   ├── model_training.html # モデル訓練画面
   ├── tracking.html       # 追跡制御画面
   └── settings.html       # 設定画面
   ```

### フェーズ2: ドローン制御機能（2-3日）

#### 高優先度 ⭐⭐⭐
- [ ] ドローン接続・切断機能
- [ ] 基本飛行制御（離陸・着陸・緊急停止）
- [ ] 手動移動制御
- [ ] リアルタイム状態表示

#### 実装手順
1. **APIクライアント実装**
   ```python
   # services/api_client.py
   class DroneAPIClient:
       async def connect_drone()
       async def takeoff()
       async def move_drone()
       # その他制御メソッド
   ```

2. **Flask-SocketIO セットアップ**
   ```python
   # services/websocket_service.py  
   class RealtimeService:
       def start_monitoring()
       def _monitor_loop()
   ```

3. **ドローン制御UI実装**
   ```javascript
   // static/js/drone-control.js
   class DroneController:
       async toggleConnection()
       async takeoff()
       async move()
   ```

### フェーズ3: カメラ・ストリーミング（1-2日）

#### 中優先度 ⭐⭐
- [ ] ビデオストリーミング表示
- [ ] カメラ制御（開始・停止）
- [ ] ストリーミング品質調整

#### 実装手順
1. **カメラストリーム統合**
   ```python
   # バックエンドの /camera/stream エンドポイント連携
   # HTMLでのストリーム表示
   ```

2. **ストリーミング制御UI**
   ```javascript
   // カメラ開始・停止ボタン
   // ストリーム品質設定
   ```

### フェーズ4: モデル訓練機能（2-3日）

#### 高優先度 ⭐⭐⭐
- [ ] ファイルアップロード機能
- [ ] モデル訓練開始・進捗監視
- [ ] モデル一覧表示・管理

#### 実装手順
1. **ファイルアップロード実装**
   ```python
   # multipart/form-data 処理
   # ファイル検証・サイズ制限
   # 進捗表示機能
   ```

2. **モデル管理UI**
   ```html
   <!-- ドラッグ&ドロップアップロード -->
   <!-- モデル一覧テーブル -->
   <!-- 訓練進捗バー -->
   ```

### フェーズ5: 追跡制御機能（2-3日）

#### 高優先度 ⭐⭐⭐
- [ ] 追跡開始・停止制御
- [ ] 対象オブジェクト選択
- [ ] 追跡状態リアルタイム監視

#### 実装手順
1. **追跡制御API実装**
   ```python
   # 追跡開始・停止エンドポイント
   # 追跡状態取得エンドポイント
   ```

2. **追跡UI実装**
   ```javascript
   // 対象選択ドロップダウン
   // 追跡モード設定
   // リアルタイム状態表示
   ```

### フェーズ6: 統合・テスト・最適化（1-2日）

#### 中優先度 ⭐⭐
- [ ] 全機能統合テスト
- [ ] エラーハンドリング強化
- [ ] パフォーマンス最適化
- [ ] レスポンシブデザイン調整

## 技術的実装詳細

### 必要なライブラリ追加
```txt
# 現在のrequirements.txtに追加
Flask-SocketIO==5.3.4
aiohttp==3.8.5
websockets==11.0.3
python-multipart==0.0.6
Werkzeug==3.0.1
```

### ディレクトリ構造
```
frontend/admin/
├── app.py                    # メインアプリケーション（既存main.pyから移行）
├── config.py                 # 設定管理
├── requirements.txt          # 依存関係（更新）
├── blueprints/               # 機能別ブループリント
│   ├── __init__.py
│   ├── dashboard.py          # ダッシュボード
│   ├── drone_control.py      # ドローン制御  
│   ├── model_training.py     # モデル訓練
│   ├── tracking.py           # 追跡制御
│   └── settings.py           # 設定管理
├── services/                 # バックエンド連携サービス
│   ├── __init__.py
│   ├── api_client.py         # REST API クライアント
│   ├── websocket_service.py  # WebSocket サービス
│   └── file_service.py       # ファイル操作サービス
├── models/                   # データモデル
│   ├── __init__.py
│   ├── drone_state.py        # ドローン状態モデル
│   ├── tracking_state.py     # 追跡状態モデル
│   └── model_info.py         # AIモデル情報
├── utils/                    # ユーティリティ
│   ├── __init__.py
│   ├── validators.py         # バリデーション
│   ├── formatters.py         # データフォーマット
│   └── exceptions.py         # カスタム例外
├── templates/                # HTMLテンプレート（既存更新）
│   ├── base.html            # 基底テンプレート
│   ├── dashboard.html       # ダッシュボード（既存index.html更新）
│   ├── drone_control.html   # ドローン制御
│   ├── model_training.html  # モデル訓練
│   ├── tracking.html        # 追跡制御
│   └── settings.html        # 設定
├── static/                  # 静的ファイル
│   ├── css/
│   │   ├── main.css
│   │   └── components.css
│   ├── js/
│   │   ├── main.js
│   │   ├── websocket.js
│   │   ├── drone-control.js
│   │   ├── model-training.js
│   │   └── tracking.js
│   └── images/
└── tmp/                     # 一時ファイル・設計文書
    ├── admin_frontend_design_plan.md      # 設計計画書
    ├── technical_specification.md         # 技術仕様書
    ├── sample_app_structure.py           # サンプル実装
    ├── sample_dashboard_template.html     # サンプルHTMLテンプレート
    └── implementation_roadmap.md          # 実装ロードマップ（このファイル）
```

## 既存ファイルからの変更点

### 1. main.py → app.py への移行
- 既存の `main.py` を `app.py` に名前変更
- Flask-SocketIO統合
- Blueprint登録機能追加
- 設定管理外部化

### 2. templates/index.html の大幅更新
- Bootstrap 5統合
- リアルタイム表示機能追加
- WebSocket通信対応
- レスポンシブデザイン対応

### 3. requirements.txt の更新
- Flask-SocketIO追加
- aiohttp追加（非同期HTTP通信）
- その他必要ライブラリ追加

## 実装上の注意点

### セキュリティ対策
1. **CSRF保護**: Flask-WTFによるCSRFトークン
2. **入力検証**: 全ての入力データの検証
3. **ファイルアップロード制限**: サイズ・形式制限
4. **エラー情報の適切な処理**: 詳細エラーの非公開

### パフォーマンス最適化
1. **非同期処理**: 重い処理の非同期実行
2. **キャッシュ**: 頻繁にアクセスするデータのキャッシュ
3. **WebSocket最適化**: 必要最小限のデータ送信
4. **ファイルサイズ最適化**: CSS/JS minification

### 運用考慮事項
1. **ログ管理**: 適切なログレベル設定
2. **エラー監視**: エラー発生時の通知機能
3. **設定外部化**: 環境変数による設定管理
4. **ドキュメント**: 運用手順書作成

## 次のステップ

### 即座に実行すべき作業
1. **既存main.pyのバックアップ**
2. **新しいapp.py作成**
3. **Blueprint構造実装**
4. **基本的なAPIクライアント作成**

### 段階的実装順序
1. フェーズ1（基盤）→ フェーズ2（制御）→ フェーズ4（モデル）→ フェーズ5（追跡）→ フェーズ3（カメラ）→ フェーズ6（統合）

### 品質保証
- 各フェーズ完了後の動作確認
- エラーハンドリングのテスト
- レスポンシブデザインの確認
- 実機でのテスト

---

この実装ロードマップに従って開発を進めることで、効率的かつ品質の高い管理用フロントエンドシステムを構築できます。