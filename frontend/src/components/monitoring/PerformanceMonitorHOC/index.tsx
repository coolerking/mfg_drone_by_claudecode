import React, { ComponentType, useEffect, useRef, useState, useCallback } from 'react'
import { Box, Alert, Collapse, IconButton, Typography, Chip } from '@mui/material'
import { Speed, ExpandMore, ExpandLess, Warning } from '@mui/icons-material'
import { PerformanceManager, measureRenderTime, FrameRateMonitor } from '../../../utils/performance'
import { useMonitoring } from '../../../utils/monitoring'

interface PerformanceData {
  renderTime: number
  renderCount: number
  averageRenderTime: number
  memoryUsage?: MemoryInfo
  frameRate?: number
  isSlowRender: boolean
  componentName: string
  timestamp: number
}

interface PerformanceMonitorOptions {
  enabled?: boolean
  showAlert?: boolean
  slowRenderThreshold?: number
  memoryThreshold?: number
  frameRateThreshold?: number
  logToConsole?: boolean
  sendMetrics?: boolean
}

interface PerformanceAlertProps {
  data: PerformanceData
  onDismiss: () => void
  show: boolean
}

const PerformanceAlert: React.FC<PerformanceAlertProps> = ({ data, onDismiss, show }) => {
  const [expanded, setExpanded] = useState(false)

  const getAlertSeverity = () => {
    if (data.renderTime > 100) return 'error'
    if (data.renderTime > 50 || (data.frameRate && data.frameRate < 30)) return 'warning'
    return 'info'
  }

  const getPerformanceIssues = () => {
    const issues = []
    
    if (data.renderTime > 100) {
      issues.push('レンダリング時間が100msを超えています')
    }
    if (data.renderTime > 50) {
      issues.push('レンダリング時間が50msを超えています')
    }
    if (data.frameRate && data.frameRate < 30) {
      issues.push('フレームレートが30fps以下です')
    }
    if (data.memoryUsage && data.memoryUsage.usedJSHeapSize > 50 * 1024 * 1024) {
      issues.push('メモリ使用量が50MBを超えています')
    }
    
    return issues
  }

  const issues = getPerformanceIssues()

  if (!show || issues.length === 0) return null

  return (
    <Collapse in={show}>
      <Alert
        severity={getAlertSeverity()}
        sx={{ mb: 2 }}
        action={
          <Box display="flex" alignItems="center" gap={1}>
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
              color="inherit"
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
            <IconButton size="small" onClick={onDismiss} color="inherit">
              ×
            </IconButton>
          </Box>
        }
      >
        <Typography variant="body2">
          {data.componentName}でパフォーマンス問題を検出しました
        </Typography>
        
        <Collapse in={expanded}>
          <Box mt={2}>
            <Typography variant="body2" gutterBottom>
              <strong>検出された問題:</strong>
            </Typography>
            {issues.map((issue, index) => (
              <Typography key={index} variant="body2" color="text.secondary">
                • {issue}
              </Typography>
            ))}
            
            <Box mt={2} display="flex" flexWrap="wrap" gap={1}>
              <Chip 
                size="small" 
                label={`レンダリング: ${data.renderTime.toFixed(1)}ms`}
                color={data.renderTime > 50 ? 'error' : 'default'}
              />
              {data.frameRate && (
                <Chip 
                  size="small" 
                  label={`FPS: ${data.frameRate.toFixed(1)}`}
                  color={data.frameRate < 30 ? 'error' : 'default'}
                />
              )}
              {data.memoryUsage && (
                <Chip 
                  size="small" 
                  label={`メモリ: ${(data.memoryUsage.usedJSHeapSize / 1024 / 1024).toFixed(1)}MB`}
                  color={data.memoryUsage.usedJSHeapSize > 50 * 1024 * 1024 ? 'error' : 'default'}
                />
              )}
            </Box>
          </Box>
        </Collapse>
      </Alert>
    </Collapse>
  )
}

export function withPerformanceMonitor<P extends object>(
  WrappedComponent: ComponentType<P>,
  options: PerformanceMonitorOptions = {}
) {
  const {
    enabled = __DEV__ || false,
    showAlert = __DEV__ || false,
    slowRenderThreshold = 50,
    memoryThreshold = 50 * 1024 * 1024, // 50MB
    frameRateThreshold = 30,
    logToConsole = __DEV__ || false,
    sendMetrics = true
  } = options

  const componentName = WrappedComponent.displayName || WrappedComponent.name || 'Component'

  const PerformanceMonitoredComponent: React.FC<P> = (props) => {
    const { reportMetric } = useMonitoring()
    const renderTimesRef = useRef<number[]>([])
    const frameMonitorRef = useRef<FrameRateMonitor | null>(null)
    const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null)
    const [showPerformanceAlert, setShowPerformanceAlert] = useState(false)
    const mountTimeRef = useRef<number>(Date.now())

    // Initialize frame rate monitor
    useEffect(() => {
      if (!enabled) return

      frameMonitorRef.current = new FrameRateMonitor()
      frameMonitorRef.current.start()

      return () => {
        if (frameMonitorRef.current) {
          frameMonitorRef.current.stop()
        }
      }
    }, [])

    // Performance measurement wrapper
    const measureComponentRender = useCallback(() => {
      if (!enabled) return

      const { result, duration } = measureRenderTime(
        `${componentName}-render`,
        () => null // We'll measure the actual render through useEffect
      )

      renderTimesRef.current.push(duration)
      
      // Keep only last 10 render times
      if (renderTimesRef.current.length > 10) {
        renderTimesRef.current.shift()
      }

      const averageRenderTime = renderTimesRef.current.reduce((a, b) => a + b, 0) / renderTimesRef.current.length
      const memoryUsage = PerformanceManager.getMemoryUsage()
      const frameRate = frameMonitorRef.current?.getAverageFPS()
      const isSlowRender = duration > slowRenderThreshold

      const data: PerformanceData = {
        renderTime: duration,
        renderCount: renderTimesRef.current.length,
        averageRenderTime,
        memoryUsage: memoryUsage || undefined,
        frameRate,
        isSlowRender,
        componentName,
        timestamp: Date.now()
      }

      setPerformanceData(data)

      // Show alert for performance issues
      if (showAlert && (isSlowRender || (frameRate && frameRate < frameRateThreshold))) {
        setShowPerformanceAlert(true)
      }

      // Log to console in development
      if (logToConsole) {
        if (isSlowRender) {
          console.warn(`🐌 Slow render in ${componentName}:`, {
            renderTime: `${duration.toFixed(2)}ms`,
            averageRenderTime: `${averageRenderTime.toFixed(2)}ms`,
            renderCount: renderTimesRef.current.length,
            frameRate: frameRate ? `${frameRate.toFixed(1)}fps` : 'N/A',
            memoryUsage: memoryUsage ? `${(memoryUsage.usedJSHeapSize / 1024 / 1024).toFixed(1)}MB` : 'N/A'
          })
        } else {
          console.log(`⚡ ${componentName} render:`, `${duration.toFixed(2)}ms`)
        }
      }

      // Send metrics to monitoring service
      if (sendMetrics) {
        reportMetric('component_render_time', duration, {
          component: componentName,
          isSlowRender,
          frameRate: frameRate || 0,
          memoryUsage: memoryUsage?.usedJSHeapSize || 0
        })

        if (isSlowRender) {
          reportMetric('slow_render_detected', 1, {
            component: componentName,
            renderTime: duration,
            threshold: slowRenderThreshold
          })
        }
      }
    }, [componentName, enabled, showAlert, slowRenderThreshold, frameRateThreshold, logToConsole, sendMetrics, reportMetric])

    // Measure render on every update
    useEffect(() => {
      measureComponentRender()
    })

    // Log component lifecycle metrics
    useEffect(() => {
      if (!enabled || !sendMetrics) return

      const mountTime = Date.now() - mountTimeRef.current
      
      reportMetric('component_mount_time', mountTime, {
        component: componentName
      })

      return () => {
        const unmountTime = Date.now()
        const totalLifetime = unmountTime - mountTimeRef.current
        
        reportMetric('component_lifetime', totalLifetime, {
          component: componentName,
          renderCount: renderTimesRef.current.length,
          averageRenderTime: renderTimesRef.current.length > 0 
            ? renderTimesRef.current.reduce((a, b) => a + b, 0) / renderTimesRef.current.length 
            : 0
        })
      }
    }, [componentName, enabled, sendMetrics, reportMetric])

    if (!enabled) {
      return <WrappedComponent {...props} />
    }

    return (
      <>
        {performanceData && (
          <PerformanceAlert
            data={performanceData}
            onDismiss={() => setShowPerformanceAlert(false)}
            show={showPerformanceAlert}
          />
        )}
        <WrappedComponent {...props} />
      </>
    )
  }

  PerformanceMonitoredComponent.displayName = `withPerformanceMonitor(${componentName})`

  return PerformanceMonitoredComponent
}

// Hook for manual performance tracking within components
export const usePerformanceTracking = (componentName?: string) => {
  const { reportMetric } = useMonitoring()
  const renderCountRef = useRef(0)
  const mountTimeRef = useRef(Date.now())

  const trackRender = useCallback((customData?: Record<string, any>) => {
    renderCountRef.current++
    const renderTime = performance.now()

    reportMetric('manual_render_track', renderTime, {
      component: componentName || 'Unknown',
      renderCount: renderCountRef.current,
      ...customData
    })
  }, [componentName, reportMetric])

  const trackUserAction = useCallback((action: string, duration?: number) => {
    reportMetric('user_action_performance', duration || 0, {
      component: componentName || 'Unknown',
      action,
      renderCount: renderCountRef.current
    })
  }, [componentName, reportMetric])

  const trackAsyncOperation = useCallback((operationName: string, startTime: number, endTime: number) => {
    const duration = endTime - startTime
    
    reportMetric('async_operation_performance', duration, {
      component: componentName || 'Unknown',
      operation: operationName,
      renderCount: renderCountRef.current
    })
  }, [componentName, reportMetric])

  return {
    trackRender,
    trackUserAction,
    trackAsyncOperation,
    renderCount: renderCountRef.current,
    componentLifetime: Date.now() - mountTimeRef.current
  }
}

// Performance debugging component
export const PerformanceDebugger: React.FC<{
  component: ComponentType<any>
  enabled?: boolean
}> = ({ component, enabled = __DEV__ }) => {
  const [performanceLog, setPerformanceLog] = useState<PerformanceData[]>([])
  const componentName = component.displayName || component.name || 'Component'

  if (!enabled) return null

  return (
    <Box sx={{ 
      position: 'fixed', 
      bottom: 16, 
      left: 16, 
      zIndex: 9999,
      backgroundColor: 'rgba(0,0,0,0.8)',
      color: 'white',
      p: 2,
      borderRadius: 1,
      maxWidth: 300,
      fontSize: '0.75rem'
    }}>
      <Box display="flex" alignItems="center" gap={1} mb={1}>
        <Speed fontSize="small" />
        <Typography variant="caption">
          {componentName} パフォーマンス
        </Typography>
      </Box>
      
      {performanceLog.slice(-5).map((data, index) => (
        <Typography key={index} variant="caption" display="block">
          レンダリング{index + 1}: {data.renderTime.toFixed(1)}ms
        </Typography>
      ))}
    </Box>
  )
}

export default withPerformanceMonitor