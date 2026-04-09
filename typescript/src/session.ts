import { AgentBay } from "./agent-bay";
import { Agent } from "./agent/agent";
import { Client } from "./api/client";
import * as $_client from "./api";
import {
  CallMcpToolRequest,
  DeleteSessionAsyncRequest,
  GetLabelRequest,
  GetLinkRequest,
  GetMcpResourceRequest,
  GetSessionDetailRequest,
  ListMcpToolsRequest,
  RefreshSessionIdleTimeRequest,
  SetLabelRequest,
} from "./api/models/model";
import { Browser } from "./browser";
import { Code } from "./code";
import { Command } from "./command";
import { Computer } from "./computer";
import { Env } from "./env";
import {
  ContextManager,
  ContextSyncResult,
  newContextManager,
} from "./context-manager";
import { FileSystem } from "./filesystem";
import { Git } from "./git";
import { Mobile } from "./mobile";
import { Oss } from "./oss";
import { WsClient } from "./_internal/ws-client";
import {
  ApiResponse,
  DeleteResult,
  extractRequestId,
  OperationResult,
  SessionPauseResult,
  SessionResumeResult,
  SessionMetrics,
  SessionMetricsResult,
} from "./types/api-response";
import {
  logError,
  logInfo,
  logDebug,
  logWarn,
  logAPICall,
  logAPIResponseWithDetails,
  logCodeExecutionOutput,
  logInfoWithColor,
  setRequestId,
} from "./utils/logger";

async function fetchCompat(
  input: any,
  init: any,
  timeoutMs?: number
): Promise<any> {
  // Add timeout support using AbortController if timeout is specified
  if (timeoutMs && timeoutMs > 0) {
    // Use globalThis.AbortController for better compatibility
    const AbortControllerClass = (globalThis as any).AbortController;
    if (!AbortControllerClass) {
      // If AbortController is not available, fallback to fetch without timeout
      const f = (globalThis as any).fetch;
      if (typeof f === "function") {
        return await f(input, init);
      }

      const mod: any = await import("node-fetch");
      const nodeFetch = mod.default || mod;
      return await nodeFetch(input, init);
    }

    const controller = new AbortControllerClass();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    init = {
      ...init,
      signal: controller.signal,
    };

    try {
      const f = (globalThis as any).fetch;
      if (typeof f === "function") {
        const response = await f(input, init);
        clearTimeout(timeoutId);
        return response;
      }

      const mod: any = await import("node-fetch");
      const nodeFetch = mod.default || mod;
      const response = await nodeFetch(input, init);
      clearTimeout(timeoutId);
      return response;
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === "AbortError") {
        throw new Error(`Request timeout after ${timeoutMs}ms`);
      }
      throw error;
    }
  }

  const f = (globalThis as any).fetch;
  if (typeof f === "function") {
    return await f(input, init);
  }

  const mod: any = await import("node-fetch");
  const nodeFetch = mod.default || mod;
  return await nodeFetch(input, init);
}

/**
 * Represents an MCP tool with complete information.
 */
export interface McpTool {
  name: string;
  description: string;
  inputSchema: Record<string, any>;
  server: string;
  tool: string;
}

/**
 * Result containing MCP tools list and request ID.
 */
export interface McpToolsResult extends OperationResult {
  tools: McpTool[];
}

/**
 * Result containing MCP resource information and request ID.
 */
export interface McpResourceResult extends OperationResult {
  uri: string;
  name: string;
  description: string;
  mimeType: string;
}

/**
 * Result containing MCP resource content and request ID.
 */
export interface McpResourceContentResult extends OperationResult {
  contents: Array<{
    uri: string;
    mimeType: string;
    text?: string;
    blob?: string;
  }>;
}

/**
 * Result of Session.getStatus() (status only).
 */
export interface SessionStatusResult extends ApiResponse {
  requestId: string;
  httpStatusCode: number;
  code: string;
  success: boolean;
  status: string;
  errorMessage?: string;
}

/**
 * Contains information about a session.
 */
export interface SessionInfo {
  sessionId: string;
  resourceUrl: string;
  appId?: string;
  authCode?: string;
  connectionProperties?: string;
  resourceId?: string;
  resourceType?: string;
  ticket?: string;
}

/**
 * SessionInfo class to match Python version structure
 */
export class SessionInfoClass {
  sessionId: string;
  resourceUrl: string;
  appId: string;
  authCode: string;
  connectionProperties: string;
  resourceId: string;
  resourceType: string;
  ticket: string;

  constructor(
    sessionId = "",
    resourceUrl = "",
    appId = "",
    authCode = "",
    connectionProperties = "",
    resourceId = "",
    resourceType = "",
    ticket = ""
  ) {
    this.sessionId = sessionId;
    this.resourceUrl = resourceUrl;
    this.appId = appId;
    this.authCode = authCode;
    this.connectionProperties = connectionProperties;
    this.resourceId = resourceId;
    this.resourceType = resourceType;
    this.ticket = ticket;
  }
}

/**
 * Represents a session in the AgentBay cloud environment.
 */
export class Session {
  private agentBay: AgentBay;
  public sessionId: string;

  // Resource URL for accessing the session
  public resourceUrl = "";

  // LinkUrl-based direct tool call (non-VPC)
  public token = "";
  public linkUrl = "";

  // WS long connection URL (for streaming output)
  public wsUrl = "";
  private _wsClient: WsClient | null = null;

  // Recording functionality
  public enableBrowserReplay?: boolean; // Whether browser recording is enabled for this session (undefined = server default)

  // File, command, code, and oss handlers (matching Python naming)
  public fileSystem: FileSystem; // file_system in Python
  public command: Command;
  public env: Env;
  public code: Code;
  public oss: Oss;

  // Computer and Mobile automation (new modules)
  public computer: Computer;
  public mobile: Mobile;

  // Agent for task execution
  public agent: Agent;

  // Browser for web automation
  public browser: Browser;

  // Git operations
  public git: Git;

  // Context management (matching Go version)
  public context: ContextManager;

  // MCP tools list returned by backend for this session
  public mcpTools: McpTool[] = [];

  /**
   * Initialize a Session object.
   *
   * @param agentBay - The AgentBay instance that created this session.
   * @param sessionId - The ID of this session.
   */
  constructor(agentBay: AgentBay, sessionId: string) {
    this.agentBay = agentBay;
    this.sessionId = sessionId;

    // Initialize file system, command and code handlers (matching Python naming)
    this.fileSystem = new FileSystem(this);
    this.command = new Command(this);
    this.env = new Env(this);
    this.code = new Code(this);
    this.oss = new Oss(this);

    // Initialize Computer and Mobile modules
    this.computer = new Computer(this);
    this.mobile = new Mobile(this);

    // Initialize Agent
    this.agent = new Agent(this);

    // Initialize Browser
    this.browser = new Browser(this);

    // Initialize Git
    this.git = new Git(this);

    // Initialize context manager (matching Go version)
    this.context = newContextManager(this);
  }

  /**
   * Internal helper for WS streaming features.
   */
  async getWsClient(): Promise<WsClient> {
    if (!this.wsUrl) {
      throw new Error("Missing wsUrl on session; streaming is not available");
    }
    if (!this.token) {
      throw new Error("Missing token on session; streaming is not available");
    }
    if (!this._wsClient) {
      this._wsClient = new WsClient(this.wsUrl, this.token);
    }
    await this._wsClient.connect();
    return this._wsClient;
  }

  /**
   * Alias of fileSystem.
   */
  get fs(): FileSystem {
    return this.fileSystem;
  }

  /**
   * Alias of fileSystem.
   */
  get filesystem(): FileSystem {
    return this.fileSystem;
  }

  /**
   * Alias of fileSystem.
   */
  get files(): FileSystem {
    return this.fileSystem;
  }

  /**
   * Return the AgentBay instance that created this session.
   *
   * @returns The AgentBay client instance
   * @internal
   */
  getAgentBay(): AgentBay {
    return this.agentBay;
  }

  /**
   * Return the API key for this session.
   * Note: This method is used internally by SDK modules (Code, Computer, Mobile, Agent).
   *
   * @returns The API key string
   * @internal
   */
  getAPIKey(): string {
    return this.agentBay.getAPIKey();
  }

  /**
   * @deprecated Internal SDK use only. Will be removed in a future version.
   */
  getToken(): string {
    return this.token;
  }

  /**
   * @deprecated Internal SDK use only. Will be removed in a future version.
   */
  getLinkUrl(): string {
    return this.linkUrl;
  }

  /**
   * Return the HTTP client for this session.
   *
   * @returns The Client instance used for API communication
   * @internal
   */
  getClient(): Client {
    return this.agentBay.getClient();
  }

  /**
   * Return the session_id for this session.
   * Note: This method is used internally by SDK modules. Users should prefer using the `sessionId` property.
   *
   * @returns The session ID string
   * @internal
   */
  getSessionId(): string {
    return this.sessionId;
  }

  /**
   * Get basic session status.
   *
   * @returns SessionStatusResult containing status only.
   */
  async getStatus(): Promise<SessionStatusResult> {
    try {
      logAPICall("GetSessionDetail", { sessionId: this.sessionId });

      const request = new GetSessionDetailRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId,
      });

      const response = await this.getClient().getSessionDetail(request);
      const body = response.body;
      const requestId = extractRequestId(response) || body?.requestId || "";

      setRequestId(requestId);

      // Check for API-level errors
      if (body?.success === false && body.code) {
        logAPIResponseWithDetails(
          "GetSessionDetail",
          requestId,
          false,
          {},
          `[${body.code}] ${body.message || "Unknown error"}`
        );
        logDebug(
          "Full GetSessionDetail response:",
          JSON.stringify(body, null, 2)
        );
        return {
          requestId,
          httpStatusCode: body.httpStatusCode || 0,
          code: body.code,
          success: false,
          status: "",
          errorMessage: `[${body.code}] ${body.message || "Unknown error"}`,
        };
      }

      const result: SessionStatusResult = {
        requestId,
        httpStatusCode: body?.httpStatusCode || 0,
        code: body?.code || "",
        success: body?.success || false,
        status: body?.data?.status || "",
        errorMessage: "",
      };

      logAPIResponseWithDetails("GetSessionDetail", requestId, true, {
        status: result.status,
      });

      return result;
    } catch (error: any) {
      const errorStr = String(error);
      const errorCode = error?.data?.Code || error?.code || "";

      if (
        errorCode === "InvalidMcpSession.NotFound" ||
        errorStr.includes("NotFound")
      ) {
        logInfoWithColor(`Session not found: ${this.sessionId}`);
        logDebug(`GetSessionDetail error details: ${errorStr}`);
        return {
          requestId: "",
          httpStatusCode: 400,
          code: "InvalidMcpSession.NotFound",
          success: false,
          status: "",
          errorMessage: `Session ${this.sessionId} not found`,
        };
      }

      logError("Error calling GetSessionDetail:", error);
      return {
        requestId: "",
        httpStatusCode: 0,
        code: "",
        success: false,
        status: "",
        errorMessage: `Failed to get session detail ${this.sessionId}: ${error}`,
      };
    }
  }

  /**
   * Refresh the backend idle timer for this session.
   *
   * This method calls the RefreshSessionIdleTime API.
   */
  async keepAlive(): Promise<OperationResult> {
    try {
      logAPICall("RefreshSessionIdleTime", { sessionId: this.sessionId });

      const request = new RefreshSessionIdleTimeRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId,
      });

      const response = await this.getClient().refreshSessionIdleTime(request);
      const requestId =
        extractRequestId(response) || response?.body?.requestId || "";

      const body = response?.body;
      if (body?.success === false && body.code) {
        const errorMessage = `[${body.code}] ${
          body.message || "Unknown error"
        }`;
        logAPIResponseWithDetails(
          "RefreshSessionIdleTime",
          requestId,
          false,
          {},
          JSON.stringify(body, null, 2)
        );
        return {
          requestId,
          success: false,
          errorMessage,
        };
      }

      logAPIResponseWithDetails("RefreshSessionIdleTime", requestId, true, {
        session_id: this.sessionId,
      });

      return {
        requestId,
        success: true,
      };
    } catch (error) {
      logError("Error calling RefreshSessionIdleTime:", error);
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to keep session alive ${this.sessionId}: ${error}`,
      };
    }
  }

  /**
   * Alias of keepAlive for API compatibility.
   */
  async keepAliveAsync(): Promise<OperationResult> {
    return await this.keepAlive();
  }

  /**
   * Delete this session.
   *
   * @param syncContext - Whether to sync context data (trigger file uploads) before deleting the session. Defaults to false.
   * @returns DeleteResult indicating success or failure and request ID
   */
  /**
   * Deletes the session and releases all associated resources.
   *
   * @param syncContext - Whether to synchronize context data before deletion.
   *                      If true, uploads all context data to OSS.
   *                      If false but browser replay is enabled, syncs only the recording context.
   *                      Defaults to false.
   *
   * @returns Promise resolving to DeleteResult containing:
   *          - success: Whether deletion succeeded
   *          - requestId: Unique identifier for this API request
   *          - errorMessage: Error description if deletion failed
   *
   * @throws Error if the API call fails or network issues occur.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.fileSystem.writeFile('/tmp/data.txt', 'data');
   *   const deleteResult = await result.session.delete(true);
   *   console.log('Session deleted:', deleteResult.success);
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - If `syncContext=true`: Uploads all context data to OSS before deletion
   * - If `syncContext=false` but browser replay enabled: Syncs only recording context
   * - If `syncContext=false` and no browser replay: Deletes immediately without sync
   * - Continues with deletion even if context sync fails
   * - Releases all associated resources (browser, computer, mobile, etc.)
   *
   * **Best Practices:**
   * - Use `syncContext=true` when you need to preserve context data for later retrieval
   * - For temporary sessions, use `syncContext=false` for faster cleanup
   * - Always call `delete()` when done to avoid resource leaks
   * - Handle deletion errors gracefully in production code
   *
   * @see {@link info}, {@link ContextManager.sync}
   */
  async delete(syncContext = false): Promise<DeleteResult> {
    try {
      if (this._wsClient) {
        try {
          await this._wsClient.close();
        } catch (_e) {}
        this._wsClient = null;
      }
      if (syncContext) {
        logDebug(
          "Triggering context synchronization before session deletion..."
        );

        // Use the new sync method without callback (sync mode)
        const syncStartTime = Date.now();

        try {
          // Sync all contexts
          const syncResult: ContextSyncResult = await this.context.sync();
          logInfo("🔄 Synced all contexts");

          const syncDuration = Date.now() - syncStartTime;

          if (syncResult.success) {
            logInfo(`Context sync completed in ${syncDuration}ms`);
          } else {
            logInfo(
              `Context sync completed with failures after ${syncDuration}ms`
            );
          }
        } catch (error) {
          const syncDuration = Date.now() - syncStartTime;
          logError(
            `Failed to trigger context sync after ${syncDuration}ms:`,
            error
          );
          // Continue with deletion even if sync fails
        }
      }

      // Proceed with session deletion
      const request = new DeleteSessionAsyncRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId,
      });

      const response = await this.getClient().deleteSessionAsync(request);
      logDebug(
        `Response from delete_session_async: ${JSON.stringify(response)}`
      );

      // Extract request ID
      const requestId = extractRequestId(response) || "";

      // Check if the response is success (matching Python logic)
      const responseBody = response.body;
      const success = responseBody?.success !== false; // Note: capital S to match Python

      if (!success) {
        const errorMessage = `[${responseBody?.code || "Unknown"}] ${
          responseBody?.message || "Failed to delete session"
        }`;
        logAPIResponseWithDetails(
          "DeleteSessionAsync",
          requestId,
          false,
          {},
          JSON.stringify(responseBody, null, 2)
        );
        return {
          requestId,
          success: false,
          errorMessage,
        };
      }

      // Poll for session deletion status
      logInfo(`🔄 Waiting for session ${this.sessionId} to be deleted...`);
      const pollTimeout = 300000; // 5 minutes timeout
      const pollInterval = 1000; // Poll every 1 second
      const pollStartTime = Date.now();

      while (true) {
        // Check timeout
        const elapsedTime = Date.now() - pollStartTime;
        if (elapsedTime >= pollTimeout) {
          const errorMessage = `Timeout waiting for session deletion after ${pollTimeout}ms`;
          logWarn(`⏱️  ${errorMessage}`);
          return {
            requestId,
            success: false,
            errorMessage,
          };
        }

        // Get session status
        const sessionResult = await this.getStatus();

        // Check if session is deleted (NotFound error)
        if (!sessionResult.success) {
          const errorCode = sessionResult.code || "";
          const errorMessage = sessionResult.errorMessage || "";
          const httpStatusCode = sessionResult.httpStatusCode || 0;

          // Check for InvalidMcpSession.NotFound, 400 with "not found", or error_message containing "not found"
          const isNotFound =
            errorCode === "InvalidMcpSession.NotFound" ||
            (httpStatusCode === 400 &&
              (errorMessage.toLowerCase().includes("not found") ||
                errorMessage.includes("NotFound") ||
                errorCode.toLowerCase().includes("not found"))) ||
            errorMessage.toLowerCase().includes("not found");

          if (isNotFound) {
            // Session is deleted
            logInfo(
              `✅ Session ${this.sessionId} successfully deleted (NotFound)`
            );
            break;
          } else {
            // Other error, continue polling
            logDebug(`⚠️  Get session error (will retry): ${errorMessage}`);
            // Continue to next poll iteration
          }
        }
        // Check session status if we got valid data
        else if (sessionResult.status) {
          const status = sessionResult.status;
          logDebug(`📊 Session status: ${status}`);
          if (status === "FINISH") {
            logInfo(`✅ Session ${this.sessionId} successfully deleted`);
            break;
          }
        }

        // Wait before next poll
        await new Promise((resolve) => setTimeout(resolve, pollInterval));
      }

      // Log successful deletion
      logAPIResponseWithDetails("DeleteSessionAsync", requestId, true, {
        sessionId: this.sessionId,
      });

      // Return success result with request ID
      return {
        requestId,
        success: true,
      };
    } catch (error) {
      logError("Error calling delete_session_async:", error);
      // In case of error, return failure result with error message (matching Python)
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to delete session ${this.sessionId}: ${error}`,
      };
    }
  }

  /**
   * Validates labels parameter for label operations.
   *
   * @param labels - The labels to validate
   * @returns null if validation passes, or OperationResult with error if validation fails
   */
  private validateLabels(
    labels: Record<string, string>
  ): OperationResult | null {
    // Check if labels is null, undefined, or invalid type
    if (!labels || typeof labels !== "object") {
      return {
        requestId: "",
        success: false,
        errorMessage:
          "Labels cannot be null, undefined, or invalid type. Please provide a valid labels object.",
      };
    }

    // Check if labels is an array or other non-plain object
    if (Array.isArray(labels)) {
      return {
        requestId: "",
        success: false,
        errorMessage:
          "Labels cannot be an array. Please provide a valid labels object.",
      };
    }

    // Check if labels is a Date, RegExp, or other built-in object types
    if (
      labels instanceof Date ||
      labels instanceof RegExp ||
      labels instanceof Error ||
      labels instanceof Map ||
      labels instanceof Set ||
      labels instanceof WeakMap ||
      labels instanceof WeakSet ||
      labels instanceof Promise
    ) {
      return {
        requestId: "",
        success: false,
        errorMessage:
          "Labels must be a plain object. Built-in object types are not allowed.",
      };
    }

    // Check if labels object is empty
    if (Object.keys(labels).length === 0) {
      return {
        requestId: "",
        success: false,
        errorMessage:
          "Labels cannot be empty. Please provide at least one label.",
      };
    }

    for (const [key, value] of Object.entries(labels)) {
      // Check key validity
      if (!key || key.trim() === "") {
        return {
          requestId: "",
          success: false,
          errorMessage: "Label keys cannot be empty Please provide valid keys.",
        };
      }

      // Check value is not null or undefined
      if (!value || value.trim() === "") {
        return {
          requestId: "",
          success: false,
          errorMessage:
            "Label values cannot be empty Please provide valid values.",
        };
      }
    }

    // Validation passed
    return null;
  }

  /**
   * Sets the labels for this session.
   *
   * @param labels - The labels to set for the session.
   * @returns OperationResult indicating success or failure with request ID
   * @throws Error if the operation fails (matching Python SessionError)
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const setResult = await result.session.setLabels({ project: 'demo', env: 'test' });
   *   console.log('Labels set:', setResult.success);
   *   await result.session.delete();
   * }
   * ```
   */
  async setLabels(labels: Record<string, string>): Promise<OperationResult> {
    try {
      // Validate labels using the extracted validation function
      const validationResult = this.validateLabels(labels);
      if (validationResult !== null) {
        return validationResult;
      }

      // Convert labels to JSON string
      const labelsJSON = JSON.stringify(labels);

      const request = new SetLabelRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId,
        labels: labelsJSON,
      });

      const response = await this.getClient().setLabel(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";

      return {
        requestId,
        success: true,
      };
    } catch (error) {
      logError("Error calling set_label:", error);
      throw new Error(
        `Failed to set labels for session ${this.sessionId}: ${error}`
      );
    }
  }

  /**
   * Gets the labels for this session.
   *
   * @returns OperationResult containing the labels as data and request ID
   * @throws Error if the operation fails (matching Python SessionError)
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.setLabels({ project: 'demo', env: 'test' });
   *   const getResult = await result.session.getLabels();
   *   console.log('Labels:', JSON.stringify(getResult.data));
   *   await result.session.delete();
   * }
   * ```
   */
  async getLabels(): Promise<OperationResult> {
    try {
      const request = new GetLabelRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId,
      });

      const response = await this.getClient().getLabel(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";

      // Extract labels from response (matching Python structure)
      const responseBody = response?.body;
      const data = responseBody?.data; // Capital D to match Python
      const labelsJSON = data?.labels; // Capital L to match Python

      let labels = {};
      if (labelsJSON) {
        labels = JSON.parse(labelsJSON);
      }

      return {
        requestId,
        success: true,
        data: labels,
      };
    } catch (error) {
      logError("Error calling get_label:", error);
      throw new Error(
        `Failed to get labels for session ${this.sessionId}: ${error}`
      );
    }
  }

  /**
   * Retrieves detailed information about the current session.
   *
   * @returns Promise resolving to OperationResult containing:
   *          - success: Whether the operation succeeded (always true if no exception)
   *          - data: SessionInfo object with the following fields:
   *            - sessionId (string): The session identifier
   *            - resourceUrl (string): URL for accessing the session
   *            - appId (string): Application ID (for desktop sessions)
   *            - authCode (string): Authentication code
   *            - connectionProperties (string): Connection configuration
   *            - resourceId (string): Resource identifier
   *            - resourceType (string): Type of resource (e.g., "Desktop")
   *            - ticket (string): Access ticket
   *          - requestId: Unique identifier for this API request
   *          - errorMessage: Error description if operation failed
   *
   * @throws Error if the API request fails or response is invalid.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const infoResult = await result.session.info();
   *   console.log(`Session ID: ${infoResult.data.sessionId}`);
   *   console.log(`Resource URL: ${infoResult.data.resourceUrl}`);
   *   await result.session.delete();
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - This method calls the GetMcpResource API to retrieve session metadata
   * - The returned SessionInfo contains:
   *   - sessionId: The session identifier
   *   - resourceUrl: URL for accessing the session
   *   - Desktop-specific fields (appId, authCode, connectionProperties, etc.)
   *     are populated from the DesktopInfo section of the API response
   * - Session info is retrieved from the AgentBay API in real-time
   * - The resourceUrl can be used for browser-based access
   * - Desktop-specific fields (appId, authCode) are only populated for desktop sessions
   * - This method does not modify the session state
   *
   * @see {@link delete}, {@link getLink}
   */
  async info(): Promise<OperationResult> {
    try {
      const request = new GetMcpResourceRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId,
      });

      logAPICall("GetMcpResource");
      logDebug(`Request: SessionId=${this.sessionId}`);

      const response = await this.getClient().getMcpResource(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";

      // Check for API-level errors
      if (response?.body?.success === false && response.body?.code) {
        const errorMessage = `[${response.body.code}] ${
          response.body.message || "Unknown error"
        }`;
        const fullResponse = response.body
          ? JSON.stringify(response.body, null, 2)
          : "";
        logAPIResponseWithDetails(
          "GetMcpResource",
          requestId,
          false,
          undefined,
          fullResponse
        );
        return {
          requestId,
          success: false,
          errorMessage,
        };
      }

      // Extract session info from response (matching Python structure)
      const responseBody = response.body;
      const data = responseBody?.data; // Capital D to match Python

      const sessionInfo = new SessionInfoClass();

      if (data?.sessionId) {
        // Capital S and I to match Python
        sessionInfo.sessionId = data.sessionId;
      }

      if (data?.resourceUrl) {
        // Capital R and U to match Python
        sessionInfo.resourceUrl = data.resourceUrl;
      }

      // Transfer DesktopInfo fields to SessionInfo (matching Python structure)
      if (data?.desktopInfo) {
        // Capital D and I to match Python
        const desktopInfo = data.desktopInfo;
        if (desktopInfo.appId) {
          sessionInfo.appId = desktopInfo.appId;
        }
        if (desktopInfo.authCode) {
          sessionInfo.authCode = desktopInfo.authCode;
        }
        if (desktopInfo.connectionProperties) {
          sessionInfo.connectionProperties = desktopInfo.connectionProperties;
        }
        if (desktopInfo.resourceId) {
          sessionInfo.resourceId = desktopInfo.resourceId;
        }
        if (desktopInfo.resourceType) {
          sessionInfo.resourceType = desktopInfo.resourceType;
        }
        if (desktopInfo.ticket) {
          sessionInfo.ticket = desktopInfo.ticket;
        }
      }

      // Log API response with key fields
      const keyFields: Record<string, any> = {
        session_id: this.sessionId,
      };
      if (sessionInfo.resourceUrl) {
        keyFields.resource_url = sessionInfo.resourceUrl;
      }
      if (sessionInfo.appId) {
        keyFields.app_id = sessionInfo.appId;
      }
      const fullResponse = responseBody
        ? JSON.stringify(responseBody, null, 2)
        : "";
      logAPIResponseWithDetails(
        "GetMcpResource",
        requestId,
        true,
        keyFields,
        fullResponse
      );

      return {
        requestId,
        success: true,
        data: sessionInfo,
      };
    } catch (error: any) {
      // Check if this is an expected business error (e.g., session not found)
      const errorStr = String(error);
      const errorCode = error?.data?.Code || error?.code || "";

      if (
        errorCode === "InvalidMcpSession.NotFound" ||
        errorStr.includes("NotFound")
      ) {
        // This is an expected error - session doesn't exist
        // Use info level logging without stack trace, but with red color for visibility
        logInfoWithColor(`Session not found: ${this.sessionId}`);
        logDebug(`GetMcpResource error details: ${errorStr}`);
        return {
          requestId: "",
          success: false,
          errorMessage: `Session ${this.sessionId} not found`,
        };
      } else {
        // This is an unexpected error - log with full error
        logError(
          `❌ Failed to get session info for session ${this.sessionId}`,
          error
        );
        throw new Error(
          `Failed to get session info for session ${this.sessionId}: ${error}`
        );
      }
    }
  }

  /**
   * Retrieves an access link for the session.
   *
   * @param protocolType - Protocol type for the link (optional, reserved for future use)
   * @param port - Specific port number to access (default open range: [30100, 30199]; other ports require whitelist approval via agentbay_dev@alibabacloud.com).
   *               If not specified, returns the default session link.
   *
   * @returns Promise resolving to OperationResult containing:
   *          - success: Whether the operation succeeded
   *          - data: String URL for accessing the session
   *          - requestId: Unique identifier for this API request
   *          - errorMessage: Error description if operation failed
   *
   * @throws Error if the API call fails or port is out of valid range.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const linkResult = await result.session.getLink();
   *   console.log(`Session link: ${linkResult.data}`);
   *   await result.session.delete();
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - Without port: Returns the default session access URL
   * - With port: Returns URL for accessing specific port-mapped service
   * - Default open port range: [30100, 30199]; other ports require whitelist approval
   * - For ADB connections, use `session.mobile.getAdbUrl()` with appropriate ADB public key
   *
   * **Best Practices:**
   * - Use default link for general session access
   * - Use port-specific links when you've started services on specific ports
   * - Validate port range before calling to avoid errors
   *
   * @see {@link info}
   */
  async getLink(
    protocolType?: string,
    port?: number,
    options?: string
  ): Promise<OperationResult> {
    try {
      // Log API call
      let requestParams = `SessionId=${this.getSessionId()}, ProtocolType=${
        protocolType || "default"
      }, Port=${port || "default"}`;
      if (options) {
        requestParams += ", Options=provided";
      }
      logAPICall("GetLink", requestParams);

      const request = new GetLinkRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.getSessionId(),
        protocolType,
        port,
        option: options,
      });

      const response = await this.agentBay.getClient().getLink(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";

      const responseBody = response.body;

      if (typeof responseBody !== "object") {
        throw new Error(
          "Invalid response format: expected a dictionary from response body"
        );
      }

      let data = responseBody.data || {}; // Capital D to match Python
      logDebug(`Data: ${JSON.stringify(data)}`);

      if (typeof data !== "object") {
        try {
          data = typeof data === "string" ? JSON.parse(data) : {};
        } catch (jsonError) {
          data = {};
        }
      }

      const url = (data as any).Url || (data as any).url;

      // Log API response
      const keyFields: Record<string, any> = {};
      if (url) {
        keyFields.url = url;
      }
      logAPIResponseWithDetails("GetLink", requestId, true, keyFields);

      return {
        requestId,
        success: true,
        data: url,
      };
    } catch (error) {
      if (
        error instanceof Error &&
        error.message.includes("Invalid response format")
      ) {
        throw error;
      }
      throw new Error(`Failed to get link: ${error}`);
    }
  }

  /**
   * Asynchronously get a link associated with the current session.
   *
   * @param protocolType - Optional protocol type to use for the link
   * @param port - Optional port to use for the link (default open range: [30100, 30199]; other ports require whitelist approval)
   * @returns OperationResult containing the link as data and request ID
   * @throws Error if the operation fails (matching Python SessionError)
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const linkResult = await result.session.getLinkAsync(undefined, 30150);
   *   console.log(`Port link: ${linkResult.data}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async getLinkAsync(
    protocolType?: string,
    port?: number,
    options?: string
  ): Promise<OperationResult> {
    try {
      // Log API call
      let requestParams = `SessionId=${this.getSessionId()}, ProtocolType=${
        protocolType || "default"
      }, Port=${port || "default"}`;
      if (options) {
        requestParams += ", Options=provided";
      }
      logAPICall("GetLink", requestParams);

      const request = new GetLinkRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.getSessionId(),
        protocolType,
        port,
        option: options,
      });

      // Note: In TypeScript, async is the default, but keeping this method for API compatibility
      const response = await this.agentBay.getClient().getLink(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";

      const responseBody = response?.body;

      if (typeof responseBody !== "object") {
        throw new Error(
          "Invalid response format: expected a dictionary from response body"
        );
      }

      let data = responseBody?.data || {}; // Capital D to match Python
      logDebug(`Data: ${JSON.stringify(data)}`);

      if (typeof data !== "object") {
        try {
          data = typeof data === "string" ? JSON.parse(data) : {};
        } catch (jsonError) {
          data = {};
        }
      }

      const url = (data as any).Url || (data as any).url;

      // Log API response
      const keyFields: Record<string, any> = {};
      if (url) {
        keyFields.url = url;
      }
      logAPIResponseWithDetails("GetLink", requestId, true, keyFields);

      return {
        requestId,
        success: true,
        data: url,
      };
    } catch (error) {
      if (
        error instanceof Error &&
        error.message.includes("Invalid response format")
      ) {
        throw error;
      }
      throw new Error(`Failed to get link asynchronously: ${error}`);
    }
  }

  /**
   * List MCP tools available for this session.
   *
   * @param imageId Optional image ID, defaults to session's imageId or "linux_latest"
   * @returns McpToolsResult containing tools list and request ID
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const toolsResult = await result.session.listMcpTools();
   *   console.log(`Found ${toolsResult.tools.length} MCP tools`);
   *   await result.session.delete();
   * }
   * ```
   */
  async listMcpTools(imageId?: string): Promise<McpToolsResult> {
    // Use provided imageId, session's imageId, or default
    if (!imageId) {
      imageId = (this as any).imageId || "linux_latest";
    }

    const request = new ListMcpToolsRequest({
      authorization: `Bearer ${this.getAPIKey()}`,
      imageId: imageId,
    });

    logAPICall("ListMcpTools");
    logDebug(`Request: ImageId=${imageId}`);

    const response = await this.getClient().listMcpTools(request);

    // Extract request ID
    const requestId = extractRequestId(response) || "";

    // Check for API-level errors
    if (response?.body?.success === false && response.body?.code) {
      const errorMessage = `[${response.body.code}] ${
        response.body.message || "Unknown error"
      }`;
      const fullResponse = response.body
        ? JSON.stringify(response.body, null, 2)
        : "";
      logAPIResponseWithDetails(
        "ListMcpTools",
        requestId,
        false,
        undefined,
        fullResponse
      );
      return {
        requestId,
        success: false,
        tools: [],
        errorMessage,
      };
    }

    // Parse the response data
    const tools: McpTool[] = [];
    if (response && response.body && response.body.data) {
      try {
        const toolsData = JSON.parse(response.body.data as string);
        for (const toolData of toolsData) {
          const tool: McpTool = {
            name: toolData.name || "",
            description: toolData.description || "",
            inputSchema: toolData.inputSchema || {},
            server: toolData.server || "",
            tool: toolData.tool || "",
          };
          tools.push(tool);
        }
      } catch (error) {
        logError(`Error unmarshaling tools data: ${error}`);
      }
    }

    // Do not store MCP tools in Session.

    // Log API response with key fields
    const keyFields: Record<string, any> = {
      image_id: imageId,
      tool_count: tools.length,
    };
    const fullResponse = response.body
      ? JSON.stringify(response.body, null, 2)
      : "";
    logAPIResponseWithDetails(
      "ListMcpTools",
      requestId,
      true,
      keyFields,
      fullResponse
    );

    return {
      requestId,
      success: true,
      tools,
    };
  }

  getMcpServerForTool(toolName: string): string | null {
    for (const tool of this.mcpTools || []) {
      if (tool && tool.name === toolName) {
        return tool.server || null;
      }
    }
    return null;
  }

  /**
   * Call an MCP tool and return the result in a format compatible with Agent.
   *
   * @param toolName - Name of the MCP tool to call
   * @param args - Arguments to pass to the tool
   * @param autoGenSession - Whether to automatically generate session if not exists (default: false)
   * @returns McpToolResult containing the response data
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const shellResult = await result.session.callMcpTool('shell', { command: "echo 'Hello'" });
   *   console.log(`Output: ${shellResult.data}`);
   *   await result.session.delete();
   * }
   * ```
   *
   * @remarks
   * For press_keys tool, key names are automatically normalized to correct case format.
   * This improves case compatibility (e.g., "CTRL" -> "Ctrl", "tab" -> "Tab").
   */
  async callMcpTool(
    toolName: string,
    args: any,
    autoGenSession = false
  ): Promise<import("./agent/agent").McpToolResult> {
    try {
      // Normalize press_keys arguments for better case compatibility
      if (toolName === "press_keys" && args && Array.isArray(args.keys)) {
        const { normalizeKeys } = await import("./key-normalizer");
        args = { ...args }; // Don't modify the original args
        args.keys = normalizeKeys(args.keys);
        logDebug(`Normalized press_keys arguments: ${JSON.stringify(args)}`);
      }

      // Server name is optional for API-based tool calls.
      // Some environments do not return ToolList in CreateSession, and the backend
      // can resolve the server by tool name.
      const serverName = this.getMcpServerForTool(toolName) || "";

      const argsJSON = JSON.stringify(args);

      // LinkUrl route requires explicit server name. If it's not available,
      // fall back to API-based call to let backend resolve the server.
      if (this.getLinkUrl() && this.getToken() && serverName) {
        return await this.callMcpToolLinkUrl(toolName, args, serverName);
      }

      // Use traditional API call
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.getSessionId(),
        name: toolName,
        args: argsJSON,
        autoGenSession: autoGenSession,
        server: serverName,
      });

      const response = await this.getClient().callMcpTool(callToolRequest);

      if (!response.body?.data) {
        return {
          success: false,
          data: "",
          errorMessage: "Invalid response data format",
          requestId: extractRequestId(response) || "",
        };
      }

      // Check for API-level errors before parsing Data
      if (response.body.success === false && response.body.code) {
        const errorMessage = `[${response.body.code}] ${
          response.body.message || "Unknown error"
        }`;
        return {
          success: false,
          data: "",
          errorMessage,
          requestId: extractRequestId(response) || "",
        };
      }

      const data = response.body.data as Record<string, any>;
      const reqId = extractRequestId(response) || "";
      if (reqId) {
        setRequestId(reqId);
      }

      // For run_code tool, return raw data to let Code service handle parsing
      if (toolName === "run_code") {
        let dataStr = "";

        // Check if data has content array (standard MCP tool response)
        // The backend might wrap the actual result JSON inside content[0].text
        if (
          data &&
          Array.isArray(data.content) &&
          data.content.length > 0 &&
          data.content[0].text
        ) {
          dataStr = data.content[0].text;
        } else {
          // Fallback: use the whole data object/string
          dataStr =
            typeof response.body.data === "string"
              ? response.body.data
              : JSON.stringify(response.body.data);
        }

        logCodeExecutionOutput(reqId, dataStr);

        // If the backend marked it as an error, we should reflect that
        const isError = data.isError === true;

        return {
          success: !isError,
          data: dataStr,
          errorMessage: isError ? dataStr : "",
          requestId: reqId,
        };
      }

      // Check if there's an error in the response
      if (data.isError) {
        const errorContent = data.content || [];
        const errorMessage = errorContent
          .map((item: any) => item.text || "Unknown error")
          .join("; ");

        return {
          success: false,
          data: "",
          errorMessage,
          requestId: reqId,
        };
      }

      // Extract text content from content array
      const content = data.content || [];
      let textContent = "";
      if (content.length > 0) {
        const c0 = content[0] || {};
        if (typeof c0.text === "string" && c0.text) {
          textContent = c0.text;
        } else if (typeof c0.blob === "string" && c0.blob) {
          textContent = c0.blob;
        } else if (typeof c0.data === "string" && c0.data) {
          textContent = c0.data;
        }
      }

      return {
        success: true,
        data: textContent || JSON.stringify(data),
        errorMessage: "",
        requestId: reqId,
      };
    } catch (error) {
      return {
        success: false,
        data: "",
        errorMessage: error instanceof Error ? error.message : String(error),
        requestId: "",
      };
    }
  }

  private async callMcpToolLinkUrl(
    toolName: string,
    args: any,
    serverName: string
  ): Promise<import("./agent/agent").McpToolResult> {
    if (!serverName) {
      return {
        success: false,
        data: "",
        errorMessage: `Server name is required for LinkUrl tool call: ${toolName}`,
        requestId: "",
      };
    }

    const linkUrl = this.getLinkUrl();
    const token = this.getToken();
    if (!linkUrl || !token) {
      return {
        success: false,
        data: "",
        errorMessage: "LinkUrl/token not available",
        requestId: "",
      };
    }

    const requestId = `link-${Date.now()}-${Math.floor(
      Math.random() * 1_000_000_000
    )
      .toString()
      .padStart(9, "0")}`;

    logAPICall(
      "CallMcpTool(LinkUrl)",
      `Tool=${toolName}, ArgsLength=${
        JSON.stringify(args).length
      }, RequestId=${requestId}`
    );

    const url = `${linkUrl.replace(/\/+$/, "")}/callTool`;
    const payload = {
      args,
      server: serverName,
      requestId,
      tool: toolName,
      token,
    };

    const resp = await fetchCompat(
      url,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Access-Token": token,
        },
        body: JSON.stringify(payload),
      },
      900000
    ); // 900 seconds timeout

    if (!resp.ok) {
      const bodyText = await resp.text().catch(() => "");
      logAPIResponseWithDetails(
        "CallMcpTool(LinkUrl) Response",
        requestId,
        false,
        { http_status: resp.status, tool_name: toolName },
        bodyText
      );
      return {
        success: false,
        data: "",
        errorMessage: `HTTP request failed with code: ${resp.status}`,
        requestId,
      };
    }

    const outer = await resp.json();
    const dataField = outer?.data;
    let parsedData: any = dataField;
    if (typeof dataField === "string") {
      parsedData = JSON.parse(dataField);
    }

    const resultField = parsedData?.result;
    const isError = resultField?.isError === true;
    const content = Array.isArray(resultField?.content)
      ? resultField.content
      : [];
    const first = content[0] ?? {};
    const textContent =
      typeof first === "string"
        ? first
        : (first as any).text ??
          (first as any).blob ??
          (first as any).data ??
          "";

    logAPIResponseWithDetails(
      "CallMcpTool(LinkUrl) Response",
      requestId,
      !isError,
      {
        tool_name: toolName,
        server: serverName,
        is_error: isError,
        data_len: String(textContent ?? "").length,
      },
      isError ? String(textContent ?? "") : ""
    );

    if (toolName === "run_code") {
      const dataStr =
        typeof textContent === "string"
          ? textContent
          : JSON.stringify(textContent);
      logCodeExecutionOutput(requestId, dataStr);
      return {
        success: !isError,
        data: dataStr,
        errorMessage: isError ? dataStr : "",
        requestId,
      };
    }

    return {
      success: !isError,
      data: String(textContent ?? ""),
      errorMessage: isError ? String(textContent ?? "") : "",
      requestId,
    };
  }

  /**
   * Get runtime metrics for this session.
   *
   * The underlying service returns a JSON string. This method parses it and
   * returns a structured result.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: "your_api_key" });
   * const create = await agentBay.create({ imageId: "linux_latest" });
   * if (create.success && create.session) {
   *   const metrics = await create.session.getMetrics();
   *   console.log(metrics.data);
   *   await create.session.delete();
   * }
   * ```
   */
  async getMetrics(): Promise<SessionMetricsResult> {
    const toolResult = await this.callMcpTool("get_metrics", {}, false);
    const requestId = toolResult.requestId || "";

    if (!toolResult.success) {
      return {
        requestId,
        success: false,
        data: undefined,
        raw: undefined,
        errorMessage: toolResult.errorMessage || "",
      };
    }

    try {
      const raw =
        typeof toolResult.data === "string"
          ? JSON.parse(toolResult.data)
          : toolResult.data;

      if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
        throw new Error("get_metrics returned non-object JSON");
      }

      const metrics: SessionMetrics = {
        cpuCount: Number((raw as any).cpu_count ?? 0),
        cpuUsedPct: Number((raw as any).cpu_used_pct ?? 0),
        diskTotal: Number((raw as any).disk_total ?? 0),
        diskUsed: Number((raw as any).disk_used ?? 0),
        memTotal: Number((raw as any).mem_total ?? 0),
        memUsed: Number((raw as any).mem_used ?? 0),
        rxRateKbytePerS: Number(
          (raw as any).rx_rate_kbyte_per_s ??
            (raw as any).rx_rate_kbps ??
            (raw as any).rx_rate_KBps ??
            0
        ),
        txRateKbytePerS: Number(
          (raw as any).tx_rate_kbyte_per_s ??
            (raw as any).tx_rate_kbps ??
            (raw as any).tx_rate_KBps ??
            0
        ),
        rxUsedKbyte: Number(
          (raw as any).rx_used_kbyte ??
            (raw as any).rx_used_kb ??
            (raw as any).rx_used_KB ??
            0
        ),
        txUsedKbyte: Number(
          (raw as any).tx_used_kbyte ??
            (raw as any).tx_used_kb ??
            (raw as any).tx_used_KB ??
            0
        ),
        timestamp: String((raw as any).timestamp ?? ""),
      };

      return {
        requestId,
        success: true,
        data: metrics,
        raw: raw as Record<string, any>,
        errorMessage: "",
      };
    } catch (err: any) {
      return {
        requestId,
        success: false,
        data: undefined,
        raw: undefined,
        errorMessage: `Failed to parse get_metrics response: ${
          err?.message || String(err)
        }`,
      };
    }
  }

  /**
   * Asynchronously pause this session (beta), putting it into a dormant state.
   *
   * **Note**: This feature is currently in whitelist-only access.
   * Contact agentbay_dev@alibabacloud.com to request access.
   *
   * This method calls the PauseSessionAsync API to initiate the pause operation and then polls
   * the GetSession API to check the session status until it becomes PAUSED or until timeout is reached.
   * During the paused state, resource usage and costs are reduced while session state is preserved.
   *
   * @param timeout - Timeout in seconds to wait for the session to pause. Defaults to 600 seconds.
   * @param pollInterval - Interval in seconds between status polls. Defaults to 2.0 seconds.
   *
   * @returns Promise resolving to SessionPauseResult containing:
   *          - success: Whether the pause operation succeeded
   *          - requestId: Unique identifier for this API request
   *          - status: Final session status (should be "PAUSED" if successful)
   *          - errorMessage: Error description if pause failed
   *
   * @throws Error if the API call fails or network issues occur.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const pauseResult = await result.session.betaPauseAsync();
   *   if (pauseResult.success) {
   *     console.log('Session paused successfully');
   *   }
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - Initiates pause operation through PauseSessionAsync API
   * - Polls session status until PAUSED state or timeout
   * - Session state transitions: RUNNING -> PAUSING -> PAUSED
   * - All session state is preserved during pause
   *
   * **Important Notes:**
   * - Paused sessions cannot perform operations (deletion, task execution, etc.)
   * - Use {@link betaResumeAsync} to restore the session to RUNNING state
   * - During pause, both resource usage and costs are lower
   * - If timeout is exceeded, returns with success=false
   *
   * @see {@link betaResumeAsync}
   */
  async betaPauseAsync(
    timeout = 600,
    pollInterval = 2.0
  ): Promise<SessionPauseResult> {
    try {
      const request = new $_client.PauseSessionAsyncRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId,
      });

      logAPICall("PauseSessionAsync", `SessionId=${this.sessionId}`);

      const response = await this.getClient().pauseSessionAsync(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";
      setRequestId(requestId);

      // Check for API-level errors
      const responseMap = response.to_map ? response.to_map() : response;
      if (!responseMap) {
        return {
          requestId: requestId || "",
          success: false,
          errorMessage: "Invalid response format",
        };
      }

      const body = responseMap.body;
      if (!body) {
        return {
          requestId: requestId || "",
          success: false,
          errorMessage: "Invalid response body",
        };
      }

      // Extract fields from response body
      const success = body.success !== false;
      const code = body.code || "";
      const message = body.message || "";
      const httpStatusCode = body.httpStatusCode || 0;

      // Build error message if not successful
      if (!success) {
        const errorMessage = `[${code}] ${message}` || "Unknown error";
        logError("PauseSessionAsync", errorMessage);
        return {
          requestId: requestId || "",
          success: false,
          errorMessage,
          code,
          message,
          httpStatusCode,
        };
      }

      logInfo(
        `PauseSessionAsync`,
        `Session ${this.sessionId} pause initiated successfully`
      );

      // Poll for session status until PAUSED or timeout
      const startTime = Date.now();
      const maxAttempts = Math.floor(timeout / pollInterval);
      let attempt = 0;

      while (attempt < maxAttempts) {
        // Get session status
        const getResult = await this.agentBay._getSession(this.sessionId);
        if (!getResult.success) {
          logError(`Failed to get session status: ${getResult.errorMessage}`);
          return {
            requestId: getResult.requestId || "",
            success: false,
            errorMessage: `Failed to get session status: ${getResult.errorMessage}`,
          };
        }

        // Check session status
        if (getResult.data) {
          const status = getResult.data.status || "UNKNOWN";
          logDebug(
            `Session status: ${status} (attempt ${attempt + 1}/${maxAttempts})`
          );

          // Check if session is paused
          if (status === "PAUSED") {
            const elapsed = Date.now() - startTime;
            logInfo(`Session paused successfully in ${elapsed}ms`);
            return {
              requestId: getResult.requestId || "",
              success: true,
              status,
            };
          } else if (status === "PAUSING") {
            // Normal transitioning state, continue polling
          } else {
            // Any other status is unexpected - pause API succeeded but session is not pausing/paused
            const elapsed = Date.now() - startTime;
            const errorMessage = `Session pause failed: unexpected state '${status}' after ${elapsed}ms`;
            logError(errorMessage);
            return {
              requestId: getResult.requestId || "",
              success: false,
              errorMessage,
              status,
            };
          }
        }

        // Wait before next query (using setTimeout to avoid blocking)
        // Only wait if we're not at the last attempt
        attempt++;
        if (attempt < maxAttempts) {
          await new Promise((resolve) =>
            setTimeout(resolve, pollInterval * 1000)
          );
        }
      }

      // Timeout
      const elapsed = Date.now() - startTime;
      const errorMsg = `Session pause timed out after ${elapsed}ms`;
      logError(errorMsg);
      return {
        requestId: "",
        success: false,
        errorMessage: errorMsg,
      };
    } catch (error) {
      logError("PauseSessionAsync", error);
      return {
        requestId: "",
        success: false,
        errorMessage: `Unexpected error pausing session: ${error}`,
      };
    }
  }

  /**
   * Asynchronously resume this session (beta) from a paused state.
   *
   * This method calls the ResumeSessionAsync API to initiate the resume operation and then polls
   * the GetSession API to check the session status until it becomes RUNNING or until timeout is reached.
   * After resuming, the session restores full functionality and can perform all operations normally.
   *
   * @param timeout - Timeout in seconds to wait for the session to resume. Defaults to 600 seconds.
   * @param pollInterval - Interval in seconds between status polls. Defaults to 2.0 seconds.
   *
   * @returns Promise resolving to SessionResumeResult containing:
   *          - success: Whether the resume operation succeeded
   *          - requestId: Unique identifier for this API request
   *          - status: Final session status (should be "RUNNING" if successful)
   *          - errorMessage: Error description if resume failed
   *
   * @throws Error if the API call fails or network issues occur.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.get('paused_session_id');
   * if (result.success) {
   *   const resumeResult = await result.session.betaResumeAsync();
   *   if (resumeResult.success) {
   *     console.log('Session resumed successfully');
   *   }
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - Initiates resume operation through ResumeSessionAsync API
   * - Polls session status until RUNNING state or timeout
   * - Session state transitions: PAUSED -> RESUMING -> RUNNING
   * - All previous session state is restored during resume
   *
   * **Important Notes:**
   * - Only sessions in PAUSED state can be resumed
   * - After resume, the session can perform all operations normally
   * - Use {@link betaPauseAsync} to put a session into PAUSED state
   * - If timeout is exceeded, returns with success=false
   *
   * @see {@link betaPauseAsync}
   */
  async betaResumeAsync(
    timeout = 600,
    pollInterval = 2.0
  ): Promise<SessionResumeResult> {
    try {
      const request = new $_client.ResumeSessionAsyncRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId,
      });

      logAPICall("ResumeSessionAsync", `SessionId=${this.sessionId}`);

      const response = await this.getClient().resumeSessionAsync(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";
      setRequestId(requestId);

      // Check for API-level errors
      const responseMap = response.to_map ? response.to_map() : response;
      if (!responseMap) {
        return {
          requestId: requestId || "",
          success: false,
          errorMessage: "Invalid response format",
        };
      }

      const body = responseMap.body;
      if (!body) {
        return {
          requestId: requestId || "",
          success: false,
          errorMessage: "Invalid response body",
        };
      }

      // Extract fields from response body
      const success = body.success !== false;
      const code = body.code || "";
      const message = body.message || "";
      const httpStatusCode = body.httpStatusCode || 0;

      // Build error message if not successful
      if (!success) {
        const errorMessage = `[${code}] ${message}` || "Unknown error";
        logError("ResumeSessionAsync", errorMessage);
        return {
          requestId: requestId || "",
          success: false,
          errorMessage,
          code,
          message,
          httpStatusCode,
        };
      }

      logInfo(
        `ResumeSessionAsync`,
        `Session ${this.sessionId} resume initiated successfully`
      );

      // Poll for session status until RUNNING or timeout
      const startTime = Date.now();
      const maxAttempts = Math.floor(timeout / pollInterval);
      let attempt = 0;

      while (attempt < maxAttempts) {
        // Get session status
        const getResult = await this.agentBay._getSession(this.sessionId);
        if (!getResult.success) {
          logError(`Failed to get session status: ${getResult.errorMessage}`);
          return {
            requestId: getResult.requestId || "",
            success: false,
            errorMessage: `Failed to get session status: ${getResult.errorMessage}`,
          };
        }

        // Check session status
        if (getResult.data) {
          const status = getResult.data.status || "UNKNOWN";
          logDebug(
            `Session status: ${status} (attempt ${attempt + 1}/${maxAttempts})`
          );

          // Check if session is running
          if (status === "RUNNING") {
            const elapsed = Date.now() - startTime;
            logInfo(`Session resumed successfully in ${elapsed}ms`);
            return {
              requestId: getResult.requestId || "",
              success: true,
              status,
            };
          } else if (status === "RESUMING") {
            // Normal transitioning state, continue polling
          } else {
            // Any other status is unexpected - resume API succeeded but session is not resuming/running
            const elapsed = Date.now() - startTime;
            const errorMessage = `Session resume failed: unexpected state '${status}' after ${elapsed}ms`;
            logError(errorMessage);
            return {
              requestId: getResult.requestId || "",
              success: false,
              errorMessage,
              status,
            };
          }
        }

        // Wait before next query (using setTimeout to avoid blocking)
        // Only wait if we're not at the last attempt
        attempt++;
        if (attempt < maxAttempts) {
          await new Promise((resolve) =>
            setTimeout(resolve, pollInterval * 1000)
          );
        }
      }

      // Timeout
      const elapsed = Date.now() - startTime;
      const errorMsg = `Session resume timed out after ${elapsed}ms`;
      logError(errorMsg);
      return {
        requestId: "",
        success: false,
        errorMessage: errorMsg,
      };
    } catch (error) {
      logError("ResumeSessionAsync", error);
      return {
        requestId: "",
        success: false,
        errorMessage: `Unexpected error resuming session: ${error}`,
      };
    }
  }
}
