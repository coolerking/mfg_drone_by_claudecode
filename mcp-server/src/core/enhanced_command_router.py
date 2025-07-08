"""
Enhanced Command Router for MCP Server - Phase 2
Advanced command routing with dependency analysis and batch optimization
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
from dataclasses import dataclass
from enum import Enum

from ..models.command_models import (
    ParsedIntent, CommandResponse, ExecutionDetails, 
    BatchCommandResponse, BatchCommandSummary
)
from ..models.drone_models import OperationResponse
from ..models.camera_models import PhotoResponse, DetectionResponse
from ..models.system_models import ErrorCodes, ApiError
from .backend_client import BackendClient, BackendClientError
from .enhanced_nlp_engine import ParsedCommand, ConfidenceLevel
from config.logging import get_logger


logger = get_logger(__name__)


class CommandPriority(Enum):
    """Command priority levels"""
    EMERGENCY = "emergency"      # Immediate execution
    HIGH = "high"               # Important operations
    NORMAL = "normal"           # Standard operations
    LOW = "low"                 # Background tasks


class DependencyType(Enum):
    """Command dependency types"""
    REQUIRES = "requires"       # Must complete before
    CONFLICTS = "conflicts"     # Cannot run simultaneously
    ENHANCES = "enhances"       # Better if run together


@dataclass
class CommandDependency:
    """Command dependency definition"""
    source_action: str
    target_action: str
    dependency_type: DependencyType
    description: str


@dataclass
class ExecutionPlan:
    """Optimized execution plan for batch commands"""
    execution_groups: List[List[int]]  # Groups of command indices to run together
    total_estimated_time: float
    parallelizable_count: int
    sequential_count: int
    dependencies: List[CommandDependency]
    warnings: List[str]


class EnhancedCommandRouter:
    """Enhanced command router with dependency analysis and optimization"""
    
    def __init__(self, backend_client: BackendClient):
        """Initialize enhanced command router"""
        self.backend_client = backend_client
        
        # Command priority mapping
        self.command_priorities = {
            "emergency": CommandPriority.EMERGENCY,
            "connect": CommandPriority.HIGH,
            "disconnect": CommandPriority.HIGH,
            "takeoff": CommandPriority.HIGH,
            "land": CommandPriority.HIGH,
            "move": CommandPriority.NORMAL,
            "rotate": CommandPriority.NORMAL,
            "altitude": CommandPriority.NORMAL,
            "photo": CommandPriority.NORMAL,
            "streaming": CommandPriority.NORMAL,
            "learning": CommandPriority.LOW,
            "detection": CommandPriority.NORMAL,
            "tracking": CommandPriority.NORMAL,
            "status": CommandPriority.LOW,
            "health": CommandPriority.LOW
        }
        
        # Command dependencies
        self.dependencies = [
            # Connection dependencies
            CommandDependency("connect", "takeoff", DependencyType.REQUIRES, 
                            "Must connect before takeoff"),
            CommandDependency("connect", "move", DependencyType.REQUIRES,
                            "Must connect before movement"),
            CommandDependency("takeoff", "move", DependencyType.REQUIRES,
                            "Must takeoff before movement"),
            CommandDependency("takeoff", "land", DependencyType.CONFLICTS,
                            "Cannot takeoff and land simultaneously"),
            
            # Movement conflicts
            CommandDependency("move", "rotate", DependencyType.CONFLICTS,
                            "Cannot move and rotate simultaneously"),
            CommandDependency("emergency", "move", DependencyType.CONFLICTS,
                            "Emergency stops all movement"),
            
            # Camera enhancements
            CommandDependency("photo", "detection", DependencyType.ENHANCES,
                            "Photo helps with detection accuracy"),
            CommandDependency("streaming", "tracking", DependencyType.ENHANCES,
                            "Streaming enhances tracking performance")
        ]
        
        # Action mappings with enhanced error handling
        self.action_mappings = {
            # Connection actions
            "connect": self._execute_connect,
            "disconnect": self._execute_disconnect,
            
            # Flight control actions
            "takeoff": self._execute_takeoff,
            "land": self._execute_land,
            "emergency": self._execute_emergency,
            
            # Movement actions
            "move": self._execute_move,
            "rotate": self._execute_rotate,
            "altitude": self._execute_altitude,
            
            # Camera actions
            "photo": self._execute_photo,
            "streaming": self._execute_streaming,
            "learning": self._execute_learning_data,
            
            # Vision actions
            "detection": self._execute_detection,
            "tracking": self._execute_tracking,
            
            # System actions
            "status": self._execute_status,
            "health": self._execute_health
        }
        
        # Execution statistics
        self.execution_stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "average_execution_time": 0.0
        }
        
        logger.info("Enhanced command router initialized")
    
    async def execute_enhanced_command(self, parsed_command: ParsedCommand) -> CommandResponse:
        """Execute command with enhanced analysis and error handling"""
        start_time = datetime.now()
        backend_calls = []
        
        try:
            logger.info(f"Executing enhanced command: {parsed_command.primary_intent.action}")
            
            # Pre-execution validation
            validation_result = await self._validate_command(parsed_command)
            if not validation_result["valid"]:
                raise ValueError(validation_result["error"])
            
            # Handle low confidence commands
            if parsed_command.confidence_level == ConfidenceLevel.VERY_LOW:
                return self._create_suggestion_response(parsed_command, start_time)
            
            # Get executor function
            executor = self.action_mappings.get(parsed_command.primary_intent.action)
            if not executor:
                # Try alternatives if primary action fails
                for alt_intent in parsed_command.alternative_intents:
                    alt_executor = self.action_mappings.get(alt_intent.action)
                    if alt_executor:
                        logger.info(f"Using alternative action: {alt_intent.action}")
                        executor = alt_executor
                        parsed_command.primary_intent = alt_intent
                        break
                
                if not executor:
                    raise ValueError(f"Unknown action: {parsed_command.primary_intent.action}")
            
            # Execute command with retry logic
            result = await self._execute_with_retry(executor, parsed_command.primary_intent.parameters)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_execution_stats(execution_time, True)
            
            # Create execution details
            execution_details = ExecutionDetails(
                backend_calls=backend_calls,
                execution_time=execution_time
            )
            
            # Create enhanced response
            response = CommandResponse(
                success=True,
                message=f"Command '{parsed_command.primary_intent.action}' executed successfully",
                parsed_intent=parsed_command.primary_intent,
                execution_details=execution_details,
                result=result
            )
            
            # Add confidence and alternative information
            response.result.update({
                "confidence_level": parsed_command.confidence_level.value,
                "alternatives_available": len(parsed_command.alternative_intents),
                "parameter_confidence": parsed_command.parameter_confidence
            })
            
            logger.info(f"Enhanced command executed successfully in {execution_time:.2f}s")
            return response
            
        except BackendClientError as e:
            logger.error(f"Backend error executing enhanced command: {e.message}")
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(execution_time, False)
            
            return self._create_error_response(
                parsed_command, e.message, e.error_code, execution_time, backend_calls
            )
            
        except Exception as e:
            logger.error(f"Error executing enhanced command: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(execution_time, False)
            
            return self._create_error_response(
                parsed_command, str(e), ErrorCodes.INTERNAL_SERVER_ERROR, 
                execution_time, backend_calls
            )
    
    async def execute_optimized_batch(self, parsed_commands: List[ParsedCommand], 
                                    execution_mode: str = "sequential",
                                    stop_on_error: bool = True) -> BatchCommandResponse:
        """Execute batch commands with dependency analysis and optimization"""
        logger.info(f"Executing optimized batch of {len(parsed_commands)} commands")
        
        start_time = datetime.now()
        results = []
        successful_commands = 0
        failed_commands = 0
        
        try:
            # Create execution plan
            execution_plan = self._create_execution_plan(parsed_commands, execution_mode)
            
            logger.info(f"Execution plan: {len(execution_plan.execution_groups)} groups, "
                       f"estimated time: {execution_plan.total_estimated_time:.2f}s")
            
            # Execute according to plan
            for group_index, command_indices in enumerate(execution_plan.execution_groups):
                logger.debug(f"Executing group {group_index + 1}: commands {command_indices}")
                
                if len(command_indices) == 1:
                    # Sequential execution
                    cmd_index = command_indices[0]
                    response = await self.execute_enhanced_command(parsed_commands[cmd_index])
                    results.append(response)
                    
                    if response.success:
                        successful_commands += 1
                    else:
                        failed_commands += 1
                        if stop_on_error:
                            break
                else:
                    # Parallel execution
                    tasks = []
                    for cmd_index in command_indices:
                        task = self.execute_enhanced_command(parsed_commands[cmd_index])
                        tasks.append(task)
                    
                    group_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for i, result in enumerate(group_results):
                        if isinstance(result, Exception):
                            # Handle exceptions
                            error_response = CommandResponse(
                                success=False,
                                message=f"Error: {str(result)}",
                                timestamp=datetime.now()
                            )
                            results.append(error_response)
                            failed_commands += 1
                        else:
                            results.append(result)
                            if result.success:
                                successful_commands += 1
                            else:
                                failed_commands += 1
                    
                    if stop_on_error and failed_commands > 0:
                        break
            
            # Fill remaining results if stopped early
            while len(results) < len(parsed_commands):
                skipped_response = CommandResponse(
                    success=False,
                    message="Command skipped due to previous error",
                    timestamp=datetime.now()
                )
                results.append(skipped_response)
                failed_commands += 1
            
            # Calculate total execution time
            total_execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create summary
            summary = BatchCommandSummary(
                total_commands=len(parsed_commands),
                successful_commands=successful_commands,
                failed_commands=failed_commands,
                total_execution_time=total_execution_time
            )
            
            # Create enhanced batch response
            response = BatchCommandResponse(
                success=failed_commands == 0,
                message=f"Optimized batch execution completed: {successful_commands}/{len(parsed_commands)} successful",
                results=results,
                summary=summary
            )
            
            # Add optimization information
            response.result = {
                "execution_plan": {
                    "groups": len(execution_plan.execution_groups),
                    "parallelizable": execution_plan.parallelizable_count,
                    "sequential": execution_plan.sequential_count,
                    "estimated_time": execution_plan.total_estimated_time,
                    "actual_time": total_execution_time,
                    "efficiency": execution_plan.total_estimated_time / total_execution_time if total_execution_time > 0 else 1.0
                },
                "warnings": execution_plan.warnings
            }
            
            logger.info(f"Optimized batch execution completed: {successful_commands}/{len(parsed_commands)} successful")
            return response
            
        except Exception as e:
            logger.error(f"Error in optimized batch execution: {str(e)}")
            
            # Create error response
            total_execution_time = (datetime.now() - start_time).total_seconds()
            summary = BatchCommandSummary(
                total_commands=len(parsed_commands),
                successful_commands=successful_commands,
                failed_commands=len(parsed_commands) - successful_commands,
                total_execution_time=total_execution_time
            )
            
            return BatchCommandResponse(
                success=False,
                message=f"Batch execution failed: {str(e)}",
                results=results,
                summary=summary
            )
    
    def _create_execution_plan(self, parsed_commands: List[ParsedCommand], 
                             execution_mode: str) -> ExecutionPlan:
        """Create optimized execution plan with dependency analysis"""
        logger.debug("Creating optimized execution plan")
        
        commands = [cmd.primary_intent for cmd in parsed_commands]
        execution_groups = []
        dependencies = []
        warnings = []
        
        if execution_mode == "sequential":
            # Simple sequential execution
            execution_groups = [[i] for i in range(len(commands))]
            parallelizable_count = 0
            sequential_count = len(commands)
        else:
            # Analyze dependencies for parallel optimization
            dependency_graph = self._build_dependency_graph(commands)
            execution_groups = self._optimize_execution_order(commands, dependency_graph)
            
            parallelizable_count = sum(len(group) for group in execution_groups if len(group) > 1)
            sequential_count = len(commands) - parallelizable_count
            
            # Check for conflicts and warnings
            for i, cmd1 in enumerate(commands):
                for j, cmd2 in enumerate(commands[i+1:], i+1):
                    if self._has_conflict(cmd1, cmd2):
                        warnings.append(f"Commands {i+1} and {j+1} may conflict: {cmd1.action} vs {cmd2.action}")
        
        # Estimate total execution time
        total_estimated_time = self._estimate_batch_execution_time(commands, execution_groups)
        
        return ExecutionPlan(
            execution_groups=execution_groups,
            total_estimated_time=total_estimated_time,
            parallelizable_count=parallelizable_count,
            sequential_count=sequential_count,
            dependencies=dependencies,
            warnings=warnings
        )
    
    def _build_dependency_graph(self, commands: List[ParsedIntent]) -> Dict[int, List[int]]:
        """Build dependency graph for commands"""
        graph = {i: [] for i in range(len(commands))}
        
        for i, cmd1 in enumerate(commands):
            for j, cmd2 in enumerate(commands):
                if i != j:
                    for dep in self.dependencies:
                        if (cmd1.action == dep.source_action and 
                            cmd2.action == dep.target_action and
                            dep.dependency_type == DependencyType.REQUIRES):
                            graph[i].append(j)
        
        return graph
    
    def _optimize_execution_order(self, commands: List[ParsedIntent], 
                                dependency_graph: Dict[int, List[int]]) -> List[List[int]]:
        """Optimize execution order based on dependencies"""
        # Simple topological sort with grouping
        in_degree = {i: 0 for i in range(len(commands))}
        for dependencies in dependency_graph.values():
            for dep in dependencies:
                in_degree[dep] += 1
        
        execution_groups = []
        remaining = set(range(len(commands)))
        
        while remaining:
            # Find commands with no dependencies
            ready = [i for i in remaining if in_degree[i] == 0]
            
            if not ready:
                # Break cycles - take remaining commands
                ready = list(remaining)
            
            # Group compatible commands for parallel execution
            parallel_groups = self._group_parallel_commands(ready, commands)
            
            for group in parallel_groups:
                execution_groups.append(group)
                for cmd_idx in group:
                    remaining.remove(cmd_idx)
                    # Update in-degrees
                    for dep in dependency_graph[cmd_idx]:
                        if dep in in_degree:
                            in_degree[dep] -= 1
        
        return execution_groups
    
    def _group_parallel_commands(self, ready_commands: List[int], 
                               commands: List[ParsedIntent]) -> List[List[int]]:
        """Group commands that can be executed in parallel"""
        if len(ready_commands) <= 1:
            return [[cmd] for cmd in ready_commands]
        
        # Separate by drone ID and action type
        drone_groups = {}
        for cmd_idx in ready_commands:
            cmd = commands[cmd_idx]
            drone_id = cmd.parameters.get("drone_id", "unknown")
            
            if drone_id not in drone_groups:
                drone_groups[drone_id] = []
            drone_groups[drone_id].append(cmd_idx)
        
        # Create parallel groups
        parallel_groups = []
        for drone_commands in drone_groups.values():
            if len(drone_commands) == 1:
                parallel_groups.append(drone_commands)
            else:
                # Check for conflicts within drone
                safe_group = []
                for cmd_idx in drone_commands:
                    cmd = commands[cmd_idx]
                    if not any(self._has_conflict(cmd, commands[other_idx]) 
                             for other_idx in safe_group):
                        safe_group.append(cmd_idx)
                    else:
                        # Start new group for conflicting command
                        if safe_group:
                            parallel_groups.append(safe_group)
                        safe_group = [cmd_idx]
                
                if safe_group:
                    parallel_groups.append(safe_group)
        
        return parallel_groups
    
    def _has_conflict(self, cmd1: ParsedIntent, cmd2: ParsedIntent) -> bool:
        """Check if two commands conflict"""
        # Same drone conflicts
        if (cmd1.parameters.get("drone_id") == cmd2.parameters.get("drone_id") and
            cmd1.parameters.get("drone_id") is not None):
            
            # Check for conflicting actions
            for dep in self.dependencies:
                if ((cmd1.action == dep.source_action and cmd2.action == dep.target_action) or
                    (cmd2.action == dep.source_action and cmd1.action == dep.target_action)):
                    if dep.dependency_type == DependencyType.CONFLICTS:
                        return True
        
        return False
    
    def _estimate_batch_execution_time(self, commands: List[ParsedIntent], 
                                     execution_groups: List[List[int]]) -> float:
        """Estimate total execution time for batch"""
        time_estimates = {
            "connect": 2.0, "disconnect": 1.0, "takeoff": 5.0, "land": 3.0,
            "emergency": 0.5, "move": 3.0, "rotate": 2.0, "altitude": 4.0,
            "photo": 1.0, "streaming": 1.0, "learning": 30.0, "detection": 2.0,
            "tracking": 1.0, "status": 0.5, "health": 0.5
        }
        
        total_time = 0.0
        for group in execution_groups:
            if len(group) == 1:
                # Sequential
                cmd = commands[group[0]]
                total_time += time_estimates.get(cmd.action, 2.0)
            else:
                # Parallel - use maximum time in group
                group_times = [time_estimates.get(commands[i].action, 2.0) for i in group]
                total_time += max(group_times)
        
        return total_time
    
    async def _validate_command(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """Validate command before execution"""
        intent = parsed_command.primary_intent
        
        # Check required parameters
        if parsed_command.missing_parameters:
            return {
                "valid": False,
                "error": f"Missing required parameters: {', '.join(parsed_command.missing_parameters)}"
            }
        
        # Check drone availability for drone-specific commands
        if "drone_id" in intent.parameters:
            drone_id = intent.parameters["drone_id"]
            try:
                # Quick status check
                await self.backend_client.get_drone_status(drone_id)
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Drone {drone_id} not available: {str(e)}"
                }
        
        return {"valid": True}
    
    async def _execute_with_retry(self, executor, parameters: Dict[str, Any], 
                                max_retries: int = 2) -> Dict[str, Any]:
        """Execute command with retry logic"""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await executor(parameters)
            except BackendClientError as e:
                last_error = e
                if attempt < max_retries and e.error_code != ErrorCodes.DRONE_NOT_FOUND:
                    logger.warning(f"Retrying command (attempt {attempt + 1}): {e.message}")
                    await asyncio.sleep(1.0)  # Brief delay before retry
                else:
                    raise
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"Retrying command (attempt {attempt + 1}): {str(e)}")
                    await asyncio.sleep(1.0)
                else:
                    raise
        
        if last_error:
            raise last_error
    
    def _create_suggestion_response(self, parsed_command: ParsedCommand, 
                                  start_time: datetime) -> CommandResponse:
        """Create response with suggestions for low confidence commands"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return CommandResponse(
            success=False,
            message="Command confidence too low. Please provide more specific instructions.",
            parsed_intent=parsed_command.primary_intent,
            execution_details=ExecutionDetails(
                backend_calls=[],
                execution_time=execution_time
            ),
            result={
                "suggestions": parsed_command.suggestions,
                "alternatives": [alt.action for alt in parsed_command.alternative_intents],
                "confidence_level": parsed_command.confidence_level.value,
                "missing_parameters": parsed_command.missing_parameters
            }
        )
    
    def _create_error_response(self, parsed_command: ParsedCommand, error_message: str,
                             error_code: str, execution_time: float, 
                             backend_calls: List[Dict[str, Any]]) -> CommandResponse:
        """Create standardized error response"""
        return CommandResponse(
            success=False,
            message=f"Error: {error_message}",
            parsed_intent=parsed_command.primary_intent,
            execution_details=ExecutionDetails(
                backend_calls=backend_calls,
                execution_time=execution_time
            ),
            result={
                "error_code": error_code,
                "suggestions": parsed_command.suggestions if hasattr(parsed_command, 'suggestions') else [],
                "alternatives": [alt.action for alt in parsed_command.alternative_intents] if hasattr(parsed_command, 'alternative_intents') else []
            }
        )
    
    def _update_execution_stats(self, execution_time: float, success: bool):
        """Update execution statistics"""
        self.execution_stats["total_commands"] += 1
        if success:
            self.execution_stats["successful_commands"] += 1
        else:
            self.execution_stats["failed_commands"] += 1
        
        # Update average execution time
        total = self.execution_stats["total_commands"]
        current_avg = self.execution_stats["average_execution_time"]
        self.execution_stats["average_execution_time"] = (
            (current_avg * (total - 1) + execution_time) / total
        )
    
    # Original executor methods (unchanged)
    async def _execute_connect(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute connect command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for connection")
        
        result = await self.backend_client.connect_drone(drone_id)
        return {"operation": "connect", "drone_id": drone_id, "result": result.dict()}
    
    async def _execute_disconnect(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute disconnect command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for disconnection")
        
        result = await self.backend_client.disconnect_drone(drone_id)
        return {"operation": "disconnect", "drone_id": drone_id, "result": result.dict()}
    
    async def _execute_takeoff(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute takeoff command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for takeoff")
        
        target_height = parameters.get("height")
        result = await self.backend_client.takeoff_drone(drone_id, target_height)
        return {"operation": "takeoff", "drone_id": drone_id, "target_height": target_height, "result": result.dict()}
    
    async def _execute_land(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute land command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for landing")
        
        result = await self.backend_client.land_drone(drone_id)
        return {"operation": "land", "drone_id": drone_id, "result": result.dict()}
    
    async def _execute_emergency(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute emergency stop command"""
        drone_id = parameters.get("drone_id")
        if not drone_id:
            raise ValueError("Drone ID is required for emergency stop")
        
        result = await self.backend_client.emergency_stop(drone_id)
        return {"operation": "emergency", "drone_id": drone_id, "result": result.dict()}
    
    async def _execute_move(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute move command"""
        drone_id = parameters.get("drone_id")
        direction = parameters.get("direction")
        distance = parameters.get("distance")
        speed = parameters.get("speed")
        
        if not drone_id:
            raise ValueError("Drone ID is required for movement")
        if not direction:
            raise ValueError("Direction is required for movement")
        if not distance:
            raise ValueError("Distance is required for movement")
        
        result = await self.backend_client.move_drone(drone_id, direction, distance, speed)
        return {
            "operation": "move",
            "drone_id": drone_id,
            "direction": direction,
            "distance": distance,
            "speed": speed,
            "result": result.dict()
        }
    
    async def _execute_rotate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rotate command"""
        drone_id = parameters.get("drone_id")
        direction = parameters.get("direction")
        angle = parameters.get("angle")
        
        if not drone_id:
            raise ValueError("Drone ID is required for rotation")
        if not direction:
            raise ValueError("Direction is required for rotation")
        if not angle:
            raise ValueError("Angle is required for rotation")
        
        result = await self.backend_client.rotate_drone(drone_id, direction, angle)
        return {
            "operation": "rotate",
            "drone_id": drone_id,
            "direction": direction,
            "angle": angle,
            "result": result.dict()
        }
    
    async def _execute_altitude(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute altitude command"""
        drone_id = parameters.get("drone_id")
        height = parameters.get("height")
        mode = parameters.get("mode", "absolute")
        
        if not drone_id:
            raise ValueError("Drone ID is required for altitude adjustment")
        if not height:
            raise ValueError("Height is required for altitude adjustment")
        
        result = await self.backend_client.set_altitude(drone_id, height, mode)
        return {
            "operation": "altitude",
            "drone_id": drone_id,
            "height": height,
            "mode": mode,
            "result": result.dict()
        }
    
    async def _execute_photo(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute photo command"""
        drone_id = parameters.get("drone_id")
        filename = parameters.get("filename")
        quality = parameters.get("quality", "high")
        
        if not drone_id:
            raise ValueError("Drone ID is required for photo capture")
        
        result = await self.backend_client.take_photo(drone_id, filename, quality)
        return {
            "operation": "photo",
            "drone_id": drone_id,
            "filename": filename,
            "quality": quality,
            "result": result.dict()
        }
    
    async def _execute_streaming(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute streaming command"""
        drone_id = parameters.get("drone_id")
        action = parameters.get("action", "start")
        quality = parameters.get("quality", "medium")
        resolution = parameters.get("resolution", "720p")
        
        if not drone_id:
            raise ValueError("Drone ID is required for streaming control")
        
        result = await self.backend_client.control_streaming(drone_id, action, quality, resolution)
        return {
            "operation": "streaming",
            "drone_id": drone_id,
            "action": action,
            "quality": quality,
            "resolution": resolution,
            "result": result.dict()
        }
    
    async def _execute_learning_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute learning data collection command"""
        drone_id = parameters.get("drone_id")
        object_name = parameters.get("object_name")
        
        if not drone_id:
            raise ValueError("Drone ID is required for learning data collection")
        if not object_name:
            raise ValueError("Object name is required for learning data collection")
        
        result = await self.backend_client.collect_learning_data(drone_id, object_name, **parameters)
        return {
            "operation": "learning_data",
            "drone_id": drone_id,
            "object_name": object_name,
            "result": result
        }
    
    async def _execute_detection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute detection command"""
        drone_id = parameters.get("drone_id")
        model_id = parameters.get("model_id")
        confidence_threshold = parameters.get("confidence_threshold", 0.5)
        
        if not drone_id:
            raise ValueError("Drone ID is required for object detection")
        
        result = await self.backend_client.detect_objects(drone_id, model_id, confidence_threshold)
        return {
            "operation": "detection",
            "drone_id": drone_id,
            "model_id": model_id,
            "confidence_threshold": confidence_threshold,
            "result": [detection.dict() for detection in result]
        }
    
    async def _execute_tracking(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tracking command"""
        drone_id = parameters.get("drone_id")
        action = parameters.get("action", "start")
        
        if not drone_id:
            raise ValueError("Drone ID is required for object tracking")
        
        result = await self.backend_client.control_tracking(action, drone_id, **parameters)
        return {
            "operation": "tracking",
            "drone_id": drone_id,
            "action": action,
            "result": result.dict()
        }
    
    async def _execute_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute status command"""
        drone_id = parameters.get("drone_id")
        
        if drone_id:
            # Get specific drone status
            result = await self.backend_client.get_drone_status(drone_id)
            return {
                "operation": "status",
                "drone_id": drone_id,
                "result": result.dict()
            }
        else:
            # Get system status
            result = await self.backend_client.get_system_status()
            return {
                "operation": "system_status",
                "result": result
            }
    
    async def _execute_health(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute health check command"""
        result = await self.backend_client.health_check()
        return {
            "operation": "health_check",
            "result": result
        }
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()


# Global enhanced command router instance (to be initialized with backend client)
enhanced_command_router = None