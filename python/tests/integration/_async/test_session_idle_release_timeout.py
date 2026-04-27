"""Integration test for SDK idle release timeout (async version).

This test validates that a session created with `idle_release_timeout` will be
automatically released after being idle for long enough.

Notes:
- This is an end-to-end integration test and requires a real AGENTBAY_API_KEY.
- It uses `session.get_status()` to observe the session lifecycle.
"""

import asyncio
import time

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams


def _mask_secret(secret: str, visible: int = 4) -> str:
    """Mask a secret value, keeping only the last `visible` characters."""
    if not secret:
        return ""
    if len(secret) <= visible:
        return "*" * len(secret)
    return ("*" * (len(secret) - visible)) + secret[-visible:]


def _is_not_found_status_result(status_result) -> bool:
    """Return True if get_status result indicates session is gone."""
    if getattr(status_result, "success", False):
        return False
    error_message = (getattr(status_result, "error_message", "") or "").lower()
    code = (getattr(status_result, "code", "") or "").lower()
    return ("notfound" in code) or ("not found" in error_message)


@pytest.mark.asyncio
async def test_session_releases_after_idle_timeout(agent_bay_client: AsyncAgentBay):
    """Verify that a session with idle_release_timeout is released automatically.

    We only call `get_status()` periodically without running any MCP tools or user
    interactions, so the environment is considered idle from the SDK side.
    """
    idle_release_timeout = 60  # seconds
    max_over_seconds = 60  # must not exceed timeout + 60s
    poll_interval = 2  # seconds
    image_id = "linux_latest"

    print("api_key =", _mask_secret(getattr(agent_bay_client, "_api_key", "") or ""))
    print(
        f"Creating session with image_id={image_id}, idle_release_timeout={idle_release_timeout}s"
    )

    session = None
    start_time = time.monotonic()
    try:
        params = CreateSessionParams(
            image_id=image_id,
            idle_release_timeout=idle_release_timeout,
            labels={
                "test": "idle-release-timeout",
                "sdk": "python-async",
            },
        )
        result = await agent_bay_client.create(params)
        assert result.success, f"Create session failed: {result.error_message}"
        assert result.session is not None, "Session should not be None"
        session = result.session
        print(f"Session created: {session.session_id}")

        timeout_deadline = start_time + idle_release_timeout
        while True:
            now = time.monotonic()
            if now >= timeout_deadline:
                break
            status = await session.get_status()
            if _is_not_found_status_result(status):
                pytest.fail(
                    "Session was released too early: got NotFound before "
                    f"{idle_release_timeout}s"
                )
            if status.success and status.status in ["FINISH", "DELETING", "DELETED"]:
                pytest.fail(
                    "Session was released too early: status="
                    f"{status.status} before {idle_release_timeout}s"
                )
            remaining = timeout_deadline - now
            await asyncio.sleep(min(poll_interval, max(0.0, remaining)))

        deadline = timeout_deadline + max_over_seconds
        last_status = None
        while time.monotonic() < deadline:
            status = await session.get_status()
            last_status = status

            if _is_not_found_status_result(status):
                elapsed = time.monotonic() - start_time
                assert elapsed >= idle_release_timeout, "Session was released too early"
                assert elapsed <= idle_release_timeout + max_over_seconds, "Session was released too late"
                print(
                    f"Session released: get_status returned NotFound, elapsed={elapsed:.2f}s"
                )
                return

            if status.success and status.status in ["FINISH", "DELETING", "DELETED"]:
                elapsed = time.monotonic() - start_time
                assert elapsed >= idle_release_timeout, "Session was released too early"
                assert elapsed <= idle_release_timeout + max_over_seconds, "Session was released too late"
                print(f"Session released: status={status.status}, elapsed={elapsed:.2f}s")
                return

            await asyncio.sleep(poll_interval)

        details = ""
        if last_status is not None:
            details = (
                f"last_success={getattr(last_status, 'success', False)}, "
                f"last_status={getattr(last_status, 'status', '')}, "
                f"last_error={getattr(last_status, 'error_message', '')}"
            )
        pytest.fail(
            "Session was not released within expected time window: "
            f"{idle_release_timeout}s~{idle_release_timeout + max_over_seconds}s. {details}"
        )
    finally:
        if session is not None:
            try:
                status_final = await session.get_status()
                if not _is_not_found_status_result(status_final) and not (
                    status_final.success
                    and status_final.status in ["FINISH", "DELETING", "DELETED"]
                ):
                    print("Cleaning up: deleting session explicitly...")
                    await agent_bay_client.delete(session)
            except Exception:
                pass
