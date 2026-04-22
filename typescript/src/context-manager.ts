import { Client } from "./api/client";
import {
  GetContextInfoRequest,
  SyncContextRequest,
  BindContextsRequest,
  BindContextsRequestPersistenceDataList,
  DescribeSessionContextsRequest,
} from "./api/models/model";
import {
  ApiResponse,
  ContextBinding,
  ContextBindResult,
  ContextBindingsResult,
  extractRequestId,
} from "./types/api-response";
import { ContextSync } from "./context-sync";
import {
  log,
  logError,
  logInfo,
  logDebug,
  logAPICall,
  logAPIResponseWithDetails,
  setRequestId,
  getRequestId,
} from "./utils/logger";

export interface ContextStatusData {
  contextId: string;
  path: string;
  errorMessage: string;
  status: string;
  startTime: number;
  finishTime: number;
  taskType: string;
}

export interface ContextStatusItem {
  type: string;
  data: string;
}

export interface ContextInfoResult extends ApiResponse {
  success?: boolean;
  contextStatusData: ContextStatusData[];
  errorMessage?: string;
}

export interface ContextSyncResult extends ApiResponse {
  success: boolean;
  errorMessage?: string;
}

export type SyncCallback = (success: boolean) => void;

export interface SessionInterface {
  getAPIKey(): string;
  getClient(): Client;
  getSessionId(): string;
}

export class ContextManager {
  private session: SessionInterface;

  constructor(session: SessionInterface) {
    this.session = session;
  }

  /**
   * Gets information about context synchronization status for the current session.
   *
   * @returns Promise resolving to ContextInfoResult containing context status data and request ID
   * @throws Error if the API call fails
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const info = await result.session.context.info();
   *   console.log(`Context count: ${info.contextStatusData.length}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async info(): Promise<ContextInfoResult> {
    return this.infoWithParams();
  }

  /**
   * Gets information about context synchronization status with optional filter parameters.
   *
   * @param contextId - Optional context ID to filter results
   * @param path - Optional path to filter results
   * @param taskType - Optional task type to filter results (e.g., "upload", "download")
   * @returns Promise resolving to ContextInfoResult containing filtered context status data and request ID
   * @throws Error if the API call fails
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const info = await result.session.context.infoWithParams('SdkCtx-xxx', '/mnt/persistent');
   *   console.log(`Context status: ${info.contextStatusData[0]?.status}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async infoWithParams(
    contextId?: string,
    path?: string,
    taskType?: string
  ): Promise<ContextInfoResult> {
    const request = new GetContextInfoRequest({
      authorization: `Bearer ${this.session.getAPIKey()}`,
      sessionId: this.session.getSessionId(),
    });

    // Set optional parameters if provided
    if (contextId) {
      request.contextId = contextId;
    }
    if (path) {
      request.path = path;
    }
    if (taskType) {
      request.taskType = taskType;
    }

    // Log API request (matching Go version format)
    logAPICall("GetContextInfo");
    let requestLog = `Request: SessionId=${request.sessionId}`;
    if (request.contextId) {
      requestLog += `, ContextId=${request.contextId}`;
    }
    if (request.path) {
      requestLog += `, Path=${request.path}`;
    }
    if (request.taskType) {
      requestLog += `, TaskType=${request.taskType}`;
    }
    logDebug(requestLog);

    try {
      const response = await this.session.getClient().getContextInfo(request);

      // Extract RequestID
      const requestId = extractRequestId(response) || "";

      // Check for API-level errors
      if (response?.body?.success === false && response.body.code) {
        const errorMsg = `[${response.body.code}] ${
          response.body.message || "Unknown error"
        }`;
        const fullResponse = response.body
          ? JSON.stringify(response.body, null, 2)
          : "";
        logAPIResponseWithDetails(
          "GetContextInfo",
          requestId,
          false,
          undefined,
          fullResponse
        );
        return {
          requestId,
          success: false,
          contextStatusData: [],
          errorMessage: errorMsg,
        };
      }

      // Parse the context status data
      const contextStatusData: ContextStatusData[] = [];
      if (response?.body?.data?.contextStatus) {
        try {
          // First, parse the outer array
          const contextStatusStr = response.body.data.contextStatus;
          const statusItems: ContextStatusItem[] = JSON.parse(contextStatusStr);

          // Process each item in the array
          for (const item of statusItems) {
            if (item.type === "data") {
              // Parse the inner data string
              const dataItems: ContextStatusData[] = JSON.parse(item.data);
              contextStatusData.push(...dataItems);
            }
          }
        } catch (error) {
          logError("Error parsing context status:", error);
        }
      }

      // Log API response with key fields
      const keyFields: Record<string, any> = {
        session_id: request.sessionId,
        context_count: contextStatusData.length,
      };
      if (request.contextId) {
        keyFields.context_id = request.contextId;
      }
      if (request.path) {
        keyFields.path = request.path;
      }
      if (request.taskType) {
        keyFields.task_type = request.taskType;
      }
      const fullResponse = response.body
        ? JSON.stringify(response.body, null, 2)
        : "";
      logAPIResponseWithDetails(
        "GetContextInfo",
        requestId,
        true,
        keyFields,
        fullResponse
      );

      return {
        requestId,
        success: true,
        contextStatusData,
        errorMessage: undefined,
      };
    } catch (error) {
      logError("Error calling GetContextInfo:", error);
      throw new Error(`Failed to get context info: ${error}`);
    }
  }

  /**
   * Synchronizes a context with the session. Supports both async and callback modes.
   *
   * @param contextId - Optional context ID to synchronize. If provided, `path` must also be provided.
   * @param path - Optional path where the context should be mounted. If provided, `contextId` must also be provided.
   * @param mode - Optional synchronization mode (e.g., "upload", "download")
   * @param callback - Optional callback function. If provided, runs in background and calls callback when complete
   * @param maxRetries - Maximum number of retries for polling completion status (default: 150)
   * @param retryInterval - Initial interval in milliseconds for exponential backoff polling (default: 500). Interval grows by factor 1.1 up to 5000ms.
   * @returns Promise resolving to ContextSyncResult with success status and request ID
   * @throws Error if the API call fails
   * @throws Error if `contextId` or `path` is provided without the other parameter.
   *               Both must be provided together, or both must be omitted.
   *
   * @example
   * Sync all contexts (no parameters):
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const syncResult = await result.session.context.sync();
   *   console.log(`Sync: ${syncResult.success}`);
   *   await result.session.delete();
   * }
   * ```
   *
   * @example
   * Sync specific context with path:
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const ctxResult = await agentBay.context.get('my-context', true);
   *   const syncResult = await result.session.context.sync(ctxResult.context!.id, '/mnt/persistent', 'upload');
   *   console.log(`Sync: ${syncResult.success}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async sync(
    contextId?: string,
    path?: string,
    mode?: string,
    callback?: SyncCallback,
    maxRetries = 150,
    retryInterval = 500
  ): Promise<ContextSyncResult> {
    // Validate that contextId and path are provided together or both omitted
    const hasContextId = contextId !== undefined && contextId.trim() !== "";
    const hasPath = path !== undefined && path.trim() !== "";

    if (hasContextId !== hasPath) {
      throw new Error(
        "contextId and path must be provided together or both omitted. " +
          "If you want to sync a specific context, both contextId and path are required. " +
          "If you want to sync all contexts, omit both parameters."
      );
    }

    const request = new SyncContextRequest({
      authorization: `Bearer ${this.session.getAPIKey()}`,
      sessionId: this.session.getSessionId(),
    });

    // Set optional parameters if provided
    if (contextId) {
      request.contextId = contextId;
    }
    if (path) {
      request.path = path;
    }
    if (mode) {
      request.mode = mode;
    }

    // Log API request (matching Go version format)
    logAPICall("SyncContext");
    let requestLog = `Request: SessionId=${request.sessionId}`;
    if (request.contextId) {
      requestLog += `, ContextId=${request.contextId}`;
    }
    if (request.path) {
      requestLog += `, Path=${request.path}`;
    }
    if (request.mode) {
      requestLog += `, Mode=${request.mode}`;
    }
    logDebug(requestLog);

    try {
      const response = await this.session.getClient().syncContext(request);

      // Extract RequestID
      const requestId = extractRequestId(response) || "";

      // Check for API-level errors
      if (response?.body?.success === false && response.body.code) {
        const errorMsg = `[${response.body.code}] ${
          response.body.message || "Unknown error"
        }`;
        const fullResponse = response.body
          ? JSON.stringify(response.body, null, 2)
          : "";
        logAPIResponseWithDetails(
          "SyncContext",
          requestId,
          false,
          undefined,
          fullResponse
        );
        return {
          requestId,
          success: false,
          errorMessage: errorMsg,
        };
      }

      let success = false;
      if (response?.body?.success !== undefined) {
        success = response.body.success;
      }

      // Log API response with key fields
      const keyFields: Record<string, any> = {
        session_id: request.sessionId,
        success: success,
      };
      if (request.contextId) {
        keyFields.context_id = request.contextId;
      }
      if (request.path) {
        keyFields.path = request.path;
      }
      if (request.mode) {
        keyFields.mode = request.mode;
      }
      const fullResponse = response.body
        ? JSON.stringify(response.body, null, 2)
        : "";
      logAPIResponseWithDetails(
        "SyncContext",
        requestId,
        success,
        keyFields,
        fullResponse
      );

      // If callback is provided, start polling in background (async mode)
      if (callback && success) {
        // Start polling in background without blocking
        this.pollForCompletion(
          callback,
          contextId,
          path,
          maxRetries,
          retryInterval
        ).catch((error) => {
          logError("Error in background polling:", error);
          callback(false);
        });
        return {
          requestId,
          success,
        };
      }

      // If no callback, wait for completion (sync mode)
      if (success) {
        const finalSuccess = await this.pollForCompletionAsync(
          contextId,
          path,
          maxRetries,
          retryInterval
        );
        return {
          requestId,
          success: finalSuccess,
        };
      }

      return {
        requestId,
        success,
      };
    } catch (error) {
      logError("Error calling SyncContext:", error);
      throw new Error(`Failed to sync context: ${error}`);
    }
  }

  /**
   * Polls the info interface to check if sync is completed and calls callback.
   */
  private async pollForCompletion(
    callback: SyncCallback,
    contextId?: string,
    path?: string,
    maxRetries = 150,
    retryInterval = 500
  ): Promise<void> {
    const maxInterval = 5000;
    const backoffFactor = 1.1;
    let currentInterval = retryInterval;

    for (let retry = 0; retry < maxRetries; retry++) {
      try {
        const infoResult = await this.infoWithParams(contextId, path);

        let allCompleted = true;
        let hasFailure = false;
        let hasSyncTasks = false;

        for (const item of infoResult.contextStatusData) {
          if (item.taskType !== "upload" && item.taskType !== "download") {
            continue;
          }

          hasSyncTasks = true;
          logDebug(
            `Sync task ${item.contextId} status: ${item.status}, path: ${item.path}`
          );

          if (item.status !== "Success" && item.status !== "Failed") {
            allCompleted = false;
            break;
          }

          if (item.status === "Failed") {
            hasFailure = true;
            logError(
              `Sync failed for context ${item.contextId}: ${item.errorMessage}`
            );
          }
        }

        if (allCompleted || !hasSyncTasks) {
          if (hasFailure) {
            logInfo("Context sync completed with failures");
            callback(false);
          } else if (hasSyncTasks) {
            logInfo("Context sync completed successfully");
            callback(true);
          } else {
            logDebug("No sync tasks found");
            callback(true);
          }
          return;
        }

        logDebug(
          `Waiting for context sync to complete, attempt ${
            retry + 1
          }/${maxRetries}, next interval: ${currentInterval}ms`
        );
        await this.sleep(currentInterval);
        currentInterval = Math.min(
          currentInterval * backoffFactor,
          maxInterval
        );
      } catch (error) {
        logError(
          `Error checking context status on attempt ${retry + 1}:`,
          error
        );
        await this.sleep(currentInterval);
        currentInterval = Math.min(
          currentInterval * backoffFactor,
          maxInterval
        );
      }
    }

    logError(`Context sync polling timed out after ${maxRetries} attempts`);
    callback(false);
  }

  /**
   * Async version of polling for sync completion.
   */
  private async pollForCompletionAsync(
    contextId?: string,
    path?: string,
    maxRetries = 150,
    retryInterval = 500
  ): Promise<boolean> {
    const maxInterval = 5000;
    const backoffFactor = 1.1;
    let currentInterval = retryInterval;

    for (let retry = 0; retry < maxRetries; retry++) {
      try {
        const infoResult = await this.infoWithParams(contextId, path);

        let allCompleted = true;
        let hasFailure = false;
        let hasSyncTasks = false;

        for (const item of infoResult.contextStatusData) {
          if (item.taskType !== "upload" && item.taskType !== "download") {
            continue;
          }

          hasSyncTasks = true;
          logDebug(
            `Sync task ${item.contextId} status: ${item.status}, path: ${item.path}`
          );

          if (item.status !== "Success" && item.status !== "Failed") {
            allCompleted = false;
            break;
          }

          if (item.status === "Failed") {
            hasFailure = true;
            logError(
              `Sync failed for context ${item.contextId}: ${item.errorMessage}`
            );
          }
        }

        if (allCompleted || !hasSyncTasks) {
          if (hasFailure) {
            logInfo("Context sync completed with failures");
            return false;
          } else if (hasSyncTasks) {
            logInfo("Context sync completed successfully");
            return true;
          } else {
            logDebug("No sync tasks found");
            return true;
          }
        }

        logDebug(
          `Waiting for context sync to complete, attempt ${
            retry + 1
          }/${maxRetries}, next interval: ${currentInterval}ms`
        );
        await this.sleep(currentInterval);
        currentInterval = Math.min(
          currentInterval * backoffFactor,
          maxInterval
        );
      } catch (error) {
        logError(
          `Error checking context status on attempt ${retry + 1}:`,
          error
        );
        await this.sleep(currentInterval);
        currentInterval = Math.min(
          currentInterval * backoffFactor,
          maxInterval
        );
      }
    }

    logError(`Context sync polling timed out after ${maxRetries} attempts`);
    return false;
  }

  /**
   * Dynamically binds one or more contexts to the current session.
   *
   * @param contexts - One or more ContextSync objects specifying contexts to bind
   * @param waitForCompletion - Whether to poll until all bindings are confirmed (default: true)
   * @returns Promise resolving to ContextBindResult
   *
   * @example
   * ```typescript
   * const contextSync = new ContextSync(context.id, '/tmp/ctx-data');
   * const result = await session.context.bind(contextSync);
   * console.log(`Bind success: ${result.success}`);
   * ```
   */
  async bind(
    contexts: ContextSync | ContextSync[],
    waitForCompletion = true
  ): Promise<ContextBindResult> {
    const ctxArray = Array.isArray(contexts) ? contexts : [contexts];

    if (ctxArray.length === 0) {
      return {
        requestId: "",
        success: false,
        errorMessage: "At least one context is required",
      };
    }

    const persistenceDataList = ctxArray.map((ctx) => {
      const item = new BindContextsRequestPersistenceDataList({
        contextId: ctx.contextId,
        path: ctx.path,
      });
      if (ctx.policy) {
        item.policy = JSON.stringify(ctx.policy);
      }
      return item;
    });

    const request = new BindContextsRequest({
      authorization: `Bearer ${this.session.getAPIKey()}`,
      sessionId: this.session.getSessionId(),
      persistenceDataList,
    });

    logAPICall("BindContexts");
    logDebug(
      `Request: SessionId=${request.sessionId}, Contexts=${ctxArray
        .map((c) => c.contextId)
        .join(",")}`
    );

    try {
      const response = await this.session.getClient().bindContexts(request);
      const requestId = extractRequestId(response) || "";

      if (response?.body?.success === false) {
        const errorMsg = `[${response.body.code || "Unknown"}] ${
          response.body.message || "Unknown error"
        }`;
        const fullResponse = response.body
          ? JSON.stringify(response.body, null, 2)
          : "";
        logAPIResponseWithDetails(
          "BindContexts",
          requestId,
          false,
          undefined,
          fullResponse
        );
        return { requestId, success: false, errorMessage: errorMsg };
      }

      const fullResponse = response.body
        ? JSON.stringify(response.body, null, 2)
        : "";
      logAPIResponseWithDetails(
        "BindContexts",
        requestId,
        true,
        {
          context_count: ctxArray.length,
        },
        fullResponse
      );

      if (waitForCompletion) {
        await this.pollForBindCompletion(ctxArray.map((c) => c.contextId));
      }

      return { requestId, success: true };
    } catch (error) {
      logError("Error calling BindContexts:", error);
      throw new Error(`Failed to bind contexts: ${error}`);
    }
  }

  /**
   * Lists all context bindings for the current session.
   *
   * @returns Promise resolving to ContextBindingsResult with the list of bindings
   *
   * @example
   * ```typescript
   * const result = await session.context.listBindings();
   * for (const binding of result.bindings) {
   *   console.log(`Context ${binding.contextId} bound at ${binding.path}`);
   * }
   * ```
   */
  async listBindings(): Promise<ContextBindingsResult> {
    const request = new DescribeSessionContextsRequest({
      authorization: `Bearer ${this.session.getAPIKey()}`,
      sessionId: this.session.getSessionId(),
    });

    logAPICall("DescribeSessionContexts");
    logDebug(`Request: SessionId=${request.sessionId}`);

    try {
      const response = await this.session
        .getClient()
        .describeSessionContexts(request);
      const requestId = extractRequestId(response) || "";

      if (response?.body?.success === false) {
        const errorMsg = `[${response.body.code || "Unknown"}] ${
          response.body.message || "Unknown error"
        }`;
        const fullResponse = response.body
          ? JSON.stringify(response.body, null, 2)
          : "";
        logAPIResponseWithDetails(
          "DescribeSessionContexts",
          requestId,
          false,
          undefined,
          fullResponse
        );
        return {
          requestId,
          success: false,
          bindings: [],
          errorMessage: errorMsg,
        };
      }

      const bindings: ContextBinding[] = [];
      if (response?.body?.data) {
        for (const item of response.body.data) {
          bindings.push({
            contextId: item.contextId || "",
            contextName: item.contextName,
            path: item.path || "",
            policy: item.policy,
            bindTime: item.bindTime,
          });
        }
      }

      const fullResponse = response.body
        ? JSON.stringify(response.body, null, 2)
        : "";
      logAPIResponseWithDetails(
        "DescribeSessionContexts",
        requestId,
        true,
        {
          binding_count: bindings.length,
        },
        fullResponse
      );

      return { requestId, success: true, bindings };
    } catch (error) {
      logError("Error calling DescribeSessionContexts:", error);
      throw new Error(`Failed to list bindings: ${error}`);
    }
  }

  private async pollForBindCompletion(
    expectedContextIds: string[],
    maxRetries = 60,
    retryInterval = 2000
  ): Promise<boolean> {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const result = await this.listBindings();
        if (result.success) {
          const boundIds = new Set(result.bindings.map((b) => b.contextId));
          if (expectedContextIds.every((id) => boundIds.has(id))) {
            logInfo("All contexts bound successfully");
            return true;
          }
        }
      } catch {
        logDebug(`Polling attempt ${i + 1} failed, retrying...`);
      }
      await this.sleep(retryInterval);
    }
    logError(`Bind polling timed out after ${maxRetries} attempts`);
    return false;
  }

  /**
   * Sleep utility function for TypeScript
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export function newContextManager(session: SessionInterface): ContextManager {
  return new ContextManager(session);
}
