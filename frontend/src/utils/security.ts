/**
 * セキュリティユーティリティ
 */

// =============================================================================
// Input Sanitization
// =============================================================================

/**
 * HTMLエスケープ
 */
export const escapeHtml = (text: string): string => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

/**
 * XSS対策のためのHTML文字列サニタイズ
 */
export const sanitizeHtml = (html: string): string => {
  const allowedTags = ['b', 'i', 'em', 'strong', 'span', 'p', 'br']
  const allowedAttributes = ['class', 'id']
  
  // 簡易的なサニタイズ（実際のプロダクションではDOMPurifyなどを使用）
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = html
  
  const sanitize = (element: Element): void => {
    // 許可されていないタグを削除
    if (!allowedTags.includes(element.tagName.toLowerCase())) {
      element.remove()
      return
    }
    
    // 許可されていない属性を削除
    Array.from(element.attributes).forEach(attr => {
      if (!allowedAttributes.includes(attr.name.toLowerCase())) {
        element.removeAttribute(attr.name)
      }
    })
    
    // 子要素を再帰的にサニタイズ
    Array.from(element.children).forEach(child => {
      sanitize(child)
    })
  }
  
  Array.from(tempDiv.children).forEach(child => {
    sanitize(child)
  })
  
  return tempDiv.innerHTML
}

/**
 * SQLインジェクション対策のための文字列エスケープ
 */
export const escapeSql = (input: string): string => {
  return input.replace(/'/g, "''").replace(/;/g, '\\;')
}

/**
 * パス・ディレクトリトラバーサル攻撃対策
 */
export const sanitizePath = (path: string): string => {
  return path
    .replace(/\.\./g, '') // ../ を除去
    .replace(/[<>:"|?*]/g, '') // 無効な文字を除去
    .replace(/^\/+/, '') // 先頭のスラッシュを除去
    .trim()
}

// =============================================================================
// Token Management
// =============================================================================

/**
 * JWTトークンのデコード（検証なし）
 */
export const decodeJwt = (token: string): any => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    return null
  }
}

/**
 * JWTトークンの有効期限チェック
 */
export const isTokenExpired = (token: string): boolean => {
  const decoded = decodeJwt(token)
  if (!decoded || !decoded.exp) {
    return true
  }
  
  const currentTime = Math.floor(Date.now() / 1000)
  return decoded.exp < currentTime
}

/**
 * トークンの安全な保存
 */
export const secureTokenStorage = {
  setToken: (token: string): void => {
    // HttpOnly Cookieが理想だが、フロントエンドでは暗号化してlocalStorageに保存
    const encrypted = btoa(token) // 簡易暗号化（実際にはより強力な暗号化を使用）
    localStorage.setItem('auth_token', encrypted)
  },
  
  getToken: (): string | null => {
    const encrypted = localStorage.getItem('auth_token')
    if (!encrypted) return null
    
    try {
      return atob(encrypted) // 復号化
    } catch {
      localStorage.removeItem('auth_token')
      return null
    }
  },
  
  removeToken: (): void => {
    localStorage.removeItem('auth_token')
  },
  
  refreshToken: (newToken: string): void => {
    secureTokenStorage.removeToken()
    secureTokenStorage.setToken(newToken)
  }
}

// =============================================================================
// Content Security Policy
// =============================================================================

/**
 * CSP違反レポート処理
 */
export const handleCSPViolation = (violationReport: any): void => {
  console.warn('CSP Violation:', violationReport)
  
  // 違反レポートをサーバーに送信
  fetch('/api/security/csp-violation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(violationReport)
  }).catch(error => {
    console.error('CSP violation report failed:', error)
  })
}

/**
 * CSP違反監視の設定
 */
export const setupCSPMonitoring = (): void => {
  document.addEventListener('securitypolicyviolation', (event) => {
    handleCSPViolation({
      blockedURI: event.blockedURI,
      documentURI: event.documentURI,
      effectiveDirective: event.effectiveDirective,
      originalPolicy: event.originalPolicy,
      referrer: event.referrer,
      violatedDirective: event.violatedDirective,
      timestamp: new Date().toISOString()
    })
  })
}

// =============================================================================
// Session Management
// =============================================================================

/**
 * セッション管理
 */
export class SessionManager {
  private static instance: SessionManager
  private sessionTimeout: number = 15 * 60 * 1000 // 15分
  private timeoutId: number | null = null
  private lastActivity: number = Date.now()
  
  static getInstance(): SessionManager {
    if (!SessionManager.instance) {
      SessionManager.instance = new SessionManager()
    }
    return SessionManager.instance
  }
  
  private constructor() {
    this.setupActivityTracking()
  }
  
  private setupActivityTracking(): void {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
    
    events.forEach(event => {
      document.addEventListener(event, () => {
        this.updateActivity()
      }, { passive: true })
    })
  }
  
  private updateActivity(): void {
    this.lastActivity = Date.now()
    this.resetTimeout()
  }
  
  private resetTimeout(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
    }
    
    this.timeoutId = window.setTimeout(() => {
      this.handleSessionTimeout()
    }, this.sessionTimeout)
  }
  
  private handleSessionTimeout(): void {
    // セッションタイムアウト時の処理
    secureTokenStorage.removeToken()
    window.location.href = '/login'
    
    // タイムアウト通知
    alert('セッションがタイムアウトしました。再度ログインしてください。')
  }
  
  getLastActivity(): number {
    return this.lastActivity
  }
  
  getRemainingTime(): number {
    const elapsed = Date.now() - this.lastActivity
    return Math.max(0, this.sessionTimeout - elapsed)
  }
  
  extendSession(): void {
    this.updateActivity()
  }
  
  setSessionTimeout(timeout: number): void {
    this.sessionTimeout = timeout
    this.resetTimeout()
  }
}

// =============================================================================
// Password Security
// =============================================================================

/**
 * パスワード強度チェック
 */
export interface PasswordStrength {
  score: number // 0-4
  level: 'very-weak' | 'weak' | 'fair' | 'good' | 'strong'
  suggestions: string[]
}

export const checkPasswordStrength = (password: string): PasswordStrength => {
  let score = 0
  const suggestions: string[] = []
  
  // 長さチェック
  if (password.length >= 8) score++
  else suggestions.push('8文字以上にしてください')
  
  if (password.length >= 12) score++
  
  // 文字種チェック
  if (/[a-z]/.test(password)) score++
  else suggestions.push('小文字を含めてください')
  
  if (/[A-Z]/.test(password)) score++
  else suggestions.push('大文字を含めてください')
  
  if (/[0-9]/.test(password)) score++
  else suggestions.push('数字を含めてください')
  
  if (/[^a-zA-Z0-9]/.test(password)) score++
  else suggestions.push('記号を含めてください')
  
  // 一般的なパスワードチェック
  const commonPasswords = ['password', '123456', 'qwerty', 'admin']
  if (commonPasswords.some(common => password.toLowerCase().includes(common))) {
    score = Math.max(0, score - 2)
    suggestions.push('一般的なパスワードは避けてください')
  }
  
  // レベル判定
  let level: PasswordStrength['level']
  if (score <= 1) level = 'very-weak'
  else if (score <= 2) level = 'weak'
  else if (score <= 3) level = 'fair'
  else if (score <= 4) level = 'good'
  else level = 'strong'
  
  return { score: Math.min(5, score), level, suggestions }
}

/**
 * パスワードハッシュ化（クライアント側での追加セキュリティ）
 */
export const hashPassword = async (password: string, salt: string): Promise<string> => {
  const encoder = new TextEncoder()
  const data = encoder.encode(password + salt)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

// =============================================================================
// Permission Management
// =============================================================================

/**
 * 権限レベル
 */
export enum PermissionLevel {
  GUEST = 0,
  USER = 1,
  OPERATOR = 2,
  ADMIN = 3,
  SUPER_ADMIN = 4
}

/**
 * 権限チェック
 */
export const hasPermission = (
  userRole: string,
  requiredLevel: PermissionLevel
): boolean => {
  const userLevel = getRoleLevel(userRole)
  return userLevel >= requiredLevel
}

/**
 * ロールレベル取得
 */
export const getRoleLevel = (role: string): PermissionLevel => {
  switch (role.toLowerCase()) {
    case 'super_admin':
      return PermissionLevel.SUPER_ADMIN
    case 'admin':
      return PermissionLevel.ADMIN
    case 'operator':
      return PermissionLevel.OPERATOR
    case 'user':
      return PermissionLevel.USER
    default:
      return PermissionLevel.GUEST
  }
}

/**
 * リソースアクセス権限チェック
 */
export const canAccessResource = (
  userRole: string,
  resource: string,
  action: 'read' | 'write' | 'delete' | 'admin'
): boolean => {
  const permissions: Record<string, Record<string, PermissionLevel>> = {
    drones: {
      read: PermissionLevel.USER,
      write: PermissionLevel.OPERATOR,
      delete: PermissionLevel.ADMIN,
      admin: PermissionLevel.ADMIN
    },
    datasets: {
      read: PermissionLevel.USER,
      write: PermissionLevel.USER,
      delete: PermissionLevel.OPERATOR,
      admin: PermissionLevel.ADMIN
    },
    models: {
      read: PermissionLevel.USER,
      write: PermissionLevel.OPERATOR,
      delete: PermissionLevel.ADMIN,
      admin: PermissionLevel.ADMIN
    },
    system: {
      read: PermissionLevel.OPERATOR,
      write: PermissionLevel.ADMIN,
      delete: PermissionLevel.SUPER_ADMIN,
      admin: PermissionLevel.SUPER_ADMIN
    }
  }
  
  const resourcePermissions = permissions[resource]
  if (!resourcePermissions) return false
  
  const requiredLevel = resourcePermissions[action]
  if (requiredLevel === undefined) return false
  
  return hasPermission(userRole, requiredLevel)
}

// =============================================================================
// Rate Limiting
// =============================================================================

/**
 * レート制限管理
 */
export class RateLimiter {
  private requests: Map<string, number[]> = new Map()
  private limits: Map<string, { count: number; window: number }> = new Map()
  
  setLimit(key: string, count: number, windowMs: number): void {
    this.limits.set(key, { count, window: windowMs })
  }
  
  isAllowed(key: string): boolean {
    const limit = this.limits.get(key)
    if (!limit) return true
    
    const now = Date.now()
    const requests = this.requests.get(key) || []
    
    // 古いリクエストを削除
    const validRequests = requests.filter(time => now - time < limit.window)
    
    if (validRequests.length >= limit.count) {
      return false
    }
    
    validRequests.push(now)
    this.requests.set(key, validRequests)
    return true
  }
  
  getRemainingRequests(key: string): number {
    const limit = this.limits.get(key)
    if (!limit) return Infinity
    
    const now = Date.now()
    const requests = this.requests.get(key) || []
    const validRequests = requests.filter(time => now - time < limit.window)
    
    return Math.max(0, limit.count - validRequests.length)
  }
  
  getResetTime(key: string): number {
    const requests = this.requests.get(key) || []
    const limit = this.limits.get(key)
    
    if (!limit || requests.length === 0) return 0
    
    const oldestRequest = Math.min(...requests)
    return oldestRequest + limit.window
  }
}

// =============================================================================
// Security Headers
// =============================================================================

/**
 * セキュリティヘッダーチェック
 */
export const checkSecurityHeaders = async (url?: string): Promise<{
  headers: Record<string, string>
  recommendations: string[]
}> => {
  const targetUrl = url || window.location.origin
  const recommendations: string[] = []
  const headers: Record<string, string> = {}
  
  try {
    const response = await fetch(targetUrl, { method: 'HEAD' })
    
    // 重要なセキュリティヘッダーをチェック
    const securityHeaders = [
      'Content-Security-Policy',
      'X-Frame-Options',
      'X-Content-Type-Options',
      'Referrer-Policy',
      'Permissions-Policy',
      'Strict-Transport-Security'
    ]
    
    securityHeaders.forEach(header => {
      const value = response.headers.get(header)
      if (value) {
        headers[header] = value
      } else {
        recommendations.push(`${header} ヘッダーが設定されていません`)
      }
    })
    
  } catch (error) {
    recommendations.push('セキュリティヘッダーのチェックに失敗しました')
  }
  
  return { headers, recommendations }
}

// =============================================================================
// Export Security Manager
// =============================================================================

export const SecurityManager = {
  // Input sanitization
  escapeHtml,
  sanitizeHtml,
  escapeSql,
  sanitizePath,
  
  // Token management
  decodeJwt,
  isTokenExpired,
  secureTokenStorage,
  
  // CSP
  handleCSPViolation,
  setupCSPMonitoring,
  
  // Session management
  SessionManager,
  
  // Password security
  checkPasswordStrength,
  hashPassword,
  
  // Permission management
  PermissionLevel,
  hasPermission,
  getRoleLevel,
  canAccessResource,
  
  // Rate limiting
  RateLimiter,
  
  // Security headers
  checkSecurityHeaders,
}