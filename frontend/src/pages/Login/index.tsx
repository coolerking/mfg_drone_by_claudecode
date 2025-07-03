import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Typography,
  Alert,
  Checkbox,
  FormControlLabel,
  IconButton,
  InputAdornment,
  Divider,
  LinearProgress,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  Security as SecurityIcon,
  Person as PersonIcon,
  Lock as LockIcon,
  Info as InfoIcon,
} from '@mui/icons-material'

import { useAuth } from '../../hooks/useAuth'
import { useNotification } from '../../hooks/useNotification'
import { Button, StatusBadge } from '../../components/common'
import type { LoginCredentials } from '../../types/common'

// Validation patterns
const VALIDATION_RULES = {
  username: {
    minLength: 3,
    maxLength: 50,
    pattern: /^[a-zA-Z0-9_-]+$/,
  },
  password: {
    minLength: 4,
    maxLength: 100,
  },
}

interface FormErrors {
  username?: string
  password?: string
  general?: string
}

interface LoginAttempt {
  timestamp: number
  success: boolean
}

export function Login() {
  // Basic form state
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('password')
  const [rememberMe, setRememberMe] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  
  // Enhanced state
  const [errors, setErrors] = useState<FormErrors>({})
  const [touched, setTouched] = useState({ username: false, password: false })
  const [loginAttempts, setLoginAttempts] = useState<LoginAttempt[]>([])
  const [isBlocked, setIsBlocked] = useState(false)
  const [blockTimeRemaining, setBlockTimeRemaining] = useState(0)
  const [autoLogin, setAutoLogin] = useState(false)
  
  // Hooks
  const { login, isLoading, error, clearError, user } = useAuth()
  const { showSuccess, showError } = useNotification()
  const navigate = useNavigate()
  const location = useLocation()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  
  // Get redirect path from location state
  const from = (location.state as any)?.from?.pathname || '/dashboard'

  // Validation functions
  const validateUsername = (value: string): string | undefined => {
    if (!value.trim()) return 'ユーザー名は必須です'
    if (value.length < VALIDATION_RULES.username.minLength) {
      return `ユーザー名は${VALIDATION_RULES.username.minLength}文字以上である必要があります`
    }
    if (value.length > VALIDATION_RULES.username.maxLength) {
      return `ユーザー名は${VALIDATION_RULES.username.maxLength}文字以下である必要があります`
    }
    if (!VALIDATION_RULES.username.pattern.test(value)) {
      return 'ユーザー名は英数字、ハイフン、アンダースコアのみ使用可能です'
    }
    return undefined
  }

  const validatePassword = (value: string): string | undefined => {
    if (!value) return 'パスワードは必須です'
    if (value.length < VALIDATION_RULES.password.minLength) {
      return `パスワードは${VALIDATION_RULES.password.minLength}文字以上である必要があります`
    }
    if (value.length > VALIDATION_RULES.password.maxLength) {
      return `パスワードは${VALIDATION_RULES.password.maxLength}文字以下である必要があります`
    }
    return undefined
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}
    
    const usernameError = validateUsername(username)
    if (usernameError) newErrors.username = usernameError
    
    const passwordError = validatePassword(password)
    if (passwordError) newErrors.password = passwordError
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // Security: Track login attempts
  const addLoginAttempt = (success: boolean) => {
    const attempt: LoginAttempt = {
      timestamp: Date.now(),
      success,
    }
    
    setLoginAttempts(prev => {
      const recent = prev.filter(a => Date.now() - a.timestamp < 15 * 60 * 1000) // Last 15 minutes
      return [...recent, attempt].slice(-10) // Keep last 10 attempts
    })
  }

  const checkSecurityBlock = (): boolean => {
    const recentFailures = loginAttempts.filter(
      a => !a.success && Date.now() - a.timestamp < 15 * 60 * 1000
    )
    
    if (recentFailures.length >= 5) {
      setIsBlocked(true)
      setBlockTimeRemaining(300) // 5 minutes block
      return true
    }
    
    return false
  }

  // Auto-login check
  useEffect(() => {
    const checkAutoLogin = () => {
      const savedUsername = localStorage.getItem('rememberedUsername')
      const savedRememberMe = localStorage.getItem('rememberMe') === 'true'
      
      if (savedUsername && savedRememberMe) {
        setUsername(savedUsername)
        setRememberMe(true)
        setAutoLogin(true)
      }
    }
    
    // Redirect if already logged in
    if (user) {
      navigate(from, { replace: true })
      return
    }
    
    checkAutoLogin()
  }, [user, navigate, from])

  // Block timer
  useEffect(() => {
    if (blockTimeRemaining > 0) {
      const timer = setTimeout(() => {
        setBlockTimeRemaining(prev => prev - 1)
      }, 1000)
      
      return () => clearTimeout(timer)
    } else if (isBlocked) {
      setIsBlocked(false)
    }
  }, [blockTimeRemaining, isBlocked])

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (isBlocked) {
      showError(`セキュリティのため、あと${blockTimeRemaining}秒後に再試行してください`)
      return
    }
    
    if (!validateForm()) return
    
    if (checkSecurityBlock()) {
      showError('ログイン試行回数が上限に達しました。15分後に再試行してください。')
      return
    }

    clearError()
    setErrors({})

    const credentials: LoginCredentials = { username, password }
    const result = await login(credentials)
    
    if (result.success) {
      addLoginAttempt(true)
      
      // Save remember me preference
      if (rememberMe) {
        localStorage.setItem('rememberedUsername', username)
        localStorage.setItem('rememberMe', 'true')
      } else {
        localStorage.removeItem('rememberedUsername')
        localStorage.removeItem('rememberMe')
      }
      
      showSuccess('ログインに成功しました')
      navigate(from, { replace: true })
    } else {
      addLoginAttempt(false)
      setErrors({ general: result.error || 'ログインに失敗しました' })
    }
  }

  // Handle field changes with validation
  const handleUsernameChange = (value: string) => {
    setUsername(value)
    if (touched.username) {
      const error = validateUsername(value)
      setErrors(prev => ({ ...prev, username: error }))
    }
  }

  const handlePasswordChange = (value: string) => {
    setPassword(value)
    if (touched.password) {
      const error = validatePassword(value)
      setErrors(prev => ({ ...prev, password: error }))
    }
  }

  const handleFieldBlur = (field: 'username' | 'password') => {
    setTouched(prev => ({ ...prev, [field]: true }))
    
    if (field === 'username') {
      const error = validateUsername(username)
      setErrors(prev => ({ ...prev, username: error }))
    } else {
      const error = validatePassword(password)
      setErrors(prev => ({ ...prev, password: error }))
    }
  }

  // Calculate password strength for demo
  const getPasswordStrength = (pwd: string) => {
    let strength = 0
    if (pwd.length >= 8) strength += 20
    if (/[a-z]/.test(pwd)) strength += 20
    if (/[A-Z]/.test(pwd)) strength += 20
    if (/[0-9]/.test(pwd)) strength += 20
    if (/[^A-Za-z0-9]/.test(pwd)) strength += 20
    return Math.min(strength, 100)
  }

  const passwordStrength = getPasswordStrength(password)

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1976d2, #42a5f5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
        position: 'relative',
      }}
    >
      {/* Background pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: 'radial-gradient(circle at 20% 50%, white 1px, transparent 1px)',
          backgroundSize: '20px 20px',
          opacity: 0.1,
        }}
      />

      <Card sx={{ 
        maxWidth: isMobile ? '100%' : 450, 
        width: '100%', 
        position: 'relative',
        boxShadow: theme.shadows[20],
      }}>
        {isLoading && (
          <LinearProgress 
            sx={{ 
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              borderRadius: '4px 4px 0 0',
            }} 
          />
        )}
        
        <CardContent sx={{ p: isMobile ? 3 : 4 }}>
          {/* Header */}
          <Box textAlign="center" mb={4}>
            <Typography variant="h2" component="div" gutterBottom sx={{ fontSize: 48 }}>
              🚁
            </Typography>
            <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
              MFGドローン
            </Typography>
            <Typography variant="body1" color="text.secondary">
              自動追従撮影管理システム
            </Typography>
            
            {/* System status */}
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 1 }}>
              <StatusBadge status="online" variant="chip" size="small" />
              <Chip label="v1.0.0" size="small" variant="outlined" />
            </Box>
          </Box>

          {/* Auto-login notification */}
          {autoLogin && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon fontSize="small" />
                <Typography variant="body2">
                  ユーザー "{username}" として自動ログインが有効です
                </Typography>
              </Box>
            </Alert>
          )}

          {/* Security warning */}
          {isBlocked && (
            <Alert severity="error" sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SecurityIcon fontSize="small" />
                <Box>
                  <Typography variant="body2" fontWeight="bold">
                    セキュリティブロック
                  </Typography>
                  <Typography variant="body2">
                    残り時間: {Math.floor(blockTimeRemaining / 60)}分{blockTimeRemaining % 60}秒
                  </Typography>
                </Box>
              </Box>
            </Alert>
          )}

          {/* Demo credentials info */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
              <InfoIcon fontSize="small" />
              <Box>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  📋 デモ用認証情報
                </Typography>
                <Typography variant="body2">
                  ユーザー名: admin または任意の文字
                </Typography>
                <Typography variant="body2">
                  パスワード: password または任意の文字
                </Typography>
                <Typography variant="caption" display="block" sx={{ mt: 1, fontStyle: 'italic' }}>
                  ※これはサンプル画面です。実際の認証は行われません。
                </Typography>
              </Box>
            </Box>
          </Alert>

          {/* General error */}
          {(errors.general || error) && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errors.general || error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            {/* Username field */}
            <TextField
              fullWidth
              label="ユーザー名"
              value={username}
              onChange={(e) => handleUsernameChange(e.target.value)}
              onBlur={() => handleFieldBlur('username')}
              margin="normal"
              autoFocus={!autoLogin}
              disabled={isLoading || isBlocked}
              error={Boolean(errors.username)}
              helperText={errors.username}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PersonIcon color={errors.username ? 'error' : 'action'} />
                  </InputAdornment>
                ),
              }}
            />
            
            {/* Password field */}
            <TextField
              fullWidth
              label="パスワード"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => handlePasswordChange(e.target.value)}
              onBlur={() => handleFieldBlur('password')}
              margin="normal"
              disabled={isLoading || isBlocked}
              error={Boolean(errors.password)}
              helperText={errors.password}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon color={errors.password ? 'error' : 'action'} />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      disabled={isLoading || isBlocked}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            {/* Password strength indicator */}
            {password && touched.password && (
              <Box sx={{ mt: 1, mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    パスワード強度
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {passwordStrength < 40 ? '弱' : passwordStrength < 80 ? '中' : '強'}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={passwordStrength}
                  color={passwordStrength < 40 ? 'error' : passwordStrength < 80 ? 'warning' : 'success'}
                  sx={{ height: 4, borderRadius: 2 }}
                />
              </Box>
            )}

            {/* Remember me */}
            <FormControlLabel
              control={
                <Checkbox
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  disabled={isLoading || isBlocked}
                />
              }
              label="ログイン状態を保持する"
              sx={{ mt: 1, mb: 2 }}
            />

            {/* Login button */}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoading || isBlocked || Object.keys(errors).length > 0}
              loading={isLoading}
              sx={{ 
                mt: 2,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold',
              }}
            >
              🔓 システムにログイン
            </Button>
          </form>

          <Divider sx={{ mt: 3, mb: 2 }} />

          {/* Footer info */}
          <Box textAlign="center">
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 1 }}>
              <Chip label="Version 1.0.0" size="small" variant="outlined" />
              <Chip label="Build 2025.07.03" size="small" variant="outlined" />
            </Box>
            <Typography variant="caption" color="text.secondary">
              © 2025 MFG Drone System. Sample Frontend.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}