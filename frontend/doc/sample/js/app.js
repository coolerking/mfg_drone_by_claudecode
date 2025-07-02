// MFG Drone Frontend - Sample Screens JavaScript

// ============ Global Variables ============
let currentUser = null;
let drones = [];
let datasets = [];
let models = [];
let trackingStatus = { active: false, target: null };
let systemStatus = { cpu: 45, memory: 67, disk: 23 };

// ============ Initialization ============
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize dummy data
    loadDummyData();
    
    // Set up navigation
    setupNavigation();
    
    // Set up page-specific functionality
    const currentPage = getCurrentPage();
    initializePage(currentPage);
    
    // Set up auto-refresh for dashboard
    if (currentPage === 'dashboard') {
        setInterval(updateDashboardData, 5000);
    }
}

// ============ Dummy Data Generation ============
function loadDummyData() {
    // Dummy drones
    drones = [
        {
            id: 'drone_001',
            name: 'Tello EDU - Alpha',
            status: 'online',
            battery: 85,
            altitude: 1.2,
            temperature: 23.5,
            location: { x: 100, y: 50, z: 1.2 },
            lastSeen: new Date()
        },
        {
            id: 'drone_002',
            name: 'Tello EDU - Beta',
            status: 'offline',
            battery: 34,
            altitude: 0,
            temperature: 21.8,
            location: { x: 0, y: 0, z: 0 },
            lastSeen: new Date(Date.now() - 1800000) // 30 min ago
        },
        {
            id: 'drone_003',
            name: 'Tello EDU - Gamma',
            status: 'warning',
            battery: 15,
            altitude: 2.5,
            temperature: 28.2,
            location: { x: 75, y: 120, z: 2.5 },
            lastSeen: new Date()
        }
    ];
    
    // Dummy datasets
    datasets = [
        {
            id: 'dataset_001',
            name: 'Person Detection v1.0',
            description: 'Training dataset for person detection',
            imageCount: 1250,
            labels: ['person', 'background'],
            created: '2025-06-15',
            status: 'completed'
        },
        {
            id: 'dataset_002',
            name: 'Vehicle Detection',
            description: 'Cars, trucks, motorcycles detection',
            imageCount: 850,
            labels: ['car', 'truck', 'motorcycle', 'background'],
            created: '2025-06-20',
            status: 'in_progress'
        },
        {
            id: 'dataset_003',
            name: 'Pet Detection',
            description: 'Dogs and cats tracking dataset',
            imageCount: 2100,
            labels: ['dog', 'cat', 'background'],
            created: '2025-06-25',
            status: 'completed'
        }
    ];
    
    // Dummy models
    models = [
        {
            id: 'model_001',
            name: 'PersonTracker_v2.3',
            dataset: 'Person Detection v1.0',
            accuracy: 94.2,
            trainingTime: '2h 35m',
            status: 'trained',
            created: '2025-06-16'
        },
        {
            id: 'model_002',
            name: 'VehicleDetector_v1.1',
            dataset: 'Vehicle Detection',
            accuracy: 0,
            trainingTime: '1h 15m',
            status: 'training',
            created: '2025-06-21'
        },
        {
            id: 'model_003',
            name: 'PetFollower_v1.0',
            dataset: 'Pet Detection',
            accuracy: 91.8,
            trainingTime: '3h 22m',
            status: 'trained',
            created: '2025-06-26'
        }
    ];
    
    // Current user simulation
    currentUser = {
        name: 'Administrator',
        role: 'admin',
        loginTime: new Date()
    };
}

// ============ Navigation Functions ============
function setupNavigation() {
    // Add click handlers for all navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Mobile menu toggle
    const mobileToggle = document.querySelector('.mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
}

function getCurrentPage() {
    const path = window.location.pathname;
    const filename = path.split('/').pop().replace('.html', '');
    return filename || 'index';
}

function initializePage(page) {
    switch(page) {
        case 'dashboard':
        case 'index':
            initializeDashboard();
            break;
        case 'drone-management':
            initializeDroneManagement();
            break;
        case 'drone-detail':
            initializeDroneDetail();
            break;
        case 'camera-video':
            initializeCameraVideo();
            break;
        case 'dataset-management':
            initializeDatasetManagement();
            break;
        case 'model-management':
            initializeModelManagement();
            break;
        case 'tracking-control':
            initializeTrackingControl();
            break;
        case 'tracking-monitor':
            initializeTrackingMonitor();
            break;
        case 'system-monitoring':
            initializeSystemMonitoring();
            break;
        case 'login':
            initializeLogin();
            break;
        default:
            console.log('Page specific initialization not found for:', page);
    }
}

// ============ Page-Specific Initialization ============
function initializeDashboard() {
    updateDashboardStats();
    loadRecentActivity();
    updateSystemStatus();
}

function initializeDroneManagement() {
    populateDroneList();
}

function initializeDroneDetail() {
    const urlParams = new URLSearchParams(window.location.search);
    const droneId = urlParams.get('id') || 'drone_001';
    loadDroneDetails(droneId);
}

function initializeCameraVideo() {
    startVideoSimulation();
}

function initializeDatasetManagement() {
    populateDatasetList();
}

function initializeModelManagement() {
    populateModelList();
}

function initializeTrackingControl() {
    setupTrackingControls();
    loadAvailableModels();
}

function initializeTrackingMonitor() {
    startTrackingSimulation();
}

function initializeSystemMonitoring() {
    updateSystemMetrics();
    startSystemMonitoring();
}

function initializeLogin() {
    setupLoginForm();
}

// ============ Dashboard Functions ============
function updateDashboardStats() {
    const onlineDrones = drones.filter(d => d.status === 'online').length;
    const totalDatasets = datasets.length;
    const trainedModels = models.filter(m => m.status === 'trained').length;
    const activeTracking = trackingStatus.active ? 1 : 0;
    
    // Update stat cards
    updateElement('stat-drones', onlineDrones);
    updateElement('stat-datasets', totalDatasets);
    updateElement('stat-models', trainedModels);
    updateElement('stat-tracking', activeTracking);
}

function loadRecentActivity() {
    const activities = [
        { time: '10:30', action: 'Drone Alpha connected', type: 'info' },
        { time: '10:25', action: 'Model training completed: PersonTracker_v2.3', type: 'success' },
        { time: '10:20', action: 'Dataset uploaded: Vehicle Detection', type: 'info' },
        { time: '10:15', action: 'Drone Beta low battery warning', type: 'warning' },
        { time: '10:10', action: 'Tracking session started', type: 'success' }
    ];
    
    const activityList = document.querySelector('#recent-activity');
    if (activityList) {
        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item ${activity.type}">
                <span class="time">${activity.time}</span>
                <span class="action">${activity.action}</span>
            </div>
        `).join('');
    }
}

function updateSystemStatus() {
    const cpu = Math.floor(Math.random() * 30) + 30; // 30-60%
    const memory = Math.floor(Math.random() * 40) + 40; // 40-80%
    const disk = Math.floor(Math.random() * 20) + 15; // 15-35%
    
    updateProgressBar('cpu-usage', cpu);
    updateProgressBar('memory-usage', memory);
    updateProgressBar('disk-usage', disk);
    
    systemStatus = { cpu, memory, disk };
}

function updateDashboardData() {
    updateSystemStatus();
    // Simulate random drone status changes
    drones.forEach(drone => {
        if (Math.random() < 0.1) { // 10% chance of status change
            drone.battery = Math.max(0, drone.battery - Math.floor(Math.random() * 3));
            drone.temperature = 20 + Math.random() * 15;
        }
    });
    updateDashboardStats();
}

// ============ Drone Functions ============
function populateDroneList() {
    const droneList = document.querySelector('#drone-list');
    if (!droneList) return;
    
    droneList.innerHTML = drones.map(drone => `
        <tr>
            <td>
                <a href="drone-detail.html?id=${drone.id}" class="drone-link">
                    ${drone.name}
                </a>
            </td>
            <td><span class="status status-${drone.status}">${drone.status.toUpperCase()}</span></td>
            <td>${drone.battery}%</td>
            <td>${drone.altitude}m</td>
            <td>${drone.temperature}°C</td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="controlDrone('${drone.id}', 'connect')">
                    ${drone.status === 'online' ? 'Disconnect' : 'Connect'}
                </button>
                <a href="camera-video.html?id=${drone.id}" class="btn btn-info btn-sm">Camera</a>
            </td>
        </tr>
    `).join('');
}

function loadDroneDetails(droneId) {
    const drone = drones.find(d => d.id === droneId);
    if (!drone) return;
    
    // Update drone info
    updateElement('drone-name', drone.name);
    updateElement('drone-status', drone.status.toUpperCase());
    updateElement('drone-battery', `${drone.battery}%`);
    updateElement('drone-altitude', `${drone.altitude}m`);
    updateElement('drone-temperature', `${drone.temperature}°C`);
    
    // Update battery progress bar
    updateProgressBar('battery-level', drone.battery);
    
    // Set up control buttons
    setupDroneControls(droneId);
}

function setupDroneControls(droneId) {
    const controlButtons = {
        'takeoff': () => controlDrone(droneId, 'takeoff'),
        'land': () => controlDrone(droneId, 'land'),
        'emergency': () => controlDrone(droneId, 'emergency'),
        'up': () => controlDrone(droneId, 'up'),
        'down': () => controlDrone(droneId, 'down'),
        'left': () => controlDrone(droneId, 'left'),
        'right': () => controlDrone(droneId, 'right'),
        'forward': () => controlDrone(droneId, 'forward'),
        'backward': () => controlDrone(droneId, 'backward'),
        'rotate-left': () => controlDrone(droneId, 'rotate-left'),
        'rotate-right': () => controlDrone(droneId, 'rotate-right')
    };
    
    Object.keys(controlButtons).forEach(buttonId => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', controlButtons[buttonId]);
        }
    });
}

function controlDrone(droneId, command) {
    const drone = drones.find(d => d.id === droneId);
    if (!drone) return;
    
    console.log(`Executing ${command} on drone ${droneId}`);
    
    // Simulate command execution
    switch(command) {
        case 'takeoff':
            if (drone.altitude === 0) {
                drone.altitude = 1.2;
                showNotification('Drone taking off...', 'info');
            }
            break;
        case 'land':
            if (drone.altitude > 0) {
                drone.altitude = 0;
                showNotification('Drone landing...', 'info');
            }
            break;
        case 'emergency':
            drone.altitude = 0;
            showNotification('Emergency stop executed!', 'warning');
            break;
        case 'connect':
            drone.status = drone.status === 'online' ? 'offline' : 'online';
            break;
        default:
            showNotification(`Command ${command} executed`, 'success');
    }
    
    // Refresh display
    if (getCurrentPage() === 'drone-detail') {
        loadDroneDetails(droneId);
    } else if (getCurrentPage() === 'drone-management') {
        populateDroneList();
    }
}

// ============ Camera/Video Functions ============
function startVideoSimulation() {
    const videoContainer = document.querySelector('.video-placeholder');
    if (!videoContainer) return;
    
    // Simulate live video feed
    let frameCount = 0;
    setInterval(() => {
        frameCount++;
        videoContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="font-size: 24px; margin-bottom: 10px;">📹 LIVE FEED</div>
                <div style="font-size: 14px; opacity: 0.7;">Frame ${frameCount}</div>
                <div style="font-size: 12px; opacity: 0.5; margin-top: 10px;">
                    Resolution: 1280x720 | FPS: 30 | Bitrate: 2.5 Mbps
                </div>
            </div>
        `;
    }, 1000/30); // 30 FPS simulation
}

// ============ Dataset Functions ============
function populateDatasetList() {
    const datasetList = document.querySelector('#dataset-list');
    if (!datasetList) return;
    
    datasetList.innerHTML = datasets.map(dataset => `
        <tr>
            <td>
                <a href="dataset-detail.html?id=${dataset.id}" class="dataset-link">
                    ${dataset.name}
                </a>
            </td>
            <td>${dataset.description}</td>
            <td>${dataset.imageCount}</td>
            <td>${dataset.labels.join(', ')}</td>
            <td><span class="status status-${dataset.status}">${dataset.status.toUpperCase()}</span></td>
            <td>
                <a href="dataset-detail.html?id=${dataset.id}" class="btn btn-primary btn-sm">Edit</a>
                <button class="btn btn-danger btn-sm" onclick="deleteDataset('${dataset.id}')">Delete</button>
            </td>
        </tr>
    `).join('');
}

// ============ Model Functions ============
function populateModelList() {
    const modelList = document.querySelector('#model-list');
    if (!modelList) return;
    
    modelList.innerHTML = models.map(model => `
        <tr>
            <td>${model.name}</td>
            <td>${model.dataset}</td>
            <td>${model.accuracy > 0 ? model.accuracy + '%' : 'Training...'}</td>
            <td>${model.trainingTime}</td>
            <td><span class="status status-${model.status}">${model.status.toUpperCase()}</span></td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="useModel('${model.id}')">Use</button>
                <button class="btn btn-info btn-sm" onclick="viewModel('${model.id}')">Details</button>
                <button class="btn btn-danger btn-sm" onclick="deleteModel('${model.id}')">Delete</button>
            </td>
        </tr>
    `).join('');
}

// ============ Tracking Functions ============
function setupTrackingControls() {
    const startBtn = document.getElementById('start-tracking');
    const stopBtn = document.getElementById('stop-tracking');
    
    if (startBtn) {
        startBtn.addEventListener('click', startTracking);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopTracking);
    }
}

function loadAvailableModels() {
    const modelSelect = document.getElementById('tracking-model');
    if (!modelSelect) return;
    
    const trainedModels = models.filter(m => m.status === 'trained');
    modelSelect.innerHTML = trainedModels.map(model => 
        `<option value="${model.id}">${model.name} (${model.accuracy}%)</option>`
    ).join('');
}

function startTracking() {
    trackingStatus.active = true;
    trackingStatus.target = 'person';
    showNotification('Tracking started', 'success');
    updateTrackingStatus();
}

function stopTracking() {
    trackingStatus.active = false;
    trackingStatus.target = null;
    showNotification('Tracking stopped', 'info');
    updateTrackingStatus();
}

function updateTrackingStatus() {
    const statusElement = document.getElementById('tracking-status');
    if (statusElement) {
        statusElement.innerHTML = trackingStatus.active ? 
            `<span class="status status-success">ACTIVE</span> - Tracking ${trackingStatus.target}` :
            `<span class="status status-offline">STOPPED</span>`;
    }
}

function startTrackingSimulation() {
    if (trackingStatus.active) {
        setInterval(() => {
            // Simulate tracking data
            const confidence = 0.7 + Math.random() * 0.3;
            const position = {
                x: Math.floor(Math.random() * 800),
                y: Math.floor(Math.random() * 600)
            };
            
            updateElement('detection-confidence', `${(confidence * 100).toFixed(1)}%`);
            updateElement('target-position', `X: ${position.x}, Y: ${position.y}`);
        }, 1000);
    }
}

// ============ System Monitoring ============
function updateSystemMetrics() {
    updateProgressBar('cpu-usage-detail', systemStatus.cpu);
    updateProgressBar('memory-usage-detail', systemStatus.memory);
    updateProgressBar('disk-usage-detail', systemStatus.disk);
}

function startSystemMonitoring() {
    setInterval(() => {
        updateSystemStatus();
        updateSystemMetrics();
    }, 2000);
}

// ============ Login Functions ============
function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
}

function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Simple demo authentication
    if (username && password) {
        showNotification('Login successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
    } else {
        showNotification('Please enter both username and password', 'danger');
    }
}

// ============ Utility Functions ============
function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
}

function updateProgressBar(id, percentage) {
    const progressBar = document.querySelector(`#${id} .progress-bar`);
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
    }
    
    const percentageText = document.querySelector(`#${id} .percentage`);
    if (percentageText) {
        percentageText.textContent = `${percentage}%`;
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
    }
    
    .notification-info { background: var(--info-color); }
    .notification-success { background: var(--success-color); }
    .notification-warning { background: var(--warning-color); color: black; }
    .notification-danger { background: var(--danger-color); }
    
    .notification button {
        background: none;
        border: none;
        color: inherit;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        margin-left: auto;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// ============ Export for global use ============
window.MFGDroneApp = {
    controlDrone,
    startTracking,
    stopTracking,
    showNotification,
    drones,
    datasets,
    models,
    trackingStatus
};