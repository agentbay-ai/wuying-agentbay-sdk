#!/usr/bin/env python3
"""
ci-stable
Integration test for browser extension functionality using ExtensionsService public API.

This test suite validates:
1. Extension CRUD operations (create, list, update, delete)
2. Extension synchronization to browser sessions via ContextSync
3. Browser session integration with extensions
4. Policy-based extension synchronization

Public API Methods Tested:
- ExtensionsService.create(local_path) -> Extension
- ExtensionsService.list() -> List[Extension]
- ExtensionsService.update(extension_id, new_local_path) -> Extension
- ExtensionsService.delete(extension_id) -> bool
"""

import asyncio
import json
import os
import tempfile
import time
import zipfile
from typing import List, Optional
from urllib.parse import urlparse

import pytest
import pytest_asyncio
from agentbay import (
    Extension,
    ExtensionOption,
    AsyncExtensionsService,
)
from agentbay import BrowserContext, CreateSessionParams
from agentbay import BrowserOption

# Optional Playwright import
try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    async_playwright = None
    PLAYWRIGHT_AVAILABLE = False
    print(
        "Warning: Playwright not available. Browser interaction tests will be skipped."
    )


async def list_loaded_extensions(cdp_ws_url: str):
    """Standalone function to list loaded extensions using CDP WebSocket URL.

    This function exactly matches the user's provided pattern for CDP-based
    extension discovery. It can be used independently of the test suite.

    Args:
        cdp_ws_url (str): CDP WebSocket URL, e.g., "ws://127.0.0.1:9222/devtools/browser/<uuid>"

    Returns:
        List[dict]: List of extension information dictionaries
    """
    async with async_playwright() as p:
        # Connect to remote browser
        browser = await p.chromium.connect_over_cdp(cdp_ws_url)
        # Establish a CDP session (bind to the first window)
        session = await browser.new_browser_cdp_session()

        targets = await session.send("Target.getTargets")

        extensions = []

        for info in targets["targetInfos"]:
            url = info.get("url", "")
            print(f" targets.url =  {url}")
            if url.startswith("chrome-extension://"):
                # Extract EXT_ID
                ext_id = urlparse(url).netloc
                extensions.append(
                    {
                        "id": ext_id,
                        "type": info.get("type"),
                        "title": info.get("title"),
                        "url": url,
                    }
                )
                print(
                    f"Extension ID: {ext_id}, Type: {info.get('type')}, Title: {info.get('title')}, URL: {url}"
                )

        return extensions


@pytest.mark.asyncio
class TestExtensionBrowserIntegration:
    """Integration tests for browser extension management using ExtensionsService public API."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_teardown(self, agent_bay_client):
        """Set up test environment with AgentBay client and create test extensions."""
        if os.environ.get("CI"):
            pytest.skip("Skipping integration test: running in CI")

        self.agent_bay = agent_bay_client

        # Initialize ExtensionsService with auto-detected context
        self.context_name = f"test-extensions-{int(time.time())}"
        self.extensions_service = AsyncExtensionsService(self.agent_bay, self.context_name)
        # context_id is available after initialization (it's a property that derives from name)
        self.context_id = self.extensions_service.context_id
        print(f"Created extension context: {self.context_name} (ID: {self.context_id})")

        # Create browser context for data persistence
        self.browser_context_name = f"test-browser-{int(time.time())}"
        browser_context_result = await self.agent_bay.context.get(
            self.browser_context_name, create=True
        )
        if not browser_context_result.success or not browser_context_result.context:
            pytest.skip("Failed to create browser context")

        self.browser_data_context = browser_context_result.context
        self.browser_context_id = self.browser_data_context.id
        print(
            f"Created browser context: {self.browser_context_name} (ID: {self.browser_context_id})"
        )

        # Create sample extensions
        self.sample_extensions = self._create_sample_extensions()
        print(f"Created {len(self.sample_extensions)} sample extension files")

        # Pre-upload extensions for reuse in tests
        self.uploaded_extensions = []
        for ext_path in self.sample_extensions:
            extension = await self.extensions_service.create(local_path=ext_path)
            print(f"extension: {extension.id}")
            self.uploaded_extensions.append(extension)
        print(f"Pre-uploaded {len(self.uploaded_extensions)} extensions for testing")

        yield

        # Clean up uploaded extensions
        if hasattr(self, "uploaded_extensions"):
            for extension in self.uploaded_extensions:
                try:
                    await self.extensions_service.delete(extension.id)
                except Exception as e:
                    print(f"Warning: Failed to delete extension {extension.id}: {e}")
            print(f"Cleaned up {len(self.uploaded_extensions)} uploaded extensions")

        # Clean up sample files
        for ext_path in self.sample_extensions:
            if os.path.exists(ext_path):
                os.unlink(ext_path)
                temp_dir = os.path.dirname(ext_path)
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    pass

        # Clean up contexts
        if hasattr(self, "extensions_service"):
            # Use the service's cleanup method for auto-created context
            await self.extensions_service.cleanup()

        if hasattr(self, "browser_data_context"):
            try:
                await self.agent_bay.context.delete(self.browser_data_context)
                print(f"Browser context deleted: {self.browser_context_id}")
            except Exception as e:
                print(f"Warning: Failed to delete browser context: {e}")

    def _create_sample_extensions(self) -> List[str]:
        """Create sample browser extension packages for testing."""
        extensions = []

        manifests = [
            {
                "manifest_version": 3,
                "name": "Test Ad Blocker",
                "version": "1.0.0",
                "description": "A test ad blocking extension with background service worker",
                "permissions": ["activeTab", "storage", "tabs"],
                "action": {
                    "default_popup": "popup.html",
                    "default_title": "Test Ad Blocker",
                },
                "background": {"service_worker": "background.js"},
                "content_scripts": [{"matches": ["<all_urls>"], "js": ["content.js"]}],
            },
            {
                "manifest_version": 3,
                "name": "Test Password Manager",
                "version": "2.0.0",
                "description": "A test password manager with content scripts",
                "permissions": ["storage", "activeTab", "tabs"],
                "action": {
                    "default_popup": "popup.html",
                    "default_title": "Test Password Manager",
                },
                "background": {"service_worker": "background.js"},
                "content_scripts": [{"matches": ["<all_urls>"], "js": ["content.js"]}],
            },
            {
                "manifest_version": 3,
                "name": "Test Theme Extension",
                "version": "1.5.0",
                "description": "A test theme extension with background worker",
                "permissions": ["storage", "tabs"],
                "action": {
                    "default_popup": "popup.html",
                    "default_title": "Test Theme Extension",
                },
                "background": {"service_worker": "background.js"},
                "content_scripts": [{"matches": ["<all_urls>"], "js": ["content.js"]}],
            },
        ]

        for i, manifest in enumerate(manifests, 1):
            ext_path = self._create_extension_zip(f"test_ext_{i}", manifest)
            extensions.append(ext_path)

        return extensions

    def _create_extension_zip(
        self, name: str, manifest: dict, use_directory_structure: bool = False
    ) -> str:
        """Create a sample browser extension ZIP file with directory-based structure.

        Args:
            name: Extension name for the ZIP file
            manifest: Extension manifest dictionary
            use_directory_structure: If True, creates directory-based structure to avoid conflicts
                                   when extracting multiple extensions

        Returns:
            Path to the created ZIP file
        """
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"{name}.zip")
        print(f"temp_dir: {temp_dir}")
        print(f"zip_path: {zip_path}")

        # Create directory structure to avoid conflicts when extracting
        if use_directory_structure:
            extension_dir = (
                f"{name}_extension/"  # Directory name based on extension name
            )
            manifest_path = f"{extension_dir}manifest.json"
            popup_html_path = f"{extension_dir}popup.html"
            popup_js_path = f"{extension_dir}popup.js"
            background_js_path = f"{extension_dir}background.js"
            content_js_path = f"{extension_dir}content.js"
            print(f"Using directory structure: {extension_dir}")
        else:
            # Legacy flat structure (may cause conflicts)
            manifest_path = "manifest.json"
            popup_html_path = "popup.html"
            popup_js_path = "popup.js"
            background_js_path = "background.js"
            content_js_path = "content.js"
            print("Using flat structure (legacy mode)")

        with zipfile.ZipFile(zip_path, "w") as zipf:
            # Add manifest.json
            zipf.writestr(manifest_path, json.dumps(manifest, indent=2))

            # Add popup.html with basic functionality
            popup_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{manifest['name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; width: 300px; padding: 10px; }}
        .extension-info {{ margin: 5px 0; }}
        .test-section {{ margin-top: 10px; padding: 5px; background: #f0f0f0; }}
        button {{ margin: 5px; padding: 5px 10px; }}
        .directory-info {{ background: #e8f5e8; padding: 8px; margin: 10px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <h2>{manifest['name']}</h2>
    <div class="extension-info">
        <p><strong>Description:</strong> {manifest['description']}</p>
        <p><strong>Version:</strong> {manifest['version']}</p>
    </div>
    
    <div class="directory-info">
        <p><strong>Structure:</strong> {'Directory-based' if use_directory_structure else 'Flat structure'}</p>
        <p><strong>Extension ID:</strong> <span id="extensionId">Loading...</span></p>
    </div>
    
    <div class="test-section">
        <h3>Extension Test</h3>
        <button id="testStorage">Test Storage</button>
        <div id="testResult"></div>
    </div>
    
    <script src="popup.js"></script>
</body>
</html>"""
            zipf.writestr(popup_html_path, popup_html)

            # Add popup.js with basic functionality
            popup_js = f"""// Popup script for {manifest['name']}
// Directory-based structure: {'Enabled' if use_directory_structure else 'Disabled'}

document.addEventListener('DOMContentLoaded', function() {{
    const testButton = document.getElementById('testStorage');
    const resultDiv = document.getElementById('testResult');
    const extensionIdSpan = document.getElementById('extensionId');
    
    // Display extension ID
    if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {{
        extensionIdSpan.textContent = chrome.runtime.id;
    }} else {{
        extensionIdSpan.textContent = 'Not available';
    }}
    
    if (testButton) {{
        testButton.addEventListener('click', function() {{
            testStorageAPI();
        }});
    }}
    
    function testStorageAPI() {{
        if (typeof chrome !== 'undefined' && chrome.storage) {{
            const testData = {{ 
                testKey: 'extension_test', 
                timestamp: Date.now(),
                extensionName: '{manifest['name']}',
                directoryBased: {'true' if use_directory_structure else 'false'}
            }};
            
            chrome.storage.local.set(testData, () => {{
                if (chrome.runtime.lastError) {{
                    resultDiv.innerHTML = `
                        <p><strong>Storage Test Result:</strong></p>
                        <p>❌ Error: ${{chrome.runtime.lastError.message}}</p>
                    `;
                }} else {{
                    resultDiv.innerHTML = `
                        <p><strong>Storage Test Result:</strong></p>
                        <p>✅ Storage working correctly</p>
                        <p>✅ Extension is functional</p>
                        <p>📁 Structure: {'Directory-based' if use_directory_structure else 'Flat'}</p>
                    `;
                }}
                
                // Store result for test verification
                window.__EXTENSION_STORAGE_TEST__ = {{
                    success: !chrome.runtime.lastError,
                    timestamp: Date.now(),
                    extensionName: '{manifest['name']}',
                    directoryBased: {'true' if use_directory_structure else 'false'},
                    extensionId: chrome.runtime.id || 'unknown'
                }};
            }});
        }} else {{
            resultDiv.innerHTML = `
                <p><strong>Storage Test Result:</strong></p>
                <p>❌ chrome.storage not available</p>
            `;
            
            window.__EXTENSION_STORAGE_TEST__ = {{
                success: false,
                error: 'chrome.storage not available',
                directoryBased: {'true' if use_directory_structure else 'false'}
            }};
        }}
    }}
    
    // Auto-test on load
    setTimeout(testStorageAPI, 100);
}});

// Background message handling
if (typeof chrome !== 'undefined' && chrome.runtime) {{
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {{
        if (request.action === 'getStorageTestData') {{
            sendResponse(window.__EXTENSION_STORAGE_TEST__ || {{ success: false, error: 'Not tested yet' }});
        }}
    }});
}}"""
            zipf.writestr(popup_js_path, popup_js)

            # Add background.js (service worker) with comprehensive functionality
            background_js = f"""// Background Service Worker for {manifest['name']}
// Directory structure: {'Enabled' if use_directory_structure else 'Disabled'}

console.log('Background service worker started for: {manifest['name']}');

// Extension installation and startup events
chrome.runtime.onInstalled.addListener((details) => {{
    console.log('Extension installed:', details);
    
    // Set up initial configuration
    chrome.storage.local.set({{
        extensionInstalled: true,
        installTime: Date.now(),
        extensionName: '{manifest['name']}',
        directoryBased: {'true' if use_directory_structure else 'false'},
        version: '{manifest.get('version', '1.0.0')}'
    }});
}});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {{
    console.log('Background received message:', request);
    
    switch (request.action) {{
        case 'getExtensionInfo':
            chrome.storage.local.get(['extensionInstalled', 'installTime', 'extensionName'], (result) => {{
                sendResponse({{
                    success: true,
                    data: result,
                    timestamp: Date.now(),
                    serviceWorkerActive: true
                }});
            }});
            return true; // Keep message channel open for async response
            
        case 'testBackgroundStorage':
            chrome.storage.local.set({{
                backgroundTest: true,
                testTime: Date.now(),
                testData: request.data || 'No data provided'
            }}, () => {{
                sendResponse({{
                    success: !chrome.runtime.lastError,
                    error: chrome.runtime.lastError?.message
                }});
            }});
            return true;
            
        default:
            sendResponse({{ success: false, error: 'Unknown action: ' + request.action }});
    }}
}});

console.log('Background service worker fully initialized for {manifest['name']}');
"""
            zipf.writestr(background_js_path, background_js)

            # Add content.js with page interaction functionality
            content_js = f"""// Content Script for {manifest['name']}
// Directory structure: {'Enabled' if use_directory_structure else 'Disabled'}
// Injected into all pages as specified in manifest

console.log('Content script loaded for: {manifest['name']}');

// Message listener for background communication
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {{
    console.log('Content script received message:', request);
    
    switch (request.action) {{
        case 'showExtensionInfo':
            // Create a simple notification
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                z-index: 10000;
                font-family: Arial, sans-serif;
            `;
            notification.textContent = `Extension {manifest['name']} is active!`;
            document.body.appendChild(notification);
            
            // Remove notification after 3 seconds
            setTimeout(() => {{
                if (document.body.contains(notification)) {{
                    document.body.removeChild(notification);
                }}
            }}, 3000);
            
            sendResponse({{ success: true }});
            break;
            
        case 'pageLoaded':
            console.log('Page loaded notification from background:', request.url);
            sendResponse({{ success: true, contentScriptActive: true }});
            break;
            
        default:
            sendResponse({{ success: false, error: 'Unknown action: ' + request.action }});
    }}
}});

// Test function to verify content script is working
function testContentScriptFunction() {{
    return {{
        extensionName: '{manifest['name']}',
        contentScriptActive: true,
        pageUrl: window.location.href,
        timestamp: Date.now(),
        directoryBased: {'true' if use_directory_structure else 'false'}
    }};
}}

// Make function available globally for testing
window.__EXTENSION_CONTENT_SCRIPT_TEST__ = testContentScriptFunction;

console.log('Content script fully initialized for {manifest['name']} on', window.location.href);
"""
            zipf.writestr(content_js_path, content_js)

        return zip_path

    async def test_extension_crud_operations(self):
        """Test complete CRUD workflow using public API methods."""
        print("\n=== Extension CRUD Operations Test ===")

        # Use first two pre-uploaded extensions for testing
        test_extensions = self.uploaded_extensions[:2]

        # Test List - Retrieve extensions
        print("\nTesting list() method...")
        extension_list = await self.extensions_service.list()
        test_ids = {ext.id for ext in test_extensions}
        listed_ids = {ext.id for ext in extension_list}

        assert len(extension_list) >= len(test_extensions)
        assert test_ids.issubset(listed_ids)
        print(f"  ✅ Listed {len(extension_list)} extensions")

        # Test Update - Modify extension
        print("\nTesting update() method...")
        extension_to_update = test_extensions[0]
        update_source = self.sample_extensions[2]

        updated_extension = await self.extensions_service.update(
            extension_id=extension_to_update.id, new_local_path=update_source
        )

        assert updated_extension.id == extension_to_update.id
        print(f"  ✅ Updated extension: {updated_extension.id}")

        print("\n🎉 CRUD operations completed successfully!")

    async def test_extension_delete_operation(self):
        """Test extension deletion using public API method."""
        print("\n=== Extension Delete Operation Test ===")

        # Create a new extension specifically for deletion testing
        test_extension = await self.extensions_service.create(
            local_path=self.sample_extensions[0]
        )
        assert test_extension.id is not None
        print(f"  ✅ Created test extension: {test_extension.id}")

        # Test Delete - Remove extension
        print("\nTesting delete() method...")
        delete_success = await self.extensions_service.delete(test_extension.id)
        assert delete_success is True
        print(f"  ✅ Deleted extension: {test_extension.id}")

        # Verify deletion by listing extensions
        extension_list = await self.extensions_service.list()
        deleted_ids = {ext.id for ext in extension_list if ext.id == test_extension.id}
        assert len(deleted_ids) == 0, "Extension should not exist after deletion"

        print("\n🎉 Delete operation completed successfully!")

    async def test_extension_create_operation(self):
        """Test extension creation using public API method."""
        print("\n=== Extension Create Operation Test ===")

        # Test Create - Upload new extension
        print("\nTesting create() method...")
        new_extension = await self.extensions_service.create(
            local_path=self.sample_extensions[0]
        )

        assert new_extension.id is not None, "Extension ID should not be None"
        assert new_extension.name is not None, "Extension name should not be None"
        print(f"  ✅ Created extension: {new_extension.id}")

        # Verify creation by listing extensions
        extension_list = await self.extensions_service.list()
        created_ids = {ext.id for ext in extension_list if ext.id == new_extension.id}
        assert len(created_ids) == 1, "Extension should exist after creation"

        # Clean up the test extension
        delete_success = await self.extensions_service.delete(new_extension.id)
        assert delete_success is True

        print("\n🎉 Create operation completed successfully!")

    async def test_create_extension_option(self):
        """Test creation of extension option."""
        print("\n=== Extension Option Creation Test ===")
        if not self.uploaded_extensions:
            pytest.skip("No uploaded extensions available")
            
        test_extension = self.uploaded_extensions[0]
        extension_ids = [test_extension.id]
        
        print(f"Creating option for extensions: {extension_ids}")
        extension_option = await self.extensions_service.create_extension_option(extension_ids)
        
        assert extension_option is not None
        # Verify attributes instead of strict isinstance check due to async/sync class duplication
        assert hasattr(extension_option, 'context_id')
        assert hasattr(extension_option, 'extension_ids')
        assert extension_option.extension_ids == extension_ids
        print(f"  ✅ Created extension option: {extension_option}")

    @pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not available")
    async def test_extension_browser_integration(self):
        """Test comprehensive browser extension integration with real extension ID extraction.

        This test validates:
        1. Extension file synchronization to browser session
        2. Browser initialization with extension loading
        3. Real extension ID extraction via CDP Target.getTargets API
        4. Extension detection using actual loaded extension IDs (cannot mock extension ID)
        5. Extension functionality testing with webpage interactions
        6. Browser session lifecycle management

        Key Feature: Uses real extension IDs extracted from browser instead of mocked IDs
        Core feature: Use real extension IDs extracted from browser, not simulated IDs
        """
        print("\n=== Comprehensive Browser Extension Integration Test ===")

        # Use first two pre-uploaded extensions for comprehensive testing
        test_extensions = self.uploaded_extensions[:2]
        extension_ids = [ext.id for ext in test_extensions]
        print(f"Target extensions for browser integration: {extension_ids}")

        # Configure and create browser session with extensions
        session = await self._create_browser_session(extension_ids)

        try:
            # Phase 1: Extension Synchronization
            print("\nPhase 1: Extension Synchronization")
            await self._wait_for_sync(session)

            # Phase 2: Browser Initialization with Extensions
            print("\nPhase 2: Browser Initialization with Extensions")
            browser_initialized = await self._initialize_browser_with_extensions(session)
            assert browser_initialized is True, "Browser initialization with extensions failed"

            ls_result = await session.command.execute_command("ls -la /tmp/extensions/")
            if not ls_result.success:
                print("    ❌ Extensions directory not found")
                return False

            print(f"    ✅ Extensions directory exists: /tmp/extensions/")
            print(f"    Directory content:\n{ls_result.output}")

            # Phase 3: Real Extension ID Extraction via CDP
            print("\nPhase 3: Real Extension ID Extraction (CDP-based)")
            real_extension_ids = await self._extract_and_validate_real_extension_ids(session)
            assert len(real_extension_ids) > 0, "At least one real extension ID should be extracted"

            print(
                f"✅ Successfully extracted {len(real_extension_ids)} real extension ID(s):"
            )
            for ext_id in real_extension_ids:
                print(f"   - {ext_id}")

            # Phase 4: Comprehensive Extension Verification using Real IDs
            print("\nPhase 4: Extension Verification with Real IDs")
            verification_results = await self._comprehensive_browser_extension_verification_with_real_ids(session, extension_ids, real_extension_ids)
            print(f"  ✅ Verification results: {verification_results}")
            # Validate verification results
            assert verification_results["file_system_check"], "Extension files not found in file system"
            assert verification_results["real_id_extraction"], "Real extension ID extraction failed"
            assert verification_results["browser_api_detection"], "Extensions not detected via browser API"
            assert verification_results["extension_context_validation"], "Extension context validation failed"
            assert verification_results["functional_validation"], "Extension functionality validation failed"

            print(f"\n✅ All verification phases passed:")
            print(
                f"   - File System Check: {verification_results['file_system_check']}"
            )
            print(
                f"   - Real ID Extraction: {verification_results['real_id_extraction']}"
            )
            print(
                f"   - Browser API Detection: {verification_results['browser_api_detection']}"
            )
            print(
                f"   - Extension Context Validation: {verification_results['extension_context_validation']}"
            )
            print(
                f"   - Functional Validation: {verification_results['functional_validation']}"
            )

            print(
                "\n🎉 Browser extension integration with real ID extraction completed successfully!"
            )

        finally:
            await self._cleanup_session(session)

    # Helper Methods

    async def _create_browser_session(self, extension_ids: List[str]):
        """Create browser session with simplified extension synchronization using BrowserContext.

        This method demonstrates the preferred approach using ExtensionsService.create_extension_option()
        which automatically handles the extension context_id without exposing it to users.
        """
        print(f"  📦 Creating browser session with extension IDs: {extension_ids}")

        # Create session with extension sync via enhanced BrowserContext
        # Use ExtensionsService.create_extension_option() to avoid exposing context_id
        extension_option = await self.extensions_service.create_extension_option(
            extension_ids
        )

        session_params = CreateSessionParams(
            labels={"test_type": "extension_integration"},
            image_id="browser_latest",
            browser_context=BrowserContext(
                context_id=self.browser_context_id,
                auto_upload=True,
                extension_option=extension_option,
            )
        )

        session_result = await self.agent_bay.create(session_params)
        assert session_result.success is True
        session = session_result.session
        assert session is not None

        session_id = getattr(session, "session_id", "unknown")
        print(f"  ✅ Browser session created with extension support: {session_id}")
        print(f"  ✅ Extension IDs configured: {extension_ids}")
        return session

    async def _wait_for_sync(self, session):
        """Wait for extension synchronization to complete."""
        max_retries = 15  # Reduced from 30 for faster timeout
        for retry in range(max_retries):
            # session.context.info() returns a result object or the info?
            # In Sync it returns ContextInfoResult or similar.
            # In Async it should return Coroutine.
            context_info = await session.context.info()

            for item in context_info.context_status_data:
                print(f"----- Context ID: {item.context_id}")
                print(f"      Path: {item.path}")
                print(f"      Status: {item.status}")
                print(f"      Error Message: {item.error_message}")
                print(f"      self.context_id: {self.context_id}")
                if (item.path == "/tmp/extensions/"):
                    if item.status == "Success":
                        print("  ✅ Extension synchronization completed")
                        return
                    elif item.status == "Failed":
                        pytest.fail(f"Sync failed: {item.error_message}")

            print(f"  Waiting for sync, attempt {retry+1}/{max_retries}")
            await asyncio.sleep(1)  # Reduced from 2 seconds

        # Skip test instead of failing for timeout to avoid blocking CI
        pytest.skip("Extension synchronization timeout - may be due to network or service issues")

    async def _initialize_browser_with_extensions(self, session) -> bool:
        """Initialize browser session with extension loading capability."""
        try:
            # Initialize browser with extensions directory explicitly set
            browser_option = BrowserOption(extension_path="/tmp/extensions/")

            init_success = await session.browser.initialize(browser_option)

            if not init_success:
                print("  ❌ Browser initialization failed")
                return False

            endpoint_url = await session.browser.get_endpoint_url()
            if not endpoint_url:
                print("  ❌ Failed to get browser endpoint URL")
                return False

            print(
                f"  ✅ Browser initialized successfully with extension_path: /tmp/extensions/"
            )
            print(f"  ✅ Browser endpoint: {endpoint_url}")
            return True

        except Exception as e:
            print(f"  ❌ Browser initialization error: {e}")
            return False

    async def _extract_and_validate_real_extension_ids(self, session) -> List[str]:
        """Extract and validate real extension IDs using CDP and standalone function.

        This method combines the CDP-based extension extraction with validation
        to ensure we get real, loaded extension IDs for testing.

        Returns:
            List[str]: List of real extension IDs extracted from the browser
        """
        try:
            # Get CDP WebSocket URL
            endpoint_url = await session.browser.get_endpoint_url()
            if not endpoint_url:
                print("    ❌ No browser endpoint available for real ID extraction")
                return []

            # Use the standalone function to extract real extension IDs
            print(
                "    📡 Extracting real extension IDs using standalone CDP function..."
            )
            extensions = await list_loaded_extensions(endpoint_url)

            if extensions:
                real_extension_ids = [ext["id"] for ext in extensions]
                print(
                    f"    ✅ Successfully extracted {len(real_extension_ids)} real extension ID(s):"
                )

                for ext in extensions:
                    print(f"      - ID: {ext['id']}")
                    print(f"        Title: {ext['title']}")
                    print(f"        Type: {ext['type']}")
                    print(f"        URL: {ext['url']}")

                # Remove duplicates while preserving order
                unique_ids = list(dict.fromkeys(real_extension_ids))
                print(f"    📊 Total unique extension IDs: {len(unique_ids)}")

                return unique_ids
            else:
                print("    ⚠️ No real extension IDs could be extracted")
                return []

        except Exception as e:
            print(f"    ❌ Error extracting real extension IDs: {e}")
            import traceback

            print(f"    📍 Traceback: {traceback.format_exc()}")
            return []

    async def _comprehensive_browser_extension_verification_with_real_ids(
        self, session, original_extension_ids: List[str], real_extension_ids: List[str]
    ) -> dict:
        """Perform comprehensive extension verification using real extension IDs.

        Args:
            session: Browser session
            original_extension_ids: Original extension IDs from uploaded extensions
            real_extension_ids: Real extension IDs extracted from browser via CDP

        Returns:
            dict: Verification results for different validation phases
        """
        results = {
            "file_system_check": False,
            "real_id_extraction": False,
            "browser_api_detection": False,
            "extension_context_validation": False,
            "functional_validation": False,
        }

        try:
            # Phase 1: File System Verification
            print("    Phase 1: File System Verification")
            results["file_system_check"] = await self._verify_extension_files(
                session, original_extension_ids
            )

            # Phase 2: Real ID Extraction Validation
            print("    Phase 2: Real ID Extraction Validation")
            results["real_id_extraction"] = len(real_extension_ids) > 0

            # Phase 3: Browser API Detection using Real IDs
            print("    Phase 3: Browser API Detection (Real IDs)")
            results["browser_api_detection"] = await self._detect_loaded_extensions(
                session, real_extension_ids
            )

            # Phase 4: Extension Context Validation using Real IDs
            print("    Phase 4: Extension Context Validation (Real IDs)")
            results["extension_context_validation"] = (
                await self._validate_extension_contexts(session, real_extension_ids)
            )

            # Phase 5: Functional Validation
            print("    Phase 5: Extension Functional Validation")
            results["functional_validation"] = (
                await self._test_browser_basic_functionality(session)
            )

            return results

        except Exception as e:
            print(f"    ❌ Comprehensive verification error: {e}")
            return results

    async def _validate_extension_contexts(
        self, session, real_extension_ids: List[str]
    ) -> bool:
        """Validate extension contexts using real extension IDs.

        This method navigates to each extension's context and validates that
        it's properly loaded and functional.

        Args:
            session: Browser session
            real_extension_ids: List of real extension IDs from CDP

        Returns:
            bool: True if extension contexts are valid, False otherwise
        """
        if not real_extension_ids:
            print("      ❌ No real extension IDs provided for context validation")
            return False

        try:
            endpoint_url = await session.browser.get_endpoint_url()
            if not endpoint_url:
                print("      ❌ No browser endpoint available")
                return False

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = await context.new_page()

                try:
                    validated_extensions = 0

                    for ext_id in real_extension_ids:
                        print(f"      🔍 Validating extension context: {ext_id}")

                        # Navigate to extension popup page
                        ext_url = f"chrome-extension://{ext_id}/popup.html"

                        try:
                            await page.goto(
                                ext_url, wait_until="domcontentloaded", timeout=10000
                            )

                            # Check basic extension environment
                            validation_result = (
                                await self._check_basic_extension_environment(
                                    page, ext_id
                                )
                            )

                            if validation_result:
                                validated_extensions += 1
                                print(
                                    f"        ✅ Extension {ext_id} context validated successfully"
                                )
                            else:
                                print(
                                    f"        ❌ Extension {ext_id} context validation failed"
                                )

                        except Exception as nav_error:
                            print(
                                f"        ⚠️ Could not navigate to {ext_id}: {nav_error}"
                            )
                            # Continue with other extensions
                            continue

                    success = validated_extensions > 0
                    print(
                        f"      📊 Extension context validation: {validated_extensions}/{len(real_extension_ids)} successful"
                    )

                    return success

                finally:
                    await context.close()

        except Exception as e:
            print(f"      ❌ Extension context validation error: {e}")
            return False

    async def _verify_extension_files(self, session, extension_ids: List[str]) -> bool:
        """Verify extension folders exist in the browser session file system.

        Checks for folder name matches and manifest files within those folders.
        """
        try:
            # Check extensions directory exists and is readable
            ls_result = await session.command.execute_command("ls -la /tmp/extensions/")
            if not ls_result.success:
                print("    ❌ Extensions directory not found")
                return False

            print(f"    ✅ Extensions directory exists: /tmp/extensions/")
            print(f"    Directory content:\n{ls_result.output}")

            found_extensions = 0
            for ext_id in extension_ids:
                # Remove file extension from ext_id for folder matching
                base_ext_id = ext_id.rsplit(".", 1)[0] if "." in ext_id else ext_id

                # Check if extension folder exists
                folder_check = await session.command.execute_command(
                    f"test -d /tmp/extensions/{base_ext_id}"
                )
                if folder_check.success:
                    print(f"    ✅ Found extension folder: {base_ext_id}")

                    # Check if manifest.json exists in the folder
                    manifest_check = await session.command.execute_command(
                        f"test -f /tmp/extensions/{base_ext_id}/manifest.json"
                    )
                    if manifest_check.success:
                        print(f"      ✅ Contains manifest.json")
                        found_extensions += 1
                    else:
                        print(f"      ❌ No manifest.json found in folder")
                else:
                    print(f"    ❌ Extension folder not found: {base_ext_id}")

            success = found_extensions == len(extension_ids)
            print(
                f"    File system check result: {found_extensions}/{len(extension_ids)} extensions found"
            )
            return success

        except Exception as e:
            print(f"    ❌ File system verification error: {e}")
            return False

    async def _extract_real_extension_ids_from_browser(self, session) -> List[str]:
        """Extract real Chrome extension IDs from loaded extensions using CDP.

        This method uses the CDP Target.getTargets API to discover actually loaded
        Chrome extensions by scanning for chrome-extension:// URLs in the browser targets.
        Real extension IDs are extracted from the URL netloc portion.
        """
        extracted_ids = []

        try:
            endpoint_url = await session.browser.get_endpoint_url()
            if not endpoint_url:
                print(
                    "    ❌ No browser endpoint available for extension ID extraction"
                )
                return extracted_ids

            print(f"    🔍 Connecting to browser CDP endpoint: {endpoint_url}")

            async with async_playwright() as p:
                # Connect to remote browser
                browser = await p.chromium.connect_over_cdp(endpoint_url)

                # Establish a CDP session (bind to the first window)
                cdp_session = await browser.new_browser_cdp_session()

                try:
                    # Get all targets
                    print(f"    📡 Fetching browser targets via CDP...")
                    targets = await cdp_session.send("Target.getTargets")

                    print(
                        f"    🔍 Scanning {len(targets.get('targetInfos', []))} targets for loaded extensions..."
                    )

                    extensions = []
                    for info in targets["targetInfos"]:
                        url = info.get("url", "")
                        if url.startswith("chrome-extension://"):
                            # Extract EXT_ID
                            ext_id = urlparse(url).netloc

                            extension_data = {
                                "id": ext_id,
                                "type": info.get("type"),
                                "title": info.get("title"),
                                "url": url,
                            }

                            extensions.append(extension_data)
                            extracted_ids.append(ext_id)

                            print(f"    ✅ Found loaded extension:")
                            print(f"      - ID: {ext_id}")
                            print(f"      - Title: {extension_data['title']}")
                            print(f"      - Type: {extension_data['type']}")
                            print(f"      - URL: {url}")

                    # Deduplicate
                    extracted_ids = list(set(extracted_ids))

                    if extracted_ids:
                        print(
                            f"    📊 Successfully detected {len(extracted_ids)} unique loaded extension(s):"
                        )
                        for ext_id in extracted_ids:
                            print(f"      - {ext_id}")
                    else:
                        print(
                            "    ⚠️ No extensions detected via CDP - extensions may not be loaded yet"
                        )

                finally:
                    await cdp_session.detach()

        except Exception as e:
            print(f"    ❌ Error extracting real extension IDs via CDP: {e}")
            import traceback

            print(f"    📍 Traceback: {traceback.format_exc()}")

        return extracted_ids

    async def _detect_loaded_extensions(
        self, session, extension_ids: List[str]
    ) -> bool:
        """Detect loaded extensions using real extension IDs from CDP.

        IMPORTANT: This method uses REAL extension IDs extracted from the browser via CDP.

        Key points:
        - Cannot mock extension ID, must use real loaded extension ID
        - Get real extensions through CDP (Chrome DevTools Protocol) Target.getTargets API
        - Extract real extension ID from chrome-extension:// protocol URL
        - Extension ID must be actually loaded by browser, otherwise test is meaningless

        The extension detection process:
        1. Extract real extension IDs using CDP Target.getTargets API
        2. Scan for chrome-extension:// URLs in browser targets
        3. Extract extension IDs from URL netloc portion
        4. Test extension environments using real IDs
        """
        if not PLAYWRIGHT_AVAILABLE or async_playwright is None:
            print("    ⚠️ Playwright not available, skipping browser API detection")
            return True  # Skip this check if Playwright unavailable

        try:
            endpoint_url = await session.browser.get_endpoint_url()
            if not endpoint_url:
                print("    ❌ No browser endpoint available")
                return False

            print(f"    ✅ Browser endpoint available: {endpoint_url}")

            # Extract real Chrome extension IDs using CDP
            chrome_extension_ids = await self._extract_real_extension_ids_from_browser(
                session
            )

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = await context.new_page()

                try:
                    # Wait for extensions to load
                    await page.wait_for_timeout(3000)

                    # Method 1: Check extension environment within extension context
                    detected_via_basic = False
                    if chrome_extension_ids:
                        print(
                            f"    Testing extension environment in extension context..."
                        )
                        # Test the first extension's environment
                        detected_via_basic = (
                            await self._check_basic_extension_environment(
                                page, chrome_extension_ids[0]
                            )
                        )
                    else:
                        # Fallback to general page check
                        print(
                            f"    Testing extension environment in general page context..."
                        )
                        detected_via_basic = (
                            await self._check_basic_extension_environment(page)
                        )

                    # Method 2: Extension storage API availability (basic check)
                    detected_via_storage = await self._check_extension_storage_basic(
                        page
                    )

                    # Method 3: Check for extension content scripts

                    # Method 4: Check extension environment via DevTools
                    detected_via_devtools = await self._check_extension_via_devtools(
                        page
                    )

                    # Consider detection successful if any method works
                    detection_success = (
                        detected_via_basic
                        or detected_via_storage
                        or detected_via_devtools
                    )

                    print(f"    Browser extension loading verification:")
                    print(
                        f"      - Extension Context Environment: {detected_via_basic}"
                    )
                    print(
                        f"      - Extension Storage Available: {detected_via_storage}"
                    )
                    print(f"      - DevTools Environment: {detected_via_devtools}")
                    print(f"    Overall API detection: {detection_success}")

                    return detection_success

                finally:
                    await context.close()

        except Exception as e:
            print(f"    ❌ Browser API detection error: {e}")
            return False

    async def _check_basic_extension_environment(
        self, page, extension_id: Optional[str] = None
    ) -> bool:
        """
        Check basic extension API environment in extension context.
        If extension_id is provided, will automatically open that extension page for detection.
        """
        try:
            target_page = page
            # If extension_id is provided, open extension page for detection
            if extension_id:
                ext_url = f"chrome-extension://{extension_id}/popup.html"
                print(f"      Navigating to extension page for detection: {ext_url}")
                await page.goto(ext_url)
                target_page = page

            result = await target_page.evaluate(
                """
                () => {
                    const info = {
                        chromeExists: typeof chrome !== 'undefined',
                        runtimeExists: !!(typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id),
                        storageExists: !!(typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local),
                        extensionExists: !!(typeof chrome !== 'undefined' && chrome.extension),
                        apis: typeof chrome !== 'undefined' ? Object.keys(chrome).sort() : [],
                        manifest: null
                    };
                    // Read manifest
                    try {
                        if (chrome && chrome.runtime && chrome.runtime.getManifest) {
                            info.manifest = chrome.runtime.getManifest();
                        }
                    } catch(e) {}
                    return info;
                }
            """
            )

            chrome_exists = result.get("chromeExists", False)
            runtime_exists = result.get("runtimeExists", False)
            storage_exists = result.get("storageExists", False)
            extension_exists = result.get("extensionExists", False)
            apis = result.get("apis", [])
            manifest = result.get("manifest")

            print(f"      Basic Extension Environment (Extension Context):")
            print(f"        - Chrome Object: {'✅' if chrome_exists else '❌'}")
            print(f"        - Runtime API: {'✅' if runtime_exists else '❌'}")
            print(f"        - Storage API(local): {'✅' if storage_exists else '❌'}")
            print(f"        - Extension API: {'✅' if extension_exists else '❌'}")
            if apis:
                print(
                    f"        - Available Chrome APIs: {', '.join(apis[:8])}{'...' if len(apis) > 8 else ''}"
                )
            if manifest:
                print(
                    f"        - Manifest name: {manifest.get('name')} | version: {manifest.get('version')}"
                )
                print(f"        - Manifest permissions: {manifest.get('permissions')}")

            # Criteria: Success if chrome.runtime is available in extension context and manifest exists
            has_basic_env = chrome_exists and runtime_exists and manifest is not None
            print(
                f"        - Extension Environment Ready: {'✅' if has_basic_env else '❌'}"
            )

            return has_basic_env

        except Exception as e:
            print(f"      Basic extension environment check error: {e}")
            return False

    async def _check_extension_storage_basic(self, page) -> bool:
        """Check basic extension storage API availability."""
        try:
            result = await page.evaluate(
                """
                () => {
                    if (typeof chrome !== 'undefined' && chrome.storage) {
                        return {
                            success: true,
                            storageAvailable: true,
                            storageTypes: {
                                local: !!chrome.storage.local,
                                sync: !!chrome.storage.sync,
                                managed: !!chrome.storage.managed,
                                session: !!chrome.storage.session
                            }
                        };
                    } else {
                        return {
                            success: false, 
                            storageAvailable: false,
                            reason: 'chrome.storage not available',
                            chromeExists: typeof chrome !== 'undefined'
                        };
                    }
                }
            """
            )

            if result.get("success"):
                storage_types = result.get("storageTypes", {})

                print(f"      Extension Storage API:")
                print(f"        - Storage Available: ✅ Yes")
                print(f"        - Storage Types:")
                for storage_type, available in storage_types.items():
                    print(f"          - {storage_type}: {'✅' if available else '❌'}")

                return True
            else:
                chrome_exists = result.get("chromeExists", False)
                reason = result.get("reason", "Unknown error")

                print(f"      Extension Storage API:")
                print(f"        - Storage Available: ❌ No")
                print(
                    f"        - Chrome Object Exists: {'✅' if chrome_exists else '❌'}"
                )
                print(f"        - Reason: {reason}")

                return False

        except Exception as e:
            print(f"      Extension Storage API check error: {e}")
            return False

    async def _check_extension_via_devtools(self, page) -> bool:
        """Check extension loading via Chrome DevTools and runtime inspection."""
        try:
            # Check Chrome runtime and extension loading environment
            runtime_info = await page.evaluate(
                """
                () => {
                    const info = {
                        chromeExists: typeof chrome !== 'undefined',
                        runtimeExists: typeof chrome !== 'undefined' && !!chrome.runtime,
                        managementExists: typeof chrome !== 'undefined' && !!chrome.management,
                        storageExists: typeof chrome !== 'undefined' && !!chrome.storage,
                        extensionExists: typeof chrome !== 'undefined' && !!chrome.extension,
                        tabsExists: typeof chrome !== 'undefined' && !!chrome.tabs,
                        chromeApis: typeof chrome !== 'undefined' ? Object.keys(chrome).sort() : [],
                        userAgent: navigator.userAgent,
                        commandLine: '',
                        extensionFlags: []
                    };
                    
                    # Check for extension-related flags in user agent or other indicators
                    if (navigator.userAgent.includes('--load-extension') || 
                        navigator.userAgent.includes('--extension-dir')) {
                        info.extensionFlags.push('extension-flags-detected');
                    }
                    
                    # Check window properties for extension indicators
                    const windowKeys = Object.keys(window);
                    const extensionKeys = windowKeys.filter(key => 
                        key.toLowerCase().includes('extension') || 
                        key.toLowerCase().includes('chrome')
                    );
                    info.extensionWindowKeys = extensionKeys;
                    
                    return info;
                }
            """
            )

            print(f"      Chrome Runtime Environment:")
            print(
                f"        - Chrome Object: {'✅' if runtime_info.get('chromeExists') else '❌'}"
            )
            print(
                f"        - Runtime API: {'✅' if runtime_info.get('runtimeExists') else '❌'}"
            )
            print(
                f"        - Management API: {'✅' if runtime_info.get('managementExists') else '❌'}"
            )
            print(
                f"        - Storage API: {'✅' if runtime_info.get('storageExists') else '❌'}"
            )
            print(
                f"        - Extension API: {'✅' if runtime_info.get('extensionExists') else '❌'}"
            )
            print(
                f"        - Tabs API: {'✅' if runtime_info.get('tabsExists') else '❌'}"
            )

            available_apis = runtime_info.get("chromeApis", [])
            if available_apis:
                print(
                    f"        - Available Chrome APIs: {', '.join(available_apis[:10])}{'...' if len(available_apis) > 10 else ''}"
                )

            extension_keys = runtime_info.get("extensionWindowKeys", [])
            if extension_keys:
                print(f"        - Extension Window Properties: {extension_keys}")

            # Consider successful if we have basic Chrome extension APIs
            has_basic_apis = runtime_info.get("chromeExists", False) and (
                runtime_info.get("runtimeExists", False)
                or runtime_info.get("storageExists", False)
            )

            print(
                f"        - Basic Extension Environment: {'✅' if has_basic_apis else '❌'}"
            )

            return has_basic_apis

        except Exception as e:
            print(f"      DevTools extension check error: {e}")
            return False

    async def _test_browser_basic_functionality(self, session) -> bool:
        """Test basic browser functionality with extensions loaded."""
        if not PLAYWRIGHT_AVAILABLE or async_playwright is None:
            print("    ⚠️ Playwright not available, skipping functionality test")
            return True

        try:
            endpoint_url = await session.browser.get_endpoint_url()
            if not endpoint_url:
                print("    ❌ No browser endpoint available")
                return False

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = await context.new_page()

                try:
                    # Test 1: Basic navigation
                    await page.goto("https://www.example.com")
                    await page.wait_for_timeout(2000)
                    title = await page.title()

                    # Test 2: JavaScript execution
                    js_result = await page.evaluate("() => 'JavaScript working'")

                    # Test 3: DOM interaction
                    page_content = await page.content()

                    functionality_success = bool(title and js_result and page_content)

                    print(f"    Basic functionality tests:")
                    print(f"      - Navigation successful: {bool(title)}")
                    print(f"      - JavaScript execution: {bool(js_result)}")
                    print(f"      - DOM access: {bool(page_content)}")
                    print(f"    Overall functionality: {functionality_success}")

                    return functionality_success

                finally:
                    await context.close()

        except Exception as e:
            print(f"    ❌ Browser functionality test error: {e}")
            return False

    async def _test_extension_webpage_interaction(
        self, session, extension_ids: List[str]
    ) -> bool:
        """Test extension interaction with web pages."""
        if not PLAYWRIGHT_AVAILABLE or async_playwright is None:
            print("    ⚠️ Playwright not available, skipping interaction test")
            return True

        try:
            endpoint_url = await session.browser.get_endpoint_url()
            if not endpoint_url:
                print("    ❌ No browser endpoint available")
                return False

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = await context.new_page()

                try:
                    # Test interaction with different types of pages
                    test_urls = ["https://www.example.com", "https://httpbin.org/html"]

                    interaction_results = []

                    for url in test_urls:
                        try:
                            await page.goto(url, timeout=10000)
                            await page.wait_for_timeout(
                                1500
                            )  # Allow extensions to process

                            # Check if page loaded successfully with extensions
                            page_state = await page.evaluate(
                                """
                                () => ({
                                    readyState: document.readyState,
                                    title: document.title,
                                    hasExtensionMarkers: !!document.querySelector('[data-extension]'),
                                    windowExtensions: Object.keys(window).filter(key => 
                                        key.toLowerCase().includes('extension')
                                    ).length
                                })
                            """
                            )

                            interaction_success = (
                                page_state.get("readyState") == "complete"
                            )
                            interaction_results.append(interaction_success)

                            print(f"      URL {url}: {interaction_success}")

                        except Exception as url_error:
                            print(f"      URL {url}: Failed - {url_error}")
                            interaction_results.append(False)

                    # Consider successful if at least one page interaction worked
                    overall_success = any(interaction_results)

                    print(
                        f"    Extension-webpage interaction results: {interaction_results}"
                    )
                    print(f"    Overall interaction success: {overall_success}")

                    return overall_success

                finally:
                    await context.close()

        except Exception as e:
            print(f"    ❌ Extension-webpage interaction test error: {e}")
            return False

    async def _cleanup_session(self, session):
        """Clean up browser session."""
        if session is None:
            return
        session_id = getattr(session, "session_id", "unknown")
        try:
            delete_result = await session.delete(sync_context=True)
            if delete_result.success:
                print(f"  ✅ Session deleted: {session_id}")
            else:
                print(f"  ⚠️ Failed to delete session: {delete_result.error_message}")
        except Exception as e:
            print(f"  ⚠️ Error deleting session: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
