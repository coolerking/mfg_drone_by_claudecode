import React, { useState, useEffect, useMemo } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Alert,
  Stack,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  Pagination
} from '@mui/material'
import { Add, Refresh, Search } from '@mui/icons-material'
import { 
  DroneCard, 
  DroneStats, 
  DroneControl, 
  CameraStream, 
  DroneSearch, 
  AddDroneModal 
} from '../../components/drone'
import { useNotification } from '../../hooks/useNotification'
import { useWebSocket } from '../../hooks/useWebSocket'
import { droneApi } from '../../services/api/droneApi'
import { Drone, DroneStatus } from '../../types/drone'
import { formatDistanceToNow } from 'date-fns'
import { ja } from 'date-fns/locale'

const ITEMS_PER_PAGE = 12

export function DroneManagement() {
  const [drones, setDrones] = useState<Drone[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDrone, setSelectedDrone] = useState<Drone | null>(null)
  const [controlModalOpen, setControlModalOpen] = useState(false)
  const [cameraModalOpen, setCameraModalOpen] = useState(false)
  const [addModalOpen, setAddModalOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<DroneStatus | 'all'>('all')
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'battery' | 'lastSeen'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [currentPage, setCurrentPage] = useState(1)

  const { showNotification } = useNotification()
  const { isConnected, sendMessage } = useWebSocket('drone_management')

  // Mock data for development
  const mockDrones: Drone[] = [
    {
      id: 'drone-1',
      name: 'Tello EDU - Alpha',
      model: 'Tello EDU',
      serial_number: 'TELLO-001',
      status: 'connected',
      battery: 85,
      altitude: 0,
      temperature: 24,
      signal_strength: 90,
      flight_time: 0,
      position: { x: 0, y: 0, z: 0 },
      camera: { isStreaming: false, resolution: '720p', fps: 30 },
      lastSeen: new Date().toISOString(),
      createdAt: new Date().toISOString()
    },
    {
      id: 'drone-2', 
      name: 'Tello EDU - Beta',
      model: 'Tello EDU',
      serial_number: 'TELLO-002',
      status: 'flying',
      battery: 65,
      altitude: 50,
      temperature: 26,
      signal_strength: 85,
      flight_time: 120,
      position: { x: 10, y: 5, z: 50 },
      camera: { isStreaming: true, resolution: '720p', fps: 30, streamUrl: '/api/drones/drone-2/stream' },
      lastSeen: new Date().toISOString(),
      createdAt: new Date().toISOString()
    },
    {
      id: 'drone-3',
      name: 'Tello EDU - Gamma', 
      model: 'Tello EDU',
      serial_number: 'TELLO-003',
      status: 'low_battery',
      battery: 15,
      altitude: 0,
      temperature: 22,
      signal_strength: 70,
      flight_time: 0,
      position: { x: 0, y: 0, z: 0 },
      camera: { isStreaming: false, resolution: '720p', fps: 30 },
      lastSeen: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      createdAt: new Date().toISOString()
    },
    {
      id: 'drone-4',
      name: 'Tello EDU - Delta',
      model: 'Tello EDU', 
      serial_number: 'TELLO-004',
      status: 'disconnected',
      battery: 0,
      altitude: 0,
      temperature: 20,
      signal_strength: 0,
      flight_time: 0,
      position: { x: 0, y: 0, z: 0 },
      camera: { isStreaming: false, resolution: '720p', fps: 30 },
      lastSeen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      createdAt: new Date().toISOString()
    }
  ]

  // Filtered and sorted drones
  const filteredDrones = useMemo(() => {
    let filtered = drones.filter(drone => {
      const matchesSearch = searchTerm === '' || 
        drone.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        drone.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
        drone.serial_number.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesStatus = statusFilter === 'all' || drone.status === statusFilter
      
      return matchesSearch && matchesStatus
    })

    // Sort
    filtered.sort((a, b) => {
      let aValue: any = a[sortBy]
      let bValue: any = b[sortBy]
      
      if (sortBy === 'lastSeen') {
        aValue = new Date(aValue).getTime()
        bValue = new Date(bValue).getTime()
      }
      
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
      }
      
      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

    return filtered
  }, [drones, searchTerm, statusFilter, sortBy, sortOrder])

  // Paginated drones
  const paginatedDrones = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
    return filteredDrones.slice(startIndex, startIndex + ITEMS_PER_PAGE)
  }, [filteredDrones, currentPage])

  const totalPages = Math.ceil(filteredDrones.length / ITEMS_PER_PAGE)

  useEffect(() => {
    loadDrones()
  }, [])

  const loadDrones = async () => {
    try {
      setLoading(true)
      // In a real app, this would be: const data = await droneApi.getDrones()
      // For now, use mock data
      setDrones(mockDrones)
    } catch (error) {
      showNotification('ドローンデータの取得に失敗しました', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleScanNetwork = async () => {
    try {
      showNotification('ネットワークをスキャンしています...', 'info')
      // Simulate network scan
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      const foundDrones = Math.floor(Math.random() * 3) + 1
      showNotification(`${foundDrones}台の新しいドローンが見つかりました！`, 'success')
      
      return Array.from({ length: foundDrones }, (_, i) => ({
        name: `Tello EDU - New${i + 1}`,
        model: 'Tello EDU',
        serial_number: `TELLO-NEW-${String(i + 1).padStart(3, '0')}`,
        ip_address: `192.168.1.${100 + i}`
      }))
    } catch (error) {
      showNotification('ネットワークスキャンに失敗しました', 'error')
      return []
    }
  }

  const handleAddDrone = async (data: any) => {
    try {
      const newDrone: Drone = {
        id: `drone-${Date.now()}`,
        name: data.name,
        model: data.model,
        serial_number: data.serial_number,
        status: 'disconnected',
        battery: 0,
        altitude: 0,
        temperature: 20,
        signal_strength: 0,
        flight_time: 0,
        position: { x: 0, y: 0, z: 0 },
        camera: { isStreaming: false, resolution: '720p', fps: 30 },
        lastSeen: new Date().toISOString(),
        createdAt: new Date().toISOString()
      }
      
      setDrones(prev => [...prev, newDrone])
      showNotification(`ドローン "${data.name}" が追加されました`, 'success')
    } catch (error) {
      throw new Error('ドローンの追加に失敗しました')
    }
  }

  const handleDroneAction = async (droneId: string, action: string, ...args: any[]) => {
    try {
      const drone = drones.find(d => d.id === droneId)
      if (!drone) return

      switch (action) {
        case 'connect':
          setDrones(prev => prev.map(d => 
            d.id === droneId ? { ...d, status: 'connected' as DroneStatus } : d
          ))
          showNotification(`${drone.name} に接続しました`, 'success')
          break
          
        case 'disconnect':
          setDrones(prev => prev.map(d => 
            d.id === droneId ? { ...d, status: 'disconnected' as DroneStatus } : d
          ))
          showNotification(`${drone.name} を切断しました`, 'info')
          break
          
        case 'takeoff':
          setDrones(prev => prev.map(d => 
            d.id === droneId ? { ...d, status: 'flying' as DroneStatus, altitude: 50 } : d
          ))
          showNotification(`${drone.name} が離陸しました`, 'success')
          break
          
        case 'land':
          setDrones(prev => prev.map(d => 
            d.id === droneId ? { ...d, status: 'connected' as DroneStatus, altitude: 0 } : d
          ))
          showNotification(`${drone.name} が着陸しました`, 'success')
          break
          
        case 'emergency_stop':
          setDrones(prev => prev.map(d => 
            d.id === droneId ? { ...d, status: 'connected' as DroneStatus, altitude: 0 } : d
          ))
          showNotification(`${drone.name} を緊急停止しました`, 'warning')
          break
          
        case 'start_stream':
          setDrones(prev => prev.map(d => 
            d.id === droneId ? { 
              ...d, 
              camera: { ...d.camera!, isStreaming: true, streamUrl: `/api/drones/${droneId}/stream` }
            } : d
          ))
          showNotification(`${drone.name} のカメラストリームを開始しました`, 'success')
          break
          
        case 'stop_stream':
          setDrones(prev => prev.map(d => 
            d.id === droneId ? { 
              ...d, 
              camera: { ...d.camera!, isStreaming: false, streamUrl: undefined }
            } : d
          ))
          showNotification(`${drone.name} のカメラストリームを停止しました`, 'info')
          break
          
        case 'delete':
          setDrones(prev => prev.filter(d => d.id !== droneId))
          showNotification(`${drone.name} を削除しました`, 'info')
          break
      }
    } catch (error) {
      showNotification(`操作に失敗しました: ${error}`, 'error')
    }
  }

  const handleOpenControl = (drone: Drone) => {
    setSelectedDrone(drone)
    setControlModalOpen(true)
  }

  const handleOpenCamera = (drone: Drone) => {
    setSelectedDrone(drone)
    setCameraModalOpen(true)
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>読み込み中...</Typography>
      </Box>
    )
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          ドローン管理
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            startIcon={<Search />}
            onClick={handleScanNetwork}
          >
            ドローン検索
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddModalOpen(true)}
          >
            ドローン追加
          </Button>
        </Stack>
      </Box>

      {/* Stats */}
      <Box mb={3}>
        <DroneStats drones={drones} />
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Search and Filters */}
      <Box mb={3}>
        <DroneSearch
          searchTerm={searchTerm}
          statusFilter={statusFilter}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSearchChange={setSearchTerm}
          onStatusFilterChange={setStatusFilter}
          onSortChange={(field, order) => {
            setSortBy(field as any)
            setSortOrder(order)
          }}
          onRefresh={loadDrones}
          totalResults={filteredDrones.length}
        />
      </Box>

      {/* Drone Grid */}
      {filteredDrones.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              ドローンが見つかりません
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              検索条件を変更するか、新しいドローンを追加してください
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setAddModalOpen(true)}
            >
              ドローン追加
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          <Grid container spacing={3}>
            {paginatedDrones.map((drone) => (
              <Grid item xs={12} sm={6} lg={4} key={drone.id}>
                <DroneCard
                  drone={drone}
                  onConnect={(id) => handleDroneAction(id, 'connect')}
                  onDisconnect={(id) => handleDroneAction(id, 'disconnect')}
                  onTakeoff={(id) => handleDroneAction(id, 'takeoff')}
                  onLand={(id) => handleDroneAction(id, 'land')}
                  onEmergencyStop={(id) => handleDroneAction(id, 'emergency_stop')}
                  onStartStream={(id) => handleDroneAction(id, 'start_stream')}
                  onStopStream={(id) => handleDroneAction(id, 'stop_stream')}
                  onControl={() => handleOpenControl(drone)}
                  onDelete={(id) => handleDroneAction(id, 'delete')}
                />
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination
                count={totalPages}
                page={currentPage}
                onChange={(_, page) => setCurrentPage(page)}
                color="primary"
                size="large"
              />
            </Box>
          )}
        </>
      )}

      {/* Add Drone Modal */}
      <AddDroneModal
        open={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onSubmit={handleAddDrone}
        onScanNetwork={handleScanNetwork}
      />

      {/* Control Modal */}
      <Dialog
        open={controlModalOpen}
        onClose={() => setControlModalOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>ドローン制御</DialogTitle>
        <DialogContent>
          {selectedDrone && (
            <DroneControl
              drone={selectedDrone}
              onTakeoff={() => handleDroneAction(selectedDrone.id, 'takeoff')}
              onLand={() => handleDroneAction(selectedDrone.id, 'land')}
              onEmergencyStop={() => handleDroneAction(selectedDrone.id, 'emergency_stop')}
              onMove={(direction, distance) => {
                // Handle movement
                showNotification(`${selectedDrone.name}: ${direction}に${distance}cm移動`, 'info')
              }}
              onRotate={(direction, angle) => {
                // Handle rotation
                showNotification(`${selectedDrone.name}: ${direction}に${angle}度回転`, 'info')
              }}
              onSetSpeed={(speed) => {
                // Handle speed change
                showNotification(`${selectedDrone.name}: 速度を${speed}%に設定`, 'info')
              }}
              onReturnHome={() => {
                // Handle return home
                showNotification(`${selectedDrone.name}: ホームに戻る`, 'info')
              }}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Camera Modal */}
      <Dialog
        open={cameraModalOpen}
        onClose={() => setCameraModalOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>カメラ映像</DialogTitle>
        <DialogContent>
          {selectedDrone && (
            <CameraStream
              drone={selectedDrone}
              onStartStream={() => handleDroneAction(selectedDrone.id, 'start_stream')}
              onStopStream={() => handleDroneAction(selectedDrone.id, 'stop_stream')}
              onTakePhoto={() => {
                showNotification(`${selectedDrone.name}: 写真を撮影しました`, 'success')
              }}
              onUpdateSettings={(settings) => {
                showNotification(`${selectedDrone.name}: カメラ設定を更新しました`, 'info')
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  )
}