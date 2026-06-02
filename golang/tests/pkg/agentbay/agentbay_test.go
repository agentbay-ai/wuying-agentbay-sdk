package agentbay_test

import (
	"fmt"
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestNewAgentBay(t *testing.T) {
	// Test with API key provided directly
	testAPIKey := testutil.GetTestAPIKey(t)
	client, err := agentbay.NewAgentBay(testAPIKey)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if client.APIKey != testAPIKey {
		t.Errorf("Expected API key to be '%s', got '%s'", testAPIKey, client.APIKey)
	}

	// Test with API key from environment variable
	os.Setenv("AGENTBAY_API_KEY", "env_api_key")
	defer os.Unsetenv("AGENTBAY_API_KEY")

	client, err = agentbay.NewAgentBay("")
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if client.APIKey != "env_api_key" {
		t.Errorf("Expected API key to be 'env_api_key', got '%s'", client.APIKey)
	}

	// Test with no API key
	os.Unsetenv("AGENTBAY_API_KEY")
	_, err = agentbay.NewAgentBay("")
	if err == nil {
		t.Fatal("Expected error for missing API key, got nil")
	}
}

func TestAgentBay_Create_List_Delete(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session...")
	result, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}

	// Check if RequestID exists
	if result.RequestID == "" {
		t.Logf("Warning: Expected non-empty RequestID")
	} else {
		t.Logf("Request ID: %s", result.RequestID)
	}

	session := result.Session
	t.Logf("Session created with ID: %s", session.SessionID)

	// Ensure session ID is not empty
	if session.SessionID == "" {
		t.Errorf("Expected non-empty session ID")
	}

	// List all sessions
	fmt.Println("Listing sessions...")
	listResult, err := agentBay.List("", nil, nil, nil, "")
	if err != nil {
		t.Fatalf("Error listing sessions: %v", err)
	}

	sessionIds := listResult.SessionIds

	// Ensure at least one session (the one we just created)
	if len(sessionIds) < 1 {
		t.Errorf("Expected at least 1 session, got %d", len(sessionIds))
	}

	// Check if our created session is in the list
	found := false
	for _, sessionData := range sessionIds {
		if sessionID, exists := sessionData["sessionId"]; exists {
			if sessionIDStr, ok := sessionID.(string); ok && sessionIDStr == session.SessionID {
				found = true
				break
			}
		}
	}
	if !found {
		t.Errorf("Created session with ID %s not found in sessions list", session.SessionID)
	}

	// Delete the session
	fmt.Println("Deleting the session...")
	deleteResult, err := agentBay.Delete(session)
	if err != nil {
		t.Fatalf("Error deleting session: %v", err)
	}

	// Check delete result
	if !deleteResult.Success {
		t.Errorf("Delete operation reported as unsuccessful")
	}

	// List sessions again to ensure it's deleted
	listResult, err = agentBay.List("", nil, nil, nil, "")
	if err != nil {
		t.Fatalf("Error listing sessions after deletion: %v", err)
	}

	sessionIds = listResult.SessionIds

	// Check if the deleted session is not in the list
	for _, sessionData := range sessionIds {
		if sessionID, exists := sessionData["sessionId"]; exists {
			if sessionIDStr, ok := sessionID.(string); ok && sessionIDStr == session.SessionID {
				t.Errorf("Session with ID %s still exists after deletion", session.SessionID)
			}
		}
	}
}

// TestAgentBay_List tests the functionality of listing sessions by labels
func TestAgentBay_List(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBayClient, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Define two sets of labels for different sessions
	labelsA := map[string]string{
		"environment": "development",
		"owner":       "team-a",
		"project":     "project-x",
	}

	labelsB := map[string]string{
		"environment": "testing",
		"owner":       "team-b",
		"project":     "project-y",
	}

	// Create session with labels A
	t.Log("Creating session with labels A...")
	paramsA := agentbay.NewCreateSessionParams().WithLabels(labelsA)
	resultA, err := agentBayClient.Create(paramsA)
	if err != nil {
		t.Logf("Error creating session with labels A: %v", err)
		t.Skip("Skipping test as session creation failed")
		return
	}

	sessionA := resultA.Session
	t.Logf("Session A created with ID: %s", sessionA.SessionID)

	// Ensure cleanup of session A
	defer func() {
		t.Log("Cleaning up session A...")
		_, err := agentBayClient.Delete(sessionA)
		if err != nil {
			t.Logf("Warning: Error deleting session A: %v", err)
		}
	}()

	// Create session with labels B
	t.Log("Creating session with labels B...")
	paramsB := agentbay.NewCreateSessionParams().WithLabels(labelsB)
	resultB, err := agentBayClient.Create(paramsB)
	if err != nil {
		t.Logf("Error creating session with labels B: %v", err)
		t.Skip("Skipping test as session creation failed")
		return
	}

	sessionB := resultB.Session
	t.Logf("Session B created with ID: %s", sessionB.SessionID)

	// Ensure cleanup of session B
	defer func() {
		t.Log("Cleaning up session B...")
		_, err := agentBayClient.Delete(sessionB)
		if err != nil {
			t.Logf("Warning: Error deleting session B: %v", err)
		}
	}()

	// Test 1: List all sessions
	t.Log("Listing all sessions...")
	listResult, err := agentBayClient.List("", nil, nil, nil, "")
	if err != nil {
		t.Fatalf("Error listing all sessions: %v", err)
	}

	sessionIds := listResult.SessionIds
	t.Logf("Found %d sessions in total", len(sessionIds))

	// Test 2: List sessions by environment=development label
	t.Log("Listing sessions with environment=development...")
	devLabels := map[string]string{"environment": "development"}
	devResult, err := agentBayClient.List("", devLabels, nil, nil, "")
	if err != nil {
		t.Logf("Error listing sessions by environment=development: %v", err)
	} else {
		devSessionIds := devResult.SessionIds
		t.Logf("Found %d sessions with environment=development", len(devSessionIds))

		// Verify that session A is in the results
		foundSessionA := false
		for _, sessionData := range devSessionIds {
			if sessionID, exists := sessionData["sessionId"]; exists {
				if sessionIDStr, ok := sessionID.(string); ok && sessionIDStr == sessionA.SessionID {
					foundSessionA = true
					break
				}
			}
		}

		if !foundSessionA {
			t.Errorf("Expected to find session A in development environment results")
		}
	}

	// Test 3: List sessions by owner=team-b label
	t.Log("Listing sessions with owner=team-b...")
	teamBLabels := map[string]string{"owner": "team-b"}
	teamBResult, err := agentBayClient.List("", teamBLabels, nil, nil, "")
	if err != nil {
		t.Logf("Error listing sessions by owner=team-b: %v", err)
	} else {
		teamBSessionIds := teamBResult.SessionIds
		t.Logf("Found %d sessions with owner=team-b", len(teamBSessionIds))

		// Verify that session B is in the results
		foundSessionB := false
		for _, sessionData := range teamBSessionIds {
			if sessionID, exists := sessionData["sessionId"]; exists {
				if sessionIDStr, ok := sessionID.(string); ok && sessionIDStr == sessionB.SessionID {
					foundSessionB = true
					break
				}
			}
		}

		if !foundSessionB {
			t.Errorf("Expected to find session B in team-b owner results")
		}
	}

	// Test 4: List sessions with multiple labels (environment=testing AND project=project-y)
	t.Log("Listing sessions with environment=testing AND project=project-y...")
	multiLabels := map[string]string{
		"environment": "testing",
		"project":     "project-y",
	}
	multiResult, err := agentBayClient.List("", multiLabels, nil, nil, "")
	if err != nil {
		t.Logf("Error listing sessions by multiple labels: %v", err)
	} else {
		multiLabelSessionIds := multiResult.SessionIds
		t.Logf("Found %d sessions with environment=testing AND project=project-y", len(multiLabelSessionIds))

		// Verify that session B is in the results and session A is not
		foundSessionA := false
		foundSessionB := false
		for _, sessionData := range multiLabelSessionIds {
			if sessionID, exists := sessionData["sessionId"]; exists {
				if sessionIDStr, ok := sessionID.(string); ok {
					if sessionIDStr == sessionA.SessionID {
						foundSessionA = true
					}
					if sessionIDStr == sessionB.SessionID {
						foundSessionB = true
					}
				}
			}
		}

		if foundSessionA {
			t.Errorf("Did not expect to find session A in multi-label results")
		}
		if !foundSessionB {
			t.Errorf("Expected to find session B in multi-label results")
		}
	}

	// Test 5: List sessions with non-existent label
	t.Log("Listing sessions with non-existent label...")
	nonExistentLabels := map[string]string{"non-existent": "value"}
	nonExistentResult, err := agentBayClient.List("", nonExistentLabels, nil, nil, "")
	if err != nil {
		t.Logf("Error listing sessions by non-existent label: %v", err)
	} else {
		nonExistentSessionIds := nonExistentResult.SessionIds
		t.Logf("Found %d sessions with non-existent label", len(nonExistentSessionIds))
		if len(nonExistentSessionIds) > 0 {
			t.Logf("Warning: Found sessions with non-existent label, this might indicate an issue")
		}
	}

	t.Log("Test completed successfully")
}

// TestAgentBay_CreateSessionWithRecyclePolicy tests creating a session with custom RecyclePolicy
func TestAgentBay_CreateSessionWithRecyclePolicy(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	fmt.Println("Testing session creation with custom RecyclePolicy...")

	// Create custom RecyclePolicy with Lifecycle1Day and default paths
	recyclePolicy := &agentbay.RecyclePolicy{
		Lifecycle: agentbay.Lifecycle1Day,
		Paths:     []string{""}, // Default path (applies to all paths)
	}

	// Validate the RecyclePolicy
	if err := recyclePolicy.Validate(); err != nil {
		t.Fatalf("RecyclePolicy validation failed: %v", err)
	}

	// Create custom SyncPolicy with the RecyclePolicy
	syncPolicy := &agentbay.SyncPolicy{
		UploadPolicy:   agentbay.NewUploadPolicy(),
		DownloadPolicy: agentbay.NewDownloadPolicy(),
		DeletePolicy:   agentbay.NewDeletePolicy(),
		ExtractPolicy:  agentbay.NewExtractPolicy(),
		RecyclePolicy:  recyclePolicy,
		BWList: &agentbay.BWList{
			WhiteLists: []*agentbay.WhiteList{
				{
					Path:         "",
					ExcludePaths: []string{},
				},
			},
		},
	}

	// Create ContextSync with the custom policy
	contextSync, err := agentbay.NewContextSync("test-recycle-context", "/tmp/recycle/path", syncPolicy)
	if err != nil {
		t.Fatalf("Error creating ContextSync: %v", err)
	}

	fmt.Printf("Created ContextSync with RecyclePolicy lifecycle: %s\n", recyclePolicy.Lifecycle)
	fmt.Printf("RecyclePolicy paths: %v\n", recyclePolicy.Paths)

	// Create session parameters with custom RecyclePolicy
	params := agentbay.NewCreateSessionParams().
		WithLabels(map[string]string{
			"test":      "recyclePolicy",
			"lifecycle": "1day",
		}).
		AddContextSyncConfig(contextSync)

	// Create session with custom RecyclePolicy
	fmt.Println("Creating session with custom RecyclePolicy...")
	result, err := agentBay.Create(params)
	if err != nil {
		t.Fatalf("Error creating session with RecyclePolicy: %v", err)
	}

	// Verify SessionResult structure
	if result.RequestID == "" {
		fmt.Println("Warning: Expected non-empty RequestID")
	} else {
		fmt.Printf("Create Session RequestID: %s\n", result.RequestID)
	}

	if result.Session == nil {
		t.Fatalf("Expected session to be created, got nil")
	}

	session := result.Session
	fmt.Printf("Session created successfully with ID: %s\n", session.SessionID)

	// Verify session properties
	if session.SessionID == "" {
		t.Errorf("Expected non-empty session ID")
	}

	// Verify that the session was created with the correct labels
	expectedLabels := map[string]string{
		"test":      "recyclePolicy",
		"lifecycle": "1day",
	}

	// List sessions with the labels to verify they were applied
	listResult, err := agentBay.List("", expectedLabels, nil, nil, "")
	if err != nil {
		fmt.Printf("Warning: Error listing sessions by labels: %v\n", err)
	} else {
		found := false
		for _, sessionData := range listResult.SessionIds {
			if sessionID, exists := sessionData["sessionId"]; exists {
				if sessionIDStr, ok := sessionID.(string); ok && sessionIDStr == session.SessionID {
					found = true
					break
				}
			}
		}
		if !found {
			fmt.Println("Warning: Created session not found in filtered list")
		} else {
			fmt.Println("Session successfully found in filtered list with correct labels")
		}
	}

	// Ensure cleanup
	defer func() {
		fmt.Println("Cleaning up session with custom RecyclePolicy...")
		deleteResult, err := agentBay.Delete(session)
		if err != nil {
			fmt.Printf("Warning: Error deleting session: %v\n", err)
		} else {
			fmt.Printf("Delete Session RequestID: %s\n", deleteResult.RequestID)
		}
	}()

	fmt.Println("Session with custom RecyclePolicy created and verified successfully")
}

// TestRecyclePolicy_InvalidPaths tests invalid paths with wildcards via NewContextSync
func TestRecyclePolicy_InvalidPaths(t *testing.T) {
	fmt.Println("Testing invalid paths with wildcards...")

	// Use only one invalid path instead of for loop
	invalidPath := "/invalid/path/*"

	invalidRecyclePolicy := &agentbay.RecyclePolicy{
		Lifecycle: agentbay.Lifecycle1Day,
		Paths:     []string{invalidPath},
	}

	invalidSyncPolicy := &agentbay.SyncPolicy{
		UploadPolicy:   agentbay.NewUploadPolicy(),
		DownloadPolicy: agentbay.NewDownloadPolicy(),
		DeletePolicy:   agentbay.NewDeletePolicy(),
		ExtractPolicy:  agentbay.NewExtractPolicy(),
		RecyclePolicy:  invalidRecyclePolicy,
		BWList: &agentbay.BWList{
			WhiteLists: []*agentbay.WhiteList{
				{
					Path:         "",
					ExcludePaths: []string{},
				},
			},
		},
	}

	// This should fail at NewContextSync due to validation
	_, err := agentbay.NewContextSync("invalid-path-context", "/tmp/path", invalidSyncPolicy)
	if err == nil {
		t.Errorf("Expected invalid path '%s' to fail NewContextSync validation, but it passed", invalidPath)
	} else {
		fmt.Printf("Invalid path '%s' correctly failed NewContextSync validation: %v\n", invalidPath, err)

		// Verify error message contains expected information
		expectedSubstrings := []string{
			"wildcard patterns are not supported",
			invalidPath,
			"Please use exact directory paths instead",
		}

		for _, substring := range expectedSubstrings {
			if !contains(err.Error(), substring) {
				t.Errorf("Error message for invalid path '%s' should contain '%s', but got: %v", invalidPath, substring, err)
			}
		}
	}

	fmt.Println("Invalid paths with wildcards test completed successfully")
}

// TestRecyclePolicy_CombinedInvalid tests combination of invalid Lifecycle and invalid paths via NewContextSync
func TestRecyclePolicy_CombinedInvalid(t *testing.T) {
	fmt.Println("Testing combination of invalid Lifecycle and invalid paths...")

	combinedInvalidRecyclePolicy := &agentbay.RecyclePolicy{
		Lifecycle: "invalid_lifecycle",
		Paths:     []string{"/invalid/path/*"},
	}

	combinedInvalidSyncPolicy := &agentbay.SyncPolicy{
		UploadPolicy:   agentbay.NewUploadPolicy(),
		DownloadPolicy: agentbay.NewDownloadPolicy(),
		DeletePolicy:   agentbay.NewDeletePolicy(),
		ExtractPolicy:  agentbay.NewExtractPolicy(),
		RecyclePolicy:  combinedInvalidRecyclePolicy,
		BWList: &agentbay.BWList{
			WhiteLists: []*agentbay.WhiteList{
				{
					Path:         "",
					ExcludePaths: []string{},
				},
			},
		},
	}

	// This should fail at NewContextSync due to validation
	_, err := agentbay.NewContextSync("combined-invalid-context", "/tmp/path", combinedInvalidSyncPolicy)
	if err == nil {
		t.Errorf("Expected policy with both invalid lifecycle and invalid path to fail NewContextSync validation, but it passed")
	} else {
		fmt.Printf("Policy with both invalid lifecycle and invalid path correctly failed NewContextSync validation: %v\n", err)
		// Should fail on lifecycle validation first
		if !contains(err.Error(), "invalid lifecycle value") {
			t.Errorf("Expected error to mention invalid lifecycle value, but got: %v", err)
		}
	}

	fmt.Println("Combined invalid configuration test completed successfully")
}

// Helper function to check if a string contains a substring
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(substr) == 0 ||
		(len(s) > len(substr) && (s[:len(substr)] == substr || s[len(s)-len(substr):] == substr ||
			func() bool {
				for i := 0; i <= len(s)-len(substr); i++ {
					if s[i:i+len(substr)] == substr {
						return true
					}
				}
				return false
			}())))
}

// TestAgentBay_Create_DoesNotModifyParams tests that Create() method does not modify the original params object
func TestAgentBay_Create_DoesNotModifyParams(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create params with context syncs
	params := agentbay.NewCreateSessionParams()
	params.Labels = map[string]string{"env": "test"}

	// Create context syncs
	contextSync1 := &agentbay.ContextSync{
		ContextID: "ctx-1",
		Path:      "/path1",
	}
	contextSync2 := &agentbay.ContextSync{
		ContextID: "ctx-2",
		Path:      "/path2",
	}
	params.ContextSync = []*agentbay.ContextSync{contextSync1, contextSync2}

	// Store original values
	originalLabels := make(map[string]string)
	for k, v := range params.Labels {
		originalLabels[k] = v
	}
	originalContextSyncs := make([]*agentbay.ContextSync, len(params.ContextSync))
	copy(originalContextSyncs, params.ContextSync)
	originalLabelsPtr := &params.Labels
	originalContextSyncsPtr := &params.ContextSync

	// Create a session (this may fail in unit test without API key, but we can still check params are not modified)
	// The important part is that params should not be modified even if the API call fails
	_, err = agentBay.Create(params)
	// We don't care about the error here - we just want to verify params wasn't modified
	_ = err

	// Verify the original params object was not modified
	if len(params.Labels) != len(originalLabels) {
		t.Errorf("Labels map length changed: expected %d, got %d", len(originalLabels), len(params.Labels))
	}
	for k, v := range originalLabels {
		if params.Labels[k] != v {
			t.Errorf("Label %s was modified: expected %s, got %s", k, v, params.Labels[k])
		}
	}
	if &params.Labels != originalLabelsPtr {
		t.Error("Labels map pointer was replaced (should be the same object)")
	}
	if len(params.ContextSync) != len(originalContextSyncs) {
		t.Errorf("ContextSync slice length changed: expected %d, got %d", len(originalContextSyncs), len(params.ContextSync))
	}
	if &params.ContextSync != originalContextSyncsPtr {
		t.Error("ContextSync slice pointer was replaced (should be the same object)")
	}
	for i, originalCS := range originalContextSyncs {
		if params.ContextSync[i].ContextID != originalCS.ContextID {
			t.Errorf("ContextSync[%d].ContextID was modified: expected %s, got %s", i, originalCS.ContextID, params.ContextSync[i].ContextID)
		}
		if params.ContextSync[i].Path != originalCS.Path {
			t.Errorf("ContextSync[%d].Path was modified: expected %s, got %s", i, originalCS.Path, params.ContextSync[i].Path)
		}
	}
}

// TestAgentBay_Create_WithMobileSimulate_DoesNotModifyParams tests that Create() method does not modify params when mobile simulate config is provided
func TestAgentBay_Create_WithMobileSimulate_DoesNotModifyParams(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create params with mobile simulate config
	params := agentbay.NewCreateSessionParams()
	params.Labels = map[string]string{"env": "test"}

	// Create mobile simulate config
	simulateConfig := &models.MobileSimulateConfig{
		SimulatedContextID: "mobile-sim-ctx-123",
		Simulate:           false,
	}
	mobileConfig := &models.MobileExtraConfig{
		SimulateConfig: simulateConfig,
	}
	extraConfigs := &models.ExtraConfigs{
		Mobile: mobileConfig,
	}
	params.ExtraConfigs = extraConfigs

	// Store original values
	originalLabels := make(map[string]string)
	for k, v := range params.Labels {
		originalLabels[k] = v
	}
	originalContextSyncs := params.ContextSync
	originalLabelsPtr := &params.Labels
	originalContextSyncsPtr := &params.ContextSync

	// Create a session (this may fail in unit test without API key, but we can still check params are not modified)
	// The important part is that params should not be modified even if the API call fails
	_, err = agentBay.Create(params)
	// We don't care about the error here - we just want to verify params wasn't modified
	_ = err

	// Verify the original params object was not modified
	if len(params.Labels) != len(originalLabels) {
		t.Errorf("Labels map length changed: expected %d, got %d", len(originalLabels), len(params.Labels))
	}
	for k, v := range originalLabels {
		if params.Labels[k] != v {
			t.Errorf("Label %s was modified: expected %s, got %s", k, v, params.Labels[k])
		}
	}
	if &params.Labels != originalLabelsPtr {
		t.Error("Labels map pointer was replaced (should be the same object)")
	}
	if params.ContextSync != nil && originalContextSyncs == nil {
		t.Error("ContextSync was initialized when it should remain nil")
	}
	if params.ContextSync == nil && originalContextSyncs != nil {
		t.Error("ContextSync was set to nil when it should remain initialized")
	}
	if &params.ContextSync != originalContextSyncsPtr {
		t.Error("ContextSync slice pointer was replaced (should be the same object)")
	}
}
