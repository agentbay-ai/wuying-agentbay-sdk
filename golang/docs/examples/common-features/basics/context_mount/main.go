package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	fmt.Println("📌 AgentBay Context Mount Example")

	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "akm-xxx"
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		log.Fatalf("Failed to create AgentBay client: %v", err)
	}

	if err := contextMountDemo(agentBay); err != nil {
		log.Fatalf("❌ Example execution failed: %v", err)
	}

	fmt.Println("✅ Context mount example completed")
}

func contextMountDemo(ab *agentbay.AgentBay) error {
	fmt.Println("\n🔄 === Context Mount Demonstration ===")

	// Step 1: Create a context
	fmt.Println("\n📦 Step 1: Creating context for persistent storage...")
	contextName := fmt.Sprintf("mount-demo-%d", time.Now().Unix())
	contextResult, err := ab.Context.Get(contextName, true)
	if err != nil {
		return fmt.Errorf("context creation failed: %v", err)
	}
	if contextResult.Context == nil {
		return fmt.Errorf("context not found and could not be created")
	}

	ctx := contextResult.Context
	fmt.Printf("✅ Context created: %s (name: %s)\n", ctx.ID, ctx.Name)

	// Step 2: Create first session with context mount
	fmt.Println("\n🔧 Step 2: Creating first session with context mount...")
	contextMount := agentbay.NewContextMount(ctx.ID, "/tmp/mounted_data")

	params1 := agentbay.NewCreateSessionParams()
	params1.AddContextMount(contextMount)
	params1.WithLabels(map[string]string{
		"example": "context-mount",
		"phase":   "first-session",
	})

	session1Result, err := ab.Create(params1)
	if err != nil {
		return fmt.Errorf("first session creation failed: %v", err)
	}

	session1 := session1Result.Session
	fmt.Printf("✅ First session created: %s\n", session1.SessionID)

	session1ID := session1.SessionID

	// Step 3: Write data — persisted immediately via write-through
	fmt.Println("\n💾 Step 3: Writing data (write-through persistence)...")

	_, err = session1.Command.ExecuteCommand("mkdir -p /tmp/mounted_data/config")
	if err != nil {
		log.Printf("Warning: Failed to create directory: %v", err)
	}

	configData := map[string]interface{}{
		"app":     "mount-demo",
		"version": "1.0",
		"session": session1.SessionID,
	}
	configJSON, _ := json.MarshalIndent(configData, "", "  ")

	configResult, err := session1.FileSystem.WriteFile("/tmp/mounted_data/config/app.json", string(configJSON), "overwrite")
	if err != nil {
		log.Printf("❌ Failed to write config: %v", err)
	} else if configResult.Success {
		fmt.Println("✅ Config file written (persisted immediately)")
	}

	dataResult, err := session1.FileSystem.WriteFile("/tmp/mounted_data/notes.txt",
		"This data is persisted via Context Mount.\nNo manual sync() call needed!", "overwrite")
	if err != nil {
		log.Printf("❌ Failed to write data: %v", err)
	} else if dataResult.Success {
		fmt.Println("✅ Data file written (persisted immediately)")
	}

	// List files
	fmt.Println("\n📋 Files in mounted path:")
	listResult, err := session1.Command.ExecuteCommand("find /tmp/mounted_data -type f -ls")
	if err == nil {
		fmt.Println(listResult.Output)
	}

	// No sync needed — data is already persisted
	fmt.Println("\n🧹 Deleting first session (no sync needed for mount)...")
	deleteResult1, err := ab.Delete(session1, false)
	if err != nil {
		log.Printf("❌ First session deletion failed: %v", err)
	} else if deleteResult1.Success {
		fmt.Println("✅ First session deleted")
	}

	// Step 4: Create second session to verify persistence
	fmt.Println("\n🔧 Step 4: Creating second session to verify persistence...")

	params2 := agentbay.NewCreateSessionParams()
	params2.AddContextMount(contextMount)
	params2.WithLabels(map[string]string{
		"example": "context-mount",
		"phase":   "second-session",
	})

	session2Result, err := ab.Create(params2)
	if err != nil {
		return fmt.Errorf("second session creation failed: %v", err)
	}

	session2 := session2Result.Session
	fmt.Printf("✅ Second session created: %s\n", session2.SessionID)

	// Step 5: Verify persisted data
	fmt.Println("\n🔍 Step 5: Verifying persisted data in second session...")

	filesToCheck := []string{
		"/tmp/mounted_data/config/app.json",
		"/tmp/mounted_data/notes.txt",
	}

	filesFound := 0
	for _, filePath := range filesToCheck {
		fmt.Printf("\n🔍 Checking: %s\n", filePath)
		readResult, err := session2.FileSystem.ReadFile(filePath)
		if err != nil {
			fmt.Printf("❌ Not found: %v\n", err)
		} else {
			fmt.Println("✅ File found!")
			content := readResult.Content
			if len(content) > 120 {
				content = content[:120]
			}
			fmt.Printf("   📄 Content: %s\n", content)
			filesFound++
		}
	}

	// Step 6: Dynamic mount demo (Mount)
	fmt.Println("\n🔧 Step 6: Dynamic mount using Mount()...")
	dynamicCtxResult, err := ab.Context.Get(fmt.Sprintf("dynamic-mount-%d", time.Now().Unix()), true)
	if err == nil && dynamicCtxResult.Context != nil {
		dynamicMount := agentbay.NewContextMount(dynamicCtxResult.Context.ID, "/tmp/dynamic_mount")
		bindResult, err := session2.Context.Mount(dynamicMount)
		if err != nil {
			log.Printf("❌ Dynamic mount failed: %v", err)
		} else if bindResult.Success {
			fmt.Println("✅ Dynamic mount bound successfully")
			writeResult, err := session2.FileSystem.WriteFile("/tmp/dynamic_mount/dynamic.txt", "Dynamically mounted data!", "overwrite")
			if err == nil && writeResult.Success {
				fmt.Println("✅ Wrote to dynamically mounted path")
			}
		}

		// Clean up dynamic context
		ab.Context.Delete(dynamicCtxResult.Context)
	}

	// Summary
	fmt.Println("\n📊 === Persistence Summary ===")
	fmt.Printf("✅ Context ID: %s\n", ctx.ID)
	fmt.Printf("✅ Session 1: %s (deleted)\n", session1ID)
	fmt.Printf("✅ Session 2: %s (active)\n", session2.SessionID)
	fmt.Printf("✅ Files found: %d/%d\n", filesFound, len(filesToCheck))

	if filesFound == len(filesToCheck) {
		fmt.Println("🎉 Context Mount persistence verification SUCCESSFUL!")
	} else {
		fmt.Println("⚠️  Some files not found — mount may still be initializing")
	}

	// Clean up
	fmt.Println("\n🧹 Cleaning up second session...")
	deleteResult2, err := ab.Delete(session2, false)
	if err != nil {
		log.Printf("❌ Second session deletion failed: %v", err)
	} else if deleteResult2.Success {
		fmt.Println("✅ Second session deleted")
	}

	fmt.Println("\n🧹 Cleaning up context...")
	deleteCtxResult, err := ab.Context.Delete(ctx)
	if err != nil {
		log.Printf("❌ Context deletion failed: %v", err)
	} else if deleteCtxResult.Success {
		fmt.Printf("✅ Context deleted: %s\n", deleteCtxResult.RequestID)
	}

	return nil
}
