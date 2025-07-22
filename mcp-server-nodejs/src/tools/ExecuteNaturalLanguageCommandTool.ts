import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';
import { processCommand, initializeNLP, ParsedIntent, ConfidenceEvaluation } from '@/nlp/index.js';

/**
 * 自然言語コマンド実行ツール（高度版）
 * kuromoji.jsによる形態素解析と信頼度評価を使用した自然言語でのドローン制御コマンドを解析・実行する
 */
export class ExecuteNaturalLanguageCommandTool extends BaseTool {
  private isNLPInitialized = false;

  constructor(droneService: any) {
    super(droneService, 'execute_natural_language_command');
  }

  getDescription(): string {
    return 'Execute drone commands using advanced natural language processing with kuromoji.js morphological analysis. Supports comprehensive Japanese and English command recognition with confidence evaluation and safety checks.';
  }

  getInputSchema(): Record<string, unknown> {
    return {
      type: 'object',
      properties: {
        droneId: {
          type: 'string',
          description: 'The ID of the drone to control',
        },
        command: {
          type: 'string',
          description: 'Natural language command with advanced parsing support (e.g., "前に2m移動してから高画質で写真を撮影", "time to take off at 1.5m height", "緊急停止してください")',
        },
        language: {
          type: 'string',
          enum: ['en', 'ja', 'auto'],
          description: 'Language of the command (optional, default: auto-detect)',
          default: 'auto',
        },
        confidence_threshold: {
          type: 'number',
          minimum: 0.0,
          maximum: 1.0,
          description: 'Minimum confidence threshold for command execution (default: 0.7)',
          default: 0.7,
        },
        force_execution: {
          type: 'boolean',
          description: 'Force execution even if confidence is below threshold (use with caution)',
          default: false,
        },
        include_analysis: {
          type: 'boolean',
          description: 'Include detailed NLP analysis in the response',
          default: false,
        }
      },
      required: ['droneId', 'command'],
    };
  }

  async execute(args?: Record<string, unknown>): Promise<MCPToolResponse> {
    try {
      this.validateArgs(args, ['droneId', 'command']);
      const droneId = args!.droneId as string;
      const command = args!.command as string;
      const language = args!.language as string || 'auto';
      const confidenceThreshold = args!.confidence_threshold as number || 0.7;
      const forceExecution = args!.force_execution as boolean || false;
      const includeAnalysis = args!.include_analysis as boolean || false;
      
      logger.info(`Processing advanced NLP command for drone ${droneId}: "${command}"`);

      // NLPエンジンを初期化（初回のみ）
      if (!this.isNLPInitialized) {
        await initializeNLP();
        this.isNLPInitialized = true;
        logger.info('Advanced NLP engine initialized with kuromoji.js');
      }

      // ドローンの状態確認
      await this.validateAndGetDrone(droneId);

      // 高度なNLP処理でコマンドを解析
      const context = { drone_id: droneId };
      const nlpResult = await processCommand(command, context);

      const { intent, evaluation, isExecutable } = nlpResult;
      
      logger.info(`NLP Analysis - Action: ${intent.action}, Confidence: ${evaluation.overall_confidence.toFixed(3)}, Executable: ${isExecutable}`);

      // 信頼度チェック
      if (!forceExecution && evaluation.overall_confidence < confidenceThreshold) {
        const suggestionText = evaluation.suggestions.length > 0 
          ? `\n\n提案:\n${evaluation.suggestions.map((s: any) => `- ${s.suggestion}`).join('\n')}`
          : '';
        
        throw new Error(
          `Command confidence (${evaluation.overall_confidence.toFixed(3)}) is below threshold (${confidenceThreshold}).${suggestionText}\n\nUse 'force_execution: true' to execute anyway.`
        );
      }

      // 実行可能性チェック
      if (!forceExecution && !isExecutable) {
        const riskText = evaluation.risk_factors.length > 0
          ? `\nリスク要因: ${evaluation.risk_factors.join(', ')}`
          : '';
        
        const suggestionText = evaluation.suggestions.length > 0
          ? `\n提案:\n${evaluation.suggestions.map((s: any) => `- ${s.suggestion}`).join('\n')}`
          : '';
          
        throw new Error(
          `Command is not safe to execute.${riskText}${suggestionText}\n\nUse 'force_execution: true' to override safety checks.`
        );
      }

      // コマンドを実行
      const mappedAction = this.mapActionToServiceMethod(intent.action);
      const mappedParams = this.mapParametersToService(intent.parameters);

      logger.info(`Executing mapped action: ${mappedAction} with params:`, mappedParams);

      const result = await this.droneService.executeCommand(
        droneId,
        mappedAction,
        mappedParams
      );

      if (result.success) {
        let responseMessage = `Advanced NLP command executed successfully for drone '${droneId}': "${command}" → ${intent.action}`;
        
        if (evaluation.overall_confidence < 0.85) {
          responseMessage += ` (confidence: ${evaluation.overall_confidence.toFixed(3)})`;
        }
        
        responseMessage += `. ${result.message}`;

        // 分析情報を含める場合
        if (includeAnalysis) {
          const analysis = {
            original_command: command,
            parsed_action: intent.action,
            extracted_parameters: intent.parameters,
            confidence_scores: {
              overall: evaluation.overall_confidence,
              action: evaluation.action_confidence,
              parameter: evaluation.parameter_confidence,
              completeness: evaluation.completeness_score
            },
            quality_indicators: evaluation.quality_indicators,
            suggestions: evaluation.suggestions,
            risk_factors: evaluation.risk_factors,
            execution_safe: isExecutable
          };
          
          const analysisText = `\n\n--- NLP Analysis ---\n${JSON.stringify(analysis, null, 2)}`;
          return this.createSuccessResponse(responseMessage + analysisText);
        } else {
          return this.createSuccessResponse(responseMessage);
        }
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      logger.error('NLP command execution failed:', error);
      return this.createErrorResponse(error);
    }
  }

  /**
   * NLPエンジンのアクションをドローンサービスのメソッドにマップ
   */
  private mapActionToServiceMethod(action: string): string {
    const actionMap: Record<string, string> = {
      // Connection actions
      'connect': 'connect',
      'disconnect': 'disconnect',
      
      // Flight control actions
      'takeoff': 'takeoff',
      'land': 'land',
      'emergency': 'emergency_stop',
      'emergency_stop': 'emergency_stop',
      
      // Movement actions
      'move': 'move',
      'rotate': 'rotate',
      'altitude': 'change_altitude',
      
      // Camera actions
      'photo': 'take_photo',
      'take_photo': 'take_photo',
      'streaming': 'toggle_streaming',
      'start_streaming': 'start_streaming',
      'stop_streaming': 'stop_streaming',
      
      // Vision actions
      'detection': 'detect_objects',
      'detect_objects': 'detect_objects',
      'tracking': 'start_tracking',
      'start_tracking': 'start_tracking',
      'stop_tracking': 'stop_tracking',
      
      // System actions
      'status': 'get_status',
      'get_status': 'get_status',
      'health': 'health_check',
      'health_check': 'health_check'
    };

    return actionMap[action] || action;
  }

  /**
   * NLPエンジンのパラメータをドローンサービス用にマップ・変換
   */
  private mapParametersToService(parameters: Record<string, any>): Record<string, any> {
    const mappedParams: Record<string, any> = {};

    // Parameter mappings
    for (const [key, value] of Object.entries(parameters)) {
      switch (key) {
        case 'distance':
          // NLPエンジンはcm単位で返すが、サービスはm単位を期待する場合
          mappedParams['distance'] = value / 100; // cm to m
          break;
          
        case 'height':
          // 高度もm単位に変換
          mappedParams['altitude'] = value / 100; // cm to m
          break;
          
        case 'angle':
          // 角度はそのまま
          mappedParams['angle'] = value;
          break;
          
        case 'direction':
          // 方向はそのまま
          mappedParams['direction'] = value;
          break;
          
        case 'quality':
          // 画質設定
          mappedParams['quality'] = value;
          break;
          
        case 'filename':
          // ファイル名
          mappedParams['filename'] = value;
          break;
          
        case 'drone_id':
          // ドローンIDは除外（既にdroneIdとして処理済み）
          break;
          
        case 'immediate':
          // 緊急フラグ
          mappedParams['emergency'] = value;
          break;
          
        case 'target_class':
          // 検出対象クラス
          mappedParams['target_class'] = value;
          break;
          
        case 'confidence_threshold':
          // 信頼度閾値
          mappedParams['confidence_threshold'] = value;
          break;
          
        default:
          // その他のパラメータはそのまま
          mappedParams[key] = value;
      }
    }

    return mappedParams;
  }
}