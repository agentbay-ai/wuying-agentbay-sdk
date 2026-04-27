#!/usr/bin/env python3
"""
Integration test for browser context functionality.
This test verifies that browser context (cookies, localStorage, etc.) can be persisted
across sessions using the same ContextId.
"""

# ci-stable

import asyncio
import time

import pytest
from playwright.async_api import async_playwright

from agentbay import BrowserOption

from tests.integration._common.session_life_functional import (
    AsyncSessionLifecycle,
    SessionLifecycleError,
)

# agent_bay_client fixture (AsyncAgentBay, scope="module") is provided by conftest.py


@pytest.fixture(scope="module")
async def browser_context_fixture():
    """Create and cleanup a browser context for the test module."""
    try:
        lc = AsyncSessionLifecycle()
    except SessionLifecycleError as e:
        pytest.skip(str(e))

    context_name = f"test-browser-context-{int(time.time())}"
    try:
        context = await lc.create_context(context_name)
    except SessionLifecycleError as e:
        pytest.skip(f"Failed to create context: {e}")

    print(f"Created context: {context.name} (ID: {context.id})")

    yield lc, context

    await lc.delete_all_contexts()


@pytest.mark.asyncio
async def test_browser_context_cookie_persistence(browser_context_fixture, make_session):
    """Test that manually set cookies persist across sessions with the same browser context."""
    lc, context = browser_context_fixture

    # Test data
    test_url = "https://www.baidu.com"
    test_domain = "baidu.com"

    def add_hour():
        return int(time.time()) + 3600  # 1 hour from now

    test_cookies = [
        {
            "name": "myCookie",
            "value": "cookieValue",
            "domain": test_domain,
            "path": "/",
            "httpOnly": False,
            "secure": False,
            "expires": add_hour(),
        },
        {
            "name": "test_cookie_2",
            "value": "test_value_2",
            "domain": test_domain,
            "path": "/",
            "httpOnly": False,
            "secure": False,
            "expires": add_hour(),
        },
    ]

    # Step 1 & 2: Create first session with BrowserContext via make_session
    print(f"Step 1-2: Creating first session with browser context ID: {context.id}")
    lc1 = await make_session(
        "browser_latest",
        browser_name=context.name,
        browser_kwargs={"auto_upload": True},
    )
    session1 = lc1._result.session
    print(f"First session created with ID: {session1.session_id}")

    # Step 3: Initialize browser and get endpoint URL
    print("Step 3: Initializing browser and getting browser object...")
    init_success = await session1.browser.initialize(BrowserOption())
    assert init_success, "Failed to initialize browser"
    print("Browser initialized successfully")

    endpoint_url = await session1.browser.get_endpoint_url()
    assert endpoint_url is not None, "Endpoint URL should not be None"
    print(f"Browser endpoint URL: {endpoint_url}")

    # Step 4: Connect with playwright, open baidu.com and then add test cookies
    print("Step 4: Opening baidu.com and then adding test cookies...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert browser is not None, "Failed to connect to browser"
        cdp_session = await browser.new_browser_cdp_session()

        pw_context = (
            browser.contexts[0]
            if browser.contexts
            else await browser.new_context()
        )
        page = await pw_context.new_page()

        # Navigate to test URL first
        await page.goto(test_url, timeout=60000)
        print(f"Navigated to {test_url}")

        # Wait a bit for the page to load
        await page.wait_for_timeout(3000)

        # Add test cookies after navigating to the page
        await pw_context.add_cookies(test_cookies)  # type: ignore
        print(f"Added {len(test_cookies)} test cookies after navigating to {test_url}")

        # Read cookies to verify they were set correctly
        cookies = await pw_context.cookies()
        cookie_dict = {
            cookie.get("name", ""): cookie.get("value", "")
            for cookie in cookies
        }
        print(f"Cookies found in first session: {list(cookie_dict.keys())}")
        print(f"Total cookies count: {len(cookies)}")

        await cdp_session.send("Browser.close")
        print("First session browser operations completed")

        # Wait for browser to save cookies to file
        print("Waiting for browser to save cookies to file...")
        await asyncio.sleep(2)
        print("Wait completed")

    # Step 5: make_session teardown will handle deletion with sync_context=True
    # (browser_name session automatically sets _sync_context=True in lifecycle)
    # We trigger it manually here so session2 can reuse the same context
    print("Step 5: Releasing first session with syncContext=True...")
    delete_result = await lc1.delete()
    assert delete_result.success, "Failed to delete first session"
    print(f"First session deleted successfully")

    # Wait for context sync to complete
    await asyncio.sleep(3)

    # Step 6: Create second session with same context via make_session
    print(f"Step 6: Creating second session with same context ID: {context.id}")
    lc2 = await make_session(
        "browser_latest",
        browser_name=context.name,
        browser_kwargs={"auto_upload": True},
    )
    session2 = lc2._result.session
    print(f"Second session created with ID: {session2.session_id}")

    # Step 7: Initialize browser and check cookie persistence
    print("Step 7: Getting browser object and checking test cookie persistence...")
    init_success = await session2.browser.initialize(BrowserOption())
    assert init_success, "Failed to initialize browser in second session"
    print("Second session browser initialized successfully")

    endpoint_url = await session2.browser.get_endpoint_url()
    assert endpoint_url is not None, "Endpoint URL should not be None"
    print(f"Second session browser endpoint URL: {endpoint_url}")

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert browser is not None, "Failed to connect to browser in second session"

        pw_context = (
            browser.contexts[0]
            if browser.contexts
            else await browser.new_context()
        )

        # Read cookies directly from context without opening any page
        cookies = await pw_context.cookies()
        cookie_dict = {
            cookie.get("name", ""): cookie.get("value", "")
            for cookie in cookies
        }

        print(f"Cookies found in second session (without opening page): {list(cookie_dict.keys())}")
        print(f"Total cookies count in second session: {len(cookies)}")

        # Check if our test cookies exist in the second session
        expected_cookie_names = {"myCookie", "test_cookie_2"}
        found_cookie_names = set(cookie_dict.keys())

        print(f"Expected test cookies: {expected_cookie_names}")
        print(f"Found cookies: {found_cookie_names}")

        missing_cookies = expected_cookie_names - found_cookie_names
        assert not missing_cookies, (
            f"Missing expected test cookies in second session: {missing_cookies}"
        )

        for cookie_name in expected_cookie_names:
            if cookie_name in cookie_dict:
                expected_value = next(
                    cookie["value"]
                    for cookie in test_cookies
                    if cookie["name"] == cookie_name
                )
                actual_value = cookie_dict[cookie_name]
                assert expected_value == actual_value, (
                    f"Test cookie '{cookie_name}' value should match. "
                    f"Expected: {expected_value}, Actual: {actual_value}"
                )
                print(f"✓ Test cookie '{cookie_name}' value matches: {actual_value}")

        print(f"SUCCESS: All {len(expected_cookie_names)} test cookies persisted correctly!")

    # Step 8: Delete second session (make_session teardown also handles this,
    # but we do it explicitly to ensure sync_context=True ordering)
    print("Step 8: Releasing second session with syncContext=True...")
    delete_result = await lc2.delete()
    assert delete_result.success, "Failed to delete second session"
    print(f"Second session deleted successfully")

    print("Browser context manual cookie persistence test completed successfully!")
