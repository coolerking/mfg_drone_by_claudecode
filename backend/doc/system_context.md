# システムコンテキストダイヤグラム

## 概要

MFG Drone Backend APIシステムの外部アクターとの関係、システム境界、データ交換フローを定義します。

## システムコンテキスト図

```mermaid
graph TB
    subgraph "システム境界"
        MFGDroneBackend[MFG Drone Backend API<br/>Tello EDU自動追従撮影システム<br/>バックエンド]
    end
    
    subgraph "外部アクター"
        Admin[管理者<br/>Admin User]
        GeneralUser[一般ユーザー<br/>General User]
        TelloDrone[Tello EDU<br/>ドローン]
        AdminFrontend[管理者フロントエンド<br/>Admin Frontend]
        UserFrontend[ユーザーフロントエンド<br/>User Frontend]
        iPad[iPad Air<br/>クライアントデバイス]
    end
    
    subgraph "外部システム"
        WiFiNetwork[WiFiネットワーク<br/>Home Router]
        FileSystem[ファイルシステム<br/>Raspberry Pi Storage]
    end
    
    Admin -.->|操作指示| AdminFrontend
    GeneralUser -.->|映像視聴| UserFrontend
    iPad -.->|タッチ操作| UserFrontend
    
    AdminFrontend <-->|HTTP/WebSocket<br/>制御コマンド・設定| MFGDroneBackend
    UserFrontend <-->|HTTP/WebSocket<br/>映像ストリーム要求| MFGDroneBackend
    
    MFGDroneBackend <-->|UDP/WiFi<br/>飛行制御・センサーデータ| TelloDrone
    MFGDroneBackend <-->|TCP/UDP<br/>映像ストリーム| TelloDrone
    
    MFGDroneBackend --> WiFiNetwork
    MFGDroneBackend <--> FileSystem
    
    classDef actor fill:#e1f5fe
    classDef system fill:#fff3e0
    classDef external fill:#e8f5e8
    classDef main fill:#ffecb3
    
    class Admin,GeneralUser,TelloDrone,AdminFrontend,UserFrontend,iPad actor
    class MFGDroneBackend main
    class WiFiNetwork,FileSystem external
```

## 外部アクター定義

### 人間アクター

| アクター | 役割 | 権限レベル | 主な操作 |
|---------|------|-----------|---------|
| **管理者** | システム運用・設定管理 | 高 | <ul><li>ドローン接続・切断</li><li>飛行制御（離陸・着陸・移動）</li><li>AIモデル学習・管理</li><li>物体追跡開始・停止</li><li>システム設定変更</li></ul> |
| **一般ユーザー** | 映像視聴・基本操作 | 低 | <ul><li>リアルタイム映像視聴</li><li>録画映像再生</li><li>カメラ設定変更</li></ul> |

### システムアクター

| アクター | 種類 | 接続方式 | データ交換 |
|---------|------|---------|-----------|
| **管理者フロントエンド** | Webアプリケーション | HTTP/WebSocket | <ul><li>制御コマンド送信</li><li>ステータス取得</li><li>設定データ送受信</li><li>モデル学習結果取得</li></ul> |
| **ユーザーフロントエンド** | Webアプリケーション | HTTP/WebSocket | <ul><li>映像ストリーム受信</li><li>基本操作コマンド</li><li>カメラ設定</li></ul> |
| **Tello EDU** | 物理デバイス | WiFi (UDP/TCP) | <ul><li>飛行制御コマンド</li><li>センサーデータ</li><li>映像ストリーム</li><li>状態通知</li></ul> |
| **iPad Air** | クライアントデバイス | WiFi (HTTP) | <ul><li>Webブラウザ経由アクセス</li><li>タッチインターフェース</li></ul> |

## システム境界と責任範囲

### システム内部（責任範囲内）

```mermaid
graph TB
    subgraph "MFG Drone Backend API 責任範囲"
        API[REST API エンドポイント]
        WS[WebSocket ハンドラー]
        Service[ドローンサービス]
        Model[AIモデル管理]
        Stream[映像ストリーミング]
        Data[データ永続化]
    end
    
    classDef internal fill:#fff3e0
    class API,WS,Service,Model,Stream,Data internal
```

**責任事項:**
- ドローン制御APIの提供
- リアルタイム映像配信
- 物体認識・追跡機能
- AIモデル学習・管理
- システム状態管理
- エラーハンドリング
- ログ記録

### システム外部（責任範囲外）

**責任外事項:**
- フロントエンドUI実装
- クライアントデバイス管理
- ネットワークインフラ
- ドローンハードウェア制御
- 外部ストレージ管理

## データ交換フロー

### 制御データフロー

```mermaid
sequenceDiagram
    participant Admin as 管理者
    participant AdminFE as 管理者FE
    participant Backend as Backend API
    participant Drone as Tello EDU

    Admin->>AdminFE: 制御指示
    AdminFE->>Backend: HTTP POST /drone/takeoff
    Backend->>Drone: UDP コマンド送信
    Drone-->>Backend: UDP 応答
    Backend-->>AdminFE: JSON レスポンス
    AdminFE-->>Admin: 結果表示
```

### 映像データフロー

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant UserFE as ユーザーFE  
    participant Backend as Backend API
    participant Drone as Tello EDU

    User->>UserFE: 映像視聴要求
    UserFE->>Backend: WebSocket接続
    Backend->>Drone: 映像ストリーム開始
    loop リアルタイム配信
        Drone-->>Backend: 映像フレーム
        Backend-->>UserFE: WebSocket映像送信
        UserFE-->>User: 映像表示
    end
```

### センサーデータフロー

```mermaid
sequenceDiagram
    participant Backend as Backend API
    participant Drone as Tello EDU
    participant AdminFE as 管理者FE

    loop 定期ポーリング
        Backend->>Drone: センサーデータ要求
        Drone-->>Backend: バッテリー・高度・姿勢角
        Backend->>Backend: データ処理・検証
    end
    
    AdminFE->>Backend: GET /drone/sensors/battery
    Backend-->>AdminFE: センサーデータ JSON
```

## 外部システム連携

### ネットワーク依存関係

- **WiFiルーター**: 全デバイス間通信の中継
- **インターネット接続**: 外部リソースアクセス（オプション）
- **ローカルネットワーク**: 192.168.1.0/24 セグメント

### ストレージ依存関係

- **ローカルファイルシステム**: 
  - AIモデルファイル保存
  - 録画映像ファイル
  - ログファイル
  - 設定ファイル

## セキュリティ境界

```mermaid
graph TB
    subgraph "信頼境界内"
        Backend[Backend API]
        LocalFS[ローカルFS]
    end
    
    subgraph "部分信頼境界"
        AdminFE[管理者FE]
        UserFE[ユーザーFE]
        Drone[Tello EDU]
    end
    
    subgraph "信頼境界外"
        Internet[インターネット]
        External[外部デバイス]
    end
    
    Backend <--> AdminFE
    Backend <--> UserFE
    Backend <--> Drone
    Backend --- LocalFS
    
    classDef trusted fill:#c8e6c9
    classDef partial fill:#fff9c4
    classDef untrusted fill:#ffcdd2
    
    class Backend,LocalFS trusted
    class AdminFE,UserFE,Drone partial
    class Internet,External untrusted
```

**セキュリティ考慮事項:**
- CORS設定による外部アクセス制限
- エラー情報の適切なサニタイゼーション
- センサーデータの検証とバリデーション
- ファイルアップロードの制限とスキャン