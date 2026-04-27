// ci-stable
package integration

import (
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/playwright-community/playwright-go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestBrowserScreenshot_Integration(t *testing.T) {
	// Skip if no API key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)
	require.NotNil(t, agentBay)

	// Create session with browser image
	params := &agentbay.CreateSessionParams{
		ImageId: "browser_latest",
	}

	sessionResult, err := agentBay.Create(params)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.True(t, sessionResult.Success)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session
	defer func() {
		// Clean up session
		_, err := agentBay.Delete(session, false)
		if err != nil {
			t.Logf("Warning: Failed to delete session: %v", err)
		}
	}()

	// Initialize browser
	option := browser.NewBrowserOption()
	success, err := session.Browser.Initialize(option)
	require.NoError(t, err)
	require.True(t, success)
	require.True(t, session.Browser.IsInitialized())

	// Get browser endpoint URL
	endpointURL, err := session.Browser.GetEndpointURL()
	require.NoError(t, err)
	require.NotEmpty(t, endpointURL)

	t.Run("Screenshot with valid page", func(t *testing.T) {
		// Start Playwright
		pw, err := playwright.Run()
		require.NoError(t, err)
		defer func() {
			_ = pw.Stop()
		}()

		// Connect to browser
		browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
		require.NoError(t, err)
		defer func() {
			_ = browserInstance.Close()
		}()

		context := browserInstance.Contexts()[0]
		page, err := context.NewPage()
		require.NoError(t, err)

		// Navigate to a page
		_, err = page.Goto("https://httpbin.org/html", playwright.PageGotoOptions{
			Timeout: playwright.Float(10000),
		})
		require.NoError(t, err)

		err = page.WaitForLoadState(playwright.PageWaitForLoadStateOptions{
			State: playwright.LoadStateDomcontentloaded,
		})
		require.NoError(t, err)

		// Take screenshot with default settings (full_page=false)
		screenshotData, err := session.Browser.Screenshot(page, nil)
		// Note: This should now work with Playwright integration
		assert.NoError(t, err)
		assert.NotNil(t, screenshotData)
		assert.Greater(t, len(screenshotData), 0)

		// Close page to free resources
		err = page.Close()
		assert.NoError(t, err)
	})

	t.Run("Screenshot with full page option", func(t *testing.T) {
		// Start Playwright
		pw, err := playwright.Run()
		require.NoError(t, err)
		defer func() {
			_ = pw.Stop()
		}()

		// Connect to browser
		browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
		require.NoError(t, err)
		defer func() {
			_ = browserInstance.Close()
		}()

		context := browserInstance.Contexts()[0]
		page, err := context.NewPage()
		require.NoError(t, err)

		// Navigate to a page
		_, err = page.Goto("https://httpbin.org/html", playwright.PageGotoOptions{
			Timeout: playwright.Float(10000),
		})
		require.NoError(t, err)

		err = page.WaitForLoadState(playwright.PageWaitForLoadStateOptions{
			State: playwright.LoadStateDomcontentloaded,
		})
		require.NoError(t, err)

		// Take screenshot with full_page=true
		options := &browser.ScreenshotOptions{
			FullPage: true,
		}
		screenshotData, err := session.Browser.Screenshot(page, options)
		// Note: This should now work with Playwright integration
		assert.NoError(t, err)
		assert.NotNil(t, screenshotData)
		assert.Greater(t, len(screenshotData), 0)

		// Close page to free resources
		err = page.Close()
		assert.NoError(t, err)
	})

	t.Run("Screenshot with custom options", func(t *testing.T) {
		// Start Playwright
		pw, err := playwright.Run()
		require.NoError(t, err)
		defer func() {
			_ = pw.Stop()
		}()

		// Connect to browser
		browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
		require.NoError(t, err)
		defer func() {
			_ = browserInstance.Close()
		}()

		context := browserInstance.Contexts()[0]
		page, err := context.NewPage()
		require.NoError(t, err)

		// Navigate to a page
		_, err = page.Goto("https://httpbin.org/html", playwright.PageGotoOptions{
			Timeout: playwright.Float(10000),
		})
		require.NoError(t, err)

		err = page.WaitForLoadState(playwright.PageWaitForLoadStateOptions{
			State: playwright.LoadStateDomcontentloaded,
		})
		require.NoError(t, err)

		// Take screenshot with custom options
		options := &browser.ScreenshotOptions{
			FullPage: false,
			Type:     "jpeg",
			Quality:  80,
			Timeout:  30000,
		}
		screenshotData, err := session.Browser.Screenshot(page, options)
		// Note: This should now work with Playwright integration
		assert.NoError(t, err)
		assert.NotNil(t, screenshotData)
		assert.Greater(t, len(screenshotData), 0)

		// Close page to free resources
		err = page.Close()
		assert.NoError(t, err)
	})

	t.Run("Screenshot without browser initialization", func(t *testing.T) {
		// Create a new browser instance that is not initialized
		uninitializedBrowser := browser.NewBrowser(session)

		// Start Playwright
		pw, err := playwright.Run()
		require.NoError(t, err)
		defer func() {
			_ = pw.Stop()
		}()

		// Connect to browser
		browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
		require.NoError(t, err)
		defer func() {
			_ = browserInstance.Close()
		}()

		context := browserInstance.Contexts()[0]
		page, err := context.NewPage()
		require.NoError(t, err)

		// Attempt to take screenshot with uninitialized browser
		screenshotData, err := uninitializedBrowser.Screenshot(page, nil)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "browser must be initialized before calling screenshot")
		assert.Nil(t, screenshotData)

		// Close page to free resources
		err = page.Close()
		assert.NoError(t, err)
	})

	t.Run("Screenshot with multiple pages", func(t *testing.T) {
		urls := []string{
			"https://httpbin.org/html",
			"https://httpbin.org/json",
		}

		// Start Playwright
		pw, err := playwright.Run()
		require.NoError(t, err)
		defer func() {
			_ = pw.Stop()
		}()

		// Connect to browser
		browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
		require.NoError(t, err)
		defer func() {
			_ = browserInstance.Close()
		}()

		context := browserInstance.Contexts()[0]

		for i, url := range urls {
			page, err := context.NewPage()
			require.NoError(t, err)

			// Navigate to a page
			_, err = page.Goto(url, playwright.PageGotoOptions{
				Timeout: playwright.Float(30000),
			})
			require.NoError(t, err)

			err = page.WaitForLoadState(playwright.PageWaitForLoadStateOptions{
				State: playwright.LoadStateDomcontentloaded,
			})
			require.NoError(t, err)

			// Take screenshot with default settings
			screenshotData, err := session.Browser.Screenshot(page, nil)
			// Note: This should now work with Playwright integration
			assert.NoError(t, err)
			assert.NotNil(t, screenshotData)
			assert.Greater(t, len(screenshotData), 0)

			// Close page
			err = page.Close()
			assert.NoError(t, err)

			t.Logf("Screenshot %d captured for %s", i+1, url)
		}
	})

	t.Run("Screenshot performance", func(t *testing.T) {
		// Start Playwright
		pw, err := playwright.Run()
		require.NoError(t, err)
		defer func() {
			_ = pw.Stop()
		}()

		// Connect to browser
		browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
		require.NoError(t, err)
		defer func() {
			_ = browserInstance.Close()
		}()

		context := browserInstance.Contexts()[0]
		page, err := context.NewPage()
		require.NoError(t, err)

		// Navigate to a page
		_, err = page.Goto("https://httpbin.org/html", playwright.PageGotoOptions{
			Timeout: playwright.Float(10000),
		})
		require.NoError(t, err)

		err = page.WaitForLoadState(playwright.PageWaitForLoadStateOptions{
			State: playwright.LoadStateDomcontentloaded,
		})
		require.NoError(t, err)

		// Measure screenshot time
		startTime := time.Now()

		// Take screenshot
		screenshotData, err := session.Browser.Screenshot(page, nil)
		// Note: This should now work with Playwright integration
		assert.NoError(t, err)
		assert.NotNil(t, screenshotData)
		assert.Greater(t, len(screenshotData), 0)

		endTime := time.Now()
		duration := endTime.Sub(startTime)

		t.Logf("Screenshot attempted in %v", duration)

		// Close page to free resources
		err = page.Close()
		assert.NoError(t, err)

		// Performance check (should complete within reasonable time even if it fails)
		assert.Less(t, duration, 30*time.Second, "Screenshot should complete within 30 seconds")
	})
}
