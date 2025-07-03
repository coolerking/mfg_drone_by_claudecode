import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Drone {
  id: string
  name: string
  status: 'connected' | 'disconnected' | 'flying' | 'landing' | 'error'
  battery: number
  altitude: number
  temperature: number
  signal_strength: number
  flight_time: number
}

interface DroneState {
  drones: Drone[]
  selectedDrone: string | null
  isLoading: boolean
}

const initialState: DroneState = {
  drones: [],
  selectedDrone: null,
  isLoading: false,
}

const droneSlice = createSlice({
  name: 'drone',
  initialState,
  reducers: {
    setDrones: (state, action: PayloadAction<Drone[]>) => {
      state.drones = action.payload
    },
    updateDrone: (state, action: PayloadAction<Drone>) => {
      const index = state.drones.findIndex(drone => drone.id === action.payload.id)
      if (index !== -1) {
        state.drones[index] = action.payload
      }
    },
    setSelectedDrone: (state, action: PayloadAction<string | null>) => {
      state.selectedDrone = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
  },
})

export const { setDrones, updateDrone, setSelectedDrone, setLoading } = droneSlice.actions
export default droneSlice.reducer