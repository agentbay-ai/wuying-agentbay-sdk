import asyncio
import json
import time
from typing import TYPE_CHECKING, Any, List, Optional

from .._common.exceptions import AgentBayError, ClearanceTimeoutError
from .._common.models.response import (
    ApiResponse,
    OperationResult,
    extract_request_id,
)
from ..api.models import (
    ClearContextRequest,
    DeleteContextFileRequest,
    DeleteContextRequest,
    DescribeContextFilesRequest,
    GetContextFileDownloadUrlRequest,
    GetContextFileUploadUrlRequest,
    GetContextRequest,
    ListContextsRequest,
    ModifyContextRequest,
)

from .._common.logger import (
    _log_api_call,
    _log_api_response,
    _log_api_response_with_details,
    _log_operation_error,
    get_logger,
)

# Initialize logger for this module
_logger = get_logger("context")

if TYPE_CHECKING:
    from .agentbay import AsyncAgentBay


class Context:
    """
    Represents a persistent storage context in the AgentBay cloud environment.

    Attributes:
        id (str): The unique identifier of the context.
        name (str): The name of the context.
        created_at (str): Date and time when the Context was created.
        last_used_at (str): Date and time when the Context was last used.
    """

    def __init__(
        self,
        id: str,
        name: str,
        created_at: Optional[str] = None,
        last_used_at: Optional[str] = None,
    ):
        """
        Initialize a Context object.

        Args:
            id (str): The unique identifier of the context.
            name (str): The name of the context.
            created_at (Optional[str], optional): Date and time when the Context was
                created. Defaults to None.
            last_used_at (Optional[str], optional): Date and time when the Context was
                last used. Defaults to None.
        """
        self.id = id
        self.name = name
        self.created_at = created_at
        self.last_used_at = last_used_at


class ContextResult(ApiResponse):
    """Result of operations returning a Context."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        context_id: str = "",
        context: Optional[Context] = None,
        error_message: str = "",
    ):
        """
        Initialize a ContextResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            context_id (str, optional): The unique identifier of the context.
            context (Optional[Context], optional): The Context object.
            error_message (str, optional): Error message if operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.context_id = context_id
        self.context = context
        self.error_message = error_message


class ContextListResult(ApiResponse):
    """Result of operations returning a list of Contexts."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        contexts: Optional[List[Context]] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
        total_count: Optional[int] = None,
        error_message: str = "",
    ):
        """
        Initialize a ContextListResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            contexts (Optional[List[Context]], optional): The list of context objects.
            next_token (Optional[str], optional): Token for the next page of results.
            max_results (Optional[int], optional): Maximum number of results per page.
            total_count (Optional[int], optional): Total number of contexts available.
            error_message (str, optional): Error message if operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.contexts = contexts if contexts is not None else []
        self.next_token = next_token
        self.max_results = max_results
        self.total_count = total_count
        self.error_message = error_message


class ContextFileEntry:
    """Represents a file item in a context."""

    def __init__(
        self,
        file_id: str,
        file_name: str,
        file_path: str,
        file_type: Optional[str] = None,
        gmt_create: Optional[str] = None,
        gmt_modified: Optional[str] = None,
        size: Optional[int] = None,
        status: Optional[str] = None,
    ):
        self.file_id = file_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.size = size
        self.status = status


class FileUrlResult(ApiResponse):
    """Result of a presigned URL request."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        url: str = "",
        expire_time: Optional[int] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.url = url
        self.expire_time = expire_time
        self.error_message = error_message


class ContextFileListResult(ApiResponse):
    """Result of file listing operation."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        entries: Optional[List[ContextFileEntry]] = None,
        count: Optional[int] = None,
        next_token: Optional[str] = None,
    ):
        super().__init__(request_id)
        self.success = success
        self.entries = entries or []
        self.count = count
        self.next_token = next_token


class ClearContextResult(OperationResult):
    """
    Result of context clear operations, including the real-time status.

    Attributes:
        request_id (str): Unique identifier for the API request.
        success (bool): Whether the operation was successful.
        error_message (str): Error message if the operation failed.
        status (Optional[str]): Current status of the clearing task. This corresponds to the
            context's state field. Possible values:
            - "clearing": Context data is being cleared (in progress)
            - "available": Clearing completed successfully
            - Other values may indicate the context state after clearing
        context_id (Optional[str]): The unique identifier of the context being cleared.
    """

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        status: Optional[str] = None,
        context_id: Optional[str] = None,
    ):
        super().__init__(request_id, success, None, error_message)
        self.status = status
        self.context_id = context_id


class ContextListParams:
    """Parameters for listing contexts with pagination support."""

    def __init__(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize ContextListParams.

        Args:
            max_results (Optional[int], optional): Maximum number of results per page.
                Defaults to 10 if not specified.
            next_token (Optional[str], optional): Token for the next page of results.
            session_id (Optional[str], optional): Filter by session ID.
        """
        self.max_results = max_results
        self.next_token = next_token
        self.session_id = session_id


class AsyncContextService:
    """
    Provides methods to manage persistent contexts in the AgentBay cloud environment.
    """

    def __init__(self, agent_bay: "AsyncAgentBay"):
        """
        Initialize the ContextService.

        Args:
            agent_bay (AsyncAgentBay): The AgentBay instance.
        """
        self.agent_bay = agent_bay

    async def list(
        self, params: Optional[ContextListParams] = None
    ) -> ContextListResult:
        """
        Lists all available contexts with pagination support.

        Args:
            params (Optional[ContextListParams], optional): Parameters for listing contexts.
                If None, defaults will be used.

        Returns:
            ContextListResult: A result object containing the list of Context objects,
                pagination information, and request ID.

        Example:
            ```python
            result = await agent_bay.context.list()
            params = ContextListParams(max_results=20, next_token=result.next_token)
            next_result = await agent_bay.context.list(params)
            ```
        """
        try:
            if params is None:
                params = ContextListParams()
            max_results = params.max_results if params.max_results is not None else 10
            request_details = f"MaxResults={max_results}"
            if params.next_token:
                request_details += f", NextToken={params.next_token}"
            if params.session_id:
                request_details += f", SessionId={params.session_id}"
            _log_api_call("ListContexts", request_details)
            request = ListContextsRequest(
                authorization=f"Bearer {self.agent_bay.api_key}",
                max_results=max_results,
            )
            if params.next_token:
                request.next_token = params.next_token
            if params.session_id:
                request.session_id = params.session_id
            client = self.agent_bay.client
            response = await client.list_contexts_async(request)
            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
                _log_api_response(response_body)
            except Exception:
                _logger.debug(f"Response: {response}")
            request_id = extract_request_id(response)
            try:
                response_map = response.to_map()
                if not isinstance(response_map, dict):
                    return ContextListResult(
                        request_id=request_id,
                        success=False,
                        contexts=[],
                        error_message="Invalid response format",
                    )
                body = response_map.get("body", {})
                if not isinstance(body, dict):
                    return ContextListResult(
                        request_id=request_id,
                        success=False,
                        contexts=[],
                        error_message="Invalid response body",
                    )

                # Check for API-level errors
                if not body.get("Success", True) and body.get("Code"):
                    code = body.get("Code", "Unknown")
                    message = body.get("Message", "Unknown error")
                    return ContextListResult(
                        request_id=request_id,
                        success=False,
                        contexts=[],
                        error_message=f"[{code}] {message}",
                    )

                contexts = []
                response_data = body.get("Data", [])
                if response_data and isinstance(response_data, list):
                    for context_data in response_data:
                        if isinstance(context_data, dict):
                            context = Context(
                                id=context_data.get("Id", ""),
                                name=context_data.get("Name", ""),
                                created_at=context_data.get("CreateTime"),
                                last_used_at=context_data.get("LastUsedTime"),
                            )
                            contexts.append(context)
                next_token = body.get("NextToken")
                max_results = body.get("MaxResults", max_results)
                total_count = body.get("TotalCount")
                return ContextListResult(
                    request_id=request_id,
                    success=True,
                    contexts=contexts,
                    next_token=next_token,
                    max_results=max_results,
                    total_count=total_count,
                    error_message="",
                )
            except Exception as e:
                _log_operation_error("parse ListContexts response", str(e))
                return ContextListResult(
                    request_id=request_id,
                    success=False,
                    contexts=[],
                    error_message=f"Failed to parse response: {e}",
                )
        except Exception as e:
            _log_operation_error("ListContexts", str(e))
            return ContextListResult(
                request_id="",
                success=False,
                contexts=[],
                next_token=None,
                max_results=None,
                total_count=None,
                error_message=f"Failed to list contexts: {e}",
            )

    async def get(
        self,
        name: Optional[str] = None,
        create: bool = False,
        context_id: Optional[str] = None,
    ) -> ContextResult:
        """
        Gets a context by name or ID. Optionally creates it if it doesn't exist.

        Args:
            name (Optional[str], optional): The name of the context to get. Defaults to None.
            create (bool, optional): Whether to create the context if it doesn't exist. Defaults to False.
            context_id (Optional[str], optional): The ID of the context to get. Defaults to None.

        Returns:
            ContextResult: The ContextResult object containing the Context and request ID.
                - success (bool): True if the operation succeeded
                - context (Context): The context object (if success is True)
                - context_id (str): The ID of the context
                - request_id (str): Unique identifier for this API request
                - error_message (str): Error description (if success is False)

        Raises:
            AgentBayError: If neither name nor context_id is provided, or if create=True with context_id.

        Example:
            ```python
            result = await agent_bay.context.get(name="my-context")
            result = await agent_bay.context.get(name="new-context", create=True)
            result = await agent_bay.context.get(context_id="ctx-04bdwfj7u22a1s30g")
            ```

        Note:
            - Either name or context_id must be provided (not both)
            - When create=True, only name parameter is allowed
            - Created contexts are persistent and can be shared across sessions
            - Context names must be unique within your account

        See Also:
            AsyncContextService.list, AsyncContextService.update, AsyncContextService.delete
        """
        # Validate parameters
        if name is None and context_id is None:
            raise AgentBayError("Either 'name' or 'context_id' must be provided")

        if create and context_id is not None:
            raise AgentBayError(
                "Cannot create context using context_id. Use 'name' parameter when create=True"
            )

        try:
            # Log what we're sending to the server
            log_details = f"AllowCreate={create}"
            if name is not None:
                log_details += f", Name={name}"
            if context_id is not None:
                log_details += f", Id={context_id}"

            _log_api_call("GetContext", log_details)

            request = GetContextRequest(
                name=name,
                context_id=context_id,
                allow_create=create,
                authorization=f"Bearer {self.agent_bay.api_key}",
                login_region_id=self.agent_bay.region_id if create else None,
            )
            client = self.agent_bay.client
            response = await client.get_context_async(request)
            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
                _log_api_response(response_body)
            except Exception:
                _logger.debug(f"Response: {response}")
            request_id = extract_request_id(response)
            try:
                response_map = response.to_map()
                if not isinstance(response_map, dict):
                    return ContextResult(
                        request_id=request_id,
                        success=False,
                        context_id="",
                        context=None,
                        error_message="Invalid response format",
                    )

                body = response_map.get("body", {})
                if not isinstance(body, dict):
                    return ContextResult(
                        request_id=request_id,
                        success=False,
                        context_id="",
                        context=None,
                        error_message="Invalid response body",
                    )

                # Check for API-level errors
                if not body.get("Success", True) and body.get("Code"):
                    code = body.get("Code", "Unknown")
                    message = body.get("Message", "Unknown error")
                    return ContextResult(
                        request_id=request_id,
                        success=False,
                        context_id="",
                        context=None,
                        error_message=f"[{code}] {message}",
                    )

                data = body.get("Data", {})
                if not isinstance(data, dict):
                    return ContextResult(
                        request_id=request_id,
                        success=False,
                        context_id="",
                        context=None,
                        error_message="Invalid data format",
                    )
                context_id = data.get("Id", "")
                context_name = data.get("Name", "") or name or ""
                context = Context(
                    id=context_id,
                    name=context_name,
                    created_at=data.get("CreateTime"),
                    last_used_at=data.get("LastUsedTime"),
                )
                return ContextResult(
                    request_id=request_id,
                    success=True,
                    context_id=context_id,
                    context=context,
                    error_message="",
                )
            except Exception as e:
                _log_operation_error("parse GetContext response", str(e))
                return ContextResult(
                    request_id=request_id,
                    success=False,
                    context_id="",
                    context=None,
                    error_message=f"Failed to parse response: {e}",
                )
        except Exception as e:
            _log_operation_error("GetContext", str(e))
            identifier = name if name is not None else context_id
            return ContextResult(
                request_id="",
                success=False,
                context_id="",
                context=None,
                error_message=f"Failed to get context {identifier}: {e}",
            )

    async def create(self, name: str) -> ContextResult:
        """
        Creates a new context with the given name.

        Args:
            name (str): The name for the new context.

        Returns:
            ContextResult: The created ContextResult object with request ID.

        Example:
            ```python
            result = await agent_bay.context.create("my-new-context")
            ```
        """
        return await self.get(name, create=True)

    async def update(self, context: Context) -> OperationResult:
        """
        Updates the specified context (currently only name can be updated).

        Args:
            context (Context): The Context object to update. Must have id and name attributes.

        Returns:
            OperationResult: Result object containing success status and request ID.
                - success (bool): True if the operation succeeded
                - data (str): Success message (if success is True)
                - request_id (str): Unique identifier for this API request
                - error_message (str): Error description (if success is False)

        Raises:
            AgentBayError: If the context update fails.

        Example:
            ```python
            result = await agent_bay.context.get(name="old-name")
            result.context.name = "new-name"
            update_result = await agent_bay.context.update(result.context)
            ```

        Note:
            - Currently only the context name can be updated
            - Context ID cannot be changed
            - The context must exist before it can be updated
            - Updated name must be unique within your account

        See Also:
            AsyncContextService.get, AsyncContextService.list, AsyncContextService.delete
        """
        try:
            _log_api_call("ModifyContext", f"Id={context.id}, Name={context.name}")
            request = ModifyContextRequest(
                id=context.id,
                name=context.name,
                authorization=f"Bearer {self.agent_bay.api_key}",
            )
            client = self.agent_bay.client
            response = await client.modify_context_async(request)
            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
                _log_api_response(response_body)
            except Exception:
                _logger.debug(f"Response: {response}")
            request_id = extract_request_id(response)
            try:
                response_map = response.to_map() if hasattr(response, "to_map") else {}
                if not isinstance(response_map, dict) or not isinstance(
                    response_map.get("body", {}), dict
                ):
                    return OperationResult(
                        request_id=request_id,
                        success=False,
                        error_message="Invalid response format",
                    )
                body = response_map.get("body", {})
                success = body.get("Success", False)
                error_message = (
                    ""
                    if success
                    else f"[{body.get('Code', 'Unknown')}] {body.get('Message', 'Unknown error')}"
                )
                return OperationResult(
                    request_id=request_id,
                    success=success,
                    data=True if success else False,
                    error_message=error_message,
                )
            except Exception as e:
                _logger.exception(f"Error parsing ModifyContext response: {e}")
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Failed to parse response: {str(e)}",
                )
        except Exception as e:
            _logger.exception(f"Error calling ModifyContext: {e}")
            raise AgentBayError(f"Failed to update context {context.id}: {e}")

    async def delete(self, context: Context) -> OperationResult:
        """
        Deletes the specified context.

        Args:
            context (Context): The Context object to delete.

        Returns:
            OperationResult: Result object containing success status and request ID.

        Example:
            ```python
            result = await agent_bay.context.get(name="my-context")
            delete_result = await agent_bay.context.delete(result.context)
            ```
        """
        try:
            _log_api_call("DeleteContext", f"Id={context.id}")
            request = DeleteContextRequest(
                id=context.id,
                authorization=f"Bearer {self.agent_bay.api_key}",
            )
            client = self.agent_bay.client
            response = await client.delete_context_async(request)
            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
                _log_api_response(response_body)
            except Exception:
                _logger.debug(f"Response: {response}")
            request_id = extract_request_id(response)
            try:
                response_map = response.to_map() if hasattr(response, "to_map") else {}
                if not isinstance(response_map, dict) or not isinstance(
                    response_map.get("body", {}), dict
                ):
                    return OperationResult(
                        request_id=request_id,
                        success=False,
                        error_message="Invalid response format",
                    )
                body = response_map.get("body", {})
                success = body.get("Success", False)
                error_message = (
                    ""
                    if success
                    else f"[{body.get('Code', 'Unknown')}] {body.get('Message', 'Unknown error')}"
                )
                return OperationResult(
                    request_id=request_id,
                    success=success,
                    data=True if success else False,
                    error_message=error_message,
                )
            except Exception as e:
                _logger.exception(f"Error parsing DeleteContext response: {e}")
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Failed to parse response: {str(e)}",
                )
        except Exception as e:
            _logger.exception(f"Error calling DeleteContext: {e}")
            raise AgentBayError(f"Failed to delete context {context.id}: {e}")

    async def get_file_download_url(
        self, context_id: str, file_path: str
    ) -> FileUrlResult:
        """
        Get a presigned download URL for a file in a context.

        Args:
            context_id (str): The ID of the context.
            file_path (str): The path to the file in the context.

        Returns:
            FileUrlResult: A result object containing the presigned URL, expire time, and request ID.

        Note:
            The presigned URL expires in 1 hour by default.

        Example:
            ```python
            ctx_result = await agent_bay.context.get(name="my-context", create=True)
            url_result = await agent_bay.context.get_file_download_url(ctx_result.context_id, "/path/to/file.txt")
            print(url_result.url)
            ```
        """
        _log_api_call(
            "GetContextFileDownloadUrl", f"ContextId={context_id}, FilePath={file_path}"
        )
        req = GetContextFileDownloadUrlRequest(
            authorization=f"Bearer {self.agent_bay.api_key}",
            context_id=context_id,
            file_path=file_path,
        )
        # Try async method first, fall back to sync wrapped in asyncio.to_thread
        client = self.agent_bay.client
        resp = await client.get_context_file_download_url_async(req)
        try:
            response_body = json.dumps(
                resp.to_map().get("body", {}), ensure_ascii=False, indent=2
            )
            _log_api_response(response_body)
        except Exception:
            _logger.debug(f"Response: {resp}")
        request_id = extract_request_id(resp)
        body = getattr(resp, "body", None)

        # Check for API-level errors
        if body:
            success = getattr(body, "success", False)
            if not success:
                code = getattr(body, "code", "Unknown")
                message = getattr(body, "message", "Unknown error")
                return FileUrlResult(
                    request_id=request_id,
                    success=False,
                    url="",
                    expire_time=None,
                    error_message=f"[{code}] {message}",
                )

        data = getattr(body, "data", None)
        return FileUrlResult(
            request_id=request_id,
            success=bool(body and getattr(body, "success", False)),
            url=(data.url if data else ""),
            expire_time=(data.expire_time if data else None),
            error_message="",
        )

    async def get_file_upload_url(
        self, context_id: str, file_path: str
    ) -> FileUrlResult:
        """
        Get a presigned upload URL for a file in a context.

        Args:
            context_id (str): The ID of the context.
            file_path (str): The path to the file in the context.

        Returns:
            FileUrlResult: A result object containing the presigned URL, expire time, and request ID.

        Note:
            The presigned URL expires in 1 hour by default.

        Example:
            ```python
            ctx_result = await agent_bay.context.get(name="my-context", create=True)
            url_result = await agent_bay.context.get_file_upload_url(ctx_result.context_id, "/path/to/file.txt")
            print(url_result.url)
            ```
        """
        _log_api_call(
            "GetContextFileUploadUrl", f"ContextId={context_id}, FilePath={file_path}"
        )
        req = GetContextFileUploadUrlRequest(
            authorization=f"Bearer {self.agent_bay.api_key}",
            context_id=context_id,
            file_path=file_path,
        )
        client = self.agent_bay.client
        resp = await client.get_context_file_upload_url_async(req)
        try:
            response_body = json.dumps(
                resp.to_map().get("body", {}), ensure_ascii=False, indent=2
            )
            _log_api_response(response_body)
        except Exception:
            _logger.debug(f"Response: {resp}")
        request_id = extract_request_id(resp)
        body = getattr(resp, "body", None)

        # Check for API-level errors
        if body:
            success = getattr(body, "success", False)
            if not success:
                code = getattr(body, "code", "Unknown")
                message = getattr(body, "message", "Unknown error")
                return FileUrlResult(
                    request_id=request_id,
                    success=False,
                    url="",
                    expire_time=None,
                    error_message=f"[{code}] {message}",
                )

        data = getattr(body, "data", None)
        return FileUrlResult(
            request_id=request_id,
            success=bool(body and getattr(body, "success", False)),
            url=(data.url if data else ""),
            expire_time=(data.expire_time if data else None),
            error_message="",
        )

    async def delete_file(self, context_id: str, file_path: str) -> OperationResult:
        """
        Delete a file in a context.

        Args:
            context_id (str): The ID of the context.
            file_path (str): The path to the file to delete.

        Returns:
            OperationResult: A result object containing success status and request ID.

        Example:
            ```python
            ctx_result = await agent_bay.context.get(name="my-context", create=True)
            delete_result = await agent_bay.context.delete_file(ctx_result.context_id, "/path/to/file.txt")
            ```
        """
        _log_api_call(
            "DeleteContextFile", f"ContextId={context_id}, FilePath={file_path}"
        )
        req = DeleteContextFileRequest(
            authorization=f"Bearer {self.agent_bay.api_key}",
            context_id=context_id,
            file_path=file_path,
        )
        client = self.agent_bay.client
        resp = await client.delete_context_file_async(req)
        try:
            response_body = json.dumps(
                resp.to_map().get("body", {}), ensure_ascii=False, indent=2
            )
            _log_api_response(response_body)
        except Exception:
            _logger.debug(f"Response: {resp}")
        request_id = extract_request_id(resp)
        body = getattr(resp, "body", None)
        success = bool(body and getattr(body, "success", False))

        # Check for API-level errors
        error_message = ""
        if not success and body:
            code = getattr(body, "code", "Unknown")
            message = getattr(body, "message", "Failed to delete file")
            error_message = f"[{code}] {message}"

        return OperationResult(
            request_id=request_id,
            success=success,
            data=True if success else False,
            error_message=error_message,
        )

    async def list_files(
        self,
        context_id: str,
        parent_folder_path: str,
        page_number: int = 1,
        page_size: int = 50,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> ContextFileListResult:
        """
        List files under a specific folder path in a context.

        Args:
            context_id (str): The ID of the context.
            parent_folder_path (str): The parent folder path to list files from.
            page_number (int): Deprecated. Use max_results/next_token instead.
            page_size (int): Deprecated. Use max_results/next_token instead.
            max_results (int, optional): Maximum number of entries to return per request.
            next_token (str, optional): Pagination token from a previous response.

        Returns:
            ContextFileListResult: A result object containing the list of files,
                request ID, and next_token for pagination.

        Example:
            ```python
            ctx_result = await agent_bay.context.get(name="my-context", create=True)
            files_result = await agent_bay.context.list_files(
                ctx_result.context_id, "/", max_results=50
            )
            print(f"Found {len(files_result.entries)} files")
            if files_result.next_token:
                next_page = await agent_bay.context.list_files(
                    ctx_result.context_id, "/",
                    max_results=50, next_token=files_result.next_token
                )
            ```
        """
        use_token_pagination = max_results is not None or next_token is not None
        _log_api_call(
            "DescribeContextFiles",
            f"ContextId={context_id}, ParentFolderPath={parent_folder_path}, "
            f"MaxResults={max_results}, NextToken={next_token}"
            if use_token_pagination
            else f"ContextId={context_id}, ParentFolderPath={parent_folder_path}, "
            f"PageNumber={page_number}, PageSize={page_size}",
        )
        req = DescribeContextFilesRequest(
            authorization=f"Bearer {self.agent_bay.api_key}",
            parent_folder_path=parent_folder_path,
            context_id=context_id,
            max_results=max_results if use_token_pagination else None,
            next_token=next_token if use_token_pagination else None,
            page_number=page_number if not use_token_pagination else None,
            page_size=page_size if not use_token_pagination else None,
        )
        client = self.agent_bay.client
        resp = await client.describe_context_files_async(req)
        try:
            response_body = json.dumps(
                resp.to_map().get("body", {}), ensure_ascii=False, indent=2
            )
            _log_api_response(response_body)
        except Exception:
            _logger.debug(f"Response: {resp}")
        request_id = extract_request_id(resp)
        body = getattr(resp, "body", None)
        raw_list = getattr(body, "data", None) or []
        entries = [
            ContextFileEntry(
                file_id=getattr(it, "file_id", ""),
                file_name=getattr(it, "file_name", ""),
                file_path=getattr(it, "file_path", ""),
                file_type=getattr(it, "file_type", None),
                gmt_create=getattr(it, "gmt_create", None),
                gmt_modified=getattr(it, "gmt_modified", None),
                size=getattr(it, "size", None),
                status=getattr(it, "status", None),
            )
            for it in raw_list
        ]
        return ContextFileListResult(
            request_id=request_id,
            success=bool(body and getattr(body, "success", False)),
            entries=entries,
            count=(getattr(body, "count", None) if body else None),
            next_token=(getattr(body, "next_token", None) if body else None),
        )

    async def clear_async(self, context_id: str) -> ClearContextResult:
        """
        Asynchronously initiate a task to clear the context's persistent data.

        This is a non-blocking method that returns immediately after initiating the clearing task
        on the backend. The context's state will transition to "clearing" while the operation
        is in progress.

        Args:
            context_id: Unique ID of the context to clear.

        Returns:
            A ClearContextResult object indicating the task has been successfully started,
            with status field set to "clearing".

        Raises:
            AgentBayError: If the backend API rejects the clearing request (e.g., invalid ID).

        Example:
            ```python
            result = await agent_bay.context.get(name="my-context", create=True)
            clear_result = await agent_bay.context.clear_async(result.context_id)
            ```
        """
        try:
            _log_api_call("ClearContext", f"ContextId={context_id}")
            request = ClearContextRequest(
                authorization=f"Bearer {self.agent_bay.api_key}",
                id=context_id,
            )
            client = self.agent_bay.client
            response = await client.clear_context_async(request)
            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
                _log_api_response(response_body)
            except Exception:
                _logger.debug(f"Response: {response}")

            request_id = extract_request_id(response)

            # Directly access response body object
            if not response.body:
                return ClearContextResult(
                    request_id=request_id,
                    success=False,
                    error_message="Empty response body",
                )

            body = response.body

            # Check for API-level errors
            if not body.success and body.code:
                return ClearContextResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"[{body.code}] {body.message or 'Unknown error'}",
                )

            # ClearContext API returns success info without Data field
            # Initial status is "clearing" when the task starts
            return ClearContextResult(
                request_id=request_id,
                success=True,
                context_id=context_id,
                status="clearing",
                error_message="",
            )
        except Exception as e:
            _log_operation_error("ClearContext", str(e))
            raise AgentBayError(
                f"Failed to start context clearing for {context_id}: {e}"
            )

    async def start_clear(self, context_id: str) -> ClearContextResult:
        """
        Deprecated alias for `clear_async`.

        This method is kept for backward compatibility and simply forwards to
        `clear_async`. Prefer using `clear_async` going forward.

        Args:
            context_id: Unique ID of the context to clear.

        Returns:
            ClearContextResult from `clear_async`.
        """
        return await self.clear_async(context_id)

    async def get_clear_status(self, context_id: str) -> ClearContextResult:
        """
        Query the status of the clearing task.

        This method calls GetContext API directly and parses the raw response to extract
        the state field, which indicates the current clearing status.

        Args:
            context_id: ID of the context.

        Returns:
            ClearContextResult object containing the current task status.

        Example:
            ```python
            result = await agent_bay.context.get(name="my-context", create=True)
            await agent_bay.context.clear_async(result.context_id)
            status_result = await agent_bay.context.get_clear_status(result.context_id)
            print(status_result.status)
            ```
        """
        try:
            _log_api_call("GetContext", f"ContextId={context_id} (for clear status)")
            request = GetContextRequest(
                authorization=f"Bearer {self.agent_bay.api_key}",
                context_id=context_id,
                allow_create=False,
            )
            client = self.agent_bay.client
            response = await client.get_context_async(request)
            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
                _log_api_response(response_body)
            except Exception:
                _logger.debug(f"Response: {response}")

            request_id = extract_request_id(response)

            # Directly access response body object
            if not response.body:
                return ClearContextResult(
                    request_id=request_id,
                    success=False,
                    error_message="Empty response body",
                )

            body = response.body

            # Check for API-level errors
            if not body.success and body.code:
                return ClearContextResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"[{body.code}] {body.message or 'Unknown error'}",
                )

            # Check if data exists
            if not body.data:
                return ClearContextResult(
                    request_id=request_id,
                    success=False,
                    error_message="No data in response",
                )

            data = body.data

            # Extract clearing status from the response data object
            # The server's state field indicates the clearing status:
            # - "clearing": Clearing is in progress
            # - "available": Clearing completed successfully
            # - "in-use": Context is being used
            # - "pre-available": Context is being prepared
            context_id = data.id or ""
            state = data.state or "clearing"  # Extract state from response object
            error_message = ""  # ErrorMessage is not in GetContextResponseBodyData

            return ClearContextResult(
                request_id=request_id,
                success=True,
                context_id=context_id,
                status=state,
                error_message=error_message,
            )
        except Exception as e:
            _log_operation_error("GetContext (for clear status)", str(e))
            return ClearContextResult(
                request_id="",
                success=False,
                error_message=f"Failed to get clear status: {e}",
            )

    async def clear(
        self, context_id: str, timeout: int = 60, poll_interval: float = 2.0
    ) -> ClearContextResult:
        """
        Asynchronously clear the context's persistent data and wait for the final result.

        This method wraps the `clear_async` and `get_clear_status` polling logic,
        providing the simplest and most direct way to handle clearing tasks.

        The clearing process transitions through the following states:
        - "clearing": Data clearing is in progress
        - "available": Clearing completed successfully (final success state)

        Args:
            context_id: Unique ID of the context to clear.
            timeout: Timeout in seconds to wait for task completion. Defaults to 60.
            poll_interval: Interval in seconds between status polls. Defaults to 2.0.

        Returns:
            ClearContextResult object containing the final task result.
            The status field will be "available" on success.

        Raises:
            ClearanceTimeoutError: If the task fails to complete within the timeout.
            AgentBayError: If an API or network error occurs during execution.

        Example:
            ```python
            result = await agent_bay.context.get(name="my-context", create=True)
            clear_result = await agent_bay.context.clear(result.context_id, timeout=60)
            ```
        """
        # 1. Asynchronously start the clearing task
        start_result = await self.clear_async(context_id)
        if not start_result.success:
            return start_result

        _logger.info(f"Started context clearing task for: {context_id}")

        # 2. Poll task status until completion or timeout
        start_time = time.time()
        max_attempts = int(timeout / poll_interval)
        attempt = 0

        while attempt < max_attempts:
            # Wait before querying
            await asyncio.sleep(poll_interval)
            attempt += 1

            # Query task status (using GetContext API with context ID)
            status_result = await self.get_clear_status(context_id)

            if not status_result.success:
                _logger.error(
                    f"Failed to get clear status: {status_result.error_message}"
                )
                return status_result

            status = status_result.status
            _logger.debug(
                f"Clear task status: {status} (attempt {attempt}/{max_attempts})"
            )

            # Check if completed
            # When clearing is complete, the state changes from "clearing" to "available"
            if status == "available":
                elapsed = time.time() - start_time
                _logger.info(f"Context cleared successfully in {elapsed:.2f} seconds")
                return ClearContextResult(
                    request_id=start_result.request_id,
                    success=True,
                    context_id=status_result.context_id,
                    status=status,
                    error_message="",
                )
            elif status not in ("clearing", "pre-available"):
                # If status is not "clearing" or "pre-available", and not "available",
                # treat it as a potential error or unexpected state
                elapsed = time.time() - start_time
                _logger.warning(
                    f"Context in unexpected state after {elapsed:.2f} seconds: {status}"
                )
                # Continue polling as the state might transition to "available"

        # Timeout
        elapsed = time.time() - start_time
        error_msg = f"Context clearing timed out after {elapsed:.2f} seconds"
        _logger.error(f"{error_msg}")
        raise ClearanceTimeoutError(error_msg)
