# 用語集

## 概要

MFG Drone Backend APIシステムで使用される専門用語、技術用語、略語の定義を整理しています。

## ドローン関連用語

### 基本用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **ドローン** | Drone | 無人航空機（UAV: Unmanned Aerial Vehicle） |
| **クアッドコプター** | Quadcopter | 4つのプロペラを持つマルチローター型ドローン |
| **Tello EDU** | Tello EDU | DJI製の教育用小型ドローン、プログラミング制御対応 |
| **SDK** | Software Development Kit | ソフトウェア開発キット、ドローン制御用API |
| **djitellopy** | djitellopy | Tello SDK用のPython wrapper ライブラリ |

### 飛行制御用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **離陸** | Takeoff | ドローンが地上から飛び立つ動作 |
| **着陸** | Landing | ドローンが地上に降りる動作 |
| **ホバリング** | Hovering | 空中で位置を保持する動作 |
| **ピッチ** | Pitch | 機首の上下方向の角度（X軸回転） |
| **ロール** | Roll | 機体の左右方向の傾き（Y軸回転） |
| **ヨー** | Yaw | 機首の左右方向の角度（Z軸回転） |
| **高度** | Altitude | 地上からの高さ |
| **座標移動** | Coordinate Movement | X,Y,Z座標を指定した移動 |

### センサー関連用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **IMU** | Inertial Measurement Unit | 慣性計測装置（加速度・角速度センサー） |
| **気圧センサー** | Barometric Sensor | 大気圧から高度を測定するセンサー |
| **TOF** | Time of Flight | 飛行時間測定による距離センサー |
| **加速度** | Acceleration | 速度の変化率（m/s²） |
| **角速度** | Angular Velocity | 回転の速度（deg/s） |
| **ジャイロスコープ** | Gyroscope | 角速度を測定するセンサー |

## カメラ・映像関連用語

### 映像処理用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **FPV** | First Person View | 一人称視点、ドローン搭載カメラからの映像 |
| **ストリーミング** | Streaming | リアルタイム映像配信 |
| **フレームレート** | Frame Rate | 1秒間の映像フレーム数（fps: frames per second） |
| **解像度** | Resolution | 映像の画素数（例: 720p, 1080p） |
| **レイテンシー** | Latency | 映像の遅延時間 |
| **エンコーディング** | Encoding | 映像データの符号化・圧縮 |

### 画像認識用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **オブジェクト検出** | Object Detection | 画像内の物体を検出・認識する技術 |
| **物体追跡** | Object Tracking | 動画内で物体を継続的に追跡する技術 |
| **バウンディングボックス** | Bounding Box | 検出した物体を囲む矩形枠 |
| **信頼度** | Confidence | AI検出結果の確信度（0.0〜1.0） |
| **ROI** | Region of Interest | 関心領域、処理対象の画像領域 |
| **機械学習** | Machine Learning | データから自動的にパターンを学習する技術 |

## AI・機械学習用語

### モデル関連

| 用語 | 英語 | 定義 |
|------|------|------|
| **訓練データ** | Training Data | モデル学習に使用するデータセット |
| **推論** | Inference | 学習済みモデルによる予測・判定 |
| **精度** | Accuracy | モデルの正解率 |
| **過学習** | Overfitting | 訓練データに過度に適合し汎化性能が下がる現象 |
| **データセット** | Dataset | 学習・テスト用のデータの集合 |
| **ラベリング** | Labeling | データに正解タグを付ける作業 |

### 深層学習用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **CNN** | Convolutional Neural Network | 畳み込みニューラルネットワーク |
| **エポック** | Epoch | 全訓練データを1回学習する単位 |
| **バッチサイズ** | Batch Size | 1回の学習で処理するデータ数 |
| **学習率** | Learning Rate | モデルパラメータの更新幅 |
| **損失関数** | Loss Function | モデルの誤差を計算する関数 |

## システム・技術用語

### アーキテクチャ用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **レイヤードアーキテクチャ** | Layered Architecture | 層構造による責任分離設計 |
| **依存性注入** | Dependency Injection | オブジェクトの依存関係を外部から注入する設計 |
| **REST API** | Representational State Transfer | HTTPベースのWebサービス設計原則 |
| **WebSocket** | WebSocket | 双方向リアルタイム通信プロトコル |
| **非同期処理** | Asynchronous Processing | ノンブロッキングな並行処理 |

### FastAPI関連用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **ASGI** | Asynchronous Server Gateway Interface | 非同期Webサーバーインターフェース |
| **Pydantic** | Pydantic | Pythonのデータバリデーションライブラリ |
| **OpenAPI** | OpenAPI Specification | REST API仕様記述標準（旧Swagger） |
| **Uvicorn** | Uvicorn | ASGI対応のPython Webサーバー |
| **ミドルウェア** | Middleware | リクエスト・レスポンス処理の中間層 |

### データベース・ストレージ用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **永続化** | Persistence | データを永続的に保存すること |
| **シリアライゼーション** | Serialization | オブジェクトをデータ形式に変換すること |
| **ファイルシステム** | File System | ファイルの保存・管理システム |
| **キャッシュ** | Cache | 高速アクセスのための一時的データ保存 |

## ネットワーク・通信用語

### プロトコル関連

| 用語 | 英語 | 定義 |
|------|------|------|
| **UDP** | User Datagram Protocol | 軽量で高速な通信プロトコル |
| **TCP** | Transmission Control Protocol | 信頼性の高い通信プロトコル |
| **HTTP/HTTPS** | HyperText Transfer Protocol | Web通信の標準プロトコル |
| **CORS** | Cross-Origin Resource Sharing | 異なるオリジン間のリソース共有設定 |
| **WiFi** | Wireless Fidelity | 無線LAN通信規格 |

### セキュリティ用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **JWT** | JSON Web Token | JSON形式の認証トークン |
| **認証** | Authentication | ユーザー身元確認 |
| **認可** | Authorization | アクセス権限の確認 |
| **サニタイゼーション** | Sanitization | 入力データの無害化処理 |
| **バリデーション** | Validation | 入力データの妥当性検証 |

## 開発・運用用語

### テスト関連

| 用語 | 英語 | 定義 |
|------|------|------|
| **単体テスト** | Unit Test | 個別コンポーネントのテスト |
| **統合テスト** | Integration Test | コンポーネント間連携のテスト |
| **E2Eテスト** | End-to-End Test | 全体システムの動作テスト |
| **モック** | Mock | テスト用の偽オブジェクト |
| **スタブ** | Stub | テスト用の代替実装 |
| **カバレッジ** | Coverage | テストがカバーするコード範囲 |

### CI/CD用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **CI** | Continuous Integration | 継続的インテグレーション |
| **CD** | Continuous Deployment | 継続的デプロイメント |
| **リンター** | Linter | コード品質チェックツール |
| **フォーマッター** | Formatter | コード整形ツール |
| **型チェッカー** | Type Checker | 静的型検査ツール |

### 品質管理用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **コード品質** | Code Quality | コードの保守性・可読性指標 |
| **リファクタリング** | Refactoring | 機能を変えずにコード構造を改善 |
| **技術的負債** | Technical Debt | 短期的解決による将来的メンテナンスコスト |
| **パフォーマンス** | Performance | システムの処理性能・応答速度 |

## システム固有用語

### MFGドローンシステム専用

| 用語 | 定義 |
|------|------|
| **自動追従撮影** | ドローンが対象物を自動的に追跡しながら撮影する機能 |
| **物体中心制御** | 検出した物体を画面中央に維持する制御方式 |
| **追跡感度** | 物体追跡の反応感度設定（0.1〜1.0） |
| **追跡モード** | center（中心維持）、follow（追従）等の動作モード |
| **フォールバック** | 追跡対象を見失った際の代替動作 |

### ミッションパッド関連

| 用語 | 英語 | 定義 |
|------|------|------|
| **ミッションパッド** | Mission Pad | Tello EDU用の位置マーカー |
| **パッドID** | Pad ID | 各ミッションパッドの識別子（m1〜m8） |
| **相対位置** | Relative Position | ミッションパッドを基準とした座標 |
| **精密制御** | Precision Control | ミッションパッドによる高精度位置制御 |

## 略語・頭字語一覧

| 略語 | 正式名称 | 日本語 |
|------|---------|--------|
| **API** | Application Programming Interface | アプリケーションプログラミングインターフェース |
| **SDK** | Software Development Kit | ソフトウェア開発キット |
| **UAV** | Unmanned Aerial Vehicle | 無人航空機 |
| **FPV** | First Person View | 一人称視点 |
| **IMU** | Inertial Measurement Unit | 慣性計測装置 |
| **TOF** | Time of Flight | 飛行時間測定 |
| **ROI** | Region of Interest | 関心領域 |
| **CNN** | Convolutional Neural Network | 畳み込みニューラルネットワーク |
| **ML** | Machine Learning | 機械学習 |
| **AI** | Artificial Intelligence | 人工知能 |
| **JSON** | JavaScript Object Notation | JSONデータ形式 |
| **HTTP** | HyperText Transfer Protocol | ハイパーテキスト転送プロトコル |
| **UDP** | User Datagram Protocol | ユーザーデータグラムプロトコル |
| **TCP** | Transmission Control Protocol | 伝送制御プロトコル |
| **CORS** | Cross-Origin Resource Sharing | オリジン間リソース共有 |
| **JWT** | JSON Web Token | JSON Webトークン |
| **ASGI** | Asynchronous Server Gateway Interface | 非同期サーバーゲートウェイインターフェース |
| **CRUD** | Create, Read, Update, Delete | 基本データ操作 |
| **REST** | Representational State Transfer | 表現状態転送 |
| **ORM** | Object-Relational Mapping | オブジェクト関係マッピング |
| **CI** | Continuous Integration | 継続的インテグレーション |
| **CD** | Continuous Deployment | 継続的デプロイメント |
| **TDD** | Test-Driven Development | テスト駆動開発 |
| **DI** | Dependency Injection | 依存性注入 |
| **IoC** | Inversion of Control | 制御の反転 |

## 単位・数値

### 距離・長さ

| 単位 | 説明 | 使用例 |
|------|------|--------|
| **cm** | センチメートル | ドローン移動距離指定 |
| **m** | メートル | 高度、座標位置 |
| **px** | ピクセル | 画像座標、バウンディングボックス |

### 角度・回転

| 単位 | 説明 | 使用例 |
|------|------|--------|
| **度 (deg)** | 角度の度数法表記 | 回転角度、姿勢角 |
| **rad** | ラジアン | 数学的角度表記 |

### 時間

| 単位 | 説明 | 使用例 |
|------|------|--------|
| **ms** | ミリ秒 | レイテンシー、タイムアウト |
| **fps** | フレーム毎秒 | 映像フレームレート |
| **Hz** | ヘルツ | センサー更新頻度 |

### 電気・バッテリー

| 単位 | 説明 | 使用例 |
|------|------|--------|
| **%** | パーセント | バッテリー残量 |
| **V** | ボルト | バッテリー電圧 |
| **℃** | 摂氏温度 | バッテリー・モーター温度 |

### データサイズ

| 単位 | 説明 | 使用例 |
|------|------|--------|
| **KB** | キロバイト | ファイルサイズ |
| **MB** | メガバイト | 画像・動画ファイル |
| **GB** | ギガバイト | ストレージ容量 |