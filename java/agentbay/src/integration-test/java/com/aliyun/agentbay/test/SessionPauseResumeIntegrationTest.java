// ci-stable
package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.model.SessionListResult.SessionInfo;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.junit.Assert.*;

/**
 * Integration tests for Session pause and resume operations.
 * 
 * This test class is equivalent to TestSessionPauseResumeIntegration in 
 * test_agentbay_list_status.py
 */
public class SessionPauseResumeIntegrationTest {
    private static AgentBay agentBay;
    private List<Session> testSessions;

    @BeforeClass
    public static void setUpClass() throws AgentBayException {
        // Initialize AgentBay client
        String separator = "============================================================";
        System.out.println("\n" + separator);
        System.out.println("ENVIRONMENT CONFIGURATION");
        System.out.println(separator);
        
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.out.println("API Key: ✗ Not Set");
            throw new RuntimeException("AGENTBAY_API_KEY environment variable not set");
        }
        System.out.println("API Key: ✓ Set");
        
        String regionId = System.getenv("AGENTBAY_REGION_ID");
        if (regionId != null && !regionId.isEmpty()) {
            System.out.println("Region: " + regionId);
            com.aliyun.agentbay.Config config = new com.aliyun.agentbay.Config(regionId);
            agentBay = new AgentBay(apiKey, config);
        } else {
            System.out.println("Region: Using default");
            agentBay = new AgentBay(apiKey);
        }
        System.out.println(separator + "\n");
    }

    @Before
    public void setUp() {
        // Initialize test sessions list for cleanup
        testSessions = new ArrayList<>();
    }

    @After
    public void tearDown() {
        // Clean up test sessions after each test
        System.out.println("\nCleaning up test sessions for this test...");
        for (Session session : testSessions) {
            try {
                if (session != null) {
                    // Get session status first
                    SessionStatusResult statusResult = session.getStatus();
                    System.out.println("  ✓ Session status: " + session.getSessionId() + " - " + statusResult.getStatus());
                    
                    // TODO: Implement betaResume method
                    // If session is PAUSED, resume it first
                    if ("PAUSED".equals(statusResult.getStatus())) {
                        SessionResumeResult resumeResult = session.betaResume();
                        if (resumeResult.isSuccess()) {
                            System.out.println("  ✓ Resumed session: " + session.getSessionId());
                        }
                    }
                    
                    // Delete session if not already deleting/deleted
                    if (statusResult.getStatus() != null && 
                        !statusResult.getStatus().equals("DELETING") && 
                        !statusResult.getStatus().equals("DELETED") &&
                        !statusResult.getStatus().equals("RESUMING") &&
                        !statusResult.getStatus().equals("PAUSING") &&
                        !statusResult.getStatus().equals("FINISH")) {
                        com.aliyun.agentbay.model.DeleteResult deleteResult = session.delete(false);
                        if (deleteResult.isSuccess()) {
                            System.out.println("  ✓ Deleted session: " + session.getSessionId());
                        } else {
                            System.out.println("  ✗ Failed to delete session: " + session.getSessionId());
                        }
                    }
                }
            } catch (Exception e) {
                System.out.println("  ✗ Error cleaning up session: " + e.getMessage());
            }
        }
        testSessions.clear();
    }

    /**
     * Helper method to create a test session.
     */
    private Session createTestSession() throws AgentBayException {
        String sessionName = "test-pause-resume-" + UUID.randomUUID().toString().substring(0, 8);
        System.out.println("\nCreating test session: " + sessionName);

        // Create session with labels
        Map<String, String> labels = new HashMap<>();
        labels.put("project", "piaoyun-demo");
        labels.put("environment", "testing");
        
        CreateSessionParams params = new CreateSessionParams();
        params.setLabels(labels);
        
        SessionResult result = agentBay.create(params);
        assertTrue("Failed to create session: " + result.getErrorMessage(), result.isSuccess());
        assertNotNull("Session is null", result.getSession());

        Session session = result.getSession();
        testSessions.add(session);
        System.out.println("  ✓ Session created: " + session.getSessionId());

        return session;
    }

    /**
     * Helper method to verify session status using both get_status and _get_session,
     * and verify the session appears in the list with correct status.
     */
    private String verifySessionStatusAndList(Session session, String[] expectedStatuses, String operationName) 
            throws AgentBayException, InterruptedException {
        System.out.println("\nVerifying session status after " + operationName + "...");
        
        // First call getStatus to check the current status
        SessionStatusResult statusResult = session.getStatus();
        assertTrue("Failed to get session status: " + statusResult.getErrorMessage(), 
                  statusResult.isSuccess());
        
        String initialStatus = statusResult.getStatus() != null ? statusResult.getStatus() : "UNKNOWN";
        System.out.println("  ✓ Session status from getStatus: " + initialStatus);
        
        // Verify status is one of expected statuses
        boolean statusMatched = false;
        for (String expected : expectedStatuses) {
            if (expected.equals(initialStatus)) {
                statusMatched = true;
                break;
            }
        }
        assertTrue("Unexpected status " + initialStatus + ", expected one of " + 
                  String.join(", ", expectedStatuses), statusMatched);

        if ("FINISH".equals(initialStatus)) {
            return initialStatus;
        }

        // Then call _getSession for detailed information
        GetSessionResult sessionInfo = agentBay._getSession(session.getSessionId());
        assertTrue("Failed to get session info: " + sessionInfo.getErrorMessage(), 
                  sessionInfo.isSuccess());

        String currentStatus = sessionInfo.getData() != null ? 
                              sessionInfo.getData().getStatus() : "UNKNOWN";
        assertEquals("Session status mismatch: expected " + initialStatus + ", got " + currentStatus,
                    initialStatus, currentStatus);
        System.out.println("  ✓ Session status from _getSession: " + currentStatus);
        
        // TODO: Implement list method with status filter
        // Java AgentBay doesn't have a list(status) method yet
        // For now, we skip the list verification part
        // When list method is implemented, uncomment the following code:
        
        SessionListResult listResult = agentBay.list(currentStatus);
        assertTrue("Failed to list sessions: " + listResult.getErrorMessage(), 
                  listResult.isSuccess());
        
        // Verify session is in the list and check structure
        boolean sessionFound = false;
        for (SessionInfo sessionData : listResult.getSessionInfos()) {
            String sessionId = (String) sessionData.getSessionId();
            if (session.getSessionId().equals(sessionId)) {
                sessionFound = true;
                assertNotNull("sessionStatus field missing in list result", 
                          sessionData.getSessionStatus());
                assertNotNull("sessionId field missing in list result", 
                          sessionData.getSessionId());
                assertEquals("Session status mismatch in list", 
                           currentStatus, sessionData.getSessionStatus());
                break;
            }
        }
        
        assertTrue("Session " + session.getSessionId() + " not found in list with status " + currentStatus,
                  sessionFound);
        System.out.println("  ✓ Session found in list with status " + currentStatus);
        
        System.out.println("  ✓ Session status verification completed for " + operationName);
        
        return currentStatus;
    }

    @Test
    public void testPauseSessionSuccess() throws Exception {
        String separator = "============================================================";
        System.out.println("\n" + separator);
        System.out.println("TEST: Pause Session Success");
        System.out.println(separator);

        // Step 1: Create a test session
        Session session = createTestSession();

        // Step 2: Verify session is initially in RUNNING state
        SessionStatusResult statusResult = session.getStatus();
        assertTrue("Failed to get session status: " + statusResult.getErrorMessage(), 
                  statusResult.isSuccess());
        
        String initialStatus = statusResult.getStatus() != null ? statusResult.getStatus() : "UNKNOWN";
        System.out.println("  ✓ Session status from getStatus: " + initialStatus);
        assertEquals("Unexpected initial status, expected RUNNING", "RUNNING", initialStatus);

        // Step 3: Pause the session
        System.out.println("\nStep 2: Pausing session...");
        SessionPauseResult pauseResult = agentBay.betaPause(session);

        // Verify pause result
        assertNotNull("Pause result is null", pauseResult);
        assertTrue("Pause failed: " + pauseResult.getErrorMessage(), pauseResult.isSuccess());
        System.out.println("  ✓ Session pause initiated successfully");
        System.out.println("    Request ID: " + pauseResult.getRequestId());

        // Step 4: Wait for pause to complete
        System.out.println("\nStep 3: Waiting for session to pause...");
        Thread.sleep(2000);

        // Step 5: Verify session status after pause
        String currentStatus = verifySessionStatusAndList(session, 
                                                         new String[]{"PAUSED", "PAUSING"}, 
                                                         "pause");
        
        System.out.println("\n✅ Test completed successfully：" + currentStatus);
    }

    @Test
    public void testPauseAndDeleteSessionSuccess() throws Exception {
        String separator = "============================================================";
        System.out.println("\n" + separator);
        System.out.println("TEST: Pause and Delete Session Success");
        System.out.println(separator);

        // Step 1: Create a test session
        System.out.println("\nStep 1: Creating test session...");
        Session session = createTestSession();

        // Step 2: Pause the session
        System.out.println("\nStep 2: Pausing session...");
        SessionPauseResult pauseResult = agentBay.betaPause(session);

        // Verify pause result
        assertNotNull("Pause result is null", pauseResult);
        assertTrue("Pause failed: " + pauseResult.getErrorMessage(), pauseResult.isSuccess());
        System.out.println("  ✓ Session pause initiated successfully");
        System.out.println("    Request ID: " + pauseResult.getRequestId());

        // Step 3: Wait for pause to complete
        System.out.println("\nStep 3: Waiting for session to pause...");
        Thread.sleep(2000);

        // Step 4: Check session status before resuming
        System.out.println("  ✓ Checking session status before resuming");
        
        // TODO: Implement betaResume method
        // Resume the session before deletion
        SessionResumeResult resumeResult = session.betaResume();
        assertTrue("Resume failed: " + resumeResult.getErrorMessage(), resumeResult.isSuccess());
        System.out.println("  ✓ Session resumed");

        // Step 5: Delete the session
        System.out.println("\nStep 4: Deleting session...");
        com.aliyun.agentbay.model.DeleteResult deleteResult = session.delete(false);
        if (deleteResult.isSuccess()) {
            System.out.println("  ✓ Delete session successfully");
        }

        // Step 6: Verify session status after delete
        String currentStatus = verifySessionStatusAndList(session, 
                                                         new String[]{"DELETING", "DELETED", "FINISH"}, 
                                                         "delete");
        
        System.out.println("\n✅ Test completed successfully");
    }

    // TODO: Implement test_resume_async_session_success after betaResume is implemented
    @Test
    public void testResumeAsyncSessionSuccess() throws Exception {
        String separator = "============================================================";
        System.out.println("\n" + separator);
        System.out.println("TEST: Async Resume Session Success");
        System.out.println("\n" + separator);
        // Step 1: Create a test session
        Session session = createTestSession();
    
        // Step 2: Pause the session first
        System.out.println("\nStep 1: Pausing session...");
        SessionPauseResult pauseResult = agentBay.betaPause(session);
        assertTrue("Pause failed: " + pauseResult.getErrorMessage(), pauseResult.isSuccess());
        System.out.println("  ✓ Session pause initiated successfully");
    
        // Step 3: Wait for pause to complete
        System.out.println("\nStep 2: Waiting for session to pause...");
        Thread.sleep(2000);
    
        // Step 4: Verify session is PAUSED or PAUSING
        SessionStatusResult statusResult = session.getStatus();
        assertTrue("Failed to get session status: " + statusResult.getErrorMessage(), 
                  statusResult.isSuccess());
        Thread.sleep(2000);
        
        String status = statusResult.getStatus() != null ? statusResult.getStatus() : "UNKNOWN";
        System.out.println("  ✓ Session status from getStatus: " + status);
        assertTrue("Unexpected status, expected PAUSED or PAUSING", 
                  "PAUSED".equals(status) || "PAUSING".equals(status));
        System.out.println("  ✓ Session status checked");
    
        // Step 5: Resume the session (asynchronous)
        System.out.println("\nStep 3: Resuming session asynchronously...");
        SessionResumeResult resumeResult = agentBay.betaResume(session);
    
        // Verify async resume result
        assertNotNull("Resume result is null", resumeResult);
        assertTrue("Async resume failed: " + resumeResult.getErrorMessage(), 
                  resumeResult.isSuccess());
        System.out.println("  ✓ Session resume initiated successfully");
        System.out.println("    Request ID: " + resumeResult.getRequestId());
    
        // Step 6: Wait for resume to complete
        System.out.println("\nStep 4: Waiting for session to resume...");
        Thread.sleep(2000);
    
        // Step 7: Verify session status after async resume
        String currentStatus = verifySessionStatusAndList(session, 
                                                         new String[]{"RUNNING", "RESUMING"}, 
                                                         "async resume");
        
        System.out.println("\n✅ Test completed successfully");
    }
}
