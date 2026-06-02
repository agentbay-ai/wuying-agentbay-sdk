"""
API response models for AgentBay SDK.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from agentbay._common.models.mcp_tool import McpTool
    from agentbay._sync.session import Session


class ApiResponse:
    """Base class for all API responses, containing RequestID"""

    def __init__(self, request_id: str = ""):
        """
        Initialize an ApiResponse with a request_id.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
        """
        self.request_id = request_id

    def get_request_id(self) -> str:
        """Returns the unique identifier for the API request."""
        return self.request_id


@dataclass
class BaseResult(ApiResponse):
    """
    Base result model for new typed APIs.

    This is a lightweight dataclass wrapper around ApiResponse for APIs that
    prefer returning structured results instead of generic OperationResult.
    """

    request_id: str = ""
    success: bool = False
    error_message: str = ""


class SessionPauseResult(ApiResponse):
    """Result of session pause operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        code: str = "",
        message: str = "",
        http_status_code: int = 0,
        status: Optional[str] = None,
    ):
        """
        Initialize a SessionPauseResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the pause operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
            code (str, optional): API error code. Defaults to "".
            message (str, optional): Detailed error message from API. Defaults to "".
            http_status_code (int, optional): HTTP status code. Defaults to 0.
            status (Optional[str], optional): Current status of the session.
                Possible values: "RUNNING", "PAUSED", "PAUSING".
                Defaults to None.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.code = code
        self.message = message
        self.http_status_code = http_status_code
        self.status = status


class SessionResumeResult(ApiResponse):
    """Result of session resume operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        code: str = "",
        message: str = "",
        http_status_code: int = 0,
        status: Optional[str] = None,
    ):
        """
        Initialize a SessionResumeResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the resume operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
            code (str, optional): API error code. Defaults to "".
            message (str, optional): Detailed error message from API. Defaults to "".
            http_status_code (int, optional): HTTP status code. Defaults to 0.
            status (Optional[str], optional): Current status of the session.
                Possible values: "RUNNING", "PAUSED", "RESUMING".
                Defaults to None.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.code = code
        self.message = message
        self.http_status_code = http_status_code
        self.status = status


class SessionResult(ApiResponse):
    """Result of operations returning a single Session."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        session: Optional["Session"] = None,
        code: str = "",
    ):
        """
        Initialize a SessionResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            session (Optional[Session], optional): The session object. Defaults to None.
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
            code (str, optional): API error code. Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.session = session
        self.code = code


class SessionListResult(ApiResponse):
    """Result of operations returning a list of Session IDs."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        session_ids: List[str] = None,
        next_token: str = "",
        max_results: int = 0,
        total_count: int = 0,
    ):
        """
        Initialize a SessionListResult.

        Args:
            request_id (str): The request ID.
            success (bool): Whether the operation was successful.
            error_message (str): Error message if the operation failed.
            session_ids (List[str]): List of session IDs.
            next_token (str): Token for the next page of results.
            max_results (int): Number of results per page.
            total_count (int): Total number of results available.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.session_ids = session_ids if session_ids is not None else []
        self.next_token = next_token
        self.max_results = max_results
        self.total_count = total_count


class DeleteResult(ApiResponse):
    """Result of delete operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        code: str = "",
        message: str = "",
        http_status_code: int = 0,
    ):
        """
        Initialize a DeleteResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the delete operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
            code (str, optional): API error code. Defaults to "".
            message (str, optional): Detailed error message from API. Defaults to "".
            http_status_code (int, optional): HTTP status code. Defaults to 0.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.code = code
        self.message = message
        self.http_status_code = http_status_code


class GetSessionData:
    """Data returned by GetSession API."""

    def __init__(
        self,
        app_instance_id: str = "",
        resource_id: str = "",
        session_id: str = "",
        success: bool = False,
        http_port: str = "",
        network_interface_ip: str = "",
        token: str = "",
        link_url: str = "",
        ws_url: str = "",
        vpc_resource: bool = False,
        vpc_ip: str = "",
        vpc_id: str = "",
        resource_url: str = "",
        status: str = "",
        tool_list: str = "",
        contexts: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Initialize GetSessionData.

        Args:
            app_instance_id (str): Application instance ID.
            resource_id (str): Resource ID.
            session_id (str): Session ID.
            success (bool): Success status.
            http_port (str): HTTP port for VPC sessions.
            network_interface_ip (str): Network interface IP for VPC sessions.
            token (str): Token for VPC sessions.
            vpc_resource (bool): Whether this session uses VPC resources.
            resource_url (str): Resource URL for accessing the session.
            status (str): Session status.
            contexts (Optional[List[Dict[str, str]]]): List of contexts associated with the session.
                Each context is a dict with 'name' and 'id' keys.
        """
        self.app_instance_id = app_instance_id
        self.resource_id = resource_id
        self.session_id = session_id
        self.success = success
        self.http_port = http_port
        self.network_interface_ip = network_interface_ip
        self.token = token
        self.link_url = link_url
        self.ws_url = ws_url
        self.vpc_resource = vpc_resource
        self.vpc_ip = vpc_ip
        self.vpc_id = vpc_id
        self.resource_url = resource_url
        self.status = status
        self.tool_list = tool_list
        self.contexts = contexts or []


class GetSessionResult(ApiResponse):
    """Result of GetSession operations."""

    def __init__(
        self,
        request_id: str = "",
        http_status_code: int = 0,
        code: str = "",
        success: bool = False,
        data: Optional[GetSessionData] = None,
        error_message: str = "",
    ):
        """
        Initialize a GetSessionResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            http_status_code (int, optional): HTTP status code. Defaults to 0.
            code (str, optional): Response code. Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            data (Optional[GetSessionData], optional): Session data. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.http_status_code = http_status_code
        self.code = code
        self.success = success
        self.data = data
        self.error_message = error_message


class OperationResult(ApiResponse):
    """Result of general operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Any = None,
        error_message: str = "",
        code: str = "",
        message: str = "",
        http_status_code: int = 0,
    ):
        """
        Initialize an OperationResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            data (Any, optional): Data returned by the operation. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
            code (str, optional): API error code. Defaults to "".
            message (str, optional): Detailed error message from API. Defaults to "".
            http_status_code (int, optional): HTTP status code. Defaults to 0.
        """
        super().__init__(request_id)
        self.success = success
        self.data = data
        self.error_message = error_message
        self.code = code
        self.message = message
        self.http_status_code = http_status_code


class BoolResult(ApiResponse):
    """Result of operations returning a boolean value."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Optional[bool] = None,
        error_message: str = "",
    ):
        """
        Initialize a BoolResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            data (Optional[bool], optional): The boolean result data. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.data = data
        self.error_message = error_message


class AdbUrlResult(ApiResponse):
    """Result of ADB URL retrieval operation."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        data: Optional[str] = None,
    ):
        """
        Initialize an AdbUrlResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
            data (Optional[str], optional): The ADB URL string (e.g., "adb connect IP:Port").
                Defaults to None.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.data = data


def extract_request_id(response) -> str:
    """
    Extracts RequestID from API response.
    This is a helper function used to extract RequestID in all API methods.

    Args:
        response: The response object from the API call.

    Returns:
        str: The request ID extracted from the response, or an empty string if not
            found.
    """
    if response is None:
        return ""

    try:
        # Convert response to a dictionary
        response_dict = response.to_map()

        # Extract RequestId from the body field
        if isinstance(response_dict, dict) and "body" in response_dict:
            body = response_dict.get("body", {})
            if isinstance(body, dict) and "RequestId" in body:
                return body["RequestId"]
    except (AttributeError, KeyError, TypeError):
        pass

    return ""


class McpToolsResult(ApiResponse):
    """Result containing MCP tools list and request ID."""

    def __init__(self, request_id: str = "", tools: Optional[List["McpTool"]] = None):
        """
        Initialize a McpToolsResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            tools (Optional[List[McpTool]], optional): List of MCP tools.
                Defaults to None.
        """
        super().__init__(request_id)
        self.tools = tools or []


class McpToolResult(ApiResponse):
    """Result of an MCP tool call."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: str = "",
        error_message: str = "",
    ):
        """
        Initialize a McpToolResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the tool call was successful.
                Defaults to False.
            data (str, optional): Tool output data (often a string or JSON).
                Defaults to "".
            error_message (str, optional): Error message if the call failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.data = data
        self.error_message = error_message


class SessionMetrics:
    """Structured metrics for session monitoring."""

    def __init__(
        self,
        cpu_count: int = 0,
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
        # Backward-compatible aliases (deprecated):
        rx_rate_kbps: Optional[float] = None,
        tx_rate_kbps: Optional[float] = None,
        rx_used_kb: Optional[float] = None,
        tx_used_kb: Optional[float] = None,
    ):
        self.cpu_count = cpu_count
        self.cpu_used_pct = cpu_used_pct
        self.disk_total = disk_total
        self.disk_used = disk_used
        self.mem_total = mem_total
        self.mem_used = mem_used
        self.rx_rate_kbyte_per_s = (
            rx_rate_kbyte_per_s if rx_rate_kbyte_per_s is not None else 0.0
        )
        self.tx_rate_kbyte_per_s = (
            tx_rate_kbyte_per_s if tx_rate_kbyte_per_s is not None else 0.0
        )
        self.rx_used_kbyte = rx_used_kbyte if rx_used_kbyte is not None else 0.0
        self.tx_used_kbyte = tx_used_kbyte if tx_used_kbyte is not None else 0.0

        # Backward-compatible aliases (deprecated): allow old args to fill new fields
        if rx_rate_kbps is not None and self.rx_rate_kbyte_per_s == 0.0:
            self.rx_rate_kbyte_per_s = float(rx_rate_kbps)
        if tx_rate_kbps is not None and self.tx_rate_kbyte_per_s == 0.0:
            self.tx_rate_kbyte_per_s = float(tx_rate_kbps)
        if rx_used_kb is not None and self.rx_used_kbyte == 0.0:
            self.rx_used_kbyte = float(rx_used_kb)
        if tx_used_kb is not None and self.tx_used_kbyte == 0.0:
            self.tx_used_kbyte = float(tx_used_kb)
        self.timestamp = timestamp

    # Backward-compatible properties (deprecated)
    @property
    def rx_rate_kbps(self) -> float:
        return float(self.rx_rate_kbyte_per_s)

    @property
    def tx_rate_kbps(self) -> float:
        return float(self.tx_rate_kbyte_per_s)

    @property
    def rx_used_kb(self) -> float:
        return float(self.rx_used_kbyte)

    @property
    def tx_used_kb(self) -> float:
        return float(self.tx_used_kbyte)


class SessionMetricsResult(ApiResponse):
    """Result of session get_metrics() operation."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        metrics: Optional[SessionMetrics] = None,
        error_message: str = "",
        raw: Optional[dict] = None,
    ):
        super().__init__(request_id)
        self.success = success
        self.metrics = metrics
        self.error_message = error_message
        self.raw = raw or {}


class EnvResult(ApiResponse):
    """Result of environment variable operations (get)."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        envs: Optional[Dict[str, str]] = None,
        error_message: str = "",
    ):
        """
        Initialize an EnvResult.

        Args:
            request_id: Unique identifier for the API request.
            success: Whether the operation was successful.
            envs: Dictionary of environment variable key-value pairs.
            error_message: Error message if the operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.envs = envs if envs is not None else {}
        self.error_message = error_message


Response = ApiResponse
