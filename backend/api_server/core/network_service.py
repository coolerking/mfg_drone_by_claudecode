"""
Network Service - Advanced network detection and management for Tello EDU drones
Provides comprehensive LAN scanning, device discovery, and network diagnostics
"""

import asyncio
import socket
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import ipaddress
import subprocess
import platform

try:
    from djitellopy import Tello
except ImportError:
    Tello = None

logger = logging.getLogger(__name__)


class NetworkScanMethod(Enum):
    """ネットワークスキャン方式"""
    PING_SWEEP = "ping_sweep"           # pingスキャン
    UDP_BROADCAST = "udp_broadcast"     # UDPブロードキャスト
    KNOWN_PORTS = "known_ports"         # 既知ポートスキャン
    TELLO_COMMAND = "tello_command"     # Telloコマンドテスト


@dataclass
class DetectedDrone:
    """検出されたドローン情報"""
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    battery_level: Optional[int] = None
    signal_strength: Optional[int] = None
    firmware_version: Optional[str] = None
    detected_at: datetime = None
    detection_method: NetworkScanMethod = NetworkScanMethod.PING_SWEEP
    response_time_ms: float = 0.0
    is_verified: bool = False

    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now()


@dataclass
class NetworkConfig:
    """ネットワーク設定"""
    scan_ranges: List[str] = None
    tello_ports: List[int] = None
    timeout_seconds: float = 3.0
    max_concurrent_scans: int = 50
    retry_attempts: int = 2
    scan_interval_seconds: float = 60.0

    def __post_init__(self):
        if self.scan_ranges is None:
            self.scan_ranges = [
                "192.168.1.0/24",
                "192.168.10.0/24",
                "192.168.4.0/24",
                "10.0.0.0/24"
            ]
        if self.tello_ports is None:
            self.tello_ports = [8889, 8890, 11111]


class NetworkService:
    """
    高度なネットワーク検出サービス
    Tello EDUを含む様々なドローンをLAN内で検出・管理
    """

    def __init__(self, config: Optional[NetworkConfig] = None):
        """
        初期化
        
        Args:
            config: ネットワーク設定
        """
        self.config = config or NetworkConfig()
        self.detected_drones: Dict[str, DetectedDrone] = {}
        self.scan_history: List[Dict[str, Any]] = []
        self.is_scanning = False
        self.auto_scan_enabled = False
        
        # スレッド制御
        self._scan_thread: Optional[threading.Thread] = None
        self._auto_scan_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # パフォーマンス統計
        self.scan_statistics = {
            "total_scans": 0,
            "successful_detections": 0,
            "failed_attempts": 0,
            "average_scan_time": 0.0,
            "last_scan_time": None
        }
        
        logger.info("NetworkService initialized")

    def start_auto_scan(self, interval_seconds: Optional[float] = None) -> None:
        """
        自動スキャンを開始
        
        Args:
            interval_seconds: スキャン間隔（秒）
        """
        if self.auto_scan_enabled:
            logger.warning("Auto scan already running")
            return
        
        if interval_seconds:
            self.config.scan_interval_seconds = interval_seconds
        
        self.auto_scan_enabled = True
        self._auto_scan_thread = threading.Thread(target=self._auto_scan_loop, daemon=True)
        self._auto_scan_thread.start()
        
        logger.info(f"Auto scan started with {self.config.scan_interval_seconds}s interval")

    def stop_auto_scan(self) -> None:
        """自動スキャンを停止"""
        if not self.auto_scan_enabled:
            logger.warning("Auto scan not running")
            return
        
        self.auto_scan_enabled = False
        self._stop_event.set()
        
        if self._auto_scan_thread:
            self._auto_scan_thread.join(timeout=5.0)
        
        logger.info("Auto scan stopped")

    def _auto_scan_loop(self) -> None:
        """自動スキャンループ"""
        while self.auto_scan_enabled:
            try:
                if not self.is_scanning:
                    asyncio.run(self.scan_network())
            except Exception as e:
                logger.error(f"Auto scan error: {e}")
            
            # インターバル待機
            if self._stop_event.wait(self.config.scan_interval_seconds):
                break

    async def scan_network(self, 
                          methods: Optional[List[NetworkScanMethod]] = None,
                          ip_ranges: Optional[List[str]] = None) -> List[DetectedDrone]:
        """
        ネットワークスキャンを実行
        
        Args:
            methods: 使用するスキャン方式
            ip_ranges: スキャン対象IPレンジ
            
        Returns:
            List[DetectedDrone]: 検出されたドローンリスト
        """
        if self.is_scanning:
            logger.warning("Network scan already in progress")
            return list(self.detected_drones.values())
        
        scan_start_time = time.time()
        self.is_scanning = True
        
        try:
            # デフォルト設定
            if methods is None:
                methods = [
                    NetworkScanMethod.TELLO_COMMAND,
                    NetworkScanMethod.PING_SWEEP,
                    NetworkScanMethod.KNOWN_PORTS
                ]
            
            if ip_ranges is None:
                ip_ranges = self.config.scan_ranges
            
            logger.info(f"Starting network scan with methods: {[m.value for m in methods]}")
            
            # 並列スキャン実行
            scan_tasks = []
            for method in methods:
                for ip_range in ip_ranges:
                    task = self._scan_range_with_method(ip_range, method)
                    scan_tasks.append(task)
            
            # 全スキャン完了を待機
            results = await asyncio.gather(*scan_tasks, return_exceptions=True)
            
            # 結果の集約
            new_detections = []
            for result in results:
                if isinstance(result, list):
                    new_detections.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Scan task failed: {result}")
            
            # 検出結果の更新
            self._update_detected_drones(new_detections)
            
            # 統計情報の更新
            scan_duration = time.time() - scan_start_time
            self._update_scan_statistics(scan_duration, len(new_detections))
            
            logger.info(f"Network scan completed in {scan_duration:.2f}s, {len(new_detections)} new detections")
            
            return list(self.detected_drones.values())
            
        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            return []
        finally:
            self.is_scanning = False

    async def _scan_range_with_method(self, ip_range: str, method: NetworkScanMethod) -> List[DetectedDrone]:
        """
        指定範囲を指定方式でスキャン
        
        Args:
            ip_range: IPアドレス範囲
            method: スキャン方式
            
        Returns:
            List[DetectedDrone]: 検出結果
        """
        try:
            network = ipaddress.IPv4Network(ip_range, strict=False)
            ip_list = list(network.hosts())
            
            # 同時実行数制限
            semaphore = asyncio.Semaphore(self.config.max_concurrent_scans)
            
            async def scan_ip(ip: ipaddress.IPv4Address) -> Optional[DetectedDrone]:
                async with semaphore:
                    return await self._scan_single_ip(str(ip), method)
            
            # 並列スキャン実行
            tasks = [scan_ip(ip) for ip in ip_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 成功した検出のみ返す
            detections = []
            for result in results:
                if isinstance(result, DetectedDrone):
                    detections.append(result)
                elif isinstance(result, Exception):
                    logger.debug(f"IP scan failed: {result}")
            
            return detections
            
        except Exception as e:
            logger.error(f"Range scan failed for {ip_range} with {method.value}: {e}")
            return []

    async def _scan_single_ip(self, ip_address: str, method: NetworkScanMethod) -> Optional[DetectedDrone]:
        """
        単一IPアドレスをスキャン
        
        Args:
            ip_address: IPアドレス
            method: スキャン方式
            
        Returns:
            Optional[DetectedDrone]: 検出結果
        """
        try:
            start_time = time.time()
            
            if method == NetworkScanMethod.PING_SWEEP:
                detection = await self._ping_scan(ip_address)
            elif method == NetworkScanMethod.UDP_BROADCAST:
                detection = await self._udp_broadcast_scan(ip_address)
            elif method == NetworkScanMethod.KNOWN_PORTS:
                detection = await self._port_scan(ip_address)
            elif method == NetworkScanMethod.TELLO_COMMAND:
                detection = await self._tello_command_scan(ip_address)
            else:
                logger.warning(f"Unknown scan method: {method}")
                return None
            
            if detection:
                detection.response_time_ms = (time.time() - start_time) * 1000
                detection.detection_method = method
                
            return detection
            
        except Exception as e:
            logger.debug(f"Single IP scan failed for {ip_address}: {e}")
            return None

    async def _ping_scan(self, ip_address: str) -> Optional[DetectedDrone]:
        """pingスキャン実行"""
        try:
            # プラットフォーム別pingコマンド
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", "1000", ip_address]
            else:
                cmd = ["ping", "-c", "1", "-W", "1", ip_address]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.config.timeout_seconds
            )
            
            if process.returncode == 0:
                return DetectedDrone(
                    ip_address=ip_address,
                    detection_method=NetworkScanMethod.PING_SWEEP
                )
            
        except (asyncio.TimeoutError, Exception) as e:
            logger.debug(f"Ping scan failed for {ip_address}: {e}")
        
        return None

    async def _udp_broadcast_scan(self, ip_address: str) -> Optional[DetectedDrone]:
        """UDPブロードキャストスキャン実行"""
        try:
            # Tello EDU discovery用UDPパケット送信
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.config.timeout_seconds)
            
            # Tello EDUのディスカバリーコマンド
            discovery_message = "command"
            
            sock.sendto(discovery_message.encode(), (ip_address, 8889))
            
            try:
                response, addr = sock.recvfrom(1024)
                if addr[0] == ip_address and b"ok" in response.lower():
                    return DetectedDrone(
                        ip_address=ip_address,
                        detection_method=NetworkScanMethod.UDP_BROADCAST
                    )
            except socket.timeout:
                pass
            finally:
                sock.close()
                
        except Exception as e:
            logger.debug(f"UDP broadcast scan failed for {ip_address}: {e}")
        
        return None

    async def _port_scan(self, ip_address: str) -> Optional[DetectedDrone]:
        """ポートスキャン実行"""
        try:
            for port in self.config.tello_ports:
                try:
                    future = asyncio.open_connection(
                        ip_address, 
                        port,
                        limit=1024
                    )
                    
                    reader, writer = await asyncio.wait_for(
                        future, 
                        timeout=self.config.timeout_seconds
                    )
                    
                    writer.close()
                    await writer.wait_closed()
                    
                    return DetectedDrone(
                        ip_address=ip_address,
                        detection_method=NetworkScanMethod.KNOWN_PORTS
                    )
                    
                except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                    continue
                    
        except Exception as e:
            logger.debug(f"Port scan failed for {ip_address}: {e}")
        
        return None

    async def _tello_command_scan(self, ip_address: str) -> Optional[DetectedDrone]:
        """Telloコマンドスキャン実行"""
        try:
            if not Tello:
                return None
            
            # Tello接続テスト
            loop = asyncio.get_event_loop()
            
            def connect_tello():
                try:
                    tello = Tello(host=ip_address)
                    tello.connect()
                    battery = tello.get_battery()
                    
                    # 詳細情報取得
                    try:
                        height = tello.get_height()
                        temp = tello.get_temperature()
                        signal = tello.query_wifi_signal_noise_ratio()
                    except:
                        height, temp, signal = None, None, None
                    
                    tello.end()
                    
                    return {
                        "battery": battery,
                        "height": height,
                        "temperature": temp,
                        "signal": signal
                    }
                except Exception:
                    return None
            
            result = await loop.run_in_executor(None, connect_tello)
            
            if result and result["battery"] is not None:
                return DetectedDrone(
                    ip_address=ip_address,
                    battery_level=result["battery"],
                    signal_strength=result.get("signal"),
                    detection_method=NetworkScanMethod.TELLO_COMMAND,
                    is_verified=True
                )
                
        except Exception as e:
            logger.debug(f"Tello command scan failed for {ip_address}: {e}")
        
        return None

    def _update_detected_drones(self, new_detections: List[DetectedDrone]) -> None:
        """検出されたドローン情報を更新"""
        for detection in new_detections:
            existing = self.detected_drones.get(detection.ip_address)
            
            if existing:
                # 既存の情報を更新
                existing.detected_at = detection.detected_at
                existing.response_time_ms = detection.response_time_ms
                existing.detection_method = detection.detection_method
                
                # より詳細な情報で更新
                if detection.battery_level is not None:
                    existing.battery_level = detection.battery_level
                if detection.signal_strength is not None:
                    existing.signal_strength = detection.signal_strength
                if detection.is_verified:
                    existing.is_verified = True
            else:
                # 新規追加
                self.detected_drones[detection.ip_address] = detection
                logger.info(f"New drone detected: {detection.ip_address}")

    def _update_scan_statistics(self, scan_duration: float, new_detections: int) -> None:
        """スキャン統計情報を更新"""
        self.scan_statistics["total_scans"] += 1
        self.scan_statistics["successful_detections"] += new_detections
        self.scan_statistics["last_scan_time"] = datetime.now()
        
        # 平均スキャン時間の更新
        total_scans = self.scan_statistics["total_scans"]
        current_avg = self.scan_statistics["average_scan_time"]
        self.scan_statistics["average_scan_time"] = (
            (current_avg * (total_scans - 1) + scan_duration) / total_scans
        )

    def get_detected_drones(self, 
                           verified_only: bool = False,
                           max_age_minutes: Optional[int] = None) -> List[DetectedDrone]:
        """
        検出されたドローンを取得
        
        Args:
            verified_only: 検証済みのみ
            max_age_minutes: 最大経過時間（分）
            
        Returns:
            List[DetectedDrone]: ドローンリスト
        """
        drones = list(self.detected_drones.values())
        
        if verified_only:
            drones = [d for d in drones if d.is_verified]
        
        if max_age_minutes:
            cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
            drones = [d for d in drones if d.detected_at >= cutoff_time]
        
        return sorted(drones, key=lambda d: d.detected_at, reverse=True)

    def get_network_statistics(self) -> Dict[str, Any]:
        """ネットワーク統計情報を取得"""
        return {
            "scan_statistics": self.scan_statistics.copy(),
            "detected_drones_count": len(self.detected_drones),
            "verified_drones_count": sum(1 for d in self.detected_drones.values() if d.is_verified),
            "is_scanning": self.is_scanning,
            "auto_scan_enabled": self.auto_scan_enabled,
            "scan_ranges": self.config.scan_ranges,
            "last_detections": [
                {
                    "ip": d.ip_address,
                    "detected_at": d.detected_at.isoformat(),
                    "method": d.detection_method.value,
                    "verified": d.is_verified
                }
                for d in sorted(self.detected_drones.values(), 
                               key=lambda x: x.detected_at, reverse=True)[:10]
            ]
        }

    async def verify_drone_connection(self, ip_address: str) -> bool:
        """
        ドローン接続を検証
        
        Args:
            ip_address: IPアドレス
            
        Returns:
            bool: 接続可能フラグ
        """
        detection = await self._tello_command_scan(ip_address)
        if detection:
            self.detected_drones[ip_address] = detection
            return True
        return False

    def clear_detected_drones(self, older_than_minutes: Optional[int] = None) -> int:
        """
        検出されたドローン情報をクリア
        
        Args:
            older_than_minutes: 指定分数より古い情報のみクリア
            
        Returns:
            int: クリアされた件数
        """
        if older_than_minutes is None:
            count = len(self.detected_drones)
            self.detected_drones.clear()
            logger.info(f"All detected drones cleared: {count} items")
            return count
        
        cutoff_time = datetime.now() - timedelta(minutes=older_than_minutes)
        to_remove = [
            ip for ip, drone in self.detected_drones.items()
            if drone.detected_at < cutoff_time
        ]
        
        for ip in to_remove:
            del self.detected_drones[ip]
        
        logger.info(f"Old detected drones cleared: {len(to_remove)} items")
        return len(to_remove)

    def shutdown(self) -> None:
        """サービスのシャットダウン"""
        logger.info("Shutting down NetworkService...")
        
        self.stop_auto_scan()
        self._stop_event.set()
        
        logger.info("NetworkService shutdown complete")


# グローバルサービスインスタンス
_network_service_instance: Optional[NetworkService] = None


def get_network_service() -> NetworkService:
    """シングルトンネットワークサービスを取得"""
    global _network_service_instance
    if _network_service_instance is None:
        _network_service_instance = NetworkService()
    return _network_service_instance


def initialize_network_service(config: Optional[NetworkConfig] = None) -> NetworkService:
    """ネットワークサービスを初期化"""
    global _network_service_instance
    _network_service_instance = NetworkService(config)
    return _network_service_instance