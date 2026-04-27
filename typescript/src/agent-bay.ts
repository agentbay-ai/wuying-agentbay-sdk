import { $OpenApiUtil } from "@alicloud/openapi-core";
import "dotenv/config";
import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";
import * as $_client from "./api";
import {
  ListSessionRequest,
  CreateMcpSessionRequestPersistenceDataList,
  GetSessionRequest as $GetSessionRequest,
} from "./api/models/model";
import type { McpTool } from "./session";
import { Client } from "./api/client";

import {
  Config,
  BROWSER_RECORD_PATH,
  loadConfig,
  loadDotEnvWithFallback,
} from "./config";
import type { ConfigOptions } from "./config";
import { ContextService } from "./context";
import { BetaNetworkService } from "./beta-network";
import { BetaSkillsService } from "./beta-skills";
import { ContextSync } from "./context-sync";
import { APIError, AuthenticationError } from "./exceptions";
import { Session } from "./session";
import {
  BrowserContext,
  CreateSessionParamsInterface,
  CreateSessionParams as CreateSessionParamsClass,
} from "./session-params";
import { BrowserSyncMode } from "./session-params";
import { Context } from "./context";
import { ExtraConfigs } from "./types/extra-configs";
import {
  DeleteResult,
  extractRequestId,
  GetSessionResult as $GetSessionResult,
  SessionResult,
} from "./types/api-response";
import {
  ListSessionParams,
  SessionListResult,
} from "./types/list-session-params";
import {
  log,
  logError,
  logInfo,
  logDebug,
  logAPICall,
  logAPIResponseWithDetails,
  maskSensitiveData,
  setRequestId,
  getRequestId,
  logInfoWithColor,
  logWarn,
} from "./utils/logger";
import { VERSION, IS_RELEASE } from "./version";

// Browser data path constant (moved from config.ts)
const BROWSER_DATA_PATH = "/tmp/agentbay_browser";

/**
 * Parameters for creating a session.
 * Can be either a plain object conforming to the interface or a CreateSessionParams class instance.
 */
export type CreateSessionParams = CreateSessionParamsInterface;
export { CreateSessionParams as CreateSessionParamsClass } from "./session-params";
/**
 * Main class for interacting with the AgentBay cloud runtime environment.
 */
export class AgentBay {
  private apiKey: string;
  public client: Client;
  private endpoint: string;
  private config: Config;

  /**
   * Context service for managing persistent contexts.
   */
  context: ContextService;

  /**
   * Network service for managing networks.
   */
  /** Deprecated alias: use betaNetwork */
  network: BetaNetworkService;

  /**
   * Beta network service for managing networks.
   */
  betaNetwork: BetaNetworkService;

  /**
   * Beta skills service for listing official skills metadata.
   */
  betaSkills: BetaSkillsService;

  /**
   * Initialize the AgentBay client.
   *
   * @param options - Configuration options
   * @param options.apiKey - API key for authentication. If not provided, will look for AGENTBAY_API_KEY environment variable.
   * @param options.config - Custom configuration object. If not provided, will use environment-based configuration.
   * @param options.envFile - Custom path to .env file. If not provided, will search upward from current directory.
   */
  constructor(
    options: {
      apiKey?: string;
      config?: ConfigOptions;
      envFile?: string;
    } = {}
  ) {
    // Load .env file first to ensure AGENTBAY_API_KEY is available
    loadDotEnvWithFallback(options.envFile);

    this.apiKey = options.apiKey || process.env.AGENTBAY_API_KEY || "";

    if (!this.apiKey) {
      throw new AuthenticationError(
        "API key is required. Provide it as a parameter or set the AGENTBAY_API_KEY environment variable."
      );
    }

    this.config = loadConfig(options.config, options.envFile);

    // Load configuration using the enhanced loadConfig function
    const configData = loadConfig(options.config, options.envFile);
    this.endpoint = configData.endpoint;

    const config = new $OpenApiUtil.Config({
      regionId: "",
      endpoint: this.endpoint,
    });

    config.readTimeout = configData.timeout_ms;
    config.connectTimeout = configData.timeout_ms;

    try {
      this.client = new Client(config);

      // Initialize context service
      this.context = new ContextService(this);
      this.betaNetwork = new BetaNetworkService(this);
      this.betaSkills = new BetaSkillsService(this);
      // Deprecated alias: network APIs are beta for now
      this.network = this.betaNetwork as any;
    } catch (error) {
      logError(`Failed to constructor:`, error);
      throw new AuthenticationError(`Failed to constructor: ${error}`);
    }
  }

  /**
   * Get the region ID.
   * @returns The region ID or undefined if not set.
   */
  getRegionId(): string | undefined {
    return this.config.region_id;
  }

  /**
   * Wait for mobile simulate command to complete.
   *
   * @param session - The session to wait for mobile simulate
   * @param mobileSimPath - The dev info path to the mobile simulate
   * @param mobileSimMode - The mode of the mobile simulate. If not provided, will use the default mode.
   */
  private async _waitForMobileSimulate(
    session: Session,
    mobileSimPath: string,
    mobileSimMode?: string
  ): Promise<void> {
    log("⏳ Mobile simulate: Waiting for completion");

    if (!(session as any).mobile) {
      logInfo("Mobile module not found in session, skipping mobile simulate");
      return;
    }
    if (!(session as any).command) {
      logInfo("Command module not found in session, skipping mobile simulate");
      return;
    }
    if (!mobileSimPath) {
      logInfo("Mobile simulate path is empty, skipping mobile simulate");
      return;
    }

    try {
      // Run mobile simulate command
      const startTime = Date.now();
      const devInfoFilePath = `${mobileSimPath}/dev_info.json`;
      let wyaApplyOption = "";

      if (!mobileSimMode || mobileSimMode === "PropertiesOnly") {
        wyaApplyOption = "";
      } else if (mobileSimMode === "SensorsOnly") {
        wyaApplyOption = "-sensors";
      } else if (mobileSimMode === "PackagesOnly") {
        wyaApplyOption = "-packages";
      } else if (mobileSimMode === "ServicesOnly") {
        wyaApplyOption = "-services";
      } else if (mobileSimMode === "All") {
        wyaApplyOption = "-all";
      }

      const command =
        `chmod -R a+rwx ${mobileSimPath}; wya apply ${wyaApplyOption} ${devInfoFilePath}`.trim();
      logInfo(
        `ℹ️  ⏳ Waiting for mobile simulate completion, command: [${command}]`
      );

      const cmdResult = await (session as any).command.executeCommand(command);
      if (cmdResult.success) {
        const endTime = Date.now();
        const consumeTime = (endTime - startTime) / 1000;
        log(
          `✅ Mobile simulate completed with mode: ${
            mobileSimMode || "PropertiesOnly"
          }, duration: ${consumeTime.toFixed(2)} seconds`
        );
        if (cmdResult.output) {
          log(`   Output: ${cmdResult.output.trim()}`);
        }
      } else {
        logInfo(
          `Failed to execute mobile simulate command: ${cmdResult.errorMessage}`
        );
      }
    } catch (error) {
      logInfo(`Error executing mobile simulate command: ${error}`);
    }
  }

  /**
   * Create a new session in the AgentBay cloud environment.
   *
   * @param params - Optional parameters for creating the session
   * @returns SessionResult containing the created session and request ID
   */
  /**
   * Creates a new AgentBay session with specified configuration.
   *
   * @param params - Configuration parameters for the session:
   *                 - labels: Key-value pairs for session metadata
   *                 - imageId: Custom image ID for the session environment
   *                 - contextSync: Array of context synchronization configurations
   *                 - browserContext: Browser-specific context configuration
   *                 - policyId: Security policy ID
   *                 - enableBrowserReplay: Enable browser session recording
   *                 - extraConfigs: Additional configuration options
   *                 - framework: Framework identifier for tracking
   *
   * @returns Promise resolving to SessionResult containing:
   *          - success: Whether session creation succeeded
   *          - session: Session object for interacting with the environment
   *          - requestId: Unique identifier for this API request
   *          - errorMessage: Error description if creation failed
   *
   * @throws Error if API call fails or authentication is invalid.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ labels: { project: 'demo' } });
   * if (result.success) {
   *   await result.session.filesystem.readFile('/etc/hostname');
   *   await result.session.delete();
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - Creates a new isolated cloud runtime environment
   * - Automatically creates file transfer context if not provided
   * - Waits for context synchronization if contextSync is specified
   * - Browser replay creates a separate recording context
   *
   * @see {@link get}, {@link list}, {@link Session.delete}
   */
  async create(params: CreateSessionParams = {}): Promise<SessionResult> {
    try {
      // Create a deep copy of params to avoid modifying the original object
      const paramsCopy = this.deepCopyParams(params);
      logDebug(
        `default context syncs length: ${paramsCopy.contextSync?.length}`
      );

      // Add context syncs for mobile simulate if provided
      if (paramsCopy.extraConfigs?.mobile?.simulateConfig) {
        const mobileSimContextId =
          paramsCopy.extraConfigs.mobile.simulateConfig.simulatedContextId;
        if (mobileSimContextId) {
          const mobileSimContextSync = new ContextSync(
            mobileSimContextId,
            "/data/agentbay_mobile_info"
          );
          if (!paramsCopy.contextSync) {
            paramsCopy.contextSync = [];
          }
          logInfo(
            `Adding context sync for mobile simulate: ${JSON.stringify(
              mobileSimContextSync
            )}`
          );
          paramsCopy.contextSync.push(mobileSimContextSync);
        }
      }

      const request = new $_client.CreateMcpSessionRequest({
        authorization: "Bearer " + this.apiKey,
      });

      // Only set enable_record when user explicitly sets enable_browser_replay
      // When undefined (not set), don't send the field - let server decide the default
      if (paramsCopy.enableBrowserReplay !== undefined) {
        request.enableRecord = paramsCopy.enableBrowserReplay;
      }

      // Add SDK stats for tracking
      const framework = paramsCopy?.framework || "";
      const sdkStatsJson = `{"source":"sdk","sdk_language":"typescript","sdk_version":"${VERSION}","is_release":${IS_RELEASE},"framework":"${framework}"}`;
      request.sdkStats = sdkStatsJson;

      // Add LoginRegionId if region_id is set
      if (this.config.region_id) {
        request.loginRegionId = this.config.region_id;
      }

      // Add labels if provided
      if (paramsCopy.labels) {
        request.labels = JSON.stringify(paramsCopy.labels);
      }

      // Add image_id if provided
      if (paramsCopy.imageId) {
        request.imageId = paramsCopy.imageId;
      }

      // Add PolicyId if provided
      if (paramsCopy.policyId) {
        request.mcpPolicyId = paramsCopy.policyId;
      }

      // Beta: Add NetworkId if provided
      if ((paramsCopy as any).betaNetworkId) {
        (request as any).networkId = (paramsCopy as any).betaNetworkId;
      }

      // SDK idle release timeout (seconds)
      if (
        (paramsCopy as any).idleReleaseTimeout !== undefined &&
        (paramsCopy as any).idleReleaseTimeout !== null &&
        (paramsCopy as any).idleReleaseTimeout > 0
      ) {
        (request as any).timeout = (paramsCopy as any).idleReleaseTimeout;
      }

      // Flag to indicate if we need to wait for context synchronization
      let needsContextSync = false;
      const waitContextIds = new Set<string>();

      // Flag to indicate if we need to wait for mobile simulate
      let needsMobileSim = false;
      let mobileSimMode: string | undefined = undefined;
      let mobileSimPath: string | undefined = undefined;

      // Add context sync configurations if provided
      if (paramsCopy.contextSync && paramsCopy.contextSync.length > 0) {
        const persistenceDataList: CreateMcpSessionRequestPersistenceDataList[] =
          [];
        for (const contextSync of paramsCopy.contextSync) {
          const persistenceItem =
            new CreateMcpSessionRequestPersistenceDataList({
              contextId: contextSync.contextId,
              path: contextSync.path,
            });

          // Convert policy to JSON string if provided
          if (contextSync.policy) {
            persistenceItem.policy = JSON.stringify(contextSync.policy);
          }

          persistenceDataList.push(persistenceItem);
          if ((contextSync as any).betaWaitForCompletion !== false) {
            waitContextIds.add(contextSync.contextId);
          }
        }
        request.persistenceDataList = persistenceDataList;
        needsContextSync = persistenceDataList.length > 0;
      }

      // Add BrowserContext as a ContextSync if provided
      if (paramsCopy.browserContext) {
        const bc = paramsCopy.browserContext;
        const syncMode = bc.syncMode ?? BrowserSyncMode.STANDARD;

        let whiteLists: { path: string; excludePaths: string[] }[];
        if (syncMode === BrowserSyncMode.MINIMAL) {
          whiteLists = [
            { path: "/Local State", excludePaths: [] },
            { path: "/Default/Cookies", excludePaths: [] },
            { path: "/Default/Cookies-journal", excludePaths: [] },
          ];
        } else {
          // STANDARD mode: login state + anti-risk-control data
          whiteLists = [
            // Auth core
            { path: "/Local State", excludePaths: [] },
            { path: "/Default/Cookies", excludePaths: [] },
            { path: "/Default/Cookies-journal", excludePaths: [] },
            // Anti-risk-control device fingerprint (localStorage / IndexedDB)
            { path: "/Default/Local Storage", excludePaths: [] },
            { path: "/Default/IndexedDB", excludePaths: [] },
            { path: "/Default/Session Storage", excludePaths: [] },
            // Saved passwords and form autofill
            { path: "/Default/Login Data", excludePaths: [] },
            { path: "/Default/Login Data-journal", excludePaths: [] },
            { path: "/Default/Login Data For Account", excludePaths: [] },
            {
              path: "/Default/Login Data For Account-journal",
              excludePaths: [],
            },
            { path: "/Default/Web Data", excludePaths: [] },
            { path: "/Default/Web Data-journal", excludePaths: [] },
            // Browser settings and permission consistency
            { path: "/Default/Preferences", excludePaths: [] },
            { path: "/Default/Secure Preferences", excludePaths: [] },
            // Network behavior consistency (HSTS / QUIC)
            { path: "/Default/TransportSecurity", excludePaths: [] },
            { path: "/Default/Network Persistent State", excludePaths: [] },
            // Rendering fingerprint stability
            { path: "/Default/GPUCache", excludePaths: [] },
            // Cross-domain password matching
            { path: "/Default/Affiliation Database", excludePaths: [] },
            { path: "/Default/Affiliation Database-journal", excludePaths: [] },
          ];
        }

        const syncPolicy = {
          uploadPolicy: { autoUpload: bc.autoUpload },
          downloadPolicy: null,
          deletePolicy: null,
          bwList: { whiteLists },
          recyclePolicy: null,
        };

        // Create browser context sync item
        const browserContextSync =
          new CreateMcpSessionRequestPersistenceDataList({
            contextId: bc.contextId,
            path: BROWSER_DATA_PATH,
            policy: JSON.stringify(syncPolicy),
          });

        // Add to persistence data list or create new one if not exists
        if (!request.persistenceDataList) {
          request.persistenceDataList = [];
        }
        request.persistenceDataList.push(browserContextSync);
        needsContextSync = true;
        waitContextIds.add(paramsCopy.browserContext.contextId);
      }

      // Add extra configs if provided
      if (paramsCopy.extraConfigs) {
        request.extraConfigs = JSON.stringify(paramsCopy.extraConfigs);

        // Check mobile simulate config
        if (paramsCopy.extraConfigs.mobile?.simulateConfig?.simulate) {
          mobileSimPath =
            paramsCopy.extraConfigs.mobile.simulateConfig.simulatePath;
          if (!mobileSimPath) {
            logInfo(
              "mobile_sim_path is not set now, skip mobile simulate operation"
            );
          } else {
            needsMobileSim = true;
            mobileSimMode =
              paramsCopy.extraConfigs.mobile.simulateConfig.simulateMode;
          }
        }
      }

      // Add skills loading if requested
      if (paramsCopy.loadSkills) {
        request.loadSkill = true;
        if (paramsCopy.skillNames && paramsCopy.skillNames.length > 0) {
          request.skills = paramsCopy.skillNames;
        }
      }

      // Log API request
      logAPICall("CreateMcpSession", {
        labels: paramsCopy.labels,
        imageId: paramsCopy.imageId,
        policyId: paramsCopy.policyId,
        persistenceDataCount: paramsCopy.contextSync
          ? paramsCopy.contextSync.length
          : 0,
      });

      const response = await this.client.createMcpSession(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";
      setRequestId(requestId);

      const sessionData = response.body;

      if (!sessionData || typeof sessionData !== "object") {
        logAPIResponseWithDetails(
          "CreateMcpSession",
          requestId,
          false,
          {},
          "Invalid response format: expected a dictionary"
        );
        logDebug("Full response:", JSON.stringify(sessionData, null, 2));
        return {
          requestId,
          success: false,
          errorMessage: "Invalid response format: expected a dictionary",
        };
      }

      // Check for API-level errors
      if (sessionData.success === false && sessionData.code) {
        const errorMessage = `[${sessionData.code}] ${
          sessionData.message || "Unknown error"
        }`;
        logAPIResponseWithDetails(
          "CreateMcpSession",
          requestId,
          false,
          {},
          errorMessage
        );
        logDebug("Full response:", JSON.stringify(sessionData, null, 2));
        return {
          requestId,
          success: false,
          errorMessage,
        };
      }

      const data = sessionData.data;
      if (!data || typeof data !== "object") {
        logAPIResponseWithDetails(
          "CreateMcpSession",
          requestId,
          false,
          {},
          "Invalid response format: 'data' field is not a dictionary"
        );
        logDebug("Full response:", JSON.stringify(sessionData, null, 2));
        return {
          requestId,
          success: false,
          errorMessage:
            "Invalid response format: 'data' field is not a dictionary",
        };
      }

      // Check data-level success field (business logic success)
      if (data.success === false) {
        const errorMessage = data.errMsg || "Session creation failed";
        logAPIResponseWithDetails(
          "CreateMcpSession",
          requestId,
          false,
          {},
          errorMessage
        );
        logDebug("Full response:", JSON.stringify(sessionData, null, 2));
        return {
          requestId,
          success: false,
          errorMessage,
        };
      }

      const sessionId = data.sessionId;
      if (!sessionId) {
        logAPIResponseWithDetails(
          "CreateMcpSession",
          requestId,
          false,
          {},
          "SessionId not found in response"
        );
        logDebug("Full response:", JSON.stringify(sessionData, null, 2));
        return {
          requestId,
          success: false,
          errorMessage: "SessionId not found in response",
        };
      }

      // ResourceUrl is optional in CreateMcpSession response
      const resourceUrl = data.resourceUrl || "";

      logAPIResponseWithDetails("CreateMcpSession", requestId, true, {
        sessionId,
        resourceUrl,
      });

      const session = new Session(this, sessionId);

      // Set AppInstanceId and ResourceUrl
      session.appInstanceId = data.appInstanceId || "";
      session.resourceUrl = resourceUrl;

      // LinkUrl/token may be returned by the server for direct tool calls.
      session.token = data.token || "";
      session.linkUrl = data.linkUrl || "";
      session.wsUrl = data.wsUrl || "";
      session.mcpTools = this.parseToolListToMcpTools(data.toolList);

      // Set browser recording state
      session.enableBrowserReplay = paramsCopy.enableBrowserReplay;

      // Store imageId used for this session
      (session as any).imageId = paramsCopy.imageId;

      // Apply mobile configuration if provided
      if (paramsCopy.extraConfigs && paramsCopy.extraConfigs.mobile) {
        log("Applying mobile configuration...");
        try {
          const configResult = await session.mobile.configure(
            paramsCopy.extraConfigs.mobile
          );
          if (configResult.success) {
            log("Mobile configuration applied successfully");
          } else {
            logError(
              `Warning: Failed to apply mobile configuration: ${configResult.errorMessage}`
            );
            // Continue with session creation even if mobile config fails
          }
        } catch (error) {
          logError(`Warning: Failed to apply mobile configuration: ${error}`);
          // Continue with session creation even if mobile config fails
        }
      }

      // If we have persistence data, wait for context synchronization
      if (needsContextSync && waitContextIds.size > 0) {
        logDebug("Waiting for context synchronization to complete...");

        // Exponential backoff configuration
        // Starts with short intervals (0.5s) for fast completion detection
        // Gradually increases intervals (up to 5s max) to reduce server load
        // Uses exponential backoff factor of 1.1
        const initialInterval = 500; // Start with 0.5 seconds (500ms) for quick response
        const maxInterval = 5000; // Maximum interval (5s) to avoid excessive delays
        const backoffFactor = 1.1; // Multiply interval by this factor each retry
        const maxRetries = 50; // Maximum number of retries

        let currentInterval = initialInterval;

        for (let retry = 0; retry < maxRetries; retry++) {
          try {
            // Get context status data
            const infoResult = await session.context.info();

            let hasFailure = false;
            const statusByContextId = new Map<string, string>();

            for (const item of infoResult.contextStatusData) {
              if (!waitContextIds.has(item.contextId)) {
                continue;
              }
              statusByContextId.set(item.contextId, item.status);
              logDebug(
                `Context ${item.contextId} status: ${item.status}, path: ${item.path}`
              );

              if (item.status === "Failed") {
                hasFailure = true;
                logError(
                  `Context synchronization failed for ${item.contextId}: ${item.errorMessage}`
                );
              }
            }

            let allCompleted = true;
            for (const ctxId of waitContextIds) {
              const st = statusByContextId.get(ctxId);
              if (!st || (st !== "Success" && st !== "Failed")) {
                allCompleted = false;
                break;
              }
            }

            if (allCompleted) {
              if (hasFailure) {
                logDebug("Context synchronization completed with failures");
              } else {
                logDebug("Context synchronization completed successfully");
              }
              break;
            }

            logDebug(
              `Waiting for context synchronization, attempt ${
                retry + 1
              }/${maxRetries}, next interval: ${(
                currentInterval / 1000
              ).toFixed(2)}s`
            );
            await new Promise((resolve) =>
              setTimeout(resolve, currentInterval)
            );

            // Exponential backoff: increase interval for next retry, capped at maxInterval
            currentInterval = Math.min(
              currentInterval * backoffFactor,
              maxInterval
            );
          } catch (error) {
            logError(
              `Error checking context status on attempt ${retry + 1}: ${error}`
            );
            await new Promise((resolve) =>
              setTimeout(resolve, currentInterval)
            );

            // Exponential backoff: increase interval for next retry, capped at maxInterval
            currentInterval = Math.min(
              currentInterval * backoffFactor,
              maxInterval
            );
          }
        }
      }

      // If we need to do mobile simulate by command, wait for it
      if (needsMobileSim && mobileSimPath) {
        await this._waitForMobileSimulate(
          session,
          mobileSimPath,
          mobileSimMode
        );
      }

      // Return SessionResult with request ID
      return {
        requestId,
        success: true,
        session,
      };
    } catch (error) {
      logError("Error calling create_mcp_session:", error);
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to create session: ${error}`,
      };
    }
  }

  /**
   * Returns paginated list of session IDs filtered by labels and status.
   *
   * @param labels - Optional labels to filter sessions (defaults to empty object)
   * @param page - Optional page number for pagination (starting from 1, defaults to 1)
   * @param limit - Optional maximum number of items per page (defaults to 10)
   * @param status - Optional status to filter sessions. Must be one of: RUNNING, PAUSING, PAUSED, RESUMING, DELETING, DELETED (defaults to undefined)
   * @returns SessionListResult - Paginated list of session IDs that match the labels and status
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: "your_api_key" });
   * const result = await agentBay.list({ project: "demo" }, 1, 10, "RUNNING");
   * if (result.success) {
   *  log(`Found ${result.sessionIds.length} sessions`);
   * }
   * ```
   */
  async list(
    labels: Record<string, string> = {},
    page?: number,
    limit = 10,
    status?: string
  ): Promise<SessionListResult> {
    try {
      // Validate status parameter
      if (status !== undefined) {
        const validStatuses = [
          "RUNNING",
          "PAUSING",
          "PAUSED",
          "RESUMING",
          "DELETING",
          "DELETED",
        ];
        if (!validStatuses.includes(status)) {
          return {
            requestId: "",
            success: false,
            errorMessage: `Invalid status '${status}'. Must be one of: ${validStatuses.join(
              ", "
            )}`,
            sessionIds: [],
            nextToken: "",
            maxResults: limit,
            totalCount: 0,
          };
        }
      }

      // Validate page number
      if (page !== undefined && page < 1) {
        return {
          requestId: "",
          success: false,
          errorMessage: `Cannot reach page ${page}: Page number must be >= 1`,
          sessionIds: [],
          nextToken: "",
          maxResults: limit,
          totalCount: 0,
        };
      }

      // Calculate next_token based on page number
      // Page 1 or undefined means no next_token (first page)
      // For page > 1, we need to make multiple requests to get to that page
      let nextToken = "";
      if (page !== undefined && page > 1) {
        // We need to fetch pages 1 through page-1 to get the next_token
        let currentPage = 1;
        while (currentPage < page) {
          // Make API call to get next_token
          const request = new ListSessionRequest({
            authorization: `Bearer ${this.apiKey}`,
            labels: JSON.stringify(labels),
            maxResults: limit,
          });
          if (nextToken) {
            request.nextToken = nextToken;
          }
          if (status) {
            request.status = status;
          }

          const response = await this.client.listSession(request);
          const requestId = extractRequestId(response) || "";

          if (!response.body?.success) {
            const code = response.body?.code || "Unknown";
            const message = response.body?.message || "Unknown error";
            return {
              requestId,
              success: false,
              errorMessage: `[${code}] ${message}`,
              sessionIds: [],
              nextToken: "",
              maxResults: limit,
              totalCount: 0,
            };
          }

          nextToken = response.body.nextToken || "";
          if (!nextToken) {
            // No more pages available
            return {
              requestId,
              success: false,
              errorMessage: `Cannot reach page ${page}: No more pages available`,
              sessionIds: [],
              nextToken: "",
              maxResults: limit,
              totalCount: response.body.totalCount || 0,
            };
          }
          currentPage += 1;
        }
      }

      // Make the actual request for the desired page
      const request = new ListSessionRequest({
        authorization: `Bearer ${this.apiKey}`,
        labels: JSON.stringify(labels),
        maxResults: limit,
      });
      if (nextToken) {
        request.nextToken = nextToken;
      }
      if (status) {
        request.status = status;
      }

      // Log API request
      logAPICall("ListSession", {
        labels,
        maxResults: limit,
        nextToken: nextToken || undefined,
        status: status || undefined,
      });

      const response = await this.client.listSession(request);

      // Extract request ID
      const requestId = extractRequestId(response) || "";
      setRequestId(requestId);

      // Check for errors in the response
      if (!response.body?.success) {
        const code = response.body?.code || "Unknown";
        const message = response.body?.message || "Unknown error";
        logAPIResponseWithDetails(
          "ListSession",
          requestId,
          false,
          {},
          `[${code}] ${message}`
        );
        logDebug(
          "Full ListSession response:",
          JSON.stringify(response.body, null, 2)
        );
        return {
          requestId,
          success: false,
          errorMessage: `[${code}] ${message}`,
          sessionIds: [],
          nextToken: "",
          maxResults: limit,
          totalCount: 0,
        };
      }

      const sessionIds: Array<{ sessionId: string; sessionStatus: string }> =
        [];

      // Extract session data
      if (response.body.data) {
        for (const sessionData of response.body.data) {
          if (sessionData.sessionId) {
            // Create a structured session object with both ID and status
            const sessionInfo = {
              sessionId: sessionData.sessionId,
              sessionStatus: sessionData.sessionStatus || "UNKNOWN",
            };
            sessionIds.push(sessionInfo);
          }
        }
      }

      logAPIResponseWithDetails("ListSession", requestId, true, {
        sessionCount: sessionIds.length,
        totalCount: response.body.totalCount || 0,
        maxResults: response.body.maxResults || limit,
      });

      // Return SessionListResult with request ID and pagination info
      return {
        requestId,
        success: true,
        sessionIds,
        nextToken: response.body.nextToken || "",
        maxResults: response.body.maxResults || limit,
        totalCount: response.body.totalCount || 0,
      };
    } catch (error) {
      logError("Error calling list_session:", error);
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to list sessions: ${error}`,
        sessionIds: [],
      };
    }
  }

  /**
   * Delete a session by session object.
   *
   * @param session - The session to delete.
   * @param syncContext - Whether to sync context data (trigger file uploads) before deleting the session. Defaults to false.
   * @returns DeleteResult indicating success or failure and request ID
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await agentBay.delete(result.session);
   * }
   * ```
   */
  async delete(session: Session, syncContext = false): Promise<DeleteResult> {
    try {
      // Delete the session and get the result
      logAPICall("DeleteSession", { sessionId: session.sessionId });
      const deleteResult = await session.delete(syncContext);

      logAPIResponseWithDetails(
        "DeleteSession",
        deleteResult.requestId,
        deleteResult.success,
        { sessionId: session.sessionId }
      );

      // Return the DeleteResult obtained from session.delete()
      return deleteResult;
    } catch (error) {
      logError("Error deleting session:", error);
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to delete session ${session.sessionId}: ${error}`,
      };
    }
  }

  /**
   * Get session information by session ID.
   *
   * @param sessionId - The ID of the session to retrieve.
   * @returns GetSessionResult containing session information
   */
  /**
   * Get session information by session ID (internal).
   *
   * Users should prefer {@link get} which returns a {@link Session}.
   *
   * @internal
   */
  async _getSession(sessionId: string): Promise<$GetSessionResult> {
    try {
      logAPICall("GetSession", { sessionId });

      const request = new $GetSessionRequest({
        authorization: `Bearer ${this.apiKey}`,
        sessionId: sessionId,
      });

      const response = await this.client.getSession(request);
      const requestId = extractRequestId(response) || "";
      const body = response.body;

      setRequestId(requestId);

      // Check for API-level errors
      if (body?.success === false && body.code) {
        logAPIResponseWithDetails(
          "GetSession",
          requestId,
          false,
          {},
          `[${body.code}] ${body.message || "Unknown error"}`
        );
        logDebug("Full GetSession response:", JSON.stringify(body, null, 2));
        return {
          requestId,
          httpStatusCode: body.httpStatusCode || 0,
          code: body.code,
          success: false,
          errorMessage: `[${body.code}] ${body.message || "Unknown error"}`,
        };
      }

      const result: $GetSessionResult = {
        requestId,
        httpStatusCode: body?.httpStatusCode || 0,
        code: body?.code || "",
        success: body?.success || false,
        errorMessage: "",
      };

      if (body?.data) {
        // Extract contexts list from response
        const contextsList = body.data.contexts || [];
        const contexts: Array<{ name: string; id: string }> = [];
        if (Array.isArray(contextsList)) {
          for (const ctx of contextsList) {
            if (ctx && typeof ctx === "object" && ctx.name && ctx.id) {
              contexts.push({
                name: ctx.name,
                id: ctx.id,
              });
            }
          }
        }

        const wsUrl = (body.data as any).wsUrl || "";
        const data = {
          appInstanceId: body.data.appInstanceId || "",
          resourceId: body.data.resourceId || "",
          sessionId: body.data.sessionId || "",
          success: body.data.success || false,
          httpPort: body.data.httpPort || "",
          networkInterfaceIp: body.data.networkInterfaceIp || "",
          token: body.data.token || "",
          linkUrl: (body.data as any).linkUrl || "",
          wsUrl,
          vpcResource: body.data.vpcResource || false,
          resourceUrl: body.data.resourceUrl || "",
          status: body.data.status || "",
          toolList: body.data.toolList || "",
          contexts: contexts.length > 0 ? contexts : undefined,
        };
        result.data = data;

        logAPIResponseWithDetails("GetSession", requestId, true, {
          sessionId: data.sessionId,
          resourceId: data.resourceId,
          httpPort: data.httpPort,
        });
      }

      return result;
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
        logInfo(`Session not found: ${sessionId}`);
        logDebug(`GetSession error details: ${errorStr}`);
        return {
          requestId: "",
          httpStatusCode: 400,
          code: "InvalidMcpSession.NotFound",
          success: false,
          errorMessage: `Session ${sessionId} not found`,
        };
      } else {
        // This is an unexpected error - log with full error
        logError("Error calling GetSession:", error);
        return {
          requestId: "",
          httpStatusCode: 0,
          code: "",
          success: false,
          errorMessage: `Failed to get session ${sessionId}: ${error}`,
        };
      }
    }
  }

  /**
   * Get a session by its ID.
   *
   * This method retrieves a session by calling the GetSession API
   * and returns a SessionResult containing the Session object and request ID.
   *
   * @param sessionId - The ID of the session to retrieve
   * @returns Promise resolving to SessionResult with the Session instance, request ID, and success status
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const createResult = await agentBay.create();
   * if (createResult.success) {
   *   const result = await agentBay.get(createResult.session.sessionId);
   *   await result.session?.filesystem.readFile('/etc/hostname');
   *   await result.session?.delete();
   * }
   * ```
   */
  async get(sessionId: string): Promise<SessionResult> {
    // Validate input
    if (!sessionId || (typeof sessionId === "string" && !sessionId.trim())) {
      return {
        requestId: "",
        success: false,
        errorMessage: "session_id is required",
      };
    }

    // Call GetSession API
    const getResult = await this._getSession(sessionId);

    // Check if the API call was successful
    if (!getResult.success) {
      const errorMsg = getResult.errorMessage || "Unknown error";
      return {
        requestId: getResult.requestId,
        success: false,
        errorMessage: `Failed to get session ${sessionId}: ${errorMsg}`,
      };
    }

    // Create the Session object
    const session = new Session(this, sessionId);

    // Set ResourceUrl from GetSession response
    if (getResult.data) {
      session.appInstanceId = getResult.data.appInstanceId || "";
      session.resourceUrl = getResult.data.resourceUrl;
      session.token = getResult.data.token || "";
      session.linkUrl = getResult.data.linkUrl || "";
      session.wsUrl = getResult.data.wsUrl || "";
      session.mcpTools = this.parseToolListToMcpTools(getResult.data.toolList);
    }

    return {
      requestId: getResult.requestId,
      success: true,
      session,
    };
  }

  /**
   * Get the internal HTTP client instance.
   *
   * This is primarily for internal use and advanced scenarios where you need direct access
   * to the underlying API client.
   *
   * @returns The Client instance used for API communication
   *
   * @internal
   *
   * @remarks
   * **Note:** This method is primarily for internal use. Most users should interact
   * with the SDK through higher-level methods like `create()`, `get()`, and `list()`.
   */
  getClient(): Client {
    return this.client;
  }

  /**
   * Get the API key used for authentication.
   *
   * @returns The API key string
   *
   * @internal
   *
   * @remarks
   * **Security Note:** Be careful when logging or exposing API keys. Always keep them secure
   * and never commit them to version control.
   */
  getAPIKey(): string {
    return this.apiKey;
  }

  /**
   * Asynchronously pause a session, putting it into a dormant state.
   *
   * **Note**: This feature is currently in whitelist-only access.
   * Contact agentbay_dev@alibabacloud.com to request access.
   *
   * This method directly calls the PauseSessionAsync API without waiting for the session
   * to reach the PAUSED state.
   *
   * @param session - The session to pause.
   * @param timeout - Timeout in seconds to wait for the session to pause. Defaults to 600 seconds.
   * @param pollInterval - Interval in seconds between status polls. Defaults to 2.0 seconds.
   * @returns SessionPauseResult indicating success or failure and request ID
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const session = (await agentBay.create()).session;
   * const pauseResult = await agentBay.betaPauseAsync(session);
   * await agentBay.betaResumeAsync(session);
   * await session.delete();
   * ```
   *
   * @remarks
   * **Behavior:**
   * - This method does not wait for the session to reach the PAUSED state
   * - It only submits the pause request to the API
   * - The session state transitions from RUNNING -> PAUSING -> PAUSED
   * - Paused sessions consume fewer resources but maintain their state
   *
   * @see {@link betaResumeAsync}, {@link Session.betaPauseAsync}
   */
  async betaPauseAsync(
    session: Session,
    timeout = 600,
    pollInterval = 2.0
  ): Promise<import("./types/api-response").SessionPauseResult> {
    try {
      // Call session's pause_async method directly
      return await session.betaPauseAsync(timeout, pollInterval);
    } catch (error) {
      logError("Error calling pause session async:", error);
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to pause session ${session.sessionId}: ${error}`,
      };
    }
  }

  /**
   * Asynchronously resume a session from a paused state.
   *
   * This method directly calls the ResumeSessionAsync API without waiting for the session
   * to reach the RUNNING state.
   *
   * @param session - The session to resume.
   * @param timeout - Timeout in seconds to wait for the session to resume. Defaults to 600 seconds.
   * @param pollInterval - Interval in seconds between status polls. Defaults to 2.0 seconds.
   * @returns SessionResumeResult indicating success or failure and request ID
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const session = (await agentBay.create()).session;
   * await agentBay.betaPauseAsync(session);
   * const resumeResult = await agentBay.betaResumeAsync(session);
   * await session.delete();
   * ```
   *
   * @remarks
   * **Behavior:**
   * - This method does not wait for the session to reach the RUNNING state
   * - It only submits the resume request to the API
   * - The session state transitions from PAUSED -> RESUMING -> RUNNING
   * - Only sessions in PAUSED state can be resumed
   *
   * @see {@link betaPauseAsync}, {@link Session.betaResumeAsync}
   */
  async betaResumeAsync(
    session: Session,
    timeout = 600,
    pollInterval = 2.0
  ): Promise<import("./types/api-response").SessionResumeResult> {
    try {
      // Call session's resume_async method directly
      return await session.betaResumeAsync(timeout, pollInterval);
    } catch (error) {
      logError("Error calling resume session async:", error);
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to resume session ${session.sessionId}: ${error}`,
      };
    }
  }

  private parseToolListToMcpTools(toolList: any): McpTool[] {
    if (!toolList) {
      return [];
    }

    let items = toolList;
    if (typeof toolList === "string") {
      try {
        items = JSON.parse(toolList);
      } catch (error) {
        logDebug(`Failed to parse ToolList JSON: ${error}`);
        return [];
      }
    }

    if (!Array.isArray(items)) {
      return [];
    }

    const tools: McpTool[] = [];
    for (const item of items) {
      if (!item || typeof item !== "object") {
        continue;
      }
      const name = item.name || item.Name || "";
      const server = item.server || item.serverName || item.Server || "";
      const description = item.description || item.Description || "";
      const inputSchema = item.inputSchema || item.input_schema || {};
      const tool = item.tool || item.Tool || "";
      tools.push({
        name,
        server,
        description,
        inputSchema,
        tool,
      });
    }

    return tools;
  }

  /**
   * Creates a deep copy of CreateSessionParams to avoid modifying the original object.
   * Extension contexts are automatically merged when browserContext is set in the class.
   * @param params - The original params object to copy
   * @returns A deep copy of the params object as interface with merged context syncs
   */
  private deepCopyParams(
    params: CreateSessionParams
  ): CreateSessionParamsInterface {
    let result: CreateSessionParamsInterface;

    // Check if params is a CreateSessionParams class instance
    if (params instanceof CreateSessionParamsClass) {
      // For class instances, extension contexts are already merged automatically when browserContext was set
      // We can directly use the class properties without needing toJSON()
      result = {
        labels: params.labels,
        imageId: params.imageId,
        idleReleaseTimeout: (params as any).idleReleaseTimeout,
        contextSync: params.contextSync, // Already contains merged extension contexts
        browserContext: params.browserContext,
        isVpc: params.isVpc,
        mcpPolicyId: params.mcpPolicyId,
        policyId: params.policyId,
        betaNetworkId: params.betaNetworkId,
        enableBrowserReplay: params.enableBrowserReplay,
        extraConfigs: params.extraConfigs,
        framework: params.framework,
        loadSkills: params.loadSkills,
        skillNames: params.skillNames,
      };
    } else {
      // Use any type for JSON.parse result since params could be either interface or class instance
      const copied = JSON.parse(JSON.stringify(params)) as any;
      result = copied as CreateSessionParamsInterface;
      // Don't set enableBrowserReplay default - leave as-is so server decides
      const allContextSyncs = params?.contextSync
        ? [...params.contextSync]
        : [];
      // **IMPORTANT: Apply extension context merging for plain objects automatically**
      // Check if browserContext exists and has extension syncs to merge
      if (
        result.browserContext &&
        result.browserContext.extensionContextSyncs
      ) {
        // Merge with extension syncs (equivalent to automatic merging in class)
        result.contextSync = [
          ...allContextSyncs,
          ...result.browserContext.extensionContextSyncs,
        ];
      }
      if (
        params?.browserContext &&
        params.browserContext.fingerprintContextSync
      ) {
        result.contextSync = [
          ...(result.contextSync || []),
          params.browserContext.fingerprintContextSync,
        ];
        log("Added fingerprint context sync from BrowserContext");
      }
      // Reconstruct ContextSync objects if they exist (since they might be class instances)
      if (result.contextSync && Array.isArray(result.contextSync)) {
        result.contextSync = result.contextSync.map((cs: any) => {
          // Reconstruct from plain object (JSON.parse converts class instances to plain objects)
          return new ContextSync(
            cs.contextId,
            cs.path,
            cs.policy,
            cs.betaWaitForCompletion
          );
        });
      }

      // Reconstruct BrowserContext if it exists
      if (result.browserContext) {
        const bc = result.browserContext as any;
        result.browserContext = new BrowserContext(
          bc.contextId,
          bc.autoUpload,
          bc.extensionOption,
          bc.fingerprintContext,
          bc.syncMode
        );
      }
    }

    return result;
  }
}

/**
 * Creates a new AgentBay client using default configuration.
 * This is a convenience function that allows creating an AgentBay instance without a config parameter.
 *
 * @param apiKey - API key for authentication
 * @returns A new AgentBay instance with default configuration
 */
export function newAgentBayWithDefaults(apiKey: string): AgentBay {
  return new AgentBay({ apiKey });
}
