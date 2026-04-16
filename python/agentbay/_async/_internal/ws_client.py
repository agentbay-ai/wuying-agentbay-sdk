import asyncio
import inspect
import json
import random
import ssl
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from ..._common.exceptions import AgentBayError, WsCancelledError
from ..._common.logger import _mask_sensitive_data_string, _truncate_string_for_log, get_logger

_logger = get_logger("ws_client")


class WsConnectionState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"


class WsProtocolError(AgentBayError):
    """Raised when a WS message violates the expected protocol."""


class WsHandshakeRejectedError(AgentBayError):
    """Raised when backend rejects connection-level handshake."""


class WsConnectionClosedError(AgentBayError):
    """Raised when WS connection is closed while a stream is pending."""


class WsRemoteError(AgentBayError):
    """Raised when backend sends an error for an invocation."""


ConnectionStateListener = Callable[[WsConnectionState, str], None]
OnEvent = Callable[[str, dict[str, Any]], None]
OnEnd = Callable[[str, dict[str, Any]], None]
OnError = Callable[[str, Exception], None]
PushCallback = Callable[[dict[str, Any]], Any]


def _new_invocation_id() -> str:
    return uuid.uuid4().hex


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _extract_invocation_id(msg: dict[str, Any]) -> str:
    invocation_id = msg.get("invocationId") or msg.get("requestId")
    if not isinstance(invocation_id, str) or not invocation_id:
        raise WsProtocolError("invocationId is required and must be a non-empty string")
    return invocation_id


@dataclass
class _PendingStream:
    invocation_id: str
    target: str
    on_event: Optional[OnEvent]
    on_end: Optional[OnEnd]
    on_error: Optional[OnError]
    end_future: asyncio.Future[dict[str, Any]]
    is_call: bool = False


class WsStreamHandle:
    def __init__(self, client: "WsClient", pending: _PendingStream):
        self._client = client
        self._pending = pending

    @property
    def invocation_id(self) -> str:
        return self._pending.invocation_id

    async def write(self, data: dict[str, Any]) -> None:
        await self._client._write_business(  # noqa: SLF001
            invocation_id=self._pending.invocation_id,
            target=self._pending.target,
            data=data,
        )

    async def cancel(self) -> None:
        self._client._cancel_pending(self._pending.invocation_id)  # noqa: SLF001

    async def wait_end(self) -> dict[str, Any]:
        return await asyncio.shield(self._pending.end_future)

    async def wait_end_with_timeout(self, timeout: int) -> dict[str, Any]:
        # Avoid asyncio.wait_for + asyncio.shield combination due to
        # Python 3.10 bug (bpo-45097) where CancelledError can escape
        # instead of being converted to TimeoutError.
        shielded = asyncio.shield(self._pending.end_future)
        done, _ = await asyncio.wait([shielded], timeout=timeout)
        if done:
            return done.pop().result()
        raise TimeoutError()


class WsClient:
    """
    Session-scoped WS client with message routing by invocationId.

    This is an internal SDK module. It intentionally does not interpret business
    semantics beyond minimal validation and routing.
    """

    def __init__(
        self,
        ws_url: str,
        ws_token: str,
        *,
        heartbeat_interval_s: float = 20.0,
        reconnect_initial_delay_s: float = 0.5,
        reconnect_max_delay_s: float = 5.0,
    ):
        self._ws_url = ws_url
        self._ws_token = ws_token

        self._heartbeat_interval_s = heartbeat_interval_s
        self._reconnect_initial_delay_s = reconnect_initial_delay_s
        self._reconnect_max_delay_s = reconnect_max_delay_s

        self._ws: Any = None
        self._recv_task: Optional[asyncio.Task[None]] = None
        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._reconnect_task: Optional[asyncio.Task[None]] = None

        self._connect_lock = asyncio.Lock()
        self._pending_by_id: dict[str, _PendingStream] = {}
        self._state_listeners: list[ConnectionStateListener] = []
        self._callbacks_by_target: dict[str, list[PushCallback]] = {}
        self._state: WsConnectionState = WsConnectionState.CLOSED
        self._closed_explicitly = False

    def on_connection_state_change(self, listener: ConnectionStateListener) -> Callable[[], None]:
        self._state_listeners.append(listener)

        def _unsubscribe() -> None:
            try:
                self._state_listeners.remove(listener)
            except ValueError:
                pass

        return _unsubscribe

    async def connect(self) -> None:
        """
        Establish WS connection.

        Internal helper for SDK modules and end-to-end validation.
        """
        await self._ensure_open()

    def register_callback(self, target: str, callback: PushCallback) -> Callable[[], None]:
        """
        Register a push callback routed by target.

        callback(payload) receives: {"requestId": str, "target": str, "data": dict}
        """
        if not isinstance(target, str) or not target:
            raise ValueError("target must be a non-empty string")
        if not callable(callback):
            raise ValueError("callback must be callable")
        self._callbacks_by_target.setdefault(target, []).append(callback)

        def _unsubscribe() -> None:
            self.unregister_callback(target, callback)

        return _unsubscribe

    def unregister_callback(self, target: str, callback: Optional[PushCallback] = None) -> None:
        """
        Unregister a previously registered callback.

        If callback is None, all callbacks for target will be removed.
        """
        if not isinstance(target, str) or not target:
            raise ValueError("target must be a non-empty string")
        if callback is None:
            self._callbacks_by_target.pop(target, None)
            return
        callbacks = self._callbacks_by_target.get(target)
        if not callbacks:
            return
        self._callbacks_by_target[target] = [cb for cb in callbacks if cb is not callback]
        if not self._callbacks_by_target[target]:
            self._callbacks_by_target.pop(target, None)

    def _set_state(self, state: WsConnectionState, reason: str) -> None:
        self._state = state
        for listener in list(self._state_listeners):
            try:
                listener(state, reason)
            except Exception:
                _logger.exception("ConnectionState listener failed")

    def _log_frame(self, direction: str, payload: dict[str, Any]) -> None:
        try:
            raw = _json_dumps(payload)
        except Exception:
            raw = str(payload)
        masked = _mask_sensitive_data_string(raw)
        truncated = _truncate_string_for_log(masked, 1200)
        _logger.debug(f"WS {direction} {truncated}")

    async def close(self) -> None:
        self._closed_explicitly = True
        if self._reconnect_task is not None:
            self._reconnect_task.cancel()
            self._reconnect_task = None
        await self._close_transport("explicit close")

    async def call_stream(
        self,
        *,
        target: str,
        data: dict[str, Any],
        on_event: Optional[OnEvent],
        on_end: Optional[OnEnd],
        on_error: Optional[OnError],
    ) -> WsStreamHandle:
        if not isinstance(target, str) or not target:
            raise ValueError("target must be a non-empty string")
        if not isinstance(data, dict):
            raise ValueError("data must be a dict")

        await self._ensure_open()

        invocation_id = _new_invocation_id()
        loop = asyncio.get_running_loop()
        end_future: asyncio.Future[dict[str, Any]] = loop.create_future()
        pending = _PendingStream(
            invocation_id=invocation_id,
            target=target,
            on_event=on_event,
            on_end=on_end,
            on_error=on_error,
            end_future=end_future,
        )
        self._pending_by_id[invocation_id] = pending

        try:
            await self._write_business(
                invocation_id=invocation_id,
                target=target,
                data=data,
            )
        except Exception as e:
            self._pending_by_id.pop(invocation_id, None)
            if not end_future.done():
                end_future.set_exception(e)
            if on_error is not None:
                on_error(invocation_id, e)
            raise

        return WsStreamHandle(self, pending)

    async def call(
        self,
        *,
        target: str,
        data: dict[str, Any],
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """
        Send a request and wait for a single response (no phase semantics).

        Returns the response data dict. Check data["result"] for the result.
        """
        if not isinstance(target, str) or not target:
            raise ValueError("target must be a non-empty string")
        if not isinstance(data, dict):
            raise ValueError("data must be a dict")

        await self._ensure_open()

        invocation_id = _new_invocation_id()
        loop = asyncio.get_running_loop()
        end_future: asyncio.Future[dict[str, Any]] = loop.create_future()
        pending = _PendingStream(
            invocation_id=invocation_id,
            target=target,
            on_event=None,
            on_end=None,
            on_error=None,
            end_future=end_future,
            is_call=True,
        )
        self._pending_by_id[invocation_id] = pending

        try:
            await self._write_business(
                invocation_id=invocation_id,
                target=target,
                data=data,
            )
        except Exception as e:
            self._pending_by_id.pop(invocation_id, None)
            if not end_future.done():
                end_future.set_exception(e)
            raise

        return await asyncio.wait_for(asyncio.shield(end_future), timeout=timeout)

    async def send_message(
        self,
        *,
        target: str,
        data: dict[str, Any],
    ) -> None:
        await self._ensure_open()

        try:
            invocation_id = _new_invocation_id()
            await self._write_business(
                invocation_id=invocation_id,
                target=target,
                data=data,
            )
        except Exception as e:
            _logger.warning(f"Failed to send message: {e}")

    async def _ensure_open(self) -> None:
        async with self._connect_lock:
            if self._ws is not None and self._recv_task is not None:
                return
            await self._open()

    async def _open(self) -> None:
        if self._closed_explicitly:
            raise WsConnectionClosedError("WS client is closed")

        try:
            import websockets
            from websockets.exceptions import InvalidStatus
        except Exception as e:
            raise AgentBayError(
                "Missing dependency: install 'websockets' to use WS features"
            ) from e

        self._set_state(WsConnectionState.RECONNECTING, "connecting")
        _logger.info(f"WS CONNECT url={self._ws_url}")
        headers = {"X-Access-Token": self._ws_token}

        # Build an SSL context with certifi CA bundle to avoid
        # SSLCertVerificationError on macOS where the default Python
        # installation (python.org) ships without system CA certificates.
        ssl_context: Any = None
        if self._ws_url.startswith("wss://"):
            ssl_context = ssl.create_default_context()
            try:
                import certifi
                ssl_context.load_verify_locations(certifi.where())
            except ImportError:
                _logger.debug(
                    "certifi not available; falling back to system CA certificates"
                )

        try:
            ws = await websockets.connect(
                self._ws_url,
                ping_interval=None,
                additional_headers=headers,
                ssl=ssl_context,
            )
        except InvalidStatus as e:
            raise WsHandshakeRejectedError(
                f"WS connection rejected: HTTP {e.response.status_code}; "
                f"url={self._ws_url}"
            ) from e
        self._ws = ws
        self._set_state(WsConnectionState.OPEN, "connected")
        _logger.info(f"WS CONNECTED url={self._ws_url}")
        self._recv_task = asyncio.create_task(self._recv_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _close_transport(self, reason: str) -> None:
        try:
            current = asyncio.current_task()
        except RuntimeError:
            current = None
        ws = self._ws
        self._ws = None

        if self._recv_task is not None:
            if self._recv_task is not current:
                self._recv_task.cancel()
            self._recv_task = None
        if self._heartbeat_task is not None:
            if self._heartbeat_task is not current:
                self._heartbeat_task.cancel()
            self._heartbeat_task = None

        if ws is not None:
            try:
                await ws.close()
            except Exception:
                pass

        _logger.info(f"WS CLOSED reason={reason}")
        self._set_state(WsConnectionState.CLOSED, reason)

    async def _heartbeat_loop(self) -> None:
        while True:
            await asyncio.sleep(self._heartbeat_interval_s)
            ws = self._ws
            if ws is None:
                continue
            try:
                pong_waiter = await ws.ping()
                await asyncio.wait_for(pong_waiter, timeout=self._heartbeat_interval_s)
            except Exception as e:
                await self._on_transport_error(f"heartbeat failed: {e}")
                return

    async def _recv_loop(self) -> None:
        ws = self._ws
        if ws is None:
            return
        try:
            async for raw in ws:
                try:
                    self._handle_incoming(raw)
                except WsProtocolError as e:
                    raw_str = _truncate_string_for_log(
                        _mask_sensitive_data_string(str(raw)), 2000
                    )
                    _logger.warning(f"WS protocol error (ignored): {e}; raw={raw_str}")
                    try:
                        msg_any = json.loads(raw)
                        if isinstance(msg_any, dict):
                            invocation_id = None
                            try:
                                invocation_id = _extract_invocation_id(msg_any)
                            except Exception:
                                invocation_id = None
                            if invocation_id:
                                pending = self._pending_by_id.pop(invocation_id, None)
                                if pending is not None:
                                    if pending.on_error is not None:
                                        try:
                                            pending.on_error(invocation_id, e)
                                        except Exception:
                                            _logger.exception("on_error callback failed")
                                    if not pending.end_future.done():
                                        pending.end_future.set_exception(e)
                    except Exception:
                        pass
                    continue
            await self._on_transport_error("connection closed")
        except Exception as e:
            await self._on_transport_error(f"recv loop closed: {e}")

    def _handle_incoming(self, raw: Any) -> None:
        try:
            msg = json.loads(raw)
        except Exception as e:
            raise WsProtocolError(f"Invalid JSON message: {e}") from e

        if not isinstance(msg, dict):
            raise WsProtocolError("Message must be a JSON object")

        invocation_id = _extract_invocation_id(msg)
        source = msg.get("source")
        pending = self._pending_by_id.get(invocation_id)

        # Special parsing: messages from WebSocket server control plane.
        # If an error is present, surface it to the caller directly without
        # depending on streaming `phase` semantics.
        if source == "WEBSOCKET_SERVER" and pending is not None:
            data_any = msg.get("data")
            error_msg = None
            if isinstance(msg.get("error"), str) and msg.get("error"):
                error_msg = msg.get("error")
            if error_msg is None and isinstance(data_any, dict):
                if isinstance(data_any.get("error"), str) and data_any.get("error"):
                    error_msg = data_any.get("error")
            self._log_frame("<<", {"invocationId": invocation_id, "source": source, "data": data_any})
            if error_msg is not None:
                err = WsRemoteError(_truncate_string_for_log(_mask_sensitive_data_string(error_msg), 2000))
                if pending.on_error is not None:
                    pending.on_error(invocation_id, err)
                if not pending.end_future.done():
                    pending.end_future.set_exception(err)
                self._pending_by_id.pop(invocation_id, None)
                return
            # No explicit error: treat as end/control completion.
            if pending.on_end is not None:
                pending.on_end(invocation_id, data_any if isinstance(data_any, dict) else {})
            if not pending.end_future.done():
                pending.end_future.set_result(data_any if isinstance(data_any, dict) else {})
            self._pending_by_id.pop(invocation_id, None)
            return

        target = msg.get("target")
        data_any = msg.get("data")
        if not isinstance(target, str) or not target:
            raise WsProtocolError("target is required and must be a non-empty string")
        if isinstance(data_any, dict):
            data = data_any
        elif isinstance(data_any, str):
            try:
                parsed = json.loads(data_any)
            except Exception as e:
                raise WsProtocolError(f"data is a string but not valid JSON: {e}") from e
            if not isinstance(parsed, dict):
                raise WsProtocolError("data is a string but decoded JSON is not an object")
            _logger.warning(
                "WS protocol violation: backend sent data as string; decoded to object"
            )
            data = parsed
        else:
            raise WsProtocolError("data is required and must be an object")

        self._log_frame(
            "<<",
            {"invocationId": invocation_id, "source": source, "target": target, "data": data},
        )

        if pending is None:
            route_target = target
            if (
                route_target == "SDK"
                and isinstance(source, str)
                and source
                and source != "SDK"
            ):
                route_target = source
            callbacks = list(self._callbacks_by_target.get(route_target, []))
            if not callbacks:
                _logger.debug(
                    f"Dropping push message with no callback: requestId={invocation_id}, target={route_target}"
                )
                return
            payload = {"requestId": invocation_id, "target": route_target, "data": data}
            for cb in callbacks:
                try:
                    r = cb(payload)
                    if inspect.isawaitable(r):
                        asyncio.create_task(r)
                except Exception:
                    _logger.exception("Push callback failed")
            return

        # Fast-path: any explicit error should be returned to caller.
        if isinstance(data.get("error"), str) and data.get("error"):
            err = WsRemoteError(
                _truncate_string_for_log(_mask_sensitive_data_string(str(data)), 2000)
            )
            if pending.on_error is not None:
                pending.on_error(invocation_id, err)
            if not pending.end_future.done():
                pending.end_future.set_exception(err)
            self._pending_by_id.pop(invocation_id, None)
            return

        if pending.is_call:
            result = data.get("result")
            if result is not None:
                if pending.on_end is not None:
                    pending.on_end(invocation_id, data)
                if not pending.end_future.done():
                    pending.end_future.set_result(data)
                self._pending_by_id.pop(invocation_id, None)
                return
            error = data.get("error")
            if error is not None:
                err = WsRemoteError(
                    _truncate_string_for_log(_mask_sensitive_data_string(str(error)), 2000)
                )
                if pending.on_error is not None:
                    pending.on_error(invocation_id, err)
                if not pending.end_future.done():
                    pending.end_future.set_exception(err)
                self._pending_by_id.pop(invocation_id, None)
                return
            if not pending.end_future.done():
                pending.end_future.set_result(data)
            self._pending_by_id.pop(invocation_id, None)
            return

        phase = data.get("phase")
        if phase == "event":
            if pending.on_event is not None:
                pending.on_event(invocation_id, data)
            return
        if phase == "end":
            if pending.on_end is not None:
                pending.on_end(invocation_id, data)
            if not pending.end_future.done():
                pending.end_future.set_result(data)
            self._pending_by_id.pop(invocation_id, None)
            return

        if phase == "error":
            err = WsRemoteError(_truncate_string_for_log(_mask_sensitive_data_string(str(data)), 2000))
            if pending.on_error is not None:
                pending.on_error(invocation_id, err)
            if not pending.end_future.done():
                pending.end_future.set_exception(err)
            self._pending_by_id.pop(invocation_id, None)
            return

        if phase is None:
            err = WsProtocolError(
                "WS message missing required data.phase; "
                f"invocationId={invocation_id}, data={_truncate_string_for_log(_mask_sensitive_data_string(str(data)), 2000)}"
            )
        else:
            err = WsProtocolError(
                "WS message has unsupported data.phase; "
                f"invocationId={invocation_id}, phase={phase!r}, data={_truncate_string_for_log(_mask_sensitive_data_string(str(data)), 2000)}"
            )
        if pending.on_error is not None:
            pending.on_error(invocation_id, err)
        if not pending.end_future.done():
            pending.end_future.set_exception(err)
        self._pending_by_id.pop(invocation_id, None)
        return

    async def _on_transport_error(self, reason: str) -> None:
        if self._closed_explicitly:
            await self._close_transport(reason)
            return

        _logger.warning(f"WS transport error: {reason}")
        await self._close_transport(reason)
        self._fail_all_pending(WsConnectionClosedError(reason))

        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect_loop())

    def _fail_all_pending(self, err: Exception) -> None:
        pending_items = list(self._pending_by_id.items())
        self._pending_by_id.clear()
        for invocation_id, pending in pending_items:
            if pending.on_error is not None:
                try:
                    pending.on_error(invocation_id, err)
                except Exception:
                    _logger.exception("on_error callback failed")
            if not pending.end_future.done():
                pending.end_future.set_exception(err)

    async def _reconnect_loop(self) -> None:
        delay = self._reconnect_initial_delay_s
        while not self._closed_explicitly:
            try:
                await asyncio.sleep(delay + random.random() * 0.1)
                async with self._connect_lock:
                    if self._ws is not None and self._recv_task is not None:
                        return
                    await self._open()
                return
            except Exception as e:
                self._set_state(WsConnectionState.RECONNECTING, f"reconnect failed: {e}")
                delay = min(delay * 1.5, self._reconnect_max_delay_s)
                continue

    async def _write_business(
        self,
        *,
        invocation_id: str,
        target: str,
        data: dict[str, Any],
    ) -> None:
        ws = self._ws
        if ws is None:
            raise WsConnectionClosedError("WS is not connected")
        payload = {
            "invocationId": invocation_id,
            "source": "SDK",
            "target": target,
            "data": data,
        }
        self._log_frame(">>", payload)
        await ws.send(_json_dumps(payload))

    def _cancel_pending(self, invocation_id: str) -> None:
        pending = self._pending_by_id.pop(invocation_id, None)
        if pending is None:
            return
        if pending.end_future.done():
            return
        err = WsCancelledError(f"Stream {invocation_id} was cancelled by caller")
        if pending.on_error is not None:
            try:
                pending.on_error(invocation_id, err)
            except Exception:
                _logger.exception("on_error callback failed during cancel")
        pending.end_future.set_exception(err)

