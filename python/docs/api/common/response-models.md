# Response Models API Reference

API response models for AgentBay SDK.

## ApiResponse

```python
class ApiResponse()
```

Base class for all API responses, containing RequestID

### __init__

```python
def __init__(self, request_id: str = "")
```

Initialize an ApiResponse with a request_id.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".

### get_request_id

```python
def get_request_id() -> str
```

Returns the unique identifier for the API request.

## BaseResult

```python
@dataclass
class BaseResult(ApiResponse)
```

Base result model for new typed APIs.

This is a lightweight dataclass wrapper around ApiResponse for APIs that
prefer returning structured results instead of generic OperationResult.

## SessionPauseResult

```python
class SessionPauseResult(ApiResponse)
```

Result of session pause operations.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             error_message: str = "",
             code: str = "",
             message: str = "",
             http_status_code: int = 0,
             status: Optional[str] = None)
```

Initialize a SessionPauseResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `success` _bool, optional_ - Whether the pause operation was successful.
  Defaults to False.
- `error_message` _str, optional_ - Error message if the operation failed.
  Defaults to "".
- `code` _str, optional_ - API error code. Defaults to "".
- `message` _str, optional_ - Detailed error message from API. Defaults to "".
- `http_status_code` _int, optional_ - HTTP status code. Defaults to 0.
- `status` _Optional[str], optional_ - Current status of the session.
  Possible values: "RUNNING", "PAUSED", "PAUSING".
  Defaults to None.

## SessionResumeResult

```python
class SessionResumeResult(ApiResponse)
```

Result of session resume operations.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             error_message: str = "",
             code: str = "",
             message: str = "",
             http_status_code: int = 0,
             status: Optional[str] = None)
```

Initialize a SessionResumeResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `success` _bool, optional_ - Whether the resume operation was successful.
  Defaults to False.
- `error_message` _str, optional_ - Error message if the operation failed.
  Defaults to "".
- `code` _str, optional_ - API error code. Defaults to "".
- `message` _str, optional_ - Detailed error message from API. Defaults to "".
- `http_status_code` _int, optional_ - HTTP status code. Defaults to 0.
- `status` _Optional[str], optional_ - Current status of the session.
  Possible values: "RUNNING", "PAUSED", "RESUMING".
  Defaults to None.

## SessionResult

```python
class SessionResult(ApiResponse)
```

Result of operations returning a single Session.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             error_message: str = "",
             session: Optional["Session"] = None)
```

Initialize a SessionResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `session` _Optional[Session], optional_ - The session object. Defaults to None.
- `success` _bool, optional_ - Whether the operation was successful.
  Defaults to False.
- `error_message` _str, optional_ - Error message if the operation failed.
  Defaults to "".

## SessionListResult

```python
class SessionListResult(ApiResponse)
```

Result of operations returning a list of Session IDs.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             error_message: str = "",
             session_ids: List[str] = None,
             next_token: str = "",
             max_results: int = 0,
             total_count: int = 0)
```

Initialize a SessionListResult.

**Arguments**:

- `request_id` _str_ - The request ID.
- `success` _bool_ - Whether the operation was successful.
- `error_message` _str_ - Error message if the operation failed.
- `session_ids` _List[str]_ - List of session IDs.
- `next_token` _str_ - Token for the next page of results.
- `max_results` _int_ - Number of results per page.
- `total_count` _int_ - Total number of results available.

## DeleteResult

```python
class DeleteResult(ApiResponse)
```

Result of delete operations.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             error_message: str = "",
             code: str = "",
             message: str = "",
             http_status_code: int = 0)
```

Initialize a DeleteResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `success` _bool, optional_ - Whether the delete operation was successful.
  Defaults to False.
- `error_message` _str, optional_ - Error message if the operation failed.
  Defaults to "".
- `code` _str, optional_ - API error code. Defaults to "".
- `message` _str, optional_ - Detailed error message from API. Defaults to "".
- `http_status_code` _int, optional_ - HTTP status code. Defaults to 0.

## GetSessionData

```python
class GetSessionData()
```

Data returned by GetSession API.

### __init__

```python
def __init__(self, app_instance_id: str = "",
             resource_id: str = "",
             session_id: str = "",
             success: bool = False,
             http_port: str = "",
             network_interface_ip: str = "",
             token: str = "",
             link_url: str = "",
             ws_url: str = "",
             vpc_resource: bool = False,
             resource_url: str = "",
             status: str = "",
             tool_list: str = "",
             contexts: Optional[List[Dict[str, str]]] = None)
```

Initialize GetSessionData.

**Arguments**:

- `app_instance_id` _str_ - Application instance ID.
- `resource_id` _str_ - Resource ID.
- `session_id` _str_ - Session ID.
- `success` _bool_ - Success status.
- `http_port` _str_ - HTTP port for VPC sessions.
- `network_interface_ip` _str_ - Network interface IP for VPC sessions.
- `token` _str_ - Token for VPC sessions.
- `vpc_resource` _bool_ - Whether this session uses VPC resources.
- `resource_url` _str_ - Resource URL for accessing the session.
- `status` _str_ - Session status.
- `contexts` _Optional[List[Dict[str, str]]]_ - List of contexts associated with the session.
  Each context is a dict with 'name' and 'id' keys.

## GetSessionResult

```python
class GetSessionResult(ApiResponse)
```

Result of GetSession operations.

### __init__

```python
def __init__(self, request_id: str = "",
             http_status_code: int = 0,
             code: str = "",
             success: bool = False,
             data: Optional[GetSessionData] = None,
             error_message: str = "")
```

Initialize a GetSessionResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `http_status_code` _int, optional_ - HTTP status code. Defaults to 0.
- `code` _str, optional_ - Response code. Defaults to "".
- `success` _bool, optional_ - Whether the operation was successful.
  Defaults to False.
- `data` _Optional[GetSessionData], optional_ - Session data. Defaults to None.
- `error_message` _str, optional_ - Error message if the operation failed.
  Defaults to "".

## OperationResult

```python
class OperationResult(ApiResponse)
```

Result of general operations.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             data: Any = None,
             error_message: str = "",
             code: str = "",
             message: str = "",
             http_status_code: int = 0)
```

Initialize an OperationResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `success` _bool, optional_ - Whether the operation was successful.
  Defaults to False.
- `data` _Any, optional_ - Data returned by the operation. Defaults to None.
- `error_message` _str, optional_ - Error message if the operation failed.
  Defaults to "".
- `code` _str, optional_ - API error code. Defaults to "".
- `message` _str, optional_ - Detailed error message from API. Defaults to "".
- `http_status_code` _int, optional_ - HTTP status code. Defaults to 0.

## BoolResult

```python
class BoolResult(ApiResponse)
```

Result of operations returning a boolean value.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             data: Optional[bool] = None,
             error_message: str = "")
```

Initialize a BoolResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `success` _bool, optional_ - Whether the operation was successful.
  Defaults to False.
- `data` _Optional[bool], optional_ - The boolean result data. Defaults to None.
- `error_message` _str, optional_ - Error message if the operation failed.
  Defaults to "".

## AdbUrlResult

```python
class AdbUrlResult(ApiResponse)
```

Result of ADB URL retrieval operation.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             error_message: str = "",
             data: Optional[str] = None)
```

Initialize an AdbUrlResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `success` _bool, optional_ - Whether the operation was successful.
  Defaults to False.
- `error_message` _str, optional_ - Error message if the operation failed.
  Defaults to "".
- `data` _Optional[str], optional_ - The ADB URL string (e.g., "adb connect IP:Port").
  Defaults to None.

### extract_request_id

```python
def extract_request_id(response) -> str
```

Extracts RequestID from API response.
This is a helper function used to extract RequestID in all API methods.

**Arguments**:

    response: The response object from the API call.
  

**Returns**:

    str: The request ID extracted from the response, or an empty string if not
  found.

## McpToolsResult

```python
class McpToolsResult(ApiResponse)
```

Result containing MCP tools list and request ID.

### __init__

```python
def __init__(self, request_id: str = "", tools: Optional[List["McpTool"]] = None)
```

Initialize a McpToolsResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `tools` _Optional[List[McpTool]], optional_ - List of MCP tools.
  Defaults to None.

## McpToolResult

```python
class McpToolResult(ApiResponse)
```

Result of an MCP tool call.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             data: str = "",
             error_message: str = "")
```

Initialize a McpToolResult.

**Arguments**:

- `request_id` _str, optional_ - Unique identifier for the API request.
  Defaults to "".
- `success` _bool, optional_ - Whether the tool call was successful.
  Defaults to False.
- `data` _str, optional_ - Tool output data (often a string or JSON).
  Defaults to "".
- `error_message` _str, optional_ - Error message if the call failed.
  Defaults to "".

## SessionMetrics

```python
class SessionMetrics()
```

Structured metrics for session monitoring.

### __init__

```python
def __init__(self, cpu_count: int = 0,
             cpu_used_pct: float = 0.0,
             disk_total: int = 0,
             disk_used: int = 0,
             mem_total: int = 0,
             mem_used: int = 0,
             rx_rate_kbyte_per_s: float = 0.0,
             tx_rate_kbyte_per_s: float = 0.0,
             rx_used_kbyte: float = 0.0,
             tx_used_kbyte: float = 0.0,
             timestamp: str = "",
             rx_rate_kbps: Optional[float] = None,
             tx_rate_kbps: Optional[float] = None,
             rx_used_kb: Optional[float] = None,
             tx_used_kb: Optional[float] = None)
```

### rx_rate_kbps

```python
@property
def rx_rate_kbps() -> float
```

### tx_rate_kbps

```python
@property
def tx_rate_kbps() -> float
```

### rx_used_kb

```python
@property
def rx_used_kb() -> float
```

### tx_used_kb

```python
@property
def tx_used_kb() -> float
```

## SessionMetricsResult

```python
class SessionMetricsResult(ApiResponse)
```

Result of session get_metrics() operation.

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             metrics: Optional[SessionMetrics] = None,
             error_message: str = "",
             raw: Optional[dict] = None)
```

## EnvResult

```python
class EnvResult(ApiResponse)
```

Result of environment variable operations (get).

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             envs: Optional[Dict[str, str]] = None,
             error_message: str = "")
```

Initialize an EnvResult.

**Arguments**:

    request_id: Unique identifier for the API request.
    success: Whether the operation was successful.
    envs: Dictionary of environment variable key-value pairs.
    error_message: Error message if the operation failed.

#### Response

```python
Response = ApiResponse
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
