# AgentBay API Reference

> **💡 Async Version**: This documentation covers the synchronous API. For async/await support, see [`AsyncAgentBay`](../async/async-agentbay.md) which provides the same functionality with async methods.

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session



## AgentBay

```python
class AgentBay()
```

AgentBay represents the main client for interacting with the AgentBay cloud runtime
environment synchronously.

### __init__

```python
def __init__(self, api_key: str = "",
             cfg: Optional[Config] = None,
             env_file: Optional[str] = None)
```

Initialize AgentBay client.

**Arguments**:

    api_key: API key for authentication. If not provided, will read from AGENTBAY_API_KEY environment variable.
    cfg: Configuration object. If not provided, will load from environment variables and .env file.
    env_file: Custom path to .env file. If not provided, will search upward from current directory.

### create

```python
def create(params: Optional[CreateSessionParams] = None) -> SessionResult
```

Create a new session in the AgentBay cloud environment synchronously.

**Arguments**:

- `params` _Optional[CreateSessionParams], optional_ - Parameters for creating the session.
  Defaults to None (uses default configuration).
  

**Returns**:

    SessionResult: Result containing the created session and request ID.
  - success (bool): True if the operation succeeded
  - session (SyncSession): The created session object (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    ValueError: If API key is not provided and AGENTBAY_API_KEY environment variable is not set.
    ClientException: If the API request fails due to network or authentication issues.
  

**Example**:

```python
result = agent_bay.create()
session = result.session
info_result = session.info()
print(f"Session ID: {info_result.session_id}")
session.delete()
```

### list

```python
def list(labels: Optional[Dict[str, str]] = None,
         page: Optional[int] = None,
         limit: Optional[int] = None,
         status: Optional[str] = None,
         image_id: Optional[str] = None) -> SessionListResult
```

Returns paginated list of session IDs filtered by labels synchronously.

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
def delete(session: Session, sync_context: bool = False) -> DeleteResult
```

Delete a session by session object synchronously.

**Arguments**:

- `session` _SyncSession_ - The session to delete.
- `sync_context` _bool_ - Whether to sync context data (trigger file uploads)
  before deleting the session. Defaults to False.
  

**Returns**:

    DeleteResult: Result indicating success or failure and request ID.

### get

```python
def get(session_id: str) -> SessionResult
```

Get a session by its ID synchronously.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve. Must be a non-empty string.
  

**Returns**:

    SessionResult: Result containing the Session instance, request ID, and success status.

### beta_pause

```python
def beta_pause(session: Session,
               timeout: int = 600,
               poll_interval: float = 2.0) -> SessionPauseResult
```

Synchronously pause a session (beta), putting it into a dormant state.

**Notes**:

  This feature is currently in whitelist-only access.
  Contact agentbay_dev@alibabacloud.com to request access.

### beta_resume

```python
def beta_resume(session: Session,
                timeout: int = 600,
                poll_interval: float = 2.0) -> SessionResumeResult
```

Synchronously resume a session (beta) from a paused state.

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./session.md)
- [Context API Reference](./context.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
