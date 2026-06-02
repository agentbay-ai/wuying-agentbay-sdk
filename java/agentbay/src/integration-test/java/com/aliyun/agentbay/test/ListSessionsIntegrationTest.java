// ci-stable
package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionListResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.jupiter.api.*;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class ListSessionsIntegrationTest {

    private AgentBay agentBay;
    private List<Session> testSessions;
    private String uniqueId;

    @BeforeAll
    public void setup() throws AgentBayException {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new RuntimeException("AGENTBAY_API_KEY environment variable not set");
        }

        agentBay = new AgentBay(apiKey);
        testSessions = new ArrayList<>();

        uniqueId = generateUniqueId();
        System.out.println("Using unique ID for test: " + uniqueId);

        createTestSessions();
    }

    @AfterAll
    public void cleanup() throws AgentBayException {
        System.out.println("\nCleaning up: Deleting all test sessions...");
        for (Session session : testSessions) {
            try {
                DeleteResult result = agentBay.delete(session, false);
                System.out.println(String.format(
                    "Session %s deleted. Success: %b, Request ID: %s",
                    session.getSessionId(),
                    result.isSuccess(),
                    result.getRequestId()
                ));
            } catch (Exception e) {
                System.err.println(String.format(
                    "Warning: Error deleting session %s: %s",
                    session.getSessionId(),
                    e.getMessage()
                ));
            }
        }
    }

    private String generateUniqueId() {
        long timestamp = System.nanoTime();
        int randomPart = new Random().nextInt(10000);
        return timestamp + "-" + randomPart;
    }

    private void createTestSessions() throws AgentBayException {
        System.out.println("\nCreating test sessions...");

        CreateSessionParams params1 = new CreateSessionParams();
        Map<String, String> labels1 = new HashMap<>();
        labels1.put("project", "list-test-" + uniqueId);
        labels1.put("environment", "dev");
        labels1.put("owner", "test-" + uniqueId);
        params1.setLabels(labels1);
        params1.setImageId("linux_latest");

        System.out.println("Creating session 1 with dev environment...");
        SessionResult result1 = agentBay.create(params1);
        if (result1.isSuccess()) {
            testSessions.add(result1.getSession());
            System.out.println("Session 1 created: " + result1.getSession().getSessionId());
        }

        CreateSessionParams params2 = new CreateSessionParams();
        Map<String, String> labels2 = new HashMap<>();
        labels2.put("project", "list-test-" + uniqueId);
        labels2.put("environment", "staging");
        labels2.put("owner", "test-" + uniqueId);
        params2.setLabels(labels2);
        params2.setImageId("linux_latest");

        System.out.println("Creating session 2 with staging environment...");
        SessionResult result2 = agentBay.create(params2);
        if (result2.isSuccess()) {
            testSessions.add(result2.getSession());
            System.out.println("Session 2 created: " + result2.getSession().getSessionId());
        }

        CreateSessionParams params3 = new CreateSessionParams();
        Map<String, String> labels3 = new HashMap<>();
        labels3.put("project", "list-test-" + uniqueId);
        labels3.put("environment", "prod");
        labels3.put("owner", "test-" + uniqueId);
        params3.setLabels(labels3);
        params3.setImageId("linux_latest");

        System.out.println("Creating session 3 with prod environment...");
        int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++) {
            SessionResult result3 = agentBay.create(params3);
            if (result3.isSuccess()) {
                testSessions.add(result3.getSession());
                System.out.println("Session 3 created: " + result3.getSession().getSessionId());
                break;
            } else {
                System.err.println(String.format(
                    "Attempt %d failed to create session 3: %s",
                    attempt + 1,
                    result3.getErrorMessage()
                ));
                if (attempt < maxRetries - 1) {
                    System.out.println("Waiting 5 seconds before retrying...");
                    try {
                        Thread.sleep(5000);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }
        }

        if (testSessions.size() != 3) {
            throw new RuntimeException(
                String.format("Failed to create all 3 test sessions. Only created %d sessions.", testSessions.size())
            );
        }

        System.out.println("Waiting for sessions to be fully created...");
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    @Test
    public void testListAllSessions() {
        System.out.println("\n=== Testing list() without labels ===");

        SessionListResult result = agentBay.list();

        assertTrue(result.isSuccess(), "list() should succeed");
        assertNotNull(result.getRequestId(), "Request ID should be present");
        assertNotNull(result.getSessionInfos(), "Session infos list should not be null");

        System.out.println("Total sessions found: " + result.getTotalCount());
        System.out.println("Sessions in current page: " + result.getSessionInfos().size());
        System.out.println("Request ID: " + result.getRequestId());
    }

    @Test
    public void testListWithSingleLabel() {
        System.out.println("\n=== Testing list() with single label ===");

        Map<String, String> labels = new HashMap<>();
        labels.put("project", "list-test-" + uniqueId);

        SessionListResult result = agentBay.list(labels, null, null, null, null);

        assertTrue(result.isSuccess(), "list() with single label should succeed");
        assertNotNull(result.getRequestId(), "Request ID should be present");
        assertTrue(result.getSessionInfos().size() >= 3, "Should find at least 3 sessions");

        Set<String> sessionIds = new HashSet<>();
        for (Session session : testSessions) {
            sessionIds.add(session.getSessionId());
        }

        int foundCount = 0;
        for (SessionListResult.SessionInfo sessionInfo : result.getSessionInfos()) {
            if (sessionIds.contains(sessionInfo.getSessionId())) {
                foundCount++;
            }
        }

        assertEquals(3, foundCount, "Should find exactly 3 test sessions");

        System.out.println("Found " + foundCount + " test sessions");
        System.out.println("Total sessions with label: " + result.getSessionInfos().size());
        System.out.println("Request ID: " + result.getRequestId());
    }

    @Test
    public void testListWithMultipleLabels() {
        System.out.println("\n=== Testing list() with multiple labels ===");

        Map<String, String> labels = new HashMap<>();
        labels.put("project", "list-test-" + uniqueId);
        labels.put("environment", "dev");

        SessionListResult result = agentBay.list(labels, null, null, null, null);

        assertTrue(result.isSuccess(), "list() with multiple labels should succeed");
        assertNotNull(result.getRequestId(), "Request ID should be present");
        assertTrue(result.getSessionInfos().size() >= 1, "Should find at least 1 session");

        String devSessionId = testSessions.get(0).getSessionId();
        boolean found = false;
        for (SessionListResult.SessionInfo sessionInfo : result.getSessionInfos()) {
            if (sessionInfo.getSessionId().equals(devSessionId)) {
                found = true;
                break;
            }
        }

        assertTrue(found, "Dev session should be in the results");

        System.out.println("Found dev session: " + found);
        System.out.println("Total matching sessions: " + result.getSessionInfos().size());
        System.out.println("Request ID: " + result.getRequestId());
    }

    @Test
    public void testListWithPagination() {
        System.out.println("\n=== Testing list() with pagination ===");

        SessionListResult result = agentBay.list(null, 1, 2, null, "");

        assertTrue(result.isSuccess(), "list() with pagination should succeed");
        assertNotNull(result.getRequestId(), "Request ID should be present");
        assertTrue(result.getSessionInfos().size() <= 20, "Should return at most 20 sessions");

        System.out.println("Sessions returned with page size 20: " + result.getSessionInfos().size());
        System.out.println("Total count: " + result.getTotalCount());

        if (result.getNextToken() != null && !result.getNextToken().isEmpty()) {
            System.out.println("Next token present: " + result.getNextToken());
        }
    }

    @Test
    public void testListWithStatus() {
        System.out.println("\n=== Testing list() with status filter ===");

        Map<String, String> labels = new HashMap<>();
        labels.put("project", "list-test-" + uniqueId);

        SessionListResult result = agentBay.list(labels, null, null, "RUNNING", null);

        assertTrue(result.isSuccess(), "list() with status filter should succeed");
        assertNotNull(result.getRequestId(), "Request ID should be present");

        System.out.println("Sessions with RUNNING status: " + result.getSessionInfos().size());

        for (SessionListResult.SessionInfo sessionInfo : result.getSessionInfos()) {
            System.out.println("Session ID: " + sessionInfo.getSessionId() +
                             ", Status: " + sessionInfo.getSessionStatus());
        }
    }
}
