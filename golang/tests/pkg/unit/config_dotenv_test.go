package agentbay_test

import (
	"os"
	"testing"
)

func TestEnhancedDotEnvLoading(t *testing.T) {
	// Save original environment
	originalEnv := make(map[string]string)
	envVars := []string{"AGENTBAY_REGION_ID", "AGENTBAY_TIMEOUT_MS"}
	for _, key := range envVars {
		if val, exists := os.LookupEnv(key); exists {
			originalEnv[key] = val
		}
		os.Unsetenv(key)
	}

	// Restore environment after tests
	defer func() {
		for _, key := range envVars {
			os.Unsetenv(key)
		}
		for key, val := range originalEnv {
			os.Setenv(key, val)
		}
	}()

	// Tests for private functions (findDotEnvFile, loadDotEnvWithFallback, etc.) removed
	// These are now private and tested through public APIs like NewAgentBay()
	// The functionality is covered by integration tests
}
