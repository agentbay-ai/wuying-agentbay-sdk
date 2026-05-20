// ci-stable
package integration

import (
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestRegionIDIntegration tests region_id functionality end-to-end
func TestRegionIDIntegration(t *testing.T) {
	// Skip if no API key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	t.Run("CreateAgentBayWithRegionID", func(t *testing.T) {
		// Test creating AgentBay client with region_id in config
		config := &agentbay.Config{
			TimeoutMs: 60000,
			RegionID:  "cn-hangzhou",
		}
		client, err := agentbay.NewAgentBay(apiKey, agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is set
		if client.GetRegionID() != "cn-hangzhou" {
			t.Errorf("Expected RegionID to be 'cn-hangzhou', got '%s'", client.GetRegionID())
		}
	})

	t.Run("CreateSessionWithRegionID", func(t *testing.T) {
		// Test session creation with region_id in config
		config := &agentbay.Config{
			TimeoutMs: 60000,
			RegionID:  "cn-hangzhou",
		}
		client, err := agentbay.NewAgentBay(apiKey, agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Create session with default parameters
		params := agentbay.NewCreateSessionParams()
		result, err := client.Create(params)
		if err != nil {
			t.Fatalf("Failed to create session: %v", err)
		}

		if !result.Success {
			t.Fatalf("Session creation failed")
		}

		if result.Session == nil {
			t.Fatalf("Session is nil")
		}

		// Clean up
		defer func() {
			_, deleteErr := result.Session.Delete()
			if deleteErr != nil {
				t.Logf("Warning: Failed to delete session: %v", deleteErr)
			}
		}()

		t.Logf("✅ Successfully created session %s with region_id cn-hangzhou", result.Session.SessionID)
	})

	t.Run("CreateContextWithRegionID", func(t *testing.T) {
		// Test context creation with region_id in config
		config := &agentbay.Config{
			TimeoutMs: 60000,
			RegionID:  "cn-hangzhou",
		}
		client, err := agentbay.NewAgentBay(apiKey, agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Create context
		contextName := "test-context-with-region-id"
		contextResult, err := client.Context.Get(contextName, true)
		if err != nil {
			t.Fatalf("Failed to create context: %v", err)
		}

		if !contextResult.Success {
			t.Fatalf("Context creation failed: %s", contextResult.ErrorMessage)
		}

		if contextResult.Context == nil {
			t.Fatalf("Context is nil")
		}

		// Clean up
		defer func() {
			_, deleteErr := client.Context.Delete(contextResult.Context)
			if deleteErr != nil {
				t.Logf("Warning: Failed to delete context: %v", deleteErr)
			}
		}()

		t.Logf("✅ Successfully created context %s with region_id cn-hangzhou", contextResult.Context.ID)
	})

	t.Run("GetContextWithoutCreate", func(t *testing.T) {
		// Test context get without create (should not pass LoginRegionId)
		config := &agentbay.Config{
			TimeoutMs: 60000,
			RegionID:  "cn-hangzhou",
		}
		client, err := agentbay.NewAgentBay(apiKey, agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Try to get non-existent context without create
		contextName := "non-existent-context"
		contextResult, err := client.Context.Get(contextName, false)
		if err != nil {
			t.Fatalf("Unexpected error when getting non-existent context: %v", err)
		}

		// Should return success=false for non-existent context
		if contextResult.Success {
			t.Errorf("Expected context get to fail for non-existent context, but it succeeded")
		}

		t.Logf("✅ Context get without create behaved correctly for non-existent context")
	})
}
