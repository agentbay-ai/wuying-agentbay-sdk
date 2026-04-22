// ci-stable
package integration

import (
	"fmt"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/require"
)

func getTestAPIKey() string {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("Warning: AGENTBAY_API_KEY environment variable not set. Using default test key.")
		return "akm-xxx" // Replace with your test API key
	}
	return apiKey
}

func generateUniqueId() string {
	timestamp := time.Now().UnixNano()/1000000*1000 + int64(time.Now().Nanosecond()%1000000/1000)
	randomPart := int64(time.Now().Nanosecond() % 10000)
	return fmt.Sprintf("%d-%d", timestamp, randomPart)
}

func TestContextSyncUploadModeIntegration(t *testing.T) {
	apiKey := getTestAPIKey()
	uniqueId := generateUniqueId()
	var testSessions []*agentbay.Session

	t.Logf("Using unique ID for test: %s", uniqueId)

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	// Cleanup function
	defer func() {
		t.Log("Cleaning up: Deleting all test sessions...")
		for _, session := range testSessions {
			if session != nil {
				result, err := client.Delete(session, true)
				if err != nil {
					t.Logf("Warning: Error deleting session %s: %v", session.SessionID, err)
				} else {
					t.Logf("Session %s deleted. Success: %t, Request ID: %s",
						session.SessionID, result.Success, result.RequestID)
				}
			}
		}
	}()

	t.Run("BasicFunctionality", func(t *testing.T) {
		testBasicFunctionality(t, client, uniqueId, &testSessions)
	})

	t.Run("UploadModeValidation", func(t *testing.T) {
		testUploadModeValidation(t, client, uniqueId, &testSessions)
	})

	t.Run("InvalidUploadModeValidation", func(t *testing.T) {
		testInvalidUploadModeValidation(t, client, uniqueId)
	})
}

func testBasicFunctionality(t *testing.T, client *agentbay.AgentBay, uniqueId string, testSessions *[]*agentbay.Session) {
	t.Log("\n=== Testing basic functionality with default File upload mode ===")

	// Step 1: Use context.get method to generate contextId
	contextName := fmt.Sprintf("test-context-%s", uniqueId)
	t.Logf("Creating context with name: %s", contextName)

	contextResult, err := client.Context.Get(contextName, true)
	if err != nil {
		t.Fatalf("Failed to get/create context: %v", err)
	}

	if !contextResult.Success {
		t.Fatalf("Context creation failed: %s", contextResult.ErrorMessage)
	}

	if contextResult.Context == nil {
		t.Fatal("Context is nil")
	}

	t.Logf("Generated contextId: %s", contextResult.Context.ID)
	t.Logf("Context get request ID: %s", contextResult.RequestID)

	// Step 2: Create session with contextSync using default File uploadMode
	syncPolicy := agentbay.NewSyncPolicy() // Uses default uploadMode "File"

	contextSync := &agentbay.ContextSync{
		ContextID: contextResult.Context.ID,
		Path:      "/tmp/test",
		Policy:    syncPolicy,
	}

	sessionParams := &agentbay.CreateSessionParams{
		Labels: map[string]string{
			"test": fmt.Sprintf("upload-mode-%s", uniqueId),
			"type": "basic-functionality",
		},
		ContextSync: []*agentbay.ContextSync{contextSync},
	}

	t.Log("Creating session with default File upload mode...")
	sessionResult, err := client.Create(sessionParams)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}

	// Step 3: Verify session creation success
	if sessionResult == nil {
		t.Fatal("Session result is nil")
	}

	if sessionResult.Session == nil {
		t.Fatal("Session is nil")
	}

	session := sessionResult.Session
	*testSessions = append(*testSessions, session)

	t.Log("✅ Session created successfully!")
	t.Logf("Session ID: %s", session.SessionID)
	t.Logf("Session creation request ID: %s", sessionResult.RequestID)

	// Get session status (GetSession is internal; use GetStatus here)
	sessionInfo, err := session.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session info: %v", err)
	}

	if !sessionInfo.Success {
		t.Fatalf("Get session failed: %s", sessionInfo.ErrorMessage)
	}

	t.Logf("Status: %s", sessionInfo.Status)
	t.Logf("Get status request ID: %s", sessionInfo.RequestID)

	t.Log("✅ All basic functionality tests passed!")
}

func testUploadModeValidation(t *testing.T, client *agentbay.AgentBay, uniqueId string, testSessions *[]*agentbay.Session) {
	t.Log("\n=== Testing contextId and path usage with Archive mode and code execution ===")

	contextName := fmt.Sprintf("archive-mode-context-%s", uniqueId)
	contextResult, err := client.Context.Get(contextName, true)
	if err != nil {
		t.Fatalf("Failed to get/create context: %v", err)
	}

	if !contextResult.Success {
		t.Fatalf("Context creation failed: %s", contextResult.ErrorMessage)
	}

	if contextResult.Context == nil {
		t.Fatal("Context is nil")
	}

	t.Logf("Generated contextId: %s", contextResult.Context.ID)

	// Use NewSyncPolicy and modify uploadMode to Archive
	syncPolicy := agentbay.NewSyncPolicy()
	syncPolicy.UploadPolicy.UploadMode = agentbay.UploadModeArchive // Set uploadMode to Archive

	contextSync, err := agentbay.NewContextSync(
		contextResult.Context.ID,
		"/tmp/archive-mode-test",
		syncPolicy,
	)
	if err != nil {
		t.Fatalf("Failed to create context sync: %v", err)
	}

	if contextSync.ContextID != contextResult.Context.ID {
		t.Errorf("Expected ContextID %s, got %s", contextResult.Context.ID, contextSync.ContextID)
	}

	if contextSync.Path != "/tmp/archive-mode-test" {
		t.Errorf("Expected Path /tmp/archive-mode-test, got %s", contextSync.Path)
	}

	if contextSync.Policy.UploadPolicy.UploadMode != agentbay.UploadModeArchive {
		t.Errorf("Expected UploadMode Archive, got %s", contextSync.Policy.UploadPolicy.UploadMode)
	}

	t.Log("✅ NewContextSync works correctly with contextId and path using Archive mode")

	// Create session with the contextSync
	sessionParams := &agentbay.CreateSessionParams{
		Labels: map[string]string{
			"test": fmt.Sprintf("archive-mode-%s", uniqueId),
			"type": "contextId-path-validation",
		},
		ContextSync: []*agentbay.ContextSync{contextSync},
	}

	t.Log("Creating session with Archive mode contextSync...")
	sessionResult, err := client.Create(sessionParams)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}

	if sessionResult == nil || sessionResult.Session == nil {
		t.Fatal("Session creation failed")
	}

	session := sessionResult.Session
	*testSessions = append(*testSessions, session)

	// Get session status (GetSession is internal; use GetStatus here)
	sessionInfo, err := session.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session info: %v", err)
	}

	if sessionInfo.Success {
		t.Logf("Status: %s", sessionInfo.Status)
	}

	t.Logf("✅ Session created successfully with ID: %s", session.SessionID)
	t.Logf("Session creation request ID: %s", sessionResult.RequestID)

	// Write a 5KB file using FileSystem
	t.Log("Writing 5KB file using FileSystem...")

	// Generate 5KB content (approximately 5120 bytes)
	contentSize := 5 * 1024 // 5KB
	baseContent := "Archive mode test successful! This is a test file created in the session path. "
	repeatedContent := ""
	for len(repeatedContent) < contentSize {
		repeatedContent += baseContent
	}
	fileContent := repeatedContent[:contentSize]

	// Create file path in the session path directory
	filePath := "/tmp/archive-mode-test/test-file-5kb.txt"

	t.Logf("Creating file: %s", filePath)
	t.Logf("File content size: %d bytes", len(fileContent))

	writeResult, err := session.FileSystem.WriteFile(filePath, fileContent, "overwrite")
	if err != nil {
		t.Fatalf("Failed to write file: %v", err)
	}

	// Verify file write success
	if !writeResult.Success {
		t.Fatalf("File write failed: %s", writeResult.RequestID)
	}

	t.Log("✅ File write successful!")
	t.Logf("Write file request ID: %s", writeResult.RequestID)

	// Test context sync and info functionality
	t.Log("Testing context sync functionality...")
	// Call context sync before getting info
	t.Log("Calling context sync before getting info...")
	syncResult, err := session.Context.Sync()
	if err != nil {
		t.Fatalf("Failed to sync context: %v", err)
	}

	if !syncResult.Success {
		t.Fatalf("Context sync failed: %s", syncResult.ErrorMessage)
	}

	t.Log("✅ Context sync successful!")
	t.Logf("Sync request ID: %s", syncResult.RequestID)

	// Now call context info after sync
	t.Log("Calling context info after sync...")
	infoResult, err := session.Context.Info()
	if err != nil {
		t.Fatalf("Failed to get context info: %v", err)
	}

	if !infoResult.Success {
		t.Fatalf("Context info failed: %s", infoResult.ErrorMessage)
	}

	t.Log("✅ Context info successful!")
	t.Logf("Info request ID: %s", infoResult.RequestID)
	t.Logf("Context status data count: %d", len(infoResult.ContextStatusData))

	// Log context status details
	if len(infoResult.ContextStatusData) > 0 {
		t.Log("Context status details:")
		for index, status := range infoResult.ContextStatusData {
			t.Logf("  [%d] ContextId: %s, Path: %s, Status: %s, TaskType: %s",
				index, status.ContextId, status.Path, status.Status, status.TaskType)
		}
	}

	// List files in context sync directory
	t.Log("Listing files in context sync directory...")

	// Use the sync directory path
	syncDirPath := "/tmp/archive-mode-test"

	listResult, err := client.Context.ListFiles(contextResult.Context.ID, syncDirPath, 1, 10)
	if err != nil {
		t.Fatalf("Failed to list files: %v", err)
	}

	// Verify ListFiles success
	if !listResult.Success {
		t.Fatalf("List files failed: %s", listResult.ErrorMessage)
	}

	t.Log("✅ List files successful!")
	t.Logf("List files request ID: %s", listResult.RequestID)
	t.Logf("Total files found: %d", len(listResult.Entries))

	if len(listResult.Entries) > 0 {
		t.Log("📋 Files in context sync directory:")
		for index, entry := range listResult.Entries {
			t.Logf("  [%d] FilePath: %s", index, entry.FilePath)
			t.Logf("      FileType: %s", entry.FileType)
			t.Logf("      FileName: %s", entry.FileName)
			t.Logf("      Size: %d bytes", entry.Size)
		}
	} else {
		t.Log("No files found in context sync directory")
	}

	t.Log("✅ Archive mode contextSync with contextId and path works correctly, and file operations completed successfully")
}

func testInvalidUploadModeValidation(t *testing.T, client *agentbay.AgentBay, uniqueId string) {
	t.Log("\n=== Testing invalid uploadMode validation ===")

	contextName := fmt.Sprintf("invalid-context-%s", uniqueId)
	contextResult, err := client.Context.Get(contextName, true)
	if err != nil {
		t.Fatalf("Failed to get/create context: %v", err)
	}

	if !contextResult.Success {
		t.Fatalf("Context creation failed: %s", contextResult.ErrorMessage)
	}

	// Test with NewContextSync - should return error during validation
	t.Log("Testing invalid uploadMode with NewContextSync...")
	invalidSyncPolicy := agentbay.NewSyncPolicy()
	invalidSyncPolicy.UploadPolicy.UploadMode = agentbay.UploadMode("InvalidMode") // Invalid value

	_, err = agentbay.NewContextSync(
		contextResult.Context.ID,
		"/tmp/test",
		invalidSyncPolicy,
	)

	if err == nil {
		t.Error("Expected error for invalid uploadMode, but got none")
	} else {
		expectedError := "invalid uploadMode value: InvalidMode. Valid values are: \"File\", \"Archive\""
		if err.Error() != expectedError {
			t.Errorf("Expected error message '%s', got '%s'", expectedError, err.Error())
		}
		t.Log("✅ NewContextSync correctly returned error for invalid uploadMode")
	}

	// Test with WithPolicy - should return error during validation
	t.Log("Testing invalid uploadMode with WithPolicy...")
	contextSync := &agentbay.ContextSync{
		ContextID: contextResult.Context.ID,
		Path:      "/tmp/test",
	}

	invalidSyncPolicy2 := agentbay.NewSyncPolicy()
	invalidSyncPolicy2.UploadPolicy.UploadMode = agentbay.UploadMode("WrongValue") // Invalid value

	_, err = contextSync.WithPolicy(invalidSyncPolicy2)

	if err == nil {
		t.Error("Expected error for invalid uploadMode with WithPolicy, but got none")
	} else {
		expectedError := "invalid uploadMode value: WrongValue. Valid values are: \"File\", \"Archive\""
		if err.Error() != expectedError {
			t.Errorf("Expected error message '%s', got '%s'", expectedError, err.Error())
		}
		t.Log("✅ WithPolicy correctly returned error for invalid uploadMode")
	}

	// Test valid uploadMode values
	t.Log("Testing valid uploadMode values...")

	// Test "File" mode
	fileSyncPolicy := agentbay.NewSyncPolicy()
	fileSyncPolicy.UploadPolicy.UploadMode = agentbay.UploadModeFile

	_, err = agentbay.NewContextSync(
		contextResult.Context.ID,
		"/tmp/test-file",
		fileSyncPolicy,
	)

	if err != nil {
		t.Errorf("Unexpected error for 'File' uploadMode: %v", err)
	} else {
		t.Log("✅ 'File' uploadMode accepted successfully")
	}

	// Test "Archive" mode
	archiveSyncPolicy := agentbay.NewSyncPolicy()
	archiveSyncPolicy.UploadPolicy.UploadMode = agentbay.UploadModeArchive

	_, err = agentbay.NewContextSync(
		contextResult.Context.ID,
		"/tmp/test-archive",
		archiveSyncPolicy,
	)

	if err != nil {
		t.Errorf("Unexpected error for 'Archive' uploadMode: %v", err)
	} else {
		t.Log("✅ 'Archive' uploadMode accepted successfully")
	}
}

func TestArchiveModeWithExcludePaths(t *testing.T) {
	t.Skip("archiveExcludePaths works in pre-release but not deployed to production yet. Remove this skip after production environment is updated.")

	apiKey := getTestAPIKey()
	uniqueId := generateUniqueId()

	client, err := agentbay.NewAgentBay(apiKey, nil)
	require.NoError(t, err)

	contextName := fmt.Sprintf("archive-exclude-context-%s", uniqueId)
	contextResult, err := client.Context.Get(contextName, true)
	require.NoError(t, err)
	require.True(t, contextResult.Success, contextResult.ErrorMessage)
	require.NotNil(t, contextResult.Context)

	contextID := contextResult.Context.ID
	syncPath := "/tmp/archive-exclude-test"
	t.Logf("contextId=%s syncPath=%s", contextID, syncPath)

	uploadPolicy := agentbay.NewUploadPolicy()
	uploadPolicy.UploadMode = agentbay.UploadModeArchive
	uploadPolicy.ArchiveExcludePaths = []string{"important/", "config.json"}

	syncPolicy := agentbay.NewSyncPolicy()
	syncPolicy.UploadPolicy = uploadPolicy

	contextSync, err := agentbay.NewContextSync(contextID, syncPath, syncPolicy)
	require.NoError(t, err)

	sessionParams := &agentbay.CreateSessionParams{
		Labels: map[string]string{
			"test": fmt.Sprintf("archive-exclude-%s", uniqueId),
			"type": "archive-exclude-paths",
		},
		ContextSync: []*agentbay.ContextSync{contextSync},
	}

	t.Log("Creating session with Archive mode + exclude paths...")
	sessionResult, err := client.Create(sessionParams)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session

	// Cleanup in case of failure
	defer func() {
		if session != nil {
			_, _ = client.Delete(session, true)
		}
	}()

	// Create directory structure
	_, err = session.FileSystem.CreateDirectory(syncPath + "/important")
	require.NoError(t, err)
	_, err = session.FileSystem.CreateDirectory(syncPath + "/regular")
	require.NoError(t, err)

	// Write files: some in excluded paths, some not
	writeImportant, err := session.FileSystem.WriteFile(syncPath+"/important/data.txt", "This file should be stored individually via FILE mode", "overwrite")
	require.NoError(t, err)
	require.True(t, writeImportant.Success)

	writeConfig, err := session.FileSystem.WriteFile(syncPath+"/config.json", `{"key": "value", "setting": true}`, "overwrite")
	require.NoError(t, err)
	require.True(t, writeConfig.Success)

	writeRegular, err := session.FileSystem.WriteFile(syncPath+"/regular/data.txt", "This file should be archived with the rest", "overwrite")
	require.NoError(t, err)
	require.True(t, writeRegular.Success)

	t.Log("All files written successfully")

	// Delete session with sync to trigger upload
	delResult, err := client.Delete(session, true)
	require.NoError(t, err)
	require.NotNil(t, delResult)
	require.True(t, delResult.Success, delResult.ErrorMessage)
	t.Log("Session deleted with sync_context=True")
	session = nil

	// Verify files via list_files (only list root directory like Python)
	listResult, err := client.Context.ListFiles(contextID, syncPath, 1, 20)
	require.NoError(t, err)
	require.True(t, listResult.Success, listResult.ErrorMessage)
	require.Greater(t, len(listResult.Entries), 0, "Should have files after sync")

	t.Logf("Total files found: %d", len(listResult.Entries))
	for i, entry := range listResult.Entries {
		t.Logf("  [%d] FilePath=%s FileName=%s FileType=%s Size=%d",
			i, entry.FilePath, entry.FileName, entry.FileType, entry.Size)
	}

	// Verify excluded files exist as individual entries
	filePaths := make([]string, 0, len(listResult.Entries))
	fileNames := make([]string, 0, len(listResult.Entries))
	for _, entry := range listResult.Entries {
		if entry != nil {
			filePaths = append(filePaths, entry.FilePath)
			fileNames = append(fileNames, entry.FileName)
		}
	}

	hasImportant := false
	hasConfig := false
	for _, p := range filePaths {
		if strings.Contains(p, "important") {
			hasImportant = true
			break
		}
	}
	for _, n := range fileNames {
		if strings.Contains(n, "config.json") {
			hasConfig = true
			break
		}
	}

	t.Logf("Has excluded 'important/' files individually: %v", hasImportant)
	t.Logf("Has excluded 'config.json' individually: %v", hasConfig)

	require.True(t, hasImportant,
		"Expected excluded path 'important/' files to be stored individually (archiveExcludePaths), but got: %v", fileNames)
	require.True(t, hasConfig,
		"Expected excluded file 'config.json' to be stored individually (archiveExcludePaths), but got: %v", fileNames)

	// Note: Go SDK ContextFileEntry doesn't expose presignedUrl/downloadUrl fields yet.
	// Python/TypeScript tests check these properties on excluded files.
	// Once Go SDK adds these fields, we can add similar verification here.

	t.Log("Archive mode with exclude paths test completed successfully")
}
