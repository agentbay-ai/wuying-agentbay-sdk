# PTY Terminal Sessions

## Overview

The PTY (Pseudo Terminal) module provides interactive terminal sessions in cloud sandbox environments. Unlike the [Command module](command-execution.md) which executes single commands and returns results, PTY gives you a persistent, interactive shell — similar to SSH — with real-time streaming output, terminal resize support, and session lifecycle management.

## When to Use PTY vs Command

| Feature | Command | PTY |
|---------|---------|-----|
| Single command execution | Best choice | Possible but overkill |
| Interactive programs (vim, top, etc.) | Not supported | Full support |
| Real-time streaming output | Waits for completion | Streams as produced |
| Terminal size / ANSI escape codes | No terminal | Full xterm-256color |
| Multiple concurrent shells | One-shot | Multiple sessions |
| Disconnect and reconnect | Not applicable | Supported |

## Key Concepts

### PTY Session
A PTY session represents a running shell process on the cloud sandbox. Each session has a unique `ptySessionId`, terminal dimensions (`cols` x `rows`), a status (`running` / `exited`), and an optional exit code when the process terminates.

### PTY Handle
A handle is a client-side connection to a PTY session. You can send input, receive streaming output via a callback, resize the terminal, disconnect/reconnect, wait for process exit, or kill the process.

### Lifecycle

```
create() --> PtyHandle (connected)
                |
                |-- sendInput() / resize()
                |-- onData callback receives output
                |
                |-- disconnect() --> process keeps running
                |                         |
                |                    connect(id) --> new PtyHandle
                |
                |-- kill() --> process terminated (exit code -9)
                |
                +-- "exit" command --> process exits naturally
                                      wait() returns exit code
```

## Quick Start

> The examples below use Python async. All four SDKs (Python sync/async, TypeScript, Go, Java) provide the same PTY capabilities — see the [API Reference](#api-reference) section for language-specific docs and runnable examples.

```python
import asyncio
from agentbay import AsyncAgentBay, CreateSessionParams

async def main():
    client = AsyncAgentBay()
    result = await client.create(CreateSessionParams())
    session = result.session

    output = []
    handle = await session.pty.create(
        cols=80, rows=24,
        on_data=lambda data: output.append(data.decode("utf-8", errors="replace"))
    )
    await asyncio.sleep(1)

    await handle.send_input(b"echo 'Hello PTY!'\r")
    await asyncio.sleep(2)

    print("".join(output))
    handle.disconnect()
    await session.delete()

asyncio.run(main())
```

## Common Operations

### Resize Terminal

```python
await handle.resize(120, 40)
```

### Send Control Characters

```python
await handle.send_input(b"\x03")   # Ctrl+C
await handle.send_input(b"\x04")   # Ctrl+D (EOF)
await handle.send_input(b"\x1b")   # Escape
```

### Wait for Exit

```python
await handle.send_input(b"exit\r")
exit_code = await handle.wait(timeout_s=10)
```

### Kill a Process

```python
await handle.kill()
exit_code = await handle.wait(timeout_s=10)  # returns -9
```

### Disconnect and Reconnect

```python
pty_id = handle.pty_session_id
handle.disconnect()

# Later...
handle2 = await session.pty.connect(pty_id, on_data=on_data)
```

### List Active Sessions

```python
sessions = await session.pty.list()
for s in sessions:
    print(f"PTY {s.pty_session_id}: {s.status}")
```

## Best Practices

1. **Always disconnect or wait** — When done with a PTY handle, either `disconnect()` (to keep the process running) or `wait()` after sending `exit` / `kill()` to clean up properly.

2. **Use appropriate timeouts** — `wait()` accepts a timeout to avoid blocking indefinitely.

3. **Handle output asynchronously** — The `onData` callback may be invoked from a background thread or event loop. Avoid blocking operations inside it.

4. **Set terminal size to match the client** — Pass the actual terminal dimensions when creating a PTY to ensure correct line wrapping and cursor positioning.

5. **Use `\r` (carriage return) to submit commands** — PTY interprets raw terminal input, so you need `\r` instead of `\n` to press Enter.

6. **Consider encoding** — Input is automatically encoded as UTF-8 when possible, falling back to Base64 for binary data. Output arrives as raw bytes and should be decoded with error handling.

## Related Resources

- [Command Execution](command-execution.md) — For simple, non-interactive command execution
- [Session Management](session-management.md) — Creating and managing sessions

## API Reference

| Language | API Docs | Runnable Example |
|----------|----------|------------------|
| Python (async) | [AsyncPty API](../../../../python/docs/api/async/async-pty.md) | [pty_terminal_example.py](../../../../python/docs/examples/_async/common-features/basics/pty_operations/pty_terminal_example.py) |
| Python (sync) | [Pty API](../../../../python/docs/api/sync/pty.md) | [pty_terminal_example.py](../../../../python/docs/examples/_sync/common-features/basics/pty_operations/pty_terminal_example.py) |
| TypeScript | [Pty API](../../../../typescript/docs/api/common-features/basics/pty.md) | [pty-example.ts](../../../../typescript/docs/examples/common-features/basics/pty-example/pty-example.ts) |
| Go | [Pty API](../../../../golang/docs/api/common-features/basics/pty.md) | [main.go](../../../../golang/docs/examples/common-features/basics/pty_example/main.go) |
| Java | [Pty API](../../../../java/docs/api/common-features/basics/pty.md) | [README](../../../../java/docs/examples/pty_example/README.md) |
