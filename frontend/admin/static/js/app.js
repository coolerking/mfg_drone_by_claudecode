/**
 * MFG Drone Admin Frontend - メインJavaScriptアプリケーション
 * ドローン制御、カメラ・メディア管理、リアルタイム監視
 */

class DroneAdmin {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.isConnected = false;
        this.isStreaming = false;
        this.isRecording = false;
        this.currentPage = 'dashboard';
        this.updateInterval = null;
        this.mediaFiles = [];
        
        this.init();
    }

    /**
     * アプリケーション初期化
     */
    init() {
        this.setupEventListeners();
        this.initializeNavigation();
        this.startRealtimeUpdates();
        this.loadPage('dashboard');
        console.log('MFG Drone Admin Frontend initialized');
    }

    /**
     * イベントリスナー設定
     */
    setupEventListeners() {
        // ナビゲーション
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-page]')) {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.loadPage(page);
            }
        });

        // ドローン制御ボタン
        document.addEventListener('click', (e) => {
            const action = e.target.getAttribute('data-action');
            if (action) {
                e.preventDefault();
                this.handleAction(action, e.target);
            }
        });

        // カメラ設定変更
        document.addEventListener('change', (e) => {
            if (e.target.matches('.camera-setting')) {
                this.updateCameraSettings();
            }
        });

        // ページ離脱時の処理
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    /**
     * ナビゲーション初期化
     */
    initializeNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.getAttribute('data-page');
                this.setActiveNav(page);
            });
        });
    }

    /**
     * アクティブナビゲーション設定
     */
    setActiveNav(page) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`)?.classList.add('active');
    }

    /**
     * ページロード
     */
    async loadPage(page) {
        this.currentPage = page;
        this.setActiveNav(page);
        
        const content = document.getElementById('main-content');
        if (!content) return;

        // ローディング表示
        content.innerHTML = this.getLoadingHTML();
        
        try {
            const pageContent = await this.getPageContent(page);
            content.innerHTML = pageContent;
            this.initializePageFeatures(page);
        } catch (error) {
            console.error('Page load error:', error);
            content.innerHTML = this.getErrorHTML('ページの読み込みに失敗しました');
        }
    }

    /**
     * ページコンテンツ取得
     */
    async getPageContent(page) {
        switch (page) {
            case 'dashboard':
                return this.getDashboardHTML();
            case 'connection':
                return this.getConnectionHTML();
            case 'camera':
                return this.getCameraHTML();
            case 'media':
                return this.getMediaHTML();
            case 'sensors':
                return this.getSensorsHTML();
            case 'settings':
                return this.getSettingsHTML();
            default:
                return this.getDashboardHTML();
        }
    }

    /**
     * ページ固有機能初期化
     */
    initializePageFeatures(page) {
        switch (page) {
            case 'camera':
                this.initializeCameraPage();
                break;
            case 'media':
                this.initializeMediaPage();
                break;
            case 'sensors':
                this.initializeSensorsPage();
                break;
        }
    }

    // ========== API通信 ==========

    /**
     * API リクエスト送信
     */
    async apiRequest(endpoint, options = {}) {
        try {
            const url = `${this.apiBaseUrl}${endpoint}`;
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            this.showAlert('APIリクエストが失敗しました: ' + error.message, 'danger');
            throw error;
        }
    }

    /**
     * ドローン接続
     */
    async connectDrone() {
        try {
            await this.apiRequest('/drone/connect', { method: 'POST' });
            this.isConnected = true;
            this.showAlert('ドローンに接続しました', 'success');
            this.updateConnectionStatus();
        } catch (error) {
            this.isConnected = false;
            this.showAlert('ドローン接続に失敗しました', 'danger');
        }
    }

    /**
     * ドローン切断
     */
    async disconnectDrone() {
        try {
            await this.apiRequest('/drone/disconnect', { method: 'POST' });
            this.isConnected = false;
            this.isStreaming = false;
            this.isRecording = false;
            this.showAlert('ドローンから切断しました', 'info');
            this.updateConnectionStatus();
        } catch (error) {
            this.showAlert('ドローン切断に失敗しました', 'danger');
        }
    }

    /**
     * ドローン状態取得
     */
    async getDroneStatus() {
        try {
            return await this.apiRequest('/drone/status');
        } catch (error) {
            return null;
        }
    }

    // ========== カメラ制御 ==========

    /**
     * ストリーミング開始
     */
    async startStreaming() {
        try {
            await this.apiRequest('/camera/stream/start', { method: 'POST' });
            this.isStreaming = true;
            this.showAlert('ストリーミングを開始しました', 'success');
            this.updateStreamingUI();
        } catch (error) {
            this.showAlert('ストリーミング開始に失敗しました', 'danger');
        }
    }

    /**
     * ストリーミング停止
     */
    async stopStreaming() {
        try {
            await this.apiRequest('/camera/stream/stop', { method: 'POST' });
            this.isStreaming = false;
            this.showAlert('ストリーミングを停止しました', 'info');
            this.updateStreamingUI();
        } catch (error) {
            this.showAlert('ストリーミング停止に失敗しました', 'danger');
        }
    }

    /**
     * 写真撮影
     */
    async takePhoto() {
        try {
            await this.apiRequest('/camera/photo', { method: 'POST' });
            this.showAlert('写真を撮影しました', 'success');
            this.refreshMediaGallery();
        } catch (error) {
            this.showAlert('写真撮影に失敗しました', 'danger');
        }
    }

    /**
     * 録画開始
     */
    async startRecording() {
        try {
            await this.apiRequest('/camera/video/start', { method: 'POST' });
            this.isRecording = true;
            this.showAlert('録画を開始しました', 'success');
            this.updateRecordingUI();
        } catch (error) {
            this.showAlert('録画開始に失敗しました', 'danger');
        }
    }

    /**
     * 録画停止
     */
    async stopRecording() {
        try {
            await this.apiRequest('/camera/video/stop', { method: 'POST' });
            this.isRecording = false;
            this.showAlert('録画を停止しました', 'info');
            this.updateRecordingUI();
            this.refreshMediaGallery();
        } catch (error) {
            this.showAlert('録画停止に失敗しました', 'danger');
        }
    }

    /**
     * カメラ設定更新
     */
    async updateCameraSettings() {
        const resolution = document.getElementById('camera-resolution')?.value;
        const fps = document.getElementById('camera-fps')?.value;
        const bitrate = document.getElementById('camera-bitrate')?.value;

        if (!resolution || !fps || !bitrate) return;

        try {
            await this.apiRequest('/camera/settings', {
                method: 'PUT',
                body: JSON.stringify({
                    resolution,
                    fps,
                    bitrate: parseInt(bitrate)
                })
            });
            this.showAlert('カメラ設定を更新しました', 'success');
        } catch (error) {
            this.showAlert('カメラ設定の更新に失敗しました', 'danger');
        }
    }

    // ========== UI更新 ==========

    /**
     * 接続状態UI更新
     */
    updateConnectionStatus() {
        const statusElements = document.querySelectorAll('.connection-status');
        statusElements.forEach(el => {
            el.className = `status-indicator ${this.isConnected ? 'connected' : 'disconnected'}`;
            el.innerHTML = `
                <span class="status-dot"></span>
                ${this.isConnected ? '接続中' : '未接続'}
            `;
        });

        // ボタン状態更新
        const connectBtn = document.getElementById('connect-btn');
        const disconnectBtn = document.getElementById('disconnect-btn');
        
        if (connectBtn) {
            connectBtn.disabled = this.isConnected;
            connectBtn.textContent = this.isConnected ? '接続済み' : 'ドローン接続';
        }
        
        if (disconnectBtn) {
            disconnectBtn.disabled = !this.isConnected;
        }
    }

    /**
     * ストリーミングUI更新
     */
    updateStreamingUI() {
        const streamBtn = document.getElementById('stream-btn');
        const videoElement = document.getElementById('video-stream');
        
        if (streamBtn) {
            streamBtn.textContent = this.isStreaming ? 'ストリーミング停止' : 'ストリーミング開始';
            streamBtn.className = `btn ${this.isStreaming ? 'btn-warning' : 'btn-primary'}`;
        }
        
        if (videoElement) {
            if (this.isStreaming) {
                videoElement.src = `${this.apiBaseUrl}/camera/stream`;
                videoElement.style.display = 'block';
            } else {
                videoElement.src = '';
                videoElement.style.display = 'none';
            }
        }

        // ストリーミング状態表示更新
        const statusElements = document.querySelectorAll('.streaming-status');
        statusElements.forEach(el => {
            el.className = `status-indicator ${this.isStreaming ? 'streaming' : 'disconnected'}`;
            el.innerHTML = `
                <span class="status-dot"></span>
                ${this.isStreaming ? 'ストリーミング中' : '停止中'}
            `;
        });
    }

    /**
     * 録画UI更新
     */
    updateRecordingUI() {
        const recordBtn = document.getElementById('record-btn');
        
        if (recordBtn) {
            recordBtn.textContent = this.isRecording ? '録画停止' : '録画開始';
            recordBtn.className = `btn ${this.isRecording ? 'btn-danger' : 'btn-success'}`;
        }

        // 録画状態表示更新
        const statusElements = document.querySelectorAll('.recording-status');
        statusElements.forEach(el => {
            el.className = `status-indicator ${this.isRecording ? 'recording' : 'disconnected'}`;
            el.innerHTML = `
                <span class="status-dot"></span>
                ${this.isRecording ? '録画中' : '停止中'}
            `;
        });
    }

    // ========== アクション処理 ==========

    /**
     * アクション処理
     */
    async handleAction(action, element) {
        // ボタン無効化（重複実行防止）
        element.disabled = true;
        
        try {
            switch (action) {
                case 'connect':
                    await this.connectDrone();
                    break;
                case 'disconnect':
                    await this.disconnectDrone();
                    break;
                case 'stream-toggle':
                    if (this.isStreaming) {
                        await this.stopStreaming();
                    } else {
                        await this.startStreaming();
                    }
                    break;
                case 'take-photo':
                    await this.takePhoto();
                    break;
                case 'record-toggle':
                    if (this.isRecording) {
                        await this.stopRecording();
                    } else {
                        await this.startRecording();
                    }
                    break;
                case 'refresh-media':
                    await this.refreshMediaGallery();
                    break;
                case 'refresh-sensors':
                    await this.updateSensorData();
                    break;
            }
        } finally {
            // ボタン有効化
            setTimeout(() => {
                element.disabled = false;
            }, 1000);
        }
    }

    // ========== HTMLテンプレート ==========

    /**
     * ダッシュボードHTML
     */
    getDashboardHTML() {
        return `
            <div class="fade-in">
                <div class="d-flex align-items-center justify-content-between mb-4">
                    <h1 class="text-xl font-bold">ダッシュボード</h1>
                    <div class="connection-status status-indicator disconnected">
                        <span class="status-dot"></span>
                        未接続
                    </div>
                </div>
                
                <div class="sensor-grid mb-4">
                    <div class="card sensor-card">
                        <div class="card-body">
                            <h3 class="card-title">接続状態</h3>
                            <div class="sensor-value" id="connection-value">未接続</div>
                            <button class="btn btn-primary" data-action="connect" id="connect-btn">ドローン接続</button>
                        </div>
                    </div>
                    
                    <div class="card sensor-card">
                        <div class="card-body">
                            <h3 class="card-title">バッテリー</h3>
                            <div class="sensor-value battery" id="battery-value">--</div>
                            <div class="progress-bar">
                                <div class="progress-fill" id="battery-progress" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card sensor-card">
                        <div class="card-body">
                            <h3 class="card-title">高度</h3>
                            <div class="sensor-value" id="height-value">-- cm</div>
                        </div>
                    </div>
                    
                    <div class="card sensor-card">
                        <div class="card-body">
                            <h3 class="card-title">温度</h3>
                            <div class="sensor-value" id="temperature-value">-- ℃</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">ライブ映像</h2>
                    </div>
                    <div class="card-body">
                        <div class="video-container">
                            <video id="video-stream" class="video-stream" autoplay muted style="display: none;"></video>
                            <div class="video-placeholder" id="video-placeholder">
                                ストリーミングが開始されていません
                            </div>
                            <div class="video-controls">
                                <button class="btn btn-primary" data-action="stream-toggle" id="stream-btn">ストリーミング開始</button>
                                <button class="btn btn-success" data-action="take-photo">写真撮影</button>
                                <button class="btn btn-danger" data-action="record-toggle" id="record-btn">録画開始</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 接続管理HTML
     */
    getConnectionHTML() {
        return `
            <div class="fade-in">
                <h1 class="text-xl font-bold mb-4">ドローン接続管理</h1>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h2 class="card-title">接続制御</h2>
                    </div>
                    <div class="card-body">
                        <div class="d-flex align-items-center gap-4 mb-4">
                            <div class="connection-status status-indicator disconnected">
                                <span class="status-dot"></span>
                                未接続
                            </div>
                            <button class="btn btn-primary" data-action="connect" id="connect-btn">ドローン接続</button>
                            <button class="btn btn-secondary" data-action="disconnect" id="disconnect-btn" disabled>切断</button>
                        </div>
                        
                        <div class="alert alert-info">
                            <strong>接続手順:</strong><br>
                            1. Tello EDUドローンの電源を入れてください<br>
                            2. WiFiでTello EDUネットワークに接続してください<br>
                            3. 「ドローン接続」ボタンをクリックしてください
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">ネットワーク情報</h2>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label">バックエンドAPI URL</label>
                            <input type="text" class="form-control" value="${this.apiBaseUrl}" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">接続タイムアウト</label>
                            <input type="number" class="form-control" value="10" readonly> 秒
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * カメラ制御HTML
     */
    getCameraHTML() {
        return `
            <div class="fade-in">
                <h1 class="text-xl font-bold mb-4">カメラ・映像制御</h1>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h2 class="card-title">ライブストリーミング</h2>
                    </div>
                    <div class="card-body">
                        <div class="video-container mb-4">
                            <video id="video-stream" class="video-stream" autoplay muted style="display: none;"></video>
                            <div class="video-placeholder" id="video-placeholder">
                                ストリーミングを開始してください
                            </div>
                        </div>
                        
                        <div class="d-flex align-items-center gap-3 mb-4">
                            <div class="streaming-status status-indicator disconnected">
                                <span class="status-dot"></span>
                                停止中
                            </div>
                            <div class="recording-status status-indicator disconnected">
                                <span class="status-dot"></span>
                                停止中
                            </div>
                        </div>
                        
                        <div class="d-flex gap-2">
                            <button class="btn btn-primary" data-action="stream-toggle" id="stream-btn">ストリーミング開始</button>
                            <button class="btn btn-success" data-action="take-photo">📷 写真撮影</button>
                            <button class="btn btn-danger" data-action="record-toggle" id="record-btn">🎥 録画開始</button>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">カメラ設定</h2>
                    </div>
                    <div class="card-body">
                        <div class="camera-settings">
                            <div class="form-group">
                                <label class="form-label">解像度</label>
                                <select class="form-control form-select camera-setting" id="camera-resolution">
                                    <option value="high">高解像度</option>
                                    <option value="low">低解像度</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">フレームレート</label>
                                <select class="form-control form-select camera-setting" id="camera-fps">
                                    <option value="high">高</option>
                                    <option value="middle" selected>中</option>
                                    <option value="low">低</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">ビットレート</label>
                                <select class="form-control form-select camera-setting" id="camera-bitrate">
                                    <option value="1">1</option>
                                    <option value="2">2</option>
                                    <option value="3" selected>3</option>
                                    <option value="4">4</option>
                                    <option value="5">5</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * メディア管理HTML
     */
    getMediaHTML() {
        return `
            <div class="fade-in">
                <div class="d-flex align-items-center justify-content-between mb-4">
                    <h1 class="text-xl font-bold">メディア管理</h1>
                    <button class="btn btn-primary" data-action="refresh-media">🔄 更新</button>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h2 class="card-title">ストレージ情報</h2>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span>使用容量</span>
                            <span id="storage-used">-- MB / -- GB</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="storage-progress" style="width: 45%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">メディアギャラリー</h2>
                    </div>
                    <div class="card-body">
                        <div class="media-gallery" id="media-gallery">
                            ${this.getMediaGalleryItems()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * センサー監視HTML
     */
    getSensorsHTML() {
        return `
            <div class="fade-in">
                <div class="d-flex align-items-center justify-content-between mb-4">
                    <h1 class="text-xl font-bold">センサー監視</h1>
                    <button class="btn btn-primary" data-action="refresh-sensors">🔄 更新</button>
                </div>
                
                <div class="sensor-grid">
                    <div class="card sensor-card">
                        <div class="card-body">
                            <h3 class="card-title">バッテリー</h3>
                            <div class="sensor-value battery" id="sensor-battery">--</div>
                            <div class="progress-bar">
                                <div class="progress-fill" id="sensor-battery-progress" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card sensor-card">
                        <div class="card-body">
                            <h3 class="card-title">高度</h3>
                            <div class="sensor-value" id="sensor-height">-- cm</div>
                        </div>
                    </div>
                    
                    <div class="card sensor-card">
                        <div class="card-body">
                            <h3 class="card-title">温度</h3>
                            <div class="sensor-value" id="sensor-temperature">-- ℃</div>
                        </div>
                    </div>
                    
                    <div class="card sensor-card">
                        <div class="card-body">
                            <h3 class="card-title">飛行時間</h3>
                            <div class="sensor-value" id="sensor-flight-time">-- 秒</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 設定HTML
     */
    getSettingsHTML() {
        return `
            <div class="fade-in">
                <h1 class="text-xl font-bold mb-4">システム設定</h1>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h2 class="card-title">API設定</h2>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label">バックエンドAPI URL</label>
                            <input type="url" class="form-control" id="api-url" value="${this.apiBaseUrl}">
                        </div>
                        <button class="btn btn-primary">設定保存</button>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">システム情報</h2>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label class="form-label">フロントエンドバージョン</label>
                            <input type="text" class="form-control" value="1.0.0" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">最終更新</label>
                            <input type="text" class="form-control" value="${new Date().toLocaleString('ja-JP')}" readonly>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // ========== ユーティリティ ==========

    /**
     * ローディングHTML
     */
    getLoadingHTML() {
        return `
            <div class="text-center" style="padding: 4rem;">
                <div class="loading" style="width: 3rem; height: 3rem; border: 4px solid var(--gray-200); border-top: 4px solid var(--primary-color); border-radius: 50%; margin: 0 auto 1rem;"></div>
                <p>読み込み中...</p>
            </div>
        `;
    }

    /**
     * エラーHTML
     */
    getErrorHTML(message) {
        return `
            <div class="alert alert-danger">
                <strong>エラー:</strong> ${message}
            </div>
        `;
    }

    /**
     * メディアギャラリーアイテム生成
     */
    getMediaGalleryItems() {
        // モックデータ（実際の実装では API から取得）
        const mockMedia = [
            { type: 'photo', name: 'photo_001.jpg', date: '2025-06-20 10:30' },
            { type: 'video', name: 'video_001.mp4', date: '2025-06-20 10:25' },
            { type: 'photo', name: 'photo_002.jpg', date: '2025-06-20 10:20' }
        ];

        return mockMedia.map(item => `
            <div class="media-item">
                <div class="media-thumbnail" style="background: var(--gray-200); display: flex; align-items: center; justify-content: center; color: var(--gray-500);">
                    ${item.type === 'photo' ? '📷' : '🎥'}
                </div>
                <div class="media-overlay">
                    <div>${item.name}</div>
                    <div class="text-sm text-gray">${item.date}</div>
                </div>
            </div>
        `).join('');
    }

    /**
     * アラート表示
     */
    showAlert(message, type = 'info') {
        const alertHTML = `
            <div class="alert alert-${type} fade-in" style="position: fixed; top: 1rem; right: 1rem; z-index: 1000; min-width: 300px;">
                ${message}
            </div>
        `;
        
        const alertDiv = document.createElement('div');
        alertDiv.innerHTML = alertHTML;
        document.body.appendChild(alertDiv.firstElementChild);
        
        setTimeout(() => {
            const alert = document.querySelector('.alert');
            if (alert) alert.remove();
        }, 5000);
    }

    // ========== リアルタイム更新 ==========

    /**
     * リアルタイム更新開始
     */
    startRealtimeUpdates() {
        this.updateInterval = setInterval(() => {
            if (this.isConnected) {
                this.updateSensorData();
            }
        }, 2000);
    }

    /**
     * センサーデータ更新
     */
    async updateSensorData() {
        try {
            const [status, battery, height, temperature, flightTime] = await Promise.all([
                this.apiRequest('/drone/status').catch(() => null),
                this.apiRequest('/drone/battery').catch(() => null),
                this.apiRequest('/drone/height').catch(() => null),
                this.apiRequest('/drone/temperature').catch(() => null),
                this.apiRequest('/drone/flight_time').catch(() => null)
            ]);

            this.updateSensorDisplay('battery', battery?.battery, '%');
            this.updateSensorDisplay('height', height?.height, 'cm');
            this.updateSensorDisplay('temperature', temperature?.temperature, '℃');
            this.updateSensorDisplay('flight-time', flightTime?.flight_time, '秒');

            // バッテリープログレスバー更新
            if (battery?.battery) {
                const progressBars = document.querySelectorAll('#battery-progress, #sensor-battery-progress');
                progressBars.forEach(bar => {
                    bar.style.width = `${battery.battery}%`;
                });
            }

        } catch (error) {
            console.error('Sensor data update failed:', error);
        }
    }

    /**
     * センサー表示更新
     */
    updateSensorDisplay(sensor, value, unit) {
        const elements = document.querySelectorAll(`#${sensor}-value, #sensor-${sensor}`);
        elements.forEach(el => {
            if (value !== null && value !== undefined) {
                el.textContent = `${value}${unit}`;
                el.classList.remove('warning', 'danger');
                
                // 警告状態の設定
                if (sensor === 'battery' && value < 20) {
                    el.classList.add(value < 10 ? 'danger' : 'warning');
                } else if (sensor === 'temperature' && value > 70) {
                    el.classList.add(value > 80 ? 'danger' : 'warning');
                }
            } else {
                el.textContent = `--${unit}`;
            }
        });
    }

    /**
     * メディアギャラリー更新
     */
    async refreshMediaGallery() {
        // 実際の実装では API からメディアファイル一覧を取得
        const gallery = document.getElementById('media-gallery');
        if (gallery) {
            gallery.innerHTML = this.getMediaGalleryItems();
        }
    }

    /**
     * カメラページ初期化
     */
    initializeCameraPage() {
        this.updateStreamingUI();
        this.updateRecordingUI();
    }

    /**
     * メディアページ初期化
     */
    initializeMediaPage() {
        this.refreshMediaGallery();
    }

    /**
     * センサーページ初期化
     */
    initializeSensorsPage() {
        this.updateSensorData();
    }

    /**
     * クリーンアップ
     */
    cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    window.droneAdmin = new DroneAdmin();
});

// Google Fonts読み込み
if (!document.querySelector('link[href*="fonts.googleapis.com"]')) {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
}