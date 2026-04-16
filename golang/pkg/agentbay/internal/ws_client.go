package internal

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"net/http"
	"sync"
	"time"

	"golang.org/x/net/websocket"
)

type OnEvent func(invocationID string, data map[string]interface{})
type OnEnd func(invocationID string, data map[string]interface{})
type OnError func(invocationID string, err error)

type DebugLogger func(message string)

type PushCallback = func(payload map[string]interface{})

// WsConnectionState represents the connection state of a WsClient.
type WsConnectionState string

const (
	WsStateOpen         WsConnectionState = "OPEN"
	WsStateClosed       WsConnectionState = "CLOSED"
	WsStateReconnecting WsConnectionState = "RECONNECTING"
	WsStateError        WsConnectionState = "ERROR"
)

// ConnectionStateListener is called whenever the WsClient connection state changes.
type ConnectionStateListener func(state WsConnectionState, reason string)

type endResult struct {
	data map[string]interface{}
	err  error
}

// WsCancelledError is returned when a stream is cancelled by the caller.
type WsCancelledError struct {
	InvocationID string
}

// WsTimeoutError is returned when WaitEndWithTimeout exceeds the caller's deadline.
type WsTimeoutError struct {
	Timeout time.Duration
}

func (e *WsTimeoutError) Error() string {
	return fmt.Sprintf("timeout waiting for WS end event after %v", e.Timeout)
}

func (e *WsCancelledError) Error() string {
	return fmt.Sprintf("stream %s was cancelled by caller", e.InvocationID)
}

type WsClient struct {
	wsURL  string
	token  string
	logger DebugLogger

	mu        sync.Mutex
	conn      *websocket.Conn
	pending   map[string]*pendingStream
	closedCh  chan struct{}
	callbacks map[string]map[string]PushCallback
	nextCbID  uint64

	state          WsConnectionState
	stateListeners []stateListenerEntry
	nextListenerID uint64

	closedExplicitly bool
	reconnecting     bool
	reconnectTimer   *time.Timer

	heartbeatIntervalMs    int
	reconnectInitialDelayMs int
	reconnectMaxDelayMs    int
	heartbeatStop          chan struct{}
}

type stateListenerEntry struct {
	id       uint64
	listener ConnectionStateListener
}

type pendingStream struct {
	onEvent OnEvent
	onEnd   OnEnd
	onError OnError
	endCh   chan endResult
	isCall  bool
}

type WsStreamHandle struct {
	InvocationID string
	client       *WsClient
	target       string
	waitEnd      func() (map[string]interface{}, error)
	waitEndCh    <-chan endResult
	closedCh     <-chan struct{}
	cancel       func() error
}

func (h *WsStreamHandle) WaitEnd() (map[string]interface{}, error) {
	return h.waitEnd()
}

// WaitEndWithTimeout waits for the stream to end with a caller-specified timeout.
// Returns WsTimeoutError when the timeout expires.
func (h *WsStreamHandle) WaitEndWithTimeout(timeout time.Duration) (map[string]interface{}, error) {
	select {
	case <-h.closedCh:
		return nil, fmt.Errorf("WS connection closed")
	case r := <-h.waitEndCh:
		if r.err != nil {
			return nil, r.err
		}
		return r.data, nil
	case <-time.After(timeout):
		return nil, &WsTimeoutError{Timeout: timeout}
	}
}

func (h *WsStreamHandle) Cancel() error {
	if h.cancel == nil {
		return nil
	}
	return h.cancel()
}

func (h *WsStreamHandle) Write(data map[string]interface{}) error {
	return h.client.sendStreamMessage(h.InvocationID, h.target, data)
}

func (c *WsClient) sendStreamMessage(invocationID string, target string, data map[string]interface{}) error {
	c.mu.Lock()
	conn := c.conn
	c.mu.Unlock()
	if conn == nil {
		return fmt.Errorf("WS is not connected")
	}
	payload := map[string]interface{}{
		"invocationId": invocationID,
		"source":       "SDK",
		"target":       target,
		"data":         data,
	}
	c.logFrame(">>", payload)
	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %w", err)
	}
	if err := websocket.Message.Send(conn, string(payloadBytes)); err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}
	return nil
}

func NewWsClient(wsURL string, token string, logger DebugLogger) *WsClient {
	return &WsClient{
		wsURL:     wsURL,
		token:     token,
		logger:    logger,
		pending:   make(map[string]*pendingStream),
		closedCh:  make(chan struct{}),
		callbacks: make(map[string]map[string]PushCallback),
		state:     WsStateClosed,

		heartbeatIntervalMs:     20000,
		reconnectInitialDelayMs: 1000,
		reconnectMaxDelayMs:     30000,
	}
}

// OnConnectionStateChange registers a listener that is invoked when the
// connection state changes.  Returns an unsubscribe function.
func (c *WsClient) OnConnectionStateChange(listener ConnectionStateListener) func() {
	c.mu.Lock()
	c.nextListenerID++
	id := c.nextListenerID
	c.stateListeners = append(c.stateListeners, stateListenerEntry{id: id, listener: listener})
	c.mu.Unlock()

	return func() {
		c.mu.Lock()
		defer c.mu.Unlock()
		for i, entry := range c.stateListeners {
			if entry.id == id {
				c.stateListeners = append(c.stateListeners[:i], c.stateListeners[i+1:]...)
				break
			}
		}
	}
}

func (c *WsClient) setState(state WsConnectionState, reason string) {
	c.mu.Lock()
	if c.state == state {
		c.mu.Unlock()
		return
	}
	c.state = state
	listeners := make([]ConnectionStateListener, len(c.stateListeners))
	for i, entry := range c.stateListeners {
		listeners[i] = entry.listener
	}
	c.mu.Unlock()

	if c.logger != nil {
		c.logger(fmt.Sprintf("WS state → %s: %s", state, reason))
	}
	for _, l := range listeners {
		func() {
			defer func() {
				if r := recover(); r != nil && c.logger != nil {
					c.logger(fmt.Sprintf("WS state listener panic: %v", r))
				}
			}()
			l(state, reason)
		}()
	}
}

func (c *WsClient) startHeartbeat() {
	c.stopHeartbeat()
	c.mu.Lock()
	stop := make(chan struct{})
	c.heartbeatStop = stop
	interval := c.heartbeatIntervalMs
	c.mu.Unlock()

	go func() {
		ticker := time.NewTicker(time.Duration(interval) * time.Millisecond)
		defer ticker.Stop()
		for {
			select {
			case <-stop:
				return
			case <-ticker.C:
				c.mu.Lock()
				conn := c.conn
				c.mu.Unlock()
				if conn == nil {
					return
				}
				pingMsg := map[string]interface{}{
					"type": "ping",
				}
				raw, _ := json.Marshal(pingMsg)
				if err := websocket.Message.Send(conn, string(raw)); err != nil {
					if c.logger != nil {
						c.logger(fmt.Sprintf("WS heartbeat send failed: %v", err))
					}
				}
			}
		}
	}()
}

func (c *WsClient) stopHeartbeat() {
	c.mu.Lock()
	if c.heartbeatStop != nil {
		close(c.heartbeatStop)
		c.heartbeatStop = nil
	}
	c.mu.Unlock()
}

func (c *WsClient) scheduleReconnect() {
	c.mu.Lock()
	if c.closedExplicitly || c.reconnecting {
		c.mu.Unlock()
		return
	}
	c.reconnecting = true
	initialDelay := c.reconnectInitialDelayMs
	maxDelay := c.reconnectMaxDelayMs
	c.mu.Unlock()

	c.setState(WsStateReconnecting, "connection lost")
	go c.reconnectWithBackoff(initialDelay, maxDelay)
}

func (c *WsClient) reconnectWithBackoff(initialDelayMs, maxDelayMs int) {
	attempt := 0
	for {
		c.mu.Lock()
		if c.closedExplicitly {
			c.reconnecting = false
			c.mu.Unlock()
			return
		}
		c.mu.Unlock()

		delayMs := float64(initialDelayMs) * math.Pow(2, float64(attempt))
		if delayMs > float64(maxDelayMs) {
			delayMs = float64(maxDelayMs)
		}
		jitter := delayMs * 0.3 * rand.Float64()
		delay := time.Duration(delayMs+jitter) * time.Millisecond

		if c.logger != nil {
			c.logger(fmt.Sprintf("WS reconnect attempt %d in %v", attempt+1, delay))
		}
		time.Sleep(delay)

		c.mu.Lock()
		if c.closedExplicitly {
			c.reconnecting = false
			c.mu.Unlock()
			return
		}
		c.mu.Unlock()

		err := c.openConnection()
		if err == nil {
			c.mu.Lock()
			c.reconnecting = false
			c.mu.Unlock()
			c.startHeartbeat()
			c.setState(WsStateOpen, "reconnected")
			return
		}

		if c.logger != nil {
			c.logger(fmt.Sprintf("WS reconnect failed: %v", err))
		}
		attempt++
	}
}

func (c *WsClient) cancelReconnect() {
	c.mu.Lock()
	if c.reconnectTimer != nil {
		c.reconnectTimer.Stop()
		c.reconnectTimer = nil
	}
	c.mu.Unlock()
}

// openConnection performs the raw websocket dial and starts recvLoop.
// It does NOT set state or start heartbeat — callers handle that.
func (c *WsClient) openConnection() error {
	cfg, err := websocket.NewConfig(c.wsURL, "http://localhost/")
	if err != nil {
		return err
	}
	cfg.Header = http.Header{}
	cfg.Header.Set("X-Access-Token", c.token)

	conn, err := websocket.DialConfig(cfg)
	if err != nil {
		return err
	}

	c.mu.Lock()
	c.conn = conn
	// Reset closedCh so that pending streams can use a fresh channel
	select {
	case <-c.closedCh:
		c.closedCh = make(chan struct{})
	default:
	}
	c.mu.Unlock()

	go c.recvLoop()
	return nil
}

func (c *WsClient) RegisterCallback(target string, callback PushCallback) func() {
	if target == "" {
		panic("target must be a non-empty string")
	}
	if callback == nil {
		panic("callback must not be nil")
	}
	c.mu.Lock()
	c.nextCbID++
	id := fmt.Sprintf("%d", c.nextCbID)
	if c.callbacks[target] == nil {
		c.callbacks[target] = make(map[string]PushCallback)
	}
	c.callbacks[target][id] = callback
	c.mu.Unlock()
	return func() {
		c.mu.Lock()
		m := c.callbacks[target]
		if m != nil {
			delete(m, id)
			if len(m) == 0 {
				delete(c.callbacks, target)
			}
		}
		c.mu.Unlock()
	}
}

func (c *WsClient) UnregisterCallback(target string) {
	if target == "" {
		panic("target must be a non-empty string")
	}
	c.mu.Lock()
	delete(c.callbacks, target)
	c.mu.Unlock()
}

func (c *WsClient) Connect() error {
	c.mu.Lock()
	if c.conn != nil {
		c.mu.Unlock()
		return nil
	}
	c.closedExplicitly = false
	c.mu.Unlock()

	if err := c.openConnection(); err != nil {
		c.setState(WsStateError, err.Error())
		return err
	}
	c.startHeartbeat()
	c.setState(WsStateOpen, "connected")
	return nil
}

func (c *WsClient) Close() error {
	c.mu.Lock()
	c.closedExplicitly = true
	conn := c.conn
	c.conn = nil
	c.mu.Unlock()

	c.cancelReconnect()
	c.stopHeartbeat()

	select {
	case <-c.closedCh:
	default:
		close(c.closedCh)
	}

	if conn != nil {
		_ = conn.Close()
	}
	c.failAllPending(fmt.Errorf("WS client closed"))
	c.setState(WsStateClosed, "closed by client")
	return nil
}

// SendMessage sends a message to the target without expecting a response.
// Used for one-way notifications like browser callback messages.
//
// Parameters:
//   - target: The target service identifier
//   - data: The message data to send
//
// Returns an error if the connection is not established or sending fails.
func (c *WsClient) SendMessage(target string, data map[string]interface{}) error {
	if err := c.Connect(); err != nil {
		return err
	}

	invocationID := newInvocationID()

	c.mu.Lock()
	conn := c.conn
	c.mu.Unlock()

	if conn == nil {
		return fmt.Errorf("WS is not connected")
	}

	payload := map[string]interface{}{
		"invocationId": invocationID,
		"source":       "SDK",
		"target":       target,
		"data":         data,
	}

	c.logFrame(">>", payload)

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %w", err)
	}

	if err := websocket.Message.Send(conn, string(payloadBytes)); err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}

	return nil
}

// Call sends a request and blocks until a single response arrives (no phase semantics).
// Used for PTY operations and other simple request-response patterns.
func (c *WsClient) Call(target string, data map[string]interface{}, timeoutMs int) (map[string]interface{}, error) {
	if err := c.Connect(); err != nil {
		return nil, err
	}

	invocationID := newInvocationID()
	endCh := make(chan endResult, 1)
	p := &pendingStream{
		endCh:  endCh,
		isCall: true,
	}

	c.mu.Lock()
	c.pending[invocationID] = p
	conn := c.conn
	c.mu.Unlock()

	if conn == nil {
		c.mu.Lock()
		delete(c.pending, invocationID)
		c.mu.Unlock()
		return nil, fmt.Errorf("WS is not connected")
	}

	payload := map[string]interface{}{
		"invocationId": invocationID,
		"source":       "SDK",
		"target":       target,
		"data":         data,
	}

	c.logFrame(">>", payload)

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		c.mu.Lock()
		delete(c.pending, invocationID)
		c.mu.Unlock()
		return nil, fmt.Errorf("failed to marshal payload: %w", err)
	}

	if err := websocket.Message.Send(conn, string(payloadBytes)); err != nil {
		c.mu.Lock()
		delete(c.pending, invocationID)
		c.mu.Unlock()
		return nil, fmt.Errorf("failed to send message: %w", err)
	}

	timeout := time.Duration(timeoutMs) * time.Millisecond
	if timeout <= 0 {
		timeout = 30 * time.Second
	}

	select {
	case result := <-endCh:
		if result.err != nil {
			return nil, result.err
		}
		return result.data, nil
	case <-time.After(timeout):
		c.mu.Lock()
		delete(c.pending, invocationID)
		c.mu.Unlock()
		return nil, &WsTimeoutError{Timeout: timeout}
	case <-c.closedCh:
		return nil, fmt.Errorf("WS connection closed")
	}
}

func (c *WsClient) CallStream(target string, data map[string]interface{}, onEvent OnEvent, onEnd OnEnd, onError OnError) (*WsStreamHandle, error) {
	if err := c.Connect(); err != nil {
		return nil, err
	}

	invocationID := newInvocationID()
	endCh := make(chan endResult, 1)
	p := &pendingStream{
		onEvent: onEvent,
		onEnd:   onEnd,
		onError: onError,
		endCh:   endCh,
	}

	c.mu.Lock()
	c.pending[invocationID] = p
	conn := c.conn
	c.mu.Unlock()

	if conn == nil {
		c.mu.Lock()
		delete(c.pending, invocationID)
		c.mu.Unlock()
		return nil, fmt.Errorf("WS is not connected")
	}

	payload := map[string]interface{}{
		"invocationId": invocationID,
		"source":       "SDK",
		"target":       target,
		"data":         data,
	}
	c.logFrame(">>", payload)
	if err := websocket.JSON.Send(conn, payload); err != nil {
		c.mu.Lock()
		delete(c.pending, invocationID)
		c.mu.Unlock()
		return nil, err
	}

	return &WsStreamHandle{
		InvocationID: invocationID,
		client:       c,
		target:       target,
		waitEndCh:    endCh,
		closedCh:     c.closedCh,
		waitEnd: func() (map[string]interface{}, error) {
			select {
			case <-c.closedCh:
				return nil, fmt.Errorf("WS connection closed")
			case r := <-endCh:
				if r.err != nil {
					return nil, r.err
				}
				return r.data, nil
			case <-time.After(5 * time.Minute):
				return nil, fmt.Errorf("timeout waiting for WS end event")
			}
		},
		cancel: func() error {
			c.cancelPending(invocationID)
			return nil
		},
	}, nil
}

func (c *WsClient) cancelPending(invocationID string) {
	c.mu.Lock()
	p := c.pending[invocationID]
	delete(c.pending, invocationID)
	c.mu.Unlock()
	if p == nil {
		return
	}
	err := &WsCancelledError{InvocationID: invocationID}
	if p.onError != nil {
		p.onError(invocationID, err)
	}
	select {
	case p.endCh <- endResult{err: err}:
	default:
	}
}

func (c *WsClient) recvLoop() {
	for {
		c.mu.Lock()
		conn := c.conn
		c.mu.Unlock()
		if conn == nil {
			return
		}

		var msg map[string]interface{}
		err := websocket.JSON.Receive(conn, &msg)
		if err != nil {
			c.mu.Lock()
			explicit := c.closedExplicitly
			c.conn = nil
			c.mu.Unlock()

			c.stopHeartbeat()
			_ = conn.Close()

			select {
			case <-c.closedCh:
			default:
				close(c.closedCh)
			}
			c.failAllPending(fmt.Errorf("WS connection lost: %v", err))

			if !explicit {
				c.scheduleReconnect()
			}
			return
		}
		c.handleIncoming(msg)
	}
}

func (c *WsClient) handleIncoming(msg map[string]interface{}) {
	invocationID, _ := msg["invocationId"].(string)
	if invocationID == "" {
		if rid, ok := msg["requestId"].(string); ok {
			invocationID = rid
		}
	}
	if invocationID == "" {
		return
	}

	c.mu.Lock()
	p := c.pending[invocationID]
	c.mu.Unlock()

	source, _ := msg["source"].(string)
	dataAny, _ := msg["data"]
	targetAny, _ := msg["target"]
	target, _ := targetAny.(string)

	if p == nil {
		routeTarget := target
		if routeTarget == "SDK" && source != "" && source != "SDK" {
			routeTarget = source
		}
		if routeTarget == "" {
			return
		}

		dataObj := map[string]interface{}(nil)
		if m, ok := dataAny.(map[string]interface{}); ok {
			dataObj = m
		} else if s, ok := dataAny.(string); ok && s != "" {
			var parsed map[string]interface{}
			if err := json.Unmarshal([]byte(s), &parsed); err != nil {
				return
			}
			if parsed == nil {
				return
			}
			dataObj = parsed
		} else {
			return
		}

		c.mu.Lock()
		cbMap := c.callbacks[routeTarget]
		callbacks := make([]PushCallback, 0, len(cbMap))
		for _, cb := range cbMap {
			callbacks = append(callbacks, cb)
		}
		c.mu.Unlock()
		if len(callbacks) == 0 {
			return
		}

		payload := map[string]interface{}{
			"requestId": invocationID,
			"target":    routeTarget,
			"data":      dataObj,
		}
		for _, cb := range callbacks {
			if cb != nil {
				cb(payload)
			}
		}
		return
	}

	if source == "WEBSOCKET_SERVER" {
		c.logFrame("<<", map[string]interface{}{"invocationId": invocationID, "source": source, "data": dataAny})
		errMsg := ""
		if e, ok := msg["error"].(string); ok && e != "" {
			errMsg = e
		}
		if errMsg == "" {
			if m, ok := dataAny.(map[string]interface{}); ok {
				if e, ok := m["error"].(string); ok && e != "" {
					errMsg = e
				}
			}
		}
		if errMsg != "" {
			err := fmt.Errorf("%s", errMsg)
			if p.onError != nil {
				p.onError(invocationID, err)
			}
			select {
			case p.endCh <- endResult{err: err}:
			default:
			}
			c.finishPending(invocationID)
			return
		}
		if p.onEnd != nil {
			if m, ok := dataAny.(map[string]interface{}); ok {
				p.onEnd(invocationID, m)
			} else {
				p.onEnd(invocationID, map[string]interface{}{})
			}
		}
		if m, ok := dataAny.(map[string]interface{}); ok {
			p.endCh <- endResult{data: m}
		} else {
			p.endCh <- endResult{data: map[string]interface{}{}}
		}
		c.finishPending(invocationID)
		return
	}

	data, ok := dataAny.(map[string]interface{})
	if !ok {
		if s, ok2 := dataAny.(string); ok2 && s != "" {
			var parsed map[string]interface{}
			if err := json.Unmarshal([]byte(s), &parsed); err != nil {
				return
			}
			data = parsed
		} else {
			return
		}
	}
	c.logFrame("<<", map[string]interface{}{"invocationId": invocationID, "source": source, "target": msg["target"], "data": data})

	if e, ok := data["error"].(string); ok && e != "" {
		err := fmt.Errorf("%s", e)
		if p.onError != nil {
			p.onError(invocationID, err)
		}
		select {
		case p.endCh <- endResult{err: err}:
		default:
		}
		c.finishPending(invocationID)
		return
	}

	if p.isCall {
		select {
		case p.endCh <- endResult{data: data}:
		default:
		}
		c.finishPending(invocationID)
		return
	}

	phase, _ := data["phase"].(string)
	if phase == "event" {
		if p.onEvent != nil {
			p.onEvent(invocationID, data)
		}
		return
	}
	if phase == "end" {
		if p.onEnd != nil {
			p.onEnd(invocationID, data)
		}
		p.endCh <- endResult{data: data}
		c.finishPending(invocationID)
		return
	}

	err := fmt.Errorf("unsupported phase: %v", data["phase"])
	if p.onError != nil {
		p.onError(invocationID, err)
	}
	select {
	case p.endCh <- endResult{err: err}:
	default:
	}
	c.finishPending(invocationID)
}

func (c *WsClient) finishPending(invocationID string) {
	c.mu.Lock()
	delete(c.pending, invocationID)
	c.mu.Unlock()
}

func (c *WsClient) failAllPending(err error) {
	c.mu.Lock()
	items := make(map[string]*pendingStream, len(c.pending))
	for k, v := range c.pending {
		items[k] = v
	}
	c.pending = make(map[string]*pendingStream)
	c.mu.Unlock()

	for invocationID, p := range items {
		if p.onError != nil {
			p.onError(invocationID, err)
		}
		select {
		case p.endCh <- endResult{err: err}:
		default:
		}
	}
}

func (c *WsClient) logFrame(direction string, payload map[string]interface{}) {
	if c.logger == nil {
		return
	}
	raw, err := json.Marshal(payload)
	if err != nil {
		c.logger(fmt.Sprintf("WS %s %v", direction, payload))
		return
	}
	s := string(raw)
	if len(s) > 1200 {
		s = s[:1200] + "..."
	}
	c.logger(fmt.Sprintf("WS %s %s", direction, s))
}

func newInvocationID() string {
	return fmt.Sprintf("%d", time.Now().UnixNano())
}
