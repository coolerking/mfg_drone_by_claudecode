# ネットワーク設定ガイド - Tello EDU実機統合

## 概要
このガイドでは、Tello EDU実機ドローンをLAN環境に統合するためのネットワーク設定について詳細に説明します。

## 1. ネットワークアーキテクチャ

### 1.1 推奨ネットワーク構成

```
インターネット
    |
[ ルーター ] ━━━ [ 開発PC ]
    |              │
    |              │ (有線/WiFi)
    |              │
[ WiFi AP ] ━━━ [ Tello EDU ] × N台
    |
[ その他デバイス ]
```

### 1.2 IPアドレス設計

**推奨IPアドレス範囲:**
```
ネットワーク: 192.168.1.0/24
ルーター: 192.168.1.1
開発PC: 192.168.1.10
Tello EDU: 192.168.1.100-199 (予約範囲)
その他: 192.168.1.200-254
```

**Tello EDUデフォルト設定:**
```
AP Mode IP: 192.168.10.1
Station Mode: DHCP (自動取得)
```

## 2. 自動検出システム設定

### 2.1 UDP ブロードキャスト設定

**ポート設定:**
```yaml
# config/drone_config.yaml
global:
  network:
    scan_ports:
      command: 8889      # Tello コマンドポート
      status: 8890       # Tello 状態ポート
      video: 11111       # ビデオストリームポート
    broadcast_address: "192.168.1.255"
    scan_timeout: 5.0
    max_parallel_scans: 50
```

**自動検出設定:**
```yaml
network_service:
  auto_scan:
    enabled: true
    interval_seconds: 60
    retry_count: 3
    retry_delay: 2.0
  detection_methods:
    - ping_scan
    - udp_broadcast
    - tello_command_test
```

### 2.2 検出方式詳細

#### Pingスキャン
```python
# 設定例
ping_scan:
  enabled: true
  ip_ranges:
    - "192.168.1.100-199"
    - "192.168.10.1"     # APモード
  timeout: 1.0
  concurrent: 20
```

#### UDP ブロードキャスト
```python
# 設定例
udp_broadcast:
  enabled: true
  ports: [8889]
  message: "command"
  response_timeout: 2.0
  broadcast_addresses:
    - "192.168.1.255"
    - "192.168.10.255"
```

#### Tello専用検出
```python
# 設定例
tello_detection:
  enabled: true
  command_test: true
  battery_check: true
  serial_number_read: true
```

## 3. 手動IP指定設定

### 3.1 静的IP設定

**単一ドローン設定:**
```yaml
# config/drone_config.yaml
drones:
  - id: "tello_main"
    name: "メインドローン"
    mode: "real"
    ip_address: "192.168.1.100"
    auto_detect: false
    connection:
      timeout: 10
      retry_count: 3
      retry_delay: 2.0
```

**複数ドローン設定:**
```yaml
drones:
  - id: "tello_alpha"
    name: "アルファ隊"
    mode: "real"
    ip_address: "192.168.1.101"
    auto_detect: false
  - id: "tello_beta"
    name: "ベータ隊"
    mode: "real"
    ip_address: "192.168.1.102"
    auto_detect: false
  - id: "tello_gamma"
    name: "ガンマ隊"
    mode: "real"
    ip_address: "192.168.1.103"
    auto_detect: false
```

### 3.2 動的検出との併用

**ハイブリッド設定:**
```yaml
global:
  drone_mode: "hybrid"  # auto, real, simulation, hybrid

drones:
  # 固定IP指定ドローン
  - id: "tello_fixed_001"
    mode: "real"
    ip_address: "192.168.1.100"
    auto_detect: false
    priority: 1
  
  # 自動検出ドローン
  - id: "tello_auto_001"
    mode: "auto"
    ip_address: null
    auto_detect: true
    priority: 2
    scan_range: "192.168.1.110-120"
```

## 4. ファイアウォール設定

### 4.1 Linux (Ubuntu/Debian)

**UFWを使用した設定:**
```bash
# UFW有効化
sudo ufw enable

# 必要ポートの開放
sudo ufw allow 8889/udp    # Telloコマンド
sudo ufw allow 8890/udp    # Tello状態
sudo ufw allow 11111/udp   # ビデオストリーム
sudo ufw allow 8000/tcp    # APIサーバー

# 特定IPからのアクセスのみ許可（セキュリティ強化）
sudo ufw allow from 192.168.1.0/24 to any port 8889
sudo ufw allow from 192.168.1.0/24 to any port 8890
sudo ufw allow from 192.168.1.0/24 to any port 11111

# 設定確認
sudo ufw status verbose
```

**iptablesを使用した設定:**
```bash
# Tello関連ポート開放
sudo iptables -A INPUT -p udp --dport 8889 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 8890 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 11111 -s 192.168.1.0/24 -j ACCEPT

# 設定保存
sudo iptables-save > /etc/iptables/rules.v4
```

### 4.2 Windows

**Windows Defenderファイアウォール設定:**
```powershell
# PowerShellを管理者権限で実行

# 受信規則作成
New-NetFirewallRule -DisplayName "Tello Command Port" -Direction Inbound -Protocol UDP -LocalPort 8889 -Action Allow
New-NetFirewallRule -DisplayName "Tello Status Port" -Direction Inbound -Protocol UDP -LocalPort 8890 -Action Allow
New-NetFirewallRule -DisplayName "Tello Video Stream" -Direction Inbound -Protocol UDP -LocalPort 11111 -Action Allow

# 送信規則作成
New-NetFirewallRule -DisplayName "Tello Outbound" -Direction Outbound -Protocol UDP -RemotePort 8889,8890,11111 -Action Allow
```

### 4.3 macOS

**pfctl設定:**
```bash
# /etc/pf.anchors/tello.rules ファイル作成
echo "pass in proto udp from 192.168.1.0/24 to any port {8889, 8890, 11111}" | sudo tee /etc/pf.anchors/tello.rules

# pf.conf に追加
echo "load anchor \"tello\" from \"/etc/pf.anchors/tello.rules\"" | sudo tee -a /etc/pf.conf

# pfctl再読み込み
sudo pfctl -f /etc/pf.conf
```

## 5. ルーター設定

### 5.1 ポートフォワーディング

**外部アクセス用設定（開発環境）:**
```
外部ポート → 内部IP:ポート
8000 → 192.168.1.10:8000  (APIサーバー)
8889 → 192.168.1.100:8889 (Telloコマンド)
11111 → 192.168.1.100:11111 (ビデオストリーム)
```

### 5.2 DHCP予約設定

**Tello用IP予約:**
```
MACアドレス          IPアドレス      デバイス名
60:60:1F:XX:XX:XX → 192.168.1.100  Tello-001
60:60:1F:XX:XX:XY → 192.168.1.101  Tello-002
```

### 5.3 QoS設定

**トラフィック優先度設定:**
```
最高優先度: UDP 8889 (コマンド)
高優先度: UDP 11111 (ビデオ)
中優先度: TCP 8000 (API)
低優先度: その他
```

## 6. WiFiアクセスポイント設定

### 6.1 専用AP設定

**2.4GHz専用設定:**
```
SSID: DroneNetwork
セキュリティ: WPA2-PSK
パスワード: [強力なパスワード]
チャンネル: 1, 6, または 11
帯域幅: 20MHz
最大接続数: 20
```

**5GHz併用設定:**
```
2.4GHz: ドローン専用
5GHz: その他デバイス用
デュアルバンド分離: 有効
```

### 6.2 企業環境でのVLAN設定

**VLAN分離構成:**
```
VLAN 10: 管理用 (192.168.10.0/24)
VLAN 20: ドローン用 (192.168.20.0/24)  
VLAN 30: 開発用 (192.168.30.0/24)
```

**VLAN間通信設定:**
```yaml
# config/network_vlan.yaml
vlans:
  management:
    id: 10
    subnet: "192.168.10.0/24"
    gateway: "192.168.10.1"
  
  drones:
    id: 20
    subnet: "192.168.20.0/24"
    gateway: "192.168.20.1"
    dhcp_range: "192.168.20.100-199"
  
  development:
    id: 30
    subnet: "192.168.30.0/24"
    gateway: "192.168.30.1"

inter_vlan_rules:
  - from: "development"
    to: "drones"
    protocol: "udp"
    ports: [8889, 8890, 11111]
    action: "allow"
```

## 7. セキュリティ設定

### 7.1 アクセス制御

**IP許可リスト:**
```yaml
# config/security.yaml
access_control:
  enabled: true
  allowed_networks:
    - "192.168.1.0/24"
    - "10.0.0.0/8"
    - "172.16.0.0/12"
  
  blocked_networks:
    - "0.0.0.0/0"  # デフォルト拒否
  
  rate_limiting:
    enabled: true
    requests_per_minute: 120
    burst_size: 20
```

**認証設定:**
```yaml
authentication:
  enabled: true
  methods:
    - api_key
    - jwt_token
  
  api_keys:
    drone_controller: "sk-drone-ctrl-xxxxx"
    vision_system: "sk-vision-sys-xxxxx"
  
  jwt:
    secret_key: "your-secret-key"
    expiry_hours: 24
```

### 7.2 暗号化設定

**TLS/SSL設定:**
```yaml
# config/tls.yaml
tls:
  enabled: true
  cert_file: "/etc/ssl/certs/drone_api.crt"
  key_file: "/etc/ssl/private/drone_api.key"
  protocols: ["TLSv1.2", "TLSv1.3"]
  ciphers: "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM"
```

### 7.3 VPN設定（リモートアクセス用）

**OpenVPN設定例:**
```
# /etc/openvpn/drone_network.conf
port 1194
proto udp
dev tun
server 10.8.0.0 255.255.255.0

# ドローンネットワークへのルート
push "route 192.168.1.0 255.255.255.0"

# DNS設定
push "dhcp-option DNS 192.168.1.1"
```

## 8. 監視・診断

### 8.1 ネットワーク監視

**監視対象メトリクス:**
```yaml
# config/monitoring.yaml
network_monitoring:
  enabled: true
  metrics:
    - ping_latency
    - packet_loss
    - bandwidth_usage
    - connection_count
    - port_availability
  
  thresholds:
    ping_latency_ms: 50
    packet_loss_percent: 1.0
    bandwidth_usage_percent: 80
  
  alert_channels:
    - email
    - slack
    - syslog
```

**監視スクリプト:**
```python
#!/usr/bin/env python3
import subprocess
import json
import time
from datetime import datetime

def monitor_network():
    """ネットワーク状態監視"""
    
    # Ping監視
    result = subprocess.run(
        ['ping', '-c', '4', '192.168.1.100'],
        capture_output=True, text=True
    )
    
    # パケットロス解析
    if 'packet loss' in result.stdout:
        loss_line = [line for line in result.stdout.split('\n') 
                    if 'packet loss' in line][0]
        loss_percent = float(loss_line.split('%')[0].split()[-1])
        
        if loss_percent > 1.0:
            alert_admin(f"Packet loss detected: {loss_percent}%")
    
    # ポート監視
    for port in [8889, 8890, 11111]:
        result = subprocess.run(
            ['nc', '-z', '-u', '192.168.1.100', str(port)],
            capture_output=True
        )
        if result.returncode != 0:
            alert_admin(f"Port {port} not responding")

def alert_admin(message):
    """管理者アラート"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] ALERT: {message}")
    # Slack/email通知実装

if __name__ == "__main__":
    while True:
        monitor_network()
        time.sleep(30)
```

### 8.2 パフォーマンス診断

**帯域幅測定:**
```bash
# iperf3によるスループット測定
# サーバー側（ドローン側）
iperf3 -s -p 5001

# クライアント側（PC側）
iperf3 -c 192.168.1.100 -p 5001 -t 30 -u -b 10M
```

**レイテンシー測定:**
```bash
# mtr による詳細ネットワーク解析
mtr --report --report-cycles 100 192.168.1.100

# tcptraceroute による経路追跡
tcptraceroute 192.168.1.100 8889
```

## 9. トラブルシューティング

### 9.1 接続問題診断

**診断手順:**
```bash
# 1. 基本接続確認
ping -c 4 192.168.1.100

# 2. ポート確認
nmap -sU -p 8889,8890,11111 192.168.1.100

# 3. ルーティング確認
traceroute 192.168.1.100

# 4. ARP テーブル確認
arp -a | grep 192.168.1.100

# 5. インターフェース状態確認
ip addr show
ip route show
```

### 9.2 性能問題解決

**チューニングパラメータ:**
```bash
# Linux カーネルパラメータ調整
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.ipv4.udp_mem = 102400 873800 16777216' >> /etc/sysctl.conf

# 適用
sysctl -p
```

**UDP バッファサイズ最適化:**
```python
# Python socket設定
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)  # 1MB
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)  # 1MB
```

## 10. 設定テンプレート

### 10.1 開発環境設定

**docker-compose.yml（ネットワーク設定付き）:**
```yaml
version: '3.8'
services:
  drone_backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DRONE_MODE=auto
      - NETWORK_SCAN_ENABLED=true
      - TELLO_AUTO_DETECT=true
    networks:
      drone_network:
        ipv4_address: 192.168.1.10

networks:
  drone_network:
    driver: bridge
    ipam:
      config:
        - subnet: 192.168.1.0/24
          gateway: 192.168.1.1
```

### 10.2 本番環境設定

**システムサービス設定:**
```ini
# /etc/systemd/system/drone-network-monitor.service
[Unit]
Description=Drone Network Monitor
After=network.target

[Service]
Type=simple
User=drone
ExecStart=/usr/local/bin/drone-network-monitor
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 11. FAQ

### Q1: 複数のTelloが同じIPアドレスを持つ問題
**A:** Telloは工場出荷時に同じIP（192.168.10.1）を持ちます。以下で解決：
1. Station modeで別々のWiFiネットワークに接続
2. DHCPで異なるIPを取得
3. 手動でIP予約設定

### Q2: ビデオストリームが不安定
**A:** 以下を確認・調整：
1. WiFi信号強度（-50dBm以上推奨）
2. 2.4GHz帯の干渉チェック
3. UDP受信バッファサイズ調整
4. フレームレート制限（15-30fps）

### Q3: 自動検出が機能しない
**A:** 以下を確認：
1. ファイアウォール設定
2. ネットワークセグメント分離
3. ブロードキャストドメイン設定
4. Telloの起動状態

---

## 関連リンク
- [API仕様書](./real_drone_api_specification.md)
- [トラブルシューティングガイド](./troubleshooting_real_drone.md)
- [ユーザーガイド](./user_guide.md)