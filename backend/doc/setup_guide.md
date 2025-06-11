# セットアップ手順

## 概要

MFG Drone Backend API の開発環境および本番環境（Raspberry Pi 5）のセットアップ手順を詳細に説明します。

## システム要件

### 開発環境要件

| 項目 | 要件 | 推奨 |
|------|------|------|
| **OS** | Windows 10/11, macOS 12+, Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| **Python** | 3.11+ | 3.12 |
| **メモリ** | 8GB+ | 16GB+ |
| **ストレージ** | 10GB+ 空き容量 | SSD推奨 |
| **ネットワーク** | WiFi 802.11n+ | WiFi 6対応 |

### 本番環境要件（Raspberry Pi 5）

| 項目 | 仕様 |
|------|------|
| **ハードウェア** | Raspberry Pi 5 (8GB RAM推奨) |
| **OS** | Raspberry Pi OS Lite 64-bit |
| **ストレージ** | microSD 64GB Class 10 + |
| **ネットワーク** | WiFi + Ethernet |
| **電源** | 5V/5A USB-C PD対応 |

## 開発環境セットアップ

### 1. Python環境の準備

#### Pythonインストール確認
```bash
python --version
# Python 3.11.0 以上であることを確認
```

#### pyenvを使用したPython管理（推奨）
```bash
# pyenvインストール（Linux/macOS）
curl https://pyenv.run | bash

# Pythonバージョンインストール
pyenv install 3.12.0
pyenv global 3.12.0
```

### 2. プロジェクトのクローン

```bash
# リポジトリクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/backend

# ブランチ確認
git branch -a
git checkout main
```

### 3. 仮想環境の作成

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート（Linux/macOS）
source venv/bin/activate

# 仮想環境アクティベート（Windows）
venv\Scripts\activate
```

### 4. 依存関係のインストール

```bash
# 本番依存関係インストール
pip install -r requirements.txt

# 開発・テスト用依存関係インストール
pip install -r test_requirements.txt

# インストール確認
pip list
```

### 5. 設定ファイルの準備

#### 設定ファイル作成
```bash
# 設定ディレクトリ作成
mkdir -p config

# 開発用設定ファイル作成
cat > config/development.py << EOF
# 開発環境設定
DEBUG = True
LOG_LEVEL = "DEBUG"
DRONE_SIMULATOR = True
API_HOST = "127.0.0.1"
API_PORT = 8000
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
EOF
```

#### 環境変数設定
```bash
# .envファイル作成
cat > .env << EOF
ENVIRONMENT=development
PYTHONPATH=.
LOG_LEVEL=DEBUG
DRONE_CONNECTION_TIMEOUT=10
VIDEO_STREAM_BUFFER_SIZE=1024
EOF
```

### 6. 開発サーバー起動

```bash
# FastAPIサーバー起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# または、Pythonスクリプトとして実行
python main.py
```

### 7. 開発環境確認

#### APIドキュメント確認
```bash
# ブラウザで以下URLにアクセス
# http://localhost:8000/docs      # Swagger UI
# http://localhost:8000/redoc     # ReDoc
# http://localhost:8000/health    # ヘルスチェック
```

#### 基本API動作確認
```bash
# curlでの動作確認
curl http://localhost:8000/health
curl -X POST http://localhost:8000/drone/connect
```

## Raspberry Pi 5 本番環境セットアップ

### 1. Raspberry Pi OS インストール

#### OS イメージ準備
```bash
# Raspberry Pi Imagerダウンロード・インストール
# https://www.raspberrypi.org/software/

# OS選択: Raspberry Pi OS Lite (64-bit)
# SSH有効化、WiFi設定を事前設定
```

#### 初期設定
```bash
# SSH接続
ssh pi@192.168.1.100

# システム更新
sudo apt update && sudo apt upgrade -y

# 必要パッケージインストール
sudo apt install -y git vim wget curl build-essential
```

### 2. Python 3.12 インストール

```bash
# 依存関係インストール
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
    liblzma-dev python3-openssl git

# pyenvインストール
curl https://pyenv.run | bash

# .bashrc設定追加
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Python 3.12インストール
pyenv install 3.12.0
pyenv global 3.12.0
```

### 3. システム依存関係インストール

```bash
# OpenCV用システムライブラリ
sudo apt install -y python3-opencv libopencv-dev
sudo apt install -y libhdf5-dev libhdf5-serial-dev
sudo apt install -y libqtgui4 libqtwebkit4 libqt4-test

# その他の依存関係
sudo apt install -y libjpeg-dev libtiff5-dev libpng-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libgtk2.0-dev libcanberra-gtk-module
sudo apt install -y libxvidcore-dev libx264-dev
```

### 4. プロジェクトデプロイ

```bash
# プロジェクトクローン
cd /home/pi
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/backend

# 仮想環境作成
python -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. 本番用設定

#### 設定ファイル作成
```bash
# 本番設定作成
cat > config/production.py << EOF
# 本番環境設定
DEBUG = False
LOG_LEVEL = "INFO"
DRONE_SIMULATOR = False
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = [
    "http://192.168.1.101:5000",  # Admin Frontend
    "http://192.168.1.102:5000",  # User Frontend
]
MAX_WORKERS = 4
KEEPALIVE_TIMEOUT = 120
EOF
```

#### 環境変数設定
```bash
cat > .env << EOF
ENVIRONMENT=production
PYTHONPATH=/home/pi/mfg_drone_by_claudecode/backend
LOG_LEVEL=INFO
DRONE_CONNECTION_TIMEOUT=15
VIDEO_STREAM_BUFFER_SIZE=2048
MODEL_STORAGE_PATH=/home/pi/models
LOG_FILE_PATH=/var/log/mfg_drone
EOF
```

### 6. ログディレクトリ設定

```bash
# ログディレクトリ作成
sudo mkdir -p /var/log/mfg_drone
sudo chown pi:pi /var/log/mfg_drone

# ログローテーション設定
sudo cat > /etc/logrotate.d/mfg_drone << EOF
/var/log/mfg_drone/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    copytruncate
    notifempty
}
EOF
```

### 7. Systemdサービス設定

```bash
# サービスファイル作成
sudo cat > /etc/systemd/system/mfg-drone-api.service << EOF
[Unit]
Description=MFG Drone Backend API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/mfg_drone_by_claudecode/backend
Environment=PATH=/home/pi/mfg_drone_by_claudecode/backend/venv/bin
ExecStart=/home/pi/mfg_drone_by_claudecode/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# サービス有効化・起動
sudo systemctl daemon-reload
sudo systemctl enable mfg-drone-api
sudo systemctl start mfg-drone-api

# サービス状態確認
sudo systemctl status mfg-drone-api
```

### 8. ファイアウォール設定

```bash
# UFWインストール・設定
sudo apt install -y ufw

# 基本ポリシー設定
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 必要ポート開放
sudo ufw allow ssh
sudo ufw allow 8000/tcp  # API サーバー

# ファイアウォール有効化
sudo ufw enable

# 設定確認
sudo ufw status
```

## ネットワーク設定

### 1. 静的IPアドレス設定

```bash
# dhcpcd.confファイル編集
sudo vim /etc/dhcpcd.conf

# 以下を追加
# interface wlan0
# static ip_address=192.168.1.100/24
# static routers=192.168.1.1
# static domain_name_servers=192.168.1.1 8.8.8.8

# ネットワーク再起動
sudo systemctl restart dhcpcd
```

### 2. WiFi設定

```bash
# WiFi設定確認
sudo raspi-config
# > Network Options > Wi-Fi

# 接続確認
iwconfig
ping google.com
```

## トラブルシューティング

### 開発環境での一般的な問題

#### Python バージョン問題
```bash
# Pythonバージョン確認
python --version
which python

# pyenvでの切り替え
pyenv versions
pyenv local 3.12.0
```

#### 依存関係インストールエラー
```bash
# pip更新
pip install --upgrade pip setuptools wheel

# キャッシュクリア
pip cache purge

# 個別インストール
pip install --no-cache-dir opencv-python
```

#### ポート競合
```bash
# ポート使用状況確認
netstat -tulpn | grep :8000
lsof -i :8000

# プロセス終了
kill -9 <PID>
```

### Raspberry Pi 特有の問題

#### メモリ不足
```bash
# スワップ増設
sudo dphys-swapfile swapoff
sudo vim /etc/dphys-swapfile
# CONF_SWAPSIZE=1024 に変更
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### OpenCV インストールエラー
```bash
# 事前コンパイル済みパッケージ使用
pip install opencv-python-headless

# システムパッケージ使用
sudo apt install python3-opencv
```

#### systemd サービスエラー
```bash
# ログ確認
sudo journalctl -u mfg-drone-api -f

# サービス再起動
sudo systemctl restart mfg-drone-api

# 設定確認
sudo systemctl show mfg-drone-api
```

## 開発ツール設定

### 1. IDE設定（VS Code）

#### 拡張機能インストール
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.pylint",
    "ms-toolsai.jupyter"
  ]
}
```

#### launch.json設定
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Debug",
      "type": "python",
      "request": "launch",
      "program": "main.py",
      "console": "integratedTerminal",
      "env": {
        "ENVIRONMENT": "development"
      }
    }
  ]
}
```

### 2. pre-commit フック設定

```bash
# pre-commit インストール
pip install pre-commit

# .pre-commit-config.yaml 作成
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
EOF

# フック有効化
pre-commit install
```

## 性能最適化

### 1. Raspberry Pi 最適化

```bash
# GPU メモリ分割調整
sudo raspi-config
# > Advanced Options > Memory Split > 128

# CPUガバナー設定
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# I/O スケジューラ最適化
echo 'deadline' | sudo tee /sys/block/mmcblk0/queue/scheduler
```

### 2. Python 最適化

```bash
# バイトコード最適化
export PYTHONOPTIMIZE=2

# GC調整
export PYTHONHASHSEED=0

# uvicorn設定最適化
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --loop uvloop \
  --http httptools
```

## 本番環境チェックリスト

### セキュリティ
- [ ] SSH鍵認証設定済み
- [ ] デフォルトパスワード変更済み
- [ ] ファイアウォール設定済み
- [ ] 不要サービス無効化済み

### 設定
- [ ] 静的IPアドレス設定済み
- [ ] systemdサービス設定済み
- [ ] ログローテーション設定済み
- [ ] 環境変数設定済み

### 監視
- [ ] ヘルスチェック動作確認済み
- [ ] ログ出力確認済み
- [ ] リソース使用量監視設定済み
- [ ] アラート設定済み（将来）

### 動作確認
- [ ] API応答確認済み
- [ ] ドローン接続テスト済み
- [ ] 映像ストリーミング確認済み
- [ ] 負荷テスト実施済み