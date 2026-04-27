"""
Integration tests for AsyncMobile beta screenshot APIs.

These tests use real backend resources (no mocks).
"""

import asyncio

import pytest
import pytest_asyncio

from agentbay import CreateSessionParams


async def _set_low_android_resolution(session) -> None:
    """
    Reduce Android resolution to make screenshots smaller for tests.
    """
    cmds = [
        "wm size 720x1280",
        "wm density 160",
    ]
    for cmd in cmds:
        r = await session.command.execute_command(cmd)
        assert r.success, f"Command failed: {cmd} error={r.error_message}"


async def _prepare_for_screenshot_tests(session) -> None:
    await _set_low_android_resolution(session)
    start = await session.mobile.start_app("monkey -p com.android.settings 1")
    assert start.success, f"Failed to start Settings: {start.error_message}"
    await asyncio.sleep(2)


@pytest_asyncio.fixture
async def session(make_session):
    params = CreateSessionParams(image_id="mobile-use-android-12-gw")
    lc = await make_session(params=params)
    session = lc._result.session
    # Force API-based MCP tool calls (no LinkUrl direct calls) for test stability.
    # Some environments cannot reach the sandbox LinkUrl network path from CI/dev machines.
    session.mcpTools = []
    return session


@pytest.mark.asyncio
async def test_mobile_beta_take_screenshot_png(session):
    await _prepare_for_screenshot_tests(session)
    result = await session.mobile.beta_take_screenshot()
    assert result.success is True
    assert isinstance(result.type, str)
    assert result.type.strip()
    assert result.mime_type == "image/png"
    assert isinstance(result.width, int)
    assert isinstance(result.height, int)
    assert result.width > 0
    assert result.height > 0
    assert isinstance(result.data, (bytes, bytearray))
    assert len(result.data) > 0
    assert bytes(result.data[:8]) == b"\x89PNG\r\n\x1a\n"


@pytest.mark.asyncio
async def test_mobile_beta_take_screenshot_jpeg(session):
    await _prepare_for_screenshot_tests(session)
    result = await session.mobile.beta_take_screenshot(format="jpeg")
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


@pytest.mark.asyncio
async def test_mobile_beta_take_long_screenshot_png(session):
    await _prepare_for_screenshot_tests(session)
    result = await session.mobile.beta_take_long_screenshot(max_screens=2, format="png")
    assert result.success is True
    assert isinstance(result.type, str)
    assert result.type.strip()
    assert result.mime_type == "image/png"
    assert isinstance(result.width, int)
    assert isinstance(result.height, int)
    assert result.width > 0
    assert result.height > 0
    assert isinstance(result.data, (bytes, bytearray))
    assert len(result.data) > 0
    assert bytes(result.data[:8]) == b"\x89PNG\r\n\x1a\n"


@pytest.mark.asyncio
async def test_mobile_beta_take_long_screenshot_jpeg_quality(session):
    await _prepare_for_screenshot_tests(session)

    with pytest.raises(ValueError, match=r"Invalid quality: must be an integer in \[1, 100\]"):
        await session.mobile.beta_take_long_screenshot(
            max_screens=2,
            format="jpeg",
            quality=0,
        )

    high = await session.mobile.beta_take_long_screenshot(
        max_screens=2,
        format="jpeg",
        quality=95,
    )
    low = await session.mobile.beta_take_long_screenshot(
        max_screens=2,
        format="jpeg",
        quality=10,
    )

    assert high.success is True
    assert isinstance(high.type, str)
    assert high.type.strip()
    assert high.mime_type == "image/jpeg"
    assert isinstance(high.width, int)
    assert isinstance(high.height, int)
    assert high.width > 0
    assert high.height > 0
    assert isinstance(high.data, (bytes, bytearray))
    assert len(high.data) > 0
    assert bytes(high.data[:3]) == b"\xff\xd8\xff"

    assert low.success is True
    assert isinstance(low.type, str)
    assert low.type.strip()
    assert low.mime_type == "image/jpeg"
    assert isinstance(low.width, int)
    assert isinstance(low.height, int)
    assert low.width > 0
    assert low.height > 0
    assert isinstance(low.data, (bytes, bytearray))
    assert len(low.data) > 0
    assert bytes(low.data[:3]) == b"\xff\xd8\xff"

    assert len(high.data) > len(low.data)

