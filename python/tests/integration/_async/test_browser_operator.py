"""Integration tests for Browser Operator functionality."""

import asyncio
import os
import random
import re
import time

import pytest
from playwright.async_api import async_playwright
from pydantic import BaseModel

from agentbay._async.browser_operator import ActOptions, ExtractOptions, ObserveOptions
from agentbay import BrowserFingerprint, BrowserOption, BrowserProxy


class DummySchema(BaseModel):
    """Schema for extract test."""

    title: str


def _mask_secret(secret: str, visible: int = 4) -> str:
    """Mask a secret value, keeping only the last `visible` characters."""
    if not secret:
        return ""
    if len(secret) <= visible:
        return "*" * len(secret)
    return ("*" * (len(secret) - visible)) + secret[-visible:]


def is_windows_user_agent(user_agent: str) -> bool:
    if not user_agent:
        return False
    user_agent_lower = user_agent.lower()
    windows_indicators = ["windows nt", "win32", "win64", "windows", "wow64"]
    return any(indicator in user_agent_lower for indicator in windows_indicators)


@pytest.fixture
async def browser_session(make_session):
    """Create a browser session for operator testing."""
    api_key = os.environ.get("AGENTBAY_API_KEY", "")
    print(f"api_key = {_mask_secret(api_key)}")
    print("Creating a new session for browser operator testing...")
    lc = await make_session("browser_latest")
    session = lc._result.session
    print(f"Session created with ID: {session.session_id}")
    return session


@pytest.mark.asyncio
async def test_initialize_browser(browser_session):
    browser = browser_session.browser
    assert browser is not None

    # Use default options with optimized settings for faster testing
    option = BrowserOption()
    option.headless = True  # Run in headless mode for faster execution
    init_result = await browser.initialize(option)
    assert init_result is True

    endpoint_url = await browser.get_endpoint_url()
    print("endpoint_url =", endpoint_url)
    assert endpoint_url is not None

    await asyncio.sleep(1)

    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None

        page = await playwright_browser.new_page()
        await page.goto("http://www.baidu.com")
        title = await page.title()
        print("page.title() =", title)

        assert title is not None
        await page.close()
        await playwright_browser.close()


@pytest.mark.asyncio
async def test_initialize_browser_with_fingerprint(browser_session):
    """Test browser initialization with fingerprint."""
    browser = browser_session.browser
    assert browser is not None

    option = BrowserOption(
        use_stealth=True,
        fingerprint=BrowserFingerprint(
            devices=["desktop"],
            operating_systems=["windows"],
            locales=["zh-CN"],
        ),
    )
    init_result = await browser.initialize(option)
    assert init_result is True

    endpoint_url = await browser.get_endpoint_url()
    print("endpoint_url =", endpoint_url)
    assert endpoint_url is not None

    await asyncio.sleep(3)

    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None
        default_context = playwright_browser.contexts[0]
        assert default_context is not None

        page = await default_context.new_page()
        await page.goto("https://httpbin.org/user-agent", timeout=60000)
        response = await page.evaluate("() => JSON.parse(document.body.textContent)")
        user_agent = response["user-agent"]
        print("user_agent =", user_agent)
        assert user_agent is not None
        is_windows = is_windows_user_agent(user_agent)
        assert is_windows

        await page.close()
        await playwright_browser.close()


@pytest.mark.asyncio
@pytest.mark.timeout(120)  # 2 minute timeout for captcha test
async def test_initialize_browser_with_captchas(browser_session):
    print("solve captchas begin")
    browser = browser_session.browser
    assert browser is not None

    option = BrowserOption(
        use_stealth=True,
        solve_captchas=True,
    )
    await browser.initialize(option)

    endpoint_url = await browser.get_endpoint_url()
    print("endpoint_url =", endpoint_url)
    assert endpoint_url is not None

    await asyncio.sleep(3)

    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None
        default_context = playwright_browser.contexts[0]
        assert default_context is not None

        page = await default_context.new_page()
        # Tongcheng password recovery page with captcha
        captcha_url = "https://passport.ly.com/Passport/GetPassword"
        await page.goto(captcha_url, wait_until="domcontentloaded")

        # Wait for phone input and interact
        input_selector = "#name_in"
        input_element = await page.wait_for_selector(input_selector, timeout=10000)
        phone_number = "15011556760"
        print(f"Entering phone number: {phone_number}")

        await input_element.fill("")  # Clear input field
        await input_element.type(phone_number, delay=50)
        print("Waiting for captcha")
        await asyncio.sleep(10)
        # href changed indicates captcha solved
        current_url_location = await page.evaluate(
            "() => window.location && window.location.href"
        )
        print("current_url(window.location.href) =", current_url_location)
        assert current_url_location != captcha_url

        await page.close()
        await playwright_browser.close()
    print("solve captchas end")


@pytest.mark.asyncio
async def test_act_success(browser_session):
    browser = browser_session.browser
    assert browser is not None

    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url()
    print("endpoint_url =", endpoint_url)
    assert endpoint_url is not None

    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None

        page = await playwright_browser.new_page()
        await page.goto("http://www.baidu.com")
        assert await page.title() is not None

        result = await browser.operator.act(ActOptions(action="Click search button"), page)
        print("result =", result)

        assert result.success

        await page.close()
        await playwright_browser.close()


@pytest.mark.asyncio
async def test_observe_success(browser_session):
    browser = browser_session.browser
    assert browser is not None

    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url()
    print("endpoint_url =", endpoint_url)
    assert endpoint_url is not None

    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None

        page = await playwright_browser.new_page()
        await page.goto("http://www.baidu.com")
        assert await page.title() is not None

        result, observe_results = await browser.operator.observe(
            ObserveOptions(instruction="Find the search button"), page
        )
        print(f"result = {result}")
        print(f"observe_results = {observe_results}")

        assert result is True
        assert len(observe_results) > 0
        assert hasattr(observe_results[0], "description")

        await page.close()
        await playwright_browser.close()


@pytest.mark.asyncio
async def test_extract_success(browser_session):
    browser = browser_session.browser
    assert browser is not None

    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url()
    print("endpoint_url =", endpoint_url)
    assert endpoint_url is not None

    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None

        page = await playwright_browser.new_page()
        await page.goto("http://www.baidu.com")
        assert await page.title() is not None

        result, obj = await browser.operator.extract(
            ExtractOptions(instruction="Extract the title", schema=DummySchema), page
        )
        print(f"result = {result}")
        print(f"obj = {obj}")
        assert result is True
        assert obj is not None
        assert hasattr(obj, "title")

        await page.close()
        await playwright_browser.close()


@pytest.mark.asyncio
@pytest.mark.timeout(180)  # 3 minute timeout for proxy test
async def test_restricted_proxy_ip_comparison(browser_session, make_session):
    """Test restricted proxy by comparing IP addresses before and after proxy setup."""
    browser = browser_session.browser
    assert browser is not None

    print("=== test restricted proxy IP comparison ===")

    # Phase 1: Initialize browser without proxy and get original IP
    print("phase 1: initialize browser without proxy...")
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url()
    print(f"endpoint_url = {endpoint_url}")
    assert endpoint_url is not None

    await asyncio.sleep(2)

    # Get original IP
    original_ip = None
    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None

        context = playwright_browser.contexts[0]
        page = await context.new_page()
        await page.goto("https://httpbin.org/ip")

        try:
            response = await page.evaluate(
                "() => JSON.parse(document.body.textContent)"
            )
            original_ip = response.get("origin", "").strip()
            print(f"original IP: {original_ip}")
        except Exception as e:
            print(f"get original IP failed: {e}")

        await page.close()
        await playwright_browser.close()

    await asyncio.sleep(3)

    # Phase 2: Create new session with restricted proxy via make_session
    print("phase 2: create new session with restricted proxy...")
    lc2 = await make_session("browser_latest")
    session2 = lc2._result.session

    restricted_proxy = BrowserProxy(proxy_type="wuying", strategy="restricted")
    proxy_option = BrowserOption(proxies=[restricted_proxy])

    browser2 = session2.browser
    init_result2 = await browser2.initialize(proxy_option)
    assert init_result2 is True

    # Verify proxy configuration
    saved_option = browser2.get_option()
    assert saved_option.proxies is not None
    assert len(saved_option.proxies) == 1
    assert saved_option.proxies[0].type == "wuying"
    assert saved_option.proxies[0].strategy == "restricted"
    print("✓ proxy config validation success")

    endpoint_url2 = await browser2.get_endpoint_url()
    print(f"proxy mode endpoint_url = {endpoint_url2}")

    await asyncio.sleep(2)

    # Get proxy IP
    proxy_ip = None
    async with async_playwright() as p2:
        playwright_browser2 = await p2.chromium.connect_over_cdp(endpoint_url2)
        assert playwright_browser2 is not None

        context2 = playwright_browser2.contexts[0]
        page2 = await context2.new_page()
        await page2.goto("https://httpbin.org/ip")

        try:
            response2 = await page2.evaluate(
                "() => JSON.parse(document.body.textContent)"
            )
            proxy_ip = response2.get("origin", "").strip()
            print(f"proxy IP: {proxy_ip}")
        except Exception as e:
            print(f"get proxy IP failed: {e}")

        await page2.close()
        await playwright_browser2.close()

    # Compare IPs
    if original_ip and proxy_ip:
        if original_ip != proxy_ip:
            print(
                f"✅ static proxy test success! IP changed: {original_ip} -> {proxy_ip}"
            )
        else:
            print(
                f"⚠️  warning: proxy IP is the same, maybe proxy not working: {original_ip}"
            )
            pytest.fail("proxy IP is the same, maybe proxy not working")
    else:
        print("⚠️  failed to compare IP, but proxy config applied")


@pytest.mark.asyncio
@pytest.mark.timeout(240)  # 4 minute timeout for polling proxy test
async def test_polling_proxy_multiple_ips(browser_session):
    """Test polling proxy with multiple pages to observe different IPs."""
    browser = browser_session.browser
    assert browser is not None

    print("=== test polling proxy with multiple IPs ===")

    # Initialize browser with polling proxy
    polling_proxy = BrowserProxy(proxy_type="wuying", strategy="polling", pollsize=10)

    option = BrowserOption(proxies=[polling_proxy])
    init_result = await browser.initialize(option)
    assert init_result is True

    # Verify proxy configuration
    saved_option = browser.get_option()
    assert saved_option.proxies is not None
    assert len(saved_option.proxies) == 1
    assert saved_option.proxies[0].type == "wuying"
    assert saved_option.proxies[0].strategy == "polling"
    assert saved_option.proxies[0].pollsize == 10
    print("✓ polling proxy config validation success (pollsize=10)")

    endpoint_url = await browser.get_endpoint_url()
    print(f"endpoint_url = {endpoint_url}")

    await asyncio.sleep(2)

    # Create multiple pages and collect IPs
    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None

        context = playwright_browser.contexts[0]
        ips_collected = []

        print("create multiple pages and collect IPs...")

        try:
            await context.clear_cookies()
            await context.clear_permissions()
        except Exception as e:
            print(f"clear context failed: {e}")

        for i in range(5):
            page = await context.new_page()
            try:
                try:
                    await context.clear_cookies()
                    await context.clear_permissions()
                except Exception:
                    pass

                # to avoid cache
                cache_buster = random.randint(1000000, 9999999)
                timestamp = int(time.time() * 1000)
                random_str = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=8))
                url = f"https://ifconfig.me?_cb={cache_buster}&_t={timestamp}&_r={i}&_rand={random_str}"
                # set headers to avoid cache
                await page.set_extra_http_headers(
                    {
                        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                        "Pragma": "no-cache",
                        "Expires": "0",
                        "User-Agent": f"ProxyTest-{i}-{random.randint(1000, 9999)}",
                        "X-Request-ID": f"req-{timestamp}-{i}",
                    }
                )

                print(
                    f"page {i+1} requesting with cache-busting: ifconfig.me?_cb={cache_buster}&_t={timestamp}..."
                )

                await page.goto(url, timeout=30000, wait_until="networkidle")
                await asyncio.sleep(1)

                # extract IP from ifconfig.me
                ip = await page.evaluate(
                    """
                    () => {
                        const ipElement = document.getElementById('ip_address');
                        if (ipElement) {
                            return ipElement.textContent.trim();
                        }
                        return null;
                    }
                """
                )

                if not ip:
                    # if javascript parsing failed, try to get page content and extract IP with regex
                    page_content = await page.content()
                    ip_match = re.search(
                        r'<strong id="ip_address">\s*([0-9.]+)\s*</strong>',
                        page_content,
                    )
                    if ip_match:
                        ip = ip_match.group(1).strip()
                    else:
                        print(f"Failed to extract IP from page content for page {i+1}")
                        ip = None
                ips_collected.append(ip)
                print(f"page {i+1} IP: {ip}")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"page {i+1} get IP failed: {e}")
                ips_collected.append(None)
            finally:
                await page.close()

        await playwright_browser.close()

        # Analyze results
        valid_ips = [ip for ip in ips_collected if ip]
        unique_ips = list(set(valid_ips))

        print(f"\nresult analysis:")
        print(f"  collected valid IP count: {len(valid_ips)}")
        print(f"  unique IP count: {len(unique_ips)}")
        print(f"  unique IP list: {unique_ips}")

        if len(unique_ips) > 1:
            print(
                f"✅ polling proxy test success! detected {len(unique_ips)} different IPs"
            )
        else:
            print("❌ failed to get valid IP")

        assert len(unique_ips) > 1, "at least two valid ip"
