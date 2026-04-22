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

// TestContextSyncWithMappingPolicyIntegration tests cross-platform context synchronization with MappingPolicy
// This test simulates: Windows session -> persist data -> Linux session -> access data
func TestContextSyncWithMappingPolicyIntegration(t *testing.T) {
	// Skip in CI environment or if API key is not available
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" || os.Getenv("CI") != "" {
		t.Skip("Skipping integration test: No API key available or running in CI")
	}

	// Initialize the AgentBay client
	ab, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err, "Failed to create AgentBay client")

	// 1. Create a unique context name
	contextName := fmt.Sprintf("test-mapping-policy-%d", time.Now().Unix())
	contextResult, err := ab.Context.Get(contextName, true)
	require.NoError(t, err, "Error getting/creating context")
	require.NotNil(t, contextResult.Context, "Context should not be nil")

	context := contextResult.Context
	t.Logf("Created context: %s (ID: %s)", context.Name, context.ID)

	// Ensure context is deleted after the test
	defer func() {
		deleteContextResult, err := ab.Context.Delete(context)
		if err != nil {
			t.Logf("Warning: Failed to delete context: %v", err)
		} else {
			t.Logf("Context deleted: %s (RequestID: %s)", context.ID, deleteContextResult.RequestID)
		}
	}()

	// Define paths
	windowsPath := "c:\\Users\\Administrator\\Downloads"
	linuxPath := "/home/wuying/下载"
	testFileName := "cross-platform-test.txt"
	testContent := "This file was created in Windows session and should be accessible in Linux session"

	// ========== Phase 1: Create Windows session and persist data ==========
	t.Log("========== Phase 1: Windows Session - Create and Persist Data ==========")

	// Create sync policy for Windows session (no mapping policy needed for first session)
	windowsSyncPolicy := &agentbay.SyncPolicy{
		UploadPolicy:   agentbay.NewUploadPolicy(),
		DownloadPolicy: agentbay.NewDownloadPolicy(),
		DeletePolicy:   agentbay.NewDeletePolicy(),
		ExtractPolicy:  agentbay.NewExtractPolicy(),
	}

	// Create Windows session with context sync
	windowsSessionParams := agentbay.NewCreateSessionParams()
	windowsSessionParams.AddContextSync(context.ID, windowsPath, windowsSyncPolicy)
	windowsSessionParams.WithImageId("windows_latest")
	windowsSessionParams.WithLabels(map[string]string{
		"test": "mapping-policy-windows",
	})

	// Create Windows session
	windowsSessionResult, err := ab.Create(windowsSessionParams)
	require.NoError(t, err, "Error creating Windows session")
	require.NotNil(t, windowsSessionResult.Session, "Windows session should not be nil")

	windowsSession := windowsSessionResult.Session
	t.Logf("Created Windows session: %s", windowsSession.SessionID)

	// Wait for Windows session to be ready
	t.Log("Waiting for Windows session to be ready...")
	time.Sleep(15 * time.Second)

	// Create directory in Windows session
	t.Logf("Creating directory in Windows: %s", windowsPath)
	windowsDirResult, err := windowsSession.FileSystem.CreateDirectory(windowsPath)
	require.NoError(t, err, "Error creating Windows directory")
	assert.NotEmpty(t, windowsDirResult.RequestID, "Windows directory creation request ID should not be empty")

	// Create test file in Windows session
	testFilePath := windowsPath + "\\" + testFileName
	t.Logf("Creating test file in Windows: %s", testFilePath)
	createFileCmd := fmt.Sprintf("echo %s > \"%s\"", testContent, testFilePath)
	windowsCmdResult, err := windowsSession.Command.ExecuteCommand(createFileCmd)
	require.NoError(t, err, "Error creating test file in Windows")
	t.Logf("Windows file creation result: %+v", windowsCmdResult)

	// Verify file exists in Windows session
	verifyFileCmd := fmt.Sprintf("type \"%s\"", testFilePath)
	verifyResult, err := windowsSession.Command.ExecuteCommand(verifyFileCmd)
	require.NoError(t, err, "Error verifying file in Windows")
	t.Logf("Windows file content: %s", verifyResult.Output)
	assert.Contains(t, verifyResult.Output, testContent, "File should contain test content in Windows")

	// Sync Windows session to upload data
	t.Log("Syncing Windows session to upload data...")
	windowsSyncResult, err := windowsSession.Context.Sync()
	require.NoError(t, err, "Error syncing Windows context")
	require.True(t, windowsSyncResult.Success, "Windows context sync should be successful")
	t.Logf("Windows context sync successful (RequestID: %s)", windowsSyncResult.RequestID)

	// Wait for upload to complete
	t.Log("Waiting for upload to complete...")
	time.Sleep(10 * time.Second)

	// Delete Windows session
	t.Log("Deleting Windows session...")
	windowsDeleteResult, err := ab.Delete(windowsSession, true)
	require.NoError(t, err, "Error deleting Windows session")
	t.Logf("Windows session deleted: %s (RequestID: %s)", windowsSession.SessionID, windowsDeleteResult.RequestID)

	// ========== Phase 2: Create Linux session with MappingPolicy and verify data ==========
	t.Log("========== Phase 2: Linux Session - Access Data via MappingPolicy ==========")

	// Create mapping policy with Windows path
	mappingPolicy := &agentbay.MappingPolicy{
		Path: windowsPath,
	}

	// Create sync policy with mapping policy for Linux session
	linuxSyncPolicy := &agentbay.SyncPolicy{
		UploadPolicy:   agentbay.NewUploadPolicy(),
		DownloadPolicy: agentbay.NewDownloadPolicy(),
		DeletePolicy:   agentbay.NewDeletePolicy(),
		ExtractPolicy:  agentbay.NewExtractPolicy(),
		MappingPolicy:  mappingPolicy,
	}

	// Create Linux session with context sync and mapping policy
	linuxSessionParams := agentbay.NewCreateSessionParams()
	linuxSessionParams.AddContextSync(context.ID, linuxPath, linuxSyncPolicy)
	linuxSessionParams.WithImageId("linux_latest")
	linuxSessionParams.WithLabels(map[string]string{
		"test": "mapping-policy-linux",
	})

	// Create Linux session
	linuxSessionResult, err := ab.Create(linuxSessionParams)
	require.NoError(t, err, "Error creating Linux session")
	require.NotNil(t, linuxSessionResult.Session, "Linux session should not be nil")

	linuxSession := linuxSessionResult.Session
	t.Logf("Created Linux session: %s with mapping from %s to %s", linuxSession.SessionID, windowsPath, linuxPath)

	// Ensure Linux session is deleted after the test
	defer func() {
		deleteResult, err := ab.Delete(linuxSession, true)
		if err != nil {
			t.Logf("Warning: Failed to delete Linux session: %v", err)
		} else {
			t.Logf("Linux session deleted: %s (RequestID: %s)", linuxSession.SessionID, deleteResult.RequestID)
		}
	}()

	// Wait for Linux session to be ready and data to be downloaded
	t.Log("Waiting for Linux session to be ready and data to be downloaded...")
	time.Sleep(15 * time.Second)

	// Verify file exists in Linux session at the mapped path
	linuxTestFilePath := linuxPath + "/" + testFileName
	t.Logf("Verifying file exists in Linux at: %s", linuxTestFilePath)

	// Check if file exists
	checkFileCmd := fmt.Sprintf("test -f \"%s\" && echo 'FILE_EXISTS' || echo 'FILE_NOT_FOUND'", linuxTestFilePath)
	checkResult, err := linuxSession.Command.ExecuteCommand(checkFileCmd)
	require.NoError(t, err, "Error checking file existence in Linux")
	t.Logf("Linux file check result: %s", checkResult.Output)

	// Verify file exists
	assert.Contains(t, checkResult.Output, "FILE_EXISTS", "File should exist in Linux session at mapped path")

	// Read file content in Linux session
	readFileCmd := fmt.Sprintf("cat \"%s\"", linuxTestFilePath)
	readResult, err := linuxSession.Command.ExecuteCommand(readFileCmd)
	require.NoError(t, err, "Error reading file in Linux")
	t.Logf("Linux file content: %s", readResult.Output)

	// Verify file content matches
	assert.True(t, strings.Contains(readResult.Output, testContent) || strings.Contains(readResult.Output, strings.TrimSpace(testContent)),
		"File content in Linux should match the content created in Windows")

	// Verify context info
	contextInfo, err := linuxSession.Context.Info()
	require.NoError(t, err, "Error getting context info")
	assert.NotEmpty(t, contextInfo.RequestID, "Request ID should not be empty")

	if len(contextInfo.ContextStatusData) > 0 {
		t.Log("Context status data in Linux session:")
		for i, data := range contextInfo.ContextStatusData {
			t.Logf("Context Status Data [%d]:", i)
			t.Logf("  ContextId: %s", data.ContextId)
			t.Logf("  Path: %s", data.Path)
			t.Logf("  Status: %s", data.Status)
			t.Logf("  TaskType: %s", data.TaskType)
		}

		// Verify the context data
		for _, data := range contextInfo.ContextStatusData {
			if data.ContextId == context.ID {
				assert.Equal(t, linuxPath, data.Path, "Path should match the Linux path")
			}
		}
	}

	t.Log("========== Cross-platform mapping policy test completed successfully ==========")
	t.Log("Data created in Windows session was successfully accessed in Linux session via MappingPolicy")
}
