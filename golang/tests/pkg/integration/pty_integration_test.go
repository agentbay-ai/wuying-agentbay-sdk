package integration_test

import (
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/pty"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

const ptyImageID = "linux_latest"

func createPtySession(t *testing.T) (*agentbay.AgentBay, *agentbay.Session) {
	t.Helper()
	apiKey := testutil.GetTestAPIKey(t)
	ab, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay: %v", err)
	}
	params := agentbay.NewCreateSessionParams().WithImageId(ptyImageID)
	result, err := ab.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	if !result.Success {
		t.Fatalf("Session creation failed")
	}
	t.Logf("Session created: %s", result.Session.SessionID)
	return ab, result.Session
}

func TestPtyCreateAndEcho(t *testing.T) {
	ab, session := createPtySession(t)
	defer func() {
		ab.Delete(session)
	}()

	var chunks [][]byte
	handle, err := session.Pty.Create(pty.CreateOptions{
		OnData: func(data []byte) {
			chunks = append(chunks, append([]byte{}, data...))
		},
	})
	if err != nil {
		t.Fatalf("Failed to create PTY: %v", err)
	}
	if !handle.IsConnected() {
		t.Fatal("handle should be connected")
	}

	time.Sleep(1 * time.Second)

	if err := handle.SendInput([]byte("echo 'PTY_GO_OK_54321'\r")); err != nil {
		t.Fatalf("SendInput failed: %v", err)
	}
	time.Sleep(2 * time.Second)

	combined := ""
	for _, c := range chunks {
		combined += string(c)
	}
	if !strings.Contains(combined, "PTY_GO_OK_54321") {
		t.Fatalf("Expected output to contain 'PTY_GO_OK_54321', got: %s", combined)
	}

	handle.Disconnect()
}

func TestPtyResize(t *testing.T) {
	ab, session := createPtySession(t)
	defer func() {
		ab.Delete(session)
	}()

	var chunks [][]byte
	handle, err := session.Pty.Create(pty.CreateOptions{
		OnData: func(data []byte) {
			chunks = append(chunks, append([]byte{}, data...))
		},
	})
	if err != nil {
		t.Fatalf("Failed to create PTY: %v", err)
	}

	time.Sleep(1 * time.Second)

	if err := handle.Resize(120, 40); err != nil {
		t.Fatalf("Resize failed: %v", err)
	}
	time.Sleep(1 * time.Second)

	if err := handle.SendInput([]byte("echo \"cols=$(tput cols) lines=$(tput lines)\"\r")); err != nil {
		t.Fatalf("SendInput failed: %v", err)
	}
	time.Sleep(2 * time.Second)

	combined := ""
	for _, c := range chunks {
		combined += string(c)
	}
	if !strings.Contains(combined, "cols=120") {
		t.Fatalf("Expected 'cols=120' in output, got: %s", combined)
	}

	handle.Disconnect()
}

func TestPtyList(t *testing.T) {
	ab, session := createPtySession(t)
	defer func() {
		ab.Delete(session)
	}()

	handle, err := session.Pty.Create(pty.CreateOptions{})
	if err != nil {
		t.Fatalf("Failed to create PTY: %v", err)
	}
	time.Sleep(1 * time.Second)

	sessions, err := session.Pty.List()
	if err != nil {
		t.Fatalf("Failed to list PTY sessions: %v", err)
	}

	found := false
	for _, s := range sessions {
		if s.PtySessionID == handle.PtySessionID() {
			found = true
			break
		}
	}
	if !found {
		t.Fatalf("Created PTY %s not found in list", handle.PtySessionID())
	}

	handle.Disconnect()
}

func TestPtyExitCode(t *testing.T) {
	ab, session := createPtySession(t)
	defer func() {
		ab.Delete(session)
	}()

	handle, err := session.Pty.Create(pty.CreateOptions{})
	if err != nil {
		t.Fatalf("Failed to create PTY: %v", err)
	}
	time.Sleep(1 * time.Second)

	if err := handle.SendInput([]byte("exit\r")); err != nil {
		t.Fatalf("SendInput failed: %v", err)
	}
	exitCode, err := handle.Wait(10000)
	if err != nil {
		t.Fatalf("Wait failed: %v", err)
	}

	t.Logf("Exit code: %d", exitCode)
	if handle.IsConnected() {
		t.Fatal("handle should be disconnected after exit")
	}
}

func TestPtyKill(t *testing.T) {
	ab, session := createPtySession(t)
	defer func() {
		ab.Delete(session)
	}()

	handle, err := session.Pty.Create(pty.CreateOptions{})
	if err != nil {
		t.Fatalf("Failed to create PTY: %v", err)
	}
	time.Sleep(1 * time.Second)

	if err := handle.Kill(); err != nil {
		t.Fatalf("Kill failed: %v", err)
	}
	exitCode, err := handle.Wait(10000)
	if err != nil {
		t.Fatalf("Wait failed: %v", err)
	}

	if exitCode != -9 {
		t.Fatalf("Expected exit code -9, got %d", exitCode)
	}
}

func TestPtyDisconnectReconnect(t *testing.T) {
	ab, session := createPtySession(t)
	defer func() {
		ab.Delete(session)
	}()

	handle1, err := session.Pty.Create(pty.CreateOptions{})
	if err != nil {
		t.Fatalf("Failed to create PTY: %v", err)
	}
	time.Sleep(1 * time.Second)

	ptyID := handle1.PtySessionID()
	handle1.Disconnect()
	if handle1.IsConnected() {
		t.Fatal("handle should be disconnected")
	}

	time.Sleep(1 * time.Second)

	var output2 [][]byte
	handle2, err := session.Pty.Connect(ptyID, func(data []byte) {
		output2 = append(output2, append([]byte{}, data...))
	})
	if err != nil {
		t.Fatalf("Connect failed: %v", err)
	}
	if !handle2.IsConnected() {
		t.Fatal("handle2 should be connected")
	}

	if err := handle2.SendInput([]byte("echo 'RECONNECTED_GO'\r")); err != nil {
		t.Fatalf("SendInput failed: %v", err)
	}
	time.Sleep(2 * time.Second)

	combined := ""
	for _, c := range output2 {
		combined += string(c)
	}
	if !strings.Contains(combined, "RECONNECTED_GO") {
		t.Fatalf("Expected 'RECONNECTED_GO' in output, got: %s", combined)
	}

	handle2.Disconnect()
}
