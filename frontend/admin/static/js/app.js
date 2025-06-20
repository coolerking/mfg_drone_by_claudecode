/**
 * MFG Drone Admin Frontend - JavaScript Application
 */

class DroneAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    /**
     * Make API request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // Health check
    async healthCheck() {
        return this.request('/health');
    }

    // Drone connection
    async connectDrone() {
        return this.request('/drone/connect', { method: 'POST' });
    }

    async disconnectDrone() {
        return this.request('/drone/disconnect', { method: 'POST' });
    }

    // Drone status
    async getDroneStatus() {
        return this.request('/drone/status');
    }

    async getBattery() {
        return this.request('/drone/battery');
    }

    // Flight control
    async takeoff() {
        return this.request('/drone/takeoff', { method: 'POST' });
    }

    async land() {
        return this.request('/drone/land', { method: 'POST' });
    }

    async emergency() {
        return this.request('/drone/emergency', { method: 'POST' });
    }

    // Camera
    async startStream() {
        return this.request('/camera/stream/start', { method: 'POST' });
    }

    async stopStream() {
        return this.request('/camera/stream/stop', { method: 'POST' });
    }

    getStreamURL() {
        return `${this.baseURL}/camera/stream`;
    }

    // Object Tracking
    async startTracking(targetObject, trackingMode = 'center') {
        return this.request('/tracking/start', {
            method: 'POST',
            body: JSON.stringify({
                target_object: targetObject,
                tracking_mode: trackingMode
            })
        });
    }

    async stopTracking() {
        return this.request('/tracking/stop', { method: 'POST' });
    }

    async getTrackingStatus() {
        return this.request('/tracking/status');
    }

    // Model Management
    async trainModel(objectName, imageFiles) {
        const formData = new FormData();
        formData.append('object_name', objectName);
        
        for (let i = 0; i < imageFiles.length; i++) {
            formData.append('images', imageFiles[i]);
        }

        return fetch(`${this.baseURL}/model/train`, {
            method: 'POST',
            body: formData
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        });
    }

    async getModelList() {
        return this.request('/model/list');
    }
}

class DroneAdminApp {
    constructor() {
        this.api = new DroneAPI();
        this.isConnected = false;
        this.isTracking = false;
        this.currentPage = 'dashboard';
        this.updateInterval = null;
        this.uploadedFiles = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadPage('dashboard');
        this.startStatusUpdates();
    }

    setupEventListeners() {
        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-page]')) {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.loadPage(page);
            }
        });

        // Connection buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#connect-btn')) {
                this.connectDrone();
            } else if (e.target.matches('#disconnect-btn')) {
                this.disconnectDrone();
            }
        });

        // Flight control buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#takeoff-btn')) {
                this.takeoff();
            } else if (e.target.matches('#land-btn')) {
                this.land();
            } else if (e.target.matches('#emergency-btn')) {
                this.emergency();
            }
        });

        // Camera buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#start-stream-btn')) {
                this.startStream();
            } else if (e.target.matches('#stop-stream-btn')) {
                this.stopStream();
            }
        });

        // Tracking buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#start-tracking-btn')) {
                this.startTracking();
            } else if (e.target.matches('#stop-tracking-btn')) {
                this.stopTracking();
            }
        });

        // Model management
        document.addEventListener('click', (e) => {
            if (e.target.matches('#train-model-btn')) {
                this.trainModel();
            }
        });

        // File upload
        document.addEventListener('change', (e) => {
            if (e.target.matches('#image-files')) {
                this.handleFileSelect(e);
            }
        });

        // Drag and drop
        document.addEventListener('dragover', (e) => {
            if (e.target.matches('.file-upload')) {
                e.preventDefault();
                e.target.classList.add('dragover');
            }
        });

        document.addEventListener('dragleave', (e) => {
            if (e.target.matches('.file-upload')) {
                e.target.classList.remove('dragover');
            }
        });

        document.addEventListener('drop', (e) => {
            if (e.target.matches('.file-upload')) {
                e.preventDefault();
                e.target.classList.remove('dragover');
                this.handleFileDrop(e);
            }
        });
    }

    async loadPage(page) {
        this.currentPage = page;
        
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNav = document.querySelector(`[data-page="${page}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }

        // Load page content
        try {
            const response = await fetch(`/${page}`);
            const html = await response.text();
            document.getElementById('main-content').innerHTML = html;
            
            // Initialize page-specific functionality
            if (page === 'models') {
                this.loadModels();
            } else if (page === 'tracking') {
                this.initTrackingPage();
            }
        } catch (error) {
            console.error('Error loading page:', error);
            this.showAlert('ページの読み込みに失敗しました', 'danger');
        }
    }

    // Connection Management
    async connectDrone() {
        try {
            this.showLoading('connect-btn');
            await this.api.connectDrone();
            this.isConnected = true;
            this.updateConnectionStatus();
            this.showAlert('ドローンに接続しました', 'success');
        } catch (error) {
            this.showAlert(`接続エラー: ${error.message}`, 'danger');
        } finally {
            this.hideLoading('connect-btn');
        }
    }

    async disconnectDrone() {
        try {
            this.showLoading('disconnect-btn');
            await this.api.disconnectDrone();
            this.isConnected = false;
            this.updateConnectionStatus();
            this.showAlert('ドローンから切断しました', 'success');
        } catch (error) {
            this.showAlert(`切断エラー: ${error.message}`, 'danger');
        } finally {
            this.hideLoading('disconnect-btn');
        }
    }

    // Flight Control
    async takeoff() {
        if (!this.isConnected) {
            this.showAlert('ドローンが接続されていません', 'warning');
            return;
        }

        try {
            this.showLoading('takeoff-btn');
            await this.api.takeoff();
            this.showAlert('離陸しました', 'success');
        } catch (error) {
            this.showAlert(`離陸エラー: ${error.message}`, 'danger');
        } finally {
            this.hideLoading('takeoff-btn');
        }
    }

    async land() {
        try {
            this.showLoading('land-btn');
            await this.api.land();
            this.showAlert('着陸しました', 'success');
        } catch (error) {
            this.showAlert(`着陸エラー: ${error.message}`, 'danger');
        } finally {
            this.hideLoading('land-btn');
        }
    }

    async emergency() {
        try {
            await this.api.emergency();
            this.showAlert('緊急停止しました', 'warning');
        } catch (error) {
            this.showAlert(`緊急停止エラー: ${error.message}`, 'danger');
        }
    }

    // Camera Control
    async startStream() {
        try {
            await this.api.startStream();
            this.updateStreamDisplay();
            this.showAlert('ストリーミングを開始しました', 'success');
        } catch (error) {
            this.showAlert(`ストリーミングエラー: ${error.message}`, 'danger');
        }
    }

    async stopStream() {
        try {
            await this.api.stopStream();
            this.updateStreamDisplay(false);
            this.showAlert('ストリーミングを停止しました', 'success');
        } catch (error) {
            this.showAlert(`ストリーミング停止エラー: ${error.message}`, 'danger');
        }
    }

    updateStreamDisplay(isStreaming = true) {
        const videoFeed = document.getElementById('video-feed');
        if (videoFeed) {
            if (isStreaming) {
                videoFeed.innerHTML = `<img src="${this.api.getStreamURL()}" alt="ライブ映像">`;
            } else {
                videoFeed.innerHTML = '<div class="no-video">映像なし</div>';
            }
        }
    }

    // Object Tracking
    async startTracking() {
        const targetObject = document.getElementById('target-object')?.value;
        const trackingMode = document.getElementById('tracking-mode')?.value || 'center';

        if (!targetObject) {
            this.showAlert('追跡対象を選択してください', 'warning');
            return;
        }

        try {
            this.showLoading('start-tracking-btn');
            await this.api.startTracking(targetObject, trackingMode);
            this.isTracking = true;
            this.updateTrackingStatus();
            this.showAlert('追跡を開始しました', 'success');
        } catch (error) {
            this.showAlert(`追跡開始エラー: ${error.message}`, 'danger');
        } finally {
            this.hideLoading('start-tracking-btn');
        }
    }

    async stopTracking() {
        try {
            this.showLoading('stop-tracking-btn');
            await this.api.stopTracking();
            this.isTracking = false;
            this.updateTrackingStatus();
            this.showAlert('追跡を停止しました', 'success');
        } catch (error) {
            this.showAlert(`追跡停止エラー: ${error.message}`, 'danger');
        } finally {
            this.hideLoading('stop-tracking-btn');
        }
    }

    async initTrackingPage() {
        await this.loadModels();
        this.updateTrackingStatus();
        
        // Start real-time tracking updates
        if (this.trackingUpdateInterval) {
            clearInterval(this.trackingUpdateInterval);
        }
        
        this.trackingUpdateInterval = setInterval(() => {
            this.updateTrackingDisplay();
        }, 100); // 10 FPS
    }

    async updateTrackingDisplay() {
        if (!this.isTracking) return;

        try {
            const status = await this.api.getTrackingStatus();
            this.displayTrackingResults(status);
        } catch (error) {
            console.error('Tracking update error:', error);
        }
    }

    displayTrackingResults(status) {
        const overlay = document.getElementById('detection-overlay');
        if (!overlay) return;

        overlay.innerHTML = '';

        if (status.target_detected && status.target_position) {
            const box = document.createElement('div');
            box.className = 'detection-box';
            box.style.left = `${status.target_position.x}px`;
            box.style.top = `${status.target_position.y}px`;
            box.style.width = `${status.target_position.width}px`;
            box.style.height = `${status.target_position.height}px`;

            const label = document.createElement('div');
            label.className = 'detection-label';
            label.textContent = status.target_object;
            box.appendChild(label);

            overlay.appendChild(box);
        }
    }

    // Model Management
    async loadModels() {
        try {
            const response = await this.api.getModelList();
            this.displayModels(response.models || []);
        } catch (error) {
            console.error('Error loading models:', error);
            this.showAlert('モデル一覧の読み込みに失敗しました', 'danger');
        }
    }

    displayModels(models) {
        const container = document.getElementById('model-list');
        if (!container) return;

        if (models.length === 0) {
            container.innerHTML = '<p class="text-center">まだモデルがありません。新しいモデルを訓練してください。</p>';
            return;
        }

        container.innerHTML = models.map(model => `
            <div class="model-card">
                <div class="model-header">
                    <h3 class="model-name">${model.name}</h3>
                    <span class="model-status ready">準備完了</span>
                </div>
                <div class="model-metrics">
                    <div class="metric">
                        <div class="metric-value">${(model.accuracy * 100).toFixed(1)}%</div>
                        <div class="metric-label">精度</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${new Date(model.created_at).toLocaleDateString()}</div>
                        <div class="metric-label">作成日</div>
                    </div>
                </div>
                <div class="card-actions">
                    <button class="btn btn-primary btn-sm" onclick="app.selectModel('${model.name}')">選択</button>
                    <button class="btn btn-danger btn-sm" onclick="app.deleteModel('${model.name}')">削除</button>
                </div>
            </div>
        `).join('');
    }

    selectModel(modelName) {
        const targetSelect = document.getElementById('target-object');
        if (targetSelect) {
            targetSelect.value = modelName;
        }
        this.showAlert(`モデル "${modelName}" を選択しました`, 'success');
    }

    async trainModel() {
        const objectName = document.getElementById('object-name')?.value;
        
        if (!objectName) {
            this.showAlert('オブジェクト名を入力してください', 'warning');
            return;
        }

        if (this.uploadedFiles.length === 0) {
            this.showAlert('画像ファイルを選択してください', 'warning');
            return;
        }

        try {
            this.showLoading('train-model-btn');
            const response = await this.api.trainModel(objectName, this.uploadedFiles);
            this.showAlert('モデル訓練を開始しました', 'success');
            this.uploadedFiles = [];
            this.updateFileList();
        } catch (error) {
            this.showAlert(`モデル訓練エラー: ${error.message}`, 'danger');
        } finally {
            this.hideLoading('train-model-btn');
        }
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.addFiles(files);
    }

    handleFileDrop(event) {
        const files = Array.from(event.dataTransfer.files);
        this.addFiles(files);
    }

    addFiles(files) {
        const imageFiles = files.filter(file => file.type.startsWith('image/'));
        this.uploadedFiles.push(...imageFiles);
        this.updateFileList();
        
        if (imageFiles.length !== files.length) {
            this.showAlert('画像ファイルのみ選択してください', 'warning');
        }
    }

    updateFileList() {
        const container = document.getElementById('file-list');
        if (!container) return;

        if (this.uploadedFiles.length === 0) {
            container.innerHTML = '';
            return;
        }

        container.innerHTML = this.uploadedFiles.map((file, index) => `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-icon">📷</div>
                    <div class="file-details">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button class="btn btn-sm btn-danger" onclick="app.removeFile(${index})">削除</button>
            </div>
        `).join('');
    }

    removeFile(index) {
        this.uploadedFiles.splice(index, 1);
        this.updateFileList();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Status Updates
    startStatusUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateStatus();
        }, 2000);
    }

    async updateStatus() {
        try {
            const status = await this.api.getDroneStatus();
            this.updateConnectionStatus(status.connected);
            this.updateBattery(status.battery);
        } catch (error) {
            // Silently handle connection errors
            this.updateConnectionStatus(false);
        }
    }

    updateConnectionStatus(connected = this.isConnected) {
        this.isConnected = connected;
        
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `status-indicator ${connected ? 'connected' : 'disconnected'}`;
            indicator.innerHTML = `
                <span class="status-dot"></span>
                ${connected ? '接続中' : '未接続'}
            `;
        }
    }

    updateTrackingStatus(tracking = this.isTracking) {
        this.isTracking = tracking;
        
        const indicator = document.getElementById('tracking-status');
        if (indicator) {
            indicator.className = `status-indicator ${tracking ? 'connected' : 'disconnected'}`;
            indicator.innerHTML = `
                <span class="status-dot"></span>
                ${tracking ? '追跡中' : '停止中'}
            `;
        }
    }

    updateBattery(level) {
        const indicator = document.getElementById('battery-level');
        if (indicator) {
            indicator.textContent = `${level}%`;
        }
    }

    // UI Helpers
    showLoading(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner"></span> 処理中...';
        }
    }

    hideLoading(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = false;
            // Restore original button text (you might want to store this)
            const originalTexts = {
                'connect-btn': '接続',
                'disconnect-btn': '切断',
                'takeoff-btn': '離陸',
                'land-btn': '着陸',
                'start-stream-btn': '開始',
                'stop-stream-btn': '停止',
                'start-tracking-btn': '追跡開始',
                'stop-tracking-btn': '追跡停止',
                'train-model-btn': '訓練開始'
            };
            button.innerHTML = originalTexts[buttonId] || 'ボタン';
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container') || document.body;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        alertContainer.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DroneAdminApp();
});