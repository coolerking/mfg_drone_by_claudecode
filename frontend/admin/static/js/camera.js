// MFG Drone Camera Control JavaScript

class CameraController {
    constructor() {
        this.socket = io();
        this.isStreaming = false;
        this.isRecording = false;
        this.recordingStartTime = null;
        this.recordingTimer = null;
        
        this.initializeElements();
        this.initializeSocketListeners();
        this.initializeEventListeners();
    }
    
    initializeElements() {
        // Video elements
        this.videoElement = document.getElementById('videoStream');
        this.videoPlaceholder = document.getElementById('videoPlaceholder');
        this.recordingIndicator = document.getElementById('recordingIndicator');
        
        // Control buttons
        this.startStreamBtn = document.getElementById('startStreamBtn');
        this.stopStreamBtn = document.getElementById('stopStreamBtn');
        this.capturePhotoBtn = document.getElementById('capturePhotoBtn');
        this.startRecordBtn = document.getElementById('startRecordBtn');
        this.stopRecordBtn = document.getElementById('stopRecordBtn');
        
        // Settings
        this.resolutionSelect = document.getElementById('resolutionSelect');
        this.fpsSelect = document.getElementById('fpsSelect');
        this.bitrateRange = document.getElementById('bitrateRange');
        this.bitrateValue = document.getElementById('bitrateValue');
        
        // Status elements
        this.streamStatus = document.getElementById('streamStatus');
        this.recordStatus = document.getElementById('recordStatus');
        this.alertContainer = document.getElementById('alertContainer');
    }
    
    initializeSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateStreamStatus(false);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
        
        this.socket.on('stream_started', () => {
            this.onStreamStarted();
        });
        
        this.socket.on('stream_stopped', () => {
            this.onStreamStopped();
        });
        
        this.socket.on('recording_started', () => {
            this.onRecordingStarted();
        });
        
        this.socket.on('recording_stopped', () => {
            this.onRecordingStopped();
        });
        
        this.socket.on('photo_captured', (data) => {
            this.onPhotoCaptured(data);
        });
        
        this.socket.on('error', (data) => {
            this.showAlert('danger', data.message || 'エラーが発生しました');
        });
    }
    
    initializeEventListeners() {
        // Stream controls
        this.startStreamBtn?.addEventListener('click', () => this.startStream());
        this.stopStreamBtn?.addEventListener('click', () => this.stopStream());
        
        // Capture controls
        this.capturePhotoBtn?.addEventListener('click', () => this.capturePhoto());
        this.startRecordBtn?.addEventListener('click', () => this.startRecording());
        this.stopRecordBtn?.addEventListener('click', () => this.stopRecording());
        
        // Settings
        this.resolutionSelect?.addEventListener('change', () => this.updateCameraSettings());
        this.fpsSelect?.addEventListener('change', () => this.updateCameraSettings());
        this.bitrateRange?.addEventListener('input', (e) => {
            this.bitrateValue.textContent = e.target.value;
        });
        this.bitrateRange?.addEventListener('change', () => this.updateCameraSettings());
    }
    
    // Stream control methods
    async startStream() {
        try {
            this.startStreamBtn.disabled = true;
            this.showAlert('info', 'ストリーミングを開始しています...');
            
            const response = await fetch('/api/camera/stream/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showAlert('success', 'ストリーミングが開始されました');
            } else {
                throw new Error(data.message || 'ストリーミング開始に失敗しました');
            }
        } catch (error) {
            console.error('Stream start error:', error);
            this.showAlert('danger', error.message);
            this.startStreamBtn.disabled = false;
        }
    }
    
    async stopStream() {
        try {
            this.stopStreamBtn.disabled = true;
            
            const response = await fetch('/api/camera/stream/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showAlert('success', 'ストリーミングが停止されました');
            } else {
                throw new Error(data.message || 'ストリーミング停止に失敗しました');
            }
        } catch (error) {
            console.error('Stream stop error:', error);
            this.showAlert('danger', error.message);
            this.stopStreamBtn.disabled = false;
        }
    }
    
    async capturePhoto() {
        try {
            this.capturePhotoBtn.disabled = true;
            this.showAlert('info', '写真を撮影しています...');
            
            const response = await fetch('/api/camera/photo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showAlert('success', '写真が撮影されました');
            } else {
                throw new Error(data.message || '写真撮影に失敗しました');
            }
        } catch (error) {
            console.error('Photo capture error:', error);
            this.showAlert('danger', error.message);
        } finally {
            this.capturePhotoBtn.disabled = false;
        }
    }
    
    async startRecording() {
        try {
            this.startRecordBtn.disabled = true;
            this.showAlert('info', '録画を開始しています...');
            
            const response = await fetch('/api/camera/video/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showAlert('success', '録画が開始されました');
            } else {
                throw new Error(data.message || '録画開始に失敗しました');
            }
        } catch (error) {
            console.error('Recording start error:', error);
            this.showAlert('danger', error.message);
            this.startRecordBtn.disabled = false;
        }
    }
    
    async stopRecording() {
        try {
            this.stopRecordBtn.disabled = true;
            
            const response = await fetch('/api/camera/video/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showAlert('success', '録画が停止されました');
            } else {
                throw new Error(data.message || '録画停止に失敗しました');
            }
        } catch (error) {
            console.error('Recording stop error:', error);
            this.showAlert('danger', error.message);
            this.stopRecordBtn.disabled = false;
        }
    }
    
    async updateCameraSettings() {
        try {
            const settings = {
                resolution: this.resolutionSelect?.value,
                fps: this.fpsSelect?.value,
                bitrate: parseInt(this.bitrateRange?.value)
            };
            
            const response = await fetch('/api/camera/settings', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showAlert('success', 'カメラ設定が更新されました');
            } else {
                throw new Error(data.message || '設定更新に失敗しました');
            }
        } catch (error) {
            console.error('Settings update error:', error);
            this.showAlert('danger', error.message);
        }
    }
    
    // Event handlers
    onStreamStarted() {
        this.isStreaming = true;
        this.updateStreamStatus(true);
        this.updateStreamControls();
        
        // Start video stream display
        if (this.videoElement) {
            this.videoElement.src = '/api/camera/stream';
            this.videoElement.style.display = 'block';
        }
        if (this.videoPlaceholder) {
            this.videoPlaceholder.style.display = 'none';
        }
    }
    
    onStreamStopped() {
        this.isStreaming = false;
        this.updateStreamStatus(false);
        this.updateStreamControls();
        
        // Stop video stream display
        if (this.videoElement) {
            this.videoElement.src = '';
            this.videoElement.style.display = 'none';
        }
        if (this.videoPlaceholder) {
            this.videoPlaceholder.style.display = 'flex';
        }
    }
    
    onRecordingStarted() {
        this.isRecording = true;
        this.recordingStartTime = Date.now();
        this.updateRecordingControls();
        this.startRecordingTimer();
        
        if (this.recordingIndicator) {
            this.recordingIndicator.style.display = 'block';
            this.recordingIndicator.classList.add('recording');
        }
    }
    
    onRecordingStopped() {
        this.isRecording = false;
        this.recordingStartTime = null;
        this.updateRecordingControls();
        this.stopRecordingTimer();
        
        if (this.recordingIndicator) {
            this.recordingIndicator.style.display = 'none';
            this.recordingIndicator.classList.remove('recording');
        }
    }
    
    onPhotoCaptured(data) {
        this.showAlert('success', `写真が保存されました: ${data.filename || '写真'}`);
    }
    
    // UI update methods
    updateStreamStatus(isStreaming) {
        if (this.streamStatus) {
            const indicator = this.streamStatus.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${isStreaming ? 'status-streaming' : 'status-disconnected'}`;
            }
            this.streamStatus.querySelector('.status-text').textContent = 
                isStreaming ? 'ストリーミング中' : 'ストリーミング停止';
        }
    }
    
    updateStreamControls() {
        if (this.startStreamBtn) {
            this.startStreamBtn.disabled = this.isStreaming;
        }
        if (this.stopStreamBtn) {
            this.stopStreamBtn.disabled = !this.isStreaming;
        }
        if (this.capturePhotoBtn) {
            this.capturePhotoBtn.disabled = !this.isStreaming;
        }
    }
    
    updateRecordingControls() {
        if (this.startRecordBtn) {
            this.startRecordBtn.disabled = this.isRecording;
        }
        if (this.stopRecordBtn) {
            this.stopRecordBtn.disabled = !this.isRecording;
        }
        
        if (this.recordStatus) {
            const indicator = this.recordStatus.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${this.isRecording ? 'status-recording' : 'status-disconnected'}`;
            }
            this.recordStatus.querySelector('.status-text').textContent = 
                this.isRecording ? '録画中' : '録画停止';
        }
    }
    
    startRecordingTimer() {
        this.recordingTimer = setInterval(() => {
            if (this.recordingStartTime && this.recordingIndicator) {
                const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                this.recordingIndicator.textContent = `REC ${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }
    
    stopRecordingTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
    }
    
    showAlert(type, message) {
        if (!this.alertContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        this.alertContainer.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
}

// Initialize camera controller when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cameraController = new CameraController();
});