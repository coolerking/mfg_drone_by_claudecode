/**
 * MFG Drone Tracking Control JavaScript
 * 物体追跡制御機能のJavaScript
 */

class TrackingController {
    constructor() {
        this.isTracking = false;
        this.socket = null;
        this.targetObject = null;
        this.trackingMode = 'center';
        this.statusUpdateInterval = null;
        
        this.init();
    }
    
    init() {
        this.initializeSocketIO();
        this.bindEvents();
        this.startStatusMonitoring();
        console.log('Tracking Controller initialized');
    }
    
    initializeSocketIO() {
        // Socket.IOの初期化
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.showAlert('WebSocket接続が確立されました', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            this.showAlert('WebSocket接続が切断されました', 'warning');
        });
        
        this.socket.on('tracking_status', (data) => {
            this.updateTrackingStatus(data);
        });
        
        this.socket.on('tracking_error', (data) => {
            this.handleTrackingError(data);
        });
    }
    
    bindEvents() {
        // 追跡開始ボタン
        const startBtn = document.getElementById('startTrackingBtn');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startTracking());
        }
        
        // 追跡停止ボタン
        const stopBtn = document.getElementById('stopTrackingBtn');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopTracking());
        }
        
        // 緊急停止ボタン
        const emergencyBtn = document.getElementById('emergencyStopBtn');
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => this.emergencyStop());
        }
        
        // 対象オブジェクト選択
        const targetSelect = document.getElementById('targetObjectSelect');
        if (targetSelect) {
            targetSelect.addEventListener('change', (e) => {
                this.targetObject = e.target.value;
            });
        }
        
        // 追跡モード選択
        const modeSelect = document.getElementById('trackingModeSelect');
        if (modeSelect) {
            modeSelect.addEventListener('change', (e) => {
                this.trackingMode = e.target.value;
            });
        }
        
        // 手動更新ボタン
        const refreshBtn = document.getElementById('refreshStatusBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshStatus());
        }
    }
    
    async startTracking() {
        try {
            const targetSelect = document.getElementById('targetObjectSelect');
            const modeSelect = document.getElementById('trackingModeSelect');
            
            if (!targetSelect || !targetSelect.value) {
                this.showAlert('追跡対象を選択してください', 'warning');
                return;
            }
            
            this.targetObject = targetSelect.value;
            this.trackingMode = modeSelect ? modeSelect.value : 'center';
            
            // UI更新
            this.setButtonState('starting');
            this.showAlert('追跡を開始しています...', 'info');
            
            // API呼び出し
            const response = await fetch('/tracking/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    target_object: this.targetObject,
                    tracking_mode: this.trackingMode
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.isTracking = true;
                this.setButtonState('tracking');
                this.showAlert(`追跡を開始しました: ${this.targetObject}`, 'success');
                this.showTrackingIndicator();
            } else {
                throw new Error(result.error || '追跡開始に失敗しました');
            }
            
        } catch (error) {
            console.error('Tracking start error:', error);
            this.showAlert(error.message, 'danger');
            this.setButtonState('stopped');
        }
    }
    
    async stopTracking() {
        try {
            // UI更新
            this.setButtonState('stopping');
            this.showAlert('追跡を停止しています...', 'info');
            
            // API呼び出し
            const response = await fetch('/tracking/api/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.isTracking = false;
                this.setButtonState('stopped');
                this.showAlert('追跡を停止しました', 'success');
                this.hideTrackingIndicator();
            } else {
                throw new Error(result.error || '追跡停止に失敗しました');
            }
            
        } catch (error) {
            console.error('Tracking stop error:', error);
            this.showAlert(error.message, 'danger');
        }
    }
    
    async emergencyStop() {
        if (confirm('緊急停止を実行しますか？')) {
            await this.stopTracking();
        }
    }
    
    async refreshStatus() {
        try {
            const response = await fetch('/tracking/api/status');
            const status = await response.json();
            
            if (response.ok) {
                this.updateTrackingStatus(status);
                this.showAlert('状態を更新しました', 'success');
            } else {
                throw new Error(status.error || '状態取得に失敗しました');
            }
            
        } catch (error) {
            console.error('Status refresh error:', error);
            this.showAlert(error.message, 'danger');
        }
    }
    
    updateTrackingStatus(status) {
        // 追跡状態表示を更新
        const statusElement = document.getElementById('trackingStatus');
        if (statusElement) {
            statusElement.className = `tracking-status ${status.is_tracking ? 'tracking-status-active' : 'tracking-status-inactive'}`;
            statusElement.innerHTML = `
                <div class="status-icon ${status.is_tracking ? 'active' : 'inactive'}"></div>
                <span>${status.is_tracking ? '追跡中' : '停止中'}</span>
                ${status.target_object ? `<span>対象: ${status.target_object}</span>` : ''}
            `;
        }
        
        // ボタン状態更新
        this.isTracking = status.is_tracking;
        this.setButtonState(status.is_tracking ? 'tracking' : 'stopped');
        
        // 位置情報表示更新
        if (status.target_position) {
            this.updatePositionDisplay(status.target_position);
        }
        
        // 検出状態表示更新
        const detectionElement = document.getElementById('detectionStatus');
        if (detectionElement) {
            detectionElement.textContent = status.target_detected ? '検出中' : '未検出';
            detectionElement.className = `alert ${status.target_detected ? 'alert-success' : 'alert-warning'}`;
        }
        
        // 追跡インジケーター
        if (status.is_tracking) {
            this.showTrackingIndicator();
        } else {
            this.hideTrackingIndicator();
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
                element.textContent = value || '---';
            }
        });
    }
    
    setButtonState(state) {
        const startBtn = document.getElementById('startTrackingBtn');
        const stopBtn = document.getElementById('stopTrackingBtn');
        const emergencyBtn = document.getElementById('emergencyStopBtn');
        
        if (startBtn && stopBtn && emergencyBtn) {
            switch (state) {
                case 'stopped':
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    emergencyBtn.disabled = true;
                    startBtn.textContent = '追跡開始';
                    break;
                case 'starting':
                    startBtn.disabled = true;
                    stopBtn.disabled = true;
                    emergencyBtn.disabled = false;
                    startBtn.textContent = '開始中...';
                    break;
                case 'tracking':
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                    emergencyBtn.disabled = false;
                    stopBtn.textContent = '追跡停止';
                    break;
                case 'stopping':
                    startBtn.disabled = true;
                    stopBtn.disabled = true;
                    emergencyBtn.disabled = false;
                    stopBtn.textContent = '停止中...';
                    break;
            }
        }
    }
    
    showTrackingIndicator() {
        let indicator = document.getElementById('trackingIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'trackingIndicator';
            indicator.className = 'tracking-indicator';
            document.body.appendChild(indicator);
        }
        indicator.textContent = '追跡中';
        indicator.classList.remove('hidden');
    }
    
    hideTrackingIndicator() {
        const indicator = document.getElementById('trackingIndicator');
        if (indicator) {
            indicator.classList.add('hidden');
        }
    }
    
    showAlert(message, type = 'info') {
        // 既存のアラートを削除
        const existingAlert = document.querySelector('.temp-alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        // 新しいアラートを作成
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} temp-alert fade-in`;
        alert.textContent = message;
        
        // アラートコンテナに追加
        const container = document.querySelector('.alert-container') || document.querySelector('.container');
        if (container) {
            container.insertBefore(alert, container.firstChild);
            
            // 3秒後に自動削除
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 3000);
        }
    }
    
    handleTrackingError(error) {
        console.error('Tracking error:', error);
        this.showAlert(error.message || '追跡エラーが発生しました', 'danger');
        this.setButtonState('stopped');
        this.isTracking = false;
    }
    
    startStatusMonitoring() {
        // 初期状態を取得
        this.refreshStatus();
        
        // 定期的な状態監視（1秒間隔）
        this.statusUpdateInterval = setInterval(() => {
            if (this.isTracking) {
                this.refreshStatus();
            }
        }, 1000);
    }
    
    destroy() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// ページ読み込み時に初期化
document.addEventListener('DOMContentLoaded', () => {
    window.trackingController = new TrackingController();
});

// ページ離脱時にクリーンアップ
window.addEventListener('beforeunload', () => {
    if (window.trackingController) {
        window.trackingController.destroy();
    }
});