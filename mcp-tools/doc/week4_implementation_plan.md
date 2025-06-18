# Week 4 Implementation Plan: MCP Tools Testing & Integration

## Overview

Week 4 focuses on implementing comprehensive testing infrastructure and Claude Code integration for the MCP tools based on the detailed test cases documented in `test_cases.md`.

## Implementation Strategy

### Phase 1: Testing Infrastructure (Days 1-2)
Build robust testing framework supporting both mock and real hardware testing.

### Phase 2: MCP Tools Implementation (Days 3-5)
Implement all 25 MCP tools with comprehensive error handling.

### Phase 3: Integration & Claude Testing (Days 6-7)
Complete Claude Code integration and end-to-end testing.

---

## Day 1-2: Testing Infrastructure Implementation

### 2.1 Test Framework Setup

#### Core Testing Architecture
```
mcp-tools/
├── src/
│   ├── server.ts                 # Main MCP server
│   ├── tools/                    # 25 MCP tool implementations
│   │   ├── connection.ts         # 3 connection tools
│   │   ├── flight.ts            # 5 flight control tools
│   │   ├── movement.ts          # 6 movement tools
│   │   ├── camera.ts            # 6 camera tools
│   │   └── sensors.ts           # 9 sensor tools
│   ├── bridge/
│   │   ├── api-client.ts        # FastAPI HTTP client
│   │   └── mock-client.ts       # Mock client for testing
│   └── utils/
│       ├── test-helpers.ts      # Testing utilities
│       └── validation.ts        # Parameter validation
├── tests/
│   ├── unit/                    # Unit tests (~200 tests)
│   │   ├── tools/               # Tool-specific tests
│   │   ├── bridge/              # Bridge component tests
│   │   └── validation/          # Validation tests
│   ├── integration/             # Integration tests (~150 tests)
│   │   ├── e2e-scenarios.test.ts # End-to-end flight missions
│   │   ├── error-handling.test.ts # Error scenario tests
│   │   └── performance.test.ts   # Performance benchmarks
│   ├── fixtures/                # Test data and fixtures
│   │   ├── test-data.ts         # Valid/invalid parameter sets
│   │   ├── mock-responses.ts    # Mock API responses
│   │   └── drone-states.ts      # Drone state fixtures
│   └── config/
│       ├── jest.config.js       # Jest configuration
│       ├── test-setup.ts        # Test environment setup
│       └── mock-config.ts       # Mock configuration
└── package.json                 # Test dependencies
```

### 2.2 Mock vs Real Hardware Testing

#### Mock Testing Configuration
```typescript
// tests/config/mock-config.ts
export const MockTestConfig = {
  mode: 'mock',
  backend: {
    url: 'http://localhost:8000',
    timeout: 5000,
    retries: 3
  },
  drone: {
    type: 'TelloStub',
    simulation: {
      battery: 85,
      temperature: 45,
      connected: true,
      flying: false
    }
  },
  safety: {
    skipRealHardware: true,
    enableAllTests: true
  }
};
```

#### Real Hardware Testing Configuration
```typescript
// tests/config/real-config.ts
export const RealTestConfig = {
  mode: 'real',
  backend: {
    url: 'http://192.168.1.100:8000', // Raspberry Pi
    timeout: 10000,
    retries: 1
  },
  drone: {
    type: 'TelloEDU',
    safety: {
      batteryMinimum: 30,
      maxTestHeight: 100, // cm
      testArea: 'indoor',
      emergencyLanding: true
    }
  },
  safety: {
    requireConfirmation: true,
    safetyChecks: true,
    limitedMovement: true
  }
};
```

### 2.3 Test Categories Implementation

#### Boundary Value Testing Framework
```typescript
// tests/utils/boundary-testing.ts
interface BoundaryTestCase<T> {
  parameter: string;
  validValues: T[];
  invalidValues: T[];
  expectedErrors: string[];
}

export class BoundaryValueTester {
  static async testParameter<T>(
    tool: MCPTool,
    testCase: BoundaryTestCase<T>
  ): Promise<TestResult[]> {
    const results: TestResult[] = [];
    
    // Test valid boundary values
    for (const value of testCase.validValues) {
      const result = await this.testValue(tool, testCase.parameter, value, true);
      results.push(result);
    }
    
    // Test invalid boundary values
    for (const value of testCase.invalidValues) {
      const result = await this.testValue(tool, testCase.parameter, value, false);
      results.push(result);
    }
    
    return results;
  }
}
```

#### Error Handling Test Framework
```typescript
// tests/utils/error-testing.ts
export class ErrorHandlingTester {
  static async testErrorScenarios(
    tool: MCPTool,
    errorScenarios: ErrorScenario[]
  ): Promise<ErrorTestResult[]> {
    return Promise.all(errorScenarios.map(async (scenario) => {
      const mockClient = new MockAPIClient();
      mockClient.simulateError(scenario.errorType, scenario.errorCode);
      
      try {
        await tool.execute(scenario.input, mockClient);
        return {
          scenario: scenario.name,
          passed: false,
          reason: 'Expected error but got success'
        };
      } catch (error) {
        return {
          scenario: scenario.name,
          passed: error.code === scenario.expectedErrorCode,
          actualError: error.code,
          expectedError: scenario.expectedErrorCode
        };
      }
    }));
  }
}
```

---

## Day 3-5: MCP Tools Implementation

### 3.1 Tool Implementation Pattern

#### Standard Tool Structure
```typescript
// src/tools/base-tool.ts
export abstract class BaseMCPTool implements Tool {
  abstract name: string;
  abstract description: string;
  abstract inputSchema: any;
  
  constructor(
    protected apiClient: APIClient,
    protected validator: ParameterValidator
  ) {}
  
  async call(args: any): Promise<ToolResult> {
    try {
      // 1. Validate input parameters
      const validatedArgs = await this.validator.validate(args, this.inputSchema);
      
      // 2. Check drone state if required
      await this.checkPrerequisites(validatedArgs);
      
      // 3. Execute the tool operation
      const result = await this.execute(validatedArgs);
      
      // 4. Return formatted result
      return this.formatResult(result);
      
    } catch (error) {
      return this.handleError(error);
    }
  }
  
  protected abstract execute(args: any): Promise<any>;
  protected abstract checkPrerequisites(args: any): Promise<void>;
}
```

### 3.2 Implementation Priority & Timeline

#### Day 3: Core Tools (Critical Path)
1. **Connection Tools** (3 tools - 4 hours)
   - `drone_connect` - Basic connection with retry logic
   - `drone_disconnect` - Safe disconnection with state checks
   - `drone_status` - Comprehensive status reporting

2. **Flight Control Tools** (5 tools - 4 hours)
   - `drone_takeoff` - With safety checks (battery, space)
   - `drone_land` - Graceful landing sequence
   - `drone_emergency` - Immediate emergency stop
   - `drone_stop` - Hover in place
   - `drone_get_height` - Current altitude reading

#### Day 4: Movement Tools (High Priority)
3. **Movement Tools** (6 tools - 8 hours)
   - `drone_move` - Basic directional movement
   - `drone_rotate` - Rotation control
   - `drone_flip` - Acrobatic maneuvers (mock only)
   - `drone_go_xyz` - Coordinate-based movement
   - `drone_curve` - Curved flight paths
   - `drone_rc_control` - Real-time control

#### Day 5: Sensors & Camera (Medium Priority)
4. **Sensor Tools** (9 tools - 6 hours)
   - Individual sensor reading tools
   - `drone_sensor_summary` - Consolidated sensor data

5. **Camera Tools** (6 tools - 2 hours)
   - Stream control and photo capture
   - Camera settings management

### 3.3 Parameter Validation Implementation

#### Comprehensive Validation System
```typescript
// src/utils/validation.ts
export class ParameterValidator {
  private validators = new Map<string, ValidatorFunction>();
  
  constructor() {
    this.registerBuiltinValidators();
  }
  
  private registerBuiltinValidators() {
    // Movement parameters
    this.validators.set('direction', (value: string) => {
      const validDirections = ['up', 'down', 'left', 'right', 'forward', 'back'];
      if (!validDirections.includes(value)) {
        throw new ValidationError(`Invalid direction: ${value}`, 'INVALID_PARAMETER');
      }
    });
    
    this.validators.set('distance', (value: number) => {
      if (value < 20 || value > 500) {
        throw new ValidationError(`Distance ${value} out of range [20-500]`, 'INVALID_PARAMETER');
      }
    });
    
    // Rotation parameters
    this.validators.set('angle', (value: number) => {
      if (value < 1 || value > 360) {
        throw new ValidationError(`Angle ${value} out of range [1-360]`, 'INVALID_PARAMETER');
      }
    });
    
    // Coordinate parameters
    this.validators.set('coordinate', (value: number) => {
      if (value < -500 || value > 500) {
        throw new ValidationError(`Coordinate ${value} out of range [-500-500]`, 'INVALID_PARAMETER');
      }
    });
    
    // Speed parameters
    this.validators.set('speed', (value: number) => {
      if (value < 10 || value > 100) {
        throw new ValidationError(`Speed ${value} out of range [10-100]`, 'INVALID_PARAMETER');
      }
    });
    
    // Camera parameters
    this.validators.set('resolution', (value: string) => {
      if (!['high', 'low'].includes(value)) {
        throw new ValidationError(`Invalid resolution: ${value}`, 'INVALID_PARAMETER');
      }
    });
  }
}
```

### 3.4 Error Handling Implementation

#### Comprehensive Error System
```typescript
// src/utils/errors.ts
export enum ErrorCode {
  DRONE_NOT_CONNECTED = 'DRONE_NOT_CONNECTED',
  DRONE_CONNECTION_FAILED = 'DRONE_CONNECTION_FAILED',
  INVALID_PARAMETER = 'INVALID_PARAMETER',
  COMMAND_FAILED = 'COMMAND_FAILED',
  COMMAND_TIMEOUT = 'COMMAND_TIMEOUT',
  NOT_FLYING = 'NOT_FLYING',
  ALREADY_FLYING = 'ALREADY_FLYING',
  STREAMING_NOT_STARTED = 'STREAMING_NOT_STARTED',
  STREAMING_ALREADY_STARTED = 'STREAMING_ALREADY_STARTED',
  INTERNAL_ERROR = 'INTERNAL_ERROR'
}

export class MCPError extends Error {
  constructor(
    message: string,
    public code: ErrorCode,
    public details?: any
  ) {
    super(message);
    this.name = 'MCPError';
  }
  
  toToolResult(): ErrorResult {
    return {
      isError: true,
      content: [{
        type: 'text',
        text: `Error: ${this.message}`
      }]
    };
  }
}
```

---

## Day 6-7: Integration & Claude Testing

### 6.1 Claude Code Integration

#### MCP Server Configuration
```json
// mcp-workspace.json
{
  "mcpServers": {
    "mfg-drone-tools": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "./mcp-tools",
      "env": {
        "NODE_ENV": "production",
        "BACKEND_URL": "http://localhost:8000",
        "LOG_LEVEL": "info",
        "SAFETY_MODE": "true"
      }
    }
  }
}
```

#### Production Deployment Setup
```typescript
// src/index.ts
#!/usr/bin/env node

import { MCPDroneServer } from './server.js';
import { ConfigManager } from './utils/config.js';
import { Logger } from './utils/logger.js';

async function main() {
  try {
    const config = ConfigManager.load();
    const logger = new Logger(config.logging);
    
    logger.info('Starting MCP Drone Tools Server...');
    
    const server = new MCPDroneServer(config);
    await server.start();
    
    logger.info('MCP Server ready for Claude Code integration');
    
    // Graceful shutdown handling
    process.on('SIGINT', async () => {
      logger.info('Gracefully shutting down...');
      await server.stop();
      process.exit(0);
    });
    
  } catch (error) {
    console.error('Failed to start MCP server:', error);
    process.exit(1);
  }
}

main();
```

### 6.2 End-to-End Testing

#### E2E Test Scenarios
```typescript
// tests/integration/e2e-scenarios.test.ts
describe('End-to-End Flight Missions', () => {
  test('Complete Flight Cycle', async () => {
    const scenario = new FlightScenario();
    
    // 1. Connect to drone
    await scenario.executeStep('drone_connect', {});
    expect(scenario.droneState.connected).toBe(true);
    
    // 2. Take off
    await scenario.executeStep('drone_takeoff', {});
    expect(scenario.droneState.flying).toBe(true);
    
    // 3. Move in pattern
    await scenario.executeStep('drone_move', {direction: 'forward', distance: 100});
    await scenario.executeStep('drone_rotate', {direction: 'clockwise', angle: 90});
    await scenario.executeStep('drone_move', {direction: 'forward', distance: 100});
    
    // 4. Take photo
    await scenario.executeStep('camera_take_photo', {});
    
    // 5. Return and land
    await scenario.executeStep('drone_land', {});
    expect(scenario.droneState.flying).toBe(false);
    
    // 6. Disconnect
    await scenario.executeStep('drone_disconnect', {});
    expect(scenario.droneState.connected).toBe(false);
  });
  
  test('Emergency Scenario Handling', async () => {
    const scenario = new FlightScenario();
    
    // Setup flight
    await scenario.executeStep('drone_connect', {});
    await scenario.executeStep('drone_takeoff', {});
    
    // Simulate emergency
    scenario.simulateEmergency('low_battery');
    
    // Emergency response
    await scenario.executeStep('drone_emergency', {});
    
    // Verify safe state
    expect(scenario.droneState.flying).toBe(false);
    expect(scenario.droneState.emergencyMode).toBe(true);
  });
});
```

### 6.3 Performance & Load Testing

#### Performance Benchmarks
```typescript
// tests/integration/performance.test.ts
describe('Performance Benchmarks', () => {
  test('Tool Response Times', async () => {
    const results = await PerformanceTester.benchmarkTools([
      'drone_connect',
      'drone_status', 
      'drone_battery',
      'drone_move'
    ]);
    
    expect(results.drone_connect.averageTime).toBeLessThan(100); // ms
    expect(results.drone_status.averageTime).toBeLessThan(50);   // ms
    expect(results.drone_battery.averageTime).toBeLessThan(30);  // ms
    expect(results.drone_move.averageTime).toBeLessThan(50);     // ms
  });
  
  test('Concurrent Tool Execution', async () => {
    const concurrentResult = await PerformanceTester.executeConcurrently([
      { tool: 'drone_battery', args: {} },
      { tool: 'drone_temperature', args: {} },
      { tool: 'drone_attitude', args: {} }
    ]);
    
    expect(concurrentResult.totalTime).toBeLessThan(100); // ms
    expect(concurrentResult.allSuccessful).toBe(true);
  });
});
```

---

## Week 4 Success Criteria

### Quantitative Metrics
- **Test Coverage**: ≥95% code coverage
- **Test Count**: ~500 total tests implemented
- **Performance**: All tools meet response time targets
- **Reliability**: <1% test failure rate in CI/CD

### Qualitative Metrics
- **Claude Integration**: Successful natural language control
- **Error Handling**: Graceful handling of all error scenarios
- **Documentation**: Complete API documentation and examples
- **Safety**: No unsafe operations in real hardware testing

### Deliverables

1. **Complete MCP Tools Suite** (25 tools)
2. **Comprehensive Test Suite** (~500 tests)
3. **Testing Infrastructure** (mock + real hardware)
4. **Claude Code Integration** (ready for production)
5. **Performance Benchmarks** (documented metrics)
6. **Deployment Scripts** (automated setup)
7. **User Documentation** (API reference + examples)

---

## Risk Mitigation

### Technical Risks
- **Real Hardware Testing**: Limited to safe operations, comprehensive simulation
- **Performance Issues**: Early benchmarking and optimization
- **Integration Complexity**: Incremental integration approach

### Safety Measures
- **Flight Area Restrictions**: Indoor testing only, limited height
- **Battery Monitoring**: Continuous monitoring, automatic landing
- **Emergency Protocols**: Immediate stop capabilities
- **Supervision Required**: Human operator always present

---

This implementation plan ensures a systematic approach to delivering a fully tested, production-ready MCP tools suite with comprehensive Claude Code integration.