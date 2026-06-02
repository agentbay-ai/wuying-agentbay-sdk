import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

interface Config {
  endpoint: string;
  timeout_ms: number;
  region_id?: string;
}

/**
 * User-supplied configuration. The preferred input is `region_id`; the SDK
 * derives the endpoint from it via direct pattern substitution. `endpoint`
 * is retained as a deprecated fallback: when `region_id` is not set the
 * value of `endpoint` is used as-is. When both are set, `region_id` wins.
 */
type ConfigOptions = {
  timeout_ms?: number;
  region_id?: string;
  /**
   * @deprecated Since 0.22.0. Pass `region_id` instead. The value is honored
   * only as a fallback when `region_id` is not set (in code or via
   * AGENTBAY_REGION_ID). Either form emits a deprecation warning. Will be
   * removed in a future major version.
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
 * Precedence (highest to lowest), evaluated independently for region_id and
 * the deprecated endpoint fallback:
 *  1. Explicit customConfig.region_id in code.
 *  2. Explicit customConfig.endpoint in code (deprecated fallback).
 *  3. AGENTBAY_REGION_ID environment variable.
 *  4. AGENTBAY_ENDPOINT environment variable (deprecated fallback).
 *  5. Default region (cn-hangzhou).
 *
 * When region_id is resolved at any level, the endpoint is derived from it
 * via the pattern. The endpoint fallback only kicks in when no region_id is
 * found at any level, and it bypasses the pattern (the value is used as-is).
 */
function loadConfig(
  customConfig?: ConfigOptions,
  customEnvPath?: string
): Config {
  const config = defaultConfig();
  let explicitRegion: string | undefined;
  let explicitEndpoint: string | undefined;

  if (customConfig) {
    // If custom config is provided, do NOT load env/.env.
    if (
      typeof customConfig.timeout_ms === "number" &&
      Number.isFinite(customConfig.timeout_ms) &&
      customConfig.timeout_ms > 0
    ) {
      config.timeout_ms = customConfig.timeout_ms;
    }

    if (
      typeof customConfig.region_id === "string" &&
      customConfig.region_id.length > 0
    ) {
      explicitRegion = customConfig.region_id;
    }

    if (
      typeof customConfig.endpoint === "string" &&
      customConfig.endpoint.length > 0
    ) {
      explicitEndpoint = customConfig.endpoint;
    }

    if (explicitRegion && explicitEndpoint) {
      console.warn(
        `[DeprecationWarning] Config region_id=${JSON.stringify(
          explicitRegion
        )} and endpoint=${JSON.stringify(
          explicitEndpoint
        )}: both set; endpoint is ignored because region_id takes precedence.`
      );
      explicitEndpoint = undefined;
    } else if (explicitEndpoint) {
      console.warn(
        `[DeprecationWarning] Config endpoint=${JSON.stringify(
          explicitEndpoint
        )} is deprecated; pass region_id instead. The value is used as a fallback when region_id is not set, and will be removed in a future major version.`
      );
    }
  } else {
    // Load .env file with improved search first
    try {
      loadDotEnvWithFallback(customEnvPath);
    } catch (error) {
      // Silently fail - .env loading is optional
    }

    if (process.env.AGENTBAY_TIMEOUT_MS) {
      const timeout = parseInt(process.env.AGENTBAY_TIMEOUT_MS, 10);
      if (!isNaN(timeout) && timeout > 0) {
        config.timeout_ms = timeout;
      }
    }

    if (process.env.AGENTBAY_REGION_ID) {
      explicitRegion = process.env.AGENTBAY_REGION_ID;
    }
    if (process.env.AGENTBAY_ENDPOINT) {
      const envEndpoint = process.env.AGENTBAY_ENDPOINT;
      if (explicitRegion) {
        console.warn(
          `[DeprecationWarning] AGENTBAY_ENDPOINT=${JSON.stringify(
            envEndpoint
          )} is deprecated and ignored because AGENTBAY_REGION_ID is also set. Unset AGENTBAY_ENDPOINT to silence this warning.`
        );
      } else {
        console.warn(
          `[DeprecationWarning] AGENTBAY_ENDPOINT=${JSON.stringify(
            envEndpoint
          )} is deprecated; set AGENTBAY_REGION_ID instead. The value is used as a fallback and will be removed in a future major version.`
        );
        explicitEndpoint = envEndpoint;
      }
    }
  }

  if (explicitRegion) {
    const resolved = resolveEndpoint(explicitRegion);
    config.region_id = resolved.region;
    config.endpoint = resolved.endpoint;
  } else if (explicitEndpoint) {
    // Deprecated fallback: use the user-supplied endpoint verbatim.
    // region_id is left at its default so downstream code that reads it
    // (e.g. for telemetry) still has a non-empty value.
    config.endpoint = explicitEndpoint;
  } else {
    const resolved = resolveEndpoint(config.region_id);
    config.region_id = resolved.region;
    config.endpoint = resolved.endpoint;
  }
  return config;
}

export { Config, loadConfig, loadDotEnvWithFallback, resolveEndpoint };
export type { ConfigOptions };
