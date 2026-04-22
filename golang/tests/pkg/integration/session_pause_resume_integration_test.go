// ci-stable
package integration

import (
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestSessionPauseResumeIntegration tests successful pause and resume operations on a session
func TestSessionPauseResumeIntegration(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Creating a new session for pause/resume testing...")
	createResult, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	createdSession := createResult.Session
	sessionId := createdSession.SessionID
	t.Logf("Session created with ID: %s", sessionId)

	// Ensure cleanup
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		deleteResult, err := createdSession.Delete()
		if err != nil {
			t.Logf("Failed to delete session: %v", err)
		} else {
			t.Logf("Session %s deleted successfully", sessionId)
			if !deleteResult.Success {
				t.Logf("Session deletion failed")
			}
		}
	}()

	// Verify session is initially in RUNNING state
	fmt.Println("Step 1: Verifying session is initially RUNNING...")
	getResult, err := createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	if getResult.Status != "RUNNING" {
		t.Fatalf("Expected session status RUNNING, got %s", getResult.Status)
	}
	t.Logf("✓ Session is RUNNING: %s", sessionId)

	// Pause the session
	fmt.Println("Step 2: Pausing session...")
	pauseResult, err := client.BetaPause(createdSession, 600, 2.0)
	if err != nil {
		t.Fatalf("Failed to pause session: %v", err)
	}
	if pauseResult == nil {
		t.Fatal("Pause returned nil result")
	}
	if !pauseResult.Success {
		t.Fatalf("Pause failed: %s", pauseResult.ErrorMessage)
	}
	t.Logf("✓ Session pause initiated successfully")
	t.Logf("  Request ID: %s", pauseResult.RequestID)

	// Wait a bit for pause to complete
	fmt.Println("Step 3: Waiting for session to pause...")
	time.Sleep(2 * time.Second)

	// Check session status after pause
	getResult, err = createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	// Session should be PAUSED or still PAUSING
	if getResult.Status != "PAUSED" && getResult.Status != "PAUSING" {
		t.Fatalf("Expected session status PAUSED or PAUSING, got %s", getResult.Status)
	}
	t.Logf("✓ Session status after pause: %s", getResult.Status)

	// Resume the session (synchronous)
	fmt.Println("Step 4: Resuming session...")
	resumeResult, err := client.BetaResume(createdSession, 120, 3.0)
	if err != nil {
		t.Fatalf("Failed to resume session: %v", err)
	}
	if resumeResult == nil {
		t.Fatal("Resume returned nil result")
	}
	if !resumeResult.Success {
		t.Fatalf("Resume failed: %s", resumeResult.ErrorMessage)
	}
	if resumeResult.Status != "RUNNING" {
		t.Fatalf("Expected resume status RUNNING, got %s", resumeResult.Status)
	}
	t.Logf("✓ Session resumed successfully")
	t.Logf("  Final status: %s", resumeResult.Status)
	t.Logf("  Request ID: %s", resumeResult.RequestID)

	// Verify session is RUNNING after resume
	getResult, err = createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	if getResult.Status != "RUNNING" {
		t.Fatalf("Expected session status RUNNING, got %s", getResult.Status)
	}
	t.Logf("✓ Session is RUNNING after resume: %s", sessionId)
}

// TestSessionPauseNonExistent tests pause operation on non-existent session
func TestSessionPauseNonExistent(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Testing pause operation on non-existent session...")
	// Create a mock session object with invalid session ID
	invalidSession := agentbay.NewSession(client, "non-existent-session-12345")

	// This should return a failed SessionPauseResult
	pauseResult, err := client.BetaPause(invalidSession, 600, 2.0)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if pauseResult == nil {
		t.Fatal("Pause returned nil result")
	}
	if pauseResult.Success {
		t.Fatal("Expected pause to fail for non-existent session")
	}
	t.Logf("✓ Returned SessionPauseResult with success=false as expected")
	t.Logf("  Error: %s", pauseResult.ErrorMessage)
	if pauseResult.ErrorMessage == "" {
		t.Error("Expected error message for non-existent session pause")
	}
}

// TestSessionResumeNonExistent tests resume operation on non-existent session
func TestSessionResumeNonExistent(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Testing resume operation on non-existent session...")
	// Create a mock session object with invalid session ID
	invalidSession := agentbay.NewSession(client, "non-existent-session-12345")

	// This should return a failed SessionResumeResult
	resumeResult, err := client.BetaResume(invalidSession, 600, 2.0)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if resumeResult == nil {
		t.Fatal("Resume returned nil result")
	}
	if resumeResult.Success {
		t.Fatal("Expected resume to fail for non-existent session")
	}
	t.Logf("✓ Returned SessionResumeResult with success=false as expected")
	t.Logf("  Error: %s", resumeResult.ErrorMessage)
	if resumeResult.ErrorMessage == "" {
		t.Error("Expected error message for non-existent session resume")
	}
}

// TestSessionPauseAlreadyPaused tests pausing a session that is already paused
func TestSessionPauseAlreadyPaused(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Creating a new session for already paused test...")
	createResult, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	createdSession := createResult.Session
	sessionId := createdSession.SessionID
	t.Logf("Session created with ID: %s", sessionId)

	// Ensure cleanup
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		deleteResult, err := createdSession.Delete()
		if err != nil {
			t.Logf("Failed to delete session: %v", err)
		} else {
			t.Logf("Session %s deleted successfully", sessionId)
			if !deleteResult.Success {
				t.Logf("Session deletion failed")
			}
		}
	}()

	// Pause the session
	fmt.Println("Step 1: Pausing session...")
	pauseResult1, err := client.BetaPause(createdSession, 600, 2.0)
	if err != nil {
		t.Fatalf("Failed to pause session: %v", err)
	}
	if !pauseResult1.Success {
		t.Fatalf("First pause failed: %s", pauseResult1.ErrorMessage)
	}
	t.Logf("✓ Session paused successfully")

	// Wait for pause to complete
	fmt.Println("Step 2: Waiting for session to pause...")
	time.Sleep(2 * time.Second)

	// Verify session is PAUSED or PAUSING
	getResult, err := createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	if getResult.Status != "PAUSED" && getResult.Status != "PAUSING" {
		t.Fatalf("Expected session status PAUSED or PAUSING, got %s", getResult.Status)
	}
	t.Logf("✓ Session status: %s", getResult.Status)

	// Try to pause again
	fmt.Println("Step 3: Attempting to pause already paused session...")
	pauseResult2, err := client.BetaPause(createdSession, 600, 2.0)
	if err != nil {
		t.Fatalf("Unexpected error on second pause: %v", err)
	}
	// Second pause may succeed or fail depending on API behavior
	// Both are acceptable for this test
	t.Logf("✓ Second pause completed")
	t.Logf("  Success: %t", pauseResult2.Success)
	if pauseResult2.Success {
		t.Logf("  Request ID: %s", pauseResult2.RequestID)
	} else {
		t.Logf("  Error: %s", pauseResult2.ErrorMessage)
	}
	// 删除前需要进行resume，否则会删除失败
	fmt.Println("Step 4: Resuming session before deletion...")
	resumeResult, err := client.BetaResume(createdSession, 600, 2.0)
	if err != nil {
		t.Fatalf("Failed to resume session: %v", err)
	}
	if !resumeResult.Success {
		t.Fatalf("Resume failed: %s", resumeResult.ErrorMessage)
	}
	// 获取状态，判断是否是RUNNING
	getResult, err = createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	if getResult.Status != "RUNNING" {
		t.Fatalf("Expected session status RUNNING, got %s", getResult.Status)
	}
}

// TestSessionResumeAlreadyRunning tests resuming a session that is already running
func TestSessionResumeAlreadyRunning(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Creating a new session for already running test...")
	createResult, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	createdSession := createResult.Session
	sessionId := createdSession.SessionID
	t.Logf("Session created with ID: %s", sessionId)

	// Ensure cleanup
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		deleteResult, err := createdSession.Delete()
		if err != nil {
			t.Logf("Failed to delete session: %v", err)
		} else {
			t.Logf("Session %s deleted successfully", sessionId)
			if !deleteResult.Success {
				t.Logf("Session deletion failed")
			}
		}
	}()

	// Verify session is RUNNING
	getResult, err := createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	if getResult.Status != "RUNNING" {
		t.Fatalf("Expected session status RUNNING, got %s", getResult.Status)
	}
	t.Logf("✓ Session is RUNNING: %s", sessionId)

	// Try to resume the already running session
	fmt.Println("Attempting to resume already running session...")
	resumeResult, err := client.BetaResume(createdSession, 30, 2)
	if err != nil {
		t.Fatalf("Unexpected error on resume: %v", err)
	}
	// Resume of already running session may succeed or have specific behavior
	// Just verify it doesn't crash and returns a proper result object
	if resumeResult == nil {
		t.Fatal("Resume returned nil result")
	}
	t.Logf("✓ Resume completed")
	t.Logf("  Success: %t", resumeResult.Success)
	if resumeResult.Success {
		t.Logf("  Status: %s", resumeResult.Status)
		t.Logf("  Request ID: %s", resumeResult.RequestID)
	} else {
		t.Logf("  Error: %s", resumeResult.ErrorMessage)
	}
}

// TestSessionPauseWithShortTimeout tests pause with a short timeout parameter
func TestSessionPauseWithShortTimeout(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Creating a new session for short timeout test...")
	createResult, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	createdSession := createResult.Session
	sessionId := createdSession.SessionID
	t.Logf("Session created with ID: %s", sessionId)

	// Ensure cleanup
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		deleteResult, err := createdSession.Delete()
		if err != nil {
			t.Logf("Failed to delete session: %v", err)
		} else {
			t.Logf("Session %s deleted successfully", sessionId)
			if !deleteResult.Success {
				t.Logf("Session deletion failed")
			}
		}
	}()

	// Pause with short timeout (using agent_bay method)
	fmt.Println("Pausing session with short timeout...")
	pauseResult, err := client.BetaPause(createdSession, 10, 1.0)
	if err != nil {
		t.Fatalf("Failed to pause session with short timeout: %v", err)
	}
	if pauseResult == nil {
		t.Fatal("Pause with short timeout returned nil result")
	}
	// Pause should succeed regardless of timeout parameter
	if !pauseResult.Success {
		t.Fatalf("Pause with short timeout failed: %s", pauseResult.ErrorMessage)
	}
	t.Logf("✓ Pause with short timeout successful")
	// 删除前需要进行resume，否则会删除失败
	fmt.Println("Step 4: Resuming session before deletion...")
	resumeResult, err := client.BetaResume(createdSession, 600, 2.0)
	if err != nil {
		t.Fatalf("Failed to resume session: %v", err)
	}
	if !resumeResult.Success {
		t.Fatalf("Resume failed: %s", resumeResult.ErrorMessage)
	}
	// 获取状态，判断是否是RUNNING
	getResult, err := createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	if getResult.Status != "RUNNING" {
		t.Fatalf("Expected session status RUNNING, got %s", getResult.Status)
	}
}
