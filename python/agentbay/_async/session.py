import asyncio
import json
import random
import time
from typing import TYPE_CHECKING, Any, Dict, Optional

import httpx

from .._common.exceptions import SessionError
from .._common.logger import (
    _log_api_call,
    _log_api_response_with_details,
    _log_info_with_color,
    _log_operation_error,
    _log_operation_start,
    _log_operation_success,
    _truncate_string_for_log,
    _log_warning,
    get_logger,
)
from .._common.models import (
    ApiResponse,
    DeleteResult,
    McpToolResult,
    OperationResult,
    SessionMetrics,
    SessionMetricsResult,
    SessionPauseResult,
    SessionResumeResult,
    extract_request_id,
)
from .._common.models.mcp_tool import McpTool
from ..api.models import (
    CallMcpToolRequest,
    DeleteSessionAsyncRequest,
    GetLabelRequest,
    GetLinkRequest,
    GetLinkResponse,
    GetSessionDetailRequest,
    GetMcpResourceRequest,
    ListMcpToolsRequest,
    PauseSessionAsyncRequest,
    RefreshSessionIdleTimeRequest,
    ReleaseMcpSessionRequest,
    ResumeSessionAsyncRequest,
    SetLabelRequest,
)
from .agent import AsyncAgent
from .browser import AsyncBrowser
from .code import AsyncCode
from .command import AsyncCommand
from .computer import AsyncComputer
from .context_manager import AsyncContextManager
from .env import AsyncEnv
from .filesystem import AsyncFileSystem
from .mobile import AsyncMobile
from .oss import AsyncOss

if TYPE_CHECKING:
    from .agentbay import AsyncAgentBay

# Initialize logger for this module
_logger = get_logger("session")


class SessionStatusResult(ApiResponse):
    """Result of Session.get_status() (status only)."""

    def __init__(
        self,
        request_id: str = "",
        http_status_code: int = 0,
        code: str = "",
        success: bool = False,
        status: str = "",
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.http_status_code = http_status_code
        self.code = code
        self.success = success
        self.status = status
        self.error_message = error_message


class SessionInfo:
    """
    SessionInfo contains information about a session.
    """

    def __init__(
        self,
        session_id: str = "",
        resource_url: str = "",
        app_id: str = "",
        auth_code: str = "",
        connection_properties: str = "",
        resource_id: str = "",
        resource_type: str = "",
        ticket: str = "",
    ):
        self.session_id = session_id
        self.resource_url = resource_url
        self.app_id = app_id
        self.auth_code = auth_code
        self.connection_properties = connection_properties
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.ticket = ticket


class AsyncSession:
    """
    AsyncSession represents a session in the AgentBay cloud environment.
    """

    def __init__(self, agent_bay: "AsyncAgentBay", session_id: str):
        self.agent_bay = agent_bay
        self.session_id = session_id

        # Application instance ID
        self.app_instance_id = ""

        # Resource URL for accessing the session
        self.resource_url = ""

        # VPC IP/ID, populated when upstream returns them (VPC sessions)
        self.vpc_ip = ""
        self.vpc_id = ""

        # LinkUrl-based direct tool call (non-VPC)
        self.token = ""
        self.link_url = ""

        # WebSocket URL for long connection (if provided by backend)
        self.ws_url = ""

        # Internal session-scoped WS client (lazy initialized)
        self._ws_client = None

        # Shared HTTP client for LinkUrl calls (lazy initialized)
        self._link_http_client: Optional[httpx.AsyncClient] = None

        # Recording functionality
        self.enableBrowserReplay = (
            # Whether browser recording is enabled for this session (None = server default)
            None
        )

        # MCP tool list returned by backend for this session
        self.mcpTools: list[McpTool] = []

        # Initialize file system, command and code handlers
        self.file_system = AsyncFileSystem(self)
        self.command = AsyncCommand(self)
        self.code = AsyncCode(self)
        self.oss = AsyncOss(self)

        # Initialize Computer and Mobile modules
        self.computer = AsyncComputer(self)
        self.mobile = AsyncMobile(self)

        self.context = AsyncContextManager(self)
        self.browser = AsyncBrowser(self)

        self.agent = AsyncAgent(self)

        self.env = AsyncEnv(self)

        # Initialize Git module
        from .git.git import AsyncGit
        self.git = AsyncGit(self)

        # Initialize PTY module
        from .pty import AsyncPty
        self.pty = AsyncPty(self)

    def _get_link_http_client(self) -> httpx.AsyncClient:
        """Internal: get or create a shared HTTP client for LinkUrl calls."""
        if self._link_http_client is None:
            self._link_http_client = httpx.AsyncClient(timeout=900)
        return self._link_http_client

    async def _close_link_http_client(self) -> None:
        """Internal: close the shared HTTP client for LinkUrl calls."""
        client = self._link_http_client
        self._link_http_client = None
        if client is not None:
            await client.aclose()

    async def _get_ws_client(self):
        """
        Internal: get or create a session-scoped WS client.

        This method is internal API by convention.
        """
        if not self.ws_url:
            raise SessionError("ws_url is not available for this session")
        if not self.token:
            raise SessionError("token is not available for WS connection")

        if self._ws_client is None:
            from ._internal.ws_client import WsClient

            self._ws_client = WsClient(ws_url=self.ws_url, ws_token=self.token)
        return self._ws_client

    @property
    def fs(self) -> AsyncFileSystem:
        """
        Alias of file_system.
        """
        return self.file_system

    @property
    def filesystem(self) -> AsyncFileSystem:
        """
        Alias of file_system.
        """
        return self.file_system

    @property
    def files(self) -> AsyncFileSystem:
        """
        Alias of file_system.
        """
        return self.file_system

    def _get_api_key(self) -> str:
        """Internal method to get the API key for this session."""
        return self.agent_bay.api_key

    def _get_client(self):
        """Internal method to get the HTTP client for this session."""
        return self.agent_bay.client

    def _get_session_id(self) -> str:
        """Internal method to get the session ID."""
        return self.session_id

    def _get_token(self) -> str:
        return self.token

    def _get_link_url(self) -> str:
        return self.link_url

    def get_token(self) -> str:
        """
        .. deprecated::
            Internal SDK use only. Will be removed in a future version.
        """
        import warnings
        warnings.warn(
            "get_token() is deprecated and will be removed in a future version. "
            "This method is for internal SDK use only.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._get_token()

    def get_link_url(self) -> str:
        """
        .. deprecated::
            Internal SDK use only. Will be removed in a future version.
        """
        import warnings
        warnings.warn(
            "get_link_url() is deprecated and will be removed in a future version. "
            "This method is for internal SDK use only.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._get_link_url()

    def getToken(self) -> str:
        """
        .. deprecated::
            Internal SDK use only. Will be removed in a future version.
        """
        import warnings
        warnings.warn(
            "getToken() is deprecated and will be removed in a future version. "
            "This method is for internal SDK use only.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._get_token()

    def getLinkUrl(self) -> str:
        """
        .. deprecated::
            Internal SDK use only. Will be removed in a future version.
        """
        import warnings
        warnings.warn(
            "getLinkUrl() is deprecated and will be removed in a future version. "
            "This method is for internal SDK use only.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._get_link_url()

    async def get_status(self) -> "SessionStatusResult":
        """
        Get basic session status asynchronously.

        Returns:
            SessionStatusResult: Result containing session status only.
        """
        try:
            _log_api_call("GetSessionDetail", f"SessionId={self.session_id}")
            request = GetSessionDetailRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self.session_id,
            )

            response = await self._get_client().get_session_detail_async(request)
            request_id = extract_request_id(response)

            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
            except Exception:
                response_body = str(response)

            try:
                response_map = response.to_map()
                body = response_map.get("body", {})
                http_status_code = body.get("HttpStatusCode", 0)
                code = body.get("Code", "")
                success = body.get("Success", False)
                message = body.get("Message", "")

                if not request_id:
                    request_id = body.get("RequestId", "") or ""

                if not success and code:
                    return SessionStatusResult(
                        request_id=request_id,
                        http_status_code=http_status_code,
                        code=code,
                        success=False,
                        status="",
                        error_message=f"[{code}] {message or 'Unknown error'}",
                    )

                status = ""
                if body.get("Data"):
                    data_dict = body.get("Data", {})
                    _logger.info(
                        f"  ✓ GetSessionDetail API call async successful{data_dict}"
                    )
                    status = data_dict.get("Status", "") or ""

                key_fields = {}
                if status:
                    key_fields["status"] = status
                _log_api_response_with_details(
                    api_name="GetSessionDetail",
                    request_id=request_id,
                    success=success,
                    key_fields=key_fields,
                    full_response=response_body,
                )

                return SessionStatusResult(
                    request_id=request_id,
                    http_status_code=http_status_code,
                    code=code,
                    success=success,
                    status=status,
                    error_message="",
                )

            except Exception as e:
                _logger.exception(f"Failed to parse response: {str(e)}")
                return SessionStatusResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Failed to parse response: {str(e)}",
                )

        except Exception as e:
            error_str = str(e)
            if "InvalidMcpSession.NotFound" in error_str or "NotFound" in error_str:
                _log_info_with_color(f"Session not found: {self.session_id}")
                _logger.debug(f"GetSessionDetail error details: {error_str}")
                return SessionStatusResult(
                    request_id="",
                    success=False,
                    error_message=f"Session {self.session_id} not found",
                )

            _log_operation_error("get_status", error_str, exc_info=True)
            return SessionStatusResult(
                request_id="",
                success=False,
                error_message=f"Failed to get session status {self.session_id}: {e}",
            )

    async def keep_alive(self) -> OperationResult:
        """
        Refresh the backend session idle timer.

        This method calls the RefreshSessionIdleTime API.
        """
        try:
            _log_api_call("RefreshSessionIdleTime",
                          f"SessionId={self.session_id}")
            request = RefreshSessionIdleTimeRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self.session_id,
            )
            response = await self._get_client().refresh_session_idle_time_async(request)
            request_id = extract_request_id(response)

            response_map = response.to_map() if response is not None else {}
            body = response_map.get("body", {}) if isinstance(
                response_map, dict) else {}

            success = bool(body.get("Success", False))
            if not request_id:
                request_id = body.get("RequestId", "") or ""

            if not success:
                code = body.get("Code", "") or ""
                message = body.get("Message", "") or ""
                error_message = f"[{code}] {message or 'Unknown error'}" if code else (
                    message or "Unknown error")
                _log_api_response_with_details(
                    api_name="RefreshSessionIdleTime",
                    request_id=request_id,
                    success=False,
                    full_response=json.dumps(
                        body, ensure_ascii=False, indent=2)
                    if isinstance(body, dict)
                    else str(body),
                )
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_message,
                )

            _log_api_response_with_details(
                api_name="RefreshSessionIdleTime",
                request_id=request_id,
                success=True,
                key_fields={"session_id": self.session_id},
            )
            return OperationResult(request_id=request_id, success=True)
        except Exception as e:
            _log_operation_error("RefreshSessionIdleTime",
                                 str(e), exc_info=True)
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to keep session alive {self.session_id}: {e}",
            )

    async def delete(self, sync_context: bool = False) -> DeleteResult:
        """
        Delete this session and release all associated resources.

        Args:
            sync_context (bool, optional): Whether to sync context data (trigger file uploads)
                before deleting the session. Defaults to False.

        Returns:
            DeleteResult: Result indicating success or failure with request ID.
                - success (bool): True if deletion succeeded
                - error_message (str): Error details if deletion failed
                - request_id (str): Unique identifier for this API request

        Raises:
            SessionError: If the deletion request fails or the response is invalid.
        """
        try:
            # Perform context synchronization if needed
            if sync_context:
                _log_operation_start(
                    "Context synchronization", "Before session deletion"
                )

                sync_start_time = time.time()

                try:
                    # Sync all contexts
                    sync_result = await self.context.sync()
                    _logger.info("🔄 Synced all contexts")

                    sync_duration = time.time() - sync_start_time

                    if sync_result.success:
                        _log_operation_success("Context sync")
                        _logger.info(
                            f"⏱️  Context sync completed in {sync_duration:.2f} seconds"
                        )
                    else:
                        _log_warning("Context sync completed with failures")
                        _logger.warning(
                            f"⏱️  Context sync failed after {sync_duration:.2f} seconds"
                        )

                except Exception as e:
                    sync_duration = time.time() - sync_start_time
                    _log_warning(f"Failed to trigger context sync: {e}")
                    _logger.warning(
                        f"⏱️  Context sync failed after {sync_duration:.2f} seconds"
                    )
                    # Continue with deletion even if sync fails

            # Proceed with session deletion
            request = DeleteSessionAsyncRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self.session_id,
            )
            client = self._get_client()
            response = await client.delete_session_async_async(request)

            # Extract request ID
            request_id = extract_request_id(response)

            # Check if the response is success
            response_map = response.to_map()
            body = response_map.get("body", {})
            success = body.get("Success", True)

            if not success:
                error_message = f"[{body.get('Code', 'Unknown')}] {body.get('Message', 'Failed to delete session')}"
                _log_api_response_with_details(
                    api_name="DeleteSessionAsync",
                    request_id=request_id,
                    success=False,
                    full_response=json.dumps(
                        body, ensure_ascii=False, indent=2),
                )
                return DeleteResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_message,
                )

            # Poll for session deletion status
            _logger.info(
                f"🔄 Waiting for session {self.session_id} to be deleted...")
            poll_timeout = 300.0  # 5 minutes timeout
            poll_interval = 1.0  # Poll every 1 second
            poll_start_time = time.time()

            while True:
                # Check timeout
                elapsed_time = time.time() - poll_start_time
                if elapsed_time >= poll_timeout:
                    error_message = f"Timeout waiting for session deletion after {poll_timeout}s"
                    _logger.warning(f"⏱️  {error_message}")
                    return DeleteResult(
                        request_id=request_id,
                        success=False,
                        error_message=error_message,
                    )

                # Get session status
                session_result = await self.get_status()

                # Check if session is deleted (NotFound error)
                if not session_result.success:
                    error_code = getattr(session_result, "code", "") or ""
                    error_message = session_result.error_message or ""
                    http_status_code = getattr(
                        session_result, "http_status_code", 0) or 0

                    # Check for InvalidMcpSession.NotFound, 400 with "not found", or error_message containing "not found"
                    is_not_found = (
                        error_code == "InvalidMcpSession.NotFound" or
                        (http_status_code == 400 and (
                            "not found" in error_message.lower() or
                            "NotFound" in error_message or
                            "not found" in error_code.lower()
                        )) or
                        "not found" in error_message.lower()
                    )

                    if is_not_found:
                        # Session is deleted
                        _logger.info(
                            f"✅ Session {self.session_id} successfully deleted (NotFound)")
                        break
                    else:
                        # Other error, continue polling
                        _logger.debug(
                            f"⚠️  Get session error (will retry): {error_message}")
                        # Continue to next poll iteration

                # Check session status if we got valid data
                elif session_result.status:
                    status = session_result.status
                    _logger.debug(f"📊 Session status: {status}")
                    if status == "FINISH":
                        _logger.info(
                            f"✅ Session {self.session_id} successfully deleted")
                        break

                # Wait before next poll
                await asyncio.sleep(poll_interval)

            # Log successful deletion
            _log_api_response_with_details(
                api_name="DeleteSessionAsync",
                request_id=request_id,
                success=True,
                key_fields={"session_id": self.session_id},
            )

            # Return success result with request ID
            return DeleteResult(request_id=request_id, success=True)

        except Exception as e:
            _log_operation_error("delete_session_async", str(e), exc_info=True)
            # In case of error, return failure result with error message
            return DeleteResult(
                success=False,
                error_message=f"Failed to delete session {self.session_id}: {e}",
            )
        finally:
            ws_client = self._ws_client
            self._ws_client = None
            if ws_client is not None:
                try:
                    await ws_client.close()
                except Exception:
                    pass
            try:
                await self._close_link_http_client()
            except Exception:
                pass

    def _validate_labels(self, labels: Dict[str, str]) -> Optional[OperationResult]:
        """
        Validates labels parameter for label operations.
        """
        # Check if labels is None
        if labels is None:
            return OperationResult(
                request_id="",
                success=False,
                error_message="Labels cannot be null, undefined, or invalid type. Please provide a valid labels object.",
            )

        # Check if labels is a list (array equivalent) - check this before dict check
        if isinstance(labels, list):
            return OperationResult(
                request_id="",
                success=False,
                error_message="Labels cannot be an array. Please provide a valid labels object.",
            )

        # Check if labels is not a dict (after checking for list)
        if not isinstance(labels, dict):
            return OperationResult(
                request_id="",
                success=False,
                error_message="Labels cannot be null, undefined, or invalid type. Please provide a valid labels object.",
            )

        # Check if labels object is empty
        if len(labels) == 0:
            return OperationResult(
                request_id="",
                success=False,
                error_message="Labels cannot be empty. Please provide at least one label.",
            )

        for key, value in labels.items():
            # Check key validity
            if not key or (isinstance(key, str) and key.strip() == ""):
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="Label keys cannot be empty Please provide valid keys.",
                )

            # Check value is not None or empty
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="Label values cannot be empty Please provide valid values.",
                )

        # Validation passed
        return None

    async def set_labels(self, labels: Dict[str, str]) -> OperationResult:
        """
        Sets the labels for this session asynchronously.
        """
        try:
            # Validate labels using the extracted validation function
            validation_result = self._validate_labels(labels)
            if validation_result is not None:
                return validation_result

            # Convert labels to JSON string
            labels_json = json.dumps(labels)

            request = SetLabelRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self.session_id,
                labels=labels_json,
            )

            client = self._get_client()
            response = await client.set_label_async(request)

            # Extract request ID
            request_id = extract_request_id(response)

            # Log successful label setting
            _log_api_response_with_details(
                api_name="SetLabel",
                request_id=request_id,
                success=True,
                key_fields={"session_id": self.session_id,
                            "labels_count": len(labels)},
            )

            return OperationResult(request_id=request_id, success=True)

        except Exception as e:
            _logger.exception(
                f"❌ Failed to set labels for session {self.session_id}")
            raise SessionError(
                f"Failed to set labels for session {self.session_id}: {e}"
            )

    async def get_labels(self) -> OperationResult:
        """
        Gets the labels for this session asynchronously.
        """
        try:
            request = GetLabelRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self.session_id,
            )

            # Try async method first, fall back to sync wrapped in asyncio.to_thread
            client = self._get_client()
            response = await client.get_label_async(request)

            # Extract request ID
            request_id = extract_request_id(response)

            # Extract labels from response
            labels_json = (
                response.to_map().get("body", {}).get("Data", {}).get("Labels")
            )

            labels = {}
            if labels_json:
                labels = json.loads(labels_json)

            # Log successful label retrieval
            _log_api_response_with_details(
                api_name="GetLabel",
                request_id=request_id,
                success=True,
                key_fields={"session_id": self.session_id,
                            "labels_count": len(labels)},
            )

            return OperationResult(request_id=request_id, success=True, data=labels)

        except Exception as e:
            _logger.exception(
                f"❌ Failed to get labels for session {self.session_id}")
            raise SessionError(
                f"Failed to get labels for session {self.session_id}: {e}"
            )

    async def info(self) -> OperationResult:
        """
        Get detailed information about this session asynchronously.
        """
        try:
            request = GetMcpResourceRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self.session_id,
            )

            _log_api_call("GetMcpResource", f"SessionId={self.session_id}")

            # Try async method first, fall back to sync wrapped in asyncio.to_thread
            client = self._get_client()
            response = await client.get_mcp_resource_async(request)

            # Extract request ID
            request_id = extract_request_id(response)

            # Extract session info from response
            response_map = response.to_map()
            data = response_map.get("body", {}).get("Data", {})

            session_info = SessionInfo()

            if "SessionId" in data:
                session_info.session_id = data["SessionId"]

            if "ResourceUrl" in data:
                session_info.resource_url = data["ResourceUrl"]
            # Transfer DesktopInfo fields to SessionInfo
            if "DesktopInfo" in data:
                desktop_info = data["DesktopInfo"]
                if "AppId" in desktop_info:
                    session_info.app_id = desktop_info["AppId"]
                if "AuthCode" in desktop_info:
                    session_info.auth_code = desktop_info["AuthCode"]
                if "ConnectionProperties" in desktop_info:
                    session_info.connection_properties = desktop_info[
                        "ConnectionProperties"
                    ]
                if "ResourceId" in desktop_info:
                    session_info.resource_id = desktop_info["ResourceId"]
                if "ResourceType" in desktop_info:
                    session_info.resource_type = desktop_info["ResourceType"]
                if "Ticket" in desktop_info:
                    session_info.ticket = desktop_info["Ticket"]

            # Log successful session info retrieval
            _log_api_response_with_details(
                api_name="GetMcpResource",
                request_id=request_id,
                success=True,
                key_fields={
                    "session_id": session_info.session_id,
                    "resource_url": session_info.resource_url,
                    "resource_type": session_info.resource_type,
                },
            )

            return OperationResult(
                request_id=request_id, success=True, data=session_info
            )

        except Exception as e:
            # Check if this is an expected business error (e.g., session not found)
            error_str = str(e)
            error_code = ""

            # Try to extract error code from the exception
            if hasattr(e, "data") and hasattr(e.data, "get"):
                error_code = e.data.get("Code", "")
            elif "InvalidMcpSession.NotFound" in error_str or "NotFound" in error_str:
                error_code = "InvalidMcpSession.NotFound"

            if error_code == "InvalidMcpSession.NotFound":
                # This is an expected error - session doesn't exist
                # Use info level logging without stack trace, but with red color for visibility
                _log_info_with_color(f"Session not found: {self.session_id}")
                _logger.debug(f"GetMcpResource error details: {error_str}")
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message=f"Session {self.session_id} not found",
                )
            else:
                # This is an unexpected error - log with full error
                _logger.exception(
                    f"❌ Failed to get session info for session {self.session_id}"
                )
                raise SessionError(
                    f"Failed to get session info for session {self.session_id}: {e}"
                )

    async def get_link(
        self,
        protocol_type: Optional[str] = None,
        port: Optional[int] = None,
        options: Optional[str] = None,
    ) -> OperationResult:
        """
        Asynchronously get a link associated with the current session.
        """
        try:
            # Log API call with parameters
            _log_api_call(
                "GetLink",
                f"SessionId={self.session_id}, ProtocolType={protocol_type or 'default'}, "
                f"Port={port or 'default'}, Options={'provided' if options else 'none'}",
            )

            request = GetLinkRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self._get_session_id(),
                protocol_type=protocol_type,
                port=port,
                options=options,
            )

            # Try async method first, fall back to sync wrapped in asyncio.to_thread
            client = self.agent_bay.client
            response = await client.get_link_async(request)

            # Extract request ID
            request_id = extract_request_id(response)

            response_map = response.to_map()

            if not isinstance(response_map, dict):
                raise SessionError(
                    "Invalid response format: expected a dictionary from "
                    "response.to_map()"
                )

            body = response_map.get("body", {})
            if not isinstance(body, dict):
                raise SessionError(
                    "Invalid response format: 'body' field is not a dictionary"
                )

            data = body.get("Data", {})
            _logger.debug(f"📊 Data: {data}")

            if not isinstance(data, dict):
                try:
                    data = json.loads(data) if isinstance(data, str) else {}
                except json.JSONDecodeError:
                    data = {}

            url = data.get("Url", "")

            # Log successful link retrieval
            _log_api_response_with_details(
                api_name="GetLink",
                request_id=request_id,
                success=True,
                key_fields={
                    "session_id": self.session_id,
                    "url": url,
                    "protocol_type": protocol_type or "default",
                    "port": port or "default",
                },
            )

            return OperationResult(request_id=request_id, success=True, data=url)

        except SessionError:
            raise
        except Exception as e:
            _logger.error(
                f"❌ Failed to get link for session {self.session_id}: {e}")
            raise SessionError(f"Failed to get link: {e}")

    async def list_mcp_tools(self, image_id: Optional[str] = None):
        """
        List MCP tools available for this session asynchronously.
        """
        from .._common.models.response import McpToolsResult
        from .._common.models.mcp_tool import McpTool

        # Use provided image_id, session's image_id, or default
        if image_id is None:
            image_id = getattr(self, "image_id", "") or "linux_latest"

        request = ListMcpToolsRequest(
            authorization=f"Bearer {self._get_api_key()}", image_id=image_id
        )

        _log_api_call("ListMcpTools", f"ImageId={image_id}")

        # Try async method first, fall back to sync wrapped in asyncio.to_thread
        client = self._get_client()
        response = await client.list_mcp_tools_async(request)

        # Extract request ID
        request_id = extract_request_id(response)

        if response and response.body:
            _logger.debug(f"📥 Response from ListMcpTools: {response.body}")

        # Parse the response data
        tools = []
        if response and response.body and response.body.data:
            # The Data field is a JSON string, so we need to unmarshal it
            try:
                tools_data = json.loads(response.body.data)
                for tool_data in tools_data:
                    tool = McpTool(
                        name=tool_data.get("name", "") or "",
                        server=tool_data.get("server", "") or "",
                    )
                    tools.append(tool)
            except json.JSONDecodeError as e:
                _logger.error(f"❌ Error unmarshaling tools data: {e}")

        # Log successful tools retrieval
        _log_api_response_with_details(
            api_name="ListMcpTools",
            request_id=request_id,
            success=True,
            key_fields={"image_id": image_id, "tools_count": len(tools)},
        )

        return McpToolsResult(request_id=request_id, tools=tools)

    def _get_mcp_server_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Resolve MCP server name by tool name from session tool list.

        Returns:
            Optional[str]: Server name if found, otherwise None.
        """
        for t in self.mcpTools or []:
            try:
                if t and getattr(t, "name", None) == tool_name:
                    server = getattr(t, "server", "") or ""
                    return server if server else None
            except Exception:
                continue
        return None

    async def call_mcp_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
        auto_gen_session: bool = False,
    ):
        """
        Call an MCP tool directly asynchronously.
        """
        try:
            # Normalize press_keys arguments for better case compatibility
            if tool_name == "press_keys" and "keys" in args:
                from .._common.utils.key_normalizer import normalize_keys

                args = args.copy()  # Don't modify the original args
                args["keys"] = normalize_keys(args["keys"])
                _logger.debug(f"Normalized press_keys arguments: {args}")

            # Server name is optional for API-based tool calls.
            # Some environments do not return ToolList in CreateSession, and the backend
            # can resolve the server by tool name.
            server_name = self._get_mcp_server_for_tool(tool_name) or ""

            args_json = json.dumps(args, ensure_ascii=False)

            # LinkUrl route requires explicit server name. If it's not available,
            # fall back to API-based call to let backend resolve the server.
            if self._get_link_url() and self._get_token() and server_name:
                return await self._call_mcp_tool_link_url(
                    tool_name=tool_name,
                    args=args,
                    server_name=server_name,
                )

            return await self._call_mcp_tool_api(
                tool_name,
                args_json,
                read_timeout,
                connect_timeout,
                auto_gen_session,
                server_name=server_name,
            )
        except Exception as e:
            _logger.error(f"❌ Failed to call MCP tool {tool_name}: {e}")
            return McpToolResult(
                request_id="",
                success=False,
                data="",
                error_message=f"Failed to call MCP tool: {e}",
            )

    async def _call_mcp_tool_link_url(
        self,
        tool_name: str,
        args: Dict[str, Any],
        server_name: str,
    ) -> McpToolResult:
        link_url = self._get_link_url()
        token = self._get_token()
        if not link_url or not token:
            return McpToolResult(
                request_id="",
                success=False,
                data="",
                error_message="LinkUrl/token not available",
            )

        request_id = f"link-{int(time.time() * 1000)}-{random.randint(0, 999999999):09d}"
        _log_api_call(
            "CallMcpTool(LinkUrl)",
            f"Tool={tool_name}, ArgsLength={len(json.dumps(args, ensure_ascii=False))}, RequestId={request_id}",
        )

        url = link_url.rstrip("/") + "/callTool"
        payload: Dict[str, Any] = {
            "args": args,
            "server": server_name,
            "requestId": request_id,
            "tool": tool_name,
            "token": token,
        }

        try:
            client = self._get_link_http_client()
            resp = await client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Access-Token": token,
                },
            )

            if resp.status_code < 200 or resp.status_code >= 300:
                _log_api_response_with_details(
                    api_name="CallMcpTool(LinkUrl) Response",
                    request_id=request_id,
                    success=False,
                    key_fields={"http_status": resp.status_code,
                                "tool_name": tool_name},
                    full_response=resp.text,
                )
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message=f"HTTP request failed with code: {resp.status_code}",
                )

            outer = resp.json()
            data_field = outer.get("data")
            if data_field is None:
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message="No data field in LinkUrl response",
                )

            if isinstance(data_field, str):
                parsed_data = json.loads(data_field)
            elif isinstance(data_field, dict):
                parsed_data = data_field
            else:
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message="Invalid data field type in LinkUrl response",
                )

            result_field = parsed_data.get("result", {})
            if not isinstance(result_field, dict):
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message="No result field in LinkUrl response data",
                )

            is_error = bool(result_field.get("isError", False))
            content = result_field.get("content", [])
            text_content = ""
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, str):
                    text_content = first
                elif isinstance(first, dict):
                    text_content = first.get("text") or first.get(
                        "blob") or first.get("data") or ""

            response_preview = ""
            if text_content:
                response_preview = _truncate_string_for_log(
                    str(text_content), 2000)

            key_fields = {
                "tool_name": tool_name,
                "server": server_name,
                "is_error": is_error,
                "data_len": len(str(text_content)),
            }
            if response_preview:
                key_fields["response_preview"] = response_preview

            _log_api_response_with_details(
                api_name="CallMcpTool(LinkUrl) Response",
                request_id=request_id,
                success=not is_error,
                key_fields=key_fields,
                full_response=str(text_content) if is_error else "",
            )

            if is_error:
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message=str(text_content),
                )

            return McpToolResult(
                request_id=request_id,
                success=True,
                data=str(text_content),
                error_message="",
            )
        except Exception as e:
            _log_operation_error(
                "CallMcpTool(LinkUrl)",
                f"HTTP request failed: {e}",
                True,
                request_id=request_id,
            )
            return McpToolResult(
                request_id=request_id,
                success=False,
                data="",
                error_message=f"HTTP request failed: {e}",
            )

    async def get_metrics(
        self,
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> SessionMetricsResult:
        """
        Get runtime metrics for this session.

        The underlying service returns a JSON string. This method parses it and
        returns a structured result.
        """
        tool_result = await self.call_mcp_tool(
            tool_name="get_metrics",
            args={},
            read_timeout=read_timeout,
            connect_timeout=connect_timeout,
        )

        if not tool_result.success:
            return SessionMetricsResult(
                request_id=tool_result.request_id,
                success=False,
                metrics=None,
                error_message=tool_result.error_message,
                raw={},
            )

        try:
            raw = (
                json.loads(tool_result.data)
                if isinstance(tool_result.data, str)
                else tool_result.data
            )
            if not isinstance(raw, dict):
                raise ValueError("get_metrics returned non-object JSON")

            def _float_from_first_key(data: dict, keys: list[str], default: float = 0.0) -> float:
                for k in keys:
                    if k in data and data.get(k) is not None:
                        try:
                            return float(data.get(k) or 0.0)
                        except Exception:
                            pass
                return float(default)

            metrics = SessionMetrics(
                cpu_count=int(raw.get("cpu_count", 0) or 0),
                cpu_used_pct=float(raw.get("cpu_used_pct", 0.0) or 0.0),
                disk_total=int(raw.get("disk_total", 0) or 0),
                disk_used=int(raw.get("disk_used", 0) or 0),
                mem_total=int(raw.get("mem_total", 0) or 0),
                mem_used=int(raw.get("mem_used", 0) or 0),
                rx_rate_kbyte_per_s=_float_from_first_key(
                    raw,
                    ["rx_rate_kbyte_per_s", "rx_rate_kbps", "rx_rate_KBps"],
                ),
                tx_rate_kbyte_per_s=_float_from_first_key(
                    raw,
                    ["tx_rate_kbyte_per_s", "tx_rate_kbps", "tx_rate_KBps"],
                ),
                rx_used_kbyte=_float_from_first_key(
                    raw, ["rx_used_kbyte", "rx_used_kb", "rx_used_KB"]),
                tx_used_kbyte=_float_from_first_key(
                    raw, ["tx_used_kbyte", "tx_used_kb", "tx_used_KB"]),
                timestamp=str(raw.get("timestamp", "") or ""),
            )
            return SessionMetricsResult(
                request_id=tool_result.request_id,
                success=True,
                metrics=metrics,
                error_message="",
                raw=raw,
            )
        except Exception as e:
            return SessionMetricsResult(
                request_id=tool_result.request_id,
                success=False,
                metrics=None,
                error_message=f"Failed to parse get_metrics response: {e}",
                raw={},
            )

    async def _call_mcp_tool_api(
        self,
        tool_name: str,
        args_json: str,
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
        auto_gen_session: bool = False,
        server_name: str = "",
    ):
        """
        Handle traditional API-based MCP tool calls asynchronously.
        """
        _log_api_call(
            "CallMcpTool",
            f"Tool={tool_name}, SessionId={self.session_id}, ArgsLength={len(args_json)}",
        )

        request_kwargs: Dict[str, Any] = {
            "authorization": f"Bearer {self._get_api_key()}",
            "session_id": self.session_id,
            "name": tool_name,
            "args": args_json,
            "auto_gen_session": auto_gen_session,
            "server": server_name,
        }

        request = CallMcpToolRequest(**request_kwargs)

        try:
            # Try async method first, fall back to sync wrapped in asyncio.to_thread
            client = self._get_client()
            response = await client.call_mcp_tool_async(
                request, read_timeout=read_timeout, connect_timeout=connect_timeout
            )

            # Extract request ID
            request_id = extract_request_id(response)

            # Check for API-level errors
            response_map = response.to_map()
            if not response_map:
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message="Invalid response format",
                )

            body = response_map.get("body", {})
            if not body:
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message="Invalid response body",
                )

            # Parse the Data field
            data_str = body.get("Data", "")
            if not data_str:
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message="Empty response data",
                )

            # Parse JSON data
            try:
                # Handle both string and dict responses
                if isinstance(data_str, dict):
                    data_obj = data_str
                elif isinstance(data_str, str):
                    data_obj = json.loads(data_str)
                else:
                    # Handle MagicMock or other non-string types in tests
                    data_obj = {}
            except json.JSONDecodeError as e:
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message=f"Failed to parse response data: {e}",
                )

            # Extract content
            content = data_obj.get("content", [])
            is_error = data_obj.get("isError", False)

            # Extract text from content
            text_content = ""
            if content and isinstance(content, list) and len(content) > 0:
                first_content = content[0]
                if isinstance(first_content, dict):
                    text_content = first_content.get("text", "")

            if is_error:
                _log_operation_error(
                    "CallMcpTool",
                    f"Tool returned error: {text_content}",
                    False,
                    request_id=request_id,
                )
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    data="",
                    error_message=text_content,
                )

            _log_api_response_with_details(
                "CallMcpTool",
                request_id,
                True,
                {"tool": tool_name},
                text_content[:200] if text_content else "",
            )

            return McpToolResult(
                request_id=request_id,
                success=True,
                data=text_content,
                error_message="",
            )

        except Exception as e:
            _log_operation_error(
                "CallMcpTool", f"API request failed: {e}", True)
            return McpToolResult(
                request_id="",
                success=False,
                data="",
                error_message=f"API request failed: {e}",
            )

    async def beta_pause(
        self, timeout: int = 600, poll_interval: float = 2.0
    ) -> SessionPauseResult:
        """
        Pause the session and wait until it enters PAUSED state.

        Note:
            This feature is currently in whitelist-only access.
            Contact agentbay_dev@alibabacloud.com to request access.

        Args:
            timeout: Timeout in seconds, default 600
            poll_interval: Polling interval in seconds, default 2.0

        Returns:
            SessionPauseResult: Result containing request ID, success status, and session status
        """
        try:
            # Send pause request
            request = PauseSessionAsyncRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self.session_id,
            )

            _log_api_call("PauseSessionAsync", f"SessionId={self.session_id}")

            response = await self._get_client().pause_session_async_async(request)
            request_id = extract_request_id(response)

            # Check API response
            response_map = response.to_map()
            if not response_map:
                return SessionPauseResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response format",
                )

            body = response_map.get("body", {})
            if not body:
                return SessionPauseResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response body",
                )

            success = body.get("Success", False)
            if not success:
                code = body.get("Code", "")
                message = body.get("Message", "")
                error_message = f"[{code}] {message}" if code or message else "Unknown error"
                _log_operation_error("beta_pause", error_message)
                return SessionPauseResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_message,
                )

            _logger.info(
                f"Pause request sent for session {self.session_id}, waiting for PAUSED state")

            # Poll session status
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    session_result = await self.agent_bay._get_session(self.session_id)
                    if session_result.success and session_result.data:
                        status = session_result.data.status
                        poll_request_id = session_result.request_id
                        _logger.info(
                            f"Polling session status: {status}, request_id: {poll_request_id}")

                        if status == "PAUSED":
                            _log_operation_success(
                                "beta_pause", f"Session {self.session_id} paused successfully")
                            return SessionPauseResult(
                                request_id=request_id,
                                success=True,
                                status="PAUSED",
                            )

                        if status == "PAUSING":
                            _logger.debug(
                                "Session is pausing, continue polling")
                        else:
                            _log_operation_error(
                                "beta_pause", f"Session in unexpected state: {status}")
                            return SessionPauseResult(
                                request_id=request_id,
                                success=False,
                                error_message=f"Pause failed, session in unexpected state: {status}",
                                status=status,
                            )
                except Exception as e:
                    _logger.debug(f"Failed to get session status: {e}")

                await asyncio.sleep(poll_interval)

            _log_operation_error(
                "beta_pause", f"Timeout waiting for session {self.session_id} after {timeout}s")
            return SessionPauseResult(
                success=False,
                status="",
                error_message=f"Timed out after {timeout}s waiting for PAUSED state",
            )

        except Exception as e:
            _log_operation_error("beta_pause", str(e))
            return SessionPauseResult(
                request_id="",
                success=False,
                error_message=f"Failed to pause session: {e}",
            )

    async def beta_resume(
        self, timeout: int = 600, poll_interval: float = 2.0
    ) -> SessionResumeResult:
        """
        Resume the session and wait until it enters RUNNING state.

        Args:
            timeout: Timeout in seconds, default 600
            poll_interval: Polling interval in seconds, default 2.0

        Returns:
            SessionResumeResult: Result containing request ID, success status, and session status
        """
        try:
            # Send resume request
            request = ResumeSessionAsyncRequest(
                authorization=f"Bearer {self._get_api_key()}",
                session_id=self.session_id,
            )

            _log_api_call("ResumeSessionAsync", f"SessionId={self.session_id}")

            response = await self._get_client().resume_session_async_async(request)
            request_id = extract_request_id(response)

            # Check API response
            response_map = response.to_map()
            if not response_map:
                return SessionResumeResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response format",
                )

            body = response_map.get("body", {})
            if not body:
                return SessionResumeResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response body",
                )

            success = body.get("Success", False)
            if not success:
                code = body.get("Code", "")
                message = body.get("Message", "")
                error_message = f"[{code}] {message}" if code or message else "Unknown error"
                _log_operation_error("beta_resume", error_message)
                return SessionResumeResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_message,
                )

            _logger.info(
                f"Resume request sent for session {self.session_id}, waiting for RUNNING state")

            # Poll session status
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    session_result = await self.agent_bay._get_session(self.session_id)
                    if session_result.success and session_result.data:
                        status = session_result.data.status
                        poll_request_id = session_result.request_id
                        _logger.info(
                            f"Polling session status: {status}, request_id: {poll_request_id}")

                        if status == "RUNNING":
                            _log_operation_success(
                                "beta_resume", f"Session {self.session_id} resumed successfully")
                            return SessionResumeResult(
                                request_id=request_id,
                                success=True,
                                status="RUNNING",
                            )

                        if status == "RESUMING":
                            _logger.debug(
                                "Session is resuming, continue polling")
                        else:
                            _log_operation_error(
                                "beta_resume", f"Session in unexpected state: {status}")
                            return SessionResumeResult(
                                request_id=request_id,
                                success=False,
                                error_message=f"Resume failed, session in unexpected state: {status}",
                                status=status,
                            )
                except Exception as e:
                    _logger.debug(f"Failed to get session status: {e}")

                await asyncio.sleep(poll_interval)

            _log_operation_error(
                "beta_resume", f"Timeout waiting for session {self.session_id}")
            return SessionResumeResult(
                request_id="",
                success=False,
                error_message=f"Timed out after {timeout}s waiting for RUNNING state",
            )

        except Exception as e:
            _log_operation_error("beta_resume", str(e))
            return SessionResumeResult(
                request_id="",
                success=False,
                error_message=f"Failed to resume session: {e}",
            )
