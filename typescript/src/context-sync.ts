// UploadStrategy defines the upload strategy for context synchronization
export enum UploadStrategy {
  UploadBeforeResourceRelease = "UploadBeforeResourceRelease",
}

// DownloadStrategy defines the download strategy for context synchronization
export enum DownloadStrategy {
  DownloadAsync = "DownloadAsync",
}

// UploadMode defines the upload mode for context synchronization
export enum UploadMode {
  File = "File",
  Archive = "Archive",
}

// Lifecycle defines the lifecycle options for recycle policy
export enum Lifecycle {
  Lifecycle_1Day = "Lifecycle_1Day",
  Lifecycle_3Days = "Lifecycle_3Days",
  Lifecycle_5Days = "Lifecycle_5Days",
  Lifecycle_10Days = "Lifecycle_10Days",
  Lifecycle_15Days = "Lifecycle_15Days",
  Lifecycle_30Days = "Lifecycle_30Days",
  Lifecycle_90Days = "Lifecycle_90Days",
  Lifecycle_180Days = "Lifecycle_180Days",
  Lifecycle_360Days = "Lifecycle_360Days",
  Lifecycle_Forever = "Lifecycle_Forever",
}

// UploadPolicy defines the upload policy for context synchronization
export interface UploadPolicy {
  autoUpload: boolean;
  uploadStrategy: UploadStrategy;
  uploadMode: UploadMode;
  archiveExcludePaths?: string[];
}

// DownloadPolicy defines the download policy for context synchronization
export interface DownloadPolicy {
  autoDownload: boolean;
  downloadStrategy: DownloadStrategy;
}

// DeletePolicy defines the delete policy for context synchronization
export interface DeletePolicy {
  syncLocalFile: boolean;
}

// ExtractPolicy defines the extract policy for context synchronization
export interface ExtractPolicy {
  extract: boolean;
  deleteSrcFile: boolean;
  extractToCurrentFolder: boolean;
}

// RecyclePolicy defines the recycle policy for context synchronization
export interface RecyclePolicy {
  lifecycle: Lifecycle;
  paths: string[];
}

// ExtractPolicyClass provides a class-based implementation with default values
export class ExtractPolicyClass implements ExtractPolicy {
  extract = true;
  deleteSrcFile = true;
  extractToCurrentFolder = false;

  constructor(
    extract = true,
    deleteSrcFile = true,
    extractToCurrentFolder = false
  ) {
    this.extract = extract;
    this.deleteSrcFile = deleteSrcFile;
    this.extractToCurrentFolder = extractToCurrentFolder;
  }

  /**
   * Creates a new extract policy with default values
   */
  static default(): ExtractPolicyClass {
    return new ExtractPolicyClass();
  }

  /**
   * Converts to plain object for JSON serialization
   */
  toDict(): Record<string, any> {
    return {
      extract: this.extract,
      deleteSrcFile: this.deleteSrcFile,
      extractToCurrentFolder: this.extractToCurrentFolder,
    };
  }
}

// WhiteList defines the white list configuration
export interface WhiteList {
  path: string;
  excludePaths?: string[];
}

export class WhiteListValidator {
  private static containsWildcard(path: string): boolean {
    return /[*?\[\]]/.test(path);
  }

  static validate(whitelist: WhiteList): void {
    if (this.containsWildcard(whitelist.path)) {
      throw new Error(
        `Wildcard patterns are not supported in path. Got: ${whitelist.path}. ` +
          "Please use exact directory paths instead."
      );
    }

    if (whitelist.excludePaths) {
      for (const excludePath of whitelist.excludePaths) {
        if (this.containsWildcard(excludePath)) {
          throw new Error(
            `Wildcard patterns are not supported in exclude_paths. Got: ${excludePath}. ` +
              "Please use exact directory paths instead."
          );
        }
      }
    }
  }
}

// BWList defines the black and white list configuration
export interface BWList {
  whiteLists?: WhiteList[];
}

// MappingPolicy defines the mapping policy for cross-platform context synchronization
export interface MappingPolicy {
  path: string;
}

// SyncPolicy defines the synchronization policy
export interface SyncPolicy {
  uploadPolicy?: UploadPolicy;
  downloadPolicy?: DownloadPolicy;
  deletePolicy?: DeletePolicy;
  extractPolicy?: ExtractPolicy;
  recyclePolicy?: RecyclePolicy;
  bwList?: BWList;
  mappingPolicy?: MappingPolicy;
}

const ALLOWED_POLICY_KEYS = new Set([
  "uploadPolicy",
  "downloadPolicy",
  "deletePolicy",
  "extractPolicy",
  "recyclePolicy",
  "bwList",
  "mappingPolicy",
]);

// Helper to validate object keys
function validatePolicyKeys(policy: any): void {
  if (!policy || typeof policy !== "object") return;

  for (const key of Object.keys(policy)) {
    if (!ALLOWED_POLICY_KEYS.has(key)) {
      throw new Error(
        `Unknown property in SyncPolicy: '${key}'. ` +
          `Valid properties are: ${Array.from(ALLOWED_POLICY_KEYS).join(", ")}`
      );
    }
  }
}

// SyncPolicyImpl provides a class-based implementation with default value handling
export class SyncPolicyImpl implements SyncPolicy {
  uploadPolicy?: UploadPolicy;
  downloadPolicy?: DownloadPolicy;
  deletePolicy?: DeletePolicy;
  extractPolicy?: ExtractPolicy;
  recyclePolicy?: RecyclePolicy;
  bwList?: BWList;

  constructor(policy?: Partial<SyncPolicy>) {
    if (policy) {
      validatePolicyKeys(policy);
      this.uploadPolicy = policy.uploadPolicy;
      this.downloadPolicy = policy.downloadPolicy;
      this.deletePolicy = policy.deletePolicy;
      this.extractPolicy = policy.extractPolicy;
      this.recyclePolicy = policy.recyclePolicy;
      this.bwList = policy.bwList;
    }
    this.ensureDefaults();
  }

  private ensureDefaults(): void {
    if (!this.uploadPolicy) {
      this.uploadPolicy = newUploadPolicy();
    }
    if (!this.downloadPolicy) {
      this.downloadPolicy = newDownloadPolicy();
    }
    if (!this.deletePolicy) {
      this.deletePolicy = newDeletePolicy();
    }
    if (!this.extractPolicy) {
      this.extractPolicy = newExtractPolicy();
    }
    if (!this.recyclePolicy) {
      this.recyclePolicy = newRecyclePolicy();
    }
    if (!this.bwList) {
      this.bwList = {
        whiteLists: [
          {
            path: "",
            excludePaths: [],
          },
        ],
      };
    }
  }

  toJSON(): SyncPolicy {
    this.ensureDefaults();
    return {
      uploadPolicy: this.uploadPolicy,
      downloadPolicy: this.downloadPolicy,
      deletePolicy: this.deletePolicy,
      extractPolicy: this.extractPolicy,
      recyclePolicy: this.recyclePolicy,
      bwList: this.bwList,
    };
  }
}

// ContextSync defines the context synchronization configuration
export class ContextSync {
  contextId: string;
  path: string;
  policy?: SyncPolicy;
  /**
   * Beta feature flag to control whether session creation should wait for this context's
   * initial download to finish. If set to false, the SDK will not block create() on this context.
   * Defaults to undefined (treated as true for backward compatibility).
   */
  betaWaitForCompletion?: boolean;

  /**
   * Defines a full context sync configuration with optional policy overrides.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const policy = new SyncPolicyImpl({
   *     uploadPolicy: newUploadPolicy(),
   *     downloadPolicy: newDownloadPolicy(),
   *     recyclePolicy: newRecyclePolicy(),
   *   });
   *   const syncResult = await result.session.context.sync(
   *     'project-data',
   *     '/mnt/shared',
   *     'upload'
   *   );
   *   console.log('Context sync:', syncResult.success);
   *   await result.session.delete();
   * }
   * ```
   */
  constructor(
    contextId: string,
    path: string,
    policy?: SyncPolicy,
    betaWaitForCompletion?: boolean
  ) {
    if (policy) {
      validateSyncPolicy(policy);
    }
    this.contextId = contextId;
    this.path = path;
    this.policy = policy;
    this.betaWaitForCompletion = betaWaitForCompletion;
  }

  // WithPolicy sets the policy and returns the context sync for chaining
  withPolicy(policy: SyncPolicy): ContextSync {
    validateSyncPolicy(policy);
    this.policy = policy;
    return this;
  }

  withBetaWaitForCompletion(wait: boolean): ContextSync {
    this.betaWaitForCompletion = wait;
    return this;
  }
}

// NewUploadPolicy creates a new upload policy with default values
export function newUploadPolicy(options?: Partial<UploadPolicy>): UploadPolicy {
  const policy: UploadPolicy = {
    autoUpload: options?.autoUpload ?? true,
    uploadStrategy:
      options?.uploadStrategy ?? UploadStrategy.UploadBeforeResourceRelease,
    uploadMode: options?.uploadMode ?? UploadMode.File,
  };
  if (options?.archiveExcludePaths && options.archiveExcludePaths.length > 0) {
    policy.archiveExcludePaths = options.archiveExcludePaths;
  }
  return policy;
}

// NewDownloadPolicy creates a new download policy with default values
export function newDownloadPolicy(): DownloadPolicy {
  return {
    autoDownload: true,
    downloadStrategy: DownloadStrategy.DownloadAsync,
  };
}

// NewDeletePolicy creates a new delete policy with default values
export function newDeletePolicy(): DeletePolicy {
  return {
    syncLocalFile: true,
  };
}

// NewExtractPolicy creates a new extract policy with default values
export function newExtractPolicy(): ExtractPolicy {
  return {
    extract: true,
    deleteSrcFile: true,
    extractToCurrentFolder: false,
  };
}

// NewRecyclePolicy creates a new recycle policy with default values
export function newRecyclePolicy(): RecyclePolicy {
  return {
    lifecycle: Lifecycle.Lifecycle_Forever,
    paths: [""],
  };
}

// NewMappingPolicy creates a new mapping policy with default values
export function newMappingPolicy(): MappingPolicy {
  return {
    path: "",
  };
}

// NewSyncPolicy creates a new sync policy with default values
export function newSyncPolicy(): SyncPolicy {
  return {
    uploadPolicy: newUploadPolicy(),
    downloadPolicy: newDownloadPolicy(),
    deletePolicy: newDeletePolicy(),
    extractPolicy: newExtractPolicy(),
    recyclePolicy: newRecyclePolicy(),
    bwList: {
      whiteLists: [
        {
          path: "",
          excludePaths: [],
        },
      ],
    },
  };
}

// isValidLifecycle checks if the given lifecycle value is valid
function isValidLifecycle(lifecycle: Lifecycle): boolean {
  return Object.values(Lifecycle).includes(lifecycle);
}

// isValidUploadMode checks if the given uploadMode value is valid
function isValidUploadMode(uploadMode: UploadMode): boolean {
  return uploadMode === UploadMode.File || uploadMode === UploadMode.Archive;
}

export function validateSyncPolicy(policy?: SyncPolicy): void {
  if (policy) {
    // If policy is NOT an instance of SyncPolicyImpl (which already validated keys), validate keys
    // This catches POJOs passed directly to ContextSync
    if (!(policy instanceof SyncPolicyImpl)) {
      validatePolicyKeys(policy);
    }
  }

  if (policy?.bwList?.whiteLists) {
    for (const whitelist of policy.bwList.whiteLists) {
      WhiteListValidator.validate(whitelist);
    }
  }

  if (policy?.uploadPolicy?.uploadMode) {
    // Validate uploadMode value
    if (!isValidUploadMode(policy.uploadPolicy.uploadMode)) {
      throw new Error(
        `Invalid uploadMode value: ${policy.uploadPolicy.uploadMode}. ` +
          `Valid values are: ${UploadMode.File}, ${UploadMode.Archive}`
      );
    }
  }

  if (policy?.recyclePolicy) {
    // Validate lifecycle value
    if (!isValidLifecycle(policy.recyclePolicy.lifecycle)) {
      const validValues = Object.values(Lifecycle).join(", ");
      throw new Error(
        `Invalid lifecycle value: ${policy.recyclePolicy.lifecycle}. ` +
          `Valid values are: ${validValues}`
      );
    }

    // Validate paths don't contain wildcard patterns
    if (policy.recyclePolicy.paths) {
      for (const path of policy.recyclePolicy.paths) {
        if (path && path.trim() !== "") {
          // Create a temporary WhiteList object for validation
          const tempWhiteList: WhiteList = { path: path };
          WhiteListValidator.validate(tempWhiteList);
        }
      }
    }
  }
}

// NewSyncPolicyWithDefaults creates a new sync policy with partial parameters and fills defaults
export function newSyncPolicyWithDefaults(
  policy?: Partial<SyncPolicy>
): SyncPolicy {
  return new SyncPolicyImpl(policy).toJSON();
}

// NewContextSync creates a new context sync configuration
export function newContextSync(
  contextId: string,
  path: string,
  policy?: SyncPolicy
): ContextSync {
  if (policy) {
    validateSyncPolicy(policy);
  }
  return new ContextSync(contextId, path, policy);
}
