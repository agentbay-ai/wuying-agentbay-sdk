package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.ScreenshotBytesResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.Session;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Integration tests for Computer screenshot tool selection based on Session.linkUrl.
 *
 * These tests use real backend resources (no mocks). Do not run concurrently.
 */
public class ComputerScreenshotToolSelectionByLinkUrlIntegrationTest {

    // After the multi-region refactor, endpoints are derived from region_id.
    // The pre- prefix selects the pre-release endpoint (agentbay-pre.<region>.aliyuncs.com).
    private static final String LINK_URL_REGION = "pre-cn-hangzhou";
    private static final String LINK_URL_IMAGE_ID = "linux_latest";

    private static final String NO_LINK_URL_REGION = "pre-cn-hangzhou";
    private static final String NO_LINK_URL_IMAGE_ID = "imgc-0ab5ta4lxt8rw05a2";

    private static String region(String fallback) {
        String env = System.getenv("AGENTBAY_REGION_ID");
        return (env != null && !env.isEmpty()) ? env : fallback;
    }
    @Test
    public void testComputerLinkUrlPresentRequiresBetaTakeScreenshot() throws Exception {
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
            assertNotEquals("Expected session.linkUrl to be non-empty for this endpoint/image", "", session.getLinkUrl());

            OperationResult r = session.getComputer().screenshot();
            assertFalse(r.isSuccess());
            assertTrue(String.valueOf(r.getErrorMessage()).contains("does not support `screenshot()`"));
            assertTrue(String.valueOf(r.getErrorMessage()).contains("beta_take_screenshot"));

            ScreenshotBytesResult beta = session.getComputer().betaTakeScreenshot("png");
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
    public void testComputerLinkUrlAbsentRequiresScreenshot() throws Exception {
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
            String linkUrl = session.getLinkUrl();
            assertEquals("Expected session.linkUrl to be empty for this endpoint/image",
                    "", linkUrl);

            OperationResult r = session.getComputer().screenshot();
            assertTrue(r.getErrorMessage(), r.isSuccess());
            assertNotNull(r.getData());
            assertTrue(String.valueOf(r.getData()).trim().length() > 0);

            ScreenshotBytesResult beta = session.getComputer().betaTakeScreenshot("png");
            assertFalse(beta.isSuccess());
            assertTrue(String.valueOf(beta.getErrorMessage()).contains("does not support `beta_take_screenshot()`"));
        } finally {
            agentBay.delete(session, false);
        }
    }
}

