"""
ci-stable
Integration test for AsyncComputer.beta_take_screenshot().

This test uses real backend resources (no mocks).
"""

import pytest

from agentbay import CreateSessionParams


@pytest.fixture
async def session(make_session):
    lc = await make_session(params=CreateSessionParams(image_id="linux_latest"))
    return lc._result.session


@pytest.mark.asyncio
async def test_take_screenshot_jpg_returns_jpeg_bytes(session):
    """
    Verify jpg format works (normalized to jpeg), and returns non-empty bytes.
    """
    result = await session.computer.beta_take_screenshot(format="jpg")
    assert result.success is True
    assert isinstance(result.type, str)
    assert result.type.strip()
    assert result.mime_type == "image/jpeg"
    assert isinstance(result.width, int)
    assert isinstance(result.height, int)
    assert result.width > 0
    assert result.height > 0
    assert isinstance(result.data, (bytes, bytearray))
    assert len(result.data) > 0
    assert bytes(result.data[:3]) == b"\xff\xd8\xff"
