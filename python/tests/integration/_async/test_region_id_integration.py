"""Integration tests for region_id support in AgentBay SDK."""

import asyncio
import os

import pytest

from agentbay import AsyncAgentBay, Config, CreateSessionParams
from agentbay import ContextSync


def _build_region_client() -> AsyncAgentBay:
    """Build an AsyncAgentBay client configured with region_id=cn-hangzhou."""
    config = Config(
        endpoint="wuyingai.cn-shanghai.aliyuncs.com",
        timeout_ms=60000,
        region_id="cn-hangzhou",
    )
    return AsyncAgentBay(cfg=config)


@pytest.mark.asyncio
async def test_session_creation_with_region_id():
    """Test creating a session with region_id=cn-hangzhou."""
    agent_bay = _build_region_client()
    assert agent_bay.region_id == "cn-hangzhou"

    params = CreateSessionParams()
    result = await agent_bay.create(params)
    assert result.success, f"Session creation failed: {result.error_message}"
    assert result.session is not None

    print(f"Session created successfully with region_id=cn-hangzhou")
    print(f"Session ID: {result.session.session_id}")
    print(f"Request ID: {result.request_id}")

    await result.session.delete()


@pytest.mark.asyncio
async def test_context_creation_with_region_id():
    """Test creating a context with region_id=cn-hangzhou."""
    config = Config(
        endpoint="wuyingai.cn-shanghai.aliyuncs.com",
        timeout_ms=60000,
        region_id="cn-hangzhou",
    )
    agent_bay = AsyncAgentBay(cfg=config)
    assert config.region_id == "cn-hangzhou"

    context_name = f"test-region-context-{int(asyncio.get_event_loop().time())}"
    result = await agent_bay.context.get(context_name, create=True)
    assert result.success, f"Context creation failed: {result.error_message}"
    assert result.context is not None

    print(f"Context created successfully with region_id=cn-hangzhou")
    print(f"Context ID: {result.context.id}")
    print(f"Context Name: {result.context.name}")
    print(f"Request ID: {result.request_id}")

    await agent_bay.context.delete(result.context)


@pytest.mark.asyncio
async def test_context_get_existing_without_region_id():
    """Test getting an existing context doesn't pass region_id."""
    config = Config(
        endpoint="wuyingai.cn-shanghai.aliyuncs.com",
        timeout_ms=60000,
        region_id="cn-hangzhou",
    )
    agent_bay = AsyncAgentBay(cfg=config)

    context_name = f"test-existing-context-{int(asyncio.get_event_loop().time())}"
    create_result = await agent_bay.context.get(context_name, create=True)
    assert create_result.success

    get_result = await agent_bay.context.get(context_name, create=False)
    assert get_result.success, f"Getting existing context failed: {get_result.error_message}"
    assert get_result.context is not None
    assert get_result.context.name == context_name

    print(f"Existing context retrieved successfully")
    print(f"Context ID: {get_result.context.id}")
    print(f"Context Name: {get_result.context.name}")

    await agent_bay.context.delete(get_result.context)


@pytest.mark.asyncio
async def test_session_and_context_workflow():
    """Test complete workflow: create session with context sync using region_id."""
    config = Config(
        endpoint="wuyingai.cn-shanghai.aliyuncs.com",
        timeout_ms=60000,
        region_id="cn-hangzhou",
    )
    agent_bay = AsyncAgentBay(cfg=config)

    context_name = f"test-workflow-context-{int(asyncio.get_event_loop().time())}"
    context_result = await agent_bay.context.get(context_name, create=True)
    assert context_result.success

    params = CreateSessionParams()
    params.context_syncs = [
        ContextSync(context_id=context_result.context.id, path="/tmp/test-region-sync")
    ]

    session_result = await agent_bay.create(params)
    assert session_result.success, f"Session creation failed: {session_result.error_message}"

    print(f"Complete workflow succeeded with region_id=cn-hangzhou")
    print(f"Context ID: {context_result.context.id}")
    print(f"Session ID: {session_result.session.session_id}")

    await session_result.session.delete()
    await agent_bay.context.delete(context_result.context)


@pytest.mark.asyncio
async def test_agentbay_without_region_id():
    """Test AgentBay works normally without region_id."""
    agent_bay = AsyncAgentBay()
    print(f"AgentBay created without region_id: {agent_bay.region_id}")
    assert agent_bay.region_id is not None

    params = CreateSessionParams()
    result = await agent_bay.create(params)
    assert result.success, f"Session creation failed: {result.error_message}"

    print(f"Session created successfully without region_id")
    print(f"Session ID: {result.session.session_id}")

    await result.session.delete()
