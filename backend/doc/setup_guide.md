# セットアップ手順

## 概要

MFG Drone Backend APIの開発環境構築から本番環境デプロイまでの詳細手順を説明します。

## 前提条件

### ハードウェア要件

| 項目 | 開発環境 | 本番環境（Raspberry Pi 5） |
|------|---------|-------------------------|
| **CPU** | x64, 2コア以上 | ARM64, 4コア |
| **メモリ** | 4GB以上 | 4GB以上 |
| **ストレージ** | 10GB以上 | 32GB以上（SD Card） |
| **ネットワーク** | WiFi必須 | WiFi必須 |

### ソフトウェア要件

| ソフトウェア | バージョン | 用途 |
|-------------|-----------|------|
| **Python** | 3.12以上 | ランタイム |
| **Git** | 2.0以上 | バージョン管理 |
| **WiFi接続** | - | ドローン通信 |

### 対応ドローン

- **Tello EDU** (DJI製)
- Tello (基本機能のみ対応)

## 開発環境セットアップ

### 1. リポジトリクローン

```bash
git clone https://github.com/your-org/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/backend
```

### 2. Python環境セットアップ

#### 2.1 Python 3.12インストール確認

```bash
python --version
# Python 3.12.x が表示されることを確認
```

#### 2.2 仮想環境作成

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 2.3 依存関係インストール

```bash
# 本番依存関係
pip install -e .

# 開発依存関係
pip install -e ".[dev]"

# または requirements.txtから
pip install -r requirements.txt
pip install -r test_requirements.txt
```

### 3. 設定ファイル準備

#### 3.1 環境変数設定

```bash
# .env ファイル作成
touch .env
```

`.env` ファイル内容例:
```bash
# アプリケーション設定
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true

# ドローン設定  
DRONE_TIMEOUT=5
USE_MOCK_DRONE=true

# ログ設定
LOG_LEVEL=INFO
LOG_FORMAT=json

# テスト設定
TEST_MODE=true
```

#### 3.2 ログディレクトリ作成

```bash
mkdir -p logs
mkdir -p data/models
mkdir -p data/images
mkdir -p data/videos
```

### 4. 開発ツール設定

#### 4.1 pre-commitフック設定

```bash
pre-commit install
```

#### 4.2 VSCode設定（オプション）

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"]
}
```

### 5. 動作確認

#### 5.1 テスト実行

```bash
# 全テスト実行
python -m pytest

# カバレッジ付きテスト
python -m pytest --cov=. --cov-report=html

# 特定テストのみ
python -m pytest tests/test_connection.py -v
```

#### 5.2 アプリケーション起動

```bash
# 開発サーバー起動
python main.py

# または uvicorn直接起動
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 5.3 API動作確認

```bash
# ヘルスチェック
curl http://localhost:8000/health

# OpenAPI仕様確認
curl http://localhost:8000/openapi.json

# ブラウザでSwagger UI確認
# http://localhost:8000/docs
```

## 本番環境セットアップ（Raspberry Pi 5）

### 1. Raspberry Pi OS準備

#### 1.1 OS イメージ書き込み

1. **Raspberry Pi Imager** をダウンロード
2. **Raspberry Pi OS Lite (64-bit)** を選択
3. SSH有効化、WiFi設定を事前設定
4. microSD カードに書き込み

#### 1.2 初期セットアップ

```bash
# SSH接続
ssh pi@192.168.1.100

# システム更新
sudo apt update && sudo apt upgrade -y

# 必要パッケージインストール
sudo apt install -y git python3.12 python3.12-venv \
  python3-pip build-essential cmake \
  libopencv-dev python3-opencv \
  libhdf5-dev libatlas-base-dev
```

### 2. アプリケーションデプロイ

#### 2.1 ユーザー・ディレクトリ作成

```bash
# アプリケーション用ユーザー作成
sudo useradd -m -s /bin/bash mfgdrone
sudo usermod -aG sudo mfgdrone

# アプリケーションディレクトリ準備
sudo mkdir -p /opt/mfgdrone
sudo chown mfgdrone:mfgdrone /opt/mfgdrone
```

#### 2.2 コードデプロイ

```bash
# ユーザー切り替え
sudo su - mfgdrone

# リポジトリクローン
cd /opt/mfgdrone
git clone https://github.com/your-org/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/backend

# Python仮想環境作成
python3.12 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -e .
```

#### 2.3 本番設定

本番用 `.env` ファイル:
```bash
# 本番設定
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false

# ドローン設定（実機モード）
USE_MOCK_DRONE=false
DRONE_TIMEOUT=10

# ログ設定
LOG_LEVEL=WARNING
LOG_FORMAT=json
LOG_FILE=/opt/mfgdrone/logs/app.log

# セキュリティ
SECRET_KEY=your-secret-key-here
```

### 3. システムサービス設定

#### 3.1 systemd サービス作成

`/etc/systemd/system/mfgdrone.service`:
```ini
[Unit]
Description=MFG Drone Backend API
After=network.target

[Service]
Type=exec
User=mfgdrone
Group=mfgdrone
WorkingDirectory=/opt/mfgdrone/mfg_drone_by_claudecode/backend
Environment=PATH=/opt/mfgdrone/mfg_drone_by_claudecode/backend/venv/bin
ExecStart=/opt/mfgdrone/mfg_drone_by_claudecode/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 3.2 サービス有効化

```bash
# サービス登録・有効化
sudo systemctl daemon-reload
sudo systemctl enable mfgdrone
sudo systemctl start mfgdrone

# 状態確認
sudo systemctl status mfgdrone

# ログ確認
sudo journalctl -u mfgdrone -f
```

### 4. ネットワーク設定

#### 4.1 WiFi設定確認

```bash
# 現在のWiFi接続確認
iwconfig

# WiFi接続設定
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

#### 4.2 静的IP設定（オプション）

`/etc/dhcpcd.conf` に追加:
```bash
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

#### 4.3 ファイアウォール設定

```bash
# UFW インストール・設定
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000
sudo ufw enable
```

## ドローン接続設定

### 1. Tello EDU セットアップ

#### 1.1 ドローン準備

1. **バッテリー充電**: フル充電を確認
2. **電源ON**: ドローン底面のボタンを3秒長押し
3. **WiFi確認**: LEDが黄色点滅→青点灯を確認

#### 1.2 WiFi接続

```bash
# Tello WiFiネットワーク検索
sudo iwlist wlan0 scan | grep TELLO

# Tello WiFiに接続
sudo wpa_cli
> add_network
0
> set_network 0 ssid "TELLO-XXXXXX"
> set_network 0 key_mgmt NONE
> enable_network 0
> save_config
> quit
```

### 2. 接続テスト

#### 2.1 基本通信テスト

```bash
# Tello IPアドレスにping
ping 192.168.10.1

# Tello UDP通信テスト
echo "command" | nc -u 192.168.10.1 8889
```

#### 2.2 API接続テスト

```bash
# バックエンドAPI経由接続テスト
curl -X POST http://localhost:8000/drone/connect

# 接続確認
curl http://localhost:8000/drone/sensors/battery
```

## トラブルシューティング

### 1. 一般的な問題

#### Python依存関係エラー

```bash
# キャッシュクリア
pip cache purge

# 仮想環境再作成
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e .
```

#### ポートが使用中

```bash
# ポート使用プロセス確認
sudo lsof -i :8000

# プロセス終了
sudo kill -9 <PID>
```

### 2. ドローン接続問題

#### WiFi接続失敗

```bash
# WiFiインターフェース再起動
sudo ifdown wlan0
sudo ifup wlan0

# ドローン再起動
# 電源ボタン長押しで再起動
```

#### 通信タイムアウト

```bash
# ファイアウォール確認
sudo ufw status

# ルーティング確認
route -n
```

### 3. パフォーマンス問題

#### メモリ不足

```bash
# メモリ使用量確認
free -h

# スワップファイル作成（Raspberry Pi）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 監視・メンテナンス

### 1. ログ監視

```bash
# アプリケーションログ
tail -f /opt/mfgdrone/logs/app.log

# システムログ
sudo journalctl -u mfgdrone -f

# システムリソース監視
htop
```

### 2. 定期メンテナンス

#### 自動更新スクリプト

`/opt/mfgdrone/update.sh`:
```bash
#!/bin/bash
cd /opt/mfgdrone/mfg_drone_by_claudecode
git pull origin main
cd backend
source venv/bin/activate
pip install -e .
sudo systemctl restart mfgdrone
```

#### cron設定

```bash
# 毎日午前2時に更新チェック
echo "0 2 * * * /opt/mfgdrone/update.sh" | sudo crontab -
```

### 3. バックアップ

```bash
# 設定ファイルバックアップ
sudo tar -czf backup-$(date +%Y%m%d).tar.gz \
  /opt/mfgdrone/mfg_drone_by_claudecode/backend/.env \
  /etc/systemd/system/mfgdrone.service \
  /opt/mfgdrone/logs/
```

## セキュリティ考慮事項

### 1. ネットワークセキュリティ

- 不要なポートを閉じる
- 定期的なパスワード変更
- SSH鍵認証の使用

### 2. アプリケーションセキュリティ

- 機密情報の環境変数化
- ログの適切なローテーション
- 定期的なセキュリティ更新

### 3. 物理セキュリティ

- Raspberry Pi の物理的保護
- SD カードの定期的バックアップ
- ドローンの安全な保管