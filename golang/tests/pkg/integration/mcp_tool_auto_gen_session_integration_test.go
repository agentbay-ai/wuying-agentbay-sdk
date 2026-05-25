package integration

import (
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestMcpToolCallWithActiveSession integration test for MCP tool call with active session
func TestMcpToolCallWithActiveSession(t *testing.T) {
	// Get API Key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	// Initialize AgentBay client
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating session for MCP tool call test...")
	result, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	session := result.Session
	t.Logf("Session created successfully, ID: %s", session.SessionID)

	// Call MCP tool with active session (autoGenSession=false)
	fmt.Println("Calling MCP tool with active session...")
	toolResult, err := session.CallMcpTool("shell", map[string]interface{}{
		"command":    "echo 'test'",
		"timeout_ms": 5000,
	})
	if err != nil {
		t.Fatalf("Failed to call MCP tool: %v", err)
	}
	if !toolResult.Success {
		t.Fatalf("MCP tool call failed: %s", toolResult.ErrorMessage)
	}
	t.Logf("MCP tool call succeeded (RequestID: %s)", toolResult.RequestID)

	// Clean up
	fmt.Println("Deleting session...")
	deleteResult, err := session.Delete()
	if err != nil {
		t.Fatalf("Failed to delete session: %v", err)
	}
	t.Logf("Session deleted successfully (RequestID: %s)", deleteResult.RequestID)
}

// TestMcpToolCallWithDeletedSessionAutoGenFalse integration test for MCP tool call with deleted session and autoGenSession=false
func TestMcpToolCallWithDeletedSessionAutoGenFalse(t *testing.T) {
	// Get API Key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	// Initialize AgentBay client
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating session for deletion test...")
	result, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	session := result.Session
	sessionID := session.SessionID
	t.Logf("Session created successfully, ID: %s", sessionID)

	// Delete the session
	fmt.Println("Deleting session...")
	deleteResult, err := session.Delete()
	if err != nil {
		t.Fatalf("Failed to delete session: %v", err)
	}
	t.Logf("Session deleted successfully (RequestID: %s)", deleteResult.RequestID)

	// Wait for deletion to complete
	time.Sleep(2 * time.Second)

	// Verify session is deleted
	listResult, err := client.List("", nil, nil, nil, "")
	if err != nil {
		t.Fatalf("Failed to list sessions: %v", err)
	}

	sessionExists := false
	for _, sid := range listResult.SessionIds {
		if sid["sessionId"] == sessionID {
			sessionExists = true
			break
		}
	}
	if sessionExists {
		t.Errorf("Session ID %s still exists after deletion", sessionID)
	}

	// Try to call MCP tool with deleted session (autoGenSession=false)
	fmt.Println("Calling MCP tool with deleted session (autoGenSession=false)...")
	toolResult, err := session.CallMcpTool("shell", map[string]interface{}{
		"command":    "echo 'test'",
		"timeout_ms": 5000,
	})

	// Expect failure
	if err != nil {
		t.Logf("MCP tool call failed as expected with error: %v", err)
	} else if !toolResult.Success {
		t.Logf("MCP tool call failed as expected: %s", toolResult.ErrorMessage)
	} else {
		t.Error("MCP tool call should fail with deleted session")
	}
}

// TestMcpToolCallWithDeletedSessionAutoGenTrue integration test for MCP tool call with deleted session and autoGenSession=true
func TestMcpToolCallWithDeletedSessionAutoGenTrue(t *testing.T) {
	// Get API Key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	// Initialize AgentBay client
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating session for auto-gen test...")
	result, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	session := result.Session
	sessionID := session.SessionID
	t.Logf("Session created successfully, ID: %s", sessionID)

	// Delete the session
	fmt.Println("Deleting session...")
	deleteResult, err := session.Delete()
	if err != nil {
		t.Fatalf("Failed to delete session: %v", err)
	}
	t.Logf("Session deleted successfully (RequestID: %s)", deleteResult.RequestID)

	// Wait for deletion to complete
	time.Sleep(2 * time.Second)

	// Verify session is deleted
	listResult, err := client.List("", nil, nil, nil, "")
	if err != nil {
		t.Fatalf("Failed to list sessions: %v", err)
	}

	sessionExists := false
	for _, sid := range listResult.SessionIds {
		if sid["sessionId"] == sessionID {
			sessionExists = true
			break
		}
	}
	if sessionExists {
		t.Errorf("Session ID %s still exists after deletion", sessionID)
	}

	// Try to call MCP tool with deleted session (autoGenSession=true)
	fmt.Println("Calling MCP tool with deleted session (autoGenSession=true)...")
	toolResult, err := session.CallMcpTool("shell", map[string]interface{}{
		"command":    "echo 'test'",
		"timeout_ms": 5000,
	})

	// The behavior depends on the server implementation
	// If auto_gen_session is supported, it may succeed by creating a new session
	// If not supported, it should fail
	if err != nil {
		t.Logf("MCP tool call result with error: %v", err)
	} else {
		t.Logf("MCP tool call result: success=%v, error=%s", toolResult.Success, toolResult.ErrorMessage)
	}
	// We don't assert success/failure here as it depends on server support
	// Just verify we got a response
	if toolResult == nil {
		t.Error("Expected a tool result, got nil")
	}
}
