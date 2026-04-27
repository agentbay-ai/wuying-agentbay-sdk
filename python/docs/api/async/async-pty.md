# AsyncPty API Reference

> **💡 Sync Version**: This documentation covers the asynchronous API. For synchronous operations, see [`Pty`](../sync/pty.md).
>
> ⚡ **Performance Advantage**: Async API enables concurrent operations with 4-6x performance improvements for parallel tasks.

## 💻 Related Tutorial

- [PTY Terminal Guide](../../../../docs/guides/common-features/basics/pty-terminal.md) - Learn how to use interactive terminal sessions in cloud environments

## Overview

The PTY module provides interactive terminal sessions in cloud sandbox
environments. Unlike the Command module which executes single commands,
PTY gives you a persistent, interactive shell with real-time streaming
output, terminal resize support, and session lifecycle management.




#### logger

```python
logger = logging.getLogger(__name__)
```

#### PTY_TARGET

```python
PTY_TARGET = "PTY_SERVER"
```

#### DEFAULT_ENVS

```python
DEFAULT_ENVS = {
    "TERM": "xterm-256color",
    "LANG": "en_US.UTF-8",
}
```

#### MAX_TERMINAL_SIZE

```python
MAX_TERMINAL_SIZE = 500
```

## PtySession

```python
@dataclass
class PtySession()
```

Read-only snapshot of a PTY session.

#### pty_session_id: `str`

```python
pty_session_id = None
```

#### cols: `int`

```python
cols = None
```

#### rows: `int`

```python
rows = None
```

#### status: `str`

```python
status = None
```

#### exit_code: `Optional[int]`

```python
exit_code = None
```

## PtyHandle

```python
class PtyHandle()
```

Active connection to a PTY session.

### __init__

```python
def __init__(self, pty_session_id: str,
             pty_module: "AsyncPty",
             on_data: Optional[Callable[[bytes], None]] = None)
```

### pty_session_id

```python
@property
def pty_session_id() -> str
```

### is_connected

```python
@property
def is_connected() -> bool
```

### exit_code

```python
@property
def exit_code() -> Optional[int]
```

### send_input

```python
async def send_input(data: bytes) -> None
```

Send input bytes to the PTY.

### resize

```python
async def resize(cols: int, rows: int) -> None
```

Resize the terminal.

### kill

```python
async def kill() -> None
```

Kill the PTY process (SIGKILL).

### wait

```python
async def wait(timeout_s: Optional[float] = None) -> int
```

Wait for the PTY process to exit. Returns the exit code.

### disconnect

```python
def disconnect() -> None
```

Disconnect from the PTY (local only, process continues on server).

## AsyncPty

```python
class AsyncPty()
```

PTY module entry point, accessed as session.pty.

### __init__

```python
def __init__(self, session)
```

### create

```python
async def create(cols: int = 80,
                 rows: int = 24,
                 cwd: Optional[str] = None,
                 envs: Optional[Dict[str, str]] = None,
                 shell: Optional[str] = None,
                 on_data: Optional[Callable[[bytes], None]] = None,
                 timeout_s: Optional[float] = None) -> PtyHandle
```

Create a new PTY session and return a PtyHandle.

### list

```python
async def list() -> List[PtySession]
```

List all active PTY sessions.

### connect

```python
async def connect(
        pty_session_id: str,
        on_data: Optional[Callable[[bytes], None]] = None) -> PtyHandle
```

Connect to an existing PTY session.

### kill

```python
async def kill(pty_session_id: str) -> None
```

Kill a PTY session by ID.

## Best Practices

1. Always disconnect or wait when done with a PTY handle
2. Use carriage return (\r) to submit commands instead of newline
3. Handle the on_data callback efficiently as it may be called frequently
4. Set terminal size to match the client for correct line wrapping
5. Use appropriate timeouts with wait() to avoid blocking indefinitely

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./async-session.md)
- [Command API Reference](./async-command.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
