# ci-stable
import pytest
import pytest_asyncio

from agentbay import (
    AsyncAgentBay,
    BWList,
    ContextSync,
    CreateSessionParams,
    SyncPolicy,
    WhiteList,
)


@pytest_asyncio.fixture
async def test_context(agent_bay_client: AsyncAgentBay):
    context_result = await agent_bay_client.context.get("test-wildcard-validation", create=True)
    assert context_result.success
    yield context_result.context
    await agent_bay_client.context.delete(context_result.context)


@pytest.mark.asyncio
async def test_create_session_with_wildcard_in_path_should_fail(
    agent_bay_client: AsyncAgentBay, test_context
):
    with pytest.raises(ValueError) as exc_info:
        policy = SyncPolicy(bw_list=BWList(white_lists=[WhiteList(path="*.json")]))
        context_sync = ContextSync.new(test_context.id, "/tmp/data", policy)
        await agent_bay_client.create(CreateSessionParams(context_syncs=[context_sync]))

    assert "Wildcard patterns are not supported in path" in str(exc_info.value)
    assert "*.json" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_session_with_wildcard_in_exclude_paths_should_fail(
    agent_bay_client: AsyncAgentBay, test_context
):
    with pytest.raises(ValueError) as exc_info:
        policy = SyncPolicy(
            bw_list=BWList(
                white_lists=[WhiteList(path="/src", exclude_paths=["*.log"])]
            )
        )
        context_sync = ContextSync.new(test_context.id, "/tmp/data", policy)
        await agent_bay_client.create(CreateSessionParams(context_syncs=[context_sync]))

    assert "Wildcard patterns are not supported in exclude_paths" in str(exc_info.value)
    assert "*.log" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_session_with_glob_pattern_should_fail(
    agent_bay_client: AsyncAgentBay, test_context
):
    with pytest.raises(ValueError) as exc_info:
        policy = SyncPolicy(bw_list=BWList(white_lists=[WhiteList(path="/data/*")]))
        context_sync = ContextSync.new(test_context.id, "/tmp/data", policy)
        await agent_bay_client.create(CreateSessionParams(context_syncs=[context_sync]))

    assert "Wildcard patterns are not supported in path" in str(exc_info.value)
    assert "/data/*" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_session_with_double_asterisk_should_fail(
    agent_bay_client: AsyncAgentBay, test_context
):
    with pytest.raises(ValueError) as exc_info:
        policy = SyncPolicy(
            bw_list=BWList(white_lists=[WhiteList(path="/logs/**/*.txt")])
        )
        context_sync = ContextSync.new(test_context.id, "/tmp/data", policy)
        await agent_bay_client.create(CreateSessionParams(context_syncs=[context_sync]))

    assert "Wildcard patterns are not supported in path" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_session_with_valid_paths_should_succeed(
    agent_bay_client: AsyncAgentBay, test_context
):
    policy = SyncPolicy(
        bw_list=BWList(
            white_lists=[
                WhiteList(path="/src", exclude_paths=["/node_modules", "/temp"])
            ]
        )
    )
    context_sync = ContextSync.new(test_context.id, "/tmp/data", policy)
    session_result = await agent_bay_client.create(
        CreateSessionParams(context_syncs=[context_sync])
    )

    try:
        assert session_result.success
        assert session_result.session is not None
    finally:
        if session_result.session is not None:
            await agent_bay_client.delete(session_result.session)


@pytest.mark.asyncio
async def test_validation_happens_before_api_call(
    agent_bay_client: AsyncAgentBay, test_context
):
    with pytest.raises(ValueError) as exc_info:
        policy = SyncPolicy(bw_list=BWList(white_lists=[WhiteList(path="*.txt")]))
        ContextSync.new(test_context.id, "/tmp/data", policy)

    assert "Wildcard patterns are not supported in path" in str(exc_info.value)
