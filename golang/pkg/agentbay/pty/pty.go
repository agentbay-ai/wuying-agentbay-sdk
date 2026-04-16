// Package pty provides interactive terminal (PTY) sessions in cloud sandbox environments.
package pty

import (
	"encoding/base64"
	"fmt"
	"sync"
	"time"
	"unicode/utf8"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/internal"
)

const (
	ptyTarget       = "PTY_SERVER"
	maxTerminalSize = 500
)

var defaultEnvs = map[string]string{
	"TERM": "xterm-256color",
	"LANG": "en_US.UTF-8",
}

// PtySession is a read-only snapshot of a PTY session.
type PtySession struct {
	PtySessionID string
	Cols         int
	Rows         int
	Status       string
	ExitCode     *int
}

// PtyHandle is an active connection to a PTY session.
type PtyHandle struct {
	mu           sync.Mutex
	ptySessionID string
	ptyModule    *Pty
	onData       func([]byte)
	connected    bool
	exitCode     *int
	errorMsg     *string
}

func newPtyHandle(ptySessionID string, ptyModule *Pty, onData func([]byte)) *PtyHandle {
	return &PtyHandle{
		ptySessionID: ptySessionID,
		ptyModule:    ptyModule,
		onData:       onData,
		connected:    true,
	}
}

// PtySessionID returns the PTY session identifier.
func (h *PtyHandle) PtySessionID() string {
	return h.ptySessionID
}

// IsConnected returns whether this handle is still connected.
func (h *PtyHandle) IsConnected() bool {
	h.mu.Lock()
	defer h.mu.Unlock()
	return h.connected
}

// ExitCode returns the exit code of the PTY process, or nil if not yet exited.
func (h *PtyHandle) ExitCode() *int {
	h.mu.Lock()
	defer h.mu.Unlock()
	return h.exitCode
}

// SendInput sends input bytes to the PTY.
func (h *PtyHandle) SendInput(data []byte) error {
	h.mu.Lock()
	if !h.connected {
		h.mu.Unlock()
		return fmt.Errorf("PTY handle is not connected")
	}
	h.mu.Unlock()

	var text, encoding string
	if utf8.Valid(data) {
		text = string(data)
		encoding = "utf8"
	} else {
		text = base64.StdEncoding.EncodeToString(data)
		encoding = "base64"
	}

	wsClient, err := h.ptyModule.getWsClient()
	if err != nil {
		return err
	}
	return wsClient.SendMessage(ptyTarget, map[string]interface{}{
		"method": "pty.input",
		"params": map[string]interface{}{
			"ptySessionId": h.ptySessionID,
			"encoding":     encoding,
			"data":         text,
		},
	})
}

// Resize changes the terminal size.
func (h *PtyHandle) Resize(cols, rows int) error {
	h.mu.Lock()
	if !h.connected {
		h.mu.Unlock()
		return fmt.Errorf("PTY handle is not connected")
	}
	h.mu.Unlock()

	if cols < 1 || cols > maxTerminalSize || rows < 1 || rows > maxTerminalSize {
		return fmt.Errorf("invalid terminal size: cols=%d, rows=%d (must be 1-%d)", cols, rows, maxTerminalSize)
	}

	wsClient, err := h.ptyModule.getWsClient()
	if err != nil {
		return err
	}
	return wsClient.SendMessage(ptyTarget, map[string]interface{}{
		"method": "pty.resize",
		"params": map[string]interface{}{
			"ptySessionId": h.ptySessionID,
			"cols":         cols,
			"rows":         rows,
		},
	})
}

// Kill sends SIGKILL to the PTY process.
func (h *PtyHandle) Kill() error {
	h.mu.Lock()
	if !h.connected {
		h.mu.Unlock()
		return fmt.Errorf("PTY handle is not connected")
	}
	h.mu.Unlock()

	wsClient, err := h.ptyModule.getWsClient()
	if err != nil {
		return err
	}
	_, err = wsClient.Call(ptyTarget, map[string]interface{}{
		"method": "pty.kill",
		"params": map[string]interface{}{
			"ptySessionId": h.ptySessionID,
		},
	}, 30000)
	return err
}

// Wait blocks until the PTY process exits and returns its exit code.
// Pass 0 for no timeout.
func (h *PtyHandle) Wait(timeoutMs int) (int, error) {
	var deadline time.Time
	if timeoutMs > 0 {
		deadline = time.Now().Add(time.Duration(timeoutMs) * time.Millisecond)
	}

	for {
		h.mu.Lock()
		ec := h.exitCode
		em := h.errorMsg
		h.mu.Unlock()

		if ec != nil {
			return *ec, nil
		}
		if em != nil {
			return 0, fmt.Errorf("PTY error: %s", *em)
		}
		if timeoutMs > 0 && time.Now().After(deadline) {
			return 0, fmt.Errorf("PTY wait timed out after %dms", timeoutMs)
		}
		time.Sleep(100 * time.Millisecond)
	}
}

// Disconnect detaches this handle from the PTY (process continues on server).
func (h *PtyHandle) Disconnect() {
	h.mu.Lock()
	if !h.connected {
		h.mu.Unlock()
		return
	}
	h.connected = false
	h.mu.Unlock()
	h.ptyModule.unregisterHandle(h.ptySessionID)
}

func (h *PtyHandle) handleOutput(data []byte) {
	if h.onData != nil {
		func() {
			defer func() { recover() }()
			h.onData(data)
		}()
	}
}

func (h *PtyHandle) handleExit(exitCode int) {
	h.mu.Lock()
	h.exitCode = &exitCode
	h.connected = false
	h.mu.Unlock()
}

func (h *PtyHandle) handleError(errorMsg string) {
	h.mu.Lock()
	h.errorMsg = &errorMsg
	h.connected = false
	h.mu.Unlock()
}

// CreateOptions configures a new PTY session.
type CreateOptions struct {
	Cols      int
	Rows      int
	Cwd       string
	Envs      map[string]string
	Shell     string
	OnData    func([]byte)
	TimeoutMs int
}

// Pty is the PTY module entry point, accessed as session.Pty.
type Pty struct {
	session interface {
		GetWsClient() (interface{}, error)
	}
	mu                 sync.Mutex
	wsClient           *internal.WsClient
	handles            map[string]*PtyHandle
	callbackRegistered bool
}

// NewPty creates a new Pty module for the given session.
func NewPty(session interface {
	GetWsClient() (interface{}, error)
}) *Pty {
	return &Pty{
		session: session,
		handles: make(map[string]*PtyHandle),
	}
}

func (p *Pty) getWsClient() (*internal.WsClient, error) {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.wsClient != nil {
		return p.wsClient, nil
	}
	raw, err := p.session.GetWsClient()
	if err != nil {
		return nil, err
	}
	ws, ok := raw.(*internal.WsClient)
	if !ok || ws == nil {
		return nil, fmt.Errorf("invalid or nil WsClient returned from session")
	}
	p.wsClient = ws
	return ws, nil
}

func (p *Pty) ensureCallback() error {
	p.mu.Lock()
	if p.callbackRegistered {
		p.mu.Unlock()
		return nil
	}
	p.mu.Unlock()

	ws, err := p.getWsClient()
	if err != nil {
		return err
	}
	if err := ws.Connect(); err != nil {
		return err
	}
	ws.RegisterCallback(ptyTarget, p.pushCallback)

	p.mu.Lock()
	p.callbackRegistered = true
	p.mu.Unlock()
	return nil
}

func (p *Pty) pushCallback(payload map[string]interface{}) {
	dataAny, _ := payload["data"]
	data, ok := dataAny.(map[string]interface{})
	if !ok {
		return
	}
	eventType, _ := data["eventType"].(string)
	ptySessionID, _ := data["ptySessionId"].(string)

	p.mu.Lock()
	handle := p.handles[ptySessionID]
	p.mu.Unlock()

	if handle == nil {
		return
	}

	switch eventType {
	case "pty.output":
		encoding, _ := data["encoding"].(string)
		raw, _ := data["data"].(string)
		var dataBytes []byte
		if encoding == "base64" {
			dataBytes, _ = base64.StdEncoding.DecodeString(raw)
		} else {
			dataBytes = []byte(raw)
		}
		handle.handleOutput(dataBytes)
	case "pty.exit":
		exitCode := -1
		if v, ok := data["exitCode"].(float64); ok {
			exitCode = int(v)
		}
		handle.handleExit(exitCode)
	case "pty.error":
		errMsg := "Unknown PTY error"
		if v, ok := data["error"].(string); ok {
			errMsg = v
		}
		handle.handleError(errMsg)
	}
}

func (p *Pty) unregisterHandle(ptySessionID string) {
	p.mu.Lock()
	delete(p.handles, ptySessionID)
	p.mu.Unlock()
}

// Create creates a new PTY session.
func (p *Pty) Create(opts CreateOptions) (*PtyHandle, error) {
	cols := opts.Cols
	if cols == 0 {
		cols = 80
	}
	rows := opts.Rows
	if rows == 0 {
		rows = 24
	}

	if cols < 1 || cols > maxTerminalSize || rows < 1 || rows > maxTerminalSize {
		return nil, fmt.Errorf("invalid terminal size: cols=%d, rows=%d (must be 1-%d)", cols, rows, maxTerminalSize)
	}

	if err := p.ensureCallback(); err != nil {
		return nil, err
	}
	ws, err := p.getWsClient()
	if err != nil {
		return nil, err
	}

	params := map[string]interface{}{
		"cols": cols,
		"rows": rows,
	}
	if opts.Cwd != "" {
		params["cwd"] = opts.Cwd
	}
	mergedEnvs := make(map[string]interface{})
	for k, v := range defaultEnvs {
		mergedEnvs[k] = v
	}
	for k, v := range opts.Envs {
		mergedEnvs[k] = v
	}
	params["envs"] = mergedEnvs
	if opts.Shell != "" {
		params["shell"] = opts.Shell
	}

	timeoutMs := opts.TimeoutMs
	if timeoutMs <= 0 {
		timeoutMs = 30000
	}

	response, err := ws.Call(ptyTarget, map[string]interface{}{
		"method": "pty.create",
		"params": params,
	}, timeoutMs)
	if err != nil {
		return nil, err
	}

	result, _ := response["result"].(map[string]interface{})
	ptySessionID, _ := result["ptySessionId"].(string)
	if ptySessionID == "" {
		return nil, fmt.Errorf("pty.create did not return ptySessionId: %v", response)
	}

	handle := newPtyHandle(ptySessionID, p, opts.OnData)

	p.mu.Lock()
	p.handles[ptySessionID] = handle
	p.mu.Unlock()

	return handle, nil
}

// List returns all active PTY sessions.
func (p *Pty) List() ([]PtySession, error) {
	if err := p.ensureCallback(); err != nil {
		return nil, err
	}
	ws, err := p.getWsClient()
	if err != nil {
		return nil, err
	}

	response, err := ws.Call(ptyTarget, map[string]interface{}{
		"method": "pty.list",
		"params": map[string]interface{}{},
	}, 30000)
	if err != nil {
		return nil, err
	}

	result, _ := response["result"].(map[string]interface{})
	idsRaw, _ := result["ptySessionIds"].([]interface{})
	sessions := make([]PtySession, 0, len(idsRaw))
	for _, idAny := range idsRaw {
		sid, _ := idAny.(string)
		if sid == "" {
			continue
		}
		status := "running"
		var exitCode *int

		p.mu.Lock()
		h := p.handles[sid]
		p.mu.Unlock()
		if h != nil {
			h.mu.Lock()
			if h.exitCode != nil {
				status = "exited"
				ec := *h.exitCode
				exitCode = &ec
			}
			h.mu.Unlock()
		}
		sessions = append(sessions, PtySession{
			PtySessionID: sid,
			Status:       status,
			ExitCode:     exitCode,
		})
	}
	return sessions, nil
}

// Connect reconnects to an existing PTY session.
func (p *Pty) Connect(ptySessionID string, onData func([]byte)) (*PtyHandle, error) {
	if err := p.ensureCallback(); err != nil {
		return nil, err
	}
	ws, err := p.getWsClient()
	if err != nil {
		return nil, err
	}

	response, err := ws.Call(ptyTarget, map[string]interface{}{
		"method": "pty.connect",
		"params": map[string]interface{}{
			"ptySessionId": ptySessionID,
		},
	}, 30000)
	if err != nil {
		return nil, err
	}

	result, _ := response["result"].(map[string]interface{})
	returnedID, _ := result["ptySessionId"].(string)
	if returnedID == "" {
		returnedID = ptySessionID
	}

	handle := newPtyHandle(returnedID, p, onData)

	p.mu.Lock()
	p.handles[returnedID] = handle
	p.mu.Unlock()

	return handle, nil
}

// KillSession kills a PTY session by ID.
func (p *Pty) KillSession(ptySessionID string) error {
	if err := p.ensureCallback(); err != nil {
		return err
	}
	ws, err := p.getWsClient()
	if err != nil {
		return err
	}

	_, err = ws.Call(ptyTarget, map[string]interface{}{
		"method": "pty.kill",
		"params": map[string]interface{}{
			"ptySessionId": ptySessionID,
		},
	}, 30000)
	if err != nil {
		return err
	}

	p.mu.Lock()
	if h, ok := p.handles[ptySessionID]; ok {
		h.mu.Lock()
		h.connected = false
		h.mu.Unlock()
		delete(p.handles, ptySessionID)
	}
	p.mu.Unlock()
	return nil
}
