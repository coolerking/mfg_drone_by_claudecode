import { BaseTool } from './BaseTool.js';
import { type MCPToolResponse } from '@/types/index.js';
import { logger } from '@/utils/logger.js';

/**
 * 自然言語コマンド実行ツール（基本版）
 * 自然言語でのドローン制御コマンドを解析・実行する
 */
export class ExecuteNaturalLanguageCommandTool extends BaseTool {
  constructor(droneService: any) {
    super(droneService, 'execute_natural_language_command');
  }

  getDescription(): string {
    return 'Execute drone commands using natural language. This basic version supports simple movement and control commands in English and Japanese.';
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
          description: 'Natural language command (e.g., "fly forward 2 meters", "take a photo", "land safely")',
        },
        language: {
          type: 'string',
          enum: ['en', 'ja', 'auto'],
          description: 'Language of the command (optional, default: auto-detect)',
          default: 'auto',
        },
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
      
      logger.info(`Processing natural language command for drone ${droneId}: "${command}"`);

      // ドローンの状態確認
      await this.validateAndGetDrone(droneId);

      // コマンドを解析
      const parsedCommand = this.parseNaturalLanguageCommand(command, language);

      if (!parsedCommand) {
        throw new Error(`Could not understand the command: "${command}". Please try rephrasing or use more specific terms.`);
      }

      logger.info(`Parsed command:`, parsedCommand);

      // コマンド実行
      const result = await this.droneService.executeCommand(
        droneId, 
        parsedCommand.action, 
        parsedCommand.params
      );

      if (result.success) {
        return this.createSuccessResponse(
          `Natural language command executed successfully for drone '${droneId}': "${command}" → ${parsedCommand.description}. ${result.message}`
        );
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      return this.createErrorResponse(error);
    }
  }

  /**
   * 自然言語コマンドを解析（基本版）
   */
  private parseNaturalLanguageCommand(
    command: string, 
    language: string
  ): { action: string; params: Record<string, unknown>; description: string } | null {
    const cmd = command.toLowerCase().trim();
    
    // 基本的なパターンマッチング（英語）
    if (language === 'en' || language === 'auto') {
      // 接続コマンド
      if (/connect|establish.connection/.test(cmd)) {
        return {
          action: 'connect',
          params: {},
          description: 'Connect to drone',
        };
      }

      // 離陸コマンド  
      if (/take.?off|launch|lift.?off|start.flying/.test(cmd)) {
        const altMatch = cmd.match(/(\d+(?:\.\d+)?)\s*(?:meter|metre|m)/);
        const altitude = altMatch && altMatch[1] ? parseFloat(altMatch[1]) : 1.2;
        
        return {
          action: 'takeoff',
          params: { altitude },
          description: `Take off to ${altitude}m altitude`,
        };
      }

      // 着陸コマンド
      if (/land|touch.down|come.down/.test(cmd)) {
        const immediate = /emergency|immediately|now|quick/.test(cmd);
        
        return {
          action: 'land',
          params: { immediate },
          description: immediate ? 'Emergency landing' : 'Safe landing',
        };
      }

      // 移動コマンド
      const moveMatch = cmd.match(/(forward|backward|left|right|up|down)\s*(\d+(?:\.\d+)?)\s*(?:meter|metre|m)/);
      if (moveMatch && moveMatch[1] && moveMatch[2]) {
        const direction = moveMatch[1];
        const distance = parseFloat(moveMatch[2]);
        
        return {
          action: 'move',
          params: { direction, distance },
          description: `Move ${direction} ${distance}m`,
        };
      }

      // 回転コマンド
      const rotateMatch = cmd.match(/(rotate|turn)\s*(clockwise|counterclockwise|cw|ccw|left|right)\s*(\d+)\s*(?:degree|deg|°)/);
      if (rotateMatch && rotateMatch[2] && rotateMatch[3]) {
        let direction = rotateMatch[2];
        if (direction === 'left') direction = 'counterclockwise';
        if (direction === 'right') direction = 'clockwise';
        
        const angle = parseInt(rotateMatch[3]);
        
        return {
          action: 'rotate',
          params: { direction, angle },
          description: `Rotate ${direction} ${angle}°`,
        };
      }

      // 写真撮影コマンド
      if (/take.*(photo|picture|shot)|capture.*image|snap/.test(cmd)) {
        return {
          action: 'take_photo',
          params: { quality: 'high', format: 'jpg' },
          description: 'Take a photo',
        };
      }

      // 緊急停止コマンド
      if (/emergency.stop|stop.immediately|abort|panic/.test(cmd)) {
        return {
          action: 'emergency_stop',
          params: {},
          description: 'Emergency stop',
        };
      }
    }

    // 基本的なパターンマッチング（日本語）
    if (language === 'ja' || language === 'auto') {
      // 接続
      if (/接続|つなが/.test(cmd)) {
        return {
          action: 'connect',
          params: {},
          description: 'ドローンに接続',
        };
      }

      // 離陸
      if (/離陸|飛び立|上昇/.test(cmd)) {
        const altMatch = cmd.match(/(\d+(?:\.\d+)?)\s*(?:メートル|m)/);
        const altitude = altMatch && altMatch[1] ? parseFloat(altMatch[1]) : 1.2;
        
        return {
          action: 'takeoff',
          params: { altitude },
          description: `${altitude}mまで離陸`,
        };
      }

      // 着陸
      if (/着陸|降り|下降/.test(cmd)) {
        const immediate = /緊急|すぐ|即座/.test(cmd);
        
        return {
          action: 'land',
          params: { immediate },
          description: immediate ? '緊急着陸' : '安全着陸',
        };
      }

      // 移動
      const jaMovePatter = /(前|後ろ|左|右|上|下)に?\s*(\d+(?:\.\d+)?)\s*(?:メートル|m)/;
      const jaMoveMatch = cmd.match(jaMovePatter);
      if (jaMoveMatch && jaMoveMatch[1] && jaMoveMatch[2]) {
        const dirMap: Record<string, string> = {
          '前': 'forward',
          '後ろ': 'backward', 
          '左': 'left',
          '右': 'right',
          '上': 'up',
          '下': 'down',
        };
        
        const direction = dirMap[jaMoveMatch[1]];
        const distance = parseFloat(jaMoveMatch[2]);
        
        return {
          action: 'move',
          params: { direction, distance },
          description: `${jaMoveMatch[1]}に${distance}m移動`,
        };
      }

      // 回転
      const jaRotateMatch = cmd.match(/(時計回り|反時計回り|右回り|左回り)\s*(\d+)\s*(?:度|°)/);
      if (jaRotateMatch && jaRotateMatch[1] && jaRotateMatch[2]) {
        const dirMap: Record<string, string> = {
          '時計回り': 'clockwise',
          '反時計回り': 'counterclockwise',
          '右回り': 'clockwise',
          '左回り': 'counterclockwise',
        };
        
        const direction = dirMap[jaRotateMatch[1]];
        const angle = parseInt(jaRotateMatch[2]);
        
        return {
          action: 'rotate',
          params: { direction, angle },
          description: `${jaRotateMatch[1]}に${angle}度回転`,
        };
      }

      // 写真撮影
      if (/写真|撮影|写|カメラ/.test(cmd)) {
        return {
          action: 'take_photo',
          params: { quality: 'high', format: 'jpg' },
          description: '写真を撮影',
        };
      }

      // 緊急停止
      if (/緊急停止|緊急|停止|ストップ/.test(cmd)) {
        return {
          action: 'emergency_stop',
          params: {},
          description: '緊急停止',
        };
      }
    }

    return null;
  }
}