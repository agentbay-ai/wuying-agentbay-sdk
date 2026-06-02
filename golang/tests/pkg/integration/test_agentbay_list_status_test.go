// ci-stable
package integration

import (
	"fmt"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAgentBayListStatusIntegration tests session pause and resume operations with list status verification
func TestAgentBayListStatusIntegration(t *testing.T) {
	// Get API Key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}
	fmt.Printf("api_key = %s\n", apiKey)

	// Initialize AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey, nil)
	require.NoError(t, err)
	require.NotNil(t, agentBay)

	// Create session for testing
	fmt.Println("Creating a new session for pause/resume testing...")
	params := agentbay.NewCreateSessionParams().
		WithLabels(map[string]string{
			"project":     "piaoyun-demo",
			"environment": "testing",
		})

	fmt.Println("Creating session...")
	sessionResult, err := agentBay.Create(params)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.True(t, sessionResult.Success)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session
	fmt.Printf("Session created with ID: %s\n", session.SessionID)

	// Helper function to verify session status and list
	verifySessionStatusAndList := func(expectedStatuses []agentbay.SessionStatus, operationName string) agentbay.SessionStatus {
		fmt.Printf("\nVerifying session status after %s...\n", operationName)

		// First call GetStatus to check the current status
		statusResult, err := session.GetStatus()
		require.NoError(t, err)
		require.True(t, statusResult.Success, fmt.Sprintf("Failed to get session status: %s", statusResult.ErrorMessage))

		initialStatus := statusResult.Status
		if initialStatus == "" {
			initialStatus = "UNKNOWN"
		}
		fmt.Printf("  ✓ Session status from GetStatus: %s\n", initialStatus)

		// Verify status is in expected list
		found := false
		for _, expected := range expectedStatuses {
			if initialStatus == expected.String() {
				found = true
				break
			}
		}
		require.True(t, found, fmt.Sprintf("Unexpected status %s, expected one of %v", initialStatus, expectedStatuses))

		// GetSession is internal in SDK; use GetStatus only.
		currentStatus := initialStatus

		// Test list with current status
		listResult, err := agentBay.List(currentStatus, nil, nil, nil, "")
		require.NoError(t, err)

		// Verify session is in the list and check array structure
		sessionFound := false
		for _, sessionData := range listResult.SessionIds {
			if sessionID, exists := sessionData["sessionId"]; exists && sessionID == session.SessionID {
				sessionFound = true
				require.Contains(t, sessionData, "sessionStatus", "sessionStatus field missing in list result")
				require.Contains(t, sessionData, "sessionId", "sessionId field missing in list result")
				require.Equal(t, currentStatus, sessionData["sessionStatus"])
				break
			}
		}

		require.True(t, sessionFound, fmt.Sprintf("Session %s not found in list with status %s", session.SessionID, currentStatus))
		fmt.Printf("  ✓ Session found in list with status %s\n", currentStatus)
		fmt.Printf("  ✓ Session status verification completed for %s\n", operationName)

		return agentbay.SessionStatus(currentStatus)
	}

	// Ensure cleanup
	defer func() {
		fmt.Println("\nCleaning up test sessions for this test...")
		if session != nil {
			// Try to resume session first in case it's paused
			statusResult, err := session.GetStatus()
			if err != nil {
				fmt.Printf("  ⚠ Could not get session status %s: %v\n", session.SessionID, err)
			} else if statusResult.Success {
				currentStatus := statusResult.Status

				// Resume if paused
				if currentStatus == "PAUSED" {
					_, resumeErr := agentBay.BetaResume(session, 600, 2.0)
					if resumeErr != nil {
						fmt.Printf("  ⚠ Could not resume session %s: %v\n", session.SessionID, resumeErr)
					} else {
						fmt.Printf("  ✓ Resumed session: %s\n", session.SessionID)
					}
				}

				// Delete if not already deleting or deleted
				if currentStatus != "DELETING" && currentStatus != "DELETED" &&
					currentStatus != "RESUMING" && currentStatus != "PAUSING" {
					deleteResult, err := agentBay.Delete(session, false)
					if err != nil {
						fmt.Printf("  ✗ Error deleting session %s: %v\n", session.SessionID, err)
					} else if deleteResult != nil {
						if deleteResult.Success {
							fmt.Printf("  ✓ Deleted session: %s\n", session.SessionID)
						} else {
							fmt.Printf("  ✗ Failed to delete session: %s\n", session.SessionID)
						}
					}
				}
			}
		}
	}()

	// Test 1: Pause and Resume Session Success
	t.Run("Pause and Resume Session Success", func(t *testing.T) {
		fmt.Println("\n" + strings.Repeat("=", 60))
		fmt.Println("TEST: Pause and Resume Session Success")
		fmt.Println(strings.Repeat("=", 60))

		// Verify session is initially in RUNNING state
		statusResult, err := session.GetStatus()
		require.NoError(t, err)
		require.True(t, statusResult.Success, fmt.Sprintf("Failed to get session status: %s", statusResult.ErrorMessage))

		initialStatus := statusResult.Status
		if initialStatus == "" {
			initialStatus = "UNKNOWN"
		}
		fmt.Printf("  ✓ Session status from GetStatus: %s\n", initialStatus)
		require.Equal(t, "RUNNING", initialStatus, fmt.Sprintf("Unexpected status %s, expected RUNNING", initialStatus))

		// Pause the session
		fmt.Printf("\nStep 2: Pausing session...\n")
		pauseResult, err := agentBay.BetaPause(session, 600, 2.0)
		require.NoError(t, err)
		require.NotNil(t, pauseResult)
		require.True(t, pauseResult.Success, fmt.Sprintf("Pause failed: %s", pauseResult.ErrorMessage))
		fmt.Printf("  ✓ Session pause initiated successfully\n")
		fmt.Printf("    Request ID: %s\n", pauseResult.RequestID)

		// Wait a bit for pause to complete
		fmt.Printf("\nStep 3: Waiting for session to pause...\n")
		time.Sleep(2 * time.Second)

		// Verify session status after pause
		verifySessionStatusAndList([]agentbay.SessionStatus{agentbay.SessionStatusPaused, agentbay.SessionStatusPausing}, "pause")
	})

	// Test 2: Resume Session Success
	t.Run("Resume Session Success", func(t *testing.T) {
		fmt.Println("\n" + strings.Repeat("=", 60))
		fmt.Println("TEST: Resume Session Success")
		fmt.Println(strings.Repeat("=", 60))

		// Session should be PAUSED or PAUSING after previous test
		statusResult, err := session.GetStatus()
		require.NoError(t, err)
		require.True(t, statusResult.Success, fmt.Sprintf("Failed to get session status: %s", statusResult.ErrorMessage))

		initialStatus := statusResult.Status
		if initialStatus == "" {
			initialStatus = "UNKNOWN"
		}
		fmt.Printf("  ✓ Session status from GetStatus: %s\n", initialStatus)
		require.Contains(t, []string{"PAUSED", "PAUSING"}, initialStatus, fmt.Sprintf("Unexpected status %s, expected PAUSED or PAUSING", initialStatus))

		// Resume the session
		fmt.Printf("\nStep 1: Resuming session...\n")
		resumeResult, err := agentBay.BetaResume(session, 600, 2.0)
		require.NoError(t, err)
		require.NotNil(t, resumeResult)
		require.True(t, resumeResult.Success, fmt.Sprintf("Resume failed: %s", resumeResult.ErrorMessage))
		fmt.Printf("  ✓ Session resume initiated successfully\n")
		fmt.Printf("    Request ID: %s\n", resumeResult.RequestID)

		// Wait a bit for resume to complete
		fmt.Printf("\nStep 2: Waiting for session to resume...\n")
		time.Sleep(2 * time.Second)

		// Verify session status after resume
		verifySessionStatusAndList([]agentbay.SessionStatus{agentbay.SessionStatusRunning, agentbay.SessionStatusResuming}, "resume")
	})

	// Test 3: List with Status Filter
	t.Run("List with Status Filter", func(t *testing.T) {
		fmt.Println("\n" + strings.Repeat("=", 60))
		fmt.Println("TEST: List with Status Filter")
		fmt.Println(strings.Repeat("=", 60))

		// Test listing with RUNNING status filter
		fmt.Printf("Testing list with RUNNING status filter...\n")
		listResult, err := agentBay.List(agentbay.SessionStatusRunning.String(), nil, nil, nil, "")
		require.NoError(t, err)

		// Verify our session is in the RUNNING list
		sessionFound := false
		for _, sessionData := range listResult.SessionIds {
			if sessionID, exists := sessionData["sessionId"]; exists && sessionID == session.SessionID {
				sessionFound = true
				require.Equal(t, "RUNNING", sessionData["sessionStatus"])
				break
			}
		}
		require.True(t, sessionFound, "Session should be found in RUNNING status list")
		fmt.Printf("  ✓ Session found in RUNNING status list\n")

		// Test using enum with ListByStatus method
		fmt.Printf("Testing ListByStatus with enum...\n")
		_, err = agentBay.ListByStatus(agentbay.SessionStatusRunning, nil, nil, nil)
		require.NoError(t, err)
		fmt.Printf("  ✓ ListByStatus with enum works correctly\n")

		// Test invalid status validation
		fmt.Printf("Testing invalid status validation...\n")
		_, err = agentBay.List("INVALID_STATUS", nil, nil, nil, "")
		require.Error(t, err)
		require.Contains(t, err.Error(), "invalid session status 'INVALID_STATUS'")
		fmt.Printf("  ✓ Invalid status validation works correctly\n")
	})

	fmt.Println("\nTest completed. Session will be kept alive for 5 seconds before deletion.")
	fmt.Println("You can inspect the session during this time.")
	time.Sleep(5 * time.Second)
}

// TestAgentBaySessionStatusEnumFunctionality tests the SessionStatus enum functionality
func TestAgentBaySessionStatusEnumFunctionality(t *testing.T) {
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("TEST: AgentBay SessionStatus Enum Functionality")
	fmt.Println(strings.Repeat("=", 60))

	// Test valid statuses
	validStatuses := []agentbay.SessionStatus{
		agentbay.SessionStatusRunning,
		agentbay.SessionStatusPaused,
		agentbay.SessionStatusPausing,
		agentbay.SessionStatusResuming,
		agentbay.SessionStatusDeleted,
		agentbay.SessionStatusDeleting,
		agentbay.SessionStatusUnknown,
	}

	for _, status := range validStatuses {
		t.Run(fmt.Sprintf("Valid status %s", status), func(t *testing.T) {
			assert.True(t, status.IsValid(), fmt.Sprintf("Status %s should be valid", status))
			assert.NotEmpty(t, status.String(), fmt.Sprintf("Status %s string should not be empty", status))
		})
	}

	// Test invalid status
	t.Run("Invalid status", func(t *testing.T) {
		invalidStatus := agentbay.SessionStatus("INVALID")
		assert.False(t, invalidStatus.IsValid(), "Invalid status should return false")
	})

	// Test GetValidStatuses function
	t.Run("GetValidStatuses function", func(t *testing.T) {
		allValidStatuses := agentbay.GetValidStatuses()
		assert.Len(t, allValidStatuses, 7, "Should return 7 valid statuses")

		for _, status := range allValidStatuses {
			assert.True(t, status.IsValid(), fmt.Sprintf("Status %s from GetValidStatuses should be valid", status))
		}
	})

	fmt.Println("SessionStatus enum tests completed successfully")
}
