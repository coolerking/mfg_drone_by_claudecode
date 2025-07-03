import { useEffect, useCallback } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState, AppDispatch } from '../store'
import type { LoginCredentials } from '../types/common'
import { 
  loginUser, 
  validateToken, 
  refreshToken,
  logout as logoutAction, 
  clearError 
} from '../store/slices/authSlice'

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { user, tokens, isAuthenticated, isLoading, error } = useSelector(
    (state: RootState) => state.auth
  )

  // Validate existing token on app load
  useEffect(() => {
    if (tokens?.accessToken && !isAuthenticated) {
      dispatch(validateToken())
    } else if (!tokens?.accessToken) {
      // No token, mark as not authenticated
      dispatch(logoutAction())
    }
  }, [dispatch, tokens, isAuthenticated])

  // Auto-refresh token when it's close to expiring
  useEffect(() => {
    if (!tokens?.expiresAt || !isAuthenticated) return

    const timeUntilExpiry = tokens.expiresAt - Date.now()
    const refreshThreshold = 5 * 60 * 1000 // 5 minutes before expiry

    if (timeUntilExpiry <= refreshThreshold && timeUntilExpiry > 0) {
      dispatch(refreshToken())
    }

    // Set up timer to refresh token
    const refreshTimer = setTimeout(() => {
      if (isAuthenticated && tokens?.refreshToken) {
        dispatch(refreshToken())
      }
    }, Math.max(timeUntilExpiry - refreshThreshold, 0))

    return () => clearTimeout(refreshTimer)
  }, [dispatch, tokens, isAuthenticated])

  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      const result = await dispatch(loginUser(credentials))
      
      if (loginUser.fulfilled.match(result)) {
        return { success: true }
      } else {
        return { 
          success: false, 
          error: result.payload || 'Login failed' 
        }
      }
    } catch (error) {
      return { 
        success: false, 
        error: 'Login failed' 
      }
    }
  }, [dispatch])

  const logout = useCallback(() => {
    dispatch(logoutAction())
  }, [dispatch])

  const clearAuthError = useCallback(() => {
    dispatch(clearError())
  }, [dispatch])

  const isTokenValid = useCallback(() => {
    if (!tokens?.accessToken || !tokens?.expiresAt) return false
    return Date.now() < tokens.expiresAt
  }, [tokens])

  return {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    clearError: clearAuthError,
    isTokenValid,
  }
}