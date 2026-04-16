# PTY Terminal API Reference

## 💻 Related Tutorial

- [PTY Terminal Guide](../../../../../docs/guides/common-features/basics/pty-terminal.md) - Learn how to use interactive terminal sessions in cloud environments

## Overview

The PTY module provides interactive terminal sessions in cloud sandbox
environments. Unlike the Command module which executes single commands,
PTY gives you a persistent, interactive shell with real-time streaming
output, terminal resize support, and session lifecycle management.

Package pty provides interactive terminal (PTY) sessions in cloud sandbox environments.

## Type CreateOptions

```go
type CreateOptions struct {
	Cols		int
	Rows		int
	Cwd		string
	Envs		map[string]string
	Shell		string
	OnData		func([]byte)
	TimeoutMs	int
}
```

CreateOptions configures a new PTY session.

## Type Pty

```go
type Pty struct {
	session	interface {
		GetWsClient() (interface{}, error)
	}
	mu			sync.Mutex
	wsClient		*internal.WsClient
	handles			map[string]*PtyHandle
	callbackRegistered	bool
}
```

Pty is the PTY module entry point, accessed as session.Pty.

### Methods

### Connect

```go
func (p *Pty) Connect(ptySessionID string, onData func([]byte)) (*PtyHandle, error)
```

Connect reconnects to an existing PTY session.

### Create

```go
func (p *Pty) Create(opts CreateOptions) (*PtyHandle, error)
```

Create creates a new PTY session.

### KillSession

```go
func (p *Pty) KillSession(ptySessionID string) error
```

KillSession kills a PTY session by ID.

### List

```go
func (p *Pty) List() ([]PtySession, error)
```

List returns all active PTY sessions.

### Related Functions

### NewPty

```go
func NewPty(session interface {
	GetWsClient() (interface{}, error)
}) *Pty
```

NewPty creates a new Pty module for the given session.

## Type PtyHandle

```go
type PtyHandle struct {
	mu		sync.Mutex
	ptySessionID	string
	ptyModule	*Pty
	onData		func([]byte)
	connected	bool
	exitCode	*int
	errorMsg	*string
}
```

PtyHandle is an active connection to a PTY session.

### Methods

### Disconnect

```go
func (h *PtyHandle) Disconnect()
```

Disconnect detaches this handle from the PTY (process continues on server).

### ExitCode

```go
func (h *PtyHandle) ExitCode() *int
```

ExitCode returns the exit code of the PTY process, or nil if not yet exited.

### IsConnected

```go
func (h *PtyHandle) IsConnected() bool
```

IsConnected returns whether this handle is still connected.

### Kill

```go
func (h *PtyHandle) Kill() error
```

Kill sends SIGKILL to the PTY process.

### PtySessionID

```go
func (h *PtyHandle) PtySessionID() string
```

PtySessionID returns the PTY session identifier.

### Resize

```go
func (h *PtyHandle) Resize(cols, rows int) error
```

Resize changes the terminal size.

### SendInput

```go
func (h *PtyHandle) SendInput(data []byte) error
```

SendInput sends input bytes to the PTY.

### Wait

```go
func (h *PtyHandle) Wait(timeoutMs int) (int, error)
```

Wait blocks until the PTY process exits and returns its exit code. Pass 0 for no timeout.

## Type PtySession

```go
type PtySession struct {
	PtySessionID	string
	Cols		int
	Rows		int
	Status		string
	ExitCode	*int
}
```

PtySession is a read-only snapshot of a PTY session.

## Best Practices

1. Always disconnect or wait when done with a PTY handle
2. Use carriage return (\r) to submit commands instead of newline
3. Handle the on_data callback efficiently as it may be called frequently
4. Set terminal size to match the client for correct line wrapping
5. Use appropriate timeouts with wait() to avoid blocking indefinitely

## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)

---

*Documentation generated automatically from Go source code.*
