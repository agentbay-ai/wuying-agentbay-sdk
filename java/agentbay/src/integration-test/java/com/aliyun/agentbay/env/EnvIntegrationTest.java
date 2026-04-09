package com.aliyun.agentbay.env;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.EnvResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class EnvIntegrationTest {
    private static final String ENV_TEST_IMAGE = "imgc-0ab5takivb1ke11hu";
    private AgentBay agentBay;
    private Session session;

    @BeforeEach
    void setUp() throws AgentBayException {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assumptions.assumeTrue(apiKey != null && !apiKey.isEmpty(), "AGENTBAY_API_KEY not set");
        agentBay = new AgentBay(apiKey);
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(ENV_TEST_IMAGE);
        SessionResult sessionResult = agentBay.create(params);
        assertTrue(sessionResult.isSuccess(), "Failed to create session: " + sessionResult.getErrorMessage());
        session = sessionResult.getSession();
        assertNotNull(session, "Failed to create session");
    }

    @AfterEach
    void tearDown() {
        if (session != null) {
            try {
                session.delete();
            } catch (Exception e) {
                System.err.println("Warning: Failed to delete session: " + e.getMessage());
            }
        }
    }

    @Test
    void testSetBasicEnvVars() {
        Map<String, String> envs = new HashMap<>();
        envs.put("TEST_KEY", "test_value");
        envs.put("ANOTHER_KEY", "another_value");
        BoolResult result = session.getEnv().set(envs);
        assertTrue(result.isSuccess(), "set should succeed: " + result.getErrorMessage());
    }

    @Test
    void testGetAllEnvVars() {
        Map<String, String> envs = new HashMap<>();
        envs.put("SDK_TEST_A", "value_a");
        session.getEnv().set(envs);

        EnvResult result = session.getEnv().get();
        assertTrue(result.isSuccess());
        assertEquals("value_a", result.getEnvs().get("SDK_TEST_A"));
    }

    @Test
    void testGetSpecificKeys() {
        Map<String, String> envs = new HashMap<>();
        envs.put("GET_KEY_1", "val1");
        envs.put("GET_KEY_2", "val2");
        session.getEnv().set(envs);

        EnvResult result = session.getEnv().get("GET_KEY_1", "GET_KEY_2");
        assertTrue(result.isSuccess());
        assertEquals("val1", result.getEnvs().get("GET_KEY_1"));
        assertEquals("val2", result.getEnvs().get("GET_KEY_2"));
    }

    @Test
    void testOverwrite() {
        Map<String, String> envs = new HashMap<>();
        envs.put("OW_KEY", "original");
        session.getEnv().set(envs);
        assertEquals("original", session.getEnv().get("OW_KEY").getEnvs().get("OW_KEY"));

        envs.put("OW_KEY", "updated");
        session.getEnv().set(envs);
        assertEquals("updated", session.getEnv().get("OW_KEY").getEnvs().get("OW_KEY"));
    }

    @Test
    void testVisibleInShell() {
        Map<String, String> envs = new HashMap<>();
        envs.put("SHELL_VIS", "hello_from_env");
        session.getEnv().set(envs);

        CommandResult cmdResult = session.getCommand().executeCommand("echo $SHELL_VIS", 5000);
        assertTrue(cmdResult.isSuccess());
        assertTrue(cmdResult.getStdout().contains("hello_from_env"));
    }

    @Test
    void testSetEmptyThrows() {
        assertThrows(IllegalArgumentException.class, () -> {
            session.getEnv().set(new HashMap<>());
        });
    }
}
