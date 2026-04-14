package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestRegionIDSupport tests region_id functionality in AgentBay client
func TestRegionIDSupport(t *testing.T) {
	t.Run("NewAgentBayWithRegionID", func(t *testing.T) {
		// Test creating AgentBay client with region_id in config
		config := &agentbay.Config{
			Endpoint:  "wuyingai.cn-shanghai.aliyuncs.com",
			TimeoutMs: 60000,
			RegionID:  "cn-hangzhou",
		}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is set correctly through config
		if client.GetRegionID() != "cn-hangzhou" {
			t.Errorf("Expected RegionID to be 'cn-hangzhou', got '%s'", client.GetRegionID())
		}

		// Verify other fields are set correctly
		if client.APIKey != "test-api-key" {
			t.Errorf("Expected APIKey to be 'test-api-key', got '%s'", client.APIKey)
		}

		if client.Context == nil {
			t.Error("Expected Context service to be initialized")
		}
	})

	t.Run("NewAgentBayWithPartialConfigFillsDefaults", func(t *testing.T) {
		// Only region_id is set; other values should be filled with defaults
		config := &agentbay.Config{
			RegionID: "cn-hangzhou",
		}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		if client.GetRegionID() != "cn-hangzhou" {
			t.Errorf("Expected RegionID to be 'cn-hangzhou', got '%s'", client.GetRegionID())
		}

		// Endpoint should fall back to default when not provided in config
		if client.Client == nil || client.Client.Endpoint == nil {
			t.Fatalf("Expected OpenAPI client endpoint to be initialized")
		}
		if *client.Client.Endpoint != "wuyingai.cn-shanghai.aliyuncs.com" {
			t.Errorf("Expected Endpoint to be 'wuyingai.cn-shanghai.aliyuncs.com', got '%s'", *client.Client.Endpoint)
		}
	})

	t.Run("NewAgentBayWithoutRegionID", func(t *testing.T) {
		// Clear AGENTBAY_REGION_ID env var to ensure isolation from local environment
		t.Setenv("AGENTBAY_REGION_ID", "")
		// Test creating AgentBay client without region_id
		client, err := agentbay.NewAgentBay("test-api-key")
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is empty when not provided
		if client.GetRegionID() != "" {
			t.Errorf("Expected RegionID to be empty, got '%s'", client.GetRegionID())
		}

		// Verify other fields are set correctly
		if client.APIKey != "test-api-key" {
			t.Errorf("Expected APIKey to be 'test-api-key', got '%s'", client.APIKey)
		}
	})

	t.Run("NewAgentBayWithMultipleOptions", func(t *testing.T) {
		// Test creating AgentBay client with multiple options including region_id
		config := &agentbay.Config{
			Endpoint:  "https://test.endpoint.com",
			TimeoutMs: 60000,
		}

		config.RegionID = "cn-hangzhou"
		client, err := agentbay.NewAgentBay("test-api-key",
			agentbay.WithConfig(config),
			agentbay.WithEnvFile(".env.test"))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is set correctly
		if client.GetRegionID() != "cn-hangzhou" {
			t.Errorf("Expected RegionID to be 'cn-hangzhou', got '%s'", client.GetRegionID())
		}

		// Verify API key is set correctly
		if client.APIKey != "test-api-key" {
			t.Errorf("Expected APIKey to be 'test-api-key', got '%s'", client.APIKey)
		}
	})

	t.Run("EmptyRegionID", func(t *testing.T) {
		// Clear AGENTBAY_REGION_ID env var to ensure isolation from local environment
		t.Setenv("AGENTBAY_REGION_ID", "")
		// Test creating AgentBay client with empty region_id in config
		config := &agentbay.Config{
			Endpoint:  "wuyingai.cn-shanghai.aliyuncs.com",
			TimeoutMs: 60000,
			RegionID:  "",
		}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is empty
		if client.GetRegionID() != "" {
			t.Errorf("Expected RegionID to be empty, got '%s'", client.GetRegionID())
		}
	})
}
