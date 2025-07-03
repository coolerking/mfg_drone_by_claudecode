import { useCallback } from 'react'
import { useDispatch } from 'react-redux'
import type { AppDispatch } from '../store'
import { enqueueSnackbar, closeSnackbar, OptionsObject } from 'notistack'
import type { NotificationOptions, NotificationType } from '../types/common'
import { NOTIFICATION_CONFIG } from '../utils/constants'

// Custom hook for managing notifications
export const useNotification = () => {
  const dispatch = useDispatch<AppDispatch>()

  // Show notification with specified type and message
  const showNotification = useCallback((
    message: string,
    type: NotificationType = 'info',
    options?: Partial<NotificationOptions>
  ) => {
    const defaultDuration = (() => {
      switch (type) {
        case 'success':
          return NOTIFICATION_CONFIG.SUCCESS_DURATION
        case 'error':
          return NOTIFICATION_CONFIG.ERROR_DURATION
        case 'warning':
          return NOTIFICATION_CONFIG.WARNING_DURATION
        default:
          return NOTIFICATION_CONFIG.DEFAULT_DURATION
      }
    })()

    const snackbarOptions: OptionsObject = {
      variant: type,
      autoHideDuration: options?.persistent ? null : (options?.duration || defaultDuration),
      persist: options?.persistent || false,
      preventDuplicate: true,
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
      ...options,
    }

    return enqueueSnackbar(message, snackbarOptions)
  }, [])

  // Convenience methods for different notification types
  const showSuccess = useCallback((
    message: string,
    options?: Partial<NotificationOptions>
  ) => {
    return showNotification(message, 'success', options)
  }, [showNotification])

  const showError = useCallback((
    message: string,
    options?: Partial<NotificationOptions>
  ) => {
    return showNotification(message, 'error', options)
  }, [showNotification])

  const showWarning = useCallback((
    message: string,
    options?: Partial<NotificationOptions>
  ) => {
    return showNotification(message, 'warning', options)
  }, [showNotification])

  const showInfo = useCallback((
    message: string,
    options?: Partial<NotificationOptions>
  ) => {
    return showNotification(message, 'info', options)
  }, [showNotification])

  // Close specific notification
  const closeNotification = useCallback((key?: string | number) => {
    closeSnackbar(key)
  }, [])

  // Close all notifications
  const closeAllNotifications = useCallback(() => {
    closeSnackbar()
  }, [])

  // Show notification based on API response
  const showApiResponse = useCallback((
    response: { success: boolean; message?: string; error?: string },
    successMessage?: string,
    errorMessage?: string
  ) => {
    if (response.success) {
      showSuccess(successMessage || response.message || '操作が成功しました')
    } else {
      showError(errorMessage || response.error || response.message || '操作に失敗しました')
    }
  }, [showSuccess, showError])

  // Show notification for errors with formatting
  const showErrorFromException = useCallback((
    error: any,
    fallbackMessage = 'エラーが発生しました'
  ) => {
    let message = fallbackMessage

    if (typeof error === 'string') {
      message = error
    } else if (error?.message) {
      message = error.message
    } else if (error?.response?.data?.message) {
      message = error.response.data.message
    } else if (error?.response?.data?.error) {
      message = error.response.data.error
    }

    return showError(message)
  }, [showError])

  // Show validation errors
  const showValidationErrors = useCallback((
    errors: Array<{ field: string; message: string }>,
    title = 'バリデーションエラー'
  ) => {
    if (errors.length === 1) {
      showError(errors[0].message)
    } else {
      const message = errors.map(err => `${err.field}: ${err.message}`).join('\n')
      showError(`${title}\n${message}`)
    }
  }, [showError])

  return {
    // Basic notification methods
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    
    // Notification management
    closeNotification,
    closeAllNotifications,
    
    // Specialized methods
    showApiResponse,
    showErrorFromException,
    showValidationErrors,
  }
}

// Hook for drone-specific notifications
export const useDroneNotifications = () => {
  const { showSuccess, showError, showWarning, showInfo } = useNotification()

  const showDroneConnected = useCallback((droneName: string) => {
    showSuccess(`ドローン "${droneName}" に接続しました`)
  }, [showSuccess])

  const showDroneDisconnected = useCallback((droneName: string) => {
    showInfo(`ドローン "${droneName}" から切断しました`)
  }, [showInfo])

  const showDroneError = useCallback((droneName: string, error: string) => {
    showError(`ドローン "${droneName}" でエラーが発生しました: ${error}`)
  }, [showError])

  const showBatteryLow = useCallback((droneName: string, batteryLevel: number) => {
    showWarning(`ドローン "${droneName}" のバッテリー残量が低下しています (${batteryLevel}%)`)
  }, [showWarning])

  const showBatteryCritical = useCallback((droneName: string, batteryLevel: number) => {
    showError(`ドローン "${droneName}" のバッテリー残量が危険レベルです (${batteryLevel}%)`, {
      persistent: true
    })
  }, [showError])

  const showCommandSent = useCallback((droneName: string, command: string) => {
    showSuccess(`ドローン "${droneName}" にコマンド "${command}" を送信しました`)
  }, [showSuccess])

  const showCommandFailed = useCallback((droneName: string, command: string, error: string) => {
    showError(`ドローン "${droneName}" のコマンド "${command}" が失敗しました: ${error}`)
  }, [showError])

  const showEmergencyLanding = useCallback((droneName: string) => {
    showError(`ドローン "${droneName}" が緊急着陸しました`, {
      persistent: true
    })
  }, [showError])

  return {
    showDroneConnected,
    showDroneDisconnected,
    showDroneError,
    showBatteryLow,
    showBatteryCritical,
    showCommandSent,
    showCommandFailed,
    showEmergencyLanding,
  }
}

// Hook for model training notifications
export const useTrainingNotifications = () => {
  const { showSuccess, showError, showWarning, showInfo } = useNotification()

  const showTrainingStarted = useCallback((modelName: string) => {
    showSuccess(`モデル "${modelName}" の学習を開始しました`)
  }, [showSuccess])

  const showTrainingCompleted = useCallback((modelName: string, accuracy?: number) => {
    const message = accuracy
      ? `モデル "${modelName}" の学習が完了しました (精度: ${(accuracy * 100).toFixed(1)}%)`
      : `モデル "${modelName}" の学習が完了しました`
    showSuccess(message)
  }, [showSuccess])

  const showTrainingFailed = useCallback((modelName: string, error: string) => {
    showError(`モデル "${modelName}" の学習が失敗しました: ${error}`)
  }, [showError])

  const showTrainingPaused = useCallback((modelName: string) => {
    showWarning(`モデル "${modelName}" の学習を一時停止しました`)
  }, [showWarning])

  const showTrainingResumed = useCallback((modelName: string) => {
    showInfo(`モデル "${modelName}" の学習を再開しました`)
  }, [showInfo])

  const showTrainingCancelled = useCallback((modelName: string) => {
    showWarning(`モデル "${modelName}" の学習をキャンセルしました`)
  }, [showWarning])

  return {
    showTrainingStarted,
    showTrainingCompleted,
    showTrainingFailed,
    showTrainingPaused,
    showTrainingResumed,
    showTrainingCancelled,
  }
}

// Hook for dataset notifications
export const useDatasetNotifications = () => {
  const { showSuccess, showError, showInfo } = useNotification()

  const showDatasetCreated = useCallback((datasetName: string) => {
    showSuccess(`データセット "${datasetName}" を作成しました`)
  }, [showSuccess])

  const showDatasetDeleted = useCallback((datasetName: string) => {
    showInfo(`データセット "${datasetName}" を削除しました`)
  }, [showInfo])

  const showImagesUploaded = useCallback((count: number, datasetName: string) => {
    showSuccess(`${count} 枚の画像をデータセット "${datasetName}" にアップロードしました`)
  }, [showSuccess])

  const showUploadFailed = useCallback((error: string) => {
    showError(`画像のアップロードに失敗しました: ${error}`)
  }, [showError])

  const showAutoLabelingStarted = useCallback((datasetName: string) => {
    showInfo(`データセット "${datasetName}" の自動ラベリングを開始しました`)
  }, [showInfo])

  const showAutoLabelingCompleted = useCallback((datasetName: string, labelCount: number) => {
    showSuccess(`データセット "${datasetName}" の自動ラベリングが完了しました (${labelCount} ラベル作成)`)
  }, [showSuccess])

  return {
    showDatasetCreated,
    showDatasetDeleted,
    showImagesUploaded,
    showUploadFailed,
    showAutoLabelingStarted,
    showAutoLabelingCompleted,
  }
}

// Hook for system notifications
export const useSystemNotifications = () => {
  const { showSuccess, showError, showWarning, showInfo } = useNotification()

  const showSystemOnline = useCallback(() => {
    showSuccess('システムがオンラインになりました')
  }, [showSuccess])

  const showSystemOffline = useCallback(() => {
    showError('システムがオフラインになりました', { persistent: true })
  }, [showError])

  const showHighCpuUsage = useCallback((usage: number) => {
    showWarning(`CPU使用率が高くなっています (${usage.toFixed(1)}%)`)
  }, [showWarning])

  const showHighMemoryUsage = useCallback((usage: number) => {
    showWarning(`メモリ使用率が高くなっています (${usage.toFixed(1)}%)`)
  }, [showWarning])

  const showDiskSpaceLow = useCallback((remaining: number) => {
    showWarning(`ディスク容量が不足しています (残り ${remaining.toFixed(1)}GB)`)
  }, [showWarning])

  const showMaintenanceMode = useCallback((message?: string) => {
    showInfo(message || 'システムはメンテナンスモードです', { persistent: true })
  }, [showInfo])

  return {
    showSystemOnline,
    showSystemOffline,
    showHighCpuUsage,
    showHighMemoryUsage,
    showDiskSpaceLow,
    showMaintenanceMode,
  }
}