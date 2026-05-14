"""Diagnostics for Smartclaw-style context credential delivery.

Run manually with:
RUN_AGENTBAY_CONTEXT_CREDENTIAL_DIAGNOSTIC=1 uv run pytest \
  tests/integration/_async/test_context_oss_credentials_diagnostic.py -q -s
"""

import asyncio
import os
import random
import re
import time

import pytest

from agentbay import (
    AgentBayLogger,
    ContextSync,
    CreateSessionParams,
    SyncPolicy,
    get_logger,
)


AgentBayLogger.setup(
    level=os.getenv("AGENTBAY_LOG_LEVEL", "INFO"),
    enable_console=True,
)
logger = get_logger("test_context_oss_credentials_diagnostic")

RUN_DIAGNOSTIC_ENV = "RUN_AGENTBAY_CONTEXT_CREDENTIAL_DIAGNOSTIC"
WORKSPACE_PATH = "/home/wuying/jvscrew"
SHARED_PATH = "/home/wuying/.jvscrew-shared"
TERMINAL_STATUSES = {"Success", "Failed"}


def _unique_suffix() -> str:
    timestamp = int(time.time() * 1000)
    random_part = random.randint(1000, 9999)
    return f"{timestamp}-{random_part}"


def _format_statuses(statuses) -> str:
    if not statuses:
        return "<no target context statuses returned>"

    lines = []
    for item in statuses:
        lines.append(
            "context_id={context_id}, path={path}, task_type={task_type}, "
            "status={status}, start_time={start_time}, finish_time={finish_time}, "
            "error={error}".format(
                context_id=item.context_id,
                path=item.path,
                task_type=item.task_type,
                status=item.status,
                start_time=item.start_time,
                finish_time=item.finish_time,
                error=item.error_message or "<empty>",
            )
        )
    return "\n".join(lines)


async def _create_diagnostic_contexts(agent_bay_client, unique: str):
    created_contexts = []
    for suffix in ("workspace", "shared"):
        context_name = f"smartclaw-credential-diagnostic-{suffix}-{unique}"
        context_result = await agent_bay_client.context.create(context_name)

        assert context_result.success, (
            "Failed to create context "
            f"{context_name}: {context_result.error_message} "
            f"(request_id={context_result.request_id})"
        )
        assert context_result.context is not None
        created_contexts.append(context_result.context)

    return created_contexts


def _build_context_syncs(created_contexts, wait_for_completion=None):
    workspace_context, shared_context = created_contexts
    return [
        ContextSync.new(
            workspace_context.id,
            WORKSPACE_PATH,
            SyncPolicy.default(),
            beta_wait_for_completion=wait_for_completion,
        ),
        ContextSync.new(
            shared_context.id,
            SHARED_PATH,
            SyncPolicy.default(),
            beta_wait_for_completion=wait_for_completion,
        ),
    ]


def _diagnostic_skill_names() -> list[str] | None:
    raw = os.getenv("AGENTBAY_DIAGNOSTIC_SKILL_NAMES", "").strip()
    if not raw:
        return None
    return [name.strip() for name in raw.split(",") if name.strip()]


async def _wait_for_target_download_statuses(session, context_ids: set[str]):
    """Wait until both target download tasks are visible and terminal."""
    deadline = time.monotonic() + 45
    latest_statuses = []
    latest_info = None

    while time.monotonic() < deadline:
        latest_info = await session.context.info()
        latest_statuses = [
            item
            for item in latest_info.context_status_data
            if item.context_id in context_ids and item.task_type == "download"
        ]

        seen_context_ids = {item.context_id for item in latest_statuses}
        if context_ids.issubset(seen_context_ids) and all(
            item.status in TERMINAL_STATUSES for item in latest_statuses
        ):
            return latest_info, latest_statuses

        await asyncio.sleep(1)

    return latest_info, latest_statuses


@pytest.mark.skipif(
    os.getenv(RUN_DIAGNOSTIC_ENV) != "1",
    reason=f"Set {RUN_DIAGNOSTIC_ENV}=1 to run AgentBay backend diagnostics.",
)
@pytest.mark.asyncio
async def test_smartclaw_workspace_contexts_receive_download_credentials(
    agent_bay_client,
):
    """Reproduce the Smartclaw two-context mount layout using only AgentBay SDK.

    A healthy backend should deliver OSS credentials to both mounted contexts so
    their initial download tasks end in Success. The Smartclaw failure mode is
    that the tasks end in Failed with "Wait OSS credential timeout (>10s)".
    """
    unique = _unique_suffix()
    session = None
    created_contexts = []

    try:
        created_contexts = await _create_diagnostic_contexts(agent_bay_client, unique)
        context_syncs = _build_context_syncs(created_contexts)

        session_params = CreateSessionParams(
            image_id=os.getenv("AGENTBAY_DIAGNOSTIC_IMAGE_ID", "linux_latest"),
            context_syncs=context_syncs,
            labels={
                "test": "smartclaw-context-credential-diagnostic",
                "case": unique,
            },
        )

        session_result = await agent_bay_client.create(session_params)
        assert session_result.success, (
            f"Failed to create session: {session_result.error_message} "
            f"(request_id={session_result.request_id})"
        )

        session = session_result.session
        assert session is not None
        workspace_context, shared_context = created_contexts
        target_context_ids = {workspace_context.id, shared_context.id}

        info_result, statuses = await _wait_for_target_download_statuses(
            session,
            target_context_ids,
        )
        status_summary = _format_statuses(statuses)
        logger.info(
            "Smartclaw context credential diagnostic summary:\n"
            f"session_id={session.session_id}\n"
            f"create_session_request_id={session_result.request_id}\n"
            f"get_context_info_request_id="
            f"{info_result.request_id if info_result else '<none>'}\n"
            f"{status_summary}"
        )

        missing_context_ids = target_context_ids - {
            item.context_id for item in statuses
        }
        assert not missing_context_ids, (
            "Timed out waiting for target context download statuses. "
            f"session_id={session.session_id}, missing={sorted(missing_context_ids)}, "
            f"statuses:\n{status_summary}"
        )

        credential_timeouts = [
            item
            for item in statuses
            if "Wait OSS credential timeout" in (item.error_message or "")
        ]
        assert not credential_timeouts, (
            "Backend did not deliver OSS credentials to mounted contexts. "
            f"session_id={session.session_id}, "
            f"create_session_request_id={session_result.request_id}, "
            f"get_context_info_request_id={info_result.request_id}, "
            f"statuses:\n{_format_statuses(credential_timeouts)}"
        )

        failed_statuses = [item for item in statuses if item.status != "Success"]
        assert not failed_statuses, (
            "Expected all Smartclaw workspace context download tasks to succeed. "
            f"session_id={session.session_id}, statuses:\n"
            f"{_format_statuses(failed_statuses)}"
        )
    finally:
        if session is not None:
            delete_result = await agent_bay_client.delete(session)
            logger.info(
                f"Deleted diagnostic session {session.session_id}: "
                f"success={delete_result.success} "
                f"request_id={delete_result.request_id}"
            )

        for context in created_contexts:
            delete_result = await agent_bay_client.context.delete(context)
            logger.info(
                f"Deleted diagnostic context {context.id}: "
                f"success={delete_result.success} "
                f"request_id={delete_result.request_id}"
            )


@pytest.mark.skipif(
    os.getenv(RUN_DIAGNOSTIC_ENV) != "1",
    reason=f"Set {RUN_DIAGNOSTIC_ENV}=1 to run AgentBay backend diagnostics.",
)
@pytest.mark.asyncio
async def test_load_skills_with_smartclaw_contexts_does_not_starve_credentials(
    agent_bay_client,
):
    """Reproduce Smartclaw CreateSession parameters when market skills exist."""
    unique = _unique_suffix()
    session = None
    created_contexts = []

    try:
        created_contexts = await _create_diagnostic_contexts(agent_bay_client, unique)
        context_syncs = _build_context_syncs(created_contexts)
        skill_names = _diagnostic_skill_names()

        session_params = CreateSessionParams(
            image_id=os.getenv("AGENTBAY_DIAGNOSTIC_IMAGE_ID", "linux_latest"),
            context_syncs=context_syncs,
            load_skills=True,
            skill_names=skill_names,
            labels={
                "test": "smartclaw-load-skills-credential-diagnostic",
                "case": unique,
            },
        )

        session_result = await agent_bay_client.create(session_params)
        assert session_result.success, (
            f"Failed to create session: {session_result.error_message} "
            f"(request_id={session_result.request_id})"
        )

        session = session_result.session
        assert session is not None
        workspace_context, shared_context = created_contexts
        target_context_ids = {workspace_context.id, shared_context.id}

        info_result, statuses = await _wait_for_target_download_statuses(
            session,
            target_context_ids,
        )
        status_summary = _format_statuses(statuses)
        logger.info(
            "Load-skills credential diagnostic summary:\n"
            f"session_id={session.session_id}\n"
            f"create_session_request_id={session_result.request_id}\n"
            f"skill_names={skill_names or '<all-visible>'}\n"
            f"get_context_info_request_id="
            f"{info_result.request_id if info_result else '<none>'}\n"
            f"{status_summary}"
        )

        credential_timeouts = [
            item
            for item in statuses
            if "Wait OSS credential timeout" in (item.error_message or "")
        ]
        assert not credential_timeouts, (
            "CreateSession(load_skills=True) caused mounted contexts to miss "
            "OSS credentials. "
            f"session_id={session.session_id}, "
            f"create_session_request_id={session_result.request_id}, "
            f"get_context_info_request_id={info_result.request_id}, "
            f"skill_names={skill_names or '<all-visible>'}, "
            f"statuses:\n{_format_statuses(credential_timeouts)}"
        )

        failed_statuses = [item for item in statuses if item.status != "Success"]
        assert not failed_statuses, (
            "Expected all Smartclaw workspace context download tasks to succeed "
            "when load_skills=True. "
            f"session_id={session.session_id}, statuses:\n"
            f"{_format_statuses(failed_statuses)}"
        )
    finally:
        if session is not None:
            delete_result = await agent_bay_client.delete(session)
            logger.info(
                f"Deleted diagnostic session {session.session_id}: "
                f"success={delete_result.success} "
                f"request_id={delete_result.request_id}"
            )

        for context in created_contexts:
            delete_result = await agent_bay_client.context.delete(context)
            logger.info(
                f"Deleted diagnostic context {context.id}: "
                f"success={delete_result.success} "
                f"request_id={delete_result.request_id}"
            )


@pytest.mark.skipif(
    os.getenv(RUN_DIAGNOSTIC_ENV) != "1",
    reason=f"Set {RUN_DIAGNOSTIC_ENV}=1 to run AgentBay backend diagnostics.",
)
@pytest.mark.asyncio
async def test_duplicate_bind_during_initial_download_does_not_starve_credentials(
    agent_bay_client,
):
    """Probe the Smartclaw failure branch: duplicate bind while downloads prepare.

    Smartclaw backend logs showed a second setSessionProfile call rejected with an
    overlapping path error shortly after session creation. This test uses only SDK
    calls to verify whether a duplicate bind can starve the original download
    tasks of OSS credentials.
    """
    unique = _unique_suffix()
    session = None
    created_contexts = []

    try:
        created_contexts = await _create_diagnostic_contexts(agent_bay_client, unique)
        context_syncs = _build_context_syncs(
            created_contexts,
            wait_for_completion=False,
        )

        session_params = CreateSessionParams(
            image_id=os.getenv("AGENTBAY_DIAGNOSTIC_IMAGE_ID", "linux_latest"),
            context_syncs=context_syncs,
            labels={
                "test": "smartclaw-duplicate-bind-diagnostic",
                "case": unique,
            },
        )

        session_result = await agent_bay_client.create(session_params)
        assert session_result.success, (
            f"Failed to create session: {session_result.error_message} "
            f"(request_id={session_result.request_id})"
        )

        session = session_result.session
        assert session is not None

        bind_request_id = ""
        bind_error = ""
        try:
            bind_result = await session.context.bind(
                *context_syncs,
                wait_for_completion=False,
            )
            bind_request_id = bind_result.request_id
            bind_error = bind_result.error_message
            logger.info(
                "Duplicate bind result: "
                f"success={bind_result.success}, "
                f"request_id={bind_result.request_id}, "
                f"error={bind_result.error_message or '<empty>'}"
            )
        except Exception as exc:
            bind_error = str(exc)
            request_id_match = re.search(
                r"request id:\s*([A-Za-z0-9-]+)",
                bind_error,
                re.IGNORECASE,
            )
            bind_request_id = (
                request_id_match.group(1) if request_id_match else "<exception>"
            )
            logger.info(
                "Duplicate bind raised exception: "
                f"request_id={bind_request_id}, error={bind_error}"
            )

        assert "PathAlreadyBound" in bind_error, (
            "Expected duplicate bind to be rejected by path overlap protection. "
            f"session_id={session.session_id}, "
            f"create_session_request_id={session_result.request_id}, "
            f"bind_request_id={bind_request_id}, error={bind_error}"
        )

        workspace_context, shared_context = created_contexts
        target_context_ids = {workspace_context.id, shared_context.id}
        info_result, statuses = await _wait_for_target_download_statuses(
            session,
            target_context_ids,
        )
        status_summary = _format_statuses(statuses)
        logger.info(
            "Duplicate bind credential diagnostic summary:\n"
            f"session_id={session.session_id}\n"
            f"create_session_request_id={session_result.request_id}\n"
            f"bind_request_id={bind_request_id}\n"
            f"get_context_info_request_id="
            f"{info_result.request_id if info_result else '<none>'}\n"
            f"{status_summary}"
        )

        credential_timeouts = [
            item
            for item in statuses
            if "Wait OSS credential timeout" in (item.error_message or "")
        ]
        assert not credential_timeouts, (
            "Duplicate bind caused original mounted contexts to miss OSS "
            "credentials. "
            f"session_id={session.session_id}, "
            f"create_session_request_id={session_result.request_id}, "
            f"bind_request_id={bind_request_id}, "
            f"get_context_info_request_id={info_result.request_id}, "
            f"statuses:\n{_format_statuses(credential_timeouts)}"
        )
    finally:
        if session is not None:
            delete_result = await agent_bay_client.delete(session)
            logger.info(
                f"Deleted diagnostic session {session.session_id}: "
                f"success={delete_result.success} "
                f"request_id={delete_result.request_id}"
            )

        for context in created_contexts:
            delete_result = await agent_bay_client.context.delete(context)
            logger.info(
                f"Deleted diagnostic context {context.id}: "
                f"success={delete_result.success} "
                f"request_id={delete_result.request_id}"
            )
