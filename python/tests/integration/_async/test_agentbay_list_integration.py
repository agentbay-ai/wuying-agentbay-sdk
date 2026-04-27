# ci-stable

import asyncio
import random
import time

from agentbay import CreateSessionParams

# make_session factory fixture is provided by conftest.py (auto-loaded by pytest)


def generate_unique_id():
    """Create a unique identifier for test labels to avoid conflicts with existing data."""
    timestamp = int(time.time() * 1000000)
    random_part = random.randint(0, 10000)
    return f"{timestamp}-{random_part}"


async def test_list_all_sessions(make_session):
    """Test listing all sessions without any label filter."""
    print("\n=== Testing list() without labels ===")

    lc = await make_session("linux_latest")
    agent_bay = lc.agent_bay

    result = await agent_bay.list()

    assert result.success, "list() should succeed"
    assert result.request_id is not None, "Request ID should be present"
    assert result.session_ids is not None, "Session IDs list should not be None"

    print(f"Total sessions found: {result.total_count}")
    print(f"Sessions in current page: {len(result.session_ids)}")
    print(f"Request ID: {result.request_id}")


async def test_list_with_single_label(make_session):
    """Test listing sessions with a single label filter."""
    print("\n=== Testing list() with single label ===")

    unique_id = generate_unique_id()
    print(f"Using unique ID for test: {unique_id}")

    # Create 3 sessions concurrently with the same project label but different environments
    params_list = [
        CreateSessionParams(labels={
            "project": f"list-test-{unique_id}",
            "environment": "dev",
            "owner": f"test-{unique_id}",
        }),
        CreateSessionParams(labels={
            "project": f"list-test-{unique_id}",
            "environment": "staging",
            "owner": f"test-{unique_id}",
        }),
        CreateSessionParams(labels={
            "project": f"list-test-{unique_id}",
            "environment": "prod",
            "owner": f"test-{unique_id}",
        }),
    ]

    session_ids = []
    agent_bay = None
    for i, p in enumerate(params_list):
        lc = await make_session(params=p)
        if agent_bay is None:
            agent_bay = lc.agent_bay
        session_ids.append(lc._result.session.session_id)
        print(f"Session {i + 1} created: {lc._result.session.session_id}")

    # Wait for labels to propagate
    await asyncio.sleep(5)

    result = await agent_bay.list(labels={"project": f"list-test-{unique_id}"})

    assert result.success, "list() with single label should succeed"
    assert result.request_id is not None, "Request ID should be present"
    assert len(result.session_ids) >= 3, "Should find at least 3 sessions"

    # Verify all 3 test sessions appear in the results
    found_count = 0
    for item in result.session_ids:
        sid = item.get("sessionId") if isinstance(item, dict) else item
        if sid in session_ids:
            found_count += 1

    assert found_count == 3, f"Should find exactly 3 test sessions, found {found_count}"
    print(f"Found {found_count} test sessions")
    print(f"Total sessions with label: {len(result.session_ids)}")
    print(f"Request ID: {result.request_id}")


async def test_list_with_multiple_labels(make_session):
    """Test listing sessions with multiple label filters."""
    print("\n=== Testing list() with multiple labels ===")

    unique_id = generate_unique_id()
    print(f"Using unique ID for test: {unique_id}")

    # Create dev and staging sessions concurrently
    dev_lc, _ = await asyncio.gather(
        make_session(params=CreateSessionParams(labels={
            "project": f"list-test-{unique_id}",
            "environment": "dev",
            "owner": f"test-{unique_id}",
        })),
        make_session(params=CreateSessionParams(labels={
            "project": f"list-test-{unique_id}",
            "environment": "staging",
            "owner": f"test-{unique_id}",
        })),
    )

    agent_bay = dev_lc.agent_bay
    dev_session_id = dev_lc._result.session.session_id
    print(f"Dev session ID: {dev_session_id}")

    # Wait for labels to propagate
    await asyncio.sleep(5)

    result = await agent_bay.list(labels={
        "project": f"list-test-{unique_id}",
        "environment": "dev",
    })

    assert result.success, "list() with multiple labels should succeed"
    assert result.request_id is not None, "Request ID should be present"
    assert len(result.session_ids) >= 1, "Should find at least 1 session"

    found = False
    for item in result.session_ids:
        sid = item.get("sessionId") if isinstance(item, dict) else item
        print(f"Session ID: {sid}")
        if sid == dev_session_id:
            found = True
            break

    assert found, "Dev session should be in the results"
    print(f"Found dev session: {found}")
    print(f"Total matching sessions: {len(result.session_ids)}")
    print(f"Request ID: {result.request_id}")
