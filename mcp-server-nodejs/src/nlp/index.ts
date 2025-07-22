/**
 * Natural Language Processing Module
 * Exports all NLP-related functionality for the MCP server
 */

// Core NLP Engine
export { NLPEngine } from './nlp_engine.js';
export type { ParsedIntent, CommandSuggestion } from './nlp_engine.js';

// Command Patterns
export { CommandPatterns } from './command_patterns.js';
export type { CommandPattern, ParameterPattern } from './command_patterns.js';

// Confidence Evaluation
export { ConfidenceEvaluator, confidenceEvaluator } from './confidence_evaluator.js';
export type { ConfidenceEvaluation, ConfidenceMetrics } from './confidence_evaluator.js';

// Default NLP instance for immediate use
import { NLPEngine } from './nlp_engine.js';
import { CommandPatterns } from './command_patterns.js';
import type { ParsedIntent, CommandSuggestion } from './nlp_engine.js';
import type { ConfidenceEvaluation } from './confidence_evaluator.js';

/**
 * Pre-initialized NLP engine instance for convenience
 * This needs to be initialized before use
 */
export const defaultNLPEngine = new NLPEngine();

/**
 * Initialize the default NLP engine
 * This is a convenience function to initialize the shared instance
 */
export async function initializeNLP(): Promise<void> {
  if (!defaultNLPEngine.isReady()) {
    await defaultNLPEngine.initialize();
  }
}

/**
 * Quick parsing function using the default engine
 * Automatically initializes the engine if needed
 */
export async function parseCommand(
  command: string, 
  context?: Record<string, any>
): Promise<ParsedIntent> {
  await initializeNLP();
  return defaultNLPEngine.parseCommand(command, context);
}

/**
 * Quick suggestion function using the default engine
 * Automatically initializes the engine if needed  
 */
export async function suggestCorrections(command: string): Promise<CommandSuggestion[]> {
  await initializeNLP();
  return defaultNLPEngine.suggestCorrections(command);
}

/**
 * All-in-one command processing function
 * Parses command and evaluates confidence in one call
 */
export async function processCommand(
  command: string,
  context?: Record<string, any>
): Promise<{
  intent: ParsedIntent;
  evaluation: ConfidenceEvaluation;
  isExecutable: boolean;
}> {
  // Initialize if needed
  await initializeNLP();
  
  // Parse the command
  const intent = await defaultNLPEngine.parseCommand(command, context);
  
  // Evaluate confidence
  const { confidenceEvaluator } = await import('./confidence_evaluator.js');
  const evaluation = await confidenceEvaluator.evaluateIntent(intent, command);
  
  // Determine if executable
  const isExecutable = confidenceEvaluator.isExecutable(evaluation);
  
  return {
    intent,
    evaluation, 
    isExecutable
  };
}

/**
 * Utility function to validate NLP components
 */
export function validateNLPComponents(): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // Validate command patterns
  const patternValidation = CommandPatterns.validatePatterns();
  if (!patternValidation.valid) {
    errors.push(...patternValidation.errors);
  }
  
  // Check pattern coverage
  const stats = CommandPatterns.getStatistics();
  if (stats.total_actions < 10) {
    warnings.push('Low action pattern coverage');
  }
  
  if (stats.total_parameters < 5) {
    warnings.push('Low parameter pattern coverage');
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Get comprehensive NLP statistics
 */
export function getNLPStatistics(): {
  patterns: ReturnType<typeof CommandPatterns.getStatistics>;
  engine_ready: boolean;
  confidence_threshold: number;
} {
  return {
    patterns: CommandPatterns.getStatistics(),
    engine_ready: defaultNLPEngine.isReady(),
    confidence_threshold: defaultNLPEngine.getConfidenceThreshold()
  };
}

// Note: Types are already exported above