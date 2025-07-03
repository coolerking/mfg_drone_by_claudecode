import { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState, AppDispatch } from '../store'
import { loginStart, loginSuccess, loginFailure, setAuthenticated } from '../store/slices/authSlice'

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { user, token, isAuthenticated, isLoading } = useSelector(
    (state: RootState) => state.auth
  )

  useEffect(() => {
    // Check for existing token on app load
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      // In a real app, you would validate the token with the server
      // For now, we'll just mark as authenticated
      dispatch(setAuthenticated(true))
    } else {
      dispatch(setAuthenticated(false))
    }
  }, [dispatch])

  const login = async (username: string, password: string) => {
    dispatch(loginStart())
    
    try {
      // Mock login for demo purposes
      // In a real app, this would be an API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockUser = {
        id: '1',
        username,
        role: 'admin' as const,
      }
      
      const mockToken = 'mock-jwt-token-' + Date.now()
      
      dispatch(loginSuccess({ user: mockUser, token: mockToken }))
      return { success: true }
    } catch (error) {
      dispatch(loginFailure())
      return { success: false, error: 'Login failed' }
    }
  }

  const logout = () => {
    dispatch(loginFailure())
  }

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
  }
}