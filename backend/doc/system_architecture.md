# システム構成図

## 概要

MFG Drone Backend APIは、Tello EDUドローンを制御し、リアルタイム映像配信と物体追跡機能を提供するバックエンドシステムです。

## 全体システム構成

```mermaid
graph TB
    subgraph "Windows PC環境"
        Admin[管理者フロントエンド<br/>Flask]
        User[ユーザーフロントエンド<br/>Flask]
        iPad[iPad Air<br/>Safari]
    end
    
    subgraph "Raspberry Pi 5環境"
        Backend[バックエンドAPI<br/>FastAPI]
        AI[AIモデル<br/>物体認識]
        Stream[映像ストリーミング<br/>OpenCV]
    end
    
    Drone[Tello EDU<br/>ドローン]
    Network[ホームネットワーク<br/>WiFi Router]
    
    Admin <--> Network
    User <--> Network
    iPad <--> Network
    Backend <--> Network
    Backend <--> Drone
    
    Backend --> AI
    Backend --> Stream
    Stream --> Backend
    AI --> Backend
    
    classDef frontend fill:#e1f5fe
    classDef backend fill:#fff3e0
    classDef hardware fill:#f3e5f5
    classDef network fill:#e8f5e8
    
    class Admin,User,iPad frontend
    class Backend,AI,Stream backend
    class Drone hardware
    class Network network
```

## バックエンド内部アーキテクチャ

```mermaid
graph TB
    subgraph "プレゼンテーション層"
        Router1[Connection Router]
        Router2[Flight Control Router]
        Router3[Movement Router]
        Router4[Camera Router]
        Router5[Sensors Router]
        Router6[Tracking Router]
        Router7[Mission Pad Router]
        Router8[Model Router]
        Router9[Settings Router]
        Router10[Advanced Movement Router]
    end
    
    subgraph "ビジネスロジック層"
        DroneService[Drone Service<br/>ドローン制御ビジネスロジック]
    end
    
    subgraph "データアクセス層"
        TelloAPI[djitellopy<br/>Tello SDK]
        OpenCV[OpenCV<br/>映像処理]
        AIModel[AI Model<br/>物体認識]
    end
    
    subgraph "外部デバイス"
        TelloDrone[Tello EDU]
    end
    
    Router1 --> DroneService
    Router2 --> DroneService
    Router3 --> DroneService
    Router4 --> DroneService
    Router5 --> DroneService
    Router6 --> DroneService
    Router7 --> DroneService
    Router8 --> DroneService
    Router9 --> DroneService
    Router10 --> DroneService
    
    DroneService --> TelloAPI
    DroneService --> OpenCV
    DroneService --> AIModel
    
    TelloAPI --> TelloDrone
    OpenCV --> TelloDrone
    
    classDef presentation fill:#e3f2fd
    classDef business fill:#fff3e0
    classDef data fill:#e8f5e8
    classDef external fill:#f3e5f5
    
    class Router1,Router2,Router3,Router4,Router5,Router6,Router7,Router8,Router9,Router10 presentation
    class DroneService business
    class TelloAPI,OpenCV,AIModel data
    class TelloDrone external
```

## データフロー図

```mermaid
graph LR
    subgraph "入力データ"
        Command[制御コマンド]
        Video[映像データ]
        Sensor[センサーデータ]
    end
    
    subgraph "データ処理"
        API[FastAPI<br/>エンドポイント]
        Service[DroneService<br/>ビジネスロジック]
        AI[AIモデル<br/>物体認識]
        CV[OpenCV<br/>映像処理]
    end
    
    subgraph "出力データ"
        Response[APIレスポンス]
        Stream[映像ストリーム]
        DroneCmd[ドローンコマンド]
    end
    
    Command --> API
    API --> Service
    Service --> DroneCmd
    
    Video --> CV
    CV --> AI
    AI --> Service
    Service --> Response
    
    Sensor --> Service
    Service --> Response
    
    CV --> Stream
    
    classDef input fill:#e1f5fe
    classDef process fill:#fff3e0
    classDef output fill:#e8f5e8
    
    class Command,Video,Sensor input
    class API,Service,AI,CV process
    class Response,Stream,DroneCmd output
```

## ネットワーク構成図

```mermaid
graph TB
    subgraph "ホームネットワーク (192.168.1.0/24)"
        Router[WiFi Router<br/>192.168.1.1]
        
        subgraph "Windows PC"
            AdminFE[管理者フロントエンド<br/>:5000]
            UserFE[ユーザーフロントエンド<br/>:5001]
        end
        
        subgraph "Raspberry Pi 5"
            Backend[バックエンドAPI<br/>192.168.1.100:8000]
        end
        
        Drone[Tello EDU<br/>192.168.10.1]
        iPad[iPad Air<br/>Safari]
    end
    
    Internet[インターネット]
    
    Router <--> Internet
    AdminFE <--> Router
    UserFE <--> Router
    Backend <--> Router
    iPad <--> Router
    
    Backend <--> Drone
    
    classDef network fill:#e8f5e8
    classDef device fill:#e1f5fe
    classDef drone fill:#f3e5f5
    
    class Router,Internet network
    class AdminFE,UserFE,Backend,iPad device
    class Drone drone
```

## 技術スタック詳細

| 層 | 技術 | バージョン | 用途 |
|---|---|---|---|
| **Webフレームワーク** | FastAPI | 0.115.0+ | REST API提供 |
| **ASGIサーバー** | Uvicorn | 0.32.0+ | 非同期HTTP処理 |
| **ドローン制御** | djitellopy | 2.5.0 | Tello SDK Python wrapper |
| **映像処理** | OpenCV | 4.10.0+ | カメラストリーミング・画像処理 |
| **数値計算** | NumPy | 2.1.0+ | 数値データ処理 |
| **画像処理** | Pillow | 11.0.0+ | 画像フォーマット変換 |
| **WebSocket** | websockets | 13.0+ | リアルタイム通信 |
| **ランタイム** | Python | 3.12+ | 実行環境 |

## アーキテクチャパターン

- **レイヤードアーキテクチャ**: プレゼンテーション層、ビジネスロジック層、データアクセス層の分離
- **依存性注入**: FastAPI Dependsを使用したサービス注入
- **シングルトンパターン**: DroneServiceの単一インスタンス管理
- **非同期処理**: async/awaitによる並行処理
- **RESTful API**: HTTP動詞とリソースベースのエンドポイント設計

## 非機能要件

- **パフォーマンス**: リアルタイム映像配信とドローン制御の低遅延
- **信頼性**: エラーハンドリングとフォールバック機能
- **スケーラビリティ**: 非同期処理による並行性
- **保守性**: テスト駆動開発とコード品質ツール
- **セキュリティ**: CORS設定とエラー情報の適切な管理