// MFG Drone Admin Frontend - Phase 5 完全版 JavaScript
// 高度制御機能・ミッションパッド対応・システム設定

class DroneAdminApp {
  constructor() {
    this.apiBaseUrl = 'http://localhost:8000';
    this.currentPage = 'dashboard';
    this.connectionStatus = 'disconnected';
    this.sensors = {
      battery: 0,
      altitude: 0,
      temperature: 0,
      pitch: 0,
      roll: 0,
      yaw: 0
    };
    this.missionPads = {
      detected: [],
      active: null,
      enabled: false
    };
    this.trackingStatus = {
      active: false,
      target: null,
      mode: 'center'
    };
    
    this.init();
  }

  // 初期化
  init() {
    this.setupNavigation();
    this.setupKeyboardControls();
    this.setupGamepadControls();
    this.startRealtimeUpdates();
    this.loadPage(this.currentPage);
    console.log('MFG Drone Admin App initialized');
  }

  // ナビゲーション設定
  setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = link.dataset.page;
        if (page) {
          this.loadPage(page);
        }
      });
    });
  }

  // キーボード制御設定
  setupKeyboardControls() {
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'w':
            e.preventDefault();
            this.moveForward();
            break;
          case 's':
            e.preventDefault();
            this.moveBackward();
            break;
          case 'a':
            e.preventDefault();
            this.moveLeft();
            break;
          case 'd':
            e.preventDefault();
            this.moveRight();
            break;
          case 'q':
            e.preventDefault();
            this.moveUp();
            break;
          case 'e':
            e.preventDefault();
            this.moveDown();
            break;
        }
      }
      
      // 緊急停止
      if (e.key === 'Escape') {
        e.preventDefault();
        this.emergencyStop();
      }
    });
  }

  // ゲームパッド制御設定
  setupGamepadControls() {
    // ゲームパッド接続検出
    window.addEventListener('gamepadconnected', (e) => {
      console.log('Gamepad connected:', e.gamepad);
      this.startGamepadPolling();
    });

    window.addEventListener('gamepaddisconnected', (e) => {
      console.log('Gamepad disconnected:', e.gamepad);
      this.stopGamepadPolling();
    });
  }

  // ゲームパッドポーリング開始
  startGamepadPolling() {
    if (this.gamepadInterval) return;
    
    this.gamepadInterval = setInterval(() => {
      const gamepads = navigator.getGamepads();
      const gamepad = gamepads[0];
      
      if (gamepad) {
        this.handleGamepadInput(gamepad);
      }
    }, 50); // 20Hz更新
  }

  // ゲームパッドポーリング停止
  stopGamepadPolling() {
    if (this.gamepadInterval) {
      clearInterval(this.gamepadInterval);
      this.gamepadInterval = null;
    }
  }

  // ゲームパッド入力処理
  handleGamepadInput(gamepad) {
    const leftStickX = gamepad.axes[0];
    const leftStickY = gamepad.axes[1];
    const rightStickX = gamepad.axes[2];
    const rightStickY = gamepad.axes[3];

    // デッドゾーン適用
    const deadzone = 0.1;
    const processAxis = (value) => Math.abs(value) > deadzone ? value : 0;

    const commands = {
      left_right_velocity: Math.round(processAxis(leftStickX) * 100),
      forward_backward_velocity: Math.round(-processAxis(leftStickY) * 100),
      up_down_velocity: Math.round(-processAxis(rightStickY) * 100),
      yaw_velocity: Math.round(processAxis(rightStickX) * 100)
    };

    // リアルタイム制御コマンド送信
    if (Object.values(commands).some(v => v !== 0)) {
      this.sendRCControl(commands);
    }
  }

  // ページ読み込み
  loadPage(pageName) {
    // 全ページを非表示
    const pages = document.querySelectorAll('.page-section');
    pages.forEach(page => page.classList.remove('active'));

    // アクティブナビゲーション更新
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.dataset.page === pageName) {
        link.classList.add('active');
      }
    });

    // 指定ページを表示
    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
      targetPage.classList.add('active');
      this.currentPage = pageName;
      
      // ページ固有の初期化
      this.initializePage(pageName);
    }
  }

  // ページ固有初期化
  initializePage(pageName) {
    switch (pageName) {
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
      case 'advanced':
        this.initAdvancedControl();
        break;
      case 'camera':
        this.initCameraControl();
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
      case 'mission':
        this.initMissionPad();
        break;
      case 'settings':
        this.initSettings();
        break;
    }
  }

  // リアルタイム更新開始
  startRealtimeUpdates() {
    this.updateInterval = setInterval(() => {
      this.updateSensorData();
      this.updateConnectionStatus();
      this.updateMissionPadStatus();
      this.updateTrackingStatus();
    }, 2000);
  }

  // API呼び出し汎用メソッド
  async apiCall(endpoint, method = 'GET', data = null) {
    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
      }

      const response = await fetch(`${this.apiBaseUrl}${endpoint}`, options);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'API Error');
      }

      return result;
    } catch (error) {
      console.error('API Error:', error);
      this.showAlert('error', `API Error: ${error.message}`);
      return null;
    }
  }

  // アラート表示
  showAlert(type, message) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    alertContainer.appendChild(alert);

    setTimeout(() => {
      if (alert.parentNode) {
        alert.parentNode.removeChild(alert);
      }
    }, 5000);
  }

  // ローディング状態表示
  showLoading(element) {
    if (element) {
      element.innerHTML = '<div class="loading-spinner"></div>';
    }
  }

  // ========================================
  // ダッシュボード機能
  // ========================================
  
  initDashboard() {
    this.updateDashboardMetrics();
    this.setupQuickActions();
  }

  updateDashboardMetrics() {
    // メトリクス更新
    document.getElementById('battery-level').textContent = `${this.sensors.battery}%`;
    document.getElementById('altitude-value').textContent = `${this.sensors.altitude}cm`;
    document.getElementById('temperature-value').textContent = `${this.sensors.temperature}°C`;
    document.getElementById('connection-status-text').textContent = this.connectionStatus;
  }

  setupQuickActions() {
    // クイックアクション設定
    document.getElementById('quick-connect')?.addEventListener('click', () => this.connectDrone());
    document.getElementById('quick-takeoff')?.addEventListener('click', () => this.takeoff());
    document.getElementById('quick-land')?.addEventListener('click', () => this.land());
    document.getElementById('emergency-stop')?.addEventListener('click', () => this.emergencyStop());
  }

  // ========================================
  // 接続管理機能
  // ========================================
  
  initConnection() {
    this.updateConnectionInfo();
    document.getElementById('connect-btn')?.addEventListener('click', () => this.connectDrone());
    document.getElementById('disconnect-btn')?.addEventListener('click', () => this.disconnectDrone());
  }

  async connectDrone() {
    this.connectionStatus = 'connecting';
    this.updateConnectionStatus();
    
    const result = await this.apiCall('/drone/connect', 'POST');
    if (result) {
      this.connectionStatus = 'connected';
      this.showAlert('success', 'ドローンに接続しました');
    } else {
      this.connectionStatus = 'disconnected';
      this.showAlert('error', 'ドローンの接続に失敗しました');
    }
    this.updateConnectionStatus();
  }

  async disconnectDrone() {
    const result = await this.apiCall('/drone/disconnect', 'POST');
    if (result) {
      this.connectionStatus = 'disconnected';
      this.showAlert('success', 'ドローンから切断しました');
    }
    this.updateConnectionStatus();
  }

  updateConnectionInfo() {
    const statusElement = document.getElementById('connection-status');
    const statusIndicator = document.querySelector('.connection-status .status-indicator');
    
    if (statusElement) {
      statusElement.textContent = this.connectionStatus;
    }
    
    if (statusIndicator) {
      statusIndicator.className = `status-indicator ${this.connectionStatus}`;
    }
  }

  // ========================================
  // 飛行制御機能
  // ========================================
  
  initFlightControl() {
    document.getElementById('takeoff-btn')?.addEventListener('click', () => this.takeoff());
    document.getElementById('land-btn')?.addEventListener('click', () => this.land());
    document.getElementById('emergency-btn')?.addEventListener('click', () => this.emergencyStop());
  }

  async takeoff() {
    const result = await this.apiCall('/drone/takeoff', 'POST');
    if (result) {
      this.showAlert('success', '離陸しました');
    }
  }

  async land() {
    const result = await this.apiCall('/drone/land', 'POST');
    if (result) {
      this.showAlert('success', '着陸しました');
    }
  }

  async emergencyStop() {
    const result = await this.apiCall('/drone/emergency', 'POST');
    if (result) {
      this.showAlert('warning', '緊急停止しました');
    }
  }

  // ========================================
  // 移動制御機能
  // ========================================
  
  initMovementControl() {
    this.setupDirectionalButtons();
    this.setupDistanceControl();
  }

  setupDirectionalButtons() {
    document.getElementById('move-forward')?.addEventListener('click', () => this.moveForward());
    document.getElementById('move-backward')?.addEventListener('click', () => this.moveBackward());
    document.getElementById('move-left')?.addEventListener('click', () => this.moveLeft());
    document.getElementById('move-right')?.addEventListener('click', () => this.moveRight());
    document.getElementById('move-up')?.addEventListener('click', () => this.moveUp());
    document.getElementById('move-down')?.addEventListener('click', () => this.moveDown());
    document.getElementById('rotate-cw')?.addEventListener('click', () => this.rotateCW());
    document.getElementById('rotate-ccw')?.addEventListener('click', () => this.rotateCCW());
  }

  setupDistanceControl() {
    const distanceSlider = document.getElementById('movement-distance');
    if (distanceSlider) {
      distanceSlider.addEventListener('input', (e) => {
        document.getElementById('distance-value').textContent = e.target.value;
      });
    }
  }

  getMovementDistance() {
    const slider = document.getElementById('movement-distance');
    return slider ? parseInt(slider.value) : 30;
  }

  async moveForward() {
    const distance = this.getMovementDistance();
    await this.apiCall('/drone/move/forward', 'POST', { distance });
  }

  async moveBackward() {
    const distance = this.getMovementDistance();
    await this.apiCall('/drone/move/back', 'POST', { distance });
  }

  async moveLeft() {
    const distance = this.getMovementDistance();
    await this.apiCall('/drone/move/left', 'POST', { distance });
  }

  async moveRight() {
    const distance = this.getMovementDistance();
    await this.apiCall('/drone/move/right', 'POST', { distance });
  }

  async moveUp() {
    const distance = this.getMovementDistance();
    await this.apiCall('/drone/move/up', 'POST', { distance });
  }

  async moveDown() {
    const distance = this.getMovementDistance();
    await this.apiCall('/drone/move/down', 'POST', { distance });
  }

  async rotateCW() {
    const angle = 90;
    await this.apiCall('/drone/rotate', 'POST', { direction: 'clockwise', angle });
  }

  async rotateCCW() {
    const angle = 90;
    await this.apiCall('/drone/rotate', 'POST', { direction: 'counter_clockwise', angle });
  }

  // ========================================
  // 高度制御機能（Phase 5）
  // ========================================
  
  initAdvancedControl() {
    this.setup3DCoordinateControl();
    this.setupCurveFlightControl();
    this.setupRCControl();
    this.initFlightPathVisualization();
  }

  setup3DCoordinateControl() {
    document.getElementById('goto-xyz-btn')?.addEventListener('click', () => {
      const x = parseInt(document.getElementById('coord-x').value) || 0;
      const y = parseInt(document.getElementById('coord-y').value) || 0;
      const z = parseInt(document.getElementById('coord-z').value) || 0;
      const speed = parseInt(document.getElementById('coord-speed').value) || 50;
      
      this.goToXYZ(x, y, z, speed);
    });
  }

  setupCurveFlightControl() {
    document.getElementById('curve-flight-btn')?.addEventListener('click', () => {
      const x1 = parseInt(document.getElementById('curve-x1').value) || 0;
      const y1 = parseInt(document.getElementById('curve-y1').value) || 0;
      const z1 = parseInt(document.getElementById('curve-z1').value) || 0;
      const x2 = parseInt(document.getElementById('curve-x2').value) || 0;
      const y2 = parseInt(document.getElementById('curve-y2').value) || 0;
      const z2 = parseInt(document.getElementById('curve-z2').value) || 0;
      const speed = parseInt(document.getElementById('curve-speed').value) || 30;
      
      this.curveFlightXYZ(x1, y1, z1, x2, y2, z2, speed);
    });
  }

  setupRCControl() {
    // バーチャルスティック設定
    this.setupVirtualStick('left-stick', (x, y) => {
      this.sendRCControl({
        left_right_velocity: Math.round(x * 100),
        forward_backward_velocity: Math.round(-y * 100),
        up_down_velocity: 0,
        yaw_velocity: 0
      });
    });

    this.setupVirtualStick('right-stick', (x, y) => {
      this.sendRCControl({
        left_right_velocity: 0,
        forward_backward_velocity: 0,
        up_down_velocity: Math.round(-y * 100),
        yaw_velocity: Math.round(x * 100)
      });
    });
  }

  setupVirtualStick(stickId, callback) {
    const stick = document.getElementById(stickId);
    if (!stick) return;

    let isDragging = false;
    const container = stick.parentElement;
    const containerRect = container.getBoundingClientRect();
    const centerX = containerRect.width / 2;
    const centerY = containerRect.height / 2;
    const maxRadius = containerRect.width / 2 - 20;

    stick.addEventListener('mousedown', (e) => {
      isDragging = true;
      e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;

      const containerRect = container.getBoundingClientRect();
      const deltaX = e.clientX - containerRect.left - centerX;
      const deltaY = e.clientY - containerRect.top - centerY;
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

      let x = deltaX;
      let y = deltaY;

      if (distance > maxRadius) {
        const angle = Math.atan2(deltaY, deltaX);
        x = Math.cos(angle) * maxRadius;
        y = Math.sin(angle) * maxRadius;
      }

      stick.style.transform = `translate(${x}px, ${y}px)`;
      
      // 正規化された値を渡す (-1 to 1)
      callback(x / maxRadius, y / maxRadius);
    });

    document.addEventListener('mouseup', () => {
      isDragging = false;
      stick.style.transform = 'translate(0, 0)';
      callback(0, 0); // ニュートラル位置
    });
  }

  async goToXYZ(x, y, z, speed) {
    const result = await this.apiCall('/drone/go_xyz', 'POST', { x, y, z, speed });
    if (result) {
      this.showAlert('success', `座標 (${x}, ${y}, ${z}) に移動中`);
      this.addFlightPathPoint(x, y, z);
    }
  }

  async curveFlightXYZ(x1, y1, z1, x2, y2, z2, speed) {
    const result = await this.apiCall('/drone/curve_xyz', 'POST', {
      x1, y1, z1, x2, y2, z2, speed
    });
    if (result) {
      this.showAlert('success', '曲線飛行を開始しました');
      this.addCurvePathPoints(x1, y1, z1, x2, y2, z2);
    }
  }

  async sendRCControl(velocities) {
    await this.apiCall('/drone/rc_control', 'POST', velocities);
  }

  // 飛行軌跡可視化
  initFlightPathVisualization() {
    const canvas = document.getElementById('flight-path-canvas');
    if (!canvas) return;

    this.flightPathCtx = canvas.getContext('2d');
    this.flightPath = [];
    this.drawFlightPath();
  }

  addFlightPathPoint(x, y, z) {
    this.flightPath.push({ x, y, z, timestamp: Date.now() });
    this.drawFlightPath();
  }

  addCurvePathPoints(x1, y1, z1, x2, y2, z2) {
    // 曲線を近似的に複数ポイントで表現
    for (let t = 0; t <= 1; t += 0.1) {
      const x = x1 * (1 - t) + x2 * t;
      const y = y1 * (1 - t) + y2 * t;
      const z = z1 * (1 - t) + z2 * t;
      this.addFlightPathPoint(x, y, z);
    }
  }

  drawFlightPath() {
    if (!this.flightPathCtx) return;

    const canvas = this.flightPathCtx.canvas;
    this.flightPathCtx.clearRect(0, 0, canvas.width, canvas.height);

    if (this.flightPath.length < 2) return;

    // スケール調整
    const maxCoord = 500;
    const scaleX = canvas.width / (maxCoord * 2);
    const scaleY = canvas.height / (maxCoord * 2);
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    this.flightPathCtx.strokeStyle = '#2563eb';
    this.flightPathCtx.lineWidth = 2;
    this.flightPathCtx.beginPath();

    this.flightPath.forEach((point, index) => {
      const x = centerX + point.x * scaleX;
      const y = centerY + point.y * scaleY;

      if (index === 0) {
        this.flightPathCtx.moveTo(x, y);
      } else {
        this.flightPathCtx.lineTo(x, y);
      }
    });

    this.flightPathCtx.stroke();

    // 現在位置をマーク
    if (this.flightPath.length > 0) {
      const lastPoint = this.flightPath[this.flightPath.length - 1];
      const x = centerX + lastPoint.x * scaleX;
      const y = centerY + lastPoint.y * scaleY;

      this.flightPathCtx.fillStyle = '#ef4444';
      this.flightPathCtx.beginPath();
      this.flightPathCtx.arc(x, y, 4, 0, 2 * Math.PI);
      this.flightPathCtx.fill();
    }
  }

  // ========================================
  // ミッションパッド機能（Phase 5）
  // ========================================
  
  initMissionPad() {
    this.setupMissionPadControls();
    this.updateMissionPadDisplay();
  }

  setupMissionPadControls() {
    document.getElementById('enable-mission-pad')?.addEventListener('click', () => this.enableMissionPad());
    document.getElementById('disable-mission-pad')?.addEventListener('click', () => this.disableMissionPad());
    
    // 検出方向設定
    document.getElementById('detection-direction')?.addEventListener('change', (e) => {
      this.setDetectionDirection(parseInt(e.target.value));
    });

    // パッド移動設定
    document.getElementById('mission-go-btn')?.addEventListener('click', () => {
      const x = parseInt(document.getElementById('mission-x').value) || 0;
      const y = parseInt(document.getElementById('mission-y').value) || 0;
      const z = parseInt(document.getElementById('mission-z').value) || 0;
      const speed = parseInt(document.getElementById('mission-speed').value) || 50;
      const padId = parseInt(document.getElementById('mission-pad-id').value) || 1;
      
      this.goToMissionPad(x, y, z, speed, padId);
    });
  }

  async enableMissionPad() {
    const result = await this.apiCall('/mission_pad/enable', 'POST');
    if (result) {
      this.missionPads.enabled = true;
      this.showAlert('success', 'ミッションパッド検出を有効にしました');
    }
  }

  async disableMissionPad() {
    const result = await this.apiCall('/mission_pad/disable', 'POST');
    if (result) {
      this.missionPads.enabled = false;
      this.showAlert('success', 'ミッションパッド検出を無効にしました');
    }
  }

  async setDetectionDirection(direction) {
    const result = await this.apiCall('/mission_pad/detection_direction', 'PUT', { direction });
    if (result) {
      const directions = ['下向き', '前向き', '両方'];
      this.showAlert('success', `検出方向を${directions[direction]}に設定しました`);
    }
  }

  async goToMissionPad(x, y, z, speed, missionPadId) {
    const result = await this.apiCall('/mission_pad/go_xyz', 'POST', {
      x, y, z, speed, mission_pad_id: missionPadId
    });
    if (result) {
      this.showAlert('success', `ミッションパッド${missionPadId}基準で移動中`);
    }
  }

  async updateMissionPadStatus() {
    const status = await this.apiCall('/mission_pad/status');
    if (status) {
      this.missionPads.detected = status.mission_pad_id !== -1 ? [status.mission_pad_id] : [];
      this.missionPads.active = status.mission_pad_id !== -1 ? status.mission_pad_id : null;
      this.updateMissionPadDisplay();
    }
  }

  updateMissionPadDisplay() {
    for (let i = 1; i <= 8; i++) {
      const padElement = document.getElementById(`mission-pad-${i}`);
      if (padElement) {
        padElement.className = 'mission-pad';
        if (this.missionPads.detected.includes(i)) {
          padElement.classList.add('detected');
        }
        if (this.missionPads.active === i) {
          padElement.classList.add('active');
        }
      }
    }
  }

  // ========================================
  // カメラ制御機能
  // ========================================
  
  initCameraControl() {
    this.setupCameraControls();
    this.updateVideoStream();
  }

  setupCameraControls() {
    document.getElementById('start-stream')?.addEventListener('click', () => this.startVideoStream());
    document.getElementById('stop-stream')?.addEventListener('click', () => this.stopVideoStream());
    document.getElementById('take-photo')?.addEventListener('click', () => this.takePhoto());
    document.getElementById('start-recording')?.addEventListener('click', () => this.startRecording());
    document.getElementById('stop-recording')?.addEventListener('click', () => this.stopRecording());
  }

  async startVideoStream() {
    const result = await this.apiCall('/camera/stream/start', 'POST');
    if (result) {
      this.showAlert('success', 'ビデオストリーミングを開始しました');
      this.updateVideoStream();
    }
  }

  async stopVideoStream() {
    const result = await this.apiCall('/camera/stream/stop', 'POST');
    if (result) {
      this.showAlert('success', 'ビデオストリーミングを停止しました');
    }
  }

  async takePhoto() {
    const result = await this.apiCall('/camera/photo', 'POST');
    if (result) {
      this.showAlert('success', '写真を撮影しました');
    }
  }

  async startRecording() {
    const result = await this.apiCall('/camera/recording/start', 'POST');
    if (result) {
      this.showAlert('success', '録画を開始しました');
    }
  }

  async stopRecording() {
    const result = await this.apiCall('/camera/recording/stop', 'POST');
    if (result) {
      this.showAlert('success', '録画を停止しました');
    }
  }

  updateVideoStream() {
    const videoElement = document.getElementById('live-video');
    if (videoElement) {
      videoElement.src = `${this.apiBaseUrl}/camera/stream`;
    }
  }

  // ========================================
  // センサー監視機能
  // ========================================
  
  initSensors() {
    this.updateSensorDisplay();
  }

  async updateSensorData() {
    try {
      const [battery, altitude, temperature, attitude, velocity] = await Promise.all([
        this.apiCall('/drone/battery'),
        this.apiCall('/drone/altitude'),
        this.apiCall('/drone/temperature'),
        this.apiCall('/drone/attitude'),
        this.apiCall('/drone/velocity')
      ]);

      if (battery) this.sensors.battery = battery.battery_percentage;
      if (altitude) this.sensors.altitude = altitude.altitude;
      if (temperature) this.sensors.temperature = temperature.temperature;
      if (attitude) {
        this.sensors.pitch = attitude.attitude.pitch;
        this.sensors.roll = attitude.attitude.roll;
        this.sensors.yaw = attitude.attitude.yaw;
      }

      this.updateSensorDisplay();
    } catch (error) {
      // センサー更新エラーは silent
    }
  }

  updateSensorDisplay() {
    // バッテリー
    const batteryValue = document.getElementById('battery-value');
    const batteryProgress = document.getElementById('battery-progress');
    if (batteryValue) batteryValue.textContent = `${this.sensors.battery}%`;
    if (batteryProgress) {
      batteryProgress.style.width = `${this.sensors.battery}%`;
      batteryProgress.className = `progress-bar ${this.sensors.battery < 20 ? 'danger' : this.sensors.battery < 50 ? 'warning' : 'success'}`;
    }

    // 高度
    const altitudeValue = document.getElementById('altitude-display');
    if (altitudeValue) altitudeValue.textContent = `${this.sensors.altitude}cm`;

    // 温度
    const temperatureValue = document.getElementById('temperature-display');
    if (temperatureValue) temperatureValue.textContent = `${this.sensors.temperature}°C`;

    // 姿勢角
    const pitchValue = document.getElementById('pitch-value');
    const rollValue = document.getElementById('roll-value');
    const yawValue = document.getElementById('yaw-value');
    if (pitchValue) pitchValue.textContent = `${this.sensors.pitch}°`;
    if (rollValue) rollValue.textContent = `${this.sensors.roll}°`;
    if (yawValue) yawValue.textContent = `${this.sensors.yaw}°`;
  }

  // ========================================
  // 物体追跡機能
  // ========================================
  
  initTracking() {
    this.setupTrackingControls();
  }

  setupTrackingControls() {
    document.getElementById('start-tracking')?.addEventListener('click', () => {
      const target = document.getElementById('target-object').value;
      const mode = document.getElementById('tracking-mode').value;
      this.startTracking(target, mode);
    });

    document.getElementById('stop-tracking')?.addEventListener('click', () => this.stopTracking());
  }

  async startTracking(targetObject, trackingMode = 'center') {
    const result = await this.apiCall('/tracking/start', 'POST', {
      target_object: targetObject,
      tracking_mode: trackingMode
    });
    if (result) {
      this.trackingStatus.active = true;
      this.trackingStatus.target = targetObject;
      this.trackingStatus.mode = trackingMode;
      this.showAlert('success', `${targetObject}の追跡を開始しました`);
    }
  }

  async stopTracking() {
    const result = await this.apiCall('/tracking/stop', 'POST');
    if (result) {
      this.trackingStatus.active = false;
      this.trackingStatus.target = null;
      this.showAlert('success', '追跡を停止しました');
    }
  }

  async updateTrackingStatus() {
    const status = await this.apiCall('/tracking/status');
    if (status) {
      this.trackingStatus = { ...this.trackingStatus, ...status };
      this.updateTrackingDisplay();
    }
  }

  updateTrackingDisplay() {
    const statusElement = document.getElementById('tracking-status');
    if (statusElement) {
      statusElement.textContent = this.trackingStatus.active ? 'アクティブ' : '停止中';
      statusElement.className = `badge ${this.trackingStatus.active ? 'badge-success' : 'badge-secondary'}`;
    }
  }

  // ========================================
  // モデル管理機能
  // ========================================
  
  initModels() {
    this.setupModelUpload();
    this.loadModelList();
  }

  setupModelUpload() {
    const uploadForm = document.getElementById('model-upload-form');
    if (uploadForm) {
      uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.uploadModel();
      });
    }

    // ドラッグ&ドロップ
    const dropZone = document.getElementById('upload-drop-zone');
    if (dropZone) {
      dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
      });

      dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
      });

      dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
          this.handleFileUpload(files[0]);
        }
      });
    }
  }

  async uploadModel() {
    const fileInput = document.getElementById('model-file');
    const objectName = document.getElementById('object-name').value;
    
    if (!fileInput.files[0] || !objectName) {
      this.showAlert('error', 'ファイルとオブジェクト名を指定してください');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('object_name', objectName);

    try {
      const response = await fetch(`${this.apiBaseUrl}/model/train`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        this.showAlert('success', 'モデルの訓練を開始しました');
        this.loadModelList();
      } else {
        this.showAlert('error', 'モデルの訓練に失敗しました');
      }
    } catch (error) {
      this.showAlert('error', `アップロードエラー: ${error.message}`);
    }
  }

  handleFileUpload(file) {
    const fileInput = document.getElementById('model-file');
    if (fileInput) {
      fileInput.files = file;
    }
  }

  async loadModelList() {
    const models = await this.apiCall('/model/list');
    if (models) {
      this.displayModelList(models);
    }
  }

  displayModelList(models) {
    const container = document.getElementById('model-list');
    if (!container) return;

    container.innerHTML = '';
    
    models.forEach(model => {
      const modelCard = document.createElement('div');
      modelCard.className = 'card';
      modelCard.innerHTML = `
        <div class="card-body">
          <h3 class="card-title">${model.name}</h3>
          <p class="text-sm text-secondary">作成日: ${new Date(model.created_at).toLocaleDateString()}</p>
          <p class="text-sm">精度: ${model.accuracy}%</p>
          <div class="mt-4">
            <button class="btn btn-primary btn-sm" onclick="app.selectModel('${model.name}')">選択</button>
            <button class="btn btn-danger btn-sm ml-2" onclick="app.deleteModel('${model.name}')">削除</button>
          </div>
        </div>
      `;
      container.appendChild(modelCard);
    });
  }

  async selectModel(modelName) {
    // モデル選択ロジック
    this.showAlert('success', `モデル「${modelName}」を選択しました`);
  }

  async deleteModel(modelName) {
    if (confirm(`モデル「${modelName}」を削除しますか？`)) {
      const result = await this.apiCall(`/model/${modelName}`, 'DELETE');
      if (result) {
        this.showAlert('success', 'モデルを削除しました');
        this.loadModelList();
      }
    }
  }

  // ========================================
  // システム設定機能（Phase 5）
  // ========================================
  
  initSettings() {
    this.setupSettingsControls();
    this.loadCurrentSettings();
  }

  setupSettingsControls() {
    // WiFi設定
    document.getElementById('wifi-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const ssid = document.getElementById('wifi-ssid').value;
      const password = document.getElementById('wifi-password').value;
      this.setWiFiSettings(ssid, password);
    });

    // 飛行速度設定
    document.getElementById('speed-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const speed = parseFloat(document.getElementById('flight-speed').value);
      this.setFlightSpeed(speed);
    });

    // カスタムコマンド
    document.getElementById('command-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const command = document.getElementById('custom-command').value;
      const timeout = parseInt(document.getElementById('command-timeout').value) || 7;
      this.sendCustomCommand(command, timeout);
    });
  }

  async setWiFiSettings(ssid, password) {
    const result = await this.apiCall('/drone/wifi', 'PUT', { ssid, password });
    if (result) {
      this.showAlert('success', 'WiFi設定を更新しました');
    }
  }

  async setFlightSpeed(speed) {
    const result = await this.apiCall('/drone/speed', 'PUT', { speed });
    if (result) {
      this.showAlert('success', `飛行速度を${speed}m/sに設定しました`);
    }
  }

  async sendCustomCommand(command, timeout) {
    const result = await this.apiCall('/drone/command', 'POST', { 
      command, 
      timeout,
      expect_response: true 
    });
    if (result) {
      this.showAlert('success', `コマンド実行: ${result.response}`);
    }
  }

  loadCurrentSettings() {
    // 現在の設定値を読み込み（必要に応じて実装）
  }

  // ========================================
  // 接続状態更新
  // ========================================
  
  async updateConnectionStatus() {
    try {
      const health = await this.apiCall('/health');
      if (health && health.status === 'healthy') {
        // バックエンドは生きているが、ドローン接続状態は別途確認
      }
    } catch (error) {
      // バックエンド接続エラー
    }

    this.updateConnectionInfo();
  }
}

// アプリケーション初期化
let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new DroneAdminApp();
});

// グローバル関数エクスポート（テンプレートから呼び出すため）
window.app = app;