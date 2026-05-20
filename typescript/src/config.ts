import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

interface Config {
  endpoint: string;
  timeout_ms: number;
  region_id?: string;
}

/**
 * User-supplied configuration. `endpoint` is no longer a user input — it is
 * derived from `region_id` via the mapping below.
 */
type ConfigOptions = {
  timeout_ms?: number;
  region_id?: string;
  /**
   * @deprecated Since 0.21.0. Endpoint is derived from `region_id` and any
   * value passed here is ignored (a deprecation warning is logged to
   * console.warn). Pass `region_id` instead. Will be removed in a future
   * major version.
   */
  endpoint?: string;
};

/**
 * Endpoint is no longer user-configurable; it is derived from region_id by
 * direct pattern substitution for production regions, and by a hardcoded
 * lookup table for pre-release regions (since pre-release hostnames don't
 * follow a single pattern: e.g. cn-hangzhou uses "agentbay-pre.*" while
 * ap-southeast-1 uses "wuyingai-pre.*").
 */
const DEFAULT_REGION = "cn-hangzhou";
const PRE_PREFIX = "pre-";

/**
 * Known production regions. Unknown entries are NOT rejected — they fall
 * through to the default "agentbay.{region}.aliyuncs.com" pattern with a
 * console.warn line, so newly onboarded regions work without an SDK
 * upgrade while typos still surface a hint before the request actually fires.
 */
const KNOWN_REGIONS: readonly string[] = [
  "cn-hangzhou",
  "ap-southeast-1",
  "us-east-1",
];

/**
 * Hardcoded mapping for pre-release regions (after stripping the "pre-" prefix).
 * Unknown entries fall back to "agentbay-pre.{actual}.aliyuncs.com" with a
 * console.warn line, since we genuinely don't know which pre-release naming
 * convention a new region will adopt.
 */
const PRE_REGION_ENDPOINT_MAP: { readonly [region: string]: string } = {
  "cn-hangzhou": "agentbay-pre.cn-hangzhou.aliyuncs.com",
  "ap-southeast-1": "wuyingai-pre.ap-southeast-1.aliyuncs.com",
};

/**
 * Resolve (actualRegion, endpoint) from a user-supplied region_id.
 *
 * Empty/undefined region falls back to the default. A "pre-" prefix selects
 * the pre-release endpoint and is stripped from the returned region:
 *  - Known pre regions use the hardcoded entry in PRE_REGION_ENDPOINT_MAP.
 *  - Unknown pre regions log a warning and fall back to the default
 *    "agentbay-pre.{actual}.aliyuncs.com" pattern.
 *
 * Non-pre regions are composed by direct pattern substitution. No whitelist
 * validation — any non-empty region_id is accepted so newly onboarded
 * regions work without an SDK upgrade.
 */
function resolveEndpoint(regionId?: string): {
  region: string;
  endpoint: string;
} {
  const id = regionId && regionId.length > 0 ? regionId : DEFAULT_REGION;

  if (id.startsWith(PRE_PREFIX)) {
    const actual = id.slice(PRE_PREFIX.length);
    if (actual in PRE_REGION_ENDPOINT_MAP) {
      return { region: actual, endpoint: PRE_REGION_ENDPOINT_MAP[actual] };
    }
    console.warn(
      `Unknown pre-release region 'pre-${actual}'. Falling back to ` +
        `'agentbay-pre.${actual}.aliyuncs.com'; the request may fail at DNS ` +
        `resolution if the host does not exist. Known pre regions: ` +
        `${Object.keys(PRE_REGION_ENDPOINT_MAP).join(", ")}.`
    );
    return { region: actual, endpoint: `agentbay-pre.${actual}.aliyuncs.com` };
  }

  if (!KNOWN_REGIONS.includes(id)) {
    console.warn(
      `Unknown region '${id}'. Falling back to 'agentbay.${id}.aliyuncs.com'; ` +
        `the request may fail at DNS resolution if the host does not exist. ` +
        `Known regions: ${KNOWN_REGIONS.join(", ")}.`
    );
  }
  return { region: id, endpoint: `agentbay.${id}.aliyuncs.com` };
}

/**
 * Browser data path constant
 */
const BROWSER_DATA_PATH = "/tmp/agentbay_browser";

/**
 * Browser fingerprint persistent path constant
 */
const BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint";

/**
 * Browser recording path constant
 */
export const BROWSER_RECORD_PATH = "/home/wuying/record";

/**
 * Returns the default configuration
 */
function defaultConfig(): Config {
  return {
    endpoint: resolveEndpoint(DEFAULT_REGION).endpoint,
    timeout_ms: 60000,
    region_id: DEFAULT_REGION,
  };
}

/**
 * Find .env file by searching upward from start_path.
 *
 * Search order:
 * 1. Current working directory
 * 2. Parent directories (up to root)
 * 3. Git repository root (if found)
 *
 * @param startPath Starting directory for search (defaults to current working directory)
 * @returns Path to .env file if found, null otherwise
 */
function findDotEnvFile(startPath?: string): string | null {
  const currentPath = startPath ? path.resolve(startPath) : process.cwd();
  let searchPath = currentPath;

  // Search upward until we reach root directory
  while (searchPath !== path.dirname(searchPath)) {
    const envFile = path.join(searchPath, ".env");
    if (fs.existsSync(envFile)) {
      return envFile;
    }

    // Check if this is a git repository root
    const gitDir = path.join(searchPath, ".git");
    if (fs.existsSync(gitDir)) {
      // Found git root, continue searching
    }

    searchPath = path.dirname(searchPath);
  }

  // Check root directory as well
  const rootEnv = path.join(searchPath, ".env");
  if (fs.existsSync(rootEnv)) {
    return rootEnv;
  }

  return null;
}

/**
 * Load .env file with improved search strategy.
 *
 * @param customEnvPath Custom path to .env file (optional)
 */
function loadDotEnvWithFallback(customEnvPath?: string): void {
  if (customEnvPath) {
    // Use custom path if provided
    if (fs.existsSync(customEnvPath)) {
      try {
        const envConfig = dotenv.parse(fs.readFileSync(customEnvPath));
        for (const k in envConfig) {
          // only load env variables that are not already set in process.env
          if (!process.env.hasOwnProperty(k)) {
            process.env[k] = envConfig[k];
          }
        }
        return;
      } catch (error) {
        // Silently fail - .env loading is optional
      }
    }
  }

  // Find .env file using upward search
  const envFile = findDotEnvFile();
  if (envFile) {
    try {
      const envConfig = dotenv.parse(fs.readFileSync(envFile));
      for (const k in envConfig) {
        // only load env variables that are not already set in process.env
        if (!process.env.hasOwnProperty(k)) {
          process.env[k] = envConfig[k];
        }
      }
    } catch (error) {
      // Silently fail - .env loading is optional
    }
  }
}

// Track if .env file has been loaded to avoid duplicate loading
let dotEnvLoaded = false;

// Auto-load .env file on module initialization
// This ensures environment variables are available before logger module is loaded
if (!dotEnvLoaded) {
  try {
    loadDotEnvWithFallback();
    dotEnvLoaded = true;
  } catch (error) {
    // Silently fail - .env loading is optional
  }
}

/**
 * The SDK uses the following precedence order for region_id (highest to lowest):
 * 1. Explicitly passed configuration in code.
 * 2. Environment variable AGENTBAY_REGION_ID.
 * 3. .env file.
 * 4. Default region (cn-hangzhou).
 *
 * Endpoint is always derived from the resolved region — it is not a user input.
 */
function loadConfig(
  customConfig?: ConfigOptions,
  customEnvPath?: string
): Config {
  // If custom config is provided, do NOT load env/.env.
  // Fill missing/empty fields with defaults, but preserve explicit values.
  if (customConfig) {
    const config = defaultConfig();

    // Treat non-positive numbers as "not provided" for timeout
    if (
      typeof customConfig.timeout_ms === "number" &&
      Number.isFinite(customConfig.timeout_ms) &&
      customConfig.timeout_ms > 0
    ) {
      config.timeout_ms = customConfig.timeout_ms;
    }

    // Empty string region_id is treated as "not provided" → default
    if (
      typeof customConfig.region_id === "string" &&
      customConfig.region_id.length > 0
    ) {
      config.region_id = customConfig.region_id;
    }

    // Backwards compat: warn when the deprecated `endpoint` option is set,
    // then ignore the value — endpoint is always derived from region_id.
    if (
      typeof customConfig.endpoint === "string" &&
      customConfig.endpoint.length > 0
    ) {
      console.warn(
        `[DeprecationWarning] Config endpoint=${JSON.stringify(
          customConfig.endpoint
        )} is ignored; endpoint is derived from region_id. Pass region_id instead.`
      );
    }

    const resolved = resolveEndpoint(config.region_id);
    config.region_id = resolved.region;
    config.endpoint = resolved.endpoint;
    return config;
  }

  // Create base config from default values
  const config = defaultConfig();

  // Load .env file with improved search first
  try {
    loadDotEnvWithFallback(customEnvPath);
  } catch (error) {
    // Silently fail - .env loading is optional
  }

  // Override with environment variables if they exist (highest priority)
  if (process.env.AGENTBAY_TIMEOUT_MS) {
    const timeout = parseInt(process.env.AGENTBAY_TIMEOUT_MS, 10);
    if (!isNaN(timeout) && timeout > 0) {
      config.timeout_ms = timeout;
    }
  }

  if (process.env.AGENTBAY_REGION_ID) {
    config.region_id = process.env.AGENTBAY_REGION_ID;
  }

  // Always derive endpoint from region_id; normalize region by stripping pre- prefix.
  const resolved = resolveEndpoint(config.region_id);
  config.region_id = resolved.region;
  config.endpoint = resolved.endpoint;
  return config;
}

export { Config, loadConfig, loadDotEnvWithFallback, resolveEndpoint };
export type { ConfigOptions };
