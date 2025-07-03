import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '../index'
import { getStoredTokens } from '../../services/api/apiClient'

const baseQuery = fetchBaseQuery({
  baseUrl: '/api',
  prepareHeaders: (headers, { getState }) => {
    // Try to get token from Redux state first
    const tokens = (getState() as RootState).auth.tokens
    let accessToken = tokens?.accessToken

    // If not in Redux state, try to get from localStorage
    if (!accessToken) {
      const storedTokens = getStoredTokens()
      accessToken = storedTokens?.accessToken
    }

    if (accessToken) {
      headers.set('authorization', `Bearer ${accessToken}`)
    }
    
    headers.set('content-type', 'application/json')
    return headers
  },
})

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery,
  tagTypes: [
    'Auth',
    'Drone', 
    'DroneStatus',
    'DroneCommand',
    'Dataset', 
    'DatasetImage',
    'Model', 
    'TrainingJob',
    'ModelEvaluation',
    'System',
    'Alert',
    'ActivityLog',
    'Performance',
    'TrackingSession'
  ],
  endpoints: (builder) => ({
    // Auth endpoints
    getCurrentUser: builder.query<{ user: any }, void>({
      query: () => '/auth/me',
      providesTags: ['Auth'],
    }),

    // Drone endpoints
    getDrones: builder.query<any[], void>({
      query: () => '/drones',
      providesTags: ['Drone'],
    }),

    getDrone: builder.query<any, string>({
      query: (droneId) => `/drones/${droneId}`,
      providesTags: (result, error, droneId) => [{ type: 'Drone', id: droneId }],
    }),

    getDroneStatus: builder.query<any, string>({
      query: (droneId) => `/drones/${droneId}/status`,
      providesTags: (result, error, droneId) => [{ type: 'DroneStatus', id: droneId }],
    }),

    sendDroneCommand: builder.mutation<any, { droneId: string; command: any }>({
      query: ({ droneId, command }) => ({
        url: `/drones/${droneId}/command`,
        method: 'POST',
        body: command,
      }),
      invalidatesTags: (result, error, { droneId }) => [
        { type: 'DroneStatus', id: droneId },
        { type: 'Drone', id: droneId },
      ],
    }),

    // Dataset endpoints
    getDatasets: builder.query<any[], void>({
      query: () => '/vision/datasets',
      providesTags: ['Dataset'],
    }),

    getDataset: builder.query<any, string>({
      query: (datasetId) => `/vision/datasets/${datasetId}`,
      providesTags: (result, error, datasetId) => [{ type: 'Dataset', id: datasetId }],
    }),

    createDataset: builder.mutation<any, any>({
      query: (dataset) => ({
        url: '/vision/datasets',
        method: 'POST',
        body: dataset,
      }),
      invalidatesTags: ['Dataset'],
    }),

    updateDataset: builder.mutation<any, { datasetId: string; updates: any }>({
      query: ({ datasetId, updates }) => ({
        url: `/vision/datasets/${datasetId}`,
        method: 'PATCH',
        body: updates,
      }),
      invalidatesTags: (result, error, { datasetId }) => [
        { type: 'Dataset', id: datasetId },
        'Dataset',
      ],
    }),

    deleteDataset: builder.mutation<any, string>({
      query: (datasetId) => ({
        url: `/vision/datasets/${datasetId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Dataset'],
    }),

    getDatasetImages: builder.query<any, { datasetId: string; page?: number; limit?: number; labeled?: boolean }>({
      query: ({ datasetId, page = 1, limit = 20, labeled }) => ({
        url: `/vision/datasets/${datasetId}/images`,
        params: { page, limit, labeled },
      }),
      providesTags: (result, error, { datasetId }) => [
        { type: 'DatasetImage', id: datasetId },
      ],
    }),

    // Model endpoints
    getModels: builder.query<any[], void>({
      query: () => '/models',
      providesTags: ['Model'],
    }),

    getModel: builder.query<any, string>({
      query: (modelId) => `/models/${modelId}`,
      providesTags: (result, error, modelId) => [{ type: 'Model', id: modelId }],
    }),

    createModel: builder.mutation<any, any>({
      query: (model) => ({
        url: '/models',
        method: 'POST',
        body: model,
      }),
      invalidatesTags: ['Model'],
    }),

    startTraining: builder.mutation<any, { modelName: string; config: any }>({
      query: ({ modelName, config }) => ({
        url: '/models/train',
        method: 'POST',
        body: { name: modelName, config },
      }),
      invalidatesTags: ['Model', 'TrainingJob'],
    }),

    getTrainingJobs: builder.query<any[], string | undefined>({
      query: (modelId) => ({
        url: '/models/training',
        params: modelId ? { model_id: modelId } : {},
      }),
      providesTags: ['TrainingJob'],
    }),

    // Dashboard endpoints
    getDashboardStats: builder.query<any, void>({
      query: () => '/dashboard/stats',
      providesTags: ['System'],
    }),

    getSystemStatus: builder.query<any, void>({
      query: () => '/dashboard/system-status',
      providesTags: ['System'],
    }),

    getPerformanceMetrics: builder.query<any[], { timeRange?: string; interval?: string }>({
      query: ({ timeRange = '24h', interval = '5m' }) => ({
        url: '/dashboard/metrics',
        params: { time_range: timeRange, interval },
      }),
      providesTags: ['Performance'],
    }),

    getAlerts: builder.query<any, { page?: number; limit?: number; severity?: string; dismissed?: boolean }>({
      query: ({ page = 1, limit = 20, severity, dismissed }) => ({
        url: '/dashboard/alerts',
        params: { page, limit, severity, dismissed },
      }),
      providesTags: ['Alert'],
    }),

    dismissAlert: builder.mutation<any, string>({
      query: (alertId) => ({
        url: `/dashboard/alerts/${alertId}/dismiss`,
        method: 'POST',
      }),
      invalidatesTags: ['Alert'],
    }),

    getActivityLogs: builder.query<any, { page?: number; limit?: number; filter?: any }>({
      query: ({ page = 1, limit = 50, filter }) => ({
        url: '/dashboard/activity',
        params: { page, limit, ...filter },
      }),
      providesTags: ['ActivityLog'],
    }),
  }),
})

export const {
  // Auth hooks
  useGetCurrentUserQuery,

  // Drone hooks
  useGetDronesQuery,
  useGetDroneQuery,
  useGetDroneStatusQuery,
  useSendDroneCommandMutation,

  // Dataset hooks
  useGetDatasetsQuery,
  useGetDatasetQuery,
  useCreateDatasetMutation,
  useUpdateDatasetMutation,
  useDeleteDatasetMutation,
  useGetDatasetImagesQuery,

  // Model hooks
  useGetModelsQuery,
  useGetModelQuery,
  useCreateModelMutation,
  useStartTrainingMutation,
  useGetTrainingJobsQuery,

  // Dashboard hooks
  useGetDashboardStatsQuery,
  useGetSystemStatusQuery,
  useGetPerformanceMetricsQuery,
  useGetAlertsQuery,
  useDismissAlertMutation,
  useGetActivityLogsQuery,
} = apiSlice