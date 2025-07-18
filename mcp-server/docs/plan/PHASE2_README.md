# MCP Server Phase 2 - Enhanced Natural Language Processing

Phase 2 introduces advanced natural language processing capabilities, intelligent batch processing, and sophisticated command routing with dependency analysis.

## 🚀 New Features

### Enhanced Natural Language Processing Engine
- **Advanced Japanese Command Parsing**: 300+ pattern variations for natural language understanding
- **Multiple Intent Detection**: Identifies primary and alternative interpretations
- **Context Memory**: Remembers conversation history and session parameters
- **Parameter Normalization**: Automatic unit conversion (meters to cm, degrees, etc.)
- **Confidence Scoring**: Advanced confidence calculation with context boosting
- **Intelligent Suggestions**: Smart error correction and command completion

### Enhanced Command Router
- **Dependency Analysis**: Automatic detection of command dependencies
- **Execution Optimization**: Smart ordering and parallel execution
- **Retry Mechanisms**: Configurable retry logic with exponential backoff
- **Alternative Fallback**: Automatic fallback to alternative interpretations
- **Performance Tracking**: Detailed execution statistics and analytics

### Advanced Batch Processor
- **Smart Execution Planning**: Optimized execution order based on dependencies
- **Multiple Execution Modes**: Sequential, parallel, optimized, and priority-based
- **Error Recovery Strategies**: Smart error handling and recovery options
- **Resource Management**: Drone-aware command scheduling
- **Real-time Analytics**: Detailed execution analytics and optimization metrics

## 📁 Project Structure

```
mcp-server/
├── src/
│   ├── core/
│   │   ├── enhanced_nlp_engine.py      # Advanced NLP with context awareness
│   │   ├── enhanced_command_router.py  # Intelligent command routing
│   │   ├── batch_processor.py          # Advanced batch processing
│   │   ├── backend_client.py           # Backend API communication
│   │   └── nlp_engine.py              # Original NLP (backward compatibility)
│   ├── models/                         # Data models (unchanged)
│   └── mcp_main.py                     # MCP Server main application
├── tests/
│   ├── test_enhanced_nlp_engine.py    # Enhanced NLP tests
│   ├── test_enhanced_command_router.py # Enhanced router tests
│   └── test_batch_processor.py        # Batch processor tests
├── config/                            # Configuration (unchanged)
├── requirements.txt                   # Updated dependencies
├── run_phase2_tests.py               # Test runner for Phase 2
└── PHASE2_README.md                  # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- All Phase 1 dependencies

### Install Enhanced Dependencies
```bash
cd mcp-server
pip install -r requirements.txt
```

### Start MCP Server
```bash
# MCP Server with Phase 2 enhanced features
python start_mcp_server_unified.py

# Or direct MCP server startup
python src/mcp_main.py
```

## 🧠 Enhanced Natural Language Processing

### Advanced Command Parsing

The enhanced NLP engine supports sophisticated Japanese language understanding:

```python
from src.core.enhanced_nlp_engine import EnhancedNLPEngine

engine = EnhancedNLPEngine()

# Parse with enhanced analysis
parsed = engine.parse_command("ドローンAAに接続して高度1メートルで右に50センチ移動")

print(f"Primary action: {parsed.primary_intent.action}")
print(f"Confidence: {parsed.primary_intent.confidence}")
print(f"Alternatives: {[alt.action for alt in parsed.alternative_intents]}")
print(f"Missing params: {parsed.missing_parameters}")
print(f"Suggestions: {parsed.suggestions}")
```

### Context Memory

The engine remembers conversation context:

```python
# First command
engine.parse_command("ドローンAAに接続して")

# Second command (remembers drone AA)
parsed = engine.parse_command("離陸して")
# Automatically uses drone_id: "AA"
```

### Unit Conversion

Automatic unit normalization:

```python
# Input: "1メートル上昇"
# Output: {"height": 100}  # Converted to cm

# Input: "90度右回転"  
# Output: {"angle": 90, "direction": "clockwise"}
```

## 🎯 Enhanced Command Routing

### Dependency Analysis

Commands are automatically analyzed for dependencies:

```python
from src.core.enhanced_command_router import EnhancedCommandRouter

router = EnhancedCommandRouter(backend_client)

# Execute with automatic dependency handling
response = await router.execute_enhanced_command(parsed_command)
```

### Retry Mechanisms

Configurable retry logic:

```python
# Automatic retry with exponential backoff
result = await router._execute_with_retry(
    executor_function, 
    parameters, 
    max_retries=3
)
```

## 📦 Advanced Batch Processing

### Execution Modes

1. **Sequential**: Commands execute one after another
2. **Parallel**: Maximum parallelization (ignoring dependencies)
3. **Optimized**: Smart optimization considering dependencies and resources
4. **Priority-based**: Execute by command priority levels

### Usage Example

```python
from src.core.batch_processor import AdvancedBatchProcessor, BatchExecutionContext
from src.models.command_models import NaturalLanguageCommand

# Create commands
commands = [
    NaturalLanguageCommand(command="ドローンAAに接続して"),
    NaturalLanguageCommand(command="離陸して"),
    NaturalLanguageCommand(command="右に50センチ移動して"),
    NaturalLanguageCommand(command="写真を撮って"),
    NaturalLanguageCommand(command="着陸して")
]

# Configure execution
context = BatchExecutionContext(
    execution_mode=BatchExecutionMode.OPTIMIZED,
    error_recovery=ErrorRecoveryStrategy.SMART_RECOVERY,
    max_retries=2,
    timeout_per_command=30.0
)

# Process batch
processor = AdvancedBatchProcessor(nlp_engine, command_router)
response = await processor.process_batch(commands, context)

print(f"Success: {response.success}")
print(f"Completed: {response.summary.successful_commands}/{response.summary.total_commands}")
print(f"Execution time: {response.summary.total_execution_time:.2f}s")
```

## 🌐 Enhanced API Endpoints

### Enhanced Command Execution
```http
POST /mcp/command/enhanced
Content-Type: application/json

{
  "command": "ドローンAAに接続して高度1メートルで移動",
  "analyze": true,
  "confidence_threshold": 0.7
}
```

### Advanced Batch Processing
```http
POST /mcp/command/batch/advanced
Content-Type: application/json

{
  "commands": [
    {"command": "ドローンAAに接続して"},
    {"command": "離陸して"},
    {"command": "写真を撮って"}
  ],
  "execution_mode": "optimized",
  "error_recovery": "smart_recovery",
  "max_retries": 2
}
```

### Command Analysis
```http
POST /mcp/command/analyze
Content-Type: application/json

{
  "command": "複雑なドローン操作コマンド"
}
```

### Command Suggestions
```http
POST /mcp/command/suggestions
Content-Type: application/json

{
  "partial_command": "ドローン",
  "max_suggestions": 5
}
```

## 🧪 Testing

### Run All Tests
```bash
python run_phase2_tests.py
```

### Run Specific Test Types
```bash
# NLP engine tests only
python run_phase2_tests.py --type nlp

# Command router tests only  
python run_phase2_tests.py --type router

# Batch processor tests only
python run_phase2_tests.py --type batch

# With coverage report
python run_phase2_tests.py --coverage
```

### Run Specific Tests
```bash
# Specific test file
python run_phase2_tests.py --specific tests/test_enhanced_nlp_engine.py

# Specific test function
python run_phase2_tests.py --specific tests/test_enhanced_nlp_engine.py::TestEnhancedNLPEngine::test_basic_command_parsing
```

## 📊 Performance Metrics

### Execution Analytics
The enhanced system provides detailed analytics:

```json
{
  "execution_analytics": {
    "status_distribution": {"completed": 4, "failed": 1},
    "execution_times": {"average": 2.3, "total": 11.5},
    "retry_analysis": {"total_retries": 2, "retry_rate": 0.4},
    "resource_utilization": {
      "AA": {"commands": 3, "successful": 3},
      "BB": {"commands": 2, "successful": 1}
    }
  },
  "optimization_details": {
    "mode": "optimized",
    "groups": 3,
    "estimated_time": 12.0,
    "actual_time": 11.5,
    "efficiency_ratio": 1.04,
    "parallelization_factor": 0.6
  }
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Enhanced NLP settings
NLP_CONFIDENCE_THRESHOLD=0.6
NLP_CONTEXT_BOOST_FACTOR=0.2
NLP_SYNONYM_BOOST_FACTOR=0.1

# Batch processing settings
BATCH_MAX_PARALLEL_COMMANDS=5
BATCH_DEFAULT_TIMEOUT=30.0
BATCH_MAX_RETRIES=2

# Enhanced features
ENABLE_ENHANCED_NLP=true
ENABLE_DEPENDENCY_ANALYSIS=true
ENABLE_COMMAND_ANALYTICS=true
```

## 🐛 Troubleshooting

### Common Issues

1. **Low Confidence Parsing**
   - Add more specific parameters to commands
   - Use suggested corrections from the response
   - Check context information

2. **Batch Execution Failures**
   - Review dependency conflicts in logs
   - Adjust error recovery strategy
   - Check individual command validity

3. **Performance Issues**
   - Monitor execution analytics
   - Adjust parallelization settings
   - Review command complexity scores

### Debug Mode
```bash
# Start with debug logging
DEBUG=true python src/enhanced_main.py
```

## 🔄 Backward Compatibility

Phase 2 maintains full backward compatibility:

- Original `/mcp/command` and `/mcp/command/batch` endpoints work unchanged
- Legacy NLP engine available as fallback
- All Phase 1 functionality preserved
- Gradual migration path available

## 🚀 What's Next: Phase 3

Planned features for Phase 3:
- **Advanced Vision Processing**: Real-time object detection and tracking
- **Machine Learning Integration**: Adaptive command learning
- **Multi-drone Coordination**: Swarm intelligence and coordination
- **Real-time Streaming**: Live video processing and analysis
- **Advanced Safety Systems**: Collision avoidance and safety protocols

## 📝 API Documentation

Enhanced API documentation is available at:
- **Development**: http://localhost:8001/docs
- **Enhanced Endpoints**: Marked with "enhanced-" tags in OpenAPI spec

## 🤝 Contributing

1. Follow existing code structure and patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure backward compatibility
5. Run full test suite before submitting

## 📄 License

MIT License - see LICENSE file for details.