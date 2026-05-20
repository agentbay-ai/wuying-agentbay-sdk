package agentbay_test

import (
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestRegionIDSupport tests region_id functionality in AgentBay client
func TestRegionIDSupport(t *testing.T) {
	t.Run("NewAgentBayWithRegionID", func(t *testing.T) {
		// Test creating AgentBay client with region_id in config.
		// Endpoint set on the input struct is silently ignored (and warned).
		config := &agentbay.Config{
			TimeoutMs: 60000,
			RegionID:  "cn-hangzhou",
		}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		if client.GetRegionID() != "cn-hangzhou" {
			t.Errorf("Expected RegionID to be 'cn-hangzhou', got '%s'", client.GetRegionID())
		}

		if client.APIKey != "test-api-key" {
			t.Errorf("Expected APIKey to be 'test-api-key', got '%s'", client.APIKey)
		}

		if client.Context == nil {
			t.Error("Expected Context service to be initialized")
		}
	})

	t.Run("NewAgentBayWithPartialConfigFillsDefaults", func(t *testing.T) {
		// Only region_id is set; other values should be filled with defaults.
		// Endpoint is derived from RegionID via the mapping.
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

		if client.Client == nil || client.Client.Endpoint == nil {
			t.Fatalf("Expected OpenAPI client endpoint to be initialized")
		}
		if got, want := *client.Client.Endpoint, "agentbay.cn-hangzhou.aliyuncs.com"; got != want {
			t.Errorf("Expected Endpoint to be %q, got %q", want, got)
		}
	})

	t.Run("NewAgentBayDefaultsToHangzhouUnit", func(t *testing.T) {
		// Clear AGENTBAY_REGION_ID env var to ensure isolation from local environment.
		t.Setenv("AGENTBAY_REGION_ID", "")
		client, err := agentbay.NewAgentBay("test-api-key")
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Default region is now cn-hangzhou (was empty before the multi-region refactor).
		if client.GetRegionID() != "cn-hangzhou" {
			t.Errorf("Expected RegionID to default to 'cn-hangzhou', got '%s'", client.GetRegionID())
		}

		if client.APIKey != "test-api-key" {
			t.Errorf("Expected APIKey to be 'test-api-key', got '%s'", client.APIKey)
		}
	})

	t.Run("EndpointFieldIsIgnoredAndWarned", func(t *testing.T) {
		// Setting Endpoint in a struct literal is ignored; the resolved endpoint
		// is always derived from RegionID. (We don't capture the warning here —
		// just verify the resolved endpoint is the canonical one.)
		config := &agentbay.Config{
			Endpoint:  "https://should-be-ignored.example.com",
			TimeoutMs: 60000,
			RegionID:  "ap-southeast-1",
		}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		if got, want := *client.Client.Endpoint, "agentbay.ap-southeast-1.aliyuncs.com"; got != want {
			t.Errorf("Expected Endpoint to be %q, got %q", want, got)
		}
	})

	t.Run("EmptyRegionIDFallsBackToDefault", func(t *testing.T) {
		t.Setenv("AGENTBAY_REGION_ID", "")
		config := &agentbay.Config{
			TimeoutMs: 60000,
			RegionID:  "",
		}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Empty string is treated as "not provided" → default cn-hangzhou.
		if client.GetRegionID() != "cn-hangzhou" {
			t.Errorf("Expected RegionID to default to 'cn-hangzhou', got '%s'", client.GetRegionID())
		}
	})

	t.Run("PrePrefixNormalizesRegion", func(t *testing.T) {
		config := &agentbay.Config{
			TimeoutMs: 60000,
			RegionID:  "pre-cn-hangzhou",
		}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// pre- prefix is stripped from the stored region.
		if client.GetRegionID() != "cn-hangzhou" {
			t.Errorf("Expected RegionID to be normalized to 'cn-hangzhou', got '%s'", client.GetRegionID())
		}
		// Endpoint should be the pre-release domain.
		if got, want := *client.Client.Endpoint, "agentbay-pre.cn-hangzhou.aliyuncs.com"; got != want {
			t.Errorf("Expected Endpoint to be %q, got %q", want, got)
		}
	})

	t.Run("EachSupportedRegionMapsCorrectly", func(t *testing.T) {
		cases := []struct {
			region   string
			endpoint string
		}{
			{"cn-hangzhou", "agentbay.cn-hangzhou.aliyuncs.com"},
			{"ap-southeast-1", "agentbay.ap-southeast-1.aliyuncs.com"},
			{"us-east-1", "agentbay.us-east-1.aliyuncs.com"},
		}
		for _, tc := range cases {
			tc := tc
			t.Run(tc.region, func(t *testing.T) {
				config := &agentbay.Config{RegionID: tc.region}
				client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
				if err != nil {
					t.Fatalf("Failed to create AgentBay client: %v", err)
				}
				if client.GetRegionID() != tc.region {
					t.Errorf("RegionID: want %q, got %q", tc.region, client.GetRegionID())
				}
				if got := *client.Client.Endpoint; got != tc.endpoint {
					t.Errorf("Endpoint: want %q, got %q", tc.endpoint, got)
				}
			})
		}
	})

	t.Run("InvalidRegionPanics", func(t *testing.T) {
		defer func() {
			r := recover()
			if r == nil {
				t.Fatalf("Expected panic for invalid region, got nil")
			}
			err, ok := r.(error)
			if !ok {
				t.Fatalf("Expected panic value to be error, got %T: %v", r, r)
			}
			msg := err.Error()
			if !strings.Contains(msg, "us-west-1") || !strings.Contains(msg, "cn-hangzhou") || !strings.Contains(msg, "pre-") {
				t.Errorf("Error message missing expected content: %s", msg)
			}
		}()
		config := &agentbay.Config{RegionID: "us-west-1"}
		_, _ = agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
	})
}
