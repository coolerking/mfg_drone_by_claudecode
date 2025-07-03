import { z } from 'zod'

// Common validation schemas
export const emailSchema = z.string().email('有効なメールアドレスを入力してください')

export const passwordSchema = z
  .string()
  .min(8, 'パスワードは8文字以上である必要があります')
  .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, '英大文字、英小文字、数字を含む必要があります')

export const usernameSchema = z
  .string()
  .min(3, 'ユーザー名は3文字以上である必要があります')
  .max(20, 'ユーザー名は20文字以下である必要があります')
  .regex(/^[a-zA-Z0-9_-]+$/, '英数字、アンダースコア、ハイフンのみ使用可能です')

// Drone validation schemas
export const droneIdSchema = z
  .string()
  .regex(/^[a-zA-Z0-9_-]+$/, 'ドローンIDは英数字、アンダースコア、ハイフンのみ使用可能です')

export const droneCommandSchema = z.object({
  type: z.enum(['takeoff', 'land', 'move', 'rotate', 'set_speed', 'emergency']),
  parameters: z.object({
    direction: z.enum(['up', 'down', 'left', 'right', 'forward', 'back', 'clockwise', 'counter_clockwise']).optional(),
    distance: z.number().min(20).max(500).optional(),
    angle: z.number().min(1).max(360).optional(),
    speed: z.number().min(10).max(100).optional()
  }).optional()
})

export const coordinateSchema = z.object({
  x: z.number().finite(),
  y: z.number().finite(),
  z: z.number().min(0).max(120) // Drone height limit
})

export const batteryLevelSchema = z.number().min(0).max(100)

// Dataset validation schemas
export const datasetNameSchema = z
  .string()
  .min(1, 'データセット名は必須です')
  .max(100, 'データセット名は100文字以下である必要があります')
  .regex(/^[a-zA-Z0-9_\-\s]+$/, '英数字、アンダースコア、ハイフン、スペースのみ使用可能です')

export const imageFileSchema = z
  .instanceof(File)
  .refine((file) => file.size <= 10 * 1024 * 1024, 'ファイルサイズは10MB以下である必要があります')
  .refine(
    (file) => ['image/jpeg', 'image/png', 'image/webp'].includes(file.type),
    'JPEG、PNG、WebP形式のみサポートされています'
  )

export const bboxSchema = z.object({
  x: z.number().min(0),
  y: z.number().min(0),
  width: z.number().min(1),
  height: z.number().min(1)
})

export const labelSchema = z.object({
  class_name: z.string().min(1, 'クラス名は必須です'),
  bbox: bboxSchema,
  confidence: z.number().min(0).max(1).optional(),
  verified: z.boolean().optional()
})

// Model validation schemas
export const modelNameSchema = z
  .string()
  .min(1, 'モデル名は必須です')
  .max(100, 'モデル名は100文字以下である必要があります')
  .regex(/^[a-zA-Z0-9_\-\s]+$/, '英数字、アンダースコア、ハイフン、スペースのみ使用可能です')

export const trainingConfigSchema = z.object({
  dataset_id: z.string().min(1, 'データセットIDは必須です'),
  validation_dataset_id: z.string().optional(),
  model_type: z.enum(['yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x']),
  epochs: z.number().min(1).max(1000),
  batch_size: z.number().min(1).max(64),
  learning_rate: z.number().min(0.0001).max(1),
  image_size: z.number().min(320).max(1280),
  patience: z.number().min(1).max(100),
  save_period: z.number().min(1).max(50),
  augment: z.boolean(),
  mosaic: z.boolean(),
  mixup: z.boolean(),
  copy_paste: z.boolean()
})

export const confidenceThresholdSchema = z.number().min(0).max(1)
export const iouThresholdSchema = z.number().min(0).max(1)

// Form validation functions
export interface ValidationResult {
  isValid: boolean
  errors: Array<{
    field: string
    message: string
  }>
}

export const validateForm = <T>(
  data: T,
  schema: z.ZodSchema<T>
): ValidationResult => {
  try {
    schema.parse(data)
    return { isValid: true, errors: [] }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        isValid: false,
        errors: error.errors.map((err) => ({
          field: err.path.join('.'),
          message: err.message
        }))
      }
    }
    return {
      isValid: false,
      errors: [{ field: 'unknown', message: 'バリデーションエラーが発生しました' }]
    }
  }
}

// Input sanitization
export const sanitizeInput = (input: string): string => {
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/['"]/g, '') // Remove quotes
    .slice(0, 1000) // Limit length
}

export const sanitizeFilename = (filename: string): string => {
  return filename
    .replace(/[^a-zA-Z0-9._-]/g, '_')
    .replace(/_{2,}/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 255)
}

// Drone-specific validation
export const validateDroneCommand = (
  droneId: string,
  command: any,
  droneStatus?: string
): ValidationResult => {
  // Validate drone ID
  const droneIdResult = droneIdSchema.safeParse(droneId)
  if (!droneIdResult.success) {
    return {
      isValid: false,
      errors: [{ field: 'droneId', message: 'Invalid drone ID' }]
    }
  }

  // Validate command structure
  const commandResult = droneCommandSchema.safeParse(command)
  if (!commandResult.success) {
    return {
      isValid: false,
      errors: commandResult.error.errors.map((err) => ({
        field: err.path.join('.'),
        message: err.message
      }))
    }
  }

  // Business logic validation
  const errors: Array<{ field: string; message: string }> = []

  if (command.type === 'takeoff' && droneStatus === 'flying') {
    errors.push({ field: 'command', message: 'ドローンは既に飛行中です' })
  }

  if (command.type === 'land' && droneStatus !== 'flying') {
    errors.push({ field: 'command', message: 'ドローンは飛行中ではありません' })
  }

  if (['move', 'rotate'].includes(command.type) && droneStatus !== 'flying') {
    errors.push({ field: 'command', message: '移動コマンドは飛行中のみ実行可能です' })
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

// Dataset validation
export const validateImageFile = (file: File): ValidationResult => {
  const result = imageFileSchema.safeParse(file)
  if (!result.success) {
    return {
      isValid: false,
      errors: result.error.errors.map((err) => ({
        field: 'file',
        message: err.message
      }))
    }
  }
  return { isValid: true, errors: [] }
}

export const validateImageFiles = (files: File[]): ValidationResult => {
  if (files.length === 0) {
    return {
      isValid: false,
      errors: [{ field: 'files', message: '少なくとも1つの画像ファイルを選択してください' }]
    }
  }

  if (files.length > 100) {
    return {
      isValid: false,
      errors: [{ field: 'files', message: '一度にアップロードできるファイルは100個までです' }]
    }
  }

  const errors: Array<{ field: string; message: string }> = []
  
  files.forEach((file, index) => {
    const result = validateImageFile(file)
    if (!result.isValid) {
      errors.push(...result.errors.map(err => ({
        ...err,
        field: `files[${index}]`
      })))
    }
  })

  return {
    isValid: errors.length === 0,
    errors
  }
}

// Coordinate validation for tracking
export const validateTrackingBounds = (
  bbox: { x: number; y: number; width: number; height: number },
  imageSize: { width: number; height: number }
): ValidationResult => {
  const errors: Array<{ field: string; message: string }> = []

  if (bbox.x < 0 || bbox.y < 0) {
    errors.push({ field: 'bbox', message: 'バウンディングボックスの座標は0以上である必要があります' })
  }

  if (bbox.x + bbox.width > imageSize.width) {
    errors.push({ field: 'bbox', message: 'バウンディングボックスが画像の幅を超えています' })
  }

  if (bbox.y + bbox.height > imageSize.height) {
    errors.push({ field: 'bbox', message: 'バウンディングボックスが画像の高さを超えています' })
  }

  if (bbox.width < 10 || bbox.height < 10) {
    errors.push({ field: 'bbox', message: 'バウンディングボックスのサイズが小さすぎます（最小10x10）' })
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

// Export validation schema types for use in components
export type DroneCommandType = z.infer<typeof droneCommandSchema>
export type TrainingConfigType = z.infer<typeof trainingConfigSchema>
export type LabelType = z.infer<typeof labelSchema>
export type BboxType = z.infer<typeof bboxSchema>