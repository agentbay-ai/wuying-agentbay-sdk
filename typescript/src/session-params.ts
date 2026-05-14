import { ContextMount } from "./context-mount";
import {
  ContextSync,
  SyncPolicy,
  newUploadPolicy,
  newExtractPolicy,
  newRecyclePolicy,
  Lifecycle,
  DownloadStrategy,
  WhiteList,
  newDeletePolicy,
} from "./context-sync";
import { ExtensionOption } from "./extension";
import { BrowserFingerprintContext } from "./browser";
import { ExtraConfigs, extraConfigsToJSON } from "./types/extra-configs";
import { LifecyclePolicy } from "./lifecycle-policy";

// Browser fingerprint persistent path constant (moved from config.ts)
const BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint";

/**
 * Browser data synchronization mode.
 *
 * Controls the scope of browser data synchronized between sessions.
 * - MINIMAL: Only Cookies + Local State. Smallest footprint, sufficient for basic cookie-based auth.
 * - STANDARD: Login state + anti-risk-control data. Includes Cookies, localStorage, IndexedDB,
 *   saved passwords, preferences, HSTS, GPU cache, etc. Recommended for most scenarios.
 */
export enum BrowserSyncMode {
  /** Synchronize only essential files (Cookies, Local State). */
  MINIMAL = "minimal",
  /** Synchronize login state and anti-risk-control data (recommended). */
  STANDARD = "standard",
}
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
} from "./utils/logger";

/**
 * Browser context configuration for session with optional extension support.
 *
 * This class provides browser context configuration for cloud sessions and supports
 * automatic extension synchronization when ExtensionOption is provided.
 *
 * Key Features:
 * - Browser context binding for sessions
 * - Automatic browser data upload on session end
 * - Optional extension integration with automatic context sync generation
 * - Clean API with ExtensionOption encapsulation
 *
 * Extension Configuration:
 * - **ExtensionOption**: Pass an ExtensionOption object with contextId and extensionIds
 * - **No Extensions**: Don't provide extensionOption parameter (extensionContextSyncs will be undefined)
 *
 * Usage Examples:
 * ```typescript
 * // With extensions using ExtensionOption
 * import { ExtensionOption } from "./extension";
 *
 * const extOption = new ExtensionOption(
 *   "my_extensions",
 *   ["ext1", "ext2"]
 * );
 *
 * const browserContext = new BrowserContext(
 *   "browser_session",
 *   true,
 *   extOption
 * );
 *
 * // Without extensions (minimal configuration)
 * const browserContext = new BrowserContext(
 *   "browser_session",
 *   true
 * );
 * // extensionContextSyncs will be undefined
 * ```
 */
export class BrowserContext {
  /** ID of the browser context to bind to the session */
  contextId: string;
  /** Whether to automatically upload browser data when the session ends */
  autoUpload: boolean;
  /** Browser data synchronization mode. Defaults to STANDARD. */
  syncMode: BrowserSyncMode;
  /** Optional browser fingerprint context configuration object containing fingerprintContextId */
  fingerprintContext?: BrowserFingerprintContext;
  /** ID of the fingerprint context for browser fingerprint. Set automatically from fingerprint_context. */
  fingerprintContextId?: string;
  /** Auto-generated context sync for fingerprint. None if no fingerprint configuration provided. */
  fingerprintContextSync?: ContextSync;
  /** Optional extension configuration object containing context_id and extension_ids */
  extensionOption?: ExtensionOption;
  /** ID of the extension context for browser extensions. Set automatically from extension_option. */
  extensionContextId?: string;
  /** List of extension IDs to synchronize. Set automatically from extension_option. */
  extensionIds?: string[];
  /** Auto-generated context syncs for extensions. None if no extension configuration provided. */
  extensionContextSyncs?: ContextSync[];

  /**
   * Initialize BrowserContextImpl with optional extension and fingerprint support.
   *
   * @param contextId - ID of the browser context to bind to the session.
   *                   This identifies the browser instance for the session.
   * @param autoUpload - Whether to automatically upload browser data
   *                    when the session ends. Defaults to true.
   * @param extensionOption - Extension configuration object containing
   *                         contextId and extensionIds. This encapsulates
   *                         all extension-related configuration.
   *                         Defaults to undefined.
   * @param fingerprintContext - Browser fingerprint context configuration object containing
   *                            fingerprintContextId. This encapsulates
   *                            all fingerprint-related configuration.
   *                            Defaults to undefined.
   * @param syncMode - Browser data synchronization mode.
   *                  MINIMAL: only Cookies + Local State.
   *                  STANDARD: login state + anti-risk-control data (recommended).
   *                  Defaults to STANDARD.
   *
   * Extension Configuration:
   * - **ExtensionOption**: Use extensionOption parameter with an ExtensionOption object
   * - **No Extensions**: Don't provide extensionOption parameter
   *
   * Fingerprint Configuration:
   * - **BrowserFingerprintContext**: Use fingerprintContext parameter with a BrowserFingerprintContext object
   * - **No Fingerprint**: Don't provide fingerprintContext parameter
   *
   * Auto-generation:
   * - extensionContextSyncs is automatically generated when extensionOption is provided
   * - extensionContextSyncs will be undefined if no extensionOption is provided
   * - extensionContextSyncs will be a ContextSync[] if extensionOption is valid
   * - fingerprintContextSync is automatically generated when fingerprintContext is provided
   * - fingerprintContextSync will be undefined if no fingerprintContext is provided
   * - fingerprintContextSync will be a ContextSync if fingerprintContext is valid
   */
  constructor(
    contextId: string,
    autoUpload = true,
    extensionOption?: ExtensionOption,
    fingerprintContext?: BrowserFingerprintContext,
    syncMode: BrowserSyncMode = BrowserSyncMode.STANDARD
  ) {
    this.contextId = contextId;
    this.autoUpload = autoUpload;
    this.syncMode = syncMode;
    this.extensionOption = extensionOption;
    this.fingerprintContext = fingerprintContext;

    // Handle fingerprint configuration from BrowserFingerprintContext
    if (fingerprintContext) {
      // Extract fingerprint information from BrowserFingerprintContext
      this.fingerprintContextId = fingerprintContext.fingerprintContextId;
      // Auto-generate fingerprint context sync
      this.fingerprintContextSync = this._createFingerprintContextSync();
    } else {
      // No fingerprint configuration provided
      this.fingerprintContextId = undefined;
      this.fingerprintContextSync = undefined;
    }

    // Handle extension configuration from ExtensionOption
    if (extensionOption) {
      // Extract extension information from ExtensionOption
      this.extensionContextId = extensionOption.contextId;
      this.extensionIds = extensionOption.extensionIds;
      // Auto-generate extension context syncs
      this.extensionContextSyncs = this._createExtensionContextSyncs();
    } else {
      // No extension configuration provided
      this.extensionContextId = undefined;
      this.extensionIds = [];
      this.extensionContextSyncs = undefined;
    }
  }

  /**
   * Create ContextSync configurations for browser extensions.
   *
   * This method is called only when extensionOption is provided and contains
   * valid extension configuration (contextId and extensionIds).
   *
   * @returns ContextSync[] - List of context sync configurations for extensions.
   *                         Returns empty list if extension configuration is invalid.
   */
  private _createExtensionContextSyncs(): ContextSync[] {
    if (
      !this.extensionIds ||
      this.extensionIds.length === 0 ||
      !this.extensionContextId
    ) {
      return [];
    }

    // Create whitelist for each extension ID
    const whiteLists: WhiteList[] = this.extensionIds.map((extId) => ({
      path: extId,
      excludePaths: [],
    }));

    // Create sync policy for extensions
    const syncPolicy: SyncPolicy = {
      uploadPolicy: {
        ...newUploadPolicy(),
        autoUpload: false,
      },
      extractPolicy: {
        ...newExtractPolicy(),
        extract: true,
        deleteSrcFile: true,
      },
      deletePolicy: {
        ...newDeletePolicy(),
        syncLocalFile: false,
      },
      recyclePolicy: newRecyclePolicy(),
      bwList: {
        whiteLists: whiteLists,
      },
      downloadPolicy: {
        autoDownload: true,
        downloadStrategy: DownloadStrategy.DownloadAsync,
      },
    };

    // Create context sync for extensions
    const extensionSync = new ContextSync(
      this.extensionContextId,
      "/tmp/extensions/",
      syncPolicy
    );

    return [extensionSync];
  }

  /**
   * Create ContextSync configuration for browser fingerprint.
   *
   * This method is called only when fingerprintContext is provided and contains
   * valid fingerprint configuration (fingerprintContextId).
   *
   * @returns ContextSync - Context sync configuration for fingerprint.
   *                       Returns undefined if fingerprint configuration is invalid.
   */
  private _createFingerprintContextSync(): ContextSync | undefined {
    if (!this.fingerprintContextId || !this.fingerprintContextId.trim()) {
      return undefined;
    }

    // Create sync policy for fingerprint
    const syncPolicy: SyncPolicy = {
      uploadPolicy: {
        ...newUploadPolicy(),
        autoUpload: false,
      },
      extractPolicy: {
        ...newExtractPolicy(),
        extract: true,
        deleteSrcFile: true,
      },
      deletePolicy: {
        ...newDeletePolicy(),
        syncLocalFile: false,
      },
      recyclePolicy: newRecyclePolicy(),
      bwList: {
        whiteLists: [],
      },
    };

    // Create context sync for fingerprint
    const fingerprintSync = new ContextSync(
      this.fingerprintContextId,
      BROWSER_FINGERPRINT_PERSIST_PATH,
      syncPolicy
    );

    return fingerprintSync;
  }

  /**
   * Get context syncs for extensions.
   *
   * @returns ContextSync[] - Context sync configurations for extensions. Returns empty list if no extensions configured.
   */
  getExtensionContextSyncs(): ContextSync[] {
    return this.extensionContextSyncs || [];
  }

  /**
   * Get context sync for fingerprint.
   *
   * @returns ContextSync - Context sync configuration for fingerprint.
   *                       Returns undefined if fingerprint configuration is invalid.
   */
  getFingerprintContextSync(): ContextSync | undefined {
    return this.fingerprintContextSync;
  }
}

/**
 * Parameters for creating a session.
 * This interface defines all possible fields that can be used when creating a session.
 */
export interface CreateSessionParamsInterface {
  /** Custom labels for the Session. These can be used for organizing and filtering sessions. */
  labels?: Record<string, string>;
  /** Image ID to use for the session. */
  imageId?: string;
  /** SDK-side idle release timeout in seconds (deprecated). Use lifecyclePolicy (minutes) instead. */
  idleReleaseTimeout?: number;
  /** Lifecycle policy for session timeout and manual release (minutes). Mutually exclusive with positive idleReleaseTimeout. */
  lifecyclePolicy?: LifecyclePolicy;
  /** List of context synchronization configurations. */
  contextSync?: ContextSync[];
  /** List of context mount configurations for direct-mount persistence. */
  contextMount?: ContextMount[];
  /** Optional configuration for browser data synchronization. */
  browserContext?: BrowserContext;
  /** Security policy ID (interface field name). */
  policyId?: string;
  /** Beta network ID to bind this session to. */
  betaNetworkId?: string;
  /** Whether to enable browser session recording. */
  enableBrowserReplay?: boolean;
  /** Additional configuration options. */
  extraConfigs?: ExtraConfigs;
  /** Framework identifier for tracking. */
  framework?: string;
  /** Whether to create a VPC-based session. Defaults to false. */
  isVpc?: boolean;
  /** MCP policy id to apply when creating the session (class field name). */
  mcpPolicyId?: string;
  /** Whether to load skills into the sandbox. */
  loadSkills?: boolean;
  /** Skill names to load. Loads all visible skills when loadSkills=true and this is not specified. */
  skillNames?: string[];
}

/**
 * CreateSessionParams provides a way to configure the parameters for creating a new session
 * in the AgentBay cloud environment.
 */
export class CreateSessionParams implements CreateSessionParamsInterface {
  /** Custom labels for the Session. These can be used for organizing and filtering sessions. */
  public labels: Record<string, string>;

  /** Image ID to use for the session. */
  public imageId?: string;

  /** SDK-side idle release timeout in seconds (deprecated). Default 0 when omitted. */
  public idleReleaseTimeout: number;

  /** Lifecycle policy (minutes). Mutually exclusive with positive idleReleaseTimeout. */
  public lifecyclePolicy: LifecyclePolicy | undefined;

  /**
   * List of context synchronization configurations.
   * These configurations define how contexts should be synchronized and mounted.
   */
  public contextSync: ContextSync[];

  /** List of context mount configurations for direct-mount persistence. */
  public contextMount: ContextMount[];

  /** Whether to create a VPC-based session. Defaults to false. */
  public isVpc?: boolean;

  /** MCP policy id to apply when creating the session. */
  public mcpPolicyId?: string;

  /** Security policy ID (interface field name). Maps to mcpPolicyId internally. */
  public policyId?: string;

  /** Beta network ID to bind this session to. */
  public betaNetworkId?: string;

  /** Whether to enable browser session recording. When undefined, server-side default applies. */
  public enableBrowserReplay?: boolean;

  /** Additional configuration options. */
  public extraConfigs?: ExtraConfigs;

  /** Framework identifier for tracking. */
  public framework: string;

  public browserContext?: BrowserContext;

  /** Whether to load skills into the sandbox. */
  public loadSkills?: boolean;

  /** Skill names to load. */
  public skillNames?: string[];

  constructor(params?: CreateSessionParamsInterface) {
    this.labels = params?.labels || {};
    this.imageId = params?.imageId;
    const idle = (params as any)?.idleReleaseTimeout;
    if (idle === undefined || idle === null) {
      this.idleReleaseTimeout = 0;
    } else if (
      typeof idle !== "number" ||
      !Number.isInteger(idle) ||
      idle <= 0
    ) {
      throw new Error(
        "idleReleaseTimeout must be a positive integer (seconds)"
      );
    } else {
      this.idleReleaseTimeout = idle;
    }
    this.lifecyclePolicy = (params as any)?.lifecyclePolicy || undefined;
    if (this.lifecyclePolicy && this.idleReleaseTimeout > 0) {
      throw new Error(
        "lifecyclePolicy cannot be used together with deprecated idleReleaseTimeout (seconds); use lifecyclePolicy only"
      );
    }
    this.isVpc = params?.isVpc || false;
    // Handle policyId mapping - if policyId is provided, use it, otherwise use mcpPolicyId
    this.mcpPolicyId = params?.mcpPolicyId ? params.mcpPolicyId : "";
    this.policyId = params?.policyId ? params.policyId : "";
    this.betaNetworkId = params?.betaNetworkId;
    // When not set, leave as undefined - let server decide the default
    this.enableBrowserReplay = params?.enableBrowserReplay;
    this.extraConfigs = params?.extraConfigs;
    this.framework = params?.framework || "";

    // Start with provided contextSync
    let allContextSyncs = params?.contextSync ? [...params.contextSync] : [];

    // Add extension context syncs from browserContext if available
    if (params?.browserContext && params.browserContext.extensionContextSyncs) {
      allContextSyncs = [
        ...allContextSyncs,
        ...params.browserContext.extensionContextSyncs,
      ];
      log(
        `Added ${params.browserContext.extensionContextSyncs.length} extension context sync(s) from BrowserContext`
      );
    }

    // Add fingerprint context sync from browserContext if available
    if (
      params?.browserContext &&
      params.browserContext.fingerprintContextSync
    ) {
      allContextSyncs = [
        ...allContextSyncs,
        params.browserContext.fingerprintContextSync,
      ];
      log("Added fingerprint context sync from BrowserContext");
    }

    this.contextSync = allContextSyncs;
    this.contextMount = params?.contextMount ? [...params.contextMount] : [];
    this.browserContext = params?.browserContext;
    this.loadSkills = params?.loadSkills;
    this.skillNames = params?.skillNames;
  }
}
