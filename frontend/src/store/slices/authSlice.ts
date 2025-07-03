import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'
import type { User, AuthTokens, LoginCredentials, LoginResponse } from '../../types/common'
import { api } from '../../services/api/apiClient'
import { getStoredTokens, storeTokens, clearStoredTokens } from '../../services/api/apiClient'

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

const initialState: AuthState = {
  user: null,
  tokens: getStoredTokens(),
  isAuthenticated: false,
  isLoading: true,
  error: null,
}

// Async thunks for authentication
export const loginUser = createAsyncThunk<
  LoginResponse,
  LoginCredentials,
  { rejectValue: string }
>('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const response = await api.post<LoginResponse>('/auth/login', credentials)
    return response
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.message || 'Login failed')
  }
})

export const refreshToken = createAsyncThunk<
  AuthTokens,
  void,
  { rejectValue: string }
>('auth/refresh', async (_, { rejectWithValue }) => {
  try {
    const tokens = getStoredTokens()
    if (!tokens?.refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await api.post<AuthTokens>('/auth/refresh', {
      refresh_token: tokens.refreshToken,
    })
    return response
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.message || 'Token refresh failed')
  }
})

export const validateToken = createAsyncThunk<
  User,
  void,
  { rejectValue: string }
>('auth/validate', async (_, { rejectWithValue }) => {
  try {
    const tokens = getStoredTokens()
    if (!tokens?.accessToken) {
      throw new Error('No access token available')
    }

    // Check if token is expired
    if (Date.now() >= tokens.expiresAt) {
      throw new Error('Token expired')
    }

    const response = await api.get<{ user: User }>('/auth/me')
    return response.user
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.message || 'Token validation failed')
  }
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null
      state.tokens = null
      state.isAuthenticated = false
      state.isLoading = false
      state.error = null
      clearStoredTokens()
    },
    clearError: (state) => {
      state.error = null
    },
    setAuthenticated: (state, action: PayloadAction<boolean>) => {
      state.isAuthenticated = action.payload
      state.isLoading = false
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.user = action.payload.user
        state.tokens = action.payload.tokens
        state.isAuthenticated = true
        state.isLoading = false
        state.error = null
        storeTokens(action.payload.tokens)
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.user = null
        state.tokens = null
        state.isAuthenticated = false
        state.isLoading = false
        state.error = action.payload || 'Login failed'
        clearStoredTokens()
      })

    // Token refresh
    builder
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.tokens = action.payload
        state.error = null
        storeTokens(action.payload)
      })
      .addCase(refreshToken.rejected, (state) => {
        state.user = null
        state.tokens = null
        state.isAuthenticated = false
        state.error = 'Session expired'
        clearStoredTokens()
      })

    // Token validation
    builder
      .addCase(validateToken.pending, (state) => {
        state.isLoading = true
      })
      .addCase(validateToken.fulfilled, (state, action) => {
        state.user = action.payload
        state.isAuthenticated = true
        state.isLoading = false
        state.error = null
      })
      .addCase(validateToken.rejected, (state) => {
        state.user = null
        state.tokens = null
        state.isAuthenticated = false
        state.isLoading = false
        clearStoredTokens()
      })
  },
})

export const { logout, clearError, setAuthenticated } = authSlice.actions
export default authSlice.reducer