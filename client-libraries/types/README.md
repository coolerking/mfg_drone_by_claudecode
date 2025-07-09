# @mcp-drone/types

TypeScript type definitions for MCP Drone Control Server. This package provides comprehensive type definitions for all MCP API endpoints, models, and client configurations.

## Features

- 🔷 **Complete Type Coverage**: All MCP API endpoints and models
- 🔍 **Type Guards**: Runtime type checking utilities
- 📝 **IntelliSense Support**: Full autocomplete and documentation
- 🏗️ **Modular Design**: Import only what you need
- 📊 **Validation Constraints**: Built-in validation rules
- 🌐 **WebSocket Types**: Real-time event type definitions
- 🛠️ **Utility Types**: Helper types for common patterns
- 🔧 **Constants**: API endpoints and configuration defaults

## Installation

```bash
npm install @mcp-drone/types
```

## Usage

### Basic Types

```typescript
import { 
  DroneInfo, 
  CommandResponse, 
  NaturalLanguageCommand 
} from '@mcp-drone/types';

// Drone information
const drone: DroneInfo = {
  id: 'drone_001',
  name: 'Test Drone',
  type: 'real',
  status: 'available',
  capabilities: ['camera', 'movement'],
  last_seen: '2023-01-01T12:00:00Z'
};

// Natural language command
const command: NaturalLanguageCommand = {
  command: 'ドローンAAに接続して',
  context: {
    drone_id: 'drone_001',
    language: 'ja'
  },
  options: {
    confirm_before_execution: false,
    dry_run: false
  }
};
```

### Client Configuration

```typescript
import { MCPClientConfig } from '@mcp-drone/types';

const config: MCPClientConfig = {
  baseURL: 'http://localhost:8001',
  apiKey: 'your-api-key',
  timeout: 30000
};
```

### API Responses

```typescript
import { 
  DroneListResponse, 
  CommandResponse, 
  BatchCommandResponse 
} from '@mcp-drone/types';

// Drone list response
const droneList: DroneListResponse = {
  drones: [
    {
      id: 'drone_001',
      name: 'Test Drone',
      type: 'real',
      status: 'available',
      capabilities: ['camera', 'movement']
    }
  ],
  count: 1,
  timestamp: '2023-01-01T12:00:00Z'
};

// Command response
const response: CommandResponse = {
  success: true,
  message: 'Command executed successfully',
  parsed_intent: {
    action: 'connect_drone',
    parameters: { drone_id: 'drone_001' },
    confidence: 0.95
  },
  timestamp: '2023-01-01T12:00:00Z'
};
```

### Control Commands

```typescript
import { 
  TakeoffCommand, 
  MoveCommand, 
  RotateCommand, 
  AltitudeCommand 
} from '@mcp-drone/types';

// Takeoff command
const takeoff: TakeoffCommand = {
  target_height: 100,
  safety_check: true
};

// Move command
const move: MoveCommand = {
  direction: 'forward',
  distance: 100,
  speed: 50
};

// Rotate command
const rotate: RotateCommand = {
  direction: 'clockwise',
  angle: 90
};

// Altitude command
const altitude: AltitudeCommand = {
  target_height: 150,
  mode: 'absolute'
};
```

### Camera Operations

```typescript
import { 
  PhotoCommand, 
  StreamingCommand, 
  LearningDataCommand 
} from '@mcp-drone/types';

// Photo command
const photo: PhotoCommand = {
  filename: 'aerial_shot.jpg',
  quality: 'high',
  metadata: {
    location: 'outdoor',
    weather: 'sunny'
  }
};

// Streaming command
const streaming: StreamingCommand = {
  action: 'start',
  quality: 'high',
  resolution: '720p'
};

// Learning data command
const learning: LearningDataCommand = {
  object_name: 'product_sample',
  capture_positions: ['front', 'back', 'left', 'right'],
  photos_per_position: 3,
  dataset_name: 'products_v1'
};
```

### Vision & AI

```typescript
import { 
  DetectionCommand, 
  TrackingCommand, 
  DetectionResponse 
} from '@mcp-drone/types';

// Object detection
const detection: DetectionCommand = {
  drone_id: 'drone_001',
  model_id: 'yolo_v8',
  confidence_threshold: 0.7
};

// Object tracking
const tracking: TrackingCommand = {
  action: 'start',
  drone_id: 'drone_001',
  model_id: 'yolo_v8',
  follow_distance: 200,
  confidence_threshold: 0.8
};

// Detection response
const detectionResult: DetectionResponse = {
  success: true,
  message: 'Objects detected',
  detections: [
    {
      label: 'person',
      confidence: 0.95,
      bbox: {
        x: 100,
        y: 100,
        width: 50,
        height: 100
      }
    }
  ],
  processing_time: 0.5,
  timestamp: '2023-01-01T12:00:00Z'
};
```

### System Information

```typescript
import { 
  SystemStatusResponse, 
  HealthResponse 
} from '@mcp-drone/types';

// System status
const systemStatus: SystemStatusResponse = {
  mcp_server: {
    status: 'running',
    uptime: 3600,
    version: '1.0.0',
    active_connections: 1
  },
  backend_system: {
    connection_status: 'connected',
    api_endpoint: 'http://backend:8000',
    response_time: 50
  },
  connected_drones: 1,
  active_operations: 0,
  system_health: 'healthy',
  timestamp: '2023-01-01T12:00:00Z'
};

// Health check
const health: HealthResponse = {
  status: 'healthy',
  checks: [
    {
      name: 'database',
      status: 'pass',
      message: 'Database connection healthy',
      response_time: 10
    }
  ],
  timestamp: '2023-01-01T12:00:00Z'
};
```

### Error Handling

```typescript
import { MCPError, ErrorCode } from '@mcp-drone/types';

// MCP error
const error: MCPError = {
  error: true,
  error_code: 'DRONE_NOT_FOUND',
  message: 'Drone not found',
  details: {
    suggested_corrections: ['Check drone ID']
  },
  timestamp: '2023-01-01T12:00:00Z'
};

// Using error codes
function handleError(errorCode: ErrorCode) {
  switch (errorCode) {
    case 'DRONE_NOT_FOUND':
      console.log('Drone not found');
      break;
    case 'DRONE_NOT_READY':
      console.log('Drone not ready');
      break;
    case 'AUTHENTICATION_FAILED':
      console.log('Authentication failed');
      break;
    default:
      console.log('Unknown error');
  }
}
```

### WebSocket Events

```typescript
import { WebSocketEvent, WebSocketEventType } from '@mcp-drone/types';

// WebSocket event
const event: WebSocketEvent = {
  type: 'drone_status_changed',
  data: {
    drone_id: 'drone_001',
    old_status: 'available',
    new_status: 'connected'
  },
  timestamp: '2023-01-01T12:00:00Z'
};

// Handle events
function handleWebSocketEvent(event: WebSocketEvent) {
  switch (event.type) {
    case 'drone_connected':
      console.log('Drone connected:', event.data);
      break;
    case 'drone_disconnected':
      console.log('Drone disconnected:', event.data);
      break;
    case 'command_executed':
      console.log('Command executed:', event.data);
      break;
    default:
      console.log('Unknown event:', event);
  }
}
```

### Type Guards

```typescript
import { 
  isMCPError, 
  isSuccessResponse, 
  isDroneInfo, 
  isCommandResponse 
} from '@mcp-drone/types';

// Type guard usage
function processResponse(response: any) {
  if (isMCPError(response)) {
    console.error('Error:', response.error_code, response.message);
    return;
  }
  
  if (isSuccessResponse(response)) {
    console.log('Success:', response.message);
  }
  
  if (isCommandResponse(response)) {
    console.log('Command result:', response.parsed_intent);
  }
}

// Validate drone info
function validateDrone(data: any): data is DroneInfo {
  return isDroneInfo(data);
}
```

### Constants & Endpoints

```typescript
import { 
  API_ENDPOINTS, 
  WEBSOCKET_ENDPOINTS, 
  DEFAULT_CONFIG, 
  VALIDATION_CONSTRAINTS 
} from '@mcp-drone/types';

// API endpoints
const droneStatusUrl = API_ENDPOINTS.GET_DRONE_STATUS('drone_001');
const commandUrl = API_ENDPOINTS.EXECUTE_COMMAND;

// WebSocket endpoint
const wsUrl = WEBSOCKET_ENDPOINTS.EVENTS;

// Default configuration
const config = {
  baseURL: 'http://localhost:8001',
  ...DEFAULT_CONFIG
};

// Validation constraints
const isValidHeight = (height: number) => {
  return height >= VALIDATION_CONSTRAINTS.TARGET_HEIGHT.min && 
         height <= VALIDATION_CONSTRAINTS.TARGET_HEIGHT.max;
};
```

### Utility Types

```typescript
import { 
  APIResponse, 
  PaginationParams, 
  PaginatedResponse, 
  FilterParams 
} from '@mcp-drone/types';

// API response wrapper
const apiResponse: APIResponse<DroneListResponse> = {
  data: {
    drones: [],
    count: 0,
    timestamp: '2023-01-01T12:00:00Z'
  },
  status: 200,
  headers: {
    'Content-Type': 'application/json'
  }
};

// Pagination
const paginationParams: PaginationParams = {
  page: 1,
  limit: 10,
  sort: 'name',
  order: 'asc'
};

// Filters
const filterParams: FilterParams = {
  type: 'real',
  status: 'available',
  search: 'test'
};
```

## Advanced Usage

### Custom Type Extensions

```typescript
import { DroneInfo, NaturalLanguageCommand } from '@mcp-drone/types';

// Extend existing types
interface ExtendedDroneInfo extends DroneInfo {
  customField: string;
  metadata: {
    location: string;
    owner: string;
  };
}

// Create command templates
interface CommandTemplate {
  name: string;
  command: string;
  description: string;
  parameters: string[];
}

const commandTemplates: CommandTemplate[] = [
  {
    name: 'connect',
    command: 'ドローン{drone_id}に接続して',
    description: 'Connect to drone',
    parameters: ['drone_id']
  },
  {
    name: 'takeoff',
    command: '高度{height}センチで離陸して',
    description: 'Takeoff to specified height',
    parameters: ['height']
  }
];
```

### Type-Safe API Client

```typescript
import { 
  MCPClientConfig, 
  CommandResponse, 
  DroneListResponse 
} from '@mcp-drone/types';

class TypeSafeMCPClient {
  constructor(private config: MCPClientConfig) {}
  
  async executeCommand(command: NaturalLanguageCommand): Promise<CommandResponse> {
    // Implementation with type safety
    throw new Error('Not implemented');
  }
  
  async getDrones(): Promise<DroneListResponse> {
    // Implementation with type safety
    throw new Error('Not implemented');
  }
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License

## Support

For issues and questions, please open an issue in the [GitHub repository](https://github.com/coolerking/mfg_drone_by_claudecode/issues).

## Changelog

### 1.0.0
- Initial release
- Complete type definitions for MCP API
- Type guards and validation utilities
- Constants and endpoint definitions
- WebSocket event types
- Comprehensive documentation