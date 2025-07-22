/**
 * Tests for NLP Engine
 * Comprehensive test suite for Japanese natural language processing
 */

import { NLPEngine, ParsedIntent } from '../nlp_engine.js';
import { CommandPatterns } from '../command_patterns.js';
import { confidenceEvaluator } from '../confidence_evaluator.js';

describe('NLPEngine', () => {
  let nlpEngine: NLPEngine;

  beforeAll(async () => {
    nlpEngine = new NLPEngine();
    await nlpEngine.initialize();
  });

  describe('Initialization', () => {
    test('should initialize successfully', () => {
      expect(nlpEngine.isReady()).toBe(true);
    });

    test('should have valid confidence threshold', () => {
      expect(nlpEngine.getConfidenceThreshold()).toBeGreaterThan(0);
      expect(nlpEngine.getConfidenceThreshold()).toBeLessThanOrEqual(1);
    });
  });

  describe('Command Parsing - Connection Commands', () => {
    test('should parse Japanese connection command', async () => {
      const command = 'ドローンに接続してください';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('connect');
      expect(result.confidence).toBeGreaterThan(0.7);
      expect(result.original_command).toBe(command);
    });

    test('should parse English connection command', async () => {
      const command = 'connect to drone';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('connect');
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    test('should parse disconnect command', async () => {
      const command = 'ドローンから切断';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('disconnect');
      expect(result.confidence).toBeGreaterThan(0.7);
    });
  });

  describe('Command Parsing - Flight Control', () => {
    test('should parse takeoff command', async () => {
      const command = '離陸してください';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('takeoff');
      expect(result.confidence).toBeGreaterThan(0.8);
    });

    test('should parse takeoff command with height', async () => {
      const command = '高度2mで離陸';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('takeoff');
      expect(result.parameters.height).toBe(200); // converted to cm
      expect(result.confidence).toBeGreaterThan(0.8);
    });

    test('should parse landing command', async () => {
      const command = '着陸してください';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('land');
      expect(result.confidence).toBeGreaterThan(0.8);
    });

    test('should parse emergency stop command', async () => {
      const command = '緊急停止';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('emergency');
      expect(result.confidence).toBeGreaterThan(0.9);
    });
  });

  describe('Command Parsing - Movement', () => {
    test('should parse forward movement command', async () => {
      const command = '前に2m移動';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('move');
      expect(result.parameters.direction).toBe('forward');
      expect(result.parameters.distance).toBe(200); // converted to cm
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    test('should parse movement with centimeters', async () => {
      const command = '右に50cm移動';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('move');
      expect(result.parameters.direction).toBe('right');
      expect(result.parameters.distance).toBe(50);
    });

    test('should parse rotation command', async () => {
      const command = '時計回りに90度回転';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('rotate');
      expect(result.parameters.direction).toBe('clockwise');
      expect(result.parameters.angle).toBe(90);
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    test('should parse English movement command', async () => {
      const command = 'move left 1.5 meters';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('move');
      expect(result.parameters.direction).toBe('left');
      expect(result.parameters.distance).toBe(150);
    });
  });

  describe('Command Parsing - Camera Operations', () => {
    test('should parse photo command', async () => {
      const command = '写真を撮って';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('photo');
      expect(result.confidence).toBeGreaterThan(0.8);
    });

    test('should parse photo command with quality', async () => {
      const command = '高画質で撮影してください';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('photo');
      expect(result.parameters.quality).toBe('high');
    });

    test('should parse streaming commands', async () => {
      const command = 'ストリーミングを開始';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('streaming');
      expect(result.confidence).toBeGreaterThan(0.7);
    });
  });

  describe('Command Parsing - Vision Operations', () => {
    test('should parse object detection command', async () => {
      const command = '物体検出してください';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('detection');
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    test('should parse tracking command', async () => {
      const command = '人を追跡してください';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('tracking');
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    test('should parse English detection command', async () => {
      const command = 'detect objects in the scene';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('detection');
    });
  });

  describe('Command Parsing - System Operations', () => {
    test('should parse status command', async () => {
      const command = 'ドローンの状態を教えて';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('status');
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    test('should parse health check command', async () => {
      const command = 'ヘルスチェックしてください';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('health');
      expect(result.confidence).toBeGreaterThan(0.7);
    });
  });

  describe('Parameter Extraction', () => {
    test('should extract drone ID from command', async () => {
      const command = 'ドローンalpha-01に接続';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.parameters.drone_id).toBe('alpha-01');
    });

    test('should handle unit conversions correctly', async () => {
      const testCases = [
        { command: '前に2m移動', expected: 200 },
        { command: '右に150cm進む', expected: 150 },
        { command: '上に500mm上昇', expected: 50 }
      ];

      for (const testCase of testCases) {
        const result = await nlpEngine.parseCommand(testCase.command);
        expect(result.parameters.distance).toBe(testCase.expected);
      }
    });

    test('should extract direction mappings', async () => {
      const testCases = [
        { command: '右に移動', expected: 'right' },
        { command: '時計回りに回転', expected: 'clockwise' },
        { command: '前に進む', expected: 'forward' }
      ];

      for (const testCase of testCases) {
        const result = await nlpEngine.parseCommand(testCase.command);
        expect(result.parameters.direction).toBe(testCase.expected);
      }
    });

    test('should extract angle values', async () => {
      const command = '左に180度回転';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.parameters.angle).toBe(180);
    });

    test('should extract quality parameters', async () => {
      const command = '中画質で撮影';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.parameters.quality).toBe('medium');
    });
  });

  describe('Context Handling', () => {
    test('should merge context with extracted parameters', async () => {
      const command = '前に2m移動';
      const context = { drone_id: 'test-drone-01' };
      const result = await nlpEngine.parseCommand(command, context);
      
      expect(result.parameters.drone_id).toBe('test-drone-01');
      expect(result.parameters.direction).toBe('forward');
      expect(result.parameters.distance).toBe(200);
    });

    test('should not override extracted parameters with context', async () => {
      const command = 'ドローンbeta-02で前に移動';
      const context = { drone_id: 'alpha-01' };
      const result = await nlpEngine.parseCommand(command, context);
      
      // Extracted parameter should not be overridden by context
      expect(result.parameters.drone_id).toBe('beta-02');
    });
  });

  describe('Error Handling', () => {
    test('should throw error for unrecognizable command', async () => {
      const command = 'これは全く意味不明なコマンドです';
      
      await expect(nlpEngine.parseCommand(command)).rejects.toThrow();
    });

    test('should handle empty command', async () => {
      const command = '';
      
      await expect(nlpEngine.parseCommand(command)).rejects.toThrow();
    });

    test('should handle command with only spaces', async () => {
      const command = '   ';
      
      await expect(nlpEngine.parseCommand(command)).rejects.toThrow();
    });
  });

  describe('Command Suggestions', () => {
    test('should provide suggestions for incomplete commands', async () => {
      const command = 'ドローン移動'; // Missing direction and distance
      const suggestions = await nlpEngine.suggestCorrections(command);
      
      expect(suggestions).toBeDefined();
      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions.some(s => s.suggestion.includes('距離'))).toBe(true);
    });

    test('should provide suggestions for commands without drone ID', async () => {
      const command = '移動してください'; // Missing drone ID
      const suggestions = await nlpEngine.suggestCorrections(command);
      
      expect(suggestions).toBeDefined();
      expect(suggestions.some(s => s.suggestion.includes('ドローンID'))).toBe(true);
    });

    test('should provide suggestions for vague commands', async () => {
      const command = '何かしてください'; // Too vague
      const suggestions = await nlpEngine.suggestCorrections(command);
      
      expect(suggestions).toBeDefined();
      expect(suggestions.some(s => s.suggestion.includes('動作'))).toBe(true);
    });

    test('should provide suggestions for rotation without angle', async () => {
      const command = '回転してください'; // Missing angle
      const suggestions = await nlpEngine.suggestCorrections(command);
      
      expect(suggestions).toBeDefined();
      expect(suggestions.some(s => s.suggestion.includes('角度'))).toBe(true);
    });
  });

  describe('Complex Command Parsing', () => {
    test('should parse complex multi-parameter commands', async () => {
      const command = 'ドローン01を高度2mで離陸させて、前に3m移動してから高画質で写真を撮影';
      
      // This would typically require multiple command parsing or more sophisticated NLP
      // For now, we test that it extracts the first recognizable action
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0);
    });

    test('should handle commands with multiple units', async () => {
      const command = '前に1.5m、右に80cm移動';
      const result = await nlpEngine.parseCommand(command);
      
      expect(result.action).toBe('move');
      expect(result.parameters.distance).toBeDefined();
    });
  });

  describe('Confidence Evaluation Integration', () => {
    test('should integrate with confidence evaluator', async () => {
      const command = '離陸してください';
      const intent = await nlpEngine.parseCommand(command);
      const evaluation = await confidenceEvaluator.evaluateIntent(intent, command);
      
      expect(evaluation.overall_confidence).toBeGreaterThan(0);
      expect(evaluation.action_confidence).toBeGreaterThan(0);
      expect(evaluation.parameter_confidence).toBeGreaterThan(0);
      expect(evaluation.quality_indicators).toBeDefined();
    });

    test('should provide risk assessment for dangerous commands', async () => {
      const command = '緊急停止';
      const intent = await nlpEngine.parseCommand(command);
      const evaluation = await confidenceEvaluator.evaluateIntent(intent, command);
      
      expect(evaluation.risk_factors).toBeDefined();
      expect(evaluation.suggestions).toBeDefined();
    });
  });

  describe('Performance Tests', () => {
    test('should parse commands within acceptable time', async () => {
      const commands = [
        '離陸してください',
        '前に2m移動',
        '写真を撮って',
        '着陸してください'
      ];

      const startTime = Date.now();
      
      for (const command of commands) {
        await nlpEngine.parseCommand(command);
      }
      
      const endTime = Date.now();
      const totalTime = endTime - startTime;
      
      // Should complete all commands in less than 5 seconds
      expect(totalTime).toBeLessThan(5000);
    });

    test('should handle concurrent parsing requests', async () => {
      const commands = [
        '離陸してください',
        '前に1m移動',
        '右に90度回転',
        '写真を撮影',
        '着陸してください'
      ];

      const promises = commands.map(command => nlpEngine.parseCommand(command));
      const results = await Promise.all(promises);
      
      expect(results).toHaveLength(commands.length);
      results.forEach(result => {
        expect(result.action).toBeDefined();
        expect(result.confidence).toBeGreaterThan(0);
      });
    });
  });
});

describe('CommandPatterns', () => {
  describe('Pattern Validation', () => {
    test('should have valid action patterns', () => {
      const validation = CommandPatterns.validatePatterns();
      
      expect(validation.valid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    test('should have comprehensive pattern coverage', () => {
      const stats = CommandPatterns.getStatistics();
      
      expect(stats.total_actions).toBeGreaterThan(10);
      expect(stats.total_parameters).toBeGreaterThan(5);
      expect(stats.total_patterns).toBeGreaterThan(50);
    });

    test('should provide pattern lookup functionality', () => {
      const actionPattern = CommandPatterns.getActionPattern('takeoff');
      expect(actionPattern).toBeDefined();
      expect(actionPattern?.action).toBe('takeoff');
      expect(actionPattern?.patterns.length).toBeGreaterThan(0);

      const paramPattern = CommandPatterns.getParameterPattern('distance');
      expect(paramPattern).toBeDefined();
      expect(paramPattern?.name).toBe('distance');
      expect(paramPattern?.type).toBe('number');
    });
  });
});

describe('Integration Tests', () => {
  test('should work with the full NLP pipeline', async () => {
    const nlpEngine = new NLPEngine();
    await nlpEngine.initialize();
    
    const testCommand = 'ドローン01を高度1.5mで離陸させてください';
    
    // Parse the command
    const intent = await nlpEngine.parseCommand(testCommand);
    expect(intent.action).toBe('takeoff');
    expect(intent.parameters.height).toBe(150);
    expect(intent.parameters.drone_id).toBe('01');
    
    // Evaluate confidence
    const evaluation = await confidenceEvaluator.evaluateIntent(intent, testCommand);
    expect(evaluation.overall_confidence).toBeGreaterThan(0.7);
    
    // Check if executable
    const isExecutable = confidenceEvaluator.isExecutable(evaluation);
    expect(typeof isExecutable).toBe('boolean');
  });
});