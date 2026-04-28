package integration

import (
	"os"
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func TestLifecyclePolicyCustom(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set")
	}
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("failed to create AgentBay: %v", err)
	}
	lp := agentbay.NewLifecyclePolicy()
	lp.IdleReleaseTimeout = 10
	lp.MaxRuntime = 60
	base := agentbay.NewCreateSessionParams().
		WithImageId("linux_latest").
		WithLabels(map[string]string{
			"test": "lifecycle-policy",
			"sdk":  "golang",
			"case": "custom",
		})
	params, err := base.WithLifecyclePolicy(lp)
	if err != nil {
		t.Fatalf("WithLifecyclePolicy: %v", err)
	}
	result, err := client.Create(params)
	if err != nil {
		t.Fatalf("Create: %v", err)
	}
	if result.Session == nil || strings.TrimSpace(result.Session.SessionID) == "" {
		t.Fatal("session not created")
	}
	s := result.Session
	defer func() {
		if s != nil {
			_, _ = s.Delete()
		}
	}()
	cmdResult, err := s.Command.ExecuteCommand("echo hello")
	if err != nil {
		t.Fatalf("ExecuteCommand: %v", err)
	}
	out := strings.TrimSpace(cmdResult.Output)
	if out != "hello" {
		t.Fatalf("unexpected output %q want %q", cmdResult.Output, "hello")
	}
}

func TestLifecyclePolicyManualRelease(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set")
	}
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("failed to create AgentBay: %v", err)
	}
	lp := agentbay.NewLifecyclePolicyManualRelease()
	base := agentbay.NewCreateSessionParams().
		WithImageId("linux_latest").
		WithLabels(map[string]string{
			"test": "lifecycle-policy",
			"sdk":  "golang",
			"case": "manual",
		})
	params, err := base.WithLifecyclePolicy(lp)
	if err != nil {
		t.Fatalf("WithLifecyclePolicy: %v", err)
	}
	result, err := client.Create(params)
	if err != nil {
		t.Fatalf("Create: %v", err)
	}
	if result.Session == nil || strings.TrimSpace(result.Session.SessionID) == "" {
		t.Fatal("session not created")
	}
	s := result.Session
	defer func() {
		if s != nil {
			_, _ = s.Delete()
		}
	}()
	cmdResult, err := s.Command.ExecuteCommand("echo manual")
	if err != nil {
		t.Fatalf("ExecuteCommand: %v", err)
	}
	out := strings.TrimSpace(cmdResult.Output)
	if out != "manual" {
		t.Fatalf("unexpected output %q want %q", cmdResult.Output, "manual")
	}
}

func TestLifecyclePolicyDefault(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set")
	}
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("failed to create AgentBay: %v", err)
	}
	lp := agentbay.NewLifecyclePolicy()
	base := agentbay.NewCreateSessionParams().
		WithImageId("linux_latest").
		WithLabels(map[string]string{
			"test": "lifecycle-policy",
			"sdk":  "golang",
			"case": "default",
		})
	params, err := base.WithLifecyclePolicy(lp)
	if err != nil {
		t.Fatalf("WithLifecyclePolicy: %v", err)
	}
	result, err := client.Create(params)
	if err != nil {
		t.Fatalf("Create: %v", err)
	}
	if result.Session == nil || strings.TrimSpace(result.Session.SessionID) == "" {
		t.Fatal("session not created")
	}
	s := result.Session
	defer func() {
		if s != nil {
			_, _ = s.Delete()
		}
	}()
}
