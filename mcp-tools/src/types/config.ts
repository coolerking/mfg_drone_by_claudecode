export interface ServerConfig {
  /** Backend API base URL */
  backendUrl: string;
  /** Request timeout in milliseconds */
  timeout: number;
  /** Number of retry attempts */
  retries: number;
  /** Debug mode flag */
  debug: boolean;
  /** Log level */
  logLevel: 'error' | 'warn' | 'info' | 'debug';
  /** Log file path */
  logFile?: string;
}

export interface MCPServerConfig extends ServerConfig {
  /** MCP server transport type */
  transport: 'stdio' | 'websocket' | 'http';
  /** Server port for websocket/http transport */
  port?: number;
  /** Server host for websocket/http transport */
  host?: string;
}

export const defaultConfig: ServerConfig = {
  backendUrl: 'http://localhost:8000',
  timeout: 5000,
  retries: 3,
  debug: false,
  logLevel: 'info'
};

export const defaultMCPConfig: MCPServerConfig = {
  ...defaultConfig,
  transport: 'stdio',
  port: 3000,
  host: 'localhost'
};