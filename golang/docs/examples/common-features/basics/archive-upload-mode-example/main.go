package main

import (
	"fmt"
	"math/rand"
	"os"
	"strings"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	fmt.Println("🚀 AgentBay Archive Upload Mode Context Sync Example")
	fmt.Println(strings.Repeat("=", 60))

	// Get API key from environment variable or use a default value for testing
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "your-api-key-here" // Replace with your actual API key
		fmt.Println("Warning: AGENTBAY_API_KEY environment variable not set. Using default key.")
	}

	// Initialize the AgentBay client
	ab, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("❌ Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	uniqueID := generateUniqueID()

	// Execute archive upload mode example
	if err := archiveUploadModeExample(ab, uniqueID); err != nil {
		fmt.Printf("❌ Example execution failed: %v\n", err)
		os.Exit(1)
	}

	if err := archiveExcludePathsExample(ab, uniqueID); err != nil {
		fmt.Printf("❌ Example execution failed: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("✅ Archive upload mode example completed")
}

func generateUniqueID() string {
	timestamp := time.Now().UnixNano()/1000000 + int64(rand.Intn(1000))
	randomPart := rand.Intn(10000)
	return fmt.Sprintf("%d-%d", timestamp, randomPart)
}

func archiveUploadModeExample(ab *agentbay.AgentBay, uniqueID string) error {
	fmt.Println("\n📦 === Archive Upload Mode Context Sync Example ===")

	var session *agentbay.Session

	defer func() {
		// Step 8: Cleanup
		if session != nil {
			fmt.Println("\n🧹 Step 8: Cleaning up session...")
			deleteResult, err := ab.Delete(session)
			if err != nil {
				fmt.Printf("❌ Failed to delete session: %v\n", err)
			} else {
				fmt.Printf("✅ Session deleted successfully!\n")
				fmt.Printf("   Success: %t\n", deleteResult.Success)
				fmt.Printf("   Request ID: %s\n", deleteResult.RequestID)
			}
		}
	}()

	// Step 1: Create context for Archive mode
	fmt.Println("\n📦 Step 1: Creating context for Archive upload mode...")
	contextName := fmt.Sprintf("archive-mode-context-%s", uniqueID)
	contextResult, err := ab.Context.Get(contextName, true)
	if err != nil {
		return fmt.Errorf("context creation failed: %v", err)
	}

	fmt.Printf("✅ Context created successfully!\n")
	fmt.Printf("   Context ID: %s\n", contextResult.ContextID)
	fmt.Printf("   Request ID: %s\n", contextResult.RequestID)

	// Step 2: Configure sync policy with Archive upload mode
	fmt.Println("\n⚙️  Step 2: Configuring sync policy with Archive upload mode...")
	uploadPolicy := &agentbay.UploadPolicy{
		UploadMode: agentbay.UploadModeArchive, // Set to Archive mode
	}
	syncPolicy := &agentbay.SyncPolicy{
		UploadPolicy: uploadPolicy,
	}

	fmt.Printf("✅ Sync policy configured with uploadMode: %s\n", syncPolicy.UploadPolicy.UploadMode)

	// Step 3: Create context sync configuration
	fmt.Println("\n🔧 Step 3: Creating context sync configuration...")
	contextSync := &agentbay.ContextSync{
		ContextID: contextResult.ContextID,
		Path:      "/tmp/archive-mode-test",
		Policy:    syncPolicy,
	}

	fmt.Printf("✅ Context sync created:\n")
	fmt.Printf("   Context ID: %s\n", contextSync.ContextID)
	fmt.Printf("   Path: %s\n", contextSync.Path)
	fmt.Printf("   Upload Mode: %s\n", contextSync.Policy.UploadPolicy.UploadMode)

	// Step 4: Create session with Archive mode context sync
	fmt.Println("\n🏗️  Step 4: Creating session with Archive mode context sync...")
	sessionParams := agentbay.NewCreateSessionParams().
		WithLabels(map[string]string{
			"example":    fmt.Sprintf("archive-mode-%s", uniqueID),
			"type":       "archive-upload-demo",
			"uploadMode": "Archive",
		}).
		WithContextSync([]*agentbay.ContextSync{contextSync})

	sessionResult, err := ab.Create(sessionParams)
	if err != nil {
		return fmt.Errorf("session creation failed: %v", err)
	}

	session = sessionResult.Session
	fmt.Printf("✅ Session created successfully!\n")
	fmt.Printf("   Session ID: %s\n", session.SessionID)
	fmt.Printf("   Request ID: %s\n", sessionResult.RequestID)

	// Get session status
	sessionInfo, err := session.GetStatus()
	if err == nil && sessionInfo.Success {
		fmt.Printf("   Status: %s\n", sessionInfo.Status)
	}

	// Step 5: Create and write test files
	fmt.Println("\n📝 Step 5: Creating test files in Archive mode context...")

	// Generate 5KB test content
	contentSize := 5 * 1024 // 5KB
	baseContent := "Archive mode test successful! This is a test file created in the session path. "
	repeatedContent := strings.Repeat(baseContent, (contentSize/len(baseContent))+1)
	fileContent := repeatedContent[:contentSize]

	filePath := "/tmp/archive-mode-test/test-file-5kb.txt"

	fmt.Printf("📄 Creating file: %s\n", filePath)
	fmt.Printf("📊 File content size: %d bytes\n", len(fileContent))

	writeResult, err := session.FileSystem.WriteFile(filePath, fileContent, "overwrite")
	if err != nil {
		return fmt.Errorf("file write failed: %v", err)
	}

	fmt.Printf("✅ File write successful!\n")
	fmt.Printf("   Request ID: %s\n", writeResult.RequestID)

	// Step 6: Test context sync functionality
	fmt.Println("\n🔄 Step 6: Testing context sync functionality...")
	syncResult, err := session.Context.Sync()
	if err != nil {
		return fmt.Errorf("context sync failed: %v", err)
	}

	fmt.Printf("✅ Context sync successful!\n")
	fmt.Printf("   Request ID: %s\n", syncResult.RequestID)

	// Step 6.5: Test context info functionality after sync
	fmt.Println("\n📊 Step 6.5: Testing context info functionality after sync...")
	infoResult, err := session.Context.Info()
	if err != nil {
		return fmt.Errorf("context info failed: %v", err)
	}

	fmt.Printf("✅ Context info retrieved successfully!\n")
	fmt.Printf("   Request ID: %s\n", infoResult.RequestID)
	fmt.Printf("   Context status data count: %d\n", len(infoResult.ContextStatusData))

	// Display context status details
	if len(infoResult.ContextStatusData) > 0 {
		fmt.Println("\n📋 Context status details:")
		for index, status := range infoResult.ContextStatusData {
			fmt.Printf("   [%d] Context ID: %s\n", index, status.ContextId)
			fmt.Printf("       Path: %s\n", status.Path)
			fmt.Printf("       Status: %s\n", status.Status)
			fmt.Printf("       Task Type: %s\n", status.TaskType)
			if status.ErrorMessage != "" {
				fmt.Printf("       Error: %s\n", status.ErrorMessage)
			}
		}
	}

	// Step 7: List files in context sync directory
	fmt.Println("\n🔍 Step 7: Listing files in context sync directory...")

	// Use the sync directory path
	syncDirPath := "/tmp/archive-mode-test"

	maxResultsBasic := int32(10)
	listResult, err := ab.Context.ListFilesWithPagination(contextResult.ContextID, syncDirPath, &maxResultsBasic, nil)
	if err != nil {
		return fmt.Errorf("list files failed: %v", err)
	}

	// Verify listing success
	if !listResult.Success {
		return fmt.Errorf("list files failed: %s", listResult.ErrorMessage)
	}

	fmt.Printf("✅ List files successful!\n")
	fmt.Printf("   Request ID: %s\n", listResult.RequestID)
	fmt.Printf("   Total files found: %d\n", len(listResult.Entries))
	if listResult.NextToken != "" {
		fmt.Printf("   NextToken: present\n")
	}

	if len(listResult.Entries) > 0 {
		fmt.Println("\n📋 Files in context sync directory:")
		for index, entry := range listResult.Entries {
			fmt.Printf("   [%d] FilePath: %s\n", index, entry.FilePath)
			fmt.Printf("       FileType: %s\n", entry.FileType)
			fmt.Printf("       FileName: %s\n", entry.FileName)
			fmt.Printf("       Size: %d bytes\n", entry.Size)
		}
	} else {
		fmt.Println("   No files found in context sync directory")
	}

	fmt.Println("\n🎉 Archive upload mode example completed successfully!")
	fmt.Println("✅ All operations completed without errors.")

	return nil
}

func archiveExcludePathsExample(ab *agentbay.AgentBay, uniqueID string) error {
	fmt.Println("\n📂 === Archive Upload Mode with archiveExcludePaths Example ===")

	var session *agentbay.Session

	defer func() {
		if session != nil {
			fmt.Println("\n🧹 Cleaning up exclude-paths session...")
			deleteResult, err := ab.Delete(session, true)
			if err != nil {
				fmt.Printf("❌ Failed to delete session: %v\n", err)
			} else {
				fmt.Printf("✅ Session deleted successfully!\n")
				fmt.Printf("   Success: %t\n", deleteResult.Success)
				fmt.Printf("   Request ID: %s\n", deleteResult.RequestID)
			}
		}
	}()

	fmt.Println("\n📦 Step 1: Creating context for Archive + exclude paths...")
	contextName := fmt.Sprintf("archive-exclude-context-%s", uniqueID)
	contextResult, err := ab.Context.Get(contextName, true)
	if err != nil {
		return fmt.Errorf("context creation failed: %v", err)
	}

	fmt.Printf("✅ Context ID: %s\n", contextResult.ContextID)

	fmt.Println("\n⚙️  Step 2: Configuring upload policy with ArchiveExcludePaths...")
	uploadPolicy := agentbay.NewUploadPolicy()
	uploadPolicy.UploadMode = agentbay.UploadModeArchive
	uploadPolicy.ArchiveExcludePaths = []string{"important/", "config.json"}
	syncPolicy := &agentbay.SyncPolicy{
		UploadPolicy: uploadPolicy,
	}

	syncBase := "/tmp/archive-exclude-test"
	fmt.Printf("✅ archiveExcludePaths: %v\n", uploadPolicy.ArchiveExcludePaths)

	fmt.Println("\n🔧 Step 3: Creating context sync configuration...")
	contextSync := &agentbay.ContextSync{
		ContextID: contextResult.ContextID,
		Path:      syncBase,
		Policy:    syncPolicy,
	}

	fmt.Println("\n🏗️  Step 4: Creating session...")
	sessionParams := agentbay.NewCreateSessionParams().
		WithLabels(map[string]string{
			"example":    fmt.Sprintf("archive-exclude-%s", uniqueID),
			"type":       "archive-exclude-demo",
			"uploadMode": "Archive",
		}).
		WithContextSync([]*agentbay.ContextSync{contextSync})

	sessionResult, err := ab.Create(sessionParams)
	if err != nil {
		return fmt.Errorf("session creation failed: %v", err)
	}

	session = sessionResult.Session
	fmt.Printf("✅ Session ID: %s\n", session.SessionID)

	fmt.Println("\n📝 Step 5: Writing excluded and non-excluded files...")
	if _, err := session.FileSystem.CreateDirectory(syncBase + "/important"); err != nil {
		return fmt.Errorf("create_directory important failed: %v", err)
	}
	if _, err := session.FileSystem.CreateDirectory(syncBase + "/regular"); err != nil {
		return fmt.Errorf("create_directory regular failed: %v", err)
	}

	if _, err := session.FileSystem.WriteFile(syncBase+"/important/data.txt",
		"Excluded path: stored individually when possible.", "overwrite"); err != nil {
		return fmt.Errorf("write important/data.txt failed: %v", err)
	}
	if _, err := session.FileSystem.WriteFile(syncBase+"/config.json",
		`{"key":"value"}`, "overwrite"); err != nil {
		return fmt.Errorf("write config.json failed: %v", err)
	}
	if _, err := session.FileSystem.WriteFile(syncBase+"/regular/data.txt",
		"Regular path: eligible for bulk archive packaging.", "overwrite"); err != nil {
		return fmt.Errorf("write regular/data.txt failed: %v", err)
	}

	fmt.Println("\n🔄 Step 6: Syncing context...")
	syncResult, err := session.Context.Sync()
	if err != nil {
		return fmt.Errorf("context sync failed: %v", err)
	}
	fmt.Printf("✅ Context sync OK (request %s)\n", syncResult.RequestID)

	fmt.Println("\n🔍 Step 7: Listing files...")
	maxResultsExclude := int32(20)
	listResult, err := ab.Context.ListFilesWithPagination(contextResult.ContextID, syncBase, &maxResultsExclude, nil)
	if err != nil {
		return fmt.Errorf("list files failed: %v", err)
	}
	if !listResult.Success {
		return fmt.Errorf("list files failed: %s", listResult.ErrorMessage)
	}

	fmt.Printf("✅ Listed %d entries\n", len(listResult.Entries))
	for index, entry := range listResult.Entries {
		fmt.Printf("   [%d] %s (%s, %d bytes)\n", index, entry.FilePath, entry.FileName, entry.Size)
	}

	fmt.Println("\n🎉 archiveExcludePaths example completed successfully!")
	return nil
}
