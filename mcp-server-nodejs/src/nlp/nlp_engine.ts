/**
 * Natural Language Processing Engine for MCP Server
 * TypeScript implementation of the Python NLP Engine with kuromoji.js for morphological analysis
 */

import kuromoji from 'kuromoji';
import { logger } from '@/utils/logger.js';

/**
 * 解析済みの意図を表すインターface
 */
export interface ParsedIntent {
  action: string;
  parameters: Record<string, any>;
  confidence: number;
  original_command?: string;
  parsed_at?: Date;
}

/**
 * コマンド提案を表すインターface
 */
export interface CommandSuggestion {
  suggestion: string;
  reason: string;
  confidence: number;
}

/**
 * 自然言語処理エンジン
 */
export class NLPEngine {
  private tokenizer: any = null;
  private isInitialized = false;
  private readonly confidenceThreshold: number = 0.7;
  private readonly defaultLanguage = 'ja';

  // Action patterns (Japanese)
  private readonly actionPatterns: Record<string, string[]> = {
    // Connection
    connect: [
      '.*?に?接続',
      '.*?に?繋げ',
      '.*?に?つなが',
      '.*?に?コネクト'
    ],
    disconnect: [
      '.*?から?切断',
      '.*?から?切断',
      '接続を?切',
      'ディスコネクト'
    ],
    
    // Flight control
    takeoff: [
      '離陸',
      '起動',
      '飛び立',
      'テイクオフ'
    ],
    land: [
      '着陸',
      '降り',
      'ランディング',
      '着地'
    ],
    emergency: [
      '緊急停止',
      '止ま',
      'ストップ',
      '停止'
    ],
    
    // Movement
    move: [
      '移動',
      '進',
      '動',
      '移',
      '行'
    ],
    rotate: [
      '回転',
      '回',
      '向き',
      '回る'
    ],
    altitude: [
      '高度',
      '高さ',
      '上昇',
      '下降'
    ],
    
    // Camera
    photo: [
      '写真',
      '撮影',
      '撮',
      'フォト'
    ],
    streaming: [
      'ストリーミング',
      '配信',
      '映像'
    ],
    learning: [
      '学習',
      'データ収集',
      '学習データ'
    ],
    
    // Vision
    detection: [
      '物体検出',
      '検出',
      '物体認識',
      '何が見える'
    ],
    tracking: [
      '追跡',
      '追従',
      'トラッキング'
    ],
    
    // System
    status: [
      '状態',
      'ステータス',
      '様子'
    ],
    health: [
      '正常',
      'ヘルス',
      '健康'
    ]
  };

  // Parameter extraction patterns
  private readonly parameterPatterns: Record<string, string[]> = {
    drone_id: [
      'ドローン([A-Za-z0-9_-]+)',
      'drone[-_]?([A-Za-z0-9_-]+)',
      '([A-Za-z0-9_-]+)番目',
      '([A-Za-z0-9_-]+)番'
    ],
    distance: [
      '(\\d+)\\s*(?:cm|センチ|センチメートル)',
      '(\\d+)\\s*(?:m|メートル)',
      '(\\d+)\\s*(?:mm|ミリ|ミリメートル)'
    ],
    angle: [
      '(\\d+)\\s*(?:度|°)',
      '(\\d+)\\s*(?:度|°)\\s*(?:回転|回)'
    ],
    height: [
      '高さ\\s*(\\d+)\\s*(?:cm|センチ|センチメートル)',
      '高さ\\s*(\\d+)\\s*(?:m|メートル)',
      '高度\\s*(\\d+)\\s*(?:cm|センチ|センチメートル)',
      '高度\\s*(\\d+)\\s*(?:m|メートル)'
    ],
    direction: [
      '(右|左|前|後|上|下|forward|back|left|right|up|down)',
      '(時計回り|反時計回り|clockwise|counter_clockwise)'
    ],
    quality: [
      '(高|中|低|high|medium|low)\\s*(?:画質|品質)'
    ],
    filename: [
      'ファイル名\\s*[：:]\\s*([^\\s]+)',
      '名前\\s*[：:]\\s*([^\\s]+)'
    ]
  };

  // Direction mappings
  private readonly directionMappings: Record<string, string> = {
    '右': 'right',
    '左': 'left',
    '前': 'forward',
    '後': 'back',
    '上': 'up',
    '下': 'down',
    '時計回り': 'clockwise',
    '反時計回り': 'counter_clockwise'
  };

  // Unit conversions
  private readonly unitConversions: Record<string, number> = {
    'm': 100,  // meters to cm
    'メートル': 100,
    'mm': 0.1,  // mm to cm
    'ミリ': 0.1,
    'ミリメートル': 0.1,
    'cm': 1,
    'センチ': 1,
    'センチメートル': 1
  };

  constructor() {
    logger.info('Initializing NLP engine...');
  }

  /**
   * NLPエンジンを初期化
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      // kuromoji tokenizerを初期化
      this.tokenizer = await new Promise<any>((resolve, reject) => {
        kuromoji.builder({ dicPath: 'node_modules/kuromoji/dict' }).build((err: any, tokenizer: any) => {
          if (err) {
            reject(err);
          } else {
            resolve(tokenizer);
          }
        });
      });

      this.isInitialized = true;
      logger.info('NLP engine initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize NLP engine:', error);
      throw new Error(`Failed to initialize NLP engine: ${error}`);
    }
  }

  /**
   * 自然言語コマンドを解析
   */
  async parseCommand(command: string, context?: Record<string, any>): Promise<ParsedIntent> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      logger.debug(`Parsing command: ${command}`);
      
      // コマンドをクリーニング
      const cleanCommand = command.trim();
      
      // アクションを抽出
      const [action, confidence] = await this.extractAction(cleanCommand);
      if (!action) {
        throw new Error('Could not identify action in command');
      }
      
      // パラメータを抽出
      const parameters = await this.extractParameters(cleanCommand, context);
      
      // コンテキストパラメータを追加
      if (context) {
        Object.assign(parameters, context);
      }
      
      // 解析済み意図を作成
      const parsedIntent: ParsedIntent = {
        action,
        parameters,
        confidence,
        original_command: command,
        parsed_at: new Date()
      };
      
      logger.debug('Parsed intent:', parsedIntent);
      return parsedIntent;
      
    } catch (error) {
      logger.error(`Error parsing command: ${error}`);
      throw new Error(`Could not parse command: ${error}`);
    }
  }

  /**
   * コマンドからアクションを抽出
   */
  private async extractAction(command: string): Promise<[string | null, number]> {
    let bestAction: string | null = null;
    let bestConfidence = 0.0;

    // 形態素解析を実行
    const tokens = this.tokenizer?.tokenize(command) || [];
    const morphemes = tokens.map((token: any) => token.surface_form).join(' ');
    
    for (const [action, patterns] of Object.entries(this.actionPatterns)) {
      for (const pattern of patterns) {
        const regex = new RegExp(pattern);
        if (regex.test(command) || regex.test(morphemes)) {
          let confidence = 0.8; // Base confidence
          
          // 完全一致の場合信頼度を向上
          if (command.includes(pattern) || morphemes.includes(pattern)) {
            confidence = 0.9;
          }
          
          // 形態素解析結果を使用した場合の信頼度向上
          if (this.hasRelevantMorphemes(tokens, action)) {
            confidence += 0.05;
          }
          
          if (confidence > bestConfidence) {
            bestAction = action;
            bestConfidence = confidence;
          }
        }
      }
    }

    return [bestAction, bestConfidence];
  }

  /**
   * 関連する形態素が含まれているかチェック
   */
  private hasRelevantMorphemes(tokens: kuromoji.IpadicFeatures[], action: string): boolean {
    const actionMorphemes: Record<string, string[]> = {
      connect: ['接続', 'つなぐ', 'つながる'],
      disconnect: ['切断', '切る'],
      takeoff: ['離陸', '飛ぶ', '上がる'],
      land: ['着陸', '降りる', '下がる'],
      move: ['移動', '進む', '動く'],
      rotate: ['回転', '回る', '向く'],
      photo: ['撮影', '撮る', '写真'],
      emergency: ['停止', '止める', '緊急']
    };

    const relevantMorphemes = actionMorphemes[action] || [];
    return tokens.some((token: any) => 
      relevantMorphemes.includes(token.surface_form) ||
      relevantMorphemes.includes(token.basic_form)
    );
  }

  /**
   * コマンドからパラメータを抽出
   */
  private async extractParameters(command: string, context?: Record<string, any>): Promise<Record<string, any>> {
    const parameters: Record<string, any> = {};

    // ドローンIDを抽出
    if (!context?.drone_id) {
      const droneId = this.extractDroneId(command);
      if (droneId) {
        parameters.drone_id = droneId;
      }
    }

    // 距離を抽出
    const distance = this.extractDistance(command);
    if (distance !== null) {
      parameters.distance = distance;
    }

    // 角度を抽出
    const angle = this.extractAngle(command);
    if (angle !== null) {
      parameters.angle = angle;
    }

    // 高度を抽出
    const height = this.extractHeight(command);
    if (height !== null) {
      parameters.height = height;
    }

    // 方向を抽出
    const direction = this.extractDirection(command);
    if (direction) {
      parameters.direction = direction;
    }

    // 品質を抽出
    const quality = this.extractQuality(command);
    if (quality) {
      parameters.quality = quality;
    }

    // ファイル名を抽出
    const filename = this.extractFilename(command);
    if (filename) {
      parameters.filename = filename;
    }

    return parameters;
  }

  /**
   * ドローンIDを抽出
   */
  private extractDroneId(command: string): string | null {
    const patterns = this.parameterPatterns?.drone_id;
    if (!patterns) return null;
    
    for (const pattern of patterns) {
      const match = command.match(new RegExp(pattern));
      if (match?.[1]) {
        return match[1];
      }
    }
    return null;
  }

  /**
   * 距離を抽出
   */
  private extractDistance(command: string): number | null {
    const patterns = this.parameterPatterns?.distance;
    if (!patterns) return null;
    
    for (const pattern of patterns) {
      const match = command.match(new RegExp(pattern));
      if (match?.[1]) {
        let value = parseInt(match[1], 10);
        
        // 単位をチェック
        if (match[0]?.includes('m') || match[0]?.includes('メートル')) {
          value *= 100; // cm に変換
        } else if (match[0]?.includes('mm') || match[0]?.includes('ミリ')) {
          value = Math.round(value * 0.1); // cm に変換
        }
        
        return value;
      }
    }
    return null;
  }

  /**
   * 角度を抽出
   */
  private extractAngle(command: string): number | null {
    const patterns = this.parameterPatterns?.angle;
    if (!patterns) return null;
    
    for (const pattern of patterns) {
      const match = command.match(new RegExp(pattern));
      if (match?.[1]) {
        return parseInt(match[1], 10);
      }
    }
    return null;
  }

  /**
   * 高度を抽出
   */
  private extractHeight(command: string): number | null {
    const patterns = this.parameterPatterns?.height;
    if (!patterns) return null;
    
    for (const pattern of patterns) {
      const match = command.match(new RegExp(pattern));
      if (match?.[1]) {
        let value = parseInt(match[1], 10);
        
        // 単位をチェック
        if (match[0]?.includes('m') || match[0]?.includes('メートル')) {
          value *= 100; // cm に変換
        }
        
        return value;
      }
    }
    return null;
  }

  /**
   * 方向を抽出
   */
  private extractDirection(command: string): string | null {
    const patterns = this.parameterPatterns?.direction;
    if (!patterns) return null;
    
    for (const pattern of patterns) {
      const match = command.match(new RegExp(pattern));
      if (match?.[1]) {
        const direction = match[1];
        return this.directionMappings[direction] || direction;
      }
    }
    return null;
  }

  /**
   * 品質を抽出
   */
  private extractQuality(command: string): string | null {
    const patterns = this.parameterPatterns?.quality;
    if (!patterns) return null;
    
    for (const pattern of patterns) {
      const match = command.match(new RegExp(pattern));
      if (match?.[1]) {
        const quality = match[1];
        const qualityMappings: Record<string, string> = {
          '高': 'high',
          '中': 'medium',
          '低': 'low'
        };
        return qualityMappings[quality] || quality;
      }
    }
    return null;
  }

  /**
   * ファイル名を抽出
   */
  private extractFilename(command: string): string | null {
    const patterns = this.parameterPatterns?.filename;
    if (!patterns) return null;
    
    for (const pattern of patterns) {
      const match = command.match(new RegExp(pattern));
      if (match?.[1]) {
        return match[1];
      }
    }
    return null;
  }

  /**
   * 認識できないコマンドに対する修正提案を生成
   */
  async suggestCorrections(command: string): Promise<CommandSuggestion[]> {
    const suggestions: CommandSuggestion[] = [];
    
    // よくあるタイポや不足単語をチェック
    if (!command.includes('ドローン') && !command.includes('drone')) {
      suggestions.push({
        suggestion: 'ドローンIDを指定してください',
        reason: 'コマンドにドローンの識別子が含まれていません',
        confidence: 0.8
      });
    }
    
    // アクションの存在をチェック
    const hasAction = this.actionPatterns ? Object.values(this.actionPatterns)
      .flat()
      .some(pattern => new RegExp(pattern).test(command)) : false;
    
    if (!hasAction) {
      suggestions.push({
        suggestion: '動作を明確に指定してください（例：移動、撮影、接続）',
        reason: '実行する動作が明確ではありません',
        confidence: 0.9
      });
    }
    
    // パラメータの不足をチェック
    if (command.includes('移動') && this.parameterPatterns?.distance && !this.parameterPatterns.distance.some(pattern => 
      new RegExp(pattern).test(command))) {
      suggestions.push({
        suggestion: '移動距離を指定してください（例：50cm、1m）',
        reason: '移動コマンドに距離が指定されていません',
        confidence: 0.85
      });
    }
    
    if (command.includes('回転') && this.parameterPatterns?.angle && !this.parameterPatterns.angle.some(pattern => 
      new RegExp(pattern).test(command))) {
      suggestions.push({
        suggestion: '回転角度を指定してください（例：90度、180度）',
        reason: '回転コマンドに角度が指定されていません',
        confidence: 0.85
      });
    }
    
    return suggestions;
  }

  /**
   * エンジンが初期化されているかチェック
   */
  isReady(): boolean {
    return this.isInitialized && this.tokenizer !== null;
  }

  /**
   * 信頼度閾値を取得
   */
  getConfidenceThreshold(): number {
    return this.confidenceThreshold;
  }
}

// Global NLP engine instance
export const nlpEngine = new NLPEngine();