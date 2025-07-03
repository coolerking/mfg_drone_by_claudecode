import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns'
import { ja } from 'date-fns/locale'

// Date and time formatting
export const formatDate = (date: string | Date, pattern = 'yyyy/MM/dd'): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '無効な日付'
    return format(dateObj, pattern, { locale: ja })
  } catch {
    return '無効な日付'
  }
}

export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, 'yyyy/MM/dd HH:mm:ss')
}

export const formatTime = (date: string | Date): string => {
  return formatDate(date, 'HH:mm:ss')
}

export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '無効な日付'
    return formatDistanceToNow(dateObj, { addSuffix: true, locale: ja })
  } catch {
    return '無効な日付'
  }
}

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}時間${minutes}分${remainingSeconds}秒`
  } else if (minutes > 0) {
    return `${minutes}分${remainingSeconds}秒`
  } else {
    return `${remainingSeconds}秒`
  }
}

// Number formatting
export const formatNumber = (num: number, decimals = 0): string => {
  return new Intl.NumberFormat('ja-JP', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num)
}

export const formatPercentage = (value: number, decimals = 1): string => {
  return `${formatNumber(value, decimals)}%`
}

export const formatCurrency = (amount: number, currency = 'JPY'): string => {
  return new Intl.NumberFormat('ja-JP', {
    style: 'currency',
    currency,
  }).format(amount)
}

// File size formatting
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${formatNumber(bytes / Math.pow(k, i), 2)} ${sizes[i]}`
}

// Battery level formatting
export const formatBatteryLevel = (level: number): string => {
  return `${Math.round(level)}%`
}

export const getBatteryColor = (level: number): 'error' | 'warning' | 'success' => {
  if (level <= 20) return 'error'
  if (level <= 40) return 'warning'
  return 'success'
}

// Distance formatting
export const formatDistance = (meters: number): string => {
  if (meters < 1000) {
    return `${formatNumber(meters, 1)} m`
  } else {
    return `${formatNumber(meters / 1000, 2)} km`
  }
}

// Speed formatting
export const formatSpeed = (metersPerSecond: number): string => {
  const kmh = metersPerSecond * 3.6
  return `${formatNumber(kmh, 1)} km/h`
}

// Coordinate formatting
export const formatCoordinate = (coord: number, type: 'lat' | 'lng'): string => {
  const direction = type === 'lat' 
    ? (coord >= 0 ? 'N' : 'S')
    : (coord >= 0 ? 'E' : 'W')
  
  return `${formatNumber(Math.abs(coord), 6)}° ${direction}`
}

export const formatPosition = (position: { x: number; y: number; z: number }): string => {
  return `X: ${formatNumber(position.x, 1)}m, Y: ${formatNumber(position.y, 1)}m, Z: ${formatNumber(position.z, 1)}m`
}

// Status formatting
export const formatDroneStatus = (status: string): string => {
  const statusMap: { [key: string]: string } = {
    connected: '接続済み',
    disconnected: '切断',
    flying: '飛行中',
    landed: '着陸',
    error: 'エラー',
    battery_low: 'バッテリー低下',
    emergency: '緊急事態',
    maintenance: 'メンテナンス中'
  }
  
  return statusMap[status] || status
}

export const formatTrainingStatus = (status: string): string => {
  const statusMap: { [key: string]: string } = {
    pending: '待機中',
    running: '実行中',
    completed: '完了',
    failed: '失敗',
    cancelled: 'キャンセル',
    paused: '一時停止'
  }
  
  return statusMap[status] || status
}

export const formatDatasetStatus = (status: string): string => {
  const statusMap: { [key: string]: string } = {
    active: 'アクティブ',
    processing: '処理中',
    archived: 'アーカイブ済み'
  }
  
  return statusMap[status] || status
}

// Model performance formatting
export const formatAccuracy = (accuracy: number): string => {
  return formatPercentage(accuracy * 100, 1)
}

export const formatConfidence = (confidence: number): string => {
  return formatPercentage(confidence * 100, 0)
}

export const formatMetric = (value: number, type: 'accuracy' | 'precision' | 'recall' | 'f1' | 'map'): string => {
  const percentage = value * 100
  return `${formatNumber(percentage, 1)}%`
}

// Error message formatting
export const formatErrorMessage = (error: any): string => {
  if (typeof error === 'string') return error
  if (error?.message) return error.message
  if (error?.response?.data?.message) return error.response.data.message
  if (error?.response?.data?.error) return error.response.data.error
  return 'エラーが発生しました'
}

// Training progress formatting
export const formatTrainingProgress = (progress: {
  epoch: number
  total_epochs: number
  loss: number
  accuracy?: number
  estimated_time_remaining?: number
}): string => {
  const parts = [
    `エポック ${progress.epoch}/${progress.total_epochs}`,
    `損失: ${formatNumber(progress.loss, 4)}`
  ]
  
  if (progress.accuracy !== undefined) {
    parts.push(`精度: ${formatAccuracy(progress.accuracy)}`)
  }
  
  if (progress.estimated_time_remaining !== undefined) {
    parts.push(`残り時間: ${formatDuration(progress.estimated_time_remaining)}`)
  }
  
  return parts.join(' | ')
}

// Image resolution formatting
export const formatResolution = (width: number, height: number): string => {
  return `${width} × ${height}`
}

export const formatAspectRatio = (width: number, height: number): string => {
  const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b)
  const divisor = gcd(width, height)
  return `${width / divisor}:${height / divisor}`
}

// URL formatting
export const formatApiUrl = (path: string): string => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
  return `${baseUrl}${path.startsWith('/') ? path : `/${path}`}`
}

export const formatWebSocketUrl = (path?: string): string => {
  const baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  return path ? `${baseUrl}${path.startsWith('/') ? path : `/${path}`}` : baseUrl
}

// Text truncation
export const truncateText = (text: string, maxLength: number, suffix = '...'): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - suffix.length) + suffix
}

export const truncateFilename = (filename: string, maxLength = 30): string => {
  if (filename.length <= maxLength) return filename
  
  const extension = filename.split('.').pop() || ''
  const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'))
  const maxNameLength = maxLength - extension.length - 4 // 4 for "..." and "."
  
  if (maxNameLength <= 0) return truncateText(filename, maxLength)
  
  return `${nameWithoutExt.substring(0, maxNameLength)}...${extension ? `.${extension}` : ''}`
}

// Color utilities for status indicators
export const getStatusColor = (status: string): 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' => {
  const colorMap: { [key: string]: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' } = {
    // Drone statuses
    connected: 'success',
    disconnected: 'error',
    flying: 'primary',
    landed: 'secondary',
    error: 'error',
    battery_low: 'warning',
    emergency: 'error',
    
    // Training statuses
    pending: 'secondary',
    running: 'primary',
    completed: 'success',
    failed: 'error',
    cancelled: 'warning',
    paused: 'warning',
    
    // Dataset statuses
    active: 'success',
    processing: 'primary',
    archived: 'secondary'
  }
  
  return colorMap[status] || 'secondary'
}

// Helper for safe JSON parsing
export const safeJsonParse = <T>(json: string, defaultValue: T): T => {
  try {
    return JSON.parse(json)
  } catch {
    return defaultValue
  }
}

// Helper for generating human-readable IDs
export const generateReadableId = (prefix = ''): string => {
  const timestamp = Date.now().toString(36)
  const random = Math.random().toString(36).substring(2, 8)
  return `${prefix}${prefix ? '_' : ''}${timestamp}_${random}`
}