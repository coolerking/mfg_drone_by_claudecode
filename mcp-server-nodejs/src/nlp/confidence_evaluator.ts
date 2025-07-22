/**
 * Confidence Evaluator for Natural Language Processing
 * Evaluates confidence scores for parsed commands and provides quality metrics
 */

import { logger } from '@/utils/logger.js';
import { ParsedIntent, CommandSuggestion } from './nlp_engine.js';
import { CommandPatterns, CommandPattern, ParameterPattern } from './command_patterns.js';

/**
 * 信頼度評価結果
 */
export interface ConfidenceEvaluation {
  overall_confidence: number;
  action_confidence: number;
  parameter_confidence: number;
  completeness_score: number;
  quality_indicators: {
    has_all_required_params: boolean;
    has_conflicting_params: boolean;
    has_ambiguous_terms: boolean;
    morphological_match: boolean;
  };
  suggestions: CommandSuggestion[];
  risk_factors: string[];
}

/**
 * 信頼度メトリクス
 */
export interface ConfidenceMetrics {
  precision: number;
  recall: number;
  f1_score: number;
  accuracy: number;
  total_evaluated: number;
}

/**
 * 信頼度評価器
 */
export class ConfidenceEvaluator {
  private readonly baseConfidenceThreshold = 0.7;
  private readonly highConfidenceThreshold = 0.85;
  private readonly lowConfidenceThreshold = 0.5;

  constructor(
    private confidenceThreshold: number = 0.7
  ) {}

  /**
   * 解析済み意図の信頼度を評価
   */
  async evaluateIntent(
    intent: ParsedIntent, 
    originalCommand: string,
    morphemeTokens?: any[]
  ): Promise<ConfidenceEvaluation> {
    try {
      logger.debug(`Evaluating confidence for intent: ${intent.action}`);

      // アクション信頼度を評価
      const actionConfidence = this.evaluateActionConfidence(
        intent.action, 
        originalCommand, 
        morphemeTokens
      );

      // パラメータ信頼度を評価
      const parameterConfidence = this.evaluateParameterConfidence(
        intent.action,
        intent.parameters,
        originalCommand
      );

      // 完全性スコアを計算
      const completenessScore = this.calculateCompletenessScore(
        intent.action,
        intent.parameters
      );

      // 品質指標を評価
      const qualityIndicators = this.evaluateQualityIndicators(
        intent,
        originalCommand,
        morphemeTokens
      );

      // 全体的な信頼度を計算
      const overallConfidence = this.calculateOverallConfidence(
        actionConfidence,
        parameterConfidence,
        completenessScore,
        qualityIndicators
      );

      // 提案を生成
      const suggestions = await this.generateSuggestions(
        intent,
        originalCommand,
        overallConfidence
      );

      // リスクファクターを特定
      const riskFactors = this.identifyRiskFactors(
        intent,
        qualityIndicators,
        overallConfidence
      );

      return {
        overall_confidence: overallConfidence,
        action_confidence: actionConfidence,
        parameter_confidence: parameterConfidence,
        completeness_score: completenessScore,
        quality_indicators: qualityIndicators,
        suggestions,
        risk_factors: riskFactors
      };

    } catch (error) {
      logger.error(`Error evaluating confidence: ${error}`);
      throw new Error(`Confidence evaluation failed: ${error}`);
    }
  }

  /**
   * アクション信頼度を評価
   */
  private evaluateActionConfidence(
    action: string,
    command: string,
    morphemeTokens?: any[]
  ): number {
    const actionPattern = CommandPatterns.getActionPattern(action);
    if (!actionPattern) {
      return 0.0;
    }

    let maxConfidence = 0.0;
    let patternMatches = 0;

    // パターンマッチング信頼度
    for (const pattern of actionPattern.patterns) {
      try {
        const regex = new RegExp(pattern, 'i');
        if (regex.test(command)) {
          patternMatches++;
          maxConfidence = Math.max(maxConfidence, actionPattern.confidence_base);
        }
      } catch (error) {
        logger.warn(`Invalid regex pattern: ${pattern}`);
      }
    }

    // パターンマッチが複数ある場合は信頼度向上
    if (patternMatches > 1) {
      maxConfidence *= 1.1;
    }

    // 形態素解析結果を使用した信頼度向上
    if (morphemeTokens && this.hasMorphologicalEvidence(action, morphemeTokens)) {
      maxConfidence *= 1.15;
    }

    // 完全一致の場合は信頼度向上
    if (actionPattern.patterns.some(pattern => command === pattern)) {
      maxConfidence *= 1.2;
    }

    return Math.min(maxConfidence, 1.0);
  }

  /**
   * パラメータ信頼度を評価
   */
  private evaluateParameterConfidence(
    action: string,
    parameters: Record<string, any>,
    command: string
  ): number {
    const actionPattern = CommandPatterns.getActionPattern(action);
    if (!actionPattern) {
      return 0.0;
    }

    const requiredParams = actionPattern.required_params || [];
    const optionalParams = actionPattern.optional_params || [];
    const allExpectedParams = [...requiredParams, ...optionalParams];

    if (allExpectedParams.length === 0) {
      return 1.0; // パラメータが期待されない場合は最高信頼度
    }

    let totalConfidence = 0.0;
    let evaluatedParams = 0;

    // 各パラメータの信頼度を評価
    for (const [paramName, paramValue] of Object.entries(parameters)) {
      if (allExpectedParams.includes(paramName)) {
        const paramConfidence = this.evaluateSingleParameterConfidence(
          paramName,
          paramValue,
          command
        );
        totalConfidence += paramConfidence;
        evaluatedParams++;
      }
    }

    // 必須パラメータが不足している場合は信頼度を下げる
    const missingRequiredParams = requiredParams.filter(param => !(param in parameters));
    const missingPenalty = missingRequiredParams.length * 0.3;

    const averageConfidence = evaluatedParams > 0 ? totalConfidence / evaluatedParams : 0.5;
    return Math.max(0.0, averageConfidence - missingPenalty);
  }

  /**
   * 単一パラメータの信頼度を評価
   */
  private evaluateSingleParameterConfidence(
    paramName: string,
    paramValue: any,
    command: string
  ): number {
    const paramPattern = CommandPatterns.getParameterPattern(paramName);
    if (!paramPattern) {
      return 0.5; // パターンが見つからない場合は中立
    }

    // パターンマッチング
    let patternConfidence = 0.0;
    for (const pattern of paramPattern.patterns) {
      try {
        const regex = new RegExp(pattern, 'i');
        if (regex.test(command)) {
          patternConfidence = 0.8;
          break;
        }
      } catch (error) {
        logger.warn(`Invalid regex pattern: ${pattern}`);
      }
    }

    // 値の妥当性チェック
    let validationConfidence = 0.5;
    if (paramPattern.validator) {
      try {
        if (paramPattern.validator(paramValue)) {
          validationConfidence = 0.9;
        } else {
          validationConfidence = 0.2;
        }
      } catch (error) {
        logger.warn(`Parameter validation failed for ${paramName}: ${error}`);
        validationConfidence = 0.3;
      }
    }

    // 型の一致チェック
    let typeConfidence = 0.5;
    const expectedType = paramPattern.type;
    const actualType = typeof paramValue;
    
    if (expectedType === 'number' && (actualType === 'number' && !isNaN(paramValue))) {
      typeConfidence = 0.9;
    } else if (expectedType === 'string' && actualType === 'string') {
      typeConfidence = 0.9;
    } else if (expectedType === 'boolean' && actualType === 'boolean') {
      typeConfidence = 0.9;
    }

    return Math.max(patternConfidence, (validationConfidence + typeConfidence) / 2);
  }

  /**
   * 完全性スコアを計算
   */
  private calculateCompletenessScore(action: string, parameters: Record<string, any>): number {
    const actionPattern = CommandPatterns.getActionPattern(action);
    if (!actionPattern) {
      return 0.0;
    }

    const requiredParams = actionPattern.required_params || [];
    const optionalParams = actionPattern.optional_params || [];

    // 必須パラメータの充足率
    const requiredFulfilled = requiredParams.filter(param => param in parameters).length;
    const requiredScore = requiredParams.length === 0 ? 1.0 : requiredFulfilled / requiredParams.length;

    // オプションパラメータのボーナス
    const optionalFulfilled = optionalParams.filter(param => param in parameters).length;
    const optionalBonus = optionalParams.length === 0 ? 0 : (optionalFulfilled / optionalParams.length) * 0.2;

    return Math.min(1.0, requiredScore + optionalBonus);
  }

  /**
   * 品質指標を評価
   */
  private evaluateQualityIndicators(
    intent: ParsedIntent,
    command: string,
    morphemeTokens?: any[]
  ) {
    const actionPattern = CommandPatterns.getActionPattern(intent.action);
    const requiredParams = actionPattern?.required_params || [];

    // 必須パラメータの存在チェック
    const hasAllRequiredParams = requiredParams.every(param => param in intent.parameters);

    // 競合するパラメータのチェック
    const hasConflictingParams = this.hasConflictingParameters(intent.parameters);

    // 曖昧な用語のチェック
    const hasAmbiguousTerms = this.hasAmbiguousTerms(command);

    // 形態素解析マッチのチェック
    const morphologicalMatch = morphemeTokens ? 
      this.hasMorphologicalEvidence(intent.action, morphemeTokens) : false;

    return {
      has_all_required_params: hasAllRequiredParams,
      has_conflicting_params: hasConflictingParams,
      has_ambiguous_terms: hasAmbiguousTerms,
      morphological_match: morphologicalMatch
    };
  }

  /**
   * 全体的な信頼度を計算
   */
  private calculateOverallConfidence(
    actionConfidence: number,
    parameterConfidence: number,
    completenessScore: number,
    qualityIndicators: any
  ): number {
    // 重み付き平均
    const weights = {
      action: 0.4,
      parameter: 0.3,
      completeness: 0.2,
      quality: 0.1
    };

    // 品質指標による調整
    let qualityAdjustment = 0.0;
    if (qualityIndicators.has_all_required_params) qualityAdjustment += 0.05;
    if (!qualityIndicators.has_conflicting_params) qualityAdjustment += 0.03;
    if (!qualityIndicators.has_ambiguous_terms) qualityAdjustment += 0.02;
    if (qualityIndicators.morphological_match) qualityAdjustment += 0.05;

    const baseConfidence = 
      actionConfidence * weights.action +
      parameterConfidence * weights.parameter +
      completenessScore * weights.completeness;

    return Math.min(1.0, baseConfidence + qualityAdjustment);
  }

  /**
   * 形態素解析の証拠があるかチェック
   */
  private hasMorphologicalEvidence(action: string, morphemeTokens: any[]): boolean {
    const actionKeywords: Record<string, string[]> = {
      connect: ['接続', 'つなぐ', 'つながる'],
      disconnect: ['切断', '切る'],
      takeoff: ['離陸', '飛ぶ', '上がる'],
      land: ['着陸', '降りる'],
      move: ['移動', '進む', '動く'],
      rotate: ['回転', '回る'],
      take_photo: ['撮影', '撮る', '写真'],
      emergency_stop: ['停止', '止める', '緊急']
    };

    const keywords = actionKeywords[action] || [];
    return morphemeTokens.some(token => 
      keywords.includes(token.surface_form) || 
      keywords.includes(token.basic_form)
    );
  }

  /**
   * 競合するパラメータがあるかチェック
   */
  private hasConflictingParameters(parameters: Record<string, any>): boolean {
    // 相互排他的なパラメータの組み合わせ
    const conflicts = [
      ['immediate', 'safe'], // 緊急着陸と安全着陸
      ['up', 'down'],        // 上昇と下降
      ['left', 'right'],     // 左と右
      ['clockwise', 'counterclockwise'] // 時計回りと反時計回り
    ];

    for (const conflict of conflicts) {
      const hasConflict = conflict.every(param => 
        param in parameters || 
        Object.values(parameters).includes(param)
      );
      if (hasConflict) return true;
    }

    return false;
  }

  /**
   * 曖昧な用語があるかチェック
   */
  private hasAmbiguousTerms(command: string): boolean {
    const ambiguousTerms = [
      'そこ', 'あそこ', 'どこか', 'somewhere', 'there',
      'ちょっと', 'すこし', 'a bit', 'little',
      'たくさん', 'いっぱい', 'a lot', 'many',
      'はやく', 'ゆっくり', 'fast', 'slow'
    ];

    return ambiguousTerms.some(term => command.includes(term));
  }

  /**
   * 提案を生成
   */
  private async generateSuggestions(
    intent: ParsedIntent,
    command: string,
    confidence: number
  ): Promise<CommandSuggestion[]> {
    const suggestions: CommandSuggestion[] = [];

    // 低信頼度の場合
    if (confidence < this.lowConfidenceThreshold) {
      suggestions.push({
        suggestion: 'コマンドをより具体的に記述してください',
        reason: '信頼度が低いため、より詳細な指示が必要です',
        confidence: 0.8
      });
    }

    // 必須パラメータ不足の場合
    const actionPattern = CommandPatterns.getActionPattern(intent.action);
    const requiredParams = actionPattern?.required_params || [];
    const missingParams = requiredParams.filter(param => !(param in intent.parameters));

    for (const param of missingParams) {
      const paramPattern = CommandPatterns.getParameterPattern(param);
      const examples = paramPattern?.examples || [];
      
      suggestions.push({
        suggestion: `${param}を指定してください${examples.length > 0 ? `（例：${examples[0]}）` : ''}`,
        reason: `必須パラメータ「${param}」が不足しています`,
        confidence: 0.9
      });
    }

    return suggestions;
  }

  /**
   * リスクファクターを特定
   */
  private identifyRiskFactors(
    intent: ParsedIntent,
    qualityIndicators: any,
    confidence: number
  ): string[] {
    const risks: string[] = [];

    if (confidence < this.lowConfidenceThreshold) {
      risks.push('低信頼度による実行リスク');
    }

    if (qualityIndicators.has_conflicting_params) {
      risks.push('競合するパラメータが検出されました');
    }

    if (!qualityIndicators.has_all_required_params) {
      risks.push('必須パラメータが不足しています');
    }

    if (qualityIndicators.has_ambiguous_terms) {
      risks.push('曖昧な表現が含まれています');
    }

    // 危険なアクションの場合
    const dangerousActions = ['emergency_stop', 'takeoff', 'land'];
    if (dangerousActions.includes(intent.action) && confidence < this.highConfidenceThreshold) {
      risks.push('安全に関わるコマンドの信頼度が十分ではありません');
    }

    return risks;
  }

  /**
   * 信頼度閾値を設定
   */
  setConfidenceThreshold(threshold: number): void {
    this.confidenceThreshold = Math.max(0, Math.min(1, threshold));
  }

  /**
   * 信頼度閾値を取得
   */
  getConfidenceThreshold(): number {
    return this.confidenceThreshold;
  }

  /**
   * 実行可能かどうかを判定
   */
  isExecutable(evaluation: ConfidenceEvaluation): boolean {
    return evaluation.overall_confidence >= this.confidenceThreshold &&
           evaluation.quality_indicators.has_all_required_params &&
           !evaluation.quality_indicators.has_conflicting_params;
  }
}

export const confidenceEvaluator = new ConfidenceEvaluator();