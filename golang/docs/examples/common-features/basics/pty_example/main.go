// ci-stable
package main

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/pty"
)

func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "akm-xxx"
		fmt.Println("Warning: Set AGENTBAY_API_KEY for a real run.")
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	params := agentbay.NewCreateSessionParams()
	fmt.Println("\nCreating session with default image...")
	sessionResult, err := agentBay.Create(params)
	if err != nil {
		fmt.Printf("Error creating session: %v\n", err)
		os.Exit(1)
	}
	if !sessionResult.Success {
		fmt.Println("Session creation failed")
		os.Exit(1)
	}
	session := sessionResult.Session
	fmt.Printf("Session: %s\n\n", session.SessionID)
	defer func() {
		fmt.Println("\nDeleting the session...")
		_, delErr := agentBay.Delete(session)
		if delErr != nil {
			fmt.Printf("Error deleting session: %v\n", delErr)
		} else {
			fmt.Println("Session deleted successfully")
		}
	}()

	// 1. Create PTY and echo
	var chunks [][]byte
	handle, err := session.Pty.Create(pty.CreateOptions{
		OnData: func(data []byte) {
			chunks = append(chunks, append([]byte{}, data...))
		},
	})
	if err != nil {
		fmt.Printf("Failed to create PTY: %v\n", err)
		return
	}
	fmt.Printf("1. Created PTY: %s\n", handle.PtySessionID())
	time.Sleep(1 * time.Second)
	if err := handle.SendInput([]byte("echo 'AGENTBAY_PTY_EXAMPLE_ECHO'\r")); err != nil {
		fmt.Printf("SendInput failed: %v\n", err)
		return
	}
	time.Sleep(2 * time.Second)
	combined := joinChunks(chunks)
	fmt.Printf("   Echo output contains marker: %v\n\n", strings.Contains(combined, "AGENTBAY_PTY_EXAMPLE_ECHO"))

	// 2. Resize
	if err := handle.Resize(120, 40); err != nil {
		fmt.Printf("Resize failed: %v\n", err)
		return
	}
	time.Sleep(1 * time.Second)
	if err := handle.SendInput([]byte("echo \"cols=$(tput cols) lines=$(tput lines)\"\r")); err != nil {
		fmt.Printf("SendInput failed: %v\n", err)
		return
	}
	time.Sleep(2 * time.Second)
	combined = joinChunks(chunks)
	fmt.Printf("2. Resize 120x40; cols=120 in output: %v\n\n", strings.Contains(combined, "cols=120"))

	// 3. List
	sessions, err := session.Pty.List()
	if err != nil {
		fmt.Printf("List failed: %v\n", err)
		return
	}
	found := false
	for _, s := range sessions {
		if s.PtySessionID == handle.PtySessionID() {
			found = true
			break
		}
	}
	fmt.Printf("3. List PTY sessions: count=%d, id present: %v\n\n", len(sessions), found)

	// 4. Disconnect / reconnect
	ptyID := handle.PtySessionID()
	handle.Disconnect()
	var out2 [][]byte
	handle2, err := session.Pty.Connect(ptyID, func(data []byte) {
		out2 = append(out2, append([]byte{}, data...))
	})
	if err != nil {
		fmt.Printf("Connect failed: %v\n", err)
		return
	}
	time.Sleep(1 * time.Second)
	if err := handle2.SendInput([]byte("echo 'AGENTBAY_PTY_EXAMPLE_RECONNECT'\r")); err != nil {
		fmt.Printf("SendInput failed: %v\n", err)
		return
	}
	time.Sleep(2 * time.Second)
	text2 := joinChunks(out2)
	fmt.Printf("4. Reconnect OK: %v\n\n", strings.Contains(text2, "AGENTBAY_PTY_EXAMPLE_RECONNECT"))
	handle2.Disconnect()

	// 5. Kill
	killH, err := session.Pty.Create(pty.CreateOptions{})
	if err != nil {
		fmt.Printf("Failed to create PTY for kill: %v\n", err)
		return
	}
	time.Sleep(1 * time.Second)
	if err := killH.Kill(); err != nil {
		fmt.Printf("Kill failed: %v\n", err)
		return
	}
	killCode, err := killH.Wait(10000)
	if err != nil {
		fmt.Printf("Wait after kill failed: %v\n", err)
		return
	}
	fmt.Printf("5. Kill exit code: %d (expected -9)\n\n", killCode)

	// 6. Exit with wait
	exitH, err := session.Pty.Create(pty.CreateOptions{})
	if err != nil {
		fmt.Printf("Failed to create PTY for exit: %v\n", err)
		return
	}
	time.Sleep(1 * time.Second)
	if err := exitH.SendInput([]byte("exit\r")); err != nil {
		fmt.Printf("SendInput failed: %v\n", err)
		return
	}
	exitCode, err := exitH.Wait(10000)
	if err != nil {
		fmt.Printf("Wait after exit failed: %v\n", err)
		return
	}
	fmt.Printf("6. Shell exit code: %d (expected 0)\n", exitCode)
	fmt.Println("\nPTY example completed.")
}

func joinChunks(chunks [][]byte) string {
	var b strings.Builder
	for _, c := range chunks {
		b.WriteString(string(c))
	}
	return b.String()
}
