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
};

/**
 * Endpoint is no longer user-configurable; it is derived from region_id by
 * direct pattern substitution. The "pre-" prefix selects the pre-release host
 * (e.g. "pre-cn-hangzhou" → agentbay-pre.cn-hangzhou.aliyuncs.com).
 */
const DEFAULT_REGION = "cn-hangzhou";
const PRE_PREFIX = "pre-";

/**
 * Resolve (actualRegion, endpoint) from a user-supplied region_id.
 *
 * Empty/undefined region falls back to the default. A "pre-" prefix selects
 * the pre-release endpoint and is stripped from the returned region. No
 * whitelist validation — any non-empty region_id is accepted so newly
 * onboarded regions work without an SDK upgrade.
 */
function resolveEndpoint(regionId?: string): {
  region: string;
  endpoint: string;
} {
  const id = regionId && regionId.length > 0 ? regionId : DEFAULT_REGION;

  if (id.startsWith(PRE_PREFIX)) {
    const actual = id.slice(PRE_PREFIX.length);
    return { region: actual, endpoint: `agentbay-pre.${actual}.aliyuncs.com` };
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
