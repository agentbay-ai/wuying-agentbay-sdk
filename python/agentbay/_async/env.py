import json
from typing import Dict, List, Optional

from .._common.logger import get_logger
from .._common.models.response import BoolResult, EnvResult
from .base_service import AsyncBaseService

_logger = get_logger("env")


_ENV_SERVER = "wuying_system"
_ENV_TOOLS = ["set_env", "get_env"]


class AsyncEnv(AsyncBaseService):
    """
    Async environment variable management service for AgentBay sessions.

    Provides methods to set and get global environment variables that persist
    across all MCP tools (shell, code interpreter, etc.) within a session.
    """

    def __init__(self, session):
        super().__init__(session)
        self._tools_registered = False

    def _ensure_env_tools_registered(self):
        """Register env tools in mcpTools if missing (pre-started instances may omit them)."""
        if self._tools_registered:
            return
        self._tools_registered = True
        from .._common.models.mcp_tool import McpTool
        existing = {t.name for t in (self.session.mcpTools or [])}
        for tool_name in _ENV_TOOLS:
            if tool_name not in existing:
                self.session.mcpTools.append(McpTool(name=tool_name, server=_ENV_SERVER))

    async def set(self, envs: Dict[str, str]) -> BoolResult:
        """
        Set or update global environment variables in the session sandbox.

        Existing keys are overwritten; new keys are added. Variables become
        visible to all subsequent MCP tool invocations (shell, code interpreter, etc.).

        Args:
            envs: Dictionary of environment variable key-value pairs.
                Both keys and values must be strings. Must not be empty.

        Returns:
            BoolResult: Result with success=True if variables were set successfully.

        Raises:
            ValueError: If envs is empty or contains non-string keys/values.
        """
        self._ensure_env_tools_registered()
        if not envs:
            raise ValueError("envs must not be empty")

        for key, value in envs.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"All environment variable keys must be strings, "
                    f"got {type(key).__name__} for key '{key}'"
                )
            if not isinstance(value, str):
                raise ValueError(
                    f"All environment variable values must be strings, "
                    f"got {type(value).__name__} for key '{key}'"
                )

        envs_array = [{"key": k, "value": v} for k, v in envs.items()]
        args = {"envs": envs_array}

        try:
            result = await self.session.call_mcp_tool("set_env", args)
            return BoolResult(
                request_id=result.request_id,
                success=result.success,
                data=result.success,
                error_message=result.error_message,
            )
        except Exception as e:
            _logger.error(f"Failed to set environment variables: {e}")
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to set environment variables: {e}",
            )

    async def get(
        self, keys: Optional[List[str]] = None
    ) -> EnvResult:
        """
        Get global environment variables from the session sandbox.

        Args:
            keys: Optional list of specific variable names to retrieve.
                If None or empty, returns all environment variables.

        Returns:
            EnvResult: Result containing envs dict with variable key-value pairs.
        """
        self._ensure_env_tools_registered()
        args = {}
        if keys:
            args["keys"] = keys

        try:
            result = await self.session.call_mcp_tool("get_env", args)

            if result.success and result.data:
                try:
                    if isinstance(result.data, str):
                        envs_dict = json.loads(result.data)
                    elif isinstance(result.data, dict):
                        envs_dict = result.data
                    else:
                        envs_dict = {}
                except (json.JSONDecodeError, TypeError):
                    envs_dict = {}
            else:
                envs_dict = {}

            return EnvResult(
                request_id=result.request_id,
                success=result.success,
                envs=envs_dict,
                error_message=result.error_message,
            )
        except Exception as e:
            _logger.error(f"Failed to get environment variables: {e}")
            return EnvResult(
                request_id="",
                success=False,
                error_message=f"Failed to get environment variables: {e}",
            )
