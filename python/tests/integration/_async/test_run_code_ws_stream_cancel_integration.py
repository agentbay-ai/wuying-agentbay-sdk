# ci-stable
# -*- coding: utf-8 -*-
"""Integration tests for run_code WebSocket stream cancellation."""

import asyncio
import time

import pytest

from agentbay import CreateSessionParams
from agentbay._common.exceptions import WsCancelledError


@pytest.mark.integration
@pytest.mark.asyncio
async def test_run_code_ws_stream_cancel_e2e(make_session):
    lc = await make_session()
    session = lc._result.session

    ws_client = None
    try:
        assert session.ws_url, "Backend did not return wsUrl/WsUrl in CreateSession response"

        ws_client = await session._get_ws_client()
        await ws_client.connect()

        target = "wuying_codespace"
        for tool in getattr(session, "mcpTools", []) or []:
            try:
                if getattr(tool, "name", "") == "run_code" and getattr(tool, "server", ""):
                    target = tool.server
                    break
            except Exception:
                continue

        events: list[dict] = []
        ends: list[dict] = []
        errors: list[Exception] = []

        def on_event(invocation_id: str, data: dict) -> None:
            assert invocation_id
            assert isinstance(data, dict)
            events.append(data)

        def on_end(invocation_id: str, data: dict) -> None:
            assert invocation_id
            assert isinstance(data, dict)
            ends.append(data)

        def on_error(invocation_id: str, err: Exception) -> None:
            assert invocation_id
            assert isinstance(err, Exception)
            errors.append(err)

        handle = await ws_client.call_stream(
            target=target,
            data={
                "method": "run_code",
                "mode": "stream",
                "params": {
                    "language": "python",
                    "timeoutS": 60,
                    "code": "import time\n"
                    "print(0, flush=True)\n"
                    "time.sleep(10)\n"
                    "print(1, flush=True)\n",
                },
            },
            on_event=on_event,
            on_end=on_end,
            on_error=on_error,
        )

        await asyncio.sleep(0.5)
        await handle.cancel()

        t0 = time.monotonic()
        with pytest.raises(WsCancelledError):
            await asyncio.wait_for(handle.wait_end(), timeout=2)
        assert time.monotonic() - t0 < 2.0

        assert ends == [], f"unexpected on_end after cancel: ends={ends}, events={events}, errors={errors}"
        assert len(errors) == 1, f"expected exactly 1 on_error, got errors={errors}"
        assert isinstance(errors[0], WsCancelledError), f"expected WsCancelledError, got {errors[0]!r}"
    finally:
        if ws_client is not None:
            try:
                await ws_client.close()
            except Exception:
                pass

