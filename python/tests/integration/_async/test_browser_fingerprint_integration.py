#!/usr/bin/env python3
"""
Integration test for browser fingerprint functionality.
This test verifies that browser fingerprint can be persisted
across sessions using the same ContextId and FingerprintContextId.
"""

import time
import pytest

from playwright.async_api import async_playwright

from agentbay import CreateSessionParams
from agentbay import (
    BrowserFingerprint,
    BrowserFingerprintContext,
    BrowserOption,
)
from agentbay import AsyncBrowserFingerprintGenerator

from tests.integration._common.session_life_functional import (
    AsyncSessionLifecycle,
    SessionLifecycleError,
)


def is_windows_user_agent(user_agent: str) -> bool:
    if not user_agent:
        return False
    user_agent_lower = user_agent.lower()
    windows_indicators = ["windows nt", "win32", "win64", "windows", "wow64"]
    return any(indicator in user_agent_lower for indicator in windows_indicators)

def is_linux_user_agent(user_agent: str) -> bool:
    if not user_agent:
        return False
    user_agent_lower = user_agent.lower()
    linux_indicators = ["linux", "ubuntu", "debian", "fedora", "centos", "red hat"]
    return any(indicator in user_agent_lower for indicator in linux_indicators)


@pytest.fixture(scope="class")
async def lifecycle():
    """Lifecycle fixture: owns the AgentBay client and all created contexts."""
    try:
        lc = AsyncSessionLifecycle()
    except SessionLifecycleError as e:
        pytest.skip(str(e))

    yield lc

    # Cleanup all contexts created during the test class
    await lc.delete_all_contexts()


@pytest.mark.asyncio
class TestBrowserFingerprintIntegration:
    """Integration tests for browser fingerprint persistence functionality."""

    @pytest.mark.asyncio
    async def test_browser_fingerprint_basic_usage(self, lifecycle: AsyncSessionLifecycle):
        print("===== Test browser fingerprint basic usage =====")

        result = await lifecycle.default_create("browser_latest")
        session = result.session
        print(f"Session created with ID: {session.session_id}")

        try:
            # Initialize browser with fingerprint options
            browser_option = BrowserOption(
                use_stealth=True,
                fingerprint=BrowserFingerprint(
                    devices=["desktop"],
                    operating_systems=["windows"],
                    locales=["zh-CN"],
                ),
            )
            init_success = await session.browser.initialize(browser_option)
            assert init_success, "Failed to initialize browser"
            print("Browser initialized successfully")

            # Get endpoint URL
            endpoint_url = await session.browser.get_endpoint_url()
            assert endpoint_url is not None, "Endpoint URL should not be None"
            print(f"Browser endpoint URL: {endpoint_url}")

            # Connect with playwright and test user agent
            print("Opening https://httpbin.org/user-agent and test user agent...")
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                assert browser is not None, "Failed to connect to browser"
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )

                page = await context.new_page()
                await page.goto("https://httpbin.org/user-agent", timeout=60000)

                # Wait for page to load and try different selectors
                await page.wait_for_load_state("networkidle", timeout=30000)

                # Try to get the response text using different methods
                response_text = None
                try:
                    response_text = await page.evaluate("() => document.querySelector('pre')?.textContent")
                except Exception:
                    pass

                if not response_text:
                    try:
                        response_text = await page.evaluate("() => document.body.textContent")
                    except Exception:
                        pass

                if not response_text:
                    response_text = await page.content()

                print(f"Response text: {response_text[:200]}...")

                import json
                import re
                json_match = re.search(r'\{[^}]+\}', response_text)
                if json_match:
                    response = json.loads(json_match.group())
                    user_agent = response.get("user-agent")
                else:
                    user_agent = response_text.strip()
                print("user_agent =", user_agent)
                assert user_agent is not None
                assert is_windows_user_agent(user_agent)

                await context.close()
                print("Browser fingerprint test completed")
        finally:
            delete_result = await lifecycle.delete()
            assert delete_result.success, "Failed to delete session"
            print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

    @pytest.mark.asyncio
    async def test_browser_fingerprint_persistence(self, lifecycle: AsyncSessionLifecycle):
        """Test browser fingerprint persist across sessions with the same browser and fingerprint context."""
        print("===== Test browser fingerprint persistence =====")

        agent_bay = lifecycle.agent_bay

        # Create browser context and fingerprint context via lifecycle (tracked for cleanup)
        browser_ctx = await lifecycle.create_context(
            f"test-browser-context-{int(time.time())}"
        )
        fingerprint_ctx = await lifecycle.create_context(
            f"test-browser-fingerprint-{int(time.time())}"
        )

        # Step 1: Create session with BrowserContext and FingerprintContext
        print(
            f"Step 1: Creating session with browser context ID: {browser_ctx.id} "
            f"and fingerprint context ID: {fingerprint_ctx.id}"
        )
        from agentbay import BrowserContext
        fp_context = BrowserFingerprintContext(fingerprint_ctx.id)
        br_context = BrowserContext(
            browser_ctx.id, auto_upload=True, fingerprint_context=fp_context
        )
        params1 = CreateSessionParams(
            image_id="browser_latest", browser_context=br_context
        )

        session_result = await agent_bay.create(params1)
        assert session_result.success, "Failed to create first session"
        assert session_result.session is not None, "Session should not be None"

        session1 = session_result.session
        print(f"First session created with ID: {session1.session_id}")

        # Step 2: Initialize first browser and generate fingerprint for persistence
        print(
            "Step 2: Initializing first browser and generate fingerprint for persistence..."
        )
        browser_option1 = BrowserOption(
            use_stealth=True,
            fingerprint_persistent=True,
            fingerprint=BrowserFingerprint(
                devices=["desktop"],
                operating_systems=["windows"],
                locales=["zh-CN"],
            ),
        )
        init_success = await session1.browser.initialize(browser_option1)
        assert init_success, "Failed to initialize browser"
        print("Browser initialized successfully")

        endpoint_url = await session1.browser.get_endpoint_url()
        assert endpoint_url is not None, "Endpoint URL should not be None"
        print(f"Browser endpoint URL: {endpoint_url}")

        # Step 3: Connect with playwright, test first session fingerprint
        print("Step 3: Opening https://httpbin.org/user-agent and test user agent...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                print(f"Browser connected to endpoint URL: {browser.contexts}")
                assert browser is not None, "Failed to connect to browser"
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )

                page = await context.new_page()
                await page.goto("https://httpbin.org/user-agent", timeout=60000)
                response = await page.evaluate(
                    "() => JSON.parse(document.querySelector('pre').textContent)"
                )
                user_agent = response["user-agent"]
                print("user_agent =", user_agent)
                assert user_agent is not None
                assert is_windows_user_agent(user_agent)

                await context.close()
                print("First session browser operations completed")

        finally:
            try:
                print("Step 4: Releasing first session with syncContext=True...")
                delete_result = await agent_bay.delete(session1, sync_context=True)
                if not delete_result.success:
                    print(f"Warning: Failed to delete first session (RequestID: {delete_result.request_id})")
                else:
                    print(f"First session deleted successfully (RequestID: {delete_result.request_id})")
            except Exception as e:
                print(f"Warning: Exception while deleting session: {e}")

        # Wait for context sync to complete
        time.sleep(3)

        # Step 5: Create second session with same browser context and fingerprint context
        print(
            f"Step 5: Creating second session with same browser context ID: {browser_ctx.id} "
            f"and fingerprint context ID: {fingerprint_ctx.id}"
        )
        params2 = CreateSessionParams(
            image_id="browser_latest", browser_context=br_context
        )
        session_result2 = await agent_bay.create(params2)
        assert session_result2.success, "Failed to create second session"
        assert session_result2.session is not None, "Second session should not be None"

        session2 = session_result2.session
        print(f"Second session created with ID: {session2.session_id}")

        # Step 6: Check if second session fingerprint is the same as first session
        print("Step 6: Get browser object and check if second session fingerprint is the same as first session...")
        browser_option2 = BrowserOption(
            use_stealth=True,
            fingerprint_persistent=True,
        )
        init_success = await session2.browser.initialize(browser_option2)
        assert init_success, "Failed to initialize browser in second session"
        print("Second session browser initialized successfully")

        endpoint_url = await session2.browser.get_endpoint_url()
        assert endpoint_url is not None, "Endpoint URL should not be None"
        print(f"Second session browser endpoint URL: {endpoint_url}")

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            assert browser is not None, "Failed to connect to browser in second session"

            context = (
                browser.contexts[0]
                if browser.contexts
                else await browser.new_context()
            )
            page = await context.new_page()
            await page.goto("https://httpbin.org/user-agent", timeout=60000)
            response = await page.evaluate(
                "() => JSON.parse(document.querySelector('pre').textContent)"
            )
            user_agent = response["user-agent"]
            print("user_agent =", user_agent)
            assert user_agent is not None
            assert is_linux_user_agent(user_agent), f"Expected Windows user agent, got: {user_agent}"
            print(f"SUCCESS: fingerprint persisted correctly!")

            await context.close()
            print("Second session browser operations completed")

        # Step 7: Release second session with syncContext=True
        print("Step 7: Releasing second session with syncContext=True...")
        delete_result = await agent_bay.delete(session2, sync_context=True)
        assert delete_result.success, "Failed to delete second session"
        print(f"Second session deleted successfully (RequestID: {delete_result.request_id})")

        print("Browser fingerprint persistence test completed successfully!")

    @pytest.mark.asyncio
    async def test_browser_fingerprint_local_sync(self, lifecycle: AsyncSessionLifecycle):
        """Test browser fingerprint local sync functionality."""
        print("===== Test browser fingerprint local sync =====")

        result = await lifecycle.default_create("browser_latest")
        session = result.session
        print(f"Session created with ID: {session.session_id}")

        try:
            # Generate local chrome browser fingerprint
            print("Dumping local chrome browser fingerprint...")
            fingerprint_generator = AsyncBrowserFingerprintGenerator(headless=True)
            fingerprint_format = await fingerprint_generator.generate_fingerprint()
            assert fingerprint_format is not None, "Fingerprint format should not be None"
            print("Local fingerprint generated successfully")

            browser_option = BrowserOption(
                use_stealth=True, fingerprint_format=fingerprint_format
            )
            init_success = await session.browser.initialize(browser_option)
            assert init_success, "Failed to initialize browser"
            print("Browser initialized successfully with local fingerprint")

            endpoint_url = await session.browser.get_endpoint_url()
            assert endpoint_url is not None, "Endpoint URL should not be None"
            print(f"Browser endpoint URL: {endpoint_url}")

            print("Testing fingerprint sync by checking user agent...")
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                assert browser is not None, "Failed to connect to browser"
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )

                page = await context.new_page()
                await page.goto("https://httpbin.org/user-agent", timeout=60000)
                await page.wait_for_load_state("networkidle", timeout=30000)

                response_text = None
                try:
                    response_text = await page.evaluate("() => document.querySelector('pre')?.textContent")
                except Exception:
                    pass

                if not response_text:
                    try:
                        response_text = await page.evaluate("() => document.body.textContent")
                    except Exception:
                        pass

                if not response_text:
                    response_text = await page.content()

                print(f"Response text: {response_text[:200]}...")

                import json
                import re
                json_match = re.search(r'\{[^}]+\}', response_text)
                if json_match:
                    response = json.loads(json_match.group())
                    user_agent = response.get("user-agent")
                else:
                    user_agent = response_text.strip()
                print(f"Remote user agent: {user_agent}")
                print(f"Local user agent: {fingerprint_format.fingerprint.navigator.userAgent}")

                assert (
                    user_agent == fingerprint_format.fingerprint.navigator.userAgent
                ), "User agent should match between local and remote"
                print("SUCCESS: Local fingerprint synced correctly to remote browser!")

                await context.close()
                print("Local sync test completed")
        finally:
            delete_result = await lifecycle.delete()
            assert delete_result.success, "Failed to delete session"
            print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

        print("Browser fingerprint local sync test completed successfully!")

    @pytest.mark.asyncio
    async def test_browser_fingerprint_construct(self, lifecycle: AsyncSessionLifecycle):
        """Test browser fingerprint construction from file."""
        print("===== Test browser fingerprint construct =====")

        import os
        result = await lifecycle.default_create("browser_latest")
        session = result.session
        print(f"Session created with ID: {session.session_id}")

        try:
            # Load fingerprint from example file
            print("Loading fingerprint from example file...")
            from agentbay import FingerprintFormat

            example_file_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                    )
                ),
                "resource",
                "fingerprint.example.json",
            )

            with open(example_file_path, "r") as f:
                fingerprint_json = f.read()

            fingerprint_format = FingerprintFormat.load(fingerprint_json)
            assert fingerprint_format is not None, "Fingerprint format should not be None"
            print("Fingerprint loaded from file successfully")

            browser_option = BrowserOption(
                use_stealth=True, fingerprint_format=fingerprint_format
            )
            init_success = await session.browser.initialize(browser_option)
            assert init_success, "Failed to initialize browser"
            print("Browser initialized successfully with constructed fingerprint")

            endpoint_url = await session.browser.get_endpoint_url()
            assert endpoint_url is not None, "Endpoint URL should not be None"
            print(f"Browser endpoint URL: {endpoint_url}")

            print("Testing constructed fingerprint by checking user agent...")
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                assert browser is not None, "Failed to connect to browser"
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )

                page = await context.new_page()
                await page.goto("https://httpbin.org/user-agent", timeout=60000)
                await page.wait_for_load_state("networkidle", timeout=30000)

                response_text = None
                try:
                    response_text = await page.evaluate("() => document.querySelector('pre')?.textContent")
                except Exception:
                    pass

                if not response_text:
                    try:
                        response_text = await page.evaluate("() => document.body.textContent")
                    except Exception:
                        pass

                if not response_text:
                    response_text = await page.content()

                print(f"Response text: {response_text[:200]}...")

                import json
                import re
                json_match = re.search(r'\{[^}]+\}', response_text)
                if json_match:
                    response = json.loads(json_match.group())
                    user_agent = response.get("user-agent")
                else:
                    user_agent = response_text.strip()
                print(f"Remote user agent: {user_agent}")
                print(f"Expected user agent: {fingerprint_format.fingerprint.navigator.userAgent}")

                assert (
                    user_agent == fingerprint_format.fingerprint.navigator.userAgent
                ), "User agent should match the constructed fingerprint"
                print("SUCCESS: Fingerprint constructed correctly from file!")

                await context.close()
                print("Construct test completed")
        finally:
            delete_result = await lifecycle.delete()
            assert delete_result.success, "Failed to delete session"
            print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

        print("Browser fingerprint construct test completed successfully!")
