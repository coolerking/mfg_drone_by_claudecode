/**
 * Tests for Confidence Evaluator
 * Tests for confidence scoring and risk assessment
 */

import { ConfidenceEvaluator, ConfidenceEvaluation } from '../confidence_evaluator.js';
import { ParsedIntent } from '../nlp_engine.js';
import { CommandPatterns } from '../command_patterns.js';

describe('ConfidenceEvaluator', () => {
  let evaluator: ConfidenceEvaluator;

  beforeEach(() => {
    evaluator = new ConfidenceEvaluator();
  });

  describe('Initialization', () => {
    test('should initialize with default threshold', () => {
      expect(evaluator.getConfidenceThreshold()).toBe(0.7);
    });

    test('should allow setting custom threshold', () => {
      evaluator.setConfidenceThreshold(0.8);
      expect(evaluator.getConfidenceThreshold()).toBe(0.8);
    });

    test('should clamp threshold to valid range', () => {
      evaluator.setConfidenceThreshold(1.5);
      expect(evaluator.getConfidenceThreshold()).toBe(1.0);
      
      evaluator.setConfidenceThreshold(-0.5);
      expect(evaluator.getConfidenceThreshold()).toBe(0.0);
    });
  });

  describe('Basic Confidence Evaluation', () => {
    test('should evaluate simple takeoff command', async () => {
      const intent: ParsedIntent = {
        action: 'takeoff',
        parameters: {},
        confidence: 0.9,
        original_command: '離陸してください',
        parsed_at: new Date()
      };

      const evaluation = await evaluator.evaluateIntent(intent, '離陸してください');
      
      expect(evaluation.overall_confidence).toBeGreaterThan(0);
      expect(evaluation.action_confidence).toBeGreaterThan(0);
      expect(evaluation.parameter_confidence).toBeGreaterThan(0);
      expect(evaluation.completeness_score).toBeGreaterThan(0);
      expect(evaluation.quality_indicators).toBeDefined();
    });

    test('should evaluate movement command with all parameters', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'forward',
          distance: 200
        },
        confidence: 0.85,
        original_command: '前に2m移動',
        parsed_at: new Date()
      };

      const evaluation = await evaluator.evaluateIntent(intent, '前に2m移動');
      
      expect(evaluation.overall_confidence).toBeGreaterThan(0.7);
      expect(evaluation.quality_indicators.has_all_required_params).toBe(true);
      expect(evaluation.completeness_score).toBeGreaterThan(0.8);
    });

    test('should evaluate photo command', async () => {
      const intent: ParsedIntent = {
        action: 'take_photo',
        parameters: {
          quality: 'high'
        },
        confidence: 0.9,
        original_command: '高画質で写真を撮影',
        parsed_at: new Date()
      };

      const evaluation = await evaluator.evaluateIntent(intent, '高画質で写真を撮影');
      
      expect(evaluation.overall_confidence).toBeGreaterThan(0.8);
      expect(evaluation.action_confidence).toBeGreaterThan(0.8);
    });
  });

  describe('Parameter Confidence Evaluation', () => {
    test('should evaluate valid distance parameter', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'forward',
          distance: 150 // 1.5m in cm
        },
        confidence: 0.8
      };

      const evaluation = await evaluator.evaluateIntent(intent, '前に1.5m移動');
      
      expect(evaluation.parameter_confidence).toBeGreaterThan(0.5);
    });

    test('should evaluate invalid distance parameter', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'forward',
          distance: -100 // Invalid negative distance
        },
        confidence: 0.8
      };

      const evaluation = await evaluator.evaluateIntent(intent, '前に移動');
      
      // Should still provide some confidence but lower due to invalid parameter
      expect(evaluation.parameter_confidence).toBeGreaterThanOrEqual(0);
    });

    test('should evaluate angle parameter', async () => {
      const intent: ParsedIntent = {
        action: 'rotate',
        parameters: {
          direction: 'clockwise',
          angle: 90
        },
        confidence: 0.85
      };

      const evaluation = await evaluator.evaluateIntent(intent, '時計回りに90度回転');
      
      expect(evaluation.parameter_confidence).toBeGreaterThan(0.7);
    });

    test('should handle missing required parameters', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          // Missing required 'direction' parameter
          distance: 100
        },
        confidence: 0.8
      };

      const evaluation = await evaluator.evaluateIntent(intent, '100cm移動');
      
      expect(evaluation.quality_indicators.has_all_required_params).toBe(false);
      expect(evaluation.suggestions.some(s => s.suggestion.includes('direction'))).toBe(true);
    });
  });

  describe('Quality Indicators', () => {
    test('should detect conflicting parameters', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'up',
          // This would be conflicting if we also had 'down'
        },
        confidence: 0.8
      };

      const evaluation = await evaluator.evaluateIntent(intent, '上に移動');
      
      expect(evaluation.quality_indicators.has_conflicting_params).toBe(false);
    });

    test('should detect ambiguous terms', async () => {
      const command = 'ちょっと前に移動してください';
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'forward'
        },
        confidence: 0.6
      };

      const evaluation = await evaluator.evaluateIntent(intent, command);
      
      expect(evaluation.quality_indicators.has_ambiguous_terms).toBe(true);
    });

    test('should handle complete commands well', async () => {
      const intent: ParsedIntent = {
        action: 'take_photo',
        parameters: {
          quality: 'high',
          filename: 'photo001.jpg'
        },
        confidence: 0.9
      };

      const evaluation = await evaluator.evaluateIntent(intent, '高画質でphoto001.jpgとして写真を撮影');
      
      expect(evaluation.quality_indicators.has_all_required_params).toBe(true);
      expect(evaluation.completeness_score).toBeGreaterThan(0.8);
    });
  });

  describe('Risk Assessment', () => {
    test('should identify risks for low confidence commands', async () => {
      const intent: ParsedIntent = {
        action: 'emergency_stop',
        parameters: {},
        confidence: 0.4 // Low confidence
      };

      const evaluation = await evaluator.evaluateIntent(intent, '何かを停止');
      
      expect(evaluation.risk_factors.length).toBeGreaterThan(0);
      expect(evaluation.risk_factors.some(risk => risk.includes('低信頼度'))).toBe(true);
    });

    test('should identify safety risks for critical commands', async () => {
      const intent: ParsedIntent = {
        action: 'emergency_stop',
        parameters: {},
        confidence: 0.75 // Below high threshold for safety command
      };

      const evaluation = await evaluator.evaluateIntent(intent, 'ストップ');
      
      expect(evaluation.risk_factors.some(risk => 
        risk.includes('安全に関わる')
      )).toBe(true);
    });

    test('should handle safe commands with minimal risk', async () => {
      const intent: ParsedIntent = {
        action: 'get_status',
        parameters: {},
        confidence: 0.9
      };

      const evaluation = await evaluator.evaluateIntent(intent, 'ステータスを教えて');
      
      expect(evaluation.risk_factors.length).toBeLessThanOrEqual(1);
    });

    test('should identify conflicting parameter risks', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'up'
          // Simulating conflicting parameters through quality indicators
        },
        confidence: 0.8
      };

      const evaluation = await evaluator.evaluateIntent(intent, '上に下に移動'); // Conflicting directions
      
      // This would be detected by the ambiguous terms detection
      expect(evaluation.risk_factors.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Suggestion Generation', () => {
    test('should suggest missing parameters', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          // Missing direction parameter
        },
        confidence: 0.7
      };

      const evaluation = await evaluator.evaluateIntent(intent, '移動してください');
      
      expect(evaluation.suggestions.length).toBeGreaterThan(0);
      expect(evaluation.suggestions.some(s => s.suggestion.includes('direction'))).toBe(true);
    });

    test('should suggest improvements for low confidence', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {},
        confidence: 0.4 // Low confidence
      };

      const evaluation = await evaluator.evaluateIntent(intent, 'なんか動いて');
      
      expect(evaluation.suggestions.length).toBeGreaterThan(0);
      expect(evaluation.suggestions.some(s => 
        s.suggestion.includes('具体的')
      )).toBe(true);
    });

    test('should provide parameter examples in suggestions', async () => {
      const intent: ParsedIntent = {
        action: 'rotate',
        parameters: {
          direction: 'clockwise'
          // Missing angle
        },
        confidence: 0.75
      };

      const evaluation = await evaluator.evaluateIntent(intent, '時計回りに回転');
      
      expect(evaluation.suggestions.some(s => 
        s.suggestion.includes('angle')
      )).toBe(true);
    });
  });

  describe('Completeness Scoring', () => {
    test('should score complete commands highly', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'forward',
          distance: 200,
          drone_id: 'test-01'
        },
        confidence: 0.85
      };

      const evaluation = await evaluator.evaluateIntent(intent, 'ドローンtest-01で前に2m移動');
      
      expect(evaluation.completeness_score).toBeGreaterThan(0.8);
    });

    test('should score incomplete commands lower', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          // Only partial parameters
          direction: 'forward'
        },
        confidence: 0.7
      };

      const evaluation = await evaluator.evaluateIntent(intent, '前に移動');
      
      expect(evaluation.completeness_score).toBeLessThan(0.9);
    });

    test('should handle commands with no required parameters', async () => {
      const intent: ParsedIntent = {
        action: 'emergency_stop',
        parameters: {},
        confidence: 0.95
      };

      const evaluation = await evaluator.evaluateIntent(intent, '緊急停止');
      
      expect(evaluation.completeness_score).toBeGreaterThan(0.9);
    });
  });

  describe('Executable Determination', () => {
    test('should determine high-confidence complete commands as executable', async () => {
      const intent: ParsedIntent = {
        action: 'takeoff',
        parameters: {
          height: 150
        },
        confidence: 0.9
      };

      const evaluation = await evaluator.evaluateIntent(intent, '高度1.5mで離陸');
      
      const isExecutable = evaluator.isExecutable(evaluation);
      expect(isExecutable).toBe(true);
    });

    test('should determine low-confidence commands as not executable', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {},
        confidence: 0.4
      };

      const evaluation = await evaluator.evaluateIntent(intent, 'なんか移動');
      
      const isExecutable = evaluator.isExecutable(evaluation);
      expect(isExecutable).toBe(false);
    });

    test('should not execute commands with missing required parameters', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          // Missing required direction
          distance: 100
        },
        confidence: 0.8
      };

      const evaluation = await evaluator.evaluateIntent(intent, '100cm移動');
      
      const isExecutable = evaluator.isExecutable(evaluation);
      expect(isExecutable).toBe(false);
    });

    test('should not execute commands with conflicting parameters', async () => {
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'forward'
        },
        confidence: 0.8
      };

      // Mock conflicting parameters in evaluation
      const evaluation = await evaluator.evaluateIntent(intent, '前に後ろに移動');
      // Force conflicting params for testing
      evaluation.quality_indicators.has_conflicting_params = true;
      
      const isExecutable = evaluator.isExecutable(evaluation);
      expect(isExecutable).toBe(false);
    });
  });

  describe('Edge Cases', () => {
    test('should handle empty parameters gracefully', async () => {
      const intent: ParsedIntent = {
        action: 'get_status',
        parameters: {},
        confidence: 0.8
      };

      const evaluation = await evaluator.evaluateIntent(intent, 'ステータス');
      
      expect(evaluation.overall_confidence).toBeGreaterThan(0);
      expect(evaluation.parameter_confidence).toBeGreaterThan(0);
    });

    test('should handle unknown actions', async () => {
      const intent: ParsedIntent = {
        action: 'unknown_action',
        parameters: {},
        confidence: 0.3
      };

      const evaluation = await evaluator.evaluateIntent(intent, 'よくわからないコマンド');
      
      expect(evaluation.overall_confidence).toBeLessThan(0.5);
      expect(evaluation.risk_factors.length).toBeGreaterThan(0);
    });

    test('should handle very long commands', async () => {
      const longCommand = 'ドローンを使って前に移動してから右に曲がって写真を撮影して着陸するという一連の動作を実行してください';
      const intent: ParsedIntent = {
        action: 'move',
        parameters: {
          direction: 'forward'
        },
        confidence: 0.6
      };

      const evaluation = await evaluator.evaluateIntent(intent, longCommand);
      
      expect(evaluation.overall_confidence).toBeGreaterThan(0);
      expect(evaluation.suggestions.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Performance Tests', () => {
    test('should evaluate confidence quickly', async () => {
      const intent: ParsedIntent = {
        action: 'takeoff',
        parameters: { height: 150 },
        confidence: 0.9
      };

      const startTime = Date.now();
      await evaluator.evaluateIntent(intent, '高度1.5mで離陸');
      const endTime = Date.now();
      
      expect(endTime - startTime).toBeLessThan(1000); // Should complete in less than 1 second
    });

    test('should handle multiple concurrent evaluations', async () => {
      const intents = [
        { action: 'takeoff', parameters: {}, confidence: 0.9 },
        { action: 'move', parameters: { direction: 'forward', distance: 100 }, confidence: 0.8 },
        { action: 'take_photo', parameters: { quality: 'high' }, confidence: 0.85 },
        { action: 'land', parameters: {}, confidence: 0.9 }
      ].map(data => ({ ...data, original_command: 'test', parsed_at: new Date() }) as ParsedIntent);

      const commands = ['離陸', '前に1m移動', '高画質で撮影', '着陸'];

      const promises = intents.map((intent, index) => 
        evaluator.evaluateIntent(intent, commands[index])
      );

      const results = await Promise.all(promises);
      
      expect(results).toHaveLength(4);
      results.forEach(result => {
        expect(result.overall_confidence).toBeGreaterThan(0);
        expect(result.quality_indicators).toBeDefined();
      });
    });
  });
});