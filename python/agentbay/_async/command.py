import json
from typing import Any, Dict, Optional, Tuple

from .._common.exceptions import AgentBayError, CommandError
from .._common.logger import get_logger
from .._common.models.command import CommandResult
from .._common.models.response import ApiResponse
from .base_service import AsyncBaseService

# Initialize _logger for this module
_logger = get_logger("command")


def _looks_like_wrapped_shell_payload(data_obj: Any) -> bool:
    """Conservatively determine whether a parsed JSON object looks like the
    shell-tool wrapper envelope ``{"exit_code": int, "stdout": str, "stderr": str}``.

    The check is intentionally strict: a single ``stdout`` field is not enough,
    because user commands can legitimately produce JSON that happens to contain
    a ``stdout`` field. We require either:
      * an integer ``exit_code`` plus at least one textual ``stdout``/``stderr``, or
      * both textual ``stdout`` and ``stderr`` (``exit_code`` may default to 0).
    """
    if not isinstance(data_obj, dict):
        return False
    has_int_exit_code = isinstance(data_obj.get("exit_code"), int) and not isinstance(
        data_obj.get("exit_code"), bool
    )
    has_stdout = isinstance(data_obj.get("stdout"), str)
    has_stderr = isinstance(data_obj.get("stderr"), str)
    if has_int_exit_code and (has_stdout or has_stderr):
        return True
    return has_stdout and has_stderr


def _parse_shell_payload(raw: Any) -> Tuple[str, str, int, str]:
    """Parse a shell-tool MCP response payload into ``(stdout, stderr, exit_code, trace_id)``.

    Different sandbox images return data in different shapes:

    * **Wrapped** (``code_latest`` and similar): ``{"exit_code": 0, "stdout": "...", "stderr": "..."}``
    * **Raw** (``imgc-*`` / openclaw and similar): the command's stdout returned verbatim
      with no JSON wrapping at all (whether or not it happens to be valid JSON)

    The wrapped shape is detected via :func:`_looks_like_wrapped_shell_payload`.
    Anything else — including JSON objects/arrays/scalars and plain text — is
    treated as raw command output.
    """
    if raw is None:
        return "", "", 0, ""
    if isinstance(raw, str):
        if not raw:
            return "", "", 0, ""
        try:
            data_obj = json.loads(raw)
        except (ValueError, TypeError):
            return raw, "", 0, ""
    else:
        data_obj = raw

    if _looks_like_wrapped_shell_payload(data_obj):
        return (
            data_obj.get("stdout", ""),
            data_obj.get("stderr", ""),
            data_obj.get("exit_code", 0)
            if isinstance(data_obj.get("exit_code"), int)
            else data_obj.get("errorCode", 0)
            if isinstance(data_obj.get("errorCode"), int)
            else 0,
            data_obj.get("traceId", ""),
        )

    # Raw payload: return the original string verbatim, or its repr as fallback.
    return (raw if isinstance(raw, str) else str(raw)), "", 0, ""


class AsyncCommand(AsyncBaseService):
    """
    Async command execution service for session shells in the AgentBay cloud environment.

    Use this class for non-blocking command execution; for blocking/synchronous usage,
    refer to the `Command` service in the sync API.
    """

    async def execute_command(
        self,
        command: str,
        timeout_ms: int = 50000,
        cwd: Optional[str] = None,
        envs: Optional[Dict[str, str]] = None,
    ) -> CommandResult:
        """
        Execute a shell command with optional working directory and environment variables.

        Executes a shell command in the session environment with configurable timeout,
        working directory, and environment variables. The command runs with session
        user permissions in a Linux shell environment.

        Args:
            command: The shell command to execute
            timeout_ms: Timeout in milliseconds (default: 50000ms/50s).
            cwd: The working directory for command execution. If not specified,
                the command runs in the default session directory
            envs: Environment variables as a dictionary of key-value pairs.
                These variables are set for the command execution only

        Returns:
            CommandResult: Result object containing:
                - success: Whether the command executed successfully (exit_code == 0)
                - output: Command output for backward compatibility (stdout + stderr)
                - exit_code: The exit code of the command execution (0 for success)
                - stdout: Standard output from the command execution
                - stderr: Standard error from the command execution
                - trace_id: Trace ID for error tracking (only present when exit_code != 0)
                - request_id: Unique identifier for this API request
                - error_message: Error description if execution failed

        Raises:
            CommandError: If the command execution fails due to system errors

        Example:
            session = agent_bay.create().session
            result = await session.command.execute_command("echo 'Hello, World!'")
            print(result.output)
            print(result.exit_code)
            await session.delete()

        Example:
            result = await session.command.execute_command(
                "pwd",
                timeout_ms=5000,
                cwd="/tmp",
                envs={"TEST_VAR": "test_value"}
            )
            print(result.stdout)
            await session.delete()
        """
        # Validate environment variables - strict type checking (before try block to allow ValueError to propagate)
        if envs is not None:
            invalid_vars = []
            for key, value in envs.items():
                if not isinstance(key, str):
                    invalid_vars.append(f"key '{key}' (type: {type(key).__name__})")
                if not isinstance(value, str):
                    invalid_vars.append(f"value for key '{key}' (type: {type(value).__name__})")

            if invalid_vars:
                raise ValueError(
                    f"Invalid environment variables: all keys and values must be strings. "
                    f"Found invalid entries: {', '.join(invalid_vars)}"
                )

        try:
            # Build request arguments
            args = {"command": command, "timeout_ms": timeout_ms}
            if cwd is not None:
                args["cwd"] = cwd
            if envs is not None:
                args["envs"] = envs

            result = await self.session.call_mcp_tool(
                "shell",
                args,
            )
            _logger.debug(f"Execute command response: {result}")

            if result.success:
                stdout, stderr, exit_code, trace_id = _parse_shell_payload(result.data)
                return CommandResult(
                    request_id=result.request_id,
                    success=exit_code == 0,
                    output=stdout + stderr,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr=stderr,
                    trace_id=trace_id,
                )
            else:
                stdout, stderr, exit_code, trace_id = _parse_shell_payload(result.error_message)
                effective_exit_code = exit_code if exit_code != 0 else 1
                effective_error = (
                    stderr
                    if stderr
                    else (result.error_message or "Failed to execute command")
                )
                return CommandResult(
                    request_id=result.request_id,
                    success=False,
                    output=stdout + stderr,
                    exit_code=effective_exit_code,
                    stdout=stdout,
                    stderr=stderr,
                    trace_id=trace_id,
                    error_message=effective_error,
                )
        except Exception as e:
            return CommandResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute command: {e}",
            )

    async def run(
        self,
        command: str,
        timeout_ms: int = 50000,
        cwd: Optional[str] = None,
        envs: Optional[Dict[str, str]] = None,
    ) -> CommandResult:
        """
        Alias of execute_command() for better ergonomics and LLM friendliness.
        """
        return await self.execute_command(
            command=command,
            timeout_ms=timeout_ms,
            cwd=cwd,
            envs=envs,
        )

    async def exec(
        self,
        command: str,
        timeout_ms: int = 50000,
        cwd: Optional[str] = None,
        envs: Optional[Dict[str, str]] = None,
    ) -> CommandResult:
        """
        Alias of execute_command() for better ergonomics and LLM friendliness.
        """
        return await self.execute_command(
            command=command,
            timeout_ms=timeout_ms,
            cwd=cwd,
            envs=envs,
        )
