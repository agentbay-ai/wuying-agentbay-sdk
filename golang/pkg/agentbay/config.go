package agentbay

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/joho/godotenv"
)

// Config stores SDK configuration. The preferred input is RegionID; the SDK
// derives the endpoint from it via direct pattern substitution. Endpoint is
// retained as a deprecated fallback: when RegionID is not set the value of
// Endpoint is used as-is. When both are set, RegionID wins and Endpoint is
// ignored. Either form emits a deprecation warning via Deprecated(...).
type Config struct {
	// Deprecated: pass RegionID instead. When RegionID is unset (in code or
	// via AGENTBAY_REGION_ID), Endpoint is honored as a fallback so legacy
	// callers keep working. Will be removed in a future major version.
	Endpoint  string `json:"endpoint"`
	TimeoutMs int    `json:"timeout_ms"`
	RegionID  string `json:"region_id"`
}

const (
	defaultRegion = "cn-hangzhou"
	prePrefix     = "pre-"
)

// knownRegions lists production regions that resolve silently. Unknown
// entries are NOT rejected — they fall through to the default
// "agentbay.{region}.aliyuncs.com" pattern with a warning logged.
var knownRegions = []string{"cn-hangzhou", "ap-southeast-1", "us-east-1"}

// isKnownRegion reports whether region is in the production whitelist.
func isKnownRegion(region string) bool {
	for _, k := range knownRegions {
		if k == region {
			return true
		}
	}
	return false
}

// preRegionEndpointMap is the hardcoded mapping for pre-release regions
// (after stripping the "pre-" prefix). Pre-release hostnames don't follow a
// single pattern: cn-hangzhou uses "agentbay-pre.*" while ap-southeast-1
// uses "wuyingai-pre.*". Unknown entries fall back to
// "agentbay-pre.{actual}.aliyuncs.com" with a warning logged.
var preRegionEndpointMap = map[string]string{
	"cn-hangzhou":    "agentbay-pre.cn-hangzhou.aliyuncs.com",
	"ap-southeast-1": "wuyingai-pre.ap-southeast-1.aliyuncs.com",
}

// preRegionKeys returns the supported pre-region keys in a stable order, used
// for the unknown-region warning message.
func preRegionKeys() string {
	canonical := []string{"cn-hangzhou", "ap-southeast-1"}
	out := make([]string, 0, len(canonical))
	for _, k := range canonical {
		if _, ok := preRegionEndpointMap[k]; ok {
			out = append(out, k)
		}
	}
	for k := range preRegionEndpointMap {
		found := false
		for _, c := range canonical {
			if c == k {
				found = true
				break
			}
		}
		if !found {
			out = append(out, k)
		}
	}
	return strings.Join(out, ", ")
}

// resolveEndpoint derives (actualRegion, endpoint) from a user-supplied
// region_id. Empty region falls back to the default. A "pre-" prefix selects
// the pre-release host and is stripped from the returned region:
//   - Known pre regions use the hardcoded entry in preRegionEndpointMap.
//   - Unknown pre regions log a warning and fall back to the default
//     "agentbay-pre.{actual}.aliyuncs.com" pattern.
//
// Non-pre regions are composed by direct pattern substitution. No whitelist
// validation — any non-empty region_id is accepted so newly onboarded regions
// work without an SDK upgrade.
func resolveEndpoint(regionID string) (string, string) {
	id := regionID
	if id == "" {
		id = defaultRegion
	}

	if strings.HasPrefix(id, prePrefix) {
		actual := strings.TrimPrefix(id, prePrefix)
		if endpoint, ok := preRegionEndpointMap[actual]; ok {
			return actual, endpoint
		}
		LogWarn(fmt.Sprintf(
			"Unknown pre-release region 'pre-%s'. Falling back to "+
				"'agentbay-pre.%s.aliyuncs.com'; the request may fail at DNS "+
				"resolution if the host does not exist. Known pre regions: %s.",
			actual, actual, preRegionKeys()))
		return actual, fmt.Sprintf("agentbay-pre.%s.aliyuncs.com", actual)
	}

	if !isKnownRegion(id) {
		LogWarn(fmt.Sprintf(
			"Unknown region '%s'. Falling back to 'agentbay.%s.aliyuncs.com'; "+
				"the request may fail at DNS resolution if the host does not exist. "+
				"Known regions: %s.",
			id, id, strings.Join(knownRegions, ", ")))
	}
	return id, fmt.Sprintf("agentbay.%s.aliyuncs.com", id)
}

// defaultConfig returns the default configuration
func defaultConfig() Config {
	_, endpoint := resolveEndpoint(defaultRegion)
	return Config{
		Endpoint:  endpoint,
		TimeoutMs: 60000,
		RegionID:  defaultRegion,
	}
}

// findDotEnvFile searches for .env file upward from startPath.
// Search order:
// 1. Current working directory
// 2. Parent directories (up to root)
// 3. Git repository root (if found)
//
// Args:
//
//	startPath: Starting directory for search (empty string means current directory)
//
// Returns:
//
//	Path to .env file if found, empty string otherwise
func findDotEnvFile(startPath string) string {
	if startPath == "" {
		workingDir, err := os.Getwd()
		if err != nil {
			LogWarn(fmt.Sprintf("Failed to get current working directory: %v", err))
			return ""
		}
		startPath = workingDir
	}

	currentPath, err := filepath.Abs(startPath)
	if err != nil {
		LogWarn(fmt.Sprintf("Failed to resolve absolute path: %v", err))
		return ""
	}

	// Search upward until we reach root directory
	for {
		envFile := filepath.Join(currentPath, ".env")
		if _, err := os.Stat(envFile); err == nil {
			LogDebug(fmt.Sprintf("Found .env file at: %s", envFile))
			return envFile
		}

		// Check if this is a git repository root
		gitDir := filepath.Join(currentPath, ".git")
		if _, err := os.Stat(gitDir); err == nil {
			LogDebug(fmt.Sprintf("Found git repository root at: %s", currentPath))
		}

		parentPath := filepath.Dir(currentPath)
		if parentPath == currentPath {
			// Reached root directory
			break
		}
		currentPath = parentPath
	}

	return ""
}

// loadDotEnvWithFallback loads .env file with improved search strategy.
//
// Args:
//
//	customEnvPath: Custom path to .env file (empty string means search upward)
func loadDotEnvWithFallback(customEnvPath string) {
	if customEnvPath != "" {
		// Use custom path if provided
		if _, err := os.Stat(customEnvPath); err == nil {
			err = godotenv.Load(customEnvPath)
			if err != nil {
				LogWarn(fmt.Sprintf("Failed to load custom .env file %s: %v", customEnvPath, err))
			} else {
				LogDebug(fmt.Sprintf("Loaded custom .env file from: %s", customEnvPath))
				return
			}
		} else {
			LogWarn(fmt.Sprintf("Custom .env file not found: %s", customEnvPath))
		}
	}

	// Find .env file using upward search
	envFile := findDotEnvFile("")
	if envFile != "" {
		err := godotenv.Load(envFile)
		if err != nil {
			LogWarn(fmt.Sprintf("Failed to load .env file %s: %v", envFile, err))
		} else {
			LogDebug(fmt.Sprintf("Loaded .env file from: %s", envFile))
		}
	} else {
		LogDebug("No .env file found in current directory or parent directories")
	}
}

// loadConfig loads the configuration from file or environment variables.
// Precedence (highest to lowest), evaluated independently for region_id and
// the deprecated endpoint fallback:
//  1. Explicit cfg.RegionID in code.
//  2. Explicit cfg.Endpoint in code (deprecated fallback).
//  3. AGENTBAY_REGION_ID environment variable.
//  4. AGENTBAY_ENDPOINT environment variable (deprecated fallback).
//  5. Default region (cn-hangzhou).
//
// When region_id is resolved at any level, the endpoint is derived from it via
// the pattern. The endpoint fallback only kicks in when no region_id is found
// at any level, and it bypasses the pattern (the value is used as-is).
//
// Args:
//
//	cfg: Configuration object (if provided, skips env loading)
//	customEnvPath: Custom path to .env file (empty string means search upward)
func loadConfig(cfg *Config, customEnvPath string) Config {
	config := defaultConfig()
	var explicitRegion, explicitEndpoint string

	if cfg != nil {
		// If config is explicitly provided, do NOT load env/.env.
		if cfg.TimeoutMs > 0 {
			config.TimeoutMs = cfg.TimeoutMs
		}
		if cfg.RegionID != "" {
			explicitRegion = cfg.RegionID
		}
		if cfg.Endpoint != "" {
			explicitEndpoint = cfg.Endpoint
		}
		// Both set in code: RegionID wins, Endpoint ignored with deprecation warning.
		if explicitRegion != "" && explicitEndpoint != "" {
			Deprecated(
				fmt.Sprintf(
					"Config.Endpoint=%q is ignored because Config.RegionID=%q is also set.",
					explicitEndpoint, explicitRegion),
				"Config.RegionID",
				"0.22.0",
			)
			explicitEndpoint = ""
		} else if explicitEndpoint != "" {
			Deprecated(
				fmt.Sprintf(
					"Config.Endpoint=%q is deprecated; pass RegionID instead. "+
						"The value is used as a fallback when RegionID is not set.",
					explicitEndpoint),
				"Config.RegionID",
				"0.22.0",
			)
		}
	} else {
		// Load .env file with improved search
		loadDotEnvWithFallback(customEnvPath)

		if timeoutMS := os.Getenv("AGENTBAY_TIMEOUT_MS"); timeoutMS != "" {
			_, err := fmt.Sscanf(timeoutMS, "%d", &config.TimeoutMs)
			if err != nil {
				// Warning: Failed to parse AGENTBAY_TIMEOUT_MS as integer, using default
			}
		}
		if regionID := os.Getenv("AGENTBAY_REGION_ID"); regionID != "" {
			explicitRegion = regionID
		}
		if envEndpoint := os.Getenv("AGENTBAY_ENDPOINT"); envEndpoint != "" {
			if explicitRegion != "" {
				LogWarn(fmt.Sprintf(
					"AGENTBAY_ENDPOINT=%q is deprecated and ignored because "+
						"AGENTBAY_REGION_ID is also set. Unset AGENTBAY_ENDPOINT "+
						"to silence this warning.", envEndpoint))
			} else {
				LogWarn(fmt.Sprintf(
					"AGENTBAY_ENDPOINT=%q is deprecated; set AGENTBAY_REGION_ID "+
						"instead. The value is used as a fallback and will be "+
						"removed in a future major version.", envEndpoint))
				explicitEndpoint = envEndpoint
			}
		}
	}

	if explicitRegion != "" {
		actualRegion, endpoint := resolveEndpoint(explicitRegion)
		config.RegionID = actualRegion
		config.Endpoint = endpoint
	} else if explicitEndpoint != "" {
		// Deprecated fallback: use the user-supplied endpoint verbatim.
		// RegionID is left at its default so downstream code that reads it
		// (e.g. for telemetry) still has a non-empty value.
		config.Endpoint = explicitEndpoint
	} else {
		actualRegion, endpoint := resolveEndpoint(config.RegionID)
		config.RegionID = actualRegion
		config.Endpoint = endpoint
	}
	return config
}

// loadConfigCompat provides backward compatibility for existing code
func loadConfigCompat(cfg *Config) Config {
	return loadConfig(cfg, "")
}

// BrowserRecordPath is the path constant for browser recording data.
// This path is used when syncing browser recording context during session deletion.
const BrowserRecordPath = "/home/wuying/record"

// MobileInfoDefaultPath is path constant for internal create context
const MobileInfoDefaultPath = "/data/agentbay_mobile_info"

// MobileInfoSubPath is mobile dev info sub path constant when append to user's context path
const MobileInfoSubPath = "/agentbay_mobile_info/"

// MobileInfoFileName is mobile dev info file name constant
const MobileInfoFileName = "dev_info.json"

// configManager implementation for backward compatibility
type configManager struct{}

// loadConfig implements the ConfigInterface for backward compatibility
func (c *configManager) loadConfig(cfg *Config) Config {
	return loadConfigCompat(cfg)
}

// defaultConfig implements the ConfigInterface
func (c *configManager) defaultConfig() Config {
	return defaultConfig()
}

// newConfigManager creates a new configManager instance
func newConfigManager() *configManager {
	return &configManager{}
}
