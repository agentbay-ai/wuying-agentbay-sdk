# Exceptions API Reference

## AgentBayError

```python
class AgentBayError(Exception)
```

Base exception for all AgentBay SDK errors.

### __init__

```python
def __init__(self, message=None, *args, **kwargs)
```

## WsCancelledError

```python
class WsCancelledError(AgentBayError)
```

Raised when a WS stream is cancelled by the caller.

## AuthenticationError

```python
class AuthenticationError(AgentBayError)
```

Raised when there is an authentication error.

### __init__

```python
def __init__(self, message="Authentication failed", *args, **kwargs)
```

## APIError

```python
class APIError(AgentBayError)
```

Raised when there is an error with the API.

### __init__

```python
def __init__(self, message="API error", status_code=None, *args, **kwargs)
```

## FileError

```python
class FileError(AgentBayError)
```

Raised for errors related to file operations.

### __init__

```python
def __init__(self, message="File operation error", *args, **kwargs)
```

## CommandError

```python
class CommandError(AgentBayError)
```

Raised for errors related to command execution.

### __init__

```python
def __init__(self, message="Command execution error", *args, **kwargs)
```

## SessionError

```python
class SessionError(AgentBayError)
```

Raised for errors related to session operations.

### __init__

```python
def __init__(self, message="Session error", *args, **kwargs)
```

## OssError

```python
class OssError(AgentBayError)
```

Raised for errors related to OSS operations.

### __init__

```python
def __init__(self, message="OSS operation error", *args, **kwargs)
```

## BrowserError

```python
class BrowserError(AgentBayError)
```

Raised when there is an error with the browser.

### __init__

```python
def __init__(self, message="Browser error", *args, **kwargs)
```

## AgentError

```python
class AgentError(AgentBayError)
```

Raised for errors related to Agent actions.

### __init__

```python
def __init__(self, message="Agent action error", *args, **kwargs)
```

## ClearanceTimeoutError

```python
class ClearanceTimeoutError(AgentBayError)
```

Raised when context clearing operation times out.

### __init__

```python
def __init__(self, message="Context clearing operation timed out", *args, **kwargs)
```

## GitError

```python
class GitError(AgentBayError)
```

Base exception for all git operations.

**Attributes**:

    exit_code: The exit code returned by the git command.
    stderr: The stderr output from the git command.

### __init__

```python
def __init__(self, message="Git operation error",
             exit_code=1,
             stderr="",
             *args,
             **kwargs)
```

## GitAuthError

```python
class GitAuthError(GitError)
```

Raised when git authentication fails.

Common causes include invalid credentials, missing access tokens,
or insufficient repository permissions.

### __init__

```python
def __init__(self, message="Git authentication error",
             exit_code=1,
             stderr="",
             *args,
             **kwargs)
```

## GitNotFoundError

```python
class GitNotFoundError(GitError)
```

Raised when git is not installed or not found on the remote environment.

### __init__

```python
def __init__(self, message="Git not found",
             exit_code=127,
             stderr="",
             *args,
             **kwargs)
```

## GitConflictError

```python
class GitConflictError(GitError)
```

Raised when a git merge or rebase conflict occurs.

### __init__

```python
def __init__(self, message="Git merge conflict",
             exit_code=1,
             stderr="",
             *args,
             **kwargs)
```

## GitNotARepoError

```python
class GitNotARepoError(GitError)
```

Raised when the target directory is not a git repository.

### __init__

```python
def __init__(self, message="Not a git repository",
             exit_code=128,
             stderr="",
             *args,
             **kwargs)
```

## PtyError

```python
class PtyError(AgentBayError)
```

Base exception for all PTY operations.

### __init__

```python
def __init__(self, message="PTY operation error", *args, **kwargs)
```

## PtySessionNotFoundError

```python
class PtySessionNotFoundError(PtyError)
```

Raised when a PTY session does not exist or has been terminated.

### __init__

```python
def __init__(self, message="PTY session not found", *args, **kwargs)
```

## PtyNotConnectedError

```python
class PtyNotConnectedError(PtyError)
```

Raised when attempting to use a PTY handle that is not connected.

### __init__

```python
def __init__(self, message="PTY handle is not connected", *args, **kwargs)
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
