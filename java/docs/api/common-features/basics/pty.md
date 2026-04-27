# 💻 Pty API Reference

## Overview

The PTY module provides interactive terminal sessions in cloud sandbox
environments. Unlike the Command module which executes single commands,
PTY gives you a persistent, interactive shell with real-time streaming
output, terminal resize support, and session lifecycle management.


## 📚 Tutorial

[PTY Terminal Guide](../../../../../docs/guides/common-features/basics/pty-terminal.md)

Learn how to use interactive terminal sessions in cloud environments

## Pty

PTY module entry point – accessed as session.getPty().

### Constructor

```java
public Pty(Session session)
```

### Methods

### create

```java
public PtyHandle create(int cols, int rows, String cwd, Map<String, String> envs, String shell, Consumer<byte[]> onData, long timeoutMs) throws Exception
```

```java
public PtyHandle create() throws Exception
```

```java
public PtyHandle create(int cols, int rows, Consumer<byte[]> onData) throws Exception
```

Create a new PTY session.

**Parameters:**
- `cols` (int): Terminal columns (default 80)
- `rows` (int): Terminal rows (default 24)
- `cwd` (String): Working directory (null for default)
- `envs` (Map<String,String>): Extra environment variables (null for default)
- `shell` (String): Shell program (null for default)
- `onData` (Consumer<byte[]>): Callback for output data (may be null)
- `timeoutMs` (long): Timeout in milliseconds (0 defaults to 30 000)

**Returns:**
- `PtyHandle`: A PtyHandle connected to the new session

**Throws:**
- `PtyException`: if the terminal size is invalid
- `Exception`: on communication failure

### list

```java
public List<PtySession> list() throws Exception
```

List all active PTY sessions.

### connect

```java
public PtyHandle connect(String ptySessionId, Consumer<byte[]> onData) throws Exception
```

Reconnect to an existing PTY session.

### kill

```java
public void kill(String ptySessionId) throws Exception
```

Kill a PTY session by ID.



## PtyHandle

An active connection to a PTY session.

### Methods

### getPtySessionId

```java
public String getPtySessionId()
```

### isConnected

```java
public boolean isConnected()
```

### getExitCode

```java
public Integer getExitCode()
```

### sendInput

```java
public void sendInput(byte[] data) throws PtyNotConnectedException
```

Send input bytes to the PTY.

### resize

```java
public void resize(int cols, int rows) throws PtyNotConnectedException, PtyException
```

Resize the terminal.

### kill

```java
public void kill() throws Exception
```

Kill the PTY process.

### wait

```java
public int wait(int timeoutMs) throws PtyException
```

Wait for the PTY process to exit and return its exit code.

**Parameters:**
- `timeoutMs` (int): Timeout in milliseconds (0 for no timeout)

**Returns:**
- `int`: The exit code of the PTY process

**Throws:**
- `PtyException`: on error or timeout

### disconnect

```java
public void disconnect()
```

Disconnect from the PTY (process continues on server).



## PtySession

Read-only snapshot of a PTY session.

### Constructor

```java
public PtySession(String ptySessionId, int cols, int rows, String status, Integer exitCode)
```

### Methods

### getPtySessionId

```java
public String getPtySessionId()
```

### getCols

```java
public int getCols()
```

### getRows

```java
public int getRows()
```

### getExitCode

```java
public Integer getExitCode()
```



## 💡 Best Practices

- Always disconnect or wait when done with a PTY handle
- Use carriage return (\r) to submit commands instead of newline
- Handle the on_data callback efficiently as it may be called frequently
- Set terminal size to match the client for correct line wrapping
- Use appropriate timeouts with wait() to avoid blocking indefinitely

## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [Command API Reference](../../../api/common-features/basics/command.md)

