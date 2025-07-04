import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense } from 'react'
import { Box } from '@mui/material'

import { Layout } from './components/common/Layout'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { DroneManagement } from './pages/DroneManagement'
import { DatasetManagement } from './pages/DatasetManagement'
import { ModelManagement } from './pages/ModelManagement'
import { TrackingControl } from './pages/TrackingControl'
import { SystemMonitoring } from './pages/SystemMonitoring'
import { Settings } from './pages/Settings'
import { ErrorBoundary, PageLoading, OfflineIndicator } from './components/common'
import { useAuth } from './hooks/useAuth'

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <PageLoading text="認証情報を確認中..." />
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
              <>
                <Layout>
                  <Suspense fallback={<PageLoading text="ページを読み込み中..." />}>
                    <Routes>
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/drones" element={<DroneManagement />} />
                      <Route path="/datasets" element={<DatasetManagement />} />
                      <Route path="/models" element={<ModelManagement />} />
                      <Route path="/tracking" element={<TrackingControl />} />
                      <Route path="/monitoring" element={<SystemMonitoring />} />
                      <Route path="/settings" element={<Settings />} />
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                  </Suspense>
                </Layout>
                
                {/* Offline Indicator - Fixed Position */}
                <OfflineIndicator position="fixed" />
              </>
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