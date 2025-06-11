# 用語集

## 概要

MFG Drone Backend API システムで使用される専門用語、技術用語、略語を体系的に定義します。

## ドローン関連用語

### 基本用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **ドローン** | Drone | 無人航空機。本システムではDJI Tello EDUを指す |
| **クアッドコプター** | Quadcopter | 4つのローターを持つマルチコプター型ドローン |
| **ホバリング** | Hovering | 空中の一点で静止飛行を維持する動作 |
| **離陸** | Takeoff | 地上から空中へ上昇する動作 |
| **着陸** | Landing | 空中から地上へ降下する動作 |
| **緊急停止** | Emergency Stop | 全モーターを即座に停止する安全機能 |

### 飛行制御用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **ピッチ** | Pitch | 機体の前後方向の傾き角度 |
| **ロール** | Roll | 機体の左右方向の傾き角度 |
| **ヨー** | Yaw | 機体の水平回転角度 |
| **スロットル** | Throttle | 上下方向の推力制御 |
| **ラダー** | Rudder | ヨー軸回転制御 |
| **エレベーター** | Elevator | ピッチ軸制御 |
| **エルロン** | Aileron | ロール軸制御 |

### センサー用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **IMU** | Inertial Measurement Unit | 慣性計測装置（加速度センサー+ジャイロスコープ） |
| **ToF** | Time of Flight | 飛行時間測定による距離センサー |
| **バロメーター** | Barometer | 気圧センサー（高度測定用） |
| **オドメトリ** | Odometry | 移動距離・位置推定 |
| **6DOF** | 6 Degrees of Freedom | 6自由度（X,Y,Z軸移動 + ピッチ,ロール,ヨー回転） |

## AI・画像処理用語

### 物体認識用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **物体検出** | Object Detection | 画像内の特定物体を認識・位置特定する技術 |
| **物体追跡** | Object Tracking | 連続フレーム間での物体位置を追跡する技術 |
| **バウンディングボックス** | Bounding Box | 検出された物体を囲む矩形領域 |
| **信頼度** | Confidence Score | AI モデルの予測確信度（0.0-1.0） |
| **閾値** | Threshold | 判定基準となる境界値 |
| **推論** | Inference | 訓練済みモデルによる予測処理 |

### 機械学習用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **訓練データ** | Training Data | モデル学習に使用するデータセット |
| **検証データ** | Validation Data | モデル性能評価用データ |
| **過学習** | Overfitting | 訓練データに過度に適合し汎化性能が低下する現象 |
| **精度** | Accuracy | 正解率（正しい予測数 / 全予測数） |
| **再現率** | Recall | 実際の正例のうち正しく検出できた割合 |
| **適合率** | Precision | 検出した正例のうち実際に正しかった割合 |
| **F1スコア** | F1 Score | 適合率と再現率の調和平均 |

### 画像処理用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **フレーム** | Frame | 映像の1コマ |
| **FPS** | Frames Per Second | 1秒間のフレーム数 |
| **解像度** | Resolution | 画像の画素数（幅×高さ） |
| **ビットレート** | Bitrate | 1秒間のデータ転送量 |
| **エンコード** | Encoding | 映像データの符号化 |
| **ストリーミング** | Streaming | リアルタイム映像配信 |

## 技術・システム用語

### ネットワーク用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **API** | Application Programming Interface | アプリケーション間のインターフェース |
| **REST** | Representational State Transfer | HTTPベースのWebAPIアーキテクチャスタイル |
| **WebSocket** | WebSocket | 双方向リアルタイム通信プロトコル |
| **UDP** | User Datagram Protocol | コネクションレス型通信プロトコル |
| **TCP** | Transmission Control Protocol | コネクション型信頼性通信プロトコル |
| **CORS** | Cross-Origin Resource Sharing | 異なるオリジン間のリソース共有制御 |

### プログラミング用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **非同期処理** | Asynchronous Processing | ノンブロッキングな並行処理 |
| **コルーチン** | Coroutine | 協調的マルチタスキングの実行単位 |
| **依存性注入** | Dependency Injection | オブジェクトの依存関係を外部から注入する設計パターン |
| **ミドルウェア** | Middleware | リクエスト/レスポンス処理の中間層 |
| **バリデーション** | Validation | 入力データの妥当性検証 |
| **シリアライゼーション** | Serialization | オブジェクトのデータ形式変換 |

### アーキテクチャ用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **レイヤードアーキテクチャ** | Layered Architecture | 機能を層状に分離した設計 |
| **マイクロサービス** | Microservices | 小規模で独立したサービス群による構成 |
| **モノリス** | Monolith | 単一の実行可能単位として構成されたアプリケーション |
| **ヘキサゴナルアーキテクチャ** | Hexagonal Architecture | ポート&アダプターパターンによる設計 |
| **SOLID原則** | SOLID Principles | オブジェクト指向設計の5つの基本原則 |

## システム固有用語

### MFG Drone システム用語

| 用語 | 定義 |
|------|------|
| **Backend API** | Raspberry Pi 5上で動作するドローン制御バックエンドサービス |
| **Admin Frontend** | システム管理者向けのWebアプリケーション |
| **User Frontend** | 一般ユーザー向けの映像視聴アプリケーション |
| **自動追従** | AI による物体認識を使用したドローンの自動追従飛行機能 |
| **ミッションパッド** | Tello EDU の位置認識用マーカー |

### 運用用語

| 用語 | 定義 |
|------|------|
| **ヘルスチェック** | システムの正常性を確認する監視機能 |
| **フェイルセーフ** | 障害時に安全な状態に移行する機能 |
| **グレースフルデグラデーション** | 部分的障害時でも基本機能を維持する設計 |
| **ホットスワップ** | システム停止せずにコンポーネントを交換する機能 |

## 略語・頭字語

### 技術関連略語

| 略語 | 正式名称 | 意味 |
|------|---------|------|
| **API** | Application Programming Interface | アプリケーション プログラミング インターフェース |
| **HTTP** | HyperText Transfer Protocol | ハイパーテキスト転送プロトコル |
| **JSON** | JavaScript Object Notation | JavaScript オブジェクト記法 |
| **SDK** | Software Development Kit | ソフトウェア開発キット |
| **IDE** | Integrated Development Environment | 統合開発環境 |
| **CLI** | Command Line Interface | コマンドライン インターフェース |
| **GUI** | Graphical User Interface | グラフィカル ユーザー インターフェース |
| **URL** | Uniform Resource Locator | 統一資源位置指定子 |
| **URI** | Uniform Resource Identifier | 統一資源識別子 |
| **UUID** | Universally Unique Identifier | 汎用一意識別子 |

### ドローン関連略語

| 略語 | 正式名称 | 意味 |
|------|---------|------|
| **UAV** | Unmanned Aerial Vehicle | 無人航空機 |
| **UAS** | Unmanned Aircraft System | 無人航空機システム |
| **VTOL** | Vertical Take-Off and Landing | 垂直離着陸 |
| **GPS** | Global Positioning System | 全地球測位システム |
| **RTK** | Real-Time Kinematic | リアルタイム キネマティック測位 |
| **LiDAR** | Light Detection and Ranging | レーザー測距 |

### AI・機械学習略語

| 略語 | 正式名称 | 意味 |
|------|---------|------|
| **AI** | Artificial Intelligence | 人工知能 |
| **ML** | Machine Learning | 機械学習 |
| **DL** | Deep Learning | 深層学習 |
| **CNN** | Convolutional Neural Network | 畳み込みニューラルネットワーク |
| **RNN** | Recurrent Neural Network | 再帰型ニューラルネットワーク |
| **YOLO** | You Only Look Once | 物体検出アルゴリズム |
| **OpenCV** | Open Source Computer Vision Library | オープンソース コンピュータビジョン ライブラリ |

### ネットワーク・通信略語

| 略語 | 正式名称 | 意味 |
|------|---------|------|
| **WiFi** | Wireless Fidelity | 無線LAN規格 |
| **TCP** | Transmission Control Protocol | 伝送制御プロトコル |
| **UDP** | User Datagram Protocol | ユーザー データグラム プロトコル |
| **IP** | Internet Protocol | インターネット プロトコル |
| **DHCP** | Dynamic Host Configuration Protocol | 動的ホスト構成プロトコル |
| **NAT** | Network Address Translation | ネットワーク アドレス変換 |
| **VPN** | Virtual Private Network | 仮想専用ネットワーク |

### 開発・運用略語

| 略語 | 正式名称 | 意味 |
|------|---------|------|
| **CI/CD** | Continuous Integration/Continuous Deployment | 継続的インテグレーション/継続的デプロイメント |
| **TDD** | Test-Driven Development | テスト駆動開発 |
| **BDD** | Behavior-Driven Development | 振る舞い駆動開発 |
| **MVP** | Minimum Viable Product | 実用最小限の製品 |
| **SLA** | Service Level Agreement | サービス レベル アグリーメント |
| **RPO** | Recovery Point Objective | 目標復旧時点 |
| **RTO** | Recovery Time Objective | 目標復旧時間 |
| **MTTR** | Mean Time To Repair | 平均修復時間 |
| **MTBF** | Mean Time Between Failures | 平均故障間隔 |

## 品質・性能指標用語

### パフォーマンス指標

| 用語 | 英語 | 定義 |
|------|------|------|
| **レイテンシー** | Latency | 応答遅延時間 |
| **スループット** | Throughput | 単位時間あたりの処理量 |
| **QPS** | Queries Per Second | 1秒間のクエリ処理数 |
| **TPS** | Transactions Per Second | 1秒間のトランザクション処理数 |
| **可用性** | Availability | システムが利用可能な時間の割合 |
| **信頼性** | Reliability | システムが正常動作し続ける能力 |

### 測定単位

| 用語 | 英語 | 定義 |
|------|------|------|
| **パーセンタイル** | Percentile | 分布における位置を示す統計値 |
| **平均** | Mean/Average | 算術平均値 |
| **中央値** | Median | 50パーセンタイル値 |
| **標準偏差** | Standard Deviation | データのばらつきを示す指標 |

## セキュリティ用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **認証** | Authentication | ユーザーまたはシステムの身元確認 |
| **認可** | Authorization | リソースへのアクセス権限制御 |
| **暗号化** | Encryption | データの秘匿化 |
| **ハッシュ化** | Hashing | 固定長の値への一方向変換 |
| **ソルト** | Salt | ハッシュ化時のランダム値 |
| **トークン** | Token | 認証・認可に使用される文字列 |
| **JWT** | JSON Web Token | JSON ベースのトークン形式 |
| **CSRF** | Cross-Site Request Forgery | クロスサイト リクエスト フォージェリ |
| **XSS** | Cross-Site Scripting | クロスサイト スクリプティング |

## エラー・例外用語

| 用語 | 英語 | 定義 |
|------|------|------|
| **例外** | Exception | プログラム実行中の異常事態 |
| **ハンドリング** | Handling | 例外やエラーの処理 |
| **スタックトレース** | Stack Trace | エラー発生時の呼び出し履歴 |
| **デバッグ** | Debug | プログラムの問題を特定・修正する作業 |
| **ログ** | Log | システムの動作記録 |
| **トレース** | Trace | 処理の詳細な実行履歴 |

## 単位・測定値

### 物理単位

| 単位 | 英語 | 定義 |
|------|------|------|
| **cm** | Centimeter | センチメートル（長さ） |
| **m/s** | Meter per Second | メートル毎秒（速度） |
| **cm/s** | Centimeter per Second | センチメートル毎秒（速度） |
| **度** | Degree | 角度の単位 |
| **g** | Gravity | 重力加速度の単位 |
| **hPa** | Hectopascal | ヘクトパスカル（気圧） |
| **℃** | Celsius | 摂氏温度 |
| **%** | Percent | パーセント |

### 情報単位

| 単位 | 英語 | 定義 |
|------|------|------|
| **Byte** | Byte | 情報量の基本単位（8bit） |
| **KB** | Kilobyte | キロバイト（1024 Byte） |
| **MB** | Megabyte | メガバイト（1024 KB） |
| **GB** | Gigabyte | ギガバイト（1024 MB） |
| **bps** | Bits per Second | ビット毎秒（通信速度） |
| **Mbps** | Megabits per Second | メガビット毎秒 |

## 参考資料・関連リンク

### 公式ドキュメント
- [Tello SDK Documentation](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenCV Documentation](https://docs.opencv.org/)

### 規格・標準
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 6455 - WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [OpenAPI Specification](https://swagger.io/specification/)

### 業界用語集
- [IEEE Standards](https://standards.ieee.org/)
- [ISO/IEC Standards](https://www.iso.org/standards.html)