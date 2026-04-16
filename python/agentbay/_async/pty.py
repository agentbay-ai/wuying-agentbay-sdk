import asyncio
import base64
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from .._common.exceptions import PtyError, PtyNotConnectedError

logger = logging.getLogger(__name__)

PTY_TARGET = "PTY_SERVER"

DEFAULT_ENVS = {
    "TERM": "xterm-256color",
    "LANG": "en_US.UTF-8",
}

MAX_TERMINAL_SIZE = 500


@dataclass
class PtySession:
    """Read-only snapshot of a PTY session."""

    pty_session_id: str
    cols: int
    rows: int
    status: str
    exit_code: Optional[int] = None


class PtyHandle:
    """Active connection to a PTY session."""

    def __init__(
        self,
        pty_session_id: str,
        pty_module: "AsyncPty",
        on_data: Optional[Callable[[bytes], None]] = None,
    ):
        self._pty_session_id = pty_session_id
        self._pty_module = pty_module
        self._on_data = on_data
        self._connected = True
        self._exit_code: Optional[int] = None
        self._error_msg: Optional[str] = None

    @property
    def pty_session_id(self) -> str:
        return self._pty_session_id

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def exit_code(self) -> Optional[int]:
        return self._exit_code

    async def send_input(self, data: bytes) -> None:
        """Send input bytes to the PTY."""
        if not self._connected:
            raise PtyNotConnectedError()
        try:
            text = data.decode("utf-8")
            encoding = "utf8"
        except UnicodeDecodeError:
            text = base64.b64encode(data).decode("ascii")
            encoding = "base64"
        ws_client = await self._pty_module._get_ws_client()
        await ws_client.send_message(
            target=PTY_TARGET,
            data={
                "method": "pty.input",
                "params": {
                    "ptySessionId": self._pty_session_id,
                    "encoding": encoding,
                    "data": text,
                },
            },
        )

    async def resize(self, cols: int, rows: int) -> None:
        """Resize the terminal."""
        if not self._connected:
            raise PtyNotConnectedError()
        if not (0 < cols <= MAX_TERMINAL_SIZE and 0 < rows <= MAX_TERMINAL_SIZE):
            raise PtyError(
                f"Invalid terminal size: cols={cols}, rows={rows} "
                f"(must be 1-{MAX_TERMINAL_SIZE})"
            )
        ws_client = await self._pty_module._get_ws_client()
        await ws_client.send_message(
            target=PTY_TARGET,
            data={
                "method": "pty.resize",
                "params": {
                    "ptySessionId": self._pty_session_id,
                    "cols": cols,
                    "rows": rows,
                },
            },
        )

    async def kill(self) -> None:
        """Kill the PTY process (SIGKILL)."""
        if not self._connected:
            raise PtyNotConnectedError()
        ws_client = await self._pty_module._get_ws_client()
        await ws_client.call(
            target=PTY_TARGET,
            data={
                "method": "pty.kill",
                "params": {"ptySessionId": self._pty_session_id},
            },
        )

    async def wait(self, timeout_s: Optional[float] = None) -> int:
        """Wait for the PTY process to exit. Returns the exit code."""
        deadline = None
        if timeout_s is not None:
            deadline = time.monotonic() + timeout_s
        while self._exit_code is None and self._error_msg is None:
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError(f"PTY wait timed out after {timeout_s}s")
            await asyncio.sleep(0.1)
        if self._error_msg is not None:
            raise PtyError(self._error_msg)
        return self._exit_code

    def disconnect(self) -> None:
        """Disconnect from the PTY (local only, process continues on server)."""
        if not self._connected:
            return
        self._connected = False
        self._pty_module._unregister_handle(self._pty_session_id)

    def _on_output(self, data_bytes: bytes) -> None:
        if self._on_data is not None:
            try:
                self._on_data(data_bytes)
            except Exception:
                logger.exception("on_data callback raised an exception")

    def _on_exit(self, exit_code: int) -> None:
        self._exit_code = exit_code
        self._connected = False

    def _on_error(self, error_msg: str) -> None:
        self._error_msg = error_msg
        self._connected = False


class AsyncPty:
    """PTY module entry point, accessed as session.pty."""

    def __init__(self, session):
        self._session = session
        self._ws_client = None
        self._handles: Dict[str, PtyHandle] = {}
        self._callback_registered = False

    async def _get_ws_client(self):
        if self._ws_client is None:
            self._ws_client = await self._session._get_ws_client()
        return self._ws_client

    async def _ensure_callback(self) -> None:
        if self._callback_registered:
            return
        ws_client = await self._get_ws_client()
        await ws_client.connect()
        ws_client.register_callback(PTY_TARGET, self._push_callback)
        self._callback_registered = True

    def _push_callback(self, payload: dict) -> None:
        data = payload.get("data", {})
        event_type = data.get("eventType", "")
        pty_session_id = data.get("ptySessionId", "")

        if event_type == "pty.output":
            handle = self._handles.get(pty_session_id)
            if handle is None:
                return
            encoding = data.get("encoding", "utf8")
            raw = data.get("data", "")
            if encoding == "base64":
                data_bytes = base64.b64decode(raw)
            else:
                data_bytes = raw.encode("utf-8") if isinstance(raw, str) else raw
            handle._on_output(data_bytes)
        elif event_type == "pty.exit":
            handle = self._handles.get(pty_session_id)
            if handle is None:
                return
            exit_code = data.get("exitCode", -1)
            handle._on_exit(exit_code)
        elif event_type == "pty.error":
            handle = self._handles.get(pty_session_id)
            if handle is None:
                return
            error_msg = data.get("error", "Unknown PTY error")
            handle._on_error(error_msg)

    def _unregister_handle(self, pty_session_id: str) -> None:
        self._handles.pop(pty_session_id, None)

    async def create(
        self,
        cols: int = 80,
        rows: int = 24,
        cwd: Optional[str] = None,
        envs: Optional[Dict[str, str]] = None,
        shell: Optional[str] = None,
        on_data: Optional[Callable[[bytes], None]] = None,
        timeout_s: Optional[float] = None,
    ) -> PtyHandle:
        """Create a new PTY session and return a PtyHandle."""
        if not (0 < cols <= MAX_TERMINAL_SIZE and 0 < rows <= MAX_TERMINAL_SIZE):
            raise PtyError(
                f"Invalid terminal size: cols={cols}, rows={rows} "
                f"(must be 1-{MAX_TERMINAL_SIZE})"
            )

        await self._ensure_callback()
        ws_client = await self._get_ws_client()

        params: Dict[str, Any] = {"cols": cols, "rows": rows}
        if cwd is not None:
            params["cwd"] = cwd
        merged_envs = dict(DEFAULT_ENVS)
        if envs:
            merged_envs.update(envs)
        params["envs"] = merged_envs
        if shell is not None:
            params["shell"] = shell

        timeout = timeout_s if timeout_s is not None else 30.0
        response = await ws_client.call(
            target=PTY_TARGET,
            data={"method": "pty.create", "params": params},
            timeout=timeout,
        )

        result = response.get("result", {})
        pty_session_id = result.get("ptySessionId")
        if not pty_session_id:
            raise PtyError(f"pty.create did not return ptySessionId: {response}")

        handle = PtyHandle(pty_session_id, self, on_data=on_data)
        self._handles[pty_session_id] = handle
        return handle

    async def list(self) -> List[PtySession]:
        """List all active PTY sessions."""
        await self._ensure_callback()
        ws_client = await self._get_ws_client()

        response = await ws_client.call(
            target=PTY_TARGET,
            data={"method": "pty.list", "params": {}},
        )

        result = response.get("result", {})
        sessions = []
        for sid in result.get("ptySessionIds", []):
            handle = self._handles.get(sid)
            status = "running"
            exit_code = None
            if handle and handle.exit_code is not None:
                status = "exited"
                exit_code = handle.exit_code
            sessions.append(PtySession(
                pty_session_id=sid,
                cols=0,
                rows=0,
                status=status,
                exit_code=exit_code,
            ))
        return sessions

    async def connect(
        self,
        pty_session_id: str,
        on_data: Optional[Callable[[bytes], None]] = None,
    ) -> PtyHandle:
        """Connect to an existing PTY session."""
        await self._ensure_callback()
        ws_client = await self._get_ws_client()

        response = await ws_client.call(
            target=PTY_TARGET,
            data={
                "method": "pty.connect",
                "params": {"ptySessionId": pty_session_id},
            },
        )

        result = response.get("result", {})
        returned_id = result.get("ptySessionId", pty_session_id)

        handle = PtyHandle(returned_id, self, on_data=on_data)
        self._handles[returned_id] = handle
        return handle

    async def kill(self, pty_session_id: str) -> None:
        """Kill a PTY session by ID."""
        await self._ensure_callback()
        ws_client = await self._get_ws_client()

        await ws_client.call(
            target=PTY_TARGET,
            data={
                "method": "pty.kill",
                "params": {"ptySessionId": pty_session_id},
            },
        )

        handle = self._handles.pop(pty_session_id, None)
        if handle is not None:
            handle._connected = False
