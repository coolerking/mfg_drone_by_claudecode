/**
 * Command Patterns for Natural Language Processing
 * Defines patterns for matching and extracting commands from natural language input
 */

import { logger } from '@/utils/logger.js';

/**
 * コマンドパターンの定義
 */
export interface CommandPattern {
  action: string;
  patterns: string[];
  confidence_base: number;
  required_params?: string[];
  optional_params?: string[];
  examples?: string[];
}

/**
 * パラメータパターンの定義
 */
export interface ParameterPattern {
  name: string;
  patterns: string[];
  type: 'string' | 'number' | 'boolean';
  converter?: (value: string) => any;
  validator?: (value: any) => boolean;
  examples?: string[];
}

/**
 * コマンドパターンマネージャー
 */
export class CommandPatterns {
  
  /**
   * アクションパターンの定義
   */
  static readonly ACTION_PATTERNS: CommandPattern[] = [
    // 接続関連
    {
      action: 'connect',
      patterns: [
        '.*?に?接続',
        '.*?に?繋げ',
        '.*?に?つなが',
        '.*?に?コネクト',
        'connect\\s+to.*?',
        'establish.*?connection'
      ],
      confidence_base: 0.8,
      required_params: [],
      optional_params: ['drone_id'],
      examples: ['ドローンに接続', 'drone_01に接続してください', 'connect to drone']
    },
    {
      action: 'disconnect',
      patterns: [
        '.*?から?切断',
        '接続を?切',
        'ディスコネクト',
        'disconnect.*?',
        'close.*?connection'
      ],
      confidence_base: 0.8,
      required_params: [],
      optional_params: ['drone_id'],
      examples: ['ドローンから切断', 'disconnect drone', '接続を切ってください']
    },
    
    // フライト制御
    {
      action: 'takeoff',
      patterns: [
        '離陸',
        '起動',
        '飛び立',
        'テイクオフ',
        'take\\s*off',
        'launch',
        'lift\\s*off',
        'start\\s*flying'
      ],
      confidence_base: 0.9,
      required_params: [],
      optional_params: ['height', 'altitude'],
      examples: ['離陸してください', 'take off to 2 meters', '高度1.5mで離陸']
    },
    {
      action: 'land',
      patterns: [
        '着陸',
        '降り',
        'ランディング',
        '着地',
        'land',
        'touch\\s*down',
        'come\\s*down'
      ],
      confidence_base: 0.9,
      required_params: [],
      optional_params: ['immediate'],
      examples: ['着陸してください', 'land safely', '緊急着陸']
    },
    {
      action: 'emergency_stop',
      patterns: [
        '緊急停止',
        '止ま',
        'ストップ',
        '停止',
        'emergency.*?stop',
        'stop.*?immediately',
        'abort',
        'panic'
      ],
      confidence_base: 0.95,
      required_params: [],
      optional_params: [],
      examples: ['緊急停止', 'emergency stop', 'すぐに停止してください']
    },
    
    // 移動関連
    {
      action: 'move',
      patterns: [
        '移動',
        '進',
        '動',
        '移',
        '行',
        'move',
        'go',
        'fly',
        'forward',
        'backward',
        'left',
        'right',
        'up',
        'down'
      ],
      confidence_base: 0.8,
      required_params: ['direction'],
      optional_params: ['distance'],
      examples: ['前に2m移動', 'move forward 1.5 meters', '左に50cm動いて']
    },
    {
      action: 'rotate',
      patterns: [
        '回転',
        '回',
        '向き',
        '回る',
        'rotate',
        'turn',
        'spin'
      ],
      confidence_base: 0.8,
      required_params: ['direction'],
      optional_params: ['angle'],
      examples: ['時計回りに90度回転', 'rotate left 180 degrees', '右に45度回って']
    },
    {
      action: 'altitude',
      patterns: [
        '高度',
        '高さ',
        '上昇',
        '下降',
        'altitude',
        'height',
        'climb',
        'descend'
      ],
      confidence_base: 0.8,
      required_params: ['direction'],
      optional_params: ['height', 'distance'],
      examples: ['高度を2m上げて', 'climb to 3 meters', '1m下降してください']
    },
    
    // カメラ関連
    {
      action: 'take_photo',
      patterns: [
        '写真',
        '撮影',
        '撮',
        'フォト',
        'take.*?photo',
        'take.*?picture',
        'capture.*?image',
        'snap'
      ],
      confidence_base: 0.9,
      required_params: [],
      optional_params: ['quality', 'filename'],
      examples: ['写真を撮って', 'take a high quality photo', '高画質で撮影してください']
    },
    {
      action: 'start_streaming',
      patterns: [
        'ストリーミング.*?開始',
        '配信.*?開始',
        '映像.*?開始',
        'start.*?streaming',
        'begin.*?stream',
        'enable.*?video'
      ],
      confidence_base: 0.85,
      required_params: [],
      optional_params: ['quality', 'resolution'],
      examples: ['ストリーミングを開始', 'start video streaming', '映像配信を始めて']
    },
    {
      action: 'stop_streaming',
      patterns: [
        'ストリーミング.*?停止',
        '配信.*?停止',
        '映像.*?停止',
        'stop.*?streaming',
        'end.*?stream',
        'disable.*?video'
      ],
      confidence_base: 0.85,
      required_params: [],
      optional_params: [],
      examples: ['ストリーミングを停止', 'stop video streaming', '映像配信を終了']
    },
    
    // ビジョン関連
    {
      action: 'detect_objects',
      patterns: [
        '物体検出',
        '検出',
        '物体認識',
        '何が見える',
        'detect.*?objects?',
        'find.*?objects?',
        'what.*?can.*?see',
        'identify.*?objects?'
      ],
      confidence_base: 0.8,
      required_params: [],
      optional_params: ['target_class', 'confidence_threshold'],
      examples: ['物体検出してください', 'detect people in the image', '何が見えますか？']
    },
    {
      action: 'start_tracking',
      patterns: [
        '追跡.*?開始',
        '追従.*?開始',
        'トラッキング.*?開始',
        'start.*?tracking',
        'begin.*?following',
        'track.*?object'
      ],
      confidence_base: 0.85,
      required_params: [],
      optional_params: ['target_id', 'target_class'],
      examples: ['物体追跡を開始', 'start tracking person', '人を追従してください']
    },
    {
      action: 'stop_tracking',
      patterns: [
        '追跡.*?停止',
        '追従.*?停止',
        'トラッキング.*?停止',
        'stop.*?tracking',
        'end.*?following',
        'cancel.*?tracking'
      ],
      confidence_base: 0.85,
      required_params: [],
      optional_params: [],
      examples: ['追跡を停止', 'stop tracking', '追従を終了してください']
    },
    
    // システム関連
    {
      action: 'get_status',
      patterns: [
        '状態',
        'ステータス',
        '様子',
        'status',
        'state',
        'condition',
        'how.*?are.*?you'
      ],
      confidence_base: 0.8,
      required_params: [],
      optional_params: ['detailed'],
      examples: ['ステータスを教えて', 'what is the status', 'ドローンの状態は？']
    },
    {
      action: 'health_check',
      patterns: [
        '正常',
        'ヘルス',
        '健康',
        'health.*?check',
        'system.*?check',
        'diagnostic'
      ],
      confidence_base: 0.8,
      required_params: [],
      optional_params: ['full_check'],
      examples: ['ヘルスチェック', 'perform health check', 'システム診断してください']
    }
  ];

  /**
   * パラメータパターンの定義
   */
  static readonly PARAMETER_PATTERNS: ParameterPattern[] = [
    {
      name: 'drone_id',
      patterns: [
        'ドローン([A-Za-z0-9_-]+)',
        'drone[-_]?([A-Za-z0-9_-]+)',
        '([A-Za-z0-9_-]+)番目',
        '([A-Za-z0-9_-]+)番',
        'drone\\s+([A-Za-z0-9_-]+)',
        'id\\s*[：:]\\s*([A-Za-z0-9_-]+)'
      ],
      type: 'string',
      examples: ['ドローン01', 'drone_alpha', '1番目のドローン']
    },
    {
      name: 'distance',
      patterns: [
        '(\\d+(?:\\.\\d+)?)\\s*(?:cm|センチ|センチメートル)',
        '(\\d+(?:\\.\\d+)?)\\s*(?:m|メートル)',
        '(\\d+(?:\\.\\d+)?)\\s*(?:mm|ミリ|ミリメートル)',
        '(\\d+(?:\\.\\d+)?)\\s*(?:meter|metre)s?',
        '(\\d+(?:\\.\\d+)?)\\s*(?:centimeter|cm)s?',
        '(\\d+(?:\\.\\d+)?)\\s*(?:millimeter|mm)s?'
      ],
      type: 'number',
      converter: (value: string): number => {
        const match = value.match(/([\d.]+)\s*(.+)/);
        if (!match || !match[1]) return parseFloat(value);
        
        const num = parseFloat(match[1]);
        const unit = match[2] || '';
        
        // Convert to centimeters
        if (unit.match(/m|メートル|meter|metre/)) {
          return num * 100;
        } else if (unit.match(/mm|ミリ|millimeter/)) {
          return num * 0.1;
        }
        return num; // Already in cm
      },
      validator: (value: number): boolean => value > 0 && value <= 1000, // Max 10m
      examples: ['2.5m', '150cm', '50センチメートル']
    },
    {
      name: 'angle',
      patterns: [
        '(\\d+)\\s*(?:度|°)',
        '(\\d+)\\s*(?:度|°)\\s*(?:回転|回)',
        '(\\d+)\\s*degrees?',
        '(\\d+)\\s*deg'
      ],
      type: 'number',
      converter: (value: string): number => parseInt(value.match(/\d+/)?.[0] || '0', 10),
      validator: (value: number): boolean => value >= 0 && value <= 360,
      examples: ['90度', '180°', '45 degrees']
    },
    {
      name: 'height',
      patterns: [
        '高さ\\s*(\\d+(?:\\.\\d+)?)\\s*(?:cm|センチ|センチメートル)',
        '高さ\\s*(\\d+(?:\\.\\d+)?)\\s*(?:m|メートル)',
        '高度\\s*(\\d+(?:\\.\\d+)?)\\s*(?:cm|センチ|センチメートル)',
        '高度\\s*(\\d+(?:\\.\\d+)?)\\s*(?:m|メートル)',
        'height\\s*(\\d+(?:\\.\\d+)?)\\s*(?:m|meter|metre)s?',
        'altitude\\s*(\\d+(?:\\.\\d+)?)\\s*(?:m|meter|metre)s?'
      ],
      type: 'number',
      converter: (value: string): number => {
        const match = value.match(/([\d.]+)\s*(.+)/);
        if (!match || !match[1]) return parseFloat(value);
        
        const num = parseFloat(match[1]);
        const unit = match[2] || '';
        
        // Convert to centimeters
        if (unit.match(/m|メートル|meter|metre/)) {
          return num * 100;
        }
        return num; // Already in cm
      },
      validator: (value: number): boolean => value > 0 && value <= 1000, // Max 10m
      examples: ['高度2m', 'height 1.5 meters', '高さ120cm']
    },
    {
      name: 'direction',
      patterns: [
        '(右|左|前|後|上|下|forward|backward|back|left|right|up|down)',
        '(時計回り|反時計回り|clockwise|counterclockwise|counter_clockwise|cw|ccw)',
        '(north|south|east|west|北|南|東|西)'
      ],
      type: 'string',
      converter: (value: string): string => {
        const mappings: Record<string, string> = {
          '右': 'right',
          '左': 'left', 
          '前': 'forward',
          '後': 'backward',
          '後ろ': 'backward',
          '上': 'up',
          '下': 'down',
          '時計回り': 'clockwise',
          '反時計回り': 'counterclockwise',
          '北': 'north',
          '南': 'south',
          '東': 'east',
          '西': 'west',
          'back': 'backward',
          'counter_clockwise': 'counterclockwise',
          'cw': 'clockwise',
          'ccw': 'counterclockwise'
        };
        return mappings[value] || value.toLowerCase();
      },
      examples: ['前', 'forward', '時計回り', 'clockwise']
    },
    {
      name: 'quality',
      patterns: [
        '(高|中|低|high|medium|low)\\s*(?:画質|品質|quality)?',
        '(最高|最低|highest|lowest)\\s*(?:画質|品質|quality)?',
        '(ultra|super|basic)\\s*(?:quality)?'
      ],
      type: 'string',
      converter: (value: string): string => {
        const mappings: Record<string, string> = {
          '高': 'high',
          '中': 'medium',
          '低': 'low',
          '最高': 'highest',
          '最低': 'lowest',
          'ultra': 'highest',
          'super': 'high',
          'basic': 'low'
        };
        return mappings[value] || value.toLowerCase();
      },
      examples: ['高画質', 'high quality', '最高品質']
    },
    {
      name: 'filename',
      patterns: [
        'ファイル名\\s*[：:]\\s*([^\\s]+)',
        '名前\\s*[：:]\\s*([^\\s]+)',
        'filename\\s*[:]\\s*([^\\s]+)',
        'name\\s*[:]\\s*([^\\s]+)',
        'save\\s+as\\s+([^\\s]+)',
        'として\\s*([^\\s]+)'
      ],
      type: 'string',
      examples: ['ファイル名: photo001.jpg', 'save as image.png', 'photo001として']
    },
    {
      name: 'target_class',
      patterns: [
        '(人|person|people|human)',
        '(車|car|vehicle|automobile)',
        '(動物|animal|cat|dog|bird)',
        '(物体|object|item|thing)'
      ],
      type: 'string',
      converter: (value: string): string => {
        const mappings: Record<string, string> = {
          '人': 'person',
          '車': 'car',
          '動物': 'animal',
          '物体': 'object'
        };
        return mappings[value] || value.toLowerCase();
      },
      examples: ['人を検出', 'detect cars', '動物を追跡']
    },
    {
      name: 'confidence_threshold',
      patterns: [
        '信頼度\\s*(\\d+(?:\\.\\d+)?)%?',
        'confidence\\s*(\\d+(?:\\.\\d+)?)%?',
        'threshold\\s*(\\d+(?:\\.\\d+)?)%?',
        '閾値\\s*(\\d+(?:\\.\\d+)?)%?'
      ],
      type: 'number',
      converter: (value: string): number => {
        const num = parseFloat(value.match(/[\d.]+/)?.[0] || '0');
        return num > 1 ? num / 100 : num; // Convert percentage to decimal if needed
      },
      validator: (value: number): boolean => value >= 0 && value <= 1,
      examples: ['信頼度80%', 'confidence 0.75', 'threshold 85%']
    }
  ];

  /**
   * アクションパターンを取得
   */
  static getActionPatterns(): CommandPattern[] {
    return this.ACTION_PATTERNS;
  }

  /**
   * パラメータパターンを取得
   */
  static getParameterPatterns(): ParameterPattern[] {
    return this.PARAMETER_PATTERNS;
  }

  /**
   * 特定のアクションのパターンを取得
   */
  static getActionPattern(action: string): CommandPattern | null {
    return this.ACTION_PATTERNS.find(pattern => pattern.action === action) || null;
  }

  /**
   * 特定のパラメータのパターンを取得
   */
  static getParameterPattern(paramName: string): ParameterPattern | null {
    return this.PARAMETER_PATTERNS.find(pattern => pattern.name === paramName) || null;
  }

  /**
   * すべてのアクション名を取得
   */
  static getAllActionNames(): string[] {
    return this.ACTION_PATTERNS.map(pattern => pattern.action);
  }

  /**
   * すべてのパラメータ名を取得
   */
  static getAllParameterNames(): string[] {
    return this.PARAMETER_PATTERNS.map(pattern => pattern.name);
  }

  /**
   * パターンの統計情報を取得
   */
  static getStatistics(): {
    total_actions: number;
    total_parameters: number;
    total_patterns: number;
    action_coverage: Record<string, number>;
  } {
    const totalPatterns = this.ACTION_PATTERNS.reduce((sum, ap) => sum + ap.patterns.length, 0) +
                         this.PARAMETER_PATTERNS.reduce((sum, pp) => sum + pp.patterns.length, 0);
    
    const actionCoverage: Record<string, number> = {};
    this.ACTION_PATTERNS.forEach(pattern => {
      actionCoverage[pattern.action] = pattern.patterns.length;
    });

    return {
      total_actions: this.ACTION_PATTERNS.length,
      total_parameters: this.PARAMETER_PATTERNS.length,
      total_patterns: totalPatterns,
      action_coverage: actionCoverage
    };
  }

  /**
   * パターンの妥当性をチェック
   */
  static validatePatterns(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Action patterns validation
    for (const actionPattern of this.ACTION_PATTERNS) {
      if (!actionPattern.action || actionPattern.action.trim() === '') {
        errors.push(`Action pattern missing action name`);
      }
      
      if (!actionPattern.patterns || actionPattern.patterns.length === 0) {
        errors.push(`Action '${actionPattern.action}' has no patterns`);
      }

      for (const pattern of actionPattern.patterns) {
        try {
          new RegExp(pattern);
        } catch (e) {
          errors.push(`Invalid regex pattern in action '${actionPattern.action}': ${pattern}`);
        }
      }
    }

    // Parameter patterns validation  
    for (const paramPattern of this.PARAMETER_PATTERNS) {
      if (!paramPattern.name || paramPattern.name.trim() === '') {
        errors.push(`Parameter pattern missing name`);
      }

      if (!paramPattern.patterns || paramPattern.patterns.length === 0) {
        errors.push(`Parameter '${paramPattern.name}' has no patterns`);
      }

      for (const pattern of paramPattern.patterns) {
        try {
          new RegExp(pattern);
        } catch (e) {
          errors.push(`Invalid regex pattern in parameter '${paramPattern.name}': ${pattern}`);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}

logger.info('Command patterns loaded successfully', CommandPatterns.getStatistics());