# Context Manager API Reference

> **💡 Async Version**: This documentation covers the synchronous API. For async/await support, see [`AsyncContextManager`](../async/async-context-manager.md) which provides the same functionality with async methods.



## ContextManager

```python
class ContextManager()
```

Manages context operations within a session in the AgentBay cloud environment.

The SyncContextManager provides methods to get information about context synchronization
status and to synchronize contexts with the session.

### __init__

```python
def __init__(self, session)
```

### bind

```python
def bind(*contexts: Union[ContextSync, BetaContextMount],
         wait_for_completion: bool = True) -> ContextBindResult
```

Dynamically bind one or more contexts to the running session.

Accepts both ContextSync (sync-based persistence) and BetaContextMount (direct-mount
write-through persistence) objects. They can be mixed in a single call.

**Arguments**:

    *contexts: One or more ContextSync or BetaContextMount objects.
    wait_for_completion: If True, waits for bind registration and data download
  to complete (ContextSync only). BetaContextMount only waits for bind registration.
  

**Returns**:

  ContextBindResult with success status, error_message, and request_id.
  
  Example
  

```python
result = session.context.bind(
ContextSync(context_id="SdkCtx-xxx", path="/tmp/ctx-data"),
)

result = session.context.bind(
BetaContextMount(context_id="SdkCtx-yyy", path="/mnt/data"),
)

```

### list_bindings

```python
def list_bindings() -> ContextBindingsResult
```

Query all context bindings on the current session.

**Returns**:

  ContextBindingsResult with list of ContextBinding objects.
  
  Example
  

```python
result = session.context.list_bindings()
for binding in result.bindings:
print(f"Context {binding.context_id} at {binding.path}")

```

### info

```python
def info(context_id: Optional[str] = None,
         path: Optional[str] = None,
         task_type: Optional[str] = None) -> ContextInfoResult
```

Get information about context synchronization status synchronously.

**Arguments**:

    context_id: Optional ID of the context to get information for
    path: Optional path where the context is mounted
    task_type: Optional type of task to get information for (e.g., "upload", "download")
  

**Returns**:

    ContextInfoResult: Result object containing context status data and request ID
  

**Example**:

session_result = agent_bay.create()
if session_result.success:
session = session_result.session
result = session.context_manager.info(
context_id="project-data",
path="/mnt/shared",
task_type="upload",
)
for status in result.context_status_data:
    print(f"{status.context_id}: {status.status}")
session.delete()

### sync

```python
def sync(context_id: Optional[str] = None,
         path: Optional[str] = None,
         mode: Optional[str] = None,
         max_retries: int = 150,
         retry_interval: int = 500) -> ContextSyncResult
```

Synchronize a context with the session synchronously.

**Arguments**:

    context_id: Optional ID of the context to synchronize
    path: Optional path where the context should be mounted; not limited to
  the path specified when creating the session (other backend-allowed
  paths are acceptable)
    mode: Optional synchronization mode (e.g., "upload", "download")
    max_retries: Maximum number of retries for polling completion status (default: 150)
    retry_interval: Initial interval in milliseconds for exponential backoff
  polling (default: 500). Interval grows by factor 1.1 up to 5000ms.
  

**Returns**:

    ContextSyncResult: Result object containing success status and request ID
  

**Example**:

session_result = agent_bay.create()
if session_result.success:
session = session_result.session
sync_result = session.context_manager.sync(
context_id="project-data",
path="/mnt/shared",
mode="upload",
max_retries=60,
retry_interval=1000,
)
print(f"Sync completed: {sync_result.success}")
session.delete()


**Example**:

session_result = agent_bay.create()
if session_result.success:
session = session_result.session
async def on_sync_complete(result):
print(f"Callback received: {result.success}")
sync_result = session.context_manager.sync(
context_id="reports",
path="/mnt/reports",
mode="download",
max_retries=80,
retry_interval=500,
)
on_sync_complete(sync_result)
session.delete()

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
