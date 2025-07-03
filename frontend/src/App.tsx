import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense } from 'react'
import { Box, CircularProgress } from '@mui/material'

import { Layout } from './components/common/Layout'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { DroneManagement } from './pages/DroneManagement'
import { DatasetManagement } from './pages/DatasetManagement'
import { ModelManagement } from './pages/ModelManagement'
import { TrackingControl } from './pages/TrackingControl'
import { Settings } from './pages/Settings'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { useAuth } from './hooks/useAuth'

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    )
  }

  return (
    <ErrorBoundary>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />
          }
        />
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <Layout>
                <Suspense
                  fallback={
                    <Box
                      display="flex"
                      justifyContent="center"
                      alignItems="center"
                      minHeight="50vh"
                    >
                      <CircularProgress />
                    </Box>
                  }
                >
                  <Routes>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/drones" element={<DroneManagement />} />
                    <Route path="/datasets" element={<DatasetManagement />} />
                    <Route path="/models" element={<ModelManagement />} />
                    <Route path="/tracking" element={<TrackingControl />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </Suspense>
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </ErrorBoundary>
  )
}

export default App