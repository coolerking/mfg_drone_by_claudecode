# MFG ドローン - 自動追従撮影システム

Tello EDU ドローンを使用した自動追従撮影システムです。物体認識AI、実機制御、シミュレーション機能を統合した包括的なドローン制御プラットフォームを提供します。

## 概要（Description）

このプロジェクトは、Tello EDU ドローンを使って移動する対象物を自動的に追跡・撮影するシステムです。手動制御から自動追従まで、幅広い撮影ニーズに対応できる高機能なドローン制御システムを実現しています。

### 主な特徴
- **実機・シミュレーション統合**: 開発からテスト、本番運用まで一貫したワークフロー
- **AI物体追跡**: YOLOv8ベースの高精度物体検出・追跡システム
- **Webベース管理**: React製の直感的な管理インターフェース
- **自然言語制御**: Claude統合によるAI支援ドローン制御
- **包括的監視**: リアルタイム状態監視・アラート機能

### 解決する課題
- 手動でのドローン撮影における操作の複雑さ
- 移動する被写体の追跡・撮影の困難さ
- 複数ドローンの同時管理・制御の複雑さ
- 実機テストの効率化（シミュレーション環境での事前検証）

## 目次（Table of Contents）

1. [概要（Description）](#概要description)
2. [インストール方法（Installation）](#インストール方法installation)
3. [使い方（Usage）](#使い方usage)
4. [動作環境・要件（Requirements）](#動作環境要件requirements)
5. [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
6. [貢献方法（Contributing）](#貢献方法contributing)
7. [ライセンス（License）](#ライセンスlicense)
8. [謝辞・参考情報（Acknowledgements/References）](#謝辞参考情報acknowledgementsreferences)
9. [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## インストール方法（Installation）

### 前提条件
- **Python 3.9+** (バックエンド)
- **Node.js 18+** (フロントエンド)
- **Docker & Docker Compose** (本番環境)
- **Tello EDU ドローン** (実機テスト用、オプション)

### 基本セットアップ

#### 1. リポジトリのクローン
```bash
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode
```

#### 2. バックエンドのセットアップ
```bash
cd backend
pip install -r requirements.txt

# 設定ファイルの作成
cp config/drone_config.yaml.example config/drone_config.yaml

# 環境変数の設定
export DRONE_MODE=auto              # auto, simulation, real
export TELLO_AUTO_DETECT=true       # 自動検出有効
export LOG_LEVEL=INFO

# サーバーの起動
python start_api_server.py
```

#### 3. フロントエンドのセットアップ
```bash
cd frontend
npm install
npm run dev
```

#### 4. MCPサーバーのセットアップ（オプション）
```bash
cd mcp-server
pip install -r requirements.txt
python start_mcp_server.py
```

### Docker環境での起動
```bash
# 開発環境
docker-compose -f docker-compose.dev.yml up

# 本番環境
docker-compose -f docker-compose.prod.yml up
```

## 使い方（Usage）

### 基本的な使用方法

#### 1. システムの起動
```bash
# バックエンドAPI
cd backend && python start_api_server.py

# フロントエンド
cd frontend && npm run dev

# ブラウザでアクセス
# http://localhost:3000
```

#### 2. ドローンの接続
- **シミュレーションモード**: 自動的に仮想ドローンが利用可能
- **実機モード**: Tello EDU をWiFi接続して自動検出
- **ハイブリッドモード**: 実機・シミュレーション同時制御

#### 3. 基本操作
- **手動制御**: Web画面のコントロールパネルでドローンを操作
- **物体追跡**: カメラ画像から追跡対象を学習・設定
- **自動飛行**: 設定したモデルに基づいて自動追従開始

### サンプルコード

#### APIクライアント例
```python
import requests

# ドローン一覧取得
response = requests.get('http://localhost:8000/api/drones')
drones = response.json()

# ドローンの離陸
drone_id = drones[0]['id']
requests.post(f'http://localhost:8000/api/drones/{drone_id}/takeoff')

# 前進指示
requests.post(f'http://localhost:8000/api/drones/{drone_id}/move', 
              json={'direction': 'forward', 'distance': 50})
```

#### WebSocket接続例
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('ドローン状態:', data);
};

// コマンド送信
ws.send(JSON.stringify({
    type: 'takeoff',
    drone_id: 'drone_001'
}));
```

## 動作環境・要件（Requirements）

### ハードウェア要件

#### 最小構成
- **CPU**: Intel i3 または AMD Ryzen 3 以上
- **メモリ**: 8GB RAM
- **ストレージ**: 10GB 以上の空き容量
- **ネットワーク**: WiFi 802.11n 以上

#### 推奨構成
- **CPU**: Intel i5 または AMD Ryzen 5 以上
- **メモリ**: 16GB RAM
- **ストレージ**: SSD 20GB 以上
- **GPU**: NVIDIA GTX 1060 以上（AI処理加速用）

### ソフトウェア要件

#### バックエンド
- **OS**: Windows 10/11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.9以上
- **必要ライブラリ**: 
  - FastAPI 0.104.1+
  - OpenCV 4.8.1+
  - djitellopy 2.5.0+
  - ultralytics 8.0.196+ (YOLOv8)

#### フロントエンド
- **Node.js**: 18.0以上
- **必要ライブラリ**:
  - React 18.2+
  - TypeScript 4.9+
  - Material-UI 5.11+
  - Redux Toolkit 1.9+

#### データベース
- **PostgreSQL**: 13以上 (推奨)
- **Redis**: 6以上 (キャッシュ・セッション用)

### ネットワーク要件
- **LAN環境**: 1Gbps以上推奨
- **Tello EDU接続**: 2.4GHz WiFi
- **インターネット**: モデル更新・外部API用

## ディレクトリ構成（Directory Structure）

```
mfg_drone_by_claudecode/
├── backend/                    # バックエンドAPI
│   ├── api_server/            # FastAPI アプリケーション
│   │   ├── main.py           # メインアプリケーション
│   │   ├── api/              # APIエンドポイント
│   │   ├── core/             # コアサービス
│   │   └── models/           # データモデル
│   ├── src/                   # シミュレーションシステム
│   ├── tests/                 # テストスイート
│   ├── config/               # 設定ファイル
│   ├── docs/                 # ドキュメント
│   └── requirements.txt      # Python依存関係
├── frontend/                   # フロントエンド
│   ├── src/                   # Reactアプリケーション
│   │   ├── components/       # UIコンポーネント
│   │   ├── pages/            # ページコンポーネント
│   │   ├── services/         # API呼び出し
│   │   └── hooks/            # カスタムフック
│   ├── package.json          # Node.js依存関係
│   └── docs/                 # フロントエンド仕様
├── mcp-server/                # MCPサーバー
│   ├── src/                   # MCPサーバーコード
│   ├── tests/                # テスト
│   └── requirements.txt      # Python依存関係
├── shared/                    # 共有リソース
│   ├── api-specs/            # OpenAPI仕様
│   └── config/               # 共通設定
├── tests/                     # 統合テスト
├── docs/                      # プロジェクトドキュメント
├── scripts/                   # ビルド・デプロイスクリプト
├── docker-compose.yml        # Docker設定
└── README.md                 # このファイル
```

### 主要コンポーネント

- **backend/api_server/**: FastAPIベースのメインAPIサーバー
- **frontend/**: React + TypeScriptのWeb管理インターフェース  
- **mcp-server/**: Claude統合のためのMCPサーバー
- **shared/**: 共通定義・設定ファイル

## 貢献方法（Contributing）

このプロジェクトへの貢献を歓迎します。以下の手順に従ってください：

### 開発ワークフロー

1. **リポジトリのフォーク**
   ```bash
   # GitHub上でフォーク後
   git clone https://github.com/your-username/mfg_drone_by_claudecode.git
   ```

2. **開発ブランチの作成**
   ```bash
   git checkout -b feature/new-feature
   ```

3. **開発・テスト**
   ```bash
   # バックエンドテスト
   cd backend && python -m pytest tests/

   # フロントエンドテスト
   cd frontend && npm test
   ```

4. **コミット・プッシュ**
   ```bash
   git commit -m "Add: 新機能の追加"
   git push origin feature/new-feature
   ```

5. **プルリクエスト作成**
   - 変更内容の詳細説明
   - テスト結果の報告
   - 関連issueのリンク

### 開発ガイドライン

- **コーディング規約**: PEP8 (Python), ESLint (TypeScript)
- **テスト**: 新機能には必ず単体テストを追加
- **ドキュメント**: APIの変更時はOpenAPI仕様も更新
- **レビュー**: プルリクエストには必ずレビューが必要

### 報告・質問

- **バグ報告**: GitHub Issues にてバグレポートを作成
- **機能要求**: GitHub Issues にて機能要求を作成
- **質問**: GitHub Discussions または Issues を利用

## ライセンス（License）

このプロジェクトは MIT ライセンスの下で公開されています。

```
MIT License

Copyright (c) 2025 Tasuku Hori

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

詳細は [LICENSE](LICENSE) ファイルをご参照ください。

## 謝辞・参考情報（Acknowledgements/References）

### 利用技術・ライブラリ

- **[DJI Tello EDU](https://www.ryzerobotics.com/jp/tello-edu)**: 実機ドローンプラットフォーム
- **[djitellopy](https://github.com/damiafuentes/DJITelloPy)**: Python Tello SDKライブラリ
- **[FastAPI](https://fastapi.tiangolo.com/)**: 高性能WebAPIフレームワーク
- **[React](https://react.dev/)**: フロントエンドUIライブラリ
- **[YOLOv8](https://github.com/ultralytics/ultralytics)**: 物体検出AIモデル
- **[OpenCV](https://opencv.org/)**: コンピュータビジョンライブラリ

### 参考プロジェクト

- **[TelloPy](https://github.com/hanyazou/TelloPy)**: Tello制御の先駆的実装
- **[OpenDroneMap](https://www.opendronemap.org/)**: ドローン画像処理参考
- **[AirSim](https://github.com/Microsoft/AirSim)**: ドローンシミュレーション参考

### 開発支援

- **[Claude Code](https://claude.ai/code)**: AI支援開発環境
- **[GitHub Copilot](https://copilot.github.com/)**: コーディング支援
- **[Cursor](https://cursor.sh/)**: AI統合開発環境

## 更新履歴（Changelog/History）

### Version 1.0.0 - Phase 6 (2025-01-15)
- ✅ **実機統合**: Tello EDU実機制御機能の完全統合
- ✅ **ハイブリッド運用**: 実機・シミュレーション同時制御
- ✅ **自動検出**: LAN内ドローン自動発見機能
- ✅ **API拡張**: 実機制御用API追加（100%後方互換性）
- ✅ **包括的テスト**: 実機・シミュレーション統合テストスイート

### Version 0.9.0 - Phase 5 (2024-12-20)
- ✅ **Webダッシュボード**: リアルタイム監視インターフェース
- ✅ **Docker化**: 本番環境対応コンテナ構成
- ✅ **包括的監視**: Prometheus + Grafana統合

### Version 0.8.0 - Phase 4 (2024-12-10)
- ✅ **セキュリティ**: API認証・レート制限・セキュリティヘッダー
- ✅ **アラート**: 閾値ベース監視・通知システム
- ✅ **パフォーマンス**: システム監視・最適化

### Version 0.7.0 - Phase 3 (2024-11-25)
- ✅ **ビジョンAI**: YOLOv8物体検出・追跡システム
- ✅ **自動追従**: リアルタイム物体追従機能
- ✅ **データセット管理**: 学習データ作成・管理システム

### Version 0.6.0 - Phase 2 (2024-11-10)
- ✅ **WebSocket**: リアルタイム双方向通信
- ✅ **カメラ制御**: 仮想カメラストリーミング
- ✅ **並行処理**: 複数ドローン同時制御

### Version 0.5.0 - Phase 1 (2024-10-25)
- ✅ **基盤システム**: FastAPI + React基盤構築
- ✅ **ドローンシミュレーション**: 3D物理シミュレーション
- ✅ **基本制御**: 離着陸・移動・回転制御
- ✅ **RESTful API**: OpenAPI仕様準拠API設計

---

**🚁 Happy Flying!**