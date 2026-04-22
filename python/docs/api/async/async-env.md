# AsyncEnv API Reference

## Overview

The Env module provides methods for setting and querying global environment variables within a session sandbox.
Variables set via this module persist across all MCP tools (shell, code interpreter, etc.) within the session.




## AsyncEnv

```python
class AsyncEnv(AsyncBaseService)
```

Async environment variable management service for AgentBay sessions.

Provides methods to set and get global environment variables that persist
across all MCP tools (shell, code interpreter, etc.) within a session.

### __init__

```python
def __init__(self, session)
```

### set

```python
async def set(envs: Dict[str, str]) -> BoolResult
```

Set or update global environment variables in the session sandbox.

Existing keys are overwritten; new keys are added. Variables become
visible to all subsequent MCP tool invocations (shell, code interpreter, etc.).

**Arguments**:

    envs: Dictionary of environment variable key-value pairs.
  Both keys and values must be strings. Must not be empty.
  

**Returns**:

    BoolResult: Result with success=True if variables were set successfully.
  

**Raises**:

    ValueError: If envs is empty or contains non-string keys/values.

### get

```python
async def get(keys: Optional[List[str]] = None) -> EnvResult
```

Get global environment variables from the session sandbox.

**Arguments**:

    keys: Optional list of specific variable names to retrieve.
  If None or empty, returns all environment variables.
  

**Returns**:

    EnvResult: Result containing envs dict with variable key-value pairs.

## Best Practices

1. Use env.set to configure variables before running shell commands or code
2. Both keys and values must be strings
3. Setting a key that already exists will overwrite the previous value
4. Use env.get with specific keys to reduce response size

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./async-session.md)
- [Command API Reference](./async-command.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
