"""Integration tests for context synchronization.
ci-stable
"""

import asyncio
import time

import pytest
import pytest_asyncio

from agentbay import (
    BWList,
    ContextSync,
    CreateSessionParams,
    DeletePolicy,
    DownloadPolicy,
    ExtractPolicy,
    Lifecycle,
    RecyclePolicy,
    SyncPolicy,
    UploadPolicy,
    WhiteList,
)


@pytest_asyncio.fixture
async def test_session(make_session):
    lc = await make_session("linux_latest")
    return lc._result.session


@pytest_asyncio.fixture(scope="module")
async def context_for_test(agent_bay_client):
    """Create a context for testing."""
    context_name = f"test-sync-context-{int(time.time())}"

    context_result = await agent_bay_client.context.get(context_name, True)
    if not context_result.success or not context_result.context:
        pytest.skip("Failed to create context")

    context = context_result.context
    print(f"Created context: {context.name} (ID: {context.id})")

    yield context

    try:
        await agent_bay_client.context.delete(context)
        print(f"Context deleted: {context.id}")
    except Exception as e:
        print(f"Warning: Failed to delete context: {e}")


@pytest.mark.asyncio
async def test_context_sync_status(test_session):
    """Test context synchronization status retrieval."""
    context_info = await test_session.context.info()

    assert context_info is not None
    assert context_info.request_id != ""

    print(
        f"Context sync test completed, found {len(context_info.context_status_data)} status entries"
    )


@pytest.mark.asyncio
async def test_recycle_policy_with_lifecycle_1day(agent_bay_client, context_for_test):
    """Test creating ContextSync with custom RecyclePolicy using Lifecycle_1Day."""
    custom_recycle_policy = RecyclePolicy(
        lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=["/custom/path"]
    )

    sync_policy = SyncPolicy(
        upload_policy=UploadPolicy.default(),
        download_policy=DownloadPolicy.default(),
        delete_policy=DeletePolicy.default(),
        extract_policy=ExtractPolicy.default(),
        recycle_policy=custom_recycle_policy,
        bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])]),
    )

    assert sync_policy.recycle_policy is not None
    assert sync_policy.recycle_policy.lifecycle == Lifecycle.LIFECYCLE_1DAY
    assert sync_policy.recycle_policy.paths is not None
    assert len(sync_policy.recycle_policy.paths) == 1
    assert sync_policy.recycle_policy.paths[0] == "/custom/path"

    policy_dict = sync_policy.__dict__()
    assert "recyclePolicy" in policy_dict

    recycle_policy_dict = policy_dict["recyclePolicy"]
    assert recycle_policy_dict["lifecycle"] == "Lifecycle_1Day"
    assert len(recycle_policy_dict["paths"]) == 1
    assert recycle_policy_dict["paths"][0] == "/custom/path"

    context_sync = ContextSync(
        context_id="test-recycle-context", path="/test/recycle/path", policy=sync_policy
    )
    assert context_sync.context_id == "test-recycle-context"
    assert context_sync.path == "/test/recycle/path"
    assert context_sync.policy == sync_policy

    context_sync = ContextSync.new(
        context_for_test.id, "/home/wuying/recycle-test", sync_policy
    )

    session_params = CreateSessionParams()
    session_params.context_syncs = [context_sync]
    session_params.labels = {"test": "recycle-policy-integration"}
    session_params.image_id = "linux_latest"

    session_result = await agent_bay_client.create(session_params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session for RecyclePolicy integration test")

    session = session_result.session
    print(f"Session created successfully with ID: {session.session_id}")

    try:
        await asyncio.sleep(5)

        context_info = await session.context.info()
        assert context_info.request_id is not None

        print("RecyclePolicy integration test completed successfully")
    finally:
        try:
            await agent_bay_client.delete(session)
            print(f"Session deleted: {session.session_id}")
        except Exception as e:
            print(f"Warning: Failed to delete session: {e}")


@pytest.mark.asyncio
async def test_context_sync_and_info(agent_bay_client, context_for_test):
    """Test syncing context and then getting info."""
    context_sync = ContextSync.new(
        context_for_test.id, "/home/wuying", SyncPolicy.default()
    )
    session_params = CreateSessionParams()
    session_params.context_syncs = [context_sync]
    session_params.labels = {"test": "context-sync-integration"}
    session_params.image_id = "linux_latest"

    session_result = await agent_bay_client.create(session_params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session for test")

    session = session_result.session
    print(f"Created session: {session.session_id}")

    try:
        await asyncio.sleep(2)

        sync_result = await session.context.info()

        assert sync_result.request_id is not None
        assert sync_result.request_id != ""

        print(
            f"Context status data after sync, count: {len(sync_result.context_status_data)}"
        )
        for i, data in enumerate(sync_result.context_status_data):
            print(f"Status data {i}:")
            print(f"  Context ID: {data.context_id}")
            print(f"  Path: {data.path}")
            print(f"  Status: {data.status}")
            print(f"  Task Type: {data.task_type}")
            print(f"  Start Time: {data.start_time}")
            print(f"  Finish Time: {data.finish_time}")
            if hasattr(data, "error_message") and data.error_message:
                print(f"  Error: {data.error_message}")

        found_context = False
        for data in sync_result.context_status_data:
            if data.context_id == context_for_test.id:
                found_context = True
                assert data.path == "/home/wuying"
                assert data.status is not None
                assert data.status != ""
                break

        if not found_context:
            print(
                f"Warning: Could not find context {context_for_test.id} in status data"
            )
    finally:
        try:
            await agent_bay_client.delete(session)
            print(f"Session deleted: {session.session_id}")
        except Exception as e:
            print(f"Warning: Failed to delete session: {e}")


@pytest.mark.asyncio
async def test_recycle_policy_with_invalid_wildcard_path():
    """Test that RecyclePolicy throws error when created with invalid wildcard path."""
    print("Testing RecyclePolicy creation with invalid wildcard path...")

    with pytest.raises(ValueError) as exc_info:
        RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=["/path/with/*"])

    error_message = str(exc_info.value)
    assert "Wildcard patterns are not supported in recycle policy paths" in error_message
    assert "/path/with/*" in error_message
    assert "Please use exact directory paths instead" in error_message

    print("RecyclePolicy correctly threw error for invalid wildcard path")

    with pytest.raises(ValueError):
        RecyclePolicy(
            lifecycle=Lifecycle.LIFECYCLE_1DAY,
            paths=["/valid/path", "/invalid/path?", "/another/invalid/*"],
        )

    print("RecyclePolicy correctly threw error for multiple invalid paths")

    invalid_patterns = [
        "/path/with/*",
        "/path/with/?",
        "/path/with/[abc]",
        "/path/with/file*.txt",
    ]

    for pattern in invalid_patterns:
        with pytest.raises(ValueError) as exc_info:
            RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=[pattern])

        error_message = str(exc_info.value)
        assert "Wildcard patterns are not supported" in error_message
        assert pattern in error_message

    print("All wildcard patterns correctly rejected")


@pytest.mark.asyncio
async def test_recycle_policy_default_values():
    """Test RecyclePolicy default values and behavior."""
    default_policy = RecyclePolicy.default()

    assert default_policy.lifecycle == Lifecycle.LIFECYCLE_FOREVER
    assert default_policy.paths == [""]

    no_args_policy = RecyclePolicy()

    assert no_args_policy.lifecycle == Lifecycle.LIFECYCLE_FOREVER
    assert no_args_policy.paths == [""]

    policy_dict = default_policy.__dict__()
    assert policy_dict["lifecycle"] == "Lifecycle_Forever"
    assert policy_dict["paths"] == [""]

    print("RecyclePolicy default values verified successfully")
