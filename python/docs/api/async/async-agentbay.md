# AsyncAgentBay API Reference

> **💡 Sync Version**: This documentation covers the asynchronous API. For synchronous operations, see [`AgentBay`](../sync/agentbay.md).
>
> ⚡ **Performance Advantage**: Async API enables concurrent operations with 4-6x performance improvements for parallel tasks.

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session



## AsyncAgentBay

```python
class AsyncAgentBay()
```

AsyncAgentBay represents the main client for interacting with the AgentBay cloud runtime
environment asynchronously.

### __init__

```python
def __init__(self, api_key: str = "",
             cfg: Optional[Config] = None,
             env_file: Optional[str] = None)
```

Initialize AsyncAgentBay client.

**Arguments**:

    api_key: API key for authentication. If not provided, will read from AGENTBAY_API_KEY environment variable.
    cfg: Configuration object. If not provided, will load from environment variables and .env file.
    env_file: Custom path to .env file. If not provided, will search upward from current directory.

### create

```python
async def create(
        params: Optional[CreateSessionParams] = None) -> SessionResult
```

Create a new session in the AgentBay cloud environment asynchronously.

**Arguments**:

- `params` _Optional[CreateSessionParams], optional_ - Parameters for creating the session.
  Defaults to None (uses default configuration).
  

**Returns**:

    SessionResult: Result containing the created session and request ID.
  - success (bool): True if the operation succeeded
  - session (AsyncSession): The created session object (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    ValueError: If API key is not provided and AGENTBAY_API_KEY environment variable is not set.
    ClientException: If the API request fails due to network or authentication issues.
  

**Example**:

```python
result = await agent_bay.create()
session = result.session
info_result = await session.info()
print(f"Session ID: {info_result.session_id}")
await session.delete()
```

### list

```python
async def list(labels: Optional[Dict[str, str]] = None,
               page: Optional[int] = None,
               limit: Optional[int] = None,
               status: Optional[str] = None,
               image_id: Optional[str] = None) -> SessionListResult
```

Returns paginated list of session IDs filtered by labels asynchronously.

**Arguments**:

- `labels` _Optional[Dict[str, str]], optional_ - Labels to filter sessions.
  Defaults to None (returns all sessions).
- `page` _Optional[int], optional_ - Page number for pagination (starting from 1).
  Defaults to None (returns first page).
- `limit` _Optional[int], optional_ - Maximum number of items per page.
  Defaults to None (uses default of 10).
- `status` _Optional[str], optional_ - Status to filter sessions. Must be one of:
  RUNNING, PAUSING, PAUSED, RESUMING, DELETING, DELETED.
  Defaults to None (returns sessions with any status).
- `image_id` _Optional[str], optional_ - Image ID to filter sessions.
  Defaults to None (returns sessions with any image).
  

**Returns**:

    SessionListResult: Paginated list of session IDs that match the filters.

### delete

```python
async def delete(session: AsyncSession,
                 sync_context: bool = False) -> DeleteResult
```

Delete a session by session object asynchronously.

**Arguments**:

- `session` _AsyncSession_ - The session to delete.
- `sync_context` _bool_ - Whether to sync context data (trigger file uploads)
  before deleting the session. Defaults to False.
  

**Returns**:

    DeleteResult: Result indicating success or failure and request ID.

### get

```python
async def get(session_id: str) -> SessionResult
```

Get a session by its ID asynchronously.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve. Must be a non-empty string.
  

**Returns**:

    SessionResult: Result containing the Session instance, request ID, and success status.

### beta_pause

```python
async def beta_pause(session: AsyncSession,
                     timeout: int = 600,
                     poll_interval: float = 2.0) -> SessionPauseResult
```

Asynchronously pause a session (beta), putting it into a dormant state.

**Notes**:

  This feature is currently in whitelist-only access.
  Contact agentbay_dev@alibabacloud.com to request access.

### beta_resume

```python
async def beta_resume(session: AsyncSession,
                      timeout: int = 600,
                      poll_interval: float = 2.0) -> SessionResumeResult
```

Asynchronously resume a session (beta) from a paused state.

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./async-session.md)
- [Context API Reference](./async-context.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
