package integration

import (
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

const envTestImage = "imgc-0ab5takivb1ke11hu"

func TestEnvSetAndGet(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set")
	}

	ab, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to create AgentBay: %v", err)
	}

	result, err := ab.Create(agentbay.NewCreateSessionParams().WithImageId(envTestImage))
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	session := result.Session
	defer func() {
		_, _ = session.Delete()
	}()

	// Test Set
	setResult, err := session.Env.Set(map[string]string{
		"TEST_KEY": "test_value",
		"SDK_VER":  "1.0",
	})
	if err != nil {
		t.Fatalf("Env.Set error: %v", err)
	}
	if !setResult.Success {
		t.Fatalf("Env.Set failed: %s", setResult.ErrorMessage)
	}

	// Test Get specific keys
	getResult, err := session.Env.Get("TEST_KEY", "SDK_VER")
	if err != nil {
		t.Fatalf("Env.Get error: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Env.Get failed: %s", getResult.ErrorMessage)
	}
	if getResult.Envs["TEST_KEY"] != "test_value" {
		t.Errorf("Expected TEST_KEY=test_value, got %s", getResult.Envs["TEST_KEY"])
	}
	if getResult.Envs["SDK_VER"] != "1.0" {
		t.Errorf("Expected SDK_VER=1.0, got %s", getResult.Envs["SDK_VER"])
	}

	// Test Get all
	allResult, err := session.Env.Get()
	if err != nil {
		t.Fatalf("Env.Get() all error: %v", err)
	}
	if !allResult.Success {
		t.Fatalf("Env.Get() all failed: %s", allResult.ErrorMessage)
	}
	if allResult.Envs["TEST_KEY"] != "test_value" {
		t.Errorf("Expected TEST_KEY in all envs, got %s", allResult.Envs["TEST_KEY"])
	}

	// Test overwrite
	_, err = session.Env.Set(map[string]string{"TEST_KEY": "updated"})
	if err != nil {
		t.Fatalf("Env.Set overwrite error: %v", err)
	}
	updated, _ := session.Env.Get("TEST_KEY")
	if updated.Envs["TEST_KEY"] != "updated" {
		t.Errorf("Expected TEST_KEY=updated after overwrite, got %s", updated.Envs["TEST_KEY"])
	}

	// Test visible in shell
	_, _ = session.Env.Set(map[string]string{"SHELL_VIS": "hello_from_env"})
	cmdResult, err := session.Command.ExecuteCommand("echo $SHELL_VIS", 5000)
	if err != nil {
		t.Fatalf("ExecuteCommand error: %v", err)
	}
	if !cmdResult.Success {
		t.Fatalf("Shell command failed: %s", cmdResult.ErrorMessage)
	}
	if cmdResult.Stdout == "" || cmdResult.Stdout != "hello_from_env\n" {
		t.Errorf("Expected shell to see SHELL_VIS, got stdout=%q", cmdResult.Stdout)
	}
}

func TestEnvSetEmptyReturnsError(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set")
	}

	ab, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to create AgentBay: %v", err)
	}
	result, err := ab.Create(agentbay.NewCreateSessionParams().WithImageId(envTestImage))
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	session := result.Session
	defer func() {
		_, _ = session.Delete()
	}()

	_, err = session.Env.Set(map[string]string{})
	if err == nil {
		t.Error("Expected error when setting empty envs, got nil")
	}
}
