/**
 * MFG Drone Admin Frontend - メインJavaScript
 * ドローン制御、API通信、UI管理
 */

class DroneAdminApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentView = 'dashboard';
        this.droneStatus = {
            connected: false,
            battery: 0,
            altitude: 0,
            tracking: false
        };
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupNavigation();
        this.startStatusUpdates();
        this.initializeCurrentView();
    }
    
    /**
     * イベントリスナー設定
     */
    setupEventListeners() {
        // グローバルエラーハンドリング
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showAlert('システムエラーが発生しました', 'error');
        });
        
        // サイドバーナビゲーション
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.dataset.view;
                if (view) {
                    this.navigateToView(view);
                }
            });
        });
        
        // モバイルメニュートグル
        const menuToggle = document.getElementById('menu-toggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }
        
        // キーボードショートカット
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.navigateToView('dashboard');
                        break;
                    case '2':
                        e.preventDefault();
                        this.navigateToView('connection');
                        break;
                    case '3':
                        e.preventDefault();
                        this.navigateToView('flight');
                        break;
                }
            }
            
            // 緊急停止ショートカット
            if (e.key === 'Escape') {
                this.emergencyStop();
            }
        });
    }
    
    /**
     * ナビゲーション設定
     */
    setupNavigation() {
        // URLハッシュベースのルーティング
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.slice(1);
            if (hash) {
                this.navigateToView(hash);
            }
        });
        
        // 初期ルート設定
        const hash = window.location.hash.slice(1);
        if (hash) {
            this.currentView = hash;
        }
    }
    
    /**
     * ビュー切り替え
     */
    navigateToView(view) {
        this.currentView = view;
        window.location.hash = view;
        
        // ナビゲーションの状態更新
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-view="${view}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        // ビューごとの初期化
        this.initializeView(view);
    }
    
    /**
     * ビュー初期化
     */
    initializeView(view) {
        switch(view) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'connection':
                this.initConnection();
                break;
            case 'flight':
                this.initFlightControl();
                break;
            case 'movement':
                this.initMovementControl();
                break;
            case 'camera':
                this.initCamera();
                break;
            case 'sensors':
                this.initSensors();
                break;
            case 'tracking':
                this.initTracking();
                break;
            case 'models':
                this.initModels();
                break;
            case 'settings':
                this.initSettings();
                break;
        }
    }
    
    /**
     * 現在のビュー初期化
     */
    initializeCurrentView() {
        this.initializeView(this.currentView);
    }
    
    /**
     * ダッシュボード初期化
     */
    initDashboard() {
        this.updateDashboardMetrics();
        this.loadCameraStream();
    }
    
    /**
     * 接続管理初期化
     */
    initConnection() {
        this.updateConnectionStatus();
    }
    
    /**
     * 飛行制御初期化
     */
    initFlightControl() {
        this.setupFlightControls();
    }
    
    /**
     * 移動制御初期化
     */
    initMovementControl() {
        this.setupMovementControls();
    }
    
    /**
     * カメラ初期化
     */
    initCamera() {
        this.loadCameraStream();
        this.setupCameraControls();
    }
    
    /**
     * センサー監視初期化
     */
    initSensors() {
        this.updateSensorData();
    }
    
    /**
     * 物体追跡初期化
     */
    initTracking() {
        this.updateTrackingStatus();
        this.loadCameraStream();
    }
    
    /**
     * モデル管理初期化
     */
    initModels() {
        this.loadModelList();
        this.setupImageUpload();
    }
    
    /**
     * 設定初期化
     */
    initSettings() {
        this.loadSettings();
    }
    
    /**
     * API通信メソッド
     */
    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            this.showAlert(`API エラー: ${error.message}`, 'error');
            throw error;
        }
    }
    
    /**
     * ドローン接続
     */
    async connectDrone() {
        try {
            this.showLoading('connect-btn', true);
            const result = await this.apiCall('/connect', { method: 'POST' });
            this.showAlert(result.message, 'success');
            this.droneStatus.connected = true;
            this.updateConnectionUI();
        } catch (error) {
            // エラーは apiCall で処理済み
        } finally {
            this.showLoading('connect-btn', false);
        }
    }
    
    /**
     * ドローン切断
     */
    async disconnectDrone() {
        try {
            this.showLoading('disconnect-btn', true);
            const result = await this.apiCall('/disconnect', { method: 'POST' });
            this.showAlert(result.message, 'success');
            this.droneStatus.connected = false;
            this.updateConnectionUI();
        } catch (error) {
            // エラーは apiCall で処理済み
        } finally {
            this.showLoading('disconnect-btn', false);
        }
    }
    
    /**
     * 離陸
     */
    async takeoff() {
        if (!this.droneStatus.connected) {
            this.showAlert('ドローンが接続されていません', 'warning');
            return;
        }
        
        try {
            this.showLoading('takeoff-btn', true);
            const result = await this.apiCall('/takeoff', { method: 'POST' });
            this.showAlert(result.message, 'success');
        } catch (error) {
            // エラーは apiCall で処理済み
        } finally {
            this.showLoading('takeoff-btn', false);
        }
    }
    
    /**
     * 着陸
     */
    async land() {
        if (!this.droneStatus.connected) {
            this.showAlert('ドローンが接続されていません', 'warning');
            return;
        }
        
        try {
            this.showLoading('land-btn', true);
            const result = await this.apiCall('/land', { method: 'POST' });
            this.showAlert(result.message, 'success');
        } catch (error) {
            // エラーは apiCall で処理済み
        } finally {
            this.showLoading('land-btn', false);
        }
    }
    
    /**
     * 緊急停止
     */
    async emergencyStop() {
        if (!this.droneStatus.connected) {
            return;
        }
        
        try {
            const result = await this.apiCall('/emergency', { method: 'POST' });
            this.showAlert(result.message, 'warning');
        } catch (error) {
            // エラーは apiCall で処理済み
        }
    }
    
    /**
     * ドローン移動
     */
    async moveDrone(direction, distance = 50) {
        if (!this.droneStatus.connected) {
            this.showAlert('ドローンが接続されていません', 'warning');
            return;
        }
        
        try {
            const result = await this.apiCall('/move', {
                method: 'POST',
                body: JSON.stringify({ direction, distance })
            });
            this.showAlert(result.message, 'success');
        } catch (error) {
            // エラーは apiCall で処理済み
        }
    }
    
    /**
     * 追跡開始
     */
    async startTracking(targetObject, mode = 'center') {
        if (!this.droneStatus.connected) {
            this.showAlert('ドローンが接続されていません', 'warning');
            return;
        }
        
        try {
            this.showLoading('start-tracking-btn', true);
            const result = await this.apiCall('/tracking/start', {
                method: 'POST',
                body: JSON.stringify({ target_object: targetObject, tracking_mode: mode })
            });
            this.showAlert(result.message, 'success');
            this.droneStatus.tracking = true;
            this.updateTrackingUI();
        } catch (error) {
            // エラーは apiCall で処理済み
        } finally {
            this.showLoading('start-tracking-btn', false);
        }
    }
    
    /**
     * 追跡停止
     */
    async stopTracking() {
        try {
            this.showLoading('stop-tracking-btn', true);
            const result = await this.apiCall('/tracking/stop', { method: 'POST' });
            this.showAlert(result.message, 'success');
            this.droneStatus.tracking = false;
            this.updateTrackingUI();
        } catch (error) {
            // エラーは apiCall で処理済み
        } finally {
            this.showLoading('stop-tracking-btn', false);
        }
    }
    
    /**
     * UI更新メソッド
     */
    updateConnectionUI() {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusDot = document.querySelector('.status-dot');
        
        if (statusIndicator && statusDot) {
            if (this.droneStatus.connected) {
                statusIndicator.className = 'status-indicator connected';
                statusIndicator.textContent = '接続中';
                statusDot.className = 'status-dot connected';
            } else {
                statusIndicator.className = 'status-indicator disconnected';
                statusIndicator.textContent = '未接続';
                statusDot.className = 'status-dot disconnected';
            }
        }
    }
    
    updateTrackingUI() {
        const trackingStatus = document.getElementById('tracking-status');
        if (trackingStatus) {
            trackingStatus.textContent = this.droneStatus.tracking ? '追跡中' : '停止中';
            trackingStatus.className = this.droneStatus.tracking ? 'text-success' : 'text-muted';
        }
    }
    
    updateDashboardMetrics() {
        // バッテリー残量更新
        const batteryValue = document.getElementById('battery-value');
        const batteryBar = document.getElementById('battery-bar');
        if (batteryValue && batteryBar) {
            batteryValue.textContent = `${this.droneStatus.battery}%`;
            batteryBar.style.width = `${this.droneStatus.battery}%`;
            
            if (this.droneStatus.battery < 20) {
                batteryBar.className = 'progress-bar error';
            } else if (this.droneStatus.battery < 50) {
                batteryBar.className = 'progress-bar warning';
            } else {
                batteryBar.className = 'progress-bar success';
            }
        }
        
        // 高度更新
        const altitudeValue = document.getElementById('altitude-value');
        if (altitudeValue) {
            altitudeValue.textContent = `${this.droneStatus.altitude}cm`;
        }
    }
    
    /**
     * ステータス定期更新
     */
    startStatusUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(async () => {
            try {
                const status = await this.apiCall('/status');
                if (status.status === 'success') {
                    this.droneStatus = { ...this.droneStatus, ...status.data };
                    this.updateConnectionUI();
                    this.updateDashboardMetrics();
                }
            } catch (error) {
                // 定期更新のエラーは無視（ログのみ）
                console.warn('Status update failed:', error.message);
            }
        }, 2000); // 2秒間隔
    }
    
    /**
     * UI ヘルパーメソッド
     */
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        alertContainer.appendChild(alert);
        
        // 5秒後に自動削除
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
    
    showLoading(buttonId, show) {
        const button = document.getElementById(buttonId);
        if (!button) return;
        
        if (show) {
            button.disabled = true;
            const originalText = button.textContent;
            button.dataset.originalText = originalText;
            button.innerHTML = '<span class="loading"></span> 処理中...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }
    
    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('open');
        }
    }
    
    /**
     * カメラストリーム読み込み
     */
    loadCameraStream() {
        const streamContainer = document.getElementById('camera-stream');
        if (!streamContainer) return;
        
        // APIからストリームURLを取得
        this.apiCall('/camera/stream')
            .then(result => {
                if (result.data && result.data.stream_url) {
                    const img = document.createElement('img');
                    img.src = result.data.stream_url;
                    img.alt = 'ドローンカメラ映像';
                    img.style.width = '100%';
                    img.style.height = 'auto';
                    
                    streamContainer.innerHTML = '';
                    streamContainer.appendChild(img);
                }
            })
            .catch(error => {
                streamContainer.innerHTML = '<p class="text-muted">カメラ映像を読み込めません</p>';
            });
    }
    
    /**
     * フライトコントロール設定
     */
    setupFlightControls() {
        // 離陸ボタン
        const takeoffBtn = document.getElementById('takeoff-btn');
        if (takeoffBtn) {
            takeoffBtn.addEventListener('click', () => this.takeoff());
        }
        
        // 着陸ボタン
        const landBtn = document.getElementById('land-btn');
        if (landBtn) {
            landBtn.addEventListener('click', () => this.land());
        }
        
        // 緊急停止ボタン
        const emergencyBtn = document.getElementById('emergency-btn');
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => this.emergencyStop());
        }
    }
    
    /**
     * 移動コントロール設定
     */
    setupMovementControls() {
        // 方向ボタン
        const directions = ['forward', 'backward', 'left', 'right', 'up', 'down'];
        directions.forEach(direction => {
            const btn = document.getElementById(`${direction}-btn`);
            if (btn) {
                btn.addEventListener('click', () => {
                    const distance = document.getElementById('distance-input')?.value || 50;
                    this.moveDrone(direction, parseInt(distance));
                });
            }
        });
        
        // キーボード制御
        document.addEventListener('keydown', (e) => {
            if (document.activeElement.tagName === 'INPUT') return;
            
            switch(e.key.toLowerCase()) {
                case 'w':
                    this.moveDrone('forward');
                    break;
                case 's':
                    this.moveDrone('backward');
                    break;
                case 'a':
                    this.moveDrone('left');
                    break;
                case 'd':
                    this.moveDrone('right');
                    break;
                case 'q':
                    this.moveDrone('up');
                    break;
                case 'e':
                    this.moveDrone('down');
                    break;
            }
        });
    }
    
    /**
     * カメラコントロール設定
     */
    setupCameraControls() {
        const captureBtn = document.getElementById('capture-btn');
        if (captureBtn) {
            captureBtn.addEventListener('click', async () => {
                try {
                    this.showLoading('capture-btn', true);
                    const result = await this.apiCall('/camera/capture', { method: 'POST' });
                    this.showAlert('写真を撮影しました', 'success');
                } catch (error) {
                    // エラーは apiCall で処理済み
                } finally {
                    this.showLoading('capture-btn', false);
                }
            });
        }
    }
    
    /**
     * 画像アップロード設定
     */
    setupImageUpload() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('image-files');
        
        if (uploadArea && fileInput) {
            // ドラッグ&ドロップ
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                fileInput.files = e.dataTransfer.files;
                this.handleImageUpload();
            });
            
            // ファイル選択
            fileInput.addEventListener('change', () => {
                this.handleImageUpload();
            });
        }
    }
    
    /**
     * 画像アップロード処理
     */
    async handleImageUpload() {
        const fileInput = document.getElementById('image-files');
        const objectName = document.getElementById('object-name')?.value;
        
        if (!fileInput.files.length || !objectName) {
            this.showAlert('画像ファイルとオブジェクト名を指定してください', 'warning');
            return;
        }
        
        const formData = new FormData();
        formData.append('object_name', objectName);
        
        for (let file of fileInput.files) {
            formData.append('images', file);
        }
        
        try {
            this.showLoading('upload-btn', true);
            const response = await fetch(`${this.apiBaseUrl}/models/upload`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (response.ok) {
                this.showAlert(result.message, 'success');
                this.loadModelList();
            } else {
                throw new Error(result.message || 'アップロードに失敗しました');
            }
        } catch (error) {
            this.showAlert(`アップロードエラー: ${error.message}`, 'error');
        } finally {
            this.showLoading('upload-btn', false);
        }
    }
    
    /**
     * モデル一覧読み込み
     */
    async loadModelList() {
        try {
            const result = await this.apiCall('/models');
            const modelList = document.getElementById('model-list');
            if (modelList && result.data) {
                // モデル一覧を表示
                modelList.innerHTML = result.data.map(model => `
                    <div class="card">
                        <div class="card-body">
                            <h5>${model.name}</h5>
                            <p class="text-muted">精度: ${model.accuracy || 'N/A'}%</p>
                            <button class="btn btn-primary btn-sm" onclick="app.startTracking('${model.name}')">
                                追跡開始
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            // エラーは apiCall で処理済み
        }
    }
}

// アプリケーション初期化
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new DroneAdminApp();
});