/**
 * Model Training JavaScript
 * モデル訓練機能のクライアントサイドロジック
 */

class ModelTrainingManager {
    constructor() {
        this.selectedFiles = [];
        this.socket = null;
        this.currentTaskId = null;
        this.init();
    }

    init() {
        this.initializeWebSocket();
        this.setupEventListeners();
        this.updateUI();
    }

    initializeWebSocket() {
        // Socket.IOクライアント接続
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.showConnectionStatus('connected');
            console.log('WebSocket接続が確立されました');
        });

        this.socket.on('disconnect', () => {
            this.showConnectionStatus('disconnected');
            console.log('WebSocket接続が切断されました');
        });

        this.socket.on('training_status', (data) => {
            this.updateTrainingProgress(data);
        });

        this.socket.on('training_complete', (data) => {
            this.onTrainingComplete(data);
        });
    }

    setupEventListeners() {
        // ファイル選択関連
        const fileInput = document.getElementById('imageFiles');
        const uploadZone = document.getElementById('uploadZone');
        
        if (fileInput && uploadZone) {
            // ファイル選択
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelect(e.target.files);
            });

            // ドラッグ&ドロップ
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            });

            uploadZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
            });

            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
                this.handleFileSelect(e.dataTransfer.files);
            });

            uploadZone.addEventListener('click', () => {
                fileInput.click();
            });
        }

        // 訓練開始ボタン
        const trainButton = document.getElementById('startTrainingBtn');
        if (trainButton) {
            trainButton.addEventListener('click', () => {
                this.startTraining();
            });
        }

        // フォーム送信
        const trainingForm = document.getElementById('trainingForm');
        if (trainingForm) {
            trainingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.startTraining();
            });
        }
    }

    handleFileSelect(files) {
        const fileArray = Array.from(files);
        
        // 画像ファイルのみフィルタ
        const imageFiles = fileArray.filter(file => {
            return file.type.startsWith('image/');
        });

        if (imageFiles.length !== fileArray.length) {
            this.showAlert('warning', '画像ファイル以外は除外されました');
        }

        // 既存ファイルに追加
        this.selectedFiles = this.selectedFiles.concat(imageFiles);
        
        // 重複ファイル除去（ファイル名とサイズで判定）
        this.selectedFiles = this.selectedFiles.filter((file, index, arr) => {
            return arr.findIndex(f => f.name === file.name && f.size === file.size) === index;
        });

        this.updateFilePreview();
        this.validateFiles();
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFilePreview();
        this.validateFiles();
    }

    updateFilePreview() {
        const previewContainer = document.getElementById('imagePreview');
        if (!previewContainer) return;

        previewContainer.innerHTML = '';

        this.selectedFiles.forEach((file, index) => {
            const previewDiv = document.createElement('div');
            previewDiv.className = 'image-preview fade-in';

            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.alt = file.name;
            img.title = file.name;

            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-btn';
            removeBtn.innerHTML = '×';
            removeBtn.onclick = () => {
                URL.revokeObjectURL(img.src);
                this.removeFile(index);
            };

            previewDiv.appendChild(img);
            previewDiv.appendChild(removeBtn);
            previewContainer.appendChild(previewDiv);
        });

        // ファイル数表示更新
        const fileCountElement = document.getElementById('fileCount');
        if (fileCountElement) {
            fileCountElement.textContent = this.selectedFiles.length;
        }
    }

    validateFiles() {
        const errors = [];
        const warnings = [];

        // 最小枚数チェック
        if (this.selectedFiles.length < 5) {
            errors.push(`最低5枚の画像が必要です（現在: ${this.selectedFiles.length}枚）`);
        }

        // ファイルサイズチェック
        const maxSize = 10 * 1024 * 1024; // 10MB
        const oversizedFiles = this.selectedFiles.filter(file => file.size > maxSize);
        if (oversizedFiles.length > 0) {
            errors.push(`${oversizedFiles.length}個のファイルが10MBを超えています`);
        }

        // 結果表示
        this.displayValidationResults(errors, warnings);
        
        // 訓練ボタンの有効化/無効化
        const trainButton = document.getElementById('startTrainingBtn');
        if (trainButton) {
            trainButton.disabled = errors.length > 0 || this.selectedFiles.length === 0;
        }

        return errors.length === 0;
    }

    displayValidationResults(errors, warnings) {
        const container = document.getElementById('validationResults');
        if (!container) return;

        container.innerHTML = '';

        if (errors.length > 0) {
            errors.forEach(error => {
                const alert = this.createAlert('danger', error);
                container.appendChild(alert);
            });
        }

        if (warnings.length > 0) {
            warnings.forEach(warning => {
                const alert = this.createAlert('warning', warning);
                container.appendChild(alert);
            });
        }

        if (errors.length === 0 && warnings.length === 0 && this.selectedFiles.length > 0) {
            const successAlert = this.createAlert('success', `${this.selectedFiles.length}枚の画像ファイルが準備完了です`);
            container.appendChild(successAlert);
        }
    }

    async startTraining() {
        const objectName = document.getElementById('objectName')?.value?.trim();
        
        if (!objectName) {
            this.showAlert('danger', 'オブジェクト名を入力してください');
            return;
        }

        if (!this.validateFiles()) {
            this.showAlert('danger', 'ファイルのバリデーションに失敗しました');
            return;
        }

        // フォームデータ作成
        const formData = new FormData();
        formData.append('object_name', objectName);
        
        this.selectedFiles.forEach((file, index) => {
            formData.append('images', file);
        });

        // UI状態更新
        this.setTrainingInProgress(true);

        try {
            const response = await fetch('/model/api/train', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.currentTaskId = result.task_id;
                this.showAlert('success', `訓練を開始しました (Task ID: ${result.task_id})`);
                this.startProgressMonitoring();
            } else {
                this.showAlert('danger', `訓練開始エラー: ${result.error}`);
                this.setTrainingInProgress(false);
            }
        } catch (error) {
            console.error('訓練開始エラー:', error);
            this.showAlert('danger', `ネットワークエラー: ${error.message}`);
            this.setTrainingInProgress(false);
        }
    }

    startProgressMonitoring() {
        if (this.currentTaskId && this.socket) {
            // バックエンドに進行状況をリクエスト
            this.socket.emit('training_status_request', {
                task_id: this.currentTaskId
            });
            
            // 定期的に状況を確認（5秒間隔）
            this.progressInterval = setInterval(() => {
                if (this.currentTaskId) {
                    this.socket.emit('training_status_request', {
                        task_id: this.currentTaskId
                    });
                }
            }, 5000);
        }
    }

    updateTrainingProgress(data) {
        const progressContainer = document.getElementById('trainingProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        if (progressBar) {
            const progress = data.progress || 0;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }

        if (progressText) {
            progressText.textContent = data.message || '処理中...';
        }

        // 完了チェック
        if (data.status === 'completed') {
            this.onTrainingComplete(data);
        } else if (data.status === 'failed') {
            this.onTrainingFailed(data);
        }
    }

    onTrainingComplete(data) {
        this.clearProgressInterval();
        this.setTrainingInProgress(false);
        this.showAlert('success', `モデル訓練が完了しました！精度: ${data.accuracy || 'N/A'}`);
        
        // プログレスバー完了表示
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = '100%';
            progressBar.classList.add('bg-success');
        }

        // フォームリセット
        this.resetForm();
    }

    onTrainingFailed(data) {
        this.clearProgressInterval();
        this.setTrainingInProgress(false);
        this.showAlert('danger', `モデル訓練が失敗しました: ${data.error || '不明なエラー'}`);
        
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.classList.add('bg-danger');
        }
    }

    setTrainingInProgress(inProgress) {
        const trainButton = document.getElementById('startTrainingBtn');
        const objectNameInput = document.getElementById('objectName');
        const fileInput = document.getElementById('imageFiles');

        if (trainButton) {
            trainButton.disabled = inProgress;
            trainButton.innerHTML = inProgress ? 
                '<span class="spinner-border spinner-border-sm" role="status"></span> 訓練中...' : 
                '訓練開始';
        }

        if (objectNameInput) {
            objectNameInput.disabled = inProgress;
        }

        if (fileInput) {
            fileInput.disabled = inProgress;
        }
    }

    clearProgressInterval() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    resetForm() {
        this.selectedFiles = [];
        this.currentTaskId = null;
        this.updateFilePreview();
        
        const objectNameInput = document.getElementById('objectName');
        if (objectNameInput) {
            objectNameInput.value = '';
        }

        const progressContainer = document.getElementById('trainingProgress');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }

        this.validateFiles();
    }

    showConnectionStatus(status) {
        let statusElement = document.getElementById('connectionStatus');
        
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.id = 'connectionStatus';
            statusElement.className = 'connection-status';
            document.body.appendChild(statusElement);
        }

        statusElement.className = `connection-status ${status}`;
        statusElement.innerHTML = status === 'connected' ? 
            '<i class="fas fa-wifi"></i> 接続中' : 
            '<i class="fas fa-exclamation-triangle"></i> 切断';
    }

    createAlert(type, message) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        return alert;
    }

    showAlert(type, message) {
        const container = document.getElementById('alertContainer') || document.body;
        const alert = this.createAlert(type, message);
        container.appendChild(alert);

        // 5秒後に自動削除
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    updateUI() {
        this.validateFiles();
    }
}

// DOM読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', () => {
    window.modelTraining = new ModelTrainingManager();
});