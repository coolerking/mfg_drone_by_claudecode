import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_usage: number
}

interface DashboardStats {
  connected_drones: number
  active_datasets: number
  running_models: number
  active_tracking: number
}

interface DashboardState {
  stats: DashboardStats
  systemMetrics: SystemMetrics
  alerts: string[]
  lastUpdate: string | null
  isLoading: boolean
}

const initialState: DashboardState = {
  stats: {
    connected_drones: 0,
    active_datasets: 0,
    running_models: 0,
    active_tracking: 0,
  },
  systemMetrics: {
    cpu_usage: 0,
    memory_usage: 0,
    disk_usage: 0,
    network_usage: 0,
  },
  alerts: [],
  lastUpdate: null,
  isLoading: false,
}

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setStats: (state, action: PayloadAction<DashboardStats>) => {
      state.stats = action.payload
    },
    setSystemMetrics: (state, action: PayloadAction<SystemMetrics>) => {
      state.systemMetrics = action.payload
    },
    setAlerts: (state, action: PayloadAction<string[]>) => {
      state.alerts = action.payload
    },
    addAlert: (state, action: PayloadAction<string>) => {
      state.alerts.push(action.payload)
    },
    removeAlert: (state, action: PayloadAction<number>) => {
      state.alerts.splice(action.payload, 1)
    },
    updateLastUpdate: (state) => {
      state.lastUpdate = new Date().toISOString()
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
  },
})

export const {
  setStats,
  setSystemMetrics,
  setAlerts,
  addAlert,
  removeAlert,
  updateLastUpdate,
  setLoading,
} = dashboardSlice.actions
export default dashboardSlice.reducer