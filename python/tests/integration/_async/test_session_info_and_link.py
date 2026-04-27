# ci-stable
"""Integration tests for session info and get_link APIs."""

import pytest

from agentbay import CreateSessionParams
from agentbay import SessionError
from agentbay import AsyncSession
import typing


@pytest.mark.asyncio
async def test_info(make_session):
    """Test session.info() returns expected fields."""
    params = CreateSessionParams(image_id="browser_latest")
    lc = await make_session(params=params)
    session: AsyncSession = typing.cast(AsyncSession, lc._result.session)

    print("Calling session.info()...")
    result = await session.info()
    assert result.success, "session.info() did not succeed"
    info = result.data
    print(f"SessionInfo: {info.__dict__}")
    assert hasattr(info, "session_id")
    assert info.session_id
    assert hasattr(info, "resource_url")
    assert info.resource_url
    assert hasattr(info, "ticket")
    # ticket may be empty depending on backend, but should exist
    assert hasattr(info, "app_id")
    assert hasattr(info, "auth_code")
    assert hasattr(info, "connection_properties")
    assert hasattr(info, "resource_id")
    assert hasattr(info, "resource_type")


@pytest.mark.asyncio
async def test_get_link(make_session):
    """Test session.get_link() returns a valid URL."""
    params = CreateSessionParams(image_id="browser_latest")
    lc = await make_session(params=params)
    session: AsyncSession = typing.cast(AsyncSession, lc._result.session)

    print("Calling session.get_link()...")
    result = await session.get_link()
    assert result.success, "session.get_link() did not succeed"
    url = result.data
    print(f"Session link URL: {url}")
    assert isinstance(url, str)
    assert (
        url.startswith("http") or url.startswith("wss") or url.startswith("ws")
    ), "Returned link does not look like a URL"


@pytest.mark.asyncio
async def test_get_link_with_valid_port(make_session):
    """Test session.get_link() with valid port returns a valid URL."""
    params = CreateSessionParams(image_id="browser_latest")
    lc = await make_session(params=params)
    session: AsyncSession = typing.cast(AsyncSession, lc._result.session)

    print("Calling session.get_link()...")
    result = await session.get_link()
    assert result.success, "session.get_link() did not succeed"
    url = result.data
    print(f"Session link URL: {url}")
    assert isinstance(url, str)
    assert (
        url.startswith("http") or url.startswith("wss") or url.startswith("ws")
    ), "Returned link does not look like a URL"

    # Test with port in valid range [30100, 30199]
    valid_ports = [30100, 30150, 30199]
    for port in valid_ports:
        print(f"Calling session.get_link() with port {port}...")
        result = await session.get_link(port=port)
        assert result.success, f"session.get_link(port={port}) did not succeed"
        url = result.data
        print(f"Session link URL with port {port}: {url}")
        assert isinstance(url, str)
        assert (
            url.startswith("http")
            or url.startswith("wss")
            or url.startswith("ws")
        ), f"Returned link with port {port} does not look like a URL"


@pytest.mark.asyncio
async def test_get_link_with_invalid_port_below_range(make_session):
    """Test session.get_link() with port below valid range raises SessionError."""
    params = CreateSessionParams(image_id="browser_latest")
    lc = await make_session(params=params)
    session: AsyncSession = typing.cast(AsyncSession, lc._result.session)

    invalid_port = 30099
    print(f"Calling session.get_link() with invalid port {invalid_port}...")
    with pytest.raises(SessionError):
        await session.get_link(port=invalid_port)
    print(f"Expected SessionError raised for port {invalid_port}")


@pytest.mark.asyncio
async def test_get_link_with_invalid_port_above_range(make_session):
    """Test session.get_link() with port above valid range raises SessionError."""
    params = CreateSessionParams(image_id="browser_latest")
    lc = await make_session(params=params)
    session: AsyncSession = typing.cast(AsyncSession, lc._result.session)

    invalid_port = 30200
    print(f"Calling session.get_link() with invalid port {invalid_port}...")
    with pytest.raises(SessionError):
        await session.get_link(port=invalid_port)
    print(f"Expected SessionError raised for port {invalid_port}")


@pytest.mark.asyncio
async def test_get_link_with_invalid_port_non_integer(make_session):
    """Test session.get_link() with non-integer port raises SessionError."""
    params = CreateSessionParams(image_id="browser_latest")
    lc = await make_session(params=params)
    session: AsyncSession = typing.cast(AsyncSession, lc._result.session)

    invalid_port = 30150.5
    print(f"Calling session.get_link() with non-integer port {invalid_port}...")
    with pytest.raises(SessionError):
        await session.get_link(port=invalid_port)
    print(f"Expected SessionError raised for port {invalid_port}")
