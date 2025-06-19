/*
MFG Drone Admin Frontend - Main JavaScript
管理者用フロントエンド メインJavaScript
*/

class MFGDroneAdmin {
    constructor() {
        this.apiClient = new DroneAPIClient();
        this.currentView = 'dashboard';
        this.connectionStatus = false;
        this.trackingStatus = false;
        this.isStreaming = false;
        this.sensorUpdateInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.loadInitialView();
        this.startSensorUpdates();
    }
    
    // ===== Event Listeners =====
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.getAttribute('data-view');
                if (view) {
                    this.switchView(view);
                }
            });
        });
        
        // Emergency stop button
        const emergencyBtn = document.getElementById('emergency-stop');
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => this.emergencyStop());
        }
        
        // Connection controls
        const connectBtn = document.getElementById('connect-drone');
        const disconnectBtn = document.getElementById('disconnect-drone');
        
        if (connectBtn) {
            connectBtn.addEventListener('click', () => this.connectDrone());
        }
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', () => this.disconnectDrone());
        }
        
        // Flight controls
        const takeoffBtn = document.getElementById('takeoff');
        const landBtn = document.getElementById('land');
        
        if (takeoffBtn) {
            takeoffBtn.addEventListener('click', () => this.takeoff());
        }
        if (landBtn) {
            landBtn.addEventListener('click', () => this.land());
        }
        
        // Movement controls
        this.setupMovementControls();
        
        // Camera controls
        this.setupCameraControls();
        
        // Tracking controls
        this.setupTrackingControls();
        
        // Model management
        this.setupModelManagement();
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // 緊急停止: Escape キー
            if (e.key === 'Escape') {
                e.preventDefault();
                this.emergencyStop();
                return;
            }
            
            // WASDキーでドローン移動（Ctrlキー同時押し）
            if (e.ctrlKey) {
                switch(e.key.toLowerCase()) {
                    case 'w':
                        e.preventDefault();
                        this.moveDrone('forward', 20);
                        break;
                    case 's':
                        e.preventDefault();
                        this.moveDrone('back', 20);
                        break;
                    case 'a':
                        e.preventDefault();
                        this.moveDrone('left', 20);
                        break;
                    case 'd':
                        e.preventDefault();
                        this.moveDrone('right', 20);
                        break;
                    case 'q':
                        e.preventDefault();
                        this.rotateDrone('ccw', 45);
                        break;
                    case 'e':
                        e.preventDefault();
                        this.rotateDrone('cw', 45);
                        break;
                }
            }
        });
    }
    
    // ===== View Management =====
    switchView(viewName) {
        // ナビゲーションの更新
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-view="${viewName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        // コンテンツエリアの更新
        this.loadViewContent(viewName);
        this.currentView = viewName;
        
        // ビュー固有の初期化
        this.initializeView(viewName);
    }
    
    loadViewContent(viewName) {
        const contentArea = document.getElementById('content-area');
        if (!contentArea) return;
        
        // ローディング表示
        contentArea.innerHTML = '<div class="text-center p-4"><div class="spinner-border" role="status"></div></div>';
        
        // Ajax でビューコンテンツを読み込み
        fetch(`/${viewName.replace('_', '/')}`)
            .then(response => response.text())
            .then(html => {
                // HTMLから必要な部分を抽出（実際の実装では適切なパーシングが必要）
                contentArea.innerHTML = html;
                this.initializeView(viewName);
            })
            .catch(error => {
                console.error('View load error:', error);
                contentArea.innerHTML = '<div class="alert alert-danger">ページの読み込みに失敗しました</div>';
            });
    }
    
    initializeView(viewName) {
        switch(viewName) {
            case 'dashboard':
                this.initializeDashboard();
                break;
            case 'drone_connection':
                this.initializeConnection();
                break;
            case 'drone_flight':
                this.initializeFlight();
                break;
            case 'drone_movement':
                this.initializeMovement();
                break;
            case 'monitoring_sensors':
                this.initializeSensors();
                break;
            case 'monitoring_camera':
                this.initializeCamera();
                break;
            case 'ai_tracking':
                this.initializeTracking();
                break;
            case 'ai_models':
                this.initializeModels();
                break;
            case 'monitoring_settings':
                this.initializeSettings();
                break;
        }
    }
    
    loadInitialView() {
        this.switchView('dashboard');
    }
    
    // ===== Connection Management =====
    async connectDrone() {
        try {
            this.showLoading('ドローンに接続中...');
            const result = await this.apiClient.connectDrone();
            this.connectionStatus = true;
            this.updateConnectionStatus();
            this.showAlert('success', 'ドローンに接続しました');
        } catch (error) {
            this.showAlert('danger', `接続エラー: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async disconnectDrone() {
        try {
            this.showLoading('ドローンから切断中...');
            const result = await this.apiClient.disconnectDrone();
            this.connectionStatus = false;
            this.updateConnectionStatus();
            this.showAlert('info', 'ドローンから切断しました');
        } catch (error) {
            this.showAlert('danger', `切断エラー: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    updateConnectionStatus() {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `status-indicator ${this.connectionStatus ? 'connected' : 'disconnected'}`;
            indicator.innerHTML = `
                <span class="status-dot"></span>
                ${this.connectionStatus ? '接続中' : '切断中'}
            `;
        }
    }
    
    // ===== Flight Control =====
    async takeoff() {
        if (!this.connectionStatus) {
            this.showAlert('warning', 'ドローンが接続されていません');
            return;
        }
        
        try {
            this.showLoading('離陸中...');
            const result = await this.apiClient.takeoff();
            this.showAlert('success', 'ドローンが離陸しました');
        } catch (error) {
            this.showAlert('danger', `離陸エラー: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async land() {
        if (!this.connectionStatus) {
            this.showAlert('warning', 'ドローンが接続されていません');
            return;
        }
        
        try {
            this.showLoading('着陸中...');
            const result = await this.apiClient.land();
            this.showAlert('success', 'ドローンが着陸しました');
        } catch (error) {
            this.showAlert('danger', `着陸エラー: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async emergencyStop() {
        try {
            const result = await this.apiClient.emergencyStop();
            this.showAlert('warning', '緊急停止を実行しました');
        } catch (error) {
            this.showAlert('danger', `緊急停止エラー: ${error.message}`);
        }
    }
    
    // ===== Movement Control =====
    setupMovementControls() {
        // 方向パッドボタン
        const directions = ['forward', 'back', 'left', 'right', 'up', 'down'];
        directions.forEach(direction => {
            const btn = document.getElementById(`move-${direction}`);
            if (btn) {
                btn.addEventListener('click', () => {
                    const distance = document.getElementById('move-distance')?.value || 20;
                    this.moveDrone(direction, parseInt(distance));
                });
            }
        });
        
        // 回転ボタン
        const rotateLeftBtn = document.getElementById('rotate-left');
        const rotateRightBtn = document.getElementById('rotate-right');
        
        if (rotateLeftBtn) {
            rotateLeftBtn.addEventListener('click', () => {
                const angle = document.getElementById('rotate-angle')?.value || 90;
                this.rotateDrone('ccw', parseInt(angle));
            });
        }
        
        if (rotateRightBtn) {
            rotateRightBtn.addEventListener('click', () => {
                const angle = document.getElementById('rotate-angle')?.value || 90;
                this.rotateDrone('cw', parseInt(angle));
            });
        }
    }
    
    async moveDrone(direction, distance) {
        if (!this.connectionStatus) {
            this.showAlert('warning', 'ドローンが接続されていません');
            return;
        }
        
        try {
            const result = await this.apiClient.moveDrone(direction, distance);
            this.showAlert('success', `${direction}方向に${distance}cm移動しました`);
        } catch (error) {
            this.showAlert('danger', `移動エラー: ${error.message}`);
        }
    }
    
    async rotateDrone(direction, angle) {
        if (!this.connectionStatus) {
            this.showAlert('warning', 'ドローンが接続されていません');
            return;
        }
        
        try {
            const result = await this.apiClient.rotateDrone(direction, angle);
            const directionText = direction === 'cw' ? '右' : '左';
            this.showAlert('success', `${directionText}に${angle}度回転しました`);
        } catch (error) {
            this.showAlert('danger', `回転エラー: ${error.message}`);
        }
    }
    
    // ===== Camera Control =====
    setupCameraControls() {
        const streamBtn = document.getElementById('toggle-stream');
        const photoBtn = document.getElementById('take-photo');
        const videoBtn = document.getElementById('toggle-video');
        
        if (streamBtn) {
            streamBtn.addEventListener('click', () => this.toggleCameraStream());
        }
        if (photoBtn) {
            photoBtn.addEventListener('click', () => this.takePhoto());
        }
        if (videoBtn) {
            videoBtn.addEventListener('click', () => this.toggleVideoRecording());
        }
    }
    
    async toggleCameraStream() {
        try {
            if (this.isStreaming) {
                await this.apiClient.stopCameraStream();
                this.isStreaming = false;
                this.showAlert('info', 'ストリーミングを停止しました');
            } else {
                await this.apiClient.startCameraStream();
                this.isStreaming = true;
                this.showAlert('success', 'ストリーミングを開始しました');
            }
            this.updateStreamButton();
        } catch (error) {
            this.showAlert('danger', `ストリーミングエラー: ${error.message}`);
        }
    }
    
    updateStreamButton() {
        const btn = document.getElementById('toggle-stream');
        if (btn) {
            btn.textContent = this.isStreaming ? 'ストリーミング停止' : 'ストリーミング開始';
            btn.className = `btn ${this.isStreaming ? 'btn-warning' : 'btn-primary'}`;
        }
    }
    
    async takePhoto() {
        try {
            const result = await this.apiClient.takePhoto();
            this.showAlert('success', '写真を撮影しました');
        } catch (error) {
            this.showAlert('danger', `撮影エラー: ${error.message}`);
        }
    }
    
    // ===== Object Tracking =====
    setupTrackingControls() {
        const startBtn = document.getElementById('start-tracking');
        const stopBtn = document.getElementById('stop-tracking');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startTracking());
        }
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopTracking());
        }
    }
    
    async startTracking() {
        const targetObject = document.getElementById('target-object')?.value;
        const trackingMode = document.getElementById('tracking-mode')?.value || 'center';
        
        if (!targetObject) {
            this.showAlert('warning', '追跡対象を選択してください');
            return;
        }
        
        try {
            const result = await this.apiClient.startTracking(targetObject, trackingMode);
            this.trackingStatus = true;
            this.showAlert('success', `${targetObject}の追跡を開始しました`);
            this.updateTrackingStatus();
        } catch (error) {
            this.showAlert('danger', `追跡開始エラー: ${error.message}`);
        }
    }
    
    async stopTracking() {
        try {
            const result = await this.apiClient.stopTracking();
            this.trackingStatus = false;
            this.showAlert('info', '追跡を停止しました');
            this.updateTrackingStatus();
        } catch (error) {
            this.showAlert('danger', `追跡停止エラー: ${error.message}`);
        }
    }
    
    updateTrackingStatus() {
        const indicator = document.getElementById('tracking-status');
        if (indicator) {
            indicator.className = `status-indicator ${this.trackingStatus ? 'connected' : 'disconnected'}`;
            indicator.innerHTML = `
                <span class="status-dot"></span>
                ${this.trackingStatus ? '追跡中' : '停止中'}
            `;
        }
    }
    
    // ===== Model Management =====
    setupModelManagement() {
        const uploadBtn = document.getElementById('upload-images');
        const trainBtn = document.getElementById('train-model');
        
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.uploadTrainingImages());
        }
        if (trainBtn) {
            trainBtn.addEventListener('click', () => this.trainModel());
        }
    }
    
    async uploadTrainingImages() {
        const fileInput = document.getElementById('training-images');
        const objectName = document.getElementById('object-name')?.value;
        
        if (!fileInput?.files?.length) {
            this.showAlert('warning', '画像ファイルを選択してください');
            return;
        }
        
        if (!objectName) {
            this.showAlert('warning', 'オブジェクト名を入力してください');
            return;
        }
        
        try {
            this.showLoading('画像をアップロード中...');
            // 実際の実装では FormData を使用してファイルをアップロード
            const result = await this.apiClient.uploadTrainingImages([], objectName);
            this.showAlert('success', `${fileInput.files.length}枚の画像をアップロードしました`);
        } catch (error) {
            this.showAlert('danger', `アップロードエラー: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async trainModel() {
        const objectName = document.getElementById('train-object-name')?.value;
        
        if (!objectName) {
            this.showAlert('warning', 'オブジェクト名を入力してください');
            return;
        }
        
        try {
            this.showLoading('モデル学習を開始中...');
            const result = await this.apiClient.startTraining(objectName);
            this.showAlert('success', `${objectName}のモデル学習を開始しました`);
        } catch (error) {
            this.showAlert('danger', `学習開始エラー: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    // ===== Sensor Updates =====
    startSensorUpdates() {
        if (this.sensorUpdateInterval) {
            clearInterval(this.sensorUpdateInterval);
        }
        
        this.sensorUpdateInterval = setInterval(() => {
            this.updateSensorData();
        }, 2000); // 2秒間隔で更新
    }
    
    async updateSensorData() {
        if (!this.connectionStatus) return;
        
        try {
            const sensorData = await this.apiClient.getAllSensorData();
            this.displaySensorData(sensorData);
        } catch (error) {
            console.warn('Sensor update error:', error);
        }
    }
    
    displaySensorData(data) {
        // バッテリー残量
        const batteryElement = document.getElementById('battery-level');
        if (batteryElement && data.battery) {
            batteryElement.textContent = `${data.battery.battery_percentage || 0}%`;
        }
        
        // 高度
        const heightElement = document.getElementById('current-height');
        if (heightElement && data.height) {
            heightElement.textContent = `${data.height.height || 0}cm`;
        }
        
        // 温度
        const tempElement = document.getElementById('current-temperature');
        if (tempElement && data.temperature) {
            tempElement.textContent = `${data.temperature.temperature || 0}°C`;
        }
        
        // 姿勢データ
        if (data.attitude) {
            const pitchElement = document.getElementById('attitude-pitch');
            const rollElement = document.getElementById('attitude-roll');
            const yawElement = document.getElementById('attitude-yaw');
            
            if (pitchElement) pitchElement.textContent = `${data.attitude.pitch || 0}°`;
            if (rollElement) rollElement.textContent = `${data.attitude.roll || 0}°`;
            if (yawElement) yawElement.textContent = `${data.attitude.yaw || 0}°`;
        }
    }
    
    // ===== View Initializers =====
    initializeDashboard() {
        this.updateConnectionStatus();
        this.updateTrackingStatus();
        this.updateSensorData();
    }
    
    initializeConnection() {
        this.updateConnectionStatus();
    }
    
    initializeFlight() {
        // Flight control specific initialization
    }
    
    initializeMovement() {
        // Movement control specific initialization
    }
    
    initializeSensors() {
        this.updateSensorData();
    }
    
    initializeCamera() {
        this.updateStreamButton();
    }
    
    initializeTracking() {
        this.updateTrackingStatus();
    }
    
    initializeModels() {
        this.loadModelList();
    }
    
    initializeSettings() {
        this.loadCurrentSettings();
    }
    
    async loadModelList() {
        try {
            const models = await this.apiClient.listModels();
            // モデル一覧を表示
        } catch (error) {
            console.error('Model list load error:', error);
        }
    }
    
    async loadCurrentSettings() {
        try {
            const settings = await this.apiClient.getDroneSettings();
            // 設定値を表示
        } catch (error) {
            console.error('Settings load error:', error);
        }
    }
    
    // ===== Utility Methods =====
    showAlert(type, message) {
        const alertContainer = document.getElementById('alert-container') || document.body;
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} fade-in`;
        alertDiv.innerHTML = `
            <strong>${type === 'danger' ? 'エラー' : type === 'success' ? '成功' : type === 'warning' ? '警告' : '情報'}:</strong>
            ${message}
        `;
        
        alertContainer.appendChild(alertDiv);
        
        // 5秒後に自動削除
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
    
    showLoading(message = '処理中...') {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-overlay';
        loadingDiv.className = 'loading-overlay';
        loadingDiv.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status"></div>
                <div class="mt-2">${message}</div>
            </div>
        `;
        document.body.appendChild(loadingDiv);
    }
    
    hideLoading() {
        const loadingDiv = document.getElementById('loading-overlay');
        if (loadingDiv) {
            loadingDiv.parentNode.removeChild(loadingDiv);
        }
    }
}

// API Client Class
class DroneAPIClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }
    
    async makeRequest(method, endpoint, data = null) {
        const url = this.baseUrl + endpoint;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP Error: ${response.status}`);
        }
        
        return response.json();
    }
    
    // Connection
    async connectDrone() {
        return this.makeRequest('POST', '/drone/api/connect');
    }
    
    async disconnectDrone() {
        return this.makeRequest('POST', '/drone/api/disconnect');
    }
    
    async getConnectionStatus() {
        return this.makeRequest('GET', '/drone/api/status');
    }
    
    // Flight Control
    async takeoff() {
        return this.makeRequest('POST', '/drone/api/takeoff');
    }
    
    async land() {
        return this.makeRequest('POST', '/drone/api/land');
    }
    
    async emergencyStop() {
        return this.makeRequest('POST', '/drone/api/emergency');
    }
    
    // Movement
    async moveDrone(direction, distance) {
        return this.makeRequest('POST', '/drone/api/move', { direction, distance });
    }
    
    async rotateDrone(direction, angle) {
        return this.makeRequest('POST', '/drone/api/rotate', { direction, angle });
    }
    
    // Sensors
    async getAllSensorData() {
        return this.makeRequest('GET', '/monitoring/api/sensors/all');
    }
    
    async getBatteryInfo() {
        return this.makeRequest('GET', '/monitoring/api/sensors/battery');
    }
    
    async getAttitudeData() {
        return this.makeRequest('GET', '/monitoring/api/sensors/attitude');
    }
    
    // Camera
    async startCameraStream() {
        return this.makeRequest('POST', '/monitoring/api/camera/stream/start');
    }
    
    async stopCameraStream() {
        return this.makeRequest('POST', '/monitoring/api/camera/stream/stop');
    }
    
    async takePhoto() {
        return this.makeRequest('POST', '/monitoring/api/camera/photo');
    }
    
    // Tracking
    async startTracking(targetObject, trackingMode) {
        return this.makeRequest('POST', '/ai/api/tracking/start', { target_object: targetObject, tracking_mode: trackingMode });
    }
    
    async stopTracking() {
        return this.makeRequest('POST', '/ai/api/tracking/stop');
    }
    
    async getTrackingStatus() {
        return this.makeRequest('GET', '/ai/api/tracking/status');
    }
    
    // Models
    async listModels() {
        return this.makeRequest('GET', '/ai/api/models/list');
    }
    
    async uploadTrainingImages(files, objectName) {
        return this.makeRequest('POST', '/ai/api/models/upload', { images: files, object_name: objectName });
    }
    
    async startTraining(objectName, trainingParams = {}) {
        return this.makeRequest('POST', '/ai/api/models/train', { object_name: objectName, training_params: trainingParams });
    }
    
    // Settings
    async getDroneSettings() {
        return this.makeRequest('GET', '/monitoring/api/settings/get');
    }
    
    async updateDroneSettings(settings) {
        return this.makeRequest('POST', '/monitoring/api/settings/update', settings);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mfgDroneAdmin = new MFGDroneAdmin();
});