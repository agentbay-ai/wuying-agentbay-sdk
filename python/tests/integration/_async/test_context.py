# ci-stable
"""Integration tests for Context operations."""

import time
from uuid import uuid4

import pytest

from agentbay import ContextSync, CreateSessionParams, SyncPolicy


@pytest.mark.asyncio
async def test_context_create_and_delete(agent_bay_client):
    """Test creating and deleting a context."""
    context_name = f"test-context-{uuid4().hex[:8]}"

    create_result = await agent_bay_client.context.get(name=context_name, create=True)
    assert create_result.success is True
    assert create_result.context is not None
    context = create_result.context
    print(f"Created context: {context.id}, name: {context.name}")

    assert context.id is not None
    assert context.name == context_name

    delete_result = await agent_bay_client.context.delete(context)
    assert delete_result.success is True
    print(f"Deleted context: {context.id}")


@pytest.mark.asyncio
async def test_context_get_existing(agent_bay_client):
    """Test getting an existing context."""
    context_name = f"test-existing-{uuid4().hex[:8]}"

    create_result = await agent_bay_client.context.get(name=context_name, create=True)
    assert create_result.success is True
    context = create_result.context

    try:
        get_result = await agent_bay_client.context.get(name=context_name)
        assert get_result.success is True
        assert get_result.context.id == context.id
        assert get_result.context.name == context_name
        print(f"Retrieved existing context: {get_result.context.id}")
    finally:
        await agent_bay_client.context.delete(context)


@pytest.mark.asyncio
async def test_context_get_nonexistent(agent_bay_client):
    """Test getting a non-existent context without create flag."""
    context_name = f"test-nonexistent-{uuid4().hex[:8]}"

    get_result = await agent_bay_client.context.get(name=context_name, create=False)
    assert not get_result.success
    if get_result.success and get_result.context:
        await agent_bay_client.context.delete(get_result.context)
        print("Context was auto-created, cleaned up")
    else:
        print("Correctly handled non-existent context")


@pytest.mark.asyncio
async def test_context_list(agent_bay_client):
    """Test listing contexts."""
    context_name = f"test-list-{uuid4().hex[:8]}"
    create_result = await agent_bay_client.context.get(name=context_name, create=True)
    assert create_result.success is True
    context = create_result.context

    try:
        list_result = await agent_bay_client.context.list()
        assert list_result.success is True
        assert isinstance(list_result.contexts, list)
        assert len(list_result.contexts) > 0

        context_ids = [ctx.id for ctx in list_result.contexts]
        assert context.id in context_ids
        print(f"Found {len(list_result.contexts)} contexts")
    finally:
        await agent_bay_client.context.delete(context)


@pytest.mark.asyncio
async def test_context_update(agent_bay_client):
    """Test updating a context."""
    context_name = f"test-update-{uuid4().hex[:8]}"

    create_result = await agent_bay_client.context.get(name=context_name, create=True)
    assert create_result.success is True
    context = create_result.context

    try:
        new_name = f"test-updated-{uuid4().hex[:8]}"
        context.name = new_name
        update_result = await agent_bay_client.context.update(context)
        assert update_result.success is True
        print(f"Updated context: {context.id} to new name: {new_name}")
        print("Context update completed")
    finally:
        await agent_bay_client.context.delete(context)


@pytest.mark.asyncio
async def test_context_with_session(make_session):
    """Test using context with a session."""
    context_name = f"test-session-ctx-{uuid4().hex[:8]}"

    lc = await make_session(
        "linux_latest",
        context_name=context_name,
        context_path="/tmp/test_context",
        context_policy=SyncPolicy.default(),
    )
    session = lc._result.session

    context_result = await lc.agent_bay.context.get(name=context_name)
    assert context_result.success is True
    assert context_result.context is not None
    print(f"Created session {session.session_id} with context {context_result.context.id}")


@pytest.mark.asyncio
async def test_context_cross_session_persistence(agent_bay_client):
    """Test context persistence across multiple sessions.

    Session1 writes data and deletes with sync_context=True,
    then Session2 binds the same context and verifies data persists.
    """
    context_name = f"test-cross-session-{uuid4().hex[:8]}"
    context_result = await agent_bay_client.context.get(name=context_name, create=True)
    assert context_result.success, f"Failed to create context: {context_result.error_message}"
    context = context_result.context
    print(f"Created context: {context.name} (ID: {context.id})")

    try:
        test_path = "/tmp/cross_session_test"
        test_file_path = f"{test_path}/persistence_test.txt"
        test_content = f"Cross-session test data created at {time.time()}"

        # Session1: write data and delete with sync
        context_sync = ContextSync(context_id=context.id, path=test_path)
        session1_result = await agent_bay_client.create(
            params=CreateSessionParams(context_syncs=[context_sync])
        )
        assert session1_result.success, f"Failed to create session1: {session1_result.error_message}"
        session1 = session1_result.session
        print(f"Session1 created: {session1.session_id}")

        write_result = await session1.file_system.write_file(test_file_path, test_content)
        assert write_result.success, f"Failed to write test file: {write_result.error_message}"

        session1_delete_result = await agent_bay_client.delete(session1, sync_context=True)
        assert session1_delete_result.success, f"Failed to delete session1: {session1_delete_result.error_message}"
        print(f"Session1 deleted with context sync")

        # Re-get context by ID to simulate fresh context retrieval
        context_reget_result = await agent_bay_client.context.get(context_id=context.id)
        assert context_reget_result.success, f"Failed to re-get context: {context_reget_result.error_message}"
        reget_context = context_reget_result.context
        assert reget_context.id == context.id

        # Session2: bind same context and verify data persists
        context_sync2 = ContextSync(context_id=reget_context.id, path=test_path)
        session2_result = await agent_bay_client.create(
            params=CreateSessionParams(context_syncs=[context_sync2])
        )
        assert session2_result.success, f"Failed to create session2: {session2_result.error_message}"
        session2 = session2_result.session
        print(f"Session2 created: {session2.session_id}")

        try:
            read_result = await session2.file_system.read_file(test_file_path)
            assert read_result.success, f"Failed to read test file in session2: {read_result.error_message}"
            assert read_result.content == test_content, (
                f"Content mismatch: expected '{test_content}', got '{read_result.content}'"
            )
            print(f"Data persistence verified: '{read_result.content}'")

            session2_delete_result = await agent_bay_client.delete(session2)
            assert session2_delete_result.success
            print(f"Session2 deleted")
        except Exception:
            await session2.delete()
            raise

    finally:
        await agent_bay_client.context.delete(context)
        print(f"Context deleted: {context.id}")

