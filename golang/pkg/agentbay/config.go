package agentbay

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/joho/godotenv"
)

// Config stores SDK configuration. Endpoint is no longer a user-supplied input —
// it is derived from RegionID via regionEndpointMap. The field is kept on the
// struct as the resolved output (used by AgentBay to initialize the OpenAPI client),
// but any value the caller sets in a struct literal is overwritten by loadConfig.
type Config struct {
	Endpoint  string `json:"endpoint"`
	TimeoutMs int    `json:"timeout_ms"`
	RegionID  string `json:"region_id"`
}

// regionEndpointMap maps a supported region to its unit-service endpoint.
// Pre-release endpoints are obtained by prefixing the region with "pre-".
var regionEndpointMap = map[string]string{
	"cn-hangzhou":    "agentbay.cn-hangzhou.aliyuncs.com",
	"ap-southeast-1": "agentbay.ap-southeast-1.aliyuncs.com",
	"us-east-1":      "agentbay.us-east-1.aliyuncs.com",
}

const (
	defaultRegion = "cn-hangzhou"
	prePrefix     = "pre-"
)

// supportedRegions returns the list of supported regions, used in error messages.
func supportedRegions() string {
	keys := make([]string, 0, len(regionEndpointMap))
	for k := range regionEndpointMap {
		keys = append(keys, k)
	}
	// Stable order for deterministic error messages.
	// (No need for sort: we want a fixed canonical order.)
	canonical := []string{"cn-hangzhou", "ap-southeast-1", "us-east-1"}
	out := make([]string, 0, len(canonical))
	for _, k := range canonical {
		if _, ok := regionEndpointMap[k]; ok {
			out = append(out, k)
		}
	}
	// Append any region not in the canonical order (forward-compat).
	for _, k := range keys {
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

// invalidRegionError builds a user-facing error message for an unknown region.
func invalidRegionError(regionID string) error {
	return fmt.Errorf(
		"Invalid region_id '%s'. Supported regions: %s. "+
			"For pre-release, use 'pre-' prefix (e.g., 'pre-cn-hangzhou').",
		regionID, supportedRegions(),
	)
}

// resolveEndpoint resolves (actualRegion, endpoint) from a user-supplied region_id.
// Empty region falls back to the default. A "pre-" prefix selects the pre-release
// endpoint and is stripped from the returned region. Any region not in the
// supported mapping returns an error.
func resolveEndpoint(regionID string) (string, string, error) {
	id := regionID
	if id == "" {
		id = defaultRegion
	}

	if strings.HasPrefix(id, prePrefix) {
		actual := strings.TrimPrefix(id, prePrefix)
		if _, ok := regionEndpointMap[actual]; !ok {
			return "", "", invalidRegionError(id)
		}
		return actual, fmt.Sprintf("agentbay-pre.%s.aliyuncs.com", actual), nil
	}

	endpoint, ok := regionEndpointMap[id]
	if !ok {
		return "", "", invalidRegionError(id)
	}
	return id, endpoint, nil
}

// defaultConfig returns the default configuration
func defaultConfig() Config {
	return Config{
		Endpoint:  regionEndpointMap[defaultRegion],
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
// The SDK uses the following precedence order for region_id (highest to lowest):
// 1. Explicitly passed configuration in code.
// 2. Environment variable AGENTBAY_REGION_ID.
// 3. .env file (searched upward from current directory).
// 4. Default region (cn-hangzhou).
//
// Endpoint is always derived from the resolved region — it is not a user input.
// If the caller sets cfg.Endpoint in a struct literal it is silently overwritten
// (with a warning logged); use cfg.RegionID instead.
//
// Args:
//
//	cfg: Configuration object (if provided, skips env loading)
//	customEnvPath: Custom path to .env file (empty string means search upward)
func loadConfig(cfg *Config, customEnvPath string) Config {
	config := defaultConfig()

	if cfg != nil {
		// If config is explicitly provided, do NOT load env/.env.
		// Fill missing/zero fields with defaults, but preserve explicit values.
		if cfg.TimeoutMs > 0 {
			config.TimeoutMs = cfg.TimeoutMs
		}
		if cfg.RegionID != "" {
			config.RegionID = cfg.RegionID
		}
		if cfg.Endpoint != "" {
			LogWarn(fmt.Sprintf(
				"Config.Endpoint=%q is ignored; endpoint is derived from RegionID. "+
					"Set RegionID instead.", cfg.Endpoint))
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
			config.RegionID = regionID
		}
	}

	// Always derive endpoint from region_id; normalize region by stripping pre- prefix.
	actualRegion, endpoint, err := resolveEndpoint(config.RegionID)
	if err != nil {
		// Surface the validation error by panicking; loadConfig has no error
		// return to preserve API compatibility, and an invalid region is a
		// programmer error that should fail loud at construction time.
		panic(err)
	}
	config.RegionID = actualRegion
	config.Endpoint = endpoint
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
