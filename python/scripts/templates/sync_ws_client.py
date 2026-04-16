from __future__ import annotations

import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Callable, Optional

from ..._common.exceptions import AgentBayError
from ..._async._internal.ws_client import (
    WsClient as _AsyncWsClient,
    WsConnectionState,
    WsStreamHandle as _AsyncWsStreamHandle,
)

PushCallback = Callable[[dict[str, Any]], Any]
OnEvent = Callable[[str, dict[str, Any]], None]
OnEnd = Callable[[str, dict[str, Any]], None]
OnError = Callable[[str, Exception], None]


class WsStreamHandle:
    def __init__(
        self,
        client: "WsClient",
        handle: _AsyncWsStreamHandle,
        *,
        loop: asyncio.AbstractEventLoop,
    ):
        self._client = client
        self._handle = handle
        self._loop = loop

    @property
    def invocation_id(self) -> str:
        return self._handle.invocation_id

    def write(self, data: dict[str, Any]) -> None:
        fut = asyncio.run_coroutine_threadsafe(self._handle.write(data), self._loop)
        fut.result()

    def cancel(self) -> None:
        fut = asyncio.run_coroutine_threadsafe(self._handle.cancel(), self._loop)
        fut.result()

    def wait_end(self) -> dict[str, Any]:
        fut = asyncio.run_coroutine_threadsafe(self._handle.wait_end(), self._loop)
        return fut.result()

    def wait_end_with_timeout(self, timeout: int) -> dict[str, Any]:
        fut = asyncio.run_coroutine_threadsafe(self._handle.wait_end(), self._loop)
        return fut.result(timeout=timeout)


class WsClient:
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

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._thread_started = threading.Event()
        self._thread_error: Optional[BaseException] = None
        self._async_client: Optional[_AsyncWsClient] = None
        self._closed = False

    def _ensure_thread(self) -> None:
        if self._closed:
            raise AgentBayError("WS client is closed")
        if self._thread is not None and self._loop is not None:
            return

        loop = asyncio.new_event_loop()
        self._loop = loop

        def _runner() -> None:
            try:
                asyncio.set_event_loop(loop)
                self._async_client = _AsyncWsClient(
                    ws_url=self._ws_url,
                    ws_token=self._ws_token,
                    heartbeat_interval_s=self._heartbeat_interval_s,
                    reconnect_initial_delay_s=self._reconnect_initial_delay_s,
                    reconnect_max_delay_s=self._reconnect_max_delay_s,
                )
                self._thread_started.set()
                loop.run_forever()
            except BaseException as e:
                self._thread_error = e
                self._thread_started.set()
            finally:
                try:
                    loop.close()
                except Exception:
                    pass

        t = threading.Thread(target=_runner, name="agentbay-ws-loop", daemon=True)
        self._thread = t
        t.start()
        self._thread_started.wait(timeout=10.0)
        if self._thread_error is not None:
            raise AgentBayError(f"Failed to start WS loop thread: {self._thread_error}")
        if self._async_client is None:
            raise AgentBayError("Failed to initialize async WS client")

    def _call_in_loop(self, fn: Callable[[_AsyncWsClient], Any]) -> Any:
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        fut: Future[Any] = Future()

        def _do() -> None:
            try:
                fut.set_result(fn(self._async_client))
            except BaseException as e:
                fut.set_exception(e)

        self._loop.call_soon_threadsafe(_do)
        return fut.result()

    def on_connection_state_change(
        self, listener: Callable[[WsConnectionState, str], None]
    ) -> Callable[[], None]:
        unsubscribe = self._call_in_loop(lambda c: c.on_connection_state_change(listener))

        def _unsub() -> None:
            self._call_in_loop(lambda c: unsubscribe())

        return _unsub

    def connect(self) -> None:
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        f = asyncio.run_coroutine_threadsafe(self._async_client.connect(), self._loop)
        f.result()

    def register_callback(self, target: str, callback: PushCallback) -> Callable[[], None]:
        unsubscribe = self._call_in_loop(lambda c: c.register_callback(target, callback))

        def _unsub() -> None:
            self._call_in_loop(lambda c: unsubscribe())

        return _unsub

    def unregister_callback(self, target: str, callback: Optional[PushCallback] = None) -> None:
        self._call_in_loop(lambda c: c.unregister_callback(target, callback))

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        loop = self._loop
        client = self._async_client
        if loop is None or client is None:
            return
        try:
            f = asyncio.run_coroutine_threadsafe(client.close(), loop)
            f.result(timeout=10.0)
        except Exception:
            pass
        try:
            loop.call_soon_threadsafe(loop.stop)
        except Exception:
            pass

    def call_stream(
        self,
        *,
        target: str,
        data: dict[str, Any],
        on_event: Optional[OnEvent],
        on_end: Optional[OnEnd],
        on_error: Optional[OnError],
    ) -> WsStreamHandle:
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        f = asyncio.run_coroutine_threadsafe(
            self._async_client.call_stream(
                target=target,
                data=data,
                on_event=on_event,
                on_end=on_end,
                on_error=on_error,
            ),
            self._loop,
        )
        async_handle = f.result()
        return WsStreamHandle(self, async_handle, loop=self._loop)

    def call(
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
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        f = asyncio.run_coroutine_threadsafe(
            self._async_client.call(
                target=target,
                data=data,
                timeout=timeout,
            ),
            self._loop,
        )
        return f.result(timeout=timeout + 5.0)

    def send_message(
        self,
        *,
        target: str,
        data: dict[str, Any],
    ) -> None:
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        f = asyncio.run_coroutine_threadsafe(
            self._async_client.send_message(
                target=target,
                data=data,
            ),
            self._loop,
        )
        f.result()

