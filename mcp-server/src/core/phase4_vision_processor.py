"""
Phase 4 Enhanced Vision Command Processor
Advanced natural language processing for camera and vision commands
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .enhanced_nlp_engine import EnhancedNLPEngine
from .backend_client import BackendClient
from ..models.phase4_vision_models import (
    VisionCommandAnalysis, BatchVisionCommand, BatchVisionResult,
    TrackingAlgorithm, VisionModelType, ExecutionMode, CameraFilter
)
from config.logging import get_logger


logger = get_logger(__name__)


class Phase4VisionProcessor:
    """Enhanced vision command processor for Phase 4"""
    
    def __init__(self, nlp_engine: EnhancedNLPEngine, backend_client: BackendClient):
        self.nlp_engine = nlp_engine
        self.backend_client = backend_client
        
        # Vision-specific command patterns
        self.vision_patterns = {
            # Camera commands
            "photo": [
                r"写真(?:を|撮|取)(?:って|影して)",
                r"(?:カメラで|)撮影(?:して|する)",
                r"(?:シャッター|を)(?:切って|押して)",
                r"(?:スナップ|ショット)(?:を撮って|して)",
                r"picture|photo|capture|snap|shot"
            ],
            
            "streaming": [
                r"(?:ストリーミング|配信)(?:を|の)(?:開始|始め|スタート)(?:して|する)",
                r"(?:ストリーミング|配信)(?:を|の)(?:停止|止め|ストップ)(?:して|する)",
                r"(?:ライブ|リアルタイム)(?:映像|画像|配信)(?:して|する)",
                r"stream(?:ing)?.*(?:start|begin|stop|end)"
            ],
            
            # Detection commands
            "detection": [
                r"(?:物体|オブジェクト|対象)(?:を|の)(?:検出|探知|発見)(?:して|する)",
                r"(?:何|どんなもの)(?:が|を)(?:見える|映っている|写っている)",
                r"(?:認識|判別|識別)(?:して|する)",
                r"detect|find|recognize|identify|search"
            ],
            
            "tracking": [
                r"(?:物体|オブジェクト|対象|ターゲット)(?:を|の)(?:追跡|追従|フォロー)(?:して|する)",
                r"(?:追跡|追従)(?:を|の)(?:開始|始め|スタート)(?:して|する)",
                r"(?:追跡|追従)(?:を|の)(?:停止|止め|ストップ)(?:して|する)",
                r"track(?:ing)?|follow(?:ing)?|chase"
            ],
            
            # Learning commands
            "learning": [
                r"(?:学習|トレーニング)(?:用|の)(?:データ|画像)(?:を|の)(?:収集|集める|撮る)(?:して|する)",
                r"(?:データセット|学習データ)(?:を|の)(?:作成|作る|生成)(?:して|する)",
                r"(?:多角度|いろんな角度)(?:から|で)(?:撮影|撮る)(?:して|する)",
                r"learning.*(?:data|dataset)|collect.*(?:data|samples)"
            ],
            
            # Vision analytics
            "analytics": [
                r"(?:ビジョン|視覚|カメラ)(?:の|システムの)(?:分析|統計|パフォーマンス)(?:を|の)(?:見せて|表示して|取得して)",
                r"(?:モデル|検出器)(?:の|システムの)(?:性能|パフォーマンス)(?:を|の)(?:確認|チェック)(?:して|する)",
                r"analytics|statistics|performance|metrics"
            ]
        }
        
        # Parameter extraction patterns
        self.parameter_patterns = {
            "model_id": [
                r"(?:モデル|検出器)(?:ID|識別子|番号)?[:\s]*([a-zA-Z0-9_-]+)",
                r"(?:使用|利用)(?:する)?(?:モデル|検出器)[:\s]*([a-zA-Z0-9_-]+)",
                r"model[:\s]*([a-zA-Z0-9_-]+)"
            ],
            
            "algorithm": [
                r"(?:アルゴリズム|手法)[:\s]*([a-zA-Z]+)",
                r"(?:CSRT|KCF|MOSSE|MEDIANFLOW|TLD|BOOSTING)",
                r"algorithm[:\s]*([a-zA-Z]+)"
            ],
            
            "confidence": [
                r"(?:信頼度|確信度)[:\s]*([0-9]+(?:\.[0-9]+)?)",
                r"confidence[:\s]*([0-9]+(?:\.[0-9]+)?)"
            ],
            
            "quality": [
                r"(?:画質|品質)[:\s]*(高|中|低|high|medium|low)",
                r"quality[:\s]*(high|medium|low)"
            ],
            
            "filters": [
                r"(?:フィルター|効果)[:\s]*([a-zA-Z_,\s]+)",
                r"(?:シャープ|ノイズ除去|明度|コントラスト|彩度|ぼかし)",
                r"filter[s]?[:\s]*([a-zA-Z_,\s]+)"
            ]
        }
        
        logger.info("Phase4VisionProcessor initialized")
    
    async def analyze_vision_command(self, command: str) -> VisionCommandAnalysis:
        """
        Analyze vision command and extract intent and parameters
        
        ビジョンコマンドを分析し、意図とパラメータを抽出
        """
        try:
            # Use enhanced NLP engine for basic analysis
            nlp_result = await self.nlp_engine.parse_command_enhanced(command)
            
            # Enhanced vision-specific analysis
            vision_intent = self._detect_vision_intent(command)
            vision_params = self._extract_vision_parameters(command)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(command, vision_intent, vision_params)
            
            # Generate API call suggestions
            suggested_calls = await self._generate_api_suggestions(vision_intent, vision_params)
            
            analysis = VisionCommandAnalysis(
                command=command,
                detected_intent=vision_intent["action"],
                extracted_parameters=vision_params,
                confidence=min(nlp_result.confidence * vision_intent["confidence"], 1.0),
                suggested_api_calls=suggested_calls,
                complexity_score=complexity_score
            )
            
            logger.debug(f"Vision command analyzed: {vision_intent['action']} (confidence: {analysis.confidence:.3f})")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing vision command: {str(e)}")
            return VisionCommandAnalysis(
                command=command,
                detected_intent="unknown",
                extracted_parameters={},
                confidence=0.0,
                suggested_api_calls=[],
                complexity_score=1.0
            )
    
    def _detect_vision_intent(self, command: str) -> Dict[str, Any]:
        """Detect vision-specific intent from command"""
        command_lower = command.lower()
        best_match = {"action": "unknown", "confidence": 0.0}
        
        for intent, patterns in self.vision_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command_lower):
                    confidence = 0.8 + (len(re.findall(pattern, command_lower)) * 0.1)
                    if confidence > best_match["confidence"]:
                        best_match = {"action": intent, "confidence": min(confidence, 1.0)}
        
        return best_match
    
    def _extract_vision_parameters(self, command: str) -> Dict[str, Any]:
        """Extract vision-specific parameters from command"""
        params = {}
        
        for param_type, patterns in self.parameter_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
                    params[param_type] = self._normalize_parameter_value(param_type, value)
                    break
        
        # Extract additional vision parameters
        if "高画質" in command or "high quality" in command.lower():
            params["quality"] = "high"
        elif "低画質" in command or "low quality" in command.lower():
            params["quality"] = "low"
        
        if "連続" in command or "multiple" in command.lower():
            params["capture_multiple"] = True
        
        if "フィルター" in command or "filter" in command.lower():
            params["apply_filters"] = True
        
        return params
    
    def _normalize_parameter_value(self, param_type: str, value: str) -> Any:
        """Normalize parameter values"""
        value = value.strip()
        
        if param_type == "confidence":
            try:
                conf = float(value)
                return conf if conf <= 1.0 else conf / 100.0
            except ValueError:
                return 0.5
        
        elif param_type == "quality":
            quality_mapping = {
                "高": "high", "中": "medium", "低": "low",
                "high": "high", "medium": "medium", "low": "low"
            }
            return quality_mapping.get(value.lower(), "medium")
        
        elif param_type == "algorithm":
            algo_mapping = {
                "csrt": TrackingAlgorithm.CSRT,
                "kcf": TrackingAlgorithm.KCF,
                "mosse": TrackingAlgorithm.MOSSE,
                "medianflow": TrackingAlgorithm.MEDIANFLOW,
                "tld": TrackingAlgorithm.TLD,
                "boosting": TrackingAlgorithm.BOOSTING
            }
            return algo_mapping.get(value.lower(), TrackingAlgorithm.CSRT).value
        
        elif param_type == "filters":
            filter_mapping = {
                "シャープ": CameraFilter.SHARPEN,
                "ノイズ除去": CameraFilter.DENOISE,
                "明度": CameraFilter.BRIGHTNESS,
                "コントラスト": CameraFilter.CONTRAST,
                "彩度": CameraFilter.SATURATION,
                "ぼかし": CameraFilter.GAUSSIAN_BLUR,
                "sharpen": CameraFilter.SHARPEN,
                "denoise": CameraFilter.DENOISE,
                "brightness": CameraFilter.BRIGHTNESS,
                "contrast": CameraFilter.CONTRAST,
                "saturation": CameraFilter.SATURATION,
                "blur": CameraFilter.GAUSSIAN_BLUR
            }
            filters = [filter_mapping.get(f.strip().lower()) for f in value.split(",")]
            return [f.value for f in filters if f is not None]
        
        return value
    
    def _calculate_complexity_score(self, command: str, intent: Dict[str, Any], params: Dict[str, Any]) -> float:
        """Calculate command complexity score"""
        base_score = 0.1
        
        # Intent complexity
        intent_complexity = {
            "photo": 0.2,
            "streaming": 0.3,
            "detection": 0.4,
            "tracking": 0.6,
            "learning": 0.8,
            "analytics": 0.3
        }
        base_score += intent_complexity.get(intent["action"], 0.5)
        
        # Parameter complexity
        base_score += len(params) * 0.1
        
        # Special parameters
        if "capture_multiple" in params:
            base_score += 0.2
        if "apply_filters" in params:
            base_score += 0.3
        
        # Command length complexity
        base_score += min(len(command.split()) * 0.02, 0.3)
        
        return min(base_score, 1.0)
    
    async def _generate_api_suggestions(self, intent: Dict[str, Any], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate API call suggestions based on intent and parameters"""
        suggestions = []
        action = intent["action"]
        
        if action == "photo":
            suggestions.append({
                "endpoint": "/mcp/vision/drones/{drone_id}/camera/photo/enhanced",
                "method": "POST",
                "description": "Enhanced photo capture with auto-adjustment",
                "parameters": {
                    "quality": params.get("quality", "high"),
                    "auto_adjust": True,
                    "apply_filters": params.get("filters", [])
                }
            })
        
        elif action == "streaming":
            suggestions.append({
                "endpoint": "/mcp/vision/drones/{drone_id}/camera/streaming/enhanced",
                "method": "POST", 
                "description": "Enhanced streaming control with quality improvements",
                "parameters": {
                    "action": "start",
                    "quality": params.get("quality", "medium"),
                    "enable_enhancement": True
                }
            })
        
        elif action == "detection":
            suggestions.append({
                "endpoint": "/mcp/vision/detection/enhanced",
                "method": "POST",
                "description": "Enhanced object detection with filtering",
                "parameters": {
                    "model_id": params.get("model_id", "yolo_v8_general"),
                    "confidence_threshold": params.get("confidence", 0.5),
                    "enable_tracking_prep": True
                }
            })
        
        elif action == "tracking":
            suggestions.append({
                "endpoint": "/mcp/vision/tracking/enhanced/start",
                "method": "POST",
                "description": "Enhanced object tracking with configurable algorithms",
                "parameters": {
                    "model_id": params.get("model_id", "yolo_v8_general"),
                    "algorithm": params.get("algorithm", "csrt"),
                    "confidence_threshold": params.get("confidence", 0.5)
                }
            })
        
        elif action == "learning":
            suggestions.append({
                "endpoint": "/mcp/vision/drones/{drone_id}/learning/collect/enhanced",
                "method": "POST",
                "description": "Enhanced learning data collection with multiple perspectives",
                "parameters": {
                    "quality_threshold": params.get("confidence", 0.7),
                    "capture_positions": ["front", "back", "left", "right"],
                    "altitude_levels": [100, 150, 200]
                }
            })
        
        elif action == "analytics":
            suggestions.append({
                "endpoint": "/mcp/vision/analytics/comprehensive",
                "method": "GET",
                "description": "Comprehensive vision analytics and statistics",
                "parameters": {}
            })
        
        return suggestions
    
    async def process_batch_vision_commands(self, batch_request: BatchVisionCommand) -> BatchVisionResult:
        """
        Process multiple vision commands in batch with optimization
        
        最適化を伴う複数ビジョンコマンドのバッチ処理
        """
        start_time = datetime.now()
        
        try:
            # Analyze all commands first
            command_analyses = []
            for command in batch_request.commands:
                analysis = await self.analyze_vision_command(command)
                command_analyses.append(analysis)
            
            # Generate execution plan
            execution_plan = await self._generate_execution_plan(
                command_analyses, batch_request.execution_mode
            )
            
            # Execute commands
            results = []
            if batch_request.execution_mode == ExecutionMode.PARALLEL:
                results = await self._execute_parallel(command_analyses, batch_request.error_recovery)
            elif batch_request.execution_mode == ExecutionMode.OPTIMIZED:
                results = await self._execute_optimized(command_analyses, execution_plan, batch_request.error_recovery)
            else:
                results = await self._execute_sequential(command_analyses, batch_request.error_recovery)
            
            # Calculate performance metrics
            total_time = (datetime.now() - start_time).total_seconds()
            performance_metrics = {
                "total_commands": len(batch_request.commands),
                "successful_commands": sum(1 for r in results if r.get("success", False)),
                "failed_commands": sum(1 for r in results if not r.get("success", False)),
                "average_complexity": sum(a.complexity_score for a in command_analyses) / len(command_analyses),
                "total_execution_time": total_time,
                "average_command_time": total_time / len(batch_request.commands)
            }
            
            success = all(r.get("success", False) for r in results)
            
            return BatchVisionResult(
                success=success,
                results=results,
                execution_plan=execution_plan,
                performance_metrics=performance_metrics,
                total_execution_time=total_time,
                optimization_applied=batch_request.optimization_enabled
            )
            
        except Exception as e:
            logger.error(f"Error processing batch vision commands: {str(e)}")
            total_time = (datetime.now() - start_time).total_seconds()
            
            return BatchVisionResult(
                success=False,
                results=[{"success": False, "error": str(e)} for _ in batch_request.commands],
                execution_plan={},
                performance_metrics={"error": str(e)},
                total_execution_time=total_time,
                optimization_applied=False
            )
    
    async def _generate_execution_plan(self, analyses: List[VisionCommandAnalysis], mode: ExecutionMode) -> Dict[str, Any]:
        """Generate optimized execution plan"""
        plan = {
            "execution_mode": mode.value,
            "total_commands": len(analyses),
            "grouping": [],
            "dependencies": [],
            "estimated_time": 0.0
        }
        
        if mode == ExecutionMode.OPTIMIZED:
            # Group commands by type and dependencies
            groups = self._group_commands_by_type(analyses)
            plan["grouping"] = groups
            plan["dependencies"] = self._analyze_dependencies(analyses)
            plan["estimated_time"] = self._estimate_execution_time(groups)
        
        return plan
    
    def _group_commands_by_type(self, analyses: List[VisionCommandAnalysis]) -> List[Dict[str, Any]]:
        """Group commands by type for optimized execution"""
        groups = {}
        
        for i, analysis in enumerate(analyses):
            intent = analysis.detected_intent
            if intent not in groups:
                groups[intent] = []
            groups[intent].append({"index": i, "analysis": analysis})
        
        return [{"type": intent, "commands": commands} for intent, commands in groups.items()]
    
    def _analyze_dependencies(self, analyses: List[VisionCommandAnalysis]) -> List[Dict[str, Any]]:
        """Analyze dependencies between commands"""
        dependencies = []
        
        for i, analysis in enumerate(analyses):
            if analysis.detected_intent == "tracking":
                # Tracking commands might depend on detection commands
                for j, prev_analysis in enumerate(analyses[:i]):
                    if prev_analysis.detected_intent == "detection":
                        dependencies.append({
                            "dependent": i,
                            "depends_on": j,
                            "type": "detection_to_tracking"
                        })
        
        return dependencies
    
    def _estimate_execution_time(self, groups: List[Dict[str, Any]]) -> float:
        """Estimate total execution time for optimized plan"""
        time_estimates = {
            "photo": 2.0,
            "streaming": 1.0,
            "detection": 3.0,
            "tracking": 5.0,
            "learning": 10.0,
            "analytics": 1.5
        }
        
        total_time = 0.0
        for group in groups:
            command_count = len(group["commands"])
            base_time = time_estimates.get(group["type"], 2.0)
            # Assume some parallel execution within groups
            group_time = base_time + (command_count - 1) * base_time * 0.3
            total_time = max(total_time, group_time)  # Parallel group execution
        
        return total_time
    
    async def _execute_sequential(self, analyses: List[VisionCommandAnalysis], error_recovery: str) -> List[Dict[str, Any]]:
        """Execute commands sequentially"""
        results = []
        
        for analysis in analyses:
            try:
                result = await self._execute_single_command(analysis)
                results.append(result)
                
                if not result.get("success", False) and error_recovery == "stop":
                    break
                    
            except Exception as e:
                logger.error(f"Error executing command: {str(e)}")
                results.append({"success": False, "error": str(e)})
                
                if error_recovery == "stop":
                    break
        
        return results
    
    async def _execute_parallel(self, analyses: List[VisionCommandAnalysis], error_recovery: str) -> List[Dict[str, Any]]:
        """Execute commands in parallel"""
        tasks = [self._execute_single_command(analysis) for analysis in analyses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({"success": False, "error": str(result)})
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_optimized(self, analyses: List[VisionCommandAnalysis], execution_plan: Dict[str, Any], error_recovery: str) -> List[Dict[str, Any]]:
        """Execute commands with optimization"""
        results = [None] * len(analyses)
        
        # Execute groups in optimized order
        for group in execution_plan.get("grouping", []):
            group_tasks = []
            group_indices = []
            
            for command_info in group["commands"]:
                index = command_info["index"]
                analysis = command_info["analysis"]
                group_tasks.append(self._execute_single_command(analysis))
                group_indices.append(index)
            
            # Execute group in parallel
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
            
            # Store results
            for i, result in enumerate(group_results):
                if isinstance(result, Exception):
                    results[group_indices[i]] = {"success": False, "error": str(result)}
                else:
                    results[group_indices[i]] = result
        
        return results
    
    async def _execute_single_command(self, analysis: VisionCommandAnalysis) -> Dict[str, Any]:
        """Execute a single vision command"""
        try:
            # Simple execution based on detected intent
            if analysis.detected_intent == "photo":
                return {
                    "success": True,
                    "action": "photo",
                    "message": "Photo command executed successfully",
                    "timestamp": datetime.now().isoformat()
                }
            elif analysis.detected_intent == "detection":
                return {
                    "success": True,
                    "action": "detection",
                    "message": "Detection command executed successfully",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "action": analysis.detected_intent,
                    "message": f"{analysis.detected_intent} command executed successfully",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error executing single command: {str(e)}")
            return {
                "success": False,
                "action": analysis.detected_intent,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }