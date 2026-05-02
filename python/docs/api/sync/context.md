# Context API Reference

> **💡 Async Version**: This documentation covers the synchronous API. For async/await support, see [`AsyncContextService`](../async/async-context.md) which provides the same functionality with async methods.

## 💾 Related Tutorial

- [Data Persistence Guide](../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence



## Context

```python
class Context()
```

Represents a persistent storage context in the AgentBay cloud environment.

**Attributes**:

- `id` _str_ - The unique identifier of the context.
- `name` _str_ - The name of the context.
- `created_at` _str_ - Date and time when the Context was created.
- `last_used_at` _str_ - Date and time when the Context was last used.

### __init__

```python
def __init__(self, id: str,
             name: str,
             created_at: Optional[str] = None,
             last_used_at: Optional[str] = None)
```

Initialize a Context object.

**Arguments**:

- `id` _str_ - The unique identifier of the context.
- `name` _str_ - The name of the context.
- `created_at` _Optional[str], optional_ - Date and time when the Context was
  created. Defaults to None.
- `last_used_at` _Optional[str], optional_ - Date and time when the Context was
  last used. Defaults to None.

## ContextResult

```python
class ContextResult(ApiResponse)
```

Result of operations returning a Context.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             context_id: str = "",
             context: Optional[Context] = None,
             error_message: str = "")
```

Initialize a ContextResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
- `success` _bool, optional_ - Whether the operation was successful.
- `context_id` _str, optional_ - The unique identifier of the context.
- `context` _Optional[Context], optional_ - The Context object.
- `error_message` _str, optional_ - Error message if operation failed.

## ContextListResult

```python
class ContextListResult(ApiResponse)
```

Result of operations returning a list of Contexts.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             contexts: Optional[List[Context]] = None,
             next_token: Optional[str] = None,
             max_results: Optional[int] = None,
             total_count: Optional[int] = None,
             error_message: str = "")
```

Initialize a ContextListResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
- `success` _bool, optional_ - Whether the operation was successful.
- `contexts` _Optional[List[Context]], optional_ - The list of context objects.
- `next_token` _Optional[str], optional_ - Token for the next page of results.
- `max_results` _Optional[int], optional_ - Maximum number of results per page.
- `total_count` _Optional[int], optional_ - Total number of contexts available.
- `error_message` _str, optional_ - Error message if operation failed.

## ContextFileEntry

```python
class ContextFileEntry()
```

Represents a file item in a context.

### __init__

```python
def __init__(self, file_id: str,
             file_name: str,
             file_path: str,
             file_type: Optional[str] = None,
             gmt_create: Optional[str] = None,
             gmt_modified: Optional[str] = None,
             size: Optional[int] = None,
             status: Optional[str] = None)
```

## FileUrlResult

```python
class FileUrlResult(ApiResponse)
```

Result of a presigned URL request.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             url: str = "",
             expire_time: Optional[int] = None,
             error_message: str = "")
```

## ContextFileListResult

```python
class ContextFileListResult(ApiResponse)
```

Result of file listing operation.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             entries: Optional[List[ContextFileEntry]] = None,
             count: Optional[int] = None,
             next_token: Optional[str] = None)
```

## ClearContextResult

```python
class ClearContextResult(OperationResult)
```

Result of context clear operations, including the real-time status.

**Attributes**:

- `request_id` _str_ - Unique identifier for the API request.
- `success` _bool_ - Whether the operation was successful.
- `error_message` _str_ - Error message if the operation failed.
- `status` _Optional[str]_ - Current status of the clearing task. This corresponds to the
  context's state field. Possible values:
  - "clearing": Context data is being cleared (in progress)
  - "available": Clearing completed successfully
  - Other values may indicate the context state after clearing
- `context_id` _Optional[str]_ - The unique identifier of the context being cleared.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             error_message: str = "",
             status: Optional[str] = None,
             context_id: Optional[str] = None)
```

## ContextListParams

```python
class ContextListParams()
```

Parameters for listing contexts with pagination support.

### __init__

```python
def __init__(self, max_results: Optional[int] = None,
             next_token: Optional[str] = None,
             session_id: Optional[str] = None)
```

Initialize ContextListParams.

**Arguments**:

- `max_results` _Optional[int], optional_ - Maximum number of results per page.
  Defaults to 10 if not specified.
- `next_token` _Optional[str], optional_ - Token for the next page of results.
- `session_id` _Optional[str], optional_ - Filter by session ID.

## ContextService

```python
class ContextService()
```

Provides methods to manage persistent contexts in the AgentBay cloud environment.

### __init__

```python
def __init__(self, agent_bay: "AgentBay")
```

Initialize the ContextService.

**Arguments**:

- `agent_bay` _AgentBay_ - The AgentBay instance.

### list

```python
def list(params: Optional[ContextListParams] = None) -> ContextListResult
```

Lists all available contexts with pagination support.

**Arguments**:

- `params` _Optional[ContextListParams], optional_ - Parameters for listing contexts.
  If None, defaults will be used.
  

**Returns**:

    ContextListResult: A result object containing the list of Context objects,
  pagination information, and request ID.
  

**Example**:

```python
result = agent_bay.context.list()
params = ContextListParams(max_results=20, next_token=result.next_token)
next_result = agent_bay.context.list(params)
```

### get

```python
def get(name: Optional[str] = None,
        create: bool = False,
        context_id: Optional[str] = None) -> ContextResult
```

Gets a context by name or ID. Optionally creates it if it doesn't exist.

**Arguments**:

- `name` _Optional[str], optional_ - The name of the context to get. Defaults to None.
- `create` _bool, optional_ - Whether to create the context if it doesn't exist. Defaults to False.
- `context_id` _Optional[str], optional_ - The ID of the context to get. Defaults to None.
  

**Returns**:

    ContextResult: The ContextResult object containing the Context and request ID.
  - success (bool): True if the operation succeeded
  - context (Context): The context object (if success is True)
  - context_id (str): The ID of the context
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    AgentBayError: If neither name nor context_id is provided, or if create=True with context_id.
  

**Example**:

```python
result = agent_bay.context.get(name="my-context")
result = agent_bay.context.get(name="new-context", create=True)
result = agent_bay.context.get(context_id="ctx-04bdwfj7u22a1s30g")
```


**Notes**:

- Either name or context_id must be provided (not both)
- When create=True, only name parameter is allowed
- Created contexts are persistent and can be shared across sessions
- Context names must be unique within your account


**See Also**:

SyncContextService.list, SyncContextService.update, SyncContextService.delete

### create

```python
def create(name: str) -> ContextResult
```

Creates a new context with the given name.

**Arguments**:

- `name` _str_ - The name for the new context.
  

**Returns**:

    ContextResult: The created ContextResult object with request ID.
  

**Example**:

```python
result = agent_bay.context.create("my-new-context")
```

### update

```python
def update(context: Context) -> OperationResult
```

Updates the specified context (currently only name can be updated).

**Arguments**:

- `context` _Context_ - The Context object to update. Must have id and name attributes.
  

**Returns**:

    OperationResult: Result object containing success status and request ID.
  - success (bool): True if the operation succeeded
  - data (str): Success message (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    AgentBayError: If the context update fails.
  

**Example**:

```python
result = agent_bay.context.get(name="old-name")
result.context.name = "new-name"
update_result = agent_bay.context.update(result.context)
```


**Notes**:

- Currently only the context name can be updated
- Context ID cannot be changed
- The context must exist before it can be updated
- Updated name must be unique within your account


**See Also**:

SyncContextService.get, SyncContextService.list, SyncContextService.delete

### delete

```python
def delete(context: Context) -> OperationResult
```

Deletes the specified context.

**Arguments**:

- `context` _Context_ - The Context object to delete.
  

**Returns**:

    OperationResult: Result object containing success status and request ID.
  

**Example**:

```python
result = agent_bay.context.get(name="my-context")
delete_result = agent_bay.context.delete(result.context)
```

### get_file_download_url

```python
def get_file_download_url(context_id: str, file_path: str) -> FileUrlResult
```

Get a presigned download URL for a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path to the file in the context.
  

**Returns**:

    FileUrlResult: A result object containing the presigned URL, expire time, and request ID.
  

**Notes**:

  The presigned URL expires in 1 hour by default.
  

**Example**:

```python
ctx_result = agent_bay.context.get(name="my-context", create=True)
url_result = agent_bay.context.get_file_download_url(ctx_result.context_id, "/path/to/file.txt")
print(url_result.url)
```

### get_file_upload_url

```python
def get_file_upload_url(context_id: str, file_path: str) -> FileUrlResult
```

Get a presigned upload URL for a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path to the file in the context.
  

**Returns**:

    FileUrlResult: A result object containing the presigned URL, expire time, and request ID.
  

**Notes**:

  The presigned URL expires in 1 hour by default.
  

**Example**:

```python
ctx_result = agent_bay.context.get(name="my-context", create=True)
url_result = agent_bay.context.get_file_upload_url(ctx_result.context_id, "/path/to/file.txt")
print(url_result.url)
```

### delete_file

```python
def delete_file(context_id: str, file_path: str) -> OperationResult
```

Delete a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path to the file to delete.
  

**Returns**:

    OperationResult: A result object containing success status and request ID.
  

**Example**:

```python
ctx_result = agent_bay.context.get(name="my-context", create=True)
delete_result = agent_bay.context.delete_file(ctx_result.context_id, "/path/to/file.txt")
```

### list_files

```python
def list_files(context_id: str,
               parent_folder_path: str,
               page_number: int = 1,
               page_size: int = 50,
               max_results: Optional[int] = None,
               next_token: Optional[str] = None) -> ContextFileListResult
```

List files under a specific folder path in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `parent_folder_path` _str_ - The parent folder path to list files from.
- `page_number` _int_ - Deprecated. Use max_results/next_token instead.
- `page_size` _int_ - Deprecated. Use max_results/next_token instead.
- `max_results` _int, optional_ - Maximum number of entries to return per request.
- `next_token` _str, optional_ - Pagination token from a previous response.
  

**Returns**:

    ContextFileListResult: A result object containing the list of files,
  request ID, and next_token for pagination.
  

**Example**:

```python
ctx_result = agent_bay.context.get(name="my-context", create=True)
files_result = agent_bay.context.list_files(
  ctx_result.context_id, "/", max_results=50
)
print(f"Found {len(files_result.entries)} files")
if files_result.next_token:
  next_page = agent_bay.context.list_files(
      ctx_result.context_id, "/",
      max_results=50, next_token=files_result.next_token
  )
```

### clear_async

```python
def clear_async(context_id: str) -> ClearContextResult
```

Synchronously initiate a task to clear the context's persistent data.

This is a non-blocking method that returns immediately after initiating the clearing task
on the backend. The context's state will transition to "clearing" while the operation
is in progress.

**Arguments**:

    context_id: Unique ID of the context to clear.
  

**Returns**:

  A ClearContextResult object indicating the task has been successfully started,
  with status field set to "clearing".
  

**Raises**:

    AgentBayError: If the backend API rejects the clearing request (e.g., invalid ID).
  

**Example**:

```python
result = agent_bay.context.get(name="my-context", create=True)
clear_result = agent_bay.context.clear_async(result.context_id)
```

### start_clear

```python
def start_clear(context_id: str) -> ClearContextResult
```

Deprecated alias for `clear_async`.

This method is kept for backward compatibility and simply forwards to
`clear_async`. Prefer using `clear_async` going forward.

**Arguments**:

    context_id: Unique ID of the context to clear.
  

**Returns**:

  ClearContextResult from `clear_async`.

### get_clear_status

```python
def get_clear_status(context_id: str) -> ClearContextResult
```

Query the status of the clearing task.

This method calls GetContext API directly and parses the raw response to extract
the state field, which indicates the current clearing status.

**Arguments**:

    context_id: ID of the context.
  

**Returns**:

  ClearContextResult object containing the current task status.
  

**Example**:

```python
result = agent_bay.context.get(name="my-context", create=True)
agent_bay.context.clear_async(result.context_id)
status_result = agent_bay.context.get_clear_status(result.context_id)
print(status_result.status)
```

### clear

```python
def clear(context_id: str,
          timeout: int = 60,
          poll_interval: float = 2.0) -> ClearContextResult
```

Synchronously clear the context's persistent data and wait for the final result.

This method wraps the `clear_async` and `get_clear_status` polling logic,
providing the simplest and most direct way to handle clearing tasks.

The clearing process transitions through the following states:
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)

**Arguments**:

    context_id: Unique ID of the context to clear.
    timeout: Timeout in seconds to wait for task completion. Defaults to 60.
    poll_interval: Interval in seconds between status polls. Defaults to 2.0.
  

**Returns**:

  ClearContextResult object containing the final task result.
  The status field will be "available" on success.
  

**Raises**:

    ClearanceTimeoutError: If the task fails to complete within the timeout.
    AgentBayError: If an API or network error occurs during execution.
  

**Example**:

```python
result = agent_bay.context.get(name="my-context", create=True)
clear_result = agent_bay.context.clear(result.context_id, timeout=60)
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./session.md)
- [Context Manager API Reference](./context-manager.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
