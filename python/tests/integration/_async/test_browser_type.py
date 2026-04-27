"""Integration tests for browser type selection (chrome vs chromium)."""
# ci-stable

import pytest

from agentbay import BrowserOption


@pytest.fixture
async def computer_session(make_session):
    """Create a session with computer use image (required for browser type selection).

    Note: browser_type option is only available for computer use images (windows_latest).
    """
    lc = await make_session("windows_latest")
    return lc._result.session


@pytest.fixture
async def browser_session(make_session):
    """Create a session with standard browser image."""
    lc = await make_session("browser_latest")
    return lc._result.session


@pytest.mark.asyncio
async def test_browser_type_default_none(computer_session):
    """Test that None is the default browser type."""
    print("\n=== Testing default browser type (None) ===")

    # Create browser option with default settings
    browser_option = BrowserOption()

    # Verify default browser type is None
    assert browser_option.browser_type is None
    print(f"Default browser type: {browser_option.browser_type}")

    # Initialize browser
    print("Initializing browser with default options...")
    success = await computer_session.browser.initialize(browser_option)
    assert success is True, "Failed to initialize browser"
    print("Browser initialized successfully")

    # Verify browser is initialized
    assert computer_session.browser.is_initialized()
    print("Browser is initialized")

    # Get endpoint URL
    endpoint_url = await computer_session.browser.get_endpoint_url()
    assert endpoint_url is not None
    print(f"Browser endpoint URL: {endpoint_url}")


@pytest.mark.asyncio
async def test_browser_type_chrome(computer_session):
    """Test Chrome browser type selection."""
    print("\n=== Testing Chrome browser type ===")

    # Create browser option with Chrome type
    browser_option = BrowserOption(browser_type="chrome")

    # Verify browser type is set correctly
    assert browser_option.browser_type == "chrome"
    print(f"Browser type set to: {browser_option.browser_type}")

    # Initialize browser
    print("Initializing browser with Chrome type...")
    success = await computer_session.browser.initialize(browser_option)
    assert success is True, "Failed to initialize browser with Chrome type"
    print("Browser initialized successfully with Chrome")

    # Verify browser is initialized
    assert computer_session.browser.is_initialized()
    print("Browser is initialized")

    # Get endpoint URL
    endpoint_url = await computer_session.browser.get_endpoint_url()
    assert endpoint_url is not None
    print(f"Browser endpoint URL: {endpoint_url}")


@pytest.mark.asyncio
async def test_browser_type_chromium_explicit(browser_session):
    """Test explicit Chromium browser type selection."""
    print("\n=== Testing explicit Chromium browser type ===")

    # Create browser option with explicit Chromium type
    browser_option = BrowserOption(browser_type="chromium")

    # Verify browser type is set correctly
    assert browser_option.browser_type == "chromium"
    print(f"Browser type set to: {browser_option.browser_type}")

    # Initialize browser
    print("Initializing browser with explicit Chromium type...")
    success = await browser_session.browser.initialize(browser_option)
    assert success is True, "Failed to initialize browser with Chromium type"
    print("Browser initialized successfully with Chromium")

    # Verify browser is initialized
    assert browser_session.browser.is_initialized()
    print("Browser is initialized")

    # Get endpoint URL
    endpoint_url = await browser_session.browser.get_endpoint_url()
    assert endpoint_url is not None
    print(f"Browser endpoint URL: {endpoint_url}")


@pytest.mark.asyncio
async def test_browser_type_invalid():
    """Test that invalid browser types raise ValueError."""
    print("\n=== Testing invalid browser type validation ===")

    # Test invalid browser type
    with pytest.raises(ValueError) as exc_info:
        BrowserOption(browser_type="firefox")

    assert "browser_type must be 'chrome' or 'chromium'" in str(exc_info.value)
    print("Invalid browser type correctly rejected")

    # Test another invalid browser type
    with pytest.raises(ValueError) as exc_info:
        BrowserOption(browser_type="edge")

    assert "browser_type must be 'chrome' or 'chromium'" in str(exc_info.value)
    print("Another invalid browser type correctly rejected")


@pytest.mark.asyncio
async def test_browser_type_with_other_options(computer_session):
    """Test browser type with other browser options."""
    print("\n=== Testing browser type with other options ===")

    # Create browser option with Chrome type and other options
    browser_option = BrowserOption(
        browser_type="chrome",
        use_stealth=True,
        user_agent="Mozilla/5.0 (Test) AppleWebKit/537.36",
        solve_captchas=True,
    )

    # Verify all options are set correctly
    assert browser_option.browser_type == "chrome"
    assert browser_option.use_stealth is True
    assert browser_option.user_agent == "Mozilla/5.0 (Test) AppleWebKit/537.36"
    assert browser_option.solve_captchas is True
    print("All browser options set correctly")

    # Initialize browser
    print("Initializing browser with Chrome type and other options...")
    success = await computer_session.browser.initialize(browser_option)
    assert success is True, "Failed to initialize browser with Chrome and other options"
    print("Browser initialized successfully with all options")

    # Verify browser is initialized
    assert computer_session.browser.is_initialized()
    print("Browser is initialized")

    # Get endpoint URL
    endpoint_url = await computer_session.browser.get_endpoint_url()
    assert endpoint_url is not None
    print(f"Browser endpoint URL: {endpoint_url}")


@pytest.mark.asyncio
async def test_browser_type_serialization():
    """Test that browser type is properly serialized in _to_map()."""
    print("\n=== Testing browser type serialization ===")

    # Test Chrome browser type serialization
    chrome_option = BrowserOption(browser_type="chrome")
    chrome_map = chrome_option._to_map()

    assert "browserType" in chrome_map
    assert chrome_map["browserType"] == "chrome"
    print("Chrome browser type serialized correctly")

    # Test Chromium browser type serialization
    chromium_option = BrowserOption(browser_type="chromium")
    chromium_map = chromium_option._to_map()

    assert "browserType" in chromium_map
    assert chromium_map["browserType"] == "chromium"
    print("Chromium browser type serialized correctly")

    # Test default browser type serialization (should be None/not in map)
    default_option = BrowserOption()
    default_map = default_option._to_map()

    assert "browserType" not in default_map
    print("Default browser type (None) not included in map - correct")


@pytest.mark.asyncio
async def test_browser_type_standard_image_fallback(browser_session):
    """Test that browser type works with standard browser images (should fallback to default behavior)."""
    print("\n=== Testing browser type with standard browser image ===")

    # Test Chrome browser type with standard image (should still work)
    browser_option = BrowserOption(browser_type="chrome")
    print("Initializing browser with Chrome type on standard image...")
    success = await browser_session.browser.initialize(browser_option)
    assert success is True, "Failed to initialize browser with Chrome type on standard image"
    print("Browser initialized successfully with Chrome on standard image")

    # Verify browser is initialized
    assert browser_session.browser.is_initialized()
    print("Browser is initialized")
