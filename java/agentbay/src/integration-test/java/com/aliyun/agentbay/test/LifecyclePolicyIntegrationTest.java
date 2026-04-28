// ci-stable
package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.LifecyclePolicy;
import com.aliyun.agentbay.session.Session;
import org.junit.Assume;
import org.junit.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * End-to-end tests for {@link LifecyclePolicy} on session create.
 */
public class LifecyclePolicyIntegrationTest {

    private static final String IMAGE_ID = "linux_latest";

    @Test
    public void testCustomLifecyclePolicy() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue(
                "AGENTBAY_API_KEY must be set for integration tests",
                apiKey != null && !apiKey.trim().isEmpty());

        AgentBay agentBay = new AgentBay(apiKey);
        LifecyclePolicy lp = new LifecyclePolicy(10, 60);
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(IMAGE_ID);
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "lifecycle-policy");
        labels.put("sdk", "java");
        labels.put("case", "custom");
        params.setLabels(labels);
        params.setLifecyclePolicy(lp);

        Session session = null;
        try {
            SessionResult createResult = agentBay.create(params);
            assertTrue(
                    "Create failed: " + createResult.getErrorMessage(),
                    createResult.isSuccess());
            assertNotNull(createResult.getSession());
            session = createResult.getSession();
            CommandResult cmd = session.getCommand().execute("echo hello");
            assertTrue(cmd.getOutput() != null && cmd.getOutput().trim().contains("hello"));
        } finally {
            if (session != null) {
                DeleteResult dr = agentBay.delete(session);
                assertTrue("Delete failed: " + dr.getErrorMessage(), dr.isSuccess());
            }
        }
    }

    @Test
    public void testManualReleasePolicy() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue(
                "AGENTBAY_API_KEY must be set for integration tests",
                apiKey != null && !apiKey.trim().isEmpty());

        AgentBay agentBay = new AgentBay(apiKey);
        LifecyclePolicy lp = LifecyclePolicy.manualRelease();
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(IMAGE_ID);
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "lifecycle-policy");
        labels.put("sdk", "java");
        labels.put("case", "manual");
        params.setLabels(labels);
        params.setLifecyclePolicy(lp);

        Session session = null;
        try {
            SessionResult createResult = agentBay.create(params);
            assertTrue(
                    "Create failed: " + createResult.getErrorMessage(),
                    createResult.isSuccess());
            assertNotNull(createResult.getSession());
            session = createResult.getSession();
            CommandResult cmd = session.getCommand().execute("echo manual");
            assertTrue(cmd.getOutput() != null && cmd.getOutput().trim().contains("manual"));
        } finally {
            if (session != null) {
                DeleteResult dr = agentBay.delete(session);
                assertTrue("Delete failed: " + dr.getErrorMessage(), dr.isSuccess());
            }
        }
    }

    @Test
    public void testDefaultLifecyclePolicy() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue(
                "AGENTBAY_API_KEY must be set for integration tests",
                apiKey != null && !apiKey.trim().isEmpty());

        AgentBay agentBay = new AgentBay(apiKey);
        LifecyclePolicy lp = new LifecyclePolicy();
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(IMAGE_ID);
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "lifecycle-policy");
        labels.put("sdk", "java");
        labels.put("case", "default");
        params.setLabels(labels);
        params.setLifecyclePolicy(lp);

        Session session = null;
        try {
            SessionResult createResult = agentBay.create(params);
            assertTrue(
                    "Create failed: " + createResult.getErrorMessage(),
                    createResult.isSuccess());
            assertNotNull(createResult.getSession());
            session = createResult.getSession();
        } finally {
            if (session != null) {
                DeleteResult dr = agentBay.delete(session);
                assertTrue("Delete failed: " + dr.getErrorMessage(), dr.isSuccess());
            }
        }
    }
}
