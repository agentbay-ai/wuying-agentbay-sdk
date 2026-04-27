"""Integration tests for Context dynamic binding (bind/list_bindings).
ci-stable
"""

from uuid import uuid4

import pytest
import pytest_asyncio

from agentbay import CreateSessionParams, ContextSync


@pytest_asyncio.fixture(scope="module")
async def context_id(agent_bay_client):
    """Create a test context and return its ID. Clean up after all tests."""
    context_name = f"test-bind-{uuid4().hex[:8]}"
    create_result = await agent_bay_client.context.get(name=context_name, create=True)
    assert create_result.success is True, f"Failed to create context: {create_result.error_message}"
    ctx = create_result.context
    print(f"Created test context: {ctx.id}, name: {ctx.name}")
    yield ctx.id
    await agent_bay_client.context.delete(ctx)
    print(f"Deleted test context: {ctx.id}")


@pytest.mark.asyncio
async def test_bind_single_context(agent_bay_client, context_id):
    """Test dynamically binding a single context to a running session."""
    session_result = await agent_bay_client.create(CreateSessionParams())
    assert session_result.success, f"Failed to create session: {session_result.error_message}"
    session = session_result.session
    try:
        result = await session.context.bind(
            ContextSync(context_id=context_id, path="/tmp/test-bind"),
        )
        assert result.success is True, f"bind() failed: {result.error_message}"
        print(f"Bind result: success={result.success}, request_id={result.request_id}")
    finally:
        await session.delete()


@pytest.mark.asyncio
async def test_list_bindings_after_bind(agent_bay_client, context_id):
    """Test listing bindings after dynamically binding a context."""
    session_result = await agent_bay_client.create(CreateSessionParams())
    assert session_result.success, f"Failed to create session: {session_result.error_message}"
    session = session_result.session
    try:
        bind_result = await session.context.bind(
            ContextSync(context_id=context_id, path="/tmp/test-list"),
        )
        assert bind_result.success is True, f"bind() failed: {bind_result.error_message}"

        bindings_result = await session.context.list_bindings()
        assert bindings_result.success is True, f"list_bindings() failed: {bindings_result.error_message}"
        assert len(bindings_result.bindings) > 0, "Expected at least one binding"

        found = False
        for b in bindings_result.bindings:
            print(f"  Binding: {b.context_id} -> {b.path} (name={b.context_name})")
            if b.context_id == context_id and b.path == "/tmp/test-list":
                found = True
        assert found, f"Expected to find binding for context_id={context_id} at /tmp/test-list"
    finally:
        await session.delete()


@pytest.mark.asyncio
async def test_bind_multiple_contexts(agent_bay_client):
    """Test dynamically binding multiple contexts at once."""
    ctx_name_1 = f"test-multi-1-{uuid4().hex[:8]}"
    ctx_name_2 = f"test-multi-2-{uuid4().hex[:8]}"

    ctx1_result = await agent_bay_client.context.get(name=ctx_name_1, create=True)
    ctx2_result = await agent_bay_client.context.get(name=ctx_name_2, create=True)
    assert ctx1_result.success and ctx2_result.success

    session_result = await agent_bay_client.create(CreateSessionParams())
    assert session_result.success, f"Failed to create session: {session_result.error_message}"
    session = session_result.session
    try:
        result = await session.context.bind(
            ContextSync(context_id=ctx1_result.context.id, path="/tmp/multi-1"),
            ContextSync(context_id=ctx2_result.context.id, path="/tmp/multi-2"),
        )
        assert result.success is True, f"bind() failed: {result.error_message}"

        bindings_result = await session.context.list_bindings()
        assert bindings_result.success is True
        bound_context_ids = {b.context_id for b in bindings_result.bindings}
        assert ctx1_result.context.id in bound_context_ids, "context 1 not found in bindings"
        assert ctx2_result.context.id in bound_context_ids, "context 2 not found in bindings"
        print(f"Bound {len(bindings_result.bindings)} contexts successfully")
    finally:
        await session.delete()
        await agent_bay_client.context.delete(ctx1_result.context)
        await agent_bay_client.context.delete(ctx2_result.context)


@pytest.mark.asyncio
async def test_list_bindings_empty_session(agent_bay_client):
    """Test list_bindings on a session with no dynamically bound contexts."""
    session_result = await agent_bay_client.create(CreateSessionParams())
    assert session_result.success, f"Failed to create session: {session_result.error_message}"
    session = session_result.session
    try:
        bindings_result = await session.context.list_bindings()
        assert bindings_result.success is True, f"list_bindings() failed: {bindings_result.error_message}"
        print(f"Bindings count on empty session: {len(bindings_result.bindings)}")
    finally:
        await session.delete()
