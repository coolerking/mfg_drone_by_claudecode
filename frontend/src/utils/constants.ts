// Application constants

// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const

// WebSocket Events
export const WS_EVENTS = {
  // Connection events
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  RECONNECT: 'reconnect',
  ERROR: 'error',
  
  // Drone events
  DRONE_STATUS: 'drone_status',
  DRONE_COMMAND: 'drone_command',
  DRONE_TELEMETRY: 'drone_telemetry',
  
  // Camera events
  CAMERA_FRAME: 'camera_frame',
  CAMERA_STREAM_START: 'camera_stream_start',
  CAMERA_STREAM_STOP: 'camera_stream_stop',
  
  // Tracking events
  TRACKING_STATUS: 'tracking_status',
  TRACKING_START: 'tracking_start',
  TRACKING_STOP: 'tracking_stop',
  
  // System events
  SYSTEM_STATUS: 'system_status',
  ALERT: 'alert',
  
  // Model events
  MODEL_TRAINING_PROGRESS: 'model_training_progress',
  MODEL_INFERENCE_RESULT: 'model_inference_result',
} as const

// Drone Configuration
export const DRONE_CONFIG = {
  MAX_HEIGHT: 120, // meters
  MAX_DISTANCE: 500, // meters
  MIN_BATTERY_LEVEL: 15, // percentage
  CRITICAL_BATTERY_LEVEL: 10, // percentage
  MAX_SPEED: 100, // percentage
  MIN_SPEED: 10, // percentage
  COMMAND_TIMEOUT: 5000, // milliseconds
  TELEMETRY_INTERVAL: 1000, // milliseconds
} as const

export const DRONE_COMMANDS = {
  TAKEOFF: 'takeoff',
  LAND: 'land',
  EMERGENCY: 'emergency',
  MOVE: 'move',
  ROTATE: 'rotate',
  SET_SPEED: 'set_speed',
  FLIP: 'flip',
  CALIBRATE: 'calibrate',
} as const

export const MOVEMENT_DIRECTIONS = {
  UP: 'up',
  DOWN: 'down',
  LEFT: 'left',
  RIGHT: 'right',
  FORWARD: 'forward',
  BACK: 'back',
} as const

export const ROTATION_DIRECTIONS = {
  CLOCKWISE: 'clockwise',
  COUNTER_CLOCKWISE: 'counter_clockwise',
} as const

// Status Constants
export const DRONE_STATUSES = {
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  FLYING: 'flying',
  LANDED: 'landed',
  ERROR: 'error',
  BATTERY_LOW: 'battery_low',
  EMERGENCY: 'emergency',
  MAINTENANCE: 'maintenance',
} as const

export const TRAINING_STATUSES = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
  PAUSED: 'paused',
} as const

export const DATASET_STATUSES = {
  ACTIVE: 'active',
  PROCESSING: 'processing',
  ARCHIVED: 'archived',
} as const

// File Upload Configuration
export const FILE_UPLOAD = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  MAX_BATCH_SIZE: 100, // files
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  ALLOWED_MODEL_TYPES: ['application/octet-stream', '.pt', '.onnx'],
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks
} as const

// Model Configuration
export const MODEL_TYPES = {
  YOLO: 'yolo',
  CUSTOM: 'custom',
  PRETRAINED: 'pretrained',
} as const

export const YOLO_VARIANTS = {
  YOLOV8N: 'yolov8n',
  YOLOV8S: 'yolov8s',
  YOLOV8M: 'yolov8m',
  YOLOV8L: 'yolov8l',
  YOLOV8X: 'yolov8x',
} as const

export const TRAINING_CONFIG = {
  MIN_EPOCHS: 1,
  MAX_EPOCHS: 1000,
  DEFAULT_EPOCHS: 100,
  MIN_BATCH_SIZE: 1,
  MAX_BATCH_SIZE: 64,
  DEFAULT_BATCH_SIZE: 16,
  MIN_LEARNING_RATE: 0.0001,
  MAX_LEARNING_RATE: 1,
  DEFAULT_LEARNING_RATE: 0.01,
  MIN_IMAGE_SIZE: 320,
  MAX_IMAGE_SIZE: 1280,
  DEFAULT_IMAGE_SIZE: 640,
} as const

// UI Configuration
export const UI_CONFIG = {
  SIDEBAR_WIDTH: 280,
  SIDEBAR_COLLAPSED_WIDTH: 60,
  HEADER_HEIGHT: 64,
  FOOTER_HEIGHT: 40,
  CHART_HEIGHT: 300,
  CARD_MIN_HEIGHT: 200,
  GRID_SPACING: 2,
} as const

// Notification Configuration
export const NOTIFICATION_CONFIG = {
  DEFAULT_DURATION: 5000, // milliseconds
  SUCCESS_DURATION: 3000,
  ERROR_DURATION: 8000,
  WARNING_DURATION: 6000,
  MAX_NOTIFICATIONS: 5,
} as const

// Pagination Configuration
export const PAGINATION_CONFIG = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
  MAX_PAGE_SIZE: 500,
} as const

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKENS: 'mfg_drone_tokens',
  USER_PREFERENCES: 'mfg_drone_preferences',
  THEME: 'mfg_drone_theme',
  LANGUAGE: 'mfg_drone_language',
  SIDEBAR_STATE: 'mfg_drone_sidebar',
  DASHBOARD_LAYOUT: 'mfg_drone_dashboard_layout',
  RECENT_ITEMS: 'mfg_drone_recent',
} as const

// Theme Configuration
export const THEME_CONFIG = {
  MODES: {
    LIGHT: 'light',
    DARK: 'dark',
    AUTO: 'auto',
  },
  PRIMARY_COLORS: {
    BLUE: '#1976d2',
    GREEN: '#388e3c',
    RED: '#d32f2f',
    ORANGE: '#f57c00',
    PURPLE: '#7b1fa2',
  },
} as const

// Chart Configuration
export const CHART_CONFIG = {
  COLORS: [
    '#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2',
    '#0097a7', '#5d4037', '#616161', '#303f9f', '#689f38'
  ],
  ANIMATION_DURATION: 750,
  GRID_COLOR: '#e0e0e0',
  TEXT_COLOR: '#424242',
  BACKGROUND_COLOR: '#ffffff',
} as const

// Map Configuration
export const MAP_CONFIG = {
  DEFAULT_CENTER: {
    lat: 35.6762,
    lng: 139.6503, // Tokyo
  },
  DEFAULT_ZOOM: 15,
  MIN_ZOOM: 8,
  MAX_ZOOM: 20,
  MARKER_COLORS: {
    DRONE: '#1976d2',
    TARGET: '#f57c00',
    WAYPOINT: '#388e3c',
    HOME: '#d32f2f',
  },
} as const

// Validation Constants
export const VALIDATION = {
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 20,
    PATTERN: /^[a-zA-Z0-9_-]+$/,
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
  },
  DATASET_NAME: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 100,
    PATTERN: /^[a-zA-Z0-9_\-\s]+$/,
  },
  MODEL_NAME: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 100,
    PATTERN: /^[a-zA-Z0-9_\-\s]+$/,
  },
} as const

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'ネットワークエラーが発生しました',
  AUTHENTICATION_FAILED: '認証に失敗しました',
  UNAUTHORIZED: '権限がありません',
  NOT_FOUND: 'リソースが見つかりません',
  SERVER_ERROR: 'サーバーエラーが発生しました',
  VALIDATION_ERROR: '入力内容に誤りがあります',
  FILE_TOO_LARGE: 'ファイルサイズが大きすぎます',
  UNSUPPORTED_FILE_TYPE: 'サポートされていないファイル形式です',
  DRONE_NOT_CONNECTED: 'ドローンが接続されていません',
  BATTERY_TOO_LOW: 'バッテリー残量が不足しています',
  TRAINING_IN_PROGRESS: '学習処理が実行中です',
  MODEL_NOT_FOUND: 'モデルが見つかりません',
  DATASET_EMPTY: 'データセットが空です',
} as const

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'ログインしました',
  LOGOUT_SUCCESS: 'ログアウトしました',
  SAVE_SUCCESS: '保存しました',
  UPDATE_SUCCESS: '更新しました',
  DELETE_SUCCESS: '削除しました',
  UPLOAD_SUCCESS: 'アップロードが完了しました',
  TRAINING_STARTED: '学習を開始しました',
  TRAINING_COMPLETED: '学習が完了しました',
  MODEL_DEPLOYED: 'モデルをデプロイしました',
  DRONE_CONNECTED: 'ドローンに接続しました',
  DRONE_DISCONNECTED: 'ドローンから切断しました',
  COMMAND_SENT: 'コマンドを送信しました',
} as const

// Feature Flags
export const FEATURES = {
  MULTI_DRONE_SUPPORT: true,
  REAL_TIME_TRACKING: true,
  MODEL_TRAINING: true,
  BATCH_PREDICTION: true,
  AUTO_LABELING: true,
  EXPORT_IMPORT: true,
  PERFORMANCE_MONITORING: true,
  OFFLINE_MODE: false, // Not implemented yet
  VOICE_COMMANDS: false, // Future feature
  AR_OVERLAY: false, // Future feature
} as const

// Browser Support
export const BROWSER_SUPPORT = {
  MIN_CHROME_VERSION: 90,
  MIN_FIREFOX_VERSION: 88,
  MIN_SAFARI_VERSION: 14,
  MIN_EDGE_VERSION: 90,
  WEBRTC_REQUIRED: true,
  WEBSOCKET_REQUIRED: true,
} as const

// Performance Thresholds
export const PERFORMANCE = {
  PAGE_LOAD_WARNING: 3000, // milliseconds
  API_RESPONSE_WARNING: 2000, // milliseconds
  WEBSOCKET_PING_INTERVAL: 30000, // milliseconds
  MEMORY_USAGE_WARNING: 0.8, // 80%
  FPS_TARGET: 30,
  FPS_WARNING: 15,
} as const

// Export all constants as a single object for easier importing
export const CONSTANTS = {
  API_CONFIG,
  WS_EVENTS,
  DRONE_CONFIG,
  DRONE_COMMANDS,
  MOVEMENT_DIRECTIONS,
  ROTATION_DIRECTIONS,
  DRONE_STATUSES,
  TRAINING_STATUSES,
  DATASET_STATUSES,
  FILE_UPLOAD,
  MODEL_TYPES,
  YOLO_VARIANTS,
  TRAINING_CONFIG,
  UI_CONFIG,
  NOTIFICATION_CONFIG,
  PAGINATION_CONFIG,
  STORAGE_KEYS,
  THEME_CONFIG,
  CHART_CONFIG,
  MAP_CONFIG,
  VALIDATION,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  FEATURES,
  BROWSER_SUPPORT,
  PERFORMANCE,
} as const