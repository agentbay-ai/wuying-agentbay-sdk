package agentbay_test

import (
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

	t.Run("PrePrefixUsesHardcodedMapping", func(t *testing.T) {
		// Known pre regions resolve via the hardcoded mapping. Different
		// regions can use different pre-release naming conventions:
		// cn-hangzhou uses agentbay-pre.* while ap-southeast-1 uses wuyingai-pre.*.
		cases := []struct {
			input    string
			region   string
			endpoint string
		}{
			{"pre-cn-hangzhou", "cn-hangzhou", "agentbay-pre.cn-hangzhou.aliyuncs.com"},
			{"pre-ap-southeast-1", "ap-southeast-1", "wuyingai-pre.ap-southeast-1.aliyuncs.com"},
		}
		for _, tc := range cases {
			tc := tc
			t.Run(tc.input, func(t *testing.T) {
				config := &agentbay.Config{RegionID: tc.input}
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

	t.Run("RegionMapsByDirectSubstitution", func(t *testing.T) {
		// Soft whitelist — known regions resolve silently, unknown regions
		// emit a LogWarn (not asserted here) and still compose the
		// pattern-based endpoint. No validation error for unknowns: newly
		// onboarded regions work without an SDK upgrade.
		cases := []struct {
			region   string
			endpoint string
			known    bool
		}{
			{"cn-hangzhou", "agentbay.cn-hangzhou.aliyuncs.com", true},
			{"ap-southeast-1", "agentbay.ap-southeast-1.aliyuncs.com", true},
			{"us-east-1", "agentbay.us-east-1.aliyuncs.com", true},
			{"us-west-1", "agentbay.us-west-1.aliyuncs.com", false},
			{"eu-central-1", "agentbay.eu-central-1.aliyuncs.com", false},
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

	t.Run("UnknownPreRegionFallsBackToDefaultPatternWithWarning", func(t *testing.T) {
		// Unknown pre regions emit a LogWarn line and fall back to the default
		// agentbay-pre.{actual}.aliyuncs.com pattern. (We don't capture stderr
		// here — just verify the fallback endpoint and that no error is raised.)
		config := &agentbay.Config{RegionID: "pre-us-west-1"}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}
		if client.GetRegionID() != "us-west-1" {
			t.Errorf("RegionID: want %q, got %q", "us-west-1", client.GetRegionID())
		}
		if got, want := *client.Client.Endpoint, "agentbay-pre.us-west-1.aliyuncs.com"; got != want {
			t.Errorf("Endpoint: want %q, got %q", want, got)
		}
	})

	t.Run("DeprecatedEndpointFieldIsIgnoredAndEmitsDeprecationLog", func(t *testing.T) {
		// Backwards compat: setting Config.Endpoint in a struct literal does
		// not break — the value is ignored and the endpoint is derived from
		// RegionID. A [DEPRECATION] log line is emitted by the Deprecated()
		// helper (not asserted here; this test verifies non-breaking behavior).
		config := &agentbay.Config{
			Endpoint:  "should-be-ignored.example.com",
			RegionID:  "ap-southeast-1",
			TimeoutMs: 30000,
		}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}
		if got, want := *client.Client.Endpoint, "agentbay.ap-southeast-1.aliyuncs.com"; got != want {
			t.Errorf("Endpoint: want %q, got %q", want, got)
		}
	})

	t.Run("CfgEndpointAloneIsUsedAsFallback", func(t *testing.T) {
		// Deprecated fallback: when only Endpoint is set (no RegionID at any
		// level), the user-supplied endpoint is honored as-is.
		t.Setenv("AGENTBAY_REGION_ID", "")
		t.Setenv("AGENTBAY_ENDPOINT", "")
		config := &agentbay.Config{Endpoint: "custom.example.com"}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}
		if got, want := *client.Client.Endpoint, "custom.example.com"; got != want {
			t.Errorf("Endpoint: want %q, got %q", want, got)
		}
	})

	t.Run("CfgEndpointWinsOverEnvRegionID", func(t *testing.T) {
		// Code layer beats env layer entirely: cfg.Endpoint takes effect even
		// though AGENTBAY_REGION_ID is set in the environment.
		t.Setenv("AGENTBAY_REGION_ID", "us-east-1")
		config := &agentbay.Config{Endpoint: "cfg-endpoint.example.com"}
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithConfig(config))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}
		if got, want := *client.Client.Endpoint, "cfg-endpoint.example.com"; got != want {
			t.Errorf("Endpoint: want %q, got %q", want, got)
		}
	})
}
