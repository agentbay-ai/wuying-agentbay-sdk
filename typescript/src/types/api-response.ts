/**
 * Base interface for API responses
 */
export interface ApiResponse {
  /** Optional request identifier for tracking API calls */
  requestId?: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
  /** Optional status code if the operation failed */
  success?: boolean;
}

/**
 * Generic interface for API responses that include data payload
 * @template T The type of the data being returned
 */
export interface ApiResponseWithData<T> extends ApiResponse {
  /** The actual data payload returned by the API */
  session?: T;
  data?: T;
}

/**
 * Interface for delete operation responses
 */
export interface DeleteResult extends ApiResponse {
  /** Whether the delete operation was successful */
  success: boolean;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for context information in GetSession response
 */
export interface ContextInfo {
  /** Context name */
  name: string;
  /** Context ID */
  id: string;
}

/**
 * Interface for GetSession data
 */
export interface GetSessionData {
  /** Application instance ID */
  appInstanceId: string;
  /** Resource ID */
  resourceId: string;
  /** Session ID */
  sessionId: string;
  /** Success status */
  success: boolean;
  /** HTTP port for VPC sessions */
  httpPort: string;
  /** Network interface IP for VPC sessions */
  networkInterfaceIp: string;
  /** Token for VPC sessions */
  token: string;
  /** LinkUrl for direct MCP tool calls (non-VPC) */
  linkUrl?: string;
  /** WebSocket URL for streaming/push features */
  wsUrl?: string;
  /** Whether this session uses VPC resources */
  vpcResource: boolean;
  /** VPC IP. Returned only for sessions created on a custom VPC network; empty otherwise. */
  vpcIp: string;
  /** VPC ID. Returned only for sessions created on a custom VPC network; empty otherwise. */
  vpcId: string;
  /** Resource URL for accessing the session */
  resourceUrl: string;
  /** Current status of the session */
  status: string;
  /** Tool list (JSON string) returned by GetSession */
  toolList?: string;
  /** List of contexts associated with the session */
  contexts?: ContextInfo[];
}

/**
 * Interface for GetSession operation responses
 */
export interface GetSessionResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** HTTP status code */
  httpStatusCode: number;
  /** Response code */
  code: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Session data */
  data?: GetSessionData;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for session creation operation responses
 * Corresponds to Python's SessionResult type
 */
export interface SessionResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the session creation was successful */
  success: boolean;
  /** The created session object (only present if successful) */
  session?: any; // Will be Session type, avoiding circular import
  /** Error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for operation results
 * Corresponds to Python's OperationResult type
 */
export interface OperationResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Optional data payload */
  data?: any;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Structured runtime metrics returned by Session.getMetrics().
 */
export interface SessionMetrics {
  cpuCount: number;
  cpuUsedPct: number;
  diskTotal: number;
  diskUsed: number;
  memTotal: number;
  memUsed: number;
  rxRateKbytePerS: number;
  txRateKbytePerS: number;
  rxUsedKbyte: number;
  txUsedKbyte: number;
  timestamp: string;
}

/**
 * Result of Session.getMetrics() operation.
 */
export interface SessionMetricsResult extends OperationResult {
  data?: SessionMetrics;
  raw?: Record<string, any>;
}

/**
 * Interface for session info operation responses
 * Corresponds to Go's InfoResult type
 */
export interface InfoResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Session information object */
  info?: any; // Will be SessionInfo type, avoiding circular import
}

/**
 * Interface for label operation responses
 * Corresponds to Go's LabelResult type
 */
export interface LabelResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Labels string (JSON format) */
  labels: string;
}

/**
 * Interface for link operation responses
 * Corresponds to Go's LinkResult type
 */
export interface LinkResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Link string */
  link: string;
}

/**
 * Interface for process list operation responses
 * Corresponds to Python's ProcessListResult type
 */
export interface Process {
  pname: string;
  pid: number;
  cmdline?: string;
}

export interface ProcessListResult extends OperationResult {
  data: Process[];
}

/**
 * Interface for installed app list operation responses
 * Corresponds to Python's InstalledAppListResult type
 */
// export interface InstalledAppListResult extends ApiResponse {
//   /** Request identifier for tracking API calls */
//   requestId: string;
//   /** Whether the operation was successful */
//   success: boolean;
//   /** The list of installed app objects */
//   data: any[]; // Will be InstalledApp[] type, avoiding circular import
//   /** Optional error message if the operation failed */
//   errorMessage?: string;
// }

export interface InstalledApp {
  name: string;
  startCmd: string;
  stopCmd?: string;
  workDirectory?: string;
}

export interface InstalledAppListResult extends OperationResult {
  data: InstalledApp[];
}

/**
 * Interface for application operation responses
 * Corresponds to Python's AppOperationResult type
 */
export interface AppOperationResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for application info operation responses
 * Corresponds to Python's AppInfoResult type
 */
export interface AppInfoResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Application information */
  appInfo: Record<string, any>;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for application list operation responses
 * Corresponds to Python's AppListResult type
 */
export interface AppListResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** List of applications */
  apps: Record<string, any>[];
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for application installation responses
 * Corresponds to Python's AppInstallResult type
 */
export interface AppInstallResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the installation was successful */
  success: boolean;
  /** Result description or error message */
  message: string;
}

/**
 * Interface for command execution operation responses
 * Corresponds to Python's CommandResult type
 */
export interface CommandResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the command execution was successful */
  success: boolean;
  /** The command output (for backward compatibility, equals stdout + stderr) */
  output: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
  /** The exit code of the command execution. Default is 0. */
  exitCode?: number;
  /** Standard output from the command execution */
  stdout?: string;
  /** Standard error from the command execution */
  stderr?: string;
  /** Trace ID for error tracking. Only present when exit_code != 0. Used for quick problem localization. */
  traceId?: string;
}

/**
 * Interface for single result item in enhanced code execution
 */
export interface CodeExecutionResultItem {
  text?: string;
  html?: string;
  markdown?: string;
  png?: string;
  jpeg?: string;
  svg?: string;
  latex?: string;
  json?: any;
  chart?: any;
  isMainResult?: boolean;
}

/**
 * Interface for code execution logs
 */
export interface CodeExecutionLogs {
  stdout: string[];
  stderr: string[];
}

/**
 * Interface for code execution error details
 */
export interface CodeExecutionError {
  name: string;
  value: string;
  traceback: string;
}

/**
 * Interface for code execution operation responses
 * Corresponds to Python's EnhancedCodeExecutionResult type
 */
export interface CodeExecutionResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the code execution was successful */
  success: boolean;
  /** The execution result (backward compatible text) */
  result: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;

  /** Enhanced fields */
  logs?: CodeExecutionLogs;
  results?: CodeExecutionResultItem[];
  error?: CodeExecutionError;
  executionTime?: number;
  executionCount?: number;
}

/**
 * Interface for boolean operation responses
 * Corresponds to Python's BoolResult type
 */
export interface BoolResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Boolean data result */
  data?: boolean;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for file info operation responses
 * Corresponds to Python's FileInfoResult type
 */
export interface FileInfoResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** File information object */
  fileInfo?: Record<string, any>;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for directory list operation responses
 * Corresponds to Python's DirectoryListResult type
 */
export interface DirectoryListResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Directory entries */
  entries: Record<string, any>[];
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for file content operation responses
 * Corresponds to Python's FileContentResult type
 */
export interface FileContentResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** File content */
  content: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for binary file content operation responses
 * Corresponds to Python's BinaryFileContentResult type
 */
export interface BinaryFileContentResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Binary file content */
  content: Uint8Array;
  /** Optional error message if the operation failed */
  errorMessage?: string;
  /** Optional MIME type of the file */
  contentType?: string;
  /** Optional size of the file in bytes */
  size?: number;
}

/**
 * Interface for multiple file content operation responses
 * Corresponds to Python's MultipleFileContentResult type
 */
export interface MultipleFileContentResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Multiple file contents */
  contents: Record<string, string>;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for file search operation responses
 * Corresponds to Python's FileSearchResult type
 */
export interface FileSearchResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Matching file paths */
  matches: string[];
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for OSS client creation operation responses
 * Corresponds to Python's OSSClientResult type
 */
export interface OSSClientResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** OSS client configuration */
  clientConfig: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for OSS upload operation responses
 * Corresponds to Python's OSSUploadResult type
 */
export interface OSSUploadResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Result of the upload operation */
  content: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for OSS download operation responses
 * Corresponds to Python's OSSDownloadResult type
 */
export interface OSSDownloadResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Result of the download operation */
  content: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for UI element list operation responses
 * Corresponds to Python's UIElementListResult type
 */
export interface UIElementListResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** UI elements */
  elements: Record<string, any>[];
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

export interface WindowInfo {
  windowId: number;
  title: string;
  pid: number;
  pname: string;
}

/**
 * Interface for window list operation responses
 * Corresponds to Python's WindowListResult type
 */
export interface WindowListResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** List of windows */
  windows: WindowInfo[]; // Will be Window[] type, avoiding circular import
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

export interface Window {
  windowId: number;
  title: string;
  absoluteUpperLeftX?: number;
  absoluteUpperLeftY?: number;
  width?: number;
  height?: number;
  pid?: number;
  pname?: string;
  childWindows?: Window[];
}

/**
 * Interface for window info operation responses
 * Corresponds to Python's WindowInfoResult type
 */
export interface WindowInfoResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Window object */
  window?: Window[]; // Will be Window type, avoiding circular import
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for context operation responses
 * Corresponds to Python's ContextResult type
 */
export interface ContextResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** The context ID */
  contextId: string;
  /** The context object (only present if successful) */
  context?: any; // Will be Context type, avoiding circular import
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for context list operation responses
 * Corresponds to Python's ContextListResult type
 */
export interface ContextListResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** List of contexts */
  contexts: any[]; // Will be Context[] type, avoiding circular import
  /** Token for the next page of results */
  nextToken?: string;
  /** Maximum number of results per page */
  maxResults?: number;
  /** Total number of contexts available */
  totalCount?: number;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for network create operation responses.
 */
export interface NetworkResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Created/returned network id */
  networkId: string;
  /** Network token for the created network */
  networkToken: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Interface for network describe operation responses.
 */
export interface NetworkStatusResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Whether network is online */
  online: boolean;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Result of a presigned URL request
 */
export interface FileUrlResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** The presigned URL */
  url: string;
  /** Optional expire time (epoch seconds) */
  expireTime?: number;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Represents a file item in a context
 */
export interface ContextFileEntry {
  fileId?: string;
  fileName?: string;
  filePath: string;
  fileType?: string;
  gmtCreate?: string;
  gmtModified?: string;
  size?: number;
  status?: string;
}

/**
 * Result of context file listing
 */
export interface ContextFileListResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** File entries under a folder */
  entries: ContextFileEntry[];
  /** Optional total count returned by backend */
  count?: number;
  /** Token for the next page when using MaxResults/NextToken pagination */
  nextToken?: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Helper function to extract request ID from API responses
 */
export function extractRequestId(response: any): string | undefined {
  if (!response) return undefined;

  // If response is a string (like body?.requestId), return it directly
  if (typeof response === "string" && response.length > 0) {
    return response;
  }

  // Check for requestId in response.body first
  if (response.body && response.body.requestId) {
    return response.body.requestId;
  }
  // Check for requestId directly on response
  if (response.requestId) {
    return response.requestId;
  }

  return undefined;
}

/**
 * Result of context clear operations, including the real-time status.
 * Corresponds to Python's ClearContextResult type
 */
export interface ClearContextResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the operation was successful */
  success: boolean;
  /** Current status of the clearing task. This corresponds to the
      context's state field. Possible values:
      - "clearing": Context data is being cleared (in progress)
      - "available": Clearing completed successfully
      - Other values may indicate the context state after clearing */
  status?: string;
  /** The unique identifier of the context being cleared */
  contextId?: string;
  /** Optional error message if the operation failed */
  errorMessage?: string;
}

/**
 * Result of session pause operations.
 */
export interface SessionPauseResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the pause operation was successful */
  success: boolean;
  /** Error message if the operation failed */
  errorMessage?: string;
  /** API error code */
  code?: string;
  /** Detailed error message from API */
  message?: string;
  /** HTTP status code */
  httpStatusCode?: number;
  /** Current status of the session. Possible values: "RUNNING", "PAUSED", "PAUSING" */
  status?: string;
}

/**
 * Result of session resume operations.
 */
export interface SessionResumeResult extends ApiResponse {
  /** Request identifier for tracking API calls */
  requestId: string;
  /** Whether the resume operation was successful */
  success: boolean;
  /** Error message if the operation failed */
  errorMessage?: string;
  /** API error code */
  code?: string;
  /** Detailed error message from API */
  message?: string;
  /** HTTP status code */
  httpStatusCode?: number;
  /** Current status of the session. Possible values: "RUNNING", "PAUSED", "RESUMING" */
  status?: string;
}

/**
 * Represents the screen dimensions and DPI scaling information.
 *
 * @interface ScreenSize
 * @extends OperationResult
 */
export interface ScreenSize extends OperationResult {
  /** Screen width in pixels */
  width: number;
  /** Screen height in pixels */
  height: number;
  /** DPI scaling factor (e.g., 1.0 for 100%, 1.5 for 150%, 2.0 for 200%) */
  dpiScalingFactor: number;
}

/**
 * Represents the current cursor position on screen.
 *
 * @interface CursorPosition
 * @extends OperationResult
 */
export interface CursorPosition extends OperationResult {
  /** X coordinate in pixels (0 is left edge of screen) */
  x: number;
  /** Y coordinate in pixels (0 is top edge of screen) */
  y: number;
}

/**
 * Represents a single context binding entry returned by DescribeSessionContexts.
 */
export interface ContextBinding {
  contextId: string;
  contextName?: string;
  path: string;
  policy?: string;
  bindTime?: string;
}

/**
 * Result of a bind() operation on contexts.
 */
export interface ContextBindResult extends ApiResponse {
  requestId: string;
  success: boolean;
  errorMessage?: string;
}

/**
 * Result of a listBindings() operation.
 */
export interface ContextBindingsResult extends ApiResponse {
  requestId: string;
  success: boolean;
  bindings: ContextBinding[];
  errorMessage?: string;
}
