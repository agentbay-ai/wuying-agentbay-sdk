import asyncio
import os
import random
import tempfile
import time

import pytest
import httpx

from agentbay import AsyncAgentBay, Context, ContextSync, CreateSessionParams, SyncPolicy


def _generate_unique_id() -> str:
    timestamp = int(time.time() * 1000000) + random.randint(0, 999)
    random_part = random.randint(0, 9999)
    return f"{timestamp}-{random_part}"


def _create_temp_file(size_mb: int) -> str:
    chunk = b"\0" * (1024 * 1024)
    with tempfile.NamedTemporaryFile(delete=False) as f:
        for _ in range(size_mb):
            f.write(chunk)
        return f.name


async def _upload_file_with_retries(
    upload_url: str,
    local_path: str,
    max_attempts: int = 5,
) -> None:
    timeout = httpx.Timeout(300.0, connect=30.0)
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                with open(local_path, "rb") as f:
                    resp = client.put(upload_url, content=f)
            if resp.status_code not in (200, 204):
                raise RuntimeError(
                    f"Upload failed: status={resp.status_code}, body={resp.text[:200]}"
                )
            return
        except Exception as e:
            last_error = e
            if attempt >= max_attempts:
                break
            await asyncio.sleep(min(2.0**attempt, 10.0))
    raise RuntimeError(f"Upload failed after {max_attempts} attempts: {last_error}") from last_error


async def _upload_large_file_to_context(
    agent_bay: AsyncAgentBay,
    context_id: str,
    context_file_path: str,
    size_mb: int,
) -> None:
    url_result = await agent_bay.context.get_file_upload_url(context_id, context_file_path)
    assert url_result.success, f"Failed to get upload URL: {url_result.error_message}"
    assert url_result.url, "Upload URL should be non-empty"
    local_path = _create_temp_file(size_mb=size_mb)
    try:
        await _upload_file_with_retries(url_result.url, local_path)
    finally:
        try:
            os.unlink(local_path)
        except Exception:
            pass


async def _assert_context_download_terminal_success(session, context_id: str, label: str) -> None:
    info = await session.context.info(context_id=context_id, task_type="download")
    assert info.success, f"{label}: failed to get context info: {info.error_message}"
    statuses = [it.status for it in info.context_status_data if it.context_id == context_id]
    assert statuses, f"{label}: expected at least one download status entry"
    assert all(s in ["Success", "Failed"] for s in statuses), f"{label}: non-terminal statuses={statuses}"
    assert "Failed" not in statuses, f"{label}: download failed statuses={statuses}"


async def _wait_context_download_terminal_success(session, context_id: str, timeout_s: int = 240) -> None:
    deadline = time.monotonic() + timeout_s
    last_statuses: list[str] = []
    while time.monotonic() < deadline:
        info = await session.context.info(context_id=context_id, task_type="download")
        assert info.success, f"Polling: failed to get context info: {info.error_message}"
        statuses = [it.status for it in info.context_status_data if it.context_id == context_id]
        if statuses:
            last_statuses = statuses
        if statuses and all(s in ["Success", "Failed"] for s in statuses):
            assert "Failed" not in statuses, f"Download failed statuses={statuses}"
            return
        await asyncio.sleep(2.0)
    raise AssertionError(
        f"Context download did not reach terminal state within {timeout_s}s. last_statuses={last_statuses}"
    )


@pytest.mark.asyncio
async def test_create_session_beta_wait_for_completion_flag(agent_bay_client: AsyncAgentBay):
    agent_bay = agent_bay_client
    unique_id = _generate_unique_id()
    context_name_1 = f"test-beta-wait-flag-1-{unique_id}"
    context_name_2 = f"test-beta-wait-flag-2-{unique_id}"
    ctx1_result = await agent_bay.context.create(context_name_1)
    ctx2_result = await agent_bay.context.create(context_name_2)
    assert ctx1_result.success, f"Failed to create context1: {ctx1_result.error_message}"
    assert ctx2_result.success, f"Failed to create context2: {ctx2_result.error_message}"

    context_id_1 = ctx1_result.context_id
    context_id_2 = ctx2_result.context_id

    session_wait_both = None
    session_wait_one = None
    session_wait_none = None

    try:
        mount_path_1 = "/tmp/beta-wait-flag-1"
        mount_path_2 = "/tmp/beta-wait-flag-2"
        image_id = "linux_latest"
        await _upload_large_file_to_context(
            agent_bay,
            context_id_1,
            context_file_path=f"{mount_path_1}/large.bin",
            size_mb=200,
        )
        await _upload_large_file_to_context(
            agent_bay,
            context_id_2,
            context_file_path=f"{mount_path_2}/large.bin",
            size_mb=200,
        )

        wait_both_syncs = [
            ContextSync.new(context_id_1, mount_path_1, SyncPolicy.default()),
            ContextSync.new(context_id_2, mount_path_2, SyncPolicy.default()),
        ]
        wait_both_params = CreateSessionParams(
            image_id=image_id,
            labels={"test": "beta-wait-flag", "mode": "wait-both"},
            context_syncs=wait_both_syncs,
        )

        t0 = time.monotonic()
        wait_both_result = await agent_bay.create(wait_both_params)
        t_wait_both = time.monotonic() - t0
        assert wait_both_result.success, f"Create session (wait-both) failed: {wait_both_result.error_message}"
        assert wait_both_result.session is not None
        session_wait_both = wait_both_result.session
        await _assert_context_download_terminal_success(session_wait_both, context_id_1, "wait-both ctx1")
        await _assert_context_download_terminal_success(session_wait_both, context_id_2, "wait-both ctx2")

        wait_one_syncs = [
            ContextSync.new(context_id_1, mount_path_1, SyncPolicy.default()),
            ContextSync.new(
                context_id_2,
                mount_path_2,
                SyncPolicy.default(),
                beta_wait_for_completion=False,
            ),
        ]
        wait_one_params = CreateSessionParams(
            image_id=image_id,
            labels={"test": "beta-wait-flag", "mode": "wait-one"},
            context_syncs=wait_one_syncs,
        )

        t1 = time.monotonic()
        wait_one_result = await agent_bay.create(wait_one_params)
        t_wait_one = time.monotonic() - t1
        assert wait_one_result.success, f"Create session (wait-one) failed: {wait_one_result.error_message}"
        assert wait_one_result.session is not None
        session_wait_one = wait_one_result.session
        await _assert_context_download_terminal_success(session_wait_one, context_id_1, "wait-one ctx1")
        await _wait_context_download_terminal_success(session_wait_one, context_id_2, timeout_s=240)

        wait_none_syncs = [
            ContextSync.new(
                context_id_1,
                mount_path_1,
                SyncPolicy.default(),
                beta_wait_for_completion=False,
            ),
            ContextSync.new(
                context_id_2,
                mount_path_2,
                SyncPolicy.default(),
                beta_wait_for_completion=False,
            ),
        ]
        wait_none_params = CreateSessionParams(
            image_id=image_id,
            labels={"test": "beta-wait-flag", "mode": "wait-none"},
            context_syncs=wait_none_syncs,
        )

        t2 = time.monotonic()
        wait_none_result = await agent_bay.create(wait_none_params)
        t_wait_none = time.monotonic() - t2
        assert wait_none_result.success, f"Create session (wait-none) failed: {wait_none_result.error_message}"
        assert wait_none_result.session is not None
        session_wait_none = wait_none_result.session
        await _wait_context_download_terminal_success(session_wait_none, context_id_1, timeout_s=240)
        await _wait_context_download_terminal_success(session_wait_none, context_id_2, timeout_s=240)

        assert t_wait_both >= t_wait_one, (
            "Expected create(wait-both) to be slower than or equal to create(wait-one). "
            f"t_wait_both={t_wait_both:.2f}s, t_wait_one={t_wait_one:.2f}s"
        )
        assert t_wait_one >= t_wait_none, (
            "Expected create(wait-one) to be slower than or equal to create(wait-none). "
            f"t_wait_one={t_wait_one:.2f}s, t_wait_none={t_wait_none:.2f}s"
        )
    finally:
        for s in [session_wait_none, session_wait_one, session_wait_both]:
            if s is None:
                continue
            try:
                await agent_bay.delete(s, sync_context=False)
            except Exception:
                pass

        try:
            await agent_bay.context.delete(Context(id=context_id_1, name=context_name_1))
        except Exception:
            pass
        try:
            await agent_bay.context.delete(Context(id=context_id_2, name=context_name_2))
        except Exception:
            pass

