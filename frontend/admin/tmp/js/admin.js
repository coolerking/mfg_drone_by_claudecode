// MFG Drone Admin Interface JavaScript

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let droneConnected = false;
let droneStatus = null;
let trackingActive = false;
let streamActive = false;

// DOM Elements
const connectionIndicator = document.querySelector('.connection-status');
const statusIndicator = document.querySelector('.status-indicator');

// Utility Functions
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.alert-container') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="btn btn-sm">×</button>
        </div>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container';
    container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 1000; width: 300px;';
    document.body.appendChild(container);
    return container;
}

function updateConnectionStatus(connected) {
    droneConnected = connected;
    
    if (connectionIndicator) {
        connectionIndicator.className = `connection-status ${connected ? 'status-connected' : 'status-disconnected'}`;
        connectionIndicator.innerHTML = `
            <div class="status-indicator"></div>
            ${connected ? '接続中' : '切断'}
        `;
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showAlert(`API Error: ${error.message}`, 'danger');
        throw error;
    }
}

// Drone Connection Functions
async function connectDrone() {
    try {
        showAlert('ドローンに接続中...', 'info');
        const result = await apiCall('/drone/connect', { method: 'POST' });
        
        if (result.success) {
            updateConnectionStatus(true);
            showAlert('ドローンに接続しました', 'success');
            await updateDroneStatus();
        } else {
            showAlert('ドローン接続に失敗しました', 'danger');
        }
    } catch (error) {
        showAlert('ドローン接続エラー', 'danger');
    }
}

async function disconnectDrone() {
    try {
        const result = await apiCall('/drone/disconnect', { method: 'POST' });
        
        if (result.success) {
            updateConnectionStatus(false);
            showAlert('ドローンから切断しました', 'info');
        }
    } catch (error) {
        showAlert('ドローン切断エラー', 'danger');
    }
}

// Drone Status Functions
async function updateDroneStatus() {
    try {
        const status = await apiCall('/drone/status');
        droneStatus = status;
        updateStatusDisplay(status);
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

function updateStatusDisplay(status) {
    // Update battery
    const batteryElement = document.querySelector('.battery-level');
    if (batteryElement) {
        batteryElement.textContent = `${status.battery}%`;
        batteryElement.className = `battery-level ${status.battery < 20 ? 'text-danger' : status.battery < 50 ? 'text-warning' : 'text-success'}`;
    }
    
    // Update height
    const heightElement = document.querySelector('.height-value');
    if (heightElement) {
        heightElement.textContent = `${status.height}cm`;
    }
    
    // Update temperature
    const tempElement = document.querySelector('.temperature-value');
    if (tempElement) {
        tempElement.textContent = `${status.temperature}°C`;
    }
    
    // Update flight time
    const flightTimeElement = document.querySelector('.flight-time-value');
    if (flightTimeElement) {
        flightTimeElement.textContent = formatTime(status.flight_time);
    }
}

// Flight Control Functions
async function takeoff() {
    try {
        showAlert('離陸中...', 'info');
        const result = await apiCall('/drone/takeoff', { method: 'POST' });
        
        if (result.success) {
            showAlert('離陸しました', 'success');
            await updateDroneStatus();
        }
    } catch (error) {
        showAlert('離陸に失敗しました', 'danger');
    }
}

async function land() {
    try {
        showAlert('着陸中...', 'info');
        const result = await apiCall('/drone/land', { method: 'POST' });
        
        if (result.success) {
            showAlert('着陸しました', 'success');
            await updateDroneStatus();
        }
    } catch (error) {
        showAlert('着陸に失敗しました', 'danger');
    }
}

async function emergency() {
    if (confirm('緊急停止を実行しますか？')) {
        try {
            const result = await apiCall('/drone/emergency', { method: 'POST' });
            
            if (result.success) {
                showAlert('緊急停止しました', 'warning');
                await updateDroneStatus();
            }
        } catch (error) {
            showAlert('緊急停止に失敗しました', 'danger');
        }
    }
}

// Movement Functions
async function moveDrone(direction, distance = 50) {
    try {
        const result = await apiCall('/drone/move', {
            method: 'POST',
            body: JSON.stringify({ direction, distance })
        });
        
        if (result.success) {
            showAlert(`${direction}に${distance}cm移動しました`, 'success');
        }
    } catch (error) {
        showAlert('移動に失敗しました', 'danger');
    }
}

// Camera Functions
async function startStream() {
    try {
        const result = await apiCall('/camera/stream/start', { method: 'POST' });
        
        if (result.success) {
            streamActive = true;
            showAlert('ストリーミングを開始しました', 'success');
            
            // Update video element
            const videoElement = document.querySelector('.video-stream');
            if (videoElement) {
                videoElement.src = `${API_BASE_URL}/camera/stream`;
            }
        }
    } catch (error) {
        showAlert('ストリーミング開始に失敗しました', 'danger');
    }
}

async function stopStream() {
    try {
        const result = await apiCall('/camera/stream/stop', { method: 'POST' });
        
        if (result.success) {
            streamActive = false;
            showAlert('ストリーミングを停止しました', 'info');
            
            // Clear video element
            const videoElement = document.querySelector('.video-stream');
            if (videoElement) {
                videoElement.src = '';
            }
        }
    } catch (error) {
        showAlert('ストリーミング停止に失敗しました', 'danger');
    }
}

async function takePhoto() {
    try {
        const result = await apiCall('/camera/photo', { method: 'POST' });
        
        if (result.success) {
            showAlert('写真を撮影しました', 'success');
        }
    } catch (error) {
        showAlert('写真撮影に失敗しました', 'danger');
    }
}

// Tracking Functions
async function startTracking(targetObject) {
    try {
        const result = await apiCall('/tracking/start', {
            method: 'POST',
            body: JSON.stringify({ target_object: targetObject })
        });
        
        if (result.success) {
            trackingActive = true;
            showAlert(`${targetObject}の追跡を開始しました`, 'success');
        }
    } catch (error) {
        showAlert('追跡開始に失敗しました', 'danger');
    }
}

async function stopTracking() {
    try {
        const result = await apiCall('/tracking/stop', { method: 'POST' });
        
        if (result.success) {
            trackingActive = false;
            showAlert('追跡を停止しました', 'info');
        }
    } catch (error) {
        showAlert('追跡停止に失敗しました', 'danger');
    }
}

// Model Management Functions
async function loadModels() {
    try {
        const result = await apiCall('/model/list');
        
        const modelList = document.querySelector('.model-list');
        if (modelList && result.models) {
            modelList.innerHTML = result.models.map(model => `
                <div class="model-item">
                    <h4>${model.name}</h4>
                    <p>作成日: ${new Date(model.created_at).toLocaleDateString()}</p>
                    <p>精度: ${(model.accuracy * 100).toFixed(1)}%</p>
                </div>
            `).join('');
        }
    } catch (error) {
        showAlert('モデル一覧の取得に失敗しました', 'danger');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Connection buttons
    const connectBtn = document.querySelector('.connect-btn');
    const disconnectBtn = document.querySelector('.disconnect-btn');
    
    if (connectBtn) connectBtn.addEventListener('click', connectDrone);
    if (disconnectBtn) disconnectBtn.addEventListener('click', disconnectDrone);
    
    // Flight control buttons
    const takeoffBtn = document.querySelector('.takeoff-btn');
    const landBtn = document.querySelector('.land-btn');
    const emergencyBtn = document.querySelector('.emergency-btn');
    
    if (takeoffBtn) takeoffBtn.addEventListener('click', takeoff);
    if (landBtn) landBtn.addEventListener('click', land);
    if (emergencyBtn) emergencyBtn.addEventListener('click', emergency);
    
    // Movement buttons
    document.querySelectorAll('.movement-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const direction = this.dataset.direction;
            const distance = parseInt(document.querySelector('.distance-input')?.value) || 50;
            moveDrone(direction, distance);
        });
    });
    
    // Camera buttons
    const startStreamBtn = document.querySelector('.start-stream-btn');
    const stopStreamBtn = document.querySelector('.stop-stream-btn');
    const photoBtn = document.querySelector('.photo-btn');
    
    if (startStreamBtn) startStreamBtn.addEventListener('click', startStream);
    if (stopStreamBtn) stopStreamBtn.addEventListener('click', stopStream);
    if (photoBtn) photoBtn.addEventListener('click', takePhoto);
    
    // Tracking buttons
    const startTrackingBtn = document.querySelector('.start-tracking-btn');
    const stopTrackingBtn = document.querySelector('.stop-tracking-btn');
    
    if (startTrackingBtn) {
        startTrackingBtn.addEventListener('click', function() {
            const targetObject = document.querySelector('.target-object-input')?.value;
            if (targetObject) {
                startTracking(targetObject);
            } else {
                showAlert('追跡対象を選択してください', 'warning');
            }
        });
    }
    
    if (stopTrackingBtn) stopTrackingBtn.addEventListener('click', stopTracking);
    
    // Initial status update
    updateDroneStatus();
    
    // Periodic status updates
    setInterval(updateDroneStatus, 5000);
    
    // Load models on model management page
    if (document.querySelector('.model-list')) {
        loadModels();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Only handle shortcuts when no input is focused
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
        return;
    }
    
    switch(e.key) {
        case 'c':
            if (e.ctrlKey) return; // Prevent conflict with Ctrl+C
            if (!droneConnected) connectDrone();
            break;
        case 'd':
            if (e.ctrlKey) return; // Prevent conflict with Ctrl+D
            if (droneConnected) disconnectDrone();
            break;
        case 't':
            takeoff();
            break;
        case 'l':
            land();
            break;
        case 'e':
            emergency();
            break;
        case 'ArrowUp':
        case 'w':
            e.preventDefault();
            moveDrone('up');
            break;
        case 'ArrowDown':
        case 's':
            e.preventDefault();
            moveDrone('down');
            break;
        case 'ArrowLeft':
        case 'a':
            e.preventDefault();
            moveDrone('left');
            break;
        case 'ArrowRight':
        case 'd':
            e.preventDefault();
            moveDrone('right');
            break;
    }
});

// Export functions for global access
window.DroneAdmin = {
    connectDrone,
    disconnectDrone,
    takeoff,
    land,
    emergency,
    moveDrone,
    startStream,
    stopStream,
    takePhoto,
    startTracking,
    stopTracking,
    loadModels,
    showAlert,
    updateDroneStatus
};