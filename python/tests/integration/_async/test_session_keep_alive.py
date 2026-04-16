"""Integration test for Session.keep_alive (async version).

This test validates that calling keep_alive refreshes the backend idle timer.

Strategy (no mocks, end-to-end):
- Create 2 sessions with the same idle_release_timeout.
- Call keep_alive on one session halfway through.
- Wait until the control session is released.
- Assert the refreshed session is still alive at that moment.

Notes:
- Requires a real AGENTBAY_API_KEY.
- Uses GetSessionDetail polling to observe lifecycle.
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


def _is_terminal_status(status_result) -> bool:
    if not getattr(status_result, "success", False):
        return _is_not_found_status_result(status_result)
    return getattr(status_result, "status", "") in ["FINISH", "DELETING", "DELETED"]


@pytest.mark.asyncio
async def test_keep_alive_resets_idle_timer(agent_bay_client: AsyncAgentBay):
    idle_release_timeout = 30  # seconds
    max_over_seconds = 60  # control session must be released within timeout + 60s
    poll_interval = 15  # seconds
    image_id = "linux_latest"

    print(
        "Creating 2 sessions with "
        f"image_id={image_id}, idle_release_timeout={idle_release_timeout}s"
    )

    control_session = None
    refreshed_session = None

    start_time = time.monotonic()
    try:
        common_labels = {"test": "session-keep-alive", "sdk": "python-async"}

        control_params = CreateSessionParams(
            image_id=image_id,
            idle_release_timeout=idle_release_timeout,
            labels={**common_labels, "role": "control"},
        )
        refreshed_params = CreateSessionParams(
            image_id=image_id,
            idle_release_timeout=idle_release_timeout,
            labels={**common_labels, "role": "refreshed"},
        )

        control_result = await agent_bay_client.create(control_params)
        assert control_result.success, f"Create control session failed: {control_result.error_message}"
        assert control_result.session is not None
        control_session = control_result.session

        refreshed_result = await agent_bay_client.create(refreshed_params)
        assert refreshed_result.success, f"Create refreshed session failed: {refreshed_result.error_message}"
        assert refreshed_result.session is not None
        refreshed_session = refreshed_result.session

        print(f"✅ Control session: {control_session.session_id}")
        print(f"✅ Refreshed session: {refreshed_session.session_id}")

        # Wait until halfway through, then refresh the idle timer for refreshed session.
        await asyncio.sleep(idle_release_timeout / 2)
        keep_alive_result = await refreshed_session.keep_alive()
        assert keep_alive_result.success, f"keep_alive failed: {getattr(keep_alive_result, 'error_message', '')}"

        deadline = start_time + idle_release_timeout + max_over_seconds
        control_released_at = None

        while time.monotonic() < deadline:
            control_status = await control_session.get_status()
            refreshed_status = await refreshed_session.get_status()

            if _is_terminal_status(control_status):
                control_released_at = time.monotonic()
                assert not _is_terminal_status(refreshed_status), (
                    "Refreshed session was released no later than control session; "
                    "keep_alive did not extend idle timer as expected"
                )
                elapsed = control_released_at - start_time
                print(
                    "✅ Control session released while refreshed session still alive, "
                    f"elapsed={elapsed:.2f}s"
                )
                return

            # Check if refreshed session was released before control session (unexpected)
            if _is_terminal_status(refreshed_status):
                pytest.fail(
                    "Refreshed session was released before control session; "
                    "keep_alive may have failed"
                )

            await asyncio.sleep(poll_interval)
    finally:
        # Best-effort cleanup.
        for s in [refreshed_session, control_session]:
            if s is None:
                continue
            try:
                status_final = await s.get_status()
                if not _is_terminal_status(status_final):
                    await agent_bay_client.delete(s)
            except Exception:
                pass
