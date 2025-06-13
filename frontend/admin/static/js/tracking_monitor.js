/**
 * MFG Drone Tracking Monitor JavaScript
 * 追跡状態監視機能のJavaScript
 */

class TrackingMonitor {
    constructor() {
        this.socket = null;
        this.monitoringInterval = null;
        this.startTime = null;
        this.stats = {
            detectionCount: 0,
            totalChecks: 0,
            positionHistory: [],
            deviationHistory: []
        };
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.bindEvents();
        this.startMonitoring();
        console.log('Tracking Monitor initialized');
    }
    
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Monitor WebSocket connected');
            this.addStatusMessage('監視システムに接続しました', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Monitor WebSocket disconnected');
            this.addStatusMessage('監視システムから切断されました', 'warning');
        });
        
        this.socket.on('tracking_status', (data) => {
            this.updateMonitorData(data);
        });
        
        this.socket.on('tracking_error', (data) => {
            this.handleTrackingError(data);
        });
    }
    
    bindEvents() {
        // リアルタイム更新トグル
        const toggleBtn = document.getElementById('toggleRealtimeBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleRealtimeUpdates());
        }
        
        // データリセット
        const resetBtn = document.getElementById('resetDataBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetMonitorData());
        }
        
        // 統計エクスポート
        const exportBtn = document.getElementById('exportStatsBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportStatistics());
        }
        
        // アラート設定
        const alertSettingsBtn = document.getElementById('alertSettingsBtn');
        if (alertSettingsBtn) {
            alertSettingsBtn.addEventListener('click', () => this.showAlertSettings());
        }
    }
    
    updateMonitorData(data) {
        // 基本統計更新
        this.updateBasicStats(data);
        
        // 位置データ処理
        if (data.target_position && data.target_detected) {
            this.processPositionData(data.target_position);
        }
        
        // 検出率計算
        this.calculateDetectionRate(data.target_detected);
        
        // パフォーマンス監視
        this.monitorPerformance(data);
        
        // UI更新
        this.updateMonitorUI(data);
    }
    
    updateBasicStats(data) {
        // 追跡時間計算
        if (data.is_tracking && !this.startTime) {
            this.startTime = new Date();
        } else if (!data.is_tracking && this.startTime) {
            this.startTime = null;
        }
        
        // 追跡時間表示
        if (this.startTime) {
            const duration = new Date() - this.startTime;
            const hours = Math.floor(duration / 3600000);
            const minutes = Math.floor((duration % 3600000) / 60000);
            const seconds = Math.floor((duration % 60000) / 1000);
            
            const timeElement = document.getElementById('trackingTime');
            if (timeElement) {
                timeElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }
    }
    
    processPositionData(position) {
        const timestamp = new Date();
        
        // 位置履歴に追加
        this.stats.positionHistory.push({
            timestamp: timestamp,
            x: position.x,
            y: position.y,
            width: position.width,
            height: position.height
        });
        
        // 中央からの偏差計算
        const centerX = 320; // カメラ画面の中央X座標（仮定）
        const centerY = 240; // カメラ画面の中央Y座標（仮定）
        const deviation = Math.sqrt(
            Math.pow(position.x - centerX, 2) + 
            Math.pow(position.y - centerY, 2)
        );
        
        this.stats.deviationHistory.push({
            timestamp: timestamp,
            deviation: deviation
        });
        
        // 履歴サイズ制限
        const maxHistory = 1000;
        if (this.stats.positionHistory.length > maxHistory) {
            this.stats.positionHistory.shift();
        }
        if (this.stats.deviationHistory.length > maxHistory) {
            this.stats.deviationHistory.shift();
        }
        
        // 偏差アラートチェック
        this.checkDeviationAlert(deviation);
    }
    
    calculateDetectionRate(detected) {
        this.stats.totalChecks++;
        if (detected) {
            this.stats.detectionCount++;
        }
        
        const rate = this.stats.totalChecks > 0 ? 
            (this.stats.detectionCount / this.stats.totalChecks) * 100 : 0;
        
        const rateElement = document.getElementById('detectionRate');
        if (rateElement) {
            rateElement.textContent = `${rate.toFixed(1)}%`;
        }
    }
    
    monitorPerformance(data) {
        // 応答時間監視（模擬）
        const responseTime = 50 + Math.random() * 100;
        
        // 安定性評価
        const stability = this.calculateTrackingStability();
        
        // パフォーマンス指標更新
        const responseElement = document.getElementById('responseTime');
        if (responseElement) {
            responseElement.textContent = `${Math.round(responseTime)}ms`;
        }
        
        const stabilityElement = document.getElementById('stabilityScore');
        if (stabilityElement) {
            stabilityElement.textContent = stability;
        }
    }
    
    calculateTrackingStability() {
        if (this.stats.deviationHistory.length < 10) {
            return 'N/A';
        }
        
        // 最近の偏差データから安定性を計算
        const recentDeviations = this.stats.deviationHistory.slice(-10);
        const avgDeviation = recentDeviations.reduce((sum, d) => sum + d.deviation, 0) / recentDeviations.length;
        const variance = recentDeviations.reduce((sum, d) => sum + Math.pow(d.deviation - avgDeviation, 2), 0) / recentDeviations.length;
        
        // 安定性スコア（100点満点）
        const stabilityScore = Math.max(0, Math.min(100, 100 - variance / 10));
        
        return `${Math.round(stabilityScore)}点`;
    }
    
    checkDeviationAlert(deviation) {
        const alertThresholds = {
            warning: 80,
            critical: 150
        };
        
        const alertContainer = document.getElementById('deviationAlerts');
        if (!alertContainer) return;
        
        // 既存のアラートをクリア
        alertContainer.innerHTML = '';
        
        if (deviation > alertThresholds.critical) {
            this.showDeviationAlert('critical', '🚨 対象が中央から大きく離れています！', deviation);
        } else if (deviation > alertThresholds.warning) {
            this.showDeviationAlert('warning', '⚠️ 対象が中央から離れています', deviation);
        }
    }
    
    showDeviationAlert(level, message, deviation) {
        const alertContainer = document.getElementById('deviationAlerts');
        if (!alertContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `deviation-alert ${level}`;
        alert.innerHTML = `
            <span>${message}</span>
            <span style="margin-left: auto; font-weight: bold;">${Math.round(deviation)}px</span>
        `;
        
        alertContainer.appendChild(alert);
        
        // アラート音を鳴らす（オプション）
        if (level === 'critical') {
            this.playAlertSound();
        }
    }
    
    updateMonitorUI(data) {
        // 追跡状態表示
        const statusElement = document.getElementById('trackingStatus');
        if (statusElement) {
            statusElement.className = `tracking-status ${data.is_tracking ? 'tracking-status-active' : 'tracking-status-inactive'}`;
            statusElement.innerHTML = `
                <div class="status-icon ${data.is_tracking ? 'active' : 'inactive'}"></div>
                <span>${data.is_tracking ? '追跡中' : '停止中'}</span>
                ${data.target_object ? `<span>対象: ${data.target_object}</span>` : ''}
            `;
        }
        
        // 位置情報表示
        if (data.target_position) {
            this.updatePositionDisplay(data.target_position);
        }
        
        // 検出状態表示
        const detectionElement = document.getElementById('detectionStatus');
        if (detectionElement) {
            detectionElement.className = `alert ${data.target_detected ? 'alert-success' : 'alert-warning'}`;
            detectionElement.textContent = data.target_detected ? '✅ 対象検出中' : '❌ 対象未検出';
        }
        
        // 最終更新時刻
        const timestampElement = document.getElementById('lastUpdateTime');
        if (timestampElement) {
            timestampElement.textContent = new Date().toLocaleTimeString();
        }
    }
    
    updatePositionDisplay(position) {
        const elements = {
            'positionX': position.x,
            'positionY': position.y,
            'detectionWidth': position.width,
            'detectionHeight': position.height
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value !== undefined ? value : '---';
            }
        });
        
        // 中央からの距離計算
        const centerX = 320, centerY = 240;
        const distance = Math.sqrt(
            Math.pow(position.x - centerX, 2) + 
            Math.pow(position.y - centerY, 2)
        );
        
        const distanceElement = document.getElementById('centerDistance');
        if (distanceElement) {
            distanceElement.textContent = `${Math.round(distance)}px`;
        }
    }
    
    toggleRealtimeUpdates() {
        const btn = document.getElementById('toggleRealtimeBtn');
        if (!btn) return;
        
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
            btn.textContent = 'リアルタイム更新開始';
            btn.className = 'btn btn-success';
            this.addStatusMessage('リアルタイム更新を停止しました', 'info');
        } else {
            this.startMonitoring();
            btn.textContent = 'リアルタイム更新停止';
            btn.className = 'btn btn-warning';
            this.addStatusMessage('リアルタイム更新を開始しました', 'info');
        }
    }
    
    resetMonitorData() {
        if (confirm('監視データをリセットしますか？')) {
            this.stats = {
                detectionCount: 0,
                totalChecks: 0,
                positionHistory: [],
                deviationHistory: []
            };
            
            this.startTime = null;
            
            // UI要素をリセット
            const elementsToReset = [
                'trackingTime', 'detectionRate', 'responseTime', 
                'stabilityScore', 'centerDistance'
            ];
            
            elementsToReset.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = id === 'trackingTime' ? '00:00:00' : '---';
                }
            });
            
            // アラートをクリア
            const alertContainer = document.getElementById('deviationAlerts');
            if (alertContainer) {
                alertContainer.innerHTML = '';
            }
            
            this.addStatusMessage('監視データをリセットしました', 'success');
        }
    }
    
    exportStatistics() {
        const stats = {
            exportTime: new Date().toISOString(),
            trackingSession: {
                startTime: this.startTime,
                duration: this.startTime ? new Date() - this.startTime : 0,
                detectionRate: this.stats.totalChecks > 0 ? (this.stats.detectionCount / this.stats.totalChecks) * 100 : 0
            },
            positionHistory: this.stats.positionHistory,
            deviationHistory: this.stats.deviationHistory,
            summary: {
                totalChecks: this.stats.totalChecks,
                detectionCount: this.stats.detectionCount,
                averageDeviation: this.stats.deviationHistory.length > 0 ? 
                    this.stats.deviationHistory.reduce((sum, d) => sum + d.deviation, 0) / this.stats.deviationHistory.length : 0,
                maxDeviation: this.stats.deviationHistory.length > 0 ? 
                    Math.max(...this.stats.deviationHistory.map(d => d.deviation)) : 0
            }
        };
        
        const blob = new Blob([JSON.stringify(stats, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tracking_statistics_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.addStatusMessage('統計データをエクスポートしました', 'success');
    }
    
    showAlertSettings() {
        // アラート設定モーダル表示（簡易版）
        const settings = prompt('偏差アラートの閾値を設定してください（ピクセル単位）', '80');
        if (settings) {
            this.alertThreshold = parseInt(settings);
            this.addStatusMessage(`アラート閾値を${settings}pxに設定しました`, 'info');
        }
    }
    
    addStatusMessage(message, type = 'info') {
        const container = document.querySelector('.alert-container');
        if (!container) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} fade-in`;
        alert.textContent = message;
        container.appendChild(alert);
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 3000);
    }
    
    playAlertSound() {
        // ブラウザでアラート音を再生（Web Audio API使用）
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (error) {
            console.warn('Alert sound playback failed:', error);
        }
    }
    
    handleTrackingError(error) {
        console.error('Tracking error:', error);
        this.addStatusMessage(`追跡エラー: ${error.message}`, 'danger');
    }
    
    startMonitoring() {
        // 定期的な状態監視（1秒間隔）
        this.monitoringInterval = setInterval(() => {
            if (this.socket && this.socket.connected) {
                this.socket.emit('request_tracking_status');
            }
        }, 1000);
    }
    
    destroy() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// モニター機能をグローバルに公開
window.TrackingMonitor = TrackingMonitor;