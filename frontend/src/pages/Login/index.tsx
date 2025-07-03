import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Checkbox,
  FormControlLabel,
} from '@mui/material'
import { useAuth } from '../../hooks/useAuth'
import { useNotification } from '../../hooks/useNotification'
import type { LoginCredentials } from '../../types/common'

export function Login() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('password')
  const [rememberMe, setRememberMe] = useState(true)
  
  const { login, isLoading, error, clearError } = useAuth()
  const { showSuccess, showErrorFromException } = useNotification()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!username || !password) {
      showErrorFromException('ユーザー名とパスワードを入力してください')
      return
    }

    clearError()

    const credentials: LoginCredentials = { username, password }
    const result = await login(credentials)
    
    if (result.success) {
      showSuccess('ログインしました')
      navigate('/dashboard')
    } else {
      showErrorFromException(result.error || 'ログインに失敗しました')
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0d6efd, #0dcaf0)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 400, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Box textAlign="center" mb={3}>
            <Typography variant="h3" component="div" gutterBottom>
              🚁
            </Typography>
            <Typography variant="h4" component="h1" gutterBottom>
              MFGドローン
            </Typography>
            <Typography variant="body2" color="text.secondary">
              自動追従撮影管理システム
            </Typography>
          </Box>

          {/* Demo credentials info */}
          <Alert severity="info" sx={{ mb: 3 }}>
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
          </Alert>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="ユーザー名"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              autoFocus
              disabled={isLoading}
            />
            
            <TextField
              fullWidth
              label="パスワード"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              disabled={isLoading}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  disabled={isLoading}
                />
              }
              label="ログイン状態を保持する"
              sx={{ mt: 1, mb: 2 }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoading}
              sx={{ mt: 2 }}
            >
              {isLoading ? (
                <CircularProgress size={24} />
              ) : (
                '🔓 システムにログイン'
              )}
            </Button>
          </form>

          <Box textAlign="center" mt={3}>
            <Typography variant="caption" color="text.secondary">
              Version 1.0.0 | Build 2025.07.03
            </Typography>
            <br />
            <Typography variant="caption" color="text.secondary">
              © 2025 MFG Drone System. Sample Frontend.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}