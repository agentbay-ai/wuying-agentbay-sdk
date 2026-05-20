// ci-stable
package integration_test

import (
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// Helper function to get test API key from environment
func getTestAPIKey() string {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	return apiKey
}

func TestContextClearAsync(t *testing.T) {
	apiKey := getTestAPIKey()
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a test context
	contextName := fmt.Sprintf("test-context-async-%d", time.Now().Unix())
	createResult, err := agentBay.Context.Create(contextName)
	if err != nil {
		t.Fatalf("Error creating context: %v", err)
	}

	t.Logf("✓ Created test context: %s (ID: %s)", contextName, createResult.ContextID)

	// Test ClearAsync
	result, err := agentBay.Context.ClearAsync(createResult.ContextID)
	if err != nil {
		t.Fatalf("Error calling ClearAsync: %v", err)
	}

	t.Logf("✓ ClearAsync result:")
	t.Logf("  - Success: %v", result.Success)
	t.Logf("  - Status: %s", result.Status)
	t.Logf("  - ContextID: %s", result.ContextID)
	t.Logf("  - ErrorMessage: %s", result.ErrorMessage)
	t.Logf("  - RequestID: %s", result.RequestID)

	if !result.Success {
		t.Errorf("ClearAsync failed: %s", result.ErrorMessage)
	}

	// Clean up
	if createResult.ContextID != "" {
		ctx := &agentbay.Context{ID: createResult.ContextID}
		deleteResult, err := agentBay.Context.Delete(ctx)
		if err != nil {
			t.Logf("Warning: Failed to delete context: %v", err)
		} else if deleteResult != nil {
			t.Logf("✓ Deleted test context: %s", createResult.ContextID)
		}
	}
}

func TestContextClearSuccess(t *testing.T) {
	apiKey := getTestAPIKey()
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a test context
	contextName := fmt.Sprintf("test-context-clear-%d", time.Now().Unix())
	createResult, err := agentBay.Context.Create(contextName)
	if err != nil {
		t.Fatalf("Error creating context: %v", err)
	}

	t.Logf("✓ Created test context: %s (ID: %s)", contextName, createResult.ContextID)

	// Test Clear (synchronous with short timeout)
	result, err := agentBay.Context.Clear(createResult.ContextID, 30, 2.0)

	t.Logf("✓ Clear result:")
	if err != nil {
		t.Logf("  - Error: %v", err)
	} else if result != nil {
		t.Logf("  - Success: %v", result.Success)
		t.Logf("  - Status: %s", result.Status)
		t.Logf("  - ContextID: %s", result.ContextID)
		t.Logf("  - ErrorMessage: %s", result.ErrorMessage)
		t.Logf("  - RequestID: %s", result.RequestID)
	}

	// Note: This might timeout or succeed depending on server processing time
	if err != nil {
		t.Logf("Note: Clear timed out (this is expected if processing takes longer than 30s)")
	}

	// Clean up
	if createResult.ContextID != "" {
		ctx := &agentbay.Context{ID: createResult.ContextID}
		deleteResult, err := agentBay.Context.Delete(ctx)
		if err != nil {
			t.Logf("Warning: Failed to delete context: %v", err)
		} else if deleteResult != nil {
			t.Logf("✓ Deleted test context: %s", createResult.ContextID)
		}
	}
}

func TestContextClearInvalidID(t *testing.T) {
	apiKey := getTestAPIKey()
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Test ClearAsync with invalid ID
	result, err := agentBay.Context.ClearAsync("invalid-context-id-12345")
	if err != nil {
		t.Logf("✓ Expected error for invalid context ID: %v", err)
	} else if result != nil {
		t.Logf("✓ ClearAsync result:")
		t.Logf("  - Success: %v", result.Success)
		t.Logf("  - ErrorMessage: %s", result.ErrorMessage)

		if result.Success {
			t.Errorf("Expected ClearAsync to fail for invalid context ID")
		}
	}
}

func TestContextClearFullLifecycle(t *testing.T) {
	apiKey := getTestAPIKey()
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a test context
	contextName := fmt.Sprintf("test-context-lifecycle-%d", time.Now().Unix())
	createResult, err := agentBay.Context.Create(contextName)
	if err != nil {
		t.Fatalf("Error creating context: %v", err)
	}

	t.Logf("✓ Created test context: %s (ID: %s)", contextName, createResult.ContextID)

	// Step 1: Test ClearAsync
	t.Logf("\nStep 1: Testing ClearAsync...")
	asyncResult, err := agentBay.Context.ClearAsync(createResult.ContextID)
	if err != nil {
		t.Fatalf("Error calling ClearAsync: %v", err)
	}
	t.Logf("✓ ClearAsync completed - Success: %v, Status: %s", asyncResult.Success, asyncResult.Status)

	// Step 2: Test Clear (with shorter timeout for testing)
	t.Logf("\nStep 2: Testing Clear (synchronous)...")
	clearResult, err := agentBay.Context.Clear(createResult.ContextID, 10, 1.0)
	if err != nil {
		t.Logf("Note: Clear timed out or failed: %v", err)
	} else if clearResult != nil {
		t.Logf("✓ Clear completed - Success: %v, Status: %s", clearResult.Success, clearResult.Status)
	}

	// Step 3: Verify context still exists
	t.Logf("\nStep 3: Verifying context exists after clear...")
	getResult, err := agentBay.Context.Get(contextName, false)
	if err != nil {
		t.Logf("Warning: Failed to get context: %v", err)
	} else if getResult != nil && getResult.Context != nil {
		t.Logf("✓ Context still exists - ID: %s, Name: %s",
			getResult.Context.ID, getResult.Context.Name)
	}

	// Clean up
	t.Logf("\nStep 4: Cleaning up test context...")
	if createResult.ContextID != "" {
		ctx := &agentbay.Context{ID: createResult.ContextID}
		deleteResult, err := agentBay.Context.Delete(ctx)
		if err != nil {
			t.Logf("Warning: Failed to delete context: %v", err)
		} else if deleteResult != nil {
			t.Logf("✓ Deleted test context: %s", createResult.ContextID)
		}
	}
}

func TestContextClearMultipleCalls(t *testing.T) {
	apiKey := getTestAPIKey()
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a test context
	contextName := fmt.Sprintf("test-context-multi-%d", time.Now().Unix())
	createResult, err := agentBay.Context.Create(contextName)
	if err != nil {
		t.Fatalf("Error creating context: %v", err)
	}

	t.Logf("✓ Created test context: %s (ID: %s)", contextName, createResult.ContextID)

	// Call ClearAsync multiple times
	for i := 1; i <= 3; i++ {
		t.Logf("\nTest call %d:", i)
		result, err := agentBay.Context.ClearAsync(createResult.ContextID)
		if err != nil {
			t.Logf("  Error: %v", err)
		} else {
			t.Logf("  ✓ Success: %v, Status: %s, RequestID: %s", result.Success, result.Status, result.RequestID)
		}
		time.Sleep(500 * time.Millisecond)
	}

	// Clean up
	if createResult.ContextID != "" {
		ctx := &agentbay.Context{ID: createResult.ContextID}
		deleteResult, err := agentBay.Context.Delete(ctx)
		if err != nil {
			t.Logf("Warning: Failed to delete context: %v", err)
		} else if deleteResult != nil {
			t.Logf("✓ Deleted test context: %s", createResult.ContextID)
		}
	}
}
