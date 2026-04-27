# =============================================================================
# conftest.py  –  Shared fixtures for _async integration tests
#
# This file is loaded automatically by pytest; no explicit import is needed.
# It exposes the ``make_session`` factory fixture for every test file under
# the _async/ directory.
#
# Key capabilities:
#   - Wraps all three AsyncSessionLifecycle creation modes in one entry point:
#       default_create / create_with_context_name / create_with_browser_name
#   - Unified SessionLifecycleError handling:
#       "no authorized app"  → pytest.skip  (environment not authorised)
#       any other failure    → pytest.fail  (code / network issue)
#   - scope="function": each session is deleted immediately after its test
#     function finishes.
#
# When adding a new creation mode, update session_life_functional.py and add
# the corresponding branch in _factory; keep _sync/conftest.py in sync.
# =============================================================================
"""
Shared pytest fixtures for _async integration tests.

Provides a factory fixture ``make_session`` that creates an
AsyncSessionLifecycle instance on demand, supports all three creation modes
(default / context_name / browser_name), and cleans up all sessions when
the test function ends.

Usage::

    async def test_something(make_session):
        lc = await make_session("linux_latest")
        status = await lc.get_status()
        assert status

    async def test_browser(make_session):
        lc = await make_session("linux_latest", browser_name="ctx", browser_kwargs={"auto_upload": True})
        assert lc._result.session.session_id

    async def test_ctx_sync(make_session):
        lc = await make_session("linux_latest", context_name="ctx", context_path="/data", context_policy=my_policy)
        assert lc._result.session.session_id
"""

import asyncio
import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from .._common import AsyncSessionLifecycle, SessionLifecycleError


@pytest.fixture(scope="module")
def agent_bay_client() -> AsyncAgentBay:
    """Lightweight module-scoped fixture: constructs an AsyncAgentBay client
    without creating any cloud session.

    Use this fixture when a test only needs to call AgentBay-level APIs
    (e.g. ``get``, ``list``, ``create``, ``delete``, ``context.*``) directly,
    without going through the ``make_session`` factory.

    Typical use-cases:
      - Parameter validation tests (empty / whitespace session IDs)
      - Tests that create and manage sessions manually via ``agent_bay_client.create()``
      - Tests that need ``agent_bay`` alongside a ``make_session``-managed session
        (access ``lc.agent_bay`` instead for those cases)

    Skips automatically when ``AGENTBAY_API_KEY`` is not set.
    """
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable is not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture(scope="function")
async def make_session():
    """
    Factory fixture: create an AsyncSessionLifecycle with any imageId and
    creation mode.  All sessions created through this factory are
    automatically deleted when the test function ends.

    Args passed to the factory callable:
        image_id (str): Required.  The image ID to create the session with.
        context_name (str): Optional context name for create_with_context_name.
        context_path (str): Optional path for create_with_context_name.
        context_policy: Required SyncPolicy when context_name is provided.
        browser_name (str): Optional context name for create_with_browser_name.
        browser_kwargs (dict): Optional kwargs forwarded to BrowserContext.

    Returns:
        AsyncSessionLifecycle with a cached session result.

    Raises (inside the factory):
        pytest.skip  – when "no authorized app" is in the error message.
        pytest.fail  – for all other creation failures.
    """
    created: list[AsyncSessionLifecycle] = []

    async def _factory(image_id: str = None, *, params=None, context_name=None, context_path=None, context_policy=None, browser_name=None, browser_kwargs=None):
        lc = AsyncSessionLifecycle()
        try:
            if context_name is not None:
                await lc.create_with_context_name(image_id, context_name, path=context_path or "", policy=context_policy)
            elif browser_name is not None:
                await lc.create_with_browser_name(image_id, browser_name, **(browser_kwargs or {}))
            else:
                await lc.default_create(image_id, params=params)
        except SessionLifecycleError as e:
            if "no authorized app" in str(e):
                pytest.skip(str(e))
            pytest.fail(str(e))
        created.append(lc)
        return lc

    yield _factory

    # Teardown: clean up all sessions and contexts created during this test function concurrently
    async def _delete_one(lc: AsyncSessionLifecycle):
        try:
            result = await lc.delete()
            assert result.success, f"Session delete failed: {result.error_message}"
        except SessionLifecycleError as e:
            print(f"Warning: teardown delete failed: {e}")
        await lc.delete_all_contexts()

    await asyncio.gather(*(_delete_one(lc) for lc in created))
