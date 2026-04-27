# ci-stable
"""Integration tests for session get_metrics API."""

import pytest

from agentbay import CreateSessionParams


@pytest.mark.asyncio
async def test_get_metrics_returns_structured_data(make_session):
    """Test that get_metrics returns valid structured data."""
    lc = await make_session()
    session = lc._result.session
    assert session is not None

    metrics_result = await session.get_metrics()
    assert metrics_result.success, f"get_metrics failed: {metrics_result.error_message}"
    assert metrics_result.metrics is not None

    m = metrics_result.metrics
    assert m.cpu_count >= 1
    assert m.mem_total > 0
    assert m.disk_total > 0
    assert m.cpu_used_pct >= 0.0
    assert m.cpu_used_pct <= 100.0
    assert len(m.timestamp) > 0
