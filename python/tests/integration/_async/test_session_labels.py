# ci-stable
import random
import time

import pytest

from agentbay import CreateSessionParams


def _generate_unique_id():
    """Create a unique identifier for test labels to avoid conflicts with existing data."""
    timestamp = int(time.time() * 1000000)
    random_part = random.randint(0, 10000)
    return f"{timestamp}-{random_part}"


@pytest.mark.asyncio
async def test_set_get_labels(make_session):
    """Test setting and getting labels for a session."""
    lc = await make_session()
    session = lc._result.session

    unique_id = _generate_unique_id()
    test_labels = {
        "environment": f"testing-{unique_id}",
        "owner": f"test-team-{unique_id}",
        "project": f"labels-test-{unique_id}",
        "version": "1.0.0",
    }

    # Test 1: Set labels using set_labels
    print("Setting labels for the session...")
    set_result = await session.set_labels(test_labels)
    assert set_result.success, "Failed to set labels"
    print(f"Labels set successfully. Request ID: {set_result.request_id}")

    # Test 2: Get labels using get_labels
    print("Getting labels for the session...")
    get_result = await session.get_labels()
    print(f"Retrieved labels: {get_result.data}")
    print(f"Request ID: {get_result.request_id}")

    retrieved_labels = get_result.data
    for key, expected_value in test_labels.items():
        assert key in retrieved_labels, f"Expected label '{key}' not found in retrieved labels"
        assert expected_value == retrieved_labels[key], (
            f"Label '{key}' value mismatch: expected '{expected_value}' got '{retrieved_labels[key]}'"
        )


@pytest.mark.asyncio
async def test_empty_labels_handling(make_session):
    """2.4 Empty labels handling test - should handle setting empty labels object."""
    lc = await make_session()
    session = lc._result.session

    empty_labels = {}
    set_result = await session.set_labels(empty_labels)

    # Verification points - based on validation logic, empty labels should fail
    assert not set_result.success
    assert "empty" in set_result.error_message.lower()
    print("Empty labels handled correctly")


@pytest.mark.asyncio
async def test_set_labels_invalid_parameters(make_session):
    """5.1 setLabels invalid parameter handling test - should handle invalid parameters."""
    lc = await make_session()
    session = lc._result.session

    # Test None parameter
    null_result = await session.set_labels(None)
    print(f"Null result: {null_result}")
    assert not null_result.success
    assert "null" in null_result.error_message.lower()
    assert null_result.request_id == ""
    print("setLabels invalid parameters: All invalid parameter types correctly rejected")
