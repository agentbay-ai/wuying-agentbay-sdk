// ci-stable
package integration_test

import (
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

// TestListGetDeleteWorkflow demonstrates List -> Get -> Delete workflow
func TestListGetDeleteWorkflow(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	t.Log(strings.Repeat("=", 80))
	t.Log("LIST -> GET -> DELETE WORKFLOW TEST")
	t.Log("Step 1: List all sessions | Step 2: Get each session | Step 3: Delete each")
	t.Log(strings.Repeat("=", 80))

	// Step 1: List all sessions
	t.Log("\n[STEP 1] Listing all sessions using agentbay.List()...")
	t.Log(strings.Repeat("─", 80))

	listResult, err := client.List("", nil, nil, nil, "")
	if err != nil {
		t.Fatalf("Failed to list sessions: %v", err)
	}

	sessionIDs := listResult.SessionIds
	totalCount := listResult.TotalCount

	t.Logf("✅ Listed sessions successfully!")
	t.Logf("   Total sessions in system: %d", totalCount)
	t.Logf("   Sessions returned: %d", len(sessionIDs))
	t.Logf("   Request ID: %s", listResult.RequestID)

	if len(sessionIDs) == 0 {
		t.Log("ℹ️  No sessions found. Test completed.")
		return
	}

	// Step 2: Retrieve each session using agentbay.Get()
	t.Log("\n[STEP 2] Getting each session using agentbay.Get()...")
	t.Log(strings.Repeat("─", 80))

	sessions := make([]*agentbay.Session, 0)

	for i, sessionData := range sessionIDs {
		// Extract sessionId from the map
		sessionID, ok := sessionData["sessionId"].(string)
		if !ok {
			t.Logf("\n  [%d/%d] ⚠️  Invalid session data: sessionId not found or not a string", i+1, len(sessionIDs))
			continue
		}

		t.Logf("\n  [%d/%d] Getting session: %s", i+1, len(sessionIDs), sessionID)

		getResult, err := client.Get(sessionID)
		if err != nil {
			t.Logf("     ⚠️  Failed to get session: %v", err)
			continue
		}

		if getResult.Session == nil {
			t.Logf("     ⚠️  Retrieved session is nil")
			continue
		}

		sessions = append(sessions, getResult.Session)

		t.Logf("     ✅ Successfully retrieved!")
		t.Logf("        • Session ID: %s", getResult.Session.SessionID)
		t.Logf("        • Resource URL: %s", getResult.Session.ResourceUrl)
		t.Logf("        • Request ID: %s", getResult.RequestID)
	}

	retrievedCount := len(sessions)
	t.Logf("\n✅ Successfully retrieved %d out of %d sessions", retrievedCount, len(sessionIDs))

	// Step 3: Delete each retrieved session using session.Delete()
	t.Log("\n[STEP 3] Deleting each session using session.Delete()...")
	t.Log(strings.Repeat("─", 80))

	successCount := 0
	failureCount := 0

	for i, session := range sessions {
		t.Logf("\n  [%d/%d] Deleting session: %s", i+1, len(sessions), session.SessionID)

		deleteResult, err := session.Delete()
		if err != nil {
			t.Logf("     ❌ Failed to delete session: %v", err)
			failureCount++
			continue
		}

		if !deleteResult.Success {
			t.Logf("     ❌ Delete operation failed")
			failureCount++
			continue
		}

		successCount++
		t.Logf("     ✅ Successfully deleted!")
		t.Logf("        • Request ID: %s", deleteResult.RequestID)
	}

	// Summary
	t.Log("\n" + strings.Repeat("=", 80))
	t.Log("TEST SUMMARY")
	t.Log(strings.Repeat("=", 80))
	t.Logf("Sessions listed:        %d", len(sessionIDs))
	t.Logf("Sessions retrieved:     %d", retrievedCount)
	t.Logf("Sessions deleted:       %d", successCount)
	t.Logf("Failures:               %d", failureCount)
	t.Log(strings.Repeat("=", 80))

	if successCount > 0 {
		t.Logf("\n✅ Workflow completed! Deleted %d sessions.\n", successCount)
	}
}
