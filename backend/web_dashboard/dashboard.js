/**
 * MFG Drone Control Dashboard
 * Phase 5 - Web Dashboard Implementation
 */

class DroneDashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.wsUrl = 'ws://localhost:8000/ws';
        this.apiKey = '';
        this.websocket = null;
        this.selectedDroneId = '';
        this.isConnected = false;
        this.updateInterval = null;
        this.charts = {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadDefaultApiKey();
    }

    loadDefaultApiKey() {
        const apiKeyInput = document.getElementById('apiKey');
        this.apiKey = apiKeyInput.value || 'mfg-drone-admin-key-2024';
    }

    setupEventListeners() {
        // Connection
        document.getElementById('connectBtn').addEventListener('click', () => this.connect());
        
        // API Key input
        document.getElementById('apiKey').addEventListener('change', (e) => {
            this.apiKey = e.target.value;
        });

        // Drone selection
        document.getElementById('droneSelector').addEventListener('change', (e) => {
            this.selectedDroneId = e.target.value;
            if (this.selectedDroneId) {
                this.updateDroneStatus();
            }
        });

        // Drone control buttons
        document.getElementById('connectDrone').addEventListener('click', () => this.connectDrone());
        document.getElementById('disconnectDrone').addEventListener('click', () => this.disconnectDrone());
        document.getElementById('takeoffDrone').addEventListener('click', () => this.takeoffDrone());
        document.getElementById('landDrone').addEventListener('click', () => this.landDrone());
        document.getElementById('emergencyStop').addEventListener('click', () => this.emergencyStop());

        // Movement controls
        document.querySelectorAll('.move-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const direction = e.target.closest('.move-btn').dataset.direction;
                this.moveDrone(direction);
            });
        });

        // Distance slider
        const distanceSlider = document.getElementById('moveDistance');
        const distanceValue = document.getElementById('distanceValue');
        distanceSlider.addEventListener('input', (e) => {
            distanceValue.textContent = `${e.target.value} cm`;
        });

        // Camera controls
        document.getElementById('startStream').addEventListener('click', () => this.startCameraStream());
        document.getElementById('stopStream').addEventListener('click', () => this.stopCameraStream());
        document.getElementById('takePhoto').addEventListener('click', () => this.takePhoto());

        // Vision controls
        document.getElementById('startDetection').addEventListener('click', () => this.startDetection());
        document.getElementById('stopDetection').addEventListener('click', () => this.stopDetection());
        document.getElementById('startTracking').addEventListener('click', () => this.startTracking());
        document.getElementById('stopTracking').addEventListener('click', () => this.stopTracking());

        // Refresh buttons
        document.getElementById('refreshOverview').addEventListener('click', () => this.updateSystemOverview());
        document.getElementById('refreshAlerts').addEventListener('click', () => this.updateAlerts());
    }

    async connect() {
        try {
            this.updateConnectionStatus('connecting', 'Connecting...');
            
            // Test API connection
            const response = await this.apiCall('/health');
            if (response.status === 'healthy') {
                await this.connectWebSocket();
                this.isConnected = true;
                this.updateConnectionStatus('connected', 'Connected');
                this.startPeriodicUpdates();
                this.showNotification('Connected successfully!', 'success');
            } else {
                throw new Error('API health check failed');
            }
        } catch (error) {
            console.error('Connection failed:', error);
            this.updateConnectionStatus('disconnected', 'Connection failed');
            this.showNotification('Connection failed: ' + error.message, 'error');
        }
    }

    async connectWebSocket() {
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(this.wsUrl);
                
                this.websocket.onopen = () => {
                    console.log('WebSocket connected');
                    resolve();
                };

                this.websocket.onmessage = (event) => {
                    this.handleWebSocketMessage(JSON.parse(event.data));
                };

                this.websocket.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.isConnected = false;
                    this.updateConnectionStatus('disconnected', 'Disconnected');
                };

                this.websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    handleWebSocketMessage(data) {
        if (data.type === 'drone_status' && data.drone_id === this.selectedDroneId) {
            this.updateDroneStatusDisplay(data.status);
        } else if (data.type === 'system_status') {
            this.updateSystemMetrics(data.status);
        } else if (data.type === 'alert') {
            this.handleAlert(data.alert);
        }
    }

    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            }
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    updateConnectionStatus(status, message) {
        const statusElement = document.getElementById('connectionStatus');
        statusElement.className = `connection-status ${status}`;
        
        let icon = 'fas fa-circle-notch fa-spin';
        if (status === 'connected') icon = 'fas fa-check-circle';
        else if (status === 'disconnected') icon = 'fas fa-times-circle';
        
        statusElement.innerHTML = `<i class="${icon}"></i> ${message}`;
    }

    startPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Update every 5 seconds
        this.updateInterval = setInterval(() => {
            this.updateSystemOverview();
            this.updateAlerts();
            if (this.selectedDroneId) {
                this.updateDroneStatus();
            }
        }, 5000);

        // Initial updates
        this.updateSystemOverview();
        this.updateAlerts();
    }

    async updateSystemOverview() {
        try {
            const systemStatus = await this.apiCall('/api/dashboard/system');
            this.updateSystemMetrics(systemStatus);
        } catch (error) {
            console.error('Failed to update system overview:', error);
        }
    }

    updateSystemMetrics(status) {
        // Update CPU usage
        document.getElementById('cpuUsage').textContent = `${status.cpu_usage?.toFixed(1) || '--'}%`;
        this.updateChart('cpuChart', status.cpu_usage || 0);

        // Update Memory usage
        document.getElementById('memoryUsage').textContent = `${status.memory_usage?.toFixed(1) || '--'}%`;
        this.updateChart('memoryChart', status.memory_usage || 0);

        // Update connected drones
        document.getElementById('connectedDrones').textContent = status.connected_drones || '--';

        // Update active alerts
        document.getElementById('activeAlerts').textContent = status.active_alerts || '--';

        // Update last update time
        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
    }

    async updateDroneStatus() {
        if (!this.selectedDroneId) return;

        try {
            const droneStatus = await this.apiCall(`/api/drones/${this.selectedDroneId}/status`);
            this.updateDroneStatusDisplay(droneStatus);
        } catch (error) {
            console.error('Failed to update drone status:', error);
        }
    }

    updateDroneStatusDisplay(status) {
        document.getElementById('droneConnection').textContent = status.connection_status || 'Unknown';
        document.getElementById('droneConnection').className = `status-value status-${status.connection_status}`;
        
        document.getElementById('flightStatus').textContent = status.flight_status || 'Unknown';
        document.getElementById('flightStatus').className = `status-value status-${status.flight_status}`;
        
        document.getElementById('batteryLevel').textContent = `${status.battery_level || '--'}%`;
        document.getElementById('droneHeight').textContent = `${status.height || '--'} cm`;
    }

    async updateAlerts() {
        try {
            const alertsResponse = await this.apiCall('/api/alerts?unresolved_only=true');
            this.displayAlerts(alertsResponse.alerts || []);
        } catch (error) {
            console.error('Failed to update alerts:', error);
        }
    }

    displayAlerts(alerts) {
        const alertsList = document.getElementById('alertsList');
        
        if (alerts.length === 0) {
            alertsList.innerHTML = '<div class="alert-item"><div class="alert-message">No active alerts</div></div>';
            return;
        }

        alertsList.innerHTML = alerts.map(alert => `
            <div class="alert-item alert-${alert.severity}">
                <div class="alert-header">
                    <span class="alert-title">${alert.title}</span>
                    <span class="alert-time">${new Date(alert.created_at).toLocaleString()}</span>
                </div>
                <div class="alert-message">${alert.message}</div>
            </div>
        `).join('');
    }

    // Drone Control Methods
    async connectDrone() {
        if (!this.selectedDroneId) {
            this.showNotification('Please select a drone first', 'warning');
            return;
        }

        try {
            await this.apiCall(`/api/drones/${this.selectedDroneId}/connect`, { method: 'POST' });
            this.showNotification('Drone connected successfully', 'success');
            await this.updateDroneStatus();
        } catch (error) {
            this.showNotification('Failed to connect drone: ' + error.message, 'error');
        }
    }

    async disconnectDrone() {
        if (!this.selectedDroneId) return;

        try {
            await this.apiCall(`/api/drones/${this.selectedDroneId}/disconnect`, { method: 'POST' });
            this.showNotification('Drone disconnected', 'info');
            await this.updateDroneStatus();
        } catch (error) {
            this.showNotification('Failed to disconnect drone: ' + error.message, 'error');
        }
    }

    async takeoffDrone() {
        if (!this.selectedDroneId) return;

        try {
            await this.apiCall(`/api/drones/${this.selectedDroneId}/takeoff`, { method: 'POST' });
            this.showNotification('Drone takeoff initiated', 'success');
            await this.updateDroneStatus();
        } catch (error) {
            this.showNotification('Failed to takeoff: ' + error.message, 'error');
        }
    }

    async landDrone() {
        if (!this.selectedDroneId) return;

        try {
            await this.apiCall(`/api/drones/${this.selectedDroneId}/land`, { method: 'POST' });
            this.showNotification('Drone landing initiated', 'success');
            await this.updateDroneStatus();
        } catch (error) {
            this.showNotification('Failed to land: ' + error.message, 'error');
        }
    }

    async emergencyStop() {
        if (!this.selectedDroneId) return;

        try {
            await this.apiCall(`/api/drones/${this.selectedDroneId}/emergency`, { method: 'POST' });
            this.showNotification('Emergency stop activated', 'warning');
            await this.updateDroneStatus();
        } catch (error) {
            this.showNotification('Failed emergency stop: ' + error.message, 'error');
        }
    }

    async moveDrone(direction) {
        if (!this.selectedDroneId) return;

        const distance = parseInt(document.getElementById('moveDistance').value);
        
        try {
            await this.apiCall(`/api/drones/${this.selectedDroneId}/move`, {
                method: 'POST',
                body: JSON.stringify({ direction, distance })
            });
            this.showNotification(`Moving ${direction} ${distance}cm`, 'info');
        } catch (error) {
            this.showNotification('Failed to move drone: ' + error.message, 'error');
        }
    }

    // Camera & Vision Methods
    async startCameraStream() {
        if (!this.selectedDroneId) return;

        try {
            await this.apiCall(`/api/drones/${this.selectedDroneId}/camera/stream/start`, { method: 'POST' });
            this.showNotification('Camera stream started', 'success');
            
            // Update stream placeholder
            const streamElement = document.getElementById('cameraStream');
            streamElement.innerHTML = `
                <div style="background: #000; color: #fff; padding: 2rem; text-align: center;">
                    <i class="fas fa-video"></i>
                    <p>Camera stream active for ${this.selectedDroneId}</p>
                    <p style="font-size: 0.8rem; opacity: 0.7;">Live stream would appear here in production</p>
                </div>
            `;
        } catch (error) {
            this.showNotification('Failed to start camera: ' + error.message, 'error');
        }
    }

    async stopCameraStream() {
        if (!this.selectedDroneId) return;

        try {
            await this.apiCall(`/api/drones/${this.selectedDroneId}/camera/stream/stop`, { method: 'POST' });
            this.showNotification('Camera stream stopped', 'info');
            
            // Reset stream placeholder
            const streamElement = document.getElementById('cameraStream');
            streamElement.innerHTML = `
                <i class="fas fa-camera-slash"></i>
                <p>Camera stream not active</p>
            `;
        } catch (error) {
            this.showNotification('Failed to stop camera: ' + error.message, 'error');
        }
    }

    async takePhoto() {
        if (!this.selectedDroneId) return;

        try {
            const photo = await this.apiCall(`/api/drones/${this.selectedDroneId}/camera/photo`, { method: 'POST' });
            this.showNotification('Photo taken successfully', 'success');
            console.log('Photo data:', photo);
        } catch (error) {
            this.showNotification('Failed to take photo: ' + error.message, 'error');
        }
    }

    async startDetection() {
        const modelId = document.getElementById('modelSelector').value;
        if (!modelId) {
            this.showNotification('Please select a model first', 'warning');
            return;
        }

        try {
            this.showNotification('Object detection started', 'success');
            // In a real implementation, this would start continuous detection
        } catch (error) {
            this.showNotification('Failed to start detection: ' + error.message, 'error');
        }
    }

    async stopDetection() {
        try {
            this.showNotification('Object detection stopped', 'info');
        } catch (error) {
            this.showNotification('Failed to stop detection: ' + error.message, 'error');
        }
    }

    async startTracking() {
        const modelId = document.getElementById('modelSelector').value;
        if (!modelId || !this.selectedDroneId) {
            this.showNotification('Please select both a model and drone', 'warning');
            return;
        }

        try {
            await this.apiCall('/api/vision/tracking/start', {
                method: 'POST',
                body: JSON.stringify({
                    model_id: modelId,
                    drone_id: this.selectedDroneId,
                    follow_distance: 200
                })
            });
            this.showNotification('Object tracking started', 'success');
            document.getElementById('trackingStatus').textContent = 'Status: Active';
        } catch (error) {
            this.showNotification('Failed to start tracking: ' + error.message, 'error');
        }
    }

    async stopTracking() {
        try {
            await this.apiCall('/api/vision/tracking/stop', { method: 'POST' });
            this.showNotification('Object tracking stopped', 'info');
            document.getElementById('trackingStatus').textContent = 'Status: Inactive';
        } catch (error) {
            this.showNotification('Failed to stop tracking: ' + error.message, 'error');
        }
    }

    // Chart Management
    initializeCharts() {
        // CPU Chart
        const cpuCtx = document.getElementById('cpuChart').getContext('2d');
        this.charts.cpu = new Chart(cpuCtx, {
            type: 'line',
            data: {
                labels: Array(10).fill(''),
                datasets: [{
                    data: Array(10).fill(0),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { display: false, min: 0, max: 100 }
                }
            }
        });

        // Memory Chart
        const memoryCtx = document.getElementById('memoryChart').getContext('2d');
        this.charts.memory = new Chart(memoryCtx, {
            type: 'line',
            data: {
                labels: Array(10).fill(''),
                datasets: [{
                    data: Array(10).fill(0),
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { display: false, min: 0, max: 100 }
                }
            }
        });

        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        this.charts.performance = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: Array(20).fill('').map((_, i) => new Date(Date.now() - (19-i) * 30000).toLocaleTimeString()),
                datasets: [
                    {
                        label: 'CPU Usage (%)',
                        data: Array(20).fill(0),
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 2,
                        tension: 0.4
                    },
                    {
                        label: 'Memory Usage (%)',
                        data: Array(20).fill(0),
                        borderColor: '#27ae60',
                        backgroundColor: 'rgba(39, 174, 96, 0.1)',
                        borderWidth: 2,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'top' }
                },
                scales: {
                    x: { display: true },
                    y: { display: true, min: 0, max: 100, title: { display: true, text: 'Usage (%)' } }
                }
            }
        });
    }

    updateChart(chartName, value) {
        const chart = this.charts[chartName.replace('Chart', '')];
        if (!chart) return;

        const data = chart.data.datasets[0].data;
        data.shift();
        data.push(value);
        chart.update('none');
    }

    // Utility Methods
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;

        // Add to DOM
        document.body.appendChild(notification);

        // Add styles if not already present
        if (!document.getElementById('notificationStyles')) {
            const style = document.createElement('style');
            style.id = 'notificationStyles';
            style.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 1rem 1.5rem;
                    border-radius: 6px;
                    color: white;
                    font-weight: 500;
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    min-width: 300px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    animation: slideIn 0.3s ease-out;
                }
                .notification-success { background: #27ae60; }
                .notification-error { background: #e74c3c; }
                .notification-warning { background: #f39c12; }
                .notification-info { background: #3498db; }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    handleAlert(alert) {
        this.showNotification(`Alert: ${alert.message}`, alert.severity);
        this.updateAlerts(); // Refresh alerts display
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DroneDashboard();
});

// Add some global utility functions
window.formatBytes = function(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

window.formatDuration = function(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
};