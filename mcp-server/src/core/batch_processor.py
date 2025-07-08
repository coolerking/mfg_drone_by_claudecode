"""
Advanced Batch Processor for MCP Server - Phase 2
Implements dependency analysis, execution optimization, and error recovery
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..models.command_models import (
    ParsedIntent, CommandResponse, BatchCommandResponse, 
    BatchCommandSummary, NaturalLanguageCommand
)
from .enhanced_nlp_engine import ParsedCommand, EnhancedNLPEngine, ConfidenceLevel
from .enhanced_command_router import EnhancedCommandRouter, CommandPriority, DependencyType
from config.logging import get_logger


logger = get_logger(__name__)


class BatchExecutionMode(Enum):
    """Batch execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    OPTIMIZED = "optimized"      # Smart optimization based on dependencies
    PRIORITY_BASED = "priority"  # Execute by priority levels


class ErrorRecoveryStrategy(Enum):
    """Error recovery strategies"""
    STOP_ON_ERROR = "stop_on_error"
    CONTINUE_ON_ERROR = "continue_on_error"
    RETRY_AND_CONTINUE = "retry_and_continue"
    SMART_RECOVERY = "smart_recovery"  # Context-aware recovery


@dataclass
class BatchExecutionContext:
    """Context for batch execution"""
    execution_mode: BatchExecutionMode
    error_recovery: ErrorRecoveryStrategy
    max_retries: int = 2
    retry_delay: float = 1.0
    timeout_per_command: float = 30.0
    max_parallel_commands: int = 5
    priority_weights: Dict[CommandPriority, float] = field(default_factory=lambda: {
        CommandPriority.EMERGENCY: 1.0,
        CommandPriority.HIGH: 0.8,
        CommandPriority.NORMAL: 0.6,
        CommandPriority.LOW: 0.4
    })


@dataclass
class CommandExecution:
    """Individual command execution state"""
    command_index: int
    parsed_command: ParsedCommand
    status: str = "pending"  # pending, running, completed, failed, skipped
    result: Optional[CommandResponse] = None
    attempts: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dependencies: List[int] = field(default_factory=list)
    dependents: List[int] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class BatchExecutionState:
    """Overall batch execution state"""
    executions: List[CommandExecution]
    context: BatchExecutionContext
    start_time: datetime
    completion_estimates: Dict[int, float] = field(default_factory=dict)
    resource_locks: Dict[str, Set[int]] = field(default_factory=dict)  # drone_id -> command_indices
    execution_groups: List[List[int]] = field(default_factory=list)
    current_group_index: int = 0
    total_estimated_time: float = 0.0


class AdvancedBatchProcessor:
    """Advanced batch processor with dependency analysis and optimization"""
    
    def __init__(self, nlp_engine: EnhancedNLPEngine, command_router: EnhancedCommandRouter):
        """Initialize batch processor"""
        self.nlp_engine = nlp_engine
        self.command_router = command_router
        
        # Execution time estimates (in seconds)
        self.execution_time_estimates = {
            "connect": 2.0, "disconnect": 1.0,
            "takeoff": 5.0, "land": 3.0, "emergency": 0.5,
            "move": 3.0, "rotate": 2.0, "altitude": 4.0,
            "photo": 1.5, "streaming": 1.0, "learning": 30.0,
            "detection": 2.5, "tracking": 1.0,
            "status": 0.5, "health": 0.5
        }
        
        # Command dependencies
        self.dependency_rules = {
            "takeoff": {"requires": ["connect"], "conflicts": ["land"]},
            "move": {"requires": ["connect", "takeoff"], "conflicts": ["land", "emergency"]},
            "rotate": {"requires": ["connect", "takeoff"], "conflicts": ["move", "emergency"]},
            "altitude": {"requires": ["connect", "takeoff"], "conflicts": ["land"]},
            "photo": {"requires": ["connect"]},
            "streaming": {"requires": ["connect"]},
            "learning": {"requires": ["connect", "takeoff"]},
            "detection": {"requires": ["connect"]},
            "tracking": {"requires": ["connect"]},
            "land": {"requires": ["connect"], "conflicts": ["takeoff", "move", "rotate", "altitude"]},
            "emergency": {"requires": ["connect"], "conflicts": ["move", "rotate", "altitude"]},
            "disconnect": {"conflicts": ["takeoff", "move", "rotate", "altitude", "photo", "streaming", "learning", "detection", "tracking"]}
        }
        
        logger.info("Advanced batch processor initialized")
    
    async def process_batch(self, commands: List[NaturalLanguageCommand], 
                          context: BatchExecutionContext) -> BatchCommandResponse:
        """Process batch of commands with advanced optimization"""
        logger.info(f"Processing batch of {len(commands)} commands with mode: {context.execution_mode.value}")
        
        start_time = datetime.now()
        
        try:
            # Parse all commands first
            parsed_commands = []
            parsing_errors = []
            
            for i, cmd in enumerate(commands):
                try:
                    parsed_cmd = self.nlp_engine.parse_command(cmd.command, cmd.context)
                    parsed_commands.append(parsed_cmd)
                except Exception as e:
                    logger.error(f"Failed to parse command {i+1}: {str(e)}")
                    parsing_errors.append((i, str(e)))
                    # Create dummy parsed command for error tracking
                    dummy_intent = ParsedIntent(action="unknown", parameters={}, confidence=0.0)
                    dummy_parsed = ParsedCommand(
                        primary_intent=dummy_intent,
                        alternative_intents=[],
                        confidence_level=ConfidenceLevel.VERY_LOW,
                        parameter_confidence={},
                        missing_parameters=[],
                        suggestions=[f"Failed to parse: {str(e)}"]
                    )
                    parsed_commands.append(dummy_parsed)
            
            # Create execution state
            execution_state = self._create_execution_state(parsed_commands, context)
            
            # Analyze dependencies and create execution plan
            self._analyze_dependencies(execution_state)
            self._create_execution_plan(execution_state)
            
            logger.info(f"Execution plan: {len(execution_state.execution_groups)} groups, "
                       f"estimated time: {execution_state.total_estimated_time:.2f}s")
            
            # Execute according to plan
            results = await self._execute_batch(execution_state)
            
            # Handle parsing errors
            for error_index, error_msg in parsing_errors:
                if error_index < len(results):
                    results[error_index] = CommandResponse(
                        success=False,
                        message=f"Parsing error: {error_msg}",
                        timestamp=datetime.now()
                    )
            
            # Calculate statistics
            total_execution_time = (datetime.now() - start_time).total_seconds()
            successful_commands = sum(1 for r in results if r.success)
            failed_commands = len(results) - successful_commands
            
            # Create summary
            summary = BatchCommandSummary(
                total_commands=len(commands),
                successful_commands=successful_commands,
                failed_commands=failed_commands,
                total_execution_time=total_execution_time
            )
            
            # Create response with optimization details
            response = BatchCommandResponse(
                success=failed_commands == 0,
                message=f"Advanced batch processing completed: {successful_commands}/{len(commands)} successful",
                results=results,
                summary=summary
            )
            
            # Add execution analytics
            response.result = {
                "execution_analytics": self._generate_execution_analytics(execution_state, total_execution_time),
                "optimization_details": {
                    "mode": context.execution_mode.value,
                    "groups": len(execution_state.execution_groups),
                    "estimated_time": execution_state.total_estimated_time,
                    "actual_time": total_execution_time,
                    "efficiency_ratio": execution_state.total_estimated_time / total_execution_time if total_execution_time > 0 else 1.0,
                    "parallelization_factor": self._calculate_parallelization_factor(execution_state)
                }
            }
            
            logger.info(f"Advanced batch processing completed: {successful_commands}/{len(commands)} successful in {total_execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in advanced batch processing: {str(e)}")
            total_execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create error response
            summary = BatchCommandSummary(
                total_commands=len(commands),
                successful_commands=0,
                failed_commands=len(commands),
                total_execution_time=total_execution_time
            )
            
            return BatchCommandResponse(
                success=False,
                message=f"Batch processing failed: {str(e)}",
                results=[],
                summary=summary
            )
    
    def _create_execution_state(self, parsed_commands: List[ParsedCommand], 
                              context: BatchExecutionContext) -> BatchExecutionState:
        """Create initial execution state"""
        executions = []
        
        for i, parsed_cmd in enumerate(parsed_commands):
            execution = CommandExecution(
                command_index=i,
                parsed_command=parsed_cmd
            )
            executions.append(execution)
        
        return BatchExecutionState(
            executions=executions,
            context=context,
            start_time=datetime.now()
        )
    
    def _analyze_dependencies(self, execution_state: BatchExecutionState):
        """Analyze command dependencies"""
        executions = execution_state.executions
        
        for i, exec1 in enumerate(executions):
            action1 = exec1.parsed_command.primary_intent.action
            drone_id1 = exec1.parsed_command.primary_intent.parameters.get("drone_id")
            
            for j, exec2 in enumerate(executions):
                if i == j:
                    continue
                
                action2 = exec2.parsed_command.primary_intent.action
                drone_id2 = exec2.parsed_command.primary_intent.parameters.get("drone_id")
                
                # Skip if different drones (no dependency)
                if drone_id1 and drone_id2 and drone_id1 != drone_id2:
                    continue
                
                # Check dependency rules
                if action1 in self.dependency_rules:
                    rules = self.dependency_rules[action1]
                    
                    # Check if action2 is required before action1
                    if "requires" in rules and action2 in rules["requires"]:
                        if j < i:  # action2 comes before action1
                            exec1.dependencies.append(j)
                            exec2.dependents.append(i)
                    
                    # Check if action2 conflicts with action1
                    if "conflicts" in rules and action2 in rules["conflicts"]:
                        # These cannot run in parallel
                        if j > i:  # Ensure later command waits
                            exec2.dependencies.append(i)
                            exec1.dependents.append(j)
        
        logger.debug(f"Dependency analysis completed: {sum(len(e.dependencies) for e in executions)} dependencies found")
    
    def _create_execution_plan(self, execution_state: BatchExecutionState):
        """Create optimized execution plan"""
        context = execution_state.context
        executions = execution_state.executions
        
        if context.execution_mode == BatchExecutionMode.SEQUENTIAL:
            # Simple sequential execution
            execution_state.execution_groups = [[i] for i in range(len(executions))]
        
        elif context.execution_mode == BatchExecutionMode.PARALLEL:
            # Maximum parallelization (ignoring dependencies)
            group_size = min(len(executions), context.max_parallel_commands)
            execution_state.execution_groups = []
            for i in range(0, len(executions), group_size):
                group = list(range(i, min(i + group_size, len(executions))))
                execution_state.execution_groups.append(group)
        
        elif context.execution_mode == BatchExecutionMode.PRIORITY_BASED:
            # Group by priority levels
            execution_state.execution_groups = self._create_priority_groups(execution_state)
        
        else:  # OPTIMIZED
            # Smart optimization considering dependencies and resources
            execution_state.execution_groups = self._create_optimized_groups(execution_state)
        
        # Calculate total estimated time
        execution_state.total_estimated_time = self._calculate_estimated_time(execution_state)
    
    def _create_priority_groups(self, execution_state: BatchExecutionState) -> List[List[int]]:
        """Create execution groups based on command priorities"""
        executions = execution_state.executions
        priority_groups = {priority: [] for priority in CommandPriority}
        
        for i, execution in enumerate(executions):
            action = execution.parsed_command.primary_intent.action
            priority = self.command_router.command_priorities.get(action, CommandPriority.NORMAL)
            priority_groups[priority].append(i)
        
        # Create execution groups in priority order
        groups = []
        for priority in [CommandPriority.EMERGENCY, CommandPriority.HIGH, 
                        CommandPriority.NORMAL, CommandPriority.LOW]:
            if priority_groups[priority]:
                groups.append(priority_groups[priority])
        
        return groups
    
    def _create_optimized_groups(self, execution_state: BatchExecutionState) -> List[List[int]]:
        """Create optimized execution groups considering dependencies and resources"""
        executions = execution_state.executions
        remaining = set(range(len(executions)))
        groups = []
        
        while remaining:
            # Find commands with no unfulfilled dependencies
            ready = []
            for i in remaining:
                dependencies_met = all(dep not in remaining for dep in executions[i].dependencies)
                if dependencies_met:
                    ready.append(i)
            
            if not ready:
                # Break deadlock - take commands with minimal dependencies
                min_deps = min(len(executions[i].dependencies) for i in remaining)
                ready = [i for i in remaining if len(executions[i].dependencies) == min_deps]
            
            # Group ready commands by resources (drone_id)
            resource_groups = {}
            for cmd_idx in ready:
                drone_id = executions[cmd_idx].parsed_command.primary_intent.parameters.get("drone_id", "system")
                if drone_id not in resource_groups:
                    resource_groups[drone_id] = []
                resource_groups[drone_id].append(cmd_idx)
            
            # Create parallel groups within resource constraints
            current_group = []
            for drone_commands in resource_groups.values():
                # For each drone, select one non-conflicting command
                if drone_commands:
                    # Prioritize by command priority and confidence
                    drone_commands.sort(key=lambda i: (
                        -self._get_command_priority_score(executions[i]),
                        -executions[i].parsed_command.primary_intent.confidence
                    ))
                    
                    # Add first command (highest priority)
                    cmd_idx = drone_commands[0]
                    current_group.append(cmd_idx)
                    remaining.remove(cmd_idx)
                    
                    # Check if we can add more commands for this drone
                    for other_idx in drone_commands[1:]:
                        if not self._commands_conflict(executions[cmd_idx], executions[other_idx]):
                            current_group.append(other_idx)
                            remaining.remove(other_idx)
                            break
            
            if current_group:
                groups.append(current_group)
            else:
                # Fallback: take one command to avoid infinite loop
                cmd_idx = next(iter(remaining))
                groups.append([cmd_idx])
                remaining.remove(cmd_idx)
        
        return groups
    
    def _commands_conflict(self, exec1: CommandExecution, exec2: CommandExecution) -> bool:
        """Check if two commands conflict"""
        action1 = exec1.parsed_command.primary_intent.action
        action2 = exec2.parsed_command.primary_intent.action
        
        # Check conflict rules
        if action1 in self.dependency_rules:
            conflicts = self.dependency_rules[action1].get("conflicts", [])
            if action2 in conflicts:
                return True
        
        if action2 in self.dependency_rules:
            conflicts = self.dependency_rules[action2].get("conflicts", [])
            if action1 in conflicts:
                return True
        
        return False
    
    def _get_command_priority_score(self, execution: CommandExecution) -> float:
        """Get numerical priority score for command"""
        action = execution.parsed_command.primary_intent.action
        priority = self.command_router.command_priorities.get(action, CommandPriority.NORMAL)
        
        priority_scores = {
            CommandPriority.EMERGENCY: 4.0,
            CommandPriority.HIGH: 3.0,
            CommandPriority.NORMAL: 2.0,
            CommandPriority.LOW: 1.0
        }
        
        return priority_scores[priority]
    
    def _calculate_estimated_time(self, execution_state: BatchExecutionState) -> float:
        """Calculate total estimated execution time"""
        total_time = 0.0
        
        for group in execution_state.execution_groups:
            if len(group) == 1:
                # Sequential
                action = execution_state.executions[group[0]].parsed_command.primary_intent.action
                total_time += self.execution_time_estimates.get(action, 2.0)
            else:
                # Parallel - use maximum time in group
                group_times = []
                for cmd_idx in group:
                    action = execution_state.executions[cmd_idx].parsed_command.primary_intent.action
                    group_times.append(self.execution_time_estimates.get(action, 2.0))
                total_time += max(group_times)
        
        return total_time
    
    async def _execute_batch(self, execution_state: BatchExecutionState) -> List[CommandResponse]:
        """Execute batch according to execution plan"""
        results = [None] * len(execution_state.executions)
        
        for group_index, command_indices in enumerate(execution_state.execution_groups):
            execution_state.current_group_index = group_index
            logger.debug(f"Executing group {group_index + 1}/{len(execution_state.execution_groups)}: commands {[i+1 for i in command_indices]}")
            
            if len(command_indices) == 1:
                # Sequential execution
                cmd_idx = command_indices[0]
                result = await self._execute_single_command(execution_state, cmd_idx)
                results[cmd_idx] = result
                
                # Check for stop conditions
                if not result.success and execution_state.context.error_recovery == ErrorRecoveryStrategy.STOP_ON_ERROR:
                    # Fill remaining results with skipped status
                    for remaining_idx in range(len(results)):
                        if results[remaining_idx] is None:
                            results[remaining_idx] = CommandResponse(
                                success=False,
                                message="Command skipped due to previous error",
                                timestamp=datetime.now()
                            )
                    break
            else:
                # Parallel execution
                tasks = []
                for cmd_idx in command_indices:
                    task = self._execute_single_command(execution_state, cmd_idx)
                    tasks.append((cmd_idx, task))
                
                # Execute all tasks in parallel
                group_results = await asyncio.gather(
                    *[task for _, task in tasks], 
                    return_exceptions=True
                )
                
                # Process results
                group_failed = False
                for i, (cmd_idx, result) in enumerate(zip([idx for idx, _ in tasks], group_results)):
                    if isinstance(result, Exception):
                        # Handle exceptions
                        result = CommandResponse(
                            success=False,
                            message=f"Execution exception: {str(result)}",
                            timestamp=datetime.now()
                        )
                    
                    results[cmd_idx] = result
                    if not result.success:
                        group_failed = True
                
                # Check for stop conditions
                if group_failed and execution_state.context.error_recovery == ErrorRecoveryStrategy.STOP_ON_ERROR:
                    # Fill remaining results
                    for remaining_idx in range(len(results)):
                        if results[remaining_idx] is None:
                            results[remaining_idx] = CommandResponse(
                                success=False,
                                message="Command skipped due to previous group error",
                                timestamp=datetime.now()
                            )
                    break
        
        return results
    
    async def _execute_single_command(self, execution_state: BatchExecutionState, 
                                    cmd_idx: int) -> CommandResponse:
        """Execute a single command with error recovery"""
        execution = execution_state.executions[cmd_idx]
        context = execution_state.context
        
        execution.start_time = datetime.now()
        execution.status = "running"
        
        max_attempts = context.max_retries + 1
        last_error = None
        
        for attempt in range(max_attempts):
            execution.attempts = attempt + 1
            
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    self.command_router.execute_enhanced_command(execution.parsed_command),
                    timeout=context.timeout_per_command
                )
                
                execution.status = "completed" if result.success else "failed"
                execution.result = result
                execution.end_time = datetime.now()
                
                if result.success or context.error_recovery == ErrorRecoveryStrategy.CONTINUE_ON_ERROR:
                    return result
                
                # Handle retry for failed commands
                if attempt < max_attempts - 1 and context.error_recovery in [
                    ErrorRecoveryStrategy.RETRY_AND_CONTINUE, 
                    ErrorRecoveryStrategy.SMART_RECOVERY
                ]:
                    logger.warning(f"Retrying command {cmd_idx + 1} (attempt {attempt + 2}): {result.message}")
                    await asyncio.sleep(context.retry_delay)
                    continue
                
                return result
                
            except asyncio.TimeoutError:
                error_msg = f"Command {cmd_idx + 1} timed out after {context.timeout_per_command}s"
                logger.error(error_msg)
                last_error = error_msg
                
            except Exception as e:
                error_msg = f"Command {cmd_idx + 1} failed: {str(e)}"
                logger.error(error_msg)
                last_error = error_msg
            
            # Retry delay
            if attempt < max_attempts - 1:
                await asyncio.sleep(context.retry_delay)
        
        # All attempts failed
        execution.status = "failed"
        execution.error_message = last_error
        execution.end_time = datetime.now()
        
        return CommandResponse(
            success=False,
            message=last_error or "Command failed after all retry attempts",
            timestamp=datetime.now()
        )
    
    def _generate_execution_analytics(self, execution_state: BatchExecutionState, 
                                    actual_time: float) -> Dict[str, Any]:
        """Generate detailed execution analytics"""
        executions = execution_state.executions
        
        # Command status distribution
        status_counts = {}
        for execution in executions:
            status = execution.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Execution time analysis
        execution_times = []
        for execution in executions:
            if execution.start_time and execution.end_time:
                exec_time = (execution.end_time - execution.start_time).total_seconds()
                execution_times.append(exec_time)
        
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        # Retry analysis
        total_retries = sum(max(0, execution.attempts - 1) for execution in executions)
        
        # Resource utilization
        drone_utilization = {}
        for execution in executions:
            drone_id = execution.parsed_command.primary_intent.parameters.get("drone_id", "system")
            if drone_id not in drone_utilization:
                drone_utilization[drone_id] = {"commands": 0, "successful": 0}
            drone_utilization[drone_id]["commands"] += 1
            if execution.status == "completed":
                drone_utilization[drone_id]["successful"] += 1
        
        return {
            "status_distribution": status_counts,
            "execution_times": {
                "average": avg_execution_time,
                "total": actual_time,
                "individual": execution_times
            },
            "retry_analysis": {
                "total_retries": total_retries,
                "retry_rate": total_retries / len(executions) if executions else 0.0
            },
            "resource_utilization": drone_utilization,
            "dependency_stats": {
                "total_dependencies": sum(len(e.dependencies) for e in executions),
                "avg_dependencies_per_command": sum(len(e.dependencies) for e in executions) / len(executions) if executions else 0.0
            }
        }
    
    def _calculate_parallelization_factor(self, execution_state: BatchExecutionState) -> float:
        """Calculate how much parallelization was achieved"""
        total_commands = len(execution_state.executions)
        if total_commands <= 1:
            return 1.0
        
        # Calculate average group size
        total_groups = len(execution_state.execution_groups)
        if total_groups == 0:
            return 1.0
        
        parallel_commands = sum(len(group) for group in execution_state.execution_groups if len(group) > 1)
        sequential_commands = total_commands - parallel_commands
        
        # Parallelization factor: how much we reduced execution time through parallelization
        max_possible_parallel = total_commands
        actual_parallel = parallel_commands
        
        return actual_parallel / max_possible_parallel if max_possible_parallel > 0 else 0.0


# Global batch processor instance (to be initialized)
batch_processor = None