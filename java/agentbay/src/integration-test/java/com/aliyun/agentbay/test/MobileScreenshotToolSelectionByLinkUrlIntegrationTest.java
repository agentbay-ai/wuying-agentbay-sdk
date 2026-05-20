package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.ScreenshotBytesResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Integration tests for Mobile screenshot tool selection based on Session.linkUrl.
 *
 * These tests use real backend resources (no mocks). Do not run concurrently.
 */
public class MobileScreenshotToolSelectionByLinkUrlIntegrationTest {

    // After the multi-region refactor, endpoints are derived from region_id.
    // Both pre-release endpoints map to the "pre-cn-hangzhou" region.
    private static final String LINK_URL_REGION = "pre-cn-hangzhou";
    private static final String LINK_URL_IMAGE_ID = "mobile-use-android-12-gw";

    private static final String NO_LINK_URL_REGION = "pre-cn-hangzhou";
    private static final String NO_LINK_URL_IMAGE_ID = "imgc-0ab5ta4lxt8rw05a2";

    private static String region(String fallback) {
        String env = System.getenv("AGENTBAY_REGION_ID");
        return (env != null && !env.isEmpty()) ? env : fallback;
    }

    @Test
    public void testMobileLinkUrlPresentRequiresBetaTakeScreenshot() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        Config cfg = new Config(region(LINK_URL_REGION), 60000);
        AgentBay agentBay = new AgentBay(apiKey, cfg);

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(LINK_URL_IMAGE_ID);
        SessionResult create = agentBay.create(params);
        assertTrue(create.getErrorMessage(), create.isSuccess());
        Session session = create.getSession();
        assertNotNull(session);

        try {
            assertNotNull(session.getLinkUrl());
            OperationResult r = session.getMobile().screenshot();
            assertFalse(r.isSuccess());
            assertTrue(String.valueOf(r.getErrorMessage()).contains("does not support `screenshot()`"));
            assertTrue(String.valueOf(r.getErrorMessage()).contains("beta_take_screenshot"));

            ScreenshotBytesResult beta = session.getMobile().betaTakeScreenshot();
            assertTrue(beta.getErrorMessage(), beta.isSuccess());
            assertEquals("image", beta.getType());
            assertEquals("image/png", beta.getMimeType());
            assertNotNull(beta.getWidth());
            assertNotNull(beta.getHeight());
            assertTrue(beta.getWidth() > 0);
            assertTrue(beta.getHeight() > 0);
            assertNotNull(beta.getData());
            assertTrue(beta.getData().length > 8);
            assertEquals((byte) 0x89, beta.getData()[0]);
            assertEquals((byte) 0x50, beta.getData()[1]);
            assertEquals((byte) 0x4e, beta.getData()[2]);
            assertEquals((byte) 0x47, beta.getData()[3]);
        } finally {
            agentBay.delete(session, false);
        }
    }

    @Test
    public void testMobileLinkUrlAbsentRequiresScreenshot() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        Config cfg = new Config(region(NO_LINK_URL_REGION), 60000);
        AgentBay agentBay = new AgentBay(apiKey, cfg);

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(NO_LINK_URL_IMAGE_ID);
        SessionResult create = agentBay.create(params);
        assertTrue(create.getErrorMessage(), create.isSuccess());
        Session session = create.getSession();
        assertNotNull(session);

        try {
            // Assert link_url is empty/null for this endpoint/image
            String linkUrl = session.getLinkUrl();
            assertTrue("Expected session.link_url to be empty or null for this endpoint/image", 
                linkUrl == null || linkUrl.isEmpty());
            
            // screenshot() should succeed when link_url is absent
            OperationResult r = session.getMobile().screenshot();
            assertTrue(r.getErrorMessage(), r.isSuccess());
            assertTrue("Expected screenshot data to be a String", r.getData() instanceof String);
            String screenshotData = (String) r.getData();
            assertNotNull("Expected screenshot data to be present", screenshotData);
            assertTrue("Expected screenshot data to be non-empty", screenshotData.trim().length() > 0);

            // beta_take_screenshot() should fail with clear guidance when link_url is absent
            try {
                ScreenshotBytesResult beta = session.getMobile().betaTakeScreenshot();
                assertFalse(beta.getErrorMessage(), beta.isSuccess());
            } catch (Exception e) {
                // Expected: should throw exception with guidance message
                String errorMsg = e.getMessage();
                assertNotNull("Expected error message", errorMsg);
                assertTrue("Expected error message to contain 'does not support `beta_take_screenshot()`'",
                    errorMsg.contains("does not support") && errorMsg.contains("`beta_take_screenshot()`"));
            }

        } finally {
            agentBay.delete(session, false);
        }
    }
}

