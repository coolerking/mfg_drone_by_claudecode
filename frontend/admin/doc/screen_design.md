# 管理者用フロントエンド 画面設計

## 概要

MFG Drone Admin Frontend の画面設計では、管理者が直感的にドローン制御システムを操作できるUIを提供します。画面構成図と画面遷移図を通じて、ユーザビリティを重視した設計を示します。

## 画面構成図

### 全体レイアウト構成

```mermaid
graph TB
    subgraph "Admin Frontend Layout"
        Header[ヘッダー<br/>- システム名<br/>- 接続状態表示<br/>- アラート領域]
        
        subgraph "メインコンテンツエリア"
            Nav[ナビゲーション<br/>- ダッシュボード<br/>- ドローン制御<br/>- カメラ・映像<br/>- AI・追跡<br/>- システム監視<br/>- 設定管理]
            
            Content[コンテンツエリア<br/>- 各機能画面<br/>- リアルタイム情報表示<br/>- 操作パネル]
        end
        
        Footer[ステータスバー<br/>- ドローン状態<br/>- 接続情報<br/>- システム時刻]
    end

    Header --> Nav
    Nav --> Content
    Content --> Footer
    
    style Header fill:#e3f2fd
    style Nav fill:#e8f5e8
    style Content fill:#fff3e0
    style Footer fill:#fce4ec
```

### 詳細画面構成

```mermaid
graph LR
    subgraph "ヘッダー領域 (Fixed Top)"
        A1[MFG Drone Admin]
        A2[接続状態LED]
        A3[アラート表示]
    end
    
    subgraph "ナビゲーション領域 (Left Sidebar)"
        B1[ダッシュボード]
        B2[ドローン制御]
        B3[カメラ・映像]
        B4[AI・追跡]
        B5[システム監視]
        B6[設定管理]
    end
    
    subgraph "メインコンテンツ領域 (Center)"
        C1[機能別画面表示]
        C2[リアルタイムデータ]
        C3[操作コントロール]
        C4[ステータス表示]
    end
    
    subgraph "ステータスバー (Fixed Bottom)"
        D1[バッテリー: 85%]
        D2[高度: 120cm]
        D3[状態: 飛行中]
        D4[2025-06-17 23:57:45]
    end
    
    style A1 fill:#1976d2,color:#fff
    style A2 fill:#4caf50
    style A3 fill:#ff9800
```

## 個別画面設計

### 1. ダッシュボード画面

```mermaid
graph TB
    subgraph "Dashboard Layout"
        D1[システム概要<br/>- 接続状態<br/>- バッテリー<br/>- 飛行時間]
        
        D2[ライブ映像<br/>- ドローン映像<br/>- 解像度選択<br/>- 録画ボタン]
        
        D3[クイック操作<br/>- 離陸/着陸<br/>- 緊急停止<br/>- ホバリング]
        
        D4[システム監視<br/>- センサーデータ<br/>- 接続状況<br/>- アラート履歴]
    end
    
    D1 --> D2
    D2 --> D3
    D3 --> D4
```

### 2. ドローン制御画面

```mermaid
graph TB
    subgraph "Drone Control Layout"
        DC1[接続管理パネル<br/>- 接続/切断<br/>- 接続状態<br/>- 再接続]
        
        DC2[基本飛行制御<br/>- 離陸/着陸<br/>- 方向移動<br/>- 回転制御]
        
        DC3[高度制御<br/>- 座標指定<br/>- 速度設定<br/>- 経路表示]
        
        DC4[飛行状態表示<br/>- 現在位置<br/>- 速度<br/>- 姿勢角]
    end
    
    DC1 --> DC2
    DC2 --> DC3
    DC3 --> DC4
```

### 3. カメラ・映像画面

```mermaid
graph TB
    subgraph "Camera Control Layout"
        CC1[映像表示<br/>- メイン映像<br/>- フルスクリーン<br/>- 画質選択]
        
        CC2[撮影制御<br/>- 写真撮影<br/>- 動画録画<br/>- ファイル一覧]
        
        CC3[カメラ設定<br/>- 解像度<br/>- FPS<br/>- ビットレート]
        
        CC4[ストリーミング制御<br/>- 開始/停止<br/>- 品質調整<br/>- 遅延表示]
    end
    
    CC1 --> CC2
    CC2 --> CC3
    CC3 --> CC4
```

### 4. AI・追跡画面

```mermaid
graph TB
    subgraph "AI Tracking Layout"
        AI1[モデル管理<br/>- 訓練済みモデル一覧<br/>- 新規訓練<br/>- モデル選択]
        
        AI2[画像アップロード<br/>- ファイル選択<br/>- プレビュー<br/>- オブジェクト名入力]
        
        AI3[追跡制御<br/>- 追跡開始/停止<br/>- 追跡モード選択<br/>- 対象物体選択]
        
        AI4[追跡状態表示<br/>- 物体検出状況<br/>- 追跡精度<br/>- 位置情報]
    end
    
    AI1 --> AI2
    AI2 --> AI3
    AI3 --> AI4
```

### 5. システム監視画面

```mermaid
graph TB
    subgraph "System Monitor Layout"
        SM1[ドローン状態<br/>- バッテリー残量<br/>- 温度<br/>- 飛行時間]
        
        SM2[センサーデータ<br/>- 加速度<br/>- 姿勢角<br/>- 気圧・高度]
        
        SM3[ネットワーク状態<br/>- 接続品質<br/>- 遅延情報<br/>- データ転送量]
        
        SM4[ログ・履歴<br/>- イベントログ<br/>- エラー履歴<br/>- アラート履歴]
    end
    
    SM1 --> SM2
    SM2 --> SM3
    SM3 --> SM4
```

### 6. 設定管理画面

```mermaid
graph TB
    subgraph "Settings Layout"
        ST1[ドローン設定<br/>- WiFi設定<br/>- 飛行速度<br/>- 安全パラメータ]
        
        ST2[カメラ設定<br/>- デフォルト解像度<br/>- 録画品質<br/>- 保存先]
        
        ST3[システム設定<br/>- Backend URL<br/>- タイムアウト値<br/>- 更新間隔]
        
        ST4[ユーザー設定<br/>- 表示設定<br/>- 言語設定<br/>- テーマ設定]
    end
    
    ST1 --> ST2
    ST2 --> ST3
    ST3 --> ST4
```

## 画面遷移図

### メイン画面遷移フロー

```mermaid
graph TD
    Start([システム起動]) --> Dashboard[ダッシュボード]
    
    Dashboard --> DroneControl[ドローン制御]
    Dashboard --> Camera[カメラ・映像]
    Dashboard --> AITracking[AI・追跡]
    Dashboard --> Monitor[システム監視]
    Dashboard --> Settings[設定管理]
    
    DroneControl --> Connect{接続確認}
    Connect -->|Yes| FlightControl[飛行制御]
    Connect -->|No| ConnectionSetup[接続設定]
    ConnectionSetup --> Connect
    
    FlightControl --> Takeoff[離陸]
    FlightControl --> Movement[移動制御]
    FlightControl --> Landing[着陸]
    FlightControl --> Emergency[緊急停止]
    
    Camera --> StreamStart[ストリーミング開始]
    StreamStart --> LiveView[ライブ映像]
    LiveView --> Recording[録画]
    LiveView --> PhotoCapture[写真撮影]
    
    AITracking --> ModelManagement[モデル管理]
    ModelManagement --> TrainingStart[モデル訓練]
    ModelManagement --> TrackingControl[追跡制御]
    TrackingControl --> AutoTracking[自動追跡]
    
    Monitor --> StatusCheck[状態確認]
    StatusCheck --> AlertManagement[アラート管理]
    
    Settings --> DroneSettings[ドローン設定]
    Settings --> SystemSettings[システム設定]
    
    %% Return paths
    DroneControl --> Dashboard
    Camera --> Dashboard
    AITracking --> Dashboard
    Monitor --> Dashboard
    Settings --> Dashboard
    
    style Start fill:#4caf50
    style Dashboard fill:#2196f3,color:#fff
    style Emergency fill:#f44336,color:#fff
```

### 詳細操作フロー

#### ドローン制御フロー

```mermaid
graph TD
    DroneControlPage[ドローン制御画面] --> CheckConnection{接続状態確認}
    
    CheckConnection -->|未接続| ConnectDrone[ドローン接続]
    CheckConnection -->|接続済み| FlightMenu[飛行制御メニュー]
    
    ConnectDrone --> ConnectionSuccess{接続成功?}
    ConnectionSuccess -->|Yes| FlightMenu
    ConnectionSuccess -->|No| ConnectionError[エラー表示]
    ConnectionError --> ConnectDrone
    
    FlightMenu --> PreFlightCheck[離陸前チェック]
    PreFlightCheck --> TakeoffAction[離陸実行]
    TakeoffAction --> FlightControl[飛行制御]
    
    FlightControl --> BasicMovement[基本移動]
    FlightControl --> AdvancedMovement[高度移動]
    FlightControl --> LandingAction[着陸]
    FlightControl --> EmergencyStop[緊急停止]
    
    BasicMovement --> FlightControl
    AdvancedMovement --> FlightControl
    LandingAction --> FlightComplete[飛行完了]
    EmergencyStop --> SafetyStop[安全停止]
```

#### AI・追跡フロー

```mermaid
graph TD
    AITrackingPage[AI・追跡画面] --> ModelCheck{モデル確認}
    
    ModelCheck -->|なし| CreateModel[新規モデル作成]
    ModelCheck -->|あり| SelectModel[モデル選択]
    
    CreateModel --> UploadImages[画像アップロード]
    UploadImages --> SetObjectName[オブジェクト名設定]
    SetObjectName --> StartTraining[訓練開始]
    StartTraining --> TrainingProgress[訓練進捗監視]
    TrainingProgress --> TrainingComplete{訓練完了?}
    TrainingComplete -->|Yes| SelectModel
    TrainingComplete -->|No| TrainingProgress
    
    SelectModel --> ConfigureTracking[追跡設定]
    ConfigureTracking --> StartTracking[追跡開始]
    StartTracking --> TrackingActive[追跡実行中]
    
    TrackingActive --> ObjectDetected{物体検出?}
    ObjectDetected -->|Yes| TrackingSuccess[追跡成功]
    ObjectDetected -->|No| SearchMode[検索モード]
    
    TrackingSuccess --> TrackingActive
    SearchMode --> TrackingActive
    
    TrackingActive --> StopTracking[追跡停止]
    StopTracking --> TrackingComplete[追跡完了]
```

## 画面要素詳細仕様

### 共通UI要素

| 要素 | 仕様 | 備考 |
|------|------|------|
| ヘッダー高さ | 60px | 固定配置 |
| ナビゲーション幅 | 200px | 折りたたみ可能 |
| フッター高さ | 40px | 固定配置 |
| メインコンテンツ | 可変 | レスポンシブ対応 |

### カラーパレット

| 用途 | カラーコード | 説明 |
|------|-------------|------|
| プライマリ | #1976d2 | メインブランド色 |
| セカンダリ | #424242 | サブカラー |
| 成功 | #4caf50 | 接続成功・正常状態 |
| 警告 | #ff9800 | 注意・警告状態 |
| エラー | #f44336 | エラー・危険状態 |
| 背景 | #fafafa | ベース背景色 |

### 状態表示

#### 接続状態インジケーター

```mermaid
graph LR
    subgraph "Connection Status"
        Connected[🟢 接続済み]
        Connecting[🟡 接続中]
        Disconnected[🔴 切断]
        Error[❌ エラー]
    end
    
    style Connected fill:#4caf50,color:#fff
    style Connecting fill:#ff9800,color:#fff
    style Disconnected fill:#f44336,color:#fff
    style Error fill:#9c27b0,color:#fff
```

#### バッテリー表示

| 残量 | 表示色 | アイコン | アクション |
|------|--------|----------|-----------|
| 80-100% | 緑 | 🔋 | 通常運用 |
| 60-79% | 緑 | 🔋 | 通常運用 |
| 40-59% | 黄 | 🔋 | 注意監視 |
| 20-39% | オレンジ | ⚠️ | 着陸準備 |
| 0-19% | 赤 | 🚨 | 緊急着陸 |

## レスポンシブ設計

### ブレークポイント

| デバイス | 画面幅 | レイアウト調整 |
|----------|-------|---------------|
| Desktop | ≥1200px | フル機能表示 |
| Tablet | 768-1199px | ナビゲーション折りたたみ |
| Mobile | <768px | 単一画面表示 |

### モバイル対応

```mermaid
graph TB
    subgraph "Mobile Layout"
        MobileHeader[ヘッダー<br/>- ハンバーガーメニュー<br/>- ステータス表示]
        
        MobileContent[コンテンツ<br/>- 単一機能表示<br/>- スワイプ対応]
        
        MobileFooter[フッター<br/>- クイックアクション<br/>- 緊急停止]
    end
    
    MobileHeader --> MobileContent
    MobileContent --> MobileFooter
```

## ユーザビリティ要件

### アクセシビリティ
- **キーボード操作**: 全機能をキーボードで操作可能
- **スクリーンリーダー**: alt属性、aria-label完備
- **カラーバリアフリー**: 色以外の視覚的手がかりを提供

### 操作性
- **レスポンス時間**: 100ms以内（UI操作）
- **エラーハンドリング**: 明確なエラーメッセージと回復手順
- **確認ダイアログ**: 危険な操作には確認プロンプト

### 表示更新頻度
- **ライブ映像**: 30fps
- **センサーデータ**: 5Hz（200ms間隔）
- **システム状態**: 1Hz（1秒間隔）
- **バッテリー情報**: 0.1Hz（10秒間隔）