import { EventEmitter } from 'node:events';
import { log, Timer } from './logger.js';

/**
 * プログレスインジケータシステム
 * - タスクの進捗管理と表示
 * - リアルタイム進捗更新
 * - 入れ子タスクの管理
 * - パフォーマンス測定
 * - WebSocket経由のリアルタイム通知
 */

export interface ProgressStep {
  id: string;
  name: string;
  description?: string | undefined;
  weight?: number | undefined; // 重み付け（デフォルト: 1）
  completed: boolean;
  error?: Error | undefined;
  startTime?: Date | undefined;
  endTime?: Date | undefined;
  duration?: number | undefined;
  metadata?: Record<string, any> | undefined;
}

export interface ProgressOptions {
  id?: string | undefined;
  title: string;
  description?: string | undefined;
  showProgress?: boolean | undefined;
  showTime?: boolean | undefined;
  showPercentage?: boolean | undefined;
  autoStart?: boolean | undefined;
  logLevel?: 'debug' | 'info' | 'warn' | 'error' | undefined;
  onUpdate?: ((progress: ProgressData) => void) | undefined;
  onComplete?: ((progress: ProgressData) => void) | undefined;
  onError?: ((error: Error, progress: ProgressData) => void) | undefined;
}

export interface ProgressData {
  id: string;
  title: string;
  description?: string | undefined;
  totalSteps: number;
  completedSteps: number;
  currentStep?: ProgressStep | undefined;
  percentage: number;
  isRunning: boolean;
  isCompleted: boolean;
  hasError: boolean;
  error?: Error | undefined;
  startTime?: Date | undefined;
  endTime?: Date | undefined;
  duration?: number | undefined;
  estimatedTimeRemaining?: number | undefined;
  steps: ProgressStep[];
  metadata?: Record<string, any> | undefined;
}

export interface ProgressUpdate {
  type: 'start' | 'progress' | 'step_start' | 'step_complete' | 'step_error' | 'complete' | 'error';
  progress: ProgressData;
  step?: ProgressStep | undefined;
  timestamp: Date;
}

/**
 * プログレスインジケータクラス
 */
export class ProgressIndicator extends EventEmitter {
  private progress: ProgressData;
  private options: ProgressOptions;
  private timer?: Timer;
  private stepTimers: Map<string, Timer> = new Map();

  constructor(options: ProgressOptions) {
    super();
    
    this.options = {
      showProgress: true,
      showTime: true,
      showPercentage: true,
      autoStart: false,
      logLevel: 'info',
      ...options
    };

    this.progress = {
      id: options.id || this.generateId(),
      title: options.title,
      description: options.description || undefined,
      totalSteps: 0,
      completedSteps: 0,
      currentStep: undefined,
      percentage: 0,
      isRunning: false,
      isCompleted: false,
      hasError: false,
      error: undefined,
      startTime: undefined,
      endTime: undefined,
      duration: undefined,
      estimatedTimeRemaining: undefined,
      steps: [],
      metadata: undefined,
    };

    if (this.options.autoStart) {
      this.start();
    }
  }

  /**
   * 進捗を開始
   */
  start(): void {
    if (this.progress.isRunning) {
      log.warn(`Progress "${this.progress.title}" is already running`, { 
        progressId: this.progress.id 
      });
      return;
    }

    this.progress.isRunning = true;
    this.progress.startTime = new Date();
    this.timer = new Timer(`Progress: ${this.progress.title}`, this.progress.id);
    
    this.logProgress('info', `Started: ${this.progress.title}`);
    this.emitUpdate('start');
  }

  /**
   * ステップを追加
   */
  addStep(name: string, description?: string, weight?: number): string {
    const stepId = this.generateId();
    const step: ProgressStep = {
      id: stepId,
      name,
      description: description || undefined,
      weight: weight || 1,
      completed: false,
      error: undefined,
      startTime: undefined,
      endTime: undefined,
      duration: undefined,
      metadata: undefined,
    };

    this.progress.steps.push(step);
    this.progress.totalSteps = this.progress.steps.length;
    this.updatePercentage();

    this.logProgress('debug', `Added step: ${name}`, { stepId, step });
    return stepId;
  }

  /**
   * 複数ステップを一括追加
   */
  addSteps(steps: Array<{ name: string; description?: string; weight?: number }>): string[] {
    const stepIds: string[] = [];
    
    for (const stepData of steps) {
      const stepId = this.addStep(stepData.name, stepData.description, stepData.weight);
      stepIds.push(stepId);
    }

    this.logProgress('info', `Added ${steps.length} steps`, { stepIds });
    return stepIds;
  }

  /**
   * ステップを開始
   */
  startStep(stepId: string, metadata?: Record<string, any>): void {
    const step = this.findStep(stepId);
    if (!step) {
      throw new Error(`Step not found: ${stepId}`);
    }

    if (step.completed) {
      log.warn(`Step "${step.name}" is already completed`, { stepId });
      return;
    }

    step.startTime = new Date();
    step.metadata = { ...step.metadata, ...metadata };
    this.progress.currentStep = step;

    // ステップ用タイマーを開始
    const timer = new Timer(`Step: ${step.name}`, stepId);
    this.stepTimers.set(stepId, timer);

    this.logProgress('debug', `Started step: ${step.name}`, { stepId, step });
    this.emitUpdate('step_start', step);
  }

  /**
   * ステップを完了
   */
  completeStep(stepId: string, metadata?: Record<string, any>): void {
    const step = this.findStep(stepId);
    if (!step) {
      throw new Error(`Step not found: ${stepId}`);
    }

    if (step.completed) {
      log.warn(`Step "${step.name}" is already completed`, { stepId });
      return;
    }

    step.completed = true;
    step.endTime = new Date();
    step.metadata = { ...step.metadata, ...metadata };

    // タイマーを終了
    const timer = this.stepTimers.get(stepId);
    if (timer) {
      step.duration = timer.finish(`Step completed: ${step.name}`);
      this.stepTimers.delete(stepId);
    }

    this.progress.completedSteps++;
    this.updatePercentage();
    this.updateEstimatedTime();

    // 現在のステップを更新
    if (this.progress.currentStep?.id === stepId) {
      this.progress.currentStep = this.getNextStep();
    }

    this.logProgress('info', `Completed step: ${step.name}`, { 
      stepId, 
      duration: step.duration,
      percentage: this.progress.percentage
    });
    
    this.emitUpdate('step_complete', step);

    // 全ステップ完了チェック
    if (this.isAllStepsCompleted()) {
      this.complete();
    }
  }

  /**
   * ステップでエラーが発生
   */
  errorStep(stepId: string, error: Error, metadata?: Record<string, any>): void {
    const step = this.findStep(stepId);
    if (!step) {
      throw new Error(`Step not found: ${stepId}`);
    }

    step.error = error;
    step.endTime = new Date();
    step.metadata = { ...step.metadata, ...metadata };

    // タイマーを終了
    const timer = this.stepTimers.get(stepId);
    if (timer) {
      step.duration = timer.finishWithError(error, `Step failed: ${step.name}`);
      this.stepTimers.delete(stepId);
    }

    this.progress.hasError = true;
    this.progress.error = error;

    this.logProgress('error', `Step failed: ${step.name}`, { 
      stepId, 
      error: error.message,
      duration: step.duration
    });

    this.emitUpdate('step_error', step);
    
    // エラーハンドラーを呼び出し
    if (this.options.onError) {
      this.options.onError(error, this.progress);
    }
  }

  /**
   * 進捗を手動更新
   */
  updateProgress(completedSteps?: number, metadata?: Record<string, any>): void {
    if (completedSteps !== undefined) {
      this.progress.completedSteps = Math.min(completedSteps, this.progress.totalSteps);
      this.updatePercentage();
    }

    if (metadata) {
      this.progress.metadata = { ...this.progress.metadata, ...metadata };
    }

    this.updateEstimatedTime();
    this.emitUpdate('progress');
  }

  /**
   * 進捗を完了
   */
  complete(metadata?: Record<string, any>): void {
    if (this.progress.isCompleted) {
      log.warn(`Progress "${this.progress.title}" is already completed`, { 
        progressId: this.progress.id 
      });
      return;
    }

    this.progress.isCompleted = true;
    this.progress.isRunning = false;
    this.progress.endTime = new Date();
    this.progress.percentage = 100;

    if (metadata) {
      this.progress.metadata = { ...this.progress.metadata, ...metadata };
    }

    // メインタイマーを終了
    if (this.timer) {
      this.progress.duration = this.timer.finish(`Progress completed: ${this.progress.title}`);
    }

    // 未完了のステップタイマーを終了
    for (const [stepId, timer] of this.stepTimers) {
      const step = this.findStep(stepId);
      if (step && !step.completed) {
        timer.finish(`Step completed by progress end: ${step.name}`);
      }
    }
    this.stepTimers.clear();

    this.logProgress('info', `Completed: ${this.progress.title}`, { 
      duration: this.progress.duration,
      totalSteps: this.progress.totalSteps,
      completedSteps: this.progress.completedSteps
    });

    this.emitUpdate('complete');

    // 完了ハンドラーを呼び出し
    if (this.options.onComplete) {
      this.options.onComplete(this.progress);
    }
  }

  /**
   * 進捗をエラーで終了
   */
  error(error: Error, metadata?: Record<string, any>): void {
    this.progress.hasError = true;
    this.progress.error = error;
    this.progress.isRunning = false;
    this.progress.endTime = new Date();

    if (metadata) {
      this.progress.metadata = { ...this.progress.metadata, ...metadata };
    }

    // メインタイマーを終了
    if (this.timer) {
      this.progress.duration = this.timer.finishWithError(error, `Progress failed: ${this.progress.title}`);
    }

    // 未完了のステップタイマーを終了
    for (const [stepId, timer] of this.stepTimers) {
      const step = this.findStep(stepId);
      if (step && !step.completed) {
        timer.finishWithError(error, `Step interrupted by progress error: ${step.name}`);
      }
    }
    this.stepTimers.clear();

    this.logProgress('error', `Failed: ${this.progress.title}`, { 
      error: error.message,
      duration: this.progress.duration
    });

    this.emitUpdate('error');

    // エラーハンドラーを呼び出し
    if (this.options.onError) {
      this.options.onError(error, this.progress);
    }
  }

  /**
   * 現在の進捗データを取得
   */
  getData(): ProgressData {
    return { ...this.progress };
  }

  /**
   * 進捗状況を文字列として取得
   */
  toString(): string {
    const percentage = this.options.showPercentage ? ` (${this.progress.percentage.toFixed(1)}%)` : '';
    const time = this.options.showTime && this.progress.duration ? ` [${this.formatDuration(this.progress.duration)}]` : '';
    const eta = this.progress.estimatedTimeRemaining ? ` ETA: ${this.formatDuration(this.progress.estimatedTimeRemaining)}` : '';
    
    return `${this.progress.title}: ${this.progress.completedSteps}/${this.progress.totalSteps}${percentage}${time}${eta}`;
  }

  /**
   * プログレスバーを文字列として取得
   */
  getProgressBar(width: number = 40): string {
    const percentage = this.progress.percentage / 100;
    const filled = Math.round(width * percentage);
    const empty = width - filled;
    
    return `[${'='.repeat(filled)}${' '.repeat(empty)}] ${this.progress.percentage.toFixed(1)}%`;
  }

  // Private methods

  private generateId(): string {
    return `progress_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private findStep(stepId: string): ProgressStep | undefined {
    return this.progress.steps.find(step => step.id === stepId);
  }

  private getNextStep(): ProgressStep | undefined {
    return this.progress.steps.find(step => !step.completed && !step.error);
  }

  private isAllStepsCompleted(): boolean {
    return this.progress.steps.length > 0 && 
           this.progress.steps.every(step => step.completed || step.error);
  }

  private updatePercentage(): void {
    if (this.progress.totalSteps === 0) {
      this.progress.percentage = 0;
      return;
    }

    // 重み付きパーセンテージ計算
    const totalWeight = this.progress.steps.reduce((sum, step) => sum + (step.weight || 1), 0);
    const completedWeight = this.progress.steps
      .filter(step => step.completed)
      .reduce((sum, step) => sum + (step.weight || 1), 0);
    
    this.progress.percentage = totalWeight > 0 ? (completedWeight / totalWeight) * 100 : 0;
  }

  private updateEstimatedTime(): void {
    if (this.progress.completedSteps === 0 || !this.progress.startTime) {
      this.progress.estimatedTimeRemaining = undefined;
      return;
    }

    const elapsedTime = Date.now() - this.progress.startTime.getTime();
    const averageTimePerStep = elapsedTime / this.progress.completedSteps;
    const remainingSteps = this.progress.totalSteps - this.progress.completedSteps;
    
    this.progress.estimatedTimeRemaining = remainingSteps * averageTimePerStep;
  }

  private logProgress(level: string, message: string, metadata?: Record<string, any>): void {
    if (this.options.logLevel && this.shouldLog(level)) {
      const logMeta = {
        progressId: this.progress.id,
        title: this.progress.title,
        percentage: this.progress.percentage,
        ...metadata
      };

      switch (level) {
        case 'debug':
          log.debug(message, logMeta);
          break;
        case 'info':
          log.info(message, logMeta);
          break;
        case 'warn':
          log.warn(message, logMeta);
          break;
        case 'error':
          log.error(message, logMeta);
          break;
      }
    }
  }

  private shouldLog(level: string): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    const currentLevelIndex = levels.indexOf(this.options.logLevel || 'info');
    const messageLevelIndex = levels.indexOf(level);
    return messageLevelIndex >= currentLevelIndex;
  }

  private emitUpdate(type: ProgressUpdate['type'], step?: ProgressStep): void {
    const update: ProgressUpdate = {
      type,
      progress: { ...this.progress },
      step: step ? { ...step } : undefined,
      timestamp: new Date(),
    };

    this.emit('update', update);
    this.emit(type, update);

    // カスタムアップデートハンドラーを呼び出し
    if (this.options.onUpdate) {
      this.options.onUpdate(this.progress);
    }
  }

  private formatDuration(milliseconds: number): string {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }
}

/**
 * グローバル進捗管理
 */
class ProgressManager {
  private progresses: Map<string, ProgressIndicator> = new Map();

  /**
   * 新しい進捗インジケータを作成
   */
  create(options: ProgressOptions): ProgressIndicator {
    const progress = new ProgressIndicator(options);
    this.progresses.set(progress.getData().id, progress);
    
    // 完了またはエラー時に自動削除
    progress.once('complete', () => {
      setTimeout(() => this.remove(progress.getData().id), 5000); // 5秒後に削除
    });
    
    progress.once('error', () => {
      setTimeout(() => this.remove(progress.getData().id), 10000); // 10秒後に削除
    });

    return progress;
  }

  /**
   * 進捗インジケータを取得
   */
  get(id: string): ProgressIndicator | undefined {
    return this.progresses.get(id);
  }

  /**
   * 全ての進捗インジケータを取得
   */
  getAll(): ProgressIndicator[] {
    return Array.from(this.progresses.values());
  }

  /**
   * アクティブな進捗インジケータを取得
   */
  getActive(): ProgressIndicator[] {
    return this.getAll().filter(progress => {
      const data = progress.getData();
      return data.isRunning && !data.isCompleted && !data.hasError;
    });
  }

  /**
   * 進捗インジケータを削除
   */
  remove(id: string): boolean {
    const progress = this.progresses.get(id);
    if (progress) {
      progress.removeAllListeners();
      this.progresses.delete(id);
      return true;
    }
    return false;
  }

  /**
   * 全ての進捗インジケータをクリア
   */
  clear(): void {
    for (const progress of this.progresses.values()) {
      progress.removeAllListeners();
    }
    this.progresses.clear();
  }

  /**
   * 統計情報を取得
   */
  getStats(): {
    total: number;
    active: number;
    completed: number;
    failed: number;
  } {
    const all = this.getAll();
    const stats = {
      total: all.length,
      active: 0,
      completed: 0,
      failed: 0,
    };

    for (const progress of all) {
      const data = progress.getData();
      if (data.isRunning && !data.isCompleted && !data.hasError) {
        stats.active++;
      } else if (data.isCompleted && !data.hasError) {
        stats.completed++;
      } else if (data.hasError) {
        stats.failed++;
      }
    }

    return stats;
  }
}

// グローバル進捗マネージャー
export const progressManager = new ProgressManager();

// エクスポート
export { ProgressManager };
export default ProgressIndicator;