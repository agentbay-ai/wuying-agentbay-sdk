# ci-stable
"""Integration tests for Context operations."""

from uuid import uuid4

import pytest

from agentbay import SyncPolicy


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
async def test_context_file_operations(agent_bay_client):
    """Test context file upload/download URL operations."""
    context_name = f"test-file-ops-{uuid4().hex[:8]}"

    create_result = await agent_bay_client.context.get(name=context_name, create=True)
    assert create_result.success is True
    context = create_result.context

    try:
        upload_url_result = await agent_bay_client.context.get_file_upload_url(
            context.id, "/test_file.txt"
        )
        assert upload_url_result.success is True
        assert upload_url_result.url is not None
        assert len(upload_url_result.url) > 0
        print(f"Got upload URL: {upload_url_result.url[:50]}...")

        try:
            download_url_result = await agent_bay_client.context.get_file_download_url(
                context.id, "/test_file.txt"
            )
            print(f"Download URL result success: {download_url_result.success}")
        except Exception:
            print("Download URL failed as expected: file not exist")
    finally:
        await agent_bay_client.context.delete(context)
